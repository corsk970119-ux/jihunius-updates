import time,unittest
from unittest.mock import patch
import test_material_hold_ui as hold
from material_quick import QuickBridge

class MassModeUITests(unittest.TestCase):
 setUp=hold.MaterialHoldUITests.setUp
 cleanup=hold.MaterialHoldUITests.cleanup
 pump=hold.MaterialHoldUITests.pump
 prepare=hold.MaterialHoldUITests.prepare
 def test_adjacent_buttons_fit_and_pause_blocks_quick_inputs_then_resumes(self):
  self.prepare();self.assertIn('mass_mode',self.app.rows[1])
  self.root.geometry('1000x790');self.root.update()
  for row in self.app.rows.values():
   left,right=row['switch14'],row['mass_mode']
   self.assertGreaterEqual(right.winfo_rootx(),left.winfo_rootx()+left.winfo_width())
   self.assertGreaterEqual(right.winfo_width(),right.winfo_reqwidth())
   self.assertLessEqual(right.winfo_rootx()+right.winfo_width(),self.root.winfo_rootx()+1000)
  before=self.app.store.snapshot(1)['active_material']
  with patch('tkinter.messagebox.askokcancel',return_value=False):self.app.rows[1]['mass_mode'].invoke()
  self.assertEqual(self.session.outbox.items(),[])
  with patch('tkinter.messagebox.askokcancel',return_value=True):self.app.rows[1]['mass_mode'].invoke()
  self.pump(lambda:self.app.store.snapshot(1).get('mass_mode'))
  self.assertEqual(self.app.rows[1]['mass_mode'].cget('text'),'집계 재개')
  self.assertEqual(self.app.rows[1]['switch14'].cget('state'),'disabled')
  self.assertIn('양산품',self.app.rows[1]['program'].cget('text'))
  bridge=QuickBridge(self.app,self.tmp.name,'nonce');row=bridge.status()['rows'][0]
  self.assertFalse(row['can_defect']);self.assertFalse(row['can_rotate'])
  self.app.on_close();self.root.update();self.assertTrue(self.session.state['collection'])
  self.app.show_front()
  with patch('tkinter.messagebox.askokcancel',return_value=True):self.app.rows[1]['mass_mode'].invoke()
  self.pump(lambda:not self.app.store.snapshot(1).get('mass_mode'))
  self.assertEqual(self.app.store.snapshot(1)['active_material'],before)
  self.assertEqual(self.app.rows[1]['mass_mode'].cget('text'),'양산품 교체')
 def test_old_owner_and_disconnected_state_disable_mass_button(self):
  self.prepare();self.assertIn('mass_mode',self.app.rows[1])
  self.app.store.state['capabilities']=['temporary14'];self.app.refresh()
  self.assertEqual(self.app.rows[1]['mass_mode'].cget('state'),'disabled')
  self.app.store.state['capabilities'].append('mass_mode');self.app.connected=False;self.app.refresh()
  self.assertEqual(self.app.rows[1]['mass_mode'].cget('state'),'disabled')
