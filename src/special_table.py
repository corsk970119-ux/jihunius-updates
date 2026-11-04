"""Special protrusion reference: fixed columns, editable rows and pinned notes."""
import ctypes
import copy, errno, hashlib, json, multiprocessing, os, queue, stat, tempfile, threading, time, uuid
from contextlib import contextmanager
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

SHARED_FOLDER = Path(r'\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈\지후니우스_인수인계')
BG, CELL, ALT, HEADER, LINE, TEXT, MUTED, BLUE = '#101722','#172130','#1b2636','#26364b','#34465c','#e6edf5','#a4b6cc','#2965e8'
SEED_ROWS = [{'id': 'seed-4', 'cells': ['블루다이아RC', '드릴값(위) 9.1(7.88)', '스크류 길이 (1.75~1.8) /']}, {'id': 'seed-5', 'cells': ['블루다이아NC', '드릴값(위) 9.0(7.78)', '스크류 길이 (3.05~3.1)  /']}, {'id': 'seed-6', 'cells': ['스트라우만 RC', '드릴값 8.8', '(구)드릴-드릴값 2.43']}, {'id': 'seed-7', 'cells': ['스트라우만 NC', '드릴값 +0.06', '(구)드릴-드릴값 2.43']}, {'id': 'seed-8', 'cells': ['심플라인', '드릴값 5.4', '심플라인 환봉 스크류로 체크 (2.5)']}, {'id': 'seed-9', 'cells': ['네오 IU', '드릴값 위 5.42 아래 +0.2', '네오 스크류 네오 돌출량']}, {'id': 'seed-10', 'cells': ['성남 리더스', '3X -0.03 헥사 2.475', '성남리더스 전용 랩아나로그 사용(빡빡하게 들어가면 안됨)']}, {'id': 'seed-11', 'cells': ['TSV(짐머)', '드릴값 6.41', '스크류 길이 (2.3)']}, {'id': 'seed-12', 'cells': ['오스템M KS', '드릴값 4.4', '스크류 길이 (2.8~2.85)']}, {'id': 'seed-13', 'cells': ['바이오뎀M', '드릴값 4.2', '오스템M 스크류에 길이 (2.5)']}, {'id': 'seed-14', 'cells': ['오스템KS', '가이드O', '스크류 길이 (1.45~1.5)']}, {'id': 'seed-15', 'cells': ['', '가이드X', '스크류길이 (2.35~2.4)']}, {'id': 'seed-16', 'cells': ['네오ITI', '드릴값 위 5.25 아래 +0.6', '스크류 길이 (2.4~2.45)']}, {'id': 'seed-17', 'cells': ['브라이트', '드릴값 위 -0.3', '스크류 길이 (2.15~2.2)']}, {'id': 'seed-18', 'cells': ['노멀엑티브M', '헥사2.24', '돌출량 2.6']}, {'id': 'seed-19', 'cells': ['노멀엑티브R', '드릴값 위 -0.3', '돌출량 2.6']}, {'id': 'seed-20', 'cells': ['탑플란', '헥사 2.465~2.475', '드릴값  W-0.3  / R +0.5해야함.']}, {'id': 'seed-21', 'cells': ['BLX', '', '돌출량 1.5~1.55']}, {'id': 'seed-22', 'cells': ['탑플란SS', '치수 : R4.8 / W6.0 공구 : T400 탑플란R에서 W -0.053 Z0.51', '돌출량 : R 2.7 / W 3.4 (스크류 오스템SS)']}, {'id': 'seed-23', 'cells': ['', '탑플란W에서 일반W (Z-0.02 T15 -0.12)', '일반R에서 탑플란R (Z+0.045,T15Z-0.36)']}, {'id': 'seed-24', 'cells': ['워렌텍IT', '', '돌출량 3.45~3.5 (네오R 스크류)']}, {'id': 'seed-25', 'cells': ['탑플란M', '드릴값 위 -0.03', '돌출량 3.2~3.25(오스템M 드릴)']}, {'id': 'seed-26', 'cells': ['아름R', '', '오스템스크류 2.8~2.85']}, {'id': 'seed-27', 'cells': ['스트라우만 RC정품', '모스테이퍼 두께로 판별 정품이 더 큼 1.7@ 이상', '스크류 돌출량 짧게 나옴 1.75 이하로 나옴']}, {'id': 'seed-28', 'cells': ['IU', '드릴값 위 -0.19', '']}, {'id': 'seed-29', 'cells': ['아름R', '', '']}]
SEED_NOTES = '덴티움 탑플란 메가젠스크류로 덴티움 길이값 맞추는것은 위에 수치만 -0.25 했음 잘나오면 이대로하고 아니면 치수조정해야함 \n수정된 사항은 추가 할것'


def _diagnostic_error(message,stage):
    import sys
    module=sys.modules.get("jihunius_error_history")
    if module is not None:module.capture(message,stage=stage)


