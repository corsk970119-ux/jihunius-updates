"""세척완료 POP 체크: 건수가 많아도 끝까지, 잘못 누르지 않고 진행하는지 가짜 POP 화면으로 확인합니다.

실제 POP에는 접속하지 않습니다. FakePop이 접근성 판독 결과(MSAA 기록)와 스크롤·체크 동작을 흉내 냅니다.
"""
import sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_release_package as release

COLUMNS = ['선택', '프로젝트No', '설비명', '지시일', '품명', '수량', '비고', '작업자']
WIDTHS = [40, 120, 80, 90, 160, 50, 120, 80]
ROW_H = 20
GRID = 200  # 표 창 핸들
TOP = 100   # POP 창 핸들


def load(source, name):
    scope = {'__name__': name}
    exec(compile(source, name, 'exec'), scope)
    scope['validate_conditions'] = lambda *a, **k: {'date': '', 'worker': '', 'sequence': '', 'project_filter': ''}
    return scope


def new_module():
    return load((ROOT / 'src/host/wash_pop.py').read_text(encoding='utf-8'), 'wash_pop_new')


def old_module():
    return load(release.assignments(release.BASE / 'app.pyw')['WASH_POP_SOURCE'], 'wash_pop_old')


class Stop:
    def is_set(self): return False
    def wait(self, seconds): return False


