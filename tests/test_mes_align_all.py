"""MES 정렬 전체 흐름: 메뉴로 화면 열기 → 메뉴 칸 줄이기 → 작업지시관리 표(칸 없애기·너비·순서) → 생산일보관리(판 크기·칸 너비).

가짜 MES는 현장 점검(1·2판)으로 확인한 규칙을 따릅니다(tests/mes_fake.py).
"""
import importlib.util
import os
import sys
import tempfile
import threading
import unittest
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mes_fake as fake

spec = importlib.util.spec_from_file_location('mes_layout_for_align_all', ROOT / 'src/host/mes_layout.py')
layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)

ORDER = [name for name, _ in layout.DEFAULT_WORK_ORDER]
ARRANGED = ORDER + ['직경', '각도', 'LOT-NO']          # 기준 순서 뒤에, 기준에 순서가 없는 칸들이 원래 순서로


def fresh(**changes):
    """MES를 막 켠 상태: 메뉴 칸 200, 작업지시관리 문서의 '작업지시관리' 탭, 표는 기본 순서(없앨 칸 6개 포함)."""
    mes = fake.six(menu=200)
    mes.inner = '작업지시관리'
    mes.allow_clicks = True
    mes.movable = {mes.work}                             # 칸 제목을 끌어도 되는 표는 작업지시관리 표뿐
    for name, value in changes.items():
        setattr(mes, name, value)
    mes.layout()
    return mes


def run(mes, standard=None, user=None, stop=None, call=None):
    user = user or fake.FakeUser32(mes)
    api = SimpleNamespace(u=user, target={'handle': 1, 'pid': 1, 'title': 'ROOT MES'}, Input=fake.Input)
    pointer = layout.Pointer(api, sleep=user.sleep, clock=user.clock)
    notes, reads = [], []

    def capture(target, text, halt):
        reads.append((text, target.get('handle')))
        return mes.report(target.get('handle'))

    action = call or layout.align_all
    arguments = (api.target, pointer, capture, stop or threading.Event(), lambda kind, value: notes.append((kind, value)))
    result = action(*arguments) if call is layout.capture_standard else action(*arguments, standard or layout.default_standard())
    return SimpleNamespace(result=result, notes=notes, reads=reads, pointer=pointer, user=user)


class Checks:
    def assert_work(self, mes, widths=None):
        self.assertEqual([name for name, _ in mes.work.columns], ARRANGED)
        for name, width in (widths or OrderedDict(layout.DEFAULT_WORK_ORDER)).items():
            self.assertLessEqual(abs(dict(mes.work.columns)[name] - width), 1, name)

    def assert_daily(self, mes, widths=None):
        sizes = mes.grid_sizes()
        for index in (0, 1):
            self.assertLessEqual(max(size[index] for size in sizes) - min(size[index] for size in sizes), 2, sizes)
        for panel in mes.widths():
            for name, width in (widths or OrderedDict(layout.DEFAULT_DAILY)).items():
                self.assertLessEqual(abs(panel[name] - width), 1, name)


