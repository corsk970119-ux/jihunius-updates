"""Original material dashboard, asynchronous shared commands and owner lifecycle."""
import json
import os
from pathlib import Path
import queue
import time
import uuid
from datetime import datetime
import material_counter as core
from material_client import ClientSession,CachedStore,ReportJobs,DEFAULT_SHARE
from material_sync import atomic_json,read_json
from material_quick import QuickBridge

TITLE='소재 사용량 조사(Beta)'

class NoCollector:
    def __init__(self,*args):pass
    def start(self):pass
    def close(self):pass

class SyncedApplication(core.Application):
    backup_before_reset=False
    dashboard_actions=False
    temporary14_actions=True
    mass_mode_actions=True
    def __init__(self,root,session):
        self.session=session;self.writes={};self.toggle_pending=False;self.connected=False
        self._history_loading=False;self._history_again=False;self._inventory_loading=False
        self._last_revision=None;self._shutdown_started=False;self._connection_error='수집 PC 연결 대기'
        self._report_revision=None;self._report_scope=''
        self._ui_timer=None;self._control_id=None;self._control_timer=None;self._control_status=None
        self._front_timer=None
        self.quick_bridge=None
        folder=session.coordinator.folder
        super().__init__(root,CachedStore(folder/'counter.sqlite3'),folder,
                         collector_factory=NoCollector,jobs_factory=lambda path:ReportJobs(session))
        root.bind("<Destroy>",self._destroyed,add="+")
        root.title(TITLE)
        self.failed_storage=True
        self.refresh()
        self.control_folder=os.environ.get('JIHUNIUS_UPDATE_SESSION','')
        self.control_nonce=os.environ.get('JIHUNIUS_UPDATE_NONCE','')
        if self.control_folder and self.control_nonce:
            self.quick_bridge=QuickBridge(self,self.control_folder,self.control_nonce)
            self._control_timer=root.after(250,self.poll_control)
    def _build(self):
        super()._build()
        top=self.root.winfo_children()[0]
        labels=[w for w in top.winfo_children() if w.winfo_class()=='Label']
        labels[0].configure(text=TITLE,font=(self.font,18,'bold'))
        if len(labels)>1:labels[1].configure(text='  재고 · 생산 통계')
        self.collection_button=self.button(self.nav,'이 PC 수집  OFF',self.toggle_collection,width=16)
        self.collection_button.pack(side='right')
        self.full_reset_button=self.button(self.nav,'모두 초기화',self.full_reset_dialog)
        self.full_reset_button.configure(fg=core.PALETTE['red'])
        self.full_reset_button.pack(side='right',padx=(0,10))
        self.inventory_hint.configure(text='최근 200건 표시 · CSV는 전체 이력 · 수집 담당 PC에 함께 저장됩니다.')
        for variable in (self.date_from,self.date_to,self.period_machine):
            variable.trace_add('write',lambda *args:self._report_notice())
    def toggle_collection(self):
        if self.toggle_pending or self._shutdown_started:return
        if self.session.outbox.items():self.tell('입력 저장 결과를 확인한 뒤 수집 설정을 변경해주세요.',True);return
        self.toggle_pending=True;self.collection_button.configure(state='disabled',text='수집 설정 중…')
        current=self.session.coordinator.settings['enabled']
        try:self.session.toggle(not current)
        except queue.Full:self.toggle_pending=False;self.tell('연결 확인 중입니다. 잠시 뒤 다시 눌러주세요.',True)
    def tick(self):
        if self.closed:return
        try:
            self._finish_jobs()
            changed=False
            for _ in range(30):
                try:event=self.session.events.get_nowait()
                except queue.Empty:break
                kind=event[0]
                if kind=='state':
                    state=event[1];self.store.update(state);self.connected=True
                    if self._last_revision and self._last_revision[0]!=state['revision'][0]:
                        self._clear_reset_views()
                    self.failed_storage=bool(state['failure']);self._connection_error=state['failure']
                    self.server_detail=state['detail'];self.server_ok=state['collection'];self.errors=state['errors']
                    if state['revision']!=self._last_revision:
                        self.dirty_history=self.dirty_inventory=True;self._last_revision=state['revision']
                    changed=True
                elif kind=='connection':
                    self.connected=False;self.failed_storage=True;self._connection_error=event[2];changed=True
                elif kind=='toggle':
                    self.toggle_pending=False
                    if not event[1]:self.tell(event[2],True)
                    else:self.tell('이 PC 데이터 수집 '+('ON' if self.session.coordinator.settings['enabled'] else 'OFF'))
                    changed=True
                elif kind=='command':
                    request_id,result=event[1:]
                    if self.quick_bridge:self.quick_bridge.finish(request_id,result)
                    callbacks=self.writes.pop(request_id,None)
                    if callbacks:
                        success,failure=callbacks
                        if result['ok']:success(result.get('value'))
                        elif failure:failure(result.get('error','입력을 반영하지 못했습니다.'))
                        else:self.tell(result.get('error','입력을 반영하지 못했습니다.'),True)
                    else:self.tell('이전 입력 저장 결과: '+('저장 완료' if result['ok'] else result.get('error','반영되지 않음')),not result['ok'])
                    self.dirty_history=self.dirty_inventory=True;changed=True
            fresh=self.session.state is not None and time.monotonic()-self.session.received_at<=6
            if not fresh and self.connected:
                self.connected=False;self.failed_storage=True;self._connection_error='연결 응답이 늦습니다. 표시된 값은 마지막 수신 자료입니다.';changed=True
            pending=self.session.busy_machines()
            if set(self.pending)!=pending:
                self.pending={n:('',time.time(),False) for n in pending};changed=True
            if changed:self.refresh()
            if self.connected and not self.resetting:
                active=self.tabs.select()
                if active==str(self.history_tab) and self.dirty_history:self.refresh_history()
                if active==str(self.inventory_tab) and self.dirty_inventory:self.refresh_inventory()
        except Exception as exc:self.callback_error(type(exc),exc,exc.__traceback__)
        finally:
            if not self.closed:self._ui_timer=self.root.after(100,self.tick)
    def refresh(self):
        if not self.connected:self.store.live.clear()
        super().refresh()
        state=self.store.state
        owner=state['owner'] if state else '미설정'
        actual=bool(state and self.session.coordinator.is_owner and state['collection'])
        if hasattr(self,'collection_button') and not self.toggle_pending:
            self.collection_button.configure(text='이 PC 수집  '+('ON' if actual else 'OFF'),
                bg=core.PALETTE['green'] if actual else core.PALETTE['card'],state='normal')
        if not self.connected or self.failed_storage:
            self.footer.configure(text='연결 확인 · '+self._connection_error[:115],fg=core.PALETTE['yellow'])
        elif self.session.outbox.items():
            self.footer.configure(text='저장 확인 대기 {}건 · 수집 PC: {} · 확인 전에는 다시 입력하지 마세요.'.format(len(self.session.outbox.items()),owner),fg=core.PALETTE['yellow'])
        elif 'manual_material_edits' not in (state or {}).get('capabilities',[]):
            self.footer.configure(text='수집 담당 PC의 지후니우스를 업데이트하면 수집 ON/OFF와 관계없이 소재 입력을 함께 사용할 수 있습니다.',fg=core.PALETTE['yellow'])
        else:
            stamp=datetime.fromtimestamp(state['at']).strftime('%H:%M:%S') if state else '—'
            self.footer.configure(text='동기화 '+stamp+'  ·  수집 PC: '+owner+'  ·  담당 PC 수집 '+('ON' if state['collection'] else 'OFF'),fg=core.PALETTE['muted'])
        self._report_notice()
        if hasattr(self,'reset_button'):
            self.reset_button.configure(state='normal' if self.connected and not self.resetting and not self.session.outbox.items() else 'disabled')
        if hasattr(self,'full_reset_button'):
            self.full_reset_button.configure(state='normal' if self.connected and not self.failed_storage and not self.resetting and not self.session.outbox.items() else 'disabled')
        for n,widgets in self.rows.items():
            row=self.store.snapshot(n);held=row.get('parked')
            paused=bool(row.get('mass_mode'))
            returning=bool(held and held['role']=='original')
            widgets['switch14'].configure(text='확인 중…' if n in self.pending else ('원소재로 복귀' if returning else '14파이 교체'),
                bg=core.PALETTE['yellow'] if returning else core.PALETTE['blue'],
                fg=core.PALETTE['bg'] if returning else 'white',
                state='normal' if self.can_switch_14(n,row) else 'disabled')
            widgets['mass_mode'].configure(text='확인 중…' if n in self.pending else ('집계 재개' if paused else '양산품 교체'),
                bg=core.PALETTE['yellow'] if paused else core.PALETTE['blue'],
                fg=core.PALETTE['bg'] if paused else 'white',
                state='normal' if self.can_toggle_mass_mode(n,row) else 'disabled')
            if paused:
                widgets['program'].configure(text=('O'+row['program'] if row['program'] else '—')+'\n양산품 · 집계 중지',fg=core.PALETTE['yellow'])
            widgets['material'].configure(cursor='arrow' if paused else 'hand2')
            if held:
                widgets['material'].configure(text=widgets['material'].cget('text')+'\n보관 '+core.material_label(held['material_type'])+
                    ' · 양품 {} / 불량 {}'.format(held['good'],held['defects']))

    def action_availability(self,n,row=None,now=None):
        row=self.store.snapshot(n) if row is None else row
        state=self.store.state or {}
        ready=(self.connected and not self._shutdown_started and not self.failed_storage
               and not self.resetting and n not in self.pending)
        manual='manual_material_edits' in state.get('capabilities',[])
        # Manual entries use the shared owner, not the telemetry ON/OFF switch.
        # Fresh telemetry is obtained by the owner when available.
        return dict(rotate=bool(ready and manual),
                    defect=bool(ready and row['good']>0 and (manual or not row.get('mass_mode'))))

    def can_toggle_mass_mode(self,n,row=None):
        row=self.store.snapshot(n) if row is None else row
        state=self.store.state or {}
        return bool('mass_mode' in state.get('capabilities',[])
            and self.action_availability(n,row)['rotate']
            and row['active_material'] is not None)

    def toggle_mass_mode(self,n):
        from tkinter import messagebox
        if getattr(self,'_switch_confirming',False) or not self.can_toggle_mass_mode(n):return
        row=self.store.snapshot(n);expected=dict(row['expected']);epoch=self.store.state['epoch']
        paused=bool(row.get('mass_mode'));title='집계 재개' if paused else '양산품 교체'
        message=('원래 소재를 다시 장착한 상태인가요?\n보관한 양품·불량 수량에서 집계를 이어갑니다.' if paused else
                 '현재 소재와 양품·불량을 보관하고 이 호기의 집계를 멈춥니다.\n양산품 작업은 소재사용량에 합산하지 않습니다.')
        self._switch_confirming=True
        try:accepted=messagebox.askokcancel(title,'{}호기\n{}\n재고는 차감하지 않습니다.'.format(n,message),parent=self.root,default='cancel')
        finally:self._switch_confirming=False
        if not accepted:return
        if not self.can_toggle_mass_mode(n) or (self.store.state or {}).get('epoch')!=epoch:
            self.tell('연결 또는 소재 기록이 변경되었습니다. 최신 상태를 확인하고 다시 눌러주세요.',True);return
        self._mutate('toggle_mass_mode',[n],expected,
            lambda value:self.tell('{}호기 {} 완료 · 현재 소재의 누적 기록 유지'.format(n,title)))

    def can_switch_14(self,n,row=None):
        row=self.store.snapshot(n) if row is None else row
        state=self.store.state or {};held=row.get('parked')
        return bool('temporary14' in state.get('capabilities',[]) and self.action_availability(n,row)['rotate']
            and row['active_material'] is not None and row['material_type']
            and (row['material_type']!='14' or (held and held['role']=='original')))

    def switch_14(self,n):
        from tkinter import messagebox
        if getattr(self,'_switch_confirming',False) or not self.can_switch_14(n):return
        row=self.store.snapshot(n);held=row.get('parked');expected=dict(row['expected'])
        epoch=self.store.state['epoch'];returning=bool(held and held['role']=='original')
        title='원소재로 복귀' if returning else '14파이 교체'
        target=core.material_label(held['material_type']) if held else '새 Ø14'
        message='{}호기 · {}로 전환할까요?\n현재 {} 봉의 양품·불량을 보관합니다.\n'.format(n,target,core.material_label(row['material_type']))
        message+=('보관한 봉의 집계를 이어가며 재고는 차감하지 않습니다.' if held else '새 Ø14 재고 1봉을 차감합니다.')
        self._switch_confirming=True
        try:accepted=messagebox.askokcancel(title,message,parent=self.root,default='cancel')
        finally:self._switch_confirming=False
        if not accepted:return
        if not self.can_switch_14(n) or (self.store.state or {}).get('epoch')!=epoch:
            self.tell('연결 또는 소재 기록이 변경되었습니다. 최신 상태를 확인하고 다시 눌러주세요.',True);return
        self._mutate('switch_14',[n],expected,
            lambda value:self.tell('{}호기 {} 완료 · 보관한 봉의 기록 유지'.format(n,title)))
    def _mutate(self,method,args,expected,success=None,failure=None,epoch=None):
        if self._shutdown_started or self.resetting:return False
        try:
            token=self.session.command(method,args,expected,**({'epoch':epoch} if epoch is not None else {}))
            self.writes[token]=(success or (lambda value:self.tell('수집 PC에 저장했습니다.')),failure)
            self.pending={n:('',time.time(),False) for n in self.session.busy_machines()}
            self.tell('수집 PC에 저장 결과를 확인하고 있습니다.');self.refresh()
            return True
        except Exception as exc:self.tell(str(exc),True);return False
    def defect(self,n):
        if n in self.pending or self.failed_storage:return
        self._mutate('defect',[n],dict(self.store.snapshot(n)['expected']),
            lambda value:self.tell('{}호기 저장 완료 · 양품 −1 / 불량 +1'.format(n)))
    def rotate(self,n,early=False):
        if n in self.pending or self.failed_storage or not self._debounce(n,'rotate'):return
        row=self.store.snapshot(n)
        if not row['material_type']:
            self.material_dialog(n);self.tell('사용 중인 소재를 지정한 뒤 소재교체를 눌러주세요.');return
        self._mutate('rotate',[n,early],dict(row['expected']),
            lambda value:self.tell('{}호기 {} 저장 완료 · 새 봉 재고 1봉 차감'.format(n,'중도교체' if early else '소재교체')))
    def undo(self,n):
        from tkinter import messagebox
        if n in self.pending or self.failed_storage:return
        row=self.store.snapshot(n);label=row['undo_label'];expected=dict(row['expected'])
        if not label:return
        if not messagebox.askyesno('입력 취소','{}호기의 {}를 진행할까요?'.format(n,label),parent=self.root):return
        self._mutate('undo',[n],expected,lambda value:self.tell('{}호기: {} 저장 완료'.format(n,label)))
    def stock_dialog(self,type_id,mode):
        from tkinter import simpledialog
        if self.failed_storage or self.resetting or self.session.outbox.items():return
        row=next(r for r in self.store.inventory() if r['type_id']==type_id)
        expected=dict(self.store.state['stock_revisions'][type_id]);label=core.material_label(type_id)
        if not row['registered']:
            qty=simpledialog.askinteger('최초 재고 등록',label+' 보관 재고는 몇 봉인가요?\n이미 기계에 넣은 소재는 빼고 입력하세요.',minvalue=0,maxvalue=1000000,parent=self.root)
            if qty is None:return
            method,args='register_stock',[type_id,qty]
        elif mode=='receive':
            qty=simpledialog.askinteger('소재 입고',label+' 새로 입고된 수량 (봉)',minvalue=1,maxvalue=1000000,parent=self.root)
            if qty is None:return
            method,args='receive_stock',[type_id,qty]
        else:
            qty=simpledialog.askinteger('재고 수정',label+' 실제 보관 재고 (봉)',initialvalue=row['quantity'],minvalue=0,maxvalue=1000000,parent=self.root)
            if qty is None:return
            reason=simpledialog.askstring('수정 이유','재고 수정 이유를 입력하세요.',parent=self.root)
            if reason is None:return
            method,args='adjust_stock',[type_id,qty,reason]
        self._mutate(method,args,expected,lambda value:self.tell(label+' 재고 저장 완료'))
    def material_dialog(self,n):
        if n in self.pending or self.failed_storage or self.resetting:return
        row=self.store.snapshot(n);initial=not row['material_type'];expected=dict(row['expected'])
        epoch=self.store.state['epoch'];retry_context=False
        if row.get('mass_mode'):
            self.tell('양산품 모드입니다. 집계 재개 후 소재를 설정해주세요.',True);return
        dialog=self.tk.Toplevel(self.root);dialog.title('{}호기 소재 지정'.format(n))
        dialog.configure(bg=core.PALETTE['bg']);dialog.resizable(False,False);dialog.transient(self.root)
        heading=self.label(dialog,'',size=14,bold=True);heading.pack(padx=24,pady=(20,10))
        hint=self.label(dialog,'',color=core.PALETTE['muted'],wraplength=330);hint.pack(padx=24,pady=6)
        def show_context(latest):
            heading.configure(text='{}호기 · {}'.format(n,'현재 사용 소재' if initial else '다음 교체 소재'))
            hint.configure(text='최초 소재 지정은 재고를 차감하지 않습니다.' if initial else
                '현재: {} · 다음: {}\n다음 소재교체부터 적용됩니다.'.format(core.material_label(latest['material_type']),
                    core.material_label(latest.get('next_type') or latest['material_type'])))
        show_context(row)
        value=core.MATERIAL_TYPES.get(row.get('next_type') or row['material_type'],core.MATERIAL_TYPES[core.DEFAULT_MATERIAL_TYPE])
        chosen=self.tk.StringVar(value=value)
        combo=self.ttk.Combobox(dialog,style='Round.TCombobox',values=list(core.MATERIAL_TYPES.values()),textvariable=chosen,state='readonly',width=22)
        combo.pack(padx=24,pady=10)
        status=self.label(dialog,'',size=9,color=core.PALETTE['yellow'],wraplength=330);status.pack(padx=20)
        def ready(value):
            self.tell('{}호기 소재 설정 저장 완료'.format(n))
            if dialog.winfo_exists():dialog.destroy()
        def failed(error):
            nonlocal retry_context
            retry_context=True
            self.tell(error,True)
            if dialog.winfo_exists():status.configure(text=error);apply.configure(state='normal');dialog.protocol('WM_DELETE_WINDOW',dialog.destroy)
        def save():
            nonlocal initial,expected,epoch,retry_context
            if (not self.connected or self.failed_storage or self.resetting or self._shutdown_started
                    or n in self.pending or time.monotonic()-self.session.received_at>6):
                status.configure(text='최신 연결 또는 저장 결과를 기다리고 있습니다. 잠시 뒤 다시 눌러주세요.');return
            latest=self.store.snapshot(n);current=dict(latest['expected']);current_epoch=self.store.state['epoch']
            keys=('material','material_type','next_type','switch_revision')
            changed=current_epoch!=epoch or any(current.get(k)!=expected.get(k) for k in keys)
            first_sample=(initial and current_epoch==epoch and expected.get('material') is None
                and current.get('material') is not None and current.get('material_type') is None
                and all(current.get(k)==expected.get(k) for k in ('material_type','next_type','switch_revision')))
            if changed or retry_context:
                expected=current;epoch=current_epoch;initial=not latest['material_type']
                show_context(latest)
                review=retry_context or not first_sample;retry_context=False
                if review:
                    status.configure(text='최신 소재 정보를 불러왔습니다. 위 내용과 선택을 확인한 뒤 적용을 다시 눌러주세요.');return
            if latest.get('mass_mode'):
                status.configure(text='양산품 모드입니다. 집계 재개 후 소재를 설정해주세요.');return
            kind=next(k for k,v in core.MATERIAL_TYPES.items() if v==chosen.get())
            if self._mutate('assign_material' if initial else 'set_next_type',[n,kind],expected,ready,failed,epoch=epoch):
                apply.configure(state='disabled');status.configure(text='저장 확인 중…');dialog.protocol('WM_DELETE_WINDOW',lambda:None)
        apply=self.button(dialog,'적용',save,primary=True);apply.pack(pady=(6,20))
        dialog.grab_set();combo.focus_set()
    def refresh_history(self,force=False):
        if not self.connected or not hasattr(self,'history_tree'):return
        if self._history_loading:
            self._history_again=self._history_again or force;return
        if not force and not self.dirty_history:return
        self._history_loading=True;self.dirty_history=False;n=self._selected_machine();revision=self._last_revision
        def ready(value):
            self._history_loading=False
            if revision and self._last_revision and revision[0]!=self._last_revision[0]:
                self.dirty_history=True;return
            self.store.histories[n],self.store.event_lists[n]=value
            if n==self._selected_machine():super(SyncedApplication,self).refresh_history(force=True)
            self.dirty_history=self._history_again or revision!=self._last_revision
            self._history_again=False
        def failed(error):
            self._history_loading=False;self.tell('소재 기록 조회 실패: '+str(error),True)
        if not self.run_report_job(lambda v:(v.history(n),v.events(n)),ready,failed):self._history_loading=False
    def refresh_inventory(self):
        if not hasattr(self,'stock_tree'):return
        super().refresh_inventory()
        if not self.connected or self._inventory_loading:return
        self._inventory_loading=True;revision=self._last_revision
        def ready(value):
            self._inventory_loading=False
            if revision and self._last_revision and revision[0]!=self._last_revision[0]:
                self.dirty_inventory=True;return
            self.store.movement_list=value
            super(SyncedApplication,self).refresh_inventory()
            self.dirty_inventory=revision!=self._last_revision
        def failed(error):self._inventory_loading=False;self.tell('입출고 기록 조회 실패: '+str(error),True)
        if not self.run_report_job(lambda v:v.movements(),ready,failed):self._inventory_loading=False
    def _render_period(self,report):
        revision=report.get('_sync_revision')
        if revision and self._last_revision and revision[0]!=self._last_revision[0]:return
        super()._render_period(report)
        self._report_revision=report.get('_sync_revision',self._last_revision)
        stamp=datetime.fromtimestamp(report.get('_queried_at',time.time())).strftime('%H:%M:%S')
        self._report_scope=self.period_scope.cget('text')+' · 조회 '+stamp
        self._report_notice()
    def _report_notice(self):
        report=getattr(self,'_period_report',None)
        if report is None or not self._report_scope:return
        try:changed=self.period_range()!=(report['start'],report['end'],report['machine'])
        except ValueError:changed=True
        reason=''
        if changed:reason='조회 조건 변경 · 다시 조회'
        elif self._report_revision!=self._last_revision:reason='새 기록 있음 · 다시 조회'
        elif not self.connected:reason='연결 확인 필요 · 마지막 조회 자료'
        self.period_scope.configure(text=self._report_scope+('  |  '+reason if reason else ''),
            fg=core.PALETTE['yellow'] if reason else core.PALETTE['muted'])
    def _clear_reset_views(self):
        self.store.histories.clear();self.store.event_lists.clear();self.store.movement_list=[]
        self.event_details={};self.last_click.clear()
        self._period_request+=1;self._period_report=None
        self._report_revision=None;self._report_scope=''
        for tree in (self.history_tree,self.event_tree,self.stock_tree,self.report_tree,self.daily_tree):
            children=tree.get_children()
            if children:tree.delete(*children)
        for value,note in self.period_cards.values():
            value.configure(text='—');note.configure(text='초기화됨 · 다시 조회')
        self.period_scope.configure(text='기록이 초기화되었습니다. 새 기록은 조회 버튼으로 확인하세요.',fg=core.PALETTE['muted'])
        self.period_summary.configure(text='초기화 이전의 통계를 비웠습니다.',fg=core.PALETTE['muted'])
        self.period_observed.configure(text='기간 중 수집 · 조회 대기')
        core.Application.refresh_inventory(self)
        self.dirty_history=self.dirty_inventory=True
    def full_reset_dialog(self):
        from tkinter import messagebox
        if not self.connected or self.failed_storage or self.resetting:return
        if self.session.outbox.items() or self.job_callbacks or self.writes:
            self.tell('입력 저장·조회·내보내기가 끝난 뒤 모두 초기화해주세요.',True);return
        if not messagebox.askyesno('소재 사용량 조사 · 모두 초기화',
                '모든 PC가 함께 사용하는 소재 사용량 조사 데이터를 초기화할까요?\n\n'
                '• 가공·불량·소재교체·입출고 기록과 현재 집계·보관 소재 삭제\n'
                '• 재고 수량 및 호기별 사용 소재·다음 소재 설정 초기화\n\n'
                '자동 백업 없이 삭제하며 프로그램에서 되돌릴 수 없습니다.\n'
                'PC 연결과 수집 ON/OFF 설정은 유지합니다.\n'
                '수집 ON 상태라면 새 기준으로 수집을 이어갑니다.',parent=self.root):return
        self._begin_reset(True)
    def _begin_reset(self,reset_stock,dialog=None,status=None,apply_button=None,cancel=None):
        if not self.connected or self.failed_storage or self.resetting or self.session.outbox.items() or self.job_callbacks:return False
        expected=dict(revision=list(self.store.state['revision']))
        def done(value):
            self.resetting=False
            if dialog:dialog.destroy()
            self.tell('모두 초기화 완료' if reset_stock else '기록 삭제 완료')
            self.dirty_history=self.dirty_inventory=True
        def failed(error):
            self.resetting=False;self.tell(error,True)
            if status:status.configure(text=error)
            if apply_button:apply_button.configure(state='normal')
            if cancel:cancel.configure(state='normal')
            if dialog:dialog.protocol('WM_DELETE_WINDOW',dialog.destroy)
        accepted=self._mutate('reset_records',[reset_stock],expected,done,failed)
        if accepted:self.resetting=True
        else:failed('삭제 요청을 보내지 못했습니다. 연결 상태를 확인해주세요.')
        return accepted
    def diagnostics(self):
        from tkinter import filedialog
        path=filedialog.asksaveasfilename(parent=self.root,title='확인용 데이터 저장',defaultextension='.json',initialfile='소재사용량_진단.json',filetypes=[('JSON','*.json')])
        if not path:return
        def work(view):
            payload=dict(version='0.5.0-beta',saved_at=core.date_text(time.time()),
                state=view.client.call('state'),materials=view.history(),events=view.events(limit=1000),stock_movements=view.movements(limit=1000))
            view.validate_export_path(path);atomic_json(path,payload)
        self.run_report_job(work,lambda value:self.tell('확인용 데이터를 저장했습니다.'))
    def help(self):
        from tkinter import messagebox
        messagebox.showinfo(TITLE+' 사용 안내',
            '수집 담당 PC 한 대에서만 이 PC 수집을 ON으로 사용합니다.\n'
            '두 PC 모두 수집 ON/OFF와 관계없이 불량·소재교체·14파이·양산품 전환을 입력할 수 있습니다.\n'
            '입력 결과는 담당 PC에 저장된 뒤 두 PC에 표시됩니다.\n'
            '수집 담당 PC와 지후니우스가 실행되어 있어야 동기화할 수 있습니다.\n\n'
            '보관 재고 등록 → 호기별 사용 소재 지정 순서로 시작합니다.\n'
            '번호가 집계 대상 4자리로 바뀔 때 가공 +1, 3999·9012·9020·9999는 제외합니다.\n'
            '9020 이후 같은 작업번호로 돌아오면 +0, 다른 집계 대상 번호면 +1입니다.\n'
            '사이트 카운터는 읽거나 기록하지 않으며 수량은 프로그램 번호 변화만으로 판단합니다.\n'
            '불량 +1은 기존 양품을 불량으로 변경하며 전체 가공 수는 유지됩니다.\n'
            '소재교체는 현재 봉을 마감하고 새 소재 재고 1봉을 차감합니다.\n'
            '현재집계의 14파이 교체는 원소재를 보관하고, 원소재로 복귀는 같은 봉의 누적 집계를 이어갑니다.\n'
            '설비 응답이 있으면 최신 번호까지 반영합니다. 응답이 없으면 수동 경계를 기록하고 다음 첫 관측은 기준값으로만 사용합니다.\n'
            '복귀 시 14파이도 보관합니다. 보관 봉 재사용은 재고를 차감하지 않으며 새 Ø14 최초 투입만 1봉 차감합니다.\n'
            '양산품 교체는 해당 호기의 소재·수량을 보관하고 집계만 멈춥니다. 원래 소재를 장착한 뒤 집계 재개를 누르세요.\n'
            '다 쓴 봉은 메인의 소재교체로 마감합니다. 사용 중·보관 중인 봉은 마감 후 기간통계에 반영됩니다.\n'
            '가공량이 적어도 소재교체한 봉은 소모 1봉에 포함합니다. 우클릭으로 마지막 입력을 취소할 수 있습니다.\n'
            '봉당 평균은 기간 내 사용을 끝낸 완전측정 봉 기준입니다.\n'
            '중간 시작·수집 공백·불량초과 봉은 평균에서 제외하고 표시합니다.\n\n'
            '저장 담당 PC와 연결이 끊기면 마지막 수신 자료를 표시하고 새 입력을 막습니다.\n'
            '저장 확인 대기인 입력은 재연결 후 같은 번호로 결과를 확인하므로 다시 입력하지 마세요.\n'
            '창을 닫으면 숨겨지며 수집은 계속됩니다. 지후니우스 완전 종료 시 함께 종료됩니다.',parent=self.root)
    def on_close(self):
        if self.root.grab_current() is not None:return
        if self._front_timer is not None:
            self.root.after_cancel(self._front_timer);self._front_timer=None
        placement=getattr(self,'placement',None)
        if placement:placement.flush()
        self.root.withdraw();self.session.visible=False
    def show_front(self):
        if self.closed or self._shutdown_started:return
        self.root.deiconify();self.session.visible=True
        self.root.update_idletasks()
        self.root.lift()
        modal=self.root.grab_current()
        target=modal.winfo_toplevel() if modal is not None else self.root
        target.lift();target.focus_force()
        if self._front_timer is not None:self.root.after_cancel(self._front_timer)
        # Activation follows Tk mapping and saved-placement restoration. A
        # one-shot callback avoids keeping a hidden or background window on top.
        self._front_timer=self.root.after_idle(self._focus_front)
    def _focus_front(self):
        self._front_timer=None
        if self.closed or self._shutdown_started or self.root.state() in ('withdrawn','iconic'):return
        placement=getattr(self,'placement',None)
        if placement is not None and not getattr(placement,'ready',True):placement.restore()
        modal=self.root.grab_current()
        target=modal.winfo_toplevel() if modal is not None else self.root
        target.lift();target.focus_force()
        if os.name=='nt':
            try:
                import ctypes
                from ctypes import wintypes as w
                user=ctypes.WinDLL('user32',use_last_error=True)
                user.GetAncestor.argtypes=[w.HWND,w.UINT];user.GetAncestor.restype=w.HWND
                user.SetForegroundWindow.argtypes=[w.HWND];user.SetForegroundWindow.restype=w.BOOL
                hwnd=user.GetAncestor(target.winfo_id(),2)
                if hwnd:user.SetForegroundWindow(hwnd)
            except (AttributeError,OSError):pass
    def poll_control(self):
        if self.closed:return
        try:
            if self.quick_bridge:self.quick_bridge.poll()
            command=read_json(Path(self.control_folder)/'material-control.json',{})
            if command.get('nonce')==self.control_nonce and command.get('id')!=self._control_id and command.get('expires',0)>time.time():
                self._control_id=command['id']
                if command.get('action')=='show':
                    self.show_front()
                elif command.get('action')=='toggle':
                    if self.root.state() in ('withdrawn','iconic'):self.show_front()
                    else:self.on_close()
                elif command.get('action')=='exit':
                    if self.root.grab_current() is not None:
                        self.root.deiconify();self.root.lift();self.tell('열린 입력창을 처리한 뒤 완전 종료해주세요.',True)
                    else:self.shutdown()
            status=dict(nonce=self.control_nonce,visible=self.root.state()!='withdrawn',at=int(time.time()))
            if self.quick_bridge:status['quick']=self.quick_bridge.status()
            if status!=self._control_status:
                atomic_json(Path(self.control_folder)/'material-status.json',status);self._control_status=status
        except (OSError,ValueError):pass
        if not self.closed:self._control_timer=self.root.after(300,self.poll_control)
    def _destroyed(self,event):
        if event.widget is not self.root:return
        self.closed=True;self.session.close();self.jobs.close()
        for timer in (self._ui_timer,self._control_timer,self._front_timer):
            if timer:
                try:self.root.after_cancel(timer)
                except Exception:pass
    def callback_error(self,kind,value,trace):
        recorder=getattr(core,'_err_module',None)
        if recorder:
            import traceback
            recorder.capture(str(value),feature=TITLE,stage='화면 처리',detail=''.join(traceback.format_exception(kind,value,trace)))
        self.tell('화면 처리 오류: '+str(value)[:150],True)
    def shutdown(self):
        if self._shutdown_started:return
        if self.job_callbacks:
            self.root.deiconify();self.session.visible=True
            self.tell('진행 중인 조회·내보내기가 끝난 뒤 완전 종료해주세요.',True);return
        if self.session.outbox.items():
            from tkinter import messagebox
            self.root.deiconify();self.session.visible=True
            if not messagebox.askyesno('저장 확인 대기',
                    '저장 결과를 아직 확인하지 못한 입력이 있습니다.\n\n'
                    '확인 대기 기록을 이 PC에 유지하고 종료할까요?\n'
                    '다음 실행에서 수집 PC에 저장 여부를 다시 확인합니다.\n'
                    '같은 작업을 다시 입력하지 마세요.',parent=self.root):return
        elif self.writes:
            self.tell('입력 결과를 표시하는 중입니다. 잠시 뒤 다시 종료해주세요.',True);return
        self._shutdown_started=True;self.jobs.close();self.session.close();self._wait_shutdown()
    def _wait_shutdown(self):
        if self.session.closed:
            self.closed=True
            if self._ui_timer:
                try:self.root.after_cancel(self._ui_timer)
                except Exception:pass
            self.root.destroy()
        else:self.root.after(100,self._wait_shutdown)

