"""Public GitHub update transport and local Python version selection. Python 3.8+."""
import ast
import ctypes
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

OWNER = 'corsk970119-ux'
REPO = 'jihunius-updates'
CHANNEL = 'channels/stable.json'
MAX_PAYLOAD = 8 * 1024 * 1024
MAX_MANIFEST = 128 * 1024
SHA = re.compile(r'[0-9a-f]{64}')

class UpdateError(Exception):
    pass

def version(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}\.\d{1,2}\.\d{1,2}\.[1-9]\d{0,5}',value):
        raise UpdateError('배포 버전 형식을 확인해 주세요.')
    parts=tuple(int(x) for x in value.split('.'))
    try:date(*parts[:3])
    except ValueError:raise UpdateError('배포 날짜가 올바르지 않습니다.') from None
    return parts

def descriptor(value, require_protocol=True):
    if not isinstance(value,dict):raise UpdateError('배포 정보가 올바르지 않습니다.')
    v=value.get('version');version(v)
    if not SHA.fullmatch(str(value.get('sha256',''))):raise UpdateError('배포 검증 값이 올바르지 않습니다.')
    size=value.get('size')
    if type(size) is not int or not 0 < size <= MAX_PAYLOAD:raise UpdateError('배포 파일 크기를 확인해 주세요.')
    if value.get('path')!='releases/jihunius/{}/app.pyw'.format(v):raise UpdateError('지후니우스 배포 경로가 아닙니다.')
    minimum=value.get('min_python',[3,8])
    if not isinstance(minimum,list) or len(minimum)!=2 or any(type(x) is not int or not 0<=x<100 for x in minimum):
        raise UpdateError('실행 환경 정보가 올바르지 않습니다.')
    if tuple(sys.version_info[:2])<tuple(minimum):raise UpdateError('이 버전은 더 새로운 Python이 필요합니다.')
    if require_protocol and value.get('update_protocol')!=1:raise UpdateError('현재 실행기에서 지원하지 않는 배포입니다.')
    result={k:value[k] for k in ('version','path','sha256','size')}
    result.update(min_python=minimum,update_protocol=value.get('update_protocol',0),notes=str(value.get('notes',''))[:10000])
    return result

def verify(data, value):
    if len(data)!=value['size'] or hashlib.sha256(data).hexdigest()!=value['sha256']:
        raise UpdateError('받은 파일의 크기 또는 검증 값이 맞지 않습니다. 기존 버전을 유지합니다.')
    try:compile(data,'지후니우스.pyw','exec')
    except (SyntaxError,ValueError,TypeError):raise UpdateError('받은 파일의 Python 문법을 확인하지 못했습니다.') from None

