import sys, tempfile, time, unittest, uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import material_counter as core
try:
 import material_sync as sync
except ImportError:
 sync=None

class CommandTests(unittest.TestCase):
 def setUp(self):
  self.assertIsNotNone(sync,'Synchronized command storage is not implemented')
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.path=Path(self.tmp.name)/'counter.sqlite3'
  self.s=sync.CommandStore(self.path);self.addCleanup(lambda:self.s.close())
  self.s.register_stock('10Z',10);self.s.assign_material(1,'10Z')
  for p in ('1001','1002','1003'):
   self.s.observe(dict(machine=1,program=p,state='STOP',part_count='0'))
 def req(self,method='defect',args=None):
  return dict(id=uuid.uuid4().hex,client='pc-A',epoch=self.s.epoch(),method=method,
    args=args or [1],expected=self.s.expectations(1),expires=time.time()+30)
 def test_retry_after_restart_does_not_count_defect_twice(self):
  r=self.req();a=self.s.apply(r);self.assertTrue(a['ok'])
  self.s.close();self.s=sync.CommandStore(self.path)
  self.assertEqual(self.s.apply(r),a)
  self.assertEqual((self.s.snapshot(1)['good'],self.s.snapshot(1)['defects']),(1,1))
 def test_two_pcs_distinct_defects_both_preserved(self):
  a=self.req();b=self.req();b['client']='pc-B'
  self.assertTrue(self.s.apply(a)['ok']);self.assertTrue(self.s.apply(b)['ok'])
  self.assertEqual(self.s.snapshot(1)['defects'],2)
 def test_competing_rotation_consumes_only_one_rod(self):
  a=self.req('rotate');b=self.req('rotate')
  self.assertTrue(self.s.apply(a)['ok']);self.assertFalse(self.s.apply(b)['ok'])
  self.assertEqual(self.s.inventory()[0]['quantity'],9)
  self.assertEqual(len([r for r in self.s.events() if r['kind']=='rotate']),1)
 def test_delayed_defect_cannot_move_to_new_rod(self):
  d=self.req();self.s.apply(self.req('rotate'))
  self.assertFalse(self.s.apply(d)['ok']);self.assertEqual(self.s.snapshot(1)['defects'],0)
 def test_stale_undo_does_not_undo_another_pcs_new_action(self):
  self.s.apply(self.req());u=self.req('undo');self.s.apply(self.req())
  self.assertFalse(self.s.apply(u)['ok']);self.assertEqual(self.s.snapshot(1)['defects'],2)
 def test_reused_id_different_contents_rejected(self):
  r=self.req();self.s.apply(r);r['method']='rotate'
  with self.assertRaises(ValueError):self.s.apply(r)
  self.assertEqual(self.s.inventory()[0]['quantity'],10)
 def test_expired_request_and_old_reset_epoch_rejected(self):
  a=self.req();a['expires']=time.time()-1
  self.assertFalse(self.s.apply(a)['ok'])
  b=self.req();self.s.reset_records()
  self.assertFalse(self.s.apply(b)['ok']);self.assertEqual(self.s.snapshot(1)['defects'],0)
 def test_failed_receipt_insert_rolls_back_business_write(self):
  self.s.db.execute("CREATE TRIGGER fail_receipt BEFORE INSERT ON sync_receipts BEGIN SELECT RAISE(ABORT,'full disk'); END")
  self.s.db.commit()
  with self.assertRaises(Exception):self.s.apply(self.req())
  self.assertEqual(self.s.snapshot(1)['defects'],0)
 def test_stock_adjustment_conflict_preserves_intervening_receipt(self):
  a=self.req('adjust_stock',['10Z',5,'실사']);a['expected']=self.s.stock_expectations('10Z')
  self.s.receive_stock('10Z',3)
  self.assertFalse(self.s.apply(a)['ok']);self.assertEqual(self.s.inventory()[0]['quantity'],13)
 def test_existing_counting_exclusions_and_early_change_report_preserved(self):
  for p in ('3999','1003','9012','9999','1004'):
   self.s.observe(dict(machine=1,program=p,state='STOP',part_count='900'))
  self.assertEqual(self.s.snapshot(1)['total'],4)
  r=self.req('rotate',[1,True]);self.assertTrue(self.s.apply(r)['ok'])
  old=self.s.history()[0]
  self.assertEqual((old['total'],old['early_end']),(4,1))

if __name__=='__main__':unittest.main()

class QuietCollector:
 def __init__(self,out):self.out=out;self.running=False;self.program='1001'
 def start(self):self.running=True
 def close(self):self.running=False
 def checkpoint(self,n,token):
  if not self.running:raise ValueError('stopped')
  self.out.put(('sample','192.168.1.10',1,dict(machine=n,program=self.program,state='STOP',part_count='0'),time.time(),token,None))

