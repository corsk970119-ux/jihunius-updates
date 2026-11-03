"""Save acknowledgements must precede closure; failed or stale requests cannot update."""
import hashlib
import os
from pathlib import Path
from types import ModuleType, SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
module = ModuleType('companions_test')
exec((ROOT/'src/companion_update.py').read_text()+'\n'+(ROOT/'src/companions.py').read_text(), module.__dict__)
adapters = ModuleType('adapters_test')
exec((ROOT/'src/companion_update.py').read_text()+'\n'+(ROOT/'src/companion_adapters.py').read_text(), adapters.__dict__)


class SaveHandshakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        env = patch.dict(os.environ, LOCALAPPDATA=self.tmp.name); env.start(); self.addCleanup(env.stop)
        data = b'# companion\n'
        payloads = {key: {'data':data, 'sha256':hashlib.sha256(data).hexdigest(), 'title':key}
                    for key in ('protrusion', 'wash-log', 'special-table')}
        self.children = []
        def spawn(*args, **kwargs):
            process = Mock(pid=100+len(self.children)); process.poll.return_value = None
            self.children.append(process)
            return process
        self.manager = module.CompanionManager(payloads, self.tmp.name, _backend=Mock(), _popen=spawn)
        for key in payloads: self.manager.open(key)
        self.manager.begin_update_save()

    def response(self, key, status, **overrides):
        session, nonce = self.manager.sessions[key]
        value = {'nonce':nonce, 'id':self.manager.update_save['id'], 'status':status, **overrides}
        module._cu_write(session/'response.json', value)

    def command(self, key):
        return module._cu_read(self.manager.sessions[key][0]/'request.json')['phase']

    def test_all_saves_must_acknowledge_before_any_close(self):
        self.response('protrusion', 'ready')
        self.assertFalse(self.manager.poll_update_save())
        self.assertEqual(self.command('protrusion'), 'prepare')
        self.response('wash-log', 'ready')
        self.assertFalse(self.manager.poll_update_save())
        self.assertEqual(self.command('wash-log'), 'prepare')
        self.response('special-table', 'ready')
        self.assertFalse(self.manager.poll_update_save())
        self.assertEqual(self.command('protrusion'), 'close')
        self.assertEqual(self.command('wash-log'), 'close')
        self.assertEqual(self.command('special-table'), 'close')
        for key in self.manager.sessions: self.response(key, 'closed')
        self.assertFalse(self.manager.poll_update_save())
        for process in self.children: process.poll.return_value = 0
        self.assertTrue(self.manager.poll_update_save())
        self.assertEqual(self.manager.running_keys(), [])
        self.assertEqual(self.manager.sessions, {})

    def test_failed_save_cancels_without_native_close_or_kill(self):
        self.response('protrusion', 'ready')
        self.response('wash-log', 'error', message='shared folder offline')
        with self.assertRaisesRegex(RuntimeError, 'offline'): self.manager.poll_update_save()
        self.manager.cancel_update_save()
        self.assertEqual(self.command('protrusion'), 'cancel')
        self.manager.backend.close.assert_not_called()
        for process in self.children:
            process.terminate.assert_not_called(); process.kill.assert_not_called()

    def test_stale_or_wrong_nonce_acknowledgement_is_ignored(self):
        for override in ({'id':'previous'}, {'nonce':'invalid'}):
            self.response('protrusion', 'ready', **override)
            self.response('wash-log', 'ready')
            self.assertFalse(self.manager.poll_update_save())
            self.assertEqual(self.command('wash-log'), 'prepare')

    def test_process_crash_cannot_count_as_successful_save(self):
        self.children[0].poll.return_value = 1
        with self.assertRaises(RuntimeError): self.manager.poll_update_save()

    def test_timeout_does_not_quit_late(self):
        self.manager.update_save['start'] -= 91
        with self.assertRaises(RuntimeError): self.manager.poll_update_save()
        self.manager.cancel_update_save()
        self.assertIsNone(self.manager.update_save)
        self.assertEqual(self.command('wash-log'), 'cancel')

    def test_another_companion_cannot_open_mid_update(self):
        with self.assertRaises(RuntimeError): self.manager.open('wash-log')


