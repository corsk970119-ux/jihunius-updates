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
# 칸 경계에서 포인터를 올려 볼 위치(경계 기준 픽셀). 현장 확인: 크기 조절 모양이 되는 범위는 표에 따라 -2~+3 또는 -5~+3.
EDGE_OFFSETS = (-1, 0, -2, 1, 2, -3, -4)
HOVER_SECONDS = 0.15         # 포인터 모양이 바뀌기를 기다리는 시간
MENU_COLLAPSED = 40          # 왼쪽 메뉴 칸(파란 바)이 이 너비 이하면 이미 줄여 둔 것으로 봅니다.
PRESET_VERSION = 1


WORK_GROUP, WORK_ITEM = '생산관리', '작업지시관리'      # 왼쪽 메뉴의 묶음 → 항목
TOOL_GROUP, TOOL_ITEM = '설비관리', '설비별공구관리'
WORK_TAB, DAILY_TAB = '작업지시관리', '생산일보관리'    # 작업지시관리 문서의 안쪽 탭
MENU_WORKING_WIDTH = 200     # 메뉴 항목을 누를 때의 메뉴 칸 너비(좁으면 글자가 세로로 접혀 항목이 화면 밖으로 밀림)

# 기본 기준: 2026-11-13 현장 PC에서 사용자가 손으로 정리해 둔 화면을 점검 프로그램으로 읽은 값.
# [기준 저장]을 누르면 그때 화면이 이 값을 대신합니다.
DEFAULT_DAILY = (('No.', 40), ('선택', 35), ('P/No.', 50), ('거래처명', 119), ('Fixture', 61), ('Size', 50),
                 ('환자명', 50), ('치식', 35), ('세척', 40), ('비고', 55), ('영점', 51))
DEFAULT_WORK_ORDER = (('선택', 35), ('지시일', 85), ('시간', 47), ('프로젝트No', 49), ('작업자', 48), ('설비코드', 54), ('설비명', 125),
                      ('특이사항1', 100), ('특이사항2', 100), ('특이사항3', 100), ('거래처명', 140), ('지역', 50), ('Fixture Name', 80),
                      ('Type', 60), ('Size', 60), ('치과명', 80), ('환자명', 80), ('치식', 40), ('stl', 40), ('납기일', 90),
                      ('배송업체', 80), ('출하일', 90), ('진행상태', 80), ('세척순서', 60), ('길이', 60))
# 정리된 표에 남아 있던 칸 전부(화면 오른쪽 밖 칸 포함). 여기에 없는 칸은 없앱니다.
DEFAULT_WORK_KEEP = tuple(name for name, _ in DEFAULT_WORK_ORDER) + (
    '직경', '각도', '순서', 'LOT-NO', '소재구분', '소재 LOT-NO', '투입스크류 LOT-NO', 'M/M No.', 'V/C No.', 'V/M No.', '표준코드',
    '수량', '잔량', '라벨출력여부', '재가공구분', '수주보류', '거래명세서입력여부', '거래명세서입력일', '가공', '공정검사', '세척', '포장',
    '완제품검사', '작지승인', '성적서승인', '작지작성구분', '완료구분')


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


def grids(report, required=REQUIRED_HEADERS):
    """화면에 보이는 표와 칸 제목 위치. required: 이 칸 이름이 모두 있는 표만(기본: 생산일보 표), ()이면 모든 표."""
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
        if not names or any(name not in names for name in required):
            continue
        if required and len(set(names)) != len(names):
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
                      'scrolled': scrolled,
                      # 판독에 나온 모든 칸 제목(표 밖 것 포함, 판독 순서 그대로): (이름, x, y, w, h)
                      'headers': [(str(header.get('name', '')),) + _box(header) for header in headers]})
    return found


