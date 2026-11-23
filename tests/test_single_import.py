"""하나만 가져오기(사용자 요청 2026-11-23): '파일만 가져오기 + 날짜 폴더'와 같은 동작을 따로 여닫는 작은 창에서.

기본 날짜는 하루 전날(월요일은 그 전주 금요일)이고, 메인 화면의 번호 목록·날짜 폴더·작업 모드와 리스트 파일은 건드리지 않습니다.
"""
import hashlib
import os
import time
import tkinter as tk
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

import test_main_window_placement as placement
from test_host_stability import load_app

PROGRAM = '%\r\nO1482\r\nG0X-15.25Y21.0\r\nM11\r\nG1X-14.6F0.02\r\nM30\r\n%\r\n'


def files(folder):
    return {str(path.relative_to(folder)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(Path(folder).rglob('*')) if path.is_file()}


class DefaultDateTests(unittest.TestCase):
    def setUp(self):
        self.m = load_app()

    def test_default_is_the_day_before_and_the_friday_before_on_mondays(self):
        default = self.m.single_import_default_date
        for today, expected in ((date(2026, 11, 24), date(2026, 11, 23)),      # 화 → 월
                                (date(2026, 11, 23), date(2026, 11, 20)),      # 월 → 그 전주 금
                                (date(2026, 11, 27), date(2026, 11, 26)),      # 금 → 목
                                (date(2026, 11, 28), date(2026, 11, 27)),      # 토 → 금
                                (date(2026, 11, 29), date(2026, 11, 28)),      # 일 → 토
                                (date(2026, 12, 1), date(2026, 11, 30)),       # 1일 → 전달 말일
                                (date(2026, 11, 2), date(2026, 10, 30)),       # 월요일이 달 초: 전달의 금요일
                                (date(2027, 1, 1), date(2026, 12, 31)),        # 해가 바뀜
                                (date(2027, 1, 4), date(2027, 1, 1))):         # 새해 첫 월요일 → 1월 1일(금)
            self.assertEqual(default(today), expected, today)
        self.assertEqual(default(), default(date.today()))

    def test_folder_text_is_written_like_the_date_box_on_the_main_screen(self):
        self.assertEqual(self.m.single_import_folder_text(date(2026, 11, 3)), '11.03')
        self.assertEqual(self.m.single_import_folder_text(date(2026, 7, 1)), '7.01')
        self.assertEqual(self.m.single_import_folder_text(date(2026, 11, 20)), '11.20')
        roots = self.m.date_search_folders(self.m.single_import_folder_text(date(2025, 12, 31)), 2025, base_root='base')
        self.assertEqual(roots, [Path('base') / '★ 2025' / '12월' / '12.31'])     # 해가 다르면 그 해의 폴더


@unittest.skipUnless(os.environ.get('DISPLAY') or os.name == 'nt', 'requires Tk display')
class SingleImportTests(unittest.TestCase):
    setUp = placement.MainWindowPlacementTests.setUp
    cleanup = placement.MainWindowPlacementTests.cleanup
    close_app = placement.MainWindowPlacementTests.close_app
    FRIDAY = date(2026, 11, 20)

    def launch(self):
        self.stack.enter_context(patch.object(self.m, 'single_import_default_date', return_value=self.FRIDAY))
        root = tk.Tk()
        app = self.m.IntegrationApp(root)
        self.apps.append(app)
        app.messagebox = Mock()
        app.messagebox.askyesno.return_value = True
        base = Path(self.tmp.name)
        self.base, self.card = base / 'nc', base / 'card'
        self.day_folder = self.base / '★ 2026' / '11월' / '11.20'
        (self.day_folder / '하위').mkdir(parents=True)
        self.card.mkdir()
        app.program_base_root = str(self.base)
        app.destination = self.card
        # 메인 화면에서 하던 일: 번호 목록·날짜·모드
        app.number_input.insert('1.0', '1061\n1062')
        app.folder_input.delete(0, 'end'); app.folder_input.insert(0, '11.23')
        root.update()
        return app

    def main_inputs(self, app):
        return (app.number_input.get('1.0', 'end'), app.folder_input.get(), app.year_input.get(),
                app.mode.get(), app.list_number.get())

    def wait(self, app, condition, seconds=10):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            app.window.update()
            if condition():
                return
            time.sleep(.01)
        self.fail('시간 안에 끝나지 않았습니다')

    def fake_batch(self, missing=(), alarms=()):
        calls = []

        def run_batch(roots, destination, numbers, chooser=None, popup=True, mode=None, list_number=None):
            calls.append(dict(roots=list(roots), destination=destination, numbers=list(numbers), popup=popup,
                              mode=mode, list_number=list_number, chooser=chooser))
            return {'alarms': list(alarms), 'copied_sources': [], 'list_created': False, 'list_number': list_number,
                    'missing_numbers': [number for number in numbers if number in missing], 'mode': mode}
        self.stack.enter_context(patch.object(self.m, 'run_batch', run_batch))
        return calls

    def fetch(self, app, text):
        panel = app.single_import
        panel.number.delete(0, 'end'); panel.number.insert(0, text)
        self.assertEqual(panel.submit(), 'break')
        self.wait(app, lambda: not app.busy and panel.pending is None)

    # ── 여닫기 ──
    def test_button_opens_and_closes_the_window_and_the_main_screen_stays_as_it_was(self):
        app = self.launch(); root = app.window; panel = app.single_import
        before = (self.main_inputs(app), root.minsize(), root.geometry())
        self.assertFalse(panel.visible())
        self.assertEqual(str(app.single_import_button.cget('style')), 'Popup.TButton')
        app.single_import_button.invoke(); root.update()
        self.assertTrue(panel.visible())
        self.assertEqual(str(app.single_import_button.cget('style')), 'Open.Popup.TButton')
        self.assertEqual(panel.window.title(), '하나만 가져오기')
        self.assertEqual(panel.selected, self.FRIDAY)                    # 전날(월요일이면 금요일)로 맞춰져 있음
        self.assertIn('11.20 (금)', panel.chosen_text.get())
        self.assertEqual(panel.heading.cget('text'), '2026년 11월')
        self.assertEqual((self.main_inputs(app), root.minsize(), root.geometry()), before)
        app.single_import_button.invoke(); root.update()                 # 다시 누르면 닫힘
        self.assertFalse(panel.visible())
        self.assertEqual(str(app.single_import_button.cget('style')), 'Popup.TButton')
        panel.open(); root.update()
        root.tk.call(panel.window.protocol('WM_DELETE_WINDOW')); root.update()   # 창의 X로 닫아도 같음
        self.assertFalse(panel.visible())
        self.assertEqual((self.main_inputs(app), root.minsize(), root.geometry()), before)
        self.assertFalse(app.busy)

    def test_every_opening_starts_from_the_day_before_and_remembers_where_the_window_was(self):
        app = self.launch(); root = app.window; panel = app.single_import
        panel.open(); root.update()
        panel.day_buttons[date(2026, 11, 12)].invoke(); root.update()
        self.assertEqual(panel.selected, date(2026, 11, 12))
        panel.window.geometry('+333+222'); root.update()
        placed = (panel.window.winfo_x(), panel.window.winfo_y())
        panel.close(); panel.open(); root.update()
        self.assertEqual(panel.selected, self.FRIDAY)                    # 다시 열면 전날로
        self.assertEqual((panel.window.winfo_x(), panel.window.winfo_y()), placed)

    def test_a_day_is_chosen_by_clicking_it_and_months_can_be_turned(self):
        app = self.launch(); root = app.window; panel = app.single_import
        panel.open(); root.update()
        self.assertEqual(sorted(panel.day_buttons), [date(2026, 11, day) for day in range(1, 31)])
        panel.day_buttons[date(2026, 11, 19)].invoke(); root.update()
        self.assertEqual(panel.selected, date(2026, 11, 19))
        self.assertIn('11.19 (목)', panel.chosen_text.get())
        self.assertEqual(panel.day_buttons[date(2026, 11, 19)].cget('background'), panel.ACCENT)
        self.assertNotEqual(panel.day_buttons[date(2026, 11, 20)].cget('background'), panel.ACCENT)
        panel.move(-1); root.update()                                    # 달만 넘겨서는 날짜가 바뀌지 않음
        self.assertEqual(panel.heading.cget('text'), '2026년 10월')
        self.assertEqual(panel.selected, date(2026, 11, 19))
        panel.day_buttons[date(2026, 10, 30)].invoke(); root.update()
        self.assertEqual(panel.selected, date(2026, 10, 30))
        for _ in range(3):
            panel.move(1)
        self.assertEqual(panel.heading.cget('text'), '2027년 1월')
        panel.select(self.m.single_import_default_date()); root.update()  # [전날로]
        self.assertEqual((panel.selected, panel.heading.cget('text')), (self.FRIDAY, '2026년 11월'))

    # ── 가져오기 ──
    def test_enter_fetches_that_number_from_that_day_as_files_only_and_leaves_the_main_inputs(self):
        app = self.launch(); root = app.window; panel = app.single_import
        calls = self.fake_batch()
        before = self.main_inputs(app)
        panel.open(); root.update()
        self.assertTrue(panel.number.bind('<Return>'))
        self.fetch(app, '1482')
        self.assertEqual(len(calls), 1)
        call = calls[0]
        self.assertEqual(call['roots'], [self.day_folder])               # 그날 폴더만
        self.assertEqual((call['numbers'], call['mode'], call['popup'], call['destination']),
                         (['1482'], self.m.MODE_FILES, False, self.card))
        self.assertEqual(self.main_inputs(app), before)                  # 번호 목록·날짜·모드 그대로
        self.assertEqual(panel.number.get(), '')                         # 바로 다음 번호를 칠 수 있게
        self.assertEqual(panel.listing.get(0, 'end'), ('O1482 · 11.20 · 저장됨',))
        self.assertIn('O1482 저장됨', panel.status.get())
        self.assertTrue(panel.visible())                                 # 창은 열어 둠
        self.assertEqual(str(panel.fetch.cget('state')), 'normal')
        app.messagebox.showwarning.assert_not_called()
        app.messagebox.askyesno.assert_not_called()                      # 카드에 같은 번호가 없으면 묻지 않음
        self.fetch(app, 'O1490')                                         # 이어서 하나 더
        self.assertEqual(calls[1]['numbers'], ['1490'])
        self.assertEqual(panel.listing.get(0, 'end'), ('O1490 · 11.20 · 저장됨', 'O1482 · 11.20 · 저장됨'))
        self.assertEqual(self.main_inputs(app), before)

    def test_another_day_and_year_use_that_days_folder(self):
        app = self.launch(); root = app.window; panel = app.single_import
        calls = self.fake_batch()
        panel.open(); root.update()
        panel.select(date(2025, 12, 31)); root.update()
        self.fetch(app, '1482')
        self.assertEqual(calls[0]['roots'], [self.base / '★ 2025' / '12월' / '12.31'])
        self.assertEqual(app.year_input.get(), '2026')                   # 메인 화면의 연도 칸은 그대로

    def test_a_number_that_is_not_in_that_folder_stays_in_the_box_and_is_reported(self):
        app = self.launch(); root = app.window; panel = app.single_import
        self.fake_batch(missing=('1490',))
        panel.open(); root.update()
        self.fetch(app, '1482 1490')
        self.assertEqual(panel.number.get(), '1490')                     # 날짜만 바꿔 다시 누를 수 있게
        self.assertEqual(panel.listing.get(0, 'end'), ('O1490 · 11.20 · 못 찾음', 'O1482 · 11.20 · 저장됨'))
        self.assertIn('11.20 폴더에 없음', panel.status.get())
        app.messagebox.showwarning.assert_called_once()
        self.assertIn('O1490', app.messagebox.showwarning.call_args.args[1])
        self.assertIs(app.messagebox.showwarning.call_args.kwargs['parent'], panel.window)

    def test_asks_once_before_replacing_a_file_of_the_same_number_on_the_card(self):
        app = self.launch(); root = app.window; panel = app.single_import
        calls = self.fake_batch()
        app.drive_item_paths = [self.card / 'O1061', self.card / 'O1482', self.card / 'O3999']
        panel.open(); root.update()
        app.messagebox.askyesno.return_value = False
        panel.number.insert(0, '1482'); panel.submit(); root.update()
        self.assertEqual(calls, [])                                      # 아니오: 가져오지 않음
        self.assertFalse(app.busy)
        self.assertEqual(panel.number.get(), '1482')
        self.assertIn('O1482', app.messagebox.askyesno.call_args.args[1])
        self.assertNotIn('O1061', app.messagebox.askyesno.call_args.args[1])
        app.messagebox.askyesno.return_value = True
        self.fetch(app, '1482')
        self.assertEqual(len(calls), 1)                                  # 예: 가져옴
        self.assertEqual(app.messagebox.askyesno.call_count, 2)

    def test_nothing_starts_while_another_job_is_running_or_after_the_request_changed(self):
        app = self.launch(); root = app.window; panel = app.single_import
        calls = self.fake_batch()
        panel.open(); root.update()
        app.set_busy(True, '다른 작업 중...'); root.update()
        self.assertEqual(str(panel.fetch.cget('state')), 'disabled')
        panel.number.insert(0, '1482'); panel.submit(); root.update()
        self.assertEqual(calls, [])
        self.assertIn('다른 작업이 끝난 뒤', panel.status.get())
        app.set_busy(False); root.update()
        self.assertEqual(str(panel.fetch.cget('state')), 'normal')
        # 드라이브 확인을 기다리는 사이 번호를 고치면 예전 요청은 실행하지 않습니다.
        held = []
        with patch.object(app, 'run_with_current_drive', side_effect=held.append):
            panel.submit()
        panel.number.delete(0, 'end'); panel.number.insert(0, '1490')
        held[0](self.card); root.update()
        self.assertEqual(calls, [])
        self.assertFalse(app.busy)
        # 빈 칸·잘못된 번호·리스트 번호
        panel.number.delete(0, 'end'); panel.submit()
        self.assertIn('번호를 입력', panel.status.get())
        for wrong in ('abc', '3999'):
            panel.number.delete(0, 'end'); panel.number.insert(0, wrong); panel.submit()
        self.assertEqual(app.messagebox.showerror.call_count, 2)
        self.assertEqual(calls, [])

    def test_the_result_is_exactly_what_files_only_mode_writes_and_the_list_is_untouched(self):
        app = self.launch(); root = app.window; panel = app.single_import
        self.stack.enter_context(patch.object(self.m, 'validate_fixed_destination'))   # Windows 드라이브 확인만 건너뜀
        source = self.day_folder / '하위' / 'O1482 고객.nc'
        source.write_bytes(PROGRAM.encode('utf-8'))
        (self.day_folder / 'O1490.nc').write_bytes(PROGRAM.replace('O1482', 'O1490').encode('utf-8'))
        (self.card / 'O3999').write_bytes(b'LIST-BEFORE')                 # 이미 만들어 둔 리스트
        (self.card / 'O1061').write_bytes(b'today')
        sources_before = files(self.day_folder)
        before = self.main_inputs(app)
        panel.open(); root.update()
        self.fetch(app, '1482')
        # 같은 번호를 '파일만 가져오기'로 가져온 결과와 한 글자도 다르지 않아야 합니다.
        reference = Path(self.tmp.name) / 'reference'
        reference.mkdir()
        (reference / 'O3999').write_bytes(b'LIST-BEFORE'); (reference / 'O1061').write_bytes(b'today')
        with patch.object(self.m, 'print', create=True, new=lambda *args, **kwargs: None):
            self.m.run_batch([self.day_folder], reference, ['1482'], popup=False, mode=self.m.MODE_FILES)
        self.assertEqual(files(self.card), files(reference))
        fetched = [name for name in files(self.card) if name not in ('O1061', 'O3999')]
        self.assertEqual([self.m.filename_number(name) for name in fetched], ['1482'])  # 그 번호 파일 하나만 늘어남
        self.assertEqual((self.card / 'O3999').read_bytes(), b'LIST-BEFORE')           # 리스트는 그대로
        self.assertEqual((self.card / 'O1061').read_bytes(), b'today')
        self.assertNotEqual((self.card / fetched[0]).read_bytes(), source.read_bytes()) # 수정 규칙이 적용된 복사본
        self.assertIn(b'X-14.25', (self.card / fetched[0]).read_bytes())
        self.assertEqual(files(self.day_folder), sources_before)                        # 원본은 그대로
        self.assertEqual(self.main_inputs(app), before)
        self.assertEqual(panel.listing.get(0, 'end'), ('O1482 · 11.20 · 저장됨',))
        self.assertFalse(app.busy)

    def test_a_missing_day_folder_stops_with_the_usual_message_and_keeps_the_number(self):
        app = self.launch(); root = app.window; panel = app.single_import
        self.stack.enter_context(patch.object(self.m, 'validate_fixed_destination'))
        panel.open(); root.update()
        panel.select(date(2026, 11, 19)); root.update()                  # 폴더가 없는 날
        before = self.main_inputs(app)
        self.fetch(app, '1482')
        app.messagebox.showerror.assert_called_once()
        self.assertIn('검색 폴더를 찾을 수 없습니다', app.messagebox.showerror.call_args.args[1])
        self.assertEqual(panel.number.get(), '1482')
        self.assertEqual(panel.listing.get(0, 'end'), ('O1482 · 11.19 · 중단',))
        self.assertEqual(files(self.card), {})
        self.assertEqual(self.main_inputs(app), before)
        self.assertFalse(app.busy)

    def test_the_usual_import_still_clears_its_own_number_box_and_ignores_the_window(self):
        app = self.launch(); root = app.window; panel = app.single_import
        calls = self.fake_batch()
        panel.open(); root.update()
        panel.number.insert(0, '1482')
        app.mode.set(self.m.MODE_FILES); app.update_mode()
        app.start_import()
        self.wait(app, lambda: not app.busy and calls)
        root.update()
        self.assertEqual(calls[0]['numbers'], ['1061', '1062'])          # 메인 화면의 번호·날짜로
        self.assertEqual(calls[0]['roots'], [self.base / '★ 2026' / '11월' / '11.23'])
        self.assertEqual(app.number_input.get('1.0', 'end').strip(), '')  # 평소처럼 메인 번호 칸을 비움
        self.assertEqual(panel.number.get(), '1482')                     # 작은 창의 번호는 그대로
        self.assertEqual(panel.listing.get(0, 'end'), ())


if __name__ == '__main__':
    unittest.main()
