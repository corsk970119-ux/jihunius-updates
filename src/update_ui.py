"""In-app controls. Concatenated with engine.py by the distribution builder."""
import queue
import threading
import time

AUTO_CHECK_SECONDS = 60

def block_reason(app, update_window=None, allow_companions=False):
    if 'native_dialog_open' in globals() and native_dialog_open(app.window,update_window):
        return '파일 선택 또는 확인 창을 먼저 닫은 뒤 다시 눌러 주세요.'
    if getattr(getattr(app,'wash_app',None),'busy',False):
        return '세척완료 작업 중입니다. 작업이 끝난 뒤 다시 눌러 주세요.'
    if getattr(app,'busy',False) or getattr(app,'card_modifier_pending',False):
        return '파일 작업 중입니다. 작업이 끝난 뒤 다시 눌러 주세요.'
    if getattr(app,'handover_writing',False) or getattr(app,'handover_dialog',None) is not None:
        return '인수인계 내용을 저장하고 창을 닫은 뒤 다시 눌러 주세요.'
    stl=getattr(app,'stl_app',None)
    worker=getattr(stl,'worker',None)
    if getattr(stl,'busy',False) is True or (worker is not None and worker.is_alive()):
        return 'STL 검색 중입니다. 검색이 끝난 뒤 다시 눌러 주세요.'
    if not allow_companions and app._suite_children.running_keys():
        return '돌출량·세척일보 보조창을 저장하고 닫은 뒤 다시 눌러 주세요.'
    if getattr(app,'_suite_exit_pending',False):return '종료 처리가 진행 중입니다.'
    if app.number_input.get('1.0','end-1c').strip():
        return '프로그램 번호 입력 내용이 남아 있습니다. 필요한 내용을 보관하고 입력칸을 비운 뒤 다시 눌러 주세요.'
    stl_input=getattr(stl,'input',None)
    if stl_input is not None and stl_input.get('1.0','end-1c').strip():
        return 'STL 주문 입력 내용이 남아 있습니다. 내용을 보관하고 입력칸을 비운 뒤 다시 눌러 주세요.'
    for window in app.window.winfo_children():
        if window is not update_window and window.winfo_class()=='Toplevel' and window.winfo_exists():
            return '열린 설정·입력 창을 먼저 닫아 주세요.'
    return ''

