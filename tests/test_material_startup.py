import errno,json,os,sys,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import material_ui as ui


class StartupTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)/'MaterialCounter';self.folder.mkdir()
        self.session_folder=Path(self.tmp.name)/'JihuniusSuite/companions/control'/('a'*32)
        self.session_folder.mkdir(parents=True);self.nonce='b'*32
        self.root=Mock();self.lock=Mock();self.session=Mock();self.app=Mock()
        self.error=Mock();self.constructor=Mock(return_value=self.session)
        self.patches=[patch.dict(os.environ,JIHUNIUS_UPDATE_SESSION=str(self.session_folder),JIHUNIUS_UPDATE_NONCE=self.nonce),
            patch.object(ui.core,'default_folder',return_value=self.folder),patch('tkinter.Tk',return_value=self.root),
            patch('tkinter.messagebox.showerror',self.error),patch.object(ui,'ClientSession',self.constructor),
            patch.object(ui,'SyncedApplication',return_value=self.app),
            patch.object(ui.core,'_CuExistingProcess',return_value=Mock(pid=42,started='12345'),create=True)]
        for p in self.patches:p.start();self.addCleanup(p.stop)

    def test_duplicate_boot_hands_control_back_without_second_session_or_raw_dialog(self):
        registry=self.folder/'ui-instance.json'
        original=dict(pid=42,started='12345',nonce='c'*32,session='existing',at=time.time())
        registry.write_text(json.dumps(original));before=registry.read_bytes()
        with patch.object(ui.core,'InstanceLock',side_effect=ui.core.InstanceAlreadyRunning('sync-ui.lock')):
            with self.assertRaises(SystemExit) as result:ui.boot()
        self.assertEqual(result.exception.code,73)
        self.assertFalse(self.error.called);self.assertFalse(self.constructor.called)
        self.assertEqual(registry.read_bytes(),before);self.root.destroy.assert_called_once()

    def test_successful_boot_publishes_current_control_session_then_cleans_only_itself(self):
        seen=[]
        self.root.mainloop.side_effect=lambda:seen.append(json.loads((self.folder/'ui-instance.json').read_text()))
        with patch.object(ui.core,'InstanceLock',return_value=self.lock):ui.boot()
        self.assertEqual(seen[0]['nonce'],self.nonce);self.assertEqual(seen[0]['session'],str(self.session_folder))
        self.assertFalse((self.folder/'ui-instance.json').exists());self.assertFalse(self.error.called)
        self.lock.close.assert_called_once();self.session.close.assert_called_once()

    def test_real_permission_error_names_failing_stage_and_path(self):
        error=PermissionError(errno.EACCES,'Permission denied','C:/blocked/sync-ui.lock')
        with patch.object(ui.core,'InstanceLock',side_effect=error):ui.boot()
        self.assertEqual(self.error.call_count,1)
        message=self.error.call_args.args[1]
        self.assertIn('실행 잠금',message);self.assertIn('C:/blocked/sync-ui.lock',message)
        self.assertFalse(self.constructor.called)

    def test_stale_registry_does_not_end_concurrent_startup_grace_period(self):
        registry=self.folder/'ui-instance.json'
        registry.write_text(json.dumps(dict(pid=999999,started='dead',at=0)))
        clock=[0.0]
        def sleep(seconds):clock[0]+=seconds
        with patch.object(ui.core,'InstanceLock',side_effect=ui.core.InstanceAlreadyRunning('sync-ui.lock')), \
             patch.object(ui.core,'_CuExistingProcess',side_effect=OSError('process gone')) as process, \
             patch.object(ui.time,'monotonic',side_effect=lambda:clock[0]),patch.object(ui.time,'sleep',side_effect=sleep):
            with self.assertRaises(SystemExit):ui.boot()
        self.assertGreaterEqual(clock[0],2)
        self.assertGreater(process.call_count,1)
        self.assertFalse(self.error.called)

    def test_cleanup_does_not_remove_another_session_registry(self):
        def mainloop():
            p=self.folder/'ui-instance.json';record=json.loads(p.read_text());record['nonce']='c'*32;p.write_text(json.dumps(record))
        self.root.mainloop.side_effect=mainloop
        with patch.object(ui.core,'InstanceLock',return_value=self.lock):ui.boot()
        self.assertEqual(json.loads((self.folder/'ui-instance.json').read_text())['nonce'],'c'*32)


if __name__=='__main__':unittest.main()
