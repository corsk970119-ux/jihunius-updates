"""Save adapters, appended only to the matching embedded companion application."""


class ProtrusionUpdateSave:
    def __init__(self, app):
        self.app = app

    def begin(self):
        app = self.app
        if app.closing or app.closed or not app.ready:
            raise RuntimeError('돌출량표 연결과 저장 상태를 먼저 확인해 주세요.')
        app._memo_changed()
        self.sequence = app._update_sync_sequence
        self.error_sequence = app._update_error_sequence
        app._start_sync()

    def saved(self):
        app = self.app
        if app._update_error_sequence != self.error_sequence:
            raise RuntimeError('돌출량표를 공유폴더에 저장하지 못했습니다. 입력을 유지합니다.')
        return (app._update_sync_sequence > self.sequence and not app.busy
                and not app.pending and not app.resolving_conflicts and not app.last_error)

    def finish(self):
        self.app._destroy()


class WashLogUpdateSave:
    def __init__(self, app):
        self.app = app

    @staticmethod
    def draft_path():
        return CONFIG_DIR / 'update_note_draft.json'

    @classmethod
    def restore_draft(cls, app):
        # A draft is local input, never a note-posting operation.
        draft = cls.read_draft()
        if draft and draft.get('folder') == app.cfg.get('folder', DEFAULT_FOLDER):
            if isinstance(draft.get('text'), str) and not app.note_input.get('1.0', 'end-1c'):
                app.note_input.insert('1.0', draft['text'])
                if isinstance(draft.get('dept'), str): app.dept.set(draft['dept'])
                app.note_feedback.set('업데이트 전 작성하던 메모 · Enter로 전송')
                try: cls.draft_path().unlink()
                except FileNotFoundError: pass

    @classmethod
    def read_draft(cls):
        try:
            value = json.loads(cls.draft_path().read_text(encoding='utf-8'))
            return value if isinstance(value, dict) else {}
        except FileNotFoundError: return {}

    def begin(self):
        app = self.app
        if app.closing or not app.connected or not app.online or app.connecting:
            raise RuntimeError('세척일보 공유폴더 연결을 먼저 확인해 주세요.')
        if any(op.get('kind') == 'day' for op in app.pending_updates.values()):
            raise RuntimeError('세척일보 날짜 변경이 끝난 뒤 다시 눌러 주세요.')
        app.cancel_plate_drag()
        self.failure_count = len(app.failed_operations)
        self.error_sequence = app._update_error_sequence
        if app.edit and not app.edit['saving']: app.edit['commit']()
        for index in range(len(app.toolvars)): app.submit_tool(index)

    def saved(self):
        app = self.app
        if (not app.online or len(app.failed_operations) > self.failure_count
                or app._update_error_sequence != self.error_sequence):
            raise RuntimeError('세척일보 저장에 실패했습니다. 현재 창과 입력을 유지합니다.')
        if (app.busy or app.pending_updates or app.edit or app.tool_drafts
                or any(v.get() != app.data['tools'][i] for i, v in enumerate(app.toolvars))):
            return False
        app.save_config()
        old = self.read_draft()
        if old.get('text') and old.get('folder') != app.active_folder:
            raise RuntimeError('다른 공유폴더의 작성 중 메모가 보관돼 있습니다. 먼저 확인해 주세요.')
        return True

    def finish(self):
        app = self.app
        _cu_write(self.draft_path(), {'folder': app.active_folder,
                                    'text': app.note_input.get('1.0', 'end-1c'), 'dept': app.dept.get()})
        app.closing = True
        app.stop.set()
        app.destroy()
