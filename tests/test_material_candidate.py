import importlib.util,sys,tempfile,unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

class CandidateTests(unittest.TestCase):
 def test_candidate_does_not_launch_or_attach_public_updater(self):
  try:import build_material_candidate as builder
  except ImportError:builder=None
  self.assertIsNotNone(builder,'Private candidate packaging missing')
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'candidate.pyw';builder.build(path,ROOT)
   m=ModuleType('candidate_test');m.__file__=str(path);sys.modules[m.__name__]=m
   exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__)
   root=Mock();app=Mock();lease=Mock();lease.acquire.return_value=True
   with patch.object(m.SuiteUpdater,'FileLock',return_value=lease),patch.object(m.SuiteUpdater,'launch') as launch,patch.object(m.SuiteUpdater,'attach') as attach,patch.object(m.SuiteUpdater,'mark_ready') as mark,patch.object(m,'IntegrationApp',return_value=app),patch.object(m,'configure_windows_app_identity'),patch('tkinter.Tk',return_value=root),patch.object(m.SuiteErrors,'install'),patch.object(m.SuiteErrors,'attach'):
    m.main();launch.assert_not_called();attach.assert_not_called();mark.assert_not_called()
    root.mainloop.assert_called_once();lease.release.assert_called_once()
