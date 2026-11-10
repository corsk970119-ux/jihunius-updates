"""오류 기록의 고정 형식([환경]→[진단]→[추적])과 세척완료 진단 정보, AI 전달용 복사."""
import os, tempfile, time, unittest
from pathlib import Path
from types import SimpleNamespace
from test_error_history import eh
from test_host_stability import load_app


class DetailLayoutTests(unittest.TestCase):
    def test_sections_keep_a_fixed_order_and_fit_the_stored_limit(self):
        text = eh.compose_detail('POP 목록 72줄', 'Traceback\n' + 'x' * 40000, 'Windows 10 · 배율 165%')
        self.assertTrue(text.startswith('[환경] Windows 10 · 배율 165%\n[진단]\nPOP 목록 72줄\n[추적]\n'))
        self.assertLessEqual(len(text), 16384)        # 저장 한도 안: 앞쪽 [환경]·[진단]이 잘리지 않음
        self.assertTrue(text.endswith('x' * 100))     # 추적 정보는 끝부분을 남김
        self.assertEqual(eh.compose_detail('', '', ''), '')
        self.assertEqual(eh.compose_detail('', 'trace only', ''), '[추적]\ntrace only')

    def test_recorder_stores_environment_and_context_with_every_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            recorder = eh.Recorder(Path(tmp) / 'h.sqlite', '지후니우스', '2026.11.11.3')
            recorder.environment = 'TestOS · Python 3.8'
            recorder.capture('버튼이 다른 창에 가려져 있어 중단했습니다.', feature='세척완료', stage='POP 미반영 항목 재확인',
                             detail='Traceback (most recent call last): …', context='POP 목록 72줄\n체크 클릭 12회')
            recorder.capture('알림만 있는 오류', stage='오류 알림')
            recorder.events.join(); recorder.close()
            rows = sorted(eh.LocalStore(Path(tmp) / 'h.sqlite').view()['records'], key=lambda r: r['stage'])
        wash = next(r for r in rows if r['feature'] == '세척완료')
        self.assertEqual(wash['detail'].split('\n')[0], '[환경] TestOS · Python 3.8')
        self.assertIn('[진단]\nPOP 목록 72줄\n체크 클릭 12회\n[추적]\nTraceback', wash['detail'])
        plain = next(r for r in rows if r['feature'] == '지후니우스')
        self.assertEqual(plain['detail'], '[환경] TestOS · Python 3.8')

    def test_long_context_keeps_summary_and_latest_lines(self):
        context = '요약 줄\n' + '\n'.join('기록 {:04d} '.format(i) + 'x' * 60 for i in range(400))
        text = eh.compose_detail(context, 'trace', 'env')
        self.assertIn('요약 줄', text); self.assertIn('기록 0399', text); self.assertIn('(가운데 생략)', text)
        self.assertNotIn('기록 0200', text); self.assertLessEqual(len(text), 16384)

    def test_traceback_is_recorded_even_when_the_caller_passes_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = eh._recorder
            eh._recorder = eh.Recorder(Path(tmp) / 'h.sqlite', '지후니우스', 'test')
            try:
                try: raise OSError('공유 폴더 없음')
                except OSError as error: eh.capture(error, feature='인수인계', stage='읽기')   # 예외 객체
                try: {}['없는키']
                except KeyError: eh.capture('설정 읽기 실패', feature='설정', stage='불러오기')    # 처리 중인 예외
                eh.capture('그냥 안내', feature='안내', stage='표시')                               # 예외 없음
                eh._recorder.events.join(); eh._recorder.close()
                rows = {r['feature']: r['detail'] for r in eh.LocalStore(Path(tmp) / 'h.sqlite').view()['records']}
            finally:
                eh._recorder = previous
        self.assertIn("[추적]\nTraceback", rows['인수인계']); self.assertIn('OSError: 공유 폴더 없음', rows['인수인계'])
        self.assertIn("KeyError: '없는키'", rows['설정'])
        self.assertNotIn('[추적]', rows['안내'])

    def test_environment_never_raises(self):
        self.assertIn('Python', eh.environment())


