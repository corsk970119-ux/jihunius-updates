"""저장 위치 옮기기 — 지후니우스의 공유 자료를 개인 폴더에서 생산공유폴더로 옮기는 프로그램.

    이 파일을 '저장위치옮기기.pyw'로 복사해 회사 PC 한 대에서 더블클릭합니다(Python 3.8 이상, 추가 설치 없음).

순서
1. [점검]   예전 위치는 읽기만 하고(이름·개수·크기·날짜, 내용은 적지 않음), 새 위치에는 시험 폴더를 만들어
            쓰기·이름 바꾸기·잠금을 해 본 뒤 지웁니다.
2. [옮기기] 모든 PC에서 지후니우스를 끈 뒤에 누릅니다.
            복사 → 파일마다 대조 → 복사하는 동안 바뀐 것이 없는지 확인 → 예전 자료를 개인 폴더 안의
            '지후니우스 예전 자료 (옮김 완료 - 지워도 됨)' 폴더로 모음 → 새 위치에 '옮김 완료' 표시.
            중간에 실패하면 예전 위치를 원래대로 되돌리고 멈춥니다.
3. [예전 자료 지우기] 새 위치에서 잘 되는 것을 확인한 뒤에 누릅니다. 옮긴 목록과 대조가 맞는 파일만 지웁니다.

개인 폴더의 다른 파일(엑셀·도면 등)은 읽지도 건드리지도 않습니다.
새 위치의 폴더 이름과 '옮김 완료' 표시는 src/storage_location.py와 같아야 합니다(tests/test_storage_move.py가 확인).
제품(지후니우스)에는 들어가지 않는 별도 프로그램입니다.
"""
import ctypes
import hashlib
import json
import os
import platform
import re
import socket
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

PROBE_VERSION = '3'
REQUIRED_APP_VERSION = '2026.11.17.2'   # 새 위치를 아는 첫 지후니우스 버전
OLD_PARENT = r'\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈'
NEW_ROOT = r'\\srvc5352374b\생산공유폴더\지후니우스 저장'
HANDOVER_NAME = '지후니우스_인수인계'
WASH_NAME = '세척일보'
MARKER_NAME = '저장위치_옮김완료.json'
READY_NAME = '준비된 PC'
NEW_NAMES = {'wash': '세척일보', 'handover': '인수인계', 'protrusion': '돌출량 표', 'special': '특수 돌출량',
             'errors': '오류기록', 'material': '소재 사용량 조사', 'wash_run': '세척완료'}
RECORD_NAME = '옮기기 기록'
JOURNAL_NAME = '진행중.json'
MANIFEST_NAME = '옮긴 파일 목록.json'
SETASIDE_NAME = '지후니우스 예전 자료 (옮김 완료 - 지워도 됨)'
LEFTOVER_NAME = '개인 폴더 바로 아래 있던 예전 세척일보'
OTHER_NAME = '예전 인수인계 폴더의 그 밖의 파일'
TOMBSTONES = (HANDOVER_NAME, WASH_NAME)
TOMBSTONE_TEXT = ('지후니우스 자료는 생산공유폴더의 "지후니우스 저장" 폴더로 옮겼습니다.\r\n'
                  '이 파일은 업데이트하지 않은 예전 지후니우스가 여기에 새 자료를 만들지 못하게 막는 표시입니다.\r\n'
                  '모든 PC를 업데이트한 뒤에는 지워도 됩니다.\r\n')
NOTE = re.compile(r'[0-9a-f]{32}\.json')
DAY = re.compile(r'\d{4}-\d{2}-\d{2}\.json')
WALK_LIMIT = 30000          # 한 폴더에서 세는 항목 수 한도
WALK_SECONDS = 25.0         # 한 폴더를 세는 시간 한도


def size_text(count):
    if count < 1024:
        return '{}B'.format(count)
    if count < 1024 * 1024:
        return '{:.1f}KB'.format(count / 1024)
    return '{:.1f}MB'.format(count / 1024 / 1024)


def when(seconds):
    return datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M')


def explain(error):
    code = getattr(error, 'winerror', None)
    text = '{}: {}'.format(type(error).__name__, error)
    return ('[WinError {}] '.format(code) if code is not None and 'WinError' not in text else '') + text[:300]


def file_line(path):
    """이름 · 크기 · 수정 시각. 없으면 '없음'."""
    try:
        info = path.stat()
    except FileNotFoundError:
        return '{}: 없음'.format(path.name)
    except OSError as error:
        return '{}: 확인 실패 · {}'.format(path.name, explain(error))
    return '{}: {} · {}'.format(path.name, size_text(info.st_size), when(info.st_mtime))


def tree_total(folder):
    """(파일 수, 전체 크기, 가장 최근 수정 시각, 다 셌는지). 내용은 읽지 않습니다."""
    files = total = 0
    newest = 0.0
    complete = True
    deadline = time.monotonic() + WALK_SECONDS
    stack = [str(folder)]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    if files >= WALK_LIMIT or time.monotonic() > deadline:
                        return files, total, newest, False
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                        else:
                            info = entry.stat(follow_symlinks=False)
                            files += 1
                            total += info.st_size
                            newest = max(newest, info.st_mtime)
                    except OSError:
                        complete = False
        except OSError:
            complete = False
    return files, total, newest, complete


def tree_line(folder, label=None):
    label = label or folder.name
    if not folder.is_dir():
        return '{}\\: 없음'.format(label), 0
    files, total, newest, complete = tree_total(folder)
    line = '{}\\: 파일 {}개 · {}'.format(label, files, size_text(total))
    if newest:
        line += ' · 최근 수정 {}'.format(when(newest))
    if not complete:
        line += ' · (다 세지 못함)'
    return line, total


def read_json(path, limit=8 * 1024 * 1024):
    with path.open('rb') as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError('파일이 너무 큽니다')
    return json.loads(data.decode('utf-8'))


# ── 예전 위치: 인수인계 폴더(인수인계·돌출량·특수 돌출량·오류기록·소재 연결) ─────────────

