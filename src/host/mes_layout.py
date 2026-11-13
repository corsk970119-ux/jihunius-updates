"""MES 생산일보관리 화면 정렬 (지후니우스 'MES 정렬').

하는 일
  0) 왼쪽 메뉴 칸(파란 바)을 왼쪽 끝까지 줄입니다: 메뉴와 본문 사이 경계선을 끕니다.
  1) 화면에 보이는 생산일보 표(판)를 모두 같은 크기로: 판 사이 경계선을 끌어 가로·세로를 똑같이 나눕니다.
  2) 모든 표의 칸 너비를 기준(칸 이름 → 너비)에 맞춥니다: 칸 제목의 오른쪽 경계선을 끕니다.

읽기는 세척완료와 같은 화면 판독(mes_rows: 표·칸 제목 위치와 창 목록)과 창 위치 조회만 씁니다.
조작은 '경계선 끌기' 하나뿐입니다. 누르기 전에 마우스를 경계선에 올려 포인터가 크기 조절 모양으로
바뀌는 것을 확인하고, 바뀌지 않으면 누르지 않습니다(칸 제목을 눌러 정렬·이동시키지 않기 위함).
MES의 행·값·저장은 건드리지 않습니다.
"""
import ctypes
import json
import os
import time
from collections import OrderedDict

REQUIRED_HEADERS = ('P/No.', '세척')   # 생산일보 표를 알아보는 칸 이름
TOLERANCE = 1                # 이 픽셀 이내 차이는 같은 크기로 봅니다.
MAX_GAP = 60                 # 판 사이 틈이 이보다 넓으면 경계선으로 보지 않습니다.
PANEL_ROUNDS = 4             # 판 크기 맞춤 반복 한도
COLUMN_PASSES = 3            # 칸 너비 맞춤 반복 한도(매번 화면을 다시 읽어 확인)
EDGE_OFFSETS = (-2, -1, -3, 0, -4, 1, 2)   # 칸 경계에서 포인터를 올려 볼 위치(경계 기준 픽셀)
HOVER_SECONDS = 0.15         # 포인터 모양이 바뀌기를 기다리는 시간
MENU_COLLAPSED = 40          # 왼쪽 메뉴 칸(파란 바)이 이 너비 이하면 이미 줄여 둔 것으로 봅니다.
MENU_WORDS = ('생산관리', '설비관리', '작업지시관리', '설비별공구관리', '생산일보관리', '작업지시조회', '메뉴', '즐겨찾기')
PRESET_VERSION = 1


class Stopped(Exception):
    pass


# ── 화면 판독 결과 해석 ─────────────────────────────────────────────────────────

def elements(report):
    return [r for r in report.get('records', ()) if isinstance(r, dict) and r.get('kind') == 'element']


def native_parents(report):
    """창 손잡이 → 부모 창 손잡이."""
    return {r.get('handle'): r.get('native_parent') for r in report.get('records', ())
            if isinstance(r, dict) and r.get('kind') == 'native_window'}


def native_classes(report):
    return {r.get('handle'): str(r.get('class', '')) for r in report.get('records', ())
            if isinstance(r, dict) and r.get('kind') == 'native_window'}


def _box(item):
    bounds = item.get('bounds') or ()
    if len(bounds) != 4:
        return 0, 0, 0, 0
    return int(bounds[0]), int(bounds[1]), int(bounds[2]), int(bounds[3])


def grids(report):
    """화면에 보이는 생산일보 표와 칸 제목 위치."""
    items = elements(report)
    children = {}
    for item in items:
        children.setdefault(item.get('parent'), []).append(item)
    found = []
    for table in items:
        if table.get('role') != 24:
            continue
        x, y, w, h = _box(table)
        if w <= 0 or h <= 0:
            continue
        headers = [header for group in children.get(table.get('id'), ())
                   for header in children.get(group.get('id'), ()) if header.get('role') == 25]
        names = [str(header.get('name', '')) for header in headers]
        if any(name not in names for name in REQUIRED_HEADERS):
            continue
        if len(set(names)) != len(names):
            raise RuntimeError('칸 이름이 겹쳐 표를 구분할 수 없습니다.')
        columns = []
        for header in headers:
            hx, hy, hw, hh = _box(header)
            if hw > 0 and hh > 0 and hx < x + w:     # 표 오른쪽 밖에서 시작하는 칸은 보이지 않는 칸
                columns.append({'name': str(header.get('name', '')), 'x': hx, 'y': hy, 'w': hw, 'h': hh})
        columns.sort(key=lambda column: column['x'])
        # 칸 제목이 표 왼쪽 밖으로 나가 있으면 가로 스크롤로 밀린 상태입니다(경계 위치를 믿을 수 없음).
        scrolled = any(_box(header)[2] > 0 and _box(header)[0] < x - 1 for header in headers)
        found.append({'handle': table.get('handle'), 'x': x, 'y': y, 'w': w, 'h': h, 'columns': columns,
                      'scrolled': scrolled})
    return found


