"""Native-boundary simulation: saved/restored geometry must match visible bounds.

Only user32 is simulated; production capture, persistence and restore all run.
This does not substitute for an actual Windows/Tk smoke test.
"""
import ctypes
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from test_window_state import m
from test_update_notice import Scheduler


class NativeWindow:
    def __init__(self):
        self.normal = [100, 100, 1220, 930]  # Old, unsnapped default.
        self.visible = [2080, 80, 3480, 1080]
        self.monitor = [1920, 0, 3840, 1200]
        self.work = [1920, 0, 3840, 1160]
        self.show = 1
        self.is_visible = True
        self.tool = False
        self.restored = None
        self.api = SimpleNamespace(
            GetAncestor=Mock(return_value=42),
            GetWindowPlacement=Mock(side_effect=self.get_placement),
            SetWindowPlacement=Mock(side_effect=self.set_placement),
            IsWindowVisible=Mock(side_effect=lambda hwnd: self.is_visible),
            GetWindowRect=Mock(side_effect=self.get_rect),
            MonitorFromWindow=Mock(return_value=7),
            GetMonitorInfoW=Mock(side_effect=self.get_monitor),
            GetWindowLongW=Mock(side_effect=lambda hwnd, index: 0x80 if self.tool else 0))

    @staticmethod
    def set_rect(rect, values):
        for field, value in zip(('left', 'top', 'right', 'bottom'), values):
            setattr(rect, field, value)

    def get_placement(self, hwnd, pointer):
        placement = pointer._obj
        placement.showCmd = self.show
        self.set_rect(placement.rcNormalPosition, self.normal)
        return 1

    def set_placement(self, hwnd, pointer):
        placement = pointer._obj
        rect = placement.rcNormalPosition
        self.restored = ([rect.left, rect.top, rect.right, rect.bottom], placement.showCmd)
        return 1

    def get_rect(self, hwnd, pointer):
        self.set_rect(pointer._obj, self.visible)
        return 1

    def get_monitor(self, handle, pointer):
        self.set_rect(pointer._obj.rcMonitor, self.monitor)
        self.set_rect(pointer._obj.rcWork, self.work)
        return 1


class WindowsVisiblePlacementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        env = patch.dict(os.environ, LOCALAPPDATA=self.tmp.name)
        env.start(); self.addCleanup(env.stop)
        self.native = NativeWindow()
        dll = patch.object(ctypes, 'WinDLL', return_value=self.native.api, create=True)
        dll.start(); self.addCleanup(dll.stop)

    def create(self):
        root = Scheduler()
        root.after_idle = lambda fn: root.after(0, fn)
        root.bind = Mock(); root.unbind = Mock(); root.destroy = Mock()
        root.update_idletasks = Mock(); root.winfo_id = Mock(return_value=41)
        root.winfo_ismapped = Mock(return_value=True)
        backend = m._WindowsPlacement(root)
        state = m.CompanionWindowState(root, 'jihunius', backend=backend)
        root.advance(0)
        return root, state

    def test_snapped_visible_size_survives_full_exit_and_reopen(self):
        root, state = self.create()
        root.destroy()
        self.assertEqual(m._cu_read(state.path)['normal'], [2080, 80, 3480, 1080])
        self.create()
        self.assertEqual(self.native.restored, ([2080, 80, 3480, 1080], 1))

    def test_left_monitor_with_top_and_left_taskbar_uses_workspace_coordinates(self):
        self.native.monitor = [-1920, -120, 0, 1080]
        self.native.work = [-1880, -80, 0, 1080]
        self.native.visible = [-1800, 20, -400, 1020]
        root, state = self.create(); root.destroy()
        self.assertEqual(m._cu_read(state.path)['normal'], [-1840, -20, -440, 980])
        self.create()
        self.assertEqual(self.native.restored, ([-1840, -20, -440, 980], 1))

    def test_tool_window_keeps_screen_coordinates(self):
        self.native.tool = True
        self.native.work = [1960, 40, 3840, 1160]
        root, state = self.create(); root.destroy()
        self.assertEqual(m._cu_read(state.path)['normal'], [2080, 80, 3480, 1080])

    def test_hidden_tray_exit_keeps_last_visible_snapshot(self):
        root, state = self.create()
        state.changed(SimpleNamespace(widget=root))
        self.native.is_visible = False
        root.destroy()
        self.assertEqual(m._cu_read(state.path)['normal'], [2080, 80, 3480, 1080])

    def test_maximized_reopens_maximized_without_losing_normal_restore_size(self):
        self.native.show = 3
        root, state = self.create(); root.destroy()
        saved = m._cu_read(state.path)
        self.assertEqual(saved['normal'], [100, 100, 1220, 930])
        self.assertTrue(saved['zoomed'])
        self.create()
        self.assertEqual(self.native.restored, ([100, 100, 1220, 930], 3))

    def test_minimized_exit_keeps_visible_size(self):
        root, state = self.create()
        state.changed(SimpleNamespace(widget=root))
        self.native.show = 2
        root.destroy()
        self.assertEqual(m._cu_read(state.path)['normal'], [2080, 80, 3480, 1080])

    def test_failed_native_read_cannot_overwrite_saved_geometry(self):
        root, state = self.create(); state.flush()
        before = state.path.read_bytes()
        self.native.api.GetWindowRect.side_effect = lambda *args: 0
        self.native.normal = [1, 1, 1001, 741]
        root.destroy()
        self.assertEqual(state.path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
