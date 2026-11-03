import importlib.util, pathlib, unittest
from types import SimpleNamespace
from unittest.mock import Mock

path=pathlib.Path(__file__).resolve().parents[1]/'src/update_ui.py'

class HostTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(path.exists(),'작업 상태를 읽기만 하는 업데이트 UI가 필요합니다')
        spec=importlib.util.spec_from_file_location('host_ui',path)
        self.u=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.u)
        self.app=SimpleNamespace(busy=False,card_modifier_pending=False,handover_writing=False,handover_dialog=None,
            wash_app=SimpleNamespace(busy=False,stop=Mock()),stl_app=SimpleNamespace(busy=False),
            _suite_children=SimpleNamespace(running_keys=lambda:[]),_suite_exit_pending=False,
            number_input=Mock(),window=Mock(),_suite_stopped=False)
        self.app.number_input.get.return_value='';self.app.window.winfo_children.return_value=[]

    def test_wash_busy_check_never_signals_stop(self):
        self.app.wash_app.busy=True
        self.assertIn('세척',self.u.block_reason(self.app))
        self.app.wash_app.stop.set.assert_not_called()

    def test_open_companion_prevents_update_without_sending_close(self):
        self.app._suite_children.running_keys=lambda:['wash-log']
        self.assertIn('보조창',self.u.block_reason(self.app))

    def test_copy_pending_handover_and_search_work_prevent_exit(self):
        for target,attribute in [(self.app,'busy'),(self.app,'card_modifier_pending'),(self.app,'handover_writing'),(self.app.stl_app,'busy')]:
            setattr(target,attribute,True)
            self.assertTrue(self.u.block_reason(self.app))
            setattr(target,attribute,False)
        self.assertEqual(self.u.block_reason(self.app),'')

    def test_incomplete_program_input_is_not_lost_during_update(self):
        self.app.number_input.get.return_value='O1004'
        self.assertIn('입력',self.u.block_reason(self.app))

if __name__=='__main__':unittest.main()