class WholeFlowTests(Checks, unittest.TestCase):
    def test_fresh_mes_ends_up_fully_arranged_with_one_press(self):
        mes = fresh()
        outcome = run(mes)
        self.assertEqual(mes.bad, [])
        self.assertEqual(mes.hidden, list(fake.WORK_EXTRA))                   # 기준에 없는 6칸을 없앰
        self.assert_work(mes)
        self.assert_daily(mes)
        self.assertEqual(mes.menu, 25)                                        # 파란 메뉴 칸은 끝까지
        self.assertEqual(mes.documents, ['작업지시관리', '설비별공구관리'])    # 설비별공구관리는 열어만 둠
        self.assertEqual((mes.active, mes.inner), ('작업지시관리', '생산일보관리'))
        self.assertEqual(mes.tool.columns, [list(item) for item in fake.TOOL_COLUMNS])
        result = outcome.result
        self.assertEqual(result['opened'], ['설비별공구관리'])
        self.assertEqual((result['menu']['before'], result['menu']['after']), (200, 25))
        self.assertEqual(result['work']['removed'], list(fake.WORK_EXTRA))
        self.assertEqual(result['work']['moved'], 3)                          # 특이사항1·2·3을 설비명 뒤로
        self.assertEqual((result['work']['stuck'], result['work']['blocked'], result['work']['remaining']), ([], None, []))
        title, lines = layout.brief_all(result, 31.24)
        self.assertTrue(title.startswith('MES 정렬 완료 · 설비별공구관리 열기 · 작업지시관리 칸 없앰 6·옮김 3·너비 '), title)
        self.assertIn('31.2초', title)
        self.assertEqual(lines, [])
        self.assertFalse(outcome.user.down)
        self.assertEqual(outcome.user.keys, set())

    def test_second_press_changes_nothing(self):
        mes = fresh()
        run(mes)
        before, presses = mes.snapshot(), mes.presses
        outcome = run(mes)
        self.assertEqual(mes.snapshot(), before)
        self.assertEqual(mes.bad, [])
        self.assertLessEqual(mes.presses - presses, 2)                        # 탭 두 번 누르는 것뿐
        self.assertEqual(outcome.result['opened'], [])
        self.assertEqual((outcome.result['work']['removed'], outcome.result['work']['moved'], outcome.result['work']['resized']), ([], 0, 0))
        self.assertTrue(layout.brief_all(outcome.result, 9.0)[0].startswith('MES 정렬 완료 · 작업지시관리 칸 없앰 0·옮김 0·너비 0'))

    def test_checks_read_only_the_table_or_the_menu_not_the_whole_mes(self):
        mes = fresh()
        outcome = run(mes)
        whole = [text for text, root in outcome.reads if root == 1]
        self.assertLessEqual(len(whole), 3, whole)                            # 전체 읽기는 처음·문서 확인 정도
        roots = {root for text, root in outcome.reads}
        self.assertIn(1220, roots)                                            # 작업지시관리 표 창만
        self.assertIn(7, roots)                                               # 메뉴 창만
        self.assertIn(10, roots)                                              # 생산일보 판들이 든 창만

    def test_documents_are_opened_or_brought_forward_as_needed(self):
        cases = (([], None), (['작업지시관리'], '작업지시관리'), (['작업지시관리', '설비별공구관리'], '설비별공구관리'),
                 (['설비별공구관리'], '설비별공구관리'), (['작업지시관리', '설비별공구관리'], '작업지시관리'))
        for documents, active in cases:
            mes = fresh(documents=list(documents), active=active or '작업지시관리', expanded='설비관리', menu=25)
            outcome = run(mes)
            self.assertEqual(mes.bad, [], (documents, active))
            self.assertEqual(sorted(mes.documents), ['설비별공구관리', '작업지시관리'], (documents, active))
            self.assertEqual((mes.active, mes.menu), ('작업지시관리', 25), (documents, active))
            self.assertEqual(sorted(outcome.result['opened']), sorted(set(['작업지시관리', '설비별공구관리']) - set(documents)))
            self.assert_work(mes)
            self.assert_daily(mes)

    def test_menu_is_left_alone_when_both_screens_are_ready(self):
        mes = fresh(documents=['작업지시관리', '설비별공구관리'], menu=25)
        outcome = run(mes)
        self.assertFalse(any(root == 7 for text, root in outcome.reads))      # 메뉴를 읽지도 누르지도 않음
        self.assertEqual(mes.menu, 25)
        self.assertEqual(mes.bad, [])

    def test_only_the_work_order_table_has_its_headers_dragged(self):
        mes = fresh()
        run(mes)
        self.assertEqual(mes.bad, [])                                         # 생산일보 표의 칸 제목을 눌렀다면 여기 기록됨
        self.assertEqual([[name for name, _ in leaf.columns] for leaf in mes.panels], [[name for name, _ in fake.COLUMNS]] * 6)


