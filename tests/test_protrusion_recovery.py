"""Network stalls are bounded and unsent edits survive a process restart safely."""
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import tkinter as tk
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import protrusion
from companion_adapters import ProtrusionUpdateSave


def _stall_shared_replace_service(connection, folder):
    """Run real shared writes, but stall their final OS replacement in the child."""
    def blocked_replace(source, destination):
        (Path(folder).parent / 'replace-started').write_text(str(source), encoding='utf-8')
        time.sleep(60)

    with patch.object(protrusion.os, 'replace', side_effect=blocked_replace):
        protrusion._shared_store_service(connection, folder)


class ProtrusionRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name) / 'shared'
        self.store = protrusion.SharedStore(self.folder)
        self.draft_path = Path(self.tmp.name) / 'local' / 'pending.json'

    def recovery(self):
        self.assertTrue(hasattr(protrusion, 'PendingRecovery'),
                        'Unsent edits need a durable local snapshot')
        return protrusion.PendingRecovery(self.store.path, path=self.draft_path)

    def client(self, timeout=1):
        self.assertTrue(hasattr(protrusion, 'SharedStoreClient'),
                        'Share I/O must run inside a terminable helper')
        client = protrusion.SharedStoreClient(self.folder, timeout=timeout)
        self.addCleanup(client.close)
        return client

    def test_latest_pending_survives_restart_without_accumulating_history(self):
        draft = self.recovery()
        draft.save({'memo': {'seq': 1, 'key': 'memo', 'base': '', 'value': 'earlier'}})
        draft.save({'memo': {'seq': 2, 'key': 'memo', 'base': '', 'value': 'latest'}})
        recovered = self.recovery().load()
        self.assertEqual(recovered['memo']['base'], '')
        self.assertEqual(recovered['memo']['value'], 'latest')
        self.assertEqual(list(self.draft_path.parent.iterdir()), [self.draft_path])
        draft.save({})
        self.assertEqual(self.recovery().load(), {})

    def test_recovered_edit_does_not_overwrite_other_pcs_new_value(self):
        self.store.sync()
        self.recovery().save({'memo': {'seq': 1, 'key': 'memo', 'base': '', 'value': 'mine'}})
        self.store.sync([{'key': 'memo', 'base': '', 'value': 'other PC'}])
        result = self.client().sync(self.recovery().load().values())
        self.assertEqual(result['conflicts'], ['memo'])
        self.assertEqual(result['state']['values']['memo'], 'other PC')
        self.assertEqual(self.recovery().load()['memo']['value'], 'mine')

    def test_lost_success_reply_replay_is_idempotent(self):
        self.store.sync()
        self.recovery().save({'memo': {'seq': 1, 'key': 'memo', 'base': '', 'value': 'mine'}})
        committed = self.store.sync(self.recovery().load().values())
        # Simulate termination after the atomic shared commit but before its reply.
        replay = self.client().sync(self.recovery().load().values())
        self.assertEqual(replay['conflicts'], [])
        self.assertEqual(replay['state']['revision'], committed['state']['revision'])
        self.assertEqual(replay['state']['values']['memo'], 'mine')

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'A local FIFO reproduces a blocked OS read')
    def test_hung_os_read_times_out_and_next_attempt_can_reconnect(self):
        self.folder.mkdir()
        os.mkfifo(self.store.path)
        client = self.client(timeout=.3)
        start = time.monotonic()
        with self.assertRaises(TimeoutError):
            client.sync()
        self.assertLess(time.monotonic() - start, 2)
        self.assertIsNone(client.process)
        self.store.path.unlink()
        result = client.sync()
        self.assertEqual(result['state']['values']['memo'], '')
        process = client.process
        client.sync()
        self.assertIs(client.process, process, 'Healthy polls should reuse the helper')

    def test_invalid_recovery_never_changes_original_file(self):
        draft = self.recovery()
        self.draft_path.parent.mkdir()
        raw = '{"version":1,"operations":[{"key":"memo","base":false,"value":"mine"}]}'
        self.draft_path.write_text(raw, encoding='utf-8')
        with self.assertRaises(ValueError):
            draft.load()
        self.assertEqual(self.draft_path.read_text(encoding='utf-8'), raw)

    def test_failed_atomic_local_save_keeps_previous_snapshot(self):
        draft = self.recovery()
        draft.save({'memo': {'key': 'memo', 'base': '', 'value': 'previous'}})
        with patch.object(protrusion.os, 'replace', side_effect=PermissionError('disk unavailable')):
            with self.assertRaises(PermissionError):
                draft.save({'memo': {'key': 'memo', 'base': '', 'value': 'new'}})
        self.assertEqual(draft.load()['memo']['value'], 'previous')
        self.assertEqual(list(self.draft_path.parent.iterdir()), [self.draft_path])

    def test_repeated_killed_writes_leave_one_stage_and_retry_preserves_committed_data(self):
        self.store.sync([{'key': 'memo', 'base': '', 'value': 'already committed'}])
        before = self.store.path.read_bytes()
        legacy = self.folder / '.roll_defect_legacy.tmp'
        legacy.write_text('unrelated legacy file', encoding='utf-8')
        original_files = set(self.folder.iterdir())
        marker = self.folder.parent / 'replace-started'
        operation = {'key': 'memo', 'base': 'already committed', 'value': 'pending retry'}
        client = self.client(timeout=.5)
        for _ in range(3):
            marker.unlink(missing_ok=True)
            with patch.object(protrusion, '_shared_store_service', _stall_shared_replace_service):
                with self.assertRaises(TimeoutError):
                    client.sync([operation])
            self.assertTrue(marker.exists(), 'The helper must reach the final write before timeout')
            self.assertEqual(self.store.path.read_bytes(), before)
            self.assertLessEqual(len(set(self.folder.iterdir()) - original_files), 1)
            self.assertIsNone(client.process)
        result = client.sync([operation])
        self.assertEqual(result['conflicts'], [])
        self.assertEqual(result['state']['values']['memo'], 'pending retry')
        self.assertEqual(json.loads(self.store.path.read_text(encoding='utf-8'))['version'], 3)
        self.assertEqual(set(self.folder.iterdir()), original_files)
        self.assertEqual(legacy.read_text(encoding='utf-8'), 'unrelated legacy file')


class ProtrusionAppRecoveryTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest('A display is required for real Tk lifecycle tests')
        self.root.withdraw()
        self.addCleanup(self.close_root)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = protrusion.SharedStore(Path(self.tmp.name) / 'shared')
        self.draft_path = Path(self.tmp.name) / 'pending.json'
        self.assertTrue(hasattr(protrusion.DefectApp, '_flush_pending'),
                        'Close and update-save must flush local pending edits')
        self.recovery = protrusion.PendingRecovery(self.store.path, path=self.draft_path)
        patcher = patch.object(protrusion, 'ProtrusionUpdateSave', ProtrusionUpdateSave, create=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in ('CompanionUpdateBridge', 'CompanionWindowState'):
            patcher = patch.object(protrusion, name, lambda *args: None, create=True)
            patcher.start()
            self.addCleanup(patcher.stop)

    def close_root(self):
        app = getattr(self, 'app', None)
        if app is not None and not app.closed:
            app._destroy()
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def wait_for(self, condition, timeout=3):
        deadline = time.monotonic() + timeout
        while not condition() and time.monotonic() < deadline:
            self.root.update()
            time.sleep(.01)
        self.assertTrue(condition(), 'Tk operation did not finish before its deadline')

    def test_close_during_blocked_save_flushes_latest_edit_before_destroy(self):
        self.app = protrusion.DefectApp(self.root, self.store, recovery=self.recovery)
        self.wait_for(lambda: self.app.ready)
        self.app.busy = True  # Save request already owns the I/O worker.
        self.app._changed('memo', 'last input before close')
        self.app._on_close()
        self.assertEqual(self.recovery.load()['memo']['value'], 'last input before close')
        with patch.object(protrusion.messagebox, 'askyesno', return_value=True):
            self.app._on_close()
        self.assertTrue(self.app.closed)
        self.assertEqual(self.recovery.load()['memo']['value'], 'last input before close')

    def test_recovered_values_are_visible_before_reconnect_and_keep_original_base(self):
        self.recovery.save({'memo': {'seq': 1, 'key': 'memo', 'base': '', 'value': 'offline input'},
                            'upper.product.0': {'seq': 2, 'key': 'upper.product.0',
                                                'base': '네오(35)', 'value': 'edited product'}})
        self.app = protrusion.DefectApp(self.root, self.store, recovery=self.recovery)
        self.assertEqual(self.app.memo_text.get('1.0', 'end-1c'), 'offline input')
        self.assertEqual(self.app.field_vars['upper.product.0'].get(), 'edited product')
        self.assertEqual(self.app.pending['upper.product.0']['base'], '네오(35)')
        self.wait_for(lambda: self.app.ready and not self.app.pending)
        self.assertFalse(self.draft_path.exists())
        self.assertEqual(self.store.sync()['state']['values']['memo'], 'offline input')

    def test_update_save_entry_flushes_new_edits_while_another_sync_is_busy(self):
        self.app = protrusion.DefectApp(self.root, self.store, recovery=self.recovery)
        self.wait_for(lambda: self.app.ready)
        self.app.busy = True
        self.app._changed('memo', 'update must retain this')
        ProtrusionUpdateSave(self.app).begin()
        self.assertEqual(self.recovery.load()['memo']['value'], 'update must retain this')

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'A local FIFO reproduces a blocked OS read')
    def test_real_network_read_timeout_releases_ui_busy_state_and_preserves_edit(self):
        self.app = protrusion.DefectApp(self.root, self.store, recovery=self.recovery)
        self.wait_for(lambda: self.app.ready)
        self.app._io.timeout = .2
        self.store.path.unlink()
        os.mkfifo(self.store.path)
        self.app._changed('memo', 'pending through timeout')
        self.app._start_sync()
        self.wait_for(lambda: not self.app.busy and bool(self.app.last_error))
        self.assertEqual(self.app.pending['memo']['value'], 'pending through timeout')
        self.assertEqual(self.recovery.load()['memo']['value'], 'pending through timeout')
        self.assertIsNone(self.app._io.process)
        self.store.path.unlink()
        self.app._start_sync()
        self.wait_for(lambda: not self.app.pending and not self.app.last_error)
        self.assertEqual(self.store.sync()['state']['values']['memo'], 'pending through timeout')


if __name__ == '__main__':
    unittest.main()
