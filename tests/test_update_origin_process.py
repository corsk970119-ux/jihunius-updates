import os, json, tempfile, unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from test_update_origin import e, ROOT, item, source

class OriginProcessTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.env=patch.dict(os.environ,LOCALAPPDATA=self.tmp.name);self.env.start();self.addCleanup(self.env.stop)
        self.origin=Path(self.tmp.name)/'공유'/'지후니우스.pyw';self.origin.parent.mkdir()
        self.old=source('2026.11.09.2');self.origin.write_bytes(self.old)
        self.store=e.Store(e.root_for(self.origin),self.origin,'2026.11.09.2');self.store.prepare()
        helper='\n'.join((ROOT/'src'/p).read_text() for p in ('update_engine.py','update_origin.py','update_ui.py'))
        self.new=source('2026.11.09.3')+('SuiteUpdater = load("updater", '+repr(helper)+')\n').encode()
        self.candidate=item(self.new,'2026.11.09.3')
        self.store.stage(self.candidate,self.new);self.nonce='a'*32
        self.store.request(self.candidate,self.nonce);self.store.consume_request(self.nonce,0)
        self.context=dict(root=self.store.root,origin=str(self.origin),nonce=self.nonce,current=self.candidate)
        e.write_json(self.store.root/'session.json',dict(nonce=self.nonce,current=self.candidate,pid=os.getpid()))
        e.write_json(self.store.root/'ready.json',dict(nonce=self.nonce))
    def test_real_child_updates_original_after_old_launcher_applies_new_cached_version(self):
        settings=Path(self.tmp.name)/'Jihunius'/'program_year.json';settings.parent.mkdir();settings.write_text('2027')
        result=e.sync_origin_bounded(self.context)
        self.assertEqual(result['kind'],'updated',result)
        self.assertEqual(self.origin.read_bytes(),self.new);self.assertEqual(settings.read_text(),'2027')
        # Another PC starts the same original: its fresh local Store selects .3.
        other=e.Store(Path(self.tmp.name)/'second-pc',self.origin,'2026.11.09.3')
        self.assertEqual(other.prepare()['sha256'],self.candidate['sha256'])
    def test_unready_or_stale_session_never_replaces_origin(self):
        for nonce in ('', 'b'*32):
            with self.subTest(nonce=nonce):
                e.write_json(self.store.root/'ready.json',dict(nonce=nonce))
                self.assertEqual(e.sync_origin_bounded(self.context)['kind'],'failed')
                self.assertEqual(self.origin.read_bytes(),self.old)
    def test_downloaded_but_unapplied_version_never_replaces_origin(self):
        state=self.store.state();state['current']=state['base'];self.store.save(state)
        self.assertEqual(e.sync_origin_bounded(self.context)['kind'],'failed')
        self.assertEqual(self.origin.read_bytes(),self.old)
    def test_hung_worker_is_killed_without_changing_origin_or_selected_version(self):
        with patch.object(e,'_ORIGIN_BOOTSTRAP','import time;time.sleep(60)'),patch.object(e,'ORIGIN_SYNC_SECONDS',.15):
            result=e.sync_origin_bounded(self.context)
        self.assertEqual(result['kind'],'failed');self.assertIn('시간',result['message'])
        self.assertEqual(self.origin.read_bytes(),self.old)
        self.assertEqual(self.store.state()['current']['sha256'],self.candidate['sha256'])
    def test_two_real_workers_leave_one_complete_origin_and_backup(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:e.sync_origin_bounded(self.context),range(2)))
        self.assertIn('updated',[r['kind'] for r in results],results)
        self.assertTrue(all(r['kind'] in ('updated','current','busy') for r in results),results)
        self.assertEqual(self.origin.read_bytes(),self.new)
        self.assertEqual(self.origin.with_name('.'+self.origin.name+'.previous').read_bytes(),self.old)

    def test_launcher_uses_version_of_bytes_read_after_other_pc_replaced_origin(self):
        self.origin.write_bytes(self.new)
        stale=e.Store(Path(self.tmp.name)/'race-cache',self.origin,'2026.11.09.2')
        self.assertEqual(stale.prepare()['version'],'2026.11.09.3')

    def test_new_child_repairs_old_launchers_stale_version_metadata(self):
        wrong=item(self.new,'2026.11.09.2')
        state=self.store.state();state['current']=wrong;state['base']=wrong;self.store.save(state)
        e.write_json(self.store.root/'session.json',dict(nonce=self.nonce,current=wrong,pid=os.getpid(),base_version='2026.11.09.2',supervisor_pid=os.getpid()))
        with patch.dict(os.environ,JIHUNIUS_UPDATE_CHILD='1',JIHUNIUS_UPDATE_ORIGIN=str(self.origin),JIHUNIUS_UPDATE_NONCE=self.nonce),patch.object(e.sys,'argv',[str(self.store.path(wrong))]):
            context=e.managed_context('2026.11.09.3')
        self.assertEqual(context['current']['version'],'2026.11.09.3')
        self.assertEqual(self.store.state()['current']['version'],'2026.11.09.3')
        self.assertEqual(self.store.state()['base']['version'],'2026.11.09.3')
        self.assertEqual(e.read_json(self.store.root/'session.json')['current']['version'],'2026.11.09.3')

if __name__=='__main__':unittest.main()
