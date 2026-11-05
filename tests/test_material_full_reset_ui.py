import sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import material_counter as core
import material_client as client
import material_sync as sync
import material_ui as ui
from test_material_sync import QuietCollector
import test_material_ui as ui_tests

class FullResetUITests(unittest.TestCase):
 pump=ui_tests.MaterialUITests.pump
 def setUp(self):
  import tkinter as tk
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  folder=Path(self.tmp.name);main=folder/'main'
  s=sync.CommandStore(main/'counter.sqlite3')
  s.register_stock('10Z',20);s.assign_material(1,'10Z')
  for program in ('1001','1002','1003'):s.observe(dict(machine=1,program=program,state='STOP',part_count='0'))
  s.defect(1);s.rotate(1);s.close()
  self.network=patch.object(client,'lan_address',return_value='127.0.0.1');self.network.start();self.addCleanup(self.network.stop)
  self.session=client.ClientSession(main,folder/'share',QuietCollector)
  self.root=tk.Tk();self.app=ui.SyncedApplication(self.root,self.session)
  self.sub=None;self.subroot=None
  self.addCleanup(self.cleanup)
  self.app.toggle_collection();self.pump(lambda:self.app.connected and self.session.state['collection'])
 def cleanup(self):
  for app,session,root in ((getattr(self,'subapp',None),self.sub,self.subroot),(self.app,self.session,self.root)):
   if app:app.jobs.close()
   if session:session.close();session.thread.join(10)
   if root:
    try:root.destroy()
    except Exception:pass
 def test_reset_button_clears_both_pcs_statistics_and_preserves_collection(self):
  import tkinter as tk
  self.sub=client.ClientSession(Path(self.tmp.name)/'sub',Path(self.tmp.name)/'share',QuietCollector)
  self.pump(lambda:self.sub.state is not None)
  self.app.refresh_period()
  self.pump(lambda:self.app._period_report is not None)
  old_report=self.app._period_report
  self.assertEqual(old_report['totals']['consumed_rods'],1)
  self.app.refresh_history(force=True);self.app.refresh_inventory()
  self.pump(lambda:not self.app.job_callbacks and self.app.history_tree.get_children() and self.app.event_tree.get_children() and self.app.stock_tree.get_children())
  self.assertTrue(hasattr(self.app,'full_reset_button'),'Always-visible full reset button missing')
  with patch('tkinter.messagebox.askyesno',return_value=False):self.app.full_reset_button.invoke()
  self.assertEqual(self.session.state['inventory'][0]['quantity'],19)
  epoch=self.session.state['epoch']
  self.pump(lambda:not self.app.job_callbacks)
  with patch('tkinter.messagebox.askyesno',return_value=True):self.app.full_reset_button.invoke()
  self.pump(lambda:self.session.state['epoch']!=epoch and self.sub.state['epoch']!=epoch,6)
  self.pump(lambda:not self.app.resetting and self.app._period_report is None)
  self.assertTrue(self.session.state['collection'])
  self.assertFalse(self.sub.coordinator.settings['enabled'])
  self.assertTrue(all(r['quantity'] is None for r in self.sub.state['inventory']))
  self.assertEqual(self.sub.state['rows'][0]['total'],0)
  for app in (self.app,):
   self.assertTrue(all(r['quantity'] is None for r in app.store.inventory()))
   self.assertEqual(app.store.snapshot(1)['total'],0)
   for tree in (app.history_tree,app.event_tree,app.stock_tree,app.report_tree,app.daily_tree):self.assertEqual(tree.get_children(),())
  # A query started before reset must not restore old totals on either PC.
  self.app._render_period(old_report)
  self.assertIsNone(self.app._period_report)
  self.assertEqual(self.app.report_tree.get_children(),())