class SaveAdapterTests(unittest.TestCase):
    def test_ready_child_waits_for_inflight_sync_before_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            bridge=module.CompanionUpdateBridge.__new__(module.CompanionUpdateBridge)
            bridge.path=Path(tmp);bridge.nonce='a'*32;bridge.request_id='current'
            bridge.active=True;bridge.ready=True;bridge.started=True;bridge.overlay=None;bridge.error=''
            bridge.root=Mock();bridge.adapter=Mock()
            bridge.adapter.saved.side_effect=[False,True]
            module._cu_write(bridge.path/'request.json',{'nonce':bridge.nonce,'id':'current',
                'phase':'close','expires':module._cu_time.time()+30})
            bridge.poll()
            self.assertTrue(bridge.active);bridge.adapter.finish.assert_not_called()
            bridge.poll()
            bridge.adapter.finish.assert_called_once()
            self.assertEqual(module._cu_read(bridge.path/'response.json')['status'],'closed')

    def test_protrusion_requires_fresh_success_and_empty_pending(self):
        app = SimpleNamespace(closing=False,closed=False,ready=True,_memo_changed=Mock(),
            _update_sync_sequence=4,_update_error_sequence=0,_start_sync=Mock(),busy=False,
            pending={'memo': 'new'},resolving_conflicts=False,last_error='',_destroy=Mock())
        adapter = adapters.ProtrusionUpdateSave(app); adapter.begin()
        self.assertFalse(adapter.saved())
        app._update_sync_sequence += 1
        self.assertFalse(adapter.saved())
        app.pending.clear(); self.assertTrue(adapter.saved())
        app._update_error_sequence += 1
        with self.assertRaises(RuntimeError): adapter.saved()
        app._destroy.assert_not_called()

    def test_wash_saves_active_cell_and_tools_but_never_posts_draft_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            adapters.CONFIG_DIR = Path(tmp)
            adapters.json = module._cu_json
            app = SimpleNamespace(closing=False,connected=True,online=True,connecting=False,
                pending_updates={},failed_operations=[],_update_error_sequence=0,
                edit={'saving':False,'commit':Mock()},toolvars=[Mock()],submit_tool=Mock(),
                cancel_plate_drag=Mock(),busy=0,tool_drafts={},data={'tools':['new']},save_config=Mock(),
                active_folder='share',note_input=Mock(),dept=Mock(),stop=Mock(),destroy=Mock(),post_note=Mock())
            app.toolvars[0].get.return_value='new'
            app.note_input.get.return_value='보내지 않은 메모'
            app.dept.get.return_value='생산'
            adapter = adapters.WashLogUpdateSave(app); adapter.begin()
            app.edit['commit'].assert_called_once(); app.submit_tool.assert_called_once_with(0)
            self.assertFalse(adapter.saved())
            app.edit=None; self.assertTrue(adapter.saved())
            self.assertFalse(adapter.draft_path().exists())
            adapter.finish()
            self.assertEqual(adapter.read_draft()['text'], '보내지 않은 메모')
            app.post_note.assert_not_called()
            app.destroy.assert_called_once()
            next_app=SimpleNamespace(cfg={'folder':'share'},note_input=Mock(),dept=Mock(),note_feedback=Mock())
            next_app.note_input.get.return_value=''
            adapters.DEFAULT_FOLDER='share'
            adapters.WashLogUpdateSave.restore_draft(next_app)
            next_app.note_input.insert.assert_called_once_with('1.0','보내지 않은 메모')
            self.assertFalse(adapter.draft_path().exists())

    def test_wash_failed_write_preserves_window(self):
        app = SimpleNamespace(closing=False,connected=True,online=True,connecting=False,
            pending_updates={},failed_operations=[],_update_error_sequence=0,edit=None,
            toolvars=[],submit_tool=Mock(),cancel_plate_drag=Mock(),busy=0,tool_drafts={},
            data={'tools':[]},save_config=Mock(side_effect=OSError('disk full')),destroy=Mock())
        adapter = adapters.WashLogUpdateSave(app); adapter.begin()
        with self.assertRaises(OSError): adapter.saved()
        app.destroy.assert_not_called()


if __name__ == '__main__': unittest.main()
