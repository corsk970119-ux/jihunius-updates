"""Windows notification-area lifecycle. Callbacks enqueue work; they never touch Tk."""
import ctypes
import os
import threading


class WindowsTray:
    def __init__(self, callback, title='지후니우스', owner_hwnd=None):
        self.callback = callback
        self.title = str(title)
        self.owner_hwnd = owner_hwnd
        self._ready = threading.Event()
        self._stopping = threading.Event()
        self._available = False
        self._thread = None
        self._backend = None
        self._lock = threading.RLock()

    @property
    def available(self):
        return self._available and not self._stopping.is_set()

    def start(self, timeout=2.0):
        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                self._ready.clear()
                self._stopping.clear()
                self._available = False
                self._backend = None
                self._thread = threading.Thread(target=self._worker, name='JihuniusTray', daemon=True)
                self._thread.start()
        if not self._ready.wait(max(0.0, float(timeout))):
            self.stop()
            return False
        return self.available

    def _dispatch(self, action):
        if self._stopping.is_set():
            return
        if action == 'ready':
            self._available = True
            return  # Internal recovery signal; no Tk work is necessary.
        if action == 'failed':
            self._available = False
        if action not in ('show', 'protrusion', 'wash-log', 'quit', 'failed'):
            return
        try:
            self.callback(action)
        except Exception:
            # A destroyed UI must not unwind through a ctypes window callback.
            pass

    def _worker(self):
        backend = None
        was_available = False
        try:
            backend = _NativeTrayBackend(self._dispatch, self.title, self.owner_hwnd)
            self._backend = backend
            ready = bool(backend.setup())
            self._available = ready and not self._stopping.is_set()
            was_available = self._available
            self._ready.set()
            if self._available:
                backend.run()
        except Exception:
            pass
        finally:
            self._available = False
            self._ready.set()
            if backend is not None:
                try:
                    backend.close()
                except Exception:
                    pass
            if was_available and not self._stopping.is_set():
                self._dispatch('failed')

    def stop(self):
        self._stopping.set()
        self._available = False
        backend = self._backend
        if backend is not None:
            try:
                backend.request_stop()
            except Exception:
                pass
        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(.15)