class WorkTableTests(Checks, unittest.TestCase):
    def test_column_that_will_not_go_away_is_reported_and_the_rest_is_still_arranged(self):
        mes = fresh(removal_works=False)
        outcome = run(mes)
        work = outcome.result['work']
        self.assertEqual(work['removed'], [])
        self.assertEqual(sorted(work['stuck']), sorted(fake.WORK_EXTRA))
        self.assertEqual(mes.hidden, [])
        names = [name for name, _ in mes.work.columns]
        self.assertEqual(names[:7], ORDER[:7])                                # 순서는 기준대로, 못 없앤 칸은 뒤로 밀림
        title, lines = layout.brief_all(outcome.result, 20.0)
        self.assertIn('일부만', title)
        self.assertTrue(any(line.startswith('작업지시관리: 없애지 못한 칸 — ') for line in lines), lines)
        self.assertEqual(mes.bad, [])

    def test_sideways_scrolled_table_is_brought_home_first(self):
        mes = fresh()
        mes.work.scroll = 600
        outcome = run(mes)
        self.assertEqual(mes.work.scroll, 0)
        self.assertFalse(outcome.result['work']['scrolled'])
        self.assert_work(mes)
        self.assertEqual(mes.bad, [])

    def test_table_that_stays_scrolled_is_not_touched_and_the_reason_is_given(self):
        mes = fresh(autoscroll_left=False)
        mes.work.scroll = 600
        before = [list(item) for item in mes.work.columns]
        outcome = run(mes)
        self.assertTrue(outcome.result['work']['scrolled'])
        self.assertEqual(mes.work.columns, before)
        self.assertEqual(mes.hidden, [])
        self.assert_daily(mes)                                                # 생산일보는 그대로 진행
        title, lines = layout.brief_all(outcome.result, 20.0)
        self.assertIn('일부만', title)
        self.assertTrue(any('가로 스크롤을 왼쪽 끝으로' in line for line in lines), lines)

    def test_widths_land_exactly_because_the_edge_goes_where_it_is_dropped(self):
        mes = fresh()
        run(mes)
        widths = dict(mes.work.columns)
        self.assertEqual({name: widths[name] for name, _ in layout.DEFAULT_WORK_ORDER}, dict(layout.DEFAULT_WORK_ORDER))

    def test_visible_run_ignores_stale_positions_left_behind_by_scrolling(self):
        mes = fresh()
        mes.work.scroll = 600
        mes.layout()
        report = mes.report(1220)
        grid = layout.grids(report, required=())[0]
        visible = layout.chain(grid)
        self.assertLess(len(visible), len(grid['columns']))                   # 예전 위치가 남은 칸은 빼고
        self.assertFalse(layout.tidy(grid))
        for one, two in zip(visible, visible[1:]):
            self.assertLessEqual(abs(one['x'] + one['w'] - two['x']), 1)       # 빈틈없이 이어진 줄만
        mes.work.scroll = 0
        self.assertTrue(layout.tidy(layout.grids(mes.report(1220), required=())[0]))


class StandardTests(Checks, unittest.TestCase):
    def test_default_standard_is_the_arrangement_read_on_site(self):
        standard = layout.default_standard()
        self.assertEqual(standard['work']['order'][:11], ['선택', '지시일', '시간', '프로젝트No', '작업자', '설비코드', '설비명',
                                                         '특이사항1', '특이사항2', '특이사항3', '거래처명'])
        self.assertEqual(len(standard['work']['order']), 25)
        self.assertEqual(len(standard['work']['keep']), 52)
        self.assertNotIn('PART-NO', standard['work']['keep'])
        self.assertEqual(sum(standard['work']['widths'].values()), 1833)
        self.assertEqual(standard['daily']['거래처명'], 119)
        self.assertFalse(standard['custom'])

    def test_saved_screen_becomes_the_standard_and_is_applied_to_a_fresh_mes(self):
        arranged = fresh()
        run(arranged)
        dict_work = dict(arranged.work.columns)
        arranged.work.columns = [[name, dict_work[name] + (7 if name == '거래처명' else 0)] for name in
                                 ['지시일', '선택'] + [name for name, _ in arranged.work.columns if name not in ('지시일', '선택')]]
        for leaf in arranged.panels:
            leaf.columns[3][1] = 131                                          # 생산일보 거래처명을 넓혀 둠
        presses = arranged.presses
        captured = run(arranged, call=layout.capture_standard).result
        self.assertLessEqual(arranged.presses - presses, 2)                   # 탭만 누름
        self.assertEqual(arranged.bad, [])
        self.assertEqual(arranged.inner, '생산일보관리')                       # 처음 탭으로 돌아옴
        self.assertEqual(captured['work']['order'][:2], ['지시일', '선택'])
        self.assertEqual(captured['work']['widths']['거래처명'], 147)
        self.assertNotIn('PART-NO', captured['work']['keep'])
        self.assertIn('LOT-NO', captured['work']['keep'])
        self.assertEqual(captured['daily']['거래처명'], 131)
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'Jihunius', 'mes_layout.json')
            layout.save_standard(path, captured['daily'], captured['work'])
            loaded = layout.load_standard(path)
            self.assertTrue(loaded['custom'])
            self.assertTrue(loaded['saved_at'])
            self.assertEqual(list(layout.load_preset(path).items()), list(captured['daily'].items()))   # 예전 형식으로도 읽힘
        mes = fresh()
        run(mes, standard=loaded)
        names = [name for name, _ in mes.work.columns]
        self.assertEqual(names[:3], ['지시일', '선택', '시간'])
        self.assertEqual(dict(mes.work.columns)['거래처명'], 147)
        self.assertEqual(mes.hidden, list(fake.WORK_EXTRA))
        self.assert_daily(mes, loaded['daily'])
        self.assertEqual(mes.bad, [])

    def test_saving_refuses_a_scrolled_or_hidden_screen(self):
        mes = fresh()
        run(mes)
        mes.work.scroll = 300
        with self.assertRaises(RuntimeError) as caught:
            run(mes, call=layout.capture_standard)
        self.assertIn('가로로 밀려 있어', str(caught.exception))
        mes.work.scroll = 0
        mes.active = '설비별공구관리'
        mes.layout()
        with self.assertRaises(RuntimeError) as caught:
            run(mes, call=layout.capture_standard)
        self.assertIn('작업지시관리 화면이 앞에 보이지 않습니다', str(caught.exception))

    def test_broken_or_old_file_falls_back_to_defaults_piece_by_piece(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'mes_layout.json')
            self.assertFalse(layout.load_standard(path)['custom'])
            for text in ('', '{', '[]', '{"columns": 5, "work": 7}'):
                Path(path).write_text(text, encoding='utf-8')
                loaded = layout.load_standard(path)
                self.assertEqual(loaded['work']['order'], ORDER, text)
                self.assertFalse(loaded['custom'], text)
            Path(path).write_text('{"version": 1, "columns": [["거래처명", 130], ["치식", 99999]], "saved_at": "2026-11-13 09:00"}', encoding='utf-8')
            loaded = layout.load_standard(path)                               # 생산일보만 저장돼 있던 예전 파일
            self.assertEqual(dict(loaded['daily']), {'거래처명': 130})
            self.assertEqual(loaded['work']['order'], ORDER)
            self.assertEqual((loaded['custom'], loaded['saved_at']), (True, '2026-11-13 09:00'))


