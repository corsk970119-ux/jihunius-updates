"""지후니우스 공유 저장 위치.

2026-11-17: 개인 폴더(…\\최지훈)에 있던 공유 자료를 생산공유폴더(…\\지후니우스 저장)로 옮깁니다.

- 옮기기 프로그램(tools/storage_move.py)이 자료를 복사·대조한 뒤 새 위치에 '옮김 완료' 표시 파일을 둡니다.
- 그 표시를 네트워크로 확인하는 것은 메인 프로그램뿐입니다(시작할 때 한 번, 그 뒤 1분마다, 창을 멈추지 않게 따로).
  확인한 사실은 이 PC에 기억합니다.
- 보조창(세척일보·돌출량·특수 돌출량·소재)과 저장 코드는 PC에 기억된 것만 봅니다(네트워크 확인 없음).
- 표시를 보기 전에는 지금까지처럼 예전 위치를 씁니다. 한 번 새 위치로 넘어간 PC는 예전 위치로 돌아가지 않습니다
  (새 위치가 잠깐 안 되더라도 예전 위치에 새 자료를 만들지 않도록).
"""
import json
import os
import threading
from pathlib import Path

OLD_PARENT = r'\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈'
NEW_ROOT = r'\\srvc5352374b\생산공유폴더\지후니우스 저장'
MARKER_NAME = '저장위치_옮김완료.json'
READY_NAME = '준비된 PC'
OLD_FOLDERS = {
    'wash': OLD_PARENT + r'\세척일보',
    'handover': OLD_PARENT + r'\지후니우스_인수인계',
    'protrusion': OLD_PARENT + r'\지후니우스_인수인계',
    'special': OLD_PARENT + r'\지후니우스_인수인계',
    'errors': OLD_PARENT + r'\지후니우스_인수인계\오류기록',
    'material': OLD_PARENT + r'\지후니우스_인수인계\소재재고조사',
    'wash_run': OLD_PARENT + r'\지후니우스_인수인계',
}
# 새 위치는 기능별 폴더로 나눕니다(사용자 요청 2026-11-17).
NEW_NAMES = {
    'wash': '세척일보',
    'handover': '인수인계',
    'protrusion': '돌출량 표',
    'special': '특수 돌출량',
    'errors': '오류기록',
    'material': '소재 사용량 조사',
    'wash_run': '세척완료',
}
CHECK_SECONDS = 60
STARTUP_WAIT = 1.5
NOTICE = ('지후니우스 저장 위치가 생산공유폴더로 옮겨졌습니다.\n\n'
          '이 PC는 지후니우스를 다시 실행한 뒤부터 새 위치를 씁니다.\n'
          '하던 작업을 마치고 완전 종료한 다음 다시 실행해 주세요.\n\n새 위치: ')


def state_path():
    override = os.environ.get('JIHUNIUS_STORAGE_STATE')
    if override:
        return Path(override)
    return Path(os.environ.get('LOCALAPPDATA') or str(Path.home())) / 'Jihunius' / 'storage_location.json'


def moved():
    """이 PC가 새 위치로 넘어갔는지. PC에 기억된 것만 봅니다(네트워크 없음)."""
    try:
        with state_path().open('rb') as stream:
            value = json.loads(stream.read(65536).decode('utf-8'))
    except (OSError, ValueError):
        return False
    return (isinstance(value, dict) and value.get('version') == 1 and value.get('moved') is True
            and value.get('root') == NEW_ROOT)


def remember():
    """새 위치로 넘어갔음을 이 PC에 기억합니다."""
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.{}.tmp'.format(os.getpid()))
    try:
        with temporary.open('w', encoding='utf-8') as stream:
            json.dump({'version': 1, 'moved': True, 'root': NEW_ROOT}, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(path))
    finally:
        try:
            temporary.unlink()
        except OSError:
            pass


def folder(feature):
    """기능별 공유 저장 폴더. 넘어간 PC는 새 위치, 아니면 예전 위치."""
    if moved():
        return os.path.join(NEW_ROOT, NEW_NAMES[feature])
    return OLD_FOLDERS[feature]


def marker_present():
    """새 위치에 '옮김 완료' 표시가 있는지(네트워크). 못 읽으면 없는 것으로 봅니다."""
    try:
        with open(os.path.join(NEW_ROOT, MARKER_NAME), 'rb') as stream:
            value = json.loads(stream.read(65536).decode('utf-8'))
    except (OSError, ValueError):
        return False
    return isinstance(value, dict) and value.get('version') == 1 and value.get('moved') is True


def check():
    """표시를 확인해, 있으면 이 PC에 기억합니다. 새 위치로 넘어간 상태인지 돌려줍니다."""
    if moved():
        return True
    if not marker_present():
        return False
    remember()
    return moved()


def announce(version):
    """옮기기 전: 이 PC가 새 위치를 아는 버전으로 켜졌다는 것을 새 위치에 남깁니다.

    옮기기 프로그램이 이 목록을 보여 주어, 아직 업데이트하지 않은 PC가 있는지 옮기기 전에 알 수 있습니다.
    새 위치 폴더가 이미 있을 때만 쓰고, 실패해도 아무 일도 하지 않습니다.
    """
    import socket
    import time
    if not os.path.isdir(NEW_ROOT):
        return False
    folder = os.path.join(NEW_ROOT, READY_NAME)
    try:
        os.mkdir(folder)
    except FileExistsError:
        pass
    host = socket.gethostname()
    name = ''.join(letter if letter.isalnum() or letter in '-_' else '_' for letter in host)[:60] or 'PC'
    path = os.path.join(folder, name + '.json')
    temporary = path + '.{}.tmp'.format(os.getpid())
    try:
        with open(temporary, 'w', encoding='utf-8') as stream:
            json.dump({'pc': host, 'version': str(version), 'at': time.strftime('%Y-%m-%d %H:%M:%S')},
                      stream, ensure_ascii=False)
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except OSError:
            pass
    return True


def startup_check(version=None, wait=None):
    """프로그램을 켤 때 한 번. 새 서버가 느려도 창이 늦게 뜨지 않게 잠깐만 기다립니다."""
    if moved():
        return True
    worker = threading.Thread(target=_quiet_check, args=(version,), daemon=True)
    worker.start()
    worker.join(STARTUP_WAIT if wait is None else wait)
    return moved()


def _quiet_check(version=None):
    try:
        if not check() and version:
            announce(version)
    except Exception:
        pass


class Watcher:
    """켜져 있는 동안 저장 위치가 옮겨지면, 다시 실행하라고 한 번 알립니다."""

    def __init__(self, app, interval=None):
        self.app = app
        self.window = app.window
        self.interval = int((CHECK_SECONDS if interval is None else interval) * 1000)
        self.worker = None
        self.notified = False
        if not moved():
            self.window.after(self.interval, self.tick)

    def tick(self):
        try:
            if not self.window.winfo_exists():
                return
        except Exception:
            return
        if moved():
            self.notify()
            return
        if self.worker is None or not self.worker.is_alive():
            self.worker = threading.Thread(target=_quiet_check, daemon=True)
            self.worker.start()
        self.window.after(self.interval, self.tick)

    def notify(self):
        if self.notified:
            return
        self.notified = True
        box = getattr(self.app, 'messagebox', None)
        if box is None:
            from tkinter import messagebox as box
        box.showinfo('저장 위치가 옮겨졌습니다', NOTICE + NEW_ROOT, parent=self.window)


def attach(app):
    app._storage_watcher = Watcher(app)
    return app._storage_watcher
