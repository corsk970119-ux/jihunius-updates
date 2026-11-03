"""Update checks repeat without user input and retain an available-version notice."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location('notice_ui', Path(__file__).resolve().parents[1]/'src/update_ui.py')
u = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(u)


class Scheduler:
    def __init__(self):
        self.now = 0
        self.next_id = 0
        self.jobs = {}

    def after(self, milliseconds, callback):
        self.next_id += 1
        self.jobs[self.next_id] = (self.now + milliseconds/1000, callback)
        return self.next_id

    def after_cancel(self, key):
        self.jobs.pop(key, None)

    def advance(self, seconds):
        target = self.now + seconds
        while self.jobs:
            key = min(self.jobs, key=lambda k: self.jobs[k][0])
            when, callback = self.jobs[key]
            if when > target:
                break
            del self.jobs[key]
            self.now = when
            callback()
        self.now = target


class UpdateNoticeTests(unittest.TestCase):
    def setUp(self):
        self.root = Scheduler()
        self.button = Mock()
        self.label = Mock()
        self.app = SimpleNamespace(window=self.root, tk=SimpleNamespace(StringVar=Mock(return_value=self.label), TclError=RuntimeError),
            ttk=SimpleNamespace(Button=Mock(return_value=self.button)), title_label=SimpleNamespace(master=None),
            restore_from_tray=Mock(), request_complete_exit=Mock(), _suite_stopped=False)
        def finish():
            self.app._suite_stopped = True
        self.app._finish_suite_shutdown = finish
        self.context = {'current':{'version':'2026.11.03.4'},'root':'unused','origin':'unused','base_version':'2026.11.03.4'}
        self.clock = patch.object(u.time, 'monotonic', side_effect=lambda:self.root.now)
        self.clock.start(); self.addCleanup(self.clock.stop)
        with patch.object(u, 'Store', create=True):
            self.c = u.Controller(self.app, self.context, '2026.11.03.4')
        self.requests = []
        def task(kind, action):
            self.requests.append(kind)
            self.c.busy = True
            self.c.refresh()
            return True
        self.c.task = task
        self.c.apply = Mock()

    def result(self, ok=True, value=None):
        self.c.events.put(('check', ok, {'kind':'current'} if value is None else value))
        self.c.poll()

    def test_startup_and_repeated_checks_need_no_click_or_restore(self):
        self.root.advance(.5)
        self.assertEqual(self.requests, ['check'])
        self.result()
        self.root.advance(60)
        self.assertEqual(self.requests, ['check','check'])
        self.result()
        self.root.advance(60)
        self.assertEqual(self.requests, ['check','check','check'])
        self.c.apply.assert_not_called()

    def test_connection_failure_retries_automatically(self):
        self.root.advance(.5)
        self.result(False, 'offline')
        self.root.advance(60)
        self.assertEqual(self.requests, ['check','check'])

    def test_failed_check_is_visible_without_opening_dialog(self):
        self.root.advance(.5)
        self.result(False, 'GitHub에 연결하지 못했습니다.')
        self.assertIn('실패', self.label.set.call_args.args[0])
        self.assertIn('GitHub', self.c.message)
        self.assertIsNone(self.c.dialog)
        self.assertIsNone(self.c.offered)
        self.assertEqual(self.button.configure.call_args.kwargs['style'], 'Popup.TButton')

    def test_missing_context_explains_disabled_automatic_checks(self):
        self.root.jobs.clear()
        self.c = u.Controller(self.app, None, '2026.11.03.4')
        self.assertFalse(self.root.jobs)
        self.assertFalse(self.c.check(force=True))
        self.assertIn('꺼짐', self.app.tk.StringVar.call_args.kwargs['value'])
        self.assertIn('완전 종료', self.c.message)
        self.assertIn('다시 실행', self.c.message)

    def test_dialog_shows_current_version_and_last_completed_check_result(self):
        self.c.dialog = Mock()
        self.c.versions = Mock(); self.c.status = Mock(); self.c.notes = Mock()
        self.c.check_button = Mock(); self.c.apply_button = Mock()
        self.root.advance(.5)
        with patch.object(u.time, 'strftime', return_value='11-03 14:25:30'):
            self.result()
        text = self.c.versions.set.call_args.args[0]
        self.assertIn('2026.11.03.4', text)
        self.assertIn('11-03 14:25:30', text)
        self.assertIn('성공', text)
        self.root.advance(60)
        with patch.object(u.time, 'strftime', return_value='11-03 14:26:30'):
            self.result(False, 'offline')
        text = self.c.versions.set.call_args.args[0]
        self.assertIn('11-03 14:26:30', text)
        self.assertIn('실패', text)
        self.assertEqual(self.c.status.set.call_args.args[0], 'offline')

    def test_download_does_not_change_last_check_time_or_result(self):
        self.c.dialog = Mock()
        self.c.versions = Mock(); self.c.status = Mock(); self.c.notes = Mock()
        self.c.check_button = Mock(); self.c.apply_button = Mock()
        self.root.advance(.5)
        with patch.object(u.time, 'strftime', return_value='11-03 14:25:30'):
            self.result(value={'kind':'available','offered':{'version':'2026.11.03.5'}})
        self.c.events.put(('download', False, 'download failed'))
        self.c.poll()
        self.assertIn('11-03 14:25:30', self.c.versions.set.call_args.args[0])
        self.assertIn('성공', self.c.versions.set.call_args.args[0])
        self.assertEqual(self.label.set.call_args.args[0], '새 버전 있음')

    def test_available_notice_is_yellow_and_survives_recheck_and_error(self):
        self.root.advance(.5)
        self.result(value={'kind':'available','offered':{'version':'2026.11.03.5'}})
        self.assertEqual(self.button.configure.call_args.kwargs['style'], 'HandoverNotice.TButton')
        self.root.advance(60)
        self.assertEqual(self.label.set.call_args.args[0], '새 버전 있음')
        self.result(False, 'offline')
        self.assertEqual(self.button.configure.call_args.kwargs['style'], 'HandoverNotice.TButton')
        self.c.apply.assert_not_called()

    def test_current_or_rejected_result_clears_notice(self):
        for kind in ('current','rejected'):
            self.button.configure.reset_mock()
            self.c.offered = {'version':'2026.11.03.5'}
            self.result(value={'kind':kind})
            self.assertIsNone(self.c.offered)
            self.assertEqual(self.button.configure.call_args.kwargs['style'], 'Popup.TButton')

    def test_busy_check_is_not_duplicated_and_shutdown_cancels_future_checks(self):
        self.root.advance(.5)
        self.root.advance(60)
        self.c.check(force=True)
        self.assertEqual(self.requests, ['check'])
        self.result()
        self.root.advance(60)
        self.assertEqual(self.requests, ['check','check'])
        self.result()
        self.app._finish_suite_shutdown()
        self.assertFalse(self.root.jobs)
        self.root.advance(180)
        self.assertEqual(self.requests, ['check','check'])

    def test_manual_check_and_restore_leave_one_automatic_timer(self):
        self.root.advance(.5); self.result()
        self.root.advance(10)
        self.c.check(force=True); self.result()
        self.app.restore_from_tray()
        self.assertEqual(self.requests, ['check','check'])
        self.assertEqual(len(self.root.jobs), 1)
        self.root.advance(60)
        self.assertEqual(self.requests, ['check','check','check'])


if __name__ == '__main__':
    unittest.main()
