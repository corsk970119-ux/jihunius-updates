import sys,tempfile,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import material_sync as sync
from test_material_sync import QuietCollector

class DrainTests(unittest.TestCase):
 def test_off_drains_every_published_sample_before_marking_gap(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=sync.Authority(Path(tmp)/'db.sqlite3','x'*64,'main',QuietCollector)
   a.store=sync.CommandStore(a.path);self.addCleanup(a.store.close)
   a.collection=True;a.collector=QuietCollector(a.samples);a.collector.start()
   t=time.time()-2
   for n in range(150):a.samples.put(('sample','127.0.0.1',1,dict(machine=1,program=str(1000+n),state='STOP',part_count='0'),t+n*.01,None,None))
   a._switch(False)
   self.assertEqual(a.store.snapshot(1)['total'],149)
   self.assertTrue(a.samples.empty());self.assertEqual(a.store.live,set())
   a._switch(True);self.assertEqual(a.store.snapshot(1)['total'],149)
   a.collector.close()
 def test_shutdown_drains_every_published_sample(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'db.sqlite3';a=sync.Authority(path,'x'*64,'main',QuietCollector)
   t=time.time()-2
   for n in range(150):a.samples.put(('sample','127.0.0.1',1,dict(machine=1,program=str(1000+n),state='STOP',part_count='0'),t+n*.01,None,None))
   a.stopping.set();a._run()
   s=sync.CommandStore(path)
   try:self.assertEqual(s.snapshot(1)['total'],149)
   finally:s.close()

class ReadLimitsTests(unittest.TestCase):
 def test_read_overload_leaves_writer_available(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=sync.Authority(Path(tmp)/'db.sqlite3','x'*64,'main',QuietCollector);a.start();self.addCleanup(a.close)
   self.assertTrue(hasattr(a,'read_slots'),'Bounded report jobs missing')
   a.read_slots.acquire();a.read_slots.acquire()
   try:
    with self.assertRaises(RuntimeError):a.read_request('read',dict(name='period_report',args=[0,time.time(),None]))
    self.assertEqual(len(a.request('state')['rows']),9)
   finally:a.read_slots.release();a.read_slots.release()
 def test_long_report_deadline_does_not_stop_collection(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=sync.Authority(Path(tmp)/'db.sqlite3','x'*64,'main',QuietCollector);a.start();self.addCleanup(a.close)
   self.assertTrue(hasattr(a,'read_timeout'),'Read deadline missing')
   a.set_collection(True);a.read_timeout=0
   with self.assertRaises(TimeoutError):a.read_request('read',dict(name='period_report',args=[0,time.time(),None]))
   self.assertTrue(a.request('state')['collection'])

class RecoveryTests(unittest.TestCase):
 def test_lost_acknowledgement_reconciles_after_both_clients_restart(self):
  import material_client as client
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as tmp,patch.object(client,'lan_address',return_value='127.0.0.1'):
   root=Path(tmp);main=root/'main';main.mkdir()
   s=sync.CommandStore(main/'counter.sqlite3');s.register_stock('10Z',10);s.assign_material(1,'10Z')
   for p in ('1001','1002','1003'):s.observe(dict(machine=1,program=p,state='STOP',part_count='0'))
   s.close();owner=client.Coordinator(main,root/'share',QuietCollector);owner.toggle(True)
   sub=client.ClientSession(root/'sub',root/'share',QuietCollector)
   try:
    end=time.monotonic()+4
    while sub.state is None and time.monotonic()<end:time.sleep(.02)
    self.assertIsNotNone(sub.state)
    original=sync.RPCClient.call
    def lost_ack(connection,method,args=None):
     value=original(connection,method,args)
     if method=='command':sub.stop.set();raise ConnectionError('response lost after committed write')
     return value
    with patch.object(sync.RPCClient,'call',lost_ack):
     request_id=sub.command('defect',[1],sub.state['rows'][0]['expected'])
     sub.thread.join(5)
    self.assertTrue(sub.closed);self.assertEqual(sub.outbox.items()[0]['request']['id'],request_id)
    self.assertEqual(owner.client.call('state')['rows'][0]['defects'],1)
    owner.close();owner=client.Coordinator(main,root/'share',QuietCollector);owner.connect()
    sub=client.ClientSession(root/'sub',root/'share',QuietCollector)
    end=time.monotonic()+5
    while sub.outbox.items() and time.monotonic()<end:time.sleep(.02)
    self.assertEqual(sub.outbox.items(),[])
    self.assertEqual(owner.client.call('state')['rows'][0]['defects'],1)
   finally:
    sub.close();sub.thread.join(10);owner.close()
