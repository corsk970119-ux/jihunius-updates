"""가짜 MES 화면(시험용). 실제 MES에서 '조작 점검'으로 확인한 구조를 본뜹니다(2026-11-13 현장 결과).

  MES(1) → 나뉜 창(3) → [왼쪽 메뉴 칸(4) → 메뉴(7)] | 경계선 | [문서 영역(5)]
  문서 영역에는 문서가 겹쳐 있고, 뒤에 가려진 문서의 창과 표도 화면 판독에는 그대로 나옵니다.
    문서 '작업지시관리'(200) → 탭(201): 작업지시관리(넓은 표 하나, 쪽 202) / 작업지시조회(쪽 203) / 생산일보관리(판 6개, 쪽 2)
    문서 '설비별공구관리'(210) → 탭(211) → 쪽 212: 표 하나
  메뉴: 묶음(종류 33)은 맨 위 23픽셀이 이름 줄이고 펼쳐지면 항목들까지 포함합니다. 항목(종류 30)은 펼쳐진 묶음에서만 위치가 있습니다.
  규칙: 경계선 위에서만 포인터가 크기 조절 모양이 되고, 칸 제목 가운데를 누르면 정렬(=잘못된 누름)로 기록하며,
        같은 자리를 빠르게 두 번 누르면 더블클릭(자동 맞춤)이 됩니다.
"""
import ctypes
from collections import OrderedDict

ARROW, WAIT, BUSY, SIZEWE, VSPLIT, HSPLIT, MOVING = 65539, 65543, 65561, 65555, 70001, 70003, 71001
COLUMNS = (('No.', 37), ('선택', 38), ('P/No.', 47), ('거래처명', 120), ('Fixture', 58), ('Size', 54),
           ('환자명', 46), ('치식', 37), ('세척', 40), ('비고', 55), ('영점', 50))
WORK_COLUMNS = (('선택', 35), ('PART-NO', 90), ('품명', 130), ('지시일', 90), ('시간', 80), ('프로젝트No', 100), ('T31수정', 60),
                ('작업자코드', 80), ('작업자', 100), ('좌석번호', 60), ('설비코드', 80), ('설비명', 150), ('거래처코드', 100),
                ('거래처명', 140), ('지역', 50), ('Fixture Name', 80), ('Type', 60), ('Size', 60), ('치과명', 80), ('환자명', 80),
                ('치식', 50), ('stl', 50), ('납기일', 90), ('배송업체', 80), ('출하일', 90), ('진행상태', 90), ('세척순서', 70),
                ('길이', 50), ('특이사항1', 100), ('특이사항2', 100), ('특이사항3', 100))
TOOL_COLUMNS = (('선택', 35), ('설비코드', 100), ('설비명', 150), ('공구대', 80), ('공구코드', 110), ('공구명', 130))
WORK_TABS = ('작업지시관리', '작업지시조회', '생산일보관리')
TOOL_TABS = ('설비별공구관리', '공구교체이력관리')
HEADER = 22


class Leaf:
    """표 하나: 사용자 컨트롤 창(panel) 안에 표 창(grid)이 있습니다."""
    def __init__(self, handle, columns=COLUMNS, minimum=20, fixed=()):
        self.panel = handle
        self.grid = handle + 1000
        self.columns = [[name, width] for name, width in columns]
        self.minimum = minimum
        self.fixed = set(fixed)      # 너비를 바꿀 수 없는 칸
        self.scroll = 0              # 가로로 밀린 픽셀


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
    return FakeMes(tree, menu, panels=leaves)


