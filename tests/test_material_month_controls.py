from datetime import datetime
from unittest.mock import patch
import gc,unittest
import test_material_ui as ui_tests


class MaterialMonthTests(unittest.TestCase):
 setUp=ui_tests.MaterialUITests.setUp
 pump=ui_tests.MaterialUITests.pump

 def cleanup(self):
  # Repeated Tk roots in one test process must be reclaimed on their creator
  # thread, before a later test's collector/report thread triggers cyclic GC.
  ui_tests.MaterialUITests.cleanup(self)
  self.app.jobs.thread.join(2)
  self.app=None;self.root=None;self.session=None
  gc.collect()

 def test_whole_month_and_year_navigation_preserve_machine_and_query_once(self):
  self.app.period_machine.set('3호기')
  with patch.object(self.app,'refresh_period') as refresh:
   self.app.select_period_month(2024,2)
   self.assertEqual((self.app.date_from.get(),self.app.date_to.get()),('2024-02-01','2024-02-29'))
   begin,end,machine=self.app.period_range()
   self.assertEqual(datetime.fromtimestamp(end),datetime(2024,3,1))
   self.assertEqual(machine,3);refresh.assert_called_once()
   refresh.reset_mock();self.app.select_period_month(2026,12);self.app.shift_period_month(1)
   self.assertEqual((self.app.date_from.get(),self.app.date_to.get()),('2027-01-01','2027-01-31'))
   self.app.shift_period_month(-1)
   self.assertEqual(self.app.date_from.get(),'2026-12-01')
   self.assertEqual(refresh.call_count,3)
   self.app.select_period_month(2025,2)
   self.assertEqual(self.app.date_to.get(),'2025-02-28')

 def test_manual_range_and_invalid_input_do_not_trigger_background_queries(self):
  with patch.object(self.app,'refresh_period') as refresh:
   self.app.date_from.set('2026-09-12');self.app.date_to.set('2026-10-03')
   self.assertEqual(self.app.period_month_button.cget('text'),'월 선택')
   refresh.assert_not_called()
   self.app.shift_period_month(1)
   self.assertEqual((self.app.date_from.get(),self.app.date_to.get()),('2026-10-01','2026-10-31'))
   self.app.date_from.set('unfinished');self.app.date_to.set('2024-02-17')
   self.app.shift_period_month(0)
   self.assertEqual(self.app.date_to.get(),'2024-02-29')

 def test_month_picker_cancel_and_choose_are_distinct(self):
  self.app.tabs.select(self.app.period_tab);self.root.geometry('1000x790');self.root.update()
  self.app.date_from.set('2026-11-06');self.app.date_to.set('2026-11-06')
  with patch.object(self.app,'refresh_period') as refresh:
   self.app.open_period_month();self.root.update()
   dialog=self.app._month_dialog
   self.app.open_period_month();self.assertIs(self.app._month_dialog,dialog)
   dialog.event_generate('<Escape>');self.root.update()
   self.assertFalse(dialog.winfo_exists());refresh.assert_not_called()
   self.assertEqual(self.app.date_from.get(),'2026-11-06')
   self.app.open_period_month();self.root.update()
   self.app._month_buttons[1].invoke();self.root.update()
   self.assertEqual((self.app.date_from.get(),self.app.date_to.get()),('2026-02-01','2026-02-28'))
   refresh.assert_called_once();self.assertIsNone(self.root.grab_current())
  for w in self.app.period_controls.winfo_children():
   self.assertGreater(w.winfo_width(),5)
   self.assertGreaterEqual(w.winfo_width(),w.winfo_reqwidth())
   self.assertLessEqual(w.winfo_rootx()+w.winfo_width(),self.root.winfo_rootx()+self.root.winfo_width())
   self.assertGreaterEqual(w.winfo_rootx(),self.root.winfo_rootx())

 def test_current_month_preset_includes_last_day_and_today_remains_single_day(self):
  now=datetime.now()
  with patch.object(self.app,'refresh_period') as refresh:
   self.app.period_preset('month')
   begin,end,_=self.app.period_range()
   self.assertEqual(datetime.fromtimestamp(begin),datetime(now.year,now.month,1))
   self.assertEqual(datetime.fromtimestamp(end).day,1)
   self.assertGreater(datetime.fromtimestamp(end),now)
   self.app.period_preset('today')
   self.assertEqual(self.app.date_from.get(),now.strftime('%Y-%m-%d'))
   self.assertEqual(self.app.date_from.get(),self.app.date_to.get())
   self.assertEqual(refresh.call_count,2)

 def test_month_selection_uses_existing_async_report_and_machine_filter(self):
  self.app.toggle_collection();self.pump(lambda:self.app.connected and self.session.state['collection'])
  self.app.period_machine.set('2호기');self.app.select_period_month(2024,2)
  self.pump(lambda:self.app._period_report is not None)
  report=self.app._period_report
  self.assertEqual((datetime.fromtimestamp(report['start']),datetime.fromtimestamp(report['end']),report['machine']),
                   (datetime(2024,2,1),datetime(2024,3,1),2))
