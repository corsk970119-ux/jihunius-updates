import gc,time,unittest
from unittest.mock import patch
import test_material_full_reset_ui as reset_ui

class MaterialHoldUITests(unittest.TestCase):
 setUp=reset_ui.FullResetUITests.setUp
 pump=reset_ui.FullResetUITests.pump
 def cleanup(self):
  reset_ui.FullResetUITests.cleanup(self)
  self.app.jobs.thread.join(2);self.app=None;self.root=None;self.session=None;gc.collect()
 def prepare(self):
  self.assertIn('switch14',self.app.rows[1])
  self.session.command('register_stock',['14',5],{})
  self.pump(lambda:self.app.store.inventory()[3]['quantity']==5)
  # Keep a real STOP checkpoint for the selected host row.
  self.session.coordinator.authority.collector.program='1003'
  self.session.coordinator.authority.samples.put(('sample','192.168.1.10',1,
   dict(machine=1,program='1003',state='STOP',part_count='0'),time.time(),None,None))
  self.pump(lambda:self.app.rows[1]['switch14'].cget('state')=='normal')

 def test_current_totals_has_one_toggle_per_machine_and_minimum_layout(self):
  self.assertTrue(all('switch14' in row for row in self.app.rows.values()))
  self.root.geometry('1000x790');self.root.update()
  for row in self.app.rows.values():
   self.assertNotIn('rotate',row);self.assertNotIn('defect',row)
   w=row['switch14'];self.assertEqual(w.cget('text'),'14파이 교체')
   self.assertGreaterEqual(w.winfo_width(),w.winfo_reqwidth())
   self.assertLessEqual(w.winfo_rootx()+w.winfo_width(),self.root.winfo_rootx()+1000)
   self.assertLessEqual(w.winfo_rooty()+w.winfo_height(),self.root.winfo_rooty()+790)

 def test_confirmation_cancel_then_saved_label_and_return_keep_counts(self):
  self.prepare();old=self.app.store.snapshot(1)['active_material']
  with patch('tkinter.messagebox.askokcancel',return_value=False):self.app.rows[1]['switch14'].invoke()
  self.assertEqual(self.session.outbox.items(),[])
  with patch('tkinter.messagebox.askokcancel',return_value=True):self.app.rows[1]['switch14'].invoke()
  self.pump(lambda:self.app.rows[1]['switch14'].cget('text')=='원소재로 복귀')
  self.assertEqual(self.app.store.snapshot(1)['parked']['material_id'],old)
  self.assertIn('보관',self.app.rows[1]['material'].cget('text'))
  self.app.last_click.clear()
  with patch('tkinter.messagebox.askokcancel',return_value=True):self.app.rows[1]['switch14'].invoke()
  self.pump(lambda:self.app.store.snapshot(1)['active_material']==old)
  self.assertEqual(self.app.rows[1]['switch14'].cget('text'),'14파이 교체')
  self.assertEqual(self.app.store.inventory()[3]['quantity'],4)

 def test_offline_and_old_owner_cannot_offer_unsupported_switch(self):
  self.prepare();self.app.connected=False;self.app.failed_storage=True;self.app.refresh()
  self.assertEqual(self.app.rows[1]['switch14'].cget('state'),'disabled')
  self.app.connected=True;self.app.failed_storage=False
  self.app.store.state.pop('capabilities',None);self.app.refresh()
  self.assertEqual(self.app.rows[1]['switch14'].cget('state'),'disabled')