class FakePop:
    """한 화면에 page행만 보이는 POP 결과표."""

    def __init__(self, count, page=15, reflect_after=0, summaries=True):
        self.rows = [{'선택': '선택안됨', '프로젝트No': 'P{:04d}'.format(i), '설비명': '{}호기'.format(i % 9 + 1),
                      '지시일': '2026-11-11', '품명': '품목{}'.format(i), '수량': str(i), '비고': '', '작업자': '홍길동'}
                     for i in range(1, count + 1)]
        self.page, self.top, self.reflect_after, self.summaries = page, 0, reflect_after, summaries
        self.enabled = [True] * count
        self.pending = []          # [남은 판독 횟수, 행 번호]
        self.captures = []         # (mode, label, 읽은 셀 수)
        self.clicks = []           # 실제로 눌린 행 번호(1부터)
        self.cover = {}            # 행 번호 → 가려진 횟수
        self.glitch_labels = {}    # label → 어긋난 판독을 돌려줄 횟수
        self.mutate_after_first_list_read = None

    # --- 화면 구조 ---
    def visible_range(self):
        return range(self.top, min(len(self.rows), self.top + self.page))

    def summary(self, row):
        text = ';'.join(row[c] for c in COLUMNS) + ';'
        return text if self.summaries else ''

    def report(self, mode, glitch=False):
        records, ids = [], iter(range(10 ** 6))
        def add(parent, role, name='', value='', bounds=None, **extra):
            record = dict(kind='element', id=next(ids), parent=parent, role=role, name=name, value=value,
                          bounds=bounds or [0, 0, 0, 0], enabled=True, state_known=True, offscreen=False,
                          handle=GRID, child_count=0)
            record.update(extra); records.append(record); return record
        height = ROW_H * (self.page + 1)
        table = add(-1, 24, 'POP 결과표', bounds=[0, 0, sum(WIDTHS), height])
        group = add(table['id'], 0, '머리글 패널')
        x = 0
        for name, width in zip(COLUMNS, WIDTHS):
            add(group['id'], 25, name, bounds=[x, 0, width, ROW_H]); x += width
        panel = add(table['id'], 0, '데이터 패널', child_count=len(self.rows))
        cells_read = 0
        for index, row in enumerate(self.rows):
            shown = index in self.visible_range()
            y = ROW_H * (index - self.top + 1)
            element = add(panel['id'], 28, '행 {}'.format(index + 1), self.summary(row),
                          bounds=[0, y, sum(WIDTHS), ROW_H] if shown else [0, 0, 0, 0],
                          offscreen=not shown, child_count=len(COLUMNS))
            if mode == 'mes_rows':
                continue
            if mode == 'pop_fast' and not shown:
                element['cells_omitted'] = True
                continue
            x = 0
            for name, width in zip(COLUMNS, WIDTHS):
                shift = 9 if glitch and shown and name == '선택' else 0
                add(element['id'], 29, '{} row {}'.format(name, index + 1), row[name],
                    bounds=[x + shift, y, width, ROW_H] if shown else [0, 0, 0, 0], offscreen=not shown,
                    enabled=self.enabled[index] if name == '선택' else True)
                x += width; cells_read += 1
        records.append(dict(kind='finish', limited=False, elements=len(records), seconds=0.1))
        return dict(records=records, exit_code=0), cells_read

    # --- 판독기·조작 ---
    def capture(self, target, label, stop):
        for item in self.pending:
            item[0] -= 1
        for item in [i for i in self.pending if i[0] <= 0]:
            self.pending.remove(item); self.toggle(item[1])
        glitch = self.glitch_labels.get(label, 0) > 0
        if glitch:
            self.glitch_labels[label] -= 1
        report, cells = self.report(target['mode'], glitch)
        self.captures.append((target['mode'], label, cells))
        if self.mutate_after_first_list_read and label == 'POP 조회 후 전체 목록 1회 판독':
            action, self.mutate_after_first_list_read = self.mutate_after_first_list_read, None
            action()
        return report

    def toggle(self, number):
        row = self.rows[number - 1]
        row['선택'] = '선택' if row['선택'] == '선택안됨' else '선택안됨'

    def scroll_result_grid(self, view, direction, stop):
        step = max(1, self.page - 2)
        limit = max(0, len(self.rows) - self.page)
        self.top = max(0, self.top - step) if direction > 0 else min(limit, self.top + step)

    def checkbox_click(self, view, key, project):
        row = view['visible'].get(key); cell = view['selection_cells'].get(key)
        if not row or row.get('프로젝트No') != project or row.get('선택') != '선택안됨' or not cell or not cell['enabled']:
            raise RuntimeError('체크할 행이나 현재 선택 상태를 확실히 확인하지 못했습니다.')
        number = int(key)
        if self.cover.get(number, 0) > 0:
            self.cover[number] -= 1
            raise RuntimeError('버튼이 다른 창에 가려져 있어 중단했습니다.')
        x = cell['bounds'][0] + cell['bounds'][2] / 2; y = cell['bounds'][1] + cell['bounds'][3] / 2
        hit = self.top + int(y // ROW_H) - 1
        if not (0 <= x < WIDTHS[0]) or hit != number - 1 or hit not in self.visible_range():
            raise AssertionError('체크 칸이 아닌 곳을 눌렀습니다: 행 {} 좌표 ({}, {})'.format(key, x, y))
        self.clicks.append(number)
        if self.reflect_after:
            self.pending.append([self.reflect_after, number])
        else:
            self.toggle(number)

    def query_click(self, binding):
        pass


def matches_for(pop, numbers):
    return [{'pop': {'row': n}, 'project': pop.rows[n - 1]['프로젝트No']} for n in numbers]


def run_checks(module, pop, numbers, fast=True):
    target = {'handle': TOP, 'pid': 1}
    logs = []
    emit = lambda kind, value: logs.append(value) if kind == 'log' else None
    if fast:
        first = pop.capture({**target, 'mode': 'pop_fast'}, 'POP 조회 후 전체 목록 1회 판독', Stop())
        coverage = module['collect_pop'](target, first, {}, pop, pop.capture, Stop(), emit, summary_rows=True)
    else:
        first = pop.capture({**target, 'mode': 'pop_full'}, 'POP 조회 후 전체 목록 1회 판독', Stop())
        coverage = module['collect_pop'](target, first, {}, pop, pop.capture, Stop(), emit)
    done = module['check_matched'](target, {}, coverage, matches_for(pop, numbers), pop, pop.capture, Stop(), emit)
    return coverage, done, logs


class LegacyEquivalenceTests(unittest.TestCase):
    """한 화면에 다 보이는 짧은 목록은 예전 구현과 결과·클릭이 같아야 합니다."""

    def test_full_report_view_and_coverage_match_previous_release(self):
        old, new = old_module(), new_module()
        pop = FakePop(9, page=12)
        report, _ = pop.report('pop_full')
        before = old['pop_view'](report); after = new['pop_view'](report)
        self.assertEqual(after.pop('omitted'), [])
        self.assertEqual(before, after)
        emit = lambda *a: None
        first = old['collect_pop']({'handle': TOP}, report, {}, pop, pop.capture, Stop(), emit)
        second = new['collect_pop']({'handle': TOP}, report, {}, pop, pop.capture, Stop(), emit)
        self.assertEqual(second.pop('omitted'), [])
        second['current_view'].pop('omitted'); self.assertEqual(first, second)

    def test_every_cell_mode_reads_and_clicks_in_the_same_order_as_previous_release(self):
        """배포 기본 경로(전체 칸 판독): 화면이 바로 반영되면 예전 구현과 판독 순서·클릭이 한 글자도 다르지 않습니다."""
        traces = []
        for module in (old_module(), new_module()):
            pop = FakePop(70, page=15)
            coverage, done, _ = run_checks(module, pop, [1, 16, 17, 40, 70], fast=False)
            traces.append(([(mode, label) for mode, label, _ in pop.captures], pop.clicks,
                           [r['선택'] for r in pop.rows], [e['row'] for e in done]))
        self.assertEqual(traces[0], traces[1])
        self.assertEqual(traces[1][1], [1, 16, 17, 40, 70])

    def test_short_list_clicks_same_rows_as_previous_release(self):
        results = []
        for module in (old_module(), new_module()):
            pop = FakePop(9, page=12)
            coverage, done, _ = run_checks(module, pop, [2, 5, 9], fast=module['__name__'].endswith('new'))
            results.append((pop.clicks, [r['선택'] for r in pop.rows], [e['row'] for e in done],
                            coverage['complete'], coverage['top_verified'], coverage['bottom_verified']))
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[1][0], [2, 5, 9])