def front(found, pointer):
    """실제로 화면 앞에 보이는 표만 남깁니다.

    MES는 여러 문서를 겹쳐 두는데, 뒤에 가려진 문서의 표도 화면 판독에는 그대로 나옵니다(현장 점검으로 확인).
    또 같은 표가 바깥 창 이름으로 겹쳐 읽히기도 합니다. 첫 칸 제목 자리의 맨 위 창이 그 표 자신일 때만 씁니다.
    """
    shown = []
    for grid in found:
        if not grid['columns']:
            continue
        column = grid['columns'][0]
        # 칸 제목 줄의 왼쪽 안쪽 한 점(표가 가로로 밀려 있어도 표 안에 있는 자리)
        point = (grid['x'] + min(20, grid['w'] // 2), column['y'] + column['h'] // 2)
        if pointer.window_at(point) == grid['handle']:
            shown.append(grid)
    return shown


def common_window(native, handles):
    """handles를 모두 품는 가장 안쪽 창(그 아래만 다시 읽으면 빠릅니다). 없으면 None."""
    chains = [lineage(native, handle) for handle in handles]
    if not chains or not all(chains):
        return None
    for handle in chains[0][1:]:
        if all(handle in chain for chain in chains[1:]):
            return handle
    return None


def nav_tree(report):
    """왼쪽 메뉴(navBarControl)의 묶음과 항목(위→아래).

    묶음(종류 33)의 위치는 펼쳐지면 항목들까지 포함하므로, 묶음 이름 줄은 맨 위 23픽셀(head)입니다.
    항목(종류 30)은 펼쳐진 묶음에서만 위치가 있습니다. 같은 내용이 바깥 창마다 겹쳐 읽히므로 가장 안쪽 창의 것을 씁니다.
    반환: [{'name', 'handle', 'x', 'y', 'w', 'h', 'head': (x, y), 'items': [{'name', 'x', 'y', 'w', 'h', 'shown'}]}]
    """
    items = elements(report)
    native = native_parents(report)
    children = {}
    for item in items:
        children.setdefault(item.get('parent'), []).append(item)
    best = None
    for bar in items:
        if bar.get('role') != 16:
            continue
        groups = [group for group in children.get(bar.get('id'), ()) if group.get('role') == 33
                  and any(link.get('role') == 30 for link in children.get(group.get('id'), ()))]
        if not groups:
            continue
        rank = (len(groups), len(lineage(native, bar.get('handle'))))
        if best is None or rank > best[0]:
            best = (rank, bar, groups)
    if best is None:
        return []
    tree = []
    for group in best[2]:
        x, y, w, h = _box(group)
        entries = []
        for link in children.get(group.get('id'), ()):
            if link.get('role') != 30:
                continue
            lx, ly, lw, lh = _box(link)
            entries.append({'name': str(link.get('name', '')).strip(), 'x': lx, 'y': ly, 'w': lw, 'h': lh,
                            'shown': lw > 4 and lh > 4})
        tree.append({'name': str(group.get('name', '')).strip(), 'handle': best[1].get('handle'), 'x': x, 'y': y, 'w': w, 'h': h,
                     'head': (x + w // 2, y + min(11, max(1, h // 2))), 'items': entries})
    tree.sort(key=lambda group: group['y'])
    return tree


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


def menu_divider_beside(native, pointer, menu_window):
    """왼쪽 메뉴 칸과 본문 사이의 경계선을 메뉴 창 쪽에서 찾습니다(표가 하나도 떠 있지 않을 때 씀).

    메뉴 창의 조상 창들 가운데(바깥쪽부터), MES 창 왼쪽 끝에 닿아 있고 바로 오른쪽에 틈을 두고 형제 창이 있는 것.
    """
    chain = lineage(native, menu_window)
    children = {}
    for handle, parent in native.items():
        children.setdefault(parent, []).append(handle)
    try:
        window_left = pointer.rect(pointer.root)[0]
    except Exception:
        return None
    for index in range(len(chain) - 1, 0, -1):
        container, first = chain[index], chain[index - 1]
        try:
            left, top, right, bottom = pointer.rect(first)
        except Exception:
            continue
        if left - window_left > 12:
            continue
        best = None
        for sibling in children.get(container, ()):
            if sibling == first:
                continue
            try:
                l, t, r, b = pointer.rect(sibling)
            except Exception:
                continue
            overlap = min(b, bottom) - max(t, top)      # 세로로 가장 길게 맞닿은 형제(본문 영역)를 고릅니다.
            if 1 <= l - right <= MAX_GAP and overlap >= 100 and (best is None or overlap > best[1]):
                best = (sibling, overlap)
        if best is not None:
            return {'container': container, 'first': first, 'second': best[0], 'vertical': True, 'depth': len(chain) - index}
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
        # 현장 확인: 칸의 오른쪽 끝은 '놓은 자리'로 옵니다(잡은 자리와의 차이는 유지되지 않음). 그래서 목표 끝 위치에 놓습니다.
        pointer.drag(point, (at + amount, point[1]))
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

def align(target, pointer, capture, stop, emit, report, widths=None, collapse=True):
    """판 크기를 같게 하고 칸 너비를 widths(칸 이름 → 너비)에 맞춥니다.

    widths가 없으면 왼쪽 위 표의 지금 너비를 기준으로 씁니다(result['used_reference']=True).
    """
    def check():
        if stop.is_set():
            raise Stopped('사용자 중지')

    scope = {'handle': target.get('handle')}

    def read(text):
        # 확인용 판독은 판들이 든 창 아래만 읽습니다(MES 전체를 읽으면 몇 초씩 걸림).
        return capture(dict(target, handle=scope['handle'], mode='mes_rows'), text, stop)

    def reread(rows, text):
        return same_rows(rows, arrange(front(grids(read(text)), pointer)))

    found = grids(report)
    shown = front(found, pointer)
    rows = arrange(shown)
    count = sum(len(row) for row in rows)
    if not found:
        raise RuntimeError('MES 생산일보관리 화면에서 생산일보 표를 찾지 못했습니다.')
    if not count:
        raise RuntimeError('생산일보관리 화면이 다른 화면 뒤에 가려져 있습니다. MES에서 작업지시관리 → 생산일보관리 탭을 '
                           '앞에 띄운 뒤 다시 눌러 주세요.')
    places = {(grid['x'], grid['y'], grid['w'], grid['h']) for grid in found}
    covered = len(places - {(grid['x'], grid['y'], grid['w'], grid['h']) for grid in shown})
    if covered:   # 일부만 보이면 판 크기를 잘못 나누게 되므로 아무것도 하지 않습니다.
        raise RuntimeError('생산일보 표 {}개 중 {}개가 다른 창에 가려져 있습니다. 가린 창을 치운 뒤 다시 눌러 주세요.'.format(
            len(places), covered))
    if not rows[0][0]['columns']:
        raise RuntimeError('왼쪽 위 표의 칸 제목 위치를 읽지 못했습니다.')
    result = {'tables': count, 'layout': [len(row) for row in rows], 'used_reference': widths is None,
              'reference': label(rows, 0, 0)}
    emit('note', '표 {}개 · 배치 {} · 기준 {}'.format(
        count, result['layout'], dict(widths) if widths is not None else '없음(왼쪽 위 판의 지금 너비를 씀)'))

    native = native_parents(report)
    classes = native_classes(report)
    scope['handle'] = common_window(native, [grid['handle'] for row in rows for grid in row]) or target.get('handle')
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
    check()
    if collapse:
        emit('log', '왼쪽 메뉴 칸 줄이는 중…')
        result['menu'] = collapse_menu(rows, native, pointer, emit)
    else:   # 전체 정렬에서는 메뉴 칸을 이미 줄여 두고 들어옵니다.
        result['menu'] = {'found': True, 'moved': False, 'failed': False}
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
            rows = reread(rows, 'MES 판 크기 확인')
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
        rows = reread(rows, 'MES 칸 너비 확인')
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


# ── 기준(칸 순서·너비) ──────────────────────────────────────────────────────────

def default_standard():
    return {'daily': OrderedDict(DEFAULT_DAILY),
            'work': {'order': [name for name, _ in DEFAULT_WORK_ORDER], 'widths': OrderedDict(DEFAULT_WORK_ORDER),
                     'keep': list(DEFAULT_WORK_KEEP)},
            'saved_at': '', 'custom': False}


def load_standard(path):
    """저장한 기준을 읽습니다. 파일이 없거나 읽을 수 없는 부분은 기본값을 씁니다.

    반환: {'daily': 생산일보 칸 이름→너비, 'work': {'order': [이름…], 'widths': {이름: 너비}, 'keep': [이름…]},
           'saved_at': 저장한 때, 'custom': 저장한 기준을 썼는지}
    """
    standard = default_standard()
    try:
        with open(str(path), encoding='utf-8') as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return standard
    if not isinstance(data, dict):
        return standard

    def pairs(items):
        found = OrderedDict()
        for name, width in items:
            if isinstance(name, str) and name and isinstance(width, int) and not isinstance(width, bool) and 5 <= width <= 3000:
                found[name] = width
        return found

    try:
        daily = pairs(data.get('columns') or ())
        if daily:
            standard['daily'] = daily
            standard['custom'] = True
    except (TypeError, ValueError):
        pass
    try:
        work = data.get('work') or {}
        order = pairs(work.get('order') or ())
        keep = [name for name in (work.get('keep') or ()) if isinstance(name, str) and name]
        if order and keep:
            standard['work'] = {'order': list(order), 'widths': order, 'keep': keep}
            standard['custom'] = True
    except (TypeError, ValueError, AttributeError):
        pass
    if standard['custom']:
        standard['saved_at'] = str(data.get('saved_at', ''))
    return standard


def save_standard(path, daily, work):
    """기준 저장. daily: 생산일보 칸 이름→너비. work: 작업지시관리 표의 {'order', 'widths', 'keep'}."""
    data = {'version': 2, 'columns': [[str(name), int(width)] for name, width in daily.items()],
            'work': {'order': [[str(name), int(work['widths'][name])] for name in work['order']],
                     'keep': [str(name) for name in work['keep']]},
            'saved_at': time.strftime('%Y-%m-%d %H:%M')}
    directory = os.path.dirname(str(path))
    if directory:
        os.makedirs(directory, exist_ok=True)
    temporary = str(path) + '.tmp'
    with open(temporary, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, ensure_ascii=False)
    os.replace(temporary, str(path))
    return data


# ── 화면에 실제로 보이는 칸 ─────────────────────────────────────────────────────

def chain(grid):
    """실제로 화면에 나란히 보이는 칸 제목들(왼쪽→오른쪽).

    현장 확인: 화면 밖 칸은 위치가 없고(0), 표가 가로로 밀린 뒤에는 밀려 나간 칸에 예전 위치가 남아 있기도 합니다.
    그래서 표 안에서 시작하고 서로 빈틈없이 이어지는 줄 가운데 가장 긴 것만 믿습니다.
    """
    right = grid['x'] + grid['w']
    inside = sorted((column for column in grid['columns'] if grid['x'] - 1 <= column['x'] < right), key=lambda column: column['x'])
    best, best_width = [], 0
    for start in range(len(inside)):
        run = [inside[start]]
        for column in inside[start + 1:]:
            edge = run[-1]['x'] + run[-1]['w']
            if abs(column['x'] - edge) <= 1:
                run.append(column)
            elif column['x'] > edge + 1:
                break
        width = sum(column['w'] for column in run)
        if width > best_width:
            best, best_width = run, width
    return best


def tidy(grid):
    """표가 가로로 밀려 있지 않고 칸 제목 위치를 모두 믿을 수 있는지."""
    return not grid.get('scrolled') and len(chain(grid)) == len(grid['columns'])


def whole(grid, column):
    return column['x'] >= grid['x'] and column['x'] + column['w'] <= grid['x'] + grid['w'] - 2


# ── 화면 찾아가기 ───────────────────────────────────────────────────────────────

class Navigator:
    """MES 화면 찾아가기: 왼쪽 메뉴로 문서를 앞에 띄우고, 문서 안쪽 탭을 고릅니다.

    현장 확인(2026-11-13): 메뉴 항목을 한 번 누르면 그 화면이 열리거나(이미 열려 있으면) 앞으로 옵니다. 접힌 묶음은
    이름 줄을 누르면 펼쳐집니다. 누르기 전에는 그 자리의 맨 위 창이 메뉴·탭 자신인지 확인합니다.
    """

    def __init__(self, target, pointer, capture, stop, emit):
        self.target, self.pointer, self.capture, self.stop, self.emit = target, pointer, capture, stop, emit
        self.menu_window = None      # 메뉴(navBarControl) 창
        self.document = None         # 작업지시관리 문서의 탭 창

    def check(self):
        if self.stop.is_set():
            raise Stopped('사용자 중지')

    def read(self, text, root=None):
        self.check()
        return self.capture(dict(self.target, handle=root or self.target.get('handle'), mode='mes_rows'), text, self.stop)

    def tap(self, point, handle, what):
        hit = self.pointer.window_at(point)
        if handle not in self.pointer.lineage(hit):
            raise RuntimeError('{}: 그 자리가 다른 창에 가려져 있어 누르지 않고 중단했습니다.'.format(what))
        self.pointer.click(point)

    def menu(self):
        return nav_tree(self.read('MES 메뉴', self.menu_window))

    def open_from_menu(self, group_name, item_name):
        """메뉴에서 묶음을 (접혀 있으면) 펼치고 항목을 눌러 그 화면을 열거나 앞으로 가져옵니다."""
        def find():
            group = next((one for one in self.menu() if one['name'] == group_name), None)
            if group is None:
                raise RuntimeError('MES 메뉴에서 "{}"을 찾지 못했습니다.'.format(group_name))
            entry = next((one for one in group['items'] if one['name'] == item_name), None)
            if entry is None:
                raise RuntimeError('MES 메뉴 "{}"에서 "{}"을 찾지 못했습니다.'.format(group_name, item_name))
            return group, entry
        group, entry = find()
        if not entry['shown']:
            self.tap(group['head'], group['handle'], '메뉴 ' + group_name)
            self.pointer.sleep(0.8)
            group, entry = find()
            if not entry['shown']:
                raise RuntimeError('MES 메뉴 "{}"을 눌러도 "{}"이 보이지 않습니다.'.format(group_name, item_name))
        self.emit('note', '메뉴 {} → {} @{},{} {}x{}'.format(group_name, item_name, entry['x'], entry['y'], entry['w'], entry['h']))
        self.tap((entry['x'] + entry['w'] // 2, entry['y'] + entry['h'] // 2), group['handle'], '메뉴 ' + item_name)
        self.pointer.sleep(1.6)

    def front_tab(self, report, name):
        """앞에 보이는 탭 name: (항목, 누를 자리). 없으면 None."""
        for item in elements(report):
            bounds = item.get('bounds') or ()
            if item.get('role') == 37 and str(item.get('name', '')).strip() == name and len(bounds) == 4 and bounds[2] > 4:
                point = (bounds[0] + bounds[2] // 2, bounds[1] + bounds[3] // 2)
                if item.get('handle') in self.pointer.lineage(self.pointer.window_at(point)):
                    return item, point
        return None

    def selected_tab(self, report):
        """작업지시관리 문서에서 지금 선택된 안쪽 탭 이름(앞에 보이는 것). 없으면 None."""
        for name in (WORK_TAB, DAILY_TAB, '작업지시조회'):
            found = self.front_tab(report, name)
            if found is not None and found[0].get('selected'):
                return name
        return None

    def select_tab(self, name):
        """작업지시관리 문서의 안쪽 탭을 고르고, 그 문서 아래를 읽은 결과를 돌려줍니다."""
        report = self.read('MES 탭', self.document)
        found = self.front_tab(report, name)
        if found is None and self.document:
            report = self.read('MES 탭', None)
            found = self.front_tab(report, name)
        if found is None:
            raise RuntimeError('MES에서 "{}" 탭이 앞에 보이지 않아 중단했습니다.'.format(name))
        tab, point = found
        self.document = tab.get('handle')
        if not tab.get('selected'):
            self.tap(point, tab.get('handle'), '탭 ' + name)
            self.pointer.sleep(1.2)
        return self.read(name + ' 탭', self.document)


# ── 작업지시관리 표 ─────────────────────────────────────────────────────────────

def carry(pointer, grid, source, end):
    """칸 제목 source를 끌어 end에 놓습니다. 잡을 자리와 놓을 자리가 이 표인지 먼저 확인합니다.

    현장 확인: 다른 칸 제목의 왼쪽 절반에 놓으면 그 칸 앞으로 옮겨집니다.
    """
    start = (source['x'] + source['w'] // 2, source['y'] + source['h'] // 2)
    for point in (start, end):
        if pointer.window_at(point) != grid['handle']:
            raise RuntimeError('작업지시관리 표의 칸 제목 자리가 다른 창에 가려져 있어 중단했습니다.')
    pointer.hold(start)
    try:
        pointer.sleep(0.08)
        pointer.move((start[0], start[1] + 8) if end[1] != start[1] else (start[0] + (6 if end[0] >= start[0] else -6), start[1]))
        pointer.sleep(0.06)
        pointer.move(((start[0] + end[0]) // 2, (start[1] + end[1]) // 2))
        pointer.sleep(0.15)
        pointer.move(end)
        pointer.sleep(0.35)
    finally:
        pointer.drop()
    pointer.sleep(0.4)


def arrange_work(nav, handle, standard):
    """작업지시관리 표를 기준대로 정리합니다: 기준에 없는 칸 없애기 → 칸 너비 → 칸 순서(다시 너비 확인).

    화면에 보이는 칸만 다룹니다(가로 스크롤은 하지 않음). 칸을 없애고 줄이면 뒤 칸들이 화면 안으로 들어옵니다.
    """
    pointer, emit = nav.pointer, nav.emit
    order, widths, keep = list(standard['order']), standard['widths'], set(standard['keep'])
    result = {'removed': [], 'stuck': [], 'moved': 0, 'resized': 0, 'blocked': None, 'scrolled': False, 'remaining': []}
    box = {}

    def look(text):
        report = nav.read(text, handle)
        found = [grid for grid in front(grids(report, required=()), pointer) if grid['handle'] == handle]
        if not found:
            raise RuntimeError('작업지시관리 표가 화면 앞에서 사라져 중단했습니다.')
        box['grid'] = found[0]
        return found[0]

    def home():
        """표가 가로로 밀려 있으면, 칸 제목을 끈 채 왼쪽 끝에 두어 처음 자리로 되돌립니다(Esc로 끌기는 취소)."""
        for _ in range(3):
            grid = box['grid']
            if tidy(grid):
                return True
            inside = [column for column in chain(grid) if whole(grid, column) and column['x'] > grid['x'] + 40]
            if not inside:
                return False
            source = inside[len(inside) // 2]
            start = (source['x'] + source['w'] // 2, source['y'] + source['h'] // 2)
            if pointer.window_at(start) != grid['handle']:
                return False
            pointer.hold(start)
            try:
                pointer.sleep(0.08)
                pointer.move((start[0] - 6, start[1]))
                pointer.sleep(0.06)
                pointer.move((grid['x'] + 30, start[1]))     # 표의 왼쪽 끝(맨 앞 번호 칸 위)
                pointer.sleep(2.5)
                pointer.key(0x1B)
                pointer.sleep(0.2)
            finally:
                pointer.drop()
            pointer.sleep(0.4)
            look('가로 스크롤 되돌린 뒤')
        return tidy(box['grid'])

    def reorder():
        moves = 0
        for _ in range(60):
            nav.check()
            grid = box['grid']
            visible = chain(grid)
            names = [column['name'] for column in visible]
            present = set(header[0] for header in grid['headers'])
            wanted = [name for name in order if name in present]
            index = next((i for i, name in enumerate(wanted) if i < len(names) and names[i] != name), None)
            if index is None:
                return moves, None
            name = wanted[index]
            source = next((column for column in visible if column['name'] == name and whole(grid, column)), None)
            if source is None:
                return moves, name
            target = visible[index]
            carry(pointer, grid, source, (target['x'] + max(3, target['w'] // 4), target['y'] + target['h'] // 2))
            moves += 1
            now = [column['name'] for column in chain(look('칸 옮긴 뒤'))]
            emit('note', '칸 옮김 · {} → {}번째 · {}'.format(name, index + 1, '됨' if index < len(now) and now[index] == name else '안 됨'))
            if index >= len(now) or now[index] != name:
                return moves, name
        return moves, None

    look('작업지시관리 표')
    if not home():
        result['scrolled'] = True
        return result

    emit('log', '작업지시관리 표: 기준에 없는 칸 없애는 중…')
    for _ in range(40):
        nav.check()
        grid = box['grid']
        extra = next((column for column in chain(grid) if column['name'] and column['name'] not in keep
                      and column['name'] not in result['stuck'] and whole(grid, column)), None)
        if extra is None:
            break
        # 칸 제목을 표 안쪽(아래)으로 끌어다 놓으면 그 칸이 없어집니다.
        carry(pointer, grid, extra, (extra['x'] + extra['w'] // 2, extra['y'] + extra['h'] // 2 + 140))
        gone = all(header[0] != extra['name'] for header in look('칸 없앤 뒤')['headers'])
        result['removed' if gone else 'stuck'].append(extra['name'])
        emit('note', '칸 없애기 · {} · {}'.format(extra['name'], '없어짐' if gone else '그대로 있음'))

    emit('log', '작업지시관리 표: 칸 너비·순서 맞추는 중…')
    for _ in range(3):
        nav.check()
        grid = box['grid']
        done, _ = align_columns(dict(grid, columns=chain(grid)), widths, pointer, emit, nav.check)
        if done:
            result['resized'] += done
            look('칸 너비 확인')
        moved, blocked = reorder()
        result['moved'] += moved
        result['blocked'] = blocked
        if not done and not moved:
            break
    grid = box['grid']
    result['remaining'] = [(column['name'], column['w'], int(widths[column['name']])) for column in chain(grid)
                           if column['name'] in widths and whole(grid, column) and abs(int(widths[column['name']]) - column['w']) > TOLERANCE]
    return result


# ── 전체 정렬 ───────────────────────────────────────────────────────────────────

def menu_bar(nav, first):
    """왼쪽 메뉴 칸의 경계선과 너비 재기·끌기 함수."""
    pointer = nav.pointer
    tree = nav_tree(first)
    if not tree:
        raise RuntimeError('MES 왼쪽 메뉴를 읽지 못했습니다. MES 화면을 확인해 주세요.')
    nav.menu_window = tree[0]['handle']
    item = menu_divider_beside(native_parents(first), pointer, nav.menu_window)
    if item is None:
        raise RuntimeError('MES 왼쪽 메뉴 칸의 경계선을 찾지 못했습니다.')

    def width():
        left, _, right, _ = pointer.rect(item['first'])
        return right - left

    def pull(amount):
        if not drag_divider(pointer, item, amount, nav.emit):
            raise RuntimeError('MES 왼쪽 메뉴 칸의 경계선에서 크기 조절 모양을 확인하지 못해 중단했습니다.')
        settle(pointer, item)
        pointer.sleep(0.3)

    def collapse():
        if width() > MENU_COLLAPSED:
            pull(pointer.rect(item['first'])[0] - divider_gap(pointer, item)[0] + 1)

    return width, pull, collapse


def align_all(target, pointer, capture, stop, emit, standard):
    """MES 정렬 전체: 메뉴로 작업지시관리·설비별공구관리 열기 → 메뉴 칸 줄이기 → 작업지시관리 표 → 생산일보관리."""
    nav = Navigator(target, pointer, capture, stop, emit)
    result = {'opened': [], 'menu': {}, 'work': None, 'daily': None}
    emit('log', 'MES 화면 읽는 중…')
    first = nav.read('MES 구조')
    width, pull, collapse = menu_bar(nav, first)
    result['menu']['before'] = width()

    names = set(str(item.get('name', '')).strip() for item in elements(first) if item.get('role') == 37)
    work_open, tool_open = WORK_TAB in names and DAILY_TAB in names, TOOL_ITEM in names
    shown = work_open and nav.front_tab(first, WORK_TAB) is not None
    emit('note', '작업지시관리 {} · 설비별공구관리 {} · 메뉴 칸 {}'.format(
        ('앞에 있음' if shown else '뒤에 있음') if work_open else '안 열림', '열림' if tool_open else '안 열림', width()))
    if not (work_open and tool_open and shown):
        emit('log', '메뉴에서 화면 여는 중…')
        if width() < MENU_WORKING_WIDTH - 20:
            pull(MENU_WORKING_WIDTH - width())
        if not work_open:
            nav.open_from_menu(WORK_GROUP, WORK_ITEM)
            result['opened'].append(WORK_ITEM)
        if not tool_open:
            nav.open_from_menu(TOOL_GROUP, TOOL_ITEM)
            result['opened'].append(TOOL_ITEM)
        if not tool_open or (work_open and not shown):     # 작업지시관리를 다시 앞으로
            nav.open_from_menu(WORK_GROUP, WORK_ITEM)
        if nav.front_tab(nav.read('MES 문서 확인'), WORK_TAB) is None:
            raise RuntimeError('메뉴에서 작업지시관리를 눌렀지만 그 화면이 앞에 보이지 않아 중단했습니다.')

    emit('log', '왼쪽 메뉴 칸 줄이는 중…')
    collapse()
    result['menu']['after'] = width()

    emit('log', '작업지시관리 표 읽는 중…')
    tables = front(grids(nav.select_tab(WORK_TAB), required=()), pointer)
    if not tables:
        raise RuntimeError('작업지시관리 탭에서 표를 찾지 못해 중단했습니다.')
    result['work'] = arrange_work(nav, max(tables, key=lambda grid: len(grid['headers']))['handle'], standard['work'])

    emit('log', '생산일보관리 읽는 중…')
    result['daily'] = align(target, pointer, capture, stop, emit, nav.select_tab(DAILY_TAB), widths=standard['daily'], collapse=False)
    return result


def capture_standard(target, pointer, capture, stop, emit):
    """지금 화면(손으로 정리해 둔 상태)을 기준으로 읽습니다. 탭만 누르고 표는 건드리지 않습니다.

    반환: {'daily': 생산일보 왼쪽 위 판의 칸 이름→너비, 'work': {'order', 'widths', 'keep'}}
    """
    nav = Navigator(target, pointer, capture, stop, emit)
    first = nav.read('MES 구조')
    if nav.front_tab(first, WORK_TAB) is None:
        raise RuntimeError('작업지시관리 화면이 앞에 보이지 않습니다. MES에서 작업지시관리를 띄운 뒤 다시 눌러 주세요.')
    chosen = nav.selected_tab(first)
    tables = front(grids(nav.select_tab(WORK_TAB), required=()), pointer)
    if not tables:
        raise RuntimeError('작업지시관리 탭에서 표를 찾지 못했습니다.')
    grid = max(tables, key=lambda one: len(one['headers']))
    if not tidy(grid):
        raise RuntimeError('작업지시관리 표가 가로로 밀려 있어 칸 순서를 정확히 읽을 수 없습니다. '
                           '표 아래 가로 스크롤을 왼쪽 끝으로 옮긴 뒤 다시 눌러 주세요.')
    visible = [column for column in chain(grid) if column['name']]
    if visible and not whole(grid, visible[-1]):     # 오른쪽 끝에서 잘린 칸은 너비를 믿을 수 없습니다.
        visible = visible[:-1]
    names = [column['name'] for column in visible]
    if len(set(names)) != len(names) or not names:
        raise RuntimeError('작업지시관리 표의 칸 이름을 구분할 수 없어 기준으로 저장하지 못했습니다.')
    work = {'order': names, 'widths': OrderedDict((column['name'], column['w']) for column in visible),
            'keep': [header[0] for header in grid['headers'] if header[0]]}
    rows = arrange(front(grids(nav.select_tab(DAILY_TAB)), pointer))
    if not rows or not rows[0][0]['columns']:
        raise RuntimeError('생산일보관리에서 왼쪽 위 표의 칸 제목을 읽지 못했습니다.')
    if clipped(rows[0][0]):
        raise RuntimeError('생산일보관리 왼쪽 위 표의 칸이 표 밖으로 잘려 있어 너비를 정확히 읽을 수 없습니다. '
                           '왼쪽 위 판의 칸을 모두 보이게 맞춘 뒤 다시 저장해 주세요.')
    daily = widths_of(rows[0][0])
    if chosen and chosen != DAILY_TAB:
        nav.select_tab(chosen)
    return {'daily': daily, 'work': work}


def brief_all(result, elapsed):
    """전체 정렬 결과 요약. 반환: (제목, 자세한 줄들)"""
    work, daily = result['work'], result['daily']
    lines = []
    if work['scrolled']:
        lines.append('작업지시관리 표가 가로로 밀려 있어 정리하지 못했습니다. 표 아래 가로 스크롤을 왼쪽 끝으로 옮긴 뒤 다시 눌러 주세요.')
    if work['stuck']:
        lines.append('작업지시관리: 없애지 못한 칸 — ' + ', '.join(work['stuck']))
    if work['blocked']:
        lines.append('작업지시관리: "{}" 칸을 제자리로 옮기지 못했습니다(화면에 다 보이지 않거나 옮겨지지 않음).'.format(work['blocked']))
    if work['remaining']:
        lines.append('작업지시관리: 기준과 다른 칸 너비 — ' + ', '.join('{} {}→{}'.format(name, now, want) for name, now, want in work['remaining']))
    lines.extend(line for line in brief(daily, elapsed)[1] if line != '맞추지 못한 곳:')
    done = '{}작업지시관리 칸 없앰 {}·옮김 {}·너비 {} · 생산일보 판 경계 {}회·칸 {}개 · {:.1f}초'.format(
        '{} 열기 · '.format('·'.join(result['opened'])) if result['opened'] else '',
        len(work['removed']), work['moved'], work['resized'], daily['panels']['moved'], daily['columns_moved'], elapsed)
    if lines:
        return 'MES 정렬 일부만 완료 · ' + done, ['맞추지 못한 곳:'] + lines
    return 'MES 정렬 완료 · ' + done, []


# ── 화면 구조 요약(읽기 전용 점검) ───────────────────────────────────────────────

def describe(report, rect=None, at=None, limit=260):
    """MES 화면 구조 요약. 칸 제목·탭·메뉴의 이름과 위치만 담고 행·칸의 값은 담지 않습니다.

    rect: 창 손잡이 → (왼쪽, 위, 오른쪽, 아래). at: (x, y) → 그 자리 맨 위 창. 주면 창 위치와 '앞에 보임/가려짐'을 적습니다.
    """
    items = elements(report)
    native = native_parents(report)
    children = {}
    for item in items:
        children.setdefault(item.get('parent'), []).append(item)

    def spot(item):
        bounds = item.get('bounds') or ()
        return '@{},{} {}x{}'.format(*bounds) if len(bounds) == 4 else '@?'

    lines = ['창 {}개 · 항목 {}개'.format(len(native), len(items))]
    lines.append('[탭] 이름@위치')
    for item in items:
        if item.get('role') == 37:
            lines.append('  {}{} {} · 창{}'.format(item.get('name', ''), ' (선택)' if item.get('selected') else '', spot(item), item.get('handle')))

    lines.append('[표] 칸 이름과 너비(판독 순서. ▷ 화면 밖이라 위치 없음, ◁ 왼쪽으로 밀려 있음). 겹쳐 읽힌 표는 한 번만 적음')
    kept = {}
    for grid in grids(report, required=()):
        key = (grid['x'], grid['y'], grid['w'], grid['h'], tuple(header[0] for header in grid['headers']))
        depth = len(lineage(native, grid['handle']))
        if key not in kept or depth > kept[key][0]:
            kept[key] = (depth, grid)
    for key in sorted(kept, key=lambda item: (item[1], item[0])):
        grid = kept[key][1]
        seen = ''
        if at is not None and grid['columns']:
            first = grid['columns'][0]
            seen = ' · 앞에 보임' if at((grid['x'] + min(20, grid['w'] // 2), first['y'] + first['h'] // 2)) == grid['handle'] else ' · 가려짐'
        lines.append('  표 @{},{} {}x{} · 칸 {}개(화면에 이어져 보이는 것 {}개){} · 창{}'.format(
            grid['x'], grid['y'], grid['w'], grid['h'], len(grid['headers']), len(chain(grid)), seen, grid['handle']))
        right = grid['x'] + grid['w']
        text = ['{}{} {}'.format('▷' if header[3] <= 0 or header[1] >= right else ('◁' if header[1] < grid['x'] - 1 else ''),
                                  header[0], header[3]) for header in grid['headers']]
        for start in range(0, len(text), 10):
            lines.append('    ' + ' | '.join(text[start:start + 10]))
        if rect is not None:
            links = []
            for handle in lineage(native, grid['handle'])[:8]:
                try:
                    links.append('{}({},{},{},{})'.format(handle, *rect(handle)))
                except Exception:
                    links.append('{}(위치 못 읽음)'.format(handle))
            lines.append('    창 구조: ' + ' ← '.join(links))

    tree = nav_tree(report)
    lines.append('[메뉴] 묶음 {}개{}'.format(len(tree), ' · 창{}'.format(tree[0]['handle']) if tree else ''))
    if tree:
        lines.append('  묶음: ' + ' | '.join('{}@{},{} {}x{}'.format(group['name'], group['x'], group['y'], group['w'], group['h']) for group in tree))
        for group in tree:
            shown = [entry for entry in group['items'] if entry['shown']]
            if shown:
                lines.append('  펼쳐진 묶음 "{}"의 항목: '.format(group['name'])
                             + ' | '.join('{}@{},{} {}x{}'.format(entry['name'], entry['x'], entry['y'], entry['w'], entry['h']) for entry in shown))
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
        self.holding = False     # 지금 버튼을 누르고 있는지

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

    def _send(self, flags, x=0, y=0, data=0):
        item = self.api.Input()
        item.type = 0
        item.payload.mi.dx = x
        item.payload.mi.dy = y
        item.payload.mi.data = data & 0xffffffff
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

    def hold(self, start):
        """start를 누른 채로 둡니다. 반드시 drop()으로 놓습니다."""
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
        self.holding = True
        self._send(self.press_flag)

    def drop(self):
        """누르고 있던 버튼을 놓습니다(누르고 있지 않아도 놓기 입력을 보내 안전하게 둡니다)."""
        self.holding = False
        self._send(self.release_flag)

    def drag(self, start, end):
        """start(이미 크기 조절 모양을 확인한 곳)를 누르고 end까지 끈 뒤 놓습니다."""
        self.hold(start)
        try:
            dx, dy = end[0] - start[0], end[1] - start[1]
            for step in (0.34, 0.67):
                self.sleep(0.012)
                self.move((start[0] + int(dx * step), start[1] + int(dy * step)))
            self.sleep(0.012)
            self.move(end)
            self.sleep(0.03)
        finally:
            self.drop()   # 어떤 경우에도 버튼은 놓습니다.
        self.sleep(0.02)

    def click(self, point):
        """point를 한 번 누릅니다(움직이지 않고 눌렀다 놓음)."""
        self.hold(point)
        try:
            self.sleep(0.03)
        finally:
            self.drop()
        self.sleep(0.02)

    def double_click(self, point):
        """point를 빠르게 두 번 누릅니다(일부러 하는 더블클릭)."""
        self.check()
        if self.position() != (point[0], point[1]):
            self.move(point)
        try:
            for _ in range(2):
                self.presses += 1
                self.holding = True
                self._send(self.press_flag)
                self.sleep(0.03)
                self.drop()
                self.sleep(0.07)
        finally:
            if self.holding:
                self.drop()
        self.last_press = ((point[0], point[1]), self.clock())

    def key(self, code, down=True, up=True):
        """키 입력(예: Esc 0x1B, Shift 0x10)."""
        u = self.u
        u.keybd_event.argtypes = [self.wintypes.BYTE, self.wintypes.BYTE, self.wintypes.DWORD, ctypes.c_size_t]
        u.keybd_event.restype = None
        if down:
            u.keybd_event(code, 0, 0, 0)
            self.sleep(0.02)
        if up:
            u.keybd_event(code, 0, 2, 0)
            self.sleep(0.02)

    def wheel(self, notches, horizontal=False):
        """포인터 아래에서 휠을 굴립니다(+: 위·오른쪽)."""
        self._send(0x1000 if horizontal else 0x0800, data=int(notches) * 120)

    def restore(self):
        try:
            self.move(self.home)
        except Exception:
            pass
