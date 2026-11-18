"""대비(2026-11-18): 생산공유폴더에서 다시 개인 폴더 아래 '지후니우스 저장'으로 옮길 수 있게 그 위치를 미리 압니다.

그 위치에 '옮김 완료' 표시가 생기기 전에는 아무것도 달라지지 않고, 생기면 지난번과 같은 방식으로 넘어갑니다.
"""
import ast
import json
import os
import sys
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
sys.path.insert(0, str(ROOT / 'tests'))
from embed_companions import companion_source
from test_host_stability import load_app
from test_storage_location import Sandbox, load

NAMES = {'wash': '세척일보', 'handover': '인수인계', 'protrusion': '돌출량 표', 'special': '특수 돌출량',
         'errors': '오류기록', 'material': '소재 사용량 조사', 'wash_run': '세척완료'}
PERSONAL = r'\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈'


class SecondMove(Sandbox):
    def setUp(self):
        super().setUp()
        self.back = self.base / 'personal' / '지후니우스 저장'

    def storage(self, on_share=True):
        module = super().storage()
        module.BACK_ROOT = str(self.back)
        if on_share:                                             # 지금 상태: 생산공유폴더로 넘어가 있는 PC
            self.mark_moved(module)
            self.assertTrue(module.check())
        return module

    def mark_back(self, storage, value=None):
        self.back.mkdir(parents=True, exist_ok=True)
        (self.back / storage.MARKER_NAME).write_text(
            json.dumps({'version': 1, 'moved': True} if value is None else value), encoding='utf-8')

    def window(self):
        scheduled = []
        window = Mock()
        window.winfo_exists.return_value = True
        window.after.side_effect = lambda delay, callback: scheduled.append((delay, callback))
        return window, scheduled


