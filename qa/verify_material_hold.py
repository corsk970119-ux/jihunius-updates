import json,os,sys,tempfile,time,tkinter as tk
from pathlib import Path
from unittest.mock import patch
from PIL import ImageGrab
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tests')]
import material_sync as sync
import material_client as client
import material_ui as ui
from test_material_sync import QuietCollector
client.lan_address=lambda:'127.0.0.1'
class MappedCollector(QuietCollector):
 def checkpoint(self,n,token):
  if not self.running:raise ValueError('stopped')
  self.out.put(('sample','192.168.1.'+str(n),1,dict(machine=n,program='1001',state='STOP',part_count='0'),time.time(),token,None))

def wait(root,condition,timeout=8):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  root.update()
  if condition():return
  time.sleep(.01)
 raise AssertionError('state not reached')
def shot(root,name):
 root.update();x,y=root.winfo_rootx(),root.winfo_rooty()
 ImageGrab.grab(xdisplay=os.environ['DISPLAY']).crop((x,y,x+root.winfo_width(),y+root.winfo_height())).save(ROOT/'qa'/name)

with tempfile.TemporaryDirectory() as tmp:
 folder=Path(tmp);s=sync.CommandStore(folder/'main/counter.sqlite3');at=time.time()-100
 for kind in sync.core.MATERIAL_TYPES:s.register_stock(kind,50,at)
 for n in range(1,10):
  kind=('10Z','10B','12')[(n-1)%3];s.assign_material(n,kind,at)
  s.observe(dict(machine=n,program='1001',state='STOP',part_count='0'),at)
  s.rotate(n,at+.1)
  for i in range(n*3):s.observe(dict(machine=n,program=str(1002+i),state='STOP',part_count='0'),at+1+i)
  s.defect(n,at+40)
 s.close()
 session=client.ClientSession(folder/'main',folder/'share',MappedCollector);session.toggle(True)
 root=tk.Tk();errors=[];root.report_callback_exception=lambda *a:errors.append(str(a))
 app=ui.SyncedApplication(root,session);root.geometry('1000x790+30+30')
 wait(root,lambda:app.connected and session.state['collection'])
 sub=client.ClientSession(folder/'sub',folder/'share',QuietCollector)
 wait(root,lambda:sub.state is not None)
 assert not sub.coordinator.settings['enabled']
 for n in range(1,10):sub.command('switch_14',[n],sub.state['rows'][n-1]['expected'])
 wait(root,lambda:all(row.get('parked') for row in app.store.state['rows']))
 for widgets in app.rows.values():
  assert widgets['switch14'].cget('text')=='원소재로 복귀'
  for key in ('material','switch14'):
   w=widgets[key]
   assert w.winfo_width()>=w.winfo_reqwidth(),(key,w.winfo_width(),w.winfo_reqwidth())
   assert w.winfo_rootx()+w.winfo_width()<=root.winfo_rootx()+1000
   assert w.winfo_rooty()+w.winfo_height()<=root.winfo_rooty()+790
 shot(root,'material-hold-all.png')
 saved=app.store.snapshot(1)['parked']
 with patch('tkinter.messagebox.askokcancel',return_value=True):app.rows[1]['switch14'].invoke()
 wait(root,lambda:app.store.snapshot(1)['active_material']==saved['material_id'])
 assert app.store.snapshot(1)['good']==saved['good']
 wait(root,lambda:sub.state['rows'][0]['active_material']==saved['material_id'])
 shot(root,'material-hold-return.png')
 app.on_close();assert root.state()=='withdrawn'
 assert session.coordinator.authority.collection
 sub.close();sub.thread.join(10);app.shutdown();wait(root,lambda:app.closed)
 assert not errors,errors
 report=dict(window=[1000,790],nine_rows_fit=True,toggle_labels=True,sub_off_switch=True,return_same_rod=True,hide_keeps_collection=True,tk_errors=errors,synthetic_monitoring=True)
 (ROOT/'qa/hold-ui.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