class WashDiagnosticsTests(unittest.TestCase):
    def wash(self):
        module = load_app()
        app = module.WashApp.__new__(module.WashApp)
        app.started = time.monotonic() - 95; app.trail = []; app.reads = []; app.progress = {}; app.last_result = None
        app.run_sequence = '07'
        app.stop = SimpleNamespace(is_set=lambda: False); app.events = SimpleNamespace(put=lambda item: None)
        return module, app

    def test_error_record_carries_progress_counts_and_recent_steps(self):
        module, app = self.wash()
        captured = []
        original = module.SuiteErrors.capture
        module.SuiteErrors.capture = lambda *args, **kwargs: captured.append((args, kwargs))
        try:
            for index in range(60):
                app.emit('log', '진행 {}'.format(index))
            app.emit('result', {'coverage': {'declared_rows': 72, 'summary_supported': True, 'top_verified': True,
                                             'wheel_moves': 4, 'basis': 'MSAA 전체 행과 셀 직접 판독',
                                             'raw': [['선택안됨'] * 23] * 72, 'current_view': {'visible': dict.fromkeys(range(18))}},
                                'matching': {'matched': [1] * 40, 'already_selected': [1, 2]}})
            for _ in range(12): app.emit('check', {'status': 'attempt'})
            for _ in range(11): app.emit('check', {'status': 'verified'})
            app.reads += [('POP 조회 후 전체 목록 1회 판독', 'pop_full', 61.2, 5120), ('POP 아래로 확인 1', 'mes_rows', 0.8, 300)]
            app.emit('reading', ('POP 미반영 항목 재확인', time.monotonic()))
            app.emit('error', '버튼이 다른 창에 가려져 있어 중단했습니다.')
        finally:
            module.SuiteErrors.capture = original
        (args, kwargs), = captured
        self.assertEqual(kwargs['stage'], 'POP 미반영 항목 재확인')
        context = kwargs['context']
        for expected in ('경과 9', '세척순번 07', 'POP 표: 한 줄 23칸 · 화면에 보이는 줄 18',
                         'POP 목록 72줄 · 행 요약값 사용 · 맨 위 확인 예 · 맨 아래 확인 아니오 · 아래로 이동 1회',
                         '매칭 대상 40개 · 이미 선택 2개', '체크 클릭 12회 · 체크 확인 11개',
                         '화면 판독 2회 · 합계 62.0초 · 가장 오래: POP 조회 후 전체 목록 1회 판독 (pop_full · 61.2초 · 항목 5120개)',
                         '마지막 판독: POP 조회 후 전체 목록 1회 판독 (pop_full · 61.2초) → POP 아래로 확인 1 (mes_rows · 0.8초)',
                         '[진행 기록 · 처음 8줄 + 최근 32줄]', '진행 0\n', '진행 7\n', '줄 생략', '진행 59',
                         '중단: 버튼이 다른 창에 가려져'):
            self.assertIn(expected, context)
        self.assertNotIn('진행 19\n', context)   # 가운데는 줄임: 시작 상황과 멈추기 직전이 남음

    def test_diagnostics_failure_never_blocks_the_error_record(self):
        module, app = self.wash()
        app.progress = None    # 고의로 망가뜨림
        self.assertIn('진단 정보를 만들지 못했습니다', app.diagnostics())


@unittest.skipUnless(os.environ.get('DISPLAY') or os.name == 'nt', 'requires Tk display')
class AiCopyTests(unittest.TestCase):
    def test_ai_copy_has_selected_record_and_recent_list_in_fixed_labels(self):
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog
        with tempfile.TemporaryDirectory() as tmp:
            m = load_app(); e = m.SuiteErrors; root = tk.Tk()
            label = ttk.Label(root, text='지후니우스'); label.pack()
            app = SimpleNamespace(window=root, tk=tk, ttk=ttk, title_label=label, messagebox=messagebox, filedialog=filedialog)
            e._recorder = e.Recorder(Path(tmp) / 'main.sqlite', '지후니우스', 'test')
            share = Path(tmp) / 'share'; share.mkdir()
            store = e.LocalStore(Path(tmp) / 'pc.sqlite', 'pc8')
            store.record('세척완료', '버튼이 다른 창에 가려져 있어 중단했습니다.', stage='POP 미반영 항목 재확인', version='2026.11.11.3',
                         detail=e.compose_detail('POP 목록 72줄', 'Traceback …', 'Windows 10'))
            store.record('드라이브 정리', "[WinError 87] 매개 변수가 틀립니다", stage='새로고침', version='2026.11.11.3')
            request = store.request(); store.accept(request, e.sync_shared(share, request))
            ui = e.HistoryUI(app, share, e.SYNC_SOURCE)
            try:
                ui.open(); end = time.monotonic() + 4
                while len(ui.tree.get_children()) != 2 and time.monotonic() < end: root.update(); time.sleep(.02)
                wash = next(r['id'] for r in ui.rows.values() if r['feature'] == '세척완료')
                ui.tree.selection_set(wash); root.update(); ui.copy_for_ai()
                text = root.clipboard_get()
            finally:
                ui.close(); ui.service.close(); e._recorder.close(); root.destroy()
        self.assertTrue(text.startswith('===== 지후니우스 오류 기록 (AI 전달용) ====='))
        for expected in ('[선택한 오류]', '버전: 2026.11.11.3', 'PC: pc8', '기능: 세척완료', '단계: POP 미반영 항목 재확인',
                         '오류: 버튼이 다른 창에 가려져 있어 중단했습니다.', '--- 상세 정보 ---', '[환경] Windows 10',
                         '[진단]\nPOP 목록 72줄', '[최근 오류 목록 · 2건 / 표시 2건]', '| 드라이브 정리 | 새로고침 |'):
            self.assertIn(expected, text)


if __name__ == '__main__':
    unittest.main()
