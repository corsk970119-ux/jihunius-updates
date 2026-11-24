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
 def require_height(self,app,height):
  # Font metrics differ between machines; the restore check needs a size above the content minimum.
  if app.minimum_height>height:self.skipTest('this font set needs {}px > {}px under test'.format(app.minimum_height,height))
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
  app=self.launch();self.require_height(app,920);app.window.geometry('1230x920+2180+120');app.window.update()
  self.assertEqual(self.geometry(app),(1230,920,2180,120))
  self.close_app(app)
  next_app=self.launch()
  self.assertEqual(self.geometry(next_app),(1230,920,2180,120))
  self.assertEqual(next_app._window_state.path.name,'jihunius.json')
  self.assertEqual(next_app.material_button.cget('text'),'소재 사용량 조사')
 def test_tray_flush_and_later_resize_are_preserved_without_sharing_pc_preferences(self):
  app=self.launch();self.require_height(app,900);app.window.geometry('1180x900+2100+95');app.window.update()
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
 def tall(self,app,extra=0):
  # 글꼴에 따라 최소 높이가 달라지므로, 그보다 조금 큰 높이를 그때그때 정합니다(건너뛰지 않고 항상 확인).
  return app.minimum_height+30+extra
 def test_handover_panel_width_is_not_remembered_as_the_window_size(self):
  # 사용자 보고(2026-11-16): "창 껐다 켜면 창 크기가 원래 설정해둔 것보다 커져 있음".
  # 인수인계 칸을 펼치면 창이 왼쪽으로 320 넓어지는데, 그 상태로 끄면 넓어진 크기가 기억돼 다시 켤 때마다 커졌다.
  app=self.launch();h=self.tall(app);app.window.geometry('1180x{}+2100+95'.format(h));app.window.update()
  app.toggle_handover();app.window.update()
  self.assertEqual(self.geometry(app),(1500,h,1780,95))                   # 펼친 동안에는 넓어져 있음
  self.close_app(app)
  path=Path(self.tmp.name)/'JihuniusSuite/window-state/jihunius.json'
  self.assertEqual(json.loads(path.read_text())['normal'],[2100,95,3280,95+h])   # 기억되는 것은 접었을 때의 크기
  again=self.launch()
  self.assertFalse(again.handover_expanded)
  self.assertEqual(self.geometry(again),(1180,h,2100,95))
  for _ in range(3):                                                      # 펼친 채 끄기를 되풀이해도 커지지 않음
   again.toggle_handover();again.window.update();self.close_app(again)
   again=self.launch()
   self.assertEqual(self.geometry(again),(1180,h,2100,95))
  self.close_app(again)
 def test_size_changed_while_the_handover_panel_is_open_keeps_only_the_base_part(self):
  app=self.launch();h=self.tall(app);app.window.geometry('1180x{}+2100+95'.format(h));app.window.update()
  app.toggle_handover();app.window.update()
  app.window.geometry('1600x{}+1700+60'.format(h+40));app.window.update()   # 펼친 채로 사용자가 크기를 바꿈
  app._hide_to_tray()
  path=Path(self.tmp.name)/'JihuniusSuite/window-state/jihunius.json'
  self.assertEqual(json.loads(path.read_text())['normal'],[2020,60,3300,60+h+40])   # 1600-320=1280, 왼쪽으로 밀린 320만큼 되돌림
  app.restore_from_tray();app.window.update()
  self.assertEqual(self.geometry(app),(1600,h+40,1700,60))                # 보이는 창은 그대로
  app.toggle_handover();app.window.update()                               # 접으면 그 크기로
  self.assertEqual(self.geometry(app),(1280,h+40,2020,60))
  self.close_app(app)
  again=self.launch();self.assertEqual(self.geometry(again),(1280,h+40,2020,60));self.close_app(again)
 def test_narrow_window_keeps_at_least_the_minimum_width_as_its_base(self):
  app=self.launch();h=self.tall(app);app.window.geometry('1000x{}+2100+95'.format(h));app.window.update()
  app.toggle_handover();app.window.update()
  self.assertEqual(self.geometry(app)[0],1320)                            # 펼치면 최소 1320
  self.close_app(app)
  again=self.launch();self.assertEqual(self.geometry(again),(1000,h,2100,95));self.close_app(again)
 def test_closed_panel_changes_nothing_about_what_is_remembered(self):
  app=self.launch();h=self.tall(app);app.window.geometry('1210x{}+140+70'.format(h));app.window.update()
  app.toggle_handover();app.window.update();app.toggle_handover();app.window.update()   # 펼쳤다 접음
  self.assertEqual(self.geometry(app),(1210,h,140,70))
  self.close_app(app)
  again=self.launch();self.assertEqual(self.geometry(again),(1210,h,140,70));self.close_app(again)
