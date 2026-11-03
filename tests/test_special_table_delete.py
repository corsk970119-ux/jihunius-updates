"""Shared row deletion must survive retries and concurrent editor actions."""
import copy,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import special_table as m

class SharedDeleteTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.store=m.TableStore(Path(self.temp.name)/'share');self.original=self.store.sync()['state']
  self.row=self.original['rows'][0]
 def delete(self,row=None):
  row=row or self.row
  return {'kind':'delete','row':row['id'],'base':list(row['cells'])}
 def apply(self,ops):
  try:return self.store.sync(ops)
  except ValueError as e:self.fail('Delete operation must be supported: '+str(e))
 def test_delete_is_shared_and_retry_does_not_change_revision(self):
  a=self.apply([self.delete()]);b=self.apply([self.delete()])
  self.assertEqual(a['state'],b['state']);self.assertEqual(a['conflicts'],[])
  self.assertNotIn(self.row['id'],[r['id'] for r in b['state']['rows']]);self.assertEqual(len(b['state']['rows']),25)
  self.assertEqual(b['state']['notes'],self.original['notes'])
 def test_concurrent_remote_edit_prevents_unseen_delete(self):
  self.store.sync([{'kind':'cell','row':self.row['id'],'col':2,'base':self.row['cells'][2],'value':'edited remotely'}])
  result=self.apply([self.delete()]);self.assertEqual(result['conflicts'],['delete:'+self.row['id']])
  self.assertEqual(result['state']['rows'][0]['cells'][2],'edited remotely')
 def test_stale_edit_and_stale_add_cannot_resurrect_deleted_row(self):
  row={'id':'added-row','cells':['new','','']};add={'kind':'add','row':row}
  self.store.sync([add]);self.apply([self.delete(row)])
  result=self.apply([copy.deepcopy(add)])
  self.assertEqual(result['conflicts'],['add:added-row']);self.assertNotIn('added-row',[r['id'] for r in result['state']['rows']])
  result=self.apply([{'kind':'cell','row':'added-row','col':1,'base':'','value':'late edit'}])
  self.assertEqual(result['conflicts'],['cell:added-row:1']);self.assertNotIn('added-row',[r['id'] for r in result['state']['rows']])
 def test_all_rows_deleted_stay_empty_on_reopen(self):
  self.apply([self.delete(r) for r in self.original['rows']]);self.assertEqual(m.TableStore(self.store.folder).sync()['state']['rows'],[])
 def test_pending_delete_keeps_base_through_local_recovery(self):
  draft=m.PendingDraft(self.store.folder,base=Path(self.temp.name)/'local');op=self.delete();draft.save([op])
  try:loaded=draft.load()
  except ValueError as e:self.fail('Delete must restore: '+str(e))
  self.assertEqual(loaded,[op]);self.apply(loaded)

if __name__=='__main__':unittest.main()
