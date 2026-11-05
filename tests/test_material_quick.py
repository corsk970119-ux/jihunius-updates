import sys,tempfile,time,unittest,uuid
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from material_sync import Outbox,atomic_json
import test_material_full_reset_ui as reset_ui

class QuickInputTests(unittest.TestCase):
 def test_same_request_in_outbox_is_stored_once_and_conflict_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   box=Outbox(Path(d)/'pending.json');request={'id':'a'*32,'method':'defect','args':[1]}
   box.add('owner',request);box.add('owner',dict(request))
   self.assertEqual(len(box.items()),1)
   with self.assertRaises(ValueError):box.add('owner',dict(request,args=[2]))
 def test_quick_input_survives_host_restart_without_changing_request_identity(self):
  try:from material_quick import QuickChannel
  except ImportError:self.fail('Main material input channel missing')
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);session=root/'session';session.mkdir()
   manager=SimpleNamespace(sessions={'material':(session,'nonce')},running_keys=lambda:['material'])
   status={'nonce':'nonce','at':time.time(),'quick':dict(connected=True,client='c'*32,owner='o',epoch='e',at=time.time(),rows=[dict(machine=1,expected={'material':5})])}
   atomic_json(session/'material-status.json',status)
   channel=QuickChannel(manager,root/'quick-inputs.json');channel.poll()
   token=channel.submit('defect',1)
   first=channel.pending[token]['request']
   channel=QuickChannel(manager,root/'quick-inputs.json');channel.poll()
   self.assertEqual(channel.pending[token]['request'],first)
   import json
   sent=json.loads((session/('material-quick-'+token+'.json')).read_text())
   self.assertEqual(sent['request'],first)
   atomic_json(session/('material-result-'+token+'.json'),dict(nonce='nonce',id=token,result={'ok':True,'value':None}))
   _,results=channel.poll()
   self.assertEqual(results[0]['machine'],1);self.assertTrue(results[0]['result']['ok'])
   self.assertEqual(channel.pending,{})
   self.assertEqual(QuickChannel(manager,root/'quick-inputs.json').pending,{})

class QuickBridgeTests(unittest.TestCase):
 setUp=reset_ui.FullResetUITests.setUp
 cleanup=reset_ui.FullResetUITests.cleanup
 pump=reset_ui.FullResetUITests.pump
 def test_main_inputs_work_with_collection_off_and_popup_hidden(self):
  from material_quick import QuickChannel,QuickBridge
  folder=Path(self.tmp.name)/'off-control';folder.mkdir()
  self.app.control_folder=str(folder);self.app.control_nonce='nonce'
  self.app.quick_bridge=QuickBridge(self.app,folder,'nonce');self.app.poll_control()
  authority=self.session.coordinator.authority
  for program in ('1004','1005'):
   authority.samples.put(('sample','192.168.1.1',1,dict(machine=1,program=program,state='RUN',part_count='0'),time.time(),None,None))
  self.pump(lambda:self.app.store.snapshot(1)['good']==1)
  authority.set_collection(False)
  self.pump(lambda:not self.app.store.state['collection'])
  status=self.app.quick_bridge.status()['rows'][0]
  self.assertTrue(status['can_defect'])
  self.assertTrue(status['can_rotate'],'Manual replacement must remain available with collection OFF')
  self.app.on_close()
  manager=SimpleNamespace(sessions={'material':(folder,'nonce')},running_keys=lambda:['material'])
  channel=QuickChannel(manager,Path(self.tmp.name)/'off-inputs.json')
  self.pump(lambda:channel.poll()[0].get('connected'))
  results=[]
  def completed():
   _,items=channel.poll();results.extend(items);return bool(results)
  channel.submit('defect',1);channel.poll();self.pump(completed,6)
  self.assertTrue(results[-1]['result']['ok'],results)
  self.pump(lambda:self.app.store.snapshot(1)['defects']==1)
  original=self.app.store.snapshot(1)['active_material'];results.clear()
  self.pump(lambda:bool(channel.poll()[0].get('rows')) and channel.state['rows'][0].get('can_rotate'))
  channel.submit('rotate',1,confirmed=channel.rotation_context(1));channel.poll();self.pump(completed,6)
  self.assertTrue(results[-1]['result']['ok'],results)
  self.pump(lambda:self.app.store.snapshot(1)['active_material']!=original)
  self.assertEqual(self.app.store.inventory()[0]['quantity'],18)
  self.assertEqual(self.root.state(),'withdrawn')
  self.assertFalse(self.app.store.state['collection'])

 def test_hidden_popup_accepts_main_buttons_with_receipt_deduplication(self):
  from material_quick import QuickChannel,QuickBridge
  folder=Path(self.tmp.name)/'control';folder.mkdir()
  self.app.control_folder=str(folder);self.app.control_nonce='nonce'
  self.app.quick_bridge=QuickBridge(self.app,folder,'nonce')
  self.app.poll_control()
  authority=self.session.coordinator.authority
  for program in ('1004','1005'):
   authority.samples.put(('sample','192.168.1.1',1,dict(machine=1,program=program,state='STOP',part_count='0'),time.time(),None,None))
  self.pump(lambda:self.app.store.snapshot(1)['good']==1)
  self.assertNotIn('defect',self.app.rows[1])
  self.assertNotIn('rotate',self.app.rows[1])
  self.assertTrue(self.app.quick_bridge.status()['rows'][0]['can_defect'])
  self.assertTrue(self.app.quick_bridge.status()['rows'][0]['can_rotate'])
  self.app.on_close()
  manager=SimpleNamespace(sessions={'material':(folder,'nonce')},running_keys=lambda:['material'])
  channel=QuickChannel(manager,Path(self.tmp.name)/'host-inputs.json')
  self.pump(lambda:channel.poll()[0].get('connected'))
  token=channel.submit('defect',1);item=channel.pending[token];channel.poll()
  results=[]
  def completed():
   _,items=channel.poll();results.extend(items);return bool(results)
  self.pump(completed,6)
  self.assertTrue(results[-1]['result']['ok'])
  self.pump(lambda:self.app.store.snapshot(1)['defects']==1)
  self.assertFalse(self.app.quick_bridge.status()['rows'][0]['can_defect'])
  self.assertEqual(self.root.state(),'withdrawn')
  atomic_json(folder/('material-quick-'+token+'.json'),dict(nonce='nonce',**item))
  self.pump(lambda:(folder/('material-result-'+token+'.json')).exists(),6)
  self.assertEqual(self.session.coordinator.client.call('state')['rows'][0]['defects'],1)
  old=self.app.store.snapshot(1)['active_material'];results.clear();channel.poll()
  channel.submit('rotate',1);channel.poll();self.pump(completed,6)
  self.assertTrue(results[-1]['result']['ok'],results)
  self.pump(lambda:self.app.store.snapshot(1)['active_material']!=old)
  self.assertEqual(self.app.store.inventory()[0]['quantity'],18)
  self.assertEqual(self.root.state(),'withdrawn')