class ServiceTests(unittest.TestCase):
 def setUp(self):
  self.assertTrue(sync and hasattr(sync,'Authority'),'Authority service is not implemented')
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.s=sync.CommandStore(Path(self.tmp.name)/'counter.sqlite3')
  self.s.register_stock('10Z',10);self.s.assign_material(1,'10Z')
  self.s.close()
  self.a=sync.Authority(Path(self.tmp.name)/'counter.sqlite3',token='a'*64,owner='main',collector_factory=QuietCollector)
  self.a.start();self.addCleanup(self.a.close)
  self.c=sync.RPCClient('127.0.0.1',self.a.port,'a'*64)
 def feed(self,p):
  self.a.collector.program=p
  self.a.samples.put(('sample','192.168.1.10',1,dict(machine=1,program=p,state='STOP',part_count='0'),time.time(),None,None))
  end=time.monotonic()+2
  while time.monotonic()<end:
   if self.c.call('state')['rows'][0]['program']==p:return
  self.fail('sample not processed')
 def command(self,method='defect',args=None):
  s=self.c.call('state')
  return dict(id=uuid.uuid4().hex,client='sub',epoch=s['epoch'],method=method,args=args or [1],expected=s['rows'][0]['expected'],expires=time.time()+30)
 def test_off_submits_defect_and_rotation_to_one_writer(self):
  self.a.set_collection(True)
  for p in ('1001','1002','1003'):self.feed(p)
  request=self.command();self.assertTrue(self.c.call('command',request)['ok'])
  other=sync.RPCClient('127.0.0.1',self.a.port,'a'*64)
  self.assertEqual(other.call('state')['rows'][0]['defects'],1)
  rotate=self.command('rotate',[1,False]);self.assertTrue(other.call('command',rotate)['ok'])
  self.assertTrue(self.c.call('command',rotate)['ok'])
  state=self.c.call('state');self.assertEqual(state['inventory'][0]['quantity'],9)
  self.assertEqual(state['rows'][0]['defects'],0)
 def test_owner_off_stops_collection_but_serves_records(self):
  self.a.set_collection(True);self.feed('1001');self.feed('1002')
  self.a.set_collection(False)
  state=self.c.call('state');self.assertFalse(state['collection']);self.assertFalse(state['live'])
  self.assertTrue(self.c.call('command',self.command())['ok'])
  self.assertTrue(self.c.call('command',self.command('rotate',[1,False]))['ok'])
  self.assertTrue(self.c.call('state')['rows'][0]['gap'])
 def test_wrong_token_cannot_read_or_write(self):
  wrong=sync.RPCClient('127.0.0.1',self.a.port,'b'*64)
  with self.assertRaises(PermissionError):wrong.call('state')
 def test_second_service_same_database_rejected(self):
  other=sync.Authority(Path(self.tmp.name)/'counter.sqlite3',token='b'*64,owner='other',collector_factory=QuietCollector)
  with self.assertRaises(RuntimeError):other.start()
 def test_reports_and_backup_are_consistent_original_data(self):
  self.a.set_collection(True);self.feed('1001');self.feed('1002')
  report=self.c.call('read',{'name':'period_report','args':[0,time.time()+5,None]})
  self.assertIsInstance(report,dict)
  import base64,sqlite3
  path=Path(self.tmp.name)/'copy.sqlite3';path.write_bytes(base64.b64decode(self.c.call('backup')['data']))
  db=sqlite3.connect(str(path));self.addCleanup(db.close)
  self.assertEqual(db.execute('PRAGMA quick_check').fetchone()[0],'ok')
  self.assertEqual(db.execute('SELECT SUM(auto_delta) FROM events').fetchone()[0],1)

class DiscoveryTests(unittest.TestCase):
 def setUp(self):
  self.assertTrue(hasattr(sync,'Discovery'),'Shared owner discovery is not implemented')
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)
 def test_only_one_pc_can_claim_collection_owner(self):
  d=sync.Discovery(self.root)
  a=dict(owner_id='a'*32,owner_name='main',token='a'*64,host='127.0.0.1',port=10000)
  b=dict(owner_id='b'*32,owner_name='sub',token='b'*64,host='127.0.0.1',port=10001)
  self.assertEqual(d.exchange('claim',a)['owner_id'],'a'*32)
  with self.assertRaises(ValueError):d.exchange('claim',b)
  self.assertEqual(d.exchange('read')['owner_id'],'a'*32)
 def test_wrong_owner_cannot_overwrite_endpoint(self):
  d=sync.Discovery(self.root)
  a=dict(owner_id='a'*32,owner_name='main',token='a'*64,host='127.0.0.1',port=10000)
  d.exchange('claim',a);a['owner_id']='b'*32
  with self.assertRaises(ValueError):d.exchange('publish',a)
 def test_journal_survives_restart_without_changing_request_id(self):
  self.assertTrue(hasattr(sync,'Outbox'),'Durable pending journal missing')
  p=self.root/'pending.json';j=sync.Outbox(p)
  r=dict(id='a'*32,client='sub',epoch='period',method='defect',args=[1],expected={'material':1},expires=1)
  j.add('owner',r);again=sync.Outbox(p)
  self.assertEqual(again.items()[0],dict(owner='owner',request=r))
  again.remove(r['id']);self.assertEqual(sync.Outbox(p).items(),[])

