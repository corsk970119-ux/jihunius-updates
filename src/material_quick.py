"""Main-window material input using the existing companion's durable command queue."""
import json
import os
from pathlib import Path
import time
import uuid

def read(path,default=None):
    try:
        with Path(path).open('rb') as stream:data=stream.read(131073)
        if len(data)>131072:raise ValueError('소재 빠른 입력 파일이 너무 큽니다.')
        return json.loads(data)
    except FileNotFoundError:return default

def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with temporary.open('w',encoding='utf8') as stream:
            json.dump(value,stream,ensure_ascii=False,allow_nan=False);stream.flush();os.fsync(stream.fileno())
        os.replace(str(temporary),str(path))
    finally:
        try:temporary.unlink()
        except FileNotFoundError:pass

def remove(path):
    try:Path(path).unlink()
    except FileNotFoundError:pass

class QuickChannel:
    def __init__(self,manager,path):
        self.manager=manager;self.path=Path(path);self.pending=read(path,{})
        if not isinstance(self.pending,dict) or len(self.pending)>20:
            raise ValueError('소재 빠른 입력의 확인 대기 파일을 확인해주세요.')
        for key,item in self.pending.items():
            if (not isinstance(key,str) or len(key)!=32 or any(c not in '0123456789abcdef' for c in key)
                    or not isinstance(item,dict) or not isinstance(item.get('request'),dict)
                    or item['request'].get('id')!=key or item['request'].get('method') not in ('defect','rotate')
                    or not isinstance(item['request'].get('args'),list) or not item['request']['args']
                    or type(item['request']['args'][0]) is not int or not 1<=item['request']['args'][0]<=9):
                raise ValueError('소재 빠른 입력의 확인 대기 파일이 올바르지 않습니다.')
        self.state={};self.checked_at=0
    def rotation_context(self,n):
        if not self.state.get('connected') or time.monotonic()-self.checked_at>6:
            raise ValueError('소재 사용량 조사 연결을 확인한 뒤 입력해주세요.')
        row=next(r for r in self.state['rows'] if r['machine']==n)
        if row.get('busy') or any(v['request']['args'][0]==n for v in self.pending.values()):
            raise ValueError('이 호기는 저장 확인 중입니다.')
        if not row.get('can_rotate'):raise ValueError('소재교체가 가능한 상태인지 확인해주세요.')
        return (self.state['owner'],self.state['epoch'],
                *(row['expected'][key] for key in ('material','next_type','material_type')),
                row['expected'].get('switch_revision'))
    def submit(self,method,n,confirmed=None):
        if method not in ('defect','rotate') or type(n) is not int or not 1<=n<=9:raise ValueError('잘못된 소재 입력입니다.')
        state=self.state
        if not state.get('connected') or time.monotonic()-self.checked_at>6:
            raise ValueError('소재 사용량 조사 연결을 확인한 뒤 입력해주세요.')
        if any(v['request']['args'][0]==n for v in self.pending.values()):raise ValueError('이 호기는 저장 확인 중입니다.')
        if confirmed is not None and confirmed!=self.rotation_context(n):
            raise ValueError('확인 중 소재 정보가 변경되었습니다. 최신 내용을 확인한 뒤 다시 눌러주세요.')
        row=next(r for r in state['rows'] if r['machine']==n)
        token=uuid.uuid4().hex
        request=dict(id=token,client=state['client'],epoch=state['epoch'],method=method,
                     args=[n] if method=='defect' else [n,False],expected=row['expected'],expires=state['at']+30)
        pending=dict(self.pending);pending[token]=dict(owner=state['owner'],request=request)
        if len(pending)>20:raise ValueError('먼저 저장 확인 대기 중인 입력을 확인해주세요.')
        write(self.path,pending);self.pending=pending
        return token
    def poll(self):
        results=[];self.state={}
        if 'material' not in self.manager.running_keys():return self.state,results
        folder,nonce=self.manager.sessions['material']
        value=read(folder/'material-status.json',{})
        if not isinstance(value,dict):raise ValueError('소재 연결 상태 파일을 확인해주세요.')
        if value.get('nonce')==nonce and 0<=time.time()-value.get('at',0)<=7:
            self.state=value.get('quick',{})
            self.checked_at=time.monotonic()
        for token,item in list(self.pending.items()):
            request_path=folder/('material-quick-'+token+'.json')
            response_path=folder/('material-result-'+token+'.json')
            response=read(response_path,{})
            if response.get('nonce')==nonce and response.get('id')==token and isinstance(response.get('result'),dict):
                pending=dict(self.pending);del pending[token]
                write(self.path,pending);self.pending=pending
                results.append(dict(machine=item['request']['args'][0],method=item['request']['method'],result=response['result']))
                remove(request_path);remove(response_path)
            elif not request_path.exists():
                write(request_path,dict(nonce=nonce,**item))
        return self.state,results

