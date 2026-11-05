import sys,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import test_material_sync as service_tests
from material_sync import RPCClient

class MaterialHoldServiceTests(unittest.TestCase):
 setUp=service_tests.ServiceTests.setUp
 feed=service_tests.ServiceTests.feed
 command=service_tests.ServiceTests.command

 def setup_rods(self):
  self.a.set_collection(True);self.feed('1001');self.feed('1002')
  request=self.command('register_stock',['14',3]);self.assertTrue(self.c.call('command',request)['ok'])

 def test_sub_pc_switch_roundtrip_and_retry_share_one_rod_identity(self):
  self.setup_rods();other=RPCClient('127.0.0.1',self.a.port,'a'*64)
  original=self.c.call('state')['rows'][0]
  self.assertIn('temporary14',self.c.call('state')['capabilities'])
  request=self.command('switch_14');result=other.call('command',request)
  self.assertTrue(result['ok'],result);self.assertEqual(other.call('command',request),result)
  state=self.c.call('state');fourteen=state['rows'][0]['active_material']
  self.assertEqual(state['rows'][0]['parked']['material_id'],original['active_material'])
  self.feed('1003');self.feed('1004')
  self.assertTrue(other.call('command',self.command('switch_14'))['ok'])
  row=self.c.call('state')['rows'][0]
  self.assertEqual((row['active_material'],row['good']),(original['active_material'],original['good']))
  self.assertEqual((row['parked']['material_id'],row['parked']['good']),(fourteen,2))
  self.assertEqual(self.c.call('state')['inventory'][3]['quantity'],2)

 def test_checkpoint_rejects_unknown_machine_state_and_collection_off_blocks_switch(self):
  self.setup_rods();before=self.c.call('state')['rows'][0]['active_material']
  def running(n,token):
   self.a.samples.put(('sample','192.168.1.10',1,dict(machine=n,program='1002',state='UNKNOWN',part_count='0'),time.time(),token,None))
  self.a.collector.checkpoint=running
  result=self.c.call('command',self.command('switch_14'))
  self.assertFalse(result['ok']);self.assertEqual(self.c.call('state')['rows'][0]['active_material'],before)
  self.a.set_collection(False)
  self.assertFalse(self.c.call('command',self.command('switch_14'))['ok'])
  self.assertEqual(self.c.call('state')['inventory'][3]['quantity'],3)
