import time,unittest
from unittest.mock import patch
import test_material_hold as hold
import test_material_sync as service
import test_material_hold_ui as hold_ui


class RunningSwitchStoreTests(unittest.TestCase):
 setUp=hold.MaterialHoldTests.setUp
 feed=hold.MaterialHoldTests.feed
 stock=hold.MaterialHoldTests.stock
 def test_running_14_switch_and_return_keep_existing_counts_and_one_stock_debit(self):
  self.feed(3,state='RUN')
  self.s.switch_14(1,self.at+.1)
  self.assertEqual(self.s.snapshot(1)['parked']['good'],3)
  self.feed(2,state='RUN');self.s.switch_14(1,self.at+.1)
  row=self.s.snapshot(1)
  self.assertEqual((row['active_material'],row['good'],row['parked']['good']),(self.original,3,2))
  self.assertEqual(self.stock('14'),19)
  with self.assertRaises(ValueError):self.s.rotate(1,self.at+.2)
 def test_running_pause_resume_uses_current_program_as_baseline_without_extra_count(self):
  self.feed(4,state='RUN');self.s.toggle_mass_mode(1,self.at+.1)
  self.feed(5,state='RUN');self.s.toggle_mass_mode(1,self.at+.1)
  self.s.observe(dict(machine=1,program=str(self.program),state='RUN',part_count='0'),self.at+.2)
  self.assertEqual(self.s.snapshot(1)['good'],4)
  self.feed(2,state='RUN');self.assertEqual(self.s.snapshot(1)['good'],6)
  self.assertEqual(self.stock('10Z'),19)


class RunningSwitchServiceTests(unittest.TestCase):
 setUp=service.ServiceTests.setUp
 feed=service.ServiceTests.feed
 command=service.ServiceTests.command
 def test_running_checkpoint_applies_both_switches_but_stale_or_missing_sample_never_does(self):
  self.a.set_collection(True);self.feed('1001');self.feed('1002')
  self.assertTrue(self.c.call('command',self.command('register_stock',['14',3]))['ok'])
  self.program='1003'
  def running(n,token):
   self.a.samples.put(('sample','192.168.1.10',1,dict(machine=n,program=self.program,state='RUN',part_count='0'),time.time(),token,None))
  self.a.collector.checkpoint=running
  self.assertTrue(self.c.call('command',self.command('switch_14'))['ok'])
  row=self.c.call('state')['rows'][0]
  self.assertEqual((row['good'],row['parked']['good']),(0,2))
  self.program='1004'
  self.assertTrue(self.c.call('command',self.command('toggle_mass_mode'))['ok'])
  self.assertEqual(self.c.call('state')['rows'][0]['good'],1)
  self.program='7001'
  self.assertTrue(self.c.call('command',self.command('toggle_mass_mode'))['ok'])
  self.assertEqual(self.c.call('state')['rows'][0]['good'],1)
  def stale(n,token):
   self.a.samples.put(('sample','192.168.1.10',1,dict(machine=n,program='7001',state='RUN',part_count='0'),time.time()-30,token,None))
  self.a.collector.checkpoint=stale
  self.assertFalse(self.c.call('command',self.command('switch_14'))['ok'])
  self.assertEqual(self.c.call('state')['rows'][0]['material_type'],'14')
  def missing(n,token):self.a.samples.put(('sample','192.168.1.10',1,None,time.time(),token,'unavailable'))
  self.a.collector.checkpoint=missing
  self.assertFalse(self.c.call('command',self.command('toggle_mass_mode'))['ok'])
  self.assertFalse(self.c.call('state')['rows'][0]['mass_mode'])


class RunningSwitchUITests(unittest.TestCase):
 setUp=hold_ui.MaterialHoldUITests.setUp
 cleanup=hold_ui.MaterialHoldUITests.cleanup
 pump=hold_ui.MaterialHoldUITests.pump
 prepare=hold_ui.MaterialHoldUITests.prepare
 def test_running_buttons_accept_confirmed_transitions_and_old_owner_remains_guarded(self):
  self.prepare();authority=self.session.coordinator.authority
  def running(n,token):
   authority.samples.put(('sample','192.168.1.10',1,dict(machine=n,program='1003',state='RUN',part_count='0'),time.time(),token,None))
  authority.collector.checkpoint=running;running(1,None)
  self.pump(lambda:self.app.store.snapshot(1)['state']=='RUN')
  self.assertEqual(self.app.rows[1]['switch14'].cget('state'),'normal')
  self.assertEqual(self.app.rows[1]['mass_mode'].cget('state'),'normal')
  with patch('tkinter.messagebox.askokcancel',return_value=True):self.app.rows[1]['switch14'].invoke()
  self.pump(lambda:self.app.store.snapshot(1)['material_type']=='14')
  with patch('tkinter.messagebox.askokcancel',return_value=True):self.app.rows[1]['mass_mode'].invoke()
  self.pump(lambda:self.app.store.snapshot(1)['mass_mode'])
  with patch('tkinter.messagebox.askokcancel',return_value=True):self.app.rows[1]['mass_mode'].invoke()
  self.pump(lambda:not self.app.store.snapshot(1)['mass_mode'])
  self.app.store.state['capabilities']=['temporary14','mass_mode'];self.app.refresh()
  self.assertEqual(self.app.rows[1]['switch14'].cget('state'),'disabled')
  self.assertEqual(self.app.rows[1]['mass_mode'].cget('state'),'disabled')
