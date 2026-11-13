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


def fresh(plain=False, **changes):
    """MES를 막 켠 상태: 메뉴 칸 200, 작업지시관리 문서의 '작업지시관리' 탭, 표는 기본 순서(없앨 칸 6개 포함).

    작업지시관리 표는 실제 MES처럼 행 번호 칸 51픽셀, 왼쪽 고정 칸 6개(뒤에 2픽셀 구분선), 세로 스크롤 막대가 있습니다.
    plain=True: 고정 칸·행 번호 칸·스크롤 막대가 없는 단순한 표.
    """
    mes = fake.six(menu=200)
    mes.inner = '작업지시관리'
    mes.allow_clicks = True
    mes.movable = {mes.work}                             # 칸 제목을 끌어도 되는 표는 작업지시관리 표뿐
    if not plain:
        mes.work.frozen, mes.work.indent, mes.work.scrollbar = set(fake.WORK_FROZEN), fake.WORK_INDENT, 17
    for name, value in changes.items():
        setattr(mes, name, value)
    mes.layout()
    return mes


def run(mes, standard=None, user=None, stop=None, call=None):
    user = user or fake.FakeUser32(mes)
    api = SimpleNamespace(u=user, target={'handle': 1, 'pid': 1, 'title': 'ROOT MES'}, Input=fake.Input)
    pointer = layout.Pointer(api, sleep=user.sleep, clock=user.clock)
    notes, reads, where = [], [], []

    def capture(target, text, halt):
        reads.append((text, target.get('handle')))
        where.append((text, user.cursor))                 # 화면을 읽는 순간의 포인터 자리
        return mes.report(target.get('handle'))

    action = call or layout.align_all
    arguments = (api.target, pointer, capture, stop or threading.Event(), lambda kind, value: notes.append((kind, value)))
    result = action(*arguments) if call is layout.capture_standard else action(*arguments, standard or layout.default_standard())
    return SimpleNamespace(result=result, notes=notes, reads=reads, where=where, pointer=pointer, user=user)


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
        self.assertEqual(sorted(mes.hidden), sorted(fake.WORK_EXTRA))         # 기준에 없는 6칸을 없앰
        self.assert_work(mes)
        self.assert_daily(mes)
        self.assertEqual(mes.menu, 25)                                        # 파란 메뉴 칸은 끝까지
        self.assertEqual(mes.documents, ['작업지시관리', '설비별공구관리'])    # 설비별공구관리는 열어만 둠
        self.assertEqual((mes.active, mes.inner), ('작업지시관리', '생산일보관리'))
        self.assertEqual(mes.tool.columns, [list(item) for item in fake.TOOL_COLUMNS])
        result = outcome.result
        self.assertEqual(result['opened'], ['설비별공구관리'])
        self.assertEqual((result['menu']['before'], result['menu']['after']), (200, 25))
        self.assertEqual(sorted(result['work']['removed']), sorted(fake.WORK_EXTRA))
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
        mes = fresh(plain=True, removal_works=False)
        outcome = run(mes)
        work = outcome.result['work']
        self.assertEqual(work['removed'], [])
        self.assertEqual(sorted(work['stuck']), sorted(fake.WORK_EXTRA))
        self.assertEqual(mes.hidden, [])
        self.assertEqual([way for _, way in mes.drops], ['위', '아래', '위', '아래'])   # 두 칸만 해 보고 더 끌지 않음
        names = [name for name, _ in mes.work.columns]
        self.assertEqual(names[:7], ORDER[:7])                                # 순서는 기준대로, 못 없앤 칸은 뒤로 밀림
        title, lines = layout.brief_all(outcome.result, 20.0)
        self.assertIn('일부만', title)
        self.assertTrue(any(line.startswith('작업지시관리: 없애지 못한 칸 — ') for line in lines), lines)
        self.assertEqual(mes.bad, [])
        self.assertTrue(any(value.startswith('작업지시관리 표(끝난 뒤)') for kind, value in outcome.notes if kind == 'record'))

    def test_stuck_frozen_columns_block_the_order_and_that_is_reported(self):
        mes = fresh(removal_works=False)                                      # 실제처럼 고정 칸이 있는 표에서 버리기가 안 될 때
        outcome = run(mes)
        work = outcome.result['work']
        self.assertEqual(sorted(work['stuck']), sorted(fake.WORK_EXTRA))
        names = [name for name, _ in mes.work.columns]
        self.assertEqual(names[:4], ORDER[:4])                                # 고정 칸끼리는 기준 순서로
        self.assertEqual(work['blocked'], '작업자')                           # 고정 칸 사이로는 옮겨지지 않음
        lines = layout.brief_all(outcome.result, 20.0)[1]
        self.assertTrue(any('"작업자" 칸을 제자리로 옮기지 못했습니다' in line for line in lines), lines)
        self.assertEqual(mes.bad, [])

    def test_sideways_scrolled_table_is_brought_home_first(self):
        mes = fresh()
        mes.work.scroll = 600
        outcome = run(mes)
        self.assertEqual(mes.work.scroll, 0)
        self.assertFalse(outcome.result['work']['scrolled'])
        self.assert_work(mes)
        self.assertEqual(mes.bad, [])

    def test_table_that_stays_scrolled_keeps_its_order_and_the_reason_is_given(self):
        mes = fresh(autoscroll_left=False)
        mes.work.scroll = 480                                                 # 거래처코드부터 오른쪽이 보이는 만큼 밀림
        mes.work.columns = [[name, {'지역': 70, 'Type': 75}.get(name, width)] for name, width in mes.work.columns]
        before = [name for name, _ in mes.work.columns]
        outcome = run(mes)
        work = outcome.result['work']
        self.assertTrue(work['scrolled'])
        self.assertEqual(work['moved'], 0)                                    # 순서는 판단할 수 없어 옮기지 않음
        self.assertEqual([name for name in before if name not in mes.hidden], [name for name, _ in mes.work.columns])
        self.assertEqual(mes.bad, [])                                         # 가려진 칸 자리(고정 칸 밑)는 누르지 않음
        self.assertTrue(set(mes.hidden) <= set(fake.WORK_EXTRA))              # 보이는 칸 가운데 필요 없는 것만 버림
        self.assertEqual(mes.hidden, ['거래처코드'])
        checks = [text for text, root in outcome.reads if text == '칸 버린 뒤']
        self.assertEqual(len(checks), len(mes.hidden))                        # 밀린 표는 한 칸 버릴 때마다 다시 읽어 확인
        shown = dict(mes.work.columns)
        self.assertEqual((shown['지역'], shown['Type']), (50, 60))            # 보이는 칸의 너비는 기준대로
        self.assertEqual(len([text for text, root in outcome.reads if text == '칸 너비 확인']), 2)   # 너비도 한 칸씩 확인
        self.assertEqual(shown['설비명'], 150)                                # 고정 칸 밑에 가려진 칸은 그대로
        self.assertEqual(work['remaining'], [])
        self.assertGreater(mes.work.scroll, 0)                                # 가로로 밀린 것은 사용자가 되돌림
        self.assert_daily(mes)                                                # 생산일보는 그대로 진행
        title, lines = layout.brief_all(outcome.result, 20.0)
        self.assertIn('일부만', title)
        self.assertTrue(any('가로 스크롤을 왼쪽 끝으로' in line for line in lines), lines)
        self.assertTrue(any('겹쳐 읽힌 칸' in line for line in lines), lines)   # 화면 사진만 봐도 원인을 알 수 있게

    def test_widths_land_exactly_because_the_edge_goes_where_it_is_dropped(self):
        mes = fresh()
        run(mes)
        widths = dict(mes.work.columns)
        self.assertEqual({name: widths[name] for name, _ in layout.DEFAULT_WORK_ORDER}, dict(layout.DEFAULT_WORK_ORDER))

    def test_columns_hidden_under_the_frozen_ones_are_not_trusted(self):
        mes = fresh()
        mes.work.scroll = 600
        mes.layout()
        grid = layout.grids(mes.report(1220), required=())[0]
        self.assertFalse(layout.tidy(grid))
        visible = layout.chain(grid)
        self.assertLess(len(visible), len(grid['columns']))                   # 고정 칸과 겹쳐 읽힌 칸은 빼고
        for column in visible:                                                # 남은 칸은 그 자리에 실제로 보이는 칸
            hit = mes.header_at(mes.work, column['x'] + column['w'] // 2, column['y'] + 5)
            self.assertEqual(mes.work.columns[hit[0]][0], column['name'])
        mes.work.scroll = 0
        self.assertTrue(layout.tidy(layout.grids(mes.report(1220), required=())[0]))

    def test_frozen_columns_and_their_divider_do_not_look_like_a_scrolled_table(self):
        # 2026.11.13.4에서 실제 MES의 작업지시관리 표를 통째로 건너뛴 원인: 고정 칸 뒤 구분선(틈)을 '밀린 표'로 봄.
        mes = fresh()
        grid = layout.grids(mes.report(1220), required=())[0]
        names = [column['name'] for column in grid['columns']]
        gap = grid['columns'][names.index('T31수정')]['x'] - (grid['columns'][names.index('프로젝트No')]['x'] + 100)
        self.assertEqual(gap, fake.FROZEN_GAP)
        self.assertEqual(grid['columns'][0]['x'] - grid['x'], fake.WORK_INDENT)
        self.assertTrue(layout.tidy(grid))
        self.assertEqual([column['name'] for column in layout.chain(grid)], names)

    def test_unneeded_columns_are_thrown_away_upward_like_the_user_does(self):
        mes = fresh()
        outcome = run(mes)
        self.assertEqual(sorted(mes.hidden), sorted(fake.WORK_EXTRA))
        self.assertEqual(mes.drops, [(name, '위') for name in mes.hidden])     # 모두 위로 끌어다 버림
        self.assertEqual(outcome.result['work']['removed'], mes.hidden)
        reads = [text for text, root in outcome.reads if text == '칸 버린 뒤']
        self.assertEqual(len(reads), 2, reads)                                # 한 칸 확인 + 나머지 묶어서 확인
        self.assertTrue(any('칸 버리기' in value and '위로' in value for kind, value in outcome.notes if kind == 'record'))

    def test_dropping_inside_the_table_is_tried_when_upward_does_nothing(self):
        mes = fresh(removal_works=False, removal_down_works=True)
        outcome = run(mes)
        self.assertEqual(sorted(mes.hidden), sorted(fake.WORK_EXTRA))
        self.assertEqual(mes.drops[0][1], '위')                               # 먼저 위로 한 번
        self.assertEqual({way for _, way in mes.drops[1:]}, {'아래'})
        self.assert_work(mes)
        self.assertEqual(outcome.result['work']['stuck'], [])
        self.assertEqual(mes.bad, [])

    def test_header_is_carried_further_up_until_the_pointer_shows_it_will_be_thrown_away(self):
        mes = fresh(removal_distance=60)                                      # 꽤 멀리 올려야 버려지는 MES
        outcome = run(mes)
        self.assertEqual(sorted(mes.hidden), sorted(fake.WORK_EXTRA))
        self.assertEqual({way for _, way in mes.drops}, {'위'})
        self.assertEqual(len(mes.drops), 6)                                   # 헛손질 없이 한 번씩
        first = next(value for kind, value in outcome.notes if kind == 'record' and value.startswith('칸 버리기'))
        self.assertIn('위로 80픽셀', first)
        self.assertIn(str(fake.REMOVING), first)                              # 바뀐 포인터 모양도 기록

    def test_header_is_dropped_at_the_top_step_when_the_pointer_never_changes(self):
        mes = fresh(removal_cursor=False)
        outcome = run(mes)
        self.assertEqual(sorted(mes.hidden), sorted(fake.WORK_EXTRA))
        self.assertEqual(len(mes.drops), 6)
        self.assertTrue(any('위로 100픽셀' in value for kind, value in outcome.notes if kind == 'record'))
        self.assert_work(mes)

    def test_no_room_above_the_table_means_dropping_inside_it(self):
        mes = fresh(removal_down_works=True)
        steps = layout.DISCARD_STEPS
        layout.DISCARD_STEPS = (400, 500)                                     # 위로 올릴 자리가 MES 창 밖
        try:
            run(mes)
        finally:
            layout.DISCARD_STEPS = steps
        self.assertEqual(sorted(mes.hidden), sorted(fake.WORK_EXTRA))
        self.assertEqual({way for _, way in mes.drops}, {'아래'})
        self.assertEqual(mes.bad, [])

    def test_pointer_is_parked_on_the_corner_while_the_table_is_read(self):
        # 칸 제목 위에 포인터를 둔 채 읽으면 MES가 설명 풍선을 띄워 칸 제목을 가릴 수 있다.
        mes = fresh()
        outcome = run(mes)
        mes.inner = '작업지시관리'                                             # 끝나면 생산일보관리 탭이 떠 있으므로 표를 다시 띄움
        mes.layout()
        left, top = mes.rects[mes.work.grid][0], mes.rects[mes.work.grid][1]
        spots = [point for text, point in outcome.where if text in ('칸 버린 뒤', '칸 옮긴 뒤', '칸 너비 확인')]
        self.assertGreaterEqual(len(spots), 6)
        for x, y in spots:
            self.assertTrue(left <= x < left + fake.WORK_INDENT and top <= y < top + fake.HEADER, (x, y))

    def test_scrollbar_over_the_header_row_is_not_part_of_the_table(self):
        mes = fresh()
        outcome = run(mes)
        mes.inner = '작업지시관리'
        mes.layout()
        left, _, right, _ = mes.rects[mes.work.grid]
        grid = layout.grids(mes.report(1220), required=())[0]
        limit = layout.reach(outcome.pointer, grid)
        self.assertTrue(right - 21 <= limit <= right - 17, (limit, right))
        last = [column for column in layout.chain(grid)][-1]                  # 오른쪽 끝에서 잘린 칸
        self.assertFalse(layout.whole(dict(grid, reach=limit), last))
        self.assertEqual(mes.bad, [])                                         # 스크롤 막대나 그 밑은 누르지 않음

    def test_columns_off_the_right_edge_are_left_alone(self):
        mes = fresh()
        run(mes)
        tail = [name for name, _ in mes.work.columns if name not in ORDER]
        self.assertEqual(tail, ['직경', '각도', 'LOT-NO'])                     # 화면 밖 칸은 순서도 너비도 그대로
        self.assertEqual([dict(mes.work.columns)[name] for name in tail], [dict(fake.WORK_COLUMNS)[name] for name in tail])
        self.assertEqual(mes.work.scroll, 0)                                  # 가로로 밀지 않음

    def test_plain_table_without_frozen_columns_is_arranged_too(self):
        mes = fresh(plain=True)
        outcome = run(mes)
        self.assertEqual(sorted(mes.hidden), sorted(fake.WORK_EXTRA))
        self.assert_work(mes)
        self.assertEqual(mes.bad, [])
        self.assertTrue(layout.brief_all(outcome.result, 9.0)[0].startswith('MES 정렬 완료'))

    def test_first_look_at_the_table_is_written_to_the_record(self):
        outcome = run(fresh())
        notes = [value for kind, value in outcome.notes if kind == 'record']
        first = next(value for value in notes if value.startswith('작업지시관리 표 ('))
        self.assertIn('칸 제목 34개', first)
        self.assertIn('겹침 0개', first)
        self.assertTrue(any('선택@' in value and 'PART-NO@' in value for value in notes))
        self.assertTrue(all(len(value) <= 160 for value in notes if value.startswith('  ')), notes)   # 기록 한 줄 길이 한도 안
        self.assertFalse(any('비밀환자' in value or '홍길동' in value for value in notes))           # 행 내용은 적지 않음


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
        self.assertEqual(sorted(mes.hidden), sorted(fake.WORK_EXTRA))
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

    def test_small_window_that_goes_away_does_not_stop_the_run(self):
        # 설명 풍선처럼 칸 제목 위에 잠깐 떴다 사라지는 창: 기다렸다가 계속합니다(계속 가리고 있으면 위 시험처럼 중단).
        mes = fresh(documents=['작업지시관리', '설비별공구관리'], menu=25)
        column = next(item for item in layout.grids(mes.report(1220), required=())[0]['columns'] if item['name'] == '거래처코드')
        center = (column['x'] + column['w'] // 2, column['y'] + column['h'] // 2)
        state = {'left': 2}
        original = mes.window_at

        def window_at(x, y):
            if (x, y) == center and state['left'] > 0:
                state['left'] -= 1
                return 9998
            return original(x, y)
        mes.window_at = window_at
        outcome = run(mes)
        self.assertEqual(state['left'], 0)
        self.assertEqual(sorted(mes.hidden), sorted(fake.WORK_EXTRA))
        self.assertEqual(mes.bad, [])
        self.assertTrue(layout.brief_all(outcome.result, 9.0)[0].startswith('MES 정렬 완료'))


if __name__ == '__main__':
    unittest.main()