def arrange(found):
    """표들을 줄(위→아래)과 그 안의 순서(왼쪽→오른쪽)로 묶습니다."""
    rows = []
    for grid in sorted(found, key=lambda g: (g['y'], g['x'])):
        for row in rows:
            head = row[0]
            overlap = min(head['y'] + head['h'], grid['y'] + grid['h']) - max(head['y'], grid['y'])
            if overlap * 2 > min(head['h'], grid['h']):
                row.append(grid)
                break
        else:
            rows.append([grid])
    for row in rows:
        row.sort(key=lambda g: g['x'])
    rows.sort(key=lambda row: row[0]['y'])
    return rows


def label(rows, r, c):
    if len(rows) == 2 and all(len(row) == 3 for row in rows):
        return ('위쪽', '아래쪽')[r] + ' ' + ('왼쪽', '가운데', '오른쪽')[c]
    return '{}줄 {}번째'.format(r + 1, c + 1)


def widths_of(grid):
    return OrderedDict((column['name'], column['w']) for column in grid['columns'])


def same_rows(before, after):
    """다시 읽은 화면이 같은 표들인지 확인하고 새 위치를 돌려줍니다."""
    if [[g['handle'] for g in row] for row in before] != [[g['handle'] for g in row] for row in after]:
        raise RuntimeError('정렬하는 동안 MES 화면 구성이 바뀌어 중단했습니다.')
    return after


def follow(grid, before, after):
    """판 경계를 옮겨 표가 움직인 만큼 표와 칸 제목 위치를 옮깁니다(화면을 다시 읽지 않고 계산)."""
    dx, dy = after[0] - before[0], after[1] - before[1]
    grid['x'] += dx
    grid['y'] += dy
    grid['w'] += (after[2] - after[0]) - (before[2] - before[0])
    grid['h'] += (after[3] - after[1]) - (before[3] - before[1])
    for column in grid['columns']:
        column['x'] += dx
        column['y'] += dy


def remaining(rows, widths):
    """기준과 아직 다른 칸: {판 이름: [(칸 이름, 현재 너비, 기준 너비), …]}"""
    left = OrderedDict()
    for r, row in enumerate(rows):
        for c, grid in enumerate(row):
            differ = [(column['name'], column['w'], int(widths[column['name']])) for column in grid['columns']
                      if column['name'] in widths and abs(int(widths[column['name']]) - column['w']) > TOLERANCE]
            if differ:
                left[label(rows, r, c)] = differ
    return left


# ── 기준 너비 저장 ──────────────────────────────────────────────────────────────

def load_preset(path):
    """저장한 기준(칸 이름 → 너비). 없거나 읽을 수 없으면 None."""
    try:
        with open(str(path), encoding='utf-8') as handle:
            data = json.load(handle)
        widths = OrderedDict()
        for name, width in data['columns']:
            if isinstance(name, str) and name and isinstance(width, int) and not isinstance(width, bool) and 5 <= width <= 3000:
                widths[name] = width
        return widths or None
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return None


def preset_saved_at(path):
    try:
        with open(str(path), encoding='utf-8') as handle:
            return str(json.load(handle).get('saved_at', ''))
    except (OSError, ValueError, TypeError, AttributeError):
        return ''


def save_preset(path, widths, source=''):
    data = {'version': PRESET_VERSION, 'columns': [[str(name), int(width)] for name, width in widths.items()],
            'source': str(source), 'saved_at': time.strftime('%Y-%m-%d %H:%M')}
    directory = os.path.dirname(str(path))
    if directory:
        os.makedirs(directory, exist_ok=True)
    temporary = str(path) + '.tmp'
    with open(temporary, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, ensure_ascii=False)
    os.replace(temporary, str(path))
    return data


# ── 판 사이 경계선 ──────────────────────────────────────────────────────────────

def lineage(native, handle):
    chain = []
    while handle and handle not in chain:
        chain.append(handle)
        handle = native.get(handle)
    return chain


def divider(native, first, second):
    """두 표를 나누는 경계: 공통 조상 창(container)과 그 바로 아래에서 갈라지는 두 창."""
    a = lineage(native, first)
    b = lineage(native, second)
    where = {handle: index for index, handle in enumerate(b)}
    for index, handle in enumerate(a):
        if handle in where:
            if index == 0 or where[handle] == 0:
                return None
            return {'container': handle, 'first': a[index - 1], 'second': b[where[handle] - 1],
                    'depth': len(a) - index}
    return None


def dividers(rows, native):
    """판 사이 경계선 목록(바깥쪽 경계부터). vertical=True는 좌우로 나누는 세로 경계입니다."""
    found = []
    seen = set()

    def add(vertical, r, c, first, second):
        split = divider(native, first['handle'], second['handle'])
        if split is None:
            return
        key = (split['container'], split['first'], split['second'])
        if key not in seen:
            seen.add(key)
            found.append(dict(split, vertical=vertical, row=r, column=c))

    for r, row in enumerate(rows):
        for c in range(len(row) - 1):
            add(True, r, c, row[c], row[c + 1])
    for r in range(len(rows) - 1):
        for c in range(min(len(rows[r]), len(rows[r + 1]))):
            add(False, r, c, rows[r][c], rows[r + 1][c])
    found.sort(key=lambda item: item['depth'])
    return found