class _NativeTrayBackend:
    CALLBACK_MESSAGE = 0x8000 + 61
    STOP_MESSAGE = 0x8000 + 62
    ICON_ID = 1
    COMMANDS = {1: 'show', 2: 'protrusion', 3: 'wash-log', 4: 'quit'}

    def __init__(self, callback, title, owner_hwnd):
        self.callback = callback
        self.title = title
        self.owner_hwnd = owner_hwnd
        self.hwnd = None
        self.icon = None
        self.atom = None
        self.icon_added = False
        self._stop_requested = threading.Event()
        self._native_ready = False
        self._menu_open = False

    def _load_api(self):
        if os.name != 'nt':
            return False
        from ctypes import wintypes
        self.w = wintypes
        self.u = ctypes.WinDLL('user32', use_last_error=True)
        self.s = ctypes.WinDLL('shell32', use_last_error=True)
        self.k = ctypes.WinDLL('kernel32', use_last_error=True)
        HANDLE = ctypes.c_void_p
        DWORD = ctypes.c_uint32
        UINT = ctypes.c_uint32
        BOOL = ctypes.c_int
        LPARAM = ctypes.c_ssize_t
        WPARAM = ctypes.c_size_t
        LRESULT = ctypes.c_ssize_t
        self.WNDPROC = ctypes.WINFUNCTYPE(LRESULT, HANDLE, UINT, WPARAM, LPARAM)

        class GUID(ctypes.Structure):
            _fields_ = [('Data1', DWORD), ('Data2', ctypes.c_uint16),
                        ('Data3', ctypes.c_uint16), ('Data4', ctypes.c_ubyte * 8)]

        class NOTIFYICONDATAW(ctypes.Structure):
            _fields_ = [('cbSize', DWORD), ('hWnd', HANDLE), ('uID', UINT),
                        ('uFlags', UINT), ('uCallbackMessage', UINT), ('hIcon', HANDLE),
                        ('szTip', ctypes.c_wchar * 128), ('dwState', DWORD),
                        ('dwStateMask', DWORD), ('szInfo', ctypes.c_wchar * 256),
                        ('uVersion', UINT), ('szInfoTitle', ctypes.c_wchar * 64),
                        ('dwInfoFlags', DWORD), ('guidItem', GUID), ('hBalloonIcon', HANDLE)]

        class WNDCLASSEXW(ctypes.Structure):
            _fields_ = [('cbSize', UINT), ('style', UINT), ('lpfnWndProc', self.WNDPROC),
                        ('cbClsExtra', ctypes.c_int), ('cbWndExtra', ctypes.c_int),
                        ('hInstance', HANDLE), ('hIcon', HANDLE), ('hCursor', HANDLE),
                        ('hbrBackground', HANDLE), ('lpszMenuName', ctypes.c_wchar_p),
                        ('lpszClassName', ctypes.c_wchar_p), ('hIconSm', HANDLE)]

        self.NOTIFYICONDATAW = NOTIFYICONDATAW
        self.WNDCLASSEXW = WNDCLASSEXW

        def api(dll, name, result, arguments):
            function = getattr(dll, name)
            function.restype = result
            function.argtypes = arguments
            return function

        api(self.k, 'GetModuleHandleW', HANDLE, [ctypes.c_wchar_p])
        api(self.u, 'RegisterClassExW', ctypes.c_uint16, [ctypes.POINTER(WNDCLASSEXW)])
        api(self.u, 'UnregisterClassW', BOOL, [ctypes.c_wchar_p, HANDLE])
        api(self.u, 'CreateWindowExW', HANDLE, [DWORD, ctypes.c_wchar_p, ctypes.c_wchar_p,
                                             DWORD, ctypes.c_int, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int, HANDLE, HANDLE,
                                             HANDLE, ctypes.c_void_p])
        api(self.u, 'DefWindowProcW', LRESULT, [HANDLE, UINT, WPARAM, LPARAM])
        api(self.u, 'DestroyWindow', BOOL, [HANDLE])
        api(self.u, 'PostMessageW', BOOL, [HANDLE, UINT, WPARAM, LPARAM])
        api(self.u, 'PostQuitMessage', None, [ctypes.c_int])
        api(self.u, 'GetMessageW', BOOL, [ctypes.POINTER(wintypes.MSG), HANDLE, UINT, UINT])
        api(self.u, 'TranslateMessage', BOOL, [ctypes.POINTER(wintypes.MSG)])
        api(self.u, 'DispatchMessageW', LRESULT, [ctypes.POINTER(wintypes.MSG)])
        api(self.u, 'RegisterWindowMessageW', UINT, [ctypes.c_wchar_p])
        api(self.u, 'LoadIconW', HANDLE, [HANDLE, ctypes.c_void_p])
        api(self.u, 'CopyIcon', HANDLE, [HANDLE])
        api(self.u, 'DestroyIcon', BOOL, [HANDLE])
        api(self.u, 'SendMessageTimeoutW', LRESULT, [HANDLE, UINT, WPARAM, LPARAM,
                                                   UINT, UINT, ctypes.POINTER(WPARAM)])
        class_name = 'GetClassLongPtrW' if ctypes.sizeof(HANDLE) == 8 else 'GetClassLongW'
        self.get_class_icon = api(self.u, class_name, WPARAM, [HANDLE, ctypes.c_int])
        api(self.s, 'Shell_NotifyIconW', BOOL, [DWORD, ctypes.POINTER(NOTIFYICONDATAW)])
        api(self.u, 'CreatePopupMenu', HANDLE, [])
        api(self.u, 'AppendMenuW', BOOL, [HANDLE, UINT, WPARAM, ctypes.c_wchar_p])
        api(self.u, 'SetMenuDefaultItem', BOOL, [HANDLE, UINT, UINT])
        api(self.u, 'SetForegroundWindow', BOOL, [HANDLE])
        api(self.u, 'SetWindowPos', BOOL, [HANDLE, HANDLE, ctypes.c_int, ctypes.c_int,
                                         ctypes.c_int, ctypes.c_int, UINT])
        api(self.u, 'GetCursorPos', BOOL, [ctypes.POINTER(wintypes.POINT)])
        api(self.u, 'TrackPopupMenu', BOOL, [HANDLE, UINT, ctypes.c_int, ctypes.c_int,
                                          ctypes.c_int, HANDLE, ctypes.c_void_p])
        api(self.u, 'DestroyMenu', BOOL, [HANDLE])
        api(self.u, 'EndMenu', BOOL, [])
        self._native_ready = True
        return True

    def _copy_icon(self):
        candidates = []
        if self.owner_hwnd:
            # Timeout protects startup if Tk is waiting for this worker's readiness.
            value = ctypes.c_size_t()
            if self.u.SendMessageTimeoutW(self.owner_hwnd, 0x007F, 2, 0,
                                          0x0002, 80, ctypes.byref(value)) and value.value:
                candidates.append(value.value)
            for index in (-34, -14):  # GCLP_HICONSM, GCLP_HICON
                candidate = self.get_class_icon(self.owner_hwnd, index)
                if candidate:
                    candidates.append(candidate)
        candidates.append(self.u.LoadIconW(None, ctypes.c_void_p(32512)))
        for candidate in candidates:
            if candidate:
                copied = self.u.CopyIcon(candidate)
                if copied:
                    return copied
        return None

    def setup(self):
        if not self._load_api() or self._stop_requested.is_set():
            return False
        self.instance = self.k.GetModuleHandleW(None)
        self.class_name = 'JihuniusTray_{}_{}'.format(os.getpid(), id(self))
        self.window_proc = self.WNDPROC(self._window_proc)
        window_class = self.WNDCLASSEXW()
        window_class.cbSize = ctypes.sizeof(window_class)
        window_class.lpfnWndProc = self.window_proc
        window_class.hInstance = self.instance
        window_class.lpszClassName = self.class_name
        self.atom = self.u.RegisterClassExW(ctypes.byref(window_class))
        if not self.atom:
            return False
        self.taskbar_created = self.u.RegisterWindowMessageW('TaskbarCreated')
        # Hidden top-level windows receive Explorer's TaskbarCreated broadcast;
        # message-only windows do not.
        # A temporary tool popup can own an active menu without adding a taskbar
        # button. It stays hidden except while the tray menu is being tracked.
        self.hwnd = self.u.CreateWindowExW(0x00000080, self.class_name, self.title, 0x80000000,
                                           0, 0, 0, 0, None, None, self.instance, None)
        if not self.hwnd:
            return False
        self.icon = self._copy_icon()
        if not self.icon:
            return False
        self.nid = self.NOTIFYICONDATAW()
        self.nid.cbSize = ctypes.sizeof(self.nid)
        self.nid.hWnd = self.hwnd
        self.nid.uID = self.ICON_ID
        self.nid.uFlags = 0x0001 | 0x0002 | 0x0004 | 0x0080
        self.nid.uCallbackMessage = self.CALLBACK_MESSAGE
        self.nid.hIcon = self.icon
        # A wide-char tooltip allows Korean labels without an ANSI conversion.
        self.nid.szTip = self.title[:127]
        if self._stop_requested.is_set():
            return False
        return self._add_icon()

    def _add_icon(self):
        self.icon_added = bool(self.s.Shell_NotifyIconW(0, ctypes.byref(self.nid)))
        if self.icon_added:
            self.nid.uVersion = 4
            self.s.Shell_NotifyIconW(4, ctypes.byref(self.nid))
        return self.icon_added

    def _popup_menu(self, wparam):
        if self._menu_open or self._stop_requested.is_set() or not self.hwnd:
            return
        self._menu_open = True
        owner = self.hwnd
        menu = None
        selected = 0
        presented = False
        try:
            menu = self.u.CreatePopupMenu()
            if not menu:
                self.callback('show')
                return
            for identifier, label in ((1, '열기'), (2, '돌출량'), (3, '세척일보')):
                self.u.AppendMenuW(menu, 0, identifier, label)
            self.u.AppendMenuW(menu, 0x0800, 0, None)
            self.u.AppendMenuW(menu, 0, 4, '완전 종료')
            self.u.SetMenuDefaultItem(menu, 1, 0)
            point = self.w.POINT()
            if not self.u.GetCursorPos(ctypes.byref(point)):
                point.x = ctypes.c_int16(wparam & 0xffff).value
                point.y = ctypes.c_int16((wparam >> 16) & 0xffff).value
            # Explorer's hidden-icons panel is topmost. Promote only this tiny
            # menu owner, not the main app or companion windows. A visible popup
            # can be activated; the previous hidden 0x0 window could not reliably
            # bring its menu ahead of that panel.
            presented = True
            self.u.SetWindowPos(owner, -1, point.x, point.y, 1, 1, 0x0040 | 0x0010)
            self.u.SetForegroundWindow(owner)
            selected = self.u.TrackPopupMenu(menu, 0x0100 | 0x0002 | 0x0020 | 0x0008 | 0x4000,
                                             point.x, point.y, 0, owner, None)
        finally:
            try:
                if menu:
                    try:
                        # WM_CLOSE may destroy the owner inside the native menu
                        # loop. Do not act on its stale handle in that case.
                        if presented and self.hwnd == owner:
                            self.u.PostMessageW(owner, 0, 0, 0)  # WM_NULL
                            self.u.SetWindowPos(owner, -2, 0, 0, 0, 0,
                                                0x0080 | 0x0010 | 0x0001 | 0x0002)
                    finally:
                        self.u.DestroyMenu(menu)
            finally:
                self._menu_open = False
        # Finish native menu cleanup before any main-thread exit/save dialogs.
        if self._stop_requested.is_set() or not self.hwnd:
            return
        if selected in self.COMMANDS:
            self.callback(self.COMMANDS[selected])
        else:
            self.s.Shell_NotifyIconW(3, ctypes.byref(self.nid))  # NIM_SETFOCUS

    def _window_proc(self, hwnd, message, wparam, lparam):
        try:
            if message == self.STOP_MESSAGE or message == 0x0010:  # WM_CLOSE
                self.u.EndMenu()
                self.u.DestroyWindow(hwnd)
                return 0
            if message == 0x0002:  # WM_DESTROY
                self.hwnd = None
                self.u.PostQuitMessage(0)
                return 0
            if message == self.CALLBACK_MESSAGE:
                event = int(lparam) & 0xffff
                if event in (0x0203, 0x0400, 0x0401):
                    self.callback('show')  # double-click, select, keyboard select
                elif event in (0x007B, 0x0205):
                    self._popup_menu(int(wparam))
                return 0
            if getattr(self, 'taskbar_created', None) and message == self.taskbar_created:
                self.icon_added = False
                if not self._stop_requested.is_set():
                    self.callback('ready' if self._add_icon() else 'failed')
                return 0
        except Exception:
            self.callback('failed')
            return 0
        return self.u.DefWindowProcW(hwnd, message, wparam, lparam)

    def run(self):
        if self._stop_requested.is_set():
            return
        message = self.w.MSG()
        while True:
            result = self.u.GetMessageW(ctypes.byref(message), None, 0, 0)
            if result <= 0:
                break
            self.u.TranslateMessage(ctypes.byref(message))
            self.u.DispatchMessageW(ctypes.byref(message))

    def request_stop(self):
        self._stop_requested.set()
        hwnd = self.hwnd
        if hwnd and self._native_ready:
            self.u.PostMessageW(hwnd, self.STOP_MESSAGE, 0, 0)

    def close(self):
        if not self._native_ready:
            return
        if self.icon_added:
            self.s.Shell_NotifyIconW(2, ctypes.byref(self.nid))
            self.icon_added = False
        if self.hwnd:
            self.u.DestroyWindow(self.hwnd)
            self.hwnd = None
        if self.icon:
            self.u.DestroyIcon(self.icon)
            self.icon = None
        if self.atom:
            self.u.UnregisterClassW(self.class_name, self.instance)
            self.atom = None
