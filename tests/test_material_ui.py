import sys, tempfile, time, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
try:import material_ui as ui
except ImportError:ui=None
import material_client as client
from test_material_sync import QuietCollector

class MaterialUITests(unittest.TestCase):
 def setUp(self):
  self.assertIsNotNone(ui,'Material popup integration missing')
  import tkinter as tk
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=tk.Tk();self.root.withdraw()
  self.session=client.ClientSession(Path(self.tmp.name)/'main',Path(self.tmp.name)/'share',QuietCollector)
  self.app=ui.SyncedApplication(self.root,self.session)
  self.root.deiconify()
  self.addCleanup(self.cleanup)
 def cleanup(self):
  self.app.jobs.close();self.session.close();self.session.thread.join(10)
  try:self.root.destroy()
  except Exception:pass
 def pump(self,predicate,seconds=4):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   self.root.update()
   if predicate():return
   time.sleep(.01)
  self.fail('UI state not reached')
 def test_beta_title_and_pc_switch_survive_hide(self):
  self.assertEqual(self.root.title(),'소재사용량조사(Beta)')
  self.assertIn('OFF',self.app.collection_button.cget('text'))
  self.app.toggle_collection()
  self.pump(lambda:self.session.state and self.session.state['collection'])
  self.pump(lambda:'ON' in self.app.collection_button.cget('text'))
  self.app.on_close();self.root.update()
  self.assertEqual(self.root.state(),'withdrawn')
  self.assertTrue(self.session.coordinator.authority.collection)
 def test_disconnected_actions_are_disabled_and_reports_do_not_claim_saved(self):
  self.root.update()
  self.assertFalse(self.app.action_availability(1)['defect'])
  self.app.defect(1)
  self.assertEqual(self.session.outbox.items(),[])
 def test_layout_fits_original_minimum_size(self):
  self.root.geometry('1000x790');self.root.update()
  for w in (self.app.collection_button,self.app.full_reset_button,self.app.rows[9]['material'],self.app.footer):
   self.assertGreater(w.winfo_width(),5)
   self.assertLessEqual(w.winfo_rootx()+w.winfo_width(),self.root.winfo_rootx()+self.root.winfo_width())
   self.assertLessEqual(w.winfo_rooty()+w.winfo_height(),self.root.winfo_rooty()+self.root.winfo_height())

 def test_offline_full_exit_preserves_exact_unconfirmed_request(self):
  from unittest.mock import patch
  r=dict(id='c'*32,client='sub',epoch='old',method='defect',args=[1],expected={'material':4},expires=1)
  self.session.outbox.add('owner',r);before=self.session.outbox.path.read_bytes()
  with patch('tkinter.messagebox.askyesno',return_value=True):self.app.shutdown()
  self.pump(lambda:self.app.closed,7)
  self.assertEqual(self.session.outbox.path.read_bytes(),before)
 def test_period_scope_stays_identifiable_and_remote_changes_mark_stale(self):
  self.app.toggle_collection();self.pump(lambda:self.app.connected and self.session.state['collection'])
  self.app.date_from.set('2026-01-01');self.app.date_to.set('2026-01-31')
  self.app.refresh_period();self.pump(lambda:self.app._period_report is not None)
  scope=self.app.period_scope.cget('text')
  self.assertIn('2026-01-01',scope);self.assertIn('2026-01-31',scope)
  self.app.date_to.set('2026-02-28');self.root.update()
  self.assertIn('다시 조회',self.app.period_scope.cget('text'))
  self.assertIn('2026-01-31',self.app.period_scope.cget('text'))
  self.app.date_to.set('2026-01-31');self.app.refresh_period();self.pump(lambda:self.app._period_report is not None)
  self.session.command('register_stock',['10Z',5],{})
  self.pump(lambda:'새 기록' in self.app.period_scope.cget('text'))