def complete_windows_ime():
    """Commit pending composition in this UI thread, without inserting text twice."""
    if os.name != 'nt':
        return False
    from ctypes import wintypes as W
    user = ctypes.WinDLL('user32')
    imm = ctypes.WinDLL('imm32')
    user.GetFocus.argtypes = []; user.GetFocus.restype = W.HWND
    imm.ImmGetContext.argtypes = [W.HWND]; imm.ImmGetContext.restype = W.HANDLE
    imm.ImmReleaseContext.argtypes = [W.HWND, W.HANDLE]; imm.ImmReleaseContext.restype = W.BOOL
    imm.ImmGetCompositionStringW.argtypes = [W.HANDLE, W.DWORD, W.LPVOID, W.DWORD]
    imm.ImmGetCompositionStringW.restype = ctypes.c_long
    imm.ImmNotifyIME.argtypes = [W.HANDLE, W.DWORD, W.DWORD, W.DWORD]
    imm.ImmNotifyIME.restype = W.BOOL
    hwnd = user.GetFocus()  # GetFocus is limited to the current thread, not MES/POP.
    if not hwnd:
        return False
    context = imm.ImmGetContext(hwnd)
    if not context:
        return False
    try:
        if imm.ImmGetCompositionStringW(context, 8, None, 0) <= 0:
            return False
        if not imm.ImmNotifyIME(context, 0x15, 1, 0):  # NI_COMPOSITIONSTR / CPS_COMPLETE
            raise RuntimeError('한글 입력을 확정하지 못했어요. 입력칸에서 오른쪽 방향키를 누른 뒤 다시 실행해 주세요.')
        return True
    finally:
        imm.ImmReleaseContext(hwnd, context)

def defer_ime_commit(window, action):
    """Run an input-consuming action after Tk processes the IME result message."""
    if getattr(window, '_ime_replaying', False):
        return False
    if getattr(window, '_ime_pending', False):
        return True
    if not complete_windows_ime():
        return False
    window._ime_pending = True
    def resume():
        window._ime_pending = False
        if not window.winfo_exists():
            return
        window._ime_replaying = True
        try:
            action()
        finally:
            window._ime_replaying = False
    window.after(20, resume)
    return True

def atomic_json(path, value, staging=None):
    payload=json.dumps(value,ensure_ascii=False).encode('utf-8')
    if len(payload)>4*1024*1024:raise ValueError('표 내용이 저장 가능한 크기(4MB)를 넘었습니다. 너무 긴 붙여넣기 내용을 줄여 주세요.')
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if staging is None:fd,name=tempfile.mkstemp(prefix='.special-',suffix='.tmp',dir=str(path.parent))
    else:
        name=str(staging);fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(payload);f.flush();os.fsync(f.fileno())
        os.replace(name,str(path))
    finally:
        try:os.unlink(name)
        except OSError:pass


def read_json(path):
    with Path(path).open('rb') as f:data=f.read(4*1024*1024+1)
    if len(data)>4*1024*1024:raise ValueError('표 저장 파일이 너무 큽니다. 원본을 확인해 주세요.')
    return json.loads(data.decode('utf-8'))


@contextmanager
def file_lock(path):
    with Path(path).open('a+b') as f:
        f.seek(0,2)
        if not f.tell():f.write(b'0');f.flush()
        end=time.monotonic()+5
        while True:
            f.seek(0)
            try:
                if os.name=='nt':
                    import msvcrt
                    msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
                else:
                    import fcntl
                    fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
                break
            except OSError as exc:
                code=getattr(exc,'winerror',None)
                if not (code in (32,33) if code is not None else exc.errno in (errno.EACCES,errno.EAGAIN)):raise
                if time.monotonic()>=end:raise OSError('다른 PC에서 저장 중입니다. 잠시 후 다시 시도합니다.')
                time.sleep(.05)
        try:yield
        finally:
            f.seek(0)
            if os.name=='nt':msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(f.fileno(),fcntl.LOCK_UN)


def operation_key(op):
    if op['kind']=='notes':return 'notes'
    if op['kind']=='add':return 'add:'+op['row']['id']
    if op['kind']=='delete':return 'delete:'+op['row']
    if op['kind']=='cell':return 'cell:'+op['row']+':'+str(op['col'])
    raise ValueError('알 수 없는 표 편집 작업입니다.')


def validate_row(row):
    if (not isinstance(row,dict) or not isinstance(row.get('id'),str) or not row['id']
        or len(row['id'])>100 or not isinstance(row.get('cells'),list) or len(row['cells'])!=3
        or not all(isinstance(v,str) for v in row['cells'])):
        raise ValueError('표의 행 형식을 확인할 수 없습니다.')


def validate_operation(op):
    if not isinstance(op,dict):raise ValueError('보관된 편집 내용의 형식이 올바르지 않습니다.')
    kind=op.get('kind')
    if kind=='add':validate_row(op.get('row'));return
    if kind=='delete':validate_row({'id':op.get('row'),'cells':op.get('base')});return
    if kind not in ('cell','notes') or not all(isinstance(op.get(k),str) for k in ('base','value')):raise ValueError('표 편집 값이 올바르지 않습니다.')
    if kind=='cell' and (not isinstance(op.get('row'),str) or type(op.get('col')) is not int or not 0<=op['col']<3):raise ValueError('표의 편집 위치가 올바르지 않습니다.')