def needed(item, rows, size):
    """같은 크기가 되려면 이 경계를 얼마나 옮겨야 하는지(+: 오른쪽·아래)."""
    if item['vertical']:
        values = [size(grid)[0] for grid in rows[item['row']]]
        index = item['column']
    else:
        values = [size(row[min(item['column'], len(row) - 1)])[1] for row in rows]
        index = item['row']
    mean = sum(values) / float(len(values))
    return int(round((index + 1) * mean - sum(values[:index + 1])))


def divider_gap(pointer, item):
    """경계선이 놓인 틈: (틈 시작, 틈 끝, 경계선 길이 방향 시작, 끝). 틈이 이상하면 None."""
    l1, t1, r1, b1 = pointer.rect(item['first'])
    l2, t2, r2, b2 = pointer.rect(item['second'])
    if item['vertical']:
        low, high, start, end = r1, l2, max(t1, t2), min(b1, b2)
    else:
        low, high, start, end = b1, t2, max(l1, l2), min(r1, r2)
    if not 1 <= high - low <= MAX_GAP or end - start < 60:
        return None
    return low, high, start, end


def drag_divider(pointer, item, amount, emit):
    gap = divider_gap(pointer, item)
    if gap is None:
        emit('note', '경계선 틈을 찾지 못함 · {} · {}'.format('세로' if item['vertical'] else '가로', item))
        return False
    low, high, start, end = gap
    middle = (low + high - 1) // 2
    across = sorted(range(low, high), key=lambda value: (abs(value - middle), value))[:9]

    def on_divider(hit):   # 두 판 어느 쪽에도 속하지 않고 공통 조상 창 안에 있는 곳
        chain = pointer.lineage(hit)
        return item['container'] in chain and item['first'] not in chain and item['second'] not in chain

    # 경계선 한가운데(접기 단추가 있을 수 있는 자리)는 피해서 잡습니다.
    for fraction in (0.25, 0.75):
        along = start + int((end - start) * fraction)
        if item['vertical']:
            neutral = (low - 24, along)
            points = [(value, along) for value in across]
        else:
            neutral = (along, low - 24)
            points = [(along, value) for value in across]
        point = pointer.find_edge(neutral, points, on_divider)
        if point is not None:
            target = (point[0] + amount, point[1]) if item['vertical'] else (point[0], point[1] + amount)
            pointer.drag(point, target)
            emit('note', '판 경계 {} {:+d} · {} → {}'.format('세로' if item['vertical'] else '가로', amount, point, target))
            return True
    emit('note', '판 경계에서 크기 조절 모양을 확인하지 못함 · {} · 틈 {}~{} · {}'.format(
        '세로' if item['vertical'] else '가로', low, high, pointer.trace))
    return False


def settle(pointer, item):
    """경계선을 놓은 뒤 양쪽 창의 위치가 더 바뀌지 않을 때까지 잠깐 기다립니다."""
    previous = None
    for _ in range(30):
        current = (pointer.rect(item['first']), pointer.rect(item['second']))
        if current == previous:
            return
        previous = current
        pointer.sleep(0.02)


def menu_divider(rows, native, pointer):
    """왼쪽 메뉴 칸(파란 바)과 본문 사이의 경계선.

    왼쪽 위 표의 조상 창들 가운데(바깥쪽부터), 바로 왼쪽에 틈을 두고 형제 창이 붙어 있고 그 형제 창이
    MES 창의 왼쪽 끝에 닿아 있는 것을 찾습니다. 없으면 None.
    """
    chain = lineage(native, rows[0][0]['handle'])
    children = {}
    for handle, parent in native.items():
        children.setdefault(parent, []).append(handle)
    try:
        window_left = pointer.rect(pointer.root)[0]
    except Exception:
        return None
    for index in range(len(chain) - 1, 0, -1):
        container, second = chain[index], chain[index - 1]
        try:
            left, top, right, bottom = pointer.rect(second)
        except Exception:
            continue
        best = None
        for sibling in children.get(container, ()):
            if sibling == second:
                continue
            try:
                l, t, r, b = pointer.rect(sibling)
            except Exception:
                continue
            if (1 <= left - r <= MAX_GAP and l - window_left <= 12 and min(b, bottom) - max(t, top) >= 100
                    and (best is None or r > best[1])):
                best = (sibling, r)
        if best is not None:
            return {'container': container, 'first': best[0], 'second': second, 'vertical': True,
                    'depth': len(chain) - index}
    return None


def collapse_menu(rows, native, pointer, emit):
    """왼쪽 메뉴 칸을 갈 수 있는 데까지 왼쪽으로 줄입니다. 반환: found/moved/failed와 줄이기 전후 너비."""
    item = menu_divider(rows, native, pointer)
    if item is None:
        emit('note', '왼쪽 메뉴 칸의 경계선을 찾지 못함')
        return {'found': False, 'moved': False, 'failed': False}
    left, _, right, _ = pointer.rect(item['first'])
    state = {'found': True, 'moved': False, 'failed': False, 'before': right - left, 'after': right - left}
    emit('note', '왼쪽 메뉴 칸 {} · 너비 {} · 틈 {}'.format(pointer.rect(item['first']), right - left, divider_gap(pointer, item)))
    if right - left <= MENU_COLLAPSED:
        return state
    gap = divider_gap(pointer, item)
    if gap is not None and drag_divider(pointer, item, left - gap[0] + 1, emit):
        settle(pointer, item)
        left, _, right, _ = pointer.rect(item['first'])
        state.update(moved=True, after=right - left)
    else:
        state['failed'] = True
    return state


