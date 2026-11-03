"""Production package uses the managed updater and preserves the prior engines."""
import ast,base64,hashlib,sys,tempfile,unittest,zlib
from pathlib import Path
from unittest.mock import Mock,patch
from types import SimpleNamespace
from test_host_stability import load_app
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'releases/jihunius/2026.11.03.10'
sys.path.insert(0,str(ROOT/'tools'))
from embed_companions import companion_source


def assignments(path):
 result={}
 for n in ast.parse(path.read_text()).body:
  if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name):
   try:result[n.targets[0].id]=ast.literal_eval(n.value)
   except (ValueError,TypeError):pass
 return result

class PrivatePackageTests(unittest.TestCase):
 def test_automation_and_conversion_payloads_unchanged(self):
  before=assignments(BASE/'app.pyw');after=assignments(ROOT/'apps/jihunius/app.pyw')
  keys=[k for k in before if (k.endswith('_SOURCE') or k.startswith('WASH_')) and isinstance(before[k],(str,bytes))]
  self.assertIn('WASH_MES_SOURCE',keys);self.assertIn('WASH_POP_SOURCE',keys)
  self.assertIn('STL_FINDER_SOURCE',keys)
  self.assertEqual(before['CARD_MODIFIER_BYTES'],after['CARD_MODIFIER_BYTES'])
  for k in keys:self.assertEqual(before[k],after[k],k)
  self.assertEqual(hashlib.sha256((ROOT/'src/wash_log.py').read_bytes()).hexdigest(),'229a4f2544a82bf3e505f0b4ef444edf1725b889ff028a7bd4d14421a7343d61')
 def test_embedded_sources_match_reviewed_sources(self):
  payloads=assignments(ROOT/'apps/jihunius/app.pyw')['SUITE_COMPANIONS']
  self.assertEqual(set(payloads),{'wash-log','protrusion','special-table'})
  for key,payload in payloads.items():
   data=zlib.decompress(base64.b64decode(payload['compressed']))
   self.assertEqual(data,companion_source(ROOT,key),key)
   self.assertEqual(hashlib.sha256(data).hexdigest(),payload['sha256'])
   compile(data,key,'exec')
 def test_production_launch_uses_updater_entrypoint(self):
  m=load_app()
  self.assertFalse(hasattr(m,'SUITE_PRIVATE_BUILD'))
  with patch.object(m.SuiteUpdater,'managed_context',return_value=None),patch.object(m.SuiteUpdater,'launch',return_value=0) as launch,patch.object(m,'IntegrationApp') as app:
   m.main();launch.assert_called_once();app.assert_not_called()
 def test_managed_production_launch_attaches_update_checks(self):
  m=load_app();root=Mock();app=Mock();lease=Mock();context={'test':True}
  with patch.object(m.SuiteUpdater,'managed_context',return_value=context),patch.object(m.SuiteUpdater,'managed_lease',return_value=lease),patch.object(m.SuiteUpdater,'attach') as attach,patch.object(m.SuiteUpdater,'mark_ready') as ready,patch.object(m,'IntegrationApp',return_value=app),patch.object(m,'configure_windows_app_identity'),patch('tkinter.Tk',return_value=root):
   m.main();attach.assert_called_once_with(app,context,m.SUITE_APP_VERSION);ready.assert_called_once_with(context)
   root.mainloop.assert_called_once();lease.release.assert_called_once()

if __name__=='__main__':unittest.main()