class TableStore:
    def __init__(self,folder=SHARED_FOLDER):
        self.folder=Path(folder);self.path=self.folder/'특수_돌출량.json'
    def _read(self):
        try:data=read_json(self.path)
        except FileNotFoundError as exc:
            code=getattr(exc,'winerror',None)
            if (code is not None and code!=2) or (code is None and exc.errno!=errno.ENOENT):raise
            if not stat.S_ISDIR(self.folder.stat().st_mode):raise NotADirectoryError(str(self.folder))
            return {'schema':1,'revision':0,'rows':copy.deepcopy(SEED_ROWS),'notes':SEED_NOTES},True
        if (not isinstance(data,dict) or data.get('schema')!=1 or type(data.get('revision')) is not int
            or not isinstance(data.get('rows'),list) or not isinstance(data.get('notes'),str)):
            raise ValueError('특수 돌출량 저장 형식이 올바르지 않습니다. 기존 파일은 유지합니다.')
        ids=set()
        for row in data['rows']:
            validate_row(row)
            if row['id'] in ids:raise ValueError('중복된 행 식별자가 있습니다.')
            ids.add(row['id'])
        deleted=data.get('deleted_rows',[])
        if (not isinstance(deleted,list) or not all(isinstance(v,str) and v and len(v)<=100 for v in deleted)
                or len(set(deleted))!=len(deleted) or ids.intersection(deleted)):
            raise ValueError('삭제된 줄 식별자 형식이 올바르지 않습니다. 기존 파일은 유지합니다.')
        return data,False
    def sync(self,operations=()):
        operations=copy.deepcopy(list(operations))
        for op in operations:validate_operation(op)
        if not self.folder.parent.is_dir():raise OSError('공유폴더에 연결할 수 없습니다: '+str(self.folder.parent))
        self.folder.mkdir(exist_ok=True)
        with file_lock(self.folder/'특수_돌출량.lock'):
            state,created=self._read();changed=False;conflicts=[]
            rows={r['id']:r for r in state['rows']}
            deleted=set(state.get('deleted_rows',[]))
            for op in operations:
                kind=op['kind'];key=operation_key(op)
                if kind=='add':
                    row=op['row']
                    if row['id'] in deleted:conflicts.append(key);continue
                    if row['id'] not in rows:
                        state['rows'].append(row);rows[row['id']]=row;changed=True
                    continue
                if kind=='delete':
                    row=rows.get(op['row'])
                    if row is not None and row['cells']!=op['base']:conflicts.append(key);continue
                    if row is not None:
                        state['rows'].remove(row);rows.pop(op['row']);changed=True
                    if op['row'] not in deleted:deleted.add(op['row']);changed=True
                    continue
                if kind=='cell' and op['row'] not in rows:conflicts.append(key);continue
                current=state['notes'] if kind=='notes' else rows[op['row']]['cells'][op['col']]
                if current==op['value']:continue
                if current!=op['base']:conflicts.append(key);continue
                if kind=='notes':state['notes']=op['value']
                else:rows[op['row']]['cells'][op['col']]=op['value']
                changed=True
            if created or changed:
                # Keep identifiers only, so stale pending adds cannot recreate deleted rows.
                if deleted:state['deleted_rows']=sorted(deleted)
                # This fixed staging file is owned by the exclusive table lock.
                # A killed/hung writer can leave at most one retryable snapshot.
                state['revision']+=1;atomic_json(self.path,state,self.folder/'.special_table_pending.tmp')
            return {'state':state,'conflicts':conflicts}


class PendingDraft:
    def __init__(self,folder,base=None):
        base=Path(base or os.environ.get('LOCALAPPDATA') or Path.home())/'Jihunius'/'special-table'
        key=hashlib.sha256(os.path.normcase(str(Path(folder).absolute())).encode('utf-8')).hexdigest()[:20]
        self.path=base/(key+'.json')
    def load(self):
        try:data=read_json(self.path)
        except FileNotFoundError:return []
        if not isinstance(data,dict) or data.get('schema')!=1 or not isinstance(data.get('operations'),list):raise ValueError('이 PC의 미저장 내용 형식을 확인해 주세요: '+str(self.path))
        for op in data['operations']:validate_operation(op)
        return data['operations']
    def save(self,operations):
        operations=list(operations)
        if operations:atomic_json(self.path,{'schema':1,'operations':operations})
        else:
            try:self.path.unlink()
            except FileNotFoundError:pass


def table_service(connection,folder):
    try:
        store=TableStore(folder)
        while True:
            ops=connection.recv()
            if ops is None:return
            try:reply=(True,store.sync(ops))
            except Exception as exc:reply=(False,str(exc))
            connection.send(reply)
    except (EOFError,OSError):pass
    finally:connection.close()


