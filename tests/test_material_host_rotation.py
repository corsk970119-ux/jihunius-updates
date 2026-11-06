"""The actual host must display confirmation before a material request can leave it."""
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

import test_main_window_placement as host_fixture
import test_material_full_reset_ui as material_fixture


class HostRotationDialogTests(unittest.TestCase):
    setUp = host_fixture.MainWindowPlacementTests.setUp
    cleanup = host_fixture.MainWindowPlacementTests.cleanup
    close_app = host_fixture.MainWindowPlacementTests.close_app
    launch = host_fixture.MainWindowPlacementTests.launch

    def connect_panel(self):
        app = self.launch()
        self.root = app.window
        self.errors = []
        self.root.report_callback_exception = lambda *args: self.errors.append(args[1])
        folder = Path(self.tmp.name) / 'quick-session'
        folder.mkdir()
        manager = SimpleNamespace(sessions={'material': (folder, 'nonce')},
                                  running_keys=lambda: ['material'])
        quick = self.m.SuiteMaterialQuick
        quick.write(folder / 'material-status.json', dict(nonce='nonce', at=time.time(), quick=dict(
            connected=True, client='pc', owner='owner', epoch='epoch', at=time.time(),
            rows=[dict(machine=1, can_rotate=True, can_defect=True, busy=False,
                       expected=dict(material=5, material_type='10B', next_type='10B', switch_revision=0))])))
        panel = app.material_quick
        panel.channel = quick.QuickChannel(manager, folder / 'inputs.json')
        panel.poll()
        return panel

    def click_with_dialog_response(self, panel, response):
        # Real Tcl confirmation, driven only by a test user response.
        observed = []
        def respond():
            dialog = '.__tk__messagebox'
            if self.root.tk.call('winfo', 'exists', dialog):
                observed.append(str(self.root.tk.call('wm', 'title', dialog)))
                self.root.tk.call(dialog + '.' + response, 'invoke')
        timer = self.root.after(100, respond)
        watchdog = self.root.after(2000, lambda: self.root.tk.call('set', '::tk::Priv(button)', 'cancel'))
        try:
            panel.rows[1]['rotate'].invoke()
        finally:
            self.root.after_cancel(timer)
            self.root.after_cancel(watchdog)
        self.assertEqual(self.errors, [], 'Button callback failed before showing confirmation')
        self.assertEqual(observed, ['소재교체 확인'])

    def test_actual_host_cancel_displays_dialog_and_does_not_enqueue(self):
        panel = self.connect_panel()
        self.click_with_dialog_response(panel, 'cancel')
        self.assertFalse(panel.channel.pending)
        self.assertFalse(panel.channel.path.exists())

    def test_actual_host_accept_enqueues_only_one_replacement(self):
        panel = self.connect_panel()
        self.click_with_dialog_response(panel, 'ok')
        panel.rows[1]['rotate'].invoke()  # disabled while awaiting the first result
        self.assertEqual(len(panel.channel.pending), 1)
        request = next(iter(panel.channel.pending.values()))['request']
        self.assertEqual(request['method'], 'rotate')
        self.assertEqual(request['args'], [1, False])
        self.assertEqual(request['expected']['material'], 5)


class RotationSyncTests(unittest.TestCase):
    setUp = material_fixture.FullResetUITests.setUp
    cleanup = material_fixture.FullResetUITests.cleanup
    pump = material_fixture.FullResetUITests.pump

    def test_both_pc_buttons_rotate_and_debit_selected_stock_once_with_collection_on_or_off(self):
        import tkinter as tk
        from tkinter import ttk
        from unittest.mock import patch
        import material_client as client
        import material_ui as ui
        from material_quick import QuickPanel, QuickChannel, QuickBridge
        from test_material_sync import QuietCollector

        base = Path(self.tmp.name)
        self.sub = client.ClientSession(base / 'sub', base / 'share', QuietCollector)
        self.subroot = tk.Tk()
        # Separate PCs have separate default Tk interpreters.
        with patch.object(tk, '_default_root', self.subroot):
            self.subapp = ui.SyncedApplication(self.subroot, self.sub)
        self.pump(lambda: self.subapp.connected)
        self.session.command('register_stock', ['10B', 10], {})
        self.pump(lambda: self.app.store.inventory()[1]['quantity'] == 10)
        self.session.command('set_next_type', [1, '10B'], self.app.store.snapshot(1)['expected'])
        self.pump(lambda: self.subapp.store.snapshot(1)['next_type'] == '10B')

        panels = []
        for name, app in (('main', self.app), ('sub', self.subapp)):
            folder = base / (name + '-control')
            folder.mkdir()
            app.control_folder = str(folder)
            app.control_nonce = name
            app.quick_bridge = QuickBridge(app, folder, name)
            app.poll_control()
            app.on_close()
            window = tk.Toplevel(self.root)
            host = SimpleNamespace(window=window, tk=tk, ttk=ttk, style=ttk.Style(window))
            panel = QuickPanel(host, ttk.Frame(window))
            manager = SimpleNamespace(sessions={'material': (folder, name)}, running_keys=lambda: ['material'])
            panel.channel = QuickChannel(manager, base / (name + '-inputs.json'))
            panels.append(panel)

        remaining = 10
        for collection in (False, True):
            self.session.coordinator.authority.set_collection(collection)
            self.pump(lambda: self.app.store.state['collection'] == collection
                      and self.subapp.store.state['collection'] == collection)
            for panel in panels:
                with self.subTest(collection=collection, pc=panel.app.window):
                    def ready():
                        panel.poll()
                        rows = panel.channel.state.get('rows', [])
                        # Wait for the other PC's completed replacement to reach
                        # this host; stale simultaneous requests are rejected.
                        return (str(panel.rows[1]['rotate'].cget('state')) == 'normal'
                                and rows and rows[0]['expected']['material']
                                == self.app.store.snapshot(1)['active_material'])
                    self.pump(ready)
                    old = self.app.store.snapshot(1)['active_material']
                    with patch('tkinter.messagebox.askokcancel', return_value=True):
                        panel.rows[1]['rotate'].invoke()
                        panel.rows[1]['rotate'].invoke()
                    self.assertEqual(len(panel.channel.pending), 1)
                    remaining -= 1
                    def saved():
                        panel.poll()
                        if not panel.channel.pending and panel.message.get() and '저장 완료' not in panel.message.get():
                            self.fail(panel.message.get())
                        return (not panel.channel.pending
                                and self.app.store.inventory()[1]['quantity'] == remaining
                                and self.subapp.store.inventory()[1]['quantity'] == remaining)
                    try:
                        self.pump(saved, 8)
                    except AssertionError:
                        self.fail(str(dict(message=panel.message.get(), pending=panel.channel.pending,
                            main_stock=self.app.store.inventory(), sub_stock=self.subapp.store.inventory(),
                            quick=panel.channel.state)))
                    current = self.app.store.snapshot(1)
                    self.assertNotEqual(current['active_material'], old)
                    self.assertEqual(current['active_material'], self.subapp.store.snapshot(1)['active_material'])
                    self.assertEqual(current['material_type'], '10B')
                    self.assertEqual(self.app.store.inventory()[0]['quantity'], 19)
                    self.assertIn('저장 완료', panel.message.get())
        self.assertEqual(remaining, 6)
        self.assertFalse(self.sub.coordinator.settings['enabled'])
