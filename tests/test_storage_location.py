"""공유 저장 위치: '옮김 완료' 표시를 보기 전에는 예전 위치, 본 뒤에는 새 위치만 씁니다."""
import importlib.util
import json
import os
import sys
import tempfile
import threading
import time
import unittest
import uuid
from pathlib import Path, PureWindowsPath
from types import ModuleType
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'src'))
from embed_companions import companion_source
from test_host_stability import load_app


def same(first, second):
    """Windows 경로로 봤을 때 같은 곳인지(이 시험은 Linux에서도 돌기 때문에 구분자를 맞춰 비교)."""
    return PureWindowsPath(str(first)) == PureWindowsPath(str(second))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Sandbox(unittest.TestCase):
    """PC에 기억하는 파일과 새 위치를 임시 폴더로 돌립니다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.new = self.base / 'new' / '지후니우스 저장'
        self.new.mkdir(parents=True)
        self.state = self.base / 'pc' / 'storage_location.json'
        environment = patch.dict(os.environ, {'JIHUNIUS_STORAGE_STATE': str(self.state),
                                              'LOCALAPPDATA': str(self.base / 'pc')})
        environment.start()
        self.addCleanup(environment.stop)
        # 다른 시험이 보조창 프로그램을 불러오며 남긴 저장 위치 모듈이 있으면 잠시 치워 둡니다.
        left = sys.modules.pop('jihunius_storage', None)
        if left is not None:
            self.addCleanup(sys.modules.__setitem__, 'jihunius_storage', left)

    def storage(self):
        module = load('src/storage_location.py', 'storage_' + uuid.uuid4().hex)
        module.NEW_ROOT = str(self.new)
        return module

    def mark_moved(self, storage, value=None):
        (self.new / storage.MARKER_NAME).write_text(
            json.dumps({'version': 1, 'moved': True} if value is None else value), encoding='utf-8')

    def as_companion_module(self, storage):
        previous = sys.modules.get('jihunius_storage')
        sys.modules['jihunius_storage'] = storage
        self.addCleanup(lambda: sys.modules.pop('jihunius_storage', None) if previous is None
                        else sys.modules.__setitem__('jihunius_storage', previous))


class StorageLocationTests(Sandbox):
    def test_before_the_move_every_feature_uses_the_old_location(self):
        storage = self.storage()
        self.assertFalse(storage.moved())
        self.assertFalse(storage.check())
        parent = r'\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈'
        self.assertEqual(storage.folder('wash'), parent + r'\세척일보')
        for feature in ('handover', 'protrusion', 'special', 'wash_run'):
            self.assertEqual(storage.folder(feature), parent + r'\지후니우스_인수인계')
        self.assertEqual(storage.folder('errors'), parent + r'\지후니우스_인수인계\오류기록')
        self.assertEqual(storage.folder('material'), parent + r'\지후니우스_인수인계\소재재고조사')
        self.assertFalse(self.state.exists())

    def test_marker_switches_this_pc_to_feature_folders_and_is_remembered(self):
        storage = self.storage()
        self.mark_moved(storage)
        self.assertFalse(storage.moved())                       # 확인하기 전에는 아직 예전 위치
        self.assertTrue(storage.check())
        self.assertTrue(storage.moved())
        names = {'wash': '세척일보', 'handover': '인수인계', 'protrusion': '돌출량 표', 'special': '특수 돌출량',
                 'errors': '오류기록', 'material': '소재 사용량 조사', 'wash_run': '세척완료'}
        for feature, name in names.items():
            self.assertEqual(Path(storage.folder(feature)), self.new / name)
        self.assertEqual(len({storage.folder(feature) for feature in names}), len(names))
        self.assertEqual(json.loads(self.state.read_text(encoding='utf-8')),
                         {'version': 1, 'moved': True, 'root': str(self.new)})

    def test_a_pc_that_moved_never_goes_back_even_if_the_new_location_disappears(self):
        storage = self.storage()
        self.mark_moved(storage)
        storage.check()
        (self.new / storage.MARKER_NAME).unlink()
        again = self.storage()                                   # 프로그램을 다시 켠 것처럼
        self.assertTrue(again.moved())
        self.assertTrue(again.check())
        self.assertEqual(Path(again.folder('handover')), self.new / '인수인계')

    def test_unreadable_or_foreign_markers_do_not_switch(self):
        storage = self.storage()
        for value in ({'version': 2, 'moved': True}, {'version': 1, 'moved': 'yes'}, {'version': 1}, [], 'x'):
            self.mark_moved(storage, value)
            self.assertFalse(storage.check(), value)
        (self.new / storage.MARKER_NAME).write_bytes(b'{"version": 1, "moved": tr')
        self.assertFalse(storage.check())
        self.assertFalse(self.state.exists())

    def test_state_for_another_destination_or_a_damaged_state_file_counts_as_not_moved(self):
        storage = self.storage()
        self.state.parent.mkdir(parents=True, exist_ok=True)
        self.state.write_text(json.dumps({'version': 1, 'moved': True, 'root': 'somewhere else'}), encoding='utf-8')
        self.assertFalse(storage.moved())
        self.state.write_text('{', encoding='utf-8')
        self.assertFalse(storage.moved())

    def test_companions_and_stores_never_touch_the_network(self):
        storage = self.storage()
        self.mark_moved(storage)
        with patch.object(storage, 'marker_present', side_effect=AssertionError('network')):
            self.assertFalse(storage.moved())
            self.assertTrue(storage.folder('wash').endswith('세척일보'))

    def test_startup_check_does_not_wait_for_a_slow_server(self):
        storage = self.storage()
        release = threading.Event()
        self.addCleanup(release.set)

        def slow():
            release.wait(5)
            return False

        with patch.object(storage, 'marker_present', slow):
            started = time.monotonic()
            self.assertFalse(storage.startup_check(wait=.2))
            self.assertLess(time.monotonic() - started, 1.5)
        self.mark_moved(storage)
        self.assertTrue(storage.startup_check(wait=2))
        with patch.object(storage, 'marker_present', side_effect=AssertionError('network')):
            self.assertTrue(storage.startup_check(wait=2))       # 넘어간 뒤에는 확인하지 않음

    def test_watcher_asks_once_for_a_restart_when_the_move_happens_while_running(self):
        storage = self.storage()
        scheduled = []
        window = Mock()
        window.winfo_exists.return_value = True
        window.after.side_effect = lambda delay, callback: scheduled.append((delay, callback))
        app = Mock(window=window)
        watcher = storage.attach(app)
        self.assertEqual([delay for delay, _ in scheduled], [60000])
        scheduled.pop()[1]()                                     # 1분 뒤: 아직 표시 없음
        watcher.worker.join(5)
        app.messagebox.showinfo.assert_not_called()
        self.assertEqual(len(scheduled), 1)
        self.mark_moved(storage)
        scheduled.pop()[1]()                                     # 다음 확인에서 표시 발견
        watcher.worker.join(5)
        scheduled.pop()[1]()
        app.messagebox.showinfo.assert_called_once()
        title, text = app.messagebox.showinfo.call_args.args
        self.assertIn('옮겨졌습니다', title)
        self.assertIn('다시 실행', text)
        self.assertIn(str(self.new), text)
        self.assertEqual(scheduled, [])                          # 알린 뒤에는 더 확인하지 않음
        watcher.notify()
        app.messagebox.showinfo.assert_called_once()

    def test_before_the_move_a_started_pc_leaves_its_name_and_version_in_the_new_place(self):
        storage = self.storage()
        self.assertFalse(storage.startup_check('2026.11.17.2', wait=5))
        ready = list((self.new / storage.READY_NAME).glob('*.json'))
        self.assertEqual(len(ready), 1)
        value = json.loads(ready[0].read_text(encoding='utf-8'))
        self.assertEqual((value['version'], bool(value['pc']), bool(value['at'])), ('2026.11.17.2', True, True))
        self.assertEqual(list((self.new / storage.READY_NAME).glob('*.tmp')), [])
        self.assertFalse(storage.startup_check(None, wait=5))            # 버전을 모르면 남기지 않음(덮어쓰지도 않음)
        self.mark_moved(storage)
        ready[0].unlink()
        self.assertTrue(storage.startup_check('2026.11.17.2', wait=5))
        self.assertEqual(list((self.new / storage.READY_NAME).glob('*.json')), [])   # 옮긴 뒤에는 남기지 않음

    def test_nothing_is_created_when_the_new_place_does_not_exist(self):
        storage = self.storage()
        storage.NEW_ROOT = str(self.base / '없는 폴더' / '지후니우스 저장')
        self.assertFalse(storage.startup_check('2026.11.17.2', wait=5))
        self.assertFalse((self.base / '없는 폴더').exists())
        self.assertFalse(storage.announce('2026.11.17.2'))

    def test_a_failing_check_never_stops_the_program_from_starting(self):
        storage = self.storage()
        with patch.object(storage, 'marker_present', side_effect=RuntimeError('unexpected')):
            self.assertFalse(storage.startup_check('2026.11.17.2', wait=5))
        with patch.object(storage, 'announce', side_effect=PermissionError(13, 'denied')):
            self.assertFalse(storage.startup_check('2026.11.17.2', wait=5))

    def test_watcher_does_nothing_on_a_pc_that_already_moved(self):
        storage = self.storage()
        self.mark_moved(storage)
        storage.check()
        window = Mock()
        storage.attach(Mock(window=window))
        window.after.assert_not_called()


class HostStorageTests(Sandbox):
    def host(self):
        module = load_app()
        module.SuiteStorage.NEW_ROOT = str(self.new)
        return module

    def test_host_stores_use_the_old_folders_until_the_marker_was_seen(self):
        m = self.host()
        old = PureWindowsPath(m.HANDOVER_SHARED_PARENT) / m.HANDOVER_FOLDER_NAME
        self.assertTrue(same(m.HandoverStore().path, old))
        self.assertTrue(same(m.SuiteStorage.folder('errors'), old / '오류기록'))
        self.assertTrue(same(m.SuiteStorage.folder('wash_run'), old))
        (self.new / m.SuiteStorage.MARKER_NAME).write_text('{"version": 1, "moved": true}', encoding='utf-8')
        self.assertTrue(same(m.HandoverStore().path, old))        # 확인 전
        self.assertTrue(m.SuiteStorage.startup_check(wait=5))
        self.assertEqual(m.HandoverStore().path, self.new / '인수인계')
        self.assertEqual(Path(m.SuiteStorage.folder('errors')), self.new / '오류기록')
        self.assertEqual(Path(m.SuiteStorage.folder('wash_run')), self.new / '세척완료')

    def test_explicit_handover_folder_is_untouched(self):
        m = self.host()
        self.assertEqual(m.HandoverStore(self.base / 'custom').path, self.base / 'custom')

    def test_startup_checks_before_the_window_and_watches_afterwards(self):
        m = self.host()
        order = []
        with patch.object(m.SuiteUpdater, 'managed_context', return_value={'test': True}), \
                patch.object(m.SuiteUpdater, 'managed_lease', return_value=Mock()), \
                patch.object(m.SuiteUpdater, 'attach'), patch.object(m.SuiteUpdater, 'mark_ready'), \
                patch.object(m.SuiteErrors, 'install'), patch.object(m.SuiteErrors, 'attach') as errors, \
                patch.object(m, 'configure_windows_app_identity'), \
                patch.object(m.SuiteStorage, 'startup_check', side_effect=lambda version: order.append(('check', version))), \
                patch.object(m.SuiteStorage, 'attach', side_effect=lambda app: order.append('watch')), \
                patch.object(m, 'IntegrationApp', side_effect=lambda window: order.append('app') or Mock()), \
                patch('tkinter.Tk', return_value=Mock()):
            m.main()
        self.assertEqual(order, [('check', m.SUITE_APP_VERSION), 'app', 'watch'])
        self.assertTrue(same(errors.call_args.args[1], m.SuiteStorage.folder('errors')))


class CompanionStorageTests(Sandbox):
    def moved_storage(self):
        storage = self.storage()
        self.mark_moved(storage)
        self.assertTrue(storage.check())
        self.as_companion_module(storage)
        return storage

    def test_protrusion_table_follows_the_move_and_keeps_unsaved_input(self):
        protrusion = load('src/protrusion.py', 'protrusion_' + uuid.uuid4().hex)
        self.assertEqual(protrusion.shared_folder(), protrusion.SHARED_FOLDER)          # 단독 실행·시험
        old_path = protrusion.SHARED_FOLDER / protrusion.SHARED_FILENAME
        pending = {'memo': {'key': 'memo', 'base': '', 'value': '아직 저장 못 한 메모', 'seq': 1}}
        protrusion.PendingRecovery(old_path).save(pending)                              # 옮기기 전에 보관된 입력
        storage = self.moved_storage()
        self.assertEqual(protrusion.shared_folder(), self.new / '돌출량 표')
        self.assertEqual(protrusion.SharedStore().folder, self.new / '돌출량 표')
        self.assertEqual(Path(protrusion.SharedStoreClient().folder), self.new / '돌출량 표')
        new_path = protrusion.SharedStore().path
        self.assertTrue(same(protrusion.previous_shared_path(new_path), old_path))
        recovery = protrusion.PendingRecovery(new_path, previous_shared_path=protrusion.previous_shared_path(new_path))
        loaded = recovery.load()
        self.assertEqual({key: (item['base'], item['value']) for key, item in loaded.items()},
                         {'memo': ('', '아직 저장 못 한 메모')})
        self.assertTrue(recovery.path.exists())
        self.assertFalse(protrusion.PendingRecovery(old_path).path.exists())            # 이어받은 뒤 예전 보관본은 지움
        again = protrusion.PendingRecovery(new_path, previous_shared_path=protrusion.previous_shared_path(new_path))
        self.assertEqual(again.load()['memo']['value'], '아직 저장 못 한 메모')
        again.save({})
        self.assertEqual(protrusion.PendingRecovery(
            new_path, previous_shared_path=protrusion.previous_shared_path(new_path)).load(), {})
        self.assertIsNone(protrusion.previous_shared_path(old_path))
        self.assertTrue(storage.moved())

    def test_protrusion_before_the_move_has_nothing_to_adopt(self):
        protrusion = load('src/protrusion.py', 'protrusion_' + uuid.uuid4().hex)
        self.as_companion_module(self.storage())
        self.assertTrue(same(protrusion.shared_folder(), protrusion.SHARED_FOLDER))
        self.assertIsNone(protrusion.previous_shared_path(protrusion.SHARED_FOLDER / protrusion.SHARED_FILENAME))

    def test_special_table_follows_the_move_and_keeps_unsaved_input(self):
        special = load('src/special_table.py', 'special_' + uuid.uuid4().hex)
        self.assertEqual(special.shared_folder(), special.SHARED_FOLDER)
        operation = {'kind': 'notes', 'base': '', 'value': '아직 저장 못 한 특이사항'}
        special.PendingDraft(special.SHARED_FOLDER).save([operation])
        self.moved_storage()
        self.assertEqual(special.shared_folder(), self.new / '특수 돌출량')
        self.assertEqual(special.TableStore().folder, self.new / '특수 돌출량')
        new_folder = special.shared_folder()
        draft = special.PendingDraft(new_folder, previous=special.previous_folder(new_folder))
        self.assertEqual(draft.load(), [operation])
        self.assertTrue(draft.path.exists())
        self.assertFalse(special.PendingDraft(special.SHARED_FOLDER).path.exists())
        self.assertEqual(special.PendingDraft(new_folder, previous=special.previous_folder(new_folder)).load(), [operation])
        self.assertIsNone(special.previous_folder(special.SHARED_FOLDER))
        self.assertEqual(special.TableStore(self.base / 'custom').folder, self.base / 'custom')

    def test_material_link_folder_follows_the_move_unless_overridden(self):
        try:
            import material_ui
        except Exception as error:                                # pragma: no cover - 화면 없는 환경
            self.skipTest(str(error))
        with patch.dict(os.environ):
            os.environ.pop('JIHUNIUS_MATERIAL_SHARED', None)
            self.assertEqual(material_ui.shared_folder(), material_ui.DEFAULT_SHARE)
            self.moved_storage()
            self.assertEqual(Path(material_ui.shared_folder()), self.new / '소재 사용량 조사')
            os.environ['JIHUNIUS_MATERIAL_SHARED'] = str(self.base / 'elsewhere')
            self.assertEqual(material_ui.shared_folder(), str(self.base / 'elsewhere'))

    def run_wash_log(self, moved, saved_folder):
        """배포본에 실리는 세척일보 프로그램을 그대로 불러옵니다(창은 만들지 않음)."""
        source = companion_source(ROOT, 'wash-log').decode('utf-8')
        probe = load('src/storage_location.py', 'storage_' + uuid.uuid4().hex)
        if moved:
            self.state.parent.mkdir(parents=True, exist_ok=True)
            self.state.write_text(json.dumps({'version': 1, 'moved': True, 'root': probe.NEW_ROOT}), encoding='utf-8')
        settings = self.base / 'pc' / 'WashLog' / 'settings.json'
        settings.parent.mkdir(parents=True, exist_ok=True)
        if saved_folder is not None:
            settings.write_text(json.dumps({'folder': saved_folder, 'dept': '가공'}, ensure_ascii=False), encoding='utf-8')
        name = 'wash_log_embedded_' + uuid.uuid4().hex
        module = ModuleType(name)
        module.__file__ = str(ROOT / 'src/wash_log.py')
        sys.modules[name] = module
        self.addCleanup(sys.modules.pop, name, None)
        previous = sys.modules.get('jihunius_storage')
        self.addCleanup(lambda: sys.modules.pop('jihunius_storage', None) if previous is None
                        else sys.modules.__setitem__('jihunius_storage', previous))
        exec(compile(source, name, 'exec'), module.__dict__)
        saved = json.loads(settings.read_text(encoding='utf-8')) if settings.exists() else None
        return module, saved, probe

    def test_wash_log_keeps_the_old_default_before_the_move(self):
        old_default = r'\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈\세척일보'
        module, saved, _probe = self.run_wash_log(False, old_default)
        self.assertEqual(module.DEFAULT_FOLDER, old_default)
        self.assertEqual(saved, {'folder': old_default, 'dept': '가공'})

    def test_wash_log_default_and_remembered_default_folder_move_together(self):
        old_default = r'\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈\세척일보'
        module, saved, probe = self.run_wash_log(True, old_default.upper().replace('세척일보', '세척일보') + '\\')
        expected = os.path.join(probe.NEW_ROOT, '세척일보')
        self.assertEqual(module.DEFAULT_FOLDER, expected)
        self.assertEqual(module.DEFAULT_PARENT, probe.NEW_ROOT)
        self.assertEqual(saved, {'folder': expected, 'dept': '가공'})       # 다른 설정은 그대로

    def test_wash_log_old_folder_remembered_through_a_drive_letter_also_moves(self):
        for remembered in (r'Y:\생산관리\일일 업무 보고\최지훈\세척일보', 'y:/생산관리/일일 업무 보고/최지훈/세척일보/',
                           r'\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈'):      # 개인 폴더를 잘못 골랐던 PC
            module, saved, probe = self.run_wash_log(True, remembered)
            self.assertEqual(saved, {'folder': os.path.join(probe.NEW_ROOT, '세척일보'), 'dept': '가공'}, remembered)

    def test_wash_log_folder_the_user_chose_is_left_alone(self):
        for chosen in (r'D:\다른 폴더\세척일보', r'\\192.168.0.254\내부공유폴더\다른 사람\세척일보', r'D:\최지훈'):
            module, saved, probe = self.run_wash_log(True, chosen)
            self.assertEqual(module.DEFAULT_FOLDER, os.path.join(probe.NEW_ROOT, '세척일보'))
            self.assertEqual(saved, {'folder': chosen, 'dept': '가공'}, chosen)

    def test_wash_log_without_saved_settings_just_uses_the_new_default(self):
        module, saved, probe = self.run_wash_log(True, None)
        self.assertEqual(module.DEFAULT_FOLDER, os.path.join(probe.NEW_ROOT, '세척일보'))
        self.assertIsNone(saved)

    def test_every_companion_carries_the_storage_module(self):
        for key in ('protrusion', 'wash-log', 'special-table', 'material'):
            source = companion_source(ROOT, key).decode('utf-8')
            self.assertEqual(source.count("_storage_sys.modules['jihunius_storage'] = _storage_module"), 1, key)
            self.assertEqual(source.count('if _storage_module.moved():'), 1 if key == 'wash-log' else 0, key)


if __name__ == '__main__':
    unittest.main()
