"""MES 조작 점검.

지후니우스 'MES 정렬'이 쓰려는 조작이 실제 MES에서 어떻게 먹히는지, 작게 해 보고 되돌린 뒤 결과를 글로 정리합니다.
스스로 화면을 찾아갑니다: 왼쪽 메뉴로 작업지시관리를 앞에 띄우고 → '작업지시관리' 탭의 표에서 칸 시험 →
'생산일보관리' 탭에서 칸 시험 → (선택) 설비별공구관리를 열었다가 작업지시관리로 돌아오기.
  · 칸 경계의 포인터 모양, 칸 너비 끌기(되돌림)
  · 칸 제목을 끌어 순서 바꾸기(되돌림), Esc로 끌기 취소
  · 표 가로 스크롤, 칸을 끈 채 표 끝에 두었을 때의 자동 스크롤
  · (선택) 칸 없애기
누르기 전에는 항상 그 자리의 맨 위 창이 누르려는 표·메뉴·탭인지 확인하고, 아니면 누르지 않습니다.
MES의 행·값·저장은 건드리지 않습니다. 결과 글에는 칸 제목·탭·메뉴 이름과 숫자만 들어가고 행의 값은 들어가지 않습니다.

이 파일은 tools/build_mes_probe.py가 만든 결과물로 실행합니다(아래 값들이 빌드 때 채워짐).
"""
import os
import queue
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

PROBE_VERSION = '2'
APP_VERSION = ...  # build: 지후니우스 버전
WASH_POP_SOURCE = ...  # build: src/host/wash_pop.py
WASH_MES_SOURCE = ...  # build: src/host/wash_mes.py
WASH_READER_SOURCE = ...  # build: src/host/jihunius_main.py 의 WashReader
MES_LAYOUT_SOURCE = ...  # build: src/host/mes_layout.py

NARROW_BOUNDS = ("if(role==24 || role==25 || role==28 || (role==29 && CellBoundsMode!=1 && !skipCellBounds) || "
                 "role==37 || (role>=41 && role<=47)) {")
WIDE_BOUNDS = "if(role!=29 || (CellBoundsMode!=1 && !skipCellBounds)) {"
WORK_GROUP, WORK_ITEM = '생산관리', '작업지시관리'      # 메뉴 묶음 → 항목
TOOL_GROUP, TOOL_ITEM = '설비관리', '설비별공구관리'
WORK_TAB, DAILY_TAB = '작업지시관리', '생산일보관리'    # 작업지시관리 문서의 안쪽 탭
MENU_WORKING_WIDTH = 200                                # 메뉴를 누를 때의 메뉴 칸 너비


def load(source, name):
    scope = {'__name__': name}
    exec(compile(source, name + '.py', 'exec'), scope)
    return SimpleNamespace(**scope)


def explain(error):
    return '{}: {}'.format(type(error).__name__, error)


