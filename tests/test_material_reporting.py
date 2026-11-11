"""Hand-calculated CEO report fixtures: completed cohort, exclusions, undo, stock."""
import sys,tempfile,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import material_counter as core
import material_sync as sync

class ReportingTests(unittest.TestCase):
 def test_completed_cohort_with_partial_and_early_discard(self):
  for factory in (core.Store,sync.CommandStore):
   with self.subTest(store=factory.__name__),tempfile.TemporaryDirectory() as tmp:
    s=factory(Path(tmp)/'db.sqlite3');t=time.time()-100
    try:
     s.register_stock('10Z',10,t);s.assign_material(1,'10Z',t)
     def observe(p,at):s.observe(dict(machine=1,program=p,state='STOP',part_count='999'),at)
     observe('1001',t);observe('1002',t+1);s.rotate(1,t+2)
     observe('1003',t+3);observe('1004',t+4);s.defect(1,t+5);s.rotate(1,t+6,early=True)
     r=s.period_report(t,t+10)['totals']
     expected={'consumed_rods':2,'normal_rods':1,'early_rods':1,'loaded_rods':2,
       'eligible_rods':1,'excluded_rods':1,'completed_production':3,'completed_good':2,
       'completed_defects':1,'avg_good_per_rod':1.0,'avg_defects_per_rod':1.0}
     # 첫 봉(집계 시작 때 이미 끼워져 있던 봉)은 평균에서 제외: 둘째 봉 양품 1·불량 1만 계산.
     for key,value in expected.items():self.assertEqual(r[key],value,key)
     self.assertEqual(s.inventory()[0]['quantity'],8)
     limited=s.period_report(t+2.5,t+7)['totals']
     self.assertEqual((limited['consumed_rods'],limited['completed_good'],limited['completed_defects']),(1,1,1))
     s.undo(1,t+7);r=s.period_report(t,t+10)['totals']
     self.assertEqual((r['consumed_rods'],r['eligible_rods'],r['loaded_rods']),(1,0,1))
     self.assertIsNone(r['avg_good_per_rod']);self.assertEqual(s.inventory()[0]['quantity'],9)
     self.assertEqual((s.snapshot(1)['good'],s.snapshot(1)['defects']),(1,1))
    finally:s.close()