class MaterialUpdateAdapter:
    def __init__(self,app):self.app=app
    def begin(self):pass
    def saved(self):
        if self.app.session.outbox.items() or self.app.job_callbacks or self.app.writes or (self.app.quick_bridge and self.app.quick_bridge.has_pending()):
            raise RuntimeError('소재 입력 저장 또는 조회 결과 확인을 마친 뒤 다시 업데이트해주세요.')
        return True
    def finish(self):self.app.shutdown()

def boot():
    import tkinter as tk
    from tkinter import messagebox
    # The integrated entry point bypasses core.main(). Give this process its own
    # taskbar identity so Windows uses the existing graph window icon.
    if os.name == 'nt':
        try:
            import ctypes
            identify = ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID
            identify.argtypes = [ctypes.c_wchar_p]
            identify.restype = ctypes.c_long
            identify('Jihunius.MaterialCounter')
        except (AttributeError, OSError):
            pass
    folder=core.default_folder();folder.mkdir(parents=True,exist_ok=True)
    root=tk.Tk();root.withdraw();lock=None;session=None
    try:
        lock=core.InstanceLock(folder/'sync-ui.lock')
        shared=os.environ.get('JIHUNIUS_MATERIAL_SHARED',DEFAULT_SHARE)
        session=ClientSession(folder,shared)
        app=SyncedApplication(root,session)
        if hasattr(core,'CompanionWindowState'):app.placement=core.CompanionWindowState(root,'material')
        if hasattr(core,'CompanionUpdateBridge'):app.update_bridge=core.CompanionUpdateBridge(root,MaterialUpdateAdapter(app))
        if os.environ.get('JIHUNIUS_MATERIAL_HIDDEN')!='1':root.after_idle(app.show_front)
        else:session.visible=False
        root.mainloop()
    except Exception as exc:
        messagebox.showerror(TITLE,str(exc),parent=root)
    finally:
        if session is not None:session.close();session.thread.join(15)
        if lock is not None:lock.close()
        try:root.destroy()
        except Exception:pass
