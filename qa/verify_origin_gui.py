import json, os, sys, tempfile, time, tkinter as tk
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    os.environ['LOCALAPPDATA']=tmp;os.environ['APPDATA']=tmp
    origin=Path(tmp)/'공유'/'지후니우스.pyw';origin.parent.mkdir()
    origin.write_bytes((ROOT/'releases/jihunius/2026.11.09.2/app.pyw').read_bytes())
    old=origin.read_bytes()
    path=ROOT/'apps/jihunius/app.pyw'
    m=ModuleType('origin_gui_smoke');m.__file__=str(origin);sys.modules[m.__name__]=m
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__)
    u=m.SuiteUpdater;store=u.Store(u.root_for(origin),origin,'2026.11.09.2');store.prepare()
    item=json.loads((ROOT/'channels/stable.json').read_text())['apps']['jihunius']
    store.stage(item,path.read_bytes());nonce='c'*32;store.request(item,nonce)
    assert store.consume_request(nonce,0)
    context=dict(root=store.root,origin=str(origin),current=item,base_version='2026.11.09.2',nonce=nonce,supervisor_pid=os.getpid())
    u.write_json(store.root/'session.json',dict(nonce=nonce,current=item,pid=os.getpid()))
    tray=Mock();tray.start.return_value=True
    children=Mock();children.running_keys.return_value=[];children.material_visible.return_value=False;children.sessions={}
    root=tk.Tk();errors=[];root.report_callback_exception=lambda *args:errors.append(str(args))
    with patch.object(m.MachineMonitor,'start'),patch.object(m.IntegrationApp,'refresh_destination'),patch.object(m.IntegrationApp,'refresh_handover'),patch.object(m,'SuiteWindowsTray',return_value=tray),patch.object(m,'SuiteCompanionManager',return_value=children),patch.object(u,'check_offer',return_value={'kind':'current'}):
        app=m.IntegrationApp(root);controller=u.attach(app,context,m.SUITE_APP_VERSION)
        u.mark_ready(context)
        ticks=[]
        def heartbeat():
            ticks.append(time.monotonic())
            if not controller.closed:root.after(25,heartbeat)
        heartbeat();deadline=time.monotonic()+15
        while controller.origin_result is None and time.monotonic()<deadline:
            root.update();time.sleep(.01)
        assert controller.origin_result and controller.origin_result['kind']=='updated',controller.origin_result
        assert origin.read_bytes()==path.read_bytes()
        assert origin.with_name('.'+origin.name+'.previous').read_bytes()==old
        controller.open();root.update()
        assert '원본 파일도 최신 버전으로 교체' in controller.status.get()
        assert controller.button.cget('style')=='Popup.TButton'
        app.year_value.set('2027');assert m.load_program_year()==2027
        assert len(ticks)>=5
        report=dict(real_tk=True,real_packaged_worker=True,old_origin='2026.11.09.2',new_origin=m.SUITE_APP_VERSION,
                    same_filename=True,one_backup=True,year_preference_retained=True,ui_heartbeat_ticks=len(ticks),callback_errors=errors)
        assert not errors,errors
        app._finish_suite_shutdown()
        (ROOT/'qa/origin-gui.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report))
