"""Bounded, event-only diagnostics. Shared I/O runs in a disposable subprocess.

Business actions never wait for this module. Local SQLite is on LOCALAPPDATA,
never SMB. Shared generations make all-PC clear independent of clock skew.
"""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import queue
import socket
import sqlite3
import subprocess
import sys
import threading
import time
import traceback
import uuid

LIMIT = 100
AGE = 30 * 86400
# 100 records at their character limits, including 4-byte Unicode, fit here.
MAX_FILE = 16 * 1024 * 1024


def _read(path, default=None):
    try:
        with open(path, 'rb') as stream: raw = stream.read(MAX_FILE + 1)
    except FileNotFoundError:
        if default is not None: return default
        raise
    if len(raw) > MAX_FILE: raise ValueError('오류 기록 파일 크기 초과')
    return json.loads(raw.decode('utf-8'))


def _write(path, value):
    data = json.dumps(value, ensure_ascii=False).encode('utf-8')
    if len(data) > MAX_FILE: raise ValueError('오류 기록 파일 크기 초과')
    temporary = path.with_suffix('.tmp')
    with open(temporary, 'wb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    os.replace(str(temporary), str(path))


def recent(rows, now=None):
    cutoff = (time.time() if now is None else now) - AGE
    return sorted((r for r in rows if r['last'] >= cutoff),
                  key=lambda r: (r['last'], r['id']), reverse=True)[:LIMIT]


class LocalStore:
    def __init__(self, path, pc=None):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        self.pc = pc or socket.gethostname()
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS errors (id TEXT PRIMARY KEY, data TEXT NOT NULL)')
            for key, value in {'epoch':'0', 'pc_id':uuid.uuid4().hex, 'enabled':True,
                               'pending':None, 'cache':[], 'seen':0, 'revision':0}.items():
                db.execute('INSERT OR IGNORE INTO state VALUES (?,?)',(key,json.dumps(value)))

    @contextlib.contextmanager
    def connect(self):
        db=sqlite3.connect(str(self.path),timeout=2)
        try:
            with db:yield db
        finally:db.close()

    @staticmethod
    def get(db, key):
        return json.loads(db.execute('SELECT value FROM state WHERE key=?',(key,)).fetchone()[0])

    @staticmethod
    def put(db, key, value):
        db.execute('UPDATE state SET value=? WHERE key=?',(json.dumps(value,ensure_ascii=False),key))

    @staticmethod
    def rows(db):
        return [json.loads(r[0]) for r in db.execute('SELECT data FROM errors')]

    def revision(self):
        with self.connect() as db:return self.get(db,'revision')

    def changed(self,db):self.put(db,'revision',self.get(db,'revision')+1)

    def _prune(self, db):
        rows = recent(self.rows(db)); keep = {r['id'] for r in rows}
        for rid, in db.execute('SELECT id FROM errors').fetchall():
            if rid not in keep: db.execute('DELETE FROM errors WHERE id=?',(rid,))
        return rows

    def record(self, feature, message, stage='', detail='', version='', work='', now=None):
        now = time.time() if now is None else now
        fields = dict(feature=str(feature)[:80], message=str(message)[:8192],
                      stage=str(stage)[:300], detail=str(detail)[-16384:],
                      version=str(version)[:64], work=str(work)[:120])
        signature = hashlib.sha256(json.dumps([fields[k] for k in
            ('feature','stage','message','work')],ensure_ascii=False).encode()).hexdigest()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if not self.get(db,'enabled'): return
            rows = self._prune(db)
            row = next((r for r in rows if r['signature']==signature and 0<=now-r['last']<60),None)
            if row is None:
                row = dict(fields, id=uuid.uuid4().hex, epoch=self.get(db,'epoch'),
                           pc_id=self.get(db,'pc_id'),pc=self.pc,first=now,last=now,
                           count=1,signature=signature)
            else:
                row.update(last=now,count=min(1000000000,row['count']+1),detail=fields['detail'] or row['detail'])
            db.execute('INSERT OR REPLACE INTO errors VALUES (?,?)',
                       (row['id'],json.dumps(row,ensure_ascii=False)))
            self._prune(db)
            self.changed(db)

    def set_enabled(self, enabled):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE');self.put(db,'enabled',bool(enabled));self.changed(db)

    def mark_seen(self):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE');self.put(db,'seen',time.time());self.changed(db)

    def clear_all(self):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            pending=self.get(db,'pending')
            if pending: return  # An outstanding request is idempotent.
            token=uuid.uuid4().hex
            self.put(db,'pending',{'base':self.get(db,'epoch'),'token':token})
            self.put(db,'epoch',token);self.put(db,'cache',[])
            db.execute('DELETE FROM errors')
            self.changed(db)

    def request(self):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            return dict(epoch=self.get(db,'epoch'),pc_id=self.get(db,'pc_id'),pc=self.pc,
                        pending=self.get(db,'pending'),records=self._prune(db))

    def accept(self, request, result):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            # A clear initiated while SMB was busy supersedes its old response.
            if self.get(db,'epoch') != request['epoch']: return
            if result['epoch'] != request['epoch']:
                db.execute('DELETE FROM errors')
                self.put(db,'epoch',result['epoch'])
            self.put(db,'pending',None)
            self.put(db,'cache',recent(result['records']))
            self.changed(db)

    def view(self):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            own=self.get(db,'pc_id'); epoch=self.get(db,'epoch')
            rows=self._prune(db)
            rows += [r for r in self.get(db,'cache') if r['pc_id']!=own and r['epoch']==epoch]
            rows=recent(rows)
            seen=self.get(db,'seen')
            return dict(records=rows,enabled=self.get(db,'enabled'),pc_id=own,
                        pending_clear=bool(self.get(db,'pending')),
                        unread=sum(r['last']>seen for r in rows))


@contextlib.contextmanager
def shared_lock(folder):
    folder.mkdir(parents=True,exist_ok=True)
    with open(folder/'history.lock','a+b') as handle:
        handle.seek(0,2)
        if handle.tell()==0: handle.write(b'0');handle.flush()
        end=time.monotonic()+2
        while True:
            try:
                handle.seek(0)
                if os.name=='nt':
                    import msvcrt
                    msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
                else:
                    import fcntl
                    fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic()>=end: raise TimeoutError('오류 기록 공유 잠금 대기 초과')
                time.sleep(.025)
        try: yield
        finally:
            handle.seek(0)
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)
            else:
                import fcntl
                fcntl.flock(handle,fcntl.LOCK_UN)