def atomic(path, data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.update-',suffix='.tmp',dir=str(path.parent))
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(name,str(path))
    finally:
        try:os.unlink(name)
        except FileNotFoundError:pass

def read_json(path):
    try:
        p=Path(path)
        if p.stat().st_size>MAX_MANIFEST:return {}
        value=json.loads(p.read_text(encoding='utf-8'))
        return value if isinstance(value,dict) else {}
    except (OSError,ValueError):return {}

def write_json(path,value):
    atomic(path,json.dumps(value,ensure_ascii=False,indent=2).encode('utf-8'))

class FileLock:
    def __init__(self,path):self.path=Path(path);self.stream=None
    def acquire(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.stream=self.path.open('a+b');self.stream.seek(0,2)
        if not self.stream.tell():self.stream.write(b'0');self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            return True
        except OSError:self.stream.close();self.stream=None;return False
    def release(self):
        if self.stream is None:return
        try:
            self.stream.seek(0)
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(),msvcrt.LK_UNLCK,1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(),fcntl.LOCK_UN)
        finally:self.stream.close();self.stream=None

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise UpdateError('배포 응답 경로가 달라 확인을 보류했습니다.')

def public_fetch(path,maximum,seconds):
    if not isinstance(path,str) or '\\' in path or any(x in ('','..','.') for x in path.split('/')):
        raise UpdateError('잘못된 배포 경로입니다.')
    # Public raw content avoids per-PC authentication and API rate limits.
    url='https://raw.githubusercontent.com/{}/{}/main/{}'.format(OWNER,REPO,urllib.parse.quote(path,safe='/'))
    def read():
        request=urllib.request.Request(url,headers={'User-Agent':'Jihunius-Updater/1','Cache-Control':'no-cache'})
        with urllib.request.build_opener(NoRedirect()).open(request,timeout=seconds) as response:
            if response.geturl()!=url:raise UpdateError('예상하지 못한 배포 응답입니다.')
            data=response.read(maximum+1)
            if len(data)>maximum:raise UpdateError('배포 파일이 허용 크기를 초과했습니다.')
            return data
    # Limit total wall time as well as socket read time. At most one fetch is in flight per UI.
    result=queue.Queue(maxsize=1)
    def worker():
        try:result.put((True,read()))
        except Exception as exc:result.put((False,exc))
    threading.Thread(target=worker,daemon=True).start()
    try:ok,value=result.get(timeout=seconds)
    except queue.Empty:raise UpdateError('업데이트 확인 시간이 초과됐습니다. 현재 버전은 계속 사용할 수 있습니다.') from None
    if not ok:
        if isinstance(value,UpdateError):raise value
        if isinstance(value,urllib.error.HTTPError) and value.code==404:
            raise UpdateError('공개 배포 정보를 아직 찾을 수 없습니다. 현재 버전은 계속 사용할 수 있습니다.') from None
        raise UpdateError('GitHub에 연결하지 못했습니다. 현재 버전은 계속 사용할 수 있습니다.') from None
    return value

def check_offer(current,fetch=public_fetch,rejected_sha=None):
    try:manifest=json.loads(fetch(CHANNEL,MAX_MANIFEST,12).decode('utf-8-sig'))
    except (ValueError,UnicodeError):raise UpdateError('배포 목록을 읽지 못했습니다.') from None
    if not isinstance(manifest,dict) or manifest.get('schema')!=1 or not isinstance(manifest.get('apps'),dict):
        raise UpdateError('배포 목록 형식을 확인해 주세요.')
    offered=descriptor(manifest['apps'].get('jihunius'),require_protocol=False)
    if version(offered['version'])<version(current['version']):return {'kind':'current'}
    if version(offered['version'])==version(current['version']):
        if offered['sha256']!=current['sha256']:raise UpdateError('같은 버전의 내용이 달라 업데이트를 보류했습니다.')
        return {'kind':'current'}
    offered=descriptor(offered)
    if offered['sha256']==rejected_sha:return {'kind':'rejected','offered':offered}
    return {'kind':'available','offered':offered}

def embedded_version(data, fallback):
    """A shared origin may change after the launcher was loaded by Python."""
    values=[]
    try:
        for node in ast.parse(data).body:
            if (isinstance(node,ast.Assign) and len(node.targets)==1
                    and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='SUITE_APP_VERSION'):
                values.append(ast.literal_eval(node.value))
        if len(values)>1:raise ValueError('duplicate version')
        result=values[0] if values else fallback
        version(result)
        return result
    except (SyntaxError,ValueError,TypeError,UpdateError):
        raise UpdateError('실행 파일에 기록된 버전을 확인하지 못했습니다.') from None

class Store:
    def __init__(self,root,origin,base_version):
        self.root=Path(root);self.origin=Path(origin).resolve();self.base_version=base_version
    def state(self):return read_json(self.root/'state.json')
    def save(self,state):write_json(self.root/'state.json',state)
    def path(self,value):
        if not isinstance(value,dict) or not SHA.fullmatch(str(value.get('sha256',''))):raise UpdateError('캐시 정보가 올바르지 않습니다.')
        return self.root/'versions'/value['sha256']/'app.pyw'
    def valid(self,value):
        try:
            value=descriptor(value);p=self.path(value)
            if p.is_symlink() or p.parent.is_symlink() or p.stat().st_size!=value['size']:return None
            verify(p.read_bytes(),value);return value
        except (OSError,ValueError,TypeError,KeyError,UpdateError):return None
    def prepare(self):
        data=self.origin.read_bytes()
        self.base_version=embedded_version(data,self.base_version)
        base=descriptor({'version':self.base_version,'path':'releases/jihunius/{}/app.pyw'.format(self.base_version),
                         'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),'min_python':[3,8],'update_protocol':1})
        verify(data,base)
        if not self.valid(base):atomic(self.path(base),data)
        state=self.state();current=self.valid(state.get('current'));previous=self.valid(state.get('previous'))
        if current is None:current=previous
        if current is None or version(current['version'])<version(base['version']):current=base
        state.update(current=current,previous=previous,base=base)
        self.save(state);self.cancel_request();self.prune(state)
        return current
    def stage(self,value,data):
        value=descriptor(value);verify(data,value)
        atomic(self.path(value),data)
        return value
    def request(self,value,nonce):
        value=self.valid(value)
        if value is None:raise UpdateError('준비된 업데이트 파일을 확인하지 못했습니다.')
        current=self.state().get('current')
        if version(value['version'])<=version(current['version']):raise UpdateError('더 새로운 버전만 적용할 수 있습니다.')
        write_json(self.root/'request.json',{'nonce':nonce,'offered':value})
    def cancel_request(self):
        try:(self.root/'request.json').unlink()
        except FileNotFoundError:pass
    def consume_request(self,nonce,returncode):
        request=read_json(self.root/'request.json');self.cancel_request()
        if returncode!=0 or request.get('nonce')!=nonce:return False
        offered=self.valid(request.get('offered'));state=self.state();current=self.valid(state.get('current'))
        if offered is None or current is None or version(offered['version'])<=version(current['version']):return False
        state.update(previous=current,current=offered,rejected_sha=None,trial=offered['sha256'])
        self.save(state);return True
    def restore_failed(self,current):
        state=self.state()
        if state.get('trial')!=current['sha256']:return False
        previous=self.valid(state.get('previous'))
        if previous is None:return False
        state.update(current=previous,previous=None,trial=None,rejected_sha=current['sha256'])
        self.save(state);return True
    def confirm(self,current):
        state=self.state()
        if state.get('trial')==current['sha256']:state['trial']=None;self.save(state)
    def prune(self,state):
        keep={x['sha256'] for x in (state.get('base'),state.get('current'),state.get('previous')) if isinstance(x,dict) and SHA.fullmatch(str(x.get('sha256','')))}
        for p in (self.root/'versions').glob('*'):
            if SHA.fullmatch(p.name) and p.name not in keep and p.is_dir() and not p.is_symlink():shutil.rmtree(p,ignore_errors=True)

def root_for(origin):
    key=hashlib.sha256(os.path.normcase(str(Path(origin).resolve())).encode('utf-8')).hexdigest()[:24]
    return Path(os.environ.get('LOCALAPPDATA') or Path.home())/'JihuniusTools'/'desktop-v1'/key

def show_message(text):
    if os.name=='nt':ctypes.windll.user32.MessageBoxW(0,text,'지후니우스 업데이트',0x40)
    else:print(text,file=sys.stderr)

def focus_process(pid):
    if os.name!='nt' or type(pid) is not int or pid<=0:return False
    from ctypes import wintypes as w
    u=ctypes.WinDLL('user32',use_last_error=True);cb=ctypes.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
    u.EnumWindows.argtypes=[cb,w.LPARAM];u.EnumWindows.restype=w.BOOL
    u.GetWindowThreadProcessId.argtypes=[w.HWND,ctypes.POINTER(w.DWORD)];u.GetWindowThreadProcessId.restype=w.DWORD
    u.GetWindowTextW.argtypes=[w.HWND,w.LPWSTR,ctypes.c_int];u.GetWindowTextW.restype=ctypes.c_int
    u.ShowWindow.argtypes=[w.HWND,ctypes.c_int];u.ShowWindow.restype=w.BOOL
    u.SetForegroundWindow.argtypes=[w.HWND];u.SetForegroundWindow.restype=w.BOOL
    found=[]
    def visit(hwnd,lparam):
        actual=w.DWORD();u.GetWindowThreadProcessId(hwnd,ctypes.byref(actual))
        if actual.value==pid:
            title=ctypes.create_unicode_buffer(128);u.GetWindowTextW(hwnd,title,128)
            if title.value=='지후니우스':found.append(hwnd)
        return True
    u.EnumWindows(cb(visit),0)
    if not found:return False
    u.ShowWindow(found[0],9);u.SetForegroundWindow(found[0]);return True

def managed_context(app_version=None):
    if os.environ.get('JIHUNIUS_UPDATE_CHILD')!='1':return None
    origin=os.environ.get('JIHUNIUS_UPDATE_ORIGIN','');nonce=os.environ.get('JIHUNIUS_UPDATE_NONCE','')
    if not origin or not re.fullmatch(r'[0-9a-f]{32}',nonce):return None
    root=root_for(origin);session=read_json(root/'session.json')
    if session.get('nonce')!=nonce or session.get('pid') not in (None,os.getpid()):return None
    value=descriptor(session.get('current'))
    if Path(sys.argv[0]).resolve()!=root/'versions'/value['sha256']/'app.pyw':return None
    if app_version is not None and app_version!=value['version']:
        # Old installed launchers could pair freshly replaced shared bytes with
        # their already-loaded version constant. Correct metadata only for these
        # exact verified bytes, before the UI announces a version or copies origin.
        data=Path(sys.argv[0]).read_bytes();verify(data,value)
        if embedded_version(data,None)!=app_version:raise UpdateError('실행 중인 버전 정보를 확인하지 못했습니다.')
        state=read_json(root/'state.json')
        if state.get('current',{}).get('sha256')!=value['sha256']:
            raise UpdateError('적용 버전이 변경됐습니다. 프로그램을 다시 실행해 주세요.')
        corrected=dict(value,version=app_version,path='releases/jihunius/'+app_version+'/app.pyw')
        descriptor(corrected)
        for key in ('current','base','previous'):
            if isinstance(state.get(key),dict) and state[key].get('sha256')==value['sha256']:
                state[key]=dict(state[key],version=app_version,path=corrected['path'])
        write_json(root/'state.json',state)
        session['current']=corrected
        if isinstance(state.get('base'),dict):session['base_version']=state['base']['version']
        write_json(root/'session.json',session);value=corrected
    return {'origin':origin,'nonce':nonce,'root':root,'current':value,'base_version':session['base_version'],
            'supervisor_pid':session.get('supervisor_pid')}

def process_alive(pid):
    if type(pid) is not int or pid<=0:return False
    if os.name=='nt':
        from ctypes import wintypes as w
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];kernel.OpenProcess.restype=w.HANDLE
        kernel.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD];kernel.WaitForSingleObject.restype=w.DWORD
        kernel.CloseHandle.argtypes=[w.HANDLE];kernel.CloseHandle.restype=w.BOOL
        handle=kernel.OpenProcess(0x00100000,False,pid)
        if not handle:return False
        try:return kernel.WaitForSingleObject(handle,0)==258
        finally:kernel.CloseHandle(handle)
    try:os.kill(pid,0);return True
    except OSError:return False

def managed_lease(context):
    lease=FileLock(context['root']/'active-app.lock')
    if not lease.acquire():raise UpdateError('이미 실행 중인 지후니우스 창을 먼저 확인해 주세요.')
    return lease

def native_dialog_open(root, allowed_grab=None):
    try:
        grabbed=root.grab_current()
        if grabbed is not None and grabbed is not allowed_grab:return True
        if os.name!='nt':return False
        from ctypes import wintypes as w
        u=ctypes.WinDLL('user32',use_last_error=True)
        u.GetAncestor.argtypes=[w.HWND,w.UINT];u.GetAncestor.restype=w.HWND
        u.IsWindowEnabled.argtypes=[w.HWND];u.IsWindowEnabled.restype=w.BOOL
        owner=u.GetAncestor(root.winfo_id(),2)
        return bool(owner) and not bool(u.IsWindowEnabled(owner))
    except Exception:
        # If the native state cannot be checked, do not assume it is safe to exit.
        return True

def mark_ready(context):
    if context:
        # Older installed launchers check this marker before creating a shortcut.
        # Keep them disabled when they start a newer cached version.
        atomic(context['root']/'shortcut-created',b'disabled')
        write_json(context['root']/'ready.json',{'nonce':context['nonce']})

def launch(origin,base_version,argv=None,icon_bytes=None):
    origin=Path(origin).resolve();store=Store(root_for(origin),origin,base_version)
    lock=FileLock(store.root/'instance.lock')
    if not lock.acquire():
        if not focus_process(read_json(store.root/'session.json').get('pid')):
            show_message('지후니우스가 이미 실행 중입니다. 트레이 아이콘에서 열어 주세요.')
        return 0
    try:
        active=FileLock(store.root/'active-app.lock')
        if not active.acquire():
            if not focus_process(read_json(store.root/'session.json').get('pid')):
                show_message('지후니우스가 실행 중입니다. 트레이에서 열거나 완전 종료한 뒤 다시 실행하세요.')
            return 0
        active.release()
        current=store.prepare()
        while True:
            nonce=uuid.uuid4().hex
            session={'nonce':nonce,'current':current,'base_version':store.base_version,'supervisor_pid':os.getpid()}
            write_json(store.root/'session.json',session)
            try:(store.root/'ready.json').unlink()
            except FileNotFoundError:pass
            environment=os.environ.copy()
            environment.update(JIHUNIUS_UPDATE_CHILD='1',JIHUNIUS_UPDATE_ORIGIN=str(origin),JIHUNIUS_UPDATE_NONCE=nonce,
                               JIHUNIUS_LAUNCH_DIR=str(origin.parent))
            executable=Path(sys.executable)
            if os.name=='nt' and executable.with_name('pythonw.exe').is_file():executable=executable.with_name('pythonw.exe')
            try:
                process=subprocess.Popen([str(executable),str(store.path(current))]+list(argv or []),cwd=str(origin.parent),env=environment)
            except OSError:
                store.restore_failed(current)
                raise UpdateError('프로그램을 시작하지 못했습니다. 기존 버전과 Python 설치를 확인해 주세요.') from None
            session['pid']=process.pid;write_json(store.root/'session.json',session)
            code=process.wait()
            ready=read_json(store.root/'ready.json').get('nonce')==nonce
            if not ready:
                if store.restore_failed(current):
                    show_message('새 버전이 시작되지 않아 이전 버전으로 복구했습니다. 같은 파일을 다시 실행해 주세요.')
                else:show_message('지후니우스가 시작을 완료하지 못했습니다. 표시된 실행 오류를 확인해 주세요.')
                store.cancel_request();return code or 1
            store.confirm(current)
            if not store.consume_request(nonce,code):return code
            current=store.state()['current']
    except (OSError,ValueError,UpdateError) as exc:
        show_message(str(exc) if isinstance(exc,UpdateError) else '업데이트 저장 공간을 확인해 주세요. 업무 파일은 변경하지 않았습니다.')
        return 1
    finally:lock.release()
