"""tools/run_tests.py: 파일 단위로 나눠 돌리는 실행기가 결과를 정확히 모으는지."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('run_tests_tool', ROOT / 'tools/run_tests.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

PASSED = '...\n----------------------------------------------------------------------\nRan 3 tests in 0.120s\n\nOK\n'
SKIPPED = '.s.\n----------------------------------------------------------------------\nRan 3 tests in 0.1s\n\nOK (skipped=1)\n'
FAILED = ('.F\n======================================================================\nFAIL: test_x (m.T.test_x)\n'
          '----------------------------------------------------------------------\nTraceback ...\n\n'
          '----------------------------------------------------------------------\nRan 2 tests in 0.01s\n\n'
          'FAILED (failures=1, skipped=2)\n')


class RunTestsToolTests(unittest.TestCase):
    def test_every_test_file_is_found_and_filters_narrow_the_list(self):
        names = runner.test_modules()
        self.assertEqual(names, sorted(path.stem for path in (ROOT / 'tests').glob('test_*.py')))
        self.assertIn('test_run_tests_tool', names)
        self.assertEqual(runner.test_modules(['run_tests_tool']), ['test_run_tests_tool'])
        self.assertEqual(runner.test_modules(['없는 이름']), [])

    def test_longest_files_start_first_and_unknown_files_before_them(self):
        self.assertEqual(runner.ordered(['a', 'b', 'c', 'd'], {'a': 1.0, 'b': 9.0, 'c': 3.0}), ['d', 'b', 'c', 'a'])

    def test_output_is_read_as_counts_and_pass_or_fail(self):
        self.assertEqual(runner.parse(PASSED, 0), (3, 0, True))
        self.assertEqual(runner.parse(SKIPPED, 0), (3, 1, True))
        self.assertEqual(runner.parse(FAILED, 1), (2, 2, False))
        self.assertEqual(runner.parse('Traceback: ModuleNotFoundError', 1), (0, 0, False))   # 불러오지도 못한 파일
        self.assertEqual(runner.parse('', 0), (0, 0, False))                                  # 아무것도 안 돌았으면 통과 아님
        self.assertEqual(runner.parse(PASSED, -9), (3, 0, False))                             # 중간에 죽은 프로세스

    def test_summary_totals_and_shows_the_output_of_failed_files_only(self):
        results = [{'name': 'test_a', 'seconds': 2.0, 'ran': 3, 'skipped': 1, 'passed': True, 'output': 'quiet'},
                   {'name': 'test_b', 'seconds': 5.0, 'ran': 2, 'skipped': 0, 'passed': False, 'output': 'FAIL: test_x\nboom'}]
        text, passed = runner.summarize(results, 5.5)
        self.assertFalse(passed)
        self.assertIn('Ran 5 tests in 5.5s (2개 파일)', text)
        self.assertIn('FAILED (파일 1개: test_b) (skipped=1)', text)
        self.assertIn('실패한 파일: tests/test_b.py', text)
        self.assertIn('boom', text)
        self.assertNotIn('quiet', text)
        text, passed = runner.summarize(results[:1], 2.0)
        self.assertTrue(passed)
        self.assertTrue(text.rstrip().endswith('OK (skipped=1)'))

    def test_one_file_really_runs_in_its_own_process(self):
        results = runner.run(['test_build_app'], jobs=1, show=lambda text: None)
        self.assertEqual([(value['name'], value['passed']) for value in results], [('test_build_app', True)])
        self.assertGreater(results[0]['ran'], 0)


if __name__ == '__main__':
    unittest.main()