class QuickBridge:
    def __init__(self,app,folder,nonce):
        self.app=app;self.folder=Path(folder);self.nonce=nonce;self.inflight=set()
        app.session.quick_active=True
    def has_pending(self):return bool(self.inflight or next(self.folder.glob('material-quick-*.json'),None))
    def finish(self,token,result):
        path=self.folder/('material-quick-'+token+'.json')
        if token not in self.inflight and not path.exists():return
        try:
            write(self.folder/('material-result-'+token+'.json'),dict(nonce=self.nonce,id=token,result=result))
            remove(path)
        finally:self.inflight.discard(token)
    def poll(self):
        app=self.app
        for path in list(self.folder.glob('material-quick-*.json'))[:20]:
            token=path.stem[len('material-quick-'):]
            if len(token)!=32 or any(c not in '0123456789abcdef' for c in token):continue
            if token in self.inflight:continue
            try:
                item=read(path,{})
                if item.get('nonce')!=self.nonce:continue
                r=item.get('request',{})
                if r.get('id')!=token or r.get('method') not in ('defect','rotate'):
                    raise ValueError('메인 화면 소재 입력 형식이 올바르지 않습니다.')
                args=r.get('args')
                if not isinstance(args,list) or not args or type(args[0]) is not int or not 1<=args[0]<=9:
                    raise ValueError('입력 호기가 올바르지 않습니다.')
                if (r['method']=='defect' and len(args)!=1) or (r['method']=='rotate' and (len(args)!=2 or args[1] is not False)):
                    raise ValueError('메인 화면 소재 입력 항목이 올바르지 않습니다.')
                if app.resetting or app._shutdown_started or not app.connected:continue
                app.session.submit_request(item.get('owner'),r)
                self.inflight.add(token)
            except (ValueError,TypeError,KeyError) as exc:self.finish(token,dict(ok=False,error=str(exc)))
    def status(self):
        app=self.app;session=app.session;state=app.store.state
        connected=bool(app.connected and not app.failed_storage and not app.resetting and not app._shutdown_started
                       and state and time.monotonic()-session.received_at<=6)
        rows=[];busy=session.busy_machines()
        for n in range(1,10):
            row=app.store.snapshot(n);actions=app.action_availability(n,row)
            rows.append(dict(machine=n,good=row['good'],defects=row['defects'],material_type=row['material_type'],
                next_type=row['next_type'],expected=row['expected'],busy=n in busy,
                can_defect=connected and n not in busy and actions['defect'],
                can_rotate=connected and n not in busy and bool(row['material_type'])
                    and actions['rotate']))
        return dict(connected=connected,rows=rows,client=session.coordinator.settings['pc_id'],
                    owner=(session.coordinator.owner or {}).get('owner_id'),epoch=state['epoch'] if state else '',
                    at=state['at'] if state else 0)

