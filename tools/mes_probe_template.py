"""MES 조작 점검.

지후니우스 'MES 정렬'이 쓰려는 조작이 실제 MES에서 어떻게 먹히는지, 작게 해 보고 되돌린 뒤 결과를 글로 정리합니다.
  · 경계선에 마우스를 올렸을 때의 포인터 모양
  · 칸 너비 끌기, 판 사이 경계와 왼쪽 메뉴 칸 경계 끌기 (끌었다가 되돌림)
  · 칸 제목을 끌어 순서 바꾸기 (바꿨다가 되돌림), Esc로 끌기 취소
  · 표 가로 스크롤, 칸을 끈 채 표 끝에 두었을 때의 자동 스크롤
  · (선택) 칸 없애기, 왼쪽 메뉴로 화면 열기
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

PROBE_VERSION = '1'
APP_VERSION = ...  # build: 지후니우스 버전
WASH_POP_SOURCE = ...  # build: src/host/wash_pop.py
WASH_MES_SOURCE = ...  # build: src/host/wash_mes.py
WASH_READER_SOURCE = ...  # build: src/host/jihunius_main.py 의 WashReader
MES_LAYOUT_SOURCE = ...  # build: src/host/mes_layout.py

NARROW_BOUNDS = ("if(role==24 || role==25 || role==28 || (role==29 && CellBoundsMode!=1 && !skipCellBounds) || "
                 "role==37 || (role>=41 && role<=47)) {")
WIDE_BOUNDS = "if(role!=29 || (CellBoundsMode!=1 && !skipCellBounds)) {"


def load(source, name):
    scope = {'__name__': name}
    exec(compile(source, name + '.py', 'exec'), scope)
    return SimpleNamespace(**scope)


def explain(error):
    return '{}: {}'.format(type(error).__name__, error)


def experiments(env):
    """조작 시험을 차례로 하고 결과 줄들을 돌려줍니다. env: L(정렬 모듈), pointer, read(이름, 넓게), log, options, clock."""
    L, pointer, read, log = env.L, env.pointer, env.read, env.log
    out = ['MES 조작 점검 결과 · 점검 {} · 지후니우스 {}'.format(PROBE_VERSION, APP_VERSION)]
    say = out.append
    state = {'escape': None, 'scroll': None, 'removed': None}

    def section(title):
        say('')
        say('■ ' + title)
        log(title + '…')

    def attempt(title, action):
        section(title)
        try:
            action()
        except L.Stopped:
            raise
        except Exception as failure:
            say('  ✗ 이 시험은 오류로 중단: ' + explain(failure))
            say('    ' + ' / '.join(line.strip() for line in traceback.format_exc().strip().splitlines()[-4:])[:500])
        finally:
            if pointer.holding:
                pointer.drop()

    def tables(report):
        return [grid for row in L.arrange(L.grids(report, required=())) for grid in row]

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
        """판독에 나온 칸 제목의 x(표 밖이어도). 없으면 None."""
        return {header[0]: header[1] for header in grid['headers']}.get(name)

    # ── 환경 ──
    u = pointer.u
    say('화면 {}x{} (시작 {},{}) · MES 창 {} · 화살표 모양 {} · 더블클릭 간격 {:.0f}ms · 좌우 버튼 바꿈 {}'.format(
        u.GetSystemMetrics(78), u.GetSystemMetrics(79), u.GetSystemMetrics(76), u.GetSystemMetrics(77),
        pointer.rect(pointer.root), pointer.arrow, (pointer.double_click - 0.08) * 1000,
        '예' if pointer.press_flag == 0x0008 else '아니오'))

    # ── 처음 화면 ──
    section('처음 화면 읽기')
    started = env.clock()
    first = read('처음 화면', True)
    say('  읽는 데 {:.1f}초'.format(env.clock() - started))
    say(L.describe(first, rect=pointer.rect))
    usable = [grid for grid in tables(first) if sum(1 for item in grid['columns'] if whole(grid, item)) >= 4]
    if not usable:
        say('')
        say('✗ 시험할 표(칸이 4개 이상 보이는 표)를 찾지 못했습니다. MES에서 작업지시관리나 생산일보관리를 띄운 뒤 다시 해 주세요.')
        return out
    box = {'grid': usable[0]}
    handle = box['grid']['handle']
    native = L.native_parents(first)
    classes = L.native_classes(first)
    try:
        production = L.arrange(L.grids(first))
    except Exception:
        production = []
    original = order(box['grid'])
    original_widths = dict(L.widths_of(box['grid']))
    reading = [header[0] for header in box['grid']['headers']]

    def refresh(label):
        report = read(label, False)
        for grid in tables(report):
            if grid['handle'] == handle:
                box['grid'] = grid
                return grid
        raise RuntimeError('시험하던 표가 화면에서 사라졌습니다.')

    def pick():
        columns = box['grid']['columns']
        for start in (2, 1, 0):
            for index in range(start, len(columns) - 1):
                one, two = columns[index], columns[index + 1]
                if whole(box['grid'], one) and whole(box['grid'], two) and one['w'] >= 30 and two['w'] >= 30:
                    return one['name'], two['name']
        raise RuntimeError('나란히 보이는 칸 두 개를 찾지 못했습니다.')

    first_name, second_name = pick()
    say('')
    say('시험할 표: 왼쪽 위 ({}, {}) {}x{} · 보이는 칸 {}개 / 판독에 나온 칸 제목 {}개 · 판독 순서와 화면 순서 {}'.format(
        box['grid']['x'], box['grid']['y'], box['grid']['w'], box['grid']['h'], len(names(box['grid'])),
        len(box['grid']['headers']), '같음' if reading == original else '다름'))
    say('시험에 쓰는 칸: "{}" 과 그 오른쪽 "{}"'.format(first_name, second_name))

    # ── 포인터 모양 ──
    def edge_shapes():
        grid = box['grid']
        item = column(grid, first_name)
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
        say('  칸 "{}"의 오른쪽 경계(x={}) 둘레 — ◆ 크기 조절 모양, · 평소 모양'.format(first_name, edge))
        say('  ' + ' '.join(marks))
        say('  칸 제목 가운데에서의 모양 {} · 경계 둘레에서 본 모양 {}'.format(base, seen))

    def grab_edge(name):
        grid = box['grid']
        item = column(grid, name)
        edge, y = item['x'] + item['w'], item['y'] + item['h'] // 2
        points = [(edge + offset, y) for offset in L.EDGE_OFFSETS if grid['x'] <= edge + offset < grid['x'] + grid['w']]
        return pointer.find_edge(middle(item), points, lambda hit: hit == handle)

    # ── 칸 너비 ──
    def resize():
        grid = box['grid']
        before = dict(L.widths_of(grid))
        spot = column(grid, second_name)['x']
        point = grab_edge(first_name)
        if point is None:
            say('  ✗ 경계에서 크기 조절 모양을 확인하지 못해 누르지 않음 · ' + pointer.trace)
            return
        pointer.drag(point, (point[0] + 12, point[1]))
        pointer.sleep(0.25)
        now = refresh('칸 너비 +12 뒤')
        after = dict(L.widths_of(now))
        got = after.get(first_name, 0) - before[first_name]
        others = {name: after[name] - before[name] for name in after if name != first_name and name in before and after[name] != before[name]}
        say('  경계를 오른쪽으로 12 끎 → "{}" 너비 {} → {} ({:+d})'.format(first_name, before[first_name], after.get(first_name), got))
        say('  바로 뒤 칸 "{}" 위치 {:+d} · 다른 칸 너비 변화 {}'.format(
            second_name, column(now, second_name)['x'] - spot if column(now, second_name) else 0, others or '없음'))
        if got:
            point = grab_edge(first_name)
            if point is None:
                say('  ✗ 되돌리려는데 경계를 잡지 못함 · ' + pointer.trace)
                return
            pointer.drag(point, (point[0] - got, point[1]))
            pointer.sleep(0.25)
            now = refresh('칸 너비 되돌린 뒤')
        final = L.widths_of(now).get(first_name)
        say('  되돌린 뒤 너비 {} (처음 {}) → {}'.format(final, before[first_name],
                                               '원래대로' if final is not None and abs(final - before[first_name]) <= 1 else '✗ 처음과 다름'))

    # ── 판 사이 경계·메뉴 칸 경계 ──
    def shapes_across(item, title):
        gap = L.divider_gap(pointer, item)
        if gap is None:
            say('  {}: 틈을 찾지 못함 · 양쪽 창 {} {}'.format(title, pointer.rect(item['first']), pointer.rect(item['second'])))
            return None
        low, high, start, end = gap
        along = start + (end - start) // 4
        spot = (lambda value: (value, along)) if item['vertical'] else (lambda value: (along, value))
        pointer.check()
        pointer.move(spot(low - 24))
        pointer.sleep(0.1)
        base = pointer.settled(lambda shape: True)
        marks = []
        for value in range(low - 3, high + 3):
            pointer.move(spot(value))
            pointer.sleep(0.06)
            shape = pointer.settled(lambda shape: True)
            marks.append('{}{}'.format(value, '◆' if pointer.resizing(shape, base) else '·'))
        say('  {}: 틈 {}~{} · 길이 방향 {}~{} · 담긴 창 [{}] · 양쪽 창 [{}] [{}]'.format(
            title, low, high, start, end, classes.get(item['container'], '?')[:34],
            classes.get(item['first'], '?')[:34], classes.get(item['second'], '?')[:34]))
        say('    ' + ' '.join(marks))
        return gap

    def pull(item, amount):
        """경계를 amount만큼 끌고 실제로 움직인 양을 돌려줍니다. 누르지 못했으면 None."""
        index = 2 if item['vertical'] else 3
        before = pointer.rect(item['first'])[index]
        if not L.drag_divider(pointer, item, amount, lambda kind, value: None):
            say('    ✗ 크기 조절 모양을 확인하지 못해 누르지 않음 · ' + pointer.trace)
            return None
        L.settle(pointer, item)
        pointer.sleep(0.2)
        return pointer.rect(item['first'])[index] - before

    def panel_edges():
        items = L.dividers(production, native)
        say('  판 {}개 · 찾은 경계 {}개'.format(sum(len(row) for row in production), len(items)))
        tried = set()
        for item in items:
            if item['vertical'] in tried:
                continue
            tried.add(item['vertical'])
            title = '세로 경계(좌우로 나눔)' if item['vertical'] else '가로 경계(위아래로 나눔)'
            if shapes_across(item, title) is None:
                continue
            moved = pull(item, 14)
            if moved is None:
                continue
            say('    14만큼 끎 → 경계가 {:+d} 움직임'.format(moved))
            if moved:
                back = pull(item, -moved)
                say('    되돌림 → {}'.format('원래대로' if back == -moved else '✗ {} 움직임(처음과 다름)'.format(back)))

    def menu_edge():
        item = L.menu_divider([[box['grid']]], native, pointer)
        if item is None:
            say('  ✗ 왼쪽 메뉴 칸의 경계를 창 구조에서 찾지 못함')
            return
        if shapes_across(item, '메뉴 칸 경계') is None:
            return
        left, _, right, _ = pointer.rect(item['first'])
        width = right - left
        say('    메뉴 칸 너비 {}'.format(width))
        if width > L.MENU_COLLAPSED:
            gap = L.divider_gap(pointer, item)
            moved = pull(item, left - gap[0] + 1)
            if moved is None:
                return
            left, _, right, _ = pointer.rect(item['first'])
            say('    왼쪽 끝까지 끎 → 메뉴 칸 너비 {} → {} (가장 줄어든 너비)'.format(width, right - left))
            back = pull(item, width - (right - left))
        else:
            moved = pull(item, 150)
            if moved is None:
                return
            left, _, right, _ = pointer.rect(item['first'])
            say('    오른쪽으로 150 끎 → 메뉴 칸 너비 {} → {}'.format(width, right - left))
            back = pull(item, width - (right - left))
        left, _, right, _ = pointer.rect(item['first'])
        say('    되돌림 → 메뉴 칸 너비 {} ({})'.format(right - left, '원래대로' if abs(right - left - width) <= 2 else '✗ 처음과 다름'))

    # ── 칸 순서 ──
    def carry(name, target_name, side, down=0):
        """칸 제목 name을 끌어 target_name의 앞쪽(왼쪽 절반)·뒤쪽(오른쪽 절반)에 놓습니다. down>0이면 그만큼 아래에 놓습니다."""
        grid = box['grid']
        item, target = column(grid, name), column(grid, target_name)
        start = middle(item)
        y = start[1]
        end = (target['x'] + (target['w'] // 4 if side == '앞' else target['w'] * 3 // 4), y)
        shapes = []
        pointer.hold(start)
        try:
            pointer.sleep(0.08)
            if down:
                pointer.move((start[0], y + 8))
                pointer.sleep(0.06)
                pointer.move((start[0], y + down // 2))
                pointer.sleep(0.15)
                shapes.append(pointer.shape())
                end = (start[0], y + down)
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
        pointer.sleep(0.35)
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
        before = order(box['grid'])
        i, j = before.index(first_name), before.index(second_name)
        expected = list(before)
        expected[i], expected[j] = expected[j], expected[i]
        start, end, shapes = carry(first_name, second_name, '뒤')
        after = order(refresh('칸 옮긴 뒤'))
        say('  "{}" 칸 제목(x={})을 끌어 "{}"의 오른쪽 절반(x={})에 놓음 · 끄는 동안 포인터 모양 {}'.format(
            first_name, start[0], second_name, end[0], shapes))
        if after == before:
            say('  ✗ 순서가 바뀌지 않음')
            return
        gone = [name for name in before if name not in after]
        if gone:
            say('  ✗ 칸이 사라짐: {} — MES를 다시 켜면 돌아옵니다.'.format(', '.join(gone)))
            return
        say('  → 그 자리 순서: {} → {} ({})'.format(' , '.join(before[max(0, i - 1):j + 2]), ' , '.join(after[max(0, i - 1):j + 2]),
                                              '두 칸이 자리를 바꿈' if after == expected else '예상과 다름'))
        carry(first_name, second_name, '앞')
        back = order(refresh('칸 되돌린 뒤'))
        if back == before:
            say('  "{}"을 다시 끌어 "{}"의 왼쪽 절반에 놓음 → 원래 순서로 돌아옴'.format(first_name, second_name))
        else:
            say('  ✗ 되돌린 뒤 순서가 처음과 다름 → 한 칸씩 되돌리는 중')
            say('  ' + ('원래 순서로 되돌림' if restore_order(before) else '✗ 되돌리지 못함. 지금 순서: ' + ', '.join(order(box['grid'])[:14])))

    def escape():
        # 놓으면 순서가 바뀌는 자리(오른쪽 칸의 오른쪽 절반)까지 끈 뒤 Esc → 놓음. 취소되면 순서가 그대로입니다.
        before = order(box['grid'])
        start = middle(column(box['grid'], first_name))
        target = column(box['grid'], second_name)
        end = (target['x'] + target['w'] * 3 // 4, start[1])
        pointer.hold(start)
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
        pointer.sleep(0.35)
        after = order(refresh('Esc 뒤'))
        state['escape'] = after == before
        say('  "{}" 칸 제목을 "{}"의 오른쪽 절반까지 끈 상태에서 Esc → 놓음 · Esc 뒤 포인터 모양 {}'.format(first_name, second_name, shape))
        if after == before:
            say('  → 순서 그대로(Esc로 끌기가 취소됨)')
        else:
            say('  ✗ 순서가 바뀜(Esc로 취소되지 않음): ' + ', '.join(after[:10]))
            say('  ' + ('원래 순서로 되돌림' if restore_order(before) else '✗ 되돌리지 못함'))

    # ── 가로 스크롤 ──
    def shifted_wheel(notches):
        pointer.key(0x10, up=False)
        try:
            pointer.sleep(0.05)
            pointer.wheel(notches)
            pointer.sleep(0.05)
        finally:
            pointer.key(0x10, down=False)

    def scroll():
        grid = box['grid']
        right = grid['x'] + grid['w']
        outside = [header for header in grid['headers'] if header[3] > 0 and header[1] >= right]
        nowhere = [header for header in grid['headers'] if header[3] <= 0]
        say('  판독에 나온 칸 제목 {}개 · 표 안에서 시작하는 것 {}개 · 표 오른쪽 밖 {}개 · 위치가 없는 것 {}개'.format(
            len(grid['headers']), len(grid['columns']), len(outside), len(nowhere)))
        if outside:
            say('  표 밖 칸(이름@x): ' + ' | '.join('{}@{}'.format(header[0], header[1]) for header in outside[:6]))
        if nowhere:
            say('  위치 없는 칸: ' + ' | '.join(header[0] for header in nowhere[:10]))
        last = grid['columns'][-1]
        if not outside and not nowhere and last['x'] + last['w'] <= right and not grid.get('scrolled'):
            say('  가로로 넘치는 칸이 없어 가로 스크롤 시험은 건너뜀')
            return
        spot = middle(column(grid, first_name))
        for title, forward, backward in (('가로 휠 3칸', lambda: pointer.wheel(3, True), lambda: pointer.wheel(-3, True)),
                                         ('Shift+세로 휠 3칸', lambda: shifted_wheel(-3), lambda: shifted_wheel(3))):
            pointer.check()
            pointer.move(spot)
            pointer.sleep(0.12)
            start = place(box['grid'], first_name)
            forward()
            pointer.sleep(0.5)
            moved = place(refresh(title + ' 뒤'), first_name)
            if moved is None or start is None or moved == start:
                say('  {}: 표가 움직이지 않음'.format(title))
                continue
            say('  {}: 표가 가로로 {}픽셀 움직임'.format(title, start - moved))
            pointer.check()
            pointer.move(spot)
            pointer.sleep(0.12)
            backward()
            pointer.sleep(0.5)
            back = place(refresh(title + ' 되돌린 뒤'), first_name)
            say('    반대로 굴림 → {}'.format('원래 자리' if back == start else '✗ 처음과 {}픽셀 차이'.format((back or 0) - start)))
            state['scroll'] = (forward, backward, abs(start - moved))
            return

    def unscroll(target):
        """가로로 밀린 표를 휠로 되돌립니다(되는 방식이 확인된 경우)."""
        if not state['scroll']:
            return False
        forward, backward, amount = state['scroll']
        spot = (box['grid']['x'] + 60, box['grid']['columns'][0]['y'] + box['grid']['columns'][0]['h'] // 2)
        for _ in range(8):
            now = place(box['grid'], first_name)
            if now is None or now == target:
                break
            pointer.check()
            pointer.move(spot)
            pointer.sleep(0.12)
            (backward if now < target else forward)()
            pointer.sleep(0.5)
            refresh('가로 스크롤 되돌리는 중')
        return place(box['grid'], first_name) == target

    def autoscroll():
        grid = box['grid']
        right = grid['x'] + grid['w']
        if not state['escape']:
            say('  Esc로 끌기 취소가 확인되지 않아 건너뜀')
            return
        if not any(header[1] >= right for header in grid['headers']) and grid['columns'][-1]['x'] + grid['columns'][-1]['w'] <= right:
            say('  가로로 넘치는 칸이 없어 건너뜀')
            return
        before = order(grid)
        start_place = place(grid, first_name)
        item = [one for one in grid['columns'] if whole(grid, one)][-1]
        start = middle(item)
        pointer.hold(start)
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
        pointer.sleep(0.35)
        now = refresh('끈 채 표 끝에 둔 뒤')
        moved = (start_place or 0) - (place(now, first_name) or 0)
        say('  "{}" 칸 제목을 끈 채 표 오른쪽 끝에 1.5초 둔 뒤 Esc → 표가 가로로 {}픽셀 움직임{}'.format(
            item['name'], moved, '' if moved else ' (자동 스크롤 없음)'))
        if moved:
            say('  ' + ('휠로 원래 자리로 되돌림' if unscroll(start_place) else '✗ 표가 가로로 밀린 채입니다. 표 아래 가로 스크롤을 왼쪽 끝으로 옮겨 주세요.'))
        if order(box['grid']) != before:
            say('  ✗ 순서가 바뀜 → ' + ('원래 순서로 되돌림' if restore_order(before) else '되돌리지 못함'))

    # ── 칸 없애기(선택) ──
    def remove():
        name = env.options.get('remove', '')
        grid = box['grid']
        item = column(grid, name)
        if item is None or not whole(grid, item):
            say('  "{}" 칸이 지금 화면에 다 보이지 않아 건너뜀. 보이는 칸: {}'.format(name, ', '.join(names(grid)[:14])))
            return
        before = order(grid)
        start, end, shapes = carry(name, name, '앞', down=140)
        now = refresh('칸 없앤 뒤')
        left = order(now)
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

    # ── 끝난 뒤 확인 ──
    def final():
        now = refresh('마지막 확인')
        wanted = [name for name in original if name != state['removed']]
        say('  칸 순서: ' + ('처음과 같음' if order(now) == wanted else '✗ 처음과 다름 → ' + ', '.join(order(now)[:14])))
        widths = L.widths_of(now)
        changed = {name: (original_widths[name], widths[name]) for name in wanted
                   if name in widths and abs(widths[name] - original_widths[name]) > 1}
        say('  칸 너비: ' + ('처음과 같음' if not changed else '✗ 다름(처음, 지금) {}'.format(changed)))
        say('  표 위치·크기: ({}, {}) {}x{}'.format(now['x'], now['y'], now['w'], now['h']))

    # ── 왼쪽 메뉴로 화면 열기(선택) ──
    def menu_open():
        def lookup(report, name):
            return [item for item in L.elements(report)
                    if str(item.get('name', '')).strip() == name and item.get('role') != 37
                    and len(item.get('bounds') or ()) == 4 and item['bounds'][2] > 4 and item['bounds'][3] > 4]

        def tabs(report):
            return ['{}{}'.format(str(item.get('name', '')).strip(), '(선택)' if item.get('selected') else '')
                    for item in L.elements(report) if item.get('role') == 37]

        def press(item, twice=False):
            x, y, w, h = item['bounds']
            point = (x + w // 2, y + h // 2)
            hit = pointer.window_at(point)
            if item.get('handle') not in pointer.lineage(hit):     # 그 항목이 든 창(또는 그 안쪽 창) 위일 때만 누릅니다.
                say('    ✗ "{}" 자리가 다른 창(창{})에 가려져 누르지 않음'.format(item.get('name'), hit))
                return False
            (pointer.double_click if twice else pointer.click)(point)
            return True

        report = read('메뉴 읽기', True)
        say('  지금 탭: ' + ', '.join(tabs(report)))
        group = lookup(report, '설비관리')
        if not group:
            say('  ✗ 왼쪽 메뉴에서 "설비관리"를 찾지 못함(메뉴 칸이 접혀 있으면 넓힌 뒤 다시 해 주세요).')
            return
        say('  "설비관리": 종류 {}({}) @{} · 같은 이름 {}개'.format(group[0].get('role'), group[0].get('type', ''), group[0]['bounds'], len(group)))
        if not lookup(report, '설비별공구관리'):
            if not press(group[0]):
                return
            pointer.sleep(0.8)
            report = read('설비관리 누른 뒤', True)
        entry = lookup(report, '설비별공구관리')
        if not entry:
            say('  ✗ "설비관리"를 눌러도 "설비별공구관리"가 보이지 않음')
            window = group[0].get('handle')
            say('    메뉴 창의 항목: ' + ' | '.join(str(item.get('name', ''))[:14] for item in L.elements(report)
                                              if item.get('handle') == window and str(item.get('name', '')).strip())[:600])
            return
        say('  "설비관리"를 누르니 "설비별공구관리"가 보임: 종류 {}({}) @{}'.format(entry[0].get('role'), entry[0].get('type', ''), entry[0]['bounds']))
        before = tabs(report)
        if not press(entry[0]):
            return
        pointer.sleep(1.6)
        report = read('설비별공구관리 누른 뒤', True)
        opened = any(name.startswith('설비별공구관리') for name in tabs(report)) and tabs(report) != before
        if not opened:
            say('    한 번 눌러서는 탭이 생기지 않음 → 두 번 누름')
            entry = lookup(report, '설비별공구관리')
            if entry and press(entry[0], twice=True):
                pointer.sleep(1.6)
                report = read('설비별공구관리 두 번 누른 뒤', True)
                opened = any(name.startswith('설비별공구관리') for name in tabs(report)) and tabs(report) != before
        say('  → {} · 지금 탭: {}'.format('화면이 열림' if opened else '✗ 열린 것을 확인하지 못함', ', '.join(tabs(report))))
        # 처음 화면으로 돌아가기: 문서 탭 '작업지시관리'
        back = [item for item in L.elements(report) if item.get('role') == 37 and str(item.get('name', '')).strip() == '작업지시관리'
                and len(item.get('bounds') or ()) == 4 and item['bounds'][2] > 4]
        if opened and back:
            back.sort(key=lambda item: item['bounds'][1])
            if press(back[0]):
                pointer.sleep(1.2)
                report = read('작업지시관리 탭으로 돌아온 뒤', True)
                say('  문서 탭 "작업지시관리"를 눌러 돌아옴 · 지금 탭: {} · 처음 표 {}'.format(
                    ', '.join(tabs(report)), '다시 보임' if any(grid['handle'] == handle for grid in tables(report)) else '✗ 안 보임'))
        elif opened:
            say('  ✗ 돌아갈 문서 탭 "작업지시관리"의 위치를 찾지 못함. 직접 눌러 돌아가 주세요.')

    try:
        attempt('칸 경계에서의 포인터 모양 (누르지 않음)', edge_shapes)
        attempt('칸 너비 끌기', resize)
        if sum(len(row) for row in production) >= 2:
            attempt('판 사이 경계', panel_edges)
        attempt('왼쪽 메뉴 칸 경계', menu_edge)
        attempt('경계 시험 뒤 다시 읽기', lambda: say('  표 위치 ({}, {})'.format(refresh('경계 시험 뒤')['x'], box['grid']['y'])))
        attempt('칸 제목을 끌어 순서 바꾸기', reorder)
        attempt('Esc로 끌기 취소', escape)
        attempt('표 가로 스크롤', scroll)
        attempt('칸 제목을 끈 채 표 끝에 두기(자동 스크롤)', autoscroll)
        if env.options.get('remove'):
            attempt('칸 없애기', remove)
        attempt('끝난 뒤 확인', final)
        if env.options.get('menu'):
            attempt('왼쪽 메뉴로 화면 열기', menu_open)
    except L.Stopped:
        say('')
        say('F9로 중지했습니다. 여기까지의 결과입니다.')
    finally:
        if pointer.holding:
            pointer.drop()
        pointer.restore()
    say('')
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

    def read(label, wide=False):
        log(label + ' 읽는 중…')
        if wide not in readers:
            readers[wide] = make_reader(P, wide)
        return readers[wide].capture({**target, 'mode': 'mes_rows'}, label, stop)

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
    root.geometry('820x640')
    body = ttk.Frame(root, padding=16)
    body.pack(fill='both', expand=True)
    ttk.Label(body, text='MES 조작 점검', font=('맑은 고딕', 15, 'bold')).pack(anchor='w')
    ttk.Label(body, justify='left', wraplength=780, text=(
        '지후니우스 MES 정렬이 쓰려는 조작을 실제 MES에서 작게 해 보고 되돌린 뒤, 결과를 글로 정리합니다.\n'
        '1) MES에서 시험할 화면(작업지시관리 또는 생산일보관리)을 띄워 두세요. 칸을 고치는 중이면 끝내고 시작해 주세요.\n'
        '2) [점검 시작]을 누르면 MES가 앞으로 나오고 마우스가 저절로 움직입니다. 1~2분 동안 마우스·키보드를 건드리지 말아 주세요. 멈추려면 F9.\n'
        '3) 하는 일: 칸 너비·판 경계·메뉴 칸 경계를 끌었다 되돌리기, 칸 제목을 옮겼다 되돌리기, 가로 스크롤. 행·값·저장은 건드리지 않습니다.\n'
        '4) 끝나면 결과 글이 복사되고 이 파일 옆에 저장됩니다. 그 글을 그대로 보내 주세요(칸 제목·메뉴 이름과 숫자만 들어갑니다).')).pack(anchor='w', pady=(8, 10))
    options = ttk.Frame(body)
    options.pack(fill='x')
    ttk.Label(options, text='없애 볼 칸 이름(평소 없애는 칸 하나, 비우면 안 함):').pack(side='left')
    remove = tk.StringVar(value='')
    ttk.Entry(options, textvariable=remove, width=16).pack(side='left', padx=6)
    menu = tk.BooleanVar(value=True)
    ttk.Checkbutton(body, text='왼쪽 메뉴에서 설비관리 → 설비별공구관리를 열어 보기(열고 나서 작업지시관리 탭으로 돌아옵니다)', variable=menu).pack(anchor='w', pady=(6, 0))
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
        threading.Thread(target=work, args=({'remove': remove.get().strip(), 'menu': menu.get()},), daemon=True).start()
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
