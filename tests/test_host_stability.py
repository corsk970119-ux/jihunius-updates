"""Local-only regressions for failed SMB reads and responsive USB refreshes."""
import errno
import os
from pathlib import Path
import queue
import sys
import tempfile
import threading
import time
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

SOURCE_PATH = Path(__file__).resolve().parents[1] / 'apps/jihunius/app.pyw'


def load_app():
    name = 'host_stability_' + uuid.uuid4().hex
    module = ModuleType(name)
    module.__file__ = str(SOURCE_PATH)
    sys.modules[name] = module
    exec(compile(SOURCE_PATH.read_bytes(), str(SOURCE_PATH), 'exec'), module.__dict__)
    return module


class Value:
    def __init__(self, value=''):
        self.value = value
        self.owner = threading.get_ident()

    def get(self):
        assert threading.get_ident() == self.owner, 'UI read from worker'
        return self.value

    def set(self, value):
        assert threading.get_ident() == self.owner, 'UI write from worker'
        self.value = value


class Widget:
    def __init__(self):
        self.owner = threading.get_ident()
        self.options = {}
        self.items = []
        self.selected = set()
        self.text = ""

    def check(self):
        assert threading.get_ident() == self.owner, 'UI access from worker'

    def configure(self, **kwargs): self.check(); self.options.update(kwargs)
    def get(self, *args): self.check(); return self.text
    def curselection(self): self.check(); return tuple(sorted(self.selected))
    def yview(self): self.check(); return (.25, .75)
    def delete(self, *args): self.check(); self.items.clear(); self.selected.clear()
    def insert(self, where, *values): self.check(); self.items.extend(values)
    def selection_set(self, index): self.check(); self.selected.add(index)
    def selection_clear(self, *args): self.check(); self.selected.clear()
    def activate(self, index): self.check()
    def see(self, index): self.check()
    def yview_moveto(self, value): self.check()


class Window:
    def __init__(self): self.owner = threading.get_ident(); self.idle = []; self.timers = []
    def after_idle(self, callback):
        assert threading.get_ident() == self.owner, 'Tk timer from worker'
        self.idle.append(callback)
    def after(self, delay, callback):
        assert threading.get_ident() == self.owner, 'Tk timer from worker'
        self.timers.append((delay, callback))
        return len(self.timers) - 1
    def after_cancel(self, timer):
        assert threading.get_ident() == self.owner, 'Tk cancellation from worker'
        self.timers[timer] = (0, lambda: None)
    def withdraw(self):
        assert threading.get_ident() == self.owner, 'Tk hide from worker'


def host(module):
    app = module.IntegrationApp.__new__(module.IntegrationApp)
    app.window = Window()
    app.events = queue.Queue()
    app.destination = None
    app.program_base_root = module.PROGRAM_BASE_ROOT
    app.busy = False
    app.wash_app = SimpleNamespace(busy=False)
    app._suite_stopped = False
    app._suite_exit_pending = False
    app.drive_action_pending = None
    app.tk = SimpleNamespace(TclError=RuntimeError)
    app.alerts = []
    app.messagebox = SimpleNamespace(showerror=lambda *a, **k: app.alerts.append(a),
                                     showinfo=lambda *a, **k: app.alerts.append(a))
    app.card_modifier_pending = False
    app.card_modifier_signature = None
    app.drive_refresh_loading = False
    app.drive_refresh_generation = 0
    app.drive_refresh_pending = False
    app.drive_snapshot = None
    app.drive_select_path = None
    app.drive_contents_signature = None
    app.drive_item_paths = []
    app.drive_contents = Widget()
    app.destination_text = Value()
    app.drive_contents_status = Value()
    app.status = Value('ready')
    app.mode = Value(module.MODE_BOTH)
    app.list_number = Value(module.DEFAULT_LIST_NUMBER)
    app.mode_buttons = []; app.list_buttons = []
    app.number_input = Widget(); app.folder_input = Widget(); app.year_input = Widget()
    app.empty_button = Widget(); app.import_button = Widget()
    app.logs = []
    app.append_log = app.logs.append
    return app


