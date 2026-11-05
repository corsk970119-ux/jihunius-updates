"""Asynchronous material clients; shared configuration contains no production data."""
import base64
import hashlib
import os
from pathlib import Path
import queue
import socket
import sqlite3
import tempfile
import threading
import time
import uuid
import material_counter as core
from material_sync import Authority,CommandStore,Discovery,Outbox,RPCClient,atomic_json,read_json

DEFAULT_SHARE = r'\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈\지후니우스_인수인계\소재재고조사'

def lan_address():
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        sock.connect((core.HOST,80));return sock.getsockname()[0]
    except OSError:return socket.gethostname()
    finally:sock.close()

class Coordinator:
    def __init__(self,folder,shared,collector_factory=core.Collector):
        self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True)
        self.settings_path=self.folder/'sync-settings.json'
        self.settings=read_json(self.settings_path)
        if self.settings is None:
            self.settings=dict(pc_id=uuid.uuid4().hex,enabled=False,owner=None)
            atomic_json(self.settings_path,self.settings)
        if (not isinstance(self.settings,dict) or type(self.settings.get('enabled')) is not bool
                or not isinstance(self.settings.get('pc_id'),str) or len(self.settings['pc_id'])!=32):
            raise ValueError('이 PC의 소재 수집 설정이 손상되었습니다. 기존 파일을 보존하고 확인해주세요.')
        self.discovery=Discovery(shared);self.factory=collector_factory
        self.owner=None;self.client=None;self.authority=None;self.warning=''
    @property
    def is_owner(self):return bool(self.owner and self.owner['owner_id']==self.settings['pc_id'])
    def save(self):atomic_json(self.settings_path,self.settings)
    def _activate(self,owner):
        self.owner=owner
        if self.is_owner:
            if self.authority is None:
                self.authority=Authority(self.folder/'counter.sqlite3',owner['token'],owner['owner_name'],self.factory)
                try:self.authority.start()
                except Exception:self.authority=None;raise
            self.authority.set_collection(self.settings['enabled'])
            endpoint=dict(owner,host=lan_address(),port=self.authority.port)
            self.client=RPCClient('127.0.0.1',self.authority.port,owner['token'])
            try:self.owner=self.discovery.exchange('publish',endpoint)
            except (ConnectionError,OSError,ValueError) as exc:self.warning=str(exc)
        else:
            if self.authority is not None:
                self.authority.close();self.authority=None
            if self.settings['enabled']:
                self.settings['enabled']=False
            if not owner['port']:raise ConnectionError('수집 PC가 연결을 준비 중입니다.')
            self.client=RPCClient(owner['host'],owner['port'],owner['token'])
        self.settings['owner']=self.owner;self.save()
    def connect(self):
        self.warning=''
        try:owner=self.discovery.exchange('read')
        except (ConnectionError,OSError,ValueError) as exc:
            owner=self.settings.get('owner');self.warning=str(exc)
            if owner is None:raise
        if owner is None:
            self.client=None;self.owner=None
            return
        self._activate(owner)
    def toggle(self,enabled):
        if type(enabled) is not bool:raise ValueError('수집 설정이 올바르지 않습니다.')
        if enabled:
            owner=self.discovery.exchange('read')
            if owner and owner['owner_id']!=self.settings['pc_id']:
                raise ValueError('수집 담당 PC는 '+owner['owner_name']+'입니다. 이 PC는 OFF로 사용하며 입력만 동기화합니다.')
            if owner is None:
                cached=self.settings.get('owner')
                if cached is not None:raise ValueError('공유 연결 설정 원본이 없습니다. 기존 수집 담당 PC 설정을 확인해주세요.')
                owner=dict(owner_id=self.settings['pc_id'],owner_name=socket.gethostname(),
                    token=uuid.uuid4().hex+uuid.uuid4().hex,host=lan_address(),port=0)
                owner=self.discovery.exchange('claim',owner)
            self._activate(owner)
            self.authority.set_collection(True)
        elif self.authority is not None:self.authority.set_collection(False)
        self.settings['enabled']=enabled;self.save()
    def close(self):
        if self.authority is not None:self.authority.close();self.authority=None

