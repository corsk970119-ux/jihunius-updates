import time,unittest,uuid
from pathlib import Path
import test_material_ui as ui_tests
import material_counter as core
from material_sync import atomic_json

class MaterialFrontUsageTests(unittest.TestCase):
 setUp=ui_tests.MaterialUITests.setUp
 cleanup=ui_tests.MaterialUITests.cleanup
 pump=ui_tests.MaterialUITests.pump

 def test_current_dashboard_has_no_duplicate_input_buttons(self):
  for row in self.app.rows.values():
   self.assertNotIn('rotate',row)
   self.assertNotIn('defect',row)
   self.assertIn('material',row)
   self.assertIn('defects',row)

 def test_show_command_restores_window_and_keeps_open_on_repeat(self):
  folder=Path(self.tmp.name)/'control';folder.mkdir()
  self.app.control_folder=str(folder);self.app.control_nonce='nonce'
  self.root.geometry('1000x790+40+60');self.root.update()
  self.app.on_close()
  def show():
   token=uuid.uuid4().hex
   atomic_json(folder/'material-control.json',dict(nonce='nonce',id=token,action='show',expires=time.time()+30))
   return token
  show();self.app.poll_control();self.root.update()
  self.assertEqual(self.root.state(),'normal')
  self.assertTrue(self.session.visible)
  self.assertEqual((self.root.winfo_x(),self.root.winfo_y()),(40,60))
  token=show();self.pump(lambda:self.app._control_id==token)
  self.assertEqual(self.root.state(),'normal')
  self.assertIs(self.root.focus_get(),self.root)
  dialog=self.app.tk.Toplevel(self.root);entry=self.app.tk.Entry(dialog);entry.pack();dialog.grab_set()
  token=show();self.pump(lambda:self.app._control_id==token)
  self.assertIs(self.root.grab_current(),dialog)
  self.assertIs(self.root.focus_get().winfo_toplevel(),dialog)
  dialog.destroy();self.app.on_close();self.root.update()
  self.assertEqual(self.root.state(),'withdrawn')

 def test_diameter_cards_match_completed_rods_and_clear_after_reset(self):
  for key in ('diameter10','diameter12','diameter14'):self.assertIn(key,self.app.period_cards)
  store=core.Store(Path(self.tmp.name)/'report-fixture.sqlite3');self.addCleanup(store.close)
  t=time.time()-200
  for kind in core.MATERIAL_TYPES:store.register_stock(kind,20,t)
  for machine,kind,count in ((1,'10Z',2),(2,'10B',3),(3,'12',1),(4,'14',4)):
   store.assign_material(machine,kind,t)
   for i in range(count):
    at=t+machine*10+i
    store.observe(dict(machine=machine,program=str(1001+i),state='STOP',part_count='0'),at)
    # The newly selected material must not replace the ended rod's diameter.
    if machine==1 and i==count-1:store.set_next_type(machine,'14',at)
    store.rotate(machine,at+.1,early=machine==2)
  report=store.period_report(t,t+100)
  self.app._render_period(report)
  for key,value in (('diameter10','5 봉'),('diameter12','1 봉'),('diameter14','4 봉')):
   self.assertEqual(self.app.period_cards[key][0].cget('text'),value)
  self.assertIn('Z급 2봉',self.app.period_cards['diameter10'][1].cget('text'))
  self.assertIn('B급 3봉',self.app.period_cards['diameter10'][1].cget('text'))
  self.app._render_period(store.period_report(t+20,t+30))
  self.assertEqual(self.app.period_cards['diameter10'][0].cget('text'),'3 봉')
  self.assertEqual(self.app.period_cards['diameter14'][0].cget('text'),'0 봉')
  self.app._render_period(store.period_report(t,t+100,3))
  self.assertEqual(self.app.period_cards['diameter10'][0].cget('text'),'0 봉')
  self.assertEqual(self.app.period_cards['diameter12'][0].cget('text'),'1 봉')
  self.app._clear_reset_views()
  for key in ('diameter10','diameter12','diameter14'):
   self.assertEqual(self.app.period_cards[key][0].cget('text'),'—')