def sync_shared(folder, request):
    folder=Path(folder)
    if not isinstance(request['pc_id'],str) or len(request['pc_id'])!=32 or not all(c in '0123456789abcdef' for c in request['pc_id']):
        raise ValueError('잘못된 PC 식별자')
    with shared_lock(folder):
        state=_read(folder/'generation.json',{'epoch':'0'})
        epoch=state['epoch']
        if not isinstance(epoch,str): raise ValueError('잘못된 오류 기록 상태')
        pending=request.get('pending')
        if pending and epoch==pending['base']:
            epoch=pending['token']
            _write(folder/'generation.json',{'epoch':epoch})
        elif not (folder/'generation.json').exists():
            _write(folder/'generation.json',{'epoch':epoch})
        # An offline writer must learn the generation before it can publish.
        own=recent(request['records']) if request['epoch']==epoch else []
        own=[r for r in own if r['epoch']==epoch and r['pc_id']==request['pc_id']]
        _write(folder/('pc-'+request['pc_id']+'.json'),{'epoch':epoch,'records':own})
        merged=[]
        for path in folder.glob('pc-*.json'):
            data=_read(path)
            records=recent(data['records']) if data['epoch']==epoch else []
            if records!=data['records'] or data['epoch']!=epoch:
                _write(path,{'epoch':epoch,'records':records})
            merged.extend(records)
        return {'epoch':epoch,'records':recent(merged)}


def helper_main():
    request_path,result_path=sys.argv[2:4]
    try:
        request=_read(Path(request_path))
        result={'ok':True,'data':sync_shared(request['folder'],request['request'])}
    except Exception as exc: result={'ok':False,'error':str(exc)}
    _write(Path(result_path),result)


class SharedTransport:
    def __init__(self, script, local_folder, folder, timeout=5):
        self.script=Path(script);self.local=Path(local_folder);self.folder=str(folder)
        self.timeout=timeout
        self.process=None;self._lock=threading.Lock();self.closed=False

    def close(self):
        with self._lock:
            self.closed=True
            if self.process is not None and self.process.poll() is None:
                try:self.process.kill()
                except OSError:pass

    def sync(self, request):
        # Only called by the single controller worker, never the Tk thread.
        self.local.mkdir(parents=True,exist_ok=True)
        token=uuid.uuid4().hex
        inp=self.local/(token+'-in.json');out=self.local/(token+'-out.json')
        try:
            _write(inp,{'folder':self.folder,'request':request})
            flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
            with self._lock:
                if self.closed:raise RuntimeError('오류 기록 동기화 종료 중')
                process=self.process=subprocess.Popen([sys.executable,str(self.script),'--error-sync',str(inp),str(out)],
                    stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                    creationflags=flags)
            try: process.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                process.kill();process.wait(timeout=2)
                raise TimeoutError('공유 연결 시간 초과 · 이 PC 기록은 보관 중')
            result=_read(out)
            if not result['ok']: raise OSError(result['error'])
            return result['data']
        finally:
            with self._lock:self.process=None
            for path in (inp,out,inp.with_suffix('.tmp'),out.with_suffix('.tmp')):
                try:path.unlink()
                except OSError:pass


