"""Original companion applications in separate processes, with graceful ownership.

No UI code or shared-data logic is rewritten. Native calls address only the
known main window of a live process started by this manager.
"""
import ctypes
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
import time
import uuid


class CompanionWindows:
    def __init__(self):
        if os.name != "nt":
            self.user = None
            return
        from ctypes import wintypes
        self.w = wintypes
        self.user = ctypes.WinDLL("user32", use_last_error=True)
        self.callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        declarations = {
            "EnumWindows": ([self.callback_type, wintypes.LPARAM], wintypes.BOOL),
            "GetWindowThreadProcessId": ([wintypes.HWND, ctypes.POINTER(wintypes.DWORD)], wintypes.DWORD),
            "GetWindowTextLengthW": ([wintypes.HWND], ctypes.c_int),
            "GetWindowTextW": ([wintypes.HWND, wintypes.LPWSTR, ctypes.c_int], ctypes.c_int),
            "GetClassNameW": ([wintypes.HWND, wintypes.LPWSTR, ctypes.c_int], ctypes.c_int),
            "IsWindow": ([wintypes.HWND], wintypes.BOOL),
            "IsWindowEnabled": ([wintypes.HWND], wintypes.BOOL),
            "IsWindowVisible": ([wintypes.HWND], wintypes.BOOL),
            "IsIconic": ([wintypes.HWND], wintypes.BOOL),
            "ShowWindowAsync": ([wintypes.HWND, ctypes.c_int], wintypes.BOOL),
            "SetForegroundWindow": ([wintypes.HWND], wintypes.BOOL),
            "AllowSetForegroundWindow": ([wintypes.DWORD], wintypes.BOOL),
            "GetLastActivePopup": ([wintypes.HWND], wintypes.HWND),
            "PostMessageW": ([wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM], wintypes.BOOL),
        }
        for name, (arguments, result) in declarations.items():
            function = getattr(self.user, name)
            function.argtypes = arguments
            function.restype = result

    def _owns(self, hwnd, pid):
        if not self.user or not self.user.IsWindow(hwnd):
            return False
        actual = self.w.DWORD()
        self.user.GetWindowThreadProcessId(hwnd, ctypes.byref(actual))
        return actual.value == pid

    def _main_window(self, pid, title):
        if self.user is None:
            return None
        matches = []

        def visit(hwnd, ignored):
            if not self._owns(hwnd, pid):
                return True
            length = self.user.GetWindowTextLengthW(hwnd)
            if length != len(title):
                return True
            text = ctypes.create_unicode_buffer(length + 1)
            self.user.GetWindowTextW(hwnd, text, length + 1)
            if text.value != title:
                return True
            class_name = ctypes.create_unicode_buffer(128)
            self.user.GetClassNameW(hwnd, class_name, len(class_name))
            if class_name.value == "TkTopLevel":
                matches.append(hwnd)
            return True

        callback = self.callback_type(visit)
        if not self.user.EnumWindows(callback, 0):
            raise OSError("열린 프로그램 창을 확인하지 못했습니다.")
        # Ambiguity must never result in addressing a similarly named dialog.
        return matches[0] if len(matches) == 1 else None

    def focus(self, pid, title):
        hwnd = self._main_window(pid, title)
        if not hwnd or not self._owns(hwnd, pid):
            return False
        if self.user.IsIconic(hwnd):
            self.user.ShowWindowAsync(hwnd, 9)  # SW_RESTORE; keeps saved geometry.
        elif not self.user.IsWindowVisible(hwnd):
            self.user.ShowWindowAsync(hwnd, 5)  # SW_SHOW, without resizing.
        popup = self.user.GetLastActivePopup(hwnd)
        if popup and self._owns(popup, pid) and self.user.IsWindowVisible(popup):
            hwnd = popup
        return bool(self.user.SetForegroundWindow(hwnd))

    def allow_foreground(self, pid):
        if self.user is not None:
            return bool(self.user.AllowSetForegroundWindow(pid))
        return False

    def close(self, pid, title):
        if self.user is None:
            raise RuntimeError("이 환경에서는 열린 창을 직접 닫은 뒤 완전 종료해 주세요.")
        hwnd = self._main_window(pid, title)
        if not hwnd or not self._owns(hwnd, pid):
            raise RuntimeError(title + " 창이 준비 중이거나 종료 중입니다. 잠시 후 다시 시도해 주세요.")
        if not self.user.IsWindowEnabled(hwnd):
            self.focus(pid, title)
            raise RuntimeError(title + "의 열린 확인창을 먼저 처리해 주세요.")
        if not self.user.PostMessageW(hwnd, 0x0010, 0, 0):  # WM_CLOSE; original save/cancel flow.
            raise OSError(title + "에 정상 종료 요청을 전달하지 못했습니다.")
        return True


