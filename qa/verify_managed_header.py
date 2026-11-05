import os,sys,tempfile,tkinter as tk,json
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
 os.environ['LOCALAPPDATA']=tmp;os.environ['APPDATA']=tmp
 p=ROOT/'apps/jihunius/app.pyw';m=ModuleType('managed_header');m.__file__=str(p);sys.modules[m.__name__]=m
 exec(compile(p.read_text().replace('맑은 고딕','nanumbarungothic').replace('Consolas','courier'),str(p),'exec'),m.__dict__)
 root=tk.Tk();children=Mock();children.running_keys.return_value=[];children.material_visible.return_value=False
 tray=Mock();tray.start.return_value=True
 with patch.object(m.MachineMonitor,'start'),patch.object(m.IntegrationApp,'refresh_destination'),patch.object(m.IntegrationApp,'refresh_handover'),patch.object(m,'SuiteWindowsTray',return_value=tray),patch.object(m,'SuiteCompanionManager',return_value=children),patch.object(m.SuiteErrors,'Service'):
  app=m.IntegrationApp(root);updates=m.SuiteUpdater.attach(app,None,m.SUITE_APP_VERSION);errors=m.SuiteErrors.attach(app,Path(tmp)/'shared')
  updates.label.set('업데이트 확인 중')
  app.status.set('소재 저장 결과 확인 중입니다. 잠시만 기다려주세요.')
  errors.button.configure(text='오류 기록 100')
  for width in (1120,1000):
   root.geometry(str(width)+'x1100');root.update_idletasks()
   rows=[]
   for button in [*app._suite_buttons.values(),updates.button,errors.button]:
    rows.append(dict(text=button.cget('text'),mapped=bool(button.winfo_ismapped()),width=button.winfo_width(),required=button.winfo_reqwidth(),x=button.winfo_rootx()))
   print(json.dumps(dict(window=width,buttons=rows),ensure_ascii=False),flush=True)
   assert all(row['mapped'] and row['width']>=row['required'] for row in rows),rows
   widgets=[*app.tab_buttons.values(),app.handover_toggle,errors.button,updates.button,app.header_status_label]
   for left,right in zip(widgets,widgets[1:]):
    assert left.winfo_rootx()+left.winfo_width()<=right.winfo_rootx(),(str(left),str(right))
   assert widgets[-1].winfo_rootx()+widgets[-1].winfo_width()<=root.winfo_rootx()+root.winfo_width()
  from PIL import ImageGrab
  ImageGrab.grab(xdisplay=os.environ['DISPLAY']).crop((root.winfo_rootx(),root.winfo_rooty(),root.winfo_rootx()+root.winfo_width(),root.winfo_rooty()+190)).save(ROOT/'qa/managed-header.png')
  for timer in root.tk.call('after','info'):root.after_cancel(timer)
  app._finish_suite_shutdown()
