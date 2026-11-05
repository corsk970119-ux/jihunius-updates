import gc,json,os,tempfile,tkinter as tk,unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import Mock,patch
from test_host_stability import load_app


class MainWindowPlacementTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.stack=ExitStack();self.addCleanup(self.stack.close)
  self.stack.enter_context(patch.dict(os.environ,LOCALAPPDATA=self.tmp.name,APPDATA=self.tmp.name))
  self.m=load_app();self.apps=[];self.addCleanup(self.cleanup)
  self.stack.enter_context(patch.object(self.m.MachineMonitor,'start'))
  self.stack.enter_context(patch.object(self.m.IntegrationApp,'refresh_destination'))
  self.stack.enter_context(patch.object(self.m.IntegrationApp,'refresh_handover'))
  tray=Mock();tray.start.return_value=True;tray.available=True
  self.stack.enter_context(patch.object(self.m,'SuiteWindowsTray',return_value=tray))
  def children(*args,**kwargs):
   value=Mock();value.running_keys.return_value=[];value.material_visible.return_value=False;value.sessions={};return value
  self.stack.enter_context(patch.object(self.m,'SuiteCompanionManager',side_effect=children))
 def launch(self):
  root=tk.Tk();app=self.m.IntegrationApp(root);self.apps.append(app);root.update();return app
 def geometry(self,app):
  r=app.window;return (r.winfo_width(),r.winfo_height(),r.winfo_x(),r.winfo_y())
 def close_app(self,app):
  # Test creates several Tk interpreters in one process; retire old test timers.
  for timer in app.window.tk.call('after','info'):
   app.window.after_cancel(timer)
  app._finish_suite_shutdown()
 def cleanup(self):
  for app in self.apps:
   if not app._suite_stopped:self.close_app(app)
  self.apps.clear();self.m=None;gc.collect()
 def test_main_window_restores_last_size_and_right_monitor_position_after_full_exit(self):
  app=self.launch();app.window.geometry('1230x920+2180+120');app.window.update()
  self.assertEqual(self.geometry(app),(1230,920,2180,120))
  self.close_app(app)
  next_app=self.launch()
  self.assertEqual(self.geometry(next_app),(1230,920,2180,120))
  self.assertEqual(next_app._window_state.path.name,'jihunius.json')
  self.assertEqual(next_app.material_button.cget('text'),'소재 사용량 조사(Beta)')
 def test_tray_flush_and_later_resize_are_preserved_without_sharing_pc_preferences(self):
  app=self.launch();app.window.geometry('1180x900+2100+95');app.window.update()
  app._hide_to_tray()
  path=Path(self.tmp.name)/'JihuniusSuite/window-state/jihunius.json'
  self.assertTrue(path.exists(),'Hiding must flush normal bounds before losing visible state')
  self.assertEqual(json.loads(path.read_text())['normal'],[2100,95,3280,995])
  app.restore_from_tray();app.window.update()
  self.assertEqual(self.geometry(app),(1180,900,2100,95))
  app.window.geometry('1260x940+80+70');app.window.update();self.close_app(app)
  next_app=self.launch();self.assertEqual(self.geometry(next_app),(1260,940,80,70))
  self.close_app(next_app)
  with patch.dict(os.environ,LOCALAPPDATA=str(Path(self.tmp.name)/'other-pc')):
   other=self.launch();self.assertEqual(other.window.winfo_width(),1120)
   self.assertNotEqual(self.geometry(other),(1260,940,80,70))
   self.close_app(other)