class TableIO:
    def __init__(self,folder,read_timeout=8,write_timeout=20):
        self.folder=str(folder);self.process=None;self.connection=None
        self.read_timeout=read_timeout;self.write_timeout=write_timeout
    def close(self):
        p,c=self.process,self.connection;self.process=None;self.connection=None
        if c is not None:
            try:c.close()
            except OSError:pass
        if p is not None:
            try:
                if p.is_alive():p.terminate()
                p.join(.3)
                if p.is_alive():p.kill();p.join(.3)
                if not p.is_alive():p.close()
            except (ValueError,OSError):pass
    def request(self,operations):
        try:
            if self.process is None or not self.process.is_alive():
                self.close();ctx=multiprocessing.get_context('spawn');parent,child=ctx.Pipe()
                p=ctx.Process(target=table_service,args=(child,self.folder),daemon=True)
                try:p.start()
                except Exception:parent.close();child.close();raise
                child.close();self.process=p;self.connection=parent
            self.connection.send(operations)
            if self.connection.poll(self.write_timeout if operations else self.read_timeout):return self.connection.recv()
            self.close();return False,'공유폴더 응답 시간이 초과됐습니다. 미저장 내용을 유지합니다.'
        except (OSError,EOFError,ValueError,RuntimeError) as exc:
            self.close();return False,str(exc)


