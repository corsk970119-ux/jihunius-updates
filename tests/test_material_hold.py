import ast,base64,sqlite3,sys,tempfile,time,types,unittest,uuid,zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import material_counter as core
import material_sync as sync


class MaterialHoldTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.path=Path(self.tmp.name)/'db.sqlite3';self.s=sync.CommandStore(self.path)
  self.addCleanup(lambda:self.s.close());self.at=time.time()-500;self.program=1001
  for kind in core.MATERIAL_TYPES:self.s.register_stock(kind,20,self.at)
  self.s.assign_material(1,'10Z',self.at);self.feed()
  self.s.rotate(1,self.at+.1);self.original=self.s.snapshot(1)['active_material']
 def feed(self,count=1,state='STOP'):
  for _ in range(count):
   self.at+=1;self.program+=1
   self.s.observe(dict(machine=1,program=str(self.program),state=state,part_count='0'),self.at)
 def switch(self):
  self.assertTrue(callable(getattr(self.s,'switch_14',None)),'temporary 14 mm switching must exist')
  return self.s.switch_14(1,self.at+.2)
 def stock(self,kind):return next(r['quantity'] for r in self.s.inventory() if r['type_id']==kind)
 def req(self,method='switch_14',args=None):
  return dict(id=uuid.uuid4().hex,client='A',epoch=self.s.epoch(),method=method,args=args or [1],
              expected=self.s.expectations(1),expires=time.time()+30)
 def fresh(self):
  self.at=time.time();self.s.observe(dict(machine=1,program=str(self.program),state='STOP',part_count='0'),self.at)

 def test_original_100_plus_50_and_14_counts_remain_independent(self):
  self.feed(100);self.s.defect(1,self.at+.1)
  self.switch();other=self.s.snapshot(1)['active_material']
  self.assertNotEqual(other,self.original)
  self.assertEqual(self.s.snapshot(1)['parked']['material_id'],self.original)
  self.assertEqual(self.s.snapshot(1)['parked']['good'],99)
  self.feed(7);self.s.defect(1,self.at+.1);self.switch()
  self.assertEqual(self.s.snapshot(1)['active_material'],self.original)
  self.assertEqual(self.s.snapshot(1)['parked']['material_id'],other)
  self.feed(50);row=self.s.snapshot(1)
  self.assertEqual((row['good'],row['defects']),(149,1))
  self.assertEqual((row['parked']['good'],row['parked']['defects']),(6,1))
  self.assertEqual((self.stock('10Z'),self.stock('14')),(19,19))
  self.assertEqual(self.s.period_report(self.at-200,self.at+1)['totals']['consumed_rods'],1) # Initial partial rod only.
  self.s.rotate(1,self.at+.3)
  original=next(r for r in self.s.history() if r['id']==self.original)
  self.assertEqual((original['total'],original['good'],original['defects']),(150,149,1))
  self.switch();self.assertEqual(self.s.snapshot(1)['active_material'],other)
  self.feed(3);self.s.rotate(1,self.at+.4)
  report=self.s.period_report(self.at-200,self.at+1)
  ten=next(x for x in report['by_type'] if x['type_id']=='10Z')
  fourteen=next(x for x in report['by_type'] if x['type_id']=='14')
  self.assertEqual((ten['eligible_rods'],ten['avg_good_per_rod'],ten['avg_defects_per_rod']),(1,149,1))
  self.assertEqual((fourteen['consumed_rods'],fourteen['completed_good'],fourteen['completed_defects']),(1,9,1))

 def test_repeated_switches_preserve_next_material_and_restart(self):
  self.s.set_next_type(1,'12',self.at);self.switch();other=self.s.snapshot(1)['active_material']
  self.s.close();self.s=sync.CommandStore(self.path);self.feed()
  self.switch();self.assertEqual(self.s.snapshot(1)['next_type'],'12')
  for _ in range(4):
   self.switch();self.assertEqual(self.s.snapshot(1)['active_material'],other)
   self.switch();self.assertEqual(self.s.snapshot(1)['active_material'],self.original)
  self.assertEqual(self.stock('14'),19)
  self.s.rotate(1,self.at+.3);self.assertEqual(self.s.snapshot(1)['material_type'],'12')
  self.switch();self.switch();self.assertEqual(self.s.snapshot(1)['material_type'],'12')
  self.assertEqual(self.s.db.execute('PRAGMA foreign_key_check').fetchall(),[])

 def test_failed_switch_rolls_back_every_table_and_no_stock_is_withdrawn(self):
  self.s.db.execute("CREATE TRIGGER fail_switch BEFORE INSERT ON events WHEN NEW.kind='switch14' BEGIN SELECT RAISE(ABORT,'disk full'); END")
  self.s.db.commit();before=self.s.db.total_changes
  self.assertTrue(callable(getattr(self.s,'switch_14',None)))
  with self.assertRaises(sqlite3.Error):self.s.switch_14(1,self.at+.1)
  self.assertEqual(self.s.snapshot(1)['active_material'],self.original)
  self.assertIsNone(self.s.snapshot(1)['parked']);self.assertEqual(self.stock('14'),20)
  self.assertEqual(self.s.db.execute('SELECT COUNT(*) FROM materials').fetchone()[0],2)

 def test_switch_requires_known_live_machine_and_stock_only_for_first_load(self):
  self.s.adjust_stock('14',0,'fixture',self.at)
  self.assertTrue(callable(getattr(self.s,'switch_14',None)))
  with self.assertRaises(ValueError):self.switch()
  self.s.receive_stock('14',1,self.at);self.feed(state='UNKNOWN')
  with self.assertRaises(ValueError):self.switch()
  self.feed();self.switch();self.assertEqual(self.stock('14'),0)
  self.switch();self.switch();self.assertEqual(self.stock('14'),0)
  self.s.live.clear()
  with self.assertRaises(ValueError):self.switch()

 def test_normal_replacement_cannot_discard_parked_rod_or_change_temporary_role(self):
  self.switch()
  with self.assertRaises(ValueError):self.s.set_next_type(1,'12',self.at)
  self.s.rotate(1,self.at+.3);self.switch()
  self.assertEqual(self.s.snapshot(1)['active_material'],self.original)
  with self.assertRaises(ValueError):self.s.set_next_type(1,'14',self.at)
  self.assertEqual(self.s.snapshot(1)['parked']['material_type'],'14')

 def test_undo_switch_refunds_only_unused_new_rod_and_existing_swap_is_reversible(self):
  self.switch();self.s.undo(1,self.at+.3)
  self.assertEqual(self.stock('14'),20);self.assertIsNone(self.s.snapshot(1)['parked'])
  self.assertEqual(self.s.snapshot(1)['active_material'],self.original)
  self.switch();self.feed(2)
  with self.assertRaises(ValueError):self.s.undo(1,self.at+.3)
  other=self.s.snapshot(1)['active_material'];self.switch();self.s.undo(1,self.at+.4)
  self.assertEqual(self.s.snapshot(1)['active_material'],other)
  self.assertEqual(self.s.snapshot(1)['parked']['material_id'],self.original)
  self.assertEqual(self.stock('14'),19)

 def test_normal_rotate_undo_preserves_parked_counts(self):
  self.switch();self.feed(3);old=self.s.snapshot(1)['active_material']
  self.s.rotate(1,self.at+.3);self.feed(2);self.s.undo(1,self.at+.4)
  self.assertEqual(self.s.snapshot(1)['active_material'],old)
  self.assertEqual(self.s.snapshot(1)['total'],5)
  self.assertEqual(self.s.snapshot(1)['parked']['material_id'],self.original)
  self.switch();self.assertEqual(self.s.snapshot(1)['active_material'],self.original)

 def test_undo_does_not_hide_collection_gap_on_restored_rod(self):
  self.assertFalse(self.s.snapshot(1)['gap']);self.switch()
  self.s.disconnected(1,self.at+.3)
  self.s.undo(1,self.at+.4)
  self.assertEqual(self.s.snapshot(1)['active_material'],self.original)
  self.assertTrue(self.s.snapshot(1)['gap'])

 def test_undo_existing_swap_does_not_transfer_an_old_gap_from_other_rod(self):
  self.switch();self.s.disconnected(1,self.at+.3);self.feed()
  self.switch();self.assertFalse(self.s.snapshot(1)['gap'])
  self.switch();self.assertTrue(self.s.snapshot(1)['gap'])
  self.s.undo(1,self.at+.4)
  self.assertFalse(self.s.snapshot(1)['gap'])
  self.assertTrue(self.s.snapshot(1)['parked']['gap'])

 def test_old_or_competing_commands_cannot_reverse_new_switch_and_retry_is_deduplicated(self):
  self.fresh();a=self.req();b=self.req();old_defect=self.req('defect')
  result=self.s.apply(a);self.assertTrue(result['ok'],result)
  self.assertEqual(self.s.apply(a),result);self.assertFalse(self.s.apply(b)['ok'])
  self.assertTrue(self.s.apply(self.req())['ok'])
  self.assertEqual(self.s.snapshot(1)['active_material'],self.original)
  self.assertFalse(self.s.apply(old_defect)['ok'])
  b['id']=uuid.uuid4().hex;self.assertFalse(self.s.apply(b)['ok'])
  self.assertEqual(self.stock('14'),19)

 def test_reset_clears_both_rods_and_rejects_pending_switch(self):
  self.fresh();self.assertTrue(self.s.apply(self.req())['ok'])
  pending=self.req();self.s.reset_records(False)
  self.assertIsNone(self.s.snapshot(1)['parked'])
  self.assertEqual(self.s.db.execute('SELECT COUNT(*) FROM materials').fetchone()[0],0)
  self.assertEqual(self.stock('14'),19);self.assertFalse(self.s.apply(pending)['ok'])

 def test_v3_database_migrates_without_losing_counts_and_old_writer_refuses_new_schema(self):
  path=Path(__file__).resolve().parents[1]/'releases/jihunius/2026.11.06.2/app.pyw'
  assignments={n.targets[0].id:n.value for n in ast.parse(path.read_text()).body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
  payload=ast.literal_eval(assignments['SUITE_COMPANIONS'])['material']['compressed']
  source=zlib.decompress(base64.b64decode(payload)).decode()
  definition=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='Store')
  old=types.ModuleType('old_material_core');old.__dict__.update(core.__dict__)
  exec(compile(ast.get_source_segment(source,definition),'v3 Store','exec'),old.__dict__)
  legacy=Path(self.tmp.name)/'legacy.sqlite3';s=old.Store(legacy)
  s.register_stock('10B',7);s.assign_material(2,'10B')
  for p in ('1001','1002','1003'):s.observe(dict(machine=2,program=p,state='STOP',part_count='0'))
  s.defect(2);s.close()
  s=sync.CommandStore(legacy)
  try:
   self.assertEqual(s.db.execute('PRAGMA user_version').fetchone()[0],5)
   self.assertEqual((s.snapshot(2)['good'],s.snapshot(2)['defects']),(1,1))
   self.assertIsNone(s.snapshot(2)['parked']);self.assertEqual(s.inventory()[1]['quantity'],7)
   self.assertTrue(s.migration_backup.exists())
  finally:s.close()
  with self.assertRaises(RuntimeError):old.Store(legacy)