def environment():
    """오류가 난 PC의 환경 한 줄. 알아내지 못해도 기록을 막지 않습니다."""
    import platform
    parts = [('Windows ' + platform.version()) if os.name == 'nt' else platform.system() + ' ' + platform.release(),
             'Python ' + platform.python_version()]
    if os.name == 'nt':
        try:
            import ctypes
            user = ctypes.windll.user32
            parts.append('화면 {}x{}'.format(user.GetSystemMetrics(0), user.GetSystemMetrics(1)))
            parts.append('모니터 {}대'.format(user.GetSystemMetrics(80)))
            parts.append('배율 {}%'.format(round(user.GetDpiForSystem() * 100 / 96)))
        except Exception:
            pass
    return ' · '.join(parts)


def compose_detail(context='', trace='', environment_line='', limit=16000):
    """상세 정보를 항상 [환경] → [진단] → [추적] 순서로 만듭니다(사람도 AI도 같은 자리에서 찾도록).

    저장 형식은 그대로(상세 정보 글 한 덩어리)라서 예전 버전 PC와 섞여도 됩니다.
    """
    parts = []
    if environment_line: parts.append('[환경] ' + str(environment_line)[:300])
    context = str(context or '').strip()
    if context: parts.append('[진단]\n' + context[:6000])
    trace = str(trace or '').strip()
    if trace:
        used = sum(len(p) + 1 for p in parts)
        parts.append('[추적]\n' + trace[-max(2000, limit - used - 8):])
    return '\n'.join(parts)


class Recorder:
    def __init__(self, path, feature, version):
        self.environment = ''
        self.path=Path(path);self.feature=feature;self.version=version
        self.events=queue.Queue(maxsize=200);self.closed=False;self.error='';self.store=None
        self.thread=threading.Thread(target=self._run,name='error-history-local',daemon=True)
        self.thread.start()

    def capture(self, message, feature=None, stage='', detail='', work='', context=''):
        if self.closed:return
        detail=compose_detail(context,detail,self.environment)
        try:self.events.put_nowait(dict(feature=feature or self.feature,message=str(message)[:8192],
            stage=str(stage)[:300],detail=str(detail)[-16384:],work=str(work)[:120],version=self.version))
        except queue.Full:self.error='오류가 연속 발생하여 일부 기록을 보관하지 못했습니다.'

    def _run(self):
        while True:
            event=self.events.get()
            try:
                if event is None:return
                if self.store is None:self.store=LocalStore(self.path)
                self.store.record(**event)
            except Exception as exc:self.error='오류 기록 로컬 저장 실패: '+str(exc)
            finally:self.events.task_done()

    def close(self):
        self.closed=True
        try:self.events.put_nowait(None)
        except queue.Full:pass
        self.thread.join(timeout=.5)


_recorder=None


def capture(message, feature=None, stage='', detail='', work='', context=''):
    """context: 그 기능이 아는 진단 정보(몇 줄). 상세 정보의 [진단] 자리에 들어갑니다."""
    if _recorder is not None:
        try:_recorder.capture(message,feature,stage,detail,work,context)
        except Exception:pass


