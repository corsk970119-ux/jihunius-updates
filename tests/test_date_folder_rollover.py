"""날짜 폴더 칸 자동 변경(사용자 요청 2026-11-25): 켜 둔 채로 오전 8시를 넘기면 그날 날짜로 바뀝니다.

켤 때 오늘 날짜를 넣는 것, 연도·번호 목록·작업 모드, 가져오기 동작은 그대로입니다.
"""
import os
import time
import tkinter as tk
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import Mock, patch

import test_main_window_placement as placement
from test_host_stability import load_app


class RolloverDayTests(unittest.TestCase):
    def setUp(self):
        self.m = load_app()

    def test_the_day_starts_at_eight_in_the_morning(self):
        day = self.m.date_folder_day
        self.assertEqual(self.m.DATE_FOLDER_ROLLOVER_HOUR, 8)
        for now, expected in ((datetime(2026, 11, 25, 7, 59, 59), date(2026, 11, 24)),   # 8시 전: 아직 전날
                              (datetime(2026, 11, 25, 8, 0, 0), date(2026, 11, 25)),     # 8시 정각부터 그날
                              (datetime(2026, 11, 25, 23, 59, 59), date(2026, 11, 25)),
                              (datetime(2026, 11, 26, 0, 0, 0), date(2026, 11, 25)),     # 자정을 넘겨도 8시 전까지는 전날
                              (datetime(2026, 12, 1, 7, 0, 0), date(2026, 11, 30)),      # 달이 바뀌는 날
                              (datetime(2026, 12, 1, 8, 0, 0), date(2026, 12, 1)),
                              (datetime(2027, 1, 1, 7, 59, 59), date(2026, 12, 31)),     # 해가 바뀌는 날
                              (datetime(2027, 1, 1, 8, 0, 0), date(2027, 1, 1)),
                              (datetime(2028, 2, 29, 8, 0, 0), date(2028, 2, 29))):      # 윤년
            self.assertEqual(day(now), expected, now)
        self.assertIn(day(), (day(datetime.now()), date.today()))


