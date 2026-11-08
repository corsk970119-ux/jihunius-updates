"""Search roots are local preferences, retained across launches and releases."""
import json
import os
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch
import uuid


SOURCE_PATH = Path(__file__).resolve().parents[1]/'apps/jihunius/app.pyw'


def load_app():
    name = 'program_paths_' + uuid.uuid4().hex
    module = ModuleType(name)
    module.__file__ = str(SOURCE_PATH)
    sys.modules[name] = module
    exec(compile(SOURCE_PATH.read_bytes(), str(SOURCE_PATH), 'exec'), module.__dict__)
    return module


class Value:
    def __init__(self, value): self.value = value
    def get(self): return self.value
    def set(self, value): self.value = value


def stl_app(module):
    app = module.App.__new__(module.App)
    values = {'folder': module.DEFAULT_FOLDER, 'prefer_lab': True, 'fuzzy_names': True,
              'period_mode': '최근 3일', 'start_date': '2026-11-01', 'end_date': '2026-11-03'}
    for key, value in values.items(): setattr(app, key, Value(value))
    app.load_settings()
    return app


class ProgramPathsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.local = Path(self.tmp.name)/'pc-one'
        env = patch.dict(os.environ, LOCALAPPDATA=str(self.local))
        env.start(); self.addCleanup(env.stop)
        self.app = load_app()

    def require_paths(self):
        for name in ('program_settings_path', 'load_program_base_root',
                     'save_program_base_root', 'normalize_program_base_root'):
            self.assertTrue(callable(getattr(self.app, name, None)), name + ' is required')

    def test_korean_unc_root_round_trip_and_settings_stay_on_this_pc(self):
        self.require_paths()
        selected = r'\\NAS-A\공유폴더\★NC프로그램파일'
        self.assertEqual(self.app.save_program_base_root(selected), selected)
        settings = Path(self.app.program_settings_path())
        self.assertTrue(settings.relative_to(self.local).parts)
        self.assertEqual(load_app().load_program_base_root(), selected)
        other_pc = Path(self.tmp.name)/'pc-two'
        with patch.dict(os.environ, LOCALAPPDATA=str(other_pc)):
            other = load_app()
            self.assertEqual(other.load_program_base_root(), other.PROGRAM_BASE_ROOT)
            other.save_program_base_root(r'\\NAS-B\NC 공유')
            self.assertNotEqual(Path(other.program_settings_path()), settings)
            self.assertEqual(load_app().load_program_base_root(), r'\\NAS-B\NC 공유')
        self.assertEqual(load_app().load_program_base_root(), selected)

    def test_quoted_absolute_root_is_normalized_without_network_access(self):
        self.require_paths()
        selected = r'\\NAS-A\공유폴더\★NC프로그램파일'
        self.assertEqual(self.app.normalize_program_base_root('  "' + selected + '"  '), selected)
        self.assertEqual(self.app.normalize_program_base_root(str(self.local)), str(self.local))

    def test_empty_relative_and_control_character_paths_are_rejected(self):
        self.require_paths()
        for value in ('', '   ', 'NC파일', r'.\NC파일', r'C:NC파일', '\\NAS\nA\\NC', '~jihunius_missing_user_740219'):
            with self.subTest(value=value), self.assertRaises(self.app.WorkError):
                self.app.save_program_base_root(value)
        self.assertFalse(Path(self.app.program_settings_path()).exists())

    def test_malformed_settings_fall_back_without_rewriting_file(self):
        self.require_paths()
        self.app.save_program_base_root(r'\\NAS-A\NC파일')
        path = Path(self.app.program_settings_path())
        for data in ('{broken', '[]', 'null'):
            path.write_text(data, encoding='utf-8')
            self.assertEqual(self.app.load_program_base_root(), self.app.PROGRAM_BASE_ROOT)
            self.assertEqual(path.read_text(encoding='utf-8'), data)

    def test_failed_atomic_replacement_preserves_last_saved_path(self):
        self.require_paths()
        selected = r'\\NAS-A\기존 NC파일'
        self.app.save_program_base_root(selected)
        path = Path(self.app.program_settings_path()); before = path.read_bytes()
        with patch.object(self.app.os, 'replace', side_effect=OSError('disk full')):
            with self.assertRaises((OSError, self.app.WorkError)):
                self.app.save_program_base_root(r'\\NAS-B\새 NC파일')
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.app.load_program_base_root(), selected)

    def test_selected_root_preserves_year_month_and_date_alias_resolution(self):
        self.require_paths()
        root = Path(self.tmp.name)/'NC 기본 폴더'
        actual = root/'★ 2031'/'11월'/'11.03'
        actual.mkdir(parents=True)
        self.assertEqual(self.app.year_search_root(2031, base_root=root), root/'★ 2031')
        requested = self.app.date_search_folders('11.3', year=2031, base_root=root)
        self.assertEqual(requested, [root/'★ 2031'/'11월'/'11.3'])
        self.assertEqual(self.app.resolve_date_search_folders(requested), [actual])
        self.assertEqual(self.app.year_search_root(2031), Path(self.app.PROGRAM_BASE_ROOT)/'★ 2031')

    def test_stl_retains_saved_custom_folder_across_default_path_changes(self):
        module = self.app.load_stl_finder()
        module.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        custom = r'\\NAS-A\내가 지정한 STL'
        for marker in ({'default_folder': r'\\OLD-NAS\이전 기본 폴더'}, {}):
            with self.subTest(marker=marker):
                module.CONFIG_FILE.write_text(json.dumps({'folder': custom, **marker}), encoding='utf-8')
                self.assertEqual(stl_app(module).folder.get(), custom)

    def test_nc_old_default_switches_to_production_share_but_explicit_choice_is_retained(self):
        old = r'\\192.168.0.254\내부공유폴더\★NC프로그램파일'
        new = r'\\srvc5352374b\생산공유폴더\★NC프로그램파일'
        path = self.app.program_settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        for saved in (old, old.replace('\\', '/'), old + '\\'):
            with self.subTest(saved=saved):
                path.write_text(json.dumps({'base_root': saved}), encoding='utf-8')
                before = path.read_bytes()
                self.assertEqual(load_app().load_program_base_root(), new)
                self.assertEqual(path.read_bytes(), before)
        # Choosing a different custom root, or explicitly reselecting the old
        # server in the new version, must survive the next launch.
        for selected in (r'Z:\★NC프로그램파일', r'\\NAS-B\별도 작업', old):
            self.app.save_program_base_root(selected)
            self.assertEqual(load_app().load_program_base_root(), selected)

    def test_stl_old_default_switches_without_losing_filters_or_explicit_old_server_choice(self):
        old = r'\\192.168.0.254\내부공유폴더\★커스텀 오더 2026년'
        new = r'\\srvc5352374b\생산공유폴더\★커스텀 오더 2026년'
        module = self.app.load_stl_finder()
        module.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        for marker in ({}, {'default_folder': old}):
            module.CONFIG_FILE.write_text(json.dumps(dict(folder=old, prefer_lab=False,
                fuzzy_names=False, period_mode='지정 기간', start_date='2026-10-01',
                end_date='2026-10-31', **marker)), encoding='utf-8')
            before = module.CONFIG_FILE.read_bytes()
            app = stl_app(module)
            self.assertEqual(app.folder.get(), new)
            self.assertFalse(app.prefer_lab.get())
            self.assertFalse(app.fuzzy_names.get())
            self.assertEqual((app.period_mode.get(), app.start_date.get(), app.end_date.get()),
                             ('지정 기간', '2026-10-01', '2026-10-31'))
            self.assertEqual(module.CONFIG_FILE.read_bytes(), before)
            app.folder.set(old)
            app.save_settings()
            self.assertEqual(stl_app(load_app().load_stl_finder()).folder.get(), old)

    def test_stl_chooser_and_typed_path_survive_relaunch_with_pc_isolation(self):
        module = self.app.load_stl_finder(); app = stl_app(module)
        selected = r'\\NAS-A\커스텀 오더'
        with patch.object(module.filedialog, 'askdirectory', return_value=selected):
            app.choose_folder()
        self.assertEqual(stl_app(load_app().load_stl_finder()).folder.get(), selected)
        app.folder.set(r'\\NAS-A\직접 입력한 STL')
        app.stop_event = SimpleNamespace(set=lambda: None)
        app.close(destroy=False)
        self.assertEqual(stl_app(load_app().load_stl_finder()).folder.get(), r'\\NAS-A\직접 입력한 STL')
        with patch.dict(os.environ, LOCALAPPDATA=str(Path(self.tmp.name)/'pc-two')):
            other = load_app().load_stl_finder()
            self.assertEqual(stl_app(other).folder.get(), other.DEFAULT_FOLDER)


if __name__ == '__main__': unittest.main()