def install(feature, version, path=None):
    global _recorder
    if _recorder is not None:return _recorder
    base=Path(os.environ.get('LOCALAPPDATA') or str(Path.home()))/'Jihunius'/'error-history'
    _recorder=Recorder(path or base/'history.sqlite',feature,version)
    try:_recorder.environment=environment()
    except Exception:pass
    import atexit
    atexit.register(_recorder.close)
    import tkinter as tk
    from tkinter import messagebox
    for name in ('showerror','showwarning'):
        original=getattr(messagebox,name)
        def wrapped(title=None,message=None,_original=original,_name=name,**options):
            text=str(message or '')
            if _name=='showerror' or any(word in text for word in ('실패','오류','못했','충돌','누락')):
                capture(text,stage=str(title or '오류 알림'))
            return _original(title,message,**options)
        setattr(messagebox,name,wrapped)
    old_tk=tk.Tk.report_callback_exception
    def callback(root,kind,value,tb):
        capture(value,stage='화면 처리',detail=''.join(traceback.format_exception(kind,value,tb)))
        return old_tk(root,kind,value,tb)
    tk.Tk.report_callback_exception=callback
    old_sys=sys.excepthook
    def exception(kind,value,tb):
        capture(value,stage='처리되지 않은 오류',detail=''.join(traceback.format_exception(kind,value,tb)))
        return old_sys(kind,value,tb)
    sys.excepthook=exception
    if hasattr(threading,'excepthook'):
        old_thread=threading.excepthook
        def thread_exception(args):
            capture(args.exc_value,stage='백그라운드 처리',detail=''.join(traceback.format_exception(args.exc_type,args.exc_value,args.exc_traceback)))
            return old_thread(args)
        threading.excepthook=thread_exception
    return _recorder


class Service:
    """The GUI only sends commands and reads an immutable in-memory snapshot."""
    def __init__(self, path, shared_folder, helper_source):
        self.path=Path(path);self.shared_folder=shared_folder;self.helper_source=helper_source
        self.commands=queue.Queue(maxsize=32);self.stopped=threading.Event()
        self.transport=None
        self.latest=dict(records=[],enabled=True,unread=0,pending_clear=False,pc_id='',status='기록 불러오는 중…')
        self.thread=threading.Thread(target=self._run,name='error-history-sync',daemon=True)
        self.thread.start()

    def snapshot(self):return self.latest

    def command(self, name, value=None):
        try:self.commands.put_nowait((name,value))
        except queue.Full:pass

    def close(self):
        self.stopped.set();self.command('stop')
        if self.transport is not None:self.transport.close()

    def _run(self):
        store=None;transport=None;opened=False;force=True;next_sync=0;last_key=None
        status='이 PC 기록';successful=False
        revision=None;view=None;req=None;next_prune=0
        while not self.stopped.is_set():
            try:
                if store is None:store=LocalStore(self.path)
                commands=[]
                try:commands.append(self.commands.get(timeout=.5))
                except queue.Empty:pass
                while len(commands)<32:
                    try:commands.append(self.commands.get_nowait())
                    except queue.Empty:break
                for name,value in commands:
                    if name=='stop':return
                    if name=='open':opened=bool(value);force=opened or force
                    elif name=='refresh':force=True
                    elif name=='seen':store.mark_seen()
                    elif name=='enabled':store.set_enabled(value)
                    elif name=='clear':store.clear_all();force=True
                now=time.monotonic();current=store.revision()
                if view is None or current!=revision or now>=next_prune:
                    view=store.view();req=store.request();revision=current;next_prune=now+3600
                key=(req['epoch'],tuple((r['id'],r['last'],r['count']) for r in req['records']))
                if force or (now>=next_sync and (key!=last_key or opened or req['pending'])):
                    # Publish pending state before entering potentially slow SMB.
                    self.latest=dict(view,status='전체 PC 삭제 전달 중…' if req['pending'] else '공유 기록 확인 중…')
                    try:
                        if transport is None:
                            helper_dir=self.path.parent/'sync';helper_dir.mkdir(parents=True,exist_ok=True)
                            digest=hashlib.sha256(self.helper_source.encode()).hexdigest()[:16]
                            script=helper_dir/('helper-'+digest+'.py')
                            if not script.exists():script.write_text(self.helper_source,encoding='utf-8')
                            transport=SharedTransport(script,helper_dir,self.shared_folder)
                            self.transport=transport
                        if self.stopped.is_set():transport.close();return
                        result=transport.sync(req);store.accept(req,result)
                        status='전체 PC 기록 삭제 완료' if req['pending'] else '공유 기록 확인 완료'
                        last_key=key;successful=True;next_sync=now+5
                    except Exception as exc:
                        status=('전체 PC 삭제 대기 · ' if req['pending'] else '공유 연결 대기 · ')+str(exc)[:240]
                        successful=False;next_sync=time.monotonic()+30
                    force=False;view=store.view()
                if view['pending_clear'] and '삭제' not in status:status='전체 PC 삭제 대기 · 연결되면 반영됩니다'
                self.latest=dict(view,status=status,connected=successful)
            except Exception as exc:
                self.latest=dict(self.latest,status='오류 기록 처리 실패: '+str(exc)[:240])
                self.stopped.wait(1)


if __name__=='__main__' and len(sys.argv)>1 and sys.argv[1]=='--error-sync':
    helper_main()
