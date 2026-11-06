"""Site counters must not participate in material observations or fresh history."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import material_counter as core
import material_sync as sync
import test_material_full_reset_ui as reset_ui


class ProgramOnlyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.s = sync.CommandStore(Path(self.tmp.name) / 'counter.sqlite3')
        self.addCleanup(self.s.close)
        self.s.register_stock('10B', 10)
        self.s.assign_material(1, '10B')
        self.at = 1000.0

    def feed(self, program='6001', part='900', state='RUN', omit=False):
        self.at += 1
        sample = dict(machine=1, program=program, state=state)
        if not omit:
            sample['part_count'] = part
        return self.s.observe(sample, self.at)

    def test_parser_does_not_read_site_counter(self):
        class Response(dict):
            def get(self, key, default=None):
                if key == 'part_count':
                    raise AssertionError('site counter must not be consulted')
                return super().get(key, default)
        sample = core.parse_sample(Response(message='success', machine_name='machine 1',
                                            program_number='06001', state='RUN', part_count=987654))
        self.assertEqual(sample['program'], '6001')
        self.assertEqual(sample.get('part_count', ''), '')

    def test_counter_changes_create_no_events_or_revision_changes(self):
        self.feed()
        revision = self.s.revision()
        events = self.s.events()
        for value in ('901', '999999999999', '0', '-30', None, {'bad': 1}):
            with self.subTest(value=value):
                self.assertFalse(self.feed(part=value))
                self.assertEqual(self.s.revision(), revision)
                self.assertEqual(self.s.events(), events)
                self.assertEqual(self.s.snapshot(1)['total'], 0)
                self.assertEqual(self.s.snapshot(1)['last_seen'], self.at)

    def test_missing_counter_does_not_break_program_or_state_tracking(self):
        for program, state in [('6001', 'RUN'), ('6002', 'RUN'), ('6002', 'ALARM')]:
            self.feed(program, state=state, omit=True)
        row = self.s.snapshot(1)
        self.assertEqual((row['program'], row['state'], row['good']), ('6002', 'ALARM', 1))
        self.assertTrue(all(e['part_count'] == '' for e in self.s.events()))

    def test_counter_jumps_do_not_change_9020_rework_or_defect_rules(self):
        for program, part in [('6000', '800'), ('6001', '0'), ('9020', '999999'),
                              ('6001', '1'), ('3999', '2'), ('6001', '0'),
                              ('9012', '100'), ('6001', '1'), ('9999', '999'),
                              ('6001', '0'), ('9020', '200'), ('6002', '9999')]:
            self.feed(program, part)
        self.s.defect(1, self.at + .1)
        row = self.s.snapshot(1)
        self.assertEqual((row['total'], row['good'], row['defects']), (5, 4, 1))
        self.assertEqual(self.s.inventory()[1]['quantity'], 10)
        self.assertTrue(all(e['part_count'] == '' for e in self.s.events()))
        self.assertFalse(any(e['kind'] == 'reference' for e in self.s.events()))

    def test_mass_pause_ignores_counter_only_updates(self):
        self.feed()
        self.s.toggle_mass_mode(1, self.at + .1)
        revision = self.s.revision()
        self.assertFalse(self.feed(part='999999'))
        self.assertEqual(self.s.revision(), revision)
        self.assertTrue(self.s.snapshot(1)['mass_mode'])

    def test_existing_history_is_preserved_but_not_copied_to_new_events(self):
        self.feed('6000')
        self.feed('6001')
        # Seed the fields retained in a v6 database written by the previous release.
        with self.s.transaction():
            self.s.db.execute("UPDATE machines SET part_count='700' WHERE machine=1")
            self.s.db.execute("UPDATE events SET part_count='700' WHERE machine=1")
        history = self.s.events()
        old_last = history[0]['id']
        before = self.s.snapshot(1)
        self.s.defect(1, self.at + .1)
        new = self.s.events()[0]
        self.assertEqual(new['part_count'], '')
        self.assertEqual([e for e in self.s.events() if e['id'] <= old_last], history)
        after = self.s.snapshot(1)
        self.assertEqual(after['active_material'], before['active_material'])
        self.assertEqual((after['total'], after['good'], after['defects']), (1, 0, 1))


class ProgramOnlyHistoryUITests(unittest.TestCase):
    setUp = reset_ui.FullResetUITests.setUp
    cleanup = reset_ui.FullResetUITests.cleanup
    pump = reset_ui.FullResetUITests.pump

    def test_synced_history_and_details_have_no_counter_column(self):
        self.app.refresh_history(force=True)
        self.pump(lambda: not self.app.job_callbacks and self.app.event_tree.get_children())
        tree = self.app.event_tree
        self.assertNotIn('part', tree['columns'])
        for item in tree.get_children():
            self.assertEqual(len(tree.item(item, 'values')), 4)
        tree.selection_set(tree.get_children()[0])
        with patch('tkinter.messagebox.showinfo') as show:
            self.app.event_detail()
        self.assertNotIn('사이트 카운터', show.call_args.args[1])
