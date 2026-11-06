"""First observation is not a material replacement; real concurrent edits remain guarded."""
import time
import unittest
import uuid
from unittest.mock import patch

import test_material_sync as service
import test_material_full_reset_ui as ui_fixture


class AssignmentServiceTests(unittest.TestCase):
    setUp = service.CommandTests.setUp

    def request(self, n=2):
        return dict(id=uuid.uuid4().hex, client='sub', epoch=self.s.epoch(),
                    method='assign_material', args=[n, '10B'],
                    expected=self.s.expectations(n), expires=time.time()+30)

    def observe(self, n=2):
        self.s.observe(dict(machine=n, program='6001', state='RUN', part_count='0'))

    def test_initial_assignment_survives_first_sample_arriving_after_dialog_opened(self):
        r = self.request()
        self.observe()
        self.assertTrue(self.s.apply(r)['ok'])
        self.assertEqual(self.s.snapshot(2)['material_type'], '10B')
        self.assertIsNone(self.s.inventory()[1]['quantity'])

    def test_concurrent_initial_assignment_cannot_overwrite_another_pc(self):
        r = self.request()
        self.observe()
        self.s.assign_material(2, '12')
        self.assertFalse(self.s.apply(r)['ok'])
        self.assertEqual(self.s.snapshot(2)['material_type'], '12')

    def test_missing_expected_material_and_changed_mode_are_still_rejected(self):
        r = self.request()
        del r['expected']['material']
        self.observe()
        self.assertFalse(self.s.apply(r)['ok'])
        r = self.request(3)
        self.observe(3)
        self.s.toggle_mass_mode(3, manual=True)
        self.assertFalse(self.s.apply(r)['ok'])
        self.assertIsNone(self.s.snapshot(3)['material_type'])


