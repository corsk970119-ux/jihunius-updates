"""Production package uses the managed updater and preserves the prior engines."""
import ast,base64,hashlib,re,sys,tempfile,unittest,zlib
from pathlib import Path
from unittest.mock import Mock,patch
from types import SimpleNamespace
from test_host_stability import load_app
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'releases/jihunius/2026.11.03.10'
sys.path.insert(0,str(ROOT/'tools'))
from embed_companions import companion_source


class NormalizeColors(ast.NodeTransformer):
 def visit_Constant(self,node):
  if isinstance(node.value,str) and re.fullmatch(r'#[0-9a-fA-F]{6}',node.value):
   node.value='#COLOR'
  return node


class NormalizeCalendarColors(NormalizeColors):
 def visit_ClassDef(self,node):
  if node.name=='DatePicker':
   for method in node.body:
    if isinstance(method,ast.FunctionDef) and method.name=='draw':
     for call in ast.walk(method):
      if isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute) and call.func.attr=='Button':
       for kw in call.keywords:
        if kw.arg=='fg':kw.value=ast.Constant(value='APPROVED_CALENDAR_FOREGROUND')
  return self.generic_visit(node)


def assignments(path):
 result={}
 for n in ast.parse(path.read_text()).body:
  if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name):
   try:result[n.targets[0].id]=ast.literal_eval(n.value)
   except (ValueError,TypeError):pass
 return result

# Approved 2026-11-10 (사용자 "수정사항 전부 반영"): read-only screen reader limits only.
APPROVED_READER_LIMITS=(
 ('count>=40000 || clock.Elapsed.TotalSeconds>=80','count>=15000 || clock.Elapsed.TotalSeconds>=35'),
 ('deadline = time.monotonic()+95','deadline = time.monotonic()+45'),
 ("else '95초 제한 시간'","else '45초 제한 시간'"))

def approved_reader_limits(text):
 for new,old in APPROVED_READER_LIMITS:
  text=text.replace(new,old)
 return text

