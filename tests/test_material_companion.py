import hashlib,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from test_companion_save import module

class MaterialCompanionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.env=patch.dict(os.environ,LOCALAPPDATA=self.tmp.name);self.env.start();self.addCleanup(self.env.stop)
  data=b'# child\n';self.payload={'material':dict(data=data,sha256=hashlib.sha256(data).hexdigest(),title='소재재고조사(Beta)')}
  self.backend=Mock();self.process=Mock(pid=123);self.process.poll.return_value=None
  self.spawn=Mock(return_value=self.process)
  self.manager=module.CompanionManager(self.payload,self.tmp.name,_backend=self.backend,_popen=self.spawn)
 def test_material_button_toggles_owned_window_without_restoring_before_child_and_exit_is_distinct(self):
  self.assertTrue(hasattr(self.manager,'material_control'),'Material process control missing')
  self.manager.toggle('material');self.manager.toggle('material')
  folder,nonce=self.manager.sessions['material'];control=json.loads((folder/'material-control.json').read_text())
  self.assertEqual(control['action'],'toggle');self.assertEqual(control['nonce'],nonce)
  self.backend.focus.assert_not_called()
  self.manager.request_close_all()
  self.assertEqual(json.loads((folder/'material-control.json').read_text())['action'],'exit')
  self.backend.close.assert_not_called();self.process.kill.assert_not_called()
 def test_owner_autostart_is_hidden_but_sub_pc_does_not_start(self):
  self.assertTrue(hasattr(self.manager,'start_material_owner'),'Owner autostart missing')
  p=Path(self.tmp.name)/'MaterialCounter/sync-settings.json';p.parent.mkdir()
  p.write_text(json.dumps(dict(pc_id='a',enabled=False,owner=dict(owner_id='b'))))
  self.assertFalse(self.manager.start_material_owner());self.spawn.assert_not_called()
  p.write_text(json.dumps(dict(pc_id='a',enabled=False,owner=dict(owner_id='a'))))
  self.assertTrue(self.manager.start_material_owner())
  self.assertEqual(self.spawn.call_args.kwargs['env']['JIHUNIUS_MATERIAL_HIDDEN'],'1')