class SecondMoveLocationTests(SecondMove):
    def test_the_fallback_place_is_the_folder_of_the_same_name_under_the_personal_folder(self):
        storage = load('src/storage_location.py', 'storage_' + uuid.uuid4().hex)
        self.assertEqual(storage.BACK_ROOT, PERSONAL + r'\지후니우스 저장')
        self.assertEqual(PureWindowsPath(storage.BACK_ROOT).name, PureWindowsPath(storage.NEW_ROOT).name)
        self.assertNotEqual(storage.BACK_ROOT, storage.NEW_ROOT)
        self.assertNotIn(storage.BACK_ROOT, storage.OLD_FOLDERS.values())

    def test_nothing_changes_while_the_fallback_place_has_no_marker(self):
        storage = self.storage()
        before = self.state.read_bytes()
        self.assertEqual(json.loads(before.decode('utf-8')), {'version': 1, 'moved': True, 'root': str(self.new)})
        # 대비 위치에 폴더와 복사 중인 자료가 있어도 '옮김 완료' 표시가 없으면 넘어가지 않습니다.
        for name in NAMES.values():
            (self.back / name).mkdir(parents=True)
        for value in ({'version': 2, 'moved': True}, {'version': 1, 'moved': 'yes'}, {'version': 1}, [], 'x'):
            self.mark_back(storage, value)
            self.assertTrue(storage.check(), value)
            self.assertEqual(storage.root(), str(self.new), value)
        (self.back / storage.MARKER_NAME).write_bytes(b'{"version": 1, "moved": tr')
        self.assertTrue(storage.startup_check(wait=5))
        for feature, name in NAMES.items():
            self.assertEqual(Path(storage.folder(feature)), self.new / name)
        self.assertIsNone(storage.previous_folder('protrusion'))
        self.assertEqual(storage.earlier_folders('wash'), [])
        self.assertEqual(self.state.read_bytes(), before)

    def test_marker_in_the_fallback_place_moves_a_pc_from_the_production_share(self):
        storage = self.storage()
        self.mark_back(storage)
        self.assertEqual(storage.root(), str(self.new))          # 확인하기 전에는 아직 생산공유폴더
        self.assertTrue(storage.check())
        self.assertTrue(storage.moved())
        self.assertEqual(storage.root(), str(self.back))
        for feature, name in NAMES.items():                      # 폴더 구성은 같고 위치만 다름
            self.assertEqual(Path(storage.folder(feature)), self.back / name)
            self.assertEqual(Path(storage.previous_folder(feature)), self.new / name)
        self.assertEqual([Path(item) for item in storage.earlier_folders('wash')], [self.new / '세척일보'])
        self.assertEqual(json.loads(self.state.read_text(encoding='utf-8')),
                         {'version': 1, 'moved': True, 'root': str(self.back), 'previous': str(self.new)})

    def test_a_pc_still_on_the_old_layout_goes_straight_to_the_fallback_place(self):
        storage = self.storage(on_share=False)
        self.mark_moved(storage)                                 # 생산공유폴더의 표시가 남아 있어도
        self.mark_back(storage)
        self.assertTrue(storage.check())
        self.assertEqual(storage.root(), str(self.back))         # 나중 위치가 먼저
        self.assertEqual(json.loads(self.state.read_text(encoding='utf-8')),
                         {'version': 1, 'moved': True, 'root': str(self.back)})
        self.assertIsNone(storage.previous_folder('protrusion'))  # 예전 구성에서 바로 넘어옴

    def test_a_pc_in_the_fallback_place_never_goes_back_and_stops_checking(self):
        storage = self.storage()
        self.mark_back(storage)
        storage.check()
        (self.back / storage.MARKER_NAME).unlink()               # 대비 위치의 표시가 사라지고 생산공유폴더의 표시만 남아도
        again = self.storage(on_share=False)                     # 프로그램을 다시 켠 것처럼
        with patch.object(again, 'marker_present', side_effect=AssertionError('network')), \
                patch.object(again, 'back_marker_present', side_effect=AssertionError('network')):
            self.assertTrue(again.check())
            self.assertTrue(again.startup_check('2026.11.18.3', wait=5))
            self.assertEqual(Path(again.folder('handover')), self.back / '인수인계')
        self.assertFalse((self.back / again.READY_NAME).exists())

    def test_program_started_after_the_switch_uses_the_fallback_place_at_once(self):
        storage = self.storage()
        self.mark_back(storage)
        self.assertTrue(storage.startup_check('2026.11.18.3', wait=5))
        self.assertEqual(Path(storage.folder('wash')), self.back / '세척일보')
        with patch.object(storage, 'marker_present', side_effect=AssertionError('network')), \
                patch.object(storage, 'back_marker_present', side_effect=AssertionError('network')):
            self.assertEqual(Path(storage.folder('handover')), self.back / '인수인계')   # 저장 코드는 네트워크를 보지 않음

    def test_startup_does_not_wait_for_a_slow_or_failing_fallback_server(self):
        storage = self.storage()
        release = threading.Event()
        self.addCleanup(release.set)

        def slow():
            release.wait(5)
            return False

        with patch.object(storage, 'back_marker_present', slow):
            started = time.monotonic()
            self.assertTrue(storage.startup_check('2026.11.18.3', wait=.2))
            self.assertLess(time.monotonic() - started, 1.5)
            self.assertEqual(storage.root(), str(self.new))      # 확인이 안 끝났으면 쓰던 위치 그대로
        with patch.object(storage, 'back_marker_present', side_effect=RuntimeError('unexpected')):
            self.assertTrue(storage.startup_check('2026.11.18.3', wait=5))               # 확인 실패가 시작을 막지 않음
            self.assertEqual(storage.root(), str(self.new))

    def test_startup_waits_for_the_marker_check_but_not_for_leaving_the_name(self):
        storage = self.storage()
        self.back.mkdir(parents=True)
        release = threading.Event()
        self.addCleanup(release.set)
        with patch.object(storage, 'announce', side_effect=lambda version, target=None: release.wait(5)):
            started = time.monotonic()
            self.assertTrue(storage.startup_check('2026.11.18.3', wait=5))
            self.assertLess(time.monotonic() - started, 1.5)
            release.set()
            storage._startup['worker'].join(5)

    def test_a_started_pc_leaves_its_name_in_the_fallback_place_once_that_folder_exists(self):
        storage = self.storage()
        self.assertTrue(storage.startup_check('2026.11.18.3', wait=5))
        storage._startup['worker'].join(5)
        self.assertFalse(self.back.exists())                     # 폴더가 없으면 만들지 않음
        self.back.mkdir(parents=True)
        self.assertTrue(storage.startup_check('2026.11.18.3', wait=5))
        storage._startup['worker'].join(5)
        ready = list((self.back / storage.READY_NAME).glob('*.json'))
        self.assertEqual(len(ready), 1)
        value = json.loads(ready[0].read_text(encoding='utf-8'))
        self.assertEqual((value['version'], bool(value['pc']), bool(value['at'])), ('2026.11.18.3', True, True))
        self.assertEqual(list((self.back / storage.READY_NAME).glob('*.tmp')), [])
        self.assertFalse((self.new / storage.READY_NAME).exists())        # 생산공유폴더에는 더 남기지 않음
        self.assertEqual(storage.root(), str(self.new))                   # 이름을 남겼다고 넘어가지는 않음

    def test_a_pc_still_on_the_old_layout_leaves_its_name_in_both_places(self):
        legacy = self.storage(on_share=False)
        self.back.mkdir(parents=True)
        self.assertFalse(legacy.startup_check('2026.11.18.3', wait=5))
        legacy._startup['worker'].join(5)
        self.assertEqual(len(list((self.new / legacy.READY_NAME).glob('*.json'))), 1)
        self.assertEqual(len(list((self.back / legacy.READY_NAME).glob('*.json'))), 1)

    def test_watcher_keeps_looking_and_asks_once_for_a_restart_when_the_switch_happens_while_running(self):
        storage = self.storage()
        self.assertTrue(storage.startup_check(wait=5))
        window, scheduled = self.window()
        app = Mock(window=window)
        watcher = storage.attach(app)
        self.assertEqual([delay for delay, _ in scheduled], [60000])     # 생산공유폴더를 쓰는 동안에는 계속 확인
        scheduled.pop()[1]()
        watcher.worker.join(5)
        app.messagebox.showinfo.assert_not_called()
        self.assertEqual(len(scheduled), 1)
        self.mark_back(storage)
        scheduled.pop()[1]()                                     # 다음 확인에서 표시 발견
        watcher.worker.join(5)
        scheduled.pop()[1]()
        app.messagebox.showinfo.assert_called_once()
        title, text = app.messagebox.showinfo.call_args.args
        self.assertIn('옮겨졌습니다', title)
        self.assertIn('다시 실행', text)
        self.assertIn(str(self.back), text)
        self.assertNotIn('생산공유폴더로', text)
        self.assertEqual(scheduled, [])
        after = Mock()                                           # 다시 켠 뒤(대비 위치)에는 더 확인하지 않음
        self.assertTrue(storage.startup_check(wait=5))
        storage.attach(Mock(window=after))
        after.after.assert_not_called()

    def test_watcher_notices_a_switch_that_landed_right_after_the_startup_check(self):
        storage = self.storage()
        self.assertTrue(storage.startup_check(wait=5))           # 켤 때는 생산공유폴더
        self.mark_back(storage)
        storage.check()                                          # 늦게 끝난 확인이 창이 뜨기 전에 기억함
        window, scheduled = self.window()
        app = Mock(window=window)
        storage.attach(app)
        scheduled.pop()[1]()
        app.messagebox.showinfo.assert_called_once()             # 이 프로그램은 생산공유폴더로 켜졌으므로 다시 실행하라고 알림
        self.assertIn(str(self.back), app.messagebox.showinfo.call_args.args[1])

    def test_released_versions_do_not_follow_the_switch_by_themselves(self):
        # 2026.11.18.2까지는 대비 위치를 모릅니다: 그 버전에게 이 PC의 기억(대비 위치)은 '넘어간 적 없음'으로 읽힙니다.
        # 그래서 옮기기 프로그램이 생산공유폴더의 자리를 막아 둡니다(tests/test_storage_move_back.py).
        tree = ast.parse((ROOT / 'releases/jihunius/2026.11.18.2/app.pyw').read_text(encoding='utf-8'))
        source = next(node.value.args[1].value for node in tree.body
                      if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'SuiteStorage')
        released = ModuleType('released_storage')
        exec(compile(source, 'released_storage', 'exec'), released.__dict__)
        self.assertFalse(hasattr(released, 'BACK_ROOT'))
        released.NEW_ROOT = str(self.new)
        storage = self.storage()
        self.assertTrue(released.moved())                        # 생산공유폴더: 두 버전이 같은 기억을 같이 읽음
        self.assertEqual(Path(released.folder('handover')), self.new / '인수인계')
        self.mark_back(storage)
        storage.check()
        self.assertFalse(released.moved())
        self.assertEqual(released.folder('handover'), released.OLD_FOLDERS['handover'])
        (self.new / released.MARKER_NAME).unlink()               # 옮기기 프로그램이 생산공유폴더의 표시를 치운 뒤
        self.assertFalse(released.check())
        self.assertEqual(storage.root(), str(self.back))         # 새 버전의 기억은 그대로


