import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'src/error_history.py'
if PATH.exists():
    spec = importlib.util.spec_from_file_location('error_history_test', PATH)
    eh = importlib.util.module_from_spec(spec); spec.loader.exec_module(eh)
else:
    eh = None


class ErrorHistoryTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(eh, 'error history feature is not implemented')
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.share = self.base / 'share'
        self.a = eh.LocalStore(self.base / 'a.sqlite', 'PC-1')
        self.b = eh.LocalStore(self.base / 'b.sqlite', 'PC-2')
        self.c = eh.LocalStore(self.base / 'c.sqlite', 'PC-3')

    def record(self, store, message='save failed', **kw):
        store.record('세척완료', message, stage='저장', version='test', **kw)

    def sync(self, store):
        req = store.request(); result = eh.sync_shared(self.share, req)
        store.accept(req, result)
        return result

    def test_persistence_dedup_and_new_work(self):
        self.record(self.a, work='a'); self.record(self.a, work='a')
        self.record(self.a, work='b')
        rows = eh.LocalStore(self.base / 'a.sqlite', 'PC-1').view()['records']
        self.assertEqual(len(rows), 2); self.assertEqual(sorted(r['count'] for r in rows), [1,2])

    def test_retention_limit_and_off_toggle(self):
        for i in range(105): self.record(self.a, str(i))
        self.assertEqual(len(self.a.view()['records']),100)
        self.a.set_enabled(False); self.record(self.a,'not saved')
        self.assertNotIn('not saved',[r['message'] for r in self.a.view()['records']])
        self.a.set_enabled(True)
        self.record(self.a,'old',now=time.time()-31*86400)
        self.assertNotIn('old',[r['message'] for r in self.a.view()['records']])

    def test_concurrent_local_writers(self):
        def write(i): self.record(eh.LocalStore(self.base/'a.sqlite','PC-1'),str(i))
        with ThreadPoolExecutor(4) as pool: list(pool.map(write,range(40)))
        self.assertEqual(len(self.a.view()['records']),40)

    def test_three_pcs_combined_and_distinct(self):
        for store in (self.a,self.b,self.c): self.record(store); self.sync(store)
        self.sync(self.a)
        self.assertEqual({r['pc'] for r in self.a.view()['records']},{'PC-1','PC-2','PC-3'})

    def test_clear_all_offline_and_late_snapshot_never_resurrect(self):
        for store in (self.a,self.b,self.c): self.record(store); self.sync(store)
        stale = self.c.request()
        self.a.clear_all(); self.sync(self.a)
        late = eh.sync_shared(self.share, stale); self.c.accept(stale,late)
        self.sync(self.b); self.sync(self.a)
        for store in (self.a,self.b,self.c): self.assertEqual(store.view()['records'],[])
        self.record(self.c,'new after reconnect'); self.sync(self.c); self.sync(self.a)
        self.assertEqual([r['message'] for r in self.a.view()['records']],['new after reconnect'])

    def test_clear_reply_lost_and_concurrent_clear_are_idempotent(self):
        self.sync(self.a);self.sync(self.b)
        self.a.clear_all(); old = self.a.request(); eh.sync_shared(self.share,old)
        self.sync(self.b); self.b.clear_all(); self.sync(self.b)
        self.record(self.b,'keep after newer clear');self.sync(self.b)
        self.a.accept(old,eh.sync_shared(self.share,old))
        self.assertEqual([r['message'] for r in self.a.view()['records']],['keep after newer clear'])

    def test_error_arriving_during_sync_is_preserved(self):
        self.record(self.a,'first'); req=self.a.request(); result=eh.sync_shared(self.share,req)
        self.record(self.a,'second');self.a.accept(req,result)
        self.assertEqual({r['message'] for r in self.a.view()['records']},{'first','second'})

    def test_old_sync_cannot_undo_local_clear(self):
        self.record(self.a);req=self.a.request();result=eh.sync_shared(self.share,req)
        self.a.clear_all();self.a.accept(req,result)
        self.assertEqual(self.a.view()['records'],[])
        self.assertTrue(self.a.view()['pending_clear'])
        self.sync(self.a); self.assertFalse(self.a.view()['pending_clear'])

    def test_payload_and_storage_bounded(self):
        self.record(self.a,'x'*200000,detail='z'*200000)
        row=self.a.view()['records'][0]
        self.assertLess(len(row['message']),9000);self.assertLess(len(row['detail']),17000)
        self.assertLess(len(json.dumps(self.a.request())),30000)

    def test_full_unicode_history_can_sync_and_clear(self):
        for i in range(100):self.record(self.a,str(i)+'가'*8192,detail='🛠'*16384)
        result=self.sync(self.a)
        self.assertEqual(len(result['records']),100)
        self.a.clear_all();self.sync(self.a)
        self.assertEqual(self.a.view()['records'],[])

    def test_bad_shared_state_fails_without_overwriting_local(self):
        self.record(self.a); self.share.mkdir();(self.share/'generation.json').write_text('broken')
        with self.assertRaises((ValueError,json.JSONDecodeError)): self.sync(self.a)
        self.assertEqual(len(self.a.view()['records']),1)

    def test_service_clear_and_three_pc_snapshot(self):
        self.assertTrue(hasattr(eh,'Service'),'background UI service is missing')
        self.record(self.b,'other PC');self.sync(self.b)
        service=eh.Service(self.base/'a.sqlite',self.share,PATH.read_text())
        self.addCleanup(service.close)
        service.command('refresh')
        end=time.monotonic()+3
        while time.monotonic()<end:
            snapshot=service.snapshot()
            if snapshot.get('records'):break
            time.sleep(.03)
        self.assertEqual(snapshot['records'][0]['pc'],'PC-2')
        service.command('clear')
        end=time.monotonic()+3
        while time.monotonic()<end:
            snapshot=service.snapshot()
            if not snapshot.get('records') and snapshot.get('status')=='전체 PC 기록 삭제 완료':break
            time.sleep(.03)
        self.assertEqual(snapshot['status'],'전체 PC 기록 삭제 완료')
        self.sync(self.b);self.assertEqual(self.b.view()['records'],[])

    def test_subprocess_timeout_cleans_up_and_does_not_block_capture(self):
        script=self.base/'hang.py';script.write_text('import time; time.sleep(60)')
        transport=eh.SharedTransport(script,self.base/'io',self.share,timeout=.1)
        start=time.monotonic()
        with self.assertRaises(TimeoutError):transport.sync(self.a.request())
        self.assertLess(time.monotonic()-start,2)
        self.assertEqual(list((self.base/'io').iterdir()),[])
        recorder=eh.Recorder(self.base/'capture.sqlite','test','test')
        self.addCleanup(recorder.close)
        start=time.monotonic();recorder.capture('failure')
        self.assertLess(time.monotonic()-start,.05)
        recorder.events.join()
        self.assertEqual(recorder.store.view()['records'][0]['message'],'failure')

    def test_wash_error_event_records_without_changing_event_delivery(self):
        from test_host_stability import load_app
        import queue
        from types import SimpleNamespace
        m=load_app()
        self.assertTrue(hasattr(m,'SuiteErrors'),'host error hooks are missing')
        recorder=eh.Recorder(self.base/'wash.sqlite','test','test');self.addCleanup(recorder.close)
        m.SuiteErrors._recorder=recorder
        wash=m.WashApp.__new__(m.WashApp);wash.events=queue.Queue();wash.started=12.0
        wash.stop=__import__('threading').Event()
        wash.emit('log','POP 저장 중');wash.emit('error','save timeout')
        recorder.events.join()
        row=recorder.store.view()['records'][0]
        self.assertEqual(row['feature'],'세척완료');self.assertEqual(row['stage'],'POP 저장 중')
        self.assertEqual(wash.events.get(),('log','POP 저장 중'))
        self.assertEqual(wash.events.get(),('error','save timeout'))

    def test_special_table_recovered_error_can_be_recorded_again_after_clear(self):
        import sys
        from types import SimpleNamespace
        spec=importlib.util.spec_from_file_location('special_error_test',ROOT/'src/special_table.py')
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        recorder=eh.Recorder(self.base/'special.sqlite','특수 돌출량','test');self.addCleanup(recorder.close)
        old=sys.modules.get('jihunius_error_history');sys.modules['jihunius_error_history']=SimpleNamespace(capture=recorder.capture)
        self.addCleanup(lambda:sys.modules.__setitem__('jihunius_error_history',old))
        a=module.SpecialTableApp.__new__(module.SpecialTableApp)
        a.draft_error='';a.last_error='network failed';a.pending=[];a.status=SimpleNamespace(set=lambda x:None)
        a.ready=True;a.busy=False;a.state={'rows':[]}
        a.update_status();recorder.events.join();recorder.store.clear_all()
        a.last_error='';a.update_status()
        a.last_error='network failed';a.update_status();recorder.events.join()
        self.assertEqual(len(recorder.store.view()['records']),1)

    def test_wash_log_background_disconnect_is_captured(self):
        import sys,queue
        from types import SimpleNamespace
        spec=importlib.util.spec_from_file_location('wash_error_test',ROOT/'src/wash_log.py')
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        recorder=eh.Recorder(self.base/'wash-log.sqlite','세척일보','test');self.addCleanup(recorder.close)
        old=sys.modules.get('jihunius_error_history');sys.modules['jihunius_error_history']=SimpleNamespace(capture=recorder.capture)
        self.addCleanup(lambda:sys.modules.__setitem__('jihunius_error_history',old))
        results=queue.Queue();results.put(('offline','share disconnected',None))
        def callback(*args):raise AssertionError(args)
        a=SimpleNamespace(results=results,busy=0,closing=True,online=True,
            status=SimpleNamespace(set=lambda x:None),cancel_plate_drag=lambda:None,report_callback_exception=callback)
        module.App.drain(a);recorder.events.join()
        self.assertFalse(a.online)
        self.assertIsNotNone(recorder.store,'background disconnect was not recorded')
        self.assertEqual(recorder.store.view()['records'][0]['message'],'share disconnected')

    def test_idle_service_does_not_reparse_history_without_changes(self):
        from unittest.mock import patch
        service=eh.Service(self.base/'a.sqlite',self.share,PATH.read_text());self.addCleanup(service.close)
        end=time.monotonic()+3
        while not service.snapshot().get('connected') and time.monotonic()<end:time.sleep(.03)
        time.sleep(.6)
        reads=[];original=eh.LocalStore.rows
        def rows(db):reads.append(1);return original(db)
        with patch.object(eh.LocalStore,'rows',staticmethod(rows)):
            time.sleep(1.2)
        service.close();service.thread.join(7)
        self.assertEqual(reads,[],'idle history repeatedly reads full error bodies')

    def test_close_reaps_busy_share_helper(self):
        import threading
        script=self.base/'hang.py';script.write_text('import time; time.sleep(60)')
        transport=eh.SharedTransport(script,self.base/'io',self.share,timeout=20)
        self.assertTrue(hasattr(transport,'close'),'owner shutdown cannot stop share helper')
        failures=[]
        def run():
            try:transport.sync(self.a.request())
            except Exception as exc:failures.append(exc)
        thread=threading.Thread(target=run);thread.start()
        end=time.monotonic()+2
        while transport.process is None and time.monotonic()<end:time.sleep(.01)
        child=transport.process;self.assertIsNotNone(child)
        transport.close();thread.join(2)
        self.assertFalse(thread.is_alive());self.assertIsNotNone(child.poll())


if __name__=='__main__': unittest.main()