class LargeListTests(unittest.TestCase):
    def setUp(self):
        self.module = new_module()
        self.assertEqual(self.module['CHECK_SETTLE_SECONDS'], 4.0)   # 제품 기본값
        self.module['CHECK_SETTLE_SECONDS'] = 0.05                   # 테스트는 기다리지 않게

    def test_120_rows_complete_with_bounded_reads_and_only_targets_checked(self):
        pop = FakePop(120, page=15)
        targets = list(range(3, 121, 4))
        coverage, done, _ = run_checks(self.module, pop, targets)
        self.assertEqual(sorted(pop.clicks), targets)
        self.assertEqual([n for n, r in enumerate(pop.rows, 1) if r['선택'] == '선택'], targets)
        self.assertEqual(len(done), len(targets))
        self.assertTrue(coverage['complete'] and coverage['top_verified'] and coverage['bottom_verified'])
        # 어떤 한 번의 판독도 '전체 행 × 전체 칸'을 읽지 않습니다(한 화면 분량 이내).
        self.assertNotIn('pop_full', {mode for mode, _, _ in pop.captures})
        self.assertNotIn('pop_final', {mode for mode, _, _ in pop.captures})
        self.assertLessEqual(max(cells for _, _, cells in pop.captures), pop.page * len(COLUMNS))
        # 저장 직전 검증이 쓰는 화면: 체크된 행 = 대상 행.
        view = self.module['pop_view'](coverage['final_report'], baseline_raw=coverage['final_baseline'])
        chosen = {k for k, row in zip(view['keys'], view['raw']) if row[coverage['columns']['선택']] == '선택'}
        self.assertEqual(chosen, {str(n) for n in targets})

    def test_read_work_does_not_grow_with_row_count(self):
        biggest = []
        for count in (60, 240):
            pop = FakePop(count, page=15)
            run_checks(self.module, pop, [2, count - 1])
            biggest.append(max(cells for _, _, cells in pop.captures))
        self.assertEqual(biggest[0], biggest[1])

    def test_slow_pop_gets_one_click_per_row_not_two(self):
        pop = FakePop(60, page=15, reflect_after=3)
        targets = [1, 2, 20, 41, 60]
        run_checks(self.module, pop, targets)
        self.assertEqual(sorted(pop.clicks), targets)
        self.assertEqual([n for n, r in enumerate(pop.rows, 1) if r['선택'] == '선택'], targets)

    def test_briefly_covered_checkbox_is_retried_without_wrong_clicks(self):
        pop = FakePop(60, page=15); pop.cover = {20: 2}
        _, _, logs = run_checks(self.module, pop, [5, 20, 55])
        self.assertEqual(sorted(pop.clicks), [5, 20, 55])
        self.assertTrue(any('가려져' in line for line in logs))

    def test_persistently_covered_checkbox_stops_safely(self):
        pop = FakePop(60, page=15); pop.cover = {20: 99}
        with self.assertRaisesRegex(RuntimeError, '계속 가려져'):
            run_checks(self.module, pop, [5, 20, 55])
        self.assertNotIn(20, pop.clicks)

    def test_never_reflected_check_stops_after_two_clicks(self):
        pop = FakePop(30, page=15, reflect_after=10 ** 6)
        with self.assertRaisesRegex(RuntimeError, '두 번 이내의 클릭'):
            run_checks(self.module, pop, [4])
        self.assertEqual(pop.clicks, [4, 4])

    def test_disabled_checkbox_in_hidden_row_is_never_clicked(self):
        pop = FakePop(60, page=15); pop.enabled[39] = False
        with self.assertRaisesRegex(RuntimeError, '확실히 확인하지 못했습니다'):
            run_checks(self.module, pop, [3, 40])
        self.assertNotIn(40, pop.clicks)

    def test_transient_cell_misread_is_read_again(self):
        pop = FakePop(60, page=15); pop.glitch_labels = {'POP 대상 행 셀 확인': 1}
        run_checks(self.module, pop, [40])
        self.assertEqual(pop.clicks, [40])
        self.assertGreaterEqual([label for _, label, _ in pop.captures].count('POP 대상 행 셀 확인'), 2)

    def test_semicolon_in_hidden_value_or_missing_summary_is_not_trusted(self):
        pop = FakePop(60, page=15); pop.rows[50]['비고'] = '가;나'
        report, _ = pop.report('pop_fast')
        with self.assertRaises(self.module['SummaryUnavailable']):
            self.module['pop_view'](report, summary_rows=True)
        report, _ = FakePop(60, page=15, summaries=False).report('pop_fast')
        with self.assertRaises(self.module['SummaryUnavailable']):
            self.module['pop_view'](report, summary_rows=True)
        self.assertIsNone(self.module['summary_values']({'value': 'a;b; [truncated]', 'child_count': 2}))
        self.assertEqual(self.module['summary_values']({'value': 'a;b;', 'child_count': 2}), ['a', 'b'])

    def test_unexpected_change_in_hidden_row_blocks_final_verification(self):
        pop = FakePop(60, page=15)
        original = pop.capture
        def capture(target, label, stop):
            if label == '체크 검사 최종 상태 확인':
                pop.rows[2]['선택'] = '선택'   # 대상이 아닌 화면 밖 행이 바뀐 상황
            return original(target, label, stop)
        target = {'handle': TOP, 'pid': 1}
        first = pop.capture({**target, 'mode': 'pop_fast'}, 'POP 조회 후 전체 목록 1회 판독', Stop())
        coverage = self.module['collect_pop'](target, first, {}, pop, pop.capture, Stop(), lambda *a: None, summary_rows=True)
        with self.assertRaises(RuntimeError):
            self.module['check_matched'](target, {}, coverage, matches_for(pop, [58]), pop, capture, Stop(), lambda *a: None)
        self.assertNotIn('final_report', coverage)


