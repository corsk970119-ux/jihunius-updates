"""Per-PC companion window placement. Embedded after companion_update.py.

Windows uses the matching Get/SetWindowPlacement APIs so workspace coordinates
are never confused with screen coordinates on multiple monitors or taskbars.
https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setwindowplacement
"""


def _window_record(value, backend):
    if not isinstance(value, dict) or value.get('schema') != 1 or value.get('backend') != backend:
        return None
    rect = value.get('normal')
    if (not isinstance(rect, list) or len(rect) != 4
            or any(type(n) is not int or abs(n) > 100000 for n in rect)
            or not 1 <= rect[2] - rect[0] <= 32768
            or not 1 <= rect[3] - rect[1] <= 32768
            or type(value.get('zoomed')) is not bool):
        return None
    return {'schema': 1, 'backend': backend, 'normal': list(rect), 'zoomed': value['zoomed']}


class _WindowsPlacement:
    kind = 'windows-placement'

    def __init__(self, root):
        import ctypes
        from ctypes import wintypes as w
        self.ctypes = ctypes
        self.root = root

        class Placement(ctypes.Structure):
            _fields_ = [('length', w.UINT), ('flags', w.UINT), ('showCmd', w.UINT),
                        ('ptMinPosition', w.POINT), ('ptMaxPosition', w.POINT),
                        ('rcNormalPosition', w.RECT)]

        self.Placement = Placement
        self.user = ctypes.WinDLL('user32', use_last_error=True)
        self.user.GetAncestor.argtypes = [w.HWND, w.UINT]
        self.user.GetAncestor.restype = w.HWND
        for name in ('GetWindowPlacement', 'SetWindowPlacement'):
            function = getattr(self.user, name)
            function.argtypes = [w.HWND, ctypes.POINTER(Placement)]
            function.restype = w.BOOL

    def handle(self):
        hwnd = self.user.GetAncestor(self.root.winfo_id(), 2)
        if not hwnd: raise OSError('Window is not ready')
        return hwnd

    def capture(self):
        placement = self.Placement()
        placement.length = self.ctypes.sizeof(placement)
        if not self.user.GetWindowPlacement(self.handle(), self.ctypes.byref(placement)):
            raise OSError('Cannot read window placement')
        # Never record minimized/hidden coordinates or reopen a hidden window.
        if placement.showCmd not in (1, 3): return None
        rect = placement.rcNormalPosition
        return _window_record({'schema': 1, 'backend': self.kind,
            'normal': [rect.left, rect.top, rect.right, rect.bottom],
            'zoomed': placement.showCmd == 3}, self.kind)

    def restore(self, record):
        placement = self.Placement()
        placement.length = self.ctypes.sizeof(placement)
        placement.showCmd = 3 if record['zoomed'] else 1
        placement.ptMinPosition.x = placement.ptMinPosition.y = -1
        placement.ptMaxPosition.x = placement.ptMaxPosition.y = -1
        for field, value in zip(('left', 'top', 'right', 'bottom'), record['normal']):
            setattr(placement.rcNormalPosition, field, value)
        # Windows adjusts a completely off-screen placement after monitor changes.
        if not self.user.SetWindowPlacement(self.handle(), self.ctypes.byref(placement)):
            raise OSError('Cannot restore window placement')


class _TkPlacement:
    kind = 'tk-placement'

    def __init__(self, root):
        self.root = root

    def capture(self):
        if self.root.state() != 'normal': return None
        x, y = self.root.winfo_x(), self.root.winfo_y()
        return _window_record({'schema': 1, 'backend': self.kind,
            'normal': [x, y, x + self.root.winfo_width(), y + self.root.winfo_height()],
            'zoomed': False}, self.kind)

    def restore(self, record):
        x, y, right, bottom = record['normal']
        screen_w, screen_h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        min_w, min_h = self.root.minsize()
        width = max(min_w, min(right - x, screen_w))
        height = max(min_h, min(bottom - y, screen_h))
        # This fallback is for non-Windows desktops, not Windows monitor bounds.
        x = max(0, min(x, screen_w - width))
        y = max(0, min(y, screen_h - height))
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))


class CompanionWindowState:
    def __init__(self, root, key, backend=None):
        if key not in ('protrusion', 'wash-log'): raise ValueError('Unknown companion')
        self.root = root
        base = _CuPath(_cu_os.environ.get('LOCALAPPDATA') or _CuPath.home())
        self.path = base / 'JihuniusSuite' / 'window-state' / (key + '.json')
        self.backend = backend
        if backend is None:
            try:
                self.backend = _WindowsPlacement(root) if _cu_os.name == 'nt' else _TkPlacement(root)
            except (OSError, AttributeError):
                # Optional UI preferences must never prevent the app from opening.
                self.backend = None
        self.ready = False
        self.closed = False
        self.timer = None
        self.last = None
        self.pending = None
        self.map_binding = root.bind('<Map>', self.mapped, add='+')
        self.startup = root.after_idle(self.restore)
        root.bind('<Configure>', self.changed, add='+')
        original_destroy = root.destroy

        def destroy():
            if not self.closed:
                self.flush()
                self.closed = True
                self.stop_waiting_for_map()
                for name in ('timer', 'startup'):
                    job = getattr(self, name)
                    if job is not None:
                        try: root.after_cancel(job)
                        except Exception: pass
                        setattr(self, name, None)
            return original_destroy()

        root.destroy = destroy

    def stop_waiting_for_map(self):
        if self.map_binding is not None:
            try: self.root.unbind('<Map>', self.map_binding)
            except Exception: pass
            self.map_binding = None

    def mapped(self, event):
        if (event.widget is self.root and not self.ready and not self.closed
                and self.startup is None):
            self.startup = self.root.after_idle(self.restore)

    def restore(self):
        self.startup = None
        if self.closed or self.ready: return
        # Tk's initial MapFrame drains idle callbacks BEFORE creating the native
        # top-level wrapper. update_idletasks() from inside that callback cannot
        # complete the outer MapFrame. Wait for <Map>, otherwise Windows applies
        # the saved placement to the inner window and then opens the real frame
        # at CW_USEDEFAULT. Already-mapped companions still restore at idle.
        if not self.root.winfo_ismapped(): return
        self.stop_waiting_for_map()
        try:
            if self.backend is not None:
                self.last = _window_record(_cu_read(self.path), self.backend.kind)
                if self.last is not None:
                    self.root.update_idletasks()
                    self.backend.restore(self.last)
        except Exception:
            pass
        self.ready = True

    def changed(self, event):
        if event.widget is not self.root or not self.ready or self.closed: return
        # Keep the latest visible placement in memory before a quick minimize.
        # Only the delayed flush writes to disk; minimized coordinates are ignored.
        try:
            if self.backend is not None:
                record = self.backend.capture()
                if record is not None: self.pending = record
        except Exception: pass
        if self.timer is not None:
            self.root.after_cancel(self.timer)
        self.timer = self.root.after(750, self.flush)

    def flush(self):
        if self.timer is not None:
            try: self.root.after_cancel(self.timer)
            except Exception: pass
            self.timer = None
        if not self.ready or self.closed or self.backend is None: return
        try:
            record = self.backend.capture() or self.pending
            if record is not None and record != self.last:
                _cu_write(self.path, record)
                self.last = record
            self.pending = None
        except Exception:
            # Geometry preferences must not interrupt a shared-data save or exit.
            pass