def windows_error(code):
    # CPython on Windows maps several network failures to FileNotFoundError.
    error = FileNotFoundError(errno.ENOENT, 'injected Windows network/path failure')
    error.winerror = code
    return error


class HostStabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.module = load_app()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_network_and_transient_path_errors_never_become_empty_handover(self):
        store = self.module.HandoverStore(self.root / 'handover')
        note = store.add('Keep this title', 'Keep this content')
        original_stat = Path.stat
        for code in (2, 3, 53, 64, 67, 121, 1231):
            with self.subTest(winerror=code):
                def fail_child(path, *args, **kwargs):
                    if path == store.path: raise windows_error(code)
                    return original_stat(path, *args, **kwargs)
                with patch.object(Path, 'stat', fail_child):
                    with self.assertRaises(self.module.WorkError): store.load()
        self.assertEqual(store.load()[0]['id'], note['id'])

    def test_real_missing_child_is_empty_and_first_add_still_creates_it(self):
        store = self.module.HandoverStore(self.root / 'new-handover')
        self.assertEqual(store.load(), [])
        note = store.add('First', 'Content')
        self.assertEqual(store.load(), [note])

    def test_windows_path_not_found_is_empty_only_when_parent_confirms_absence(self):
        store = self.module.HandoverStore(self.root / 'new-handover')
        original_stat = Path.stat
        def missing_child(path, *args, **kwargs):
            if path == store.path: raise windows_error(3)
            return original_stat(path, *args, **kwargs)
        with patch.object(Path, 'stat', missing_child):
            self.assertEqual(store.load(), [])
        def network_child(path, *args, **kwargs):
            if path == store.path: raise windows_error(53)
            return original_stat(path, *args, **kwargs)
        with patch.object(Path, 'stat', network_child):
            with self.assertRaises(self.module.WorkError): store.load()

    def test_missing_parent_is_a_connection_error(self):
        store = self.module.HandoverStore(self.root / 'absent-parent' / 'handover')
        with self.assertRaises(self.module.WorkError): store.load()

    def test_failed_handover_refresh_preserves_previously_displayed_notes(self):
        module = self.module
        store = module.HandoverStore(self.root / 'handover')
        note = store.add('Existing', 'Keep')
        app = host(module)
        app.handover_store = store
        app.handover_notes = {note['id']: note}
        app.handover_signature = ('previous',)
        app.handover_loading = False
        app.handover_refresh_pending = False
        app.handover_status = Value()
        app.update_handover_toggle = lambda: None
        original_stat = Path.stat
        def fail_child(path, *args, **kwargs):
            if path == store.path: raise windows_error(53)
            return original_stat(path, *args, **kwargs)
        with patch.object(Path, 'stat', fail_child):
            app.refresh_handover()
            event = app.events.get(timeout=1)
        self.assertIsNotNone(event[3], 'read failure must take the existing preserve-list path')
        app.finish_handover_load(*event[1:])
        self.assertEqual(app.handover_notes, {note['id']: note})
        self.assertTrue(app.handover_read_error)
        self.assertIn('1건', app.handover_status.get())

    def deliver(self, app):
        try: event = app.events.get(timeout=2)
        except queue.Empty: self.fail('drive refresh must deliver a background result')
        self.assertEqual(event[0], 'drive_refreshed')
        app.finish_drive_refresh(*event[1:])

    def test_poll_returns_without_waiting_for_drive_io_and_coalesces_repeats(self):
        app = host(self.module)
        (self.root / 'O1001').write_text('program')
        owner = threading.get_ident()
        entered = threading.Event(); release = threading.Event(); calls = []
        def slow_select():
            calls.append(threading.get_ident()); entered.set(); release.wait(.25)
            return self.root
        with patch.object(self.module, 'select_destination', side_effect=slow_select):
            start = time.monotonic()
            app.poll_destination()
            elapsed = time.monotonic() - start
            self.assertLess(elapsed, .1, 'drive IO blocked the UI poll')
            self.assertTrue(entered.wait(1))
            for _ in range(25): app.poll_destination()
            self.assertEqual(calls, [calls[0]])
            self.assertNotEqual(calls[0], owner)
            self.assertEqual(app.drive_item_paths, [])
            release.set(); self.deliver(app)
        self.assertEqual(app.drive_contents.items, ['O1001'])
        self.assertEqual(app.drive_item_paths, [self.root / 'O1001'])
        self.assertTrue(all(delay == 1000 for delay, _ in app.window.timers))

    def test_manual_refresh_discards_old_result_and_keeps_only_one_new_read(self):
        app = host(self.module)
        old = self.root / 'old'; new = self.root / 'new'; old.mkdir(); new.mkdir()
        (old / 'old-file').touch(); (new / 'new-file').touch()
        entered = threading.Event(); release = threading.Event(); calls = []
        def select():
            calls.append(threading.get_ident())
            if len(calls) == 1: entered.set(); release.wait(1); return old
            return new
        with patch.object(self.module, 'select_destination', side_effect=select):
            app.refresh_destination(); self.assertTrue(entered.wait(1))
            for _ in range(20): app.refresh_drive_manual()
            self.assertEqual(len(calls), 1)
            release.set(); self.deliver(app)
            self.assertEqual(app.drive_item_paths, [], 'stale drive must never appear')
            self.deliver(app)
        self.assertEqual(app.destination, new)
        self.assertEqual(app.drive_contents.items, ['new-file'])
        self.assertEqual(len(calls), 2)

    def test_busy_job_invalidates_read_and_idle_modifier_does_no_ui_thread_probe(self):
        app = host(self.module)
        (self.root / 'O1001').touch()
        entered = threading.Event(); release = threading.Event()
        def select(): entered.set(); release.wait(1); return self.root
        with patch.object(self.module, 'select_destination', side_effect=select):
            app.refresh_destination(); self.assertTrue(entered.wait(1))
            app.set_busy(True, 'file work')
            release.set(); self.deliver(app)
            self.assertEqual(app.drive_item_paths, [])
            self.assertTrue(app.busy)
            app.set_busy(False)
            app.poll_destination(); self.deliver(app)
        signature = app.drive_snapshot['modifier_signature']
        app.card_modifier_signature = signature
        with patch.object(self.module, 'card_modifier_signature', side_effect=AssertionError('Tk IO probe')):
            app.check_card_modifier()
        self.assertFalse(app.busy)
        self.assertEqual(app.drive_contents.items, ['O1001'])

    def test_read_error_keeps_cached_listing_and_actions_revalidate_destination(self):
        app = host(self.module)
        (self.root / 'O1001').touch()
        with patch.object(self.module, 'select_destination', return_value=self.root):
            app.refresh_destination(); self.deliver(app)
            app.card_modifier_signature = app.drive_snapshot['modifier_signature']
            with patch.object(self.module.os, 'scandir', side_effect=OSError('USB unavailable')):
                app.refresh_destination(); self.deliver(app)
        self.assertEqual(app.drive_item_paths, [self.root / 'O1001'])
        self.assertEqual(app.drive_contents.items, ['O1001'])
        self.assertIn('읽지 못', app.drive_contents_status.get())
        with patch.object(self.module, 'validate_fixed_destination', side_effect=self.module.WorkError('removed')):
            with self.assertRaises(self.module.WorkError): app.require_current_drive(self.root)

    def test_successful_read_after_failure_clears_error_even_when_files_are_unchanged(self):
        app = host(self.module)
        (self.root / 'O1001').touch()
        with patch.object(self.module, 'select_destination', return_value=self.root):
            app.refresh_destination(); self.deliver(app)
            with patch.object(self.module.os, 'scandir', side_effect=OSError('USB unavailable')):
                app.refresh_destination(); self.deliver(app)
            self.assertIn('읽지 못', app.drive_contents_status.get())
            app.refresh_destination(); self.deliver(app)
        self.assertIn('파일 1개', app.drive_contents_status.get())
        self.assertNotIn('읽지 못', app.drive_contents_status.get())

    def test_modifier_write_waits_for_idle_and_rechecks_the_observed_card(self):
        app = host(self.module)
        with patch.object(self.module, 'select_destination', return_value=self.root):
            app.refresh_destination(); self.deliver(app)
        self.assertFalse(app.busy)
        expected = app.drive_snapshot['modifier_signature']
        owners = []
        def sync(destination, expected_signature):
            owners.append(threading.get_ident())
            self.assertEqual(destination, self.root)
            self.assertEqual(expected_signature, expected)
            return {'added': False, 'removed': [], 'errors': [], 'signature': expected, 'retry': False}
        with patch.object(self.module, 'sync_card_modifier', side_effect=sync), \
             patch.object(self.module, 'card_modifier_signature', side_effect=AssertionError('Tk IO')):
            self.assertEqual(owners, [])
            app.window.idle.pop(0)()
            event = app.events.get(timeout=2)
        self.assertEqual(event[0], 'modifier_done')
        self.assertTrue(app.busy)
        self.assertNotEqual(owners, [threading.get_ident()])
        self.assertIsNone(event[3])

    def test_async_rename_refresh_selects_the_new_path(self):
        app = host(self.module)
        (self.root / 'O1001').touch()
        with patch.object(self.module, 'select_destination', return_value=self.root):
            app.refresh_destination(); self.deliver(app)
            (self.root / 'O1001').rename(self.root / 'O1002')
            app.drive_select_path = self.root / 'O1002'
            app.refresh_drive_contents(); self.deliver(app)
        self.assertEqual(app.drive_contents.items, ['O1002'])
        self.assertEqual(app.drive_contents.curselection(), (0,))

    def test_first_empty_click_waits_for_inflight_scan_and_runs_once_after_display(self):
        app = host(self.module)
        actions = []
        def empty(destination):
            self.assertIsNone(app.drive_action_pending, 'request must clear before executing')
            actions.append((destination, app.destination))
            return {'cleared_entries': 0}
        with patch.object(self.module, 'select_destination', return_value=self.root), \
             patch.object(self.module, 'empty_fixed_drive', side_effect=empty):
            app.refresh_destination()
            app.start_empty()
            self.assertEqual(app.alerts, [], 'an in-flight scan is not a missing disk')
            self.assertIsNotNone(app.drive_action_pending)
            self.assertEqual(actions, [])
            self.deliver(app)
            event = app.events.get(timeout=2)
            self.assertEqual(event[0], 'done')
            self.assertIsNone(event[3])
        self.assertEqual(actions, [(self.root, self.root)])
        self.assertIn(str(self.root), app.destination_text.get())
        self.assertIsNone(app.drive_action_pending)
        for _, callback in app.window.timers: callback()
        self.assertEqual(len(actions), 1)

    def test_deferred_import_replaces_pending_empty_and_runs_clicked_inputs(self):
        app = host(self.module)
        app.mode.set(self.module.MODE_LIST); app.number_input.text = 'O1001'
        imports = []; empty = []
        def batch(roots, destination, numbers, **kwargs):
            imports.append((roots, destination, numbers, kwargs['list_number']))
            return {}
        with patch.object(self.module, 'defer_ime_commit', return_value=False), \
             patch.object(self.module, 'select_destination', return_value=self.root), \
             patch.object(self.module, 'run_batch', side_effect=batch), \
             patch.object(self.module, 'empty_fixed_drive', side_effect=lambda path: empty.append(path)):
            app.refresh_destination(); app.start_empty(); app.start_import()
            self.assertEqual(app.alerts, [])
            self.assertIsNotNone(app.drive_action_pending)
            self.deliver(app)
            event = app.events.get(timeout=2)
            self.assertEqual(event[0], 'done'); self.assertIsNone(event[3])
        self.assertEqual(imports, [([], self.root, ['1001'], '3999')])
        self.assertEqual(empty, [])

    def test_editing_inputs_while_waiting_cancels_import_and_keeps_new_text(self):
        app = host(self.module)
        app.mode.set(self.module.MODE_LIST); app.number_input.text = 'O1001'
        calls = []
        with patch.object(self.module, 'defer_ime_commit', return_value=False), \
             patch.object(self.module, 'select_destination', return_value=self.root), \
             patch.object(self.module, 'run_batch', side_effect=lambda *a, **k: calls.append(a)):
            app.start_import()
            self.assertIsNotNone(app.drive_action_pending)
            app.number_input.text = 'O9999'; app.list_number.set('3998')
            self.deliver(app)
            self.assertIsNone(app.drive_action_pending)
            self.assertFalse(app.busy)
            self.assertEqual(calls, [])
            self.assertEqual(app.number_input.get('1.0', 'end'), 'O9999')
            self.assertEqual(app.list_number.get(), '3998')
            self.assertIn('입력', app.status.get())

    def test_expired_scan_cannot_trigger_delayed_empty_even_before_timeout_callback(self):
        app = host(self.module)
        actions = []
        with patch.object(self.module.time, 'monotonic', return_value=100.0) as clock, \
             patch.object(self.module, 'select_destination', return_value=self.root), \
             patch.object(self.module, 'empty_fixed_drive', side_effect=lambda path: actions.append(path)):
            app.start_empty()
            self.assertIsNotNone(app.drive_action_pending)
            delays = [delay for delay, _ in app.window.timers if delay > 0]
            self.assertEqual(len(delays), 1); self.assertLessEqual(delays[0], 3000)
            clock.return_value = 103.01
            self.deliver(app)
            self.assertIsNone(app.drive_action_pending)
            self.assertFalse(app.busy)
            self.assertEqual(actions, [])
            self.assertIn('다시', app.status.get())

    def test_changed_program_root_cancels_deferred_import(self):
        app = host(self.module)
        app.mode.set(self.module.MODE_LIST); app.number_input.text = 'O1001'
        calls = []
        with patch.object(self.module, 'defer_ime_commit', return_value=False), \
             patch.object(self.module, 'select_destination', return_value=self.root), \
             patch.object(self.module, 'run_batch', side_effect=lambda *a, **k: calls.append(a)):
            app.start_import()
            app.program_base_root = 'another source'
            self.deliver(app)
            self.assertFalse(calls); self.assertFalse(app.busy)
            self.assertEqual(app.number_input.text, 'O1001')

    def test_path_dialog_cancels_pending_empty_before_opening(self):
        app = host(self.module)
        app.program_path_dialog = SimpleNamespace(winfo_exists=lambda: True,lift=lambda:None,focus_set=lambda:None)
        with patch.object(self.module, 'select_destination', return_value=self.root):
            app.start_empty(); ready = app.events.get(timeout=2)
            app.configure_program_path()
            self.assertIsNone(app.drive_action_pending)
            app.finish_drive_refresh(*ready[1:])
            self.assertFalse(app.busy);self.assertTrue(app.events.empty())

    def test_timeout_clears_request_while_the_single_reader_is_still_pending(self):
        app = host(self.module)
        with patch.object(self.module.time, 'monotonic', return_value=100.0) as clock, \
             patch.object(self.module, 'select_destination', return_value=self.root):
            app.start_empty()
            self.assertIsNotNone(app.drive_action_pending)
            timer = next(callback for delay, callback in app.window.timers if delay > 0)
            clock.return_value = 103.0; timer()
            self.assertIsNone(app.drive_action_pending)
            self.assertTrue(app.drive_refresh_loading)
            self.deliver(app)
            self.assertFalse(app.busy)
            self.assertTrue(app.events.empty())

    def test_manual_refresh_job_and_close_invalidate_pending_destructive_action(self):
        for action in ('manual', 'job', 'close', 'tray', 'exit'):
            with self.subTest(action=action):
                app = host(self.module); calls = []
                with patch.object(self.module, 'select_destination', return_value=self.root), \
                     patch.object(self.module, 'empty_fixed_drive', side_effect=lambda path: calls.append(path)):
                    app.start_empty()
                    self.assertIsNotNone(app.drive_action_pending)
                    ready = app.events.get(timeout=2)
                    self.assertEqual(ready[0], 'drive_refreshed')
                    if action == 'manual': app.refresh_drive_manual()
                    elif action == 'job': app.start_job('other', lambda: None)
                    elif action == 'tray':
                        app._suite_tray = SimpleNamespace(available=True); app._hide_to_tray()
                    else:
                        with patch.object(self.module, 'defer_ime_commit', return_value=True):
                            (app.close if action == 'close' else app.request_complete_exit)()
                    self.assertIsNone(app.drive_action_pending)
                    app.finish_drive_refresh(*ready[1:])
                    if action == 'manual': self.deliver(app)
                    self.assertEqual(calls, [])

    def test_intervening_file_action_cancels_empty_before_its_dialog_or_validation(self):
        for action in ('add_dialog', 'add', 'delete', 'open', 'rename', 'drop'):
            with self.subTest(action=action):
                app = host(self.module)
                with patch.object(self.module, 'select_destination', return_value=self.root):
                    app.start_empty()
                    ready = app.events.get(timeout=2)
                    self.assertIsNotNone(app.drive_action_pending)
                    if action == 'add_dialog': app.choose_drive_files()
                    elif action == 'add': app.start_drive_add([self.root / 'sample'])
                    elif action == 'delete': app.start_drive_delete()
                    elif action == 'open': app.open_drive_item()
                    elif action == 'rename': app.start_rename()
                    elif action == 'drop': app.receive_drive_drop([self.root / 'sample'], None, False)
                    self.assertIsNone(app.drive_action_pending)
                    app.finish_drive_refresh(*ready[1:])
                    self.assertFalse(app.busy)
                    self.assertTrue(app.events.empty())

    def test_confirmed_missing_drive_cancels_wait_without_starting_empty(self):
        app = host(self.module)
        with patch.object(self.module, 'select_destination', side_effect=self.module.WorkError('missing')):
            app.start_empty()
            self.assertEqual(app.alerts, [])
            self.deliver(app)
        self.assertIsNone(app.drive_action_pending)
        self.assertFalse(app.busy)
        self.assertEqual(len(app.alerts), 1)
        self.assertIn('F:', app.alerts[0][1])

    def test_one_refresh_reuses_directory_entries_for_modifier_signature(self):
        app = host(self.module)
        (self.root / self.module.CARD_MODIFIER_FILENAME).write_bytes(b'existing script')
        (self.root / 'O1001').touch()
        original_scan = os.scandir
        scans = []
        def scan(path):
            scans.append(path)
            return original_scan(path)
        with patch.object(self.module, 'select_destination', return_value=self.root), \
             patch.object(self.module.os, 'scandir', side_effect=scan):
            app.refresh_destination(); self.deliver(app)
        self.assertEqual(len(scans), 1, 'one refresh must not enumerate the same card twice')
        self.assertEqual(app.drive_snapshot['modifier_signature'], self.module.card_modifier_signature(self.root))

    def test_slow_signature_probe_runs_on_worker_and_never_starts_write_while_washing(self):
        app = host(self.module)
        entered = threading.Event(); release = threading.Event(); owners = []
        original_signature = self.module.card_modifier_signature
        def signature(path, names=None):
            owners.append(threading.get_ident()); entered.set(); release.wait(.25)
            return original_signature(path, names=names)
        with patch.object(self.module, 'select_destination', return_value=self.root), \
             patch.object(self.module, 'card_modifier_signature', side_effect=signature):
            start = time.monotonic(); app.refresh_destination()
            self.assertLess(time.monotonic() - start, .1)
            self.assertTrue(entered.wait(1))
            app.wash_app.busy = True
            release.set(); self.deliver(app)
        self.assertNotEqual(owners, [threading.get_ident()])
        self.assertEqual(app.drive_item_paths, [])
        with patch.object(self.module, 'sync_card_modifier', side_effect=AssertionError('unsafe write')):
            app.check_card_modifier()
        self.assertFalse(app.busy)


if __name__ == '__main__': unittest.main()
