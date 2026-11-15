"""MES 조작 점검 (4판).

지후니우스 'MES 정렬'이 작업지시관리 표에서 쓰려는 조작이 실제 MES에서 어떻게 먹히는지, 작게 해 보고 결과를 글로 정리합니다.
제품과 똑같은 함수(src/host/mes_layout.py의 discard·carry·chain·reach…)를 그대로 씁니다.
  1) 작업지시관리 표를 읽어 칸 제목의 위치를 적음(고정 칸 뒤의 틈, 칸 제목 줄 위의 그룹화 칸, 화면 밖 칸 이름)
  2) 평소 없애는 칸 하나의 제목을 잡아 표 위쪽 바깥으로 올려 보며 포인터 모양만 봄 → 제자리로 돌아와 Esc로 취소
  3) 그 칸을 위로 끌어다 버림(제품이 쓰는 순서: 위로 → 위로 끝까지 → 아래로) → 없어졌는지 다시 읽어 확인
  4) 고정 칸 뒤쪽의 칸 하나를 멀리 왼쪽으로 옮겼다가 제자리로 되돌림
작업지시관리가 이미 앞에 떠 있으면 메뉴는 건드리지 않습니다. 생산일보관리·설비별공구관리는 이미 현장에서 확인돼 다루지 않습니다.
누르기 전에는 항상 그 자리의 맨 위 창이 누르려는 표·메뉴·탭인지 확인하고, 아니면 누르지 않습니다. 칸 제목 줄 위의
'그룹화 할 열 머리글을 여기로 끌어옵니다' 칸에는 멈추지도 놓지도 않습니다.
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

PROBE_VERSION = '4'
APP_VERSION = ...  # build: 지후니우스 버전
WASH_POP_SOURCE = ...  # build: src/host/wash_pop.py
WASH_MES_SOURCE = ...  # build: src/host/wash_mes.py
WASH_READER_SOURCE = ...  # build: src/host/jihunius_main.py 의 WashReader 와 mes_layout_reader
MES_LAYOUT_SOURCE = ...  # build: src/host/mes_layout.py

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
    state = {'doc': None, 'menu': None, 'times': {}, 'removed': None, 'target': None, 'sound': True}
    box = {'grid': None, 'handle': None}
    keep = set(L.DEFAULT_WORK_KEEP)

    def section(title):
        say('')
        say('■ ' + title)
        log(title.strip() + '…')

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
                L._release(pointer, False)       # 끌던 중이었다면 Esc로 취소하고 놓습니다.

    def read(label, wide=False, root=None, kind='전체'):
        started = env.clock()
        report = env.read(label, wide, root)
        state['times'].setdefault(kind, []).append(env.clock() - started)
        return report

    # ── 누르기: 그 자리의 맨 위 창을 먼저 확인합니다 ──
    def held(point, grid, what):
        if not L.spot(pointer, grid, point, 1.0):
            raise RuntimeError('{}: 그 자리({}, {})가 이 표가 아니라 누르지 않았습니다.'.format(what, point[0], point[1]))
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

    def order(grid):
        """표의 모든 칸 이름을 왼쪽부터. 위치가 없는 칸(화면 밖)은 판독 순서대로 뒤에 둡니다."""
        placed = sorted((header for header in grid['headers'] if header[3] > 0), key=lambda header: header[1])
        return [header[0] for header in placed] + [header[0] for header in grid['headers'] if header[3] <= 0]

    def look(label):
        """제품(MES 정렬)과 같은 방식: 포인터를 표 모서리로 치우고, 표 창 아래만 읽습니다."""
        L.park(pointer, box['grid'])
        found = L.grids(read(label, False, box['handle'], '표만'), required=())
        shown = [grid for grid in L.front(found, pointer) if grid['handle'] == box['handle']]
        if not shown:
            pointer.sleep(0.5)
            shown = [grid for grid in L.front(found, pointer) if grid['handle'] == box['handle']]
        if not shown:
            raise RuntimeError('시험하던 표가 화면 앞에서 사라졌습니다.')
        shown[0]['reach'] = L.reach(pointer, shown[0])
        box['grid'] = shown[0]
        return shown[0]

    def ready(grid, name=None):
        """끌 수 있는 칸: 그 자리에 실제로 보이고, 온전히 들어 있고, 잡는 자리가 이 표인 것."""
        return [column for column in L.chain(grid) if column['name'] and L.whole(grid, column)
                and (name is None or column['name'] == name) and L.grabbable(pointer, grid, column)]

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
    log('처음 화면…')
    first = read('처음 화면', True)
    native = L.native_parents(first)
    tree = L.nav_tree(first)
    selected_at_start = next((str(item.get('name', '')).strip() for item in L.elements(first)
                              if item.get('role') == 37 and item.get('selected') and str(item.get('name', '')).strip() in (WORK_TAB, DAILY_TAB, '작업지시조회')), None)
    menu_item = L.menu_divider_beside(native, pointer, tree[0]['handle']) if tree else None
    menu_width = None
    if tree:
        state['menu'] = tree[0]['handle']

    def menu_size():
        left, _, right, _ = pointer.rect(menu_item['first'])
        return right - left

    def pull_menu(amount):
        if not L.drag_divider(pointer, menu_item, amount, lambda kind, value: None):
            raise RuntimeError('메뉴 칸 경계에서 크기 조절 모양을 확인하지 못해 누르지 않았습니다 · ' + pointer.trace)
        L.settle(pointer, menu_item)
        pointer.sleep(0.3)

    # ── 1. (작업지시관리가 앞에 없을 때만) 메뉴로 앞에 띄우기 ──
    def bring_work():
        if not tree or menu_item is None:
            raise RuntimeError('왼쪽 메뉴를 읽지 못했습니다. MES에서 작업지시관리 화면을 직접 띄운 뒤 다시 실행해 주세요.')
        width = menu_size()
        say('  메뉴 칸 너비 {}'.format(width))
        if width < MENU_WORKING_WIDTH - 20:
            pull_menu(MENU_WORKING_WIDTH - width)
            say('  경계를 오른쪽으로 끌어 넓힘 → 너비 {}'.format(menu_size()))
        open_from_menu(WORK_GROUP, WORK_ITEM)
        found = front_tab(read('작업지시관리를 누른 뒤', False), WORK_TAB)
        if found is None:
            raise RuntimeError('메뉴에서 작업지시관리를 눌렀지만, 그 문서의 탭이 앞에 보이지 않습니다.')
        state['doc'] = found[0].get('handle')
        say('  → 작업지시관리 문서가 앞에 옴')

    # ── 2. 작업지시관리 표 ──
    def spots(columns, per=6):
        text = ['{}@{}+{}'.format(column['name'], column['x'], column['w']) for column in columns]
        return ['    ' + ' | '.join(text[start:start + per]) for start in range(0, len(text), per)]

    def show_table():
        grid = box['grid']
        columns = grid['columns']
        head = columns[0]
        say('  표 ({}, {}) {}x{} · 칸 제목 {}개 · 그중 위치 있는 것 {}개 · 닿는 오른쪽 끝 {}'.format(
            grid['x'], grid['y'], grid['w'], grid['h'], len(grid['headers']), len(columns), grid.get('reach')))
        say('  칸 제목 줄: y={} 높이 {} (표 위쪽 끝에서 {} 아래) · 첫 칸은 표 왼쪽 끝에서 {} 오른쪽'.format(
            head['y'], head['h'], head['y'] - grid['y'], min(column['x'] for column in columns) - grid['x']))
        say('  위치 있는 칸(이름@x+너비, 왼쪽부터):')
        out.extend(spots(columns))
        ordered = sorted(columns, key=lambda column: column['x'])
        gaps = ['{}|{} {:+d}'.format(one['name'], two['name'], two['x'] - one['x'] - one['w'])
                for one, two in zip(ordered, ordered[1:]) if two['x'] != one['x'] + one['w']]
        hidden = L.covered(grid)
        say('  칸 사이 틈·겹침: {} · 겹쳐 읽힌 칸 {} · 표 왼쪽 밖에 걸친 칸 {} → 가로로 밀린 흔적 {}'.format(
            ', '.join(gaps) or '없음', ', '.join(column['name'] for column in hidden) or '없음',
            '있음' if grid.get('scrolled') else '없음', '없음' if L.tidy(grid) else '있음'))
        nowhere = [header[0] for header in grid['headers'] if header[3] <= 0]
        say('  위치 없는 칸(화면 밖) {}개: {}'.format(len(nowhere), ', '.join(nowhere) or '없음'))
        shown = [column['name'] for column in L.chain(grid) if column['name'] and column['name'] not in keep]
        beyond = [name for name in nowhere if name and name not in keep]
        say('  기준(남길 칸 {}개)에 없는 칸 — 보이는 것: {} · 화면 밖 것: {}'.format(len(keep), ', '.join(shown) or '없음', ', '.join(beyond) or '없음'))
        missing = [name for name in L.DEFAULT_WORK_KEEP if name not in [header[0] for header in grid['headers']]]
        if missing:
            say('  기준에는 있는데 이 표에 없는 칸: ' + ', '.join(missing))

    def choose():
        """버려 볼 칸: 적어 준 이름, 없으면 기준에 없는 보이는 칸 가운데 가장 오른쪽."""
        grid = box['grid']
        wanted = env.options.get('remove', '')
        if wanted:
            found = ready(grid, wanted)
            if not found:
                say('  "{}" 칸이 지금 화면에 다 보이지 않아 건너뜀'.format(wanted))
            return found[0]['name'] if found else None
        extras = [column for column in ready(grid) if column['name'] not in keep]
        if not extras:
            say('  기준에 없는 칸(평소 없애는 칸)이 화면에 보이지 않아 건너뜀')
        return extras[-1]['name'] if extras else None

    def lift():
        # 칸 제목을 잡고 표 위쪽 바깥으로 올려 보며 포인터 모양만 봅니다. 놓지 않고, 제자리로 돌아와 Esc로 취소합니다.
        state['target'] = choose()
        if state['target'] is None:
            return
        grid = box['grid']
        column = ready(grid, state['target'])[0]
        start = L.grip(column)
        points = L.discard_points(pointer, grid, start, '위로')
        if not points:
            say('  ✗ 표 위쪽 바깥에 올릴 자리가 없음(표 위쪽 끝 y={})'.format(grid['y']))
            return
        before = order(grid)
        seen = []
        held(start, grid, '칸 제목 ' + column['name'])
        try:
            pointer.sleep(0.08)
            pointer.move((start[0] + 6, start[1]))
            pointer.sleep(0.1)
            base = pointer.shape()
            for point in points:
                pointer.move(point)
                pointer.sleep(0.2)
                seen.append((grid['y'] - point[1], pointer.shape()))
            pointer.move((start[0] + 6, start[1]))       # 칸 제목 줄의 제자리로 돌아옴
            pointer.sleep(0.15)
            back = pointer.shape()
        finally:
            L._release(pointer, False)                   # Esc로 끌기를 취소한 뒤 놓음
        pointer.sleep(0.4)
        after = order(look('올려 본 뒤'))
        say('  "{}" 칸 제목 ({}, {})을 잡고 끌기 시작 · 그때 포인터 모양 {}'.format(column['name'], start[0], start[1], base))
        say('  ' + ' · '.join('표 위 {}픽셀: {}{}'.format(distance, shape, '(바뀜)' if shape != base else '') for distance, shape in seen))
        say('  칸 제목 줄로 돌아왔을 때 모양 {} → Esc → 놓음'.format(back))
        state['sound'] = after == before
        say('  → 칸 순서·개수 그대로' if after == before else '  ✗ 칸이 달라짐: ' + ', '.join(after[:16]))

    def throw():
        # 제품(MES 정렬)이 쓰는 동작 그대로: 위로(모양이 바뀌면 놓음) → 위로 끝까지 → 아래로.
        name = state['target']
        if name is None:
            say('  버려 볼 칸이 없어 건너뜀')
            return
        if not state['sound']:
            say('  앞 시험에서 칸이 달라져 건너뜀')
            return
        before, count = order(box['grid']), len(box['grid']['headers'])
        ended = False
        for way in L.DISCARD_WAYS:
            grid = box['grid']
            found = ready(grid, name)
            if not found:
                say('  "{}" 칸이 화면에 다 보이지 않아 그만둠'.format(name))
                return
            if way == '위로 끝까지' and ended:
                continue
            pointer.check()
            seen, ended = L.discard(pointer, grid, found[0], way)
            now = look('칸 버린 뒤')
            gone = name not in [header[0] for header in now['headers']]
            say('  "{}" · {} → {}'.format(name, seen or way + ' · 놓을 자리 없음',
                                        '칸이 없어짐 (칸 제목 {} → {}개)'.format(count, len(now['headers'])) if gone else '그대로 있음'))
            if gone:
                state['removed'] = name
                rest = [one for one in before if one != name]
                say('  나머지 칸 순서: ' + ('그대로' if order(now) == rest else '✗ 달라짐 → ' + ', '.join(order(now)[:16])))
                say('  (평소 없애는 칸입니다. MES를 다시 켜면 돌아옵니다.)')
                return
            if order(now) != before:
                state['sound'] = False
                say('  ✗ 칸 순서가 달라져 더 하지 않음: ' + ', '.join(order(now)[:16]))
                return
        say('  ✗ 어느 방법으로도 없어지지 않음')

    def far():
        # 고정 칸 뒤쪽(첫 틈 뒤)의 칸 하나를 멀리 왼쪽으로 옮겼다가 제자리로 되돌립니다.
        if not state['sound']:
            say('  앞 시험에서 칸이 달라져 건너뜀')
            return
        grid = box['grid']
        visible = ready(grid)
        cut = next((index + 1 for index, (one, two) in enumerate(zip(visible, visible[1:]))
                    if two['x'] - (one['x'] + one['w']) >= 2), 0)
        loose = visible[cut:]
        pair = next(((loose[index], loose[index + 1]) for index in range(len(loose) - 2, 3, -1) if loose[index]['w'] >= 60), None)
        if pair is None:
            say('  옮겨 볼 칸이 모자라 건너뜀(고정 칸 뒤에 다 보이는 칸 {}개)'.format(len(loose)))
            return
        source, neighbour = pair
        target = loose[1]
        before = order(grid)
        end = (target['x'] + max(3, target['w'] // 4), target['y'] + target['h'] // 2)
        pointer.check()
        if not L.carry(pointer, grid, source, end):
            say('  ✗ 잡을 자리나 놓을 자리가 이 표가 아니라 누르지 않음')
            return
        after = order(look('칸 옮긴 뒤'))
        say('  "{}"(x={})을 끌어 "{}"(x={})의 왼쪽 1/4에 놓음 · {}픽셀 왼쪽으로'.format(
            source['name'], source['x'], target['name'], target['x'], L.grip(source)[0] - end[0]))
        if after == before:
            say('  ✗ 순서가 그대로임(옮겨지지 않음)')
            return
        moved = sorted(after) == sorted(before) and after.index(source['name']) == after.index(target['name']) - 1
        say('  → ' + ('"{}" 바로 앞으로 옮겨짐'.format(target['name']) if moved else '✗ 예상과 다름: ' + ', '.join(after[:16])))
        grid = box['grid']
        again, home = ready(grid, source['name']), ready(grid, neighbour['name'])
        if not again or not home:
            state['sound'] = False
            say('  ✗ 되돌릴 칸이 화면에 다 보이지 않아 되돌리지 못함')
            return
        end = (home[0]['x'] + max(3, home[0]['w'] // 4), home[0]['y'] + home[0]['h'] // 2)
        pointer.check()
        L.carry(pointer, grid, again[0], end)
        back = order(look('칸 되돌린 뒤'))
        state['sound'] = back == before
        say('  되돌리기: "{}"을 "{}"의 왼쪽 1/4에 놓음 → {}'.format(
            source['name'], neighbour['name'], '원래 순서로 돌아옴' if back == before else '✗ 처음과 다름: ' + ', '.join(back[:16])))

    def work_tab():
        found = tables(select_tab(WORK_TAB))
        if not found:
            raise RuntimeError('작업지시관리 탭에서 표를 찾지 못했습니다.')
        box['handle'] = max(found, key=lambda grid: len(grid['headers']))['handle']
        grid = look('작업지시관리 표')
        original, widths = order(grid), dict(L.widths_of(grid))
        show_table()
        if env.options.get('list_only'):
            return
        if not L.tidy(grid):
            say('  ✗ 표가 가로로 밀려 있는 것으로 읽혀 조작 시험은 하지 않습니다. 표 아래 가로 스크롤을 왼쪽 끝으로 옮긴 뒤 다시 실행해 주세요.')
            return
        attempt('  칸 제목을 위로 끌어 올릴 때의 포인터 모양 (놓지 않고 Esc로 취소)', lift)
        attempt('  칸 버리기 (평소 없애는 칸 하나)', throw)
        attempt('  먼 칸 옮기기 (옮겼다가 되돌림)', far)

        def final():
            now = look('마지막 확인')
            wanted = [name for name in original if name != state['removed']]
            say('  칸 순서: ' + ('처음과 같음' + (' (버린 칸 "{}" 제외)'.format(state['removed']) if state['removed'] else '')
                              if order(now) == wanted else '✗ 처음과 다름 → ' + ', '.join(order(now)[:16])))
            after = L.widths_of(now)
            changed = {name: (widths[name], after[name]) for name in after if name in widths and abs(after[name] - widths[name]) > 1}
            say('  칸 너비: ' + ('처음과 같음' if not changed else '✗ 다름(처음, 지금) {}'.format(changed)))
            say('  가로로 밀린 흔적: ' + ('없음' if L.tidy(now) else '✗ 있음'))
        attempt('  끝난 뒤 확인', final)

    def put_back():
        if selected_at_start and selected_at_start != WORK_TAB and state['doc']:
            select_tab(selected_at_start)
        if menu_item is not None and menu_width is not None and abs(menu_size() - menu_width) > 2:
            pull_menu(menu_width - menu_size())
            say('  메뉴 칸 너비를 처음({})으로 되돌림 → {}'.format(menu_width, menu_size()))
        else:
            say('  바꾼 것 없음' if not state['removed'] else '  버린 칸 "{}": 그대로 둠(평소 없애는 칸)'.format(state['removed']))

    try:
        if menu_item is not None:
            menu_width = menu_size()
        already = front_tab(first, WORK_TAB)
        if already:                                      # 작업지시관리가 이미 앞에 있으면 메뉴는 건드리지 않습니다.
            state['doc'] = already[0].get('handle')
            ready_to_go = True
        else:
            ready_to_go = attempt('메뉴로 작업지시관리 앞에 띄우기', bring_work)
        if ready_to_go:
            attempt('작업지시관리 탭의 표', work_tab)
        attempt('처음 상태로 되돌리기', put_back)
    except L.Stopped:
        say('')
        say('F9로 중지했습니다. 여기까지의 결과입니다.')
    finally:
        if pointer.holding:
            L._release(pointer, False)
        pointer.restore()
    say('')
    say('판독 시간(초): ' + ' · '.join('{} {}회 평균 {:.1f}'.format(kind, len(values), sum(values) / len(values))
                                   for kind, values in sorted(state['times'].items())))
    say('누른 횟수 {}회'.format(pointer.presses))
    return out


# --- Windows 실행부 -----------------------------------------------------------
def make_reader(P):
    """MES 정렬과 똑같은 판독기: 모든 종류 항목의 위치를 읽고, 표의 행(데이터 패널 아래)은 읽지 않습니다."""
    scope = {'queue': queue, 'time': time, 'os': os, 'Path': Path}
    exec(compile(WASH_READER_SOURCE, 'wash_reader.py', 'exec'), scope)
    return scope['mes_layout_reader'](P)


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
        if 'one' not in readers:
            readers['one'] = make_reader(P)
        return readers['one'].capture({**target, 'handle': root or target['handle'], 'mode': 'mes_rows'}, label, stop)

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
    ttk.Label(body, text='MES 조작 점검 ({}판)'.format(PROBE_VERSION), font=('맑은 고딕', 15, 'bold')).pack(anchor='w')
    ttk.Label(body, justify='left', wraplength=800, text=(
        "지후니우스 MES 정렬이 '작업지시관리' 표에서 쓰려는 조작을 실제 MES에서 작게 해 보고, 결과를 글로 정리합니다.\n"
        '1) MES를 새로 켜고 작업지시관리 화면을 띄워 둔 상태에서 실행해 주세요(표는 손대지 않은 처음 그대로).\n'
        '2) [점검 시작]을 누르면 MES가 앞으로 나오고 마우스가 저절로 움직입니다. 1분쯤 마우스·키보드를 건드리지 말아 주세요. 멈추려면 F9.\n'
        '3) 하는 일: ① 표의 칸 제목 위치를 읽음 ② 평소 없애는 칸 하나의 제목을 표 위로 올려 보며 포인터 모양만 보고 취소 '
        '③ 그 칸을 위로 끌어다 버림 ④ 칸 하나를 멀리 옮겼다가 되돌림. 행·값·저장은 건드리지 않습니다.\n'
        '   끝나면 평소 없애는 칸 하나가 없어진 상태로 남습니다(MES를 다시 켜면 돌아옵니다).\n'
        '4) 끝나면 결과 글이 복사되고 이 파일 옆에 저장됩니다. 그 글을 그대로 보내 주세요(칸 제목·메뉴 이름과 숫자만 들어갑니다).')).pack(anchor='w', pady=(8, 10))
    options = ttk.Frame(body)
    options.pack(fill='x')
    ttk.Label(options, text='버려 볼 칸 이름(비워 두면 평소 없애는 칸 가운데 하나를 알아서 고름):').pack(side='left')
    remove = tk.StringVar(value='')
    ttk.Entry(options, textvariable=remove, width=16).pack(side='left', padx=6)
    list_only = tk.BooleanVar(value=False)
    ttk.Checkbutton(body, text='조작 시험 없이 칸 목록만 읽기', variable=list_only).pack(anchor='w', pady=(6, 0))
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
        chosen = {'remove': remove.get().strip(), 'list_only': list_only.get()}
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