class CompanionManager:
    def __init__(self, payloads, origin, _backend=None, _popen=None):
        self.payloads = dict(payloads)
        self.origin = Path(origin).resolve()
        self.backend = _backend if _backend is not None else CompanionWindows()
        self._popen = _popen if _popen is not None else subprocess.Popen
        self.processes = {}
        self.sessions = {}
        self.update_save = None
        self.close_requests = {}
        self._lock = threading.RLock()
        base = Path(os.environ.get("LOCALAPPDATA") or str(Path.home()))
        self.cache = base / "JihuniusSuite" / "companions"

    def _descriptor(self, key):
        if key not in ("protrusion", "wash-log", "special-table", "material") or key not in self.payloads:
            raise ValueError("알 수 없는 프로그램입니다.")
        item = self.payloads[key]
        data, digest = item.get("data"), item.get("sha256")
        if (not isinstance(data, bytes) or not data or len(data) > 2 * 1024 * 1024
                or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
                or hashlib.sha256(data).hexdigest() != digest):
            raise ValueError("내장 프로그램 파일 검증에 실패했습니다.")
        if not isinstance(item.get("title"), str) or not item["title"]:
            raise ValueError("프로그램 창 이름이 올바르지 않습니다.")
        return item

    def _extract(self, key, item):
        destination = self.cache / key / item["sha256"] / "app.pyw"
        try:
            if destination.read_bytes() == item["data"]:
                return destination
        except FileNotFoundError:
            pass
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".app-", suffix=".tmp", dir=str(destination.parent))
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(item["data"])
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, str(destination))
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
        if hashlib.sha256(destination.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("프로그램 파일 저장 후 검증에 실패했습니다.")
        return destination

    def running_keys(self):
        with self._lock:
            ended = [key for key, process in self.processes.items() if process.poll() is not None]
            for key in ended:
                del self.processes[key]
                self.close_requests.pop(key, None)
                if self.update_save is None or key not in self.update_save['keys']:
                    self._clear_session(key)
            return list(self.processes)

    def _clear_session(self, key):
        session = self.sessions.pop(key, None)
        if session is None: return
        try:
            for name in ('request.json', 'response.json', 'material-control.json', 'material-status.json'):
                try: (session[0] / name).unlink()
                except FileNotFoundError: pass
            for pattern in ('material-quick-*.json','material-result-*.json'):
                for path in session[0].glob(pattern):path.unlink()
            session[0].rmdir()
        except OSError: pass

    def focus(self, key):
        with self._lock:
            if key not in self.running_keys():
                return False
            return self.backend.focus(self.processes[key].pid, self.payloads[key]["title"])

    def open(self, key, hidden=False):
        with self._lock:
            if self.update_save is not None:
                raise RuntimeError('업데이트 전 저장을 진행 중입니다. 잠시 기다려 주세요.')
            item = self._descriptor(key)
            if key in self.running_keys():
                self.focus(key)
                return False
            payload = self._extract(key, item)
            executable = Path(sys.executable)
            if os.name == "nt":
                windowed = executable.with_name("pythonw.exe")
                if windowed.is_file():
                    executable = windowed
            environment = os.environ.copy()
            if key == 'material':
                environment['JIHUNIUS_MATERIAL_HIDDEN'] = '1' if hidden else '0'

            environment["JIHUNIUS_LAUNCH_DIR"] = str(self.origin)
            diagnostics=sys.modules.get('jihunius_error_history')
            recorder=getattr(diagnostics,'_recorder',None)
            if recorder is not None:environment['JIHUNIUS_APP_VERSION']=recorder.version
            session = self.cache / 'control' / uuid.uuid4().hex
            session.mkdir(parents=True)
            nonce = uuid.uuid4().hex
            environment['JIHUNIUS_UPDATE_SESSION'] = str(session)
            environment['JIHUNIUS_UPDATE_NONCE'] = nonce
            # Keep a real script file for multiprocessing spawn in the wash log.
            process = self._popen([str(executable), str(payload)], cwd=str(self.origin), env=environment)
            self.processes[key] = process
            self.sessions[key] = (session, nonce)
            if key == 'material' and not hidden:
                self.backend.allow_foreground(process.pid)
            return True

    def toggle(self, key):
        with self._lock:
            if self.update_save is not None:
                raise RuntimeError('업데이트 전 저장을 진행 중입니다. 잠시 기다려 주세요.')
            item = self._descriptor(key)
            if key not in self.running_keys():
                return self.open(key)
            if key == 'material':
                # Grant focus without changing visibility before the child decides
                # whether to hide or restore. Showing first would invert a reopen.
                self.backend.allow_foreground(self.processes[key].pid)
                self.material_control('toggle')
                return False
            now = time.monotonic()
            previous = self.close_requests.get(key)
            if previous is not None and now - previous < 2:
                return False
            process = self.processes[key]
            if process.poll() is not None:
                return self.open(key)
            # Show the owned window so its original save/cancel dialog is visible.
            self.backend.focus(process.pid, item['title'])
            self.backend.close(process.pid, item['title'])
            # Repeated clicks must not queue multiple WM_CLOSE/discard prompts.
            self.close_requests[key] = now
            return False

    def _update_command(self, key, phase):
        session, nonce = self.sessions[key]
        _cu_write(session / 'request.json', {
            'id': self.update_save['id'], 'nonce': nonce, 'phase': phase,
            'expires': time.time() + 10,
        })

    def begin_update_save(self):
        with self._lock:
            if self.update_save is not None:
                raise RuntimeError('업데이트 저장 요청이 이미 진행 중입니다.')
            keys = self.running_keys()
            if any(key not in self.sessions for key in keys):
                raise RuntimeError('이전 버전의 보조창을 저장하고 닫은 뒤 다시 눌러 주세요.')
            self.update_save = {'id': uuid.uuid4().hex, 'keys': keys,
                                'phase': 'prepare', 'start': time.monotonic(), 'heartbeat': 0}
            try:
                for key in keys: self._update_command(key, 'prepare')
            except Exception:
                self.cancel_update_save()
                raise

    def cancel_update_save(self):
        with self._lock:
            if self.update_save is not None:
                for key in self.update_save['keys']:
                    try: self._update_command(key, 'cancel')
                    except OSError: pass
                self.update_save = None

    def poll_update_save(self):
        with self._lock:
            state = self.update_save
            if state is None: raise RuntimeError('업데이트 저장 요청이 없습니다.')
            if time.monotonic() - state['start'] > 90:
                raise RuntimeError('보조창 저장 확인이 지연돼 업데이트를 보류했습니다. 현재 입력을 확인해 주세요.')
            statuses = []
            for key in state['keys']:
                session, nonce = self.sessions[key]
                response = _cu_read(session / 'response.json')
                status = response.get('status') if response.get('nonce') == nonce and response.get('id') == state['id'] else None
                if status == 'error':
                    raise RuntimeError(self.payloads[key]['title'] + ': ' + response.get('message', '저장 확인 실패'))
                process = self.processes.get(key)
                exited = process is None or process.poll() is not None
                if state['phase'] == 'prepare' and exited:
                    raise RuntimeError(self.payloads[key]['title'] + ' 창이 저장 확인 전에 종료됐습니다.')
                if state['phase'] == 'close' and exited and status != 'closed':
                    raise RuntimeError(self.payloads[key]['title'] + '의 정상 종료를 확인하지 못했습니다.')
                statuses.append((status, exited))
            if state['phase'] == 'prepare' and all(status == 'ready' for status, _ in statuses):
                state['phase'] = 'close'
                for key in state['keys']: self._update_command(key, 'close')
                state['heartbeat'] = time.monotonic()
            elif state['phase'] == 'close' and all(status == 'closed' and exited for status, exited in statuses):
                self.update_save = None
                self.running_keys()
                for key in state['keys']: self._clear_session(key)
                return True
            if time.monotonic() - state['heartbeat'] > 2:
                for key in state['keys']: self._update_command(key, state['phase'])
                state['heartbeat'] = time.monotonic()
            return False

    def request_close_all(self):
        with self._lock:
            for key in self.running_keys():
                process = self.processes[key]
                # Reap immediately before addressing native windows (PID ownership).
                if process.poll() is None:
                    if key == 'material':self.material_control('exit')
                    else:self.backend.close(process.pid, self.payloads[key]["title"])
            return self.running_keys()

    def material_control(self, action):
        session, nonce = self.sessions['material']
        _cu_write(session / 'material-control.json', dict(nonce=nonce,id=uuid.uuid4().hex,
                  action=action,expires=time.time()+30))

    def material_visible(self):
        if 'material' not in self.running_keys(): return False
        session,nonce=self.sessions['material']
        record=_cu_read(session/'material-status.json')
        return bool(record.get('nonce')==nonce and record.get('visible'))

    def start_material_owner(self):
        base=Path(os.environ.get('LOCALAPPDATA') or str(Path.home()/'.local'/'share'))
        record=_cu_read(base/'MaterialCounter'/'sync-settings.json')
        owner=record.get('owner')
        if not isinstance(owner,dict) or owner.get('owner_id')!=record.get('pc_id'):return False
        return self.open('material',hidden=True)

    def start_material_client(self):
        if 'material' in self.running_keys():return False
        return self.open('material',hidden=True)