def inventory_handover(folder):
    lines = ['[예전 위치] {}'.format(folder)]
    total = 0
    try:
        with os.scandir(str(folder)) as scan:
            entries = sorted(scan, key=lambda entry: entry.name)
    except OSError as error:
        return lines + ['  열 수 없음 · ' + explain(error)], 0
    notes = [entry for entry in entries if entry.is_file() and NOTE.fullmatch(entry.name)]
    live = deleted = unreadable = 0
    note_size = 0
    newest = 0.0
    deadline = time.monotonic() + WALK_SECONDS
    counted = True
    for entry in notes:
        try:
            info = entry.stat()
            note_size += info.st_size
            newest = max(newest, info.st_mtime)
            if time.monotonic() > deadline:
                counted = False
                continue
            value = read_json(Path(entry.path), 1024 * 1024)
            if isinstance(value, dict) and value.get('deleted') is True:
                deleted += 1
            elif isinstance(value, dict) and value.get('deleted') is False:
                live += 1
            else:
                unreadable += 1
        except (OSError, ValueError):
            unreadable += 1
    total += note_size
    line = '  인수인계 메모 파일 {}개 · {}'.format(len(notes), size_text(note_size))
    if notes:
        line += ' · 보이는 메모 {} · 삭제 표시 {} · 읽지 못함 {}'.format(live, deleted, unreadable)
        line += ' · 최근 수정 {}'.format(when(newest))
        if not counted:
            line += ' · (일부만 확인)'
    lines.append(line)

    for name, describe in (('돌출량_현황표.json', lambda v: '형식 {} · 고친 횟수 {} · 항목 {}개'.format(
                                v.get('version'), v.get('revision'), len(v.get('values', {})))),
                           ('특수_돌출량.json', lambda v: '형식 {} · 고친 횟수 {} · 줄 {}개'.format(
                               v.get('schema'), v.get('revision'), len(v.get('rows', []))))):
        path = folder / name
        line = '  ' + file_line(path)
        if path.is_file():
            try:
                total += path.stat().st_size
                line += ' · ' + describe(read_json(path))
            except (OSError, ValueError, AttributeError, TypeError) as error:
                line += ' · 읽지 못함 · ' + explain(error)
        lines.append(line)
    lines.append('  ' + file_line(folder / '세척완료_실행중.json') + ' (세척완료 실행 중에만 있음)')

    errors = folder / '오류기록'
    if errors.is_dir():
        line, size = tree_line(errors, '오류기록')
        total += size
        try:
            pcs = len([p for p in errors.iterdir() if re.fullmatch(r'pc-[0-9a-f]{32}\.json', p.name)])
        except OSError:
            pcs = '?'
        lines.append('  {} · PC 파일 {}개 · 세대 파일(generation.json) {}'.format(
            line, pcs, '있음' if (errors / 'generation.json').is_file() else '없음'))
    else:
        lines.append('  오류기록\\: 없음')

    material = folder / '소재재고조사'
    if material.is_dir():
        owner = material / 'owner.json'
        lines.append('  소재재고조사\\: 연결 파일(owner.json) {} (내용은 읽지 않음)'.format(
            '있음 · ' + file_line(owner).split(': ', 1)[1] if owner.is_file() else '없음'))
        try:
            total += owner.stat().st_size
        except OSError:
            pass
    else:
        lines.append('  소재재고조사\\: 없음')

    known = {'돌출량_현황표.json', '특수_돌출량.json', '세척완료_실행중.json', '오류기록', '소재재고조사'}
    others = [entry for entry in entries if entry.name not in known and not NOTE.fullmatch(entry.name)]
    if others:
        lines.append('  그 밖의 항목 {}개:'.format(len(others)))
        for entry in others[:40]:
            try:
                if entry.is_dir():
                    line, _size = tree_line(Path(entry.path))
                    lines.append('    ' + line)
                else:
                    lines.append('    ' + file_line(Path(entry.path)))
            except OSError as error:
                lines.append('    {}: 확인 실패 · {}'.format(entry.name, explain(error)))
        if len(others) > 40:
            lines.append('    … 외 {}개'.format(len(others) - 40))
    return lines, total


# ── 예전 위치: 세척일보 ─────────────────────────────────────────────────────────

def wash_config_folder():
    """이 PC의 세척일보가 기억하는 저장 폴더(없으면 None)."""
    path = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'WashLog' / 'settings.json'
    try:
        value = read_json(path, 1024 * 1024)
    except (OSError, ValueError):
        return None
    folder = value.get('folder') if isinstance(value, dict) else None
    return folder if isinstance(folder, str) and folder.strip() else None


def inventory_wash(folder, label):
    lines = ['[세척일보 후보: {}] {}'.format(label, folder)]
    total = 0
    if not folder.is_dir():
        return lines + ['  폴더 없음'], 0, None
    identity = None
    meta = folder / '저장정보.json'
    if meta.is_file():
        try:
            value = read_json(meta, 1024 * 1024)
            identity = str(value.get('id', ''))[:8] or None
            lines.append('  저장정보.json: 있음 · 식별 번호 앞 8자 {} · 형식 {}'.format(identity, value.get('format')))
            total += meta.stat().st_size
        except (OSError, ValueError, AttributeError) as error:
            lines.append('  저장정보.json: 읽지 못함 · ' + explain(error))
    else:
        lines.append('  저장정보.json: 없음 → 세척일보 저장 폴더가 아님')
    for name in ('공구대.json', '부서메모.json', 'wash_log_data.json'):
        lines.append('  ' + file_line(folder / name))
        try:
            total += (folder / name).stat().st_size
        except OSError:
            pass
    days_root = folder / '세척일보'
    days = []
    if days_root.is_dir():
        try:
            days = sorted(path for path in days_root.glob('*년/*월/*.json') if DAY.fullmatch(path.name))
        except OSError as error:
            lines.append('  날짜별 일보: 확인 실패 · ' + explain(error))
    if days:
        size = 0
        newest = 0.0
        for path in days:
            try:
                info = path.stat()
                size += info.st_size
                newest = max(newest, info.st_mtime)
            except OSError:
                pass
        total += size
        lines.append('  날짜별 일보 {}일치 · {} · {} ~ {} · 최근 수정 {}'.format(
            len(days), size_text(size), days[0].stem, days[-1].stem, when(newest) if newest else '?'))
    else:
        lines.append('  날짜별 일보: 없음')
    for name in ('백업', '이전통합백업'):
        line, size = tree_line(folder / name)
        total += size
        lines.append('  ' + line)
    lines.append('  합계 약 ' + size_text(total))
    return lines, total, identity


def same_folder(first, second):
    return os.path.normcase(os.path.normpath(str(first))) == os.path.normcase(os.path.normpath(str(second)))


# ── 새 위치: 써 보고 지우기 ─────────────────────────────────────────────────────

