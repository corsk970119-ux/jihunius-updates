"""Tk view for event-only errors; appended to error_history by the builder."""

class HistoryUI:
    def __init__(self, app, folder, helper_source):
        self.app=app;self.root=app.window;self.dialog=None;self.rows={};self.signature=None
        style=app.ttk.Style(self.root)
        style.configure('ErrorHistory.Treeview',background='#050a14',fieldbackground='#050a14',
                        foreground='#eaf0fc',rowheight=28,borderwidth=0,font=('맑은 고딕',10))
        style.map('ErrorHistory.Treeview',background=[('selected','#1d3f86')],foreground=[('selected','#ffffff')])
        style.configure('ErrorHistory.Treeview.Heading',background='#0e1a35',foreground='#eaf0fc',
                        padding=(8,8),font=('맑은 고딕',10,'bold'),relief='flat')
        style.map('ErrorHistory.Treeview.Heading',background=[('active','#22355c')])
        style.configure('ErrorHistory.TCheckbutton',background='#060b16',foreground='#ccced2')
        style.map('ErrorHistory.TCheckbutton',background=[('active','#060b16')],foreground=[('active','#ffffff')])
        style.configure('ErrorHistory.TLabel',background='#060b16',foreground='#9fb2d6',font=('맑은 고딕',9))
        self.service=Service(_recorder.path,folder,helper_source)
        self.button=app.ttk.Button(getattr(app,'header_actions',app.title_label.master),text='오류 기록',style='Popup.TButton',command=self.open)
        self.button.pack(side='right',padx=(6,0))
        self.timer=self.root.after(500,self.poll)
        self.root.bind('<Destroy>',self.destroyed,add='+')

    def destroyed(self,event):
        if event.widget is self.root:
            self.service.close()
            if self.timer:
                try:self.root.after_cancel(self.timer)
                except self.app.tk.TclError:pass

    def poll(self):
        state=self.service.snapshot();unread=state.get('unread',0)
        self.button.configure(text='오류 기록'+(' '+str(unread) if unread else ''),
            style='HandoverNotice.TButton' if unread else 'Popup.TButton')
        if self.dialog is not None and self.dialog.winfo_exists():self.render(state)
        self.timer=self.root.after(500,self.poll)

    def open(self):
        tk=self.app.tk;ttk=self.app.ttk
        if self.dialog is not None and self.dialog.winfo_exists():
            self.dialog.lift();return
        win=self.dialog=tk.Toplevel(self.root);win.title('오류 기록 · 전체 PC');win.configure(bg='#060b16')
        win.geometry('1000x660');win.minsize(820,520);win.transient(self.root)
        win.protocol('WM_DELETE_WINDOW',self.close)
        body=ttk.Frame(win,padding=20);body.pack(fill='both',expand=True)
        body.columnconfigure(0,weight=1)
        body.rowconfigure(2,weight=3,minsize=80);body.rowconfigure(4,weight=2,minsize=70)
        ttk.Label(body,text='오류 기록',style='Title.TLabel').grid(row=0,column=0,sticky='w',pady=(0,12))
        bar=ttk.Frame(body);bar.grid(row=1,column=0,sticky='ew',pady=(0,12))
        self.filter=tk.StringVar(value='전체 PC');self.filter_map={'전체 PC':None}
        self.combo=ttk.Combobox(bar,textvariable=self.filter,state='readonly',width=24,values=['전체 PC'])
        self.combo.pack(side='left');self.combo.bind('<<ComboboxSelected>>',lambda e:self.render(self.service.snapshot(),True))
        self.enabled=tk.BooleanVar(value=self.service.snapshot()['enabled'])
        ttk.Checkbutton(bar,text='이 PC 오류 저장',variable=self.enabled,style='ErrorHistory.TCheckbutton',
                        command=lambda:self.service.command('enabled',self.enabled.get())).pack(side='left',padx=18)
        ttk.Button(bar,text='새로고침',style='Secondary.TButton',command=lambda:self.service.command('refresh')).pack(side='right')
        table=ttk.Frame(body);table.grid(row=2,column=0,sticky='nsew')
        self.tree=ttk.Treeview(table,columns=('pc','time','feature','message','count'),show='headings',selectmode='browse',height=10,style='ErrorHistory.Treeview')
        for key,label,width in [('pc','PC',135),('time','최근 발생',130),('feature','기능',110),('message','오류 내용',400),('count','횟수',55)]:
            self.tree.heading(key,text=label);self.tree.column(key,width=width,minwidth=45,stretch=key=='message')
        scroll=ttk.Scrollbar(table,command=self.tree.yview);self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y');self.tree.pack(fill='both',expand=True)
        self.tree.bind('<<TreeviewSelect>>',self.details)
        self.status=tk.StringVar();status_label=ttk.Label(body,textvariable=self.status,style='ErrorHistory.TLabel',wraplength=780)
        status_label.grid(row=3,column=0,sticky='ew',pady=10)
        body.bind('<Configure>',lambda event:status_label.configure(wraplength=max(300,event.width-40)),add='+')
        detail_frame=ttk.Frame(body);detail_frame.grid(row=4,column=0,sticky='nsew')
        self.detail=tk.Text(detail_frame,height=8,wrap='word',bg='#050a14',fg='#eaf0fc',relief='flat',padx=12,pady=10,
                            font=('맑은 고딕',10),state='disabled')
        detail_scroll=ttk.Scrollbar(detail_frame,command=self.detail.yview);self.detail.configure(yscrollcommand=detail_scroll.set)
        detail_scroll.pack(side='right',fill='y');self.detail.pack(fill='both',expand=True)
        footer=ttk.Frame(body);footer.grid(row=5,column=0,sticky='ew',pady=(16,0))
        ttk.Button(footer,text='선택 내용 복사',style='Secondary.TButton',command=self.copy).pack(side='left')
        ttk.Button(footer,text='AI 전달용 복사',style='Secondary.TButton',command=self.copy_for_ai).pack(side='left',padx=(8,0))
        ttk.Button(footer,text='기록 내보내기',style='Secondary.TButton',command=self.export).pack(side='left',padx=8)
        self.clear_button=ttk.Button(footer,text='전체 PC 기록 비우기',style='Danger.TButton',command=self.clear)
        self.clear_button.pack(side='right')
        self.signature=None;self.service.command('open',True);self.service.command('seen')
        self.render(self.service.snapshot(),True)

    def close(self):
        if self.dialog is not None:self.dialog.destroy();self.dialog=None
        self.service.command('open',False)

    @staticmethod
    def stamp(value):return time.strftime('%m-%d %H:%M:%S',time.localtime(value))

    def render(self,state,force=False):
        records=state.get('records',[])
        mapping={'전체 PC':None,'이 PC':state.get('pc_id')}
        for r in records:mapping[r['pc']+' · '+r['pc_id'][:6]]=r['pc_id']
        self.filter_map=mapping;self.combo.configure(values=list(mapping))
        if self.filter.get() not in mapping:self.filter.set('전체 PC')
        pc=mapping[self.filter.get()];shown=[r for r in records if pc is None or r['pc_id']==pc]
        signature=tuple((r['id'],r['last'],r['count']) for r in shown)
        if signature!=self.signature or force:
            selected=self.tree.selection();self.rows={r['id']:r for r in shown}
            children=self.tree.get_children()
            if children:self.tree.delete(*children)
            for r in shown:self.tree.insert('','end',iid=r['id'],values=(r['pc'],self.stamp(r['last']),r['feature'],r['message'].replace('\n',' '),r['count']))
            if selected and selected[0] in self.rows:self.tree.selection_set(selected[0])
            elif shown:self.tree.selection_set(shown[0]['id'])
            else:self.details()
            self.signature=signature
        self.enabled.set(state['enabled'])
        extra=(' · '+_recorder.error) if _recorder is not None and _recorder.error else ''
        self.status.set(f"{len(shown)}건 · 최근 100건 / 30일 · {state.get('status','')}"+extra)
        self.clear_button.configure(state='disabled' if state['pending_clear'] else 'normal')

    @staticmethod
    def full_stamp(value):return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(value))

    def record_text(self,r):
        """오류 1건을 항상 같은 순서·같은 이름표로(사람도 AI도 같은 자리에서 찾도록)."""
        return (f"버전: {r['version'] or '-'}\nPC: {r['pc']}\n기능: {r['feature']}\n단계: {r['stage'] or '-'}\n"
                f"발생: {self.full_stamp(r['last'])} (최초 {self.full_stamp(r['first'])} · {r['count']}회)\n"
                f"오류: {r['message']}"+('\n--- 상세 정보 ---\n'+r['detail'] if r['detail'] else ''))

    def selected_text(self):
        selection=self.tree.selection()
        if not selection or selection[0] not in self.rows:return ''
        return self.record_text(self.rows[selection[0]])

    def ai_text(self,limit=20):
        """선택한 오류 전체 + 화면에 표시된 최근 오류 목록. 그대로 붙여넣어 전달하는 용도."""
        rows=sorted(self.rows.values(),key=lambda r:r['last'],reverse=True)
        if not rows:return ''
        lines=['===== 지후니우스 오류 기록 (AI 전달용) =====','복사 시각: '+self.full_stamp(time.time()),'',
               '[선택한 오류]',self.selected_text() or '(선택 없음)','',
               f'[최근 오류 목록 · {min(limit,len(rows))}건 / 표시 {len(rows)}건] 발생 | PC | 버전 | 기능 | 단계 | 오류 | 횟수']
        for r in rows[:limit]:
            lines.append(' | '.join((self.full_stamp(r['last']),r['pc'],r['version'] or '-',r['feature'],r['stage'] or '-',
                                     r['message'].replace('\n',' ')[:160],f"{r['count']}회")))
        return '\n'.join(lines)

    def copy_for_ai(self):
        text=self.ai_text()
        if text:
            self.root.clipboard_clear();self.root.clipboard_append(text)
            self.status.set('AI 전달용으로 복사했습니다. 대화창에 그대로 붙여넣어 주세요.')

    def details(self,event=None):
        self.detail.configure(state='normal');self.detail.delete('1.0','end')
        self.detail.insert('1.0',self.selected_text() or '기록이 없습니다.');self.detail.configure(state='disabled')

    def copy(self):
        text=self.selected_text()
        if text:self.root.clipboard_clear();self.root.clipboard_append(text)

    def export(self):
        filename=self.app.filedialog.asksaveasfilename(parent=self.dialog,title='표시된 오류 기록 내보내기',
            defaultextension='.json',initialfile='지후니우스_오류기록.json',filetypes=[('JSON','*.json')])
        if not filename:return
        rows=list(self.rows.values())
        def write():
            try:
                with open(filename,'w',encoding='utf-8') as f:json.dump(rows,f,ensure_ascii=False,indent=2)
            except Exception as exc:capture(exc,feature='오류 기록',stage='내보내기')
        threading.Thread(target=write,daemon=True).start()

    def clear(self):
        if self.app.messagebox.askyesno('전체 PC 기록 비우기',
            '모든 PC의 오류 기록을 비울까요?\n업무 데이터는 유지됩니다.\n\n연결되지 않은 PC는 다음 연결 때 기존 오류 기록을 비웁니다.',
            parent=self.dialog,default='no'):
            self.clear_button.configure(state='disabled');self.service.command('clear')


def attach(app,folder):
    install('지후니우스',getattr(sys.modules.get(app.__class__.__module__),'SUITE_APP_VERSION',''))
    app.error_history=HistoryUI(app,folder,SYNC_SOURCE)
    return app.error_history
