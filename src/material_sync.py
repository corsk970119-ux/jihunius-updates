"""Single-writer material service; portable Python 3.8+, standard library only."""
import base64
import hashlib
import hmac
import inspect
import json
import os
from pathlib import Path
import queue
import socket
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import material_counter as core

class CommandStore(core.Store):
    WRITES = {'defect','rotate','switch_14','undo','assign_material','set_next_type',
              'register_stock','receive_stock','adjust_stock','reset_records'}
    def __init__(self, path):
        super().__init__(path)
        with self.transaction():
            self.db.execute('CREATE TABLE IF NOT EXISTS sync_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
            self.db.execute('INSERT OR IGNORE INTO sync_meta VALUES(?,?)',('epoch',uuid.uuid4().hex))
            self.db.execute('''CREATE TABLE IF NOT EXISTS sync_receipts(
                id TEXT PRIMARY KEY, digest TEXT NOT NULL, at REAL NOT NULL,
                client TEXT NOT NULL, method TEXT NOT NULL, result TEXT NOT NULL)''')
    def revision(self):
        return [self.epoch(),self.db.execute('SELECT MAX(id) FROM events').fetchone()[0],
                self.db.execute('SELECT MAX(id) FROM stock_movements').fetchone()[0]]
    def epoch(self):
        return self.db.execute("SELECT value FROM sync_meta WHERE key='epoch'").fetchone()[0]
    def expectations(self, n):
        r=self.snapshot(n)
        action=self.db.execute("SELECT id FROM events WHERE machine=? AND kind IN ('rotate','rotate_early','defect','switch14','return_original') AND undone=0 ORDER BY id DESC LIMIT 1",(n,)).fetchone()
        return dict(material=r['active_material'],next_type=r['next_type'],
                    material_type=r['material_type'],undo=action[0] if action else None,switch_revision=self.switch_revision(n))
    def stock_expectations(self, kind):
        return dict(stock=self.db.execute('SELECT MAX(id) FROM stock_movements WHERE type_id=?',(kind,)).fetchone()[0])
    def reset_records(self, reset_stock=False, at=None):
        if type(reset_stock) is not bool:raise ValueError('재고 초기화 여부가 올바르지 않습니다.')
        if self.db.in_transaction:raise RuntimeError('저장 중인 작업이 끝난 뒤 기록을 초기화해주세요.')
        self._reset_data(reset_stock,self._at(at));self.live.clear()
    def _reset_data(self, reset_stock, at):
        with self.transaction():
            super()._reset_data(reset_stock,at)
            if reset_stock:
                # Old requests carry the old epoch and cannot replay writes.
                # apply() records this reset's receipt in the same transaction.
                self.db.execute('DELETE FROM sync_receipts')
            self.db.execute("UPDATE sync_meta SET value=? WHERE key='epoch'",(uuid.uuid4().hex,))
    def previous(self, request):
        digest=hashlib.sha256(json.dumps(request,sort_keys=True,ensure_ascii=False,allow_nan=False).encode('utf8')).hexdigest()
        found=self.db.execute('SELECT digest,result FROM sync_receipts WHERE id=?',(request['id'],)).fetchone()
        if found:
            if not hmac.compare_digest(found['digest'],digest):
                raise ValueError('같은 요청 번호에 다른 내용이 전달되었습니다.')
            return digest,json.loads(found['result'])
        return digest,None
    @staticmethod
    def validate_command(r):
        if not isinstance(r,dict) or set(r)!={'id','client','epoch','method','args','expected','expires'}:
            raise ValueError('입력 요청 형식이 올바르지 않습니다.')
        if not isinstance(r['id'],str) or len(r['id'])!=32 or any(c not in '0123456789abcdef' for c in r['id']):
            raise ValueError('입력 요청 번호가 올바르지 않습니다.')
        if not isinstance(r['client'],str) or not 1<=len(r['client'])<=100:
            raise ValueError('입력 PC 정보가 올바르지 않습니다.')
        if not isinstance(r['expected'],dict) or not isinstance(r['args'],list):
            raise ValueError('입력 요청 값이 올바르지 않습니다.')
        if type(r['expires']) not in (float,int) or not 0<r['expires']<float('inf'):
            raise ValueError('입력 요청 시각이 올바르지 않습니다.')
    def check(self,r):
        if r['epoch']!=self.epoch():raise ValueError('기록이 초기화되었습니다. 최신 자료를 확인한 뒤 다시 입력해주세요.')
        if time.time()>r['expires']:raise ValueError('요청 유효 시간이 지났습니다. 반영되지 않았으니 최신 상태를 확인한 뒤 다시 입력해주세요.')
        name,args,expected=r['method'],r['args'],r['expected']
        if name not in self.WRITES:raise ValueError('허용되지 않은 입력입니다.')
        lengths={'defect':1,'rotate':2,'switch_14':1,'undo':1,'assign_material':2,'set_next_type':2,
                 'register_stock':2,'receive_stock':2,'adjust_stock':3,'reset_records':1}
        if name=='rotate' and len(args)==1:args=args+[False]
        if len(args)!=lengths[name]:raise ValueError('입력 항목 수가 올바르지 않습니다.')
        if name in ('defect','rotate','switch_14','undo','assign_material','set_next_type'):
            now=self.expectations(args[0])
            keys=['material']
            if name in ('rotate','switch_14','set_next_type'):keys+=['next_type','material_type']
            if name=='assign_material':keys+=['material_type']
            if name=='undo':keys+=['undo']
            if any(k not in expected or now[k]!=expected[k] for k in keys):
                raise ValueError('다른 PC에서 소재 또는 입력 기록이 변경되었습니다. 최신 내용을 확인한 뒤 다시 입력해주세요.')
            if now['switch_revision']!=expected.get('switch_revision'):
                raise ValueError('소재 전환 기록이 변경되었습니다. 최신 내용을 확인한 뒤 다시 입력해주세요.')
        elif name=='reset_records':
            if type(args[0]) is not bool:raise ValueError('초기화 범위가 올바르지 않습니다.')
            if expected.get('revision')!=self.revision():raise ValueError('다른 PC 또는 수집으로 기록이 변경되었습니다. 최신 내용을 확인한 뒤 다시 삭제해주세요.')
        elif name=='adjust_stock':
            if 'stock' not in expected or expected['stock']!=self.stock_expectations(args[0])['stock']:
                raise ValueError('입력 중 재고가 변경되었습니다. 최신 수량을 확인한 뒤 다시 수정해주세요.')
        return name,args
    def reject(self,r,message):
        self.validate_command(r)
        with self.transaction():
            digest,old=self.previous(r)
            if old is not None:return old
            result=dict(ok=False,error=str(message))
            self.db.execute('INSERT INTO sync_receipts VALUES(?,?,?,?,?,?)',
                (r['id'],digest,time.time(),r['client'],r['method'],json.dumps(result,ensure_ascii=False)))
            return result
    def apply(self,r):
        self.validate_command(r)
        with self.transaction():
            digest,old=self.previous(r)
            if old is not None:return old
            try:
                name,args=self.check(r)
                with self.transaction():
                    if name=='reset_records':
                        self._reset_data(args[0],time.time());self.live.clear();value=None
                    else:value=self.rotate(args[0],early=args[1]) if name=='rotate' else getattr(self,name)(*args)
                result=dict(ok=True,value=value)
            except ValueError as exc:
                result=dict(ok=False,error=str(exc))
            self.db.execute('INSERT INTO sync_receipts VALUES(?,?,?,?,?,?)',
                (r['id'],digest,time.time(),r['client'],r['method'],json.dumps(result,ensure_ascii=False)))
            return result

class RPCClient:
    def __init__(self, host, port, token, timeout=8):
        self.host,self.port,self.token,self.timeout=host,int(port),token,timeout
    def call(self,method,args=None):
        conn=HTTPConnection(self.host,self.port,timeout=self.timeout)
        try:
            data=json.dumps(dict(method=method,args=args),ensure_ascii=False,allow_nan=False).encode('utf8')
            conn.request('POST','/rpc',data,{'Content-Type':'application/json','Authorization':'Bearer '+self.token})
            response=conn.getresponse()
            if response.status==403:raise PermissionError('수집 PC 연결 인증이 맞지 않습니다. 공유 연결 설정을 확인해주세요.')
            if response.status!=200:raise ConnectionError('수집 PC 응답 오류 ({})'.format(response.status))
            size=int(response.getheader('Content-Length','0'))
            if size<1 or size>128*1024*1024:raise ValueError('수집 PC 응답 크기가 올바르지 않습니다.')
            result=json.loads(response.read(size).decode('utf8'))
            if not result.get('ok'):
                error=ConnectionError if result.get('retryable') else ValueError
                raise error(result.get('error','수집 PC 요청 처리 실패'))
            return result['value']
        finally:conn.close()

class Authority:
    """Collector and writes are serialized on one owner thread; reports use read snapshots."""
    def __init__(self,path,token,owner,collector_factory=core.Collector,bind='0.0.0.0'):
        self.path=Path(path);self.token=token;self.owner=owner
        self.factory=collector_factory;self.bind=bind
        self.commands=queue.Queue(64);self.samples=queue.Queue()
        self.stopping=threading.Event();self.ready=threading.Event()
        self.error=None;self.failure='';self.collection=False;self.collector=None
        self.pending={};self.sources={};self.server_detail='데이터 수집 OFF';self.errors={}
        self.server=None;self.lock=None;self.thread=None
        self.read_slots=threading.BoundedSemaphore(2);self.read_timeout=6.0
    def start(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.lock=core.InstanceLock(self.path.parent/'instance.lock')
        self.thread=threading.Thread(target=self._run,name='material-writer',daemon=True);self.thread.start()
        if not self.ready.wait(10):self.close();raise RuntimeError('소재 저장소 준비 시간이 초과되었습니다.')
        if self.error is not None:self.close();raise self.error
        authority=self
        class Server(ThreadingHTTPServer):
            daemon_threads=True
            allow_reuse_address=True
            slots=threading.BoundedSemaphore(8)
            def process_request(self,request,address):
                if not self.slots.acquire(blocking=False):
                    self.shutdown_request(request);return
                try:super().process_request(request,address)
                except Exception:self.slots.release();raise
            def process_request_thread(self,request,address):
                try:super().process_request_thread(request,address)
                finally:self.slots.release()
        class Handler(BaseHTTPRequestHandler):
            def setup(self):
                self.request.settimeout(10);super().setup()
            def log_message(self,*args):pass
            def do_POST(self):
                if self.path!='/rpc':self.send_error(404);return
                supplied=self.headers.get('Authorization','')
                if not hmac.compare_digest(supplied,'Bearer '+authority.token):self.send_error(403);return
                try:
                    length=int(self.headers.get('Content-Length','0'))
                    if not 1<=length<=65536:raise ValueError('요청이 너무 크거나 비어 있습니다.')
                    body=json.loads(self.rfile.read(length).decode('utf8'))
                    if body.get('method') not in ('state','command','read','backup'):
                        raise ValueError('허용되지 않은 요청입니다.')
                    value=authority.request(body['method'],body.get('args'))
                    result=dict(ok=True,value=value)
                except (ValueError,RuntimeError,KeyError,TypeError,queue.Full,TimeoutError) as exc:
                    result=dict(ok=False,error=str(exc),retryable=isinstance(exc,(RuntimeError,queue.Full,TimeoutError)))
                except Exception:
                    result=dict(ok=False,error='저장 또는 조회 오류입니다. 수집 PC 상태를 확인해주세요.',retryable=True)
                data=json.dumps(result,ensure_ascii=False,allow_nan=False).encode('utf8')
                try:
                    self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8')
                    self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
                except (OSError,TimeoutError):pass  # durable receipt handles lost acknowledgement
        try:
            self.server=Server((self.bind,0),Handler);self.port=self.server.server_address[1]
            self.http_thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.http_thread.start()
        except Exception:self.close();raise
        return self
    def close(self):
        self.stopping.set()
        if self.server is not None:
            self.server.shutdown();self.server.server_close();self.server=None
        if self.thread is not None and self.thread.is_alive():self.thread.join(10)
        if self.thread is not None and self.thread.is_alive():
            raise RuntimeError('소재 데이터 저장 종료를 기다리고 있습니다.')
        if self.lock is not None:self.lock.close();self.lock=None
    def set_collection(self,enabled):return self.request('_collection',bool(enabled))
    def request(self,method,args=None):
        if self.stopping.is_set():raise RuntimeError('수집 PC가 종료 중입니다. 저장 결과는 재연결 후 확인합니다.')
        if method in ('read','backup'):return self.read_request(method,args)
        if method not in ('state','command','_collection'):raise ValueError('허용되지 않은 요청입니다.')
        answer=queue.Queue(1);self.commands.put_nowait((method,args,answer))
        try:ok,value=answer.get(timeout=7)
        except queue.Empty:raise RuntimeError('저장 결과 확인 대기 중입니다. 같은 요청 번호로 재확인합니다.')
        if not ok:raise value
        return value
    def read_request(self,method,args):
        if not self.read_slots.acquire(blocking=False):
            raise RuntimeError('다른 통계·백업을 처리 중입니다. 잠시 뒤 다시 조회해주세요.')
        try:return self._read_request(method,args,time.monotonic()+self.read_timeout)
        finally:self.read_slots.release()
    def _read_request(self,method,args,deadline):
        def budget(*unused):
            if time.monotonic()>=deadline:raise TimeoutError('조회 시간이 길어 중단했습니다. 기간을 줄이거나 잠시 뒤 다시 시도해주세요.')
        budget()
        db=sqlite3.connect(self.path.resolve().as_uri()+'?mode=ro',uri=True,timeout=3)
        db.row_factory=sqlite3.Row
        db.set_progress_handler(lambda:int(time.monotonic()>=deadline),1000)
        view=core.Store.__new__(core.Store);view.path=self.path;view.db=db;view.live=set()
        try:
            if method=='backup':
                import tempfile
                fd,name=tempfile.mkstemp(suffix='.sqlite3',dir=str(self.path.parent));os.close(fd)
                try:
                    target=sqlite3.connect(name)
                    try:db.backup(target,pages=256,progress=budget)
                    finally:target.close()
                    data=Path(name).read_bytes()
                    return dict(data=base64.b64encode(data).decode('ascii'),sha256=hashlib.sha256(data).hexdigest())
                finally:os.unlink(name)
            if not isinstance(args,dict) or args.get('name') not in ('period_report','history','events','movements'):
                raise ValueError('허용되지 않은 조회입니다.')
            params=args.get('args',[]);kwargs=args.get('kwargs',{})
            if not isinstance(params,list) or not isinstance(kwargs,dict):raise ValueError('조회 조건이 올바르지 않습니다.')
            signature=inspect.signature(getattr(core.Store,args['name']))
            signature.bind(view,*params,**kwargs)
            if args['name']=='period_report':
                if len(params)<2 or any(type(n) not in (int,float) or not -float('inf')<n<float('inf') for n in params[:2]):
                    raise ValueError('조회 기간이 올바르지 않습니다.')
            db.execute('BEGIN')
            value=getattr(view,args['name'])(*params,**kwargs)
            if args['name']=='period_report':
                value['_sync_revision']=[db.execute("SELECT value FROM sync_meta WHERE key='epoch'").fetchone()[0],
                    db.execute('SELECT MAX(id) FROM events').fetchone()[0],db.execute('SELECT MAX(id) FROM stock_movements').fetchone()[0]]
                value['_queried_at']=time.time()
            budget()
            return value
        except sqlite3.OperationalError:
            budget();raise
        finally:db.close()
    def _switch(self,enabled):
        if enabled==self.collection:return
        if enabled:
            if self.failure:raise RuntimeError(self.failure)
            self.samples=queue.Queue();self.sources={}
            self.collector=self.factory(self.samples);self.collector.start()
            self.collection=True;self.server_detail='머신 상태를 확인하는 중입니다.'
        else:
            if self.collector:self.collector.close()
            self._drain(complete=True)
            for n in list(self.store.live):self.store.disconnected(n,reason='데이터 수집 OFF')
            self.collection=False;self.server_detail='데이터 수집 OFF'
            for key in list(self.pending):self._finish_rotation(key,'데이터 수집이 중단되었습니다. 교체를 반영하지 않았습니다.')
    def state(self):
        rows=[]
        for n in core.MACHINES:
            row=self.store.snapshot(n);row['expected']=self.store.expectations(n)
            row['undo_label']=self.store.undo_label(n);rows.append(row)
        revision=self.store.revision()
        return dict(rows=rows,inventory=self.store.inventory(),live=sorted(self.store.live),
                    stock_revisions={k:self.store.stock_expectations(k) for k in core.MATERIAL_TYPES},
                    collection=self.collection,owner=self.owner,epoch=self.store.epoch(),
                    revision=revision,detail=self.server_detail,failure=self.failure,errors=self.errors,at=time.time(),
                    capabilities=['temporary14'])
    def _run(self):
        try:self.store=CommandStore(self.path)
        except Exception as exc:self.error=exc;self.ready.set();return
        self.ready.set()
        try:
            while not self.stopping.is_set():
                try:self._drain()
                except Exception as exc:self._storage_failure(exc)
                for key,entry in list(self.pending.items()):
                    if time.monotonic()-entry['started']>6:self._finish_rotation(key,'최신 머신 상태를 확인하지 못해 소재교체를 반영하지 않았습니다.')
                try:method,args,answer=self.commands.get(timeout=.03)
                except queue.Empty:continue
                try:
                    if method=='state':result=self.state()
                    elif method=='_collection':self._switch(args);result=None
                    elif self.failure:raise RuntimeError(self.failure)
                    elif args.get('method') in ('rotate','switch_14'):
                        self.store.validate_command(args)
                        old=self.store.previous(args)[1]
                        if old is not None:result=old
                        else:
                            self.store.check(args)
                            if not self.collection:raise ValueError('수집 PC의 데이터 수집을 ON으로 켠 뒤 소재교체를 눌러주세요.')
                            key=args['id']
                            if key in self.pending:
                                if self.pending[key]['request']!=args:raise ValueError('중복 요청 내용이 다릅니다.')
                                self.pending[key]['answers'].append(answer);continue
                            self.pending[key]=dict(request=args,answers=[answer],started=time.monotonic())
                            try:self.collector.checkpoint(args['args'][0],key)
                            except Exception as exc:self._finish_rotation(key,str(exc))
                            continue
                    elif args.get('method')=='reset_records':
                        if self.pending:raise ValueError('소재교체 결과를 확인한 뒤 기록을 삭제해주세요.')
                        resume=self.collection
                        if self.collector:self.collector.close()
                        self.collection=False
                        try:
                            self._drain(complete=True)
                            result=self.store.apply(args)
                        finally:
                            for n in list(self.store.live):self.store.disconnected(n,reason='기록 초기화 확인 중 수집 중단')
                            if resume:self._switch(True)
                    else:result=self.store.apply(args)
                    answer.put((True,result))
                except ValueError as exc:
                    try:
                        answer.put((True,self.store.reject(args,str(exc))) if method=='command' else (False,exc))
                    except Exception as failure:answer.put((False,failure))
                except Exception as exc:
                    if isinstance(exc,sqlite3.Error):self._storage_failure(exc)
                    answer.put((False,exc))
        finally:
            if self.collector:self.collector.close()
            if not self.failure:
                try:
                    self._drain(complete=True)
                    for n in list(self.store.live):self.store.disconnected(n,reason='프로그램 종료')
                except Exception:pass
            for key in list(self.pending):self._finish_rotation(key,'프로그램이 종료되어 교체를 반영하지 않았습니다.')
            self.store.close()
    def _storage_failure(self,exc):
        self.failure='소재 저장 오류: '+str(exc)[:160]
        if self.collector:self.collector.close()
        self.collection=False;self.store.live.clear()
        for key in list(self.pending):self._finish_rotation(key,self.failure)
    def _drain(self,complete=False):
        processed=0
        while complete or processed<100:
            processed+=1
            try:event=self.samples.get_nowait()
            except queue.Empty:break
            if event[0]=='server':self.server_detail=event[2];continue
            kind,ip,generation,record,at,token,error=event
            old=self.sources.get(ip)
            if kind=='removed' and old and old[1]!=generation:continue
            machine=record['machine'] if record else (old[0] if old else None)
            if record and old and old[0]!=machine:self.store.disconnected(old[0],at,'머신 주소의 호기 번호 변경')
            if record:
                self.sources[ip]=(machine,generation);self.store.observe(record,at);self.errors.pop(machine,None)
            elif machine:
                self.store.disconnected(machine,at,error or '연결 중단');self.errors[machine]=error
            if token and token in self.pending:
                expected=self.pending[token]['request']['args'][0]
                self._finish_rotation(token,None if record and machine==expected else (error or '호기 정보 불일치'))
        # A delayed batch is still a continuous series of observations. Never
        # insert a false gap before the remaining FIFO samples are consumed.
        if not self.samples.empty():return
        now=time.time()
        for n in list(self.store.live):
            seen=self.store._machine(n)['last_seen']
            if seen is None or not 0<=now-seen<=core.GAP_SECONDS:self.store.disconnected(n,now,'응답 지연')
    def _finish_rotation(self,key,error=None):
        entry=self.pending.pop(key,None)
        if not entry:return
        try:result=self.store.reject(entry['request'],error) if error else self.store.apply(entry['request'])
        except Exception as exc:
            for answer in entry['answers']:answer.put((False,exc))
            raise
        for answer in entry['answers']:answer.put((True,result))

def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with temporary.open('w',encoding='utf8') as out:
            json.dump(value,out,ensure_ascii=False,allow_nan=False);out.flush();os.fsync(out.fileno())
        os.replace(str(temporary),str(path))
    finally:
        try:temporary.unlink()
        except FileNotFoundError:pass

def read_json(path,default=None):
    try:return json.loads(Path(path).read_text(encoding='utf8'))
    except FileNotFoundError:return default

# Shared-folder calls run in a killable process: an unavailable SMB share cannot
# freeze Tk, strand an accumulating set of workers, or lock the local database.
_DISCOVERY_HELPER = r'''
import json,os,sys,uuid
from pathlib import Path
request=json.load(sys.stdin);folder=Path(request['folder']);mode=request['mode'];item=request.get('item')
def read():
 try:
  with (folder/'owner.json').open('rb') as f:data=f.read(8193)
  if len(data)>8192:raise ValueError('공유 연결 설정이 너무 큽니다.')
  value=json.loads(data)
  if not isinstance(value,dict) or set(value)!={'owner_id','owner_name','token','host','port'}:raise ValueError('공유 연결 설정이 손상되었습니다.')
  if not isinstance(value['owner_id'],str) or len(value['owner_id'])!=32 or not isinstance(value['token'],str) or len(value['token'])!=64:raise ValueError('공유 연결 인증 정보가 손상되었습니다.')
  if not isinstance(value['host'],str) or not 1<=len(value['host'])<=253 or type(value['port']) is not int or not 0<=value['port']<=65535:raise ValueError('공유 연결 주소가 손상되었습니다.')
  return value
 except FileNotFoundError:return None
try:
 if mode=='read':result=read()
 else:
  folder.mkdir(parents=True,exist_ok=True)
  with (folder/'owner.lock').open('a+b') as lock:
   lock.seek(0)
   if not lock.read(1):lock.write(b'0');lock.flush()
   lock.seek(0)
   if os.name=='nt':
    import msvcrt
    msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
   else:
    import fcntl
    fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
   old=read()
   if old and (old['owner_id']!=item['owner_id'] or old['token']!=item['token']):raise ValueError('수집 담당 PC는 '+old.get('owner_name','다른 PC')+'입니다. 이 PC는 OFF로 사용해주세요.')
   if mode=='publish' and old is None:raise ValueError('공유 연결 원본이 없습니다. 수집 설정을 다시 확인해주세요.')
   result=old if mode=='claim' and old else item
   tmp=folder/('.owner-'+uuid.uuid4().hex+'.tmp')
   try:
    with tmp.open('w',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False);f.flush();os.fsync(f.fileno())
    os.replace(str(tmp),str(folder/'owner.json'))
   finally:
    if tmp.exists():tmp.unlink()
 print(json.dumps({'ok':True,'value':result},ensure_ascii=True))
except Exception as e:print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=True))
'''

class Discovery:
    def __init__(self,folder):self.folder=Path(folder)
    def exchange(self,mode,item=None):
        import subprocess,sys
        if mode not in ('read','claim','publish'):raise ValueError('연결 설정 작업이 올바르지 않습니다.')
        exe=Path(sys.executable)
        if os.name=='nt' and exe.name.lower()=='pythonw.exe':exe=exe.with_name('python.exe')
        try:
            result=subprocess.run([str(exe),'-c',_DISCOVERY_HELPER],
                input=json.dumps(dict(folder=str(self.folder),mode=mode,item=item)),
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf8',timeout=5,
                creationflags=0x08000000 if os.name=='nt' else 0)
        except subprocess.TimeoutExpired:raise ConnectionError('공유 폴더 응답이 늦습니다. 연결 설정을 다시 확인하고 있습니다.')
        if result.returncode:raise ConnectionError('공유 연결 설정을 읽지 못했습니다.')
        answer=json.loads(result.stdout)
        if not answer.get('ok'):raise ValueError(answer.get('error','공유 연결 설정 실패'))
        return answer['value']

class Outbox:
    def __init__(self,path):
        self.path=Path(path);self.lock=threading.Lock()
        self.values=read_json(path,[])
        if not isinstance(self.values,list) or any(not isinstance(x,dict) or set(x)!= {'owner','request'} for x in self.values):
            raise ValueError('미확인 입력 기록을 읽지 못했습니다. 파일을 보존하고 관리자에게 확인해주세요.')
    def items(self):
        with self.lock:return list(self.values)
    def add(self,owner,request):
        with self.lock:
            for item in self.values:
                if item['request']['id']==request['id']:
                    if item['owner']!=owner or item['request']!=request:raise ValueError('같은 요청 번호에 다른 입력이 있습니다.')
                    return
            if len(self.values)>=20:raise ValueError('저장 확인 대기 중인 입력이 있습니다. 먼저 연결을 확인해주세요.')
            values=self.values+[dict(owner=owner,request=request)]
            atomic_json(self.path,values);self.values=values
    def remove(self,request_id):
        with self.lock:
            values=[x for x in self.values if x['request']['id']!=request_id]
            atomic_json(self.path,values);self.values=values
