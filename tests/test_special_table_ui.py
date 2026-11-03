"""Real Tk edit/save/scroll lifecycle; network I/O uses a temporary local share."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import tkinter as tk
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from embed_companions import companion_source


@unittest.skipUnless(os.environ.get('DISPLAY') or os.name == 'nt', 'requires Tk display')
class SpecialTableUITests(unittest.TestCase):
    def test_always_editable_no_mode_button_and_only_three_columns(self):
        a = self.app
        self.assertEqual(str(a.notes.cget('state')), 'normal')
        self.assertEqual([w.cget('text') for w in a.header], ['타입명','수정 치수','비고'])
        self.assertFalse(hasattr(a, 'edit_button'))
        a.cell_widgets[('seed-4',0)].event_generate('<Button-1>')
        self.root.update()
        self.assertIsNotNone(a.editor)

    def test_right_click_deletes_clicked_filtered_row_without_confirmation(self):
        a = self.app
        self.assertTrue(callable(getattr(a,'row_menu',None)), 'Right-click row menu required')
        a.search.set('스트라우만');self.root.update()
        with patch.object(self.m.messagebox,'askyesno',side_effect=AssertionError('No routine delete confirmation')):
            a.cell_widgets[('seed-7',1)].event_generate('<Button-3>',x=3,y=3)
            self.root.update()
            a.context_menu.invoke(0);a.context_menu.unpost()
            self.wait(lambda:not a.busy and not a.pending)
        ids=[r['id'] for r in self.store.sync()['state']['rows']]
        self.assertNotIn('seed-7',ids);self.assertIn('seed-6',ids)

    def test_delete_while_add_is_inflight_cannot_reappear(self):
        a = self.app
        self.assertTrue(callable(getattr(a,'delete_row',None)), 'Delete row required')
        original = self.store.sync; gate=threading.Event(); entered=threading.Event()
        def paused(ops=()):entered.set();gate.wait(2);return original(ops)
        with patch.object(self.store,'sync',paused):
            a.add_row();rid=a.editor['row'];self.assertTrue(entered.wait(1))
            a.delete_row(rid);gate.set();self.wait(lambda:not a.busy and not a.pending)
        self.assertNotIn(rid,[r['id'] for r in self.store.sync()['state']['rows']])

    def test_deleted_elsewhere_edit_can_restore_as_new_row_once(self):
        a = self.app
        self.assertTrue(callable(getattr(a,'delete_row',None)), 'Delete-aware editing required')
        a.edit_cell('seed-4',1);row=a.state['rows'][0]
        a.editor['widget'].delete('1.0','end');a.editor['widget'].insert('1.0','retained edit')
        remote=self.store.sync([{'kind':'delete','row':row['id'],'base':row['cells']}])
        a.sync_success([],remote);a.commit_editor()
        with patch.object(self.m.messagebox,'askyesno',return_value=True) as choice:
            a.start_sync();self.wait(lambda:not a.busy and not a.pending)
        choice.assert_called_once()
        rows=self.store.sync()['state']['rows']
        restored=[r for r in rows if r['cells'][1]=='retained edit']
        self.assertEqual(len(restored),1);self.assertNotEqual(restored[0]['id'],'seed-4')
        self.assertEqual(restored[0]['cells'][0],row['cells'][0])

    def test_update_adapter_flushes_active_cell_and_notes_before_close(self):
        a=self.app;a.edit_cell('seed-4',1)
        a.editor['widget'].delete('1.0','end');a.editor['widget'].insert('1.0','before update')
        a.notes.delete('1.0','end');a.notes.insert('1.0','saved notes')
        adapter=self.m.SpecialTableUpdateSave(a);adapter.begin()
        self.wait(adapter.saved)
        state=self.store.sync()['state']
        self.assertEqual(state['rows'][0]['cells'][1],'before update');self.assertEqual(state['notes'],'saved notes')
        adapter.finish();self.assertTrue(a.closed)

    def test_remote_delete_restores_pending_and_open_cells_together(self):
        a=self.app;row=a.state['rows'][0]
        a.edit_cell(row['id'],1);a.editor['widget'].delete('1.0','end');a.editor['widget'].insert('1.0','first edit');a.commit_editor()
        a.edit_cell(row['id'],2);a.editor['widget'].delete('1.0','end');a.editor['widget'].insert('1.0','second edit')
        self.store.sync([{'kind':'delete','row':row['id'],'base':row['cells']}])
        with patch.object(self.m.messagebox,'askyesno',return_value=True) as choice:
            a.start_sync();self.wait(lambda:not a.busy and not a.pending)
            a.commit_editor();a.start_sync();self.wait(lambda:not a.busy and not a.pending)
        choice.assert_called_once()
        rows=[r for r in self.store.sync()['state']['rows'] if r['cells'][0]==row['cells'][0]]
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['cells'][1:],['first edit','second edit'])

    def test_clearing_cell_of_remotely_deleted_row_is_a_conflict(self):
        a=self.app;row=a.state['rows'][0]
        a.edit_cell(row['id'],1);a.editor['widget'].delete('1.0','end');a.commit_editor()
        self.store.sync([{'kind':'delete','row':row['id'],'base':row['cells']}])
        with patch.object(self.m.messagebox,'askyesno',return_value=True) as choice:
            a.start_sync();self.wait(lambda:not a.busy and not a.pending)
        choice.assert_called_once()
        rows=[r for r in self.store.sync()['state']['rows'] if r['cells'][0]==row['cells'][0]]
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['cells'][1],'')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        env = patch.dict(os.environ, LOCALAPPDATA=self.temp.name)
        env.start(); self.addCleanup(env.stop)
        self.path = Path(self.temp.name) / 'special.pyw'
        self.path.write_bytes(companion_source(ROOT, 'special-table'))
        import types
        self.m = types.ModuleType('special_ui_test'); self.m.__file__ = str(self.path)
        sys.modules[self.m.__name__] = self.m
        exec(compile(self.path.read_bytes(), str(self.path), 'exec'), self.m.__dict__)
        self.root = tk.Tk(); self.errors = []
        self.root.report_callback_exception = lambda *args: self.errors.append(args)
        self.addCleanup(self.cleanup_root)
        self.store = self.m.TableStore(Path(self.temp.name) / 'shared')
        self.app = self.m.SpecialTableApp(self.root, self.store.folder, store=self.store)
        self.wait(lambda: self.app.ready and not self.app.busy)

    def cleanup_root(self):
        if not self.app.closed: self.app.destroy()
        self.assertFalse(self.errors)

    def wait(self, predicate, timeout=3):
        until = time.monotonic() + timeout
        while time.monotonic() < until:
            self.root.update()
            if predicate(): return
            time.sleep(.01)
        self.fail('timed out waiting for Tk condition')

    def test_pinned_notes_and_headers_stay_visible_after_scroll(self):
        self.root.update()
        note_y = self.app.notes.winfo_rooty()
        header_y = self.app.header[1].winfo_rooty()
        self.app.canvas.yview_moveto(1); self.root.update()
        self.assertGreater(self.app.canvas.yview()[0], 0)
        self.assertEqual(self.app.notes.winfo_rooty(), note_y)
        self.assertEqual(self.app.header[1].winfo_rooty(), header_y)
        self.assertLess(note_y + self.app.notes.winfo_height(), self.root.winfo_rooty() + self.root.winfo_height())
        for widget, _ in self.app.labels:
            self.assertLessEqual(widget.winfo_x() + widget.winfo_width(), self.app.canvas.winfo_width() + 1)

    def test_rapid_editor_switch_does_not_commit_new_cell_from_old_focus_event(self):
        a = self.app
        a.edit_cell('seed-4', 1); self.root.update()
        old = a.editor['widget']; old.delete('1.0', 'end'); old.insert('1.0', '첫째')
        old.event_generate('<FocusOut>')
        a.edit_cell('seed-4', 2); new = a.editor
        start = time.monotonic()
        self.wait(lambda: time.monotonic() > start + .2)
        self.assertIs(a.editor, new)

    def test_add_edit_notes_and_close_save_latest_values(self):
        a = self.app
        a.add_row(); self.root.update()
        rid = a.editor['row']; edit = a.editor['widget']
        edit.delete('1.0', 'end'); edit.insert('1.0', '새로운 타입')
        a.commit_editor(); a.notes.delete('1.0', 'end'); a.notes.insert('1.0', '끝글자 한글')
        a.finish_close()
        self.wait(lambda: a.closed)
        state = self.store.sync()['state']
        self.assertEqual(len(state['rows']), 27)
        self.assertEqual(next(r for r in state['rows'] if r['id'] == rid)['cells'][0], '새로운 타입')
        self.assertEqual(state['notes'], '끝글자 한글')
        self.assertFalse(a.draft.path.exists())

    def test_newer_edit_survives_older_inflight_save(self):
        a = self.app
        original = self.store.sync
        gate = threading.Event(); entered = threading.Event()
        def paused(ops=()):
            entered.set(); gate.wait(2); return original(ops)
        with patch.object(self.store, 'sync', paused):
            a.change({'kind': 'cell', 'row': 'seed-4', 'col': 1, 'value': 'first'})
            a.start_sync(); self.assertTrue(entered.wait(1))
            a.change({'kind': 'cell', 'row': 'seed-4', 'col': 1, 'value': 'latest'})
            gate.set(); self.wait(lambda: not a.busy and not a.pending)
        self.assertEqual(self.store.sync()['state']['rows'][0]['cells'][1], 'latest')

    def test_remote_cell_change_during_edit_requires_conflict_choice(self):
        a = self.app
        a.edit_cell('seed-4', 1)
        old = a.editor['opened']
        remote = self.store.sync([{'kind':'cell','row':'seed-4','col':1,'base':old,'value':'other PC'}])
        a.sync_success([], remote)
        a.editor['widget'].delete('1.0', 'end'); a.editor['widget'].insert('1.0', 'local PC')
        a.commit_editor()
        with patch.object(self.m.messagebox, 'askyesno', return_value=False) as choice:
            a.start_sync(); self.wait(lambda:not a.busy and not a.pending)
        choice.assert_called_once()
        self.assertEqual(self.store.sync()['state']['rows'][0]['cells'][1], 'other PC')

    def test_unedited_stale_cell_does_not_overwrite_remote(self):
        a = self.app
        a.edit_cell('seed-4', 1); old = a.editor['opened']
        remote = self.store.sync([{'kind':'cell','row':'seed-4','col':1,'base':old,'value':'other PC'}])
        a.sync_success([], remote); a.commit_editor()
        self.assertFalse(a.pending)
        self.assertEqual(a.displayed_state()['rows'][0]['cells'][1], 'other PC')

    def test_remote_notes_change_while_focused_requires_conflict_choice(self):
        a = self.app; a.notes.focus_force(); self.root.update()
        old = a.state['notes']
        remote = self.store.sync([{'kind':'notes','base':old,'value':'other PC'}])
        a.sync_success([], remote)
        a.notes.delete('1.0','end'); a.notes.insert('1.0','my notes'); a.notes_changed()
        with patch.object(self.m.messagebox, 'askyesno', return_value=False) as choice:
            a.start_sync(); self.wait(lambda:not a.busy and not a.pending)
        choice.assert_called_once()
        self.assertEqual(self.store.sync()['state']['notes'], 'other PC')
        self.assertEqual(a.notes.get('1.0','end-1c'), 'other PC')

    def test_continuing_to_type_after_own_note_save_has_no_false_conflict(self):
        a = self.app; a.notes.focus_force(); self.root.update()
        with patch.object(self.m.messagebox, 'askyesno', return_value=False) as choice:
            for value in ('first note', 'second note'):
                a.notes.delete('1.0','end'); a.notes.insert('1.0',value); a.notes_changed()
                a.start_sync(); self.wait(lambda:not a.busy and not a.pending)
            choice.assert_not_called()
        self.assertEqual(self.store.sync()['state']['notes'], 'second note')

    def test_notes_conflict_refreshes_rejected_text_even_during_cell_edit(self):
        a = self.app; a.notes.focus_force(); self.root.update()
        old = a.state['notes']
        self.store.sync([{'kind':'notes','base':old,'value':'other PC'}])
        a.notes.delete('1.0','end'); a.notes.insert('1.0','rejected local'); a.notes_changed()
        a.edit_cell('seed-4',1)
        current = a.editor
        with patch.object(self.m.messagebox, 'askyesno', return_value=False) as choice:
            a.start_sync(); self.wait(lambda:not a.busy and not a.pending)
        choice.assert_called_once();self.assertIs(a.editor,current)
        self.assertEqual(a.notes.get('1.0','end-1c'),'other PC')
        self.assertEqual(a.notes_base,'other PC')

    def test_window_geometry_uses_independent_local_key(self):
        self.assertEqual(self.app._window_state.path.name, 'special-table.json')
        self.root.geometry('990x700+1400+90'); self.root.update()
        self.app.destroy()
        self.assertTrue(self.app._window_state.path.exists())


if __name__ == '__main__': unittest.main()
