"""창 맨 위 제목 줄을 어둡게: 메인 창과 거기서 여는 창 모두(Windows 호출은 가짜로 대체). 세척일보 창 제목."""
import ast, os, sys, tkinter as tk, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
import visual_theme
import build_app
from embed_companions import companion_source


@unittest.skipUnless(os.environ.get('DISPLAY') or os.name == 'nt', 'requires Tk display')
class DarkTitlebarTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk(); self.addCleanup(self.root.destroy)
        self.painted = []; self.errors = []
        self.root.report_callback_exception = lambda *details: self.errors.append(details)

    def install(self, paint=None):
        return visual_theme.install_dark_titlebars(self.root, _paint=paint or self.painted.append)

    def test_the_window_and_the_windows_opened_from_it_are_darkened_when_they_appear(self):
        self.assertTrue(self.install())
        inner = [tk.Label(self.root, text=str(index)) for index in range(30)]
        for label in inner: label.pack()
        self.root.update()
        self.assertEqual(self.painted, [self.root.winfo_id()])          # 안의 칸 30개가 나타날 때는 불리지 않음
        dialog = tk.Toplevel(self.root); tk.Button(dialog, text='확인').pack()
        self.root.update()
        self.assertEqual(self.painted, [self.root.winfo_id(), dialog.winfo_id()])
        second = tk.Toplevel(dialog); second.withdraw(); self.root.update()
        self.assertEqual(len(self.painted), 2)                           # 숨겨 둔 창은 아직
        second.deiconify(); self.root.update()
        self.assertEqual(self.painted[2:], [second.winfo_id()])          # 보일 때
        self.assertEqual(self.errors, [])

    def test_windows_without_a_title_bar_are_left_alone(self):
        self.install(); self.root.update(); del self.painted[:]
        tip = tk.Toplevel(self.root); tip.overrideredirect(True); tk.Label(tip, text='말풍선').pack()
        self.root.update()
        self.assertEqual(self.painted, [])

    def test_a_window_that_is_already_showing_is_darkened_at_once(self):
        self.root.update()
        self.install()
        self.assertEqual(self.painted, [self.root.winfo_id()])

    def test_it_is_installed_once_and_a_failure_never_reaches_the_window(self):
        def broken(window_id):
            self.painted.append(window_id); raise OSError('dwm')
        self.assertTrue(self.install(broken))
        self.assertFalse(self.install(broken))                           # 두 번 걸지 않음
        tk.Toplevel(self.root); self.root.update()
        self.assertEqual(len(self.painted), 2)                           # 창마다 한 번씩만
        self.assertEqual(self.errors, [])
        self.assertTrue(self.root.winfo_exists())

    def test_size_and_place_of_the_window_stay_the_same(self):
        self.root.geometry('420x300+40+60'); self.root.update()
        before = self.root.geometry()
        self.install(); dialog = tk.Toplevel(self.root); dialog.geometry('200x120+80+90'); self.root.update()
        self.assertEqual(self.root.geometry(), before)
        self.assertEqual(dialog.geometry(), '200x120+80+90')

    def test_nothing_is_installed_outside_windows(self):
        if os.name == 'nt': self.skipTest('Windows에서는 실제로 겁니다')
        self.assertFalse(visual_theme.install_dark_titlebars(self.root))
        self.assertFalse(self.root.bind_class('Toplevel', '<Map>'))

    def test_windows_is_asked_for_the_dark_title_bar_of_the_outer_frame(self):
        import ctypes
        for supported, expected in ((20, [20]), (19, [20, 19]), (None, [20, 19])):
            root = tk.Tk(); self.addCleanup(root.destroy)
            calls = []
            def ancestor(window_id, kind):
                self.assertEqual(kind, 2); return window_id + 1000        # 제목 줄이 달린 바깥 창
            def attribute(frame, name, value, size):
                calls.append((frame, name, value._obj.value, size)); return 0 if name == supported else -1
            user = type('User', (), {'GetAncestor': staticmethod(ancestor)})
            dwm = type('Dwm', (), {'DwmSetWindowAttribute': staticmethod(attribute)})
            libraries = {'user32': user, 'dwmapi': dwm}
            with patch('os.name', 'nt'), patch.object(ctypes, 'WinDLL', lambda name, **kwargs: libraries[name], create=True):
                self.assertTrue(visual_theme.install_dark_titlebars(root))
            root.update()
            self.assertEqual(calls, [(root.winfo_id() + 1000, name, 1, 4) for name in expected], supported)