class PopStepsTests(unittest.TestCase):
    """조회 직후 목록 읽기: 요약 판독 → 안정 확인 → (필요하면) 예전 전체 판독."""

    def steps(self, pop, numbers, summary_reading=True):
        module = new_module()
        self.assertIs(module['LARGE_LIST_SUMMARY_READING'], False)   # 배포 기본값: 예전 방식(전체 칸)
        module['LARGE_LIST_SUMMARY_READING'] = summary_reading
        module['CHECK_SETTLE_SECONDS'] = 0.05
        module['SEQUENCE'] = '01'
        module['ensure_sequence'] = lambda target, expected, api, capture, stop, emit, initial_report=None: pop.report('mes_rows')[0]
        module['validate_query'] = lambda report, binding: None
        module['match_rows'] = lambda source, rows: {'matched': matches_for(pop, numbers), 'already_selected': []}
        logs = []
        result = module['pop_steps']({'handle': TOP, 'pid': 1}, {}, {'sequence': '01'}, {'sequence': '01', 'candidates': []},
                                     pop, pop.capture, Stop(), lambda kind, value: logs.append(value) if kind == 'log' else None)
        return result, logs

    def test_default_reads_every_cell_exactly_like_before(self):
        pop = FakePop(60, page=15)
        result, _ = self.steps(pop, [3, 30, 58], summary_reading=False)
        self.assertEqual(result['check_status'], 'verified')
        self.assertEqual(sorted(pop.clicks), [3, 30, 58])
        modes = [mode for mode, _, _ in pop.captures]
        self.assertEqual((modes[0], modes[-1]), ('pop_full', 'pop_final'))
        self.assertNotIn('pop_fast', modes)
        self.assertNotIn('POP 목록 안정 확인', [label for _, label, _ in pop.captures])
        self.assertEqual(pop.captures[0][2], 60 * len(COLUMNS))    # 모든 줄 × 모든 칸

    def test_default_rereads_once_after_a_transient_misread(self):
        pop = FakePop(12, page=15); pop.glitch_labels = {'POP 조회 후 전체 목록 1회 판독': 1}
        result, _ = self.steps(pop, [2, 9], summary_reading=False)
        self.assertEqual(sorted(pop.clicks), [2, 9])
        self.assertEqual([label for _, label, _ in pop.captures][:2], ['POP 조회 후 전체 목록 1회 판독'] * 2)

    def test_large_list_uses_summary_reading_and_finishes(self):
        pop = FakePop(100, page=15)
        result, _ = self.steps(pop, [10, 50, 99])
        self.assertEqual(result['check_status'], 'verified')
        self.assertEqual(sorted(pop.clicks), [10, 50, 99])
        self.assertEqual(pop.captures[0][0], 'pop_fast')
        self.assertIn('POP 목록 안정 확인', [label for _, label, _ in pop.captures])

    def test_screen_without_usable_summaries_falls_back_to_full_reading(self):
        pop = FakePop(40, page=15, summaries=False)
        result, logs = self.steps(pop, [3, 30])
        self.assertEqual(sorted(pop.clicks), [3, 30])
        self.assertIn('pop_full', {mode for mode, _, _ in pop.captures})
        self.assertTrue(any('전체 셀 판독' in line for line in logs))

    def test_list_still_loading_is_read_again_before_any_click(self):
        pop = FakePop(40, page=15)
        def grow():
            pop.rows.append(dict(pop.rows[0], 프로젝트No='P9999')); pop.enabled.append(True)
        pop.mutate_after_first_list_read = grow
        result, logs = self.steps(pop, [3, 30])
        self.assertTrue(any('아직 바뀌는 중' in line for line in logs))
        self.assertEqual(result['coverage']['declared_rows'], 41)
        self.assertEqual(sorted(pop.clicks), [3, 30])


