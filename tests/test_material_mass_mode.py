import ast,base64,sqlite3,sys,time,types,unittest,zlib
from pathlib import Path
import test_material_hold as hold
import material_counter as core
import material_sync as sync


class MassModeTests(unittest.TestCase):
 setUp=hold.MaterialHoldTests.setUp
 feed=hold.MaterialHoldTests.feed
 stock=hold.MaterialHoldTests.stock
 req=hold.MaterialHoldTests.req
 fresh=hold.MaterialHoldTests.fresh
 def mode(self):
  self.assertTrue(callable(getattr(self.s,'toggle_mass_mode',None)),'Per-machine mass mode must preserve and pause the rod')
  return self.s.toggle_mass_mode(1,self.at+.2)

 def test_pause_excludes_mass_jobs_and_resume_keeps_counts_stock_and_other_machines(self):
  self.feed(5);self.s.defect(1,self.at+.1);self.s.set_next_type(1,'12',self.at+.1)
  before=self.s.snapshot(1);inventory=self.s.inventory();self.mode()
  events=self.s.db.execute('SELECT COUNT(*) FROM events').fetchone()[0]
  self.feed(100)
  self.s.observe(dict(machine=2,program='2001',state='STOP',part_count='0'),self.at-1)
  self.s.observe(dict(machine=2,program='2002',state='STOP',part_count='0'),self.at)
  row=self.s.snapshot(1)
  self.assertTrue(row['mass_mode']);self.assertEqual((row['good'],row['defects']),(4,1))
  self.assertEqual(self.s.snapshot(2)['good'],1)
  self.assertEqual(self.s.db.execute('SELECT COUNT(*) FROM events').fetchone()[0],events+2)
  self.mode();self.feed(3);row=self.s.snapshot(1)
  self.assertFalse(row['mass_mode']);self.assertEqual((row['good'],row['defects']),(7,1))
  self.assertEqual((row['active_material'],row['next_type']),(before['active_material'],'12'))
  self.assertEqual(self.s.inventory(),inventory);self.assertFalse(row['gap'])
  self.s.rotate(1,self.at+.3)
  ended=next(r for r in self.s.history() if r['id']==before['active_material'])
  self.assertEqual((ended['total'],ended['good'],ended['defects']),(8,7,1))

 def test_pause_restart_disconnect_and_14_parked_rod_remain_intact(self):
  self.feed(3);self.s.switch_14(1,self.at+.1);self.feed(2)
  before=self.s.snapshot(1);self.mode();self.s.disconnected(1,self.at+.3)
  self.s.close();self.s=sync.CommandStore(self.path)
  self.assertTrue(self.s.snapshot(1)['mass_mode']);self.feed(5)
  self.mode();self.feed(2);row=self.s.snapshot(1)
  self.assertEqual((row['active_material'],row['good']),(before['active_material'],4))
  self.assertEqual(row['parked'],before['parked']);self.assertFalse(row['gap'])
  self.s.switch_14(1,self.at+.3);self.assertEqual(self.s.snapshot(1)['good'],3)
  self.assertEqual(self.stock('14'),19)

 def test_paused_writes_and_undo_across_mode_boundary_are_rejected(self):
  self.feed(3);self.s.defect(1,self.at+.1);self.mode()
  for method,args in (('defect',[1]),('rotate',[1]),('switch_14',[1]),('undo',[1]),
                      ('set_next_type',[1,'12']),('assign_material',[1,'10Z'])):
   with self.subTest(method=method),self.assertRaises(ValueError):getattr(self.s,method)(*args,at=self.at+.3)
  self.assertEqual(self.s.undo_label(1),'');self.mode()
  with self.assertRaises(ValueError):self.s.undo(1,self.at+.3)
  self.s.defect(1,self.at+.3);self.s.undo(1,self.at+.4)
  self.assertEqual(self.s.snapshot(1)['defects'],1)

 def test_requires_fresh_known_state_on_both_sides(self):
  self.feed(state='UNKNOWN')
  self.assertTrue(callable(getattr(self.s,'toggle_mass_mode',None)))
  with self.assertRaises(ValueError):self.s.toggle_mass_mode(1,self.at+.2)
  self.feed();self.mode();self.feed(state='UNKNOWN')
  with self.assertRaises(ValueError):self.mode()
  self.feed();self.s.live.clear()
  with self.assertRaises(ValueError):self.mode()
  self.assertTrue(self.s.snapshot(1)['mass_mode'])

 def test_duplicate_retry_competing_pc_and_aba_stale_writes(self):
  self.fresh();old=self.req('rotate',[1,False]);a=self.req('toggle_mass_mode');b=self.req('toggle_mass_mode')
  self.assertTrue(callable(getattr(self.s,'toggle_mass_mode',None)))
  result=self.s.apply(a);self.assertTrue(result['ok'],result)
  self.assertEqual(self.s.apply(a),result);self.assertFalse(self.s.apply(b)['ok'])
  self.assertTrue(self.s.apply(self.req('toggle_mass_mode'))['ok'])
  self.assertFalse(self.s.apply(old)['ok']);self.assertEqual(self.stock('10Z'),19)
  self.s.close();self.s=sync.CommandStore(self.path)
  self.assertEqual(self.s.apply(a),result);self.assertFalse(self.s.snapshot(1)['mass_mode'])

 def test_failed_mode_write_rolls_back_and_reset_removes_mode(self):
  self.assertTrue(callable(getattr(self.s,'toggle_mass_mode',None)))
  self.s.db.execute("CREATE TRIGGER fail_mode BEFORE INSERT ON events WHEN NEW.kind='mass_pause' BEGIN SELECT RAISE(ABORT,'disk full'); END")
  with self.assertRaises(sqlite3.Error):self.mode()
  self.assertFalse(self.s.snapshot(1)['mass_mode'])
  self.s.db.execute('DROP TRIGGER fail_mode');self.mode();self.s.reset_records(False)
  self.assertFalse(self.s.snapshot(1)['mass_mode']);self.assertIsNone(self.s.snapshot(1)['active_material'])

 def test_v4_migration_preserves_rods_and_old_writer_cannot_ignore_pause(self):
  path=Path(__file__).resolve().parents[1]/'releases/jihunius/2026.11.06.5/app.pyw'
  assignments={n.targets[0].id:n.value for n in ast.parse(path.read_text()).body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
  source=zlib.decompress(base64.b64decode(ast.literal_eval(assignments['SUITE_COMPANIONS'])['material']['compressed'])).decode()
  definition=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='Store')
  old=types.ModuleType('v4_material');old.__dict__.update(core.__dict__)
  exec(compile(ast.get_source_segment(source,definition),'v4 Store','exec'),old.__dict__)
  legacy=Path(self.tmp.name)/'legacy.sqlite3';s=old.Store(legacy)
  s.register_stock('14',3);s.assign_material(1,'10B')
  for p in ('1001','1002','1003'):s.observe(dict(machine=1,program=p,state='STOP',part_count='0'))
  s.switch_14(1);before=s.snapshot(1);s.close()
  s=sync.CommandStore(legacy)
  try:
   self.assertIn('mass_mode',s.snapshot(1));self.assertFalse(s.snapshot(1)['mass_mode'])
   self.assertEqual(s.snapshot(1)['parked'],before['parked'])
   s.observe(dict(machine=1,program='1003',state='STOP',part_count='0'));s.toggle_mass_mode(1)
   self.assertTrue(s.migration_backup.exists());self.assertEqual(s.db.execute('PRAGMA foreign_key_check').fetchall(),[])
  finally:s.close()
  with self.assertRaises(RuntimeError):old.Store(legacy)
