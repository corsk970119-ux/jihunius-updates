"""Repeated companion buttons request the original save/close flow, never kill."""
import hashlib
import os
import tempfile
import unittest
from unittest.mock import Mock, patch
from test_companion_save import module


class CompanionToggleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        env=patch.dict(os.environ,LOCALAPPDATA=self.tmp.name);env.start();self.addCleanup(env.stop)
        data=b'# child\n'
        payloads={key:{'data':data,'sha256':hashlib.sha256(data).hexdigest(),'title':key}
                  for key in ('protrusion','wash-log')}
        self.backend=Mock();self.spawned=[]
        def spawn(*args,**kwargs):
            p=Mock(pid=100+len(self.spawned));p.poll.return_value=None
            self.spawned.append(p);return p
        self.manager=module.CompanionManager(payloads,self.tmp.name,_backend=self.backend,_popen=spawn)

    def test_second_press_closes_owned_window_without_starting_another(self):
        self.assertTrue(self.manager.toggle('wash-log'))
        self.assertFalse(self.manager.toggle('wash-log'))
        self.backend.close.assert_called_once_with(100,'wash-log')
        self.backend.focus.assert_called_once_with(100,'wash-log')
        self.assertEqual(len(self.spawned),1)
        self.assertEqual(self.manager.running_keys(),['wash-log'])
        self.spawned[0].terminate.assert_not_called();self.spawned[0].kill.assert_not_called()

    def test_repeated_clicks_do_not_send_multiple_discard_prompts_while_closing(self):
        with patch.object(module.time,'monotonic',return_value=10):
            self.manager.toggle('protrusion')
            for _ in range(4):self.manager.toggle('protrusion')
        self.backend.close.assert_called_once()

    def test_cancelled_close_remains_open_and_can_be_requested_again(self):
        self.manager.toggle('wash-log')
        with patch.object(module.time,'monotonic',return_value=10):self.manager.toggle('wash-log')
        with patch.object(module.time,'monotonic',return_value=13):self.manager.toggle('wash-log')
        self.assertEqual(self.backend.close.call_count,2)
        self.assertEqual(len(self.spawned),1)

    def test_after_normal_exit_next_press_reopens(self):
        self.manager.toggle('protrusion');self.manager.toggle('protrusion')
        self.spawned[0].poll.return_value=0
        self.assertTrue(self.manager.toggle('protrusion'))
        self.assertEqual(len(self.spawned),2)

    def test_modal_or_not_ready_failure_preserves_process_and_allows_retry(self):
        self.manager.toggle('wash-log');self.backend.close.side_effect=RuntimeError('modal open')
        with self.assertRaises(RuntimeError):self.manager.toggle('wash-log')
        self.backend.close.side_effect=None
        self.manager.toggle('wash-log')
        self.assertEqual(self.backend.close.call_count,2)
        self.spawned[0].kill.assert_not_called()

    def test_update_save_cannot_be_interrupted_by_companion_toggle(self):
        self.manager.toggle('protrusion');self.manager.begin_update_save()
        with self.assertRaises(RuntimeError):self.manager.toggle('protrusion')
        self.backend.close.assert_not_called()


if __name__=='__main__':unittest.main()