class QuickPanel:
    def __init__(self,app,parent):
        self.app=app;self.channel=None;self.message_until=0;self.signature=None;self.rows={};self.confirming=False
        tk,ttk=app.tk,app.ttk
        self.frame=ttk.Frame(parent,style='RoundedCard.TFrame',padding=(14,10))
        title=ttk.Frame(self.frame,style='Card.TFrame',borderwidth=0);title.grid(row=0,column=0,columnspan=9,sticky='ew',pady=(0,6))
        ttk.Label(title,text='소재 사용량 조사',style='Section.TLabel').pack(side='left')
        self.message=tk.StringVar(value='')
        self.caption=ttk.Label(title,textvariable=self.message,style='Card.TLabel',font=('맑은 고딕',9))
        self.caption.pack(side='right')
        for name in ('Danger','Secondary'):
            app.style.configure('QuickMaterial.'+name+'.TButton',padding=(4,7),font=('맑은 고딕',10,'bold'))
        for n in range(1,10):
            self.frame.columnconfigure(n-1,weight=1,uniform='material-quick')
            cell=ttk.Frame(self.frame,style='Card.TFrame',borderwidth=0);cell.grid(row=1,column=n-1,sticky='nsew',padx=3)
            cell.columnconfigure(0,weight=1)
            name=ttk.Label(cell,text=str(n)+'호기',style='Card.TLabel',font=('맑은 고딕',10,'bold'),anchor='center');name.grid(row=0,column=0,sticky='ew',pady=(0,6))
            defect=ttk.Button(cell,text='불량',style='QuickMaterial.Danger.TButton',width=8,
                command=lambda machine=n:self.submit('defect',machine));defect.grid(row=1,column=0,sticky='ew',pady=(0,6))
            rotate=ttk.Button(cell,text='소재교체',style='QuickMaterial.Secondary.TButton',width=8,
                command=lambda machine=n:self.submit('rotate',machine));rotate.grid(row=2,column=0,sticky='ew')
            defect.configure(state='disabled');rotate.configure(state='disabled')
            self.rows[n]=dict(cell=cell,name=name,defect=defect,rotate=rotate)
    def connect(self,manager):
        folder=Path(os.environ.get('LOCALAPPDATA') or str(Path.home()/'.local'/'share'))/'MaterialCounter'
        try:self.channel=QuickChannel(manager,folder/'quick-inputs.json')
        except (OSError,ValueError) as exc:self.notice(str(exc),True)
    def notice(self,message,error=False):
        self.message.set(str(message)[:90]);self.message_until=time.monotonic()+6
        self.caption.configure(foreground='#f08c9a' if error else '#91d8b3')
    def submit(self,method,n):
        if self.channel is None or self.confirming:return
        try:
            confirmed=None
            if method=='rotate':
                from tkinter import messagebox
                self.poll();confirmed=self.channel.rotation_context(n)
                self.confirming=True
                try:
                    accepted=messagebox.askokcancel('소재교체 확인',
                        '{}호기 소재를 교체할까요?\n현재 봉의 기록을 마감하고 새 소재 재고 1봉을 차감합니다.'.format(n),
                        parent=self.app.root,default='cancel')
                finally:self.confirming=False
                if not accepted:return
                self.poll()
            self.channel.submit(method,n,confirmed=confirmed);self.notice('{}호기 저장 확인 중…'.format(n));self.poll()
        except (OSError,ValueError,KeyError,StopIteration) as exc:self.notice(str(exc),True)
    def poll(self):
        if self.channel is None:return
        try:state,results=self.channel.poll()
        except (OSError,ValueError,KeyError) as exc:state={};results=[];self.notice(str(exc),True)
        for item in results:
            r=item['result'];label='양품 −1 / 불량 +1' if item['method']=='defect' else '소재교체'
            self.notice('{}호기 {} 저장 완료'.format(item['machine'],label) if r.get('ok') else '{}호기: {}'.format(item['machine'],r.get('error','저장 실패')),not r.get('ok'))
        pending={v['request']['args'][0] for v in self.channel.pending.values()}
        available=bool(state.get('connected'))
        mapping={r['machine']:r for r in state.get('rows',[])}
        signature=(available,repr(mapping),tuple(sorted(pending)))
        if signature!=self.signature:
            self.signature=signature
            for n,widgets in self.rows.items():
                row=mapping.get(n,{});busy=n in pending or row.get('busy',False)
                for action in ('defect','rotate'):
                    widgets[action].configure(state='normal' if available and not busy and row.get('can_'+action,False) else 'disabled')
        if time.monotonic()>self.message_until:
            text='저장 확인 대기 {}건'.format(len(pending)) if pending else ''
            self.message.set(text);self.caption.configure(foreground='#91a5bf')
    def has_pending(self):return bool(self.channel and self.channel.pending)