class SafetyTests(unittest.TestCase):
    def test_stop_request_ends_the_run_with_the_button_released(self):
        mes = fresh()
        user = fake.FakeUser32(mes)
        stop = threading.Event()
        mes.on_press = lambda model: stop.set() if model.presses == 7 else None
        with self.assertRaises(layout.Stopped):
            run(mes, user=user, stop=stop)
        self.assertFalse(user.down)
        self.assertIsNone(mes.grab)
        self.assertLessEqual(mes.presses, 8)

    def test_f9_ends_the_run(self):
        mes = fresh()
        user = fake.FakeUser32(mes)
        mes.on_press = lambda model: user.keys.add(0x78) if model.presses == 5 else None
        with self.assertRaises(layout.Stopped):
            run(mes, user=user)
        self.assertFalse(user.down)

    def test_frozen_mes_gets_no_press_at_all(self):
        mes = fresh()
        with self.assertRaises(RuntimeError) as caught:
            run(mes, user=fake.FakeUser32(mes, frozen=True))
        self.assertIn('메뉴', str(caught.exception))
        self.assertEqual(mes.bad, [])
        self.assertEqual(mes.menu, 200)

    def test_missing_menu_or_table_is_an_error_before_anything_moves(self):
        mes = fresh()
        keep = mes.report
        mes.report = lambda root=None: {**keep(root), 'records': [r for r in keep(root)['records'] if r.get('role') not in (16, 30, 33)]}
        with self.assertRaises(RuntimeError) as caught:
            run(mes)
        self.assertIn('왼쪽 메뉴를 읽지 못했습니다', str(caught.exception))
        self.assertEqual(mes.presses, 0)

    def test_window_over_the_work_table_stops_the_run(self):
        mes = fresh(documents=['작업지시관리', '설비별공구관리'], menu=25)
        grid = mes.rects[mes.work.grid]
        mes.rects[9999] = (grid[0] + 30, grid[1] - 5, grid[2], grid[1] + 200)    # 표 위에 뜬 다른 창(왼쪽 조금만 남김)
        mes.parent[9999] = 1
        mes.depth = lambda handle, original=mes.depth: 99 if handle == 9999 else original(handle)
        before = [list(item) for item in mes.work.columns]
        with self.assertRaises(RuntimeError) as caught:
            run(mes)
        self.assertIn('가려져', str(caught.exception))
        self.assertEqual(mes.work.columns, before)
        self.assertEqual(mes.bad, [])


if __name__ == '__main__':
    unittest.main()