class DarkTitlebarWiringTests(unittest.TestCase):
    def test_every_window_installs_it(self):
        main = (ROOT / 'src/host/jihunius_main.py').read_text(encoding='utf-8')
        self.assertIn('SuiteVisualTheme.install_dark_titlebars(window)', main)
        calls = {'protrusion': 'install_dark_titlebars(self.root)', 'special-table': 'install_dark_titlebars(r)',
                 'wash-log': 'install_dark_titlebars(self)', 'material': 'install_dark_titlebars(self.root)'}
        for key, call in calls.items():
            source = companion_source(ROOT, key).decode('utf-8')
            self.assertIn(call, source, key)
            self.assertIn('def install_dark_titlebars(root, _paint=None):', source, key)   # 그 창에 함께 실림

    def test_helper_carried_into_the_wash_log_and_material_windows_stands_alone(self):
        # 세척일보·소재 창에는 visual_theme 전체가 아니라 함수만 실리므로, 함수 밖의 이름을 쓰면 안 됩니다.
        tree = ast.parse((ROOT / 'src/visual_theme.py').read_text(encoding='utf-8'))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'install_dark_titlebars')
        module = ast.Module(body=[function], type_ignores=[])
        scope = {}
        exec(compile(module, '<install_dark_titlebars>', 'exec'), scope)
        self.assertFalse(scope['install_dark_titlebars'](object(), _paint=lambda window_id: None))   # 창이 아니면 조용히 그만둠
        if os.environ.get('DISPLAY') or os.name == 'nt':
            root = tk.Tk(); self.addCleanup(root.destroy); painted = []
            self.assertTrue(scope['install_dark_titlebars'](root, _paint=painted.append))
            root.update(); self.assertEqual(painted, [root.winfo_id()])


class WashLogTitleTests(unittest.TestCase):
    def test_wash_log_window_is_titled_just_wash_log_and_the_main_program_looks_for_that_title(self):
        tree = ast.parse((ROOT / 'src/wash_log.py').read_text(encoding='utf-8'))
        app = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'App')
        init = next(node for node in app.body if isinstance(node, ast.FunctionDef) and node.name == '__init__')
        titles = [call.args[0].value for call in ast.walk(init)
                  if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'title'
                  and isinstance(call.func.value, ast.Name) and call.func.value.id == 'self'
                  and call.args and isinstance(call.args[0], ast.Constant)]
        self.assertEqual(titles, ['세척일보'])
        # 메인은 이 제목으로 세척일보 창을 찾아 앞으로 가져오고 닫습니다 — 글자 하나까지 같아야 합니다.
        self.assertEqual(build_app.COMPANION_TITLES['wash-log'], '세척일보')
        built = ast.parse((ROOT / 'apps/jihunius/app.pyw').read_text(encoding='utf-8'))
        payloads = next(ast.literal_eval(node.value) for node in built.body
                        if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'SUITE_COMPANIONS')
        self.assertEqual(payloads['wash-log']['title'], '세척일보')
        # 세척일보에서 여는 다른 창의 제목은 '세척일보'와 달라야 합니다(같으면 메인이 어느 창인지 가리지 못합니다).
        others = [call.args[0] for call in ast.walk(tree)
                  if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'title'
                  and call.args and not (isinstance(call.func.value, ast.Name) and call.func.value.id == 'self')]
        self.assertTrue(others)
        for title in others:
            self.assertFalse(isinstance(title, ast.Constant) and title.value == '세척일보', ast.dump(title))


if __name__ == '__main__':
    unittest.main()