@unittest.skipUnless(os.environ.get('DISPLAY') or os.name == 'nt', 'requires Tk display')
class DateFolderRolloverTests(unittest.TestCase):
    setUp = placement.MainWindowPlacementTests.setUp
    cleanup = placement.MainWindowPlacementTests.cleanup
    close_app = placement.MainWindowPlacementTests.close_app

    def launch(self, started=datetime(2026, 11, 24, 9, 30)):
        """11월 24일 오전 9시 반에 켠 것처럼: 날짜 폴더 칸은 11.24."""
        root = tk.Tk()
        app = self.m.IntegrationApp(root)
        self.apps.append(app)
        app.messagebox = Mock()
        app.folder_input.delete(0, 'end')
        app.folder_input.insert(0, self.m.single_import_folder_text(started.date()))
        app.folder_day = self.m.date_folder_day(started)
        root.update()
        return app

    def log_text(self, app):
        return app.log.get('1.0', 'end')

    def test_starting_the_program_still_puts_today_in_the_box(self):
        root = tk.Tk(); app = self.m.IntegrationApp(root); self.apps.append(app)
        today = datetime.now()
        self.assertEqual(app.folder_input.get(), '{}.{:02d}'.format(today.month, today.day))
        self.assertIn(app.folder_day, (self.m.date_folder_day(today), self.m.date_folder_day()))
        self.assertFalse(app.roll_date_folder(today))          # 켠 직후에는 바꿀 것이 없음
        self.assertNotIn('날짜 폴더 자동 변경', self.log_text(app))

    def test_box_changes_to_the_new_day_at_eight_and_only_then(self):
        app = self.launch()
        for now in (datetime(2026, 11, 24, 9, 31), datetime(2026, 11, 24, 23, 59, 59),
                    datetime(2026, 11, 25, 0, 0), datetime(2026, 11, 25, 7, 59, 59)):
            self.assertFalse(app.roll_date_folder(now), now)
            self.assertEqual(app.folder_input.get(), '11.24', now)
        self.assertNotIn('날짜 폴더 자동 변경', self.log_text(app))
        self.assertTrue(app.roll_date_folder(datetime(2026, 11, 25, 8, 0, 0)))
        self.assertEqual(app.folder_input.get(), '11.25')
        self.assertIn('날짜 폴더 자동 변경(오전 8시): 11.24 → 11.25', self.log_text(app))
        # 그 날짜로 가져오면 그날 폴더를 찾습니다.
        roots = self.m.date_search_folders(app.folder_input.get(), 2026, base_root='base')
        self.assertEqual(roots, [Path('base') / '★ 2026' / '11월' / '11.25'])
        # 같은 날에는 다시 바꾸지 않습니다.
        self.assertFalse(app.roll_date_folder(datetime(2026, 11, 25, 8, 0, 1)))
        self.assertEqual(self.log_text(app).count('날짜 폴더 자동 변경'), 1)

    def test_only_the_date_box_changes(self):
        app = self.launch()
        app.number_input.insert('1.0', '1061\n1062')
        year, mode, list_number = app.year_input.get(), app.mode.get(), app.list_number.get()
        saved_year, status = app.saved_program_year, app.status.get()
        self.assertTrue(app.roll_date_folder(datetime(2026, 11, 25, 8, 0)))
        self.assertEqual(app.folder_input.get(), '11.25')
        self.assertEqual(app.number_input.get('1.0', 'end'), '1061\n1062\n')
        self.assertEqual((app.year_input.get(), app.mode.get(), app.list_number.get()), (year, mode, list_number))
        self.assertEqual((app.saved_program_year, app.status.get()), (saved_year, status))
        self.assertEqual(str(app.folder_input.cget('state')), 'normal')
        self.assertFalse(app.busy)

    def test_a_date_typed_by_hand_stays_until_the_next_eight_oclock(self):
        app = self.launch()
        self.assertTrue(app.roll_date_folder(datetime(2026, 11, 25, 8, 0)))
        app.folder_input.delete(0, 'end'); app.folder_input.insert(0, '11.20')      # 지난 날 파일을 가져오려고 고침
        for now in (datetime(2026, 11, 25, 8, 0, 5), datetime(2026, 11, 25, 17, 0), datetime(2026, 11, 26, 7, 59)):
            self.assertFalse(app.roll_date_folder(now), now)
            self.assertEqual(app.folder_input.get(), '11.20', now)
        self.assertTrue(app.roll_date_folder(datetime(2026, 11, 26, 8, 0)))
        self.assertEqual(app.folder_input.get(), '11.26')
        self.assertIn('날짜 폴더 자동 변경(오전 8시): 11.20 → 11.26', self.log_text(app))

    def test_box_already_showing_the_new_day_is_left_alone(self):
        app = self.launch()
        app.folder_input.delete(0, 'end'); app.folder_input.insert(0, '11.25')      # 8시 전에 미리 고쳐 둠
        self.assertFalse(app.roll_date_folder(datetime(2026, 11, 25, 8, 0)))
        self.assertEqual(app.folder_input.get(), '11.25')
        self.assertNotIn('날짜 폴더 자동 변경', self.log_text(app))
        app.folder_input.delete(0, 'end'); app.folder_input.insert(0, '11.20')
        self.assertFalse(app.roll_date_folder(datetime(2026, 11, 25, 8, 1)))        # 그날 몫은 이미 지나감
        self.assertEqual(app.folder_input.get(), '11.20')

    def test_nothing_changes_while_a_job_runs_and_the_box_changes_once_it_ends(self):
        app = self.launch()
        app.set_busy(True, '파일만 가져오기 중...')
        self.assertFalse(app.roll_date_folder(datetime(2026, 11, 25, 8, 0)))
        self.assertEqual(app.folder_input.get(), '11.24')
        self.assertEqual(str(app.folder_input.cget('state')), 'disabled')
        app.set_busy(False)
        self.assertTrue(app.roll_date_folder(datetime(2026, 11, 25, 8, 0, 40)))
        self.assertEqual(app.folder_input.get(), '11.25')
        self.assertEqual(str(app.folder_input.cget('state')), 'normal')

    def test_an_import_waiting_for_the_drive_check_keeps_its_inputs(self):
        app = self.launch()
        calls = []
        self.stack.enter_context(patch.object(
            self.m, 'run_batch', lambda roots, *args, **kwargs: calls.append(list(roots)) or {
                'alarms': [], 'copied_sources': [], 'list_created': False, 'list_number': '3999',
                'missing_numbers': [], 'mode': kwargs.get('mode')}))
        base = Path(self.tmp.name) / 'nc'
        app.program_base_root = str(base)
        app.destination = None                                   # 드라이브 확인을 기다리게 함
        app.mode.set(self.m.MODE_FILES); app.update_mode()
        app.number_input.insert('1.0', '1061')
        app.start_import()
        self.assertIsNotNone(app.drive_action_pending)
        self.assertFalse(app.roll_date_folder(datetime(2026, 11, 25, 8, 0)))
        self.assertEqual(app.folder_input.get(), '11.24')
        app.destination = Path(self.tmp.name)
        app.finish_drive_action(app.drive_action_pending['generation'])
        deadline = time.monotonic() + 10
        while (app.busy or not calls) and time.monotonic() < deadline:
            app.window.update(); time.sleep(.01)
        self.assertEqual(calls, [[base / '★ 2026' / '11월' / '11.24']])      # 누른 때의 날짜로 가져옴
        self.assertFalse(app.busy)
        self.assertTrue(app.roll_date_folder(datetime(2026, 11, 25, 8, 0, 3)))
        self.assertEqual(app.folder_input.get(), '11.25')

    def test_box_changes_in_list_only_mode_and_stays_locked(self):
        app = self.launch()
        app.mode.set(self.m.MODE_LIST); app.update_mode()
        self.assertEqual(str(app.folder_input.cget('state')), 'disabled')
        self.assertTrue(app.roll_date_folder(datetime(2026, 11, 25, 8, 0)))
        self.assertEqual(app.folder_input.get(), '11.25')
        self.assertEqual(str(app.folder_input.cget('state')), 'disabled')
        app.mode.set(self.m.MODE_BOTH); app.update_mode()
        self.assertEqual(str(app.folder_input.cget('state')), 'normal')
        self.assertEqual(app.folder_input.get(), '11.25')

    def test_days_missed_while_the_pc_slept_catch_up_to_the_latest_eight_oclock(self):
        app = self.launch(started=datetime(2026, 11, 20, 15, 0))                    # 금요일 오후에 켜 둠
        self.assertEqual(app.folder_input.get(), '11.20')
        self.assertTrue(app.roll_date_folder(datetime(2026, 11, 23, 8, 30)))        # 월요일 8시 반에 깨어남
        self.assertEqual(app.folder_input.get(), '11.23')
        self.assertEqual(self.log_text(app).count('날짜 폴더 자동 변경'), 1)
        # 8시 전에 깨어나면 가장 최근에 지난 오전 8시의 날짜(전날)까지만 따라갑니다.
        other = self.launch(started=datetime(2026, 11, 20, 15, 0))
        self.assertTrue(other.roll_date_folder(datetime(2026, 11, 24, 3, 0)))
        self.assertEqual(other.folder_input.get(), '11.23')
        self.assertTrue(other.roll_date_folder(datetime(2026, 11, 24, 8, 0)))
        self.assertEqual(other.folder_input.get(), '11.24')

    def test_month_and_year_change_write_the_date_like_the_start_value(self):
        app = self.launch(started=datetime(2026, 11, 30, 9, 0))
        self.assertTrue(app.roll_date_folder(datetime(2026, 12, 1, 8, 0)))
        self.assertEqual(app.folder_input.get(), '12.01')
        app = self.launch(started=datetime(2026, 12, 31, 9, 0))
        year = app.year_input.get()
        self.assertTrue(app.roll_date_folder(datetime(2027, 1, 1, 8, 0)))
        self.assertEqual(app.folder_input.get(), '1.01')
        self.assertEqual(app.year_input.get(), year)             # 연도 칸은 자동으로 바꾸지 않습니다

    def test_box_in_use_is_selected_again_after_the_change(self):
        app = self.launch()
        app.window.deiconify(); app.window.lift(); app.window.focus_force(); app.window.update()
        app.folder_input.focus_force(); app.window.update()
        if app.window.focus_get() is not app.folder_input:
            self.skipTest('this display does not give keyboard focus to the test window')
        app.folder_input.selection_clear(); app.folder_input.icursor(2)
        self.assertTrue(app.roll_date_folder(datetime(2026, 11, 25, 8, 0)))
        self.assertTrue(app.folder_input.selection_present())
        self.assertEqual(app.folder_input.selection_get(), '11.25')

    def test_running_program_checks_the_clock_by_itself(self):
        self.m.DATE_FOLDER_POLL_MS = 20
        clock = [datetime(2026, 11, 24, 9, 30)]
        real_day = self.m.date_folder_day
        self.stack.enter_context(patch.object(
            self.m, 'date_folder_day', lambda now=None: real_day(clock[0] if now is None else now)))
        root = tk.Tk(); app = self.m.IntegrationApp(root); self.apps.append(app)
        app.folder_input.delete(0, 'end'); app.folder_input.insert(0, '11.24')
        self.assertEqual(app.folder_day, date(2026, 11, 24))

        def run(seconds):
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                root.update(); time.sleep(.005)

        run(.2)
        self.assertEqual(app.folder_input.get(), '11.24')
        clock[0] = datetime(2026, 11, 25, 7, 59, 59); run(.2)
        self.assertEqual(app.folder_input.get(), '11.24')
        clock[0] = datetime(2026, 11, 25, 8, 0, 0)
        deadline = time.monotonic() + 5
        while app.folder_input.get() != '11.25' and time.monotonic() < deadline:
            root.update(); time.sleep(.005)
        self.assertEqual(app.folder_input.get(), '11.25')
        clock[0] = datetime(2026, 11, 26, 8, 0, 0)               # 다음 날도 이어서
        deadline = time.monotonic() + 5
        while app.folder_input.get() != '11.26' and time.monotonic() < deadline:
            root.update(); time.sleep(.005)
        self.assertEqual(app.folder_input.get(), '11.26')
        self.assertEqual(self.log_text(app).count('날짜 폴더 자동 변경'), 2)


if __name__ == '__main__':
    unittest.main()