class ClientSession:
    def __init__(self,folder,shared,collector_factory=core.Collector):
        self.coordinator=Coordinator(folder,shared,collector_factory)
        self.outbox=Outbox(Path(folder)/'pending-inputs.json')
        self.tasks=queue.Queue(8);self.events=queue.Queue();self.stop=threading.Event()
        self.state=None;self.received_at=0;self.visible=True;self.quick_active=False;self.failure='';self.closed=False
        self.thread=threading.Thread(target=self._run,name='material-sync',daemon=True)
        self.thread.start()
    def toggle(self,enabled):self.tasks.put_nowait(('toggle',enabled))
    def command(self,method,args,expected):
        state=self.state
        if not state or time.monotonic()-self.received_at>6 or self.coordinator.client is None:
            raise ValueError('수집 PC의 최신 자료를 받은 뒤 입력해주세요.')
        r=dict(id=uuid.uuid4().hex,client=self.coordinator.settings['pc_id'],epoch=state['epoch'],
               method=method,args=args,expected=expected,expires=state['at']+30)
        return self.submit_request(self.coordinator.owner['owner_id'],r)
    def submit_request(self,owner,request):
        CommandStore.validate_command(request)
        if request['client']!=self.coordinator.settings['pc_id']:raise ValueError('입력 PC가 일치하지 않습니다.')
        if not self.coordinator.owner or owner!=self.coordinator.owner['owner_id']:
            raise ValueError('수집 담당 PC가 변경되었습니다. 기존 입력의 저장 결과를 확인해주세요.')
        self.outbox.add(owner,request)
        return request['id']
    def busy_machines(self):
        return {x['request']['args'][0] for x in self.outbox.items()
                if x['request']['method'] in ('defect','rotate','switch_14','undo','assign_material','set_next_type')}
    def view(self):
        client=self.coordinator.client
        if client is None:raise ConnectionError('수집 PC에 연결되지 않았습니다.')
        return RemoteView(client,self.coordinator.folder/'counter.sqlite3')
    def _run(self):
        next_discovery=0;next_poll=0;next_send=0
        try:
            while not self.stop.is_set():
                now=time.monotonic()
                try:
                    action,value=self.tasks.get_nowait()
                    if action=='toggle':
                        try:
                            self.coordinator.toggle(value)
                            self.events.put(('toggle',True,''))
                            next_poll=0
                        except Exception as exc:self.events.put(('toggle',False,str(exc)))
                except queue.Empty:pass
                if now>=next_discovery:
                    try:self.coordinator.connect()
                    except Exception as exc:self.events.put(('connection',False,str(exc)))
                    next_discovery=time.monotonic()+15
                client=self.coordinator.client
                if client is not None and now>=next_send:
                    for item in self.outbox.items():
                        r=item['request']
                        if item['owner']!=self.coordinator.owner['owner_id']:
                            self.events.put(('connection',False,'미확인 입력의 수집 PC와 현재 연결 대상이 다릅니다. 기존 연결 설정을 확인해주세요.'))
                            break
                        try:
                            result=client.call('command',r)
                            self.outbox.remove(r['id'])
                            self.events.put(('command',r['id'],result));next_poll=0
                        except Exception as exc:
                            self.events.put(('connection',False,'저장 확인 대기 · '+str(exc)[:140]))
                            next_discovery=min(next_discovery,time.monotonic()+2);break
                    next_send=time.monotonic()+1
                if client is not None and now>=next_poll:
                    try:
                        state=client.call('state');self.state=state;self.received_at=time.monotonic()
                        self.events.put(('state',state))
                    except Exception as exc:
                        self.events.put(('connection',False,str(exc)))
                        next_discovery=min(next_discovery,time.monotonic()+3)
                    next_poll=time.monotonic()+(1 if self.visible or self.quick_active or self.outbox.items() else 5)
                self.stop.wait(.08)
        except Exception as exc:
            self.failure=str(exc);self.events.put(('connection',False,'동기화 중단: '+self.failure))
        finally:
            try:self.coordinator.close()
            except Exception as exc:self.failure=str(exc)
            self.closed=True
    def close(self):self.stop.set()

class RemoteView(core.Store):
    def __init__(self,client,path):
        self.client=client;self.path=Path(path);self.db=BackupView(client,self.path.parent)
    def history(self,machine=None,limit=500):return self.client.call('read',dict(name='history',args=[machine,limit]))
    def events(self,machine=None,limit=300):return self.client.call('read',dict(name='events',args=[machine,limit]))
    def movements(self,limit=200):return self.client.call('read',dict(name='movements',args=[limit]))
    def period_report(self,start,end,machine=None):return self.client.call('read',dict(name='period_report',args=[start,end,machine]))
    def snapshot(self,n):return next(r for r in self.client.call('state')['rows'] if r['machine']==n)
    def inventory(self):return self.client.call('state')['inventory']

class BackupView:
    def __init__(self,client,folder):self.client=client;self.folder=folder
    def backup(self,target):
        payload=self.client.call('backup');data=base64.b64decode(payload['data'],validate=True)
        if hashlib.sha256(data).hexdigest()!=payload['sha256']:raise ValueError('백업 파일 검증에 실패했습니다.')
        fd,name=tempfile.mkstemp(suffix='.sqlite3',dir=str(self.folder));os.close(fd)
        try:
            Path(name).write_bytes(data);source=sqlite3.connect(name)
            try:source.backup(target)
            finally:source.close()
        finally:os.unlink(name)

class ReportJobs:
    def __init__(self,session):
        self.session=session;self.tasks=queue.Queue(8);self.results=queue.Queue();self.stopped=threading.Event()
        self.thread=threading.Thread(target=self._run,name='material-reports',daemon=True);self.thread.start()
    def submit(self,token,work,writable=False):self.tasks.put_nowait((token,work))
    def close(self):self.stopped.set()
    def _run(self):
        while not self.stopped.is_set():
            try:token,work=self.tasks.get(timeout=.1)
            except queue.Empty:continue
            try:self.results.put((token,work(self.session.view()),None))
            except Exception as exc:self.results.put((token,None,exc))

class CachedStore(core.Store):
    def __init__(self,path):
        self.path=Path(path);self.live=set();self.state=None
        self.histories={};self.event_lists={};self.movement_list=[]
        self.rows={n:dict(machine=n,program='',state='',part_count='',last_seen=None,active_material=None,
            initial_type=None,next_type=None,auto=0,defects=0,total=0,partial=False,gap=False,started=None,
            material_type=None,good=0,defect_excess=0,undo_label='',expected={},parked=None) for n in core.MACHINES}
    def update(self,state):self.state=state;self.rows={r['machine']:r for r in state['rows']};self.live=set(state['live'])
    def snapshot(self,n):return self.rows[n]
    def inventory(self):
        return self.state['inventory'] if self.state else [dict(type_id=k,label=v,quantity=None,registered=False) for k,v in core.MATERIAL_TYPES.items()]
    def undo_label(self,n):return self.rows[n]['undo_label']
    def history(self,machine=None,limit=500):return self.histories.get(machine,[])
    def events(self,machine=None,limit=300):return self.event_lists.get(machine,[])
    def movements(self,limit=200):return self.movement_list
    def close(self):pass
