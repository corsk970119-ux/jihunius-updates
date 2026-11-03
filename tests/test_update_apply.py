import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from test_update_notice import Scheduler

spec=importlib.util.spec_from_file_location('apply_ui',Path(__file__).resolve().parents[1]/'src/update_ui.py')
u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)


class UpdateApplyTests(unittest.TestCase):
    def setUp(self):
        self.root=Scheduler();self.root.winfo_children=lambda:[]
        self.children=Mock();self.children.running_keys.return_value=[]
        self.app=SimpleNamespace(window=self.root,tk=SimpleNamespace(StringVar=Mock(),TclError=RuntimeError),
            ttk=SimpleNamespace(Button=Mock()),title_label=SimpleNamespace(master=None),restore_from_tray=Mock(),
            request_complete_exit=Mock(),_suite_stopped=False,_suite_children=self.children,
            number_input=Mock(),wash_app=SimpleNamespace(busy=False,stop=Mock()))
        self.app.number_input.get.return_value=''
        def finish():self.app._suite_stopped=True
        self.app._finish_suite_shutdown=finish
        context={'current':{'version':'2026.11.03.6'},'root':'unused','origin':'unused',
                 'base_version':'2026.11.03.6','nonce':'abc','supervisor_pid':123}
        with patch.object(u,'Store',create=True):self.c=u.Controller(self.app,context,'2026.11.03.6')
        self.c.dialog=Mock();self.c.offered={'version':'2026.11.03.7','sha256':'a'*64}
        self.c.staged=dict(self.c.offered);self.c.open=Mock();self.c.refresh=Mock()
        alive=patch.object(u,'process_alive',return_value=True,create=True)
        alive.start();self.addCleanup(alive.stop)

    def test_only_saved_and_exited_children_allow_request_and_shutdown(self):
        self.children.poll_update_save.side_effect=[False,True]
        self.c.apply()
        self.children.begin_update_save.assert_called_once()
        self.root.advance(.1)
        self.assertFalse(self.app._suite_stopped);self.c.store.request.assert_not_called()
        self.root.advance(.1)
        self.assertTrue(self.app._suite_stopped)
        self.c.store.request.assert_called_once()
        self.assertFalse(self.root.jobs)

    def test_save_error_keeps_host_and_cancels_other_children(self):
        self.children.poll_update_save.side_effect=RuntimeError('save failed')
        self.c.apply();self.root.advance(.1)
        self.assertFalse(self.app._suite_stopped);self.assertFalse(self.c.applying)
        self.c.store.request.assert_not_called();self.children.cancel_update_save.assert_called_once()
        self.c.dialog.grab_release.assert_called_once()

    def test_business_work_starting_during_save_prevents_update_without_stopping_it(self):
        self.c.apply();self.app.wash_app.busy=True;self.root.advance(.1)
        self.assertFalse(self.c.applying);self.assertFalse(self.app._suite_stopped)
        self.app.wash_app.stop.assert_not_called();self.c.store.request.assert_not_called()

    def test_user_cancel_and_tray_exit_do_not_bypass_save_ack(self):
        self.c.apply();self.app.request_complete_exit()
        self.c._exit.assert_not_called();self.assertTrue(self.c.applying)
        self.c.close_dialog()
        self.assertFalse(self.c.applying);self.assertFalse(self.app._suite_stopped)
        self.c.store.request.assert_not_called()

    def test_closing_dialog_during_download_cancels_late_restart(self):
        self.c.staged=None;self.c.task=Mock(return_value=True)
        self.c.apply()
        self.assertTrue(self.c._download_apply)
        self.c.close_dialog()
        self.c.events.put(('download',True,dict(self.c.offered)))
        self.c.poll()
        self.assertIsNotNone(self.c.staged)
        self.assertFalse(self.c.applying);self.assertFalse(self.app._suite_stopped)
        self.children.begin_update_save.assert_not_called();self.c.store.request.assert_not_called()


if __name__=='__main__':unittest.main()
