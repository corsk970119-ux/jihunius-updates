"""9020 is transparent to counting; other excluded programs still delimit rework."""
import sys
import ast
import base64
import sqlite3
import tempfile
import time
import types
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import material_counter as core


class Program9020Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'counter.sqlite3'
        self.s = core.Store(self.path)
        self.addCleanup(lambda: self.s.close())
        self.at = time.time()

    def feed(self, program, machine=1):
        self.at += 1
        self.s.observe(dict(machine=machine, program=program,
                            state='RUN', part_count='500'), self.at)

    def test_9020_and_same_program_return_add_nothing(self):
        for program, total in [('6000', 0), ('6001', 1), ('9020', 1),
                               ('9020', 1), ('6001', 1), ('9020', 1),
                               ('6001', 1), ('6002', 2)]:
            with self.subTest(program=program, total=total):
                self.feed(program)
                row = self.s.snapshot(1)
                self.assertEqual((row['total'], row['good']), (total, total))
                self.assertEqual(row['program'], program)

    def test_new_program_after_9020_counts_once(self):
        for program in ('6000', '9020', '6001', '6001'):
            self.feed(program)
        self.assertEqual(self.s.snapshot(1)['total'], 1)

    def test_other_exclusions_still_count_same_program_rework(self):
        self.feed('6000')
        for excluded, total in [('3999', 1), ('9012', 2), ('9999', 3)]:
            self.feed(excluded)
            self.feed('9020')
            self.feed('6000')
            self.assertEqual(self.s.snapshot(1)['total'], total)
        # A genuine rework boundary after 9020 must also remain effective.
        self.feed('9020')
        self.feed('3999')
        self.feed('6000')
        self.assertEqual(self.s.snapshot(1)['total'], 4)

    def test_first_observation_9020_does_not_invent_a_previous_program(self):
        for program in ('9020', '6000', '9020', '6000'):
            self.feed(program)
        self.assertEqual(self.s.snapshot(1)['total'], 1)

    def test_return_reference_survives_restart_and_is_independent_per_machine(self):
        for n, program in ((1, '6001'), (2, '7001'), (1, '9020'), (2, '9020')):
            self.feed(program, n)
        self.s.close()
        self.s = core.Store(self.path)
        self.feed('9020', 1)  # reconnect baseline
        self.feed('9020', 2)
        self.feed('6001', 1)
        self.feed('7002', 2)
        self.assertEqual(self.s.snapshot(1)['total'], 0)
        self.assertEqual(self.s.snapshot(2)['total'], 1)

    def test_defect_decrement_is_not_cancelled_by_9020_excursion(self):
        for program in ('6000', '6001', '6002'):
            self.feed(program)
        self.s.defect(1, self.at + .1)
        self.assertEqual((self.s.snapshot(1)['good'], self.s.snapshot(1)['defects']), (1, 1))
        self.feed('9020')
        self.feed('6002')
        row = self.s.snapshot(1)
        self.assertEqual((row['total'], row['good'], row['defects']), (2, 1, 1))
        report = self.s.period_report(0, self.at + 1)['totals']
        self.assertEqual((report['production'], report['good'], report['defects']), (2, 1, 1))
        self.s.undo(1, self.at + .2)
        self.assertEqual((self.s.snapshot(1)['good'], self.s.snapshot(1)['defects']), (2, 0))

    def test_upgrade_at_9020_preserves_recorded_totals_and_remembers_return(self):
        path = Path(__file__).resolve().parents[1]/'releases/jihunius/2026.11.06.9/app.pyw'
        assignments = {n.targets[0].id: n.value for n in ast.parse(path.read_text()).body
                       if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
        payload = ast.literal_eval(assignments['SUITE_COMPANIONS'])['material']['compressed']
        source = zlib.decompress(base64.b64decode(payload)).decode()
        definition = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == 'Store')
        legacy = types.ModuleType('legacy_9020')
        legacy.__dict__.update(core.__dict__)
        # Use the released counting predicate too: v5 counted 9020 itself.
        old_nodes = ast.parse(source).body
        for node in old_nodes:
            if ((isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                 and node.targets[0].id == 'EXCLUDED_PROGRAMS')
                    or (isinstance(node, ast.FunctionDef) and node.name == 'countable_program')):
                exec(compile(ast.get_source_segment(source, node), 'legacy counting', 'exec'), legacy.__dict__)
        exec(compile(ast.get_source_segment(source, definition), 'legacy Store', 'exec'), legacy.__dict__)
        path = Path(self.tmp.name)/'legacy.sqlite3'
        old = legacy.Store(path)
        old.register_stock('10B', 7)
        old.assign_material(1, '10B')
        for p in ('6000', '6001', '6002', '9020'):
            old.observe(dict(machine=1, program=p, state='RUN', part_count='0'))
        old.defect(1)
        before = old.snapshot(1)
        self.assertEqual((before['total'], before['good'], before['defects']), (3, 2, 1))
        old.close()
        upgraded = core.Store(path)
        try:
            for p in ('9020', '6002'):
                upgraded.observe(dict(machine=1, program=p, state='RUN', part_count='0'))
            after = upgraded.snapshot(1)
            for key in ('total', 'good', 'defects', 'active_material', 'material_type'):
                self.assertEqual(after[key], before[key], key)
            self.assertEqual(upgraded.inventory()[1]['quantity'], 7)
            self.assertTrue(upgraded.migration_backup.exists())
            backup = sqlite3.connect(upgraded.migration_backup)
            try:
                self.assertEqual(backup.execute('PRAGMA user_version').fetchone()[0], 5)
            finally:
                backup.close()
        finally:
            upgraded.close()
        with self.assertRaises(RuntimeError):
            legacy.Store(path)
