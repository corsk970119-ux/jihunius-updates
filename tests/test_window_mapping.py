"""Real Tk startup order: idle callbacks can precede creation of the native frame.

Run with a display (Xvfb also exercises Tk's real MapFrame idle ordering).
The Windows placement API itself still needs a Windows runtime.
"""
import os
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch
from test_window_state import m


@unittest.skipUnless(os.environ.get('DISPLAY') or os.name == 'nt', 'requires a Tk display')
class WindowMappingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        env = patch.dict(os.environ, LOCALAPPDATA=self.tmp.name)
        env.start(); self.addCleanup(env.stop)
        self.root = tk.Tk()
        self.addCleanup(self.cleanup_root)
        self.root.geometry('320x940')
        self.root.minsize(280, 650)
        tk.Label(self.root, text='wash-log').pack()
        self.record = {'schema': 1, 'backend': 'windows-placement',
                       'normal': [2080, 80, 2470, 900], 'zoomed': False}
        self.path = Path(self.tmp.name)/'JihuniusSuite/window-state/wash-log.json'
        m._cu_write(self.path, self.record)
        self.mapped_at_restore = []
        owner = self

        class Backend:
            kind = 'windows-placement'
            def restore(self, record):
                owner.mapped_at_restore.append(bool(owner.root.winfo_ismapped()))
                owner.assertEqual(record, owner.record)
            def capture(self):
                return owner.record

        self.backend = Backend()

    def cleanup_root(self):
        try: self.root.destroy()
        except tk.TclError: pass

    def test_fresh_wash_window_restores_only_after_native_frame_is_mapped(self):
        state = m.CompanionWindowState(self.root, 'wash-log', self.backend)
        self.root.update()
        self.assertEqual(self.mapped_at_restore, [True])
        self.assertTrue(state.ready)
        # Later map events (minimize/restore or a child mapping) must not snap back.
        self.root.event_generate('<Map>')
        self.root.update()
        self.assertEqual(self.mapped_at_restore, [True])

    def test_already_mapped_protrusion_style_startup_still_restores(self):
        self.root.update_idletasks()
        self.assertTrue(self.root.winfo_ismapped())
        m.CompanionWindowState(self.root, 'wash-log', self.backend)
        self.root.update()
        self.assertEqual(self.mapped_at_restore, [True])

    def test_close_before_first_map_preserves_saved_right_monitor(self):
        state = m.CompanionWindowState(self.root, 'wash-log', self.backend)
        self.root.after_idle(self.root.destroy)
        self.root.update()
        self.assertEqual(self.mapped_at_restore, [])
        self.assertTrue(state.closed)
        self.assertEqual(m._cu_read(self.path), self.record)


if __name__ == '__main__': unittest.main()
