"""기간 통계: 수집이 끊긴 적이 있는 봉도 빼지 않고, 사용을 끝낸 모든 봉으로 봉당 평균을 냅니다(2026-11-11 사용자 결정)."""
import gc, tempfile, time, unittest
from pathlib import Path
import test_material_ui as ui_tests
from test_material_reporting import core, sync


def scenario(store, start):
    """1호기: 처음부터 끼워져 있던 봉 → 수집이 끊긴 봉 → 실시간 확인 없이 교체한 봉."""
    store.register_stock('10B', 10, start); store.assign_material(1, '10B', start)
    def observe(program, at): store.observe(dict(machine=1, program=program, state='RUN', part_count=''), at)
    observe('1001', start); observe('1002', start + 1); observe('1003', start + 2)       # 첫 봉(중간 시작): 가공 2
    store.rotate(1, start + 3)
    observe('1004', start + 4); observe('1005', start + 5)                               # 둘째 봉: 가공 2
    store.disconnected(1, start + 6, '응답 지연')                                         # 수집 끊김
    observe('1010', start + 100); observe('1011', start + 101)                           # 다시 연결(기준) 후 가공 1 → 3
    store.defect(1, start + 102)                                                         # 불량 1
    store.rotate(1, start + 103, manual=True)                                            # 실시간 확인 없이 교체
    observe('1020', start + 200); observe('1021', start + 201)                           # 셋째 봉: 가공 1
    store.rotate(1, start + 202, manual=True)


class AllRodsAverageTests(unittest.TestCase):
    def test_interrupted_and_manually_replaced_rods_are_all_averaged(self):
        for factory in (core.Store, sync.CommandStore):
            with self.subTest(store=factory.__name__), tempfile.TemporaryDirectory() as tmp:
                store = factory(Path(tmp) / 'db.sqlite3'); start = time.time() - 1000
                try:
                    scenario(store, start)
                    report = store.period_report(start - 1, start + 300)
                    total = report['totals']
                    self.assertEqual((total['consumed_rods'], total['eligible_rods'], total['excluded_rods']), (3, 3, 0))
                    self.assertEqual((total['completed_good'], total['completed_defects']), (5, 1))   # 양품 2+2+1, 불량 0+1+0
                    self.assertAlmostEqual(total['avg_good_per_rod'], 5 / 3)
                    self.assertAlmostEqual(total['avg_defects_per_rod'], 1 / 3)
                    self.assertEqual((total['eligible_good'], total['eligible_defects']), (5, 1))
                    ten = next(row for row in report['by_type'] if row['type_id'] == '10B')
                    self.assertEqual((ten['consumed_rods'], ten['eligible_rods']), (3, 3))
                    self.assertEqual(sum(row['consumed_rods'] for row in report['daily']), 3)
                    self.assertNotIn('제외', report['basis'])
                    # 끊김 표시는 지우지 않고 기록에 그대로 남는다(통계에서 빼지 않을 뿐).
                    ended = sorted((row for row in store.history() if row['ended']), key=lambda row: row['started'])
                    self.assertEqual([(bool(row['partial']), bool(row['gap'])) for row in ended],
                                     [(True, False), (False, True), (False, True)])
                    self.assertEqual([(row['total'], row['good'], row['defects']) for row in ended], [(2, 2, 0), (3, 2, 1), (1, 1, 0)])
                finally:
                    store.close()

    def test_counting_itself_is_unchanged_by_the_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = core.Store(Path(tmp) / 'db.sqlite3'); start = time.time() - 1000
            try:
                scenario(store, start)
                # 끊긴 동안 지나간 번호(1006~1009)는 세지 않았고, 다시 연결된 첫 번호(1010)는 기준값일 뿐이다.
                self.assertEqual(store.period_report(start - 1, start + 300)['totals']['production'], 6)
            finally:
                store.close()


class PeriodTabWithoutIncompleteTests(unittest.TestCase):
    setUp = ui_tests.MaterialUITests.setUp
    pump = ui_tests.MaterialUITests.pump

    def cleanup(self):
        ui_tests.MaterialUITests.cleanup(self)
        self.app.jobs.thread.join(2)
        self.app = None; self.root = None; self.session = None
        gc.collect()

    def test_period_tab_shows_averages_for_all_rods_and_no_incomplete_wording(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = core.Store(Path(tmp) / 'db.sqlite3'); start = time.time() - 1000
            try:
                scenario(store, start); report = store.period_report(start - 1, start + 300)
            finally:
                store.close()
        self.app._render_period(report); self.root.update()
        self.assertEqual(self.app.report_tree.cget('columns'), ('name', 'consumed', 'good', 'defects', 'avg_good', 'avg_defects'))
        self.assertEqual(self.app.daily_tree.cget('columns'), ('day', 'consumed', 'good', 'defects', 'avg_good', 'avg_defects'))
        total_row = self.app.report_tree.item(self.app.report_tree.get_children()[0], 'values')
        self.assertEqual(tuple(total_row[:4]), ('전체', '3', '5', '1'))
        self.assertNotIn('—', total_row[4:])                                  # 봉당 양품·불량이 계산되어 보임
        self.assertEqual(self.app.period_cards['good'][1].cget('text'), '양품 5개 ÷ 3봉')
        self.assertEqual(self.app.period_cards['defects'][1].cget('text'), '불량 1개 ÷ 3봉')
        summary = self.app.period_summary.cget('text')
        self.assertIn('소모 3봉', summary); self.assertIn('모든 봉', summary)
        for text in (summary, self.app.period_hint.cget('text'), ' '.join(str(self.app.report_tree.heading(c, 'text')) for c in self.app.report_tree.cget('columns'))):
            for word in ('불완전', '평균 제외', '평균 대상', '수집 공백', '중간 시작'):
                self.assertNotIn(word, text)


if __name__ == '__main__':
    unittest.main()
