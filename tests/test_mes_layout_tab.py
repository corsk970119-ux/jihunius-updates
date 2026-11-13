"""'MES 정렬' 탭: 버튼·상태 표시와 실행 흐름(가짜 MES 화면)을 실제 메인 창에서 확인합니다."""
import json
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import test_main_window_placement as placement
import test_mes_layout as fake


class MesLayoutTabTests(unittest.TestCase):
    setUp = placement.MainWindowPlacementTests.setUp
    cleanup = placement.MainWindowPlacementTests.cleanup
    close_app = placement.MainWindowPlacementTests.close_app
    launch = placement.MainWindowPlacementTests.launch

    def connect(self, app, mes, windows=None):
        """세척완료와 같은 준비 단계를 가짜로 바꿔, 가짜 MES 화면에 연결합니다."""
        wash = app.wash_app
        user = fake.FakeUser32(mes)
        target = {'title': 'ROOT MES', 'handle': 1, 'pid': 1}
        wash.pop.visible_windows = lambda: [dict(target)] if windows is None else windows
        wash.mes.WindowsClicks = lambda chosen: SimpleNamespace(u=user, target=chosen, Input=fake.Input, activate=lambda: None)
        reader = SimpleNamespace(captures=[], closed=[])
        def capture(chosen, label, stop):
            reader.captures.append((chosen.get('mode'), label))
            return mes.report()
        reader.capture = capture
        reader.close = lambda: reader.closed.append(True)
        real_pointer = wash.layout.Pointer
        wash.layout.Pointer = lambda api: real_pointer(api, sleep=user.sleep, clock=user.clock)
        for item in (patch.object(self.m, 'WashReader', lambda module: reader),
                     patch.object(self.m, 'wash_prepare_window', lambda api, stop: {'maximized': True}),
                     patch.object(self.m, 'wash_ensure_mes_production', lambda module, api, report, capture, stop, emit: report),
                     patch.object(self.m.SuiteErrors, 'capture', Mock())):
            item.start()
            self.addCleanup(item.stop)
        wash.show_completion = Mock()
        return wash, user, reader

    def finish(self, wash, mode):
        """실행 버튼을 누른 것과 같은 상태로 만든 뒤 작업을 끝까지 돌리고 화면에 반영합니다."""
        wash.busy = True
        wash.layout_running = True
        wash.stop = threading.Event() if not getattr(wash, '_keep_stop', False) else wash.stop
        wash.controls()
        wash.started = self.m.time.monotonic()
        wash.trail = []
        wash.layout_work(mode)
        for _ in range(50):
            wash.poll()
            if not wash.busy:
                break
        self.assertFalse(wash.busy)

    def preset_path(self):
        return Path(self.tmp.name) / 'Jihunius' / 'mes_layout.json'

    def test_tab_sits_next_to_wash_and_shows_its_own_page(self):
        app = self.launch()
        self.assertEqual(list(app.tab_buttons), ['cnc', 'stl', 'wash', 'mes'])
        self.assertEqual(app.tab_buttons['mes'].cget('text'), 'MES 정렬')
        wash_x = app.tab_buttons['wash'].winfo_rootx()
        self.assertGreater(app.tab_buttons['mes'].winfo_rootx(), wash_x)
        app.tab_buttons['mes'].invoke(); app.window.update()
        self.assertEqual(app.active_tab, 'mes')
        self.assertTrue(app.app_pages['mes'].winfo_ismapped())
        self.assertFalse(app.app_pages['wash'].winfo_ismapped())
        wash = app.wash_app
        self.assertEqual(wash.layout_button.cget('text'), 'MES 정렬')
        self.assertTrue(str(wash.layout_button).startswith(str(app.app_pages['mes'])))
        self.assertTrue(str(wash.run_button).startswith(str(app.app_pages['wash'])))      # 세척완료 버튼은 제자리
        self.assertIn('저장한 기준 없음', wash.layout_status.get())
        app.tab_buttons['wash'].invoke(); app.window.update()
        self.assertTrue(app.app_pages['wash'].winfo_ismapped())

    def test_tabs_do_not_run_into_the_handover_button_at_the_smallest_window(self):
        app = self.launch()
        width, height = app.window.minsize()
        app.window.geometry('{}x{}'.format(width, max(height, 760))); app.window.update(); app.window.update()
        last = app.tab_buttons['mes']
        self.assertLessEqual(last.winfo_rootx() + last.winfo_width(), app.handover_toggle.winfo_rootx())

    def test_buttons_lock_while_either_job_runs(self):
        app = self.launch()
        wash = app.wash_app
        wash.busy = True; wash.controls()
        buttons = (wash.run_button, wash.layout_button, wash.layout_save_button, wash.layout_inspect_button)
        for button in buttons:
            self.assertEqual(str(button.cget('state')), 'disabled')
        wash.busy = False; wash.controls()
        for button in buttons:
            self.assertEqual(str(button.cget('state')), 'normal')

    def test_outside_windows_it_only_explains(self):
        app = self.launch()
        wash = app.wash_app
        app.messagebox = Mock()
        wash.layout_work = Mock()
        wash.launch_layout('align')
        app.messagebox.showinfo.assert_called_once()
        wash.layout_work.assert_not_called()
        self.assertFalse(wash.busy)

    def test_first_run_aligns_everything_and_saves_the_top_left_panel_as_the_standard(self):
        app = self.launch()
        mes = fake.six(widths=fake.scrambled())
        first = dict(mes.leaves[0].columns)
        wash, user, reader = self.connect(app, mes)
        self.finish(wash, 'align')
        self.assertTrue(wash.layout_status.get().startswith('MES 정렬 완료 · 판 6개'), wash.layout_status.get())
        self.assertIn('위쪽 왼쪽 판의 너비를 기준으로 저장', wash.layout_status.get())
        for widths in mes.widths():
            for name, width in first.items():
                self.assertLessEqual(abs(widths[name] - width), 1)
        sizes = mes.grid_sizes()
        self.assertLessEqual(max(w for w, _ in sizes) - min(w for w, _ in sizes), 2)
        self.assertEqual(mes.bad, [])
        saved = json.loads(self.preset_path().read_text(encoding='utf-8'))
        self.assertEqual(dict(saved['columns']), first)
        self.assertEqual(reader.closed, [True])
        self.assertEqual(user.cursor, (5, 5))                               # 마우스를 원래 자리로
        self.assertEqual(str(wash.layout_button.cget('state')), 'normal')
        self.m.SuiteErrors.capture.assert_not_called()
        wash.show_completion.assert_not_called()

    def test_saved_standard_is_applied_on_later_runs(self):
        app = self.launch()
        wash = app.wash_app
        wash.layout.save_preset(self.preset_path(), fake.STANDARD, '위쪽 왼쪽')
        mes = fake.six(widths=fake.scrambled())
        wash, user, reader = self.connect(app, mes)
        self.finish(wash, 'align')
        for widths in mes.widths():
            for name, width in fake.STANDARD.items():
                self.assertLessEqual(abs(widths[name] - width), 1)
        self.assertNotIn('기준으로 저장', wash.layout_status.get())
        self.assertEqual(dict(json.loads(self.preset_path().read_text(encoding='utf-8'))['columns']), dict(fake.STANDARD))

    def test_saving_the_standard_reads_only_and_never_presses(self):
        app = self.launch()
        mes = fake.six(widths=fake.scrambled())
        expected = dict(mes.leaves[0].columns)
        wash, user, reader = self.connect(app, mes)
        self.finish(wash, 'save')
        self.assertEqual(mes.presses, 0)
        self.assertEqual(user.cursor, (5, 5))
        self.assertEqual(dict(json.loads(self.preset_path().read_text(encoding='utf-8'))['columns']), expected)
        self.assertTrue(wash.layout_status.get().startswith('기준 저장 완료 · 왼쪽 위 판의 칸 11개'), wash.layout_status.get())
        self.assertIn('기준 저장됨: 칸 11개', wash.layout_preset_text())

    def test_wide_left_menu_is_narrowed_first(self):
        app = self.launch()
        wash = app.wash_app
        wash.layout.save_preset(self.preset_path(), fake.STANDARD, '위쪽 왼쪽')
        mes = fake.six(widths=fake.scrambled(), menu=200)
        wash, user, reader = self.connect(app, mes)
        self.finish(wash, 'align')
        self.assertEqual(mes.menu, 25)
        self.assertTrue(wash.layout_status.get().startswith('MES 정렬 완료 · 메뉴 칸 200→25 · 판 6개'), wash.layout_status.get())
        self.assertEqual(mes.bad, [])

    def test_structure_copy_only_reads_and_puts_the_text_on_the_clipboard(self):
        app = self.launch()
        mes = fake.six(menu=200)
        wash, user, reader = self.connect(app, mes)
        prepared = Mock(side_effect=AssertionError('읽기만 해야 함'))
        with patch.object(self.m, 'wash_prepare_window', prepared), patch.object(self.m, 'wash_ensure_mes_production', prepared), \
                patch.object(self.m, 'mes_structure_reader', lambda module: reader):
            wash.mes.WindowsClicks = lambda chosen: SimpleNamespace(
                u=user, target=chosen, Input=fake.Input, activate=prepared,
                rect=lambda handle: SimpleNamespace(**dict(zip(('left', 'top', 'right', 'bottom'), mes.rects[handle]))))
            self.finish(wash, 'inspect')
        self.assertEqual(mes.presses, 0)
        self.assertEqual(user.cursor, (5, 5))                               # 마우스도 움직이지 않음
        self.assertEqual(reader.captures, [('mes_rows', 'MES 화면 구조')])
        text = app.window.clipboard_get()
        self.assertTrue(text.startswith('지후니우스 {} · MES 화면 구조 (읽기만 함)'.format(self.m.SUITE_APP_VERSION)), text[:80])
        self.assertIn('거래처명@', text)
        self.assertIn('[메뉴가 든 창의 구성]', text)
        self.assertNotIn('비밀환자', text)
        self.assertEqual((Path(self.tmp.name) / 'Jihunius' / 'mes_structure.txt').read_text(encoding='utf-8'), text)
        title, shown = wash.show_completion.call_args.args
        self.assertEqual(title, '화면 구조 복사')
        self.assertIn('붙여넣기', shown)
        self.assertIn('화면 구조를 복사했습니다', wash.layout_status.get())
        self.m.SuiteErrors.capture.assert_not_called()

    def test_structure_reader_widens_only_its_own_copy_of_the_screen_reader(self):
        app = self.launch()
        wash = app.wash_app
        made = []
        with patch.object(self.m, 'WashReader', lambda module: made.append(module) or module):
            self.m.mes_structure_reader(wash.pop)
            shim = made[-1]
            self.assertIsNot(shim, wash.pop)
            self.assertIn('if(role!=29 || (CellBoundsMode!=1 && !skipCellBounds)) {', shim.POWERSHELL)
            self.assertIn('role==37 || (role>=41 && role<=47)) {', wash.pop.POWERSHELL)      # 세척완료가 쓰는 원본은 그대로
            self.assertEqual(len(shim.POWERSHELL) < len(wash.pop.POWERSHELL), True)
            self.assertIs(shim.check_capture, wash.pop.check_capture)
            changed = SimpleNamespace(POWERSHELL='다른 코드', check_capture=None, base64=None)
            self.assertIs(self.m.mes_structure_reader(changed), changed)                       # 줄을 못 찾으면 원래 판독기

    def test_missing_mes_window_is_reported_and_recorded(self):
        app = self.launch()
        wash, user, reader = self.connect(app, fake.six(), windows=[])
        self.finish(wash, 'align')
        self.assertEqual(wash.layout_status.get(), '중단: ROOT MES 창을 하나만 실행해 주세요.')
        record = self.m.SuiteErrors.capture.call_args
        self.assertEqual(record.kwargs['feature'], 'MES 정렬')
        self.assertIn('ROOT MES', record.args[0])
        wash.show_completion.assert_called_once()
        self.assertEqual(str(wash.layout_button.cget('state')), 'normal')

    def test_stop_is_not_an_error(self):
        app = self.launch()
        mes = fake.six(widths=fake.scrambled())
        wash, user, reader = self.connect(app, mes)
        wash.stop = threading.Event(); wash.stop.set(); wash._keep_stop = True
        self.finish(wash, 'align')
        self.assertTrue(wash.layout_status.get().startswith('중지함'), wash.layout_status.get())
        self.assertEqual(mes.presses, 0)
        self.m.SuiteErrors.capture.assert_not_called()
        wash.show_completion.assert_not_called()

    def test_partial_result_is_shown_with_what_is_left(self):
        app = self.launch()
        wash = app.wash_app
        target = dict(fake.STANDARD); target['치식'] = 8                      # 최소 너비보다 작은 기준
        wash.layout.save_preset(self.preset_path(), target, '위쪽 왼쪽')
        mes = fake.six()
        wash, user, reader = self.connect(app, mes)
        self.finish(wash, 'align')
        self.assertIn('일부만', wash.layout_status.get())
        title, text = wash.show_completion.call_args.args
        self.assertEqual(title, 'MES 정렬 일부만 완료')
        self.assertIn('치식 20→8', text)
        record = self.m.SuiteErrors.capture.call_args                       # 원인 파악용으로 진행 기록과 함께 남김
        self.assertEqual((record.kwargs['feature'], record.kwargs['stage']), ('MES 정렬', '일부만 완료'))
        self.assertIn('치식 20→8', record.kwargs['detail'])
        self.assertIn('경계 세로', record.kwargs['context'])

    def test_error_record_carries_the_trail_for_diagnosis(self):
        app = self.launch()
        mes = fake.six(widths=fake.scrambled())
        wash, user, reader = self.connect(app, mes)
        user.foreground = 777                                               # 다른 창이 앞에 있음
        self.finish(wash, 'align')
        self.assertIn('MES 이외의 창이 앞에 있어', wash.layout_status.get())
        record = self.m.SuiteErrors.capture.call_args
        self.assertIn('표 6개', record.kwargs['context'])
        self.assertEqual(mes.presses, 0)


if __name__ == '__main__':
    unittest.main()
