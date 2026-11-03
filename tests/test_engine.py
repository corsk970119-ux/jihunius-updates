import hashlib, importlib.util, json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('update_engine', HERE.parent/'src/update_engine.py')
e = importlib.util.module_from_spec(spec); spec.loader.exec_module(e)

def descriptor(data, version='2026.11.03.3'):
    return {'version': version, 'path': 'releases/jihunius/'+version+'/app.pyw',
            'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'min_python': [3,8], 'update_protocol': 1, 'notes': '새 기능 안내'}

class EngineTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(hasattr(e, 'Store'), '검증된 버전 보관 및 명시적 적용 엔진이 필요합니다')
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.base = self.root/'original'/'지후니우스.pyw'; self.base.parent.mkdir()
        self.base.write_bytes(b"print('baseline')\n")
        self.store = e.Store(self.root/'cache', self.base, '2026.11.03.2')
        self.current = self.store.prepare()
        self.new_data = b"print('new')\n"
        self.offered = descriptor(self.new_data)

    def test_preparing_local_version_preserves_user_data_and_needs_no_network(self):
        settings=self.base.parent/'settings.json'; settings.write_text('keep')
        self.assertEqual(self.current['version'],'2026.11.03.2')
        self.assertEqual(self.store.path(self.current).read_bytes(),self.base.read_bytes())
        self.assertEqual(settings.read_text(),'keep')

    def test_check_only_reports_new_version_without_downloading_or_applying(self):
        calls=[]
        def fetch(path, maximum, seconds):
            calls.append(path)
            return json.dumps({'schema':1,'apps':{'jihunius':self.offered}}).encode()
        result=e.check_offer(self.current, fetch)
        self.assertEqual(result['kind'],'available')
        self.assertEqual(calls,['channels/stable.json'])
        self.assertEqual(self.store.state()['current'],self.current)

    def test_staging_does_not_switch_current_version(self):
        self.store.stage(self.offered, self.new_data)
        self.assertEqual(self.store.state()['current'],self.current)
        self.assertEqual(self.store.path(self.offered).read_bytes(),self.new_data)

    def test_corrupt_download_cannot_replace_current_or_create_staged_code(self):
        with self.assertRaises(e.UpdateError): self.store.stage(self.offered,b'bad')
        self.assertEqual(self.store.state()['current'],self.current)
        self.assertFalse(self.store.path(self.offered).exists())

    def test_same_version_mutation_and_downgrade_are_not_offered(self):
        for version in ['2026.11.03.1','2026.11.03.2']:
            value=descriptor(self.new_data,version)
            def fetch(*args):return json.dumps({'schema':1,'apps':{'jihunius':value}}).encode()
            if version.endswith('.2'):
                with self.assertRaises(e.UpdateError):e.check_offer(self.current,fetch)
            else:self.assertEqual(e.check_offer(self.current,fetch)['kind'],'current')

    def test_unsafe_paths_and_missing_protocol_are_rejected(self):
        for changes in [{'path':'../../app.pyw'},{'update_protocol':None},{'min_python':[99,1]}]:
            value=dict(self.offered,**changes)
            with self.assertRaises(e.UpdateError):self.store.stage(value,self.new_data)

    def test_bad_syntax_never_becomes_staged_version(self):
        data=b'if:'
        with self.assertRaises(e.UpdateError):self.store.stage(descriptor(data),data)

    def test_commit_requires_successful_exit_and_matching_session(self):
        self.store.stage(self.offered,self.new_data)
        self.store.request(self.offered,'session-a')
        self.assertFalse(self.store.consume_request('session-a',1))
        self.assertEqual(self.store.state()['current'],self.current)
        self.store.request(self.offered,'session-a')
        self.assertFalse(self.store.consume_request('session-b',0))
        self.store.request(self.offered,'session-c')
        self.assertTrue(self.store.consume_request('session-c',0))
        self.assertEqual(self.store.state()['current']['sha256'],self.offered['sha256'])
        self.assertEqual(self.store.state()['previous'],self.current)

    def test_failed_start_restores_previous_and_rejects_bad_release(self):
        self.store.stage(self.offered,self.new_data)
        self.store.request(self.offered,'a');self.store.consume_request('a',0)
        self.assertTrue(self.store.restore_failed(self.offered))
        state=self.store.state()
        self.assertEqual(state['current'],self.current)
        self.assertEqual(state['rejected_sha'],self.offered['sha256'])
        self.assertEqual(self.store.prepare(),self.current)

    def test_deleted_current_cache_falls_back_to_previous(self):
        self.store.stage(self.offered,self.new_data)
        self.store.request(self.offered,'a');self.store.consume_request('a',0)
        self.store.path(self.offered).unlink()
        self.assertEqual(self.store.prepare(),self.current)

    def test_lock_does_not_allow_two_update_owners(self):
        a=e.FileLock(self.root/'lock');b=e.FileLock(self.root/'lock')
        self.assertTrue(a.acquire())
        try:self.assertFalse(b.acquire())
        finally:a.release()
        self.assertTrue(b.acquire());b.release()

    def test_orphan_child_lease_blocks_another_launcher_before_cache_changes(self):
        from unittest.mock import Mock
        lock=e.FileLock(e.root_for(self.base)/'active-app.lock')
        self.assertTrue(lock.acquire())
        try:
            with patch.object(e.Store,'prepare') as prepare, patch.object(e,'show_message'):
                self.assertEqual(e.launch(self.base,'2026.11.03.2'),0)
                prepare.assert_not_called()
        finally:lock.release()

    def test_native_modal_and_unknown_state_prevent_shutdown(self):
        from unittest.mock import Mock
        window=Mock();window.grab_current.return_value=object()
        self.assertTrue(e.native_dialog_open(window))
        window.grab_current.side_effect=RuntimeError('window unavailable')
        self.assertTrue(e.native_dialog_open(window))

    def test_supervisor_liveness_check(self):
        self.assertTrue(e.process_alive(os.getpid()))
        self.assertFalse(e.process_alive(None))
        self.assertFalse(e.process_alive(-1))

if __name__=='__main__':unittest.main()