class PrivatePackageTests(unittest.TestCase):
 def test_automation_and_conversion_payloads_unchanged(self):
  before=assignments(BASE/'app.pyw');after=assignments(ROOT/'apps/jihunius/app.pyw')
  keys=[k for k in before if (k.endswith('_SOURCE') or k.startswith('WASH_')) and isinstance(before[k],(str,bytes))]
  self.assertIn('WASH_MES_SOURCE',keys);self.assertIn('WASH_POP_SOURCE',keys)
  self.assertIn('STL_FINDER_SOURCE',keys)
  self.assertEqual(before['CARD_MODIFIER_BYTES'],after['CARD_MODIFIER_BYTES'])
  for k in keys:
   if k=='WASH_POP_SOURCE':
    # Only the completion-dialog reader/wait was intentionally changed.
    # check_capture: same conditions, clearer message when the reader limit is reached.
    allowed={'save_dialog_messages','save_dialog_button','save_checked_pop','check_capture'}
    old=ast.parse(before[k]);new=ast.parse(approved_reader_limits(after[k]))
    for tree in (old,new):
     tree.body=[n for n in tree.body if not (isinstance(n,ast.FunctionDef) and n.name in allowed)]
    self.assertEqual(ast.dump(old,include_attributes=False),ast.dump(new,include_attributes=False),k)
   elif k=='STL_FINDER_SOURCE':
    # Defaults and legacy-default loading changed intentionally. Path behavior
    # is covered by test_program_paths; the entire search engine stays pinned.
    old=ast.parse(before[k]);new=ast.parse(after[k])
    for tree in (old,new):
     tree.body=[n for n in tree.body if not (isinstance(n,ast.Assign)
        and isinstance(n.targets[0],ast.Name)
        and n.targets[0].id in {'DEFAULT_FOLDER','LEGACY_DEFAULT_FOLDER'})]
     # Approved visual refresh changes only ttk styling and literal colors.
     # Keep every search/ranking/matching function pinned to the prior release.
     tree.body=[n for n in tree.body if not (isinstance(n,ast.FunctionDef)
        and n.name=='configure_app_style')]
     NormalizeCalendarColors().visit(tree)
     for node in tree.body:
      if isinstance(node,ast.ClassDef) and node.name=='App':
       node.body=[n for n in node.body if not (isinstance(n,ast.FunctionDef) and n.name=='load_settings')]
    self.assertEqual(ast.dump(old,include_attributes=False),ast.dump(new,include_attributes=False),k)
   elif k=='WASH_MES_SOURCE':self.assertEqual(before[k],approved_reader_limits(after[k]),k)
   else:self.assertEqual(before[k],after[k],k)
  # Error hooks are observational. All original wash-log application definitions
  # still match the last release after removing only the new diagnostic calls.
  previous=assignments(ROOT/'releases/jihunius/2026.11.04.2/app.pyw')['SUITE_COMPANIONS']['wash-log']
  old=zlib.decompress(base64.b64decode(previous['compressed'])).decode()
  class StripDiagnostics(NormalizeColors):
   def visit_Expr(self,node):
    if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='_diagnostic_error':return None
    return self.generic_visit(node)
   def visit_Try(self,node):
    # Approved N3 visual: shared thin-scrollbar style call only (ttk layout/colors, no behavior).
    if any(isinstance(n,ast.alias) and n.name=='install_thin_scrollbars' for n in ast.walk(node)):return None
    return self.generic_visit(node)
   def visit_For(self,node):
    # Approved N3 visual: thin scrollbar style loop only (ttk layout/colors, no behavior).
    if isinstance(node.target,ast.Tuple) and [getattr(e,'id','') for e in node.target.elts]==['_orient','_sticky']:return None
    return self.generic_visit(node)
   def visit_ClassDef(self,node):
    if node.name=='RoundedButton':
     for method in node.body:
      if isinstance(method,ast.FunctionDef) and method.name=='draw':
       # Approved shallow bevel: strip only decorative lines, keep the full
       # underlying polygon/text/focus code and all interactions pinned.
       method.body=[statement for statement in method.body if not (
        isinstance(statement,ast.If) and statement.body and all(
         isinstance(item,ast.Expr) and isinstance(item.value,ast.Call)
         and isinstance(item.value.func,ast.Attribute)
         and item.value.func.attr=='create_line' for item in statement.body))]
       for call in ast.walk(method):
        if isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute) and call.func.attr=='create_polygon':
         for kw in call.keywords:
          if kw.arg=='outline':kw.value=ast.Constant(value='APPROVED_BUTTON_OUTLINE')
    return self.generic_visit(node)
  old_defs={n.name:ast.dump(StripDiagnostics().visit(n),include_attributes=False) for n in ast.parse(old).body if isinstance(n,(ast.ClassDef,ast.FunctionDef))}
  for n in ast.parse((ROOT/'src/wash_log.py').read_text()).body:
   if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name!='_diagnostic_error':
    self.assertEqual(ast.dump(StripDiagnostics().visit(n),include_attributes=False),old_defs[n.name],n.name)
 def test_embedded_sources_match_reviewed_sources(self):
  payloads=assignments(ROOT/'apps/jihunius/app.pyw')['SUITE_COMPANIONS']
  self.assertEqual(set(payloads),{'wash-log','protrusion','special-table','material'})
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
  with patch.object(m.SuiteUpdater,'managed_context',return_value=context),patch.object(m.SuiteUpdater,'managed_lease',return_value=lease),patch.object(m.SuiteUpdater,'attach') as attach,patch.object(m.SuiteUpdater,'mark_ready') as ready,patch.object(m,'IntegrationApp',return_value=app),patch.object(m,'configure_windows_app_identity'),patch('tkinter.Tk',return_value=root),patch.object(m.SuiteErrors,'install'),patch.object(m.SuiteErrors,'attach'):
   m.main();attach.assert_called_once_with(app,context,m.SUITE_APP_VERSION);ready.assert_called_once_with(context)
   root.mainloop.assert_called_once();lease.release.assert_called_once()

if __name__=='__main__':unittest.main()
