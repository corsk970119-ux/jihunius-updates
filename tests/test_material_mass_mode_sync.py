import time,unittest
import test_material_sync as service

class MassModeServiceTests(unittest.TestCase):
 setUp=service.ServiceTests.setUp
 feed=service.ServiceTests.feed
 command=service.ServiceTests.command
 def test_checkpoint_pause_and_resume_do_not_count_mass_program_boundary(self):
  self.a.set_collection(True);self.feed('1001');self.feed('1002')
  result=self.c.call('command',self.command('toggle_mass_mode'))
  self.assertTrue(result['ok'],result)
  self.feed('7001');self.feed('7002')
  # Fresh checkpoint already displays the restored custom program, not the cached mass job.
  self.a.collector.program='1002'
  self.assertTrue(self.c.call('command',self.command('toggle_mass_mode'))['ok'])
  self.assertEqual(self.c.call('state')['rows'][0]['good'],1)
  self.feed('3999');self.feed('1002')
  self.assertEqual(self.c.call('state')['rows'][0]['good'],2)
 def test_unknown_checkpoint_and_collection_off_allow_manual_mode_boundaries(self):
  self.a.set_collection(True);self.feed('1001')
  self.assertIn('mass_mode',self.c.call('state')['capabilities'])
  def running(n,token):
   self.a.samples.put(('sample','192.168.1.10',1,dict(machine=n,program='1001',state='UNKNOWN',part_count='0'),time.time(),token,None))
  self.a.collector.checkpoint=running
  self.assertTrue(self.c.call('command',self.command('toggle_mass_mode'))['ok'])
  self.assertTrue(self.c.call('state')['rows'][0]['mass_mode'])
  self.assertTrue(self.c.call('state')['rows'][0]['gap'])
  self.a.set_collection(False)
  self.assertTrue(self.c.call('command',self.command('toggle_mass_mode'))['ok'])
  self.assertFalse(self.c.call('state')['rows'][0]['mass_mode'])
