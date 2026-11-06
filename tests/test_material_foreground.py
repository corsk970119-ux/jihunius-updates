"""Cold start and deferred native activation, without reopening a hidden window."""
from types import SimpleNamespace
from unittest.mock import patch
import unittest
import tempfile
from pathlib import Path

import test_material_ui as fixture
import test_material_companion as manager_fixture
import material_ui as ui


class ColdStartTests(unittest.TestCase):
    setUp = manager_fixture.MaterialCompanionTests.setUp

    def test_user_launch_grants_foreground_but_hidden_autostart_does_not(self):
        self.manager.toggle('material')
        self.backend.allow_foreground.assert_called_once_with(self.process.pid)
        self.assertEqual(self.spawn.call_args.kwargs['env']['JIHUNIUS_MATERIAL_HIDDEN'], '0')
        self.backend.reset_mock()
        self.process.poll.return_value = 0
        self.manager.running_keys()
        self.process.poll.return_value = None
        self.manager.open('material', hidden=True)
        self.backend.allow_foreground.assert_not_called()


class ApiFunction:
    def __init__(self, function): self.function = function
    def __call__(self, *args): return self.function(*args)


class MaterialForegroundTests(unittest.TestCase):
    setUp = fixture.MaterialUITests.setUp
    cleanup = fixture.MaterialUITests.cleanup
    pump = fixture.MaterialUITests.pump

    def native(self):
        import ctypes
        backend = SimpleNamespace(foreground=None, mapped_when_activated=False)
        def activate(handle):
            backend.foreground = handle
            backend.mapped_when_activated = bool(self.root.winfo_ismapped())
            backend.placement_ready_when_activated = getattr(getattr(self.app, 'placement', None), 'ready', True)
            return 1
        backend.GetAncestor = ApiFunction(lambda handle, kind: handle + 1000)
        backend.SetForegroundWindow = ApiFunction(activate)
        for p in (patch.object(ui, 'os', SimpleNamespace(name='nt')),
                  patch.object(ctypes, 'WinDLL', return_value=backend, create=True)):
            p.start()
            self.addCleanup(p.stop)
        return backend

    def test_first_show_activates_native_window_after_mapping_and_keeps_geometry(self):
        native = self.native()
        self.root.geometry('1000x790+50+70')
        self.root.update()
        self.app.on_close()
        self.app.show_front()
        self.root.update()
        self.assertEqual(native.foreground, self.root.winfo_id() + 1000)
        self.assertTrue(native.mapped_when_activated)
        self.assertEqual((self.root.winfo_x(), self.root.winfo_y()), (50, 70))
        self.assertFalse(bool(self.root.attributes('-topmost')))

    def test_active_modal_is_focused_and_hide_cancels_pending_activation(self):
        native = self.native()
        dialog = self.app.tk.Toplevel(self.root)
        self.app.tk.Entry(dialog).pack()
        dialog.grab_set()
        self.app.show_front()
        self.root.update()
        self.assertEqual(native.foreground, dialog.winfo_id() + 1000)
        self.assertIs(self.root.grab_current(), dialog)
        dialog.destroy()
        native.foreground = None
        self.app.show_front()
        self.app.on_close()
        self.root.update()
        self.assertIsNone(native.foreground)
        self.assertEqual(self.root.state(), 'withdrawn')


class ColdMapMaterialTests(unittest.TestCase):
    native = MaterialForegroundTests.native
    cleanup = fixture.MaterialUITests.cleanup

    def setUp(self):
        import tkinter as tk
        from material_client import ClientSession
        from test_material_sync import QuietCollector
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = tk.Tk()
        self.root.withdraw()
        self.session = ClientSession(Path(self.tmp.name)/'main', Path(self.tmp.name)/'share', QuietCollector)
        self.app = ui.SyncedApplication(self.root, self.session)
        self.addCleanup(self.cleanup)

    def test_never_shown_window_restores_saved_position_before_native_activation(self):
        from test_window_state import m
        native = self.native()
        record = {'schema': 1, 'backend': 'tk-placement', 'normal': [100, 120, 1100, 910], 'zoomed': False}
        with patch.dict(m._cu_os.environ, LOCALAPPDATA=self.tmp.name):
            placement = m.CompanionWindowState(self.root, 'material', backend=m._TkPlacement(self.root))
        self.app.placement = placement
        m._cu_write(placement.path, record)
        self.root.after_idle(self.app.show_front)
        self.root.update()
        self.assertTrue(native.mapped_when_activated)
        self.assertEqual(native.foreground, self.root.winfo_id()+1000)
        self.assertTrue(native.placement_ready_when_activated)
        self.assertTrue(placement.ready)
        self.assertEqual((self.root.winfo_x(), self.root.winfo_y()), (100, 120))
