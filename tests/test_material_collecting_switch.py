"""Exercise real polling/checkpoints and mouse input while collection stays ON."""
import unittest
from pathlib import Path
from unittest.mock import patch
import test_material_full_reset_ui as reset_ui
import test_material_hold_ui as hold_ui
import material_counter as core
import material_client as client


class CollectingSwitchTests(unittest.TestCase):
    pump = hold_ui.MaterialHoldUITests.pump
    cleanup = hold_ui.MaterialHoldUITests.cleanup

    def setUp(self):
        self.program = '1003'
        self.sample_reads = 0

        def request(endpoint, fields):
            if endpoint == 'monitoring_ajax_setting.php':
                return {'ip': ['192.168.1.10']}
            self.sample_reads += 1
            return dict(message='success', machine_name='machine 1',
                        program_number=self.program, state='RUN', part_count=0)

        collector = patch.object(reset_ui, 'QuietCollector',
                                 lambda out: core.Collector(out, request=request))
        collector.start()
        self.addCleanup(collector.stop)
        reset_ui.FullResetUITests.setUp(self)

    def click(self, key):
        widget = self.app.rows[1][key]
        widget.event_generate('<Enter>', x=10, y=10)
        widget.event_generate('<ButtonPress-1>', x=10, y=10)
        # A normal polling refresh can land between mouse press and release.
        self.app.refresh()
        widget.event_generate('<ButtonRelease-1>', x=10, y=10)
        widget.event_generate('<Leave>', x=10, y=10)

    def test_live_collector_allows_14_return_pause_resume_during_run(self):
        self.session.command('register_stock', ['14', 5], {})
        self.pump(lambda: self.app.store.inventory()[3]['quantity'] == 5
                  and self.app.can_switch_14(1))
        self.assertEqual(self.app.store.snapshot(1)['state'], 'RUN')
        original = self.app.store.snapshot(1)['active_material']
        before_reads = self.sample_reads

        # Continue collecting a new program while the confirmation is open.
        def confirm(*args, **kwargs):
            self.program = '1004'
            self.pump(lambda: self.app.store.snapshot(1)['program'] == '1004', 6)
            return True

        with patch('tkinter.messagebox.askokcancel', side_effect=confirm):
            self.click('switch14')
        self.pump(lambda: self.app.store.snapshot(1)['material_type'] == '14', 6)
        row = self.app.store.snapshot(1)
        self.assertEqual(row['parked']['material_id'], original)
        self.assertEqual(row['parked']['good'], 1)
        self.assertEqual(row['good'], 0)
        self.assertGreater(self.sample_reads, before_reads)

        with patch('tkinter.messagebox.askokcancel', return_value=True):
            self.click('switch14')
            self.pump(lambda: self.app.store.snapshot(1)['active_material'] == original, 6)
            self.click('mass_mode')
            self.pump(lambda: self.app.store.snapshot(1)['mass_mode'], 6)
            self.program = '7001'
            self.pump(lambda: self.app.store.snapshot(1)['program'] == '7001', 6)
            self.click('mass_mode')
            self.pump(lambda: not self.app.store.snapshot(1)['mass_mode'], 6)

        row = self.app.store.snapshot(1)
        self.assertEqual((row['active_material'], row['good']), (original, 1))
        self.assertEqual(self.app.store.inventory()[3]['quantity'], 4)
        self.assertTrue(self.session.coordinator.authority.collection)
        self.assertTrue(self.session.state['collection'])
        self.assertTrue(self.app.can_switch_14(1))
        self.assertTrue(self.app.can_toggle_mass_mode(1))

    def test_collection_off_keeps_manual_actions_enabled_and_uses_owner_storage(self):
        self.session.command('register_stock', ['14', 5], {})
        self.pump(lambda: self.app.store.inventory()[3]['quantity'] == 5
                  and self.app.can_switch_14(1))
        self.program='1004'
        self.pump(lambda:self.app.store.snapshot(1)['good']==1,6)
        self.app.toggle_collection()
        self.pump(lambda:not self.app.toggle_pending and not self.session.state['collection'])
        self.assertFalse(self.app.store.live)
        self.sub=client.ClientSession(Path(self.tmp.name)/'sub',Path(self.tmp.name)/'share',reset_ui.QuietCollector)
        self.pump(lambda:self.sub.state is not None)
        self.assertFalse(self.sub.coordinator.settings['enabled'])
        self.assertFalse(self.sub.state['collection'])
        self.assertTrue(self.app.action_availability(1)['rotate'])
        self.assertTrue(self.app.action_availability(1)['defect'])
        self.assertEqual(self.app.rows[1]['switch14'].cget('state'),'normal')
        self.assertEqual(self.app.rows[1]['mass_mode'].cget('state'),'normal')
        original=self.app.store.snapshot(1)['active_material']
        with patch('tkinter.messagebox.askokcancel',return_value=True):
            self.click('switch14')
            self.pump(lambda:self.app.store.snapshot(1)['material_type']=='14')
            self.pump(lambda:self.sub.state['rows'][0]['material_type']=='14')
            self.sub.command('switch_14',[1],dict(self.sub.state['rows'][0]['expected']))
            self.pump(lambda:self.app.store.snapshot(1)['active_material']==original)
            self.click('mass_mode')
            self.pump(lambda:self.app.store.snapshot(1)['mass_mode'])
            self.pump(lambda:self.sub.state['rows'][0]['mass_mode'])
            self.sub.command('defect',[1],dict(self.sub.state['rows'][0]['expected']))
            self.pump(lambda:self.app.store.snapshot(1)['defects']==1)
            self.app.rotate(1)
            self.pump(lambda:self.app.store.snapshot(1)['active_material']!=original)
            self.assertTrue(self.app.store.snapshot(1)['mass_mode'])
            self.pump(lambda:self.sub.state['rows'][0]['active_material']!=original)
            self.sub.command('toggle_mass_mode',[1],dict(self.sub.state['rows'][0]['expected']))
            self.pump(lambda:not self.app.store.snapshot(1)['mass_mode'] and not self.sub.state['rows'][0]['mass_mode'])
        self.assertEqual(self.session.state['revision'],self.sub.state['revision'])
        self.assertFalse(self.session.state['collection'])
        self.assertEqual(self.app.store.inventory()[3]['quantity'],4)
