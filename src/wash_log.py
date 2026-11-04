# -*- coding: utf-8 -*-
"""세척일보 0.25 — 공유폴더 연결 유지·자동 복구 및 저장 대기 안정화."""
import os, json, uuid, time, queue, threading, tempfile, csv, io, copy, shutil, multiprocessing, errno, stat
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont

BG, PANEL, TEXT, MUTED, LINE = '#0f0f0f', '#22262c', '#e6edf5', '#a4bdd4', '#343b45'
FIELD, ACCENT, BUTTON, SELECT = '#181a1e', '#263c53', '#22262c', '#263c53'
ROW_A, ROW_B, HEADER, BLUE = '#191c20', '#1d2025', '#242d38', '#95caff'
YELLOW, YTEXT = '#f3d97a', '#27200d'
APP_ICON_PNGS = ('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')

HOME_TEST = False
CONFIG_DIR = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'WashLog'
CONFIG_FILE = CONFIG_DIR / 'settings.json'
DEFAULT_PARENT = r'\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈'
DEFAULT_FOLDER = DEFAULT_PARENT + r'\세척일보'

def _diagnostic_error(message,stage):
    import sys
    module=sys.modules.get("jihunius_error_history")
    if module is not None:module.capture(message,stage=stage)


def initial():
    return {'format': 1, 'id': str(uuid.uuid4()), 'tools': [''] * 9, 'days': {}, 'notes': []}

def new_day():
    return {'manual_plates': True, 'plates': [{'id': str(uuid.uuid4()), 'number': 1, 'cells': [''] * 15, 'put': ''}]}

def plate_title(plate):
    if plate.get('type') == 'cnt':return 'CNT'+str(plate['number'])
    return '완료' if plate.get('type') == 'complete' else str(plate['number'])+'번'

def now():
    return datetime.now().astimezone().isoformat(timespec='seconds')

class LockBusyError(RuntimeError):
    pass

@contextmanager
def file_lock(path):
    f = open(path, 'a+b')
    acquired = False
    try:
        f.seek(0, 2)
        if f.tell() == 0:
            f.write(b'0'); f.flush()
        deadline = time.monotonic() + 5
        while True:
            f.seek(0)
            try:
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except OSError as exc:
                # Only lock/sharing conflicts mean another PC is busy. A lost
                # SMB connection or invalid handle must reach transport recovery.
                winerror=getattr(exc,'winerror',None)
                contended=(winerror in (32,33) if winerror is not None
                           else exc.errno in (errno.EACCES,errno.EAGAIN))
                if not contended:raise
                if time.monotonic() >= deadline:
                    raise LockBusyError('다른 PC의 저장이 끝나지 않았습니다. 잠시 후 다시 시도해주세요.')
                time.sleep(.05)
        yield
    finally:
        try:
            if acquired:
                f.seek(0)
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        finally:
            f.close()


def atomic_json(path, value):
    fd, name = tempfile.mkstemp(prefix='.wash-', suffix='.tmp', dir=path.parent)
    replaced = False
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.flush(); os.fsync(f.fileno())
        os.replace(name, path)
        replaced = True
    finally:
        # A completed replace has no temporary file left. Avoid another SMB
        # request after commit; cleanup failure must not mask the original error.
        if not replaced:
            try:os.unlink(name)
            except OSError:pass

MISSING_JSON = object()

class Store:
    def __init__(self, folder):
        self.folder=Path(folder)
        if HOME_TEST:
            self.folder.mkdir(parents=True,exist_ok=True)
        elif str(self.folder)==DEFAULT_FOLDER and not self.folder.is_dir():
            if not Path(DEFAULT_PARENT).is_dir():raise FileNotFoundError('공유폴더에 접속할 수 없습니다. 이 PC의 경로를 확인해주세요.')
            self.folder.mkdir(exist_ok=True)
        if not self.folder.is_dir():raise FileNotFoundError('선택한 폴더에 접속할 수 없습니다.')
        self.path=self.folder/'wash_log_data.json'  # Also prevents old versions from editing migrated data.
        self.lock=self.folder/'wash_log_data.lock'
        self.meta=self.folder/'저장정보.json'
    def day_path(self,day):
        day=date.fromisoformat(day).isoformat()
        return self.folder/'세척일보'/(day[:4]+'년')/(day[5:7]+'월')/(day+'.json')
    def scope_path(self,scope,day=None):
        return self.day_path(day) if scope=='daily' else self.folder/('공구대.json' if scope=='tools' else '부서메모.json')
    def backup_dir(self,scope,day=None):
        return self.folder/'백업'/({'tools':'공구대','notes':'부서메모','daily':'세척일보'}[scope])/(day if scope=='daily' else '기록')
    def write_scope(self,path,value):
        path.parent.mkdir(parents=True,exist_ok=True);atomic_json(path,value)
    def read_optional_json(self,path,expected_id=None):
        try:return json.loads(path.read_text(encoding='utf-8'))
        except FileNotFoundError as exc:
            # Windows network-name errors can also be FileNotFoundError. Only
            # a genuinely absent file/path may initialize a new day or store.
            winerror=getattr(exc,'winerror',None)
            if winerror not in (None,2,3):raise
            if winerror is None and exc.errno not in (None,errno.ENOENT):raise
            if not stat.S_ISDIR(self.folder.stat().st_mode):
                raise NotADirectoryError('공유 데이터 폴더에 접속할 수 없습니다.')
            if expected_id is not None:
                meta=json.loads(self.meta.read_text(encoding='utf-8'))
                if meta.get('id')!=expected_id:
                    raise ConflictError('공유 데이터 ID가 변경되었습니다. 경로를 확인하고 재연결해주세요.')
            return MISSING_JSON
    def connect(self,day=None):
        with file_lock(self.lock):
            meta=self.read_optional_json(self.meta)
            if meta is MISSING_JSON:
                legacy=self.read_optional_json(self.path)
                existing=legacy is not MISSING_JSON
                if not existing:
                    # Missing identity files must not reset existing split data.
                    with os.scandir(self.folder) as entries:
                        if any(entry.name in ('공구대.json','부서메모.json','세척일보') for entry in entries):
                            raise RuntimeError('기존 자료는 있지만 저장정보 파일을 찾을 수 없습니다. 자료를 초기화하지 않았습니다.')
                    legacy=initial()
                if not existing and day:legacy['days'][day]=new_day()
                if legacy.get('format')!=1:raise RuntimeError('이전 자료 형식을 확인할 수 없습니다. 원본을 보존했습니다.')
                # Persist a resumable source before initializing split files.
                # A timeout halfway through the first connection can then resume
                # with the same ID instead of looking like a lost identity file.
                if not existing:atomic_json(self.path,legacy)
                # Complete source is retained before any conversion, including prior backups.
                archive=self.folder/'이전통합백업';archive.mkdir(exist_ok=True)
                if existing and not (archive/'전환전원본.json').exists():atomic_json(archive/'전환전원본.json',legacy)
                self.write_scope(self.scope_path('tools'),legacy['tools'])
                self.write_scope(self.scope_path('notes'),legacy['notes'])
                for key,value in legacy['days'].items():self.write_scope(self.day_path(key),value)
                meta={'format':2,'id':legacy['id']};atomic_json(self.meta,meta)
            if meta.get('format')!=2:raise RuntimeError('지원하지 않는 저장 형식입니다.')
            # Retain old backups separately; no new writes ever use them.
            archive=self.folder/'이전통합백업'
            oldbackup=self.folder/'wash_log_backups'
            if oldbackup.exists():
                archive.mkdir(exist_ok=True)
                if not (archive/'기존백업').exists():oldbackup.rename(archive/'기존백업')
            previous=self.folder/'wash_log_data.previous.json'
            if previous.exists():
                archive.mkdir(exist_ok=True)
                previous.replace(archive/'직전통합본.json')
            marker={'format':2,'id':meta['id'],'message':'날짜별 저장 방식으로 전환되었습니다. 최신 세척일보 프로그램을 사용하세요.'}
            previous_marker=self.read_optional_json(self.path,expected_id=meta['id'])
            if previous_marker is MISSING_JSON or previous_marker.get('format')!=2:atomic_json(self.path,marker)
            return self._read(day)
    def _read(self,day=None,catalog=True):
        meta=json.loads(self.meta.read_text(encoding='utf-8'))
        data={'format':2,'id':meta['id'],'tools':json.loads(self.scope_path('tools').read_text(encoding='utf-8')),
              'notes':json.loads(self.scope_path('notes').read_text(encoding='utf-8')),'days':{}}
        if catalog:data['dates']=sorted(p.stem for p in (self.folder/'세척일보').glob('*년/*월/????-??-??.json'))
        if day:
            value=self.read_optional_json(self.day_path(day),expected_id=meta['id'])
            if value is not MISSING_JSON:data['days'][day]=value
        if catalog:data['backup_dates']=sorted(p.name for p in (self.folder/'백업'/'세척일보').glob('????-??-??') if p.is_dir())
        if catalog:data['legacy_backup']= (self.folder/'이전통합백업').exists()
        return data
    def read(self,day=None,catalog=True):
        with file_lock(self.lock):return self._read(day,catalog=catalog)
    def backup(self,scope,day,value):
        folder=self.backup_dir(scope,day);folder.mkdir(parents=True,exist_ok=True)
        atomic_json(folder/(datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'-'+uuid.uuid4().hex[:8]+'.json'),value)
        # Keep the most recent 30 versions in each independent scope/day.
        # Retention is housekeeping: a temporarily locked old backup must not
        # prevent saving the user's edit after its new backup was secured.
        try:
            files=sorted(folder.glob('*.json'))
            for path in files[:-30]:
                try:path.unlink()
                except OSError:pass
        except OSError:pass
    def update(self,op,receipt=False):
        with file_lock(self.lock):
            day=op.get('day');kind=op['kind']
            # Full folder listings are needed only for explicit management and
            # date navigation, not every cell edit or chat message on all PCs.
            catalog=kind in ('day','delete_day','restore_day','purge_backups','purge_legacy')
            data=self._read(day,catalog=catalog)
            if op.get('_store_id') and op['_store_id']!=data['id']:
                raise ConflictError('저장 대상 데이터가 변경되었습니다. 경로를 확인하고 재연결해주세요.')
            before=copy.deepcopy(data)
            if kind in ('delete_day','restore_day','purge_backups','purge_legacy'):
                if kind=='restore_day':
                    if day in data['days']:raise ConflictError('현재 일보가 이미 있습니다. 덮어쓰지 않았습니다.')
                    files=sorted(self.backup_dir('daily',day).glob('*.json'))
                    if not files:raise RuntimeError('복구할 백업이 없습니다.')
                    recovered=json.loads(files[-1].read_text(encoding='utf-8'))
                    self.write_scope(self.day_path(day),recovered)
                    data['days'][day]=recovered
                    data['dates']=sorted(set(data['dates'])|{day})
                    return (data,None) if receipt else data
                if kind=='delete_day':
                    if day not in data['days']:raise ConflictError('이미 삭제된 날짜입니다.')
                    expect(data['days'][day],op['old'])
                    if not op.get('include_backups'):
                        self.backup('daily',day,data['days'][day])
                        data['backup_dates']=sorted(set(data['backup_dates'])|{day})
                    else:
                        # Do fallible cleanup before deleting the live day, so
                        # cleanup failure cannot report a committed day as failed.
                        self.remove_backups('daily',day)
                        data['backup_dates']=[d for d in data['backup_dates'] if d!=day]
                    self.day_path(day).unlink()
                    data['days'].pop(day,None)
                    data['dates']=[d for d in data['dates'] if d!=day]
                elif kind=='purge_legacy':
                    archive=self.folder/'이전통합백업'
                    if archive.exists():shutil.rmtree(archive)
                    data['legacy_backup']=False
                else:
                    self.remove_backups(op['scope'],day)
                    if op['scope']=='daily':data['backup_dates']=[d for d in data['backup_dates'] if d!=day]
                return (data,None) if receipt else data
            scope=operation_scope(op)
            if scope=='daily' and kind!='day' and day not in data['days']:
                raise ConflictError('이 날짜의 일보가 삭제되었습니다. 최신 날짜 목록을 확인해주세요.')
            apply_op(data,op)
            key={'tools':'tools','notes':'notes','daily':'days'}[scope]
            old=before[key].get(day) if scope=='daily' else before[key]
            new=data[key].get(day) if scope=='daily' else data[key]
            receipt_data=undo_record(before,data,op)
            if old!=new:
                if old is not None:self.backup(scope,day,old)
                self.write_scope(self.scope_path(scope,day),new)
                if catalog and scope=='daily':
                    data['dates']=sorted(set(data['dates'])|{day})
                    if old is not None:data['backup_dates']=sorted(set(data['backup_dates'])|{day})
            # This snapshot is authoritative while the lock is held. Re-reading
            # after the replace adds SMB traffic and could turn a successful save
            # into an apparent failure if the next network read is interrupted.
            return (data,receipt_data) if receipt else data
    def remove_backups(self,scope,day):
        folder=self.backup_dir(scope,day)
        if folder.exists():shutil.rmtree(folder)

def operation_scope(op):
    kind=op['kind']
    if kind=='tool':return 'tools'
    if kind in ('note','clear_notes'):return 'notes'
    if kind=='undo':return op['scope']
    return 'daily'

def perform_disk_request(folder,kind,arg,day):
    try:
        store=Store(folder)
        if kind=='connect':
            data=store.connect(day)
            result=('ok',data,None)
        elif kind=='poll':result=('ok',store.read(day,catalog=bool(arg and arg.get('catalog'))),None)
        else:
            view=None
            if arg['kind']!='day' and arg.get('day')!=day:
                view=store.read(day,catalog=False)
                arg=dict(arg);arg.setdefault('_store_id',view['id'])
            data,receipt=store.update(arg,receipt=True)
            # Prepare an alternate visible day BEFORE the write. Failure of a
            # later refresh must never turn a committed save into a failure.
            if view:data['days'].update(view['days'])
            result=('ok',data,receipt)
    except LockBusyError as e:
        result=('busy',str(e),None)
    except ConflictError as e:
        try:latest=store.read(day)
        except Exception:latest=None
        result=('conflict',str(e),latest)
    except OSError as e:result=('unavailable',str(e),None)
    except (ValueError,KeyError,TypeError) as e:result=('invalid','저장 자료 확인 필요: '+str(e),None)
    except RuntimeError as e:result=('rejected',str(e),None)
    except Exception as e:result=('error','작업 처리 오류: '+str(e),None)
    return result

def disk_request(connection,folder,kind,arg,day):
    result=perform_disk_request(folder,kind,arg,day)
    try:connection.send(result)
    finally:connection.close()

def disk_service(connection):
    # One reusable helper per PC. A blocked SMB call can still be terminated
    # without blocking Tk or leaving an old result in a later request's queue.
    try:
        while True:
            request=connection.recv()
            if request is None:return
            connection.send(perform_disk_request(*request))
    except (EOFError,BrokenPipeError,OSError):pass
    finally:
        connection.close()

