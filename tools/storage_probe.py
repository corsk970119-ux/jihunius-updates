"""저장 위치 점검 — 지후니우스의 공유 저장 위치를 옮기기 전에 한 번 돌려 보는 프로그램.

    이 파일을 '저장위치점검.pyw'로 복사해 회사 PC에서 더블클릭합니다(Python 3.8 이상, 추가 설치 없음).

하는 일
- 예전 위치: 읽기만 합니다. 파일 이름·개수·크기·날짜와 저장 형식 번호만 적고, 내용은 적지 않습니다.
- 새 위치: 시험 폴더 하나를 만들어 쓰기·이름 바꾸기·잠금·지우기를 해 본 뒤 그 폴더를 지웁니다.
  이미 있는 파일은 건드리지 않습니다.
- 결과 글은 클립보드와 이 프로그램 옆의 '저장위치점검결과_날짜.txt'에 남깁니다.

제품(지후니우스)에는 들어가지 않는 별도 프로그램입니다.
"""
import ctypes
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

PROBE_VERSION = '1'
OLD_PARENT = r'\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈'
NEW_ROOT = r'\\srvc5352374b\생산공유폴더\지후니우스 저장'
HANDOVER_NAME = '지후니우스_인수인계'
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
        names = sorted(entry.name for entry in os.scandir(str(root)))
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
    return '\n'.join(lines)


def main():
    import tkinter as tk
    from tkinter import ttk
    root = tk.Tk()
    root.title('지후니우스 저장 위치 점검')
    root.geometry('860x620')
    frame = ttk.Frame(root, padding=12)
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='예전 위치는 읽기만 하고, 새 위치에는 시험 폴더 하나를 만들었다가 지웁니다.').pack(anchor='w')
    paths = ttk.Frame(frame)
    paths.pack(fill='x', pady=(8, 4))
    old_value, new_value = tk.StringVar(value=OLD_PARENT), tk.StringVar(value=NEW_ROOT)
    for row, (label, variable) in enumerate((('예전 위치(개인 폴더)', old_value), ('새 위치', new_value))):
        ttk.Label(paths, text=label, width=20).grid(row=row, column=0, sticky='w', pady=2)
        ttk.Entry(paths, textvariable=variable).grid(row=row, column=1, sticky='ew', pady=2)
    paths.columnconfigure(1, weight=1)
    bar = ttk.Frame(frame)
    bar.pack(fill='x', pady=(4, 8))
    start = ttk.Button(bar, text='점검 시작')
    start.pack(side='left')
    copy = ttk.Button(bar, text='결과 복사', state='disabled')
    copy.pack(side='left', padx=8)
    status = tk.StringVar(value='[점검 시작]을 눌러 주세요. 공유폴더가 느리면 1분쯤 걸릴 수 있습니다.')
    ttk.Label(bar, textvariable=status).pack(side='left', padx=8)
    text = tk.Text(frame, wrap='word', font=('맑은 고딕', 10))
    text.pack(fill='both', expand=True)
    result = {'text': '', 'events': []}

    def put_clipboard():
        root.clipboard_clear()
        root.clipboard_append(result['text'])
        status.set('결과를 복사했습니다. 그대로 붙여넣어 보내 주세요.')
    copy.configure(command=put_clipboard)

    def work(old_path, new_path):
        try:
            output = run(old_path, new_path, log=lambda message: result['events'].append(('log', message)))
        except Exception as error:
            output = '점검 중 오류: ' + explain(error)
        result['events'].append(('done', output))

    def begin():
        start.configure(state='disabled')
        copy.configure(state='disabled')
        text.delete('1.0', 'end')
        threading.Thread(target=work, args=(old_value.get().strip(), new_value.get().strip()), daemon=True).start()
    start.configure(command=begin)

    def poll():
        while result['events']:
            kind, value = result['events'].pop(0)
            if kind == 'log':
                status.set(value)
            else:
                result['text'] = value
                text.insert('1.0', value)
                start.configure(state='normal')
                copy.configure(state='normal')
                saved = ''
                try:
                    name = '저장위치점검결과_{}.txt'.format(datetime.now().strftime('%Y%m%d-%H%M%S'))
                    target = Path(sys.argv[0]).resolve().parent / name
                    target.write_text(value, encoding='utf-8')
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