class SessionTests(unittest.TestCase):
 def test_collection_setting_persists_and_sub_pc_cannot_collect(self):
  try:import material_client as client
  except ImportError:client=None
  self.assertIsNotNone(client,'PC collection session not implemented')
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);share=root/'share';main=root/'main';sub=root/'sub'
   a=client.Coordinator(main,share,collector_factory=QuietCollector)
   try:
    a.toggle(True);self.assertTrue(a.authority.collection)
    b=client.Coordinator(sub,share,collector_factory=QuietCollector)
    try:
     b.connect();self.assertFalse(b.settings['enabled']);self.assertIsNone(b.authority)
     with self.assertRaises(ValueError):b.toggle(True)
     self.assertFalse(b.settings['enabled']);self.assertIsNone(b.authority)
    finally:b.close()
   finally:a.close()
   a=client.Coordinator(main,share,collector_factory=QuietCollector)
   try:
    a.connect();self.assertTrue(a.authority.collection)
    a.toggle(False);self.assertFalse(a.authority.collection)
   finally:a.close()
   a=client.Coordinator(main,share,collector_factory=QuietCollector)
   try:a.connect();self.assertFalse(a.authority.collection);self.assertIsNotNone(a.client)
   finally:a.close()

class ResetTests(unittest.TestCase):
 setUp=CommandTests.setUp
 req=CommandTests.req
 def test_full_reset_removes_business_data_and_old_receipts_but_retry_is_safe(self):
  old=self.req();self.assertTrue(self.s.apply(old)['ok'])
  delayed=self.req();self.s.set_next_type(1,'12')
  request=self.req('reset_records',[True]);request['expected']={'revision':self.s.revision()}
  response=self.s.apply(request);self.assertTrue(response['ok'])
  for table in ('events','materials','stock_movements'):
   self.assertEqual(self.s.db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0],0)
  self.assertEqual([r[0] for r in self.s.db.execute('SELECT id FROM sync_receipts')],[request['id']])
  for n in core.MACHINES:
   row=self.s.snapshot(n)
   self.assertEqual((row['total'],row['defects'],row['active_material'],row['initial_type'],row['next_type']),(0,0,None,None,None))
  self.assertTrue(all(r['quantity'] is None for r in self.s.inventory()))
  self.assertIsNone(response['value'])
  self.assertFalse((self.path.parent/'backups').exists())
  self.s.close();self.s=sync.CommandStore(self.path)
  self.assertEqual(self.s.apply(request),response)
  self.assertFalse(self.s.apply(delayed)['ok']);self.assertFalse(self.s.apply(old)['ok'])
  self.assertEqual(self.s.snapshot(1)['total'],0)
 def test_full_reset_succeeds_without_creating_or_requiring_a_backup(self):
  blocked=self.path.parent/'backups';blocked.write_text('No backup directory available')
  request=self.req('reset_records',[True]);request['expected']={'revision':self.s.revision()}
  self.assertTrue(self.s.apply(request)['ok'])
  self.assertEqual(self.s.snapshot(1)['total'],0)
  self.assertEqual(blocked.read_text(),'No backup directory available')
 def test_full_reset_receipt_failure_rolls_back_all_deletions(self):
  self.s.apply(self.req())
  request=self.req('reset_records',[True]);request['expected']={'revision':self.s.revision()}
  before=(self.s.revision(),self.s.snapshot(1),self.s.inventory(),[tuple(r) for r in self.s.db.execute('SELECT * FROM sync_receipts')])
  self.s.db.execute("CREATE TRIGGER fail_reset_receipt BEFORE INSERT ON sync_receipts BEGIN SELECT RAISE(ABORT,'disk full'); END");self.s.db.commit()
  with self.assertRaises(Exception):self.s.apply(request)
  self.assertEqual((self.s.revision(),self.s.snapshot(1),self.s.inventory(),[tuple(r) for r in self.s.db.execute('SELECT * FROM sync_receipts')]),before)
 def test_reset_receipt_and_epoch_commit_together(self):
  self.assertTrue(hasattr(self.s,'revision'),'Revision guarded reset is missing')
  r=self.req('reset_records',[False]);r['expected']={'revision':self.s.revision()}
  old_epoch=self.s.epoch();response=self.s.apply(r)
  self.assertTrue(response['ok']);self.assertIsNone(response['value'])
  self.assertFalse((self.path.parent/'backups').exists())
  self.assertNotEqual(self.s.epoch(),old_epoch);self.assertEqual(self.s.inventory()[0]['quantity'],10)
  self.s.close();self.s=sync.CommandStore(self.path)
  self.assertEqual(self.s.apply(r),response)
 def test_stale_reset_does_not_delete_new_input(self):
  self.assertTrue(hasattr(self.s,'revision'),'Revision guarded reset is missing')
  r=self.req('reset_records',[False]);r['expected']={'revision':self.s.revision()}
  self.s.apply(self.req());self.assertFalse(self.s.apply(r)['ok'])
  self.assertEqual(self.s.snapshot(1)['defects'],1)
