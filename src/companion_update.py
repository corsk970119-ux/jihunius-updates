"""Bounded, two-phase save handshake for parent-owned companion processes.

Embedded into each companion so the released Python file stays self-contained.
No network calls, business actions, or accumulated event log live here.
"""
import json as _cu_json
import os as _cu_os
from pathlib import Path as _CuPath
import time as _cu_time
import uuid as _cu_uuid


def _cu_write(path, value):
    path = _CuPath(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + _cu_uuid.uuid4().hex + '.tmp')
    try:
        with temp.open('w', encoding='utf-8') as stream:
            _cu_json.dump(value, stream, ensure_ascii=False)
            stream.flush()
            _cu_os.fsync(stream.fileno())
        _cu_os.replace(str(temp), str(path))
    finally:
        try: temp.unlink()
        except FileNotFoundError: pass


def _cu_read(path):
    try:
        with _CuPath(path).open('rb') as stream:
            data = stream.read(16385)
        if len(data) > 16384: return {}
        value = _cu_json.loads(data)
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


class _CuExistingProcess:
    """Observe one process lifetime without terminating or claiming another PID."""
    def __init__(self,pid,started=None):
        if type(pid) is not int or pid<=0:raise ValueError('Invalid material process')
        self.pid=pid;self._handle=None;self._closed=False
        if _cu_os.name=='nt':
            import ctypes
            from ctypes import wintypes as w
            self._kernel=ctypes.WinDLL('kernel32',use_last_error=True)
            self._kernel.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];self._kernel.OpenProcess.restype=w.HANDLE
            self._kernel.GetProcessTimes.argtypes=[w.HANDLE]+[ctypes.POINTER(w.FILETIME)]*4;self._kernel.GetProcessTimes.restype=w.BOOL
            self._kernel.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD];self._kernel.WaitForSingleObject.restype=w.DWORD
            self._kernel.CloseHandle.argtypes=[w.HANDLE];self._kernel.CloseHandle.restype=w.BOOL
            self._handle=self._kernel.OpenProcess(0x100000|0x1000,False,pid)
            if not self._handle:
                self._handle=None;raise OSError('소재 조사 프로세스를 확인하지 못했습니다.')
            stamps=[w.FILETIME() for _ in range(4)]
            if not self._kernel.GetProcessTimes(self._handle,*[ctypes.byref(t) for t in stamps]):
                self.close();raise OSError('소재 조사 실행 시각을 확인하지 못했습니다.')
            self.started=str((stamps[0].dwHighDateTime<<32)|stamps[0].dwLowDateTime)
        else:
            self.started=self._posix_stamp()
        if started is not None and self.started!=started:
            self.close();raise ValueError('Material process lifetime changed')
        if self.poll() is not None:
            self.close();raise OSError('Material process already exited')

    def _posix_stamp(self):
        return _CuPath('/proc/{}/stat'.format(self.pid)).read_text().split(') ',1)[1].split()[19]

    def poll(self):
        if self._closed:return 0
        if self._handle is not None:
            result=self._kernel.WaitForSingleObject(self._handle,0)
            if result==258:return None
            if result!=0:raise OSError('소재 조사 종료 상태를 확인하지 못했습니다.')
        else:
            try:
                if self._posix_stamp()==self.started:
                    # A zombie has exited even before its original parent reaps it.
                    state=_CuPath('/proc/{}/stat'.format(self.pid)).read_text().split(') ',1)[1].split()[0]
                    if state!='Z':return None
            except (OSError,IndexError):pass
        self.close();return 0

    def close(self):
        if self._handle is not None:
            self._kernel.CloseHandle(self._handle);self._handle=None
        self._closed=True

    def __del__(self):
        try:self.close()
        except Exception:pass


class CompanionUpdateBridge:
    def __init__(self, root, adapter):
        self.root, self.adapter = root, adapter
        self.path = _cu_os.environ.get('JIHUNIUS_UPDATE_SESSION', '')
        self.nonce = _cu_os.environ.get('JIHUNIUS_UPDATE_NONCE', '')
        self.request_id = None
        self.active = False
        self.ready = False
        self.started = False
        self.overlay = None
        self.error = ''
        if self.path and len(self.nonce) == 32:
            self.path = _CuPath(self.path)
            self.root.after(500, self.poll)

    def reply(self, status, message=''):
        _cu_write(self.path / 'response.json', {
            'nonce': self.nonce, 'id': self.request_id,
            'status': status, 'message': message[:1000],
        })

    def release(self):
        self.active = False
        self.ready = False
        self.started = False
        if self.overlay is not None:
            try:
                self.overlay.grab_release()
                self.overlay.destroy()
            except Exception: pass
            self.overlay = None

    def fail(self, message):
        self.error = str(message)
        try: self.reply('error', self.error)
        finally: self.release()

    def modal_open(self):
        if self.root.grab_current() is not None:
            return True
        if _cu_os.name == 'nt':
            import ctypes
            from ctypes import wintypes
            user = ctypes.WinDLL('user32', use_last_error=True)
            user.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
            user.GetAncestor.restype = wintypes.HWND
            user.IsWindowEnabled.argtypes = [wintypes.HWND]
            user.IsWindowEnabled.restype = wintypes.BOOL
            return not user.IsWindowEnabled(user.GetAncestor(self.root.winfo_id(), 2))
        return False

    def start(self, request):
        if self.modal_open():
            raise RuntimeError('열린 확인창을 처리한 뒤 업데이트를 다시 눌러 주세요.')
        import tkinter as tk
        from tkinter import ttk
        self.active = True
        self.error = ''
        self.started = False
        self.ready = False
        dialog = tk.Toplevel(self.root)
        self.overlay = dialog
        dialog.title('업데이트 전 저장')
        dialog.transient(self.root)
        dialog.resizable(False, False)
        ttk.Label(dialog, text='변경 내용을 저장하고 있습니다…', padding=20).pack()
        ttk.Button(dialog, text='업데이트 취소', command=lambda: self.fail('사용자가 업데이트를 취소했습니다.')).pack(pady=(0, 16))
        dialog.protocol('WM_DELETE_WINDOW', lambda: self.fail('사용자가 업데이트를 취소했습니다.'))
        dialog.grab_set()
        # A focus change plus an event-loop turn commits the last Korean IME syllable.
        dialog.focus_set()
        self.begin_after = _cu_time.monotonic() + .15
        self.reply('saving')

    def poll(self):
        try:
            request = _cu_read(self.path / 'request.json')
            valid = (request.get('nonce') == self.nonce
                     and isinstance(request.get('id'), str)
                     and isinstance(request.get('expires'), (int, float))
                     and _cu_time.time() < request['expires'])
            if self.active and (not valid or request.get('id') != self.request_id
                                or request.get('phase') == 'cancel'):
                self.fail('업데이트 저장 요청이 취소되거나 연결이 종료됐습니다.')
            if valid and request['id'] != self.request_id and request.get('phase') == 'prepare':
                self.request_id = request['id']
                self.start(request)
            if self.active and not self.started and _cu_time.monotonic() >= self.begin_after:
                self.adapter.begin()
                self.started = True
            if self.active and self.started and not self.ready:
                if self.adapter.saved():
                    self.ready = True
                    self.reply('ready')
            if self.active and self.ready and request.get('phase') == 'close':
                # Recheck immediately before close; no edit can enter through the grab.
                if self.adapter.saved():
                    self.adapter.finish()
                    self.reply('closed')
                    self.active = False
                    return
        except Exception as exc:
            try: self.fail(str(exc))
            except Exception: self.release()
        try: self.root.after(250 if self.active else 750, self.poll)
        except Exception: pass