def equalize(rows, native, pointer, emit, check):
    """판(표)들의 가로·세로 크기를 같게 맞춥니다."""
    items = dividers(rows, native)

    def size(grid):
        left, top, right, bottom = pointer.rect(grid['handle'])
        return right - left, bottom - top

    moved = 0
    missed = set()
    for _ in range(PANEL_ROUNDS):
        changed = False
        for number, item in enumerate(items):
            check()
            if number in missed:
                continue
            amount = needed(item, rows, size)
            if abs(amount) <= TOLERANCE:
                continue
            if drag_divider(pointer, item, amount, emit):
                moved += 1
                changed = True
                settle(pointer, item)
            else:
                missed.add(number)
        if not changed:
            break
    sizes = [[size(grid) for grid in row] for row in rows]
    flat = [item for row in sizes for item in row]
    uneven = (max(w for w, _ in flat) - min(w for w, _ in flat) > 2 * TOLERANCE
              or max(h for _, h in flat) - min(h for _, h in flat) > 2 * TOLERANCE)
    return {'dividers': len(items), 'moved': moved, 'missed': len(missed), 'uneven': uneven, 'sizes': sizes}


# ── 칸 너비 ─────────────────────────────────────────────────────────────────────

def clipped(grid):
    """칸 제목이 표의 보이는 범위를 벗어나 있어(가로로 밀렸거나 오른쪽이 잘림) 너비를 믿을 수 없는지."""
    right = grid['x'] + grid['w']
    return bool(grid.get('scrolled')) or any(column['x'] + column['w'] > right for column in grid['columns'])


