"""MES 정렬: 가짜 MES 화면(나뉜 판 6개·표·경계선)에서 판 크기와 칸 너비 맞춤을 검증합니다.

실제 MES 없이 Linux에서도 돌도록, Windows 함수(user32)를 흉내 내는 FakeUser32 위에서 제품의 Pointer를 그대로 씁니다.
가짜 MES는 실제와 같은 규칙을 가집니다: 경계선 위에서만 포인터가 크기 조절 모양이 되고, 칸 제목 가운데를
누르면 정렬(=잘못된 누름)로 기록되며, 같은 자리를 빠르게 두 번 누르면 더블클릭(자동 맞춤)이 됩니다.
"""
import ctypes
import importlib.util
import os
import tempfile
import threading
import unittest
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mes_layout_under_test', ROOT / 'src/host/mes_layout.py')
layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)

ARROW, WAIT, BUSY, SIZEWE, VSPLIT, HSPLIT = 65539, 65543, 65561, 65555, 70001, 70003
COLUMNS = (('No.', 37), ('선택', 38), ('P/No.', 47), ('거래처명', 120), ('Fixture', 58), ('Size', 54),
           ('환자명', 46), ('치식', 37), ('세척', 40), ('비고', 55), ('영점', 50))
HEADER = 22


class Leaf:
    """판 하나: 사용자 컨트롤 창(panel) 안에 표 창(grid)이 있습니다."""
    def __init__(self, handle, columns=COLUMNS, minimum=20, fixed=()):
        self.panel = handle
        self.grid = handle + 1000
        self.columns = [[name, width] for name, width in columns]
        self.minimum = minimum
        self.fixed = set(fixed)      # 너비를 바꿀 수 없는 칸


class Split:
    """나뉜 컨테이너: 첫째 판 창(handle+1), 경계선, 둘째 판 창(handle+2)."""
    def __init__(self, handle, vertical, first, second, position, fixed=None, thickness=7):
        self.handle = handle
        self.vertical = vertical
        self.first = first
        self.second = second
        self.position = position
        self.fixed = fixed           # 컨테이너 크기가 바뀔 때: None=비율 유지, 'first'/'second'=그쪽 크기 유지
        self.thickness = thickness
        self.size = None
        self.bar = None


def six(nesting='right', fixed=None, widths=None, positions=((640, 560), (700, 500), 380), menu=25):
    """위 3개·아래 3개 판. nesting: 'right'=[A|[B|C]], 'left'=[[A|B]|C]."""
    leaves = [Leaf(100 + 10 * i, widths[i] if widths else COLUMNS) for i in range(6)]

    def row(base, a, b, c, p1, p2):
        if nesting == 'right':
            return Split(base, True, a, Split(base + 10, True, b, c, p2, fixed), p1, fixed)
        return Split(base, True, Split(base + 10, True, a, b, p1, fixed), c, p1 + 7 + p2, fixed)

    # 눈대중으로 나눈 상태: 판 크기가 제각각이지만 왼쪽 위 판은 칸이 모두 보입니다.
    tree = Split(10, False, row(20, leaves[0], leaves[1], leaves[2], *positions[0]),
                 row(50, leaves[3], leaves[4], leaves[5], *positions[1]), positions[2], fixed)
    return FakeMes(tree, menu)