class DiskClient:
    def __init__(self,stop=None):
        self.stop=stop;self.process=None;self.connection=None
    def close(self):
        connection,self.connection=self.connection,None
        process,self.process=self.process,None
        if connection is not None:
            try:connection.close()
            except OSError:pass
        if process is not None:
            try:
                process.join(timeout=.1)
                if process.is_alive():process.terminate();process.join(timeout=.3)
                if process.is_alive():process.kill();process.join(timeout=.3)
                if not process.is_alive():process.close()
            except (OSError,ValueError):pass
    def start(self):
        if self.process is not None and self.process.is_alive():return
        self.close()
        ctx=multiprocessing.get_context('spawn');parent,child=ctx.Pipe()
        process=ctx.Process(target=disk_service,args=(child,),daemon=True)
        try:process.start()
        except Exception:
            parent.close();child.close()
            try:process.close()
            except ValueError:pass
            raise
        child.close();self.process=process;self.connection=parent
    def request(self,folder,kind,arg,day,timeout=None):
        timeout=timeout if timeout is not None else (8 if kind=='poll' else 30 if kind=='update' else 20)
        try:
            if self.stop is not None and self.stop.is_set():
                self.close();return ('cancelled','프로그램 종료 중',None)
            self.start()
            if self.stop is not None and self.stop.is_set():
                self.close();return ('cancelled','프로그램 종료 중',None)
            self.connection.send((folder,kind,arg,day))
            deadline=time.monotonic()+timeout
            while True:
                if self.stop is not None and self.stop.is_set():
                    self.close();return ('cancelled','프로그램 종료 중',None)
                remaining=deadline-time.monotonic()
                if remaining<=0:
                    self.close()
                    return ('timeout','공유폴더 응답이 지연되어 대기를 중단했습니다. '+('저장 여부는 연결 복구 후 확인해주세요.' if kind=='update' else '자동으로 연결을 다시 확인합니다.'),None)
                if self.connection.poll(min(.2,remaining)):
                    return self.connection.recv()
                if not self.process.is_alive():raise EOFError('파일 처리 프로세스 종료')
        except (OSError,EOFError,ValueError) as e:
            self.close()
            return ('unavailable','공유폴더 처리 응답을 받지 못했습니다: '+str(e),None)

def bounded_request(folder,kind,arg,day,timeout=20):
    client=DiskClient()
    try:return client.request(folder,kind,arg,day,timeout)
    finally:client.close()


class ConflictError(RuntimeError):
    pass

def expect(current, old):
    if current != old:
        raise ConflictError('다른 PC에서 같은 항목을 먼저 변경했습니다. 최신 내용을 확인하고 다시 입력해주세요.')

def undo_record(before, after, op):
    if op['kind'] in ('day','undo','delete_day','restore_day','purge_backups','purge_legacy') or before==after:return None
    scope=operation_scope(op)
    record={'kind':'undo','scope':scope,'day':op.get('day') if scope=='daily' else None,'patches':[]}
    patches=record['patches']
    if op['kind']=='reorder':
        patches.append({'target':'order','old':[p['id'] for p in before['days'][op['day']]['plates']],'new':[p['id'] for p in after['days'][op['day']]['plates']]})
    for i,(a,b) in enumerate(zip(before['tools'],after['tools'])):
        if a!=b:patches.append({'target':'tool','index':i,'old':a,'new':b})
    def changes(a,b,target):
        left={x['id']:x for x in a};right={x['id']:x for x in b}
        for ident in dict.fromkeys([*left,*right]):
            old=left.get(ident);new=right.get(ident)
            if old==new:continue
            if target=='plates' and old is not None and new is not None:
                for field in set(old)|set(new):
                    if old.get(field)==new.get(field):continue
                    if field=='cells' and len(old[field])==len(new[field]):
                        for i,(x,y) in enumerate(zip(old[field],new[field])):
                            if x!=y:patches.append({'target':'cell','id':ident,'index':i,'count':len(new[field]),'old':x,'new':y})
                    else:patches.append({'target':'field','id':ident,'field':field,'old':copy.deepcopy(old.get(field)),'new':copy.deepcopy(new.get(field))})
            else:
                patches.append({'target':target,'id':ident,'old':copy.deepcopy(old),'new':copy.deepcopy(new),'position':next((i for i,x in enumerate(a) if x['id']==ident),len(a))})
    changes(before['notes'],after['notes'],'notes')
    day=op.get('day')
    if day in before['days'] and day in after['days']:
        for target in ('plates','deleted'):
            changes(before['days'][day].get(target,[]),after['days'][day].get(target,[]),target)
    return record if patches else None

def apply_undo(data,op):
    # Store applies this to a private snapshot under its lock: any failed
    # expectation aborts the entire transaction without writing partial changes.
    for patch in op['patches']:
        target=patch['target']
        if target=='order':
            plates=data['days'][op['day']]['plates']
            expect([p['id'] for p in plates],patch['new'])
            by_id={p['id']:p for p in plates}
            plates[:]=[by_id[pid] for pid in patch['old']]
            continue
        if target=='tool':
            expect(data['tools'][patch['index']],patch['new'])
            data['tools'][patch['index']]=patch['old'];continue
        if target in ('cell','field'):
            plate=next((p for p in data['days'][op['day']]['plates'] if p['id']==patch['id']),None)
            if plate is None:raise ConflictError('다른 PC에서 판을 삭제했습니다. 되돌리지 않았습니다.')
            if target=='cell':
                expect(len(plate['cells']),patch['count'])
                expect(plate['cells'][patch['index']],patch['new'])
                plate['cells'][patch['index']]=patch['old']
            else:
                expect(plate.get(patch['field']),patch['new'])
                plate[patch['field']]=copy.deepcopy(patch['old'])
            continue
        items=data['notes'] if target=='notes' else data['days'][op['day']].setdefault(target,[])
        current=next((x for x in items if x['id']==patch['id']),None)
        expect(current,patch['new'])
        if current is not None:items.remove(current)
        if patch['old'] is not None:items.insert(min(patch['position'],len(items)),copy.deepcopy(patch['old']))

def apply_op(data, op):
    kind = op['kind']
    if kind=='undo':
        apply_undo(data,op);return
    if kind == 'day':
        day = data['days'].setdefault(op['day'], new_day())
        if not day.get('manual_plates'):
            # One-time cleanup of unused trailing default plates only.
            while len(day['plates']) > 1:
                last=day['plates'][-1]
                if last['put'] or last.get('washed') or any(last['cells']) or len(last['cells']) != 15:break
                day['plates'].pop()
            day['manual_plates']=True
        return
    if kind == 'tool':
        expect(data['tools'][op['index']], op['old'])
        data['tools'][op['index']] = op['value']; return
    if kind == 'clear_notes':
        expect(data['notes'],op['old'])
        data['notes']=[];return
    if kind == 'note':
        ident=op.get('note_id') or str(uuid.uuid4())
        existing=next((n for n in data['notes'] if n['id']==ident),None)
        if existing:
            expect((existing['dept'],existing['text']),(op['dept'],op['text']))
            return
        data['notes'].append({'id':ident,'dept':op['dept'],'text':op['text'],'time':now()});return
    day = data['days'][op['day']]
    if kind == 'reorder':
        plates=day['plates'];ids=[p['id'] for p in plates]
        expect(ids,op['old'])
        if len(op['order'])!=len(ids) or set(op['order'])!=set(ids):
            raise RuntimeError('판 목록이 변경되어 순서를 저장하지 않았습니다.')
        by_id={p['id']:p for p in plates}
        plates[:]=[by_id[pid] for pid in op['order']]
        return
    if kind == 'add':
        number = max((p['number'] for p in day['plates'] if p.get('type') not in ('complete','cnt')), default=0) + 1
        day['plates'].append({'id': str(uuid.uuid4()), 'number': number, 'cells': [''] * 15, 'put': ''}); return
    if kind == 'add_cnt':
        existing=[p['number'] for p in day['plates'] if p.get('type')=='cnt']
        number=day.get('next_cnt',min(existing)-1 if existing else 30)
        if number<1:raise RuntimeError('CNT1까지 모두 추가했습니다.')
        day['plates'].append({'id':str(uuid.uuid4()), 'type':'cnt', 'number':number, 'cells':['']*10, 'put':''})
        day['next_cnt']=number-1
        return
    if kind == 'add_complete':
        day['plates'].append({'id':str(uuid.uuid4()), 'type':'complete', 'number':0, 'cells':['']*10, 'put':''});return
    if kind == 'restore':
        record=next((r for r in day.get('deleted',[]) if r['id']==op['record']),None)
        if record is None: raise RuntimeError('이미 복구된 항목입니다.')
        if record['kind']=='delete':
            if any(p['id']==record['plate']['id'] for p in day['plates']):raise RuntimeError('같은 판이 이미 있습니다.')
            day['plates'].insert(min(record['position'],len(day['plates'])),copy.deepcopy(record['plate']))
        else:
            target=next((p for p in day['plates'] if p['id']==record['plate_id']),None)
            if target is None:raise RuntimeError('먼저 삭제된 판을 복구해주세요.')
            if record['kind']=='remove_row':
                expect(len(target['cells']),record['count']-1)
                target['cells'].append(record['value'])
            else:
                for i,value in record['values']:
                    if i>=len(target['cells']):raise RuntimeError('먼저 삭제된 칸을 복구해주세요.')
                    expect(target['cells'][i],'')
                for i,value in record['values']:target['cells'][i]=value
        day['deleted'].remove(record)
        return
    plate = next((p for p in day['plates'] if p['id'] == op['plate']), None)
    if plate is None: raise RuntimeError('이 판은 다른 PC에서 삭제되었습니다.')
    if kind == 'cells':
        for index, old, value in op['changes']:
            if index >= len(plate['cells']): raise RuntimeError('칸 구성이 변경되었습니다.')
            expect(plate['cells'][index], old)
        cleared=[[i,old] for i,old,value in op['changes'] if old and not value]
        if cleared:remember_deleted(day,plate,'cells',values=cleared)
        for index, old, value in op['changes']: plate['cells'][index] = value
    elif kind == 'put':
        expect(plate['put'], op['old'])
        plate['put'] = now() if op['value'] else ''
    elif kind == 'washed':
        expect(plate.get('washed'), op['old'])
        plate['washed'] = now() if op['value'] else None
    elif kind == 'delete':
        expect(plate,op['old'])
        remember_deleted(day,plate,'delete',plate=copy.deepcopy(plate),position=day['plates'].index(plate))
        day['plates'].remove(plate)
    elif kind == 'row': plate['cells'].append('')
    elif kind == 'remove_row':
        expect(len(plate['cells']), op['count'])
        if len(plate['cells']) <= 1:
            raise RuntimeError('최소 한 칸은 남겨야 합니다.')
        expect(plate['cells'][-1], op['old'])
        remember_deleted(day,plate,'remove_row',count=len(plate['cells']),value=plate['cells'][-1])
        plate['cells'].pop()
    else: raise RuntimeError('알 수 없는 작업입니다.')

def remember_deleted(day, target, kind, **details):
    day.setdefault('deleted',[]).append(dict(id=str(uuid.uuid4()),time=now(),title=plate_title(target),plate_id=target['id'],kind=kind,**details))

def find_plate_title(data,day,pid):
    plate=next((p for p in data.get('days',{}).get(day,{}).get('plates',[]) if p['id']==pid),None)
    return plate_title(plate) if plate else '판 정보 확인 필요'

def describe_operation(op,data):
    kind=op['kind'];day=op.get('day') or ''
    title=op.get('_plate_title') or find_plate_title(data,day,op.get('plate'))
    if kind=='cells':return day+' '+title+'\n'+'\n'.join(str(i+1)+'번째 칸: '+value for i,old,value in op['changes'])
    if kind=='tool':return str(op['index']+1)+'호기 공구대: '+op['value']
    if kind=='note':return '부서 메모 ('+op['dept']+'): '+op['text']
    names={'reorder':'판 순서 변경','washed':'포장완료 표시 변경','put':'투입 표시 변경','delete':'판 삭제','row':'칸 추가','remove_row':'마지막 칸 삭제','add':'판 추가','add_cnt':'CNT판 추가','add_complete':'완료판 추가','undo':'되돌리기','clear_notes':'부서 메모 비우기','delete_day':'날짜 일보 삭제','restore':'삭제 내용 복구','day':'날짜 열기','purge_backups':'백업 정리','purge_legacy':'이전 통합 백업 정리'}
    return day+' '+(title+' · ' if op.get('plate') else '')+names.get(kind,kind)

class RoundedButton(tk.Canvas):
    def __init__(self,parent,text,command,bg=BUTTON,fg=TEXT,activebackground='#303740',activeforeground=TEXT,padx=6,pady=3,font=('맑은 고딕',9),**kw):
        self.options=dict(text=text,command=command,bg=bg,fg=fg,activebackground=activebackground,activeforeground=activeforeground,padx=padx,pady=pady,font=font)
        self.hover=False
        super().__init__(parent,bg=parent.cget('bg'),highlightthickness=0,borderwidth=0,takefocus=1,cursor='hand2')
        self.bind('<Configure>',lambda e:self.draw())
        self.bind('<Enter>',lambda e:self.set_hover(True));self.bind('<Leave>',lambda e:self.set_hover(False))
        self.bind('<ButtonRelease-1>',lambda e:self.invoke() if 0<=e.x<self.winfo_width() and 0<=e.y<self.winfo_height() else None)
        self.bind('<Return>',lambda e:self.invoke());self.bind('<space>',lambda e:self.invoke())
        self.bind('<FocusIn>',lambda e:self.draw());self.bind('<FocusOut>',lambda e:self.draw())
        self.resize_button()
    def set_hover(self,value):self.hover=value;self.draw()
    def invoke(self):
        command=self.options['command']
        if command:command()
        return 'break'
    def configure(self,cnf=None,**kw):
        if cnf:kw.update(cnf)
        for key in list(kw):
            if key in self.options:self.options[key]=kw.pop(key)
        if kw:super().configure(**kw)
        self.resize_button()
    config=configure
    def resize_button(self):
        font=tkfont.Font(font=self.options['font'])
        super().configure(width=font.measure(self.options['text'])+2*self.options['padx']+4,height=font.metrics('linespace')+2*self.options['pady']+2)
        self.draw()
    def draw(self):
        self.delete('all')
        super().configure(bg=self.master.cget('bg'))
        w=self.winfo_width();h=self.winfo_height();r=min(6,w/2,h/2)
        fill=self.options['activebackground'] if self.hover else self.options['bg']
        points=[r,1,w-r,1,w-1,1,w-1,r,w-1,h-r,w-1,h-1,w-r,h-1,r,h-1,1,h-1,1,h-r,1,r,1,1]
        self.create_polygon(points,smooth=True,splinesteps=12,fill=fill,outline=BLUE if self.focus_get()==self else fill)
        self.create_text(w/2,h/2,text=self.options['text'],fill=self.options['activeforeground'] if self.hover else self.options['fg'],font=self.options['font'])

