"""세척완료 안전장치: 읽기 한도 안내, 여러 PC 동시 실행 표시. POP/MES 프로그램에는 접속하지 않습니다."""
import ast, json, re, tempfile, time, tkinter as tk, unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import test_main_window_placement as placement
from test_host_stability import load_app

ROOT = Path(__file__).resolve().parents[1]


def wash_source(name):
    tree = ast.parse((ROOT / 'apps/jihunius/app.pyw').read_text(encoding='utf-8'))
    return ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign)
                                 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name))


def check_capture():
    source = wash_source('WASH_POP_SOURCE')
    parts = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'check_capture']
    scope = {'re': re}
    exec(compile(ast.Module(body=parts, type_ignores=[]), '<check_capture>', 'exec'), scope)
    return scope['check_capture']


class ReaderLimitTests(unittest.TestCase):
    def test_limits_are_relaxed_in_both_readers_and_python_waits_longer(self):
        for name in ('WASH_POP_SOURCE', 'WASH_MES_SOURCE'):
            source = wash_source(name)
            self.assertIn('count>=120000 || clock.Elapsed.TotalSeconds>=300', source, name)
            self.assertIn('deadline = time.monotonic()+330', source, name)
        app = (ROOT / 'src/host/jihunius_main.py').read_text(encoding='utf-8')
        self.assertIn('deadline=start+330', app)

    def test_limited_capture_names_the_reader_limit(self):
        check = check_capture()
        ok = dict(exit_code=0, records=[dict(kind='element'), dict(kind='finish', limited=False)])
        check(ok)
        limited = dict(exit_code=0, records=[dict(kind='finish', limited=True, elements=40000, seconds=12.4)])
        with self.assertRaisesRegex(RuntimeError, '읽기 한도.*40000개 · 12초'):
            check(limited)
        broken = dict(exit_code=1, records=[dict(kind='finish', limited=False)])
        with self.assertRaisesRegex(RuntimeError, '화면을 충분히 읽지 못해'):
            check(broken)


class RunMarkerTests(unittest.TestCase):
    def setUp(self):
        self.m = load_app()
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)

    def test_other_pc_marker_is_reported_and_own_marker_is_removed(self):
        now = [1000.0]
        first = self.m.WashRunMarker(self.folder, pc='PC-A', clock=lambda: now[0])
        second = self.m.WashRunMarker(self.folder, pc='PC-B', clock=lambda: now[0])
        self.assertIsNone(second.other())
        self.assertTrue(first.write())
        self.assertIsNone(first.other(), 'same PC is never a conflict')
        self.assertEqual(second.other()['pc'], 'PC-A')
        self.assertFalse(second.release(), 'not owned')
        self.assertTrue((self.folder / self.m.WASH_RUN_MARKER_NAME).exists())
        now[0] += self.m.WASH_RUN_MARKER_STALE_SECONDS + 1
        self.assertIsNone(second.other(), 'stale marker is ignored')
        self.assertTrue(first.release())
        self.assertFalse((self.folder / self.m.WASH_RUN_MARKER_NAME).exists())
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_newer_run_from_another_pc_is_not_deleted(self):
        mine = self.m.WashRunMarker(self.folder, pc='PC-A')
        other = self.m.WashRunMarker(self.folder, pc='PC-B')
        self.assertTrue(mine.write()); self.assertTrue(other.write())
        self.assertFalse(mine.release())
        self.assertEqual(json.loads((self.folder / self.m.WASH_RUN_MARKER_NAME).read_text(encoding='utf-8'))['pc'], 'PC-B')

    def test_missing_folder_or_bad_file_never_blocks(self):
        missing = self.m.WashRunMarker(self.folder / 'none', pc='PC-A')
        self.assertFalse(missing.write()); self.assertIsNone(missing.other()); self.assertFalse(missing.release())
        (self.folder / self.m.WASH_RUN_MARKER_NAME).write_text('{broken', encoding='utf-8')
        self.assertIsNone(self.m.WashRunMarker(self.folder, pc='PC-B').other())

    def test_bounded_wait_returns_none_on_timeout_or_error(self):
        self.assertEqual(self.m.run_bounded(lambda: 7), 7)
        self.assertIsNone(self.m.run_bounded(lambda: time.sleep(1), seconds=0.05))
        self.assertIsNone(self.m.run_bounded(lambda: 1 / 0))


class ScaledLayoutTests(unittest.TestCase):
    setUp = placement.MainWindowPlacementTests.setUp
    cleanup = placement.MainWindowPlacementTests.cleanup
    close_app = placement.MainWindowPlacementTests.close_app

    def launch(self, scale):
        root = tk.Tk(); root.tk.call('tk', 'scaling', scale)
        app = self.m.IntegrationApp(root); self.apps.append(app); root.update(); return app

    def test_machine_text_and_alert_switch_do_not_overlap_when_scaled(self):
        for scale in (96 / 72, 2.2):
            app = self.launch(scale)
            app.apply_machine_status({1: {'light': 'green', 'state': 'RUN', 'prm_no': '6001', 'details': {'tool_number': '0101'}}})
            app.window.update()
            tile, light, number = app.machine_tiles[1]
            title = tile.bbox('machine_title'); digits = tile.bbox(number)
            tool = tile.bbox('machine_tool'); state = tile.bbox('machine_state')
            with self.subTest(scale=scale):
                self.assertLessEqual(title[3], digits[1] + 3)
                self.assertLessEqual(digits[3], int(tile.cget('height')) + 1)
                # 공구 번호: 프로그램 번호 오른쪽에 겹치지 않고, 칸 안에, 상태 글자 아래에.
                self.assertEqual(tile.itemcget('machine_tool', 'text'), 'T0101')
                self.assertGreater(tool[0], digits[2])
                self.assertLessEqual(tool[2], tile.winfo_width())
                self.assertLessEqual(tool[3], int(tile.cget('height')) + 1)
                self.assertLessEqual(state[3], tool[1] + 3)
                canvas = app.machine_alert_toggle
                labels = [canvas.bbox(i) for i in canvas.find_all() if canvas.type(i) == 'text'][:2]
                switch = [canvas.bbox(i) for i in canvas.find_all() if canvas.type(i) == 'image'][0]
                self.assertLess(max(b[2] for b in labels), switch[0])
            if scale == 96 / 72:
                layout = app.machine_alert_toggle_layout()
                self.assertEqual((layout['switch_x'], layout['switch_y']), (81, 8))
            self.close_app(app)

    def test_date_folder_starts_with_today(self):
        app = self.launch(96 / 72)
        today = datetime.now()
        self.assertEqual(app.folder_input.get(), '{}.{:02d}'.format(today.month, today.day))
        self.m.date_search_folders(app.folder_input.get(), today.year)


if __name__ == '__main__':
    unittest.main()