class SecondMoveProgramTests(SecondMove):
    def switched(self):
        storage = self.storage()
        self.mark_back(storage)
        self.assertTrue(storage.check())
        self.as_companion_module(storage)
        return storage

    def test_host_stores_follow_the_switch(self):
        m = load_app()
        m.SuiteStorage.NEW_ROOT, m.SuiteStorage.BACK_ROOT = str(self.new), str(self.back)
        (self.new / m.SuiteStorage.MARKER_NAME).write_text('{"version": 1, "moved": true}', encoding='utf-8')
        self.assertTrue(m.SuiteStorage.startup_check(wait=5))
        self.assertEqual(m.HandoverStore().path, self.new / '인수인계')
        self.mark_back(m.SuiteStorage)
        self.assertEqual(m.HandoverStore().path, self.new / '인수인계')   # 확인 전
        self.assertTrue(m.SuiteStorage.startup_check(wait=5))
        self.assertEqual(m.HandoverStore().path, self.back / '인수인계')
        self.assertEqual(Path(m.SuiteStorage.folder('errors')), self.back / '오류기록')
        self.assertEqual(Path(m.SuiteStorage.folder('wash_run')), self.back / '세척완료')

    def test_protrusion_table_follows_the_switch_and_keeps_unsaved_input(self):
        protrusion = load('src/protrusion.py', 'protrusion_' + uuid.uuid4().hex)
        share = self.storage()
        self.as_companion_module(share)
        share_path = protrusion.SharedStore().path               # 생산공유폴더에서 쓰던 경로
        self.assertEqual(share_path.parent, self.new / '돌출량 표')
        pending = {'memo': {'key': 'memo', 'base': '', 'value': '아직 저장 못 한 메모', 'seq': 1}}
        protrusion.PendingRecovery(share_path).save(pending)
        self.mark_back(share)
        self.assertTrue(share.check())
        self.assertEqual(protrusion.shared_folder(), self.back / '돌출량 표')
        self.assertEqual(protrusion.SharedStore().folder, self.back / '돌출량 표')
        self.assertEqual(Path(protrusion.SharedStoreClient().folder), self.back / '돌출량 표')
        new_path = protrusion.SharedStore().path
        self.assertEqual(protrusion.previous_shared_path(new_path), share_path)
        recovery = protrusion.PendingRecovery(new_path, previous_shared_path=protrusion.previous_shared_path(new_path))
        self.assertEqual({key: (item['base'], item['value']) for key, item in recovery.load().items()},
                         {'memo': ('', '아직 저장 못 한 메모')})
        self.assertTrue(recovery.path.exists())
        self.assertFalse(protrusion.PendingRecovery(share_path).path.exists())           # 이어받은 뒤 예전 보관본은 지움
        again = protrusion.PendingRecovery(new_path, previous_shared_path=protrusion.previous_shared_path(new_path))
        self.assertEqual(again.load()['memo']['value'], '아직 저장 못 한 메모')

    def test_special_table_follows_the_switch_and_keeps_unsaved_input(self):
        special = load('src/special_table.py', 'special_' + uuid.uuid4().hex)
        share = self.storage()
        self.as_companion_module(share)
        share_folder = special.shared_folder()
        self.assertEqual(share_folder, self.new / '특수 돌출량')
        operation = {'kind': 'notes', 'base': '', 'value': '아직 저장 못 한 특이사항'}
        special.PendingDraft(share_folder).save([operation])
        self.mark_back(share)
        self.assertTrue(share.check())
        new_folder = special.shared_folder()
        self.assertEqual(new_folder, self.back / '특수 돌출량')
        self.assertEqual(special.TableStore().folder, self.back / '특수 돌출량')
        self.assertEqual(special.previous_folder(new_folder), share_folder)
        draft = special.PendingDraft(new_folder, previous=special.previous_folder(new_folder))
        self.assertEqual(draft.load(), [operation])
        self.assertTrue(draft.path.exists())
        self.assertFalse(special.PendingDraft(share_folder).path.exists())

    def test_material_link_folder_follows_the_switch(self):
        try:
            import material_ui
        except Exception as error:                                # pragma: no cover - 화면 없는 환경
            self.skipTest(str(error))
        with patch.dict(os.environ):
            os.environ.pop('JIHUNIUS_MATERIAL_SHARED', None)
            self.switched()
            self.assertEqual(Path(material_ui.shared_folder()), self.back / '소재 사용량 조사')

    def run_wash_log(self, state, saved_folder):
        """배포본에 실리는 세척일보 프로그램을 그대로 불러옵니다(창은 만들지 않음). 저장 위치는 실제 경로 그대로."""
        source = companion_source(ROOT, 'wash-log').decode('utf-8')
        self.state.parent.mkdir(parents=True, exist_ok=True)
        self.state.write_text(json.dumps(state), encoding='utf-8')
        settings = self.base / 'pc' / 'WashLog' / 'settings.json'
        settings.parent.mkdir(parents=True, exist_ok=True)
        if settings.exists():
            settings.unlink()
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
        return module, (json.loads(settings.read_text(encoding='utf-8')) if settings.exists() else None)

    def test_wash_log_default_and_remembered_folder_follow_the_switch(self):
        probe = load('src/storage_location.py', 'storage_' + uuid.uuid4().hex)
        switched = {'version': 1, 'moved': True, 'root': probe.BACK_ROOT, 'previous': probe.NEW_ROOT}
        expected = os.path.join(probe.BACK_ROOT, '세척일보')
        share = os.path.join(probe.NEW_ROOT, '세척일보')
        for remembered in (share, share.upper() + '\\', PERSONAL + r'\세척일보'):
            module, saved = self.run_wash_log(switched, remembered)
            self.assertEqual(module.DEFAULT_FOLDER, expected, remembered)
            self.assertEqual(module.DEFAULT_PARENT, probe.BACK_ROOT, remembered)
            self.assertEqual(saved, {'folder': expected, 'dept': '가공'}, remembered)   # 다른 설정은 그대로
        chosen = r'D:\다른 폴더\세척일보'
        module, saved = self.run_wash_log(switched, chosen)                  # 직접 고른 폴더는 그대로
        self.assertEqual(saved, {'folder': chosen, 'dept': '가공'})
        module, saved = self.run_wash_log(switched, None)
        self.assertEqual(module.DEFAULT_FOLDER, expected)
        self.assertIsNone(saved)

    def test_wash_log_on_the_production_share_does_not_treat_the_fallback_folder_as_old(self):
        probe = load('src/storage_location.py', 'storage_' + uuid.uuid4().hex)
        on_share = {'version': 1, 'moved': True, 'root': probe.NEW_ROOT}
        fallback = os.path.join(probe.BACK_ROOT, '세척일보')
        module, saved = self.run_wash_log(on_share, fallback)
        self.assertEqual(module.DEFAULT_FOLDER, os.path.join(probe.NEW_ROOT, '세척일보'))
        self.assertEqual(module.DEFAULT_PARENT, probe.NEW_ROOT)
        self.assertEqual(saved, {'folder': fallback, 'dept': '가공'})


if __name__ == '__main__':
    unittest.main()