class RoundedCard(tk.Frame):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)
        self.corners=[]
        for right,bottom in ((False,False),(True,False),(False,True),(True,True)):
            c=tk.Canvas(self,width=8,height=8,highlightthickness=0,borderwidth=0,bg=parent.cget('bg'))
            c.place(relx=1 if right else 0,rely=1 if bottom else 0,anchor=('s' if bottom else 'n')+('e' if right else 'w'))
            self.corners.append((c,right,bottom))
        self.after_idle(self.paint_corners)
    def configure(self,cnf=None,**kw):
        super().configure(cnf,**kw)
        if hasattr(self,'corners'):self.paint_corners()
    config=configure
    def paint_corners(self):
        for c,right,bottom in self.corners:
            c.delete('all');x=-8 if right else 0;y=-8 if bottom else 0
            c.create_oval(x,y,x+16,y+16,fill=self.cget('bg'),outline=self.cget('bg'))
            c.tk.call('raise',c._w)

def clipboard_rows(text):
    rows=list(csv.reader(io.StringIO(text),delimiter='\t'))
    values=[' '.join(c.strip() for c in row if c.strip()) for row in rows]
    # A terminal line separator is not an additional company; interior blanks stay rows.
    if text.endswith(('\n','\r')) and values and not values[-1]:values.pop()
    return values