class ErrorRecordSuitabilityTests(unittest.TestCase):
    """세척완료가 멈췄을 때 남는 오류 기록만 보고 상황을 알 수 있는지(가짜 POP으로 처음부터 끝까지)."""

    def test_stopped_run_explains_where_how_far_and_what_happened(self):
        import time
        from test_host_stability import load_app
        app_module = load_app()
        wash = app_module.WashApp.__new__(app_module.WashApp)
        wash.started = time.monotonic(); wash.trail = []; wash.reads = []; wash.progress = {}; wash.last_result = None
        wash.run_sequence = '01'; wash.stop = Stop()
        wash.events = type('Q', (), {'put': lambda self, item: None})()
        records = []
        original = app_module.SuiteErrors.capture
        app_module.SuiteErrors.capture = lambda *args, **kwargs: records.append((args, kwargs))
        pop = FakePop(70, page=15); pop.cover = {40: 99}
        module = new_module(); module['CHECK_SETTLE_SECONDS'] = 0.05; module['SEQUENCE'] = '01'
        module['ensure_sequence'] = lambda *a, **k: pop.report('mes_rows')[0]
        module['validate_query'] = lambda report, binding: None
        module['match_rows'] = lambda source, rows: {'matched': matches_for(pop, [5, 20, 40, 66]), 'already_selected': []}
        def capture(target, label, stop):
            wash.emit('reading', (label, time.monotonic()))
            report = pop.capture(target, label, stop)
            wash.reads.append((label, target['mode'], 0.3, len(report['records'])))
            return report
        try:
            try:
                module['pop_steps']({'handle': TOP, 'pid': 1}, {}, {'sequence': '01'}, {'sequence': '01', 'candidates': []},
                                    pop, capture, Stop(), wash.emit)
            except RuntimeError as error:
                wash.emit('error', str(error))
        finally:
            app_module.SuiteErrors.capture = original
        (args, kwargs), = records
        self.assertIn('계속 가려져', str(args[0]))
        self.assertEqual(kwargs['stage'], 'POP 미반영 항목 재확인')        # 어디서
        context = kwargs['context']
        for expected in ('세척순번 01', 'POP 표: 한 줄 8칸 · 화면에 보이는 줄 15', 'POP 목록 70줄',   # 얼마나 큰 목록
                         '매칭 대상 4개', '체크 클릭 2회 · 체크 확인 2개',                              # 어디까지
                         '가장 오래:', 'POP 70행 판독', '40번째 줄 체크 칸이 가려짐',                    # 무슨 일이
                         '체크 칸이 잠시 가려져 있어 기다렸다 다시 확인합니다(3/3)', '중단: 체크 칸이 다른 창에 계속 가려져'):
            self.assertIn(expected, context)
        self.assertEqual(sorted(pop.clicks), [5, 20])


if __name__ == '__main__':
    unittest.main()
