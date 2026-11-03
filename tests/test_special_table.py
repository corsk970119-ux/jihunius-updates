import importlib.util,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
class SpecialTableStoreTests(unittest.TestCase):
 def setUp(self):
  path=ROOT/'src/special_table.py';self.assertTrue(path.exists(),'special table implementation missing')
  spec=importlib.util.spec_from_file_location('special_table',path);self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.store=self.m.TableStore(Path(self.tmp.name)/'shared')
 def test_seed_preserves_source_rows_and_notes(self):
  s=self.store.sync()['state'];self.assertEqual(len(s['rows']),26)
  self.assertEqual(s['rows'][0]['cells'],['블루다이아RC','드릴값(위) 9.1(7.88)','스크류 길이 (1.75~1.8) /'])
  self.assertEqual(s['rows'][11]['cells'][0],'');self.assertEqual(s['rows'][-1]['cells'],['아름R','',''])
  self.assertIn('-0.25',s['notes']);self.assertNotIn('루나 RP',json.dumps(s,ensure_ascii=False))
 def test_different_pc_cell_edits_merge(self):
  row=self.store.sync()['state']['rows'][0]
  a={'kind':'cell','row':row['id'],'col':1,'base':row['cells'][1],'value':'first'};b={'kind':'cell','row':row['id'],'col':2,'base':row['cells'][2],'value':'second'}
  self.store.sync([a]);r=self.m.TableStore(self.store.folder).sync([b]);self.assertEqual(r['state']['rows'][0]['cells'][1:],['first','second']);self.assertEqual(r['conflicts'],[])
 def test_same_cell_conflict_preserves_shared_value(self):
  row=self.store.sync()['state']['rows'][0];op={'kind':'cell','row':row['id'],'col':1,'base':row['cells'][1],'value':'pc1'}
  self.store.sync([op]);r=self.store.sync([dict(op,value='pc2')]);self.assertEqual(r['state']['rows'][0]['cells'][1],'pc1');self.assertEqual(r['conflicts'],[self.m.operation_key(op)])
 def test_lost_reply_retries_idempotent_row_add_and_cell(self):
  self.store.sync();op={'kind':'add','row':{'id':'new-one','cells':['new','','']}}
  a=self.store.sync([op]);b=self.store.sync([op]);self.assertEqual(a['state'],b['state']);self.assertEqual(len(b['state']['rows']),27)
  op={'kind':'cell','row':'new-one','col':2,'base':'','value':'+0.03'};a=self.store.sync([op]);b=self.store.sync([op]);self.assertEqual(a['state'],b['state'])
 def test_invalid_shared_data_is_not_replaced(self):
  self.store.sync();self.store.path.write_text('{broken')
  with self.assertRaises(ValueError):self.store.sync()
  self.assertEqual(self.store.path.read_text(),'{broken')
 def test_draft_keeps_bases_and_only_latest_snapshot(self):
  d=self.m.PendingDraft(self.store.folder,base=Path(self.tmp.name)/'local');op={'kind':'notes','base':'before','value':'after','seq':4}
  d.save([op]);self.assertEqual(d.load(),[op]);d.save([dict(op,value='last')]);self.assertEqual(d.load()[0]['value'],'last');self.assertEqual(len(list(d.path.parent.glob('*.json'))),1);d.save([]);self.assertFalse(d.path.exists())
 def test_failed_atomic_replace_preserves_shared_data(self):
  s=self.store.sync()['state'];before=self.store.path.read_bytes();op={'kind':'notes','base':s['notes'],'value':'changed'};original=os.replace
  def fail(a,b):
   if Path(b)==self.store.path:raise OSError('injected write failure')
   return original(a,b)
  with patch.object(os,'replace',fail):
   with self.assertRaises(OSError):self.store.sync([op])
  self.assertEqual(self.store.path.read_bytes(),before)
 def test_oversized_paste_cannot_make_shared_file_unreadable(self):
  state=self.store.sync()['state'];before=self.store.path.read_bytes()
  with self.assertRaises(ValueError):self.store.sync([{'kind':'notes','base':state['notes'],'value':'x'*(4*1024*1024)}])
  self.assertEqual(self.store.path.read_bytes(),before);self.assertEqual(self.store.sync()['state'],state)
if __name__=='__main__':unittest.main()