class App(tk.Tk):
    def __init__(self):
        if os.name=='nt':
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Morun.WashLog.Desktop')
            except (AttributeError,OSError):pass
        super().__init__()
        self.app_icons=[tk.PhotoImage(master=self,data=encoded) for encoded in APP_ICON_PNGS]
        self.iconphoto(True,*self.app_icons)
        self.title('세척일보 · 공유 작업장'); self.geometry('320x940'); self.minsize(280, 650); self.configure(bg=BG)
        try: self.cfg = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        except (OSError, ValueError): self.cfg = {}
        self.data = None; self.cards = {}; self.popups={};self.popup_close_pending=set();self.edit = None; self.busy = 0
        self.day = date.today().isoformat(); self.size = max(9, min(18, self.cfg.get('size', 10)))
        self.jobs = queue.Queue(); self.results = queue.Queue(); self.stop = threading.Event()
        self.pending_copy=None;self.recovery_window=None;self.undo_history=[];self.pending_updates={};self.busy_since=None;self.closing=False
        self.online=False;self.tool_drafts={};self.failed_operations=[];self.manager=None;self.management_dates=[]
        try:self.tool_drafts={int(k):v for k,v in json.loads((CONFIG_DIR/'공구대_미저장.json').read_text(encoding='utf-8'))['drafts'].items()}
        except (OSError,ValueError,KeyError):pass
        try:self.failed_operations=json.loads((CONFIG_DIR/'저장확인필요.json').read_text(encoding='utf-8'))
        except (OSError,ValueError):pass
        self.connected = False; self.connecting=False; self.store = None; self.active_folder = ''
        self._update_error_sequence = 0
        self.build(); self.protocol('WM_DELETE_WINDOW', self.close)
        self.data=initial();self.data['days'][self.day]=new_day();self.render()
        self.status.set('화면 미리보기 · 공유폴더 연결 중 · 아직 저장되지 않음')
        threading.Thread(target=self.worker, daemon=True).start()
        self.after(100, self.drain)
        self.after(1000,self.check_delay)
        self.after(150, self.dark_titlebar)
        self.after(200,lambda:self.connect(self.cfg.get('folder') or DEFAULT_FOLDER))
        self._update_bridge = CompanionUpdateBridge(self, WashLogUpdateSave(self))
        self._window_state = CompanionWindowState(self, 'wash-log')
        try: WashLogUpdateSave.restore_draft(self)
        except (OSError, ValueError): self.note_feedback.set('업데이트 전 메모 보관 파일을 확인해 주세요.')
    def report_callback_exception(self,exc,val,tb):
        self._update_error_sequence += 1
        import traceback
        details=''.join(traceback.format_exception(exc,val,tb))
        try:
            CONFIG_DIR.mkdir(parents=True,exist_ok=True)
            log=CONFIG_DIR/'화면오류.log'
            old=log.read_text(encoding='utf-8') if log.exists() else ''
            log.write_text((old+'\n'+now()+'\n'+details)[-200000:],encoding='utf-8')
        except OSError:pass
        try:
            self.cancel_plate_drag()
            if getattr(self,'note_pending',None) and not any(op.get('note_id')==self.note_pending for op in self.pending_updates.values()):
                self.note_pending=None
                self.note_feedback.set('전송 결과 확인 필요 · 입력 보존 · 다시 Enter로 확인')
            if self.edit and self.edit['saving'] and not any(op.get('edit_id')==self.edit['id'] for op in self.pending_updates.values()):
                self.edit['saving']=False;self.edit['widget'].configure(state='normal')
            self.status.set('화면 처리 오류 · 입력 보존 · 관리 → 재연결 · '+str(val))
        except Exception:pass
    def dark_titlebar(self):
        if os.name != 'nt':return
        try:
            import ctypes
            from ctypes import wintypes
            user=ctypes.windll.user32;dwm=ctypes.windll.dwmapi
            user.GetParent.argtypes=[wintypes.HWND];user.GetParent.restype=wintypes.HWND
            dwm.DwmSetWindowAttribute.argtypes=[wintypes.HWND,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD]
            hwnd=user.GetParent(self.winfo_id())
            enabled=ctypes.c_int(1)
            result=dwm.DwmSetWindowAttribute(hwnd,20,ctypes.byref(enabled),ctypes.sizeof(enabled))
            if result:dwm.DwmSetWindowAttribute(hwnd,19,ctypes.byref(enabled),ctypes.sizeof(enabled))
        except Exception:pass
    def label(self, parent, text, **kw):
        return tk.Label(parent, text=text, bg=kw.pop('bg', PANEL), fg=kw.pop('fg', TEXT), **kw)
    def button(self, parent, text, cmd):
        accent = text in ('투입', '메모 등록', '＋ 판 추가', '＋ 완료판 추가', '＋ CNT판 추가', '연결 / 이 PC에 적용')
        return RoundedButton(parent,text,cmd,bg=ACCENT if accent else BUTTON,fg=BLUE if accent else TEXT,activebackground='#304b65' if accent else '#303740',activeforeground='#ffffff')
    def build(self):
        self.option_add('*Font', ('맑은 고딕', 9))
        self.option_add('*Entry.background', FIELD)
        self.option_add('*Entry.foreground', TEXT)
        self.option_add('*Entry.insertBackground', TEXT)
        self.option_add('*Entry.selectBackground', SELECT)
        self.option_add('*Entry.selectForeground', '#ffffff')
        self.option_add('*Entry.relief', 'flat')
        self.option_add('*Entry.highlightThickness', 0)
        self.option_add('*Entry.borderWidth', 0)
        self.option_add('*Text.highlightThickness', 0)
        self.option_add('*Text.borderWidth', 0)
        self.option_add('*Entry.highlightBackground', LINE)
        self.option_add('*Entry.highlightColor', ACCENT)
        self.option_add('*TCombobox*Listbox.background', FIELD)
        self.option_add('*TCombobox*Listbox.foreground', TEXT)
        self.option_add('*TCombobox*Listbox.selectBackground', SELECT)
        style = ttk.Style(self); style.theme_use('clam')
        style.configure('.', font=('맑은 고딕',9), foreground=TEXT, background=PANEL, bordercolor=LINE, lightcolor=LINE, darkcolor=LINE, focuscolor=LINE)
        style.configure('TCombobox', fieldbackground=FIELD, background=BUTTON, foreground=TEXT, arrowcolor=TEXT, bordercolor=LINE, lightcolor=LINE, darkcolor=LINE, insertcolor=TEXT, relief='flat')
        style.map('TCombobox', fieldbackground=[('readonly',FIELD)], foreground=[('readonly',TEXT)], selectbackground=[('!disabled',SELECT)])
        style.configure('Vertical.TScrollbar', background=LINE, troughcolor=FIELD, borderwidth=0, bordercolor=FIELD, lightcolor=LINE, darkcolor=LINE, arrowcolor=MUTED, arrowsize=12)

        style.configure('TNotebook', background=BG, borderwidth=0, bordercolor=BG, lightcolor=BG, darkcolor=BG)
        style.configure('TNotebook.Tab', background=PANEL, foreground=MUTED, bordercolor=BG, lightcolor=BG, darkcolor=BG, focuscolor=PANEL, padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', ACCENT)], foreground=[('selected', TEXT)])
        style.configure('Treeview', background=FIELD, fieldbackground=FIELD, borderwidth=0, bordercolor=FIELD, lightcolor=FIELD, darkcolor=FIELD, foreground=TEXT, font=('맑은 고딕', self.size), rowheight=tkfont.Font(font=('맑은 고딕',self.size)).metrics('linespace')+2)
        style.layout('Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])
        style.configure('Treeview.Heading', background=HEADER, foreground=BLUE, font=('맑은 고딕',9), relief='flat', borderwidth=1, bordercolor=LINE, lightcolor=LINE, darkcolor=LINE)
        style.map('Treeview.Heading', background=[('active',HEADER)])
        style.map('Treeview', background=[('selected', SELECT)], foreground=[('selected', '#ffffff')])
        bar=tk.Frame(self,bg=BG);bar.pack(fill='x',padx=3,pady=3)
        self.datevar=tk.StringVar(value=self.day)
        date_entry=tk.Entry(bar,textvariable=self.datevar,width=11,font=('맑은 고딕',9))
        header_widgets=[date_entry]
        for text,command in [('열기',self.change_day),('오늘',self.today),('세척일보',lambda:self.show_page('daily')),('관리',self.show_management)]:
            button=self.button(bar,text,command);button.configure(padx=2,font=('맑은 고딕',8));header_widgets.append(button)
        def layout_header(event=None):
            width=event.width if event else bar.winfo_width()
            split=sum(w.winfo_reqwidth()+4 for w in header_widgets)>width
            for i,w in enumerate(header_widgets):
                row=1 if split and i>=3 else 0
                col=i-3 if row else i
                w.grid(row=row,column=col,padx=2,pady=1,sticky='w')
        bar.bind('<Configure>',layout_header)
        self.after_idle(layout_header)
        self.pages=tk.Frame(self,bg=BG);self.pages.pack(fill='both',expand=True,padx=3)
        self.daily=tk.Frame(self.pages,bg=BG);self.settings=tk.Frame(self.pages,bg=BG)
        self.daily.pack(fill='both',expand=True)
        self.tools_visible=bool(self.cfg.get('tools_visible',True))
        toolbar=tk.Frame(self.daily,bg=BG);toolbar.pack(fill='x',pady=(0,2))
        self.tool_toggle=self.button(toolbar,'',self.toggle_tools)
        self.tool_toggle.pack(side='left',fill='x',expand=True)
        toolframe = tk.Frame(self.daily, bg=PANEL)
        self.toolframe=toolframe
        self.tool_toggle.configure(text='공구대 접기 ▴' if self.tools_visible else '공구대 펼치기 ▾')
        if self.tools_visible:toolframe.pack(fill='x',pady=(0,2))
        self.toolvars=[]; self.tool_entries=[]
        for i in range(9):
            part=tk.Frame(toolframe,bg=PANEL); part.grid(row=i,column=0,sticky='ew',padx=5,pady=0)
            toolframe.columnconfigure(0,weight=1)
            self.label(part,f'{i+1}호기',font=('맑은 고딕',9)).pack(side='left')
            var=tk.StringVar(); ent=tk.Entry(part,textvariable=var,bg=PANEL,fg=TEXT,insertbackground=TEXT,relief='flat',highlightthickness=0,font=('맑은 고딕',9),width=1)
            ent.pack(side='left',fill='x',expand=True,padx=5)
            ent.bind('<KeyRelease>',lambda e,j=i:self.after_idle(lambda:self.capture_tool(j)))
            ent.bind('<FocusIn>',lambda e,j=i:self.tool_start(j))
            ent.bind('<FocusOut>',lambda e,j=i:self.tool_end(j))
            ent.bind('<Return>',lambda e:self.daily.focus_set())
            self.toolvars.append(var); self.tool_entries.append(ent)
        self.tool_old={}
        panes=tk.Frame(self.daily,bg=BG); panes.pack(fill='both',expand=True)
        self.work_panes=panes
        actions=tk.Frame(panes,bg=BG);actions.pack(side='bottom',fill='x',padx=2,pady=(2,3))
        middle=tk.Frame(panes,bg=BG);middle.pack(fill='both',expand=True)
        self.canvas=tk.Canvas(middle,bg=BG,highlightthickness=0)
        scroll=ttk.Scrollbar(middle,orient='vertical',command=self.canvas.yview);scroll.pack(side='right',fill='y')
        self.canvas.pack(side='left',fill='both',expand=True);self.canvas.configure(yscrollcommand=scroll.set)
        self.gridframe=tk.Frame(self.canvas,bg=BG);self.window=self.canvas.create_window((0,0),window=self.gridframe,anchor='nw')
        self.gridframe.bind('<Configure>',self.update_plate_scroll)
        self.canvas.bind('<Configure>',self.resize_plate_canvas)
        self.bind_all('<MouseWheel>',self.wheel)
        self.bind_all('<Control-z>',self.undo_last)
        self.bind_all('<Control-Z>',self.undo_last)
        self.bind_all('<Escape>',lambda e:(self.cancel_plate_drag(),self.deselect()))
        self.bind_all('<Button-1>',self.outside_click,add='+')
        self.bind_all('<ButtonRelease-1>',self.finish_lost_plate_drag,add='+')
        self.bind('<FocusOut>',lambda e:self.after(60,self.cancel_unfocused_plate_drag),add='+')
        self.bind('<Unmap>',lambda e:self.cancel_plate_drag() if e.widget==self else None,add='+')
        for col,(label,kind) in enumerate([('＋ 판 추가','add'),('＋ 완료판 추가','add_complete'),('＋ CNT판 추가','add_cnt')]):
            actions.columnconfigure(col,weight=1,uniform='add_buttons')
            button=self.button(actions,label,lambda k=kind:self.send({'kind':k}))
            button.configure(font=('맑은 고딕',8),padx=2)
            button.grid(row=0,column=col,sticky='ew',padx=1)
        memo=tk.Frame(panes,bg=PANEL);memo.pack(side='bottom',fill='x',before=actions,padx=2,pady=(2,3))
        self.notes_expanded=False
        self.note_notice=self.button(memo,'채팅 ▴',self.open_notes)
        self.note_notice.pack(fill='x')
        self.note_preview=self.label(memo,'등록된 메모가 없습니다.',anchor='w',font=('맑은 고딕',9),height=1)
        self.note_preview.pack(fill='x',padx=6,pady=(2,4))
        self.note_preview.bind('<Button-1>',lambda e:self.open_notes())
        self.note_body=tk.Frame(memo,bg=PANEL,height=270)
        self.note_body.pack_propagate(False)
        memo=self.note_body
        memo_head=tk.Frame(memo,bg=PANEL);memo_head.pack(fill='x',padx=8,pady=3)
        self.button(memo_head,'메모 비우기',self.clear_notes).pack(side='right')
        compose_host=tk.Frame(memo,bg=PANEL);compose_host.pack(side='bottom',fill='x')
        history=tk.Frame(memo,bg=PANEL);history.pack(fill='both',expand=True,padx=8)
        self.notes=tk.Text(history,height=3,width=1,bg=PANEL,fg=TEXT,relief='flat',wrap='word',font=('맑은 고딕',10),state='disabled')
        note_scroll=ttk.Scrollbar(history,orient='vertical',command=self.notes.yview);note_scroll.pack(side='right',fill='y')
        self.notes.configure(yscrollcommand=note_scroll.set);self.notes.pack(side='left',fill='both',expand=True)
        compose=tk.Frame(compose_host,bg=PANEL);compose.pack(fill='x',padx=8,pady=5)
        self.dept=tk.StringVar(value='포장부' if self.cfg.get('dept') in ('포장','포장부') else '생산부')
        ttk.Combobox(compose,textvariable=self.dept,values=['생산부','포장부'],state='readonly',width=8).pack(side='left',padx=(0,5))
        self.button(compose,'메모 등록',self.post_note).pack(side='right')
        self.note_input=tk.Text(compose_host,undo=True,autoseparators=True,maxundo=100,height=3,width=1,bg=FIELD,fg=TEXT,insertbackground=TEXT,relief='flat',highlightthickness=1,highlightbackground=LINE,highlightcolor=ACCENT,font=('맑은 고딕',10));self.note_input.pack(fill='x',padx=8,pady=(0,5))
        self.note_feedback=tk.StringVar(value='')
        self.note_pending=None;self.note_retry=None
        feedback_label=self.label(compose_host,'',textvariable=self.note_feedback,fg=MUTED,font=('맑은 고딕',8),anchor='w')
        self.note_feedback.trace_add('write',lambda *_:feedback_label.pack(fill='x',padx=8,pady=(0,3)) if self.note_feedback.get() else feedback_label.pack_forget())
        self.note_input.bind('<Return>',self.note_enter)
        self.note_input.bind('<FocusIn>',lambda e:self.mark_notes_read())
        self.notes.bind('<FocusIn>',lambda e:self.mark_notes_read())
        self.status=tk.StringVar(value='경로 설정에서 사용할 데이터 폴더를 선택해주세요.')
        self.label(self,textvariable=self.status,text='',bg=BG,fg='#99c8cd',anchor='w',wraplength=250,justify='left',font=('맑은 고딕',9)).pack(fill='x',padx=12,pady=(0,7))
        self.label(self.settings,'이 PC의 공유 데이터 폴더',bg=BG,font=('맑은 고딕',11,'bold')).pack(anchor='w',padx=10,pady=(25,10))
        self.label(self.settings,'각 PC에서 같은 실제 폴더를 지정하세요. 드라이브 문자나 경로 표기는 달라도 됩니다.',bg=BG,wraplength=245,justify='left').pack(anchor='w',padx=10)
        self.pathvar=tk.StringVar(value=self.cfg.get('folder') or DEFAULT_FOLDER)
        tk.Entry(self.settings,textvariable=self.pathvar,font=('맑은 고딕',11)).pack(fill='x',padx=10,pady=15)
        row=tk.Frame(self.settings,bg=BG);row.pack(fill='x',padx=10)
        self.button(row,'폴더 선택',self.browse).pack(fill='x',pady=3)
        self.button(row,'연결 / 이 PC에 적용',lambda:self.connect(self.pathvar.get().strip())).pack(fill='x',pady=3)
        self.button(row,'지후니우스 기본 경로',self.use_default).pack(fill='x',pady=3)
        self.button(row,'삭제 내역 / 복구',self.show_recovery).pack(fill='x',pady=3)
        self.connection=tk.StringVar(value='미연결 · 기본 경로: 지후니우스 인수인계 저장 위치 아래 세척일보')
        self.label(self.settings,text='',textvariable=self.connection,bg=BG,justify='left',wraplength=245).pack(anchor='w',padx=10,pady=20)
        self.label(self.settings,'처음 시험할 때는 빈 테스트 폴더를 지정하세요.\n프로그램이 해당 폴더에 전용 데이터 파일을 만듭니다.\n3대 모두 아래에 표시되는 데이터 ID가 같으면 같은 일보입니다.\n같은 실행파일을 사용해도 PC별 경로 설정은 따로 저장됩니다.\n삭제 복구는 현재 선택한 날짜 기준입니다.\n공구대·메모·날짜별 일보가 분리 저장됩니다.\n날짜 삭제와 백업 정리는 상단 관리에서 가능합니다.',bg=BG,justify='left',wraplength=245).pack(anchor='w',padx=10)
    def toggle_tools(self):
        self.tools_visible=not self.tools_visible
        if self.tools_visible:
            self.toolframe.pack(fill='x',pady=(0,2),before=self.work_panes)
        else:
            self.daily.focus_set()
            self.toolframe.pack_forget()
        self.tool_toggle.configure(text='공구대 접기 ▴' if self.tools_visible else '공구대 펼치기 ▾')
        self.cfg['tools_visible']=self.tools_visible
        self.save_config()
    def show_page(self,name):
        self.daily.pack_forget();self.settings.pack_forget()
        (self.daily if name=='daily' else self.settings).pack(fill='both',expand=True)
    def resize_plate_canvas(self,event):
        self.canvas.itemconfigure(self.window,width=event.width)
        self.update_plate_scroll()
    def update_plate_scroll(self,event=None):
        # Keep the scrollable region at least as tall as the viewport.
        # A shorter region lets Tk shift the content below the top edge.
        box=self.canvas.bbox(self.window)
        if not box:return
        viewport=max(1,self.canvas.winfo_height())
        content=max(1,box[3])
        plates=self.data['days'].get(self.day,{}).get('plates',[]) if self.data else []
        if plates and plates[-1]['id'] in self.cards:
            frame=self.cards[plates[-1]['id']]['frame']
            content+=max(frame.winfo_height(),frame.winfo_reqheight())+6
        self.canvas.configure(scrollregion=(0,0,max(1,self.canvas.winfo_width()),max(content,viewport)))
        if content<=viewport:self.canvas.yview_moveto(0)
    def reveal_last_plate(self):
        plates=self.data['days'].get(self.day,{}).get('plates',[]) if self.data else []
        if not plates or plates[-1]['id'] not in self.cards:return
        self.update_idletasks();self.update_plate_scroll()
        frame=self.cards[plates[-1]['id']]['frame']
        region=self.canvas.cget('scrollregion').split()
        if len(region)==4 and float(region[3])>0:
            self.canvas.yview_moveto(max(0,frame.winfo_y()-3)/float(region[3]))
    def wheel(self,e):
        drag=getattr(self,'plate_drag',None)
        if drag and drag['active']:
            self.canvas.yview_scroll(-int(e.delta/120),'units')
            self.refresh_plate_drag_preview()
            return 'break'
        w=e.widget
        while w is not None:
            if w==self.gridframe or w==self.canvas:
                self.update_plate_scroll()
                if self.canvas.yview()!=(0.0,1.0):
                    self.canvas.yview_scroll(-int(e.delta/120),'units')
                return 'break'
            w=getattr(w,'master',None)
    def save_config(self):
        CONFIG_DIR.mkdir(parents=True,exist_ok=True)
        self.cfg.update(size=self.size,dept=self.dept.get())
        atomic_json(CONFIG_FILE,self.cfg)
    def browse(self):
        folder=filedialog.askdirectory(title='세척일보 공용 데이터 폴더')
        if folder:self.pathvar.set(folder)
    def use_default(self):
        self.pathvar.set(DEFAULT_FOLDER);self.connect(DEFAULT_FOLDER)
    def connect(self,folder):
        if self.busy:
            messagebox.showinfo('작업 중','현재 작업이 끝나거나 연결 대기가 중단된 뒤 다시 눌러주세요.');return
        if not folder:return
        if self.connected and folder!=self.active_folder and (self.edit or self.tool_drafts):
            messagebox.showinfo('미저장 입력','업체명과 공구대 입력을 저장하거나 취소한 뒤 다른 경로로 변경해주세요.');return
        self.connecting=True
        self.cancel_plate_drag()
        self.busy_since=time.monotonic();self.busy+=1
        self.jobs.put(('connect',folder,self.day));self.status.set('폴더 연결 확인 중… 응답 지연 시 자동으로 다시 확인합니다.')
    def reconnect(self):
        self.connect(self.active_folder or self.pathvar.get().strip())
    def worker(self):
        folder=None;view_day=self.day;database_id=None;retry_at=0;poll_count=0
        initial_target=None;failures=0;client=DiskClient(self.stop)
        def request(target,kind,arg,day):
            try:
                for attempt in range(3):
                    result=client.request(target,kind,arg,day)
                    if result[0]!='busy' or kind=='poll' or attempt==2:return result
                    # Busy means the lock was never acquired: retrying is safe.
                    # Timeouts / other errors might have committed, so never replay.
                    self.results.put(('waiting','다른 PC 저장이 끝나기를 기다리는 중…',None))
                    if self.stop.wait(.4):return ('cancelled','프로그램 종료 중',None)
            except Exception as exc:
                client.close()
                return ('error','공유폴더 처리 오류: '+str(exc),None)
        try:
            while not self.stop.is_set():
                try:job=self.jobs.get(timeout=3)
                except queue.Empty:
                    if time.monotonic()<retry_at or (not folder and not initial_target):continue
                    poll_count+=1
                    target=folder or initial_target[0]
                    requested_day=view_day if folder else initial_target[1]
                    auto_kind='poll' if folder else 'connect'
                    result=request(target,auto_kind,{'catalog':poll_count%20==0},requested_day)
                    if self.stop.is_set():return
                    state,value,receipt=result
                    if state=='ok':
                        if folder and value['id']!=database_id:
                            self.results.put(('offline','공유 데이터 ID가 변경되었습니다. 관리에서 경로를 확인하고 재연결해주세요.',None))
                            folder=None;initial_target=None;continue
                        retry_at=0;failures=0
                        if auto_kind=='connect':
                            folder=target;database_id=value['id'];view_day=requested_day;initial_target=None
                            self.results.put(('auto_connect',value,target))
                        else:self.results.put(('poll',value,None))
                    elif state=='busy':
                        retry_at=time.monotonic()+2
                        self.results.put(('waiting',value,None))
                    else:
                        failures+=1;retry_at=time.monotonic()+min(10,2*failures)
                        self.results.put(('offline' if failures>=3 else 'recovering',value,None))
                    continue
                kind,arg,requested_day=job
                if kind!='connect' and folder is None:
                    self.results.put(('operation_error','연결 대상을 확인하지 못했습니다. 재연결 후 저장해주세요.',job));continue
                target=arg if kind=='connect' else folder
                result=request(target,kind,arg,requested_day)
                if self.stop.is_set():return
                state,value,receipt=result
                if state=='ok':
                    retry_at=0;failures=0
                    if kind=='connect':
                        folder=target;database_id=value['id'];view_day=requested_day;initial_target=None
                        self.results.put(('connect',value,arg))
                    else:
                        if arg['kind']=='day':view_day=arg['day']
                        extra=dict(arg);extra['_undo']=receipt
                        self.results.put(('saved',value,extra))
                elif state=='conflict':
                    if receipt is not None and receipt['id']!=database_id:
                        folder=None;initial_target=None
                        self.results.put(('conflict',('공유 데이터 ID가 변경되었습니다. 경로 확인 후 재연결해주세요.',None),job))
                        self.results.put(('offline','공유 데이터 ID 변경 · 경로 확인 후 재연결 필요',None))
                    else:self.results.put(('conflict',(value,receipt),job))
                elif state=='busy':
                    if kind=='connect' and not folder:
                        initial_target=(target,requested_day);retry_at=time.monotonic()+2
                    self.results.put(('rejected',value,job))
                elif kind!='connect' and state in ('rejected','invalid','error'):
                    self.results.put(('operation_error',value,job))
                else:
                    retry_at=time.monotonic()+2
                    if kind=='connect' and not folder:initial_target=(target,requested_day)
                    # Keep the previously opened folder after a failed path switch.
                    # Existing work is never automatically sent to a new location.
                    self.results.put(('error',value,job))
        finally:
            client.close()
    def drain(self):
        try:
            while True:
                kind,value,extra=self.results.get_nowait()
                if kind=='connect' or (kind in ('error','conflict','rejected','operation_error') and extra[0]=='connect'):
                    self.connecting=False
                if kind in ('connect','saved','error','conflict','rejected','operation_error'):self.busy=max(0,self.busy-1)
                if not self.busy:self.busy_since=None
                if kind=='saved':self.pending_updates.pop(extra.get('_job_id'),None)
                if kind in ('error','conflict','rejected','operation_error'):
                    _diagnostic_error(value[0] if kind=='conflict' else value,str(extra[0]))
                    self._update_error_sequence += 1
                    self.pending_copy=None;self.next_cell=None
                    op=extra[1] if extra[0]=='update' else None
                    if op and op['kind']=='note' and op.get('note_id')==self.note_pending:
                        self.note_pending=None
                        self.note_feedback.set('전송 확인 필요 · 입력 보존 · 연결 후 다시 Enter')
                    if op:
                        failed=self.pending_updates.pop(op.get('_job_id'),None)
                        if failed:self.failed_operations.append(failed)
                    if self.edit and op and op.get('edit_id')==self.edit['id']:
                        self.edit['saving']=False;self.edit['widget'].configure(state='normal')
                    self.datevar.set(self.day)
                    if kind=='conflict':
                        message,latest=value
                        if latest is not None and self.data and latest['id']!=self.data['id']:
                            latest=None;self.online=False
                            message='공유 데이터 ID가 변경되었습니다. 경로 확인 후 재연결해주세요.'
                        if latest is not None:self.data=latest;self.online=True
                        if op and op['kind']=='tool' and latest is not None:
                            i=op['index'];current=self.data['tools'][i]
                            draft=self.tool_drafts.get(i)
                            if draft and messagebox.askyesno('공구대 수정 충돌','최신 공구대 내용:\n'+current+'\n\n내 입력:\n'+draft['value']+'\n\n내 입력으로 다시 저장할까요?',default='no'):
                                draft['old']=current;self.save_tool_drafts();self.send({'kind':'tool','index':i,**draft})
                        elif self.edit and op and op.get('edit_id')==self.edit['id']:
                            edit=self.edit
                            plate=next((p for p in self.data['days'].get(self.day,{}).get('plates',[]) if p['id']==edit['plate']),None)
                            if latest is not None and plate and edit['index']<len(plate['cells']):
                                current=plate['cells'][edit['index']]
                                comparison='최신 내용:\n'+(current or '(빈 칸)')+'\n\n내 입력:\n'+edit['widget'].get()
                                if edit.get('batch_changes'):
                                    comparison='여러 줄 붙여넣기 충돌입니다.\n'+'\n'.join(str(j+1)+'번째 칸: '+(plate['cells'][j] if j<len(plate['cells']) else '(삭제된 칸)')+' → '+v for j,old,v in edit['batch_changes'])
                                if messagebox.askyesno('같은 칸 수정 충돌',comparison+'\n\n표시된 내 입력으로 다시 저장할까요?',default='no'):
                                    edit['old']=current
                                    if edit.get('batch_changes'):
                                        if any(j>=len(plate['cells']) for j,old,v in edit['batch_changes']):
                                            messagebox.showerror('칸 변경','칸 구성이 바뀌었습니다. 저장 확인 필요 작업에서 내용을 확인해주세요.');continue
                                        edit['batch_changes']=[(j,plate['cells'][j],v) for j,old,v in edit['batch_changes']]
                                    edit['commit']()
                            else:messagebox.showerror('저장 충돌',message+'\n내 입력을 복사해 보관할 수 있습니다.')
                        else:messagebox.showerror('되돌리기/저장 충돌',message)
                        self.render()
                        self.status.set('변경 충돌 · 내 입력은 보존했습니다. 최신 내용 확인 후 재저장하세요.')
                    elif kind=='rejected':
                        self.status.set('다른 PC 저장 대기 · 입력 보존 · 잠시 후 다시 저장해주세요.')
                        messagebox.showinfo('저장 대기',value,parent=self)
                    elif kind=='operation_error':
                        self.status.set('작업 확인 필요 · 입력 보존 · '+str(value))
                        messagebox.showerror('작업 확인 필요',str(value)+'\n\n입력은 보존했습니다. 최신 내용을 확인해주세요.')
                    else:
                        if extra[0]=='connect':
                            self.connection.set('연결 확인 지연: '+value+('\n기존 데이터 위치: '+self.active_folder if self.active_folder else '\n자동으로 다시 연결합니다.'))
                        self.status.set('연결/저장 확인 필요 · 입력 보존 · 자동 연결 확인 중')
                        messagebox.showerror('연결/저장 확인 필요',value+'\n\n입력은 보존했습니다. 자동 연결 확인 후 실제 저장 내용을 확인해주세요.')
                    self.persist_failed_operations()
                elif kind=='waiting':
                    if not self.busy:self.status.set('다른 PC 저장 중 · 잠시 후 다시 확인합니다.')
                elif kind=='recovering':
                    # A missed refresh does not invalidate the loaded data or
                    # disable editing. Only repeated failed reads set offline.
                    if not self.busy:self.status.set('연결 확인 지연 · 화면/입력 유지 · 자동으로 다시 확인 중')
                elif kind=='offline':
                    _diagnostic_error(value,'공유 연결 끊김')
                    self.online=False;self.cancel_plate_drag()
                    self.status.set('연결 끊김 · 입력 보존 · 자동 연결 확인 중 · '+str(value))
                else:
                    self.online=True
                    if kind in ('connect','auto_connect'):
                        if self.data and self.data['id']!=value['id']:
                            self.undo_history=[];self.note_retry=None
                        self.connected=True;self.cfg['folder']=extra;self.active_folder=extra;self.pathvar.set(extra)
                        try:self.save_config()
                        except OSError as e:
                            _diagnostic_error(e,'PC 설정 저장')
                            self.status.set('PC 설정 저장 실패: '+str(e))
                        self.show_page('daily');self.connection.set('연결됨: '+extra+'\n데이터 ID: '+value['id'])
                    if kind=='saved':
                        if extra['kind']=='undo':
                            if self.undo_history:self.undo_history.pop()
                        elif extra.get('_undo'):
                            self.undo_history.append(extra['_undo']);self.undo_history=self.undo_history[-100:]
                        if extra['kind']=='day':
                            if self.day!=extra['day']:self.close_all_popups()
                            self.day=extra['day']
                        if extra['kind']=='delete_day':self.undo_history=[r for r in self.undo_history if r.get('day')!=extra['day']]
                        if extra['kind']=='tool':
                            i=extra['index'];draft=self.tool_drafts.get(i)
                            if draft and draft['value']==extra['value']:self.tool_drafts.pop(i,None)
                            elif draft:
                                draft['old']=extra['value']
                                self.after_idle(lambda j=i:self.submit_tool(j))
                            self.save_tool_drafts()
                        if extra['kind']=='note':
                            if extra.get('note_id')==self.note_pending:
                                self.note_pending=None;self.note_retry=None
                            self.note_feedback.set('전송 완료')
                            if self.note_input.get('1.0','end-1c')==extra['text']:
                                self.note_input.delete('1.0','end');self.note_input.edit_reset()
                        if self.edit and extra.get('edit_id')==self.edit['id']:
                            self.edit['widget'].destroy();self.edit=None
                    if kind in ('poll','saved') and self.data:
                        value={**{k:self.data[k] for k in ('dates','backup_dates','legacy_backup') if k in self.data},**value}
                    self.data=value
                    if kind in ('connect','auto_connect') or (kind=='saved' and extra['kind']=='day'):self.datevar.set(self.day)
                    self.render();self.activate_pending();self.refresh_recovery();self.refresh_management()
                    if kind=='saved' and extra['kind'] in ('add','add_complete','add_cnt'):self.after_idle(self.reveal_last_plate)
                    self.status.set(('저장 완료' if kind=='saved' else '연결됨')+' · '+self.day+(' · 공구대 미저장 입력 있음' if self.tool_drafts else ''))
                    self.finish_copy();self.finish_popup_closes()
        except queue.Empty:pass
        except Exception:
            import sys
            self.report_callback_exception(*sys.exc_info())
        finally:
            if not self.closing:self.after(100,self.drain)
    def send(self,op):
        if self.connecting or any(item['kind']=='day' for item in self.pending_updates.values()):
            self.status.set('경로/날짜 전환 중 · 입력은 유지됩니다. 전환 후 다시 저장해주세요.');return False
        if not self.connected or not self.online:
            self.status.set('연결되지 않았습니다. 입력은 보존되며 관리 → 재연결 후 저장할 수 있습니다.');return False
        op=dict(op)
        op['_store_id']=self.data['id']
        if not op.get('day'):op['day']=self.day
        if op.get('plate') in self.cards:op['plate']=self.cards[op['plate']]['plate']['id']
        if op.get('plate'):op['_plate_title']=find_plate_title(self.data,op['day'],op['plate'])
        op['_job_id']=str(uuid.uuid4());self.pending_updates[op['_job_id']]=copy.deepcopy(op)
        if not self.busy:self.busy_since=time.monotonic()
        self.busy+=1;self.jobs.put(('update',op,self.day));self.status.set('저장 중…');return True
    def today(self):self.datevar.set(date.today().isoformat());self.change_day()
    def change_day(self):
        proposed=self.datevar.get();self.datevar.set(self.day)
        if self.edit or self.busy:
            messagebox.showinfo('편집 중','현재 편집과 저장을 마쳐주세요.');return
        try:d=date.fromisoformat(proposed).isoformat()
        except ValueError:messagebox.showerror('날짜','YYYY-MM-DD 형식으로 입력해주세요.');return
        if d not in self.data.get('dates',[]) and not messagebox.askyesno('새 날짜 일보',d+' 일보가 없습니다. 새로 만들까요?'):return
        self.send({'kind':'day','day':d})
    def tool_start(self,i):
        self.tool_old[i]=self.tool_drafts.get(i,{}).get('old',self.data['tools'][i])
    def capture_tool(self,i):
        value=self.toolvars[i].get();old=self.tool_drafts.get(i,{}).get('old',self.tool_old.get(i,self.data['tools'][i]))
        if value!=old:self.tool_drafts[i]={'old':old,'value':value}
        else:self.tool_drafts.pop(i,None)
        self.save_tool_drafts()
    def tool_end(self,i):
        self.after_idle(lambda:self.submit_tool(i))
    def submit_tool(self,i):
        if self.closing:return
        self.capture_tool(i);self.tool_old.pop(i,None)
        if i not in self.tool_drafts:return
        if any(op.get('kind')=='tool' and op['index']==i for op in self.pending_updates.values()):return
        self.send({'kind':'tool','index':i,**self.tool_drafts[i]})
    def save_tool_drafts(self):
        try:
            CONFIG_DIR.mkdir(parents=True,exist_ok=True)
            atomic_json(CONFIG_DIR/'공구대_미저장.json',{'folder':self.active_folder,'drafts':self.tool_drafts})
        except OSError as e:self.status.set('공구대 임시 보관 실패: '+str(e))
    def retry_tools(self):
        if not self.online:
            messagebox.showinfo('연결 필요','먼저 재연결해주세요.');return
        if self.busy:return
        for i in list(self.tool_drafts):self.submit_tool(i)
    def discard_tools(self):
        if self.busy:return
        if self.tool_drafts and messagebox.askyesno('공구대 입력 취소','이 PC의 미저장 입력을 취소하고 저장된 공구대 내용으로 돌아갈까요?',default='no'):
            self.tool_drafts={};self.tool_old={};self.save_tool_drafts();self.render()
    def persist_failed_operations(self):
        try:
            CONFIG_DIR.mkdir(parents=True,exist_ok=True)
            atomic_json(CONFIG_DIR/'저장확인필요.json',self.failed_operations[-100:])
        except OSError:pass
    def resize(self,delta):
        self.size=max(9,min(18,self.size+delta));ttk.Style(self).configure('Treeview',font=('맑은 고딕',self.size),rowheight=tkfont.Font(font=('맑은 고딕',self.size)).metrics('linespace')+2);self.save_config()
    def visible_note_ids(self):
        if not self.data:return []
        return [str(n.get('id') or json.dumps([n.get('time'),n.get('dept'),n.get('text')],ensure_ascii=False)) for n in self.data.get('notes',[])[-300:]]
    def refresh_note_notice(self):
        ids=self.visible_note_ids()
        seen=set(self.cfg.get('note_seen_by_store',{}).get(self.data['id'],[])) if self.data else set()
        unread=sum(note_id not in seen for note_id in ids) if self.connected else 0
        self.note_notice.configure(text=(('새 메모 '+str(unread)) if unread else '채팅')+(' ▾ 접기' if self.notes_expanded else ' ▴ 펼치기'),
                                   bg=YELLOW if unread else BUTTON,fg=YTEXT if unread else TEXT,
                                   activebackground='#ffe6a0' if unread else '#303740',
                                   activeforeground=YTEXT if unread else '#ffffff')
    def mark_notes_read(self):
        if not self.connected or not self.data:return
        seen=self.cfg.setdefault('note_seen_by_store',{})
        ids=self.visible_note_ids()
        if seen.get(self.data['id'],[])!=ids:
            seen[self.data['id']]=ids
            try:self.save_config()
            except OSError as exc:self.status.set('메모 읽음 상태 저장 실패: '+str(exc))
        self.refresh_note_notice()
    def read_notes_if_focused(self):
        if self.closing or not self.notes_expanded:return
        focus=self.focus_get()
        if focus in (self.notes,self.note_input):self.mark_notes_read()
    def open_notes(self):
        self.notes_expanded=not self.notes_expanded
        if self.notes_expanded:
            self.note_preview.pack_forget()
            self.note_body.pack(fill='x')
            self.notes.see('end');self.note_input.focus_set();self.mark_notes_read()
        else:
            self.daily.focus_set()
            self.note_body.pack_forget()
            self.note_preview.pack(fill='x',padx=6,pady=(2,4))
        self.refresh_note_notice()
    def show_card_menu(self,menu,button):
        try:menu.tk_popup(button.winfo_rootx(),button.winfo_rooty()+button.winfo_height())
        finally:menu.grab_release()
    def render(self):
        if not self.data:return
        for i,var in enumerate(self.toolvars):
            if i in self.tool_drafts:
                if self.focus_get()!=self.tool_entries[i]:var.set(self.tool_drafts[i]['value'])
            elif self.focus_get()!=self.tool_entries[i]:var.set(self.data['tools'][i])
        plates=self.data['days'].get(self.day,{'plates':[]})['plates']
        signature=(self.day,self.day in self.data['days'],tuple(p['id'] for p in plates))
        if signature!=getattr(self,'signature',None):
            self.cancel_plate_drag()
            if self.edit:return
            self.signature=signature
            for w in self.gridframe.winfo_children():w.destroy()
            self.cards={key:card for key,card in self.cards.items() if key.startswith('popup:')}
            for idx,p in enumerate(plates):self.make_card(p,idx)
        if self.day not in self.data['days'] and not self.edit and not self.gridframe.winfo_children():
            self.button(self.gridframe,'이 날짜 일보 만들기',lambda:self.send({'kind':'day','day':self.day})).pack(fill='x',padx=8,pady=15)
        live_ids={p['id'] for p in plates}
        for pid in list(self.popups):
            if pid not in live_ids:self.destroy_popup(pid)
        for p in plates:
            for key in (p['id'],'popup:'+p['id']):
                if key in self.cards:self.paint_card(self.cards[key],p)
        notes=self.data['notes'][-300:]
        text='\n\n'.join(datetime.fromisoformat(n['time']).strftime('%m/%d %H:%M')+'  '+n['dept']+'\n'+n['text'] for n in notes)
        if text!=getattr(self,'notes_text',None):
            self.notes_text=text;self.notes.configure(state='normal');self.notes.delete('1.0','end');self.notes.insert('1.0',text);self.notes.configure(state='disabled');self.notes.see('end')
        latest=self.data.get('notes',[])[-1: ]
        preview=(latest[0].get('dept','')+' · '+latest[0].get('text','').replace('\n',' ')) if latest else '등록된 메모가 없습니다.'
        self.note_preview.configure(text=preview)
        self.refresh_note_notice()
        self.read_notes_if_focused()
    def finish_lost_plate_drag(self,event):
        if getattr(self,'plate_drag',None):return self.end_plate_drag(event)
    def cancel_unfocused_plate_drag(self):
        if getattr(self,'plate_drag',None) and self.focus_displayof() is None:
            self.cancel_plate_drag()
    def cancel_plate_drag(self):
        drag=getattr(self,'plate_drag',None)
        self.plate_drag=None
        if drag and drag.get('timer'):
            self.after_cancel(drag['timer'])
        if drag:
            for key in ('ghost','marker'):
                widget=drag.get(key)
                if widget and widget.winfo_exists():widget.destroy()
        if hasattr(self,'canvas'):self.canvas.delete('plate_drop')
    def begin_plate_drag(self,event,pid):
        self.cancel_plate_drag()
        if self.edit or self.busy:
            self.status.set('입력과 저장을 마친 뒤 판 제목을 드래그해주세요.');return
        if not self.connected or not self.online:return
        ids=[p['id'] for p in self.data['days'][self.day]['plates']]
        self.plate_drag={'id':pid,'old':ids,'day':self.day,'start':event.y_root,
                         'x':event.x_root,'y':event.y_root,'active':False,'timer':None}
    def move_plate_drag(self,event):
        drag=getattr(self,'plate_drag',None)
        if not drag:return
        drag.update(x=event.x_root,y=event.y_root)
        if not drag['active'] and abs(event.y_root-drag['start'])<6:return
        if not drag['active']:
            drag['active']=True
            self.create_plate_drag_preview(drag)
        self.refresh_plate_drag_preview()
        if not drag['timer']:self.tick_plate_drag()
        return 'break'
    def create_plate_drag_preview(self,drag):
        p=self.cards[drag['id']]['plate']
        bg='#9acba6' if p.get('washed') else (YELLOW if p['put'] else PANEL)
        fg='#173c25' if p.get('washed') else (YTEXT if p['put'] else TEXT)
        ghost=tk.Toplevel(self);ghost.withdraw();ghost.overrideredirect(True)
        ghost.configure(bg=BLUE,takefocus=False)
        ghost.attributes('-topmost',True)
        if os.name=='nt':
            try:ghost.attributes('-disabled',True)
            except tk.TclError:pass
        try:ghost.attributes('-alpha',.85)
        except tk.TclError:pass
        body=tk.Frame(ghost,bg=bg);body.pack(fill='both',expand=True,padx=2,pady=2)
        tk.Label(body,text=plate_title(p)+'  · 이동 중',bg=bg,fg=fg,
                 anchor='w',font=('맑은 고딕',10,'bold')).pack(fill='x',padx=8,pady=6)
        for i,value in enumerate(p['cells'][:8],1):
            tk.Label(body,text=f'{i}  {value}',bg=bg,fg=fg,anchor='w',
                     font=('맑은 고딕',9)).pack(fill='x',padx=8,pady=1)
        if len(p['cells'])>8:
            tk.Label(body,text=f'… 전체 {len(p["cells"])}칸',bg=bg,fg=fg,
                     anchor='w',font=('맑은 고딕',9)).pack(fill='x',padx=8,pady=3)
        tk.Label(body,text='휠로 스크롤 · 놓아서 이동 · Esc 취소',bg=bg,fg=fg,
                 font=('맑은 고딕',8)).pack(fill='x',padx=8,pady=6)
        drag['ghost']=ghost
        drag['marker']=tk.Frame(self.canvas,bg=BLUE,height=5,takefocus=False)
        ghost.geometry(f"{max(240,self.cards[drag['id']]['frame'].winfo_width())}x{ghost.winfo_reqheight()}+{drag['x']+18}+{drag['y']+18}")
        ghost.update_idletasks()
        ghost.geometry(f"{max(240,self.cards[drag['id']]['frame'].winfo_width())}x{body.winfo_reqheight()+4}+{drag['x']+18}+{drag['y']+18}")
        ghost.deiconify()
    def refresh_plate_drag_preview(self):
        drag=getattr(self,'plate_drag',None)
        if not drag or not drag['active']:return
        ghost=drag.get('ghost')
        if ghost:ghost.geometry(f"+{drag['x']+18}+{drag['y']+18}")
        marker=drag.get('marker')
        if not marker:return
        x=drag['x']-self.canvas.winfo_rootx();y=drag['y']-self.canvas.winfo_rooty()
        if not (0<=x<self.canvas.winfo_width() and 0<=y<self.canvas.winfo_height()):
            marker.place_forget();return
        remaining,index,line_y=self.plate_drop_position(drag)
        screen_y=line_y-self.canvas.canvasy(0)
        marker.place(x=0,y=max(0,min(self.canvas.winfo_height()-5,screen_y-2)),relwidth=1,height=5)
        marker.lift()
        where=plate_title(self.cards[remaining[index]]['plate'])+' 앞' if index<len(remaining) else '맨 아래'
        self.status.set('판 이동 · '+where+'에 놓기 · 휠 스크롤 · Esc 취소')
    def plate_drop_position(self,drag):
        remaining=[pid for pid in drag['old'] if pid!=drag['id']]
        y=self.canvas.canvasy(drag['y']-self.canvas.winfo_rooty())
        for index,pid in enumerate(remaining):
            frame=self.cards[pid]['frame']
            if y<frame.winfo_y()+frame.winfo_height()/2:
                return remaining,index,frame.winfo_y()
        bottom=(self.cards[remaining[-1]]['frame'].winfo_y()+self.cards[remaining[-1]]['frame'].winfo_height()) if remaining else 0
        return remaining,len(remaining),bottom
    def tick_plate_drag(self):
        drag=getattr(self,'plate_drag',None)
        if not drag:return
        drag['timer']=None
        if drag['day']!=self.day or any(pid not in self.cards for pid in drag['old']):
            self.cancel_plate_drag();return
        local_y=drag['y']-self.canvas.winfo_rooty()
        local_x=drag['x']-self.canvas.winfo_rootx()
        inside=0<=local_x<self.canvas.winfo_width() and 0<=local_y<self.canvas.winfo_height()
        self.canvas.delete('plate_drop')
        if inside:
            if local_y<28:self.canvas.yview_scroll(-1,'units')
            elif local_y>self.canvas.winfo_height()-28:self.canvas.yview_scroll(1,'units')
            remaining,index,line_y=self.plate_drop_position(drag)
        self.refresh_plate_drag_preview()
        drag['timer']=self.after(80,self.tick_plate_drag)
    def end_plate_drag(self,event):
        drag=getattr(self,'plate_drag',None)
        if not drag:return
        drag.update(x=event.x_root,y=event.y_root)
        active=drag['active']
        x=event.x_root-self.canvas.winfo_rootx();y=event.y_root-self.canvas.winfo_rooty()
        if active and 0<=x<self.canvas.winfo_width() and 0<=y<self.canvas.winfo_height():
            remaining,index,_=self.plate_drop_position(drag)
            order=remaining[:index]+[drag['id']]+remaining[index:]
            self.cancel_plate_drag()
            if order!=drag['old']:
                self.send({'kind':'reorder','day':drag['day'],'old':drag['old'],'order':order})
            else:self.status.set('판 순서 변경 없음')
        else:
            self.cancel_plate_drag()
            if active:self.status.set('판 이동 취소')
        return 'break' if active else None
    def paint_card(self,card,p):
        card['plate']=copy.deepcopy(p)
        put=p['put'];washed=p.get('washed')
        colored=bool(washed or put)
        bg='#9acba6' if washed else (YELLOW if put else PANEL)
        fg='#173c25' if washed else (YTEXT if put else TEXT)
        card['frame'].configure(bg=bg);card['head'].configure(bg=bg if colored else HEADER)
        card['host'].configure(bg=bg)
        card['title'].configure(bg=bg if colored else HEADER,fg=fg if colored else BLUE,text=plate_title(p)+((' · '+datetime.fromisoformat(put).strftime('%H:%M')) if put else ''))
        card['put'].configure(text='취소' if put else '투입',bg=BUTTON if put else ACCENT,activebackground='#303740' if put else '#304b65')
        card['washed'].configure(text='완료취소' if washed else '포장완료',bg='#315b40' if washed else BUTTON,activebackground='#407550' if washed else '#303740')
        tree=card['tree'];tree.configure(height=len(p['cells']));tree.tag_configure('even',background=bg if colored else ROW_A,foreground=fg)
        tree.tag_configure('odd',background=bg if colored else ROW_B,foreground=fg)
        for iid in tree.get_children():
            if int(iid)>=len(p['cells']):tree.delete(iid)
        for i,value in enumerate(p['cells']):
            if tree.exists(str(i)):tree.item(str(i),values=(i+1,value),tags=('even' if i%2==0 else 'odd',))
            else:tree.insert('','end',iid=str(i),values=(i+1,value),tags=('even' if i%2==0 else 'odd',))
    def make_card(self,p,index,parent=None,view_key=None):
        parent=parent or self.gridframe
        floating=view_key is not None
        frame=RoundedCard(parent,bg=PANEL)
        frame.grid(row=index,column=0,sticky='nsew' if floating else 'ew',padx=1,pady=3)
        parent.columnconfigure(0,weight=1)
        if floating:parent.rowconfigure(index,weight=1)
        head=tk.Frame(frame,bg=PANEL);head.pack(fill='x',padx=4,pady=(3,2));head.columnconfigure(0,weight=1)
        title=self.label(head,plate_title(p),font=('맑은 고딕',9,'bold'),width=1,anchor='w');title.grid(row=0,column=0,sticky='ew',padx=(3,2))
        if not floating:
            for handle in (head,title):
                handle.configure(cursor='fleur')
                handle.bind('<Button-1>',lambda e,pid=p['id']:self.begin_plate_drag(e,pid))
                handle.bind('<B1-Motion>',self.move_plate_drag)
                handle.bind('<ButtonRelease-1>',self.end_plate_drag)
        pid=view_key or p['id'];put=self.button(head,'투입',lambda:self.toggle_put(pid))
        put.configure(font=('맑은 고딕',8),padx=3,pady=1);put.grid(row=0,column=1,padx=1)
        washed=self.button(head,'포장완료',lambda:self.toggle_washed(pid))
        washed.configure(font=('맑은 고딕',8),padx=3,pady=1)
        washed.grid(row=0,column=2,padx=1)
        menu=tk.Menu(head,tearoff=False,bg=PANEL,fg=TEXT,activebackground=ACCENT,activeforeground=TEXT)
        if not floating:
            menu.add_command(label='팝업으로 열기',command=lambda:self.open_plate_popup(p['id']))
            menu.add_separator()
        copy_button=self.button(head,'전체 복사',lambda:self.copy_all(pid))
        copy_button.configure(font=('맑은 고딕',8),padx=2,pady=1);copy_button.grid(row=0,column=3,padx=1)
        menu.add_command(label='＋ 칸 추가',command=lambda:self.send({'kind':'row','plate':pid}))
        menu.add_command(label='− 마지막 칸 삭제',command=lambda:self.remove_row(pid))
        menu.add_separator()
        menu.add_command(label='판 삭제',foreground='#f0969d',command=lambda:self.delete_plate(pid))
        more=self.button(head,'⋯',lambda:self.show_card_menu(menu,more));more.configure(font=('맑은 고딕',9,'bold'),padx=3,pady=1);more.grid(row=0,column=4,padx=1)
        tree_host=tk.Frame(frame,bg=PANEL);tree_host.pack(fill='both',expand=True,padx=4,pady=(0,4))
        tree=ttk.Treeview(tree_host,columns=('row','company'),show='',height=15,selectmode='extended')
        tree.heading('row',text='');tree.heading('company',text='거래처명')
        tree.column('row',width=25,minwidth=25,stretch=False,anchor='center');tree.column('company',width=210,minwidth=100)
        if floating:
            scroll=ttk.Scrollbar(tree_host,orient='vertical',command=tree.yview);scroll.pack(side='right',fill='y')
            def on_scroll(*args):
                scroll.set(*args)
                if float(args[1])-float(args[0])>=.999:scroll.pack_forget()
                elif not scroll.winfo_manager():scroll.pack(side='right',fill='y',before=tree)
                self.after_idle(lambda:self.position_editor(pid))
            tree.configure(yscrollcommand=on_scroll)
        tree.pack(side='left',fill='both',expand=True)
        tree.bind('<Configure>',lambda e:self.position_editor(pid))
        tree.bind('<MouseWheel>',lambda e:self.wheel(e) if getattr(self,'plate_drag',None) else None)
        self.cards[pid]={'frame':frame,'head':head,'title':title,'tree':tree,'host':tree_host,'put':put,'washed':washed,'plate':copy.deepcopy(p)}
        tree.bind('<Button-1>',lambda e:self.select_cell(e,pid))
        tree.bind('<B1-Motion>',lambda e:self.drag(e,pid))
        tree.bind('<ButtonRelease-1>',lambda e:self.click_edit(pid))
        tree.bind('<Control-v>',lambda e:self.paste(pid));tree.bind('<<Paste>>',lambda e:self.paste(pid))
        tree.bind('<Control-c>',lambda e:self.copy_selection(pid))
        tree.bind('<BackSpace>',lambda e:self.clear_cells(pid))
        tree.bind('<Delete>',lambda e:self.clear_cells(pid))
        tree.bind('<Double-1>',lambda e:self.start_edit(pid))
        tree.bind('<Shift-Up>',lambda e:self.shift_rows(pid,-1))
        tree.bind('<Shift-Down>',lambda e:self.shift_rows(pid,1))
        tree.bind('<F2>',lambda e:self.start_edit(pid))
        tree.bind('<Return>',lambda e:self.start_edit(pid))
    def open_plate_popup(self,pid):
        if pid in self.popups and self.popups[pid].winfo_exists():
            self.popups[pid].deiconify();self.popups[pid].lift();return
        if pid not in self.cards:return
        p=copy.deepcopy(self.cards[pid]['plate'])
        self.update_idletasks()
        original=self.cards[pid]['frame']
        width=max(240,original.winfo_width()+2);height=max(180,original.winfo_height()+8)
        win=tk.Toplevel(self);win.title(self.day+' · '+plate_title(p)+' · 세척일보');win.geometry(f'{width}x{height}');win.minsize(240,180);win.configure(bg=BG)
        win.iconphoto(False,*self.app_icons)
        self.popups[pid]=win
        self.make_card(p,0,parent=win,view_key='popup:'+pid)
        self.paint_card(self.cards['popup:'+pid],p)
        win.protocol('WM_DELETE_WINDOW',lambda:self.close_plate_popup(pid))
    def position_editor(self,key):
        if not self.edit or self.edit.get('view')!=key or key not in self.cards:return
        box=self.cards[key]['tree'].bbox(str(self.edit['index']),'company')
        widget=self.edit['widget']
        if box:widget.place(x=box[0],y=box[1],width=box[2],height=box[3])
        else:widget.place_forget()
    def close_plate_popup(self,pid):
        if self.edit and self.edit.get('view')=='popup:'+pid:
            if self.edit['saving']:
                self.popup_close_pending.add(pid)
                self.status.set('팝업 입력 저장이 끝나면 팝업을 닫습니다.');return
            if self.edit['widget'].get()!=self.edit['old'] or self.edit.get('batch_changes'):
                answer=messagebox.askyesnocancel('팝업 닫기','입력한 내용을 저장하고 팝업을 닫을까요?\n예: 저장 후 닫기 / 아니요: 입력 취소 / 취소: 계속 작업',parent=self.popups[pid])
                if answer is None:return
                if answer:
                    self.popup_close_pending.add(pid);self.edit['commit']();return
            widget=self.edit['widget'];self.edit=None;self.next_cell=None;widget.destroy()
        self.destroy_popup(pid)
    def destroy_popup(self,pid):
        key='popup:'+pid
        if self.edit and self.edit.get('view')==key:return
        self.cards.pop(key,None);self.popup_close_pending.discard(pid)
        win=self.popups.pop(pid,None)
        if win and win.winfo_exists():win.destroy()
    def close_all_popups(self):
        for pid in list(self.popups):self.destroy_popup(pid)
    def finish_popup_closes(self):
        for pid in list(self.popup_close_pending):
            if not self.edit or self.edit.get('view')!='popup:'+pid:self.destroy_popup(pid)

    def clear_tree_selection(self):
        for card in self.cards.values():
            tree=card['tree'];tree.selection_remove(*tree.selection());tree.focus('')
            tree.range_select=False
            if hasattr(tree,'anchor_row'):del tree.anchor_row
    def deselect(self,commit=False):
        self.next_cell=None
        if self.edit:
            edit=self.edit
            if commit:edit['commit']()
            elif not edit['saving']:
                self.edit=None;self.pending_copy=None;edit['widget'].destroy()
        self.clear_tree_selection()
        return 'break'
    def outside_click(self,event):
        widget=event.widget
        while widget is not None:
            if any(widget==card['tree'] for card in self.cards.values()):return
            widget=getattr(widget,'master',None)
        self.deselect(commit=True)

    def choose_rows(self,pid,row,extend=False):
        tree=self.cards[pid]['tree']
        if extend:
            anchor=getattr(tree,'anchor_row',int(row));a,b=sorted((anchor,int(row)))
            tree.selection_set([str(i) for i in range(a,b+1)]);tree.range_select=True
        else:
            tree.selection_set(row);tree.anchor_row=int(row);tree.range_select=False
        tree.focus(row);tree.focus_set()
    def select_cell(self,e,pid):
        tree=self.cards[pid]['tree'];row=tree.identify_row(e.y)
        if not row:
            self.deselect();tree.range_select=True;return 'break'
        extend=bool(e.state&0x0001)
        if self.edit:
            if not self.edit['saving'] and not self.edit.get('batch_changes') and self.edit['widget'].get()==self.edit['old']:
                widget=self.edit['widget'];self.edit=None;widget.destroy()
            else:
                self.next_cell=(pid,row,extend);self.edit['commit']()
                self.status.set('현재 칸 저장 후 선택한 칸으로 이동합니다.' if self.online else '연결 끊김 · 현재 입력 보존 중 · 자동 연결 확인 후 Enter로 저장해주세요.')
                return 'break'
        self.choose_rows(pid,row,extend)
        return 'break'
    def click_edit(self,pid):
        tree=self.cards[pid]['tree']
        if not self.edit and not getattr(tree,'range_select',False) and len(self.selected(pid))==1:self.start_edit(pid)
        return 'break'
    def activate_pending(self):
        target=getattr(self,'next_cell',None)
        if self.edit or not target:return
        self.next_cell=None;pid,row,extend=target
        if pid not in self.cards:return
        tree=self.cards[pid]['tree']
        if not tree.exists(row):return
        self.choose_rows(pid,row,extend)
        if not extend:self.start_edit(pid)
    def shift_rows(self,pid,delta):
        tree=self.cards[pid]['tree'];current=tree.focus() or '0'
        row=str(max(0,min(len(self.cards[pid]['plate']['cells'])-1,int(current)+delta)))
        self.choose_rows(pid,row,True);tree.see(row);return 'break'
    def drag(self,e,pid):
        tree=self.cards[pid]['tree'];row=tree.identify_row(e.y)
        if row and hasattr(tree,'anchor_row'):
            a,b=sorted((tree.anchor_row,int(row)));tree.selection_set([str(i) for i in range(a,b+1)]);tree.range_select=True
        return 'break'
    def selected(self,pid):return sorted(int(x) for x in self.cards[pid]['tree'].selection())
    def paste(self,pid):
        if self.edit:return 'break'
        indices=self.selected(pid)
        if not indices:return 'break'
        try:values=clipboard_rows(self.clipboard_get())
        except tk.TclError:return 'break'
        p=self.cards[pid]['plate'];start=indices[0]
        if start+len(values)>len(p['cells']):
            messagebox.showinfo('칸 부족','＋ 칸 버튼으로 칸을 추가한 뒤 붙여넣어주세요.');return 'break'
        if values:self.send({'kind':'cells','plate':pid,'changes':[(start+i,p['cells'][start+i],v) for i,v in enumerate(values)]})
        return 'break'
    def copy_text(self,text):
        self.clipboard_clear();self.clipboard_append(text);self.update_idletasks();self.status.set('복사 완료 · 메모장에서 Ctrl+V로 붙여넣으세요.')
    def copy_all(self,pid):
        self.pending_copy=(self.day,self.cards[pid]['plate']['id'])
        if self.edit:self.edit['commit']()
        self.after_idle(self.finish_copy)
    def finish_copy(self):
        if not self.pending_copy or self.busy or self.edit:return
        day,pid=self.pending_copy;self.pending_copy=None
        p=next((p for p in self.data['days'].get(day,{}).get('plates',[]) if p['id']==pid),None)
        if p:self.copy_text(plate_title(p)+'\n'+'\n'.join(f'{i}. {v}' for i,v in enumerate(p['cells'],1) if v))
        else:messagebox.showinfo('복사 불가','삭제된 판입니다.')
    def copy_selection(self,pid):
        p=self.cards[pid]['plate'];self.copy_text('\n'.join(p['cells'][i] for i in self.selected(pid)));return 'break'
    def clear_cells(self,pid):
        p=self.cards[pid]['plate'];changes=[(i,p['cells'][i],'') for i in self.selected(pid)]
        if changes:self.send({'kind':'cells','plate':pid,'changes':changes})
        return 'break'
    def start_edit(self,pid):
        if self.connecting or any(item['kind']=='day' for item in self.pending_updates.values()):
            self.status.set('경로/날짜 전환이 끝난 뒤 입력해주세요.');return 'break'
        if self.edit:return 'break'
        if not self.connected:
            messagebox.showinfo('미리보기','공유폴더 연결 후 입력할 수 있습니다. 경로 설정을 확인해주세요.');return 'break'
        sel=self.selected(pid)
        if not sel:return 'break'
        i=sel[0];tree=self.cards[pid]['tree'];box=tree.bbox(str(i),'company')
        if not box:return 'break'
        old=self.cards[pid]['plate']['cells'][i]
        entry=tk.Entry(tree,font=('맑은 고딕',self.size));entry.insert(0,old);entry.place(x=box[0],y=box[1],width=box[2],height=box[3]);entry.focus_set();entry.selection_range(0,'end')
        edit={'id':str(uuid.uuid4()),'widget':entry,'old':old,'index':i,'plate':self.cards[pid]['plate']['id'],'view':pid,'saving':False}
        self.edit=edit
        def commit(e=None):
            if self.edit is not edit or edit['saving']:return 'break'
            # Defer until the Entry has received the final IME/focus event.
            def save():
                if self.edit is not edit or edit['saving']:return
                value=entry.get()
                if value==edit['old'] and not edit.get('batch_changes'):
                    self.edit=None;entry.destroy();self.activate_pending();self.finish_copy();self.finish_popup_closes();return
                changes=copy.deepcopy(edit.get('batch_changes',[(i,edit['old'],value)]))
                changes[0]=(i,edit['old'],value)
                edit['saving']=True;entry.configure(state='readonly')
                if not self.send({'kind':'cells','plate':pid,'changes':changes,'edit_id':edit['id']}):
                    edit['saving']=False;entry.configure(state='normal')
            self.after_idle(save)
            return 'break'
        def cancel(e=None):
            if edit['saving']:return 'break'
            self.edit=None;self.next_cell=None;self.pending_copy=None;entry.destroy();self.clear_tree_selection();return 'break'
        def paste_entry(e=None):
            if edit['saving']:return 'break'
            try:values=clipboard_rows(self.clipboard_get())
            except tk.TclError:return 'break'
            if not values:return 'break'
            if len(values)==1:
                entry.delete(0,'end');entry.insert(0,values[0]);commit();return 'break'
            p=self.cards[pid]['plate']
            if i+len(values)>len(p['cells']):
                messagebox.showinfo('칸 부족','＋ 칸 버튼으로 칸을 추가한 뒤 붙여넣어주세요.');return 'break'
            # Retain the pending multi-row paste if a save fails; never silently join rows.
            changes=[(i+j,edit['old'] if j==0 else p['cells'][i+j],v) for j,v in enumerate(values)]
            edit['batch_values']=values;edit['batch_changes']=changes
            entry.delete(0,'end');entry.insert(0,values[0]);edit['saving']=True;entry.configure(state='readonly')
            if not self.send({'kind':'cells','plate':pid,'changes':changes,'edit_id':edit['id']}):
                edit['saving']=False;entry.configure(state='normal')
                self.failed_operations.append({'kind':'cells','day':self.day,'plate':pid,'changes':changes});self.persist_failed_operations()
            return 'break'
        def erase(e=None):
            if edit['saving']:return 'break'
            if entry.selection_present() and entry.index('sel.first')==0 and entry.index('sel.last')==len(entry.get()):
                entry.delete(0,'end');commit();return 'break'
            return None
        def drag_entry(e):
            if edit['saving'] or entry.get()!=old:return
            row=tree.identify_row(e.y_root-tree.winfo_rooty())
            if row and int(row)!=i:
                self.edit=None;entry.destroy();tree.focus_set();tree.anchor_row=i;tree.range_select=True
                a,b=sorted((i,int(row)));tree.selection_set([str(j) for j in range(a,b+1)])
                return 'break'
        edit['commit']=commit
        entry.bind('<Return>',commit);entry.bind('<FocusOut>',commit);entry.bind('<Escape>',cancel)
        entry.bind('<Control-v>',paste_entry);entry.bind('<<Paste>>',paste_entry)
        entry.bind('<BackSpace>',erase);entry.bind('<Delete>',erase)
        entry.bind('<B1-Motion>',drag_entry)
        def shift_from_entry(delta):
            if edit['saving'] or entry.get()!=edit['old']:return 'break'
            self.edit=None;entry.destroy();return self.shift_rows(pid,delta)
        entry.bind('<Shift-Up>',lambda e:shift_from_entry(-1))
        entry.bind('<Shift-Down>',lambda e:shift_from_entry(1))
        return 'break'
    def delete_plate(self,pid):
        if self.edit:
            if self.edit['widget'].get()==self.edit['old'] and not self.edit['saving']:
                widget=self.edit['widget'];self.edit=None;widget.destroy()
            else:
                self.edit['commit']()
                messagebox.showinfo('저장 중','현재 입력 저장이 끝난 뒤 판 삭제를 눌러주세요.');return
        if self.busy:
            messagebox.showinfo('저장 중','저장이 끝난 뒤 판 삭제를 눌러주세요.');return
        p=copy.deepcopy(self.cards[pid]['plate'])
        if messagebox.askyesno('판 삭제',f"{plate_title(p)} 판을 삭제할까요?\n업체 목록과 투입 기록도 함께 삭제됩니다.",default='no'):
            self.send({'kind':'delete','plate':pid,'old':p})
    def remove_row(self,pid):
        if self.edit:
            messagebox.showinfo('편집 중','현재 입력을 Enter로 저장하거나 Esc로 취소해주세요.');return
        p=self.cards[pid]['plate']
        if len(p['cells'])<=1:
            messagebox.showinfo('칸 줄이기','최소 한 칸은 남겨야 합니다.');return
        value=p['cells'][-1]
        if value and not messagebox.askyesno('마지막 칸 삭제',f"{plate_title(p)} 판의 마지막 칸을 삭제할까요?\n\n{value}"):return
        self.send({'kind':'remove_row','plate':pid,'count':len(p['cells']),'old':value})
    def toggle_washed(self,pid):
        p=self.cards[pid]['plate']
        if p.get('washed') and not messagebox.askyesno('포장완료 취소','포장완료 표시를 취소할까요?'):
            return
        self.send({'kind':'washed','plate':pid,'old':p.get('washed'),'value':not bool(p.get('washed'))})
    def toggle_put(self,pid):
        p=self.cards[pid]['plate']
        if p.get('washed'):
            messagebox.showinfo('포장완료된 판','완료취소 후 투입 표시를 변경해주세요.');return
        if p['put'] and not messagebox.askyesno('투입 취소',f"{plate_title(p)} 판의 투입 표시와 시간을 지울까요?"):return
        self.send({'kind':'put','plate':pid,'old':p['put'],'value':not bool(p['put'])})
    def clear_notes(self):
        if not self.connected:return
        if self.busy:
            messagebox.showinfo('저장 중','현재 저장이 끝난 뒤 메모를 비워주세요.');return
        old=copy.deepcopy(self.data['notes'])
        if not old:
            self.status.set('비울 부서 메모가 없습니다.');return
        if messagebox.askyesno('부서 메모 비우기','등록된 전체 부서 메모를 비울까요?\n다른 PC에서도 함께 지워집니다.\n\n작성 중인 메모는 유지됩니다.\n실수로 비웠다면 Ctrl+Z로 복구할 수 있습니다.',default='no'):
            self.daily.focus_set()
            self.send({'kind':'clear_notes','old':old})
    def note_enter(self,event):
        if event.state & 0x0001:return None  # Shift+Enter: native Text newline.
        self.after_idle(self.post_note)
        return 'break'
    def post_note(self):
        if self.note_pending:
            self.note_feedback.set('이전 메시지 전송 중 · 입력 내용은 유지됩니다.')
            return
        text=self.note_input.get('1.0','end-1c')
        if not text.strip():return
        if self.connecting or any(item['kind']=='day' for item in self.pending_updates.values()):
            self.note_feedback.set('경로/날짜 전환 중 · 입력 보존 · 전환 후 Enter')
            return
        if not self.connected or not self.online:
            self.note_feedback.set('연결 끊김 · 입력 보존 · 연결 후 Enter로 전송')
            return
        dept=self.dept.get().strip() or '미지정'
        token=self.note_retry
        if not token or token['text']!=text or token['dept']!=dept:
            token={'note_id':str(uuid.uuid4()),'text':text,'dept':dept}
        self.note_retry=token
        self.note_pending=token['note_id']
        waiting=bool(self.busy)
        if self.send({'kind':'note',**token}):
            self.note_feedback.set('전송 대기 · 앞선 저장이 끝나면 전송합니다.' if waiting else '전송 중…')
        else:
            self.note_pending=None
            self.note_feedback.set('전송하지 못함 · 입력 보존 · 연결 후 다시 Enter')
    def show_recovery(self):
        if not self.connected:return
        if self.recovery_window and self.recovery_window.winfo_exists():
            self.recovery_window.lift();return
        win=tk.Toplevel(self);self.recovery_window=win
        win.title('삭제 내역 / 복구');win.geometry('420x360');win.configure(bg=BG)
        self.recovery_day=self.day
        self.label(win,self.day+' 삭제 내역',bg=BG).pack(pady=8)
        self.recovery_list=tk.Listbox(win,bg=FIELD,fg=TEXT,selectbackground=SELECT,exportselection=False)
        self.recovery_list.pack(fill='both',expand=True,padx=8)
        self.button(win,'선택 항목 복구',self.restore_selected).pack(pady=8)
        self.refresh_recovery()
    def refresh_recovery(self):
        if not self.recovery_window or not self.recovery_window.winfo_exists():return
        records=list(reversed(self.data['days'].get(self.recovery_day,{}).get('deleted',[])))
        if records==getattr(self,'recovery_records',None) and self.recovery_list.size():return
        self.recovery_records=copy.deepcopy(records)
        self.recovery_list.delete(0,'end')
        names={'delete':'판 삭제','remove_row':'마지막 칸 삭제','cells':'내용 지우기'}
        for r in records:self.recovery_list.insert('end',r['time'][11:19]+'  '+r['title']+' · '+names[r['kind']])
    def restore_selected(self):
        if self.busy or self.edit:
            messagebox.showinfo('작업 중','현재 입력과 저장을 마친 뒤 복구해주세요.');return
        selected=self.recovery_list.curselection()
        if not selected:return
        record=self.recovery_records[selected[0]]
        if messagebox.askyesno('삭제 복구',record['title']+' 삭제 내용을 복구할까요?\n현재 입력된 다른 내용은 덮어쓰지 않습니다.'):
            self.send({'kind':'restore','day':self.recovery_day,'record':record['id']})
    def undo_last(self,event=None):
        focus=self.focus_get()
        if focus==self.note_input:
            # Text's class binding already handles Ctrl+Z before bind_all.
            return 'break'
        if self.busy:
            self.status.set('저장 완료 후 Ctrl+Z를 다시 눌러주세요.');return 'break'
        if self.edit:
            edit=self.edit
            if edit['widget'].get()!=edit['old']:
                edit['widget'].delete(0,'end');edit['widget'].insert(0,edit['old'])
                edit['widget'].selection_range(0,'end')
                self.status.set('입력 중인 내용을 편집 전으로 되돌렸습니다.');return 'break'
            self.edit=None;self.next_cell=None;self.pending_copy=None;edit['widget'].destroy()
        if focus in self.tool_entries:
            i=self.tool_entries.index(focus)
            old=self.tool_old.get(i,self.data['tools'][i])
            if self.toolvars[i].get()!=old:
                self.toolvars[i].set(old);self.tool_drafts.pop(i,None);self.save_tool_drafts();self.status.set('입력 중인 공구 내용을 되돌렸습니다.');return 'break'
        if not self.undo_history:
            self.status.set('되돌릴 작업이 없습니다. 실행 후 내 작업 최대 100개를 기억합니다.');return 'break'
        record=self.undo_history[-1]
        if record.get('scope')=='daily' and record.get('day') and record['day']!=self.day:
            messagebox.showinfo('되돌리기',record['day']+' 날짜를 연 뒤 Ctrl+Z를 눌러주세요.');return 'break'
        self.send(copy.deepcopy(record));return 'break'
    def check_delay(self):
        if self.closing:return
        if self.busy and self.busy_since is not None and time.monotonic()-self.busy_since>=10:
            self.status.set('연결/저장 응답 지연 · 닫기를 누르면 이 PC에 임시 보관 후 종료할 수 있습니다.')
        self.after(1000,self.check_delay)
    def save_local_draft(self):
        folder=CONFIG_DIR/'unsaved'
        folder.mkdir(parents=True,exist_ok=True)
        stamp=datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        editing=None
        if self.edit:
            editing={k:self.edit[k] for k in ('plate','index','old')}
            editing['value']=self.edit['widget'].get()
        snapshot={'time':now(),'day':self.day,'folder':self.active_folder,'data':self.data,
                  'editing':editing,'tools':[v.get() for v in self.toolvars],
                  'memo':self.note_input.get('1.0','end-1c'),'dept':self.dept.get(),
                  'pending_operations':list(self.pending_updates.values())+self.failed_operations,
                  'notice':'공유폴더 저장 결과가 불확실할 수 있습니다. 실제 일보와 비교 후 필요한 내용만 복사하세요.'}
        path=folder/(stamp+'.json');atomic_json(path,snapshot)
        return path
    def show_local_draft(self,path):
        try:draft=json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            messagebox.showerror('임시 보관 읽기 실패',str(e));return
        win=tk.Toplevel(self);win.title('임시 보관 내용 · 확인 후 필요한 내용 복사');win.geometry('540x600');win.configure(bg=BG)
        area=tk.Text(win,bg=FIELD,fg=TEXT,wrap='word');area.pack(fill='both',expand=True,padx=8,pady=8)
        lines=[draft['time'],draft['notice'],'', '선택 날짜: '+draft['day']]
        for plate in draft['data']['days'].get(draft['day'],{}).get('plates',[]):
            lines.extend(['',plate_title(plate),*plate['cells']])
        if draft['editing']:
            edit=draft['editing'];title=find_plate_title(draft['data'],draft['day'],edit['plate']);lines.extend(['','[입력 중 · '+title+' / '+str(edit['index']+1)+'번째 칸]',edit['value']])
        lines.extend(['','[공구대]',*draft['tools'],'','[미등록 메모]',draft['memo'],'','[저장 결과 확인이 필요한 작업]'])
        for op in draft['pending_operations']:
            lines.append(describe_operation(op,draft['data']))
        lines.extend(['','보관 파일: '+str(path)])
        area.insert('1.0','\n'.join(lines));area.configure(state='disabled')
        self.button(win,'확인 완료 · 보관함에서 제외',lambda:self.dismiss_local_draft(path,win)).pack(pady=6)
    def dismiss_local_draft(self,path,win):
        try:path.rename(path.with_suffix('.checked.json.bak'))
        except OSError as e:messagebox.showerror('보관 파일 변경 실패',str(e));return
        win.destroy()
    def show_management(self):
        if self.manager and self.manager.winfo_exists():self.manager.lift();return
        win=tk.Toplevel(self);self.manager=win;win.title('일보 · 백업 관리');win.geometry('400x620');win.configure(bg=BG)
        top=tk.Frame(win,bg=BG);top.pack(fill='x',padx=8,pady=8)
        self.button(top,'재연결',self.reconnect).pack(side='left')
        if not HOME_TEST:self.button(top,'경로설정',lambda:(win.destroy(),self.show_page('settings'))).pack(side='left',padx=5)
        self.button(top,'삭제 항목 복구',self.show_recovery).pack(side='right')
        self.label(win,'날짜별 일보 / 백업',bg=BG).pack(anchor='w',padx=8)
        self.date_list=tk.Listbox(win,bg=FIELD,fg=TEXT,selectbackground=SELECT,exportselection=False,height=9)
        self.date_list.pack(fill='both',expand=True,padx=8,pady=4)
        self.date_list.bind('<Double-1>',lambda e:self.open_managed_day())
        row=tk.Frame(win,bg=BG);row.pack(fill='x',padx=8)
        self.button(row,'선택 날짜 열기',self.open_managed_day).pack(side='left')
        self.button(row,'일보 삭제',self.delete_managed_day).pack(side='right')
        self.button(win,'선택 날짜의 최신 백업으로 일보 복구',self.restore_managed_day).pack(fill='x',padx=8,pady=3)
        self.delete_backups=tk.BooleanVar(value=False)
        tk.Checkbutton(win,text='일보 삭제 시 해당 날짜 백업도 삭제',variable=self.delete_backups,bg=BG,fg=TEXT,selectcolor=FIELD,activebackground=BG,activeforeground=TEXT).pack(anchor='w',padx=8)
        for text,cmd in [('선택 날짜 백업만 비우기',lambda:self.purge_backup('daily')),('공구대 백업만 비우기',lambda:self.purge_backup('tools')),('부서 메모 백업만 비우기',lambda:self.purge_backup('notes')),('이전 통합 백업 정리',self.purge_legacy),('공구대 미저장 입력 재저장',self.retry_tools),('공구대 미저장 입력 취소',self.discard_tools),('이 PC의 임시 보관함',self.open_local_drafts)]:
            self.button(win,text,cmd).pack(fill='x',padx=8,pady=2)
        self.label(win,'공구대·메모는 일보 삭제와 무관하게 유지됩니다.\n새 백업은 항목/날짜별 최근 30개를 보관합니다.\n이전 통합 백업에는 여러 날짜가 함께 남아 있습니다.',bg=BG,justify='left',wraplength=370).pack(padx=8,pady=8)
        self.refresh_management()
    def refresh_management(self):
        if not self.manager or not self.manager.winfo_exists():return
        dates=sorted(set(self.data.get('dates',[]))|set(self.data.get('backup_dates',[])),reverse=True)
        snapshot=(tuple(dates),tuple(self.data.get('dates',[])))
        if snapshot==getattr(self,'management_snapshot',None) and self.date_list.size()==len(dates):return
        self.management_snapshot=snapshot
        selected=self.date_list.curselection()
        old=self.management_dates[selected[0]] if selected and selected[0]<len(getattr(self,'management_dates',[])) else None
        self.management_dates=dates;self.date_list.delete(0,'end')
        for d in dates:self.date_list.insert('end',d+(' · 백업만 남음' if d not in self.data.get('dates',[]) else ''))
        if old in dates:self.date_list.selection_set(dates.index(old))
    def selected_date(self):
        sel=self.date_list.curselection()
        return self.management_dates[sel[0]] if sel else None
    def open_managed_day(self):
        d=self.selected_date()
        if d:self.datevar.set(d);self.change_day()
    def delete_managed_day(self):
        d=self.selected_date()
        if not d:return
        if self.busy or self.edit:
            messagebox.showinfo('작업 중','편집과 저장을 마친 뒤 삭제해주세요.');return
        if d!=self.day or d not in self.data['days']:
            messagebox.showinfo('날짜 확인','먼저 선택 날짜를 열어 일보 내용을 확인해주세요.');return
        include=self.delete_backups.get()
        text=d+' 세척일보의 판·업체·투입 기록을 삭제할까요?\n공구대와 부서 메모는 유지됩니다.\n'+('해당 날짜의 새 백업도 함께 삭제됩니다.' if include else '삭제 전 내용은 해당 날짜 백업에 보관됩니다.')+'\n날짜 전체 삭제는 Ctrl+Z 대상이 아닙니다.\n이전 통합 백업은 별도 정리해야 합니다.'
        if messagebox.askyesno('날짜 일보 삭제',text,default='no'):
            self.send({'kind':'delete_day','day':d,'old':copy.deepcopy(self.data['days'][d]),'include_backups':include})
    def restore_managed_day(self):
        d=self.selected_date()
        if not d or self.busy:return
        if d in self.data.get('dates',[]):
            messagebox.showinfo('복구 불가','현재 일보가 있는 날짜는 덮어쓰지 않습니다.');return
        if messagebox.askyesno('날짜 복구',d+'의 최신 백업으로 일보를 복구할까요?',default='no'):
            self.send({'kind':'restore_day','day':d})
    def purge_backup(self,scope):
        d=self.selected_date() if scope=='daily' else self.day
        if not d:return
        if self.busy:return
        name=d+' 일보' if scope=='daily' else '공구대' if scope=='tools' else '부서 메모'
        if messagebox.askyesno('백업 정리',name+' 백업 파일만 모두 삭제할까요?\n현재 원본은 유지되며 백업 삭제는 되돌릴 수 없습니다.',default='no'):
            self.send({'kind':'purge_backups','scope':scope,'day':d})
    def purge_legacy(self):
        if self.busy:return
        if messagebox.askyesno('이전 통합 백업 정리','전환 전에 보관한 통합 원본과 이전 백업을 삭제할까요?\n전환된 공구대·메모·날짜별 일보는 유지됩니다.\n새 기록을 확인한 뒤 정리하세요. 이 작업은 되돌릴 수 없습니다.',default='no'):
            self.send({'kind':'purge_legacy'})
    def open_local_drafts(self):
        folder=CONFIG_DIR/'unsaved'
        files=sorted(folder.glob('*.json'),reverse=True)
        win=tk.Toplevel(self);win.title('이 PC의 임시 보관함');win.geometry('420x340');win.configure(bg=BG)
        listing=tk.Listbox(win,bg=FIELD,fg=TEXT,exportselection=False);listing.pack(fill='both',expand=True,padx=8,pady=8)
        for p in files:listing.insert('end',p.stem)
        def open_selected():
            sel=listing.curselection()
            if sel:self.show_local_draft(files[sel[0]])
        self.button(win,'선택 내용 열기',open_selected).pack(pady=4)
        if self.failed_operations:
            self.button(win,'저장 확인 필요 작업 보기',self.show_failed_operations).pack(pady=4)
    def show_failed_operations(self):
        win=tk.Toplevel(self);win.title('저장 결과 확인 필요');win.geometry('480x400')
        area=tk.Text(win,bg=FIELD,fg=TEXT,wrap='word');area.pack(fill='both',expand=True)
        area.insert('end','실제 일보와 비교 후 필요한 내용만 다시 입력하세요. 자동 재전송하지 않습니다.\n\n')
        for op in self.failed_operations:area.insert('end',describe_operation(op,self.data)+'\n\n')
        area.configure(state='disabled')

    def close(self):
        if getattr(getattr(self, '_update_bridge', None), 'active', False):
            self._update_bridge.fail('업데이트를 취소했습니다. 세척일보를 계속 사용할 수 있습니다.')
            return
        self.cancel_plate_drag()
        if self.closing:return
        uncommitted_tool=any(v.get()!=self.data['tools'][i] for i,v in enumerate(self.toolvars))
        unsaved=self.busy or self.edit or self.tool_drafts or uncommitted_tool or self.note_input.get('1.0','end-1c').strip()
        if unsaved:
            if not messagebox.askyesno('임시 보관 후 종료','저장 중이거나 아직 저장하지 않은 내용이 있습니다.\n\n이 PC에 내용을 임시 보관하고 종료할까요?\n예: 임시 보관 후 종료 / 아니요: 계속 작업\n\n공유폴더 저장 여부는 확정할 수 없으므로 다음 실행 때 확인해주세요.',default='no'):return
            try:self.save_local_draft()
            except Exception as e:
                if not messagebox.askyesno('임시 보관 실패',str(e)+'\n\n임시 보관도 실패했습니다. 저장되지 않은 내용을 버리고 종료할까요?',default='no'):return
        try:self.save_config()
        except Exception as e:
            if not messagebox.askyesno('설정 저장 실패',str(e)+'\n\n설정을 저장하지 않고 종료할까요?',default='no'):return
        self.closing=True;self.stop.set();self.destroy()

if __name__=='__main__':
    multiprocessing.freeze_support()
    try:
        App().mainloop()
    except Exception:
        import traceback
        details=traceback.format_exc()
        try:
            root=tk.Tk();root.withdraw();messagebox.showerror('세척일보 실행 오류',details);root.destroy()
        except Exception:
            print(details)
        raise

