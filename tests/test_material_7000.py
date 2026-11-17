"""O7000은 집계하지 않는다(사용자 요청 2026-11-18: "소재 사용량 조사에 O7000도 제외해야할듯").

3999·9012·9999와 같은 제외다: 7000으로 바뀔 때 +0, 7000에서 집계 대상 번호로 바뀌면 +1(같은 번호로 돌아와도 재가공 +1).
9020만 '투명'하다(9020을 거쳐 같은 번호로 돌아오면 +0) — 그 규칙은 그대로다. 이미 기록된 수량은 고치지 않는다.
"""
import ast
import base64
import sys
import tempfile
import time
import types
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import material_counter as core


class Program7000Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'counter.sqlite3'
        self.s = core.Store(self.path)
        self.addCleanup(lambda: self.s.close())
        self.at = time.time()

    def feed(self, program, machine=1, store=None):
        self.at += 1
        (store or self.s).observe(dict(machine=machine, program=program, state='RUN', part_count='500'), self.at)

    def events(self, machine=1):
        return [(row['kind'], row['previous'], row['program'], row['auto_delta']) for row in self.s.db.execute(
            'SELECT kind,previous,program,auto_delta FROM events WHERE machine=? ORDER BY id', (machine,))]

    def test_7000_is_excluded_and_shown_as_excluded(self):
        self.assertIn('7000', core.EXCLUDED_PROGRAMS)
        self.assertFalse(core.countable_program('7000'))                 # 화면의 'O7000 · 집계 제외' 표시도 이 판정을 씀
        self.assertEqual(core.EXCLUDED_PROGRAMS, frozenset(('3999', '7000', '9012', '9020', '9999')))

    def test_changing_to_7000_adds_nothing_and_the_next_number_counts_once(self):
        for program, total in [('6000', 0), ('6001', 1), ('7000', 1), ('7000', 1), ('6002', 2), ('7000', 2), ('7000', 2)]:
            with self.subTest(program=program, total=total):
                self.feed(program)
                row = self.s.snapshot(1)
                self.assertEqual((row['total'], row['good'], row['defects']), (total, total, 0))
                self.assertEqual(row['program'], program)                # 화면에는 7000이 그대로 보임
        self.assertEqual(self.events(), [('baseline', '', '6000', 0), ('program', '6000', '6001', 1),
                                         ('program_skip', '6001', '7000', 0), ('program', '7000', '6002', 1),
                                         ('program_skip', '6002', '7000', 0)])

    def test_first_observation_7000_is_only_the_starting_point(self):
        for program, total in [('7000', 0), ('7000', 0), ('6000', 1), ('7000', 1)]:
            self.feed(program)
            self.assertEqual(self.s.snapshot(1)['total'], total, program)

    def test_same_number_after_7000_is_rework_plus_one_unlike_9020(self):
        for program, total in [('6000', 0), ('6001', 1), ('7000', 1), ('6001', 2),      # 7000을 거친 같은 번호: 재가공 +1
                               ('9020', 2), ('6001', 2)]:                               # 9020을 거친 같은 번호: +0 (그대로)
            self.feed(program)
            self.assertEqual(self.s.snapshot(1)['total'], total, program)

    def test_7000_counts_exactly_like_the_other_plain_exclusions(self):
        # 같은 순서를 3999·9012·9999로 돌린 것과 7000으로 돌린 것의 기록이 번호만 다르고 똑같아야 합니다(9020과 섞여도).
        order = ['6000', '6001', 'X', '6001', '9020', '6001', 'X', '9020', '6001', '9020', 'X', '6002', 'X', 'X', '6002',
                 '9020', '9020', 'X', '9020', '6003', '6003', 'X', '700', '6003']
        results = {}
        for machine, excluded in enumerate(('3999', '9012', '9999', '7000'), 1):
            for program in order:
                self.feed(excluded if program == 'X' else program, machine)
            results[excluded] = ([tuple('X' if value == excluded else value for value in event) for event in self.events(machine)],
                                 self.s.snapshot(machine)['total'])
        self.assertGreater(results['3999'][1], 0)
        for excluded in ('9012', '9999', '7000'):
            self.assertEqual(results[excluded], results['3999'], excluded)

    def test_numbers_next_to_7000_still_count(self):
        self.feed('6000')
        for total, program in enumerate(('6999', '7001', '7002', '7010', '7100', '7999', '8000', '1700'), 1):
            self.feed(program)
            self.assertEqual(self.s.snapshot(1)['total'], total, program)
            self.assertTrue(core.countable_program(program))

    def test_each_machine_is_judged_on_its_own(self):
        for machine, program in ((1, '6000'), (2, '6000'), (1, '7000'), (2, '6001'), (1, '6001'), (2, '7000'), (2, '6001')):
            self.feed(program, machine)
        self.assertEqual(self.s.snapshot(1)['total'], 1)
        self.assertEqual(self.s.snapshot(2)['total'], 2)

    def test_defects_and_period_totals_stay_consistent_around_7000(self):
        for program in ('6000', '6001', '6002'):
            self.feed(program)
        self.s.defect(1, self.at + .1)
        self.feed('7000')
        row = self.s.snapshot(1)
        self.assertEqual((row['total'], row['good'], row['defects']), (2, 1, 1))
        self.feed('6003')
        row = self.s.snapshot(1)
        self.assertEqual((row['total'], row['good'], row['defects']), (3, 2, 1))
        report = self.s.period_report(0, self.at + 1)['totals']
        self.assertEqual((report['production'], report['good'], report['defects']), (3, 2, 1))

    def test_counts_recorded_by_the_previous_release_are_kept_as_they_are(self):
        # 2026.11.18.1까지는 7000도 +1로 셌습니다. 그렇게 이미 기록된 수량은 새 버전에서 고치지 않습니다.
        path = ROOT / 'releases/jihunius/2026.11.18.1/app.pyw'
        assignments = {n.targets[0].id: n.value for n in ast.parse(path.read_text(encoding='utf-8')).body
                       if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
        payload = ast.literal_eval(assignments['SUITE_COMPANIONS'])['material']['compressed']
        source = zlib.decompress(base64.b64decode(payload)).decode()
        legacy = types.ModuleType('legacy_7000')
        legacy.__dict__.update(core.__dict__)
        for node in ast.parse(source).body:
            if ((isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'EXCLUDED_PROGRAMS')
                    or (isinstance(node, ast.FunctionDef) and node.name == 'countable_program')
                    or (isinstance(node, ast.ClassDef) and node.name == 'Store')):
                exec(compile(ast.get_source_segment(source, node), 'legacy counting', 'exec'), legacy.__dict__)
        self.assertNotIn('7000', legacy.EXCLUDED_PROGRAMS)
        path = Path(self.tmp.name) / 'legacy.sqlite3'
        old = legacy.Store(path)
        old.register_stock('10B', 7)
        old.assign_material(1, '10B')
        for program in ('6000', '6001', '7000'):
            self.feed(program, store=old)
        old.defect(1, self.at + .1)
        before = old.snapshot(1)
        self.assertEqual((before['total'], before['good'], before['defects']), (2, 1, 1))     # 예전 버전: 7000도 +1
        old.close()
        upgraded = core.Store(path)
        try:
            after = upgraded.snapshot(1)
            for key in ('total', 'good', 'defects', 'active_material', 'material_type', 'program'):
                self.assertEqual(after[key], before[key], key)
            self.assertEqual(upgraded.inventory()[1]['quantity'], 7)
            self.feed('7000', store=upgraded)                            # 다시 켠 뒤 첫 관측은 기준값
            self.feed('6002', store=upgraded)                            # 7000 → 집계 대상: +1
            self.feed('7000', store=upgraded)                            # 이제 7000은 +0
            self.feed('7000', store=upgraded)
            row = upgraded.snapshot(1)
            self.assertEqual((row['total'], row['good'], row['defects']), (3, 2, 1))
        finally:
            upgraded.close()


class ExclusionTextTests(unittest.TestCase):
    def test_every_text_that_lists_the_excluded_numbers_lists_all_of_them(self):
        found = 0
        for name in ('src/material_counter.py', 'src/material_ui.py'):
            for node in ast.walk(ast.parse((ROOT / name).read_text(encoding='utf-8'))):
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and '9012' in node.value and len(node.value) > 4:   # 문장만(번호 목록 자체는 빼고)
                    found += 1
                    for program in sorted(core.EXCLUDED_PROGRAMS):
                        self.assertIn(program, node.value, '{}: {!r}'.format(name, node.value[:80]))
        self.assertGreaterEqual(found, 6)                                 # 머리말·기록 문구 2·화면 안내 줄·내보내기 설명·사용 안내 2


if __name__ == '__main__':
    unittest.main()
