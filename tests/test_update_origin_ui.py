import unittest
from unittest.mock import patch, Mock
import test_update_apply as fixtures
u=fixtures.u

class OriginUITests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.UpdateApplyTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.c=self.fixture.c;self.root=self.fixture.root
    def test_origin_failure_keeps_local_version_and_visible_yellow_status(self):
        self.c.refresh=u.Controller.refresh.__get__(self.c)
        self.c.offered=None;self.c.dialog=None
        self.c.events.put(('origin',True,{'kind':'failed','message':'원본 교체 보류'}));self.c.poll()
        self.assertEqual(self.c.origin_result['kind'],'failed')
        self.c.button.configure.assert_called_with(style='HandoverNotice.TButton')
        self.c.label.set.assert_called_with('원본 교체 확인')
        self.assertFalse(self.fixture.app._suite_stopped)
    def test_only_first_completed_check_attempts_sync_until_manual_retry(self):
        self.c.task=Mock(return_value=True)
        with patch.object(u,'sync_origin_bounded',return_value={'kind':'current'},create=True):
            for _ in range(2):
                self.c.events.put(('check',True,{'kind':'current'}));self.c.poll()
            self.assertEqual([x.args[0] for x in self.c.task.call_args_list],['origin'])
            self.c.check(force=True)
            self.c.events.put(('check',True,{'kind':'current'}));self.c.poll()
            self.assertEqual([x.args[0] for x in self.c.task.call_args_list],['origin','check','origin'])
    def test_downloading_or_applying_does_not_start_original_copy(self):
        self.c.task=Mock(return_value=True)
        with patch.object(u,'sync_origin_bounded',create=True):
            self.c.applying=True;self.c.sync_origin()
            self.c.applying=False;self.c.busy=True;self.c.sync_origin()
        self.c.task.assert_not_called();self.assertFalse(self.c.origin_checked)

if __name__=='__main__':unittest.main()