class FakeMes:
    """창 구성: MES(1) → 나뉜 창(3) → [왼쪽 메뉴 칸(4) | 경계선 | 본문(5) → 탭 쪽(2) → 판들]"""
    def __init__(self, tree, menu=25, menu_minimum=25):
        self.tree = tree
        self.menu = menu                     # 왼쪽 메뉴 칸(파란 바) 너비
        self.menu_minimum = menu_minimum
        self.bad = []            # 잘못된 누름(칸 제목 가운데 등)과 더블클릭
        self.presses = 0
        self.grab = None
        self.last_down = None
        self.on_press = None
        self.layout()

    def layout(self):
        body = self.menu + 12
        self.menu_bar = (self.menu, 23, body, 1030)
        self.rects = {1: (0, 0, 1920, 1080), 3: (0, 23, 1920, 1030), 4: (0, 23, self.menu, 1030),
                      5: (body, 23, 1920, 1030), 2: (body + 3, 180, 1917, 1030)}
        self.parent = {1: 0, 3: 1, 4: 3, 5: 3, 2: 5}
        self.leaves = []
        self.splits = []
        self.place(self.tree, self.rects[2], 2)

    def on_menu_bar(self, hit, x, y):
        l, t, r, b = self.menu_bar
        return hit == 3 and l <= x < r and t <= y < b

    def place(self, node, rect, parent):
        left, top, right, bottom = rect
        if isinstance(node, Leaf):
            self.rects[node.panel] = (left + 2, top + 2, right - 2, bottom - 2)
            self.parent[node.panel] = parent
            self.rects[node.grid] = (left + 3, top + 87, right - 3, bottom - 3)
            self.parent[node.grid] = node.panel
            self.leaves.append(node)
            return
        self.rects[node.handle] = rect
        self.parent[node.handle] = parent
        self.splits.append(node)
        size = (right - left) if node.vertical else (bottom - top)
        if node.size is not None and node.size != size:
            if node.fixed == 'second':
                node.position += size - node.size
            elif node.fixed is None:
                node.position = int(round(node.position * size / float(node.size)))
        node.size = size
        node.position = max(40, min(size - node.thickness - 40, node.position))
        if node.vertical:
            first = (left, top, left + node.position, bottom)
            second = (left + node.position + node.thickness, top, right, bottom)
            node.bar = (first[2], top, second[0], bottom)
        else:
            first = (left, top, right, top + node.position)
            second = (left, top + node.position + node.thickness, right, bottom)
            node.bar = (left, first[3], right, second[1])
        for panel, child, area in ((node.handle + 1, node.first, first), (node.handle + 2, node.second, second)):
            self.rects[panel] = area
            self.parent[panel] = node.handle
            self.place(child, area, panel)

    def depth(self, handle):
        count = 0
        while handle:
            count += 1
            handle = self.parent.get(handle, 0)
        return count

    def window_at(self, x, y):
        inside = [h for h, (l, t, r, b) in self.rects.items() if l <= x < r and t <= y < b]
        return max(inside, key=self.depth) if inside else 0

    def leaf(self, handle):
        return next((leaf for leaf in self.leaves if leaf.grid == handle), None)

    def edge_at(self, leaf, x, y):
        left, top, right, _ = self.rects[leaf.grid]
        if not (top <= y < top + HEADER and left <= x < right):
            return None
        position = left
        best = None
        for index, (name, width) in enumerate(leaf.columns):
            position += width
            if name not in leaf.fixed and position - 4 <= x <= position + 3:
                if best is None or abs(x - position) < best[0]:
                    best = (abs(x - position), index)
        return None if best is None else best[1]

    def shape_at(self, x, y):
        hit = self.window_at(x, y)
        if self.on_menu_bar(hit, x, y):
            return VSPLIT
        for split in self.splits:
            l, t, r, b = split.bar
            if hit == split.handle and l <= x < r and t <= y < b:
                return VSPLIT if split.vertical else HSPLIT
        leaf = self.leaf(hit)
        if leaf is not None and self.edge_at(leaf, x, y) is not None:
            return SIZEWE
        return ARROW

    def press(self, x, y, now):
        self.presses += 1
        double = (self.last_down is not None and now - self.last_down[2] <= 0.5
                  and abs(x - self.last_down[0]) <= 2 and abs(y - self.last_down[1]) <= 2)
        self.last_down = (x, y, now)
        self.grab = None
        hit = self.window_at(x, y)
        if self.on_menu_bar(hit, x, y):
            if double:
                self.bad.append('메뉴 경계선 더블클릭')
            self.grab = ('menu', x)
            if self.on_press:
                self.on_press(self)
            return
        for split in self.splits:
            l, t, r, b = split.bar
            if hit == split.handle and l <= x < r and t <= y < b:
                if double:
                    self.bad.append('경계선 더블클릭')
                self.grab = ('split', split, x, y)
                break
        else:
            leaf = self.leaf(hit)
            edge = self.edge_at(leaf, x, y) if leaf is not None else None
            if edge is not None and double:
                self.bad.append('칸 경계 더블클릭(자동 맞춤): ' + leaf.columns[edge][0])
                leaf.columns[edge][1] = 77
            elif edge is not None:
                self.grab = ('column', leaf, edge, x)
            else:
                self.bad.append('경계가 아닌 곳을 누름: 창 {} ({}, {})'.format(hit, x, y))
        if self.on_press:
            self.on_press(self)

    def release(self, x, y):
        grab, self.grab = self.grab, None
        if not grab:
            return
        if grab[0] == 'menu':
            self.menu = max(self.menu_minimum, min(600, self.menu + x - grab[1]))
            self.layout()
        elif grab[0] == 'split':
            split = grab[1]
            split.position += (x - grab[2]) if split.vertical else (y - grab[3])
            self.layout()
        else:
            leaf, index, start = grab[1], grab[2], grab[3]
            leaf.columns[index][1] = max(leaf.minimum, leaf.columns[index][1] + x - start)

    def report(self):
        records = [{'kind': 'native_window', 'handle': handle, 'native_parent': parent,
                    'class': 'WindowsForms10.Window.8.app.0.1'} for handle, parent in self.parent.items()]
        ident = [0]

        def element(**values):
            ident[0] += 1
            values.update(kind='element', id=ident[0])
            records.append(values)
            return ident[0]

        element(parent=-1, role=37, handle=2, name='생산일보관리', selected=True, type='page tab', bounds=[self.menu + 215, 157, 80, 20])
        menu = element(parent=-1, role=10, handle=4, name='메뉴', type='client', depth=0)
        for position, name in enumerate(('설비관리', '생산관리', '작업지시관리')):
            element(parent=menu, role=36, handle=4, name=name, type='outline item', depth=1, bounds=[2, 240 + 23 * position, 196, 21])
        for leaf in self.leaves:
            left, top, right, bottom = self.rects[leaf.grid]
            table = element(parent=-1, role=24, handle=leaf.grid, name='', offscreen=False,
                            bounds=[left, top, right - left, bottom - top])
            group = element(parent=table, role=10, handle=leaf.grid, name='헤더 패널')
            x = left
            for name, width in leaf.columns:
                element(parent=group, role=25, handle=leaf.grid, name=name, bounds=[x, top, width, HEADER],
                        offscreen=x >= right)
                x += width
            data = element(parent=table, role=10, handle=leaf.grid, name='데이터 패널', child_count=1)
            line = element(parent=data, role=28, handle=leaf.grid, name='행 1', value='O1009;홍길동치과;비밀환자;', bounds=[left, top + HEADER, 500, 20])
            element(parent=line, role=29, handle=leaf.grid, name='환자명 row 0', value='비밀환자')
        records.append({'kind': 'finish', 'limited': False, 'elements': ident[0]})
        return {'records': records, 'exit_code': 0, 'target': {'handle': 1}}

    def grid_sizes(self):
        return [(self.rects[leaf.grid][2] - self.rects[leaf.grid][0], self.rects[leaf.grid][3] - self.rects[leaf.grid][1])
                for leaf in self.leaves]

    def widths(self):
        return [OrderedDict(leaf.columns) for leaf in self.leaves]