class AssignmentDialogTests(unittest.TestCase):
    setUp = ui_fixture.FullResetUITests.setUp
    cleanup = ui_fixture.FullResetUITests.cleanup
    pump = ui_fixture.FullResetUITests.pump

    def open_dialog(self, n):
        self.app.material_dialog(n)
        self.root.update()
        dialog = next(w for w in self.root.winfo_children() if w.winfo_class() == 'Toplevel')
        combo = next(w for w in dialog.winfo_children() if w.winfo_class() == 'TCombobox')
        apply = next(w for w in dialog.winfo_children() if w.winfo_class() == 'Button' and w.cget('text') == '적용')
        return dialog, combo, apply

    def test_open_initial_dialog_during_collection_can_apply_once(self):
        dialog, combo, apply = self.open_dialog(2)
        authority = self.session.coordinator.authority
        authority.samples.put(('sample','192.168.1.10',1,
            dict(machine=2,program='6001',state='RUN',part_count='0'),time.time(),None,None))
        self.pump(lambda: self.app.store.snapshot(2)['active_material'] is not None)
        combo.set('Ø10 B급')
        apply.invoke()
        self.pump(lambda: not dialog.winfo_exists(), 5)
        self.pump(lambda: self.app.store.snapshot(2)['material_type'] == '10B')

    def test_other_pc_assignment_refreshes_same_dialog_before_explicit_reapply(self):
        dialog, combo, apply = self.open_dialog(2)
        combo.set('Ø10 B급')
        state = self.session.coordinator.client.call('state')
        request = dict(id=uuid.uuid4().hex, client='other-pc', epoch=state['epoch'],
                       method='assign_material', args=[2, '12'],
                       expected=state['rows'][1]['expected'], expires=time.time()+30)
        self.assertTrue(self.session.coordinator.client.call('command', request)['ok'])
        self.pump(lambda: self.app.store.snapshot(2)['material_type'] == '12')
        apply.invoke()
        self.root.update()
        # First click refreshes the changed context, not the other PC's material.
        self.pump(lambda: any('다음 교체 소재' in str(w.cget('text'))
                             for w in dialog.winfo_children() if w.winfo_class() == 'Label'))
        self.assertEqual(self.app.store.snapshot(2)['material_type'], '12')
        self.assertEqual(self.app.store.snapshot(2)['next_type'], '12')
        self.assertEqual(combo.get(), 'Ø10 B급')
        apply.invoke()
        self.pump(lambda: not dialog.winfo_exists(), 5)
        self.pump(lambda: self.app.store.snapshot(2)['next_type'] == '10B')
        self.assertEqual(self.app.store.snapshot(2)['material_type'], '12')

    def test_newer_next_type_is_shown_and_retry_works_without_closing(self):
        dialog, combo, apply = self.open_dialog(1)
        combo.set('Ø10 B급')
        state = self.session.coordinator.client.call('state')
        request = dict(id=uuid.uuid4().hex, client='other-pc', epoch=state['epoch'],
                       method='set_next_type', args=[1, '12'],
                       expected=state['rows'][0]['expected'], expires=time.time()+30)
        self.assertTrue(self.session.coordinator.client.call('command', request)['ok'])
        self.pump(lambda: self.app.store.snapshot(1)['next_type'] == '12')
        apply.invoke()
        self.root.update()
        self.assertTrue(dialog.winfo_exists())
        self.assertEqual(self.app.store.snapshot(1)['next_type'], '12')
        apply.invoke()
        self.pump(lambda: not dialog.winfo_exists(), 5)
        self.pump(lambda: self.app.store.snapshot(1)['next_type'] == '10B')

    def test_server_conflict_after_apply_recovers_in_the_same_open_dialog(self):
        dialog, combo, apply = self.open_dialog(2)
        combo.set('Ø10 B급')
        original = self.session.command
        def other_pc_wins(method, args, expected, **kwargs):
            state = self.session.coordinator.client.call('state')
            request = dict(id=uuid.uuid4().hex, client='other-pc', epoch=state['epoch'],
                           method='assign_material', args=[2, '12'],
                           expected=state['rows'][1]['expected'], expires=time.time()+30)
            self.assertTrue(self.session.coordinator.client.call('command', request)['ok'])
            return original(method, args, expected, **kwargs)
        # Inject only scheduling: all writes, checks, errors and refreshes are real.
        with patch.object(self.session, 'command', side_effect=other_pc_wins):
            apply.invoke()
        self.pump(lambda: not self.app.writes and self.app.store.snapshot(2)['material_type'] == '12')
        self.assertTrue(any('다른 PC' in str(w.cget('text'))
                            for w in dialog.winfo_children() if w.winfo_class() == 'Label'))
        apply.invoke()  # reload and review, no write
        self.assertFalse(self.session.outbox.items())
        apply.invoke()  # explicit apply to the displayed, updated context
        self.pump(lambda: not dialog.winfo_exists(), 5)
        self.pump(lambda: self.app.store.snapshot(2)['next_type'] == '10B')
        self.assertEqual(self.app.store.snapshot(2)['material_type'], '12')

    def test_dialog_does_not_submit_into_a_reset_period_until_reviewed(self):
        dialog, combo, apply = self.open_dialog(2)
        combo.set('Ø12')
        state = self.session.coordinator.client.call('state')
        request = dict(id=uuid.uuid4().hex, client='other-pc', epoch=state['epoch'],
                       method='reset_records', args=[True],
                       expected=dict(revision=state['revision']), expires=time.time()+30)
        self.assertTrue(self.session.coordinator.client.call('command', request)['ok'])
        self.pump(lambda: self.app.store.state['epoch'] != state['epoch'])
        apply.invoke()
        self.root.update()
        self.assertTrue(dialog.winfo_exists())
        self.assertIsNone(self.app.store.snapshot(2)['material_type'])
        self.assertFalse(self.session.outbox.items())
        apply.invoke()
        self.pump(lambda: not dialog.winfo_exists(), 5)
        self.pump(lambda: self.app.store.snapshot(2)['material_type'] == '12')

    def test_command_preserves_the_epoch_of_the_reviewed_dialog(self):
        # A reset can race the UI check. The request must still carry its old epoch.
        self.session.close()
        self.session.thread.join(10)
        epoch = self.session.state['epoch']
        expected = dict(self.app.store.snapshot(2)['expected'])
        state = dict(self.session.state, epoch='new-period')
        with patch.object(self.session, 'state', state):
            token = self.session.command('assign_material', [2, '10B'], expected, epoch=epoch)
        request = next(x['request'] for x in self.session.outbox.items() if x['request']['id'] == token)
        self.assertEqual(request['epoch'], epoch)
