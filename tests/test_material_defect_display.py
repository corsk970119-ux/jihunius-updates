"""Main quick input, shared persistence and both dashboards show one reclassification."""
import time
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_material_full_reset_ui as fixture
from material_client import ClientSession
from material_quick import QuickBridge, QuickChannel
from material_ui import SyncedApplication
from test_material_sync import QuietCollector


class DefectDisplayTests(unittest.TestCase):
    setUp = fixture.FullResetUITests.setUp
    cleanup = fixture.FullResetUITests.cleanup
    pump = fixture.FullResetUITests.pump

    def feed(self, program):
        authority = self.session.coordinator.authority
        authority.samples.put(('sample', '192.168.1.1', 1,
            dict(machine=1, program=program, state='RUN', part_count='500'),
            time.time(), None, None))
        self.pump(lambda: self.app.store.snapshot(1)['program'] == program)

    def test_main_defect_and_sub_pc_off_input_reduce_good_on_both_screens(self):
        import tkinter as tk
        for program in ('6000', '6001', '6002'):
            self.feed(program)
        self.assertEqual(self.app.store.snapshot(1)['good'], 2)
        self.sub = ClientSession(Path(self.tmp.name)/'sub', Path(self.tmp.name)/'share', QuietCollector)
        self.subroot = tk.Tk()
        # Each PC has its own Tk interpreter. Route default-root images/variables
        # to the second interpreter while constructing that PC's real dashboard.
        with patch.object(tk, '_default_root', self.subroot):
            self.subapp = SyncedApplication(self.subroot, self.sub)
        self.pump(lambda: self.subapp.store.snapshot(1)['good'] == 2)
        folder = Path(self.tmp.name)/'control'
        folder.mkdir()
        self.app.control_folder = str(folder)
        self.app.control_nonce = 'nonce'
        self.app.quick_bridge = QuickBridge(self.app, folder, 'nonce')
        self.app.poll_control()
        manager = SimpleNamespace(sessions={'material': (folder, 'nonce')}, running_keys=lambda: ['material'])
        channel = QuickChannel(manager, Path(self.tmp.name)/'quick.json')
        self.pump(lambda: channel.poll()[0].get('connected'))
        channel.submit('defect', 1)
        channel.poll()
        self.feed('9020')
        self.feed('6002')
        results = []
        def complete():
            _, items = channel.poll()
            results.extend(items)
            return bool(results) and all(a.store.snapshot(1)['defects'] == 1 for a in (self.app, self.subapp))
        self.pump(complete, 6)
        self.assertTrue(results[-1]['result']['ok'], results)
        for app in (self.app, self.subapp):
            self.assertEqual((app.rows[1]['total'].cget('text'), app.rows[1]['defects'].cget('text')), ('1', '1'))
            self.assertEqual(app.store.snapshot(1)['total'], 2)
        self.session.coordinator.authority.set_collection(False)
        self.pump(lambda: not self.subapp.store.state['collection'])
        self.subapp.defect(1)
        self.pump(lambda: all(a.store.snapshot(1)['defects'] == 2 for a in (self.app, self.subapp)), 6)
        for app in (self.app, self.subapp):
            self.assertEqual((app.rows[1]['total'].cget('text'), app.rows[1]['defects'].cget('text')), ('0', '2'))
            self.assertEqual(app.store.snapshot(1)['total'], 2)