def experiments(env):
    """조작 시험을 차례로 하고 결과 줄들을 돌려줍니다. env: L(정렬 모듈), pointer, read(이름, 넓게, 뿌리 창), log, options, clock."""
    L, pointer, log = env.L, env.pointer, env.log
    out = ['MES 조작 점검 결과 · 점검 {} · 지후니우스 {}'.format(PROBE_VERSION, APP_VERSION)]
    say = out.append
    state = {'escape': None, 'scroll': None, 'removed': None, 'doc': None, 'menu': None, 'times': {}}
    box = {'grid': None}

    def section(title):
        say('')
        say('■ ' + title)
        log(title + '…')

    def attempt(title, action):
        """시험 하나. 오류가 나도 다음 시험은 계속합니다. 반환: 끝까지 했는지"""
        section(title)
        try:
            action()
            return True
        except L.Stopped:
            raise
        except Exception as failure:
            say('  ✗ 이 시험은 중단: ' + str(failure) if isinstance(failure, RuntimeError) else '  ✗ 이 시험은 오류로 중단: ' + explain(failure))
            if not isinstance(failure, RuntimeError):
                say('    ' + ' / '.join(line.strip() for line in traceback.format_exc().strip().splitlines()[-4:])[:500])
            return False
        finally:
            if pointer.holding:
                pointer.drop()

    def read(label, wide=False, root=None, kind='전체'):
        started = env.clock()
        report = env.read(label, wide, root)
        state['times'].setdefault(kind + (' 넓게' if wide else ''), []).append(env.clock() - started)
        return report

    # ── 누르기: 그 자리의 맨 위 창을 먼저 확인합니다 ──
    def held(point, handle, what):
        hit = pointer.window_at(point)
        if hit != handle:
            raise RuntimeError('{}: 그 자리({}, {})의 맨 위 창이 다른 창(창{})이라 누르지 않았습니다.'.format(what, point[0], point[1], hit))
        pointer.hold(point)

    def tap(point, handle, what):
        hit = pointer.window_at(point)
        if handle not in pointer.lineage(hit):
            raise RuntimeError('{}: 그 자리({}, {})의 맨 위 창이 다른 창(창{})이라 누르지 않았습니다.'.format(what, point[0], point[1], hit))
        pointer.click(point)

    # ── 표 읽기 ──
    def tables(report):
        """앞에 보이는 표(칸 제목이 있는 것)만, 위→아래·왼쪽→오른쪽."""
        return [grid for row in L.arrange(L.front(L.grids(report, required=()), pointer)) for grid in row]

    def names(grid):
        return [column['name'] for column in grid['columns']]

    def order(grid):
        """표의 모든 칸 이름을 왼쪽부터(표 밖 칸 포함). 위치를 모르는 칸은 판독 순서대로 뒤에 둡니다."""
        placed = sorted((header for header in grid['headers'] if header[3] > 0), key=lambda header: header[1])
        return [header[0] for header in placed] + [header[0] for header in grid['headers'] if header[3] <= 0]

    def column(grid, name):
        return next((item for item in grid['columns'] if item['name'] == name), None)

    def whole(grid, item):
        return grid['x'] <= item['x'] and item['x'] + item['w'] + 6 <= grid['x'] + grid['w']

    def middle(item):
        return item['x'] + item['w'] // 2, item['y'] + item['h'] // 2

    def place(grid, name):
        return {header[0]: header[1] for header in grid['headers']}.get(name)

    def listing(grid):
        right = grid['x'] + grid['w']
        text = ['{}{} {}'.format('▷' if header[1] >= right else ('◁' if header[1] < grid['x'] - 1 else ''), header[0], header[3])
                for header in sorted(grid['headers'], key=lambda header: (header[3] <= 0, header[1]))]
        return ['    ' + ' | '.join(text[start:start + 10]) for start in range(0, len(text), 10)]

    def refresh(label):
        report = read(label, False, state['doc'], '문서만')
        for grid in tables(report):
            if grid['handle'] == box['grid']['handle']:
                box['grid'] = grid
                return grid
        raise RuntimeError('시험하던 표가 화면 앞에서 사라졌습니다.')

    def pick():
        """시험에 쓸 나란한 두 칸(이름이 있고 다 보이는 것)."""
        grid = box['grid']
        columns = grid['columns']
        for start in (2, 1, 0):
            for index in range(start, len(columns) - 1):
                one, two = columns[index], columns[index + 1]
                if one['name'] and two['name'] and whole(grid, one) and whole(grid, two) and one['w'] >= 30 and two['w'] >= 30:
                    return one['name'], two['name']
        raise RuntimeError('나란히 다 보이는 칸 두 개를 찾지 못했습니다.')

    # ── 메뉴 ──
    def menu_tree():
        return L.nav_tree(read('메뉴', True, state['menu'], '메뉴만'))

    def open_from_menu(group_name, item_name):
        """메뉴에서 묶음을 (접혀 있으면) 펼치고 항목을 눌러 그 화면을 앞으로 가져옵니다."""
        def find():
            tree = menu_tree()
            group = next((one for one in tree if one['name'] == group_name), None)
            if group is None:
                raise RuntimeError('메뉴에서 묶음 "{}"을 찾지 못했습니다. 보이는 묶음: {}'.format(group_name, ', '.join(one['name'] for one in tree)))
            entry = next((one for one in group['items'] if one['name'] == item_name), None)
            if entry is None:
                raise RuntimeError('묶음 "{}"에서 항목 "{}"을 찾지 못했습니다.'.format(group_name, item_name))
            return group, entry
        group, entry = find()
        if not entry['shown']:
            say('  묶음 "{}"이 접혀 있음 → 이름 줄 ({}, {})을 누름'.format(group_name, group['head'][0], group['head'][1]))
            tap(group['head'], group['handle'], '묶음 ' + group_name)
            pointer.sleep(0.8)
            group, entry = find()
            if not entry['shown']:
                raise RuntimeError('묶음 "{}"의 이름 줄을 눌러도 항목 "{}"이 보이지 않습니다.'.format(group_name, item_name))
            say('  → 묶음이 펼쳐짐 · "{}" @{},{} {}x{}'.format(item_name, entry['x'], entry['y'], entry['w'], entry['h']))
        point = (entry['x'] + entry['w'] // 2, entry['y'] + entry['h'] // 2)
        say('  항목 "{}" ({}, {})을 한 번 누름'.format(item_name, point[0], point[1]))
        tap(point, group['handle'], '항목 ' + item_name)
        pointer.sleep(1.6)

    def front_tab(report, name):
        """앞에 보이는 탭 name(없으면 None)."""
        for item in L.elements(report):
            bounds = item.get('bounds') or ()
            if item.get('role') == 37 and str(item.get('name', '')).strip() == name and len(bounds) == 4 and bounds[2] > 4:
                point = (bounds[0] + bounds[2] // 2, bounds[1] + bounds[3] // 2)
                if item.get('handle') in pointer.lineage(pointer.window_at(point)):
                    return item, point
        return None

    def select_tab(name):
        """작업지시관리 문서의 안쪽 탭을 고릅니다. 그 문서 아래를 읽은 결과를 돌려줍니다."""
        found = front_tab(read('탭', False, state['doc'], '문서만' if state['doc'] else '전체'), name)
        if found is None:
            raise RuntimeError('탭 "{}"이 화면 앞에 보이지 않습니다.'.format(name))
        tab, point = found
        state['doc'] = tab.get('handle')
        if tab.get('selected'):
            say('  탭 "{}"은 이미 선택돼 있음'.format(name))
        else:
            tap(point, tab.get('handle'), '탭 ' + name)
            pointer.sleep(1.2)
            say('  탭 "{}" ({}, {})을 누름'.format(name, point[0], point[1]))
        return read(name + ' 탭', False, state['doc'], '문서만')

    # ── 환경과 처음 화면 ──
    u = pointer.u
    say('화면 {}x{} (시작 {},{}) · MES 창 {} · 화살표 모양 {} · 더블클릭 간격 {:.0f}ms · 좌우 버튼 바꿈 {}'.format(
        u.GetSystemMetrics(78), u.GetSystemMetrics(79), u.GetSystemMetrics(76), u.GetSystemMetrics(77),
        pointer.rect(pointer.root), pointer.arrow, (pointer.double_click - 0.08) * 1000,
        '예' if pointer.press_flag == 0x0008 else '아니오'))
    section('처음 화면')
    first = read('처음 화면', True)
    say(L.describe(first, at=pointer.window_at))
    native = L.native_parents(first)
    tree = L.nav_tree(first)
    if not tree:
        say('')
        say('✗ 왼쪽 메뉴를 읽지 못했습니다. 여기서 멈춥니다.')
        return out
    state['menu'] = tree[0]['handle']
    selected_at_start = next((str(item.get('name', '')).strip() for item in L.elements(first)
                              if item.get('role') == 37 and item.get('selected') and str(item.get('name', '')).strip() in (WORK_TAB, DAILY_TAB, '작업지시조회')), None)
    menu_item = L.menu_divider_beside(native, pointer, state['menu'])
    menu_width = None

    def menu_size():
        left, _, right, _ = pointer.rect(menu_item['first'])
        return right - left

    def pull_menu(amount):
        if not L.drag_divider(pointer, menu_item, amount, lambda kind, value: None):
            raise RuntimeError('메뉴 칸 경계에서 크기 조절 모양을 확인하지 못해 누르지 않았습니다 · ' + pointer.trace)
        L.settle(pointer, menu_item)
        pointer.sleep(0.3)

    # ── 1. 메뉴 칸을 넓히고 작업지시관리를 앞으로 ──
    def widen_menu():
        if menu_item is None:
            raise RuntimeError('메뉴 칸의 경계를 창 구조에서 찾지 못했습니다.')
        width = menu_size()
        say('  메뉴 칸 너비 {}'.format(width))
        if width < MENU_WORKING_WIDTH - 20:
            pull_menu(MENU_WORKING_WIDTH - width)
            say('  경계를 오른쪽으로 끌어 넓힘 → 너비 {}'.format(menu_size()))

    def bring_work():
        open_from_menu(WORK_GROUP, WORK_ITEM)
        report = read('작업지시관리를 누른 뒤', False)
        found = front_tab(report, WORK_TAB)
        if found is None:
            raise RuntimeError('메뉴에서 작업지시관리를 눌렀지만, 그 문서의 탭이 앞에 보이지 않습니다.')
        state['doc'] = found[0].get('handle')
        say('  → 작업지시관리 문서가 앞에 옴 (탭 창{})'.format(state['doc']))

    # ── 2. 칸 시험(지금 box['grid']에 든 표로) ──
    def edge_shapes():
        grid = box['grid']
        item = column(grid, state['one'])
        edge, y = item['x'] + item['w'], item['y'] + item['h'] // 2
        pointer.check()
        pointer.move(middle(item))
        pointer.sleep(0.1)
        base = pointer.settled(lambda shape: True)
        marks, seen = [], []
        for offset in range(-7, 8):
            pointer.move((edge + offset, y))
            pointer.sleep(0.06)
            shape = pointer.settled(lambda shape: True)
            if shape not in seen:
                seen.append(shape)
            marks.append('{:+d}{}'.format(offset, '◆' if pointer.resizing(shape, base) else '·'))
        say('  칸 "{}"의 오른쪽 경계(x={}) 둘레 — ◆ 크기 조절 모양, · 평소 모양'.format(state['one'], edge))
        say('  ' + ' '.join(marks))
        say('  칸 제목 가운데에서의 모양 {} · 경계 둘레에서 본 모양 {} · 그 자리 맨 위 창 {}'.format(
            base, seen, '이 표' if pointer.window_at((edge - 2, y)) == grid['handle'] else '✗ 다른 창{}'.format(pointer.window_at((edge - 2, y)))))

    def grab_edge(name):
        grid = box['grid']
        item = column(grid, name)
        edge, y = item['x'] + item['w'], item['y'] + item['h'] // 2
        points = [(edge + offset, y) for offset in L.EDGE_OFFSETS if grid['x'] <= edge + offset < grid['x'] + grid['w']]
        return pointer.find_edge(middle(item), points, lambda hit: hit == grid['handle'])

    def resize():
        grid = box['grid']
        one, two = state['one'], state['two']
        before = dict(L.widths_of(grid))
        spot = column(grid, two)['x']
        point = grab_edge(one)
        if point is None:
            say('  ✗ 경계에서 크기 조절 모양을 확인하지 못해 누르지 않음 · ' + pointer.trace)
            return
        pointer.drag(point, (point[0] + 12, point[1]))
        pointer.sleep(0.3)
        now = refresh('칸 너비 +12 뒤')
        after = dict(L.widths_of(now))
        got = after.get(one, 0) - before[one]
        others = {name: after[name] - before[name] for name in after if name != one and name in before and after[name] != before[name]}
        say('  경계를 오른쪽으로 12 끎 → "{}" 너비 {} → {} ({:+d})'.format(one, before[one], after.get(one), got))
        say('  바로 뒤 칸 "{}" 위치 {:+d} · 다른 칸 너비 변화 {}'.format(two, column(now, two)['x'] - spot if column(now, two) else 0, others or '없음'))
        if got:
            point = grab_edge(one)
            if point is None:
                say('  ✗ 되돌리려는데 경계를 잡지 못함 · ' + pointer.trace)
                return
            pointer.drag(point, (point[0] - got, point[1]))
            pointer.sleep(0.3)
            now = refresh('칸 너비 되돌린 뒤')
        final = L.widths_of(now).get(one)
        say('  되돌린 뒤 너비 {} (처음 {}) → {}'.format(final, before[one], '원래대로' if final is not None and abs(final - before[one]) <= 1 else '✗ 처음과 다름'))

    def carry(name, target_name, side, down=0):
        """칸 제목 name을 끌어 target_name의 앞쪽(왼쪽 절반)·뒤쪽(오른쪽 절반)에 놓습니다. down>0이면 그만큼 아래(표 안쪽)에 놓습니다."""
        grid = box['grid']
        item, target = column(grid, name), column(grid, target_name)
        if item is None or target is None:
            raise RuntimeError('옮길 칸이 화면에 보이지 않습니다: {} → {}'.format(name, target_name))
        start = middle(item)
        y = start[1]
        end = (start[0], y + down) if down else (target['x'] + (target['w'] // 4 if side == '앞' else target['w'] * 3 // 4), y)
        if pointer.window_at(end) != grid['handle']:
            raise RuntimeError('놓을 자리({}, {})가 이 표가 아니라 누르지 않았습니다.'.format(end[0], end[1]))
        shapes = []
        held(start, grid['handle'], '칸 제목 ' + name)
        try:
            pointer.sleep(0.08)
            if down:
                pointer.move((start[0], y + 8))
                pointer.sleep(0.06)
                pointer.move((start[0], y + down // 2))
            else:
                pointer.move((start[0] + (6 if end[0] >= start[0] else -6), y))
                pointer.sleep(0.06)
                pointer.move(((start[0] + end[0]) // 2, y))
            pointer.sleep(0.15)
            shapes.append(pointer.shape())
            pointer.move(end)
            pointer.sleep(0.35)
            shapes.append(pointer.shape())
        finally:
            pointer.drop()
        pointer.sleep(0.4)
        return start, end, shapes

    def restore_order(wanted):
        for _ in range(len(wanted) + 2):
            current = order(box['grid'])
            if current == wanted:
                return True
            if sorted(current) != sorted(wanted):
                return False
            index = next(i for i, (now, want) in enumerate(zip(current, wanted)) if now != want)
            if column(box['grid'], wanted[index]) is None or column(box['grid'], current[index]) is None:
                return False    # 화면 밖 칸은 여기서 옮기지 않습니다.
            carry(wanted[index], current[index], '앞')
            refresh('순서 되돌리는 중')
        return order(box['grid']) == wanted

    def reorder():
        one, two = state['one'], state['two']
        before = order(box['grid'])
        i, j = before.index(one), before.index(two)
        expected = list(before)
        expected[i], expected[j] = expected[j], expected[i]
        start, end, shapes = carry(one, two, '뒤')
        after = order(refresh('칸 옮긴 뒤'))
        say('  "{}" 칸 제목(x={})을 끌어 "{}"의 오른쪽 절반(x={})에 놓음 · 끄는 동안 포인터 모양 {}'.format(one, start[0], two, end[0], shapes))
        if after == before:
            say('  ✗ 순서가 바뀌지 않음')
            return
        gone = [name for name in before if name not in after]
        if gone:
            say('  ✗ 칸이 사라짐: {} — MES를 다시 켜면 돌아옵니다.'.format(', '.join(gone)))
            return
        say('  → 그 자리 순서: {} → {} ({})'.format(' , '.join(before[max(0, i - 1):j + 2]), ' , '.join(after[max(0, i - 1):j + 2]),
                                              '두 칸이 자리를 바꿈' if after == expected else '예상과 다름'))
        carry(one, two, '앞')
        back = order(refresh('칸 되돌린 뒤'))
        if back == before:
            say('  "{}"을 다시 끌어 "{}"의 왼쪽 절반에 놓음 → 원래 순서로 돌아옴'.format(one, two))
        else:
            say('  ✗ 되돌린 뒤 순서가 처음과 다름 → 한 칸씩 되돌리는 중')
            say('  ' + ('원래 순서로 되돌림' if restore_order(before) else '✗ 되돌리지 못함. 지금 순서: ' + ', '.join(order(box['grid'])[:14])))

    def escape():
        # 놓으면 순서가 바뀌는 자리(오른쪽 칸의 오른쪽 절반)까지 끈 뒤 Esc → 놓음. 취소되면 순서가 그대로입니다.
        grid = box['grid']
        one, two = state['one'], state['two']
        before = order(grid)
        start = middle(column(grid, one))
        target = column(grid, two)
        end = (target['x'] + target['w'] * 3 // 4, start[1])
        held(start, grid['handle'], '칸 제목 ' + one)
        try:
            pointer.sleep(0.08)
            pointer.move((start[0] + 6, start[1]))
            pointer.sleep(0.06)
            pointer.move(end)
            pointer.sleep(0.3)
            pointer.key(0x1B)
            pointer.sleep(0.2)
            shape = pointer.shape()
        finally:
            pointer.drop()
        pointer.sleep(0.4)
        after = order(refresh('Esc 뒤'))
        state['escape'] = after == before
        say('  "{}" 칸 제목을 "{}"의 오른쪽 절반까지 끈 상태에서 Esc → 놓음 · Esc 뒤 포인터 모양 {}'.format(one, two, shape))
        if after == before:
            say('  → 순서 그대로(Esc로 끌기가 취소됨)')
        else:
            say('  ✗ 순서가 바뀜(Esc로 취소되지 않음): ' + ', '.join(after[:10]))
            say('  ' + ('원래 순서로 되돌림' if restore_order(before) else '✗ 되돌리지 못함'))

    def shifted_wheel(notches):
        pointer.key(0x10, up=False)
        try:
            pointer.sleep(0.05)
            pointer.wheel(notches)
            pointer.sleep(0.05)
        finally:
            pointer.key(0x10, down=False)

    def overflowing(grid):
        right = grid['x'] + grid['w']
        return (any(header[3] > 0 and header[1] >= right for header in grid['headers']) or bool(grid.get('scrolled'))
                or any(header[3] <= 0 for header in grid['headers']) or grid['columns'][-1]['x'] + grid['columns'][-1]['w'] > right)

    def scroll():
        grid = box['grid']
        one = state['one']
        right = grid['x'] + grid['w']
        outside = [header for header in grid['headers'] if header[3] > 0 and header[1] >= right]
        nowhere = [header for header in grid['headers'] if header[3] <= 0]
        say('  판독에 나온 칸 제목 {}개 · 표 안에서 시작하는 것 {}개 · 표 오른쪽 밖 {}개 · 위치가 없는 것 {}개'.format(
            len(grid['headers']), len(grid['columns']), len(outside), len(nowhere)))
        if not overflowing(grid):
            say('  가로로 넘치는 칸이 없어 가로 스크롤 시험은 건너뜀')
            return
        spot = middle(column(grid, one))
        for title, forward, backward in (('가로 휠 3칸', lambda: pointer.wheel(3, True), lambda: pointer.wheel(-3, True)),
                                         ('Shift+세로 휠 3칸', lambda: shifted_wheel(-3), lambda: shifted_wheel(3))):
            pointer.check()
            if pointer.window_at(spot) != grid['handle']:
                raise RuntimeError('표 위가 아니라 휠을 굴리지 않았습니다.')
            pointer.move(spot)
            pointer.sleep(0.12)
            start = place(box['grid'], one)
            forward()
            pointer.sleep(0.5)
            moved = place(refresh(title + ' 뒤'), one)
            if moved is None or start is None or moved == start:
                say('  {}: 표가 움직이지 않음'.format(title))
                continue
            say('  {}: 표가 가로로 {}픽셀 움직임'.format(title, start - moved))
            pointer.check()
            pointer.move(spot)
            pointer.sleep(0.12)
            backward()
            pointer.sleep(0.5)
            back = place(refresh(title + ' 되돌린 뒤'), one)
            say('    반대로 굴림 → {}'.format('원래 자리' if back == start else '✗ 처음과 {}픽셀 차이'.format((back or 0) - start)))
            state['scroll'] = (forward, backward, abs(start - moved))
            return

    def unscroll(target):
        """가로로 밀린 표를 휠로 되돌립니다(되는 방식이 확인된 경우)."""
        if not state['scroll']:
            return False
        forward, backward, _ = state['scroll']
        grid = box['grid']
        spot = (grid['x'] + 60, grid['columns'][0]['y'] + grid['columns'][0]['h'] // 2)
        for _ in range(8):
            now = place(box['grid'], state['one'])
            if now is None or now == target:
                break
            pointer.check()
            pointer.move(spot)
            pointer.sleep(0.12)
            (backward if now < target else forward)()
            pointer.sleep(0.5)
            refresh('가로 스크롤 되돌리는 중')
        return place(box['grid'], state['one']) == target

    def autoscroll():
        grid = box['grid']
        right = grid['x'] + grid['w']
        if not state['escape']:
            say('  Esc로 끌기 취소가 확인되지 않아 건너뜀')
            return
        if not overflowing(grid):
            say('  가로로 넘치는 칸이 없어 건너뜀')
            return
        before = order(grid)
        start_place = place(grid, state['one'])
        item = [one for one in grid['columns'] if whole(grid, one) and one['name']][-1]
        start = middle(item)
        held(start, grid['handle'], '칸 제목 ' + item['name'])
        try:
            pointer.sleep(0.08)
            pointer.move((start[0] + 6, start[1]))
            pointer.sleep(0.06)
            pointer.move((right - 5, start[1]))
            pointer.sleep(1.5)
            pointer.key(0x1B)
            pointer.sleep(0.2)
        finally:
            pointer.drop()
        pointer.sleep(0.4)
        now = refresh('끈 채 표 끝에 둔 뒤')
        moved = (start_place or 0) - (place(now, state['one']) or 0)
        say('  "{}" 칸 제목을 끈 채 표 오른쪽 끝에 1.5초 둔 뒤 Esc → 표가 가로로 {}픽셀 움직임{}'.format(
            item['name'], moved, '' if moved else ' (자동 스크롤 없음)'))
        if moved:
            say('  ' + ('휠로 원래 자리로 되돌림' if unscroll(start_place) else '✗ 표가 가로로 밀린 채입니다. 표 아래 가로 스크롤을 왼쪽 끝으로 옮겨 주세요.'))
        if order(box['grid']) != before:
            say('  ✗ 순서가 바뀜 → ' + ('원래 순서로 되돌림' if restore_order(before) else '되돌리지 못함'))

    def remove():
        name = env.options.get('remove', '')
        grid = box['grid']
        item = column(grid, name)
        if item is None or not whole(grid, item):
            say('  "{}" 칸이 지금 화면에 다 보이지 않아 건너뜀. 보이는 칸: {}'.format(name, ', '.join(names(grid)[:14])))
            return
        before = order(grid)
        start, end, shapes = carry(name, name, '앞', down=140)
        left = order(refresh('칸 없앤 뒤'))
        say('  "{}" 칸 제목을 아래(표 안쪽)로 140 끌어다 놓음 · 끄는 동안 포인터 모양 {}'.format(name, shapes))
        if name not in left:
            state['removed'] = name
            rest = [one for one in before if one != name]
            say('  → 칸이 없어짐 · 나머지 순서 {}'.format('그대로' if left == rest else '달라짐: ' + ', '.join(left[:12])))
            say('    (없앤 칸은 MES를 다시 켜면 돌아옵니다.)')
        else:
            say('  ✗ 칸이 그대로 있음(이 방법으로는 없어지지 않음) · 순서 {}'.format('그대로' if left == before else '달라짐'))
            if left != before:
                say('  ' + ('원래 순서로 되돌림' if restore_order(before) else '✗ 되돌리지 못함'))

    def show_table():
        grid = box['grid']
        reading = [header[0] for header in grid['headers']]
        say('  표 ({}, {}) {}x{} · 창{} · 칸 제목 {}개(표 안 {}개) · 판독 순서와 화면 순서 {}'.format(
            grid['x'], grid['y'], grid['w'], grid['h'], grid['handle'], len(grid['headers']), len(grid['columns']),
            '같음' if reading == order(grid) else '다름'))
        say('  칸 이름과 너비(왼쪽부터, ▷ 표 오른쪽 밖):')
        out.extend(listing(grid))

    def column_tests(full):
        """box['grid']의 표에서 칸 시험. full이면 순서·스크롤·없애기까지."""
        state['one'], state['two'] = pick()
        grid = box['grid']
        original, widths = order(grid), dict(L.widths_of(grid))
        say('  시험에 쓰는 칸: "{}" 과 그 오른쪽 "{}"'.format(state['one'], state['two']))
        attempt('  칸 경계에서의 포인터 모양 (누르지 않음)', edge_shapes)
        attempt('  칸 너비 끌기', resize)
        if full:
            attempt('  칸 제목을 끌어 순서 바꾸기', reorder)
            attempt('  Esc로 끌기 취소', escape)
            attempt('  표 가로 스크롤', scroll)
            attempt('  칸 제목을 끈 채 표 끝에 두기(자동 스크롤)', autoscroll)
            if env.options.get('remove'):
                attempt('  칸 없애기', remove)

        def final():
            now = refresh('마지막 확인')
            wanted = [name for name in original if name != state['removed']]
            say('  칸 순서: ' + ('처음과 같음' if order(now) == wanted else '✗ 처음과 다름 → ' + ', '.join(order(now)[:14])))
            after = L.widths_of(now)
            changed = {name: (widths[name], after[name]) for name in after if name in widths and abs(after[name] - widths[name]) > 1}
            say('  칸 너비: ' + ('처음과 같음' if not changed else '✗ 다름(처음, 지금) {}'.format(changed)))
        attempt('  이 표 끝난 뒤 확인', final)

    def work_tab():
        found = tables(select_tab(WORK_TAB))
        if not found:
            raise RuntimeError('작업지시관리 탭에서 표를 찾지 못했습니다.')
        box['grid'] = max(found, key=lambda grid: len(grid['headers']))
        show_table()
        if not env.options.get('list_only'):
            column_tests(True)

    def daily_tab():
        rows = L.arrange(L.front(L.grids(select_tab(DAILY_TAB)), pointer))
        if not rows:
            raise RuntimeError('생산일보관리 탭에서 생산일보 표를 찾지 못했습니다.')
        say('  판 {}개 · 표 너비 {}'.format(sum(len(row) for row in rows), ' / '.join(' '.join(str(grid['w']) for grid in row) for row in rows)))
        for row in rows:
            for grid in row:
                say('    ' + ' '.join('{}{}'.format(item['name'], item['w']) for item in grid['columns']))
        if not env.options.get('list_only'):
            box['grid'] = rows[0][0]
            column_tests(False)

    def tool_and_back():
        open_from_menu(TOOL_GROUP, TOOL_ITEM)
        report = read('설비별공구관리를 누른 뒤', False)
        shown = front_tab(report, TOOL_ITEM)
        say('  → ' + ('설비별공구관리 문서가 앞에 옴' if shown else '✗ 설비별공구관리 탭이 앞에 보이지 않음'))
        open_from_menu(WORK_GROUP, WORK_ITEM)
        report = read('작업지시관리로 돌아온 뒤', False)
        say('  → ' + ('작업지시관리 문서가 다시 앞에 옴' if front_tab(report, WORK_TAB) else '✗ 작업지시관리 탭이 앞에 보이지 않음'))

    def put_back():
        if selected_at_start and state['doc']:
            select_tab(selected_at_start)
        if menu_item is not None and menu_width is not None and abs(menu_size() - menu_width) > 2:
            pull_menu(menu_width - menu_size())
            say('  메뉴 칸 너비를 처음({})으로 되돌림 → {}'.format(menu_width, menu_size()))

    try:
        if menu_item is not None:
            menu_width = menu_size()
        already = front_tab(first, WORK_TAB)
        if env.options.get('list_only') and already:      # 목록만 읽을 때는, 문서가 이미 앞에 있으면 메뉴를 건드리지 않습니다.
            state['doc'] = already[0].get('handle')
            ready = True
        else:
            ready = attempt('메뉴 칸 넓히기', widen_menu) and attempt('메뉴로 작업지시관리 앞에 띄우기', bring_work)
        if ready:
            attempt('작업지시관리 탭의 표', work_tab)
            attempt('생산일보관리 탭의 표', daily_tab)
            if env.options.get('tool') and not env.options.get('list_only'):
                attempt('메뉴로 설비별공구관리 열고 작업지시관리로 돌아오기', tool_and_back)
        attempt('처음 상태로 되돌리기', put_back)
    except L.Stopped:
        say('')
        say('F9로 중지했습니다. 여기까지의 결과입니다.')
    finally:
        if pointer.holding:
            pointer.drop()
        pointer.restore()
    say('')
    say('판독 시간(초): ' + ' · '.join('{} {}회 평균 {:.1f}'.format(kind, len(values), sum(values) / len(values))
                                   for kind, values in sorted(state['times'].items())))
    say('누른 횟수 {}회'.format(pointer.presses))
    return out


# --- Windows 실행부 -----------------------------------------------------------
def make_reader(P, wide):
    scope = {'queue': queue, 'time': time, 'os': os, 'Path': Path}
    exec(compile(WASH_READER_SOURCE, 'wash_reader.py', 'exec'), scope)
    powershell = P.POWERSHELL
    if wide and powershell.count(NARROW_BOUNDS) == 1:
        powershell = powershell.replace(NARROW_BOUNDS, WIDE_BOUNDS)
    return scope['WashReader'](SimpleNamespace(POWERSHELL=powershell, base64=P.base64, check_capture=P.check_capture))


def bring_forward(api):
    """MES를 최대화해 맨 앞으로(세척완료와 같은 준비)."""
    from ctypes import wintypes
    import ctypes
    u, root = api.u, api.target['handle']
    u.IsZoomed.argtypes = [wintypes.HWND]
    u.IsZoomed.restype = wintypes.BOOL
    u.ShowWindowAsync.argtypes = [wintypes.HWND, ctypes.c_int]
    u.ShowWindowAsync.restype = wintypes.BOOL
    api.activate()
    if not u.IsZoomed(root):
        u.ShowWindowAsync(root, 3)
        for _ in range(40):
            if u.IsZoomed(root):
                break
            time.sleep(0.1)
        time.sleep(0.5)
        api.activate()
    time.sleep(0.4)


def run_probe(options, log):
    P = load(WASH_POP_SOURCE, 'probe_wash_pop')
    M = load(WASH_MES_SOURCE, 'probe_wash_mes')
    L = load(MES_LAYOUT_SOURCE, 'probe_mes_layout')
    windows = [w for w in P.visible_windows() if w['title'] == 'ROOT MES']
    if len(windows) != 1:
        raise RuntimeError("'ROOT MES' 창을 하나만 켜 주세요. 지금 {}개입니다.".format(len(windows)))
    target = windows[0]
    api = M.WindowsClicks(target)
    stop = threading.Event()
    readers = {}

    def read(label, wide=False, root=None):
        log(label + ' 읽는 중…')
        if wide not in readers:
            readers[wide] = make_reader(P, wide)
        return readers[wide].capture({**target, 'handle': root or target['handle'], 'mode': 'mes_rows'}, label, stop)

    try:
        bring_forward(api)
        pointer = L.Pointer(api)
        return experiments(SimpleNamespace(L=L, pointer=pointer, read=read, log=log, options=options, clock=time.monotonic))
    finally:
        for reader in readers.values():
            try:
                reader.close()
            except Exception:
                pass


def main():
    import tkinter as tk
    from tkinter import ttk
    root = tk.Tk()
    root.title('MES 조작 점검')
    root.geometry('840x680')
    body = ttk.Frame(root, padding=16)
    body.pack(fill='both', expand=True)
    ttk.Label(body, text='MES 조작 점검 (2판)', font=('맑은 고딕', 15, 'bold')).pack(anchor='w')
    ttk.Label(body, justify='left', wraplength=800, text=(
        '지후니우스 MES 정렬이 쓰려는 조작을 실제 MES에서 작게 해 보고 되돌린 뒤, 결과를 글로 정리합니다.\n'
        '1) MES만 켜 두면 됩니다. 칸을 고치는 중이면 끝내고 시작해 주세요.\n'
        '2) [점검 시작]을 누르면 MES가 앞으로 나오고 마우스가 저절로 움직입니다. 2~3분 동안 마우스·키보드를 건드리지 말아 주세요. 멈추려면 F9.\n'
        '3) 하는 일: 왼쪽 메뉴로 작업지시관리를 띄움 → 작업지시관리 탭 표에서 칸 너비·순서를 바꿨다 되돌림, 가로 스크롤 → '
        '생산일보관리 탭에서 칸 너비를 바꿨다 되돌림 → 설비별공구관리를 열고 돌아옴. 행·값·저장은 건드리지 않습니다.\n'
        '4) 끝나면 결과 글이 복사되고 이 파일 옆에 저장됩니다. 그 글을 그대로 보내 주세요(칸 제목·메뉴 이름과 숫자만 들어갑니다).')).pack(anchor='w', pady=(8, 10))
    options = ttk.Frame(body)
    options.pack(fill='x')
    ttk.Label(options, text='없애 볼 칸 이름(작업지시관리 표에서 평소 없애는 칸 하나, 비우면 안 함):').pack(side='left')
    remove = tk.StringVar(value='')
    ttk.Entry(options, textvariable=remove, width=16).pack(side='left', padx=6)
    tool = tk.BooleanVar(value=True)
    ttk.Checkbutton(body, text='메뉴에서 설비관리 → 설비별공구관리를 열어 보고 작업지시관리로 돌아오기', variable=tool).pack(anchor='w', pady=(6, 0))
    list_only = tk.BooleanVar(value=False)
    ttk.Checkbutton(body, text='조작 시험 없이 칸 목록만 읽기 (작업지시관리 표를 손으로 다 정리한 뒤, 그 순서·너비를 알려 줄 때)', variable=list_only).pack(anchor='w')
    bar = ttk.Frame(body)
    bar.pack(fill='x', pady=10)
    status = tk.StringVar(value='준비됨')
    start = ttk.Button(bar, text='점검 시작')
    start.pack(side='left')
    copy = ttk.Button(bar, text='결과 복사', state='disabled')
    copy.pack(side='left', padx=8)
    ttk.Label(bar, textvariable=status).pack(side='left', padx=8)
    output = tk.Text(body, wrap='word', font=('맑은 고딕', 10))
    output.pack(fill='both', expand=True)
    events = queue.Queue()
    result = {'text': ''}

    def put_clipboard():
        root.clipboard_clear()
        root.clipboard_append(result['text'])
        status.set('결과를 복사했습니다. 그대로 붙여넣어 보내 주세요.')
    copy.configure(command=put_clipboard)

    def work(chosen):
        try:
            if os.name != 'nt':
                raise RuntimeError('MES가 실행 중인 Windows PC에서 실행해 주세요.')
            lines = run_probe(chosen, lambda text: events.put(('log', text)))
        except Exception as failure:
            lines = ['MES 조작 점검 결과 · 점검 {} · 지후니우스 {}'.format(PROBE_VERSION, APP_VERSION),
                     '점검을 끝내지 못했습니다 — ' + explain(failure), '', traceback.format_exc()[-1800:]]
        events.put(('done', '\n'.join(lines)))

    def begin():
        start.configure(state='disabled')
        copy.configure(state='disabled')
        output.delete('1.0', 'end')
        status.set('점검 중… 마우스·키보드를 건드리지 말아 주세요. (멈추려면 F9)')
        chosen = {'remove': remove.get().strip(), 'tool': tool.get(), 'list_only': list_only.get()}
        threading.Thread(target=work, args=(chosen,), daemon=True).start()
    start.configure(command=begin)

    def poll():
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == 'log':
                    status.set(value)
                else:
                    result['text'] = value
                    output.insert('1.0', value)
                    name = 'MES조작점검결과_{}.txt'.format(datetime.now().strftime('%Y%m%d-%H%M%S'))
                    saved = ''
                    for folder in (Path(sys.argv[0]).resolve().parent, Path.home() / 'Desktop', Path.home()):
                        try:
                            (folder / name).write_text(value, encoding='utf-8')
                            saved = str(folder / name)
                            break
                        except OSError:
                            continue
                    try:
                        put_clipboard()
                    except tk.TclError:
                        pass
                    status.set('끝났습니다. 결과를 복사했습니다' + (' · 저장: ' + saved if saved else '') + ' — 이 글을 보내 주세요.')
                    start.configure(state='normal')
                    copy.configure(state='normal')
                    root.deiconify()
                    root.lift()
                    root.attributes('-topmost', True)
                    root.after(400, lambda: root.attributes('-topmost', False))
        except queue.Empty:
            pass
        root.after(150, poll)
    poll()
    root.mainloop()


if __name__ == '__main__':
    main()