class Controller:
    def __init__(self,app,context,app_version):
        self.app=app;self.root=app.window;self.context=context;self.app_version=app_version
        self.current=context['current'] if context else None
        self.store=Store(context['root'],context['origin'],context['base_version']) if context else None
        self.events=queue.Queue(maxsize=4);self.busy=False;self.closed=False;self.last_check=None
        self.last_check_completed=None;self.last_check_succeeded=None
        self.dialog=None;self.offered=None;self.staged=None;self.applying=False;self.timer=None;self.check_timer=None
        self.save_timer=None
        self._download_apply=False
        self.message='시작할 때와 실행 중 1분마다 새 버전을 자동 확인합니다.'
        if self.current is None:
            self.message='자동 업데이트 실행기 연결을 확인하지 못했습니다. 트레이 메뉴에서 완전 종료한 뒤 원래 지후니우스.pyw 파일을 다시 실행해 주세요.'
        self.label=app.tk.StringVar(value='업데이트' if self.current is not None else '자동 확인 꺼짐')
        self.button=app.ttk.Button(app.title_label.master,textvariable=self.label,style='Popup.TButton',command=self.open)
        self.button.pack(side='right',padx=(12,0))
        self._restore=app.restore_from_tray
        def restore(cancel_exit=True):
            self._restore(cancel_exit=cancel_exit)
            self.check()
        app.restore_from_tray=restore
        self._exit=app.request_complete_exit
        def complete_exit():
            if self.applying:
                self.message='업데이트 전 저장 중입니다. 업데이트 창을 닫아 취소한 뒤 종료해 주세요.'
                self.open();self.refresh();return
            self._exit()
        app.request_complete_exit=complete_exit
        self._finish=app._finish_suite_shutdown
        def finish():
            if self.applying:
                reason=block_reason(app,self.dialog)
                if reason:self.abort_apply(reason);return
                try:self.store.request(self.staged,self.context['nonce'])
                except Exception:
                    self.abort_apply('업데이트 적용 요청을 저장하지 못했습니다. 현재 프로그램을 유지합니다.');return
            try:self._finish()
            except Exception:
                if self.applying:
                    self.store.cancel_request();self.abort_apply('종료하지 못했습니다. 현재 프로그램을 유지합니다.')
                raise
            if app._suite_stopped:
                self.closed=True
                for name in ('timer','check_timer','save_timer'):
                    timer=getattr(self,name)
                    if timer is not None:
                        try:self.root.after_cancel(timer)
                        except app.tk.TclError:pass
                        setattr(self,name,None)
            elif self.applying:
                self.store.cancel_request();self.abort_apply('종료 조건이 바뀌어 업데이트를 보류했습니다.')
        app._finish_suite_shutdown=finish
        self.schedule_check(500)

    def schedule_check(self,delay_ms=AUTO_CHECK_SECONDS*1000):
        if self.check_timer is not None:
            try:self.root.after_cancel(self.check_timer)
            except self.app.tk.TclError:pass
            self.check_timer=None
        if not self.closed and self.current is not None:
            self.check_timer=self.root.after(delay_ms,self.auto_check)

    def auto_check(self):
        self.check_timer=None
        if self.closed:return
        if not self.check():self.schedule_check()

    def task(self,kind,action):
        if self.busy or self.closed:return False
        self.busy=True;self.refresh()
        def worker():
            try:self.events.put((kind,True,action()))
            except Exception as exc:
                msg=str(exc) if isinstance(exc,UpdateError) else '업데이트 처리에 실패했습니다. 기존 버전은 계속 사용할 수 있습니다.'
                self.events.put((kind,False,msg))
        threading.Thread(target=worker,daemon=True).start()
        self.timer=self.root.after(100,self.poll)
        return True

    def check(self,force=False):
        if self.closed or self.busy or self.applying or self.current is None:return False
        if not force and self.last_check is not None and time.monotonic()-self.last_check<AUTO_CHECK_SECONDS:return False
        self.last_check=time.monotonic();self.message='새 버전을 확인하고 있습니다…'
        if not self.offered:self.label.set('업데이트 확인 중')
        started=self.task('check',lambda:check_offer(self.current,rejected_sha=self.store.state().get('rejected_sha')))
        if started:self.schedule_check()
        return started

    def poll(self):
        self.timer=None
        if self.closed:return
        try:kind,ok,value=self.events.get_nowait()
        except queue.Empty:
            if self.busy:self.timer=self.root.after(100,self.poll)
            return
        self.busy=False
        if kind=='check':
            self.last_check_completed=time.strftime('%m-%d %H:%M:%S')
            self.last_check_succeeded=ok
        if not ok:
            self.message=value
            self.label.set('새 버전 있음' if self.offered else '확인 실패')
        elif kind=='check':
            if value['kind']=='available':
                self.offered=value['offered'];self.label.set('새 버전 있음')
                self.message='새 버전이 있습니다. 변경 내용을 확인하고 적용해 주세요.'
            elif value['kind']=='rejected':
                self.offered=None;self.label.set('업데이트')
                self.message='시작에 실패해 복구한 버전입니다. 수정된 새 배포를 기다립니다.'
            else:
                self.offered=None;self.label.set('업데이트');self.message='현재 사용할 수 있는 최신 버전입니다.'
        elif kind=='download':
            self.staged=value;self.message='새 버전 검증을 마쳤습니다.'
            resume=self._download_apply;self._download_apply=False
            self.refresh()
            if resume:self.apply()
            return
        self.refresh()

    def open(self):
        if self.closed:return
        if self.dialog is not None and self.dialog.winfo_exists():
            self.dialog.deiconify();self.dialog.lift();return
        tk,ttk=self.app.tk,self.app.ttk
        dialog=tk.Toplevel(self.root);self.dialog=dialog
        dialog.title('지후니우스 업데이트');dialog.configure(bg='#101722')
        dialog.geometry('640x460');dialog.minsize(560,430)
        dialog.transient(self.root);dialog.protocol('WM_DELETE_WINDOW',self.close_dialog)
        frame=ttk.Frame(dialog,padding=22);frame.pack(fill='both',expand=True)
        frame.columnconfigure(0,weight=1);frame.rowconfigure(2,weight=1)
        ttk.Label(frame,text='지후니우스 업데이트',style='Title.TLabel').grid(row=0,column=0,sticky='w',pady=(0,12))
        self.versions=tk.StringVar();ttk.Label(frame,textvariable=self.versions).grid(row=1,column=0,sticky='w',pady=(0,10))
        self.notes=tk.Text(frame,height=8,wrap='word',bg='#172131',fg='#e6edf5',relief='flat',padx=12,pady=12,
                           font=('맑은 고딕',10),highlightthickness=0)
        self.notes.grid(row=2,column=0,sticky='nsew')
        self.status=tk.StringVar();ttk.Label(frame,textvariable=self.status,wraplength=585,justify='left').grid(row=3,column=0,sticky='ew',pady=(12,10))
        controls=ttk.Frame(frame);controls.grid(row=4,column=0,sticky='ew')
        self.check_button=ttk.Button(controls,text='다시 확인',style='Popup.TButton',command=lambda:self.check(force=True));self.check_button.pack(side='left')
        self.apply_button=ttk.Button(controls,text='업데이트 후 다시 시작',style='Selected.Mode.TButton',command=self.apply);self.apply_button.pack(side='right')
        dialog.bind('<Configure>',lambda event:self.status_label_wrap(frame),add='+')
        self.refresh()

    def status_label_wrap(self,frame):
        # Fixed initial size is ample; resize only the line wrapping, never poll layout.
        for widget in frame.grid_slaves(row=3,column=0):widget.configure(wraplength=max(300,frame.winfo_width()-44))

    def close_dialog(self):
        self._download_apply=False
        if self.applying:
            self.abort_apply('업데이트를 취소했습니다. 현재 버전을 계속 사용할 수 있습니다.')
            return
        if self.dialog is not None:self.dialog.destroy();self.dialog=None

    def refresh(self):
        if self.closed:return
        self.button.configure(style='HandoverNotice.TButton' if self.offered else 'Popup.TButton')
        if self.offered:self.label.set('새 버전 있음')
        if self.dialog is None or not self.dialog.winfo_exists():return
        current=self.current['version'] if self.current else self.app_version
        if self.current is None:
            checked='자동 확인 꺼짐 · 원래 실행 파일로 다시 실행해 주세요.'
        elif self.last_check_completed is None:
            checked='첫 확인 대기 중 · 실행 중 1분마다 자동 확인'
        else:
            checked='마지막 확인 '+self.last_check_completed+(' · 성공' if self.last_check_succeeded else ' · 실패')+' · 1분마다 자동 확인'
        self.versions.set('현재 '+current+('   →   새 버전 '+self.offered['version'] if self.offered else '')+'\n'+checked)
        notes=self.offered.get('notes','') if self.offered else ''
        text=notes or ('변경 내용이 등록되지 않았습니다.' if self.offered else '새 버전이 있으면 변경 내용과 사용 안내가 여기에 표시됩니다.')
        if self.notes.get('1.0','end-1c')!=text:
            self.notes.configure(state='normal');self.notes.delete('1.0','end');self.notes.insert('1.0',text);self.notes.configure(state='disabled')
        self.status.set(self.message)
        self.check_button.configure(state='disabled' if self.busy or self.applying or self.current is None else 'normal')
        self.apply_button.configure(state='normal' if self.offered and not self.busy and not self.applying else 'disabled')

    def apply(self):
        if self.closed or self.busy or self.applying or not self.offered or self.context is None:return
        if not process_alive(self.context.get('supervisor_pid')):
            self.message='재시작 실행기 연결이 종료됐습니다. 지후니우스를 완전 종료하고 기존 실행 파일을 다시 열어 주세요.'
            self.refresh();return
        reason=block_reason(self.app,self.dialog,allow_companions=True)
        if reason:self.message=reason;self.refresh();return
        if self.staged is None or self.staged['sha256']!=self.offered['sha256']:
            offered=dict(self.offered);self.message='새 버전을 내려받고 검증하고 있습니다…'
            self._download_apply=True
            self.task('download',lambda:self.store.stage(offered,public_fetch(offered['path'],offered['size'],20)))
            return
        self.open()
        self.applying=True;self.message='세척일보·돌출량표를 저장하고 있습니다…';self.refresh()
        self.dialog.grab_set()
        try:self.app._suite_children.begin_update_save()
        except Exception as exc:self.abort_apply(str(exc));return
        self.save_timer=self.root.after(100,self.poll_companion_save)

    def abort_apply(self,message):
        self._download_apply=False
        self.app._suite_children.cancel_update_save()
        if self.save_timer is not None:
            try:self.root.after_cancel(self.save_timer)
            except self.app.tk.TclError:pass
            self.save_timer=None
        if self.dialog is not None and self.dialog.winfo_exists():self.dialog.grab_release()
        self.applying=False;self.message=message;self.refresh()

    def poll_companion_save(self):
        self.save_timer=None
        if self.closed or not self.applying:return
        reason=block_reason(self.app,self.dialog,allow_companions=True)
        if reason:self.abort_apply(reason);return
        try:done=self.app._suite_children.poll_update_save()
        except Exception as exc:self.abort_apply(str(exc));return
        if done:
            self.message='저장을 확인했습니다. 업데이트 후 다시 시작합니다…';self.refresh()
            self.app._finish_suite_shutdown()
        else:self.save_timer=self.root.after(100,self.poll_companion_save)

def attach(app,context,app_version,icon_bytes=None):
    controller=Controller(app,context,app_version)
    app.updates=controller
    return controller
