import json,os,sys,tempfile,time,tkinter as tk
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock,patch
from PIL import ImageGrab
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tests')]
import material_counter as core
import material_client as client
import material_ui as ui
from test_material_sync import QuietCollector
client.lan_address=lambda: "127.0.0.1"  # local TCP fixture; real LAN is unavailable here

def pump(root,seconds=.3):
 end=time.monotonic()+seconds
 while time.monotonic()<end:root.update();time.sleep(.01)
def shot(root,name):
 root.update();x,y=root.winfo_rootx(),root.winfo_rooty()
 ImageGrab.grab(xdisplay=os.environ['DISPLAY']).crop((x,y,x+root.winfo_width(),y+root.winfo_height())).save(ROOT/'qa'/name)
with tempfile.TemporaryDirectory() as tmp:
 os.environ['LOCALAPPDATA']=tmp;os.environ['APPDATA']=tmp
 p=ROOT/'apps/jihunius/app.pyw';m=ModuleType('material_host_qa');m.__file__=str(p);sys.modules[m.__name__]=m
 source=p.read_text().replace('맑은 고딕','nanumbarungothic').replace('Consolas','courier')
 exec(compile(source,str(p),'exec'),m.__dict__)
 root=tk.Tk();errors=[];root.report_callback_exception=lambda *a:errors.append(str(a))
 tray=Mock();tray.start.return_value=True;children=Mock();children.running_keys.return_value=[];children.material_visible.return_value=False
 with patch.object(m.MachineMonitor,'start'),patch.object(m.IntegrationApp,'refresh_destination'),patch.object(m.IntegrationApp,'refresh_handover'),patch.object(m,'SuiteWindowsTray',return_value=tray),patch.object(m,'SuiteCompanionManager',return_value=children):
  app=m.IntegrationApp(root);root.geometry('1000x900+20+20');pump(root)
  for buttons in ([*app._suite_buttons.values()],[*app.tab_buttons.values(),app.handover_toggle,app.header_status_label]):
   boxes=[(w.winfo_rootx(),w.winfo_width(),w.cget('text')) for w in buttons]
   for a,b in zip(boxes,boxes[1:]):assert a[0]+a[1]<=b[0],boxes
   assert boxes[-1][0]+boxes[-1][1]<=root.winfo_rootx()+1000,boxes
  assert app.material_button.master is app._suite_buttons['special-table'].master
  assert app.material_button.cget('style')==app._suite_buttons['special-table'].cget('style')
  previous_right=0
  for n,widgets in app.material_quick.rows.items():
   assert widgets['name'].cget('text')==str(n)+'호기'
   assert widgets['defect'].winfo_rooty()<widgets['rotate'].winfo_rooty()
   assert widgets['cell'].winfo_rootx()>=previous_right
   previous_right=widgets['cell'].winfo_rootx()+widgets['cell'].winfo_width()
   for name in ('defect','rotate'):
    w=widgets[name]
    assert w.winfo_rootx()+w.winfo_width()<=root.winfo_rootx()+root.winfo_width()
    assert w.winfo_rooty()+w.winfo_height()<=root.winfo_rooty()+root.winfo_height()
  shot(root,'material-host.png')
  for timer in root.tk.call('after','info'):root.after_cancel(timer)
  app._finish_suite_shutdown();assert not errors,errors
 folder=Path(tmp)/'main';folder.mkdir();s=core.Store(folder/'counter.sqlite3')
 for kind in core.MATERIAL_TYPES:s.register_stock(kind,50)
 for n in core.MACHINES:s.assign_material(n,list(core.MATERIAL_TYPES)[(n-1)%4])
 for n,count in ((1,2),(2,1),(3,1),(4,2)):
  for i in range(count):
   at=time.time()-90+i
   s.observe(dict(machine=n,program=str(1001+i),state='STOP',part_count='0'),at)
   s.rotate(n,at+.1)
 s.close()
 session=client.ClientSession(folder,Path(tmp)/'share',QuietCollector);session.toggle(True)
 root=tk.Tk();app=ui.SyncedApplication(root,session);root.geometry('1060x810+50+50');pump(root,1.3)
 authority=session.coordinator.authority
 for n in core.MACHINES:
  for p in ('1001','1002','1003'):
   authority.samples.put(('sample','192.168.1.'+str(n),1,dict(machine=n,program=p,state='STOP',part_count='8'),time.time(),None,None))
 pump(root,1.5)
 sub=client.ClientSession(Path(tmp)/'sub',Path(tmp)/'share',QuietCollector)
 limit=time.monotonic()+4
 while sub.state is None and time.monotonic()<limit:pump(root,.05)
 assert sub.state is not None and not sub.coordinator.settings['enabled']
 sub.command('defect',[1],sub.state['rows'][0]['expected'])
 limit=time.monotonic()+5
 while app.store.snapshot(1)['defects']!=1 and time.monotonic()<limit:pump(root,.05)
 assert app.store.snapshot(1)['good']==1 and app.store.snapshot(1)['defects']==1
 shot(root,'material-popup.png')
 app.tabs.select(app.inventory_tab);pump(root,1.3);shot(root,'material-stock.png')
 app.tabs.select(app.period_tab);pump(root,1.3);shot(root,'material-period.png')
 assert app._period_report is not None
 assert app.period_cards['diameter10'][0].cget('text')=='3 봉'
 assert app.period_cards['diameter12'][0].cget('text')=='1 봉'
 assert app.period_cards['diameter14'][0].cget('text')=='2 봉'
 for widgets in app.rows.values():assert 'rotate' not in widgets and 'defect' not in widgets
 app.on_close();assert root.state()=='withdrawn';assert authority.collection
 sub.close();sub.thread.join(10);app.shutdown()
 limit=time.monotonic()+8
 while not app.closed and time.monotonic()<limit:pump(root,.05)
 assert app.closed
 (ROOT/'qa/material-ui.json').write_text(json.dumps(dict(host_min_width=1000,popup_size=[1060,810],header_nonoverlap=True,sub_off_sync_verified=True,hide_keeps_collection=True,clean_shutdown=True,synthetic_monitoring=True),indent=2))
 print('Host placement, original popup size, sub-OFF synchronized defect, reports, hide/exit verified')
