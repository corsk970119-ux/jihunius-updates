"""오류 기록 기능을 없앴다(사용자 요청 2026-11-24: "오류기록 기능은 이제 없어도 될듯함").

버튼·창·기록·공유 동기화와, 기록을 위해 프로그램 곳곳에 끼워 넣던 것들이 더는 없어야 한다.
같은 날 소재 사용량 조사의 "(Beta)" 표기도 뗐다("소재사용량조사에 (beta) 이것도 없애주고").
"""
import ast
import os
import queue
import sys
import threading
import tkinter as tk
import unittest
from pathlib import Path
from tkinter import messagebox
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'src'))
import build_app
from embed_companions import companion_source
from test_host_stability import load_app
import test_main_window_placement as placement

GONE = ('SuiteErrors', 'jihunius_error_history', '_diagnostic_error', '_err_module', 'JIHUNIUS_APP_VERSION', 'error_history')


class RemovedEverywhereTests(unittest.TestCase):
    def test_modules_and_every_hook_are_gone_from_the_sources_and_the_built_program(self):
        self.assertFalse((ROOT / 'src/error_history.py').exists())
        self.assertFalse((ROOT / 'src/error_history_ui.py').exists())
        texts = {str(path.relative_to(ROOT)): path.read_text(encoding='utf-8')
                 for folder in ('src', 'src/host', 'tools') for path in sorted((ROOT / folder).glob('*.py'))}
        texts['apps/jihunius/app.pyw'] = (ROOT / 'apps/jihunius/app.pyw').read_text(encoding='utf-8')
        for key in ('protrusion', 'wash-log', 'special-table', 'material'):
            texts['companion ' + key] = companion_source(ROOT, key).decode('utf-8')
        for name, text in texts.items():
            for word in GONE:
                self.assertNotIn(word, text, '{}: {}'.format(name, word))

    def test_starting_the_program_no_longer_wraps_message_boxes_or_error_handlers(self):
        m = load_app()
        before = (messagebox.showerror, messagebox.showwarning, tk.Tk.report_callback_exception,
                  sys.excepthook, getattr(threading, 'excepthook', None))
        with patch.object(m.SuiteUpdater, 'managed_context', return_value={'test': True}), \
                patch.object(m.SuiteUpdater, 'managed_lease', return_value=Mock()), \
                patch.object(m.SuiteUpdater, 'attach'), patch.object(m.SuiteUpdater, 'mark_ready'), \
                patch.object(m.SuiteStorage, 'startup_check'), patch.object(m.SuiteStorage, 'attach'), \
                patch.object(m, 'configure_windows_app_identity'), \
                patch.object(m, 'IntegrationApp', return_value=Mock()), patch('tkinter.Tk', return_value=Mock()):
            m.main()
        self.assertEqual((messagebox.showerror, messagebox.showwarning, tk.Tk.report_callback_exception,
                          sys.excepthook, getattr(threading, 'excepthook', None)), before)
        self.assertFalse(hasattr(m, 'SuiteErrors'))

    def test_wash_completion_only_forwards_what_the_screen_shows(self):
        m = load_app()
        for name in ('note', 'diagnostics'):
            self.assertFalse(hasattr(m.WashApp, name), name)       # 오류 기록에만 쓰이던 진행 기록·진단
        wash = m.WashApp.__new__(m.WashApp)
        wash.events = queue.Queue()
        wash.stop = threading.Event()
        for kind, value in (('log', '조건 확인 중'), ('reading', ('MES 구조', 1.0)), ('check', {'status': 'attempt'}),
                            ('result', {'ok': True}), ('error', '체크 칸이 가려져 중단'), ('reading_done', None), ('done', None)):
            wash.emit(kind, value)
        seen = []
        while not wash.events.empty():
            seen.append(wash.events.get())
        self.assertEqual([kind for kind, _ in seen], ['log', 'reading', 'result', 'error', 'reading_done', 'done'])
        self.assertEqual(dict(seen)['error'], '체크 칸이 가려져 중단')   # 화면에 띄울 오류 문구는 그대로 전달

    def test_material_survey_is_named_without_beta_everywhere_the_name_is_matched(self):
        import material_ui
        self.assertEqual(material_ui.TITLE, '소재 사용량 조사')
        self.assertEqual(build_app.COMPANION_TITLES['material'], material_ui.TITLE)   # 메인이 이 제목으로 창을 찾음
        built = ast.parse((ROOT / 'apps/jihunius/app.pyw').read_text(encoding='utf-8'))
        payloads = next(ast.literal_eval(node.value) for node in built.body
                        if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'SUITE_COMPANIONS')
        self.assertEqual(payloads['material']['title'], '소재 사용량 조사')
        host = (ROOT / 'src/host/jihunius_main.py').read_text(encoding='utf-8')
        self.assertNotIn('조사(Beta)', host)
        self.assertNotIn('조사(Beta)', companion_source(ROOT, 'material').decode('utf-8'))


@unittest.skipUnless(os.environ.get('DISPLAY') or os.name == 'nt', 'requires Tk display')
class MainWindowTests(unittest.TestCase):
    setUp = placement.MainWindowPlacementTests.setUp
    cleanup = placement.MainWindowPlacementTests.cleanup
    close_app = placement.MainWindowPlacementTests.close_app
    launch = placement.MainWindowPlacementTests.launch

    def test_there_is_no_error_record_button_and_the_material_button_has_no_beta(self):
        app = self.launch()

        def widgets(widget):
            yield widget
            for child in widget.winfo_children():
                yield from widgets(child)

        texts = [str(widget.cget('text')) for widget in widgets(app.window)
                 if widget.winfo_class() in ('TButton', 'TLabel', 'TRadiobutton')]
        self.assertEqual([text for text in texts if '오류 기록' in text], [])
        self.assertEqual([text for text in texts if 'Beta' in text], [])
        self.assertEqual(app.material_button.cget('text'), '소재 사용량 조사')
        self.assertEqual(app.header_actions.winfo_children(), [])   # 업데이트 버튼은 실행할 때 붙음(이 시험에서는 없음)
        self.assertFalse(hasattr(app, 'error_history'))


if __name__ == '__main__':
    unittest.main()