class SpecialTableApp:
    def __init__(self,root,folder=SHARED_FOLDER,store=None):
        self.root=root;self.folder=Path(folder);self.store=store;self.io=None if store is not None else TableIO(folder)
        self.events=queue.Queue();self.pending={};self.sequence=0;self.busy=False;self.closed=False;self.closing=False
        self.ready=False;self.last_error='';self.draft_error='';self.sync_sequence=0;self.error_sequence=0
        self.state={'rows':[],'notes':''};self.editor=None;self.resolving=False;self.notes_base=''
        self.render_signature=None;self.labels=[];self.timer_ids=set();self.save_timer=None;self.local_timer=None
        self.draft=PendingDraft(folder)
        try:
            for op in self.draft.load():
                self.sequence+=1;op['seq']=self.sequence;self.pending[operation_key(op)]=op
        except Exception as exc:self.draft_error=str(exc)
        self._build()
        self.root.protocol('WM_DELETE_WINDOW',self.on_close)
        if 'CompanionWindowState' in globals():self._window_state=CompanionWindowState(root,'special-table')
        if 'CompanionUpdateBridge' in globals():self._update_bridge=CompanionUpdateBridge(root,SpecialTableUpdateSave(self))
        self.later(0,self.start_sync);self.later(100,self.poll);self.later(2500,self.periodic)
    def later(self,delay,func):
        if self.closed:return None
        item={}
        def call():
            self.timer_ids.discard(item['id'])
            if not self.closed:func()
        item['id']=self.root.after(delay,call);self.timer_ids.add(item['id']);return item['id']
    def cancel(self,job):
        if job is not None:
            try:self.root.after_cancel(job)
            except tk.TclError:pass
            self.timer_ids.discard(job)
    def _build(self):
        r=self.root;r.title('특수 돌출량');r.configure(bg=BG);r.geometry('1160x800');r.minsize(740,500)
        r.columnconfigure(0,weight=1);r.rowconfigure(2,weight=1)
        style=ttk.Style(r)
        if 'clam' in style.theme_names():style.theme_use('clam')
        style.configure('Special.TButton',font=('맑은 고딕',10),padding=(10,6),background=HEADER,foreground=TEXT,bordercolor=LINE,lightcolor=LINE,darkcolor=LINE)
        style.map('Special.TButton',background=[('active','#304665'),('pressed',BLUE)],foreground=[('disabled',MUTED)])
        style.configure('Vertical.TScrollbar',background=HEADER,troughcolor=CELL,bordercolor=LINE,arrowcolor=MUTED,lightcolor=LINE,darkcolor=LINE)
        toolbar=tk.Frame(r,bg=BG);toolbar.grid(row=0,column=0,sticky='ew',padx=12,pady=10);toolbar.columnconfigure(0,weight=1)
        search_frame=tk.Frame(toolbar,bg=CELL,highlightbackground=LINE,highlightthickness=1)
        search_frame.grid(row=0,column=0,sticky='ew',padx=(0,14));search_frame.columnconfigure(1,weight=1)
        tk.Label(search_frame,text='검색',bg=CELL,fg=MUTED,font=('맑은 고딕',10),padx=10).grid(row=0,column=0)
        self.search=tk.StringVar();search=tk.Entry(search_frame,textvariable=self.search,bg=CELL,fg=TEXT,insertbackground=TEXT,relief='flat',font=('맑은 고딕',10))
        search.grid(row=0,column=1,sticky='ew',ipady=6,padx=(0,8));self.search.trace_add('write',lambda *_:self.render())
        self.add_button=ttk.Button(toolbar,text='+ 줄 추가',command=self.add_row,style='Special.TButton',state='disabled');self.add_button.grid(row=0,column=1,padx=(0,8))
        self.context_menu=tk.Menu(r,tearoff=False,bg=CELL,fg=TEXT,activebackground=BLUE,activeforeground=TEXT)
        head=tk.Frame(r,bg=HEADER);head.grid(row=1,column=0,sticky='ew',padx=12)
        self.header=[]
        for j,label in enumerate(('타입명','수정 치수','비고')):
            w=tk.Label(head,text=label,bg=HEADER,fg=TEXT,anchor='w',font=('맑은 고딕',10,'bold'),padx=9,pady=7,highlightbackground=LINE,highlightthickness=1)
            w.grid(row=0,column=j,sticky='nsew');self.header.append(w)
        head.columnconfigure(3,minsize=16);self.header_frame=head
        body=tk.Frame(r,bg=BG);body.grid(row=2,column=0,sticky='nsew',padx=12);body.columnconfigure(0,weight=1);body.rowconfigure(0,weight=1)
        self.canvas=tk.Canvas(body,bg=CELL,highlightthickness=0);self.canvas.grid(row=0,column=0,sticky='nsew')
        scrollbar=ttk.Scrollbar(body,orient='vertical',command=self.scroll);scrollbar.grid(row=0,column=1,sticky='ns');self.canvas.configure(yscrollcommand=scrollbar.set)
        self.table=tk.Frame(self.canvas,bg=LINE);self.window_item=self.canvas.create_window(0,0,window=self.table,anchor='nw')
        self.canvas.bind('<Configure>',self.resize);self.table.bind('<Configure>',lambda e:self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<MouseWheel>',self.wheel);self.canvas.bind('<Button-4>',self.wheel);self.canvas.bind('<Button-5>',self.wheel)
        notes_frame=tk.Frame(r,bg=BG);notes_frame.grid(row=3,column=0,sticky='ew',padx=12,pady=(10,0));notes_frame.columnconfigure(0,weight=1)
        tk.Label(notes_frame,text='특이사항',bg=BG,fg=TEXT,font=('맑은 고딕',10,'bold'),anchor='w').grid(row=0,column=0,sticky='w',pady=(0,5))
        self.notes=tk.Text(notes_frame,height=4,wrap='word',bg=CELL,fg=TEXT,insertbackground=TEXT,font=('맑은 고딕',10),relief='flat',padx=10,pady=6,state='disabled',undo=True)
        self.notes.grid(row=1,column=0,sticky='ew');ns=ttk.Scrollbar(notes_frame,command=self.notes.yview);ns.grid(row=1,column=1,sticky='ns');self.notes.configure(yscrollcommand=ns.set)
        self.notes.bind('<<Modified>>',self.notes_changed)
        self.status=tk.StringVar(value='공유폴더 연결 중…');bar=tk.Frame(r,bg=BG);bar.grid(row=4,column=0,sticky='ew',padx=12,pady=7);bar.columnconfigure(0,weight=1)
        tk.Label(bar,textvariable=self.status,bg=BG,fg=MUTED,anchor='w',font=('맑은 고딕',9)).grid(row=0,column=0,sticky='ew')
        ttk.Button(bar,text='새로고침',command=self.start_sync,style='Special.TButton').grid(row=0,column=1)
        self.root.bind('<Escape>',lambda e:self.cancel_editor(),add='+')
    def columns(self,width):
        usable=max(600,width);return [int(usable*.2),int(usable*.37),usable-int(usable*.2)-int(usable*.37)]
    def resize(self,event=None):
        width=self.canvas.winfo_width();self.canvas.itemconfigure(self.window_item,width=width)
        sizes=self.columns(width)
        for j,n in enumerate(sizes):
            self.header_frame.columnconfigure(j,minsize=n,weight=0);self.table.columnconfigure(j,minsize=n,weight=0)
        for label,col in self.labels:label.configure(wraplength=max(80,sizes[col]-20))
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.position_editor()
    def displayed_state(self):
        s=copy.deepcopy(self.state);rows={row['id']:row for row in s['rows']}
        for op in self.pending.values():
            if op['kind']=='add' and op['row']['id'] not in rows:
                row=copy.deepcopy(op['row']);s['rows'].append(row);rows[row['id']]=row
        for op in self.pending.values():
            if op['kind']=='notes':s['notes']=op['value']
            elif op['kind']=='cell' and op['row'] in rows:rows[op['row']]['cells'][op['col']]=op['value']
        deleted={op['row'] for op in self.pending.values() if op['kind']=='delete'}
        s['rows']=[row for row in s['rows'] if row['id'] not in deleted]
        return s
    def render(self,force_notes=False):
        s=self.displayed_state();query=self.search.get().strip().casefold()
        rows=[row for row in s['rows'] if not query or query in '\n'.join(row['cells']).casefold()]
        signature=json.dumps(rows,ensure_ascii=False)
        if signature!=self.render_signature and self.editor is None:
            scroll=self.canvas.yview()[0];self.render_signature=signature
            for child in self.table.winfo_children():child.destroy()
            self.labels=[];self.cell_widgets={}
            for i,row in enumerate(rows):
                bg=CELL if i%2==0 else ALT
                for j,text in enumerate(row['cells']):
                    label=tk.Label(self.table,text=text,bg=bg,fg=TEXT,anchor='w',justify='left',font=('맑은 고딕',10,'bold' if j==0 else 'normal'),padx=9,pady=6,highlightbackground=LINE,highlightthickness=1)
                    label.grid(row=i,column=j,sticky='nsew');self.labels.append((label,j))
                    label.bind('<MouseWheel>',self.wheel);label.bind('<Button-4>',self.wheel);label.bind('<Button-5>',self.wheel)
                    self.cell_widgets[(row['id'],j)]=label
                    label.bind('<Button-1>',lambda e,rid=row['id'],col=j:self.edit_cell(rid,col))
                    label.bind('<Button-3>',lambda e,rid=row['id']:self.row_menu(e,rid))
            self.resize();self.root.update_idletasks();self.canvas.yview_moveto(scroll)
        if force_notes or (self.notes.focus_get() is not self.notes and not self.notes.edit_modified()):
            if self.notes.get('1.0','end-1c')!=s['notes']:
                self.notes.configure(state='normal');self.notes.delete('1.0','end');self.notes.insert('1.0',s['notes']);self.notes.edit_reset();self.notes.edit_modified(False)
                self.notes.configure(state='normal' if self.ready and not self.draft_error else 'disabled')
            self.notes_base=self.pending.get('notes',{}).get('base',self.state['notes'])
    def scroll(self,*args):
        if defer_ime_commit(self.root,lambda:self.scroll(*args)):return None
        if self.editor is not None:self.commit_editor()
        self.canvas.yview(*args)
    def wheel(self,event):
        if defer_ime_commit(self.root,lambda:self.wheel(event)):return 'break'
        if self.editor is not None:self.commit_editor()
        units=-3 if getattr(event,'num',None)==4 else 3 if getattr(event,'num',None)==5 else (-1 if event.delta>0 else 1)*3
        self.canvas.yview_scroll(units,'units');return 'break'
    def value_at(self,op,state=None):
        state=self.state if state is None else state
        if op['kind']=='notes':return state['notes']
        if op['kind']=='delete':return next((list(row['cells']) for row in state['rows'] if row['id']==op['row']),None)
        return next((row['cells'][op['col']] for row in state['rows'] if row['id']==op['row']),'')
    def change(self,op):
        key=operation_key(op);self.sequence+=1
        old=self.pending.get(key)
        op=dict(op,base=old['base'] if old and 'base' in old else op.get('base',self.value_at(op)),seq=self.sequence)
        self.pending[key]=op
        self.cancel(self.local_timer);self.local_timer=self.later(150,self.save_draft)
        self.cancel(self.save_timer);self.save_timer=self.later(450,self.start_sync)
        self.update_status()
    def save_draft(self):
        self.local_timer=None
        if self.draft_error:return False
        try:self.draft.save(self.pending.values());return True
        except Exception as exc:
            self.last_error='이 PC에도 보관하지 못했습니다: '+str(exc);self.update_status();return False
    def notes_changed(self,event=None):
        if self.notes.edit_modified():
            self.notes.edit_modified(False)
            if self.ready and not self.draft_error:
                self.change({'kind':'notes','base':self.notes_base,'value':self.notes.get('1.0','end-1c')})
    def row_menu(self,event,rid):
        if defer_ime_commit(self.root,lambda:self.row_menu(event,rid)):return 'break'
        if not self.ready or self.draft_error or self.closing:return 'break'
        self.commit_editor()
        self.context_menu.delete(0,'end')
        self.context_menu.add_command(label='줄 삭제',command=lambda:self.delete_row(rid))
        try:self.context_menu.tk_popup(event.x_root,event.y_root)
        finally:self.context_menu.grab_release()
        return 'break'
    def delete_row(self,rid):
        if defer_ime_commit(self.root,lambda:self.delete_row(rid)):return
        if not self.ready or self.draft_error or self.closing:return
        self.commit_editor()
        row=next((r for r in self.displayed_state()['rows'] if r['id']==rid),None)
        if row is None:return
        original=next((r for r in self.state['rows'] if r['id']==rid),None)
        add=self.pending.get('add:'+rid)
        base=list((original or (add['row'] if add else row))['cells'])
        for key,op in list(self.pending.items()):
            if (op['kind']=='add' and op['row']['id']==rid) or (op['kind']=='cell' and op['row']==rid):self.pending.pop(key)
        self.sequence+=1
        self.pending['delete:'+rid]={'kind':'delete','row':rid,'base':base,'seq':self.sequence}
        self.save_draft();self.render();self.start_sync()
    def add_row(self):
        if defer_ime_commit(self.root,self.add_row):return None
        if not self.ready or self.draft_error:return
        self.commit_editor();self.search.set('');rid=uuid.uuid4().hex;self.sequence+=1
        op={'kind':'add','row':{'id':rid,'cells':['','','']},'seq':self.sequence};self.pending[operation_key(op)]=op
        self.save_draft();self.render();self.root.update_idletasks();self.canvas.yview_moveto(1)
        self.edit_cell(rid,0);self.start_sync()
    def edit_cell(self,rid,col):
        if defer_ime_commit(self.root,lambda:self.edit_cell(rid,col)):return None
        if not self.ready or self.draft_error or self.closing:return
        self.commit_editor()
        widget=self.cell_widgets.get((rid,col))
        if widget is None:return
        row=next((row for row in self.displayed_state()['rows'] if row['id']==rid),None)
        if row is None:return
        text=row['cells'][col]
        edit=tk.Text(self.table,wrap='word',bg='#243b58',fg=TEXT,insertbackground=TEXT,font=('맑은 고딕',10),padx=9,pady=6,highlightbackground=BLUE,highlightcolor=BLUE,highlightthickness=2,relief='flat',undo=True)
        edit.insert('1.0',text);self.editor={'widget':edit,'anchor':widget,'row':rid,'col':col,'opened':text,'base':text,'row_cells':list(row['cells'])}
        self.position_editor();edit.focus_set();edit.mark_set('insert','end');edit.tag_add('sel','1.0','end')
        current=self.editor
        commit=lambda:self.commit_editor() if self.editor is current else None
        edit.bind('<Return>',lambda e:self.commit_key(e));edit.bind('<Tab>',lambda e:self.tab_editor(e));edit.bind('<FocusOut>',lambda e:self.later(150,commit))
        edit.bind('<Button-3>',lambda e:self.row_menu(e,rid))
    def position_editor(self):
        if self.editor:
            a=self.editor['anchor'];self.editor['widget'].place(x=a.winfo_x(),y=a.winfo_y(),width=a.winfo_width(),height=max(34,a.winfo_height()))
    def commit_key(self,event):
        if defer_ime_commit(self.root,lambda:self.commit_key(event)):return 'break'
        if event.state&1:return None
        current=self.editor
        self.root.focus_set();self.later(150,lambda:self.commit_editor() if self.editor is current else None);return 'break'
    def tab_editor(self,event):
        return self.commit_key(event)
    def commit_editor(self):
        editor=self.editor
        if editor is None:return
        value=editor['widget'].get('1.0','end-1c');self.editor=None;editor['widget'].destroy()
        if value!=editor['opened']:self.change({'kind':'cell','row':editor['row'],'col':editor['col'],'base':editor['base'],'value':value,'row_cells':editor['row_cells']})
        self.render()
    def cancel_editor(self):
        if self.editor is not None:
            self.editor['widget'].destroy();self.editor=None;self.render()
    def update_status(self):
        error=self.draft_error or self.last_error
        if not error:self._diagnostic_last_error=None
        if error:
            if error!=getattr(self,'_diagnostic_last_error',None):_diagnostic_error(error,'공유 저장/연결')
            self._diagnostic_last_error=error
            self.status.set(error+' · 미저장 '+str(len(self.pending))+'건')
        elif not self.ready:self.status.set('공유폴더 연결 중…')
        elif self.pending:self.status.set(('저장 중' if self.busy else '저장 대기')+' · '+str(len(self.pending))+'건')
        else:self.status.set('총 '+str(len(self.state['rows']))+'줄 · 저장됨')
    def start_sync(self):
        self.save_timer=None
        if self.closed or self.resolving:return
        if self.busy:return
        if not self.draft_error and not self.save_draft():return
        ops=copy.deepcopy(list(self.pending.values()));self.busy=True;self.update_status()
        def work():
            try:result=(True,self.store.sync(ops)) if self.store is not None else self.io.request(ops)
            except Exception as exc:result=(False,str(exc))
            self.events.put((ops,result))
        threading.Thread(target=work,daemon=True).start()
    def periodic(self):
        if not getattr(getattr(self,'_update_bridge',None),'active',False):self.start_sync()
        self.later(2500,self.periodic)
    def poll(self):
        try:
            while True:
                ops,(ok,result)=self.events.get_nowait();self.busy=False
                if ok:self.sync_success(ops,result)
                else:
                    self.last_error=str(result);self.error_sequence+=1;self.save_draft();self.update_status()
                    if self.closing:
                        self.closing=False
                        if messagebox.askyesno('저장 확인','공유폴더에 저장하지 못했습니다.\n'+self.last_error+'\n\n이 PC에 보관한 뒤 닫을까요?',parent=self.root,default='no'):
                            if self.save_draft():self.destroy()
                if self.closed:return
        except queue.Empty:pass
        self.later(100,self.poll)
    def sync_success(self,ops,result):
        available={r['id'] for r in result['state']['rows']}
        if self.editor is not None and self.editor['row'] not in available:
            # Fold the currently typed cell into the same restore decision.
            # IME completion posts a Tk message, so consume it on a later turn.
            if getattr(self.root,'_ime_pending',False) or complete_windows_ime():
                self.resolving=True
                def resume():
                    self.resolving=False;self.sync_success(ops,result)
                self.later(30,resume)
                return
            self.commit_editor()
        previous=self.state
        self.sync_sequence+=1;self.state=result['state'];self.last_error='';self.ready=True
        conflicts=[];force_notes=False
        for sent in ops:
            key=operation_key(sent);local=self.pending.get(key)
            if sent['kind']=='cell' and key not in result['conflicts']:
                deletion=self.pending.get('delete:'+sent['row'])
                if deletion is not None and deletion['base'][sent['col']]==sent['base']:
                    deletion['base'][sent['col']]=sent['value']
            if local is None:continue
            if key in result['conflicts']:
                if (local['kind']=='notes' or (local['kind']=='cell' and local['row'] in available)) and local.get('value')==self.value_at(local):self.pending.pop(key,None)
                else:conflicts.append(key)
            else:
                if sent['kind']=='notes':self.notes_base=self.state['notes']
                if local.get('seq')==sent.get('seq'):self.pending.pop(key,None)
                elif local['kind']!='add':local['base']=self.value_at(local)
        if conflicts:
            self.resolving=True
            try:
                # Deletions normally need no dialog. An unseen remote edit is an exception.
                for key in list(conflicts):
                    op=self.pending[key]
                    if op['kind']!='delete':continue
                    current=self.value_at(op)
                    use=messagebox.askyesno('동시 수정 확인','다른 PC에서 삭제할 줄을 수정했습니다.\n\n'+' / '.join(current or [])+'\n\n수정된 줄도 삭제할까요?',parent=self.root,default='no')
                    if use and current is not None:op['base']=current
                    else:self.pending.pop(key,None)
                    conflicts.remove(key)
                # A stale edit/add cannot revive a deleted row without an explicit choice.
                available={r['id'] for r in self.state['rows']}
                missing={self.pending[k]['row']['id'] if self.pending[k]['kind']=='add' else self.pending[k]['row']
                         for k in conflicts if self.pending[k]['kind']=='add' or
                         (self.pending[k]['kind']=='cell' and self.pending[k]['row'] not in available)}
                for rid in missing:
                    related=[k for k,o in self.pending.items() if
                             (o['kind']=='add' and o['row']['id']==rid) or (o['kind']=='cell' and o['row']==rid)]
                    old=next((r for r in previous['rows'] if r['id']==rid),None)
                    add=self.pending.get('add:'+rid)
                    snapshots=[self.pending[k].get('row_cells') for k in related if self.pending[k].get('row_cells')]
                    cells=list(add['row']['cells'] if add else old['cells'] if old else snapshots[0] if snapshots else ['','',''])
                    for key in related:
                        op=self.pending[key]
                        if op['kind']=='cell':cells[op['col']]=op['value']
                    restore=messagebox.askyesno('삭제된 줄의 수정 내용','다른 PC에서 이 줄을 삭제했습니다.\n\n'+' / '.join(cells)+'\n\n내 수정 내용을 새 줄로 복원할까요?\n아니요: 삭제 유지',parent=self.root,default='no')
                    for key in related:self.pending.pop(key,None)
                    conflicts=[k for k in conflicts if k not in related]
                    if restore:
                        self.sequence+=1;newid=uuid.uuid4().hex
                        self.pending['add:'+newid]={'kind':'add','row':{'id':newid,'cells':cells},'seq':self.sequence}
                details=[]
                for key in conflicts[:5]:
                    op=self.pending[key];title='특이사항' if op['kind']=='notes' else next((r['cells'][0] or '빈 제품명' for r in self.state['rows'] if r['id']==op['row']),'삭제된 행')
                    details.append(title+'\n공유: '+self.value_at(op)[:80]+'\n내 수정: '+op['value'][:80])
                use=messagebox.askyesno('동시 수정 확인','다른 PC에서 같은 칸을 수정했습니다.\n\n'+'\n\n'.join(details)+'\n\n내 수정으로 저장할까요?\n아니요: 공유 값 사용',parent=self.root,default='no') if conflicts else False
                for key in conflicts:
                    if use:self.pending[key]['base']=self.value_at(self.pending[key])
                    else:self.pending.pop(key,None)
                    if key=='notes':self.notes_base=self.state['notes'];force_notes=not use
            finally:self.resolving=False
        self.save_draft();self.add_button.configure(state='disabled' if self.draft_error else 'normal')
        self.notes.configure(state='disabled' if self.draft_error else 'normal')
        self.render(force_notes=force_notes);self.update_status()
        if self.closing and not self.pending:self.destroy()
        elif self.pending:self.later(0,self.start_sync)
    def on_close(self):
        if defer_ime_commit(self.root,self.on_close):return None
        if getattr(getattr(self,'_update_bridge',None),'active',False):self._update_bridge.fail('업데이트를 취소했습니다.');return
        self.root.focus_set();self.later(150,self.finish_close)
    def finish_close(self):
        self.commit_editor();self.notes_changed()
        if self.draft_error and not self.pending:self.destroy();return
        if not self.save_draft():return
        if not self.pending:self.destroy();return
        if self.closing:
            if messagebox.askyesno('저장 대기','미저장 내용은 이 PC에 보관됩니다. 지금 닫을까요?',parent=self.root,default='no'):self.destroy()
            return
        self.closing=True;self.start_sync()
    def destroy(self):
        if self.closed:return
        self.closed=True
        for job in list(self.timer_ids):self.cancel(job)
        if self.io is not None:self.io.close()
        self.root.destroy()


class SpecialTableUpdateSave:
    def __init__(self,app):self.app=app
    def begin(self):
        a=self.app
        if not a.ready or a.closing or a.draft_error:raise RuntimeError('특수 돌출량 연결과 보관 상태를 먼저 확인해 주세요.')
        a.commit_editor();a.notes_changed();self.before=a.sync_sequence;self.errors=a.error_sequence;a.start_sync()
    def saved(self):
        a=self.app
        if a.error_sequence!=self.errors or a.last_error:raise RuntimeError('특수 돌출량 저장을 확인하지 못했습니다. 창과 입력을 유지합니다.')
        return a.sync_sequence>self.before and not a.busy and not a.pending and a.editor is None and not a.resolving
    def finish(self):self.app.destroy()


def main():
    multiprocessing.freeze_support();root=tk.Tk();SpecialTableApp(root);root.mainloop()

if __name__=='__main__':main()
