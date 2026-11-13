"""'MES 정렬' 탭: 버튼·상태 표시와 실행 흐름(가짜 MES 화면)을 실제 메인 창에서 확인합니다."""
import json
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import test_main_window_placement as placement
import mes_fake as fake
import test_mes_align_all as flow


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
        wash.mes.WindowsClicks = lambda chosen: SimpleNamespace(
            u=user, target=chosen, Input=fake.Input, activate=lambda: None,
            rect=lambda handle: SimpleNamespace(**dict(zip(('left', 'top', 'right', 'bottom'), mes.rects[handle]))))
        reader = SimpleNamespace(captures=[], closed=[])
        def capture(chosen, label, stop):
            reader.captures.append((chosen.get('mode'), label, chosen.get('handle')))
            return mes.report(chosen.get('handle'))
        reader.capture = capture
        reader.close = lambda: reader.closed.append(True)
        if not hasattr(wash, 'real_pointer'):
            wash.real_pointer = wash.layout.Pointer                          # 두 번 연결해도 원래 클래스를 씀
        wash.layout.Pointer = lambda api: wash.real_pointer(api, sleep=user.sleep, clock=user.clock)
        for item in (patch.object(self.m, 'mes_layout_reader', lambda module: reader),
                     patch.object(self.m, 'wash_prepare_window', lambda api, stop: {'maximized': True}),
                     patch.object(self.m.SuiteErrors, 'capture', Mock())):
            item.start()
            self.addCleanup(item.stop)
        wash.show_completion = Mock()
        return wash, user, reader

    def finish(self, wash, mode, stop=None):
        """실행 버튼을 누른 것과 같은 상태로 만든 뒤 작업을 끝까지 돌리고 화면에 반영합니다."""
        wash.busy = True
        wash.layout_running = True
        wash.stop = stop or threading.Event()
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
        self.assertGreater(app.tab_buttons['mes'].winfo_rootx(), app.tab_buttons['wash'].winfo_rootx())
        app.tab_buttons['mes'].invoke(); app.window.update()
        self.assertEqual(app.active_tab, 'mes')
        self.assertTrue(app.app_pages['mes'].winfo_ismapped())
        self.assertFalse(app.app_pages['wash'].winfo_ismapped())
        wash = app.wash_app
        self.assertEqual(wash.layout_button.cget('text'), 'MES 정렬')
        self.assertTrue(str(wash.layout_button).startswith(str(app.app_pages['mes'])))
        self.assertTrue(str(wash.run_button).startswith(str(app.app_pages['wash'])))      # 세척완료 버튼은 제자리
        self.assertIn('기준: 기본값', wash.layout_status.get())
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
        buttons = (wash.run_button, wash.layout_button, wash.layout_save_button, wash.layout_inspect_button)
        wash.busy = True; wash.controls()
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

    def test_one_press_arranges_a_fresh_mes_with_the_built_in_standard(self):
        app = self.launch()
        mes = flow.fresh()
        wash, user, reader = self.connect(app, mes)
        self.finish(wash, 'align')
        status = wash.layout_status.get()
        self.assertTrue(status.startswith('MES 정렬 완료 · 설비별공구관리 열기 · 작업지시관리 칸 없앰 6·옮김 3'), status)
        self.assertEqual(mes.bad, [])
        self.assertEqual(sorted(mes.hidden), sorted(fake.WORK_EXTRA))
        self.assertEqual([name for name, _ in mes.work.columns], flow.ARRANGED)
        self.assertEqual((mes.menu, mes.active, mes.inner), (25, '작업지시관리', '생산일보관리'))
        sizes = mes.grid_sizes()
        self.assertLessEqual(max(w for w, _ in sizes) - min(w for w, _ in sizes), 2)
        self.assertLessEqual(abs(mes.widths()[5]['거래처명'] - 119), 1)
        self.assertFalse(self.preset_path().exists())                       # 기본 기준을 썼을 뿐, 저장하지는 않음
        self.assertEqual(reader.closed, [True])
        self.assertEqual({mode for mode, label, root in reader.captures}, {'mes_rows'})
        self.assertEqual(user.cursor, (5, 5))                               # 마우스를 원래 자리로
        self.assertEqual(str(wash.layout_button.cget('state')), 'normal')
        self.m.SuiteErrors.capture.assert_not_called()
        wash.show_completion.assert_not_called()

    def test_saving_reads_the_arranged_screens_and_later_runs_use_them(self):
        app = self.launch()
        arranged = flow.fresh()
        wash, user, reader = self.connect(app, arranged)
        self.finish(wash, 'align')
        widths = dict(arranged.work.columns)
        arranged.work.columns = [[name, widths[name] + (9 if name == '설비명' else 0)] for name, _ in arranged.work.columns]
        for leaf in arranged.panels:
            leaf.columns[4][1] = 70                                          # 생산일보 Fixture를 넓혀 둠
        presses = arranged.presses
        self.finish(wash, 'save')
        self.assertLessEqual(arranged.presses - presses, 2)                 # 탭만 누름
        self.assertTrue(wash.layout_status.get().startswith('기준 저장 완료 · 작업지시관리 칸 '), wash.layout_status.get())
        saved = json.loads(self.preset_path().read_text(encoding='utf-8'))
        self.assertEqual(saved['version'], 2)
        self.assertEqual(dict(saved['work']['order'])['설비명'], 134)
        self.assertEqual(dict(saved['columns'])['Fixture'], 70)
        self.assertNotIn('PART-NO', saved['work']['keep'])
        self.assertIn('기준: 저장한 화면', wash.layout_preset_text())
        fresh = flow.fresh()
        wash, user, reader = self.connect(app, fresh)
        self.finish(wash, 'align')
        self.assertEqual(dict(fresh.work.columns)['설비명'], 134)
        self.assertEqual(fresh.widths()[3]['Fixture'], 70)
        self.assertEqual(fresh.bad, [])
        self.assertTrue(wash.layout_status.get().startswith('MES 정렬 완료'), wash.layout_status.get())

    def test_structure_copy_only_reads_and_puts_the_text_on_the_clipboard(self):
        app = self.launch()
        mes = flow.fresh()
        wash, user, reader = self.connect(app, mes)
        prepared = Mock(side_effect=AssertionError('읽기만 해야 함'))
        with patch.object(self.m, 'wash_prepare_window', prepared):
            self.finish(wash, 'inspect')
        self.assertEqual(mes.presses, 0)
        self.assertEqual(user.cursor, (5, 5))                               # 마우스도 움직이지 않음
        self.assertEqual(reader.captures, [('mes_rows', 'MES 화면 구조', 1)])
        text = app.window.clipboard_get()
        self.assertTrue(text.startswith('지후니우스 {} · MES 화면 구조 (읽기만 함)'.format(self.m.SUITE_APP_VERSION)), text[:80])
        self.assertIn('PART-NO 110', text)
        self.assertIn('앞에 보임', text)
        self.assertIn('[메뉴] 묶음 2개', text)
        self.assertNotIn('비밀환자', text)
        self.assertEqual((Path(self.tmp.name) / 'Jihunius' / 'mes_structure.txt').read_text(encoding='utf-8'), text)
        title, shown = wash.show_completion.call_args.args
        self.assertEqual(title, '화면 구조 복사')
        self.assertIn('붙여넣기', shown)
        self.m.SuiteErrors.capture.assert_not_called()

    def test_layout_reader_changes_only_its_own_copy_of_the_screen_reader(self):
        app = self.launch()
        wash = app.wash_app
        made = []
        with patch.object(self.m, 'WashReader', lambda module: made.append(module) or module):
            self.m.mes_layout_reader(wash.pop)
            shim = made[-1]
            self.assertIsNot(shim, wash.pop)
            self.assertIn('if(role!=29 || (CellBoundsMode!=1 && !skipCellBounds)) {', shim.POWERSHELL)       # 모든 항목 위치
            self.assertIn('|| Convert.ToString(row["name"])=="데이터 패널")return;', shim.POWERSHELL)           # 표의 행은 읽지 않음
            self.assertIn('role==37 || (role>=41 && role<=47)) {', wash.pop.POWERSHELL)                       # 세척완료가 쓰는 원본은 그대로
            self.assertNotIn('데이터 패널")return;', wash.pop.POWERSHELL)
            self.assertIs(shim.check_capture, wash.pop.check_capture)
            changed = SimpleNamespace(POWERSHELL='다른 코드', check_capture=None, base64=None)
            self.assertIs(self.m.mes_layout_reader(changed), changed)                                         # 줄을 못 찾으면 원래 판독기

    def test_missing_mes_window_is_reported_and_recorded(self):
        app = self.launch()
        wash, user, reader = self.connect(app, flow.fresh(), windows=[])
        self.finish(wash, 'align')
        self.assertEqual(wash.layout_status.get(), '중단: ROOT MES 창을 하나만 실행해 주세요.')
        record = self.m.SuiteErrors.capture.call_args
        self.assertEqual(record.kwargs['feature'], 'MES 정렬')
        self.assertIn('ROOT MES', record.args[0])
        wash.show_completion.assert_called_once()
        self.assertEqual(str(wash.layout_button.cget('state')), 'normal')

    def test_stop_is_not_an_error(self):
        app = self.launch()
        mes = flow.fresh()
        wash, user, reader = self.connect(app, mes)
        stop = threading.Event()
        stop.set()
        self.finish(wash, 'align', stop=stop)
        self.assertTrue(wash.layout_status.get().startswith('중지함'), wash.layout_status.get())
        self.assertEqual(mes.presses, 0)
        self.m.SuiteErrors.capture.assert_not_called()
        wash.show_completion.assert_not_called()

    def test_partial_result_is_shown_and_recorded_with_the_trail(self):
        app = self.launch()
        mes = flow.fresh(removal_works=False)                               # 칸이 없어지지 않는 MES
        wash, user, reader = self.connect(app, mes)
        self.finish(wash, 'align')
        self.assertIn('일부만', wash.layout_status.get())
        title, text = wash.show_completion.call_args.args
        self.assertEqual(title, 'MES 정렬 일부만 완료')
        self.assertIn('없애지 못한 칸', text)
        record = self.m.SuiteErrors.capture.call_args                       # 원인 파악용으로 진행 기록과 함께 남김
        self.assertEqual((record.kwargs['feature'], record.kwargs['stage']), ('MES 정렬', '일부만 완료'))
        self.assertIn('없애지 못한 칸', record.kwargs['detail'])
        self.assertIn('칸 버리기 · 거래처코드 · 그대로 있음 · 위로', record.kwargs['context'])
        tail = record.kwargs['detail'].split('[작업지시관리 표 기록]')[1]       # 표 기록은 길이 제한에 잘리지 않게 따로 붙임
        self.assertIn('작업지시관리 표 (', tail)
        self.assertIn('PART-NO@', tail)
        self.assertIn('칸 버리기 · 거래처코드 · 그대로 있음 · 아래로', tail)
        self.assertNotIn('비밀환자', record.kwargs['detail'] + record.kwargs['context'])

    def test_error_record_carries_the_trail_for_diagnosis(self):
        app = self.launch()
        mes = flow.fresh()
        wash, user, reader = self.connect(app, mes)
        user.foreground = 777                                               # 다른 창이 앞에 있음
        self.finish(wash, 'align')
        self.assertIn('MES 이외의 창이 앞에 있어', wash.layout_status.get())
        record = self.m.SuiteErrors.capture.call_args
        self.assertIn('설비별공구관리 안 열림', record.kwargs['context'])
        self.assertEqual(mes.presses, 0)


if __name__ == '__main__':
    unittest.main()
