"""Geometry stays local, independent, debounced, and safe across exits."""
import os
from pathlib import Path
from types import ModuleType, SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch
from test_update_notice import Scheduler

ROOT=Path(__file__).resolve().parents[1]
m=ModuleType('window_state_test')
exec((ROOT/'src/companion_update.py').read_text()+'\n'+(ROOT/'src/window_state.py').read_text(),m.__dict__)


class WindowStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        env=patch.dict(os.environ,LOCALAPPDATA=self.tmp.name);env.start();self.addCleanup(env.stop)

    def create(self,key='wash-log',rect=None):
        root=Scheduler();root.after_idle=lambda fn:root.after(0,fn)
        root.bind=Mock();root.destroy=Mock();root.update_idletasks=Mock()
        backend=Mock(kind='windows-placement')
        backend.capture.return_value={'schema':1,'backend':backend.kind,
            'normal':rect or [-1700,80,-1200,980],'zoomed':False}
        state=m.CompanionWindowState(root,key,backend=backend)
        root.advance(0)
        return root,backend,state

    def test_negative_monitor_position_survives_close_and_reopen(self):
        root,backend,state=self.create()
        root.destroy()
        root2,backend2,state2=self.create()
        backend2.restore.assert_called_once_with(backend.capture.return_value)
        self.assertEqual(state2.last['normal'],[-1700,80,-1200,980])

    def test_windows_are_independent_and_settings_path_survives_versions(self):
        root,backend,state=self.create();root.destroy()
        other,other_backend,other_state=self.create('protrusion')
        other_backend.restore.assert_not_called()
        self.assertNotEqual(state.path,other_state.path)
        self.assertNotIn('releases',str(state.path))

    def test_drag_is_debounced_and_unchanged_geometry_is_not_rewritten(self):
        root,backend,state=self.create()
        with patch.object(m,'_cu_write',wraps=m._cu_write) as write:
            for _ in range(20):
                state.changed(SimpleNamespace(widget=root));root.advance(.1)
            write.assert_not_called()
            root.advance(.75);write.assert_called_once()
            state.changed(SimpleNamespace(widget=root));root.advance(1)
            root.destroy();write.assert_called_once()
            self.assertFalse(root.jobs)

    def test_minimize_does_not_replace_saved_normal_or_maximized_geometry(self):
        root,backend,state=self.create()
        backend.capture.return_value['zoomed']=True
        state.flush();saved=state.path.read_bytes()
        backend.capture.return_value=None
        root.destroy()
        self.assertEqual(state.path.read_bytes(),saved)

    def test_close_before_debounce_flushes_latest_size(self):
        root,backend,state=self.create()
        state.changed(SimpleNamespace(widget=root))
        root.destroy()
        self.assertTrue(state.path.exists());self.assertFalse(root.jobs)

    def test_resize_then_immediate_minimize_keeps_latest_visible_rectangle(self):
        root,backend,state=self.create()
        state.changed(SimpleNamespace(widget=root))
        expected=dict(backend.capture.return_value)
        backend.capture.return_value=None
        state.changed(SimpleNamespace(widget=root))
        root.destroy()
        self.assertEqual(m._cu_read(state.path),expected)

    def test_child_widget_configures_do_not_schedule_disk_writes(self):
        root,backend,state=self.create()
        state.changed(SimpleNamespace(widget=object()))
        self.assertFalse(root.jobs);backend.capture.assert_not_called()

    def test_broken_preferences_or_write_failure_never_block_business_shutdown(self):
        root,backend,state=self.create()
        state.path.parent.mkdir(parents=True,exist_ok=True);state.path.write_text('{invalid')
        root2,backend2,state2=self.create();backend2.restore.assert_not_called()
        with patch.object(m,'_cu_write',side_effect=OSError('disk full')):
            root2.destroy()
        self.assertTrue(state2.closed)

    def test_invalid_rectangle_is_rejected_without_restore(self):
        valid={'schema':1,'backend':'windows-placement','normal':[1,1,400,900],'zoomed':False}
        for rect in ([0,0,0,900],[0,0,True,900],[0,0,100000,900],['x',0,400,900]):
            self.assertIsNone(m._window_record({**valid,'normal':rect},'windows-placement'))

    def test_non_windows_fallback_moves_missing_monitor_back_on_screen(self):
        root=Mock();root.winfo_screenwidth.return_value=1920;root.winfo_screenheight.return_value=1080
        root.minsize.return_value=(280,650)
        m._TkPlacement(root).restore({'normal':[-1700,80,-1200,980]})
        root.geometry.assert_called_once_with('500x900+0+80')


if __name__=='__main__':unittest.main()
