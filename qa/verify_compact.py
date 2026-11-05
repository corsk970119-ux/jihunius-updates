"""Render the real host at desktop sizes; no company drives or machines used."""
import os, sys, json, tempfile, time, tkinter as tk
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, patch
from PIL import ImageGrab

ROOT = Path(__file__).resolve().parents[1]
scale = float(sys.argv[1]) if len(sys.argv) > 1 else 1.3333
suffix = str(round(scale * 75))
def children(widget):
    for w in widget.winfo_children():
        yield w
        yield from children(w)

def capture(root, name):
    root.update();time.sleep(.15);root.update()
    x,y=root.winfo_rootx(),root.winfo_rooty()
    ImageGrab.grab(xdisplay=os.environ['DISPLAY']).crop(
        (x,y,x+root.winfo_width(),y+root.winfo_height())).save(ROOT/'qa'/name)

with tempfile.TemporaryDirectory() as tmp:
    os.environ['LOCALAPPDATA']=tmp;os.environ['APPDATA']=tmp
    p=ROOT/'apps/jihunius/app.pyw'
    m=ModuleType('compact_host_qa');m.__file__=str(p);sys.modules[m.__name__]=m
    exec(compile(p.read_text().replace('맑은 고딕','nanumbarungothic').replace('Consolas','courier'),str(p),'exec'),m.__dict__)
    root=tk.Tk();root.tk.call('tk','scaling',scale)
    errors=[];root.report_callback_exception=lambda *args:errors.append(str(args))
    manager=Mock();manager.running_keys.return_value=[];manager.material_visible.return_value=False
    tray=Mock();tray.start.return_value=True
    with patch.object(m.MachineMonitor,'start'),patch.object(m.IntegrationApp,'refresh_destination'),patch.object(m.IntegrationApp,'refresh_handover'),patch.object(m,'SuiteWindowsTray',return_value=tray),patch.object(m,'SuiteCompanionManager',return_value=manager),patch.object(m.SuiteErrors,'Service'):
        app=m.IntegrationApp(root)
        updates=m.SuiteUpdater.attach(app,None,m.SUITE_APP_VERSION)
        errors_ui=m.SuiteErrors.attach(app,Path(tmp)/'shared')
        errors_ui.service.snapshot.return_value={'unread':0}
        app.number_input.insert('1.0','\n'.join('O'+str(n) for n in range(1001,1018)))
        for n in range(14):app.drive_contents.insert('end','O'+str(1001+n)+'.nc')
        app.apply_machine_status({n:dict(machine=n,prm_no='O1001',color='green',state='RUN') for n in range(1,10)})
        bounds=[]
        for width,height in ((1120,830),(1000,800)) if scale < 1.4 else ((1250,940),(1120,900)):
            root.geometry(f'{width}x{height}+20+20');root.update_idletasks()
            for key in ('cnc','stl','wash','cnc'):
                app.select_app_tab(key);root.update_idletasks()
                clipped=[]
                for w in children(root):
                    if not w.winfo_ismapped() or w.winfo_class() not in ('TButton','TRadiobutton','TEntry','TCombobox'):continue
                    # Scrollable row contents are intentionally excluded.
                    if w.winfo_toplevel() is not root:continue
                    if (w.winfo_rootx()<root.winfo_rootx() or w.winfo_rooty()<root.winfo_rooty()
                        or w.winfo_rootx()+w.winfo_width()>root.winfo_rootx()+root.winfo_width()
                        or w.winfo_rooty()+w.winfo_height()>root.winfo_rooty()+root.winfo_height()):
                        clipped.append(str(w))
                bounds.append(dict(tab=key,requested=[width,height],actual=[root.winfo_width(),root.winfo_height()],minimum=list(root.minsize()),clipped=clipped))
                assert not clipped,bounds[-1]
                capture(root,f'balanced-{suffix}-{width}-{key}.png')
            for n,row in app.material_quick.rows.items():
                for name in ('defect','rotate'):
                    w=row[name];assert w.winfo_width()>=w.winfo_reqwidth(),(n,name,w.winfo_width(),w.winfo_reqwidth())
        for button in [*app._suite_buttons.values(),updates.button,errors_ui.button]:
            assert button.winfo_width()>=button.winfo_reqwidth(),(button.cget('text'),button.winfo_width(),button.winfo_reqwidth())
        print(json.dumps(bounds,ensure_ascii=False),flush=True)
        primary=[app.empty_button,app.drive_delete_button,app.import_button,app.drive_add_button,app.drive_refresh_button]
        fonts=[app.style.lookup(w.cget('style'),'font') for w in primary]
        heights=[w.winfo_height() for w in primary]
        assert len(set(fonts))==1,fonts
        assert len(set(heights))==1,heights
        app.close();root.update_idletasks()
        dialog=app._suite_close_dialog
        buttons=[w for w in children(dialog) if w.winfo_class()=='TButton']
        assert len({w.winfo_height() for w in buttons})==1
        assert {app.style.lookup(w.cget('style'),'font') for w in buttons}==set(fonts)
        capture(dialog,f'balanced-{suffix}-close.png')
        next(w for w in buttons if w.cget('text')=='취소').invoke();root.update_idletasks()
        assert root.winfo_viewable()
        app.toggle_handover();root.update_idletasks();capture(root,f'balanced-{suffix}-handover.png')
        app.toggle_handover();root.update_idletasks()
        app.status.set('소재 저장 결과 확인 중입니다. 잠시만 기다려주세요.')
        errors_ui.button.configure(text='오류 기록 100');updates.label.set('업데이트 확인 중')
        root.update_idletasks()
        widgets=[*app.tab_buttons.values(),app.handover_toggle,errors_ui.button,updates.button,app.header_status_label]
        for left,right in zip(widgets,widgets[1:]):
            assert left.winfo_rootx()+left.winfo_width()<=right.winfo_rootx(),(str(left),str(right))
        print(json.dumps(dict(fonts=fonts,heights=heights,errors=errors),ensure_ascii=False),flush=True)
        assert not errors,errors
        for timer in root.tk.call('after','info'):root.after_cancel(timer)
        app._finish_suite_shutdown()