class Mouse(ctypes.Structure):
    _fields_ = [('dx', ctypes.c_int32), ('dy', ctypes.c_int32), ('data', ctypes.c_uint32),
                ('flags', ctypes.c_uint32), ('time', ctypes.c_uint32), ('extra', ctypes.c_size_t)]


class Payload(ctypes.Union):
    _fields_ = [('mi', Mouse)]


class Input(ctypes.Structure):
    _fields_ = [('type', ctypes.c_uint32), ('payload', Payload)]


class FakeUser32:
    """user32 흉내. lag: 포인터를 옮긴 뒤 MES가 모양을 바꾸기까지 걸리는 조회 횟수, frozen: MES가 응답하지 않음."""
    def __init__(self, mes, lag=0, frozen=False):
        self.mes = mes
        self.lag = lag
        self.frozen = frozen
        self.now = [0.0]
        self.cursor = (5, 5)
        self.down = False
        self.shown = ARROW
        self.waiting = 0
        self.keys = set()
        self.foreground = 1
        self.swapped = False     # 마우스 좌우 버튼 바꿈 설정
        self.sleeps = []
        for name in ('GetCursorInfo', 'LoadCursorW', 'GetDoubleClickTime', 'GetCursorPos', 'WindowFromPoint', 'GetParent',
                     'GetWindowRect', 'GetAsyncKeyState', 'GetForegroundWindow', 'GetSystemMetrics', 'SendInput'):
            setattr(self, name, (lambda method: lambda *args: method(*args))(getattr(self, '_' + name)))

    def clock(self):
        return self.now[0]

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now[0] += seconds

    def _GetCursorInfo(self, reference):
        self.now[0] += 0.0005
        if not self.frozen:
            if self.waiting > 0:
                self.waiting -= 1
            else:
                self.shown = self.mes.shape_at(*self.cursor)
        reference._obj.flags = 1
        reference._obj.hCursor = self.shown
        return 1

    def _LoadCursorW(self, _, name):
        return {32512: ARROW, 32514: WAIT, 32650: BUSY}[name]

    def _GetDoubleClickTime(self):
        return 500

    def _GetCursorPos(self, reference):
        reference._obj.x, reference._obj.y = self.cursor
        return 1

    def _WindowFromPoint(self, point):
        return self.mes.window_at(point.x, point.y)

    def _GetParent(self, handle):
        return self.mes.parent.get(handle, 0)

    def _GetWindowRect(self, handle, reference):
        rect = self.mes.rects.get(handle)
        if rect is None:
            return 0
        reference._obj.left, reference._obj.top, reference._obj.right, reference._obj.bottom = rect
        return 1

    def _GetAsyncKeyState(self, key):
        return 0x8000 if key in self.keys else 0

    def _GetForegroundWindow(self):
        return self.foreground

    def _GetSystemMetrics(self, index):
        return {76: 0, 77: 0, 78: 1920, 79: 1080, 23: int(self.swapped)}[index]

    def _SendInput(self, count, reference, size):
        self.now[0] += 0.0005
        mouse = reference._obj.payload.mi
        if mouse.flags & 0x0001:
            # 실제 Windows처럼 환산 과정에서 1픽셀 어긋날 수 있게 내림으로 계산합니다.
            self.cursor = (mouse.dx * 1919 // 65535, mouse.dy * 1079 // 65535)
            self.waiting = self.lag
        press, release = (0x0008, 0x0010) if self.swapped else (0x0002, 0x0004)
        if mouse.flags & (0x0002 | 0x0008 | 0x0004 | 0x0010) & ~(press | release):
            self.mes.bad.append('주 버튼이 아닌 버튼을 누름')
        if mouse.flags & press:
            self.down = True
            self.mes.press(self.cursor[0], self.cursor[1], self.now[0])
        if mouse.flags & release:
            self.down = False
            self.mes.release(*self.cursor)
        return count


def run(mes, widths=None, lag=0, frozen=False, user=None):
    user = user or FakeUser32(mes, lag=lag, frozen=frozen)
    api = SimpleNamespace(u=user, target={'handle': 1, 'pid': 1, 'title': 'ROOT MES'}, Input=Input)
    pointer = layout.Pointer(api, sleep=user.sleep, clock=user.clock)
    notes = []
    captures = []

    def capture(target, text, stop):
        captures.append((target.get('mode'), text))
        return mes.report()

    result = layout.align(api.target, pointer, capture, threading.Event(), lambda kind, value: notes.append((kind, value)),
                          mes.report(), widths=widths)
    return SimpleNamespace(result=result, notes=notes, captures=captures, pointer=pointer, user=user)


STANDARD = OrderedDict((('No.', 36), ('선택', 34), ('P/No.', 52), ('거래처명', 150), ('Fixture', 64), ('Size', 60),
                        ('환자명', 52), ('치식', 40), ('세척', 36), ('비고', 44), ('영점', 40)))


def scrambled():
    """판마다 눈대중으로 조금씩 다르게 맞춘 칸 너비."""
    return [[(name, width + ((index * 7 + position * 5) % 23) - 9) for position, (name, width) in enumerate(COLUMNS)]
            for index in range(6)]


class ReadingTests(unittest.TestCase):
    def test_six_tables_are_found_in_reading_order_with_their_columns(self):
        mes = six()
        rows = layout.arrange(layout.grids(mes.report()))
        self.assertEqual([[g['handle'] for g in row] for row in rows], [[1100, 1110, 1120], [1130, 1140, 1150]])
        self.assertEqual([layout.label(rows, r, c) for r in range(2) for c in range(3)],
                         ['위쪽 왼쪽', '위쪽 가운데', '위쪽 오른쪽', '아래쪽 왼쪽', '아래쪽 가운데', '아래쪽 오른쪽'])
        self.assertEqual(list(layout.widths_of(rows[0][0]).items()), list(COLUMNS))

    def test_other_tables_and_hidden_ones_are_ignored(self):
        mes = six()
        report = mes.report()
        extra = max(r['id'] for r in report['records'] if r.get('kind') == 'element')
        report['records'] += [
            {'kind': 'element', 'id': extra + 1, 'parent': -1, 'role': 24, 'handle': 9000, 'bounds': [50, 200, 400, 300]},
            {'kind': 'element', 'id': extra + 2, 'parent': extra + 1, 'role': 10, 'handle': 9000},
            {'kind': 'element', 'id': extra + 3, 'parent': extra + 2, 'role': 25, 'handle': 9000, 'name': '품목', 'bounds': [50, 200, 80, 22]},
            {'kind': 'element', 'id': extra + 4, 'parent': -1, 'role': 24, 'handle': 9001, 'bounds': [0, 0, 0, 0]}]
        self.assertEqual(len(layout.grids(report)), 6)

    def test_dividers_are_found_from_the_window_tree_outermost_first(self):
        for nesting in ('right', 'left'):
            mes = six(nesting)
            report = mes.report()
            found = layout.dividers(layout.arrange(layout.grids(report)), layout.native_parents(report))
            self.assertEqual(len(found), 5, nesting)                      # 가로 1 + 줄마다 세로 2
            self.assertEqual((found[0]['vertical'], found[0]['container']), (False, 10), nesting)
            self.assertEqual(sorted(item['container'] for item in found), [10, 20, 30, 50, 60], nesting)
            self.assertEqual([item['depth'] for item in found], sorted(item['depth'] for item in found))


class Checks:
    def assert_even(self, mes):
        sizes = mes.grid_sizes()
        for index in (0, 1):
            values = [size[index] for size in sizes]
            self.assertLessEqual(max(values) - min(values), 2, sizes)

    def assert_widths(self, mes, expected):
        for index, widths in enumerate(mes.widths()):
            for name, width in expected.items():
                self.assertLessEqual(abs(widths[name] - width), 1, (index, name, widths[name], width))


class AlignmentTests(Checks, unittest.TestCase):

    def test_panels_become_the_same_size_for_every_split_arrangement(self):
        for nesting in ('right', 'left'):
            for fixed in (None, 'first', 'second'):
                mes = six(nesting, fixed)
                outcome = run(mes, widths=OrderedDict(COLUMNS))
                self.assert_even(mes)
                self.assertEqual(mes.bad, [], (nesting, fixed))
                self.assertFalse(outcome.result['panels']['uneven'], (nesting, fixed))
                self.assertEqual(outcome.result['panels']['missed'], 0)
                self.assertGreaterEqual(outcome.result['panels']['moved'], 5)
                self.assertLessEqual(outcome.result['panels']['moved'], 12, (nesting, fixed))

    def test_columns_of_all_six_tables_match_the_saved_standard(self):
        mes = six(widths=scrambled())
        outcome = run(mes, widths=STANDARD)
        self.assert_widths(mes, STANDARD)
        self.assert_even(mes)
        self.assertEqual(mes.bad, [])                                      # 칸 제목을 누르거나 더블클릭한 적 없음
        self.assertEqual(outcome.result['remaining'], OrderedDict())
        self.assertEqual(outcome.result['missed'], OrderedDict())
        self.assertFalse(outcome.result['used_reference'])
        self.assertGreater(outcome.result['columns_moved'], 40)
        self.assertEqual(mes.presses, outcome.pointer.presses)
        self.assertFalse(outcome.user.down)

    def test_without_a_saved_standard_the_top_left_table_is_the_standard(self):
        mes = six(widths=scrambled())
        first = OrderedDict(mes.leaves[0].columns)
        outcome = run(mes)
        self.assertTrue(outcome.result['used_reference'])
        self.assertEqual(outcome.result['reference'], '위쪽 왼쪽')
        self.assertEqual(outcome.result['widths'], first)
        self.assert_widths(mes, first)
        self.assertEqual(mes.bad, [])

    def test_already_aligned_screen_is_left_untouched(self):
        mes = six()
        run(mes, widths=OrderedDict(COLUMNS))
        before = (mes.grid_sizes(), mes.widths(), mes.presses)
        outcome = run(mes, widths=OrderedDict(COLUMNS))
        self.assertEqual((mes.grid_sizes(), mes.widths(), mes.presses), before)
        self.assertEqual(outcome.pointer.presses, 0)
        self.assertEqual(outcome.captures, [])                              # 바뀐 것이 없으면 다시 읽지도 않음
        title, lines = layout.brief(outcome.result, 1.5)
        self.assertTrue(title.startswith('MES 정렬 완료'), title)
        self.assertEqual(lines, [])

    def test_slow_screen_still_aligns_and_only_reads_the_screen_a_few_times(self):
        mes = six(widths=scrambled())
        outcome = run(mes, widths=STANDARD, lag=3)
        self.assert_widths(mes, STANDARD)
        self.assertEqual(mes.bad, [])
        self.assertLessEqual(len(outcome.captures), 2)                      # 맞춘 뒤 확인용으로만 다시 읽음
        self.assertEqual({mode for mode, _ in outcome.captures}, {'mes_rows'})

    def test_columns_follow_the_panels_without_rereading_and_are_verified_once(self):
        mes = six(widths=scrambled(), positions=((622, 618), (610, 630), 400))   # 칸이 모두 보이는 상태에서 시작
        outcome = run(mes, widths=STANDARD)
        self.assert_widths(mes, STANDARD)
        self.assert_even(mes)
        self.assertEqual(outcome.captures, [('mes_rows', 'MES 칸 너비 확인')])
        mes = six()                                                         # 칸은 이미 기준대로, 판 크기만 다름
        outcome = run(mes, widths=OrderedDict(COLUMNS))
        self.assertEqual(outcome.result['columns_moved'], 0)
        self.assertEqual(outcome.captures, [('mes_rows', 'MES 칸 너비 확인')])  # 판을 옮겼으면 한 번은 확인


class SafetyTests(Checks, unittest.TestCase):
    def test_nothing_is_pressed_when_the_pointer_never_turns_into_a_resize_shape(self):
        mes = six(widths=scrambled())
        before = (mes.grid_sizes(), mes.widths())
        outcome = run(mes, widths=STANDARD, frozen=True)
        self.assertEqual(mes.presses, 0)
        self.assertEqual((mes.grid_sizes(), mes.widths()), before)
        self.assertEqual(outcome.result['panels']['missed'], 5)
        self.assertEqual(len(outcome.result['missed']), 6)
        title, lines = layout.brief(outcome.result, 2.0)
        self.assertIn('일부만', title)
        self.assertTrue(any('거래처명' in line for line in lines), lines)
        self.assertTrue(any('미확인' in str(value) or '확인하지 못함' in str(value) for kind, value in outcome.notes if kind == 'note'))

    def test_stale_resize_shape_from_the_previous_edge_is_not_trusted(self):
        # MES가 멈춰서 포인터가 계속 크기 조절 모양으로 남아 있어도(이전 경계의 모양) 누르지 않는다.
        mes = six(widths=scrambled())
        user = FakeUser32(mes, frozen=True)
        user.shown = SIZEWE
        run(mes, widths=STANDARD, user=user)
        self.assertEqual(mes.presses, 0)

    def test_busy_pointer_is_not_taken_for_a_resize_shape(self):
        mes = six(widths=scrambled())
        user = FakeUser32(mes)
        mes.shape_at = lambda x, y: ARROW if y == 0 else WAIT
        outcome = run(mes, widths=STANDARD, user=user)
        self.assertEqual(mes.presses, 0)
        self.assertTrue(outcome.result['remaining'])

    def test_columns_that_cannot_be_resized_are_skipped_without_touching_others_wrongly(self):
        mes = six()
        for leaf in mes.leaves:
            leaf.fixed = {'선택'}
        target = OrderedDict(STANDARD)
        outcome = run(mes, widths=target)
        self.assertEqual(mes.bad, [])
        for widths in mes.widths():
            self.assertEqual(widths['선택'], 38)                              # 그대로
            self.assertLessEqual(abs(widths['거래처명'] - 150), 1)
        self.assertEqual(len(outcome.result['remaining']), 6)
        self.assertEqual(outcome.result['remaining']['위쪽 왼쪽'], [('선택', 38, 34)])

    def test_width_below_the_minimum_stops_after_a_few_tries_and_is_reported(self):
        mes = six()
        target = OrderedDict(COLUMNS)
        target['치식'] = 8
        outcome = run(mes, widths=target)
        self.assertEqual(mes.bad, [])
        self.assertLessEqual(mes.presses, 5 * 4 + 6 * layout.COLUMN_PASSES)
        self.assertEqual(outcome.result['remaining']['아래쪽 오른쪽'], [('치식', 20, 8)])
        self.assertIn('치식 20→8', '\n'.join(layout.brief(outcome.result, 3.0)[1]))

    def test_table_scrolled_sideways_is_skipped_and_reported(self):
        mes = six(widths=scrambled())
        keep = mes.report
        def scrolled_report():
            report = keep()
            grid = mes.leaves[4].grid
            for record in report['records']:
                if record.get('role') == 25 and record.get('handle') == grid:
                    record['bounds'][0] -= 60                             # 아래쪽 가운데 표가 왼쪽으로 60픽셀 밀림
            return report
        mes.report = scrolled_report
        before = OrderedDict(mes.leaves[4].columns)
        outcome = run(mes, widths=STANDARD)
        self.assertEqual(OrderedDict(mes.leaves[4].columns), before)
        self.assertEqual(outcome.result['scrolled'], ['아래쪽 가운데'])
        self.assertEqual(mes.bad, [])
        self.assertTrue(any('가로 스크롤을 왼쪽 끝으로' in line for line in layout.brief(outcome.result, 1.0)[1]))

    def test_column_whose_edge_is_outside_the_table_is_brought_in_by_borrowing_width(self):
        # 마지막 칸이 너무 넓어 경계가 표 밖에 있다 → 왼쪽의 넓은 칸을 잠시 줄여 들인 뒤 맞추고 되돌린다.
        wide = [(name, 130 if name == '영점' else STANDARD[name]) for name, _ in COLUMNS]
        mes = six(widths=[wide] * 6)
        run(mes, widths=OrderedDict(COLUMNS))                                # 판 크기만 먼저 같게
        for leaf in mes.leaves:
            leaf.columns = [list(item) for item in wide]
        grid = mes.rects[mes.leaves[0].grid]
        self.assertGreater(grid[0] + sum(width for _, width in wide), grid[2])   # 실제로 표 밖
        outcome = run(mes, widths=STANDARD)
        self.assertEqual(outcome.result['remaining'], OrderedDict())
        self.assert_widths(mes, STANDARD)
        self.assertEqual(mes.bad, [])

    def test_clipped_top_left_table_is_not_taken_as_the_standard(self):
        wide = [(name, 130 if name == '영점' else STANDARD[name]) for name, _ in COLUMNS]
        mes = six(widths=[wide] * 6)
        self.assertTrue(layout.clipped(layout.arrange(layout.grids(mes.report()))[0][0]))
        before = mes.widths()
        with self.assertRaises(RuntimeError) as caught:
            run(mes)
        self.assertIn('기준으로 삼을 수 없습니다', str(caught.exception))
        self.assertIn('[기준 저장]', str(caught.exception))
        self.assertEqual(mes.widths(), before)                              # 칸은 건드리지 않음
        self.assertEqual(mes.bad, [])

    def test_standard_is_taken_after_the_menu_is_narrowed_so_a_wide_menu_does_not_clip_it(self):
        # 메뉴 칸이 넓어 왼쪽 위 표가 잘려 보여도, 메뉴 칸을 줄이고 판을 맞춘 뒤의 너비를 기준으로 삼는다.
        mes = six(menu=260, positions=((520, 560), (700, 500), 380))
        self.assertTrue(layout.clipped(layout.arrange(layout.grids(mes.report()))[0][0]))
        outcome = run(mes)
        self.assertTrue(outcome.result['used_reference'])
        self.assertEqual(outcome.result['widths'], OrderedDict(COLUMNS))
        self.assertEqual(outcome.result['remaining'], OrderedDict())
        self.assertEqual(mes.bad, [])
        self.assertFalse(layout.clipped(layout.arrange(layout.grids(six().report()))[0][0]))

    def test_last_column_pushed_out_of_view_is_fixed_by_shrinking_first(self):
        # 넓힐 칸부터 끌면 마지막 칸 경계가 표 밖으로 밀려 잡을 수 없다 → 줄일 칸을 먼저 끈다.
        mes = six()
        outcome = run(mes, widths=STANDARD)
        self.assertEqual(outcome.result['remaining'], OrderedDict())
        self.assertEqual(mes.bad, [])

    def test_f9_stops_at_once_and_the_mouse_button_is_released(self):
        mes = six(widths=scrambled())
        user = FakeUser32(mes)
        mes.on_press = lambda model: user.keys.add(0x78) if model.presses == 9 else None
        with self.assertRaises(layout.Stopped):
            run(mes, widths=STANDARD, user=user)
        self.assertEqual(mes.presses, 9)
        self.assertFalse(user.down)
        self.assertIsNone(mes.grab)

    def test_stop_request_from_the_button_ends_the_run(self):
        mes = six(widths=scrambled())
        user = FakeUser32(mes)
        api = SimpleNamespace(u=user, target={'handle': 1, 'pid': 1}, Input=Input)
        pointer = layout.Pointer(api, sleep=user.sleep, clock=user.clock)
        stop = threading.Event()
        stop.set()
        with self.assertRaises(layout.Stopped):
            layout.align(api.target, pointer, lambda *a: mes.report(), stop, lambda *a: None, mes.report(), widths=STANDARD)
        self.assertEqual(mes.presses, 0)

    def test_swapped_mouse_buttons_still_press_the_primary_button(self):
        mes = six(widths=scrambled())
        user = FakeUser32(mes)
        user.swapped = True
        outcome = run(mes, widths=STANDARD, user=user)
        self.assertEqual(mes.bad, [])
        self.assertEqual(outcome.result['remaining'], OrderedDict())

    def test_unfound_divider_is_reported_as_uneven_panels(self):
        # 창 목록에서 경계선을 찾지 못해도(구성이 예상과 다름) '완료'라고 하지 않는다.
        mes = six()
        keep = mes.report
        def report():
            data = keep()
            data['records'] = [r for r in data['records'] if r.get('kind') != 'native_window']
            return data
        mes.report = report
        outcome = run(mes, widths=OrderedDict(COLUMNS))
        self.assertEqual(outcome.result['panels']['dividers'], 0)
        self.assertTrue(outcome.result['panels']['uneven'])
        title, lines = layout.brief(outcome.result, 1.0)
        self.assertIn('일부만', title)
        self.assertTrue(any(line.startswith('판 크기를 다 맞추지 못했습니다. 현재 표 크기:') for line in lines), lines)

    def test_another_window_in_front_or_a_held_key_stops_before_any_press(self):
        for change in (lambda user: setattr(user, 'foreground', 777), lambda user: user.keys.add(17)):
            mes = six(widths=scrambled())
            user = FakeUser32(mes)
            change(user)
            with self.assertRaises(RuntimeError):
                run(mes, widths=STANDARD, user=user)
            self.assertEqual(mes.presses, 0)

    def test_window_covering_an_edge_blocks_the_press_there(self):
        mes = six()
        target = OrderedDict(COLUMNS)
        target['거래처명'] = 150
        grid = mes.rects[mes.leaves[0].grid]
        mes.rects[9999] = (grid[0], grid[1] - 5, grid[2], grid[1] + 40)      # 왼쪽 위 표의 칸 제목을 덮은 다른 창
        mes.parent[9999] = 1
        keep = mes.layout
        def relayout():
            keep()
            now = mes.rects[mes.leaves[0].grid]
            mes.rects[9999] = (now[0], now[1] - 5, now[2], now[1] + 40)
            mes.parent[9999] = 1
        mes.layout = relayout
        mes.depth = lambda handle, original=mes.depth: 99 if handle == 9999 else original(handle)
        outcome = run(mes, widths=target)
        self.assertEqual(mes.bad, [])
        self.assertEqual(mes.widths()[0]['거래처명'], 120)                    # 가려진 표는 그대로
        self.assertEqual(mes.widths()[1]['거래처명'], 150)
        self.assertEqual(list(outcome.result['missed']), ['위쪽 왼쪽'])

    def test_changed_screen_between_readings_stops_the_run(self):
        mes = six(widths=scrambled())
        user = FakeUser32(mes)
        api = SimpleNamespace(u=user, target={'handle': 1, 'pid': 1}, Input=Input)
        pointer = layout.Pointer(api, sleep=user.sleep, clock=user.clock)
        def capture(target, text, stop):
            report = mes.report()
            report['records'] = [r for r in report['records'] if r.get('handle') != mes.leaves[5].grid]
            return report
        with self.assertRaises(RuntimeError) as caught:
            layout.align(api.target, pointer, capture, threading.Event(), lambda *a: None, mes.report(), widths=STANDARD)
        self.assertIn('화면 구성이 바뀌어', str(caught.exception))

    def test_no_production_table_is_an_error_before_any_mouse_move(self):
        mes = six()
        user = FakeUser32(mes)
        api = SimpleNamespace(u=user, target={'handle': 1, 'pid': 1}, Input=Input)
        pointer = layout.Pointer(api, sleep=user.sleep, clock=user.clock)
        with self.assertRaises(RuntimeError):
            layout.align(api.target, pointer, lambda *a: None, threading.Event(), lambda *a: None,
                         {'records': [{'kind': 'finish'}]}, widths=STANDARD)
        self.assertEqual(user.cursor, (5, 5))


class MenuTests(Checks, unittest.TestCase):
    def test_left_menu_is_pushed_to_the_far_left_before_panels_are_sized(self):
        for nesting in ('right', 'left'):
            mes = six(nesting, widths=scrambled(), menu=200)
            outcome = run(mes, widths=STANDARD)
            self.assertEqual(mes.menu, 25, nesting)                         # 갈 수 있는 데까지(최소 너비)
            self.assertEqual({key: outcome.result['menu'][key] for key in ('found', 'moved', 'failed', 'before', 'after')},
                             {'found': True, 'moved': True, 'failed': False, 'before': 200, 'after': 25})
            self.assert_even(mes)
            self.assert_widths(mes, STANDARD)
            self.assertEqual(mes.bad, [])
            self.assertEqual(outcome.result['remaining'], OrderedDict())
            title, lines = layout.brief(outcome.result, 5.0)
            self.assertTrue(title.startswith('MES 정렬 완료 · 메뉴 칸 200→25 · 판 6개'), title)
            self.assertEqual(lines, [])
            sizes = mes.grid_sizes()
            self.assertGreaterEqual(min(width for width, _ in sizes), 610)   # 넓어진 본문을 셋이 똑같이 나눔

    def test_menu_that_is_already_narrow_is_left_alone(self):
        mes = six(menu=25)
        outcome = run(mes, widths=OrderedDict(COLUMNS))
        self.assertEqual(mes.menu, 25)
        self.assertEqual((outcome.result['menu']['found'], outcome.result['menu']['moved']), (True, False))
        self.assertFalse(any('메뉴 칸' in line for line in [layout.brief(outcome.result, 1.0)[0]]))

    def test_menu_stops_where_the_screen_stops_it(self):
        tree_mes = six(menu=260)
        tree_mes.menu_minimum = 90                                          # 이 MES는 90까지만 줄어듦
        outcome = run(tree_mes, widths=OrderedDict(COLUMNS))
        self.assertEqual(tree_mes.menu, 90)
        self.assertEqual(outcome.result['menu']['after'], 90)
        self.assertEqual(tree_mes.bad, [])
        self.assert_even(tree_mes)

    def test_missing_or_ungrabbable_menu_divider_is_reported_and_the_rest_still_runs(self):
        mes = six(widths=scrambled(), menu=200)
        keep = mes.report
        def report():
            data = keep()
            data['records'] = [r for r in data['records'] if not (r.get('kind') == 'native_window' and r.get('handle') == 4)]
            return data
        mes.report = report
        outcome = run(mes, widths=STANDARD)
        self.assertFalse(outcome.result['menu']['found'])
        self.assertEqual(mes.menu, 200)
        self.assert_even(mes)                                               # 판 크기·칸 너비는 그대로 진행
        title, lines = layout.brief(outcome.result, 1.0)
        self.assertIn('일부만', title)
        self.assertTrue(any('왼쪽 메뉴 칸(파란 바)의 경계선을 찾지 못해' in line for line in lines), lines)
        frozen = six(menu=200)
        outcome = run(frozen, widths=OrderedDict(COLUMNS), frozen=True)
        self.assertTrue(outcome.result['menu']['failed'])
        self.assertEqual(frozen.presses, 0)
        self.assertTrue(any('줄이지 못했습니다' in line for line in layout.brief(outcome.result, 1.0)[1]))


class DescribeTests(unittest.TestCase):
    def test_structure_summary_lists_tabs_tables_columns_and_menu_but_no_row_values(self):
        mes = six(menu=200)
        text = layout.describe(mes.report(), rect=lambda handle: mes.rects[handle])
        self.assertIn('[탭]', text)
        self.assertIn('생산일보관리 (선택)', text)
        self.assertIn('표 @218,267', text)
        self.assertIn('칸 11개 · 행 1개', text)
        self.assertIn('거래처명@340,267 120x22', text)
        self.assertIn('창 구조: 창1100[WindowsForms10.Window.8.ap](218,267,', text)
        self.assertIn('[메뉴·탭 이름이 들어간 항목]', text)
        self.assertIn('작업지시관리 · 종류 36(outline item) @2,286 196x21', text)
        self.assertIn('[메뉴가 든 창의 구성] 창4', text)
        for secret in ('비밀환자', '홍길동치과', 'O1009'):
            self.assertNotIn(secret, text)

    def test_summary_works_without_window_positions_and_is_cut_when_too_long(self):
        mes = six()
        text = layout.describe(mes.report())
        self.assertIn('[표]', text)
        self.assertNotIn('위치 못 읽음', text)
        short = layout.describe(mes.report(), limit=10)
        self.assertEqual(len(short.split('\n')), 11)
        self.assertIn('줄임', short.split('\n')[-1])
        broken = layout.describe(mes.report(), rect=lambda handle: (_ for _ in ()).throw(RuntimeError('x')))
        self.assertIn('(위치 못 읽음)', broken)


class PointerTests(unittest.TestCase):
    def pointer(self, mes=None, **options):
        mes = mes or six()
        user = FakeUser32(mes, **options)
        api = SimpleNamespace(u=user, target={'handle': 1, 'pid': 1}, Input=Input)
        return mes, user, layout.Pointer(api, sleep=user.sleep, clock=user.clock)

    def test_pointer_lands_on_the_exact_pixel(self):
        mes, user, pointer = self.pointer()
        for point in ((661, 427), (1289, 835), (43, 318), (1916, 1029), (977, 637)):
            self.assertEqual(pointer.move(point), point)

    def test_button_is_released_even_when_the_drag_fails_midway(self):
        mes, user, pointer = self.pointer()
        grid = mes.rects[mes.leaves[0].grid]
        edge = (grid[0] + 37 - 2, grid[1] + 11)
        self.assertEqual(pointer.find_edge((grid[0] + 18, grid[1] + 11), [edge], lambda hit: hit == mes.leaves[0].grid), edge)
        with self.assertRaises(RuntimeError):
            pointer.drag(edge, (5000, edge[1]))                              # 모니터 밖
        self.assertFalse(user.down)

    def test_same_spot_is_never_pressed_twice_within_the_double_click_time(self):
        # 같은 경계를 곧바로 다시 잡으면 더블클릭(자동 맞춤)이 되므로 간격을 둔다.
        mes, user, pointer = self.pointer()
        leaf = mes.leaves[0]
        grid = mes.rects[leaf.grid]
        y = grid[1] + 11
        for _ in range(3):
            edge = grid[0] + sum(width for _, width in leaf.columns[:4])
            point = pointer.find_edge((edge - 60, y), [(edge - 2, y)], lambda hit: hit == leaf.grid)
            pointer.drag(point, (point[0] + 3, y))
        self.assertEqual(mes.bad, [])
        self.assertEqual(leaf.columns[3][1], 129)
        self.assertEqual(len([seconds for seconds in user.sleeps if seconds >= 0.3]), 2)

    def test_pointer_returns_to_where_the_user_left_it(self):
        mes, user, pointer = self.pointer()
        pointer.move((900, 500))
        pointer.restore()
        self.assertEqual(user.cursor, (5, 5))

    def test_hidden_pointer_is_unknown_not_a_resize_shape(self):
        mes, user, pointer = self.pointer()
        user._GetCursorInfo = lambda reference: setattr(reference._obj, 'flags', 0) or 1
        user.GetCursorInfo = lambda *args: user._GetCursorInfo(*args)
        self.assertIsNone(pointer.shape())
        self.assertFalse(pointer.resizing(None, ARROW))


class PresetTests(unittest.TestCase):
    def test_standard_is_saved_and_read_back_in_column_order(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'Jihunius', 'mes_layout.json')
            self.assertIsNone(layout.load_preset(path))
            saved = layout.save_preset(path, STANDARD, '위쪽 왼쪽')
            self.assertEqual(list(layout.load_preset(path).items()), list(STANDARD.items()))
            self.assertEqual(layout.preset_saved_at(path), saved['saved_at'])
            self.assertFalse(os.path.exists(path + '.tmp'))

    def test_broken_or_unreasonable_file_is_treated_as_no_standard(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'mes_layout.json')
            for text in ('', '{', '[]', '{"columns": 5}', '{"columns": [["거래처명", "넓게"], ["", 30], ["치식", 1], ["비고", true]]}'):
                Path(path).write_text(text, encoding='utf-8')
                self.assertIsNone(layout.load_preset(path), text)
            Path(path).write_text('{"columns": [["거래처명", 150], ["치식", 99999]]}', encoding='utf-8')
            self.assertEqual(dict(layout.load_preset(path)), {'거래처명': 150})


class BriefTests(unittest.TestCase):
    def test_summary_tells_what_was_done_and_what_is_left(self):
        mes = six(widths=scrambled())
        outcome = run(mes)
        title, lines = layout.brief(outcome.result, 6.24)
        self.assertTrue(title.startswith('MES 정렬 완료 · 판 6개 · 경계 '), title)
        self.assertIn('6.2초', title)
        self.assertIn('위쪽 왼쪽 판의 너비를 기준으로 저장', title)
        self.assertEqual(lines, [])
        wide = OrderedDict(STANDARD)
        wide['거래처명'] = 400
        outcome = run(six(), widths=wide)
        self.assertTrue(any('가로 스크롤' in line for line in layout.brief(outcome.result, 1.0)[1]))


if __name__ == '__main__':
    unittest.main()