def align_columns(grid, widths, pointer, emit, check):
    """표 하나의 칸 너비를 widths에 맞춥니다. 반환: (맞춘 칸 수, 경계를 잡지 못한 칸 이름들)

    줄여야 하는 칸을 먼저 끌고(왼쪽부터) 그다음 넓힐 칸을 끕니다. 앞 칸의 너비를 바꾸면 뒤 칸들이 그만큼
    밀리므로 이미 끈 만큼을 더해 다음 경계 위치를 잡습니다. 줄여야 할 칸의 경계가 표 오른쪽 밖으로 나가
    있으면, 왼쪽의 넓은 칸을 잠시 줄여 경계를 안으로 들인 뒤 맞추고 그 칸을 되돌립니다.
    """
    columns = grid['columns']
    applied = [0] * len(columns)
    left, right = grid['x'], grid['x'] + grid['w']

    def width(index):
        return columns[index]['w'] + applied[index]

    def edge(index):
        return columns[index]['x'] + columns[index]['w'] + sum(applied[:index + 1])

    def wanted(index):
        name = columns[index]['name']
        return int(widths[name]) - width(index) if name in widths else 0

    def pull(index, amount):
        """index번째 칸의 오른쪽 경계를 amount만큼 끕니다. 경계를 확인하지 못하면 누르지 않고 False."""
        check()
        at = edge(index)
        y = columns[index]['y'] + columns[index]['h'] // 2
        neutral = (at - width(index) // 2, y)
        points = [(at + offset, y) for offset in EDGE_OFFSETS if left <= at + offset < right]
        if not points or not left <= neutral[0] < right:
            pointer.trace = '경계가 표의 보이는 범위 밖 (경계 {} · 표 {}~{})'.format(at, left, right)
            return False
        point = pointer.find_edge(neutral, points, lambda hit: hit == grid['handle'])
        if point is None:
            return False
        pointer.drag(point, (point[0] + amount, point[1]))
        applied[index] += amount
        return True

    done = 0
    missed = []
    order = ([index for index in range(len(columns)) if wanted(index) < -TOLERANCE]
             + [index for index in range(len(columns)) if wanted(index) > TOLERANCE])
    for index in order:
        amount = wanted(index)
        lent = []
        if amount < 0 and edge(index) - 2 >= right:
            need = edge(index) - (right - 8)
            for other in sorted(range(index), key=lambda i: -width(i)):
                if need <= 0:
                    break
                give = min(need, width(other) - 30)
                if give >= 2 and pull(other, -give):
                    lent.append((other, give))
                    need -= give
        if pull(index, amount):
            done += 1
        else:
            missed.append(columns[index]['name'])
            emit('note', '칸 경계 미확인 · {} · x={} · {}'.format(columns[index]['name'], edge(index), pointer.trace))
        for other, give in lent:
            if not pull(other, give):   # 되돌리지 못해도 다음 확인에서 기준과 달라 다시 맞춥니다.
                emit('note', '빌린 너비를 되돌리지 못함 · {} · {}'.format(columns[other]['name'], pointer.trace))
    missed.sort(key=[column['name'] for column in columns].index)
    return done, missed


# ── 전체 흐름 ───────────────────────────────────────────────────────────────────

def align(target, pointer, capture, stop, emit, report, widths=None):
    """판 크기를 같게 하고 칸 너비를 widths(칸 이름 → 너비)에 맞춥니다.

    widths가 없으면 왼쪽 위 표의 지금 너비를 기준으로 씁니다(result['used_reference']=True).
    """
    def check():
        if stop.is_set():
            raise Stopped('사용자 중지')

    def read(text):
        return capture(dict(target, mode='mes_rows'), text, stop)

    rows = arrange(grids(report))
    count = sum(len(row) for row in rows)
    if not count:
        raise RuntimeError('MES 생산일보관리 화면에서 생산일보 표를 찾지 못했습니다.')
    if not rows[0][0]['columns']:
        raise RuntimeError('왼쪽 위 표의 칸 제목 위치를 읽지 못했습니다.')
    result = {'tables': count, 'layout': [len(row) for row in rows], 'used_reference': widths is None,
              'reference': label(rows, 0, 0)}
    emit('note', '표 {}개 · 배치 {} · 기준 {}'.format(
        count, result['layout'], dict(widths) if widths is not None else '없음(왼쪽 위 판의 지금 너비를 씀)'))

    native = native_parents(report)
    classes = native_classes(report)
    for item in dividers(rows, native):
        try:
            emit('note', '경계 {} · 창 {} [{}] · 양쪽 {} {} · 틈 {}'.format(
                '세로' if item['vertical'] else '가로', item['container'], classes.get(item['container'], '?')[:40],
                pointer.rect(item['first']), pointer.rect(item['second']), divider_gap(pointer, item)))
        except Exception:
            pass
    # 원인 파악용 기록: 표마다의 위치·칸 너비와, 판이 어떤 창 안에 들어 있는지(왼쪽 위 두 표).
    for r, row in enumerate(rows):
        for c, grid in enumerate(row):
            emit('note', '{} · 표 ({}, {}) {}x{}{} · 칸 {}'.format(
                label(rows, r, c), grid['x'], grid['y'], grid['w'], grid['h'], ' · 가로로 밀림' if grid.get('scrolled') else '',
                ' '.join('{}{}'.format(column['name'], column['w']) for column in grid['columns'])))
    for grid in rows[0][:2]:
        try:
            emit('note', '창 구조 · ' + ' ← '.join('{}[{}]{}'.format(handle, classes.get(handle, '?')[:30], pointer.rect(handle))
                                                 for handle in lineage(native, grid['handle'])[:8]))
        except Exception:
            pass
    before = {grid['handle']: pointer.rect(grid['handle']) for row in rows for grid in row}
    # 왼쪽 메뉴 칸을 먼저 줄여야 본문 너비가 정해지고, 그 너비를 판들이 똑같이 나눕니다.
    emit('log', '왼쪽 메뉴 칸 줄이는 중…')
    check()
    result['menu'] = collapse_menu(rows, native, pointer, emit)
    emit('log', '판 {}개 크기 맞추는 중…'.format(count))
    result['panels'] = equalize(rows, native, pointer, emit, check)
    emit('note', '판 크기 {} · 경계 {}개 중 {}회 이동 · 못 잡음 {}'.format(
        result['panels']['sizes'], result['panels']['dividers'], result['panels']['moved'], result['panels']['missed']))
    # 판을 옮겼으면 표가 움직인 만큼 칸 위치를 계산으로 따라가고(다시 읽는 시간을 아낌), 뒤에서 한 번은 다시 읽어 확인합니다.
    verify = bool(result['panels']['moved'] or result['menu']['moved'])
    if verify:
        for row in rows:
            for grid in row:
                follow(grid, before[grid['handle']], pointer.rect(grid['handle']))

    if widths is None:
        # 저장한 기준이 없으면, 판 크기를 맞춘 뒤의 왼쪽 위 판을 기준으로 삼습니다(다시 읽어 정확한 너비를 씀).
        if verify:
            rows = same_rows(rows, arrange(grids(read('MES 판 크기 확인'))))
            verify = False
        if clipped(rows[0][0]):
            raise RuntimeError('판 크기는 맞췄지만, 왼쪽 위 표의 칸이 표 밖으로 잘려 있어 기준으로 삼을 수 없습니다. '
                               '왼쪽 위 판의 칸을 모두 보이게 맞춘 뒤 [기준 저장]을 눌러 주세요.')
        widths = widths_of(rows[0][0])
    widths = OrderedDict((name, int(width)) for name, width in widths.items())
    result['widths'] = widths

    emit('log', '칸 너비 맞추는 중…')
    moved = 0
    missed = OrderedDict()
    scrolled = []
    for _ in range(COLUMN_PASSES):
        check()
        changed = 0
        missed = OrderedDict()
        scrolled = []
        for r, row in enumerate(rows):
            for c, grid in enumerate(row):
                if grid.get('scrolled'):
                    scrolled.append(label(rows, r, c))
                    continue
                done, lost = align_columns(grid, widths, pointer, emit, check)
                changed += done
                if lost:
                    missed[label(rows, r, c)] = lost
        moved += changed
        if not changed and not verify:
            break
        rows = same_rows(rows, arrange(grids(read('MES 칸 너비 확인'))))
        verify = False
    result['columns_moved'] = moved
    result['missed'] = missed
    result['scrolled'] = scrolled
    result['remaining'] = remaining(rows, widths)
    narrow = min(grid['w'] for row in rows for grid in row)
    result['overflow'] = max(0, sum(widths.values()) - narrow)
    return result


def brief(result, elapsed):
    """결과 한 줄 요약과 확인할 점. 반환: (제목, 자세한 줄들)"""
    panels = result['panels']
    menu = result.get('menu') or {'found': True, 'moved': False, 'failed': False}
    lines = []
    if not menu['found']:
        lines.append('왼쪽 메뉴 칸(파란 바)의 경계선을 찾지 못해 그대로 두었습니다.')
    elif menu['failed']:
        lines.append('왼쪽 메뉴 칸(파란 바)을 줄이지 못했습니다(경계선에서 크기 조절 모양을 확인하지 못함).')
    if panels['missed'] or panels['uneven']:
        lines.append('판 크기를 다 맞추지 못했습니다{}. 현재 표 크기: {}'.format(
            ' (경계선 {}곳을 잡지 못함)'.format(panels['missed']) if panels['missed'] else '',
            ' / '.join(' '.join('{}x{}'.format(w, h) for w, h in row) for row in panels['sizes'])))
    for place in result.get('scrolled', ()):
        lines.append('{}: 표가 가로로 밀려 있어 건너뛰었습니다. 표 아래 가로 스크롤을 왼쪽 끝으로 옮긴 뒤 다시 눌러 주세요.'.format(place))
    for place, columns in result['remaining'].items():
        if place not in result.get('scrolled', ()):
            lines.append('{}: {}'.format(place, ', '.join('{} {}→{}'.format(name, now, want) for name, now, want in columns)))
    if result.get('overflow'):
        lines.append('기준 칸 너비의 합이 판보다 {}픽셀 넓어 가로 스크롤이 생길 수 있습니다.'.format(result['overflow']))
    done = '{}판 {}개 · 경계 {}회 · 칸 {}개 조정 · {:.1f}초'.format(
        '메뉴 칸 {}→{} · '.format(menu['before'], menu['after']) if menu['moved'] else '',
        result['tables'], panels['moved'], result['columns_moved'], elapsed)
    if result.get('used_reference'):
        done += ' · {} 판의 너비를 기준으로 저장'.format(result['reference'])
    if lines:
        return 'MES 정렬 일부만 완료 · ' + done, ['맞추지 못한 곳:'] + lines
    return 'MES 정렬 완료 · ' + done, []


# ── 화면 구조 요약(읽기 전용 점검) ───────────────────────────────────────────────

def describe(report, rect=None, limit=450):
    """MES 화면 구조 요약. 칸 제목·탭·메뉴의 이름과 위치, 창 구조만 담고 행·칸의 값은 담지 않습니다.

    rect: 창 손잡이 → (왼쪽, 위, 오른쪽, 아래). 주면 창 위치도 적습니다.
    """
    items = elements(report)
    native = native_parents(report)
    classes = native_classes(report)
    by_id = {item.get('id'): item for item in items}
    children = {}
    for item in items:
        children.setdefault(item.get('parent'), []).append(item)

    def where(handle):
        if rect is None:
            return ''
        try:
            return '({},{},{},{})'.format(*rect(handle))
        except Exception:
            return '(위치 못 읽음)'

    def spot(item):
        bounds = item.get('bounds') or ()
        return '@{},{} {}x{}'.format(*bounds) if len(bounds) == 4 else '@?'

    def window(handle):
        return '창{}[{}]{}'.format(handle, classes.get(handle, '?')[:26], where(handle))

    roles = {}
    for item in items:
        roles[item.get('role')] = roles.get(item.get('role'), 0) + 1
    lines = ['창 {}개 · 항목 {}개 · 종류별 개수 {}'.format(
        len(native), len(items), ' '.join('{}:{}'.format(role, roles[role]) for role in sorted(roles, key=str)))]
    target = report.get('target') or {}
    if target.get('handle'):
        lines.append('MES ' + window(target.get('handle')))

    lines.append('[탭]')
    for item in items:
        if item.get('role') == 37:
            lines.append('  {}{} {} {}'.format(item.get('name', ''), ' (선택)' if item.get('selected') else '', spot(item),
                                           window(item.get('handle'))))

    lines.append('[표]')
    for table in items:
        if table.get('role') != 24:
            continue
        groups = children.get(table.get('id'), ())
        headers = [header for group in groups for header in children.get(group.get('id'), ()) if header.get('role') == 25]
        count = sum(1 for group in groups for row in children.get(group.get('id'), ()) if row.get('role') == 28)
        lines.append('  표 {} · 칸 {}개 · 행 {}개'.format(spot(table), len(headers), count))
        lines.append('    창 구조: ' + ' ← '.join(window(handle) for handle in lineage(native, table.get('handle'))[:9]))
        text = ['{}{}{}'.format(header.get('name', ''), spot(header), '!' if header.get('offscreen') else '') for header in headers]
        for start in range(0, len(text), 6):
            lines.append('    ' + ' | '.join(text[start:start + 6]))

    lines.append('[메뉴·탭 이름이 들어간 항목]')
    menu_windows = []
    for item in items:
        name = str(item.get('name', '')).strip()
        if not name or len(name) > 30 or item.get('role') in (25, 28, 29) or not any(word in name for word in MENU_WORDS):
            continue
        parent = by_id.get(item.get('parent'), {})
        lines.append('  {} · 종류 {}({}) {}{}{} · {} · 위 {}({})'.format(
            name, item.get('role'), item.get('type', ''), spot(item), ' 선택' if item.get('selected') else '',
            ' 숨김' if item.get('offscreen') else '', window(item.get('handle')), parent.get('name', ''), parent.get('role', '')))
        if item.get('role') != 37 and item.get('handle') not in menu_windows:
            menu_windows.append(item.get('handle'))

    for handle in menu_windows[:3]:
        lines.append('[메뉴가 든 창의 구성] ' + window(handle))
        lines.append('    창 구조: ' + ' ← '.join(window(h) for h in lineage(native, handle)[:9]))
        shown = 0
        for item in items:
            if item.get('handle') != handle or item.get('role') in (28, 29):
                continue
            lines.append('  {}{} 종류 {}({}) {}'.format('  ' * min(6, int(item.get('depth') or 0)), str(item.get('name', ''))[:30],
                                                   item.get('role'), item.get('type', ''), spot(item)))
            shown += 1
            if shown >= 70:
                lines.append('  … (줄임)')
                break
    if len(lines) > limit:
        lines = lines[:limit] + ['… (줄임: 전체 {}줄)'.format(len(lines))]
    return '\n'.join(lines)


# ── Windows 마우스 ──────────────────────────────────────────────────────────────

class Pointer:
    """마우스 포인터 이동·끌기. api는 세척완료의 WindowsClicks(user32 함수와 입력 구조체를 함께 씁니다)."""

    def __init__(self, api, sleep=time.sleep, clock=time.monotonic):
        from ctypes import wintypes
        self.api = api
        self.u = u = api.u
        self.root = api.target['handle']
        self.sleep = sleep
        self.clock = clock
        self.wintypes = wintypes
        self.trace = ''          # 마지막 모양 확인 내용(오류 기록용)
        self.presses = 0
        self.last_press = None

        class CursorInfo(ctypes.Structure):
            _fields_ = [('cbSize', wintypes.DWORD), ('flags', wintypes.DWORD),
                        ('hCursor', ctypes.c_void_p), ('ptScreenPos', wintypes.POINT)]
        self.CursorInfo = CursorInfo
        u.GetCursorInfo.argtypes = [ctypes.POINTER(CursorInfo)]
        u.GetCursorInfo.restype = wintypes.BOOL
        u.LoadCursorW.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        u.LoadCursorW.restype = ctypes.c_void_p
        u.GetDoubleClickTime.argtypes = []
        u.GetDoubleClickTime.restype = wintypes.UINT
        self.arrow = u.LoadCursorW(None, 32512)                                   # 평소 화살표
        self.busy_shapes = {u.LoadCursorW(None, 32514), u.LoadCursorW(None, 32650)}   # 모래시계류
        self.double_click = max(0.2, u.GetDoubleClickTime() / 1000.0) + 0.08
        # 마우스 좌우 버튼을 바꿔 쓰는 PC에서는 주 버튼이 오른쪽 물리 버튼입니다.
        self.press_flag, self.release_flag = (0x0008, 0x0010) if u.GetSystemMetrics(23) else (0x0002, 0x0004)
        self.home = self.position()

    def position(self):
        point = self.wintypes.POINT()
        self.u.GetCursorPos(ctypes.byref(point))
        return point.x, point.y

    def shape(self):
        """지금 보이는 포인터 모양(손잡이 값). 숨겨져 있거나 읽지 못하면 None."""
        info = self.CursorInfo()
        info.cbSize = ctypes.sizeof(info)
        if not self.u.GetCursorInfo(ctypes.byref(info)) or not info.flags & 1:
            return None
        return info.hCursor

    def window_at(self, point):
        return int(self.u.WindowFromPoint(self.wintypes.POINT(int(point[0]), int(point[1]))) or 0)

    def lineage(self, handle):
        chain = []
        while handle and handle not in chain and len(chain) < 64:
            chain.append(handle)
            handle = int(self.u.GetParent(handle) or 0)
        return chain

    def rect(self, handle):
        r = self.wintypes.RECT()
        if not self.u.GetWindowRect(handle, ctypes.byref(r)):
            raise RuntimeError('MES 창 위치를 읽지 못했습니다. 화면 구성이 바뀌었는지 확인해 주세요.')
        return r.left, r.top, r.right, r.bottom

    def check(self):
        """누르기 전 확인: 중지 요청, MES가 맨 앞인지, 사용자가 누르고 있는 키·버튼."""
        u = self.u
        if u.GetAsyncKeyState(0x78) & 0x8000:
            raise Stopped('F9 중지')
        if u.GetForegroundWindow() != self.root:
            raise RuntimeError('MES 이외의 창이 앞에 있어 중단했습니다.')
        if any(u.GetAsyncKeyState(key) & 0x8000 for key in (1, 2, 16, 17, 18, 91, 92)):
            raise RuntimeError('마우스 버튼 또는 보조 키가 눌려 있어 중단했습니다.')

    def _send(self, flags, x=0, y=0):
        item = self.api.Input()
        item.type = 0
        item.payload.mi.dx = x
        item.payload.mi.dy = y
        item.payload.mi.flags = flags
        if self.u.SendInput(1, ctypes.byref(item), ctypes.sizeof(self.api.Input)) != 1:
            raise RuntimeError('Windows가 마우스 입력을 받지 않았습니다.')

    def move(self, point):
        u = self.u
        left, top = u.GetSystemMetrics(76), u.GetSystemMetrics(77)
        width, height = u.GetSystemMetrics(78), u.GetSystemMetrics(79)
        x, y = int(point[0]), int(point[1])
        if width <= 1 or height <= 1 or not (left <= x < left + width and top <= y < top + height):
            raise RuntimeError('MES 화면이 모니터 표시 범위 밖에 있습니다.')
        # 픽셀 한가운데를 겨냥해 보내고, 그래도 1픽셀 어긋나면 3분의 1픽셀씩 고쳐 다시 보냅니다.
        unit_x, unit_y = 65536.0 / width, 65536.0 / height
        aim_x, aim_y = (x - left + 0.5) * unit_x, (y - top + 0.5) * unit_y
        for _ in range(7):
            self._send(0x8000 | 0x4000 | 0x0001, max(0, min(65535, int(aim_x))), max(0, min(65535, int(aim_y))))
            now = self.position()
            if now == (x, y):
                break
            aim_x += (x - now[0]) * unit_x * 0.34
            aim_y += (y - now[1]) * unit_y * 0.34
        return self.position()

    def settled(self, accept, seconds=HOVER_SECONDS):
        """포인터 모양이 accept를 만족한 채 두 번 연속 같을 때까지 기다립니다. 시간이 지나면 마지막 모양을 돌려줍니다."""
        deadline = self.clock() + seconds
        previous = object()
        self.sleep(0.012)
        while True:
            shape = self.shape()
            if shape == previous and accept(shape):
                return shape
            previous = shape
            if self.clock() >= deadline:
                return shape
            self.sleep(0.01)

    def resizing(self, shape, base):
        return shape is not None and shape != base and shape != self.arrow and shape not in self.busy_shapes

    def find_edge(self, neutral, points, allowed):
        """경계가 아닌 곳(neutral)에서 points로 옮겼을 때 포인터가 크기 조절 모양으로 '바뀌는' 첫 지점.

        MES가 포인터 모양을 실제로 바꾼 것을 본 뒤에만 그 지점을 돌려줍니다. 찾지 못하면 None.
        """
        self.check()
        self.move(neutral)
        base = self.settled(lambda shape: shape == self.arrow)
        seen = []
        for point in points:
            hit = self.window_at(point)
            if not allowed(hit):
                seen.append('{}:창{}'.format(point[0] if point[1] == neutral[1] else point[1], hit))
                continue
            self.move(point)
            shape = self.settled(lambda shape: self.resizing(shape, base))
            if self.resizing(shape, base):
                self.trace = '평소 {} → 경계 {}'.format(base, shape)
                return self.position()
            seen.append('{}:모양{}'.format(point[0] if point[1] == neutral[1] else point[1], shape))
        self.trace = '평소 모양 {} · 화살표 {} · 확인 {}'.format(base, self.arrow, ' '.join(seen[:9]))
        return None

    def drag(self, start, end):
        """start(이미 크기 조절 모양을 확인한 곳)를 누르고 end까지 끈 뒤 놓습니다."""
        self.check()
        if self.last_press is not None:
            (px, py), at = self.last_press
            if abs(px - start[0]) <= 16 and abs(py - start[1]) <= 16:
                wait = self.double_click - (self.clock() - at)
                if wait > 0:   # 같은 자리를 연달아 누르면 더블클릭(자동 맞춤)이 되므로 간격을 둡니다.
                    self.sleep(wait)
        if self.position() != (start[0], start[1]):
            self.move(start)
        self.last_press = ((start[0], start[1]), self.clock())
        self.presses += 1
        self._send(self.press_flag)
        try:
            dx, dy = end[0] - start[0], end[1] - start[1]
            for step in (0.34, 0.67):
                self.sleep(0.012)
                self.move((start[0] + int(dx * step), start[1] + int(dy * step)))
            self.sleep(0.012)
            self.move(end)
            self.sleep(0.03)
        finally:
            self._send(self.release_flag)   # 어떤 경우에도 버튼은 놓습니다.
        self.sleep(0.02)

    def restore(self):
        try:
            self.move(self.home)
        except Exception:
            pass