def exclusive_handle_check(path):
    """인수인계·돌출량이 쓰는 잠금: 공유 없이 연 손잡이가 두 번째 열기를 막는지."""
    if os.name == 'nt':
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        create = kernel.CreateFileW
        create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                           wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        create.restype = wintypes.HANDLE
        close = kernel.CloseHandle
        close.argtypes = [wintypes.HANDLE]
        invalid = ctypes.c_void_p(-1).value
        first = create(str(path), 0xC0000000, 0, None, 4, 0x80, None)
        if first == invalid:
            return '확인 실패 · 잠금 파일을 열지 못함 [WinError {}]'.format(ctypes.get_last_error())
        try:
            second = create(str(path), 0xC0000000, 0, None, 4, 0x80, None)
            if second != invalid:
                close(second)
                return '안 됨 · 두 번째 열기가 막히지 않음'
            code = ctypes.get_last_error()
            return '됨' if code in (32, 33) else '확인 필요 · 두 번째 열기가 [WinError {}]로 실패'.format(code)
        finally:
            close(first)
    import fcntl
    with open(str(path), 'a+b') as first, open(str(path), 'a+b') as second:
        fcntl.flock(first.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            fcntl.flock(second.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return '됨'
        return '안 됨 · 두 번째 잠금이 막히지 않음'


def range_lock_check(path):
    """세척일보·특수 돌출량·오류기록·소재 연결이 쓰는 잠금: 파일 한 바이트 잠금."""
    with open(str(path), 'a+b') as first, open(str(path), 'a+b') as second:
        first.seek(0, 2)
        if not first.tell():
            first.write(b'0')
            first.flush()
        first.seek(0)
        second.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(first.fileno(), msvcrt.LK_NBLCK, 1)
            try:
                try:
                    msvcrt.locking(second.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError:
                    return '됨'
                second.seek(0)
                msvcrt.locking(second.fileno(), msvcrt.LK_UNLCK, 1)
                return '안 됨 · 두 번째 잠금이 막히지 않음'
            finally:
                first.seek(0)
                msvcrt.locking(first.fileno(), msvcrt.LK_UNLCK, 1)
        import fcntl
        fcntl.flock(first.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            fcntl.flock(second.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return '됨'
        return '안 됨 · 두 번째 잠금이 막히지 않음'


def timed(action):
    started = time.monotonic()
    action()
    return (time.monotonic() - started) * 1000


def latency(path, rounds=15):
    """작은 파일 하나를 여러 번 확인·읽는 데 걸리는 시간(밀리초 평균, 최대)."""
    samples = []
    for _ in range(rounds):
        started = time.monotonic()
        path.stat()
        with path.open('rb') as stream:
            stream.read(4096)
        samples.append((time.monotonic() - started) * 1000)
    return sum(samples) / len(samples), max(samples)


def check_new(root, token=None):
    lines = ['[새 위치] {}'.format(root)]
    if not root.is_dir():
        return lines + ['  폴더가 없거나 이 PC에서 열 수 없습니다. 경로와 접근 권한을 확인해 주세요.'], False
    try:
        with os.scandir(str(root)) as entries:
            names = sorted(entry.name for entry in entries)
        lines.append('  지금 들어 있는 항목 {}개{}'.format(
            len(names), ': ' + ', '.join(names[:20]) + (' …' if len(names) > 20 else '') if names else ''))
    except OSError as error:
        lines.append('  목록 읽기 실패 · ' + explain(error))
    try:
        import shutil
        lines.append('  남은 공간 약 {:.1f}GB'.format(shutil.disk_usage(str(root)).free / 1024 ** 3))
    except (OSError, ValueError) as error:
        lines.append('  남은 공간 확인 실패 · ' + explain(error))
    token = token or '{}_{}'.format(socket.gethostname(), os.getpid())
    work = root / ('_저장위치점검_' + re.sub(r'[^0-9A-Za-z가-힣_-]', '_', token))
    ok = True
    made = False
    try:
        work.mkdir()
        made = True
        lines.append('  시험 폴더 만들기: 됨')
        first, second, lock = work / '시험.tmp', work / '시험.json', work / '시험.lock'
        payload = ('지후니우스 저장 위치 점검 ' * 200).encode('utf-8')

        def write():
            descriptor = os.open(str(first), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        lines.append('  파일 쓰기(저장 확정까지): 됨 · {:.0f}ms'.format(timed(write)))
        lines.append('  이름 바꿔 덮어쓰기: 됨 · {:.0f}ms'.format(timed(lambda: os.replace(str(first), str(second)))))
        # 한 번 더: 이미 있는 파일 위로 바꾸기(실제 저장이 매번 하는 일)
        write()
        lines.append('  있는 파일 위로 바꾸기: 됨 · {:.0f}ms'.format(timed(lambda: os.replace(str(first), str(second)))))
        lines.append('  다시 읽어 같은지: ' + ('같음' if second.read_bytes() == payload else '다름!'))
        if second.read_bytes() != payload:
            ok = False
        for label, check in (('독점 잠금(인수인계·돌출량 방식)', exclusive_handle_check),
                             ('바이트 잠금(세척일보·특수 돌출량·오류기록·소재 방식)', range_lock_check)):
            try:
                result = check(lock)
            except Exception as error:   # 잠금 시험 하나가 실패해도 나머지를 계속합니다.
                result = '확인 실패 · ' + explain(error)
            if result != '됨':
                ok = False
            lines.append('  {}: {}'.format(label, result))
        average, worst = latency(second)
        lines.append('  작은 파일 확인·읽기 15회: 평균 {:.1f}ms · 최대 {:.1f}ms'.format(average, worst))
    except Exception as error:
        ok = False
        lines.append('  시험 중 실패 · ' + explain(error))
    finally:
        if made:
            left = []
            for path in sorted(work.glob('*')):
                try:
                    path.unlink()
                except OSError:
                    left.append(path.name)
            try:
                work.rmdir()
                lines.append('  시험 폴더 지우기: 됨')
            except OSError as error:
                ok = False
                lines.append('  시험 폴더를 지우지 못함 · {} · 남은 것: {} → 손으로 지워 주세요: {}'.format(
                    explain(error), ', '.join(left) or '폴더만', work))
    return lines, ok


# ── 전체 실행 ───────────────────────────────────────────────────────────────────

def run(old_parent=OLD_PARENT, new_root=NEW_ROOT, config_folder='auto', log=lambda text: None):
    old_parent, new_root = Path(old_parent), Path(new_root)
    lines = ['지후니우스 저장 위치 점검 {} · {}'.format(PROBE_VERSION, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
             'PC {} · {} {} · Python {}'.format(socket.gethostname(), platform.system(), platform.release(),
                                                 platform.python_version()),
             '예전 위치는 읽기만 했고, 파일 내용은 이 글에 담지 않았습니다.', '']
    grand = 0

    log('예전 위치의 인수인계 폴더 확인 중…')
    found, size = inventory_handover(old_parent / HANDOVER_NAME)
    lines += found + ['']
    grand += size

    log('세척일보 저장 폴더 확인 중…')
    configured = wash_config_folder() if config_folder == 'auto' else config_folder
    lines.append('이 PC의 세척일보가 기억하는 저장 폴더: {}'.format(configured or '없음(기본 위치 사용)'))
    candidates = []
    if configured:
        candidates.append((Path(configured), '이 PC 설정'))
    for path, label in ((old_parent / '세척일보', '프로그램 기본 위치'), (old_parent, '개인 폴더 바로 아래')):
        if not any(same_folder(path, known) for known, _label in candidates):
            candidates.append((path, label))
    identities = {}
    for path, label in candidates:
        found, size, identity = inventory_wash(path, label)
        lines += found
        if identity:
            identities.setdefault(identity, []).append(label)
            grand += size
    if len(identities) > 1:
        lines.append('※ 세척일보 저장 폴더가 {}곳 있습니다(식별 번호가 서로 다름). 어느 쪽이 지금 쓰는 것인지 위의 "최근 수정"으로 확인합니다.'.format(len(identities)))
    lines.append('')
    try:
        target = old_parent / HANDOVER_NAME / '돌출량_현황표.json'
        average, worst = latency(target)
        lines.append('[예전 위치] 작은 파일 확인·읽기 15회: 평균 {:.1f}ms · 최대 {:.1f}ms'.format(average, worst))
    except OSError as error:
        lines.append('[예전 위치] 읽기 시간 확인 실패 · ' + explain(error))
    lines.append('옮길 자료 합계 약 ' + size_text(grand))
    lines.append('')

    log('새 위치에 써 보는 중…')
    found, ok = check_new(new_root)
    lines += found
    lines += ['', '새 위치 판정: ' + ('이 PC에서 쓸 수 있음' if ok else '문제 있음 — 위의 "안 됨/실패" 줄을 확인')]
    lines += [''] + ready_lines(new_root)
    if marker_state(new_root) == 'moved':
        lines += ['', '※ 이미 옮겨져 있습니다(새 위치에 "옮김 완료" 표시가 있음).']
    return '\n'.join(lines)


# ── 옮기기 ──────────────────────────────────────────────────────────────────────

class MoveError(Exception):
    """옮기기를 멈춘 이유(사용자에게 그대로 보여 줍니다). 멈출 때 예전 위치는 원래대로입니다."""


def skipped(name):
    """복사하지 않는 파일: 잠금 파일, 저장 중 임시 파일."""
    return name.endswith('.lock') or name.endswith('.tmp')


def all_files(folder, every=False):
    """폴더 아래 모든 파일. every가 아니면 잠금·임시 파일과 '.locks' 폴더는 뺍니다."""
    result = []
    stack = [Path(folder)]
    while stack:
        current = stack.pop()
        with os.scandir(str(current)) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    if every or entry.name != '.locks':
                        stack.append(Path(entry.path))
                elif every or not skipped(entry.name):
                    result.append(Path(entry.path))
    return sorted(result)


def has_entries(folder):
    with os.scandir(str(folder)) as entries:
        return any(True for _entry in entries)


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stat_key(path):
    info = path.stat()
    return info.st_size, info.st_mtime_ns


def version_tuple(text):
    return tuple(int(part) for part in str(text).split('.'))


def installed_app_versions():
    """이 PC에 설치 기록이 있는 지후니우스 버전들."""
    base = Path(os.environ.get('LOCALAPPDATA') or str(Path.home())) / 'JihuniusTools' / 'desktop-v1'
    versions = []
    try:
        states = list(base.glob('*/state.json'))
    except OSError:
        return versions
    for state in states:
        try:
            value = read_json(state, 1024 * 1024)
            version = str(value['current']['version'])
            version_tuple(version)
            versions.append(version)
        except (OSError, ValueError, KeyError, TypeError):
            pass
    return versions


def ready_pcs(new_root):
    """새 위치를 아는 버전의 지후니우스가 켜진 적 있는 PC들: [(PC 이름, 버전, 시각)]."""
    found = []
    try:
        paths = sorted((Path(new_root) / READY_NAME).glob('*.json'))
    except OSError:
        return found
    for path in paths:
        try:
            value = read_json(path, 65536)
            found.append((str(value['pc']), str(value['version']), str(value.get('at', ''))))
        except (OSError, ValueError, KeyError, TypeError):
            pass
    return found


def ready_lines(new_root):
    found = ready_pcs(new_root)
    lines = ['[새 버전으로 켜진 적 있는 PC] ({} 이상이 새 위치를 압니다)'.format(REQUIRED_APP_VERSION)]
    if not found:
        return lines + ['  아직 없음 → 지후니우스를 {} 이상으로 업데이트해 한 번 켠 PC가 여기에 나옵니다.'.format(REQUIRED_APP_VERSION)]
    lines += ['  {} · {} · {}'.format(pc, version, at) for pc, version, at in found]
    return lines + ['  ※ 지후니우스를 쓰는 PC가 여기에 다 있는지 확인해 주세요. 빠진 PC는 먼저 업데이트해야 합니다.']


def marker_state(new_root):
    """'moved'(옮김 완료 표시 있음) / 'absent'(없음) / 'unknown'(있는데 읽을 수 없거나 확인 실패)."""
    path = Path(new_root) / MARKER_NAME
    try:
        value = read_json(path, 65536)
    except FileNotFoundError as error:
        # Windows는 네트워크 오류도 '없음'으로 알려 줄 수 있어, 폴더가 실제로 열릴 때만 없다고 봅니다.
        if getattr(error, 'winerror', None) not in (None, 2):
            return 'unknown'
        try:
            with os.scandir(str(new_root)) as entries:
                return 'unknown' if any(entry.name == MARKER_NAME for entry in entries) else 'absent'
        except OSError:
            return 'unknown'
    except (OSError, ValueError):
        return 'unknown'
    if isinstance(value, dict) and value.get('version') == 1 and value.get('moved') is True:
        return 'moved'
    return 'unknown'


def marker_valid(new_root):
    return marker_state(new_root) == 'moved'


def build_plan(old_parent):
    """무엇을 어디로 옮길지(읽기만). items: 복사할 파일, aside: 옮긴 뒤 한 폴더로 모을 예전 항목."""
    old_parent = Path(old_parent)
    handover, wash = old_parent / HANDOVER_NAME, old_parent / WASH_NAME
    plan = {'items': [], 'aside': [], 'blockers': [], 'notes': []}

    def add(source, target, aside):
        plan['items'].append({'source': source, 'to': tuple(target), 'aside': tuple(aside)})

    if not handover.is_dir():
        plan['blockers'].append('예전 위치의 "{}" 폴더를 열 수 없습니다: {}'.format(HANDOVER_NAME, handover))
    else:
        if (handover / '세척완료_실행중.json').exists():
            plan['blockers'].append('세척완료가 실행 중인 PC가 있습니다(세척완료_실행중.json). 끝난 뒤 다시 해 주세요.')
        for path in all_files(handover):
            parts = path.relative_to(handover).parts
            if parts == ('세척완료_실행중.json',):
                continue
            if len(parts) == 1 and NOTE.fullmatch(parts[0]):
                target = (NEW_NAMES['handover'],) + parts
            elif parts == ('돌출량_현황표.json',):
                target = (NEW_NAMES['protrusion'],) + parts
            elif parts == ('특수_돌출량.json',):
                target = (NEW_NAMES['special'],) + parts
            elif parts[0] == '오류기록' and len(parts) > 1:
                target = (NEW_NAMES['errors'],) + parts[1:]
            elif parts == ('소재재고조사', 'owner.json'):
                target = (NEW_NAMES['material'], 'owner.json')
            else:
                target = (RECORD_NAME, OTHER_NAME) + parts
            add(path, target, (HANDOVER_NAME,) + parts)
        plan['aside'].append((handover, (HANDOVER_NAME,)))

    if not (wash / '저장정보.json').is_file():
        plan['blockers'].append('세척일보 저장 폴더를 찾지 못했습니다(저장정보.json 없음): {}'.format(wash))
    else:
        for path in all_files(wash):
            parts = path.relative_to(wash).parts
            add(path, (NEW_NAMES['wash'],) + parts, (WASH_NAME,) + parts)
        plan['aside'].append((wash, (WASH_NAME,)))

    # 개인 폴더 바로 아래에 남아 있는 예전 세척일보 저장 흔적(있을 때만). 기록 폴더에 따로 보관합니다.
    if (old_parent / '저장정보.json').is_file():
        for name in ('저장정보.json', '공구대.json', '부서메모.json', 'wash_log_data.json',
                     'wash_log_data.previous.json'):
            path = old_parent / name
            if path.is_file():
                add(path, (RECORD_NAME, LEFTOVER_NAME, name), (LEFTOVER_NAME, name))
                plan['aside'].append((path, (LEFTOVER_NAME, name)))
        if (old_parent / 'wash_log_data.lock').is_file():
            plan['aside'].append((old_parent / 'wash_log_data.lock', (LEFTOVER_NAME, 'wash_log_data.lock')))
        for name in ('백업', '이전통합백업'):
            folder = old_parent / name
            if not folder.is_dir():
                continue
            with os.scandir(str(folder)) as entries:
                children = {entry.name for entry in entries}
            if name == '백업' and not children <= {'공구대', '부서메모', '세척일보'}:
                plan['notes'].append('개인 폴더의 "백업" 폴더는 세척일보 백업 모양이 아니라서 건드리지 않습니다.')
                continue
            for path in all_files(folder):
                parts = path.relative_to(folder).parts
                add(path, (RECORD_NAME, LEFTOVER_NAME, name) + parts, (LEFTOVER_NAME, name) + parts)
            plan['aside'].append((folder, (LEFTOVER_NAME, name)))
    return plan


def copy_file(source, target):
    """복사하고 다시 읽어 같은지 확인합니다. (크기, sha256)"""
    data = source.read_bytes()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.옮기는중')
    descriptor = os.open(str(temporary), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(target))
    finally:
        try:
            temporary.unlink()
        except OSError:
            pass
    try:
        info = source.stat()
        os.utime(str(target), ns=(info.st_atime_ns, info.st_mtime_ns))
    except OSError:
        pass
    if target.read_bytes() != data:
        raise MoveError('복사한 파일이 원본과 다릅니다: {}'.format(target))
    return len(data), hashlib.sha256(data).hexdigest()


def write_json(path, value):
    temporary = path.with_name(path.name + '.쓰는중')
    try:
        with temporary.open('w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=1)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(path))
    finally:
        try:
            temporary.unlink()
        except OSError:
            pass


def remove_tree(folder):
    """폴더를 통째로 지웁니다(아래 wipe_partial·cleanup에서, 확인이 끝난 폴더에만)."""
    for path in all_files(folder, every=True):
        path.unlink()
    for current, _folders, _files in sorted(os.walk(str(folder)), reverse=True):
        os.rmdir(current)


def wipe_partial(new_root):
    """지난번에 끝내지 못한 복사본을 지웁니다. '진행중' 기록이 있고 '옮김 완료' 표시가 없을 때만 부릅니다."""
    new_root = Path(new_root)
    for name in list(NEW_NAMES.values()) + [RECORD_NAME]:
        folder = new_root / name
        if folder.is_dir() and folder.parent == new_root:
            remove_tree(folder)


def undo_set_aside(done, setaside):
    for source, target in reversed(done):
        try:
            if source is None:
                target.unlink()
            else:
                os.rename(str(target), str(source))
        except OSError:
            pass
    for current, _folders, _files in sorted(os.walk(str(setaside)), reverse=True):
        try:
            os.rmdir(current)
        except OSError:
            pass


def rename_patiently(source, target, seconds=8.0):
    """다른 프로그램이 잠깐 잡고 있을 수 있어, 안 되면 몇 초 동안 다시 해 봅니다."""
    deadline = time.monotonic() + seconds
    while True:
        try:
            os.rename(str(source), str(target))
            return
        except PermissionError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.4)


def set_aside(plan, old_parent):
    """예전 항목을 한 폴더로 모으고, 그 자리에 '옮겼음' 표시 파일을 둡니다. 하나라도 안 되면 전부 되돌립니다."""
    setaside = Path(old_parent) / SETASIDE_NAME
    done = []
    current = None
    try:
        setaside.mkdir()
        for source, parts in plan['aside']:
            target = setaside.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            current = source
            rename_patiently(source, target)
            done.append((source, target))
        current = None
        for name in TOMBSTONES:
            path = Path(old_parent) / name
            with open(str(path), 'x', encoding='utf-8', newline='') as stream:
                stream.write(TOMBSTONE_TEXT)
            done.append((None, path))
    except OSError as error:
        undo_set_aside(done, setaside)
        raise MoveError('예전 위치의 {} 옮겨 둘 수 없습니다. 무언가가 그 폴더를 쓰고 있습니다.\n'
                        '· 다른 PC에서 지후니우스가 아직 켜져 있을 수 있습니다(트레이에 남아 있는지도 확인).\n'
                        '· 탐색기에서 그 폴더 안을 열어 두었다면 닫아 주세요.\n'
                        '확인한 뒤 [② 옮기기]를 다시 누르면 됩니다. 예전 위치는 원래대로입니다.\n(' .format(
                            '"{}"을(를)'.format(current.name) if current is not None else '폴더를') + explain(error) + ')')
    return done, setaside


def restore_interrupted(old_parent):
    """지난번 옮기기가 '옮김 완료' 표시 전에 멈췄을 때: 모아 둔 예전 항목을 제자리로 되돌립니다."""
    old_parent = Path(old_parent)
    setaside = old_parent / SETASIDE_NAME
    if not setaside.is_dir():
        return False
    moves = [(setaside / HANDOVER_NAME, old_parent / HANDOVER_NAME), (setaside / WASH_NAME, old_parent / WASH_NAME)]
    leftover = setaside / LEFTOVER_NAME
    if leftover.is_dir():
        with os.scandir(str(leftover)) as entries:
            moves += [(Path(entry.path), old_parent / entry.name) for entry in entries]
    for source, target in moves:
        if not source.exists():
            continue
        if target.is_file() and target.name in TOMBSTONES:
            target.unlink()                     # 우리가 둔 표시 파일
        if target.exists():
            raise MoveError('지난번에 멈춘 옮기기를 되돌리지 못했습니다. 같은 이름이 이미 있습니다: {}'.format(target))
        os.rename(str(source), str(target))
    for current, _folders, _files in sorted(os.walk(str(setaside)), reverse=True):
        os.rmdir(current)
    return True


def changes_since(plan, snapshot, old_parent):
    """복사를 시작한 뒤 예전 위치에서 바뀌거나 새로 생기거나 없어진 파일."""
    fresh = build_plan(old_parent)
    now = {}
    for item in fresh['items']:
        try:
            now[item['source']] = (stat_key(item['source']), item)
        except OSError:
            pass
    changed = [item for source, (key, item) in now.items() if snapshot.get(source) != key]
    removed = [item for item in plan['items'] if item['source'] not in now]
    return fresh, changed, removed


def move(old_parent=OLD_PARENT, new_root=NEW_ROOT, log=lambda text: None, require_version=REQUIRED_APP_VERSION):
    """자료를 새 위치로 옮깁니다. 실패하면 MoveError를 내고, 그때 예전 위치는 원래대로입니다."""
    old_parent, new_root = Path(old_parent), Path(new_root)
    record = new_root / RECORD_NAME
    state = marker_state(new_root)
    if state == 'moved':
        raise MoveError('이미 옮겨져 있습니다(새 위치에 "옮김 완료" 표시가 있음).\n'
                        '예전 자료를 지우려면 [예전 자료 지우기]를 누르면 됩니다.')
    if state != 'absent':
        raise MoveError('새 위치의 "옮김 완료" 표시를 확인할 수 없어 아무것도 하지 않았습니다.\n'
                        '새 위치에 연결되는지 확인한 뒤 다시 해 주세요: {}'.format(new_root))
    if require_version:
        # 새 위치를 아는 버전은 켜질 때 새 위치의 '준비된 PC' 폴더에 이름을 남깁니다. 이 PC가 거기 없으면
        # 아직 배포·업데이트 전이라는 뜻이므로 옮기지 않습니다(예전 버전은 옮긴 자료를 찾지 못합니다).
        mine = socket.gethostname()
        seen = [version for pc, version, _at in ready_pcs(new_root) if pc == mine]
        current = None
        for version in seen:
            try:
                current = max(current or (0,), version_tuple(version))
            except ValueError:
                pass
        if current is None or current < version_tuple(require_version):
            local = ', '.join(sorted(set(installed_app_versions()))) or '기록 없음'
            raise MoveError('이 PC({})에서 {} 이상의 지후니우스를 켠 기록이 새 위치에 없습니다(이 PC에 설치된 버전: {}).\n'
                            '모든 PC를 {} 이상으로 업데이트해 한 번씩 켠 다음, 전부 끄고 다시 해 주세요.'.format(
                                mine, require_version, local, require_version))
    if (old_parent / SETASIDE_NAME).is_dir():
        log('지난번에 멈춘 옮기기를 되돌리는 중…')
        restore_interrupted(old_parent)
    plan = build_plan(old_parent)
    if plan['blockers']:
        raise MoveError('\n'.join(plan['blockers']))
    log('새 위치에 쓸 수 있는지 확인 중…')
    checked, ok = check_new(new_root)
    if not ok:
        raise MoveError('새 위치에 문제가 있어 옮기지 않았습니다.\n' + '\n'.join(checked))
    occupied = [name for name in list(NEW_NAMES.values()) + [RECORD_NAME]
                if (new_root / name).exists() and (not (new_root / name).is_dir() or has_entries(new_root / name))]
    if occupied:
        if not (record / JOURNAL_NAME).is_file():
            raise MoveError('새 위치에 이미 자료가 있어 옮기지 않았습니다: {}\n'
                            '지후니우스가 쓰던 것이 아니라면 그 폴더들을 지운 뒤 다시 해 주세요.'.format(', '.join(occupied)))
        log('지난번에 끝내지 못한 복사본을 지우는 중…')
        wipe_partial(new_root)
    record.mkdir(parents=True, exist_ok=True)
    write_json(record / JOURNAL_NAME, {'started': datetime.now().isoformat(timespec='seconds'),
                                       'pc': socket.gethostname(), 'from': str(old_parent)})
    for name in NEW_NAMES.values():
        (new_root / name).mkdir(exist_ok=True)

    copied = {}
    snapshot = {}
    pending = list(plan['items'])
    for attempt in range(4):
        for index, item in enumerate(pending, 1):
            if index == 1 or index % 10 == 0 or index == len(pending):
                log('복사 중… {} / {} (끝날 때까지 기다려 주세요)'.format(index, len(pending)))
            snapshot[item['source']] = stat_key(item['source'])
            size, digest = copy_file(item['source'], new_root.joinpath(*item['to']))
            copied[item['source']] = dict(item, size=size, sha256=digest)
        log('복사하는 동안 바뀐 것이 없는지 확인 중…')
        plan, pending, removed = changes_since(plan, snapshot, old_parent)
        if plan['blockers']:
            raise MoveError('\n'.join(plan['blockers']))
        for item in removed:
            copied.pop(item['source'], None)
            snapshot.pop(item['source'], None)
            try:
                new_root.joinpath(*item['to']).unlink()
            except OSError:
                pass
        if not pending and not removed:
            break
    else:
        names = ', '.join(sorted({item['source'].name for item in pending})[:8])
        raise MoveError('복사하는 동안 예전 위치의 파일이 계속 바뀝니다({}).\n다른 PC에서 지후니우스가 켜져 있는 것 같습니다. '
                        '모든 PC에서 완전 종료한 뒤 다시 해 주세요.'.format(names or '파일이 없어짐'))

    files = [{'from': list(item['source'].relative_to(old_parent).parts), 'aside': list(item['aside']),
              'to': list(item['to']), 'size': item['size'], 'sha256': item['sha256']}
             for item in sorted(copied.values(), key=lambda value: value['to'])]
    write_json(record / MANIFEST_NAME, {'version': 1, 'from': str(old_parent), 'to': str(new_root), 'files': files})
    log('예전 자료를 한 폴더로 모으는 중…')
    done, setaside = set_aside(plan, old_parent)
    try:
        # '진행중' 기록은 완료 표시보다 먼저 지웁니다: 둘이 함께 남으면, 나중에 누가 다시 옮기기를 눌렀을 때
        # 쓰고 있는 새 자료를 '끝내지 못한 복사본'으로 잘못 알고 지울 수 있기 때문입니다.
        (record / JOURNAL_NAME).unlink()
        write_json(new_root / MARKER_NAME, {
            'version': 1, 'moved': True, 'moved_at': datetime.now().isoformat(timespec='seconds'),
            'from': str(old_parent), 'by': socket.gethostname(), 'files': len(files), 'tool': PROBE_VERSION})
        if not marker_valid(new_root):
            raise OSError('표시 파일을 다시 읽지 못했습니다')
    except OSError as error:
        undo_set_aside(done, setaside)
        raise MoveError('새 위치에 "옮김 완료" 표시를 쓰지 못해 예전 위치를 원래대로 되돌렸습니다.\n(' + explain(error) + ')')

    counts = {}
    for entry in files:
        counts.setdefault(entry['to'][0], [0, 0])
        counts[entry['to'][0]][0] += 1
        counts[entry['to'][0]][1] += entry['size']
    lines = ['지후니우스 저장 위치 옮기기 완료 · {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
             'PC {}'.format(socket.gethostname()), '예전: {}'.format(old_parent), '새 위치: {}'.format(new_root), '',
             '옮긴 파일 {}개 · {} (파일마다 다시 읽어 원본과 같은지 확인함)'.format(
                 len(files), size_text(sum(entry['size'] for entry in files)))]
    for name in list(NEW_NAMES.values()) + [RECORD_NAME]:
        count, size = counts.get(name, (0, 0))
        lines.append('  {}\\: 파일 {}개 · {}'.format(name, count, size_text(size)))
    lines += plan['notes']
    lines += [''] + ready_lines(new_root)
    try:   # 옮긴 뒤에는 쓰지 않는 목록이라 기록 폴더로 치워 둡니다.
        os.rename(str(new_root / READY_NAME), str(record / READY_NAME))
    except OSError:
        pass
    lines += ['', '예전 자료는 지우지 않았고, 개인 폴더 안의 이 폴더로 모아 두었습니다:',
              '  ' + str(setaside),
              '개인 폴더에는 "{}", "{}" 이름의 작은 파일을 하나씩 두었습니다.'.format(*TOMBSTONES),
              '  (업데이트하지 않은 예전 지후니우스가 여기에 새 자료를 만들지 못하게 막는 표시)', '',
              '다음: 지후니우스를 다시 켜서 세척일보·인수인계·돌출량 표가 그대로 보이는지 확인한 뒤',
              '      [예전 자료 지우기]를 누르면 됩니다.']
    report = '\n'.join(lines)
    try:
        (record / '옮기기 결과_{}.txt'.format(datetime.now().strftime('%Y%m%d-%H%M%S'))).write_text(report, encoding='utf-8')
    except OSError:
        pass
    return report


def cleanup(old_parent=OLD_PARENT, new_root=NEW_ROOT, log=lambda text: None):
    """모아 둔 예전 자료를 지웁니다. 옮긴 목록과 대조가 맞는 파일만, 하나라도 이상하면 아무것도 지우지 않습니다."""
    old_parent, new_root = Path(old_parent), Path(new_root)
    if not marker_valid(new_root):
        raise MoveError('아직 옮기기가 끝나지 않았습니다(새 위치에 "옮김 완료" 표시가 없음). 지우지 않았습니다.')
    setaside = old_parent / SETASIDE_NAME
    if not setaside.is_dir():
        raise MoveError('지울 예전 자료 폴더가 없습니다(이미 지웠거나 다른 곳에 있음): {}'.format(setaside))
    try:
        manifest = read_json(new_root / RECORD_NAME / MANIFEST_NAME, 64 * 1024 * 1024)
        expected = {tuple(entry['aside']): entry for entry in manifest['files']}
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise MoveError('옮긴 파일 목록을 읽지 못해 지우지 않았습니다.\n(' + explain(error) + ')')
    for name in NEW_NAMES.values():
        if not (new_root / name).is_dir():
            raise MoveError('새 위치에 "{}" 폴더가 없습니다. 지우지 않았습니다.'.format(name))
    problems = []
    deletable = []
    total = 0
    paths = all_files(setaside, every=True)
    for index, path in enumerate(paths, 1):
        if index == 1 or index % 100 == 0 or index == len(paths):
            log('대조 중… {} / {}'.format(index, len(paths)))
        parts = path.relative_to(setaside).parts
        entry = expected.get(parts)
        if entry is None:
            if skipped(path.name) or '.locks' in parts or parts[-1] == '세척완료_실행중.json':
                deletable.append(path)
            else:
                problems.append('옮긴 목록에 없는 파일: ' + '\\'.join(parts))
            continue
        try:
            if file_hash(path) != entry['sha256']:
                problems.append('옮긴 뒤에 내용이 바뀐 파일: ' + '\\'.join(parts))
            else:
                deletable.append(path)
                total += entry['size']
        except OSError as error:
            problems.append('읽지 못한 파일: {} · {}'.format('\\'.join(parts), explain(error)))
    if problems:
        raise MoveError('이상한 점이 있어 아무것도 지우지 않았습니다:\n' + '\n'.join(problems[:20])
                        + ('\n… 외 {}건'.format(len(problems) - 20) if len(problems) > 20 else ''))
    log('지우는 중…')
    for path in deletable:
        path.unlink()
    for current, _folders, _files in sorted(os.walk(str(setaside)), reverse=True):
        os.rmdir(current)
    return ('예전 자료를 지웠습니다 · 파일 {}개 · {}\n지운 폴더: {}\n\n개인 폴더에 남은 "{}", "{}" 파일은 모든 PC를 '
            '업데이트한 뒤에 지워도 됩니다.'.format(len(deletable), size_text(total), setaside, *TOMBSTONES))


def main():
    import tkinter as tk
    from tkinter import messagebox, ttk
    root = tk.Tk()
    root.title('지후니우스 저장 위치 옮기기')
    root.geometry('900x660')
    frame = ttk.Frame(root, padding=12)
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='① 점검 → ② 모든 PC에서 지후니우스를 끄고 옮기기 → ③ 새 위치에서 확인한 뒤 예전 자료 지우기').pack(anchor='w')
    paths = ttk.Frame(frame)
    paths.pack(fill='x', pady=(8, 4))
    old_value, new_value = tk.StringVar(value=OLD_PARENT), tk.StringVar(value=NEW_ROOT)
    for row, (label, variable) in enumerate((('예전 위치(개인 폴더)', old_value), ('새 위치', new_value))):
        ttk.Label(paths, text=label, width=20).grid(row=row, column=0, sticky='w', pady=2)
        ttk.Entry(paths, textvariable=variable).grid(row=row, column=1, sticky='ew', pady=2)
    paths.columnconfigure(1, weight=1)
    bar = ttk.Frame(frame)
    bar.pack(fill='x', pady=(4, 8))
    buttons = {}
    for key, label in (('probe', '① 점검'), ('move', '② 옮기기'), ('cleanup', '③ 예전 자료 지우기'), ('copy', '결과 복사')):
        buttons[key] = ttk.Button(bar, text=label)
        buttons[key].pack(side='left', padx=(0, 8))
    buttons['copy'].configure(state='disabled')
    status = tk.StringVar(value='먼저 [① 점검]을 눌러 주세요.')
    ttk.Label(frame, textvariable=status).pack(anchor='w')
    text = tk.Text(frame, wrap='word', font=('맑은 고딕', 10))
    text.pack(fill='both', expand=True, pady=(6, 0))
    result = {'text': '', 'events': []}

    def put_clipboard():
        root.clipboard_clear()
        root.clipboard_append(result['text'])
        status.set('결과를 복사했습니다. 그대로 붙여넣어 보내 주세요.')
    buttons['copy'].configure(command=put_clipboard)

    def work(action, old_path, new_path):
        report = lambda message: result['events'].append(('log', message))
        try:
            if action == 'probe':
                output = run(old_path, new_path, log=report)
            elif action == 'move':
                # 새 버전 기록이 없는 경우는 위의 확인 창에서 이미 물어봤습니다.
                output = move(old_path, new_path, log=report, require_version=None)
            else:
                output = cleanup(old_path, new_path, log=report)
        except MoveError as error:
            output = '하지 않았습니다.\n\n' + str(error)
        except Exception as error:
            output = '오류로 멈췄습니다: ' + explain(error) + '\n\n[② 옮기기] 중이었다면 다시 누르면 처음부터 다시 합니다.'
        result['events'].append(('done', (action, output)))

    def begin(action):
        if action == 'move':
            try:
                ready = ready_pcs(new_value.get().strip())
            except Exception:
                ready = []
            mine = socket.gethostname()
            listed = ', '.join('{}({})'.format(pc, version) for pc, version, _at in ready) or '없음'
            here = any(pc == mine for pc, _version, _at in ready)
            note = ('새 버전({} 이상)으로 켠 적 있는 PC: {}\n\n'.format(REQUIRED_APP_VERSION, listed)
                    + ('' if here else
                       '※ 이 PC는 아직 새 버전으로 켠 기록이 없습니다. 그대로 옮겨도 되지만,\n'
                       '   옮긴 뒤 각 PC에서 지후니우스를 켜면 자료가 안 보이고 오류가 납니다.\n'
                       '   그때 [새 버전 있음]을 눌러 업데이트하면 새 위치의 자료가 보입니다.\n'
                       '   소재 수집 담당 PC는 업데이트할 때까지 집계가 멈춥니다.\n\n'))
            if not messagebox.askokcancel(
                    '저장 위치 옮기기', note + '모든 PC에서 지후니우스를 완전 종료했나요?(트레이 포함)\n\n'
                    '· 옮기는 동안(몇 분) 어느 PC에서도 지후니우스를 켜지 마세요.\n'
                    '· 예전 자료는 지우지 않고 개인 폴더 안의 한 폴더로 모아 둡니다.\n\n지금 옮길까요?',
                    parent=root, icon='warning', default='ok'):
                return
        if action == 'cleanup' and not messagebox.askokcancel(
                '예전 자료 지우기', '개인 폴더에 모아 둔 지후니우스 예전 자료를 지웁니다. 되돌릴 수 없습니다.\n\n'
                '지후니우스를 다시 켜서 세척일보·인수인계·돌출량 표가 새 위치에서 그대로 보이는 것을 확인했나요?',
                parent=root, icon='warning', default='cancel'):
            return
        for key in ('probe', 'move', 'cleanup', 'copy'):
            buttons[key].configure(state='disabled')
        text.delete('1.0', 'end')
        threading.Thread(target=work, args=(action, old_value.get().strip(), new_value.get().strip()), daemon=True).start()
    for key in ('probe', 'move', 'cleanup'):
        buttons[key].configure(command=lambda chosen=key: begin(chosen))

    def poll():
        while result['events']:
            kind, value = result['events'].pop(0)
            if kind == 'log':
                status.set(value)
                continue
            action, output = value
            result['text'] = output
            text.insert('1.0', output)
            for key in ('probe', 'move', 'cleanup', 'copy'):
                buttons[key].configure(state='normal')
            saved = ''
            try:
                name = '저장위치{}결과_{}.txt'.format({'probe': '점검', 'move': '옮기기', 'cleanup': '지우기'}[action],
                                                 datetime.now().strftime('%Y%m%d-%H%M%S'))
                (Path(sys.argv[0]).resolve().parent / name).write_text(output, encoding='utf-8')
                saved = ' · 파일로도 저장: ' + name
            except OSError:
                pass
            try:
                put_clipboard()
                status.set('끝났습니다. 결과를 복사했습니다' + saved)
            except tk.TclError:
                status.set('끝났습니다. [결과 복사]를 눌러 주세요' + saved)
        root.after(150, poll)
    poll()
    root.mainloop()


if __name__ == '__main__':
    main()