class FakeMes:
    def __init__(self, tree, menu=25, menu_minimum=25, panels=()):
        self.tree = tree
        self.panels = list(panels)           # 생산일보 판 6개
        self.work = Leaf(220, WORK_COLUMNS)  # 작업지시관리 탭의 표
        self.tool = Leaf(230, TOOL_COLUMNS)  # 설비별공구관리 문서의 표
        self.menu = menu                     # 왼쪽 메뉴 칸(파란 바) 너비
        self.menu_minimum = menu_minimum
        self.bad = []            # 잘못된 누름(칸 제목 가운데 등)과 더블클릭
        self.presses = 0
        self.grab = None
        self.last_down = None
        self.on_press = None
        # 아래는 '조작 점검' 시험용 동작(기본은 꺼 둠: 생산일보 정렬은 칸 제목을 누르면 안 됨)
        self.allow_moves = False     # 칸 제목을 끌어 순서 바꾸기·없애기
        self.allow_clicks = False    # 왼쪽 메뉴·탭 누르기
        self.escape_cancels = True
        self.hwheel_works = True
        self.shift_wheel_works = True
        self.hidden = []             # 없앤 칸 이름
        self.near_edge_since = None
        self.inner = '생산일보관리'  # 작업지시관리 문서에서 선택된 안쪽 탭
        self.documents = ['작업지시관리']
        self.active = '작업지시관리'  # 맨 앞 문서
        self.groups = OrderedDict((('설비관리', ['설비관리', '공구관리', '설비별공구관리']),
                                   ('생산관리', ['작업지시관리', '생산실적관리'])))
        self.expanded = '생산관리'
        self.layout()

    # ── 창 배치 ──
    def layout(self):
        body = self.menu + 12
        self.menu_bar = (self.menu, 23, body, 1030)
        self.rects = {1: (0, 0, 1920, 1080), 3: (0, 23, 1920, 1030), 4: (0, 23, self.menu, 1030),
                      7: (1, 192, max(3, self.menu - 1), 1029), 5: (body, 23, 1920, 1030)}
        self.parent = {1: 0, 3: 1, 4: 3, 7: 4, 5: 3}
        self.owner = {}
        self.leaves = []
        self.splits = []
        page = (body + 3, 180, 1917, 1030)
        for name in self.documents:
            before = set(self.rects)
            if name == '작업지시관리':
                self.rects[200] = self.rects[201] = (body + 2, 153, 1918, 1030)
                self.parent[200], self.parent[201] = 5, 200
                if self.inner == '생산일보관리':
                    self.rects[2], self.parent[2] = page, 201
                    self.place(self.tree, page, 2)
                elif self.inner == '작업지시관리':
                    self.rects[202], self.parent[202] = page, 201
                    self.place(self.work, page, 202)
                else:
                    self.rects[203], self.parent[203] = page, 201
            else:
                self.rects[210] = self.rects[211] = (body + 2, 153, 1918, 1030)
                self.parent[210], self.parent[211] = 5, 210
                self.rects[212], self.parent[212] = page, 211
                self.place(self.tool, page, 212)
            for handle in set(self.rects) - before:
                self.owner[handle] = name

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
        """그 자리의 맨 위 창. 뒤에 가려진 문서의 창은 창 목록에는 있어도 여기에는 잡히지 않습니다."""
        inside = [h for h, (l, t, r, b) in self.rects.items()
                  if l <= x < r and t <= y < b and self.owner.get(h, self.active) == self.active]
        return max(inside, key=self.depth) if inside else 0

    def leaf(self, handle):
        return next((leaf for leaf in self.leaves if leaf.grid == handle), None)

    # ── 메뉴·탭 ──
    def nav_layout(self):
        """[(종류, 이름, 사각형 또는 None)] 위→아래. 펼쳐진 묶음의 사각형은 항목들까지 포함합니다."""
        left, top, right, _ = self.rects[7]
        found = []
        y = top
        for group, entries in self.groups.items():
            if group == self.expanded:
                height = 23 + 42 * len(entries)
                found.append(('group', group, (left, y, right, y + height)))
                for index, entry in enumerate(entries):
                    found.append(('item', entry, (left, y + 23 + 42 * index, right, y + 23 + 42 * (index + 1))))
                y += height
            else:
                found.append(('group', group, (left, y, right, y + 23)))
                found.extend(('item', entry, None) for entry in entries)
                y += 23
        return found

    def tab_rect(self, index):
        return (self.menu + 15 + 94 * index, 155, self.menu + 109 + 94 * index, 178)

    def click(self, x, y):
        hit = self.window_at(x, y)
        if hit == 7:
            layout = self.nav_layout()
            for kind, name, rect in layout:
                if kind == 'item' and rect and rect[0] <= x < rect[2] and rect[1] <= y < rect[3]:
                    if name in ('작업지시관리', '설비별공구관리'):
                        if name not in self.documents:
                            self.documents.append(name)
                        self.active = name
                        self.layout()
                    else:
                        self.bad.append('다른 메뉴 항목을 누름: ' + name)
                    return
            for kind, name, rect in layout:
                if kind == 'group' and rect[0] <= x < rect[2] and rect[1] <= y < rect[1] + 23:
                    self.expanded = name
                    return
            self.bad.append('메뉴의 빈 곳을 누름 ({}, {})'.format(x, y))
            return
        if hit in (201, 211):
            for index, name in enumerate(WORK_TABS if hit == 201 else TOOL_TABS):
                l, t, r, b = self.tab_rect(index)
                if l <= x < r and t <= y < b:
                    if hit == 201:
                        self.inner = name
                        self.layout()
                    return
        self.bad.append('아무것도 없는 곳을 누름: 창 {} ({}, {})'.format(hit, x, y))

    # ── 표 ──
    def edge_at(self, leaf, x, y):
        left, top, right, _ = self.rects[leaf.grid]
        if not (top <= y < top + HEADER and left <= x < right):
            return None
        position = left - leaf.scroll
        best = None
        for index, (name, width) in enumerate(leaf.columns):
            position += width
            if name not in leaf.fixed and position - 4 <= x <= position + 3:
                if best is None or abs(x - position) < best[0]:
                    best = (abs(x - position), index)
        return None if best is None else best[1]

    def header_at(self, leaf, x, y):
        """(칸 번호, 왼쪽 절반인지) 또는 None"""
        left, top, right, _ = self.rects[leaf.grid]
        if not (top <= y < top + HEADER and left <= x < right):
            return None
        position = left - leaf.scroll
        for index, (name, width) in enumerate(leaf.columns):
            if position <= x < position + width:
                return index, x < position + width / 2.0
            position += width
        return None

    def near_right_edge(self, leaf, x):
        return self.rects[leaf.grid][2] - 14 <= x < self.rects[leaf.grid][2]

    def scroll_by(self, leaf, amount):
        left, _, right, _ = self.rects[leaf.grid]
        limit = max(0, sum(width for _, width in leaf.columns) - (right - left))
        leaf.scroll = max(0, min(limit, leaf.scroll + amount))

    def moved_to(self, x, y, now):
        if self.grab and self.grab[0] == 'move' and self.near_right_edge(self.grab[1], x):
            if self.near_edge_since is None:
                self.near_edge_since = now
        else:
            self.near_edge_since = None

    def settle_autoscroll(self, now):
        if self.grab and self.grab[0] == 'move' and self.near_edge_since is not None and now - self.near_edge_since >= 1.0:
            self.scroll_by(self.grab[1], 90)
        self.near_edge_since = None

    def escape(self, now):
        if self.grab and self.grab[0] == 'move':
            self.settle_autoscroll(now)
            if self.escape_cancels:
                self.grab = None

    def wheel(self, x, y, notches, horizontal, shift):
        leaf = self.leaf(self.window_at(x, y))
        if leaf is None:
            return
        if horizontal and self.hwheel_works:
            self.scroll_by(leaf, notches * 40)
        elif not horizontal and shift and self.shift_wheel_works:
            self.scroll_by(leaf, -notches * 40)

    def on_menu_bar(self, hit, x, y):
        l, t, r, b = self.menu_bar
        return hit == 3 and l <= x < r and t <= y < b

    def shape_at(self, x, y):
        hit = self.window_at(x, y)
        if self.grab and self.grab[0] == 'move':
            return MOVING
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
        else:
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
                header = self.header_at(leaf, x, y) if leaf is not None else None
                if edge is not None and double:
                    self.bad.append('칸 경계 더블클릭(자동 맞춤): ' + leaf.columns[edge][0])
                    leaf.columns[edge][1] = 77
                elif edge is not None:
                    self.grab = ('column', leaf, edge, x)
                elif header is not None and self.allow_moves:
                    self.grab = ('move', leaf, header[0], x, y)
                elif hit in (7, 201, 211) and self.allow_clicks:
                    self.grab = ('click', x, y)
                else:
                    self.bad.append('경계가 아닌 곳을 누름: 창 {} ({}, {})'.format(hit, x, y))
        if self.on_press:
            self.on_press(self)

    def release(self, x, y):
        grab, self.grab = self.grab, None
        if not grab:
            return
        if grab[0] == 'click':
            if (x, y) == (grab[1], grab[2]):
                self.click(x, y)
        elif grab[0] == 'move':
            leaf, index = grab[1], grab[2]
            if abs(x - grab[3]) < 4 and abs(y - grab[4]) < 4:
                self.bad.append('칸 제목을 끌지 않고 누름(정렬됨): ' + leaf.columns[index][0])
                return
            target = self.header_at(leaf, x, y)
            left, top, right, bottom = self.rects[leaf.grid]
            if target is None:
                if left <= x < right and top + HEADER <= y < bottom:     # 표 안쪽에 놓으면 칸이 없어짐
                    self.hidden.append(leaf.columns.pop(index)[0])
                return
            item = leaf.columns.pop(index)
            place = target[0] - (1 if target[0] > index else 0)
            leaf.columns.insert(place if target[1] else place + 1, item)
        elif grab[0] == 'menu':
            self.menu = max(self.menu_minimum, min(600, self.menu + x - grab[1]))
            self.layout()
        elif grab[0] == 'split':
            split = grab[1]
            split.position += (x - grab[2]) if split.vertical else (y - grab[3])
            self.layout()
        else:
            leaf, index, start = grab[1], grab[2], grab[3]
            leaf.columns[index][1] = max(leaf.minimum, leaf.columns[index][1] + x - start)

    # ── 화면 판독 결과 ──
    def report(self, root=None):
        """root를 주면 그 창 아래만 읽은 것처럼 돌려줍니다."""
        def under(handle):
            while handle:
                if handle == root:
                    return True
                handle = self.parent.get(handle, 0)
            return root is None

        records = [{'kind': 'native_window', 'handle': handle, 'native_parent': parent,
                    'class': 'WindowsForms10.Window.8.app.0.1'} for handle, parent in self.parent.items() if under(handle)]
        ident = [0]

        def element(**values):
            ident[0] += 1
            values.update(kind='element', id=ident[0])
            if under(values.get('handle')):
                records.append(values)
            return ident[0]

        for name in self.documents:
            control = 201 if name == '작업지시관리' else 211
            chosen = self.inner if control == 201 else TOOL_TABS[0]
            for index, tab in enumerate(WORK_TABS if control == 201 else TOOL_TABS):
                l, t, r, b = self.tab_rect(index)
                element(parent=-1, role=37, handle=control, name=tab, selected=tab == chosen, type='page tab',
                        bounds=[l, t, r - l, b - t])
        for window in (4, 7):       # 메뉴는 바깥 창 이름으로도 한 번 더 읽힙니다(실제와 같음).
            l, t, r, b = self.rects[7]
            bar = element(parent=-1, role=16, handle=window, name='navBarControl1', type='pane', depth=0, bounds=[l, t, r - l, b - t])
            group = None
            for kind, name, rect in self.nav_layout():
                if kind == 'group':
                    group = element(parent=bar, role=33, handle=window, name=name, type='list', depth=1,
                                    bounds=[rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]])
                else:
                    element(parent=group, role=30, handle=window, name=name, type='link', depth=2, offscreen=rect is None,
                            bounds=[rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]] if rect else [0, 0, 0, 0])
        for leaf in self.leaves:
            left, top, right, bottom = self.rects[leaf.grid]
            table = element(parent=-1, role=24, handle=leaf.grid, name='', offscreen=False,
                            bounds=[left, top, right - left, bottom - top])
            group = element(parent=table, role=10, handle=leaf.grid, name='헤더 패널')
            x = left - leaf.scroll
            for name, width in leaf.columns:
                element(parent=group, role=25, handle=leaf.grid, name=name, bounds=[x, top, width, HEADER],
                        offscreen=x >= right or x + width <= left)
                x += width
            data = element(parent=table, role=10, handle=leaf.grid, name='데이터 패널', child_count=1)
            line = element(parent=data, role=28, handle=leaf.grid, name='행 1', value='O1009;홍길동치과;비밀환자;', bounds=[left, top + HEADER, 500, 20])
            element(parent=line, role=29, handle=leaf.grid, name='환자명 row 0', value='비밀환자')
        records.append({'kind': 'finish', 'limited': False, 'elements': ident[0]})
        return {'records': records, 'exit_code': 0, 'target': {'handle': root or 1}}

    def grid_sizes(self):
        return [(self.rects[leaf.grid][2] - self.rects[leaf.grid][0], self.rects[leaf.grid][3] - self.rects[leaf.grid][1])
                for leaf in self.panels]

    def widths(self):
        return [OrderedDict(leaf.columns) for leaf in self.panels]

    def snapshot(self):
        """되돌렸는지 비교할 전체 상태."""
        return ([list(map(tuple, leaf.columns)) for leaf in self.panels + [self.work, self.tool]],
                [leaf.scroll for leaf in self.panels + [self.work, self.tool]], self.menu,
                [(split.handle, split.position) for split in self.splits], self.active, self.inner)


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
                     'GetWindowRect', 'GetAsyncKeyState', 'GetForegroundWindow', 'GetSystemMetrics', 'SendInput',
                     'keybd_event'):
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

    def _keybd_event(self, code, scan, flags, extra):
        self.now[0] += 0.0005
        if flags & 2:
            self.keys.discard(code)
        else:
            self.keys.add(code)
            if code == 0x1B:
                self.mes.escape(self.now[0])
                self.keys.discard(code)     # 시험에서는 Esc를 눌렀다 바로 뗀 것으로 봅니다.

    def _GetSystemMetrics(self, index):
        return {76: 0, 77: 0, 78: 1920, 79: 1080, 23: int(self.swapped)}[index]

    def _SendInput(self, count, reference, size):
        self.now[0] += 0.0005
        mouse = reference._obj.payload.mi
        if mouse.flags & 0x0001:
            # 실제 Windows처럼 환산 과정에서 1픽셀 어긋날 수 있게 내림으로 계산합니다.
            self.cursor = (mouse.dx * 1919 // 65535, mouse.dy * 1079 // 65535)
            self.waiting = self.lag
            self.mes.moved_to(self.cursor[0], self.cursor[1], self.now[0])
        if mouse.flags & (0x0800 | 0x1000):
            notches = ctypes.c_int32(mouse.data).value // 120
            self.mes.wheel(self.cursor[0], self.cursor[1], notches, bool(mouse.flags & 0x1000), 0x10 in self.keys)
        press, release = (0x0008, 0x0010) if self.swapped else (0x0002, 0x0004)
        if mouse.flags & (0x0002 | 0x0008 | 0x0004 | 0x0010) & ~(press | release):
            self.mes.bad.append('주 버튼이 아닌 버튼을 누름')
        if mouse.flags & press:
            self.down = True
            self.mes.press(self.cursor[0], self.cursor[1], self.now[0])
        if mouse.flags & release:
            self.down = False
            self.mes.settle_autoscroll(self.now[0])
            self.mes.release(*self.cursor)
        return count
