"""대비용 옮기기 프로그램: 생산공유폴더 → 개인 폴더 아래 '지후니우스 저장'.

시작 상태는 지난번 옮기기 프로그램(tools/storage_move.py)이 실제로 만든 생산공유폴더이고, 옮길 위치는
그 개인 폴더(지난번에 남긴 표시 파일·모아 둔 예전 자료·개인 파일이 그대로 있는 곳) 아래입니다.
옮긴 뒤에는 제품의 저장 코드로 그대로 읽히는지 봅니다.
"""
import ast
import importlib.util
import json
import os
import sys
import unittest
import uuid
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tests'))
import test_storage_move as first
from test_host_stability import load_app

snapshot, load_source, mover = first.snapshot, first.load_source, first.mover
back = load_source('tools/storage_move_back.py', 'storage_move_back_test')
SHARED = ('size_text', 'when', 'explain', 'tree_total', 'tree_line', 'read_json', 'same_folder',
          'exclusive_handle_check', 'range_lock_check', 'timed', 'latency', 'check_new',
          'skipped', 'all_files', 'has_entries', 'file_hash', 'stat_key', 'ready_pcs', 'marker_state', 'marker_valid',
          'copy_file', 'write_json', 'remove_tree', 'undo_set_aside', 'rename_patiently')
FEATURES = list(back.NEW_NAMES.values())


def without_locks(files):
    return {name: digest for name, digest in files.items()
            if not name.endswith(('.lock', '.tmp')) and '.locks' not in name.split(os.sep)}


class StorageMoveBackTests(unittest.TestCase):
    def setUp(self):
        first.StorageMoveTests.setUp(self)                       # 예전 구성의 자료(제품 코드로 만든 것) + 개인 파일
        mover.move(self.old, self.new, require_version=None)     # 지난번 옮기기: 개인 폴더 → 생산공유폴더
        self.share, self.personal_folder = self.new, self.old
        self.target = self.personal_folder / '지후니우스 저장'
        # 생산공유폴더에서 그 뒤로 일한 흔적(제품 코드로)
        self.protrusion.SharedStore(self.share / '돌출량 표').sync(
            [{'key': 'memo', 'base': '옮기기 전 메모', 'value': '생산공유폴더에서 고친 메모'}])
        notes = self.special.TableStore(self.share / '특수 돌출량').sync()['state']['notes']
        self.special.TableStore(self.share / '특수 돌출량').sync(
            [{'kind': 'notes', 'base': notes, 'value': '생산공유폴더에서 고친 특이사항'}])
        (self.share / '인수인계' / '.locks').mkdir(exist_ok=True)
        (self.share / '인수인계' / '.locks' / ('{:032x}.lock'.format(1))).write_bytes(b'')
        (self.share / '인수인계' / ('{:032x}.json'.format(3))).write_text(json.dumps(
            {'version': 1, 'id': '{:032x}'.format(3), 'revision': 'r3', 'deleted': False, 'title': '옮긴 뒤 전달',
             'content': '5호기 확인', 'created_at': '2026-11-18T07:00:00', 'updated_at': '2026-11-18T07:00:00'},
            ensure_ascii=False), encoding='utf-8')
        (self.share / '오류기록' / 'history.lock').write_bytes(b'0')
        (self.share / '소재 사용량 조사' / 'owner.lock').write_bytes(b'0')
        (self.share / '세척일보' / 'wash_log_data.lock').write_bytes(b'0')
        (self.share / '세척일보' / '세척일보' / '2026년' / '11월' / '2026-11-18.json').write_text(
            json.dumps({'day': '2026-11-18', 'rows': ['생산공유폴더에서 쓴 세척 기록']}, ensure_ascii=False), encoding='utf-8')
        (self.share / '돌출량 표' / 'stage_v1.tmp').write_bytes(b'half')
        self.share_before = snapshot(self.share)
        self.personal_before = snapshot(self.personal_folder)
        self.logs = []

    def move(self):
        return back.move(self.share, self.target, log=self.logs.append)

    def storage(self):
        """생산공유폴더로 넘어가 있는 PC의 저장 위치 모듈(새 버전)."""
        module = load_source('src/storage_location.py', 'storage_' + uuid.uuid4().hex)
        module.NEW_ROOT, module.BACK_ROOT = str(self.share), str(self.target)
        if module.root() is None:
            self.assertTrue(module.check())
        return module

    def assert_share_untouched(self):
        self.assertEqual(snapshot(self.share), self.share_before)
        self.assertFalse((self.share / back.SETASIDE_NAME).exists())
        self.assertTrue(back.marker_valid(self.share))
        for name in FEATURES:
            self.assertTrue((self.share / name).is_dir(), name)

    def personal_files(self):
        """개인 폴더에서 옮길 위치(지후니우스 저장)를 뺀 나머지."""
        return {name: digest for name, digest in snapshot(self.personal_folder).items()
                if name.split(os.sep)[0] != self.target.name}

    # ── 제품과 맞는지 ──
    def test_names_marker_and_places_match_the_product(self):
        storage = load_source('src/storage_location.py', 'storage_' + uuid.uuid4().hex)
        self.assertEqual(back.NEW_NAMES, storage.NEW_NAMES)
        self.assertEqual((back.MARKER_NAME, back.READY_NAME), (storage.MARKER_NAME, storage.READY_NAME))
        self.assertEqual(back.SOURCE_ROOT, storage.NEW_ROOT)
        self.assertEqual(back.TARGET_ROOT, storage.BACK_ROOT)
        self.assertEqual(back.FIRST_RECORD_NAME, mover.RECORD_NAME)
        self.assertEqual(back.SETASIDE_NAME, mover.SETASIDE_NAME)
        self.assertNotIn(back.RECORD_NAME, list(back.NEW_NAMES.values()) + [back.FIRST_RECORD_NAME])
        host = (ROOT / 'src/host/jihunius_main.py').read_text(encoding='utf-8')
        version = next(ast.literal_eval(node.value) for node in ast.parse(host).body
                       if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'SUITE_APP_VERSION')
        self.assertGreaterEqual(tuple(map(int, version.split('.'))), tuple(map(int, back.AWARE_APP_VERSION.split('.'))))
        self.assertFalse((ROOT / 'releases/jihunius/2026.11.18.2/app.pyw').read_text(encoding='utf-8').count('BACK_ROOT'))

    def test_proven_parts_are_the_same_as_in_the_first_tool(self):
        sources = {}
        for name in ('tools/storage_move.py', 'tools/storage_move_back.py'):
            text = (ROOT / name).read_text(encoding='utf-8')
            sources[name] = {node.name: ast.get_source_segment(text, node) for node in ast.parse(text).body
                             if isinstance(node, ast.FunctionDef)}
        for function in SHARED:
            self.assertEqual(sources['tools/storage_move_back.py'][function], sources['tools/storage_move.py'][function], function)

    def test_runs_on_python_3_8_grammar(self):
        ast.parse((ROOT / 'tools/storage_move_back.py').read_text(encoding='utf-8'), feature_version=(3, 8))

    # ── 점검·준비 ──
    def test_probe_only_makes_the_empty_folder_and_nothing_else_changes(self):
        storage = self.storage()
        state_before = Path(os.environ['JIHUNIUS_STORAGE_STATE']).read_bytes()
        report = back.run(self.share, self.target, log=self.logs.append)
        self.assertTrue(self.target.is_dir())
        self.assertEqual(list(self.target.iterdir()), [])        # 시험 폴더까지 지움
        self.assert_share_untouched()
        self.assertEqual(self.personal_files(), self.personal_before)
        self.assertIn('만들었습니다', report)
        self.assertIn('이 PC에서 쓸 수 있음', report)
        self.assertIn('준비됨', report)
        self.assertIn('있음(지금 쓰는 위치)', report)
        self.assertNotIn(first.SECRET, report)
        self.assertNotIn('생산공유폴더에서 고친 메모', report)   # 내용은 담지 않음
        again = back.run(self.share, self.target)
        self.assertNotIn('만들었습니다', again)
        self.assertTrue(storage.startup_check(wait=5))           # 폴더가 생겼다고 PC가 넘어가지는 않음
        self.assertEqual(storage.root(), str(self.share))
        self.assertEqual(Path(os.environ['JIHUNIUS_STORAGE_STATE']).read_bytes(), state_before)

    def test_probe_reports_an_unreachable_place_instead_of_raising(self):
        report = back.run(self.base / '없는 서버' / '지후니우스 저장', self.base / '없는 곳' / '최지훈' / '지후니우스 저장')
        self.assertIn('지금 위치를 열 수 없습니다', report)
        self.assertIn('윗폴더를 열 수 없습니다', report)
        self.assertIn('문제 있음', report)
        self.assertFalse((self.base / '없는 곳').exists())

    def test_pcs_that_started_an_aware_version_are_listed_before_and_after_the_move(self):
        self.assertIn('아직 없음', back.run(self.share, self.target))
        storage = self.storage()
        self.assertTrue(storage.startup_check(back.AWARE_APP_VERSION, wait=5))
        storage._startup['worker'].join(5)
        listed = back.ready_pcs(self.target)
        self.assertEqual([(version, bool(pc), bool(at)) for pc, version, at in listed], [(back.AWARE_APP_VERSION, True, True)])
        self.assertIn(listed[0][0] + ' · ' + back.AWARE_APP_VERSION, back.run(self.share, self.target))
        report = self.move()
        self.assertIn(listed[0][0] + ' · ' + back.AWARE_APP_VERSION, report)
        self.assertFalse((self.target / back.READY_NAME).exists())                     # 옮긴 뒤에는 기록 폴더로
        self.assertEqual(len(list((self.target / back.RECORD_NAME / back.READY_NAME).glob('*.json'))), 1)

    # ── 옮기기 ──
    def test_everything_lands_in_the_same_folder_names_and_the_product_reads_it(self):
        report = self.move()
        target = self.target
        self.assertEqual(sorted(path.name for path in target.iterdir()),
                         sorted(FEATURES + [back.FIRST_RECORD_NAME, back.RECORD_NAME, back.MARKER_NAME]))
        moved = {name: digest for name, digest in without_locks(self.share_before).items()
                 if name.split(os.sep)[0] in FEATURES + [back.FIRST_RECORD_NAME]}
        landed = {name: digest for name, digest in snapshot(target).items()
                  if name.split(os.sep)[0] in FEATURES + [back.FIRST_RECORD_NAME]}
        self.assertEqual(landed, moved)                          # 폴더 구성·파일 내용 그대로, 잠금·임시 파일만 빠짐
        self.assertTrue(moved)
        self.assertEqual(list((target / '세척완료').iterdir()), [])
        # 제품 코드가 옮긴 폴더에서 그대로 읽는지
        state = self.protrusion.SharedStore(target / '돌출량 표').sync()['state']
        self.assertEqual((state['values']['memo'], state['revision']), ('생산공유폴더에서 고친 메모', 3))
        table = self.special.TableStore(target / '특수 돌출량').sync()['state']
        self.assertEqual((table['notes'], table['revision']), ('생산공유폴더에서 고친 특이사항', 3))
        synced = self.errors.sync_shared(target / '오류기록', {'pc_id': self.pc, 'epoch': 'after-clear',
                                                               'records': [self.record], 'pending': None})
        self.assertEqual(synced['epoch'], 'after-clear')         # 세대가 이어져 지난 기록이 남음
        self.assertEqual([row['id'] for row in synced['records']], ['r1'])
        import material_sync
        self.assertEqual(material_sync.Discovery(target / '소재 사용량 조사').exchange('read'), self.owner)
        host = load_app()
        notes = host.HandoverStore(target / '인수인계').load()
        self.assertEqual(sorted(note['title'] for note in notes), ['교대 전달', '옮긴 뒤 전달'])
        self.assertIn('옮긴 파일 {}개'.format(len(moved)), report)
        self.assertIn(str(self.share / back.SETASIDE_NAME), report)
        self.assertFalse((target / back.RECORD_NAME / back.JOURNAL_NAME).exists())
        self.assertEqual(list(target.rglob('*.옮기는중')) + list(target.rglob('*.쓰는중')), [])
        manifest = json.loads((target / back.RECORD_NAME / back.MANIFEST_NAME).read_text(encoding='utf-8'))
        self.assertEqual({os.sep.join(entry['path']): entry['sha256'] for entry in manifest['files']}, moved)

    def test_a_pc_on_the_share_follows_after_the_move_with_no_other_step(self):
        storage = self.storage()
        previous = sys.modules.get('jihunius_storage')
        sys.modules['jihunius_storage'] = storage
        self.addCleanup(lambda: sys.modules.pop('jihunius_storage', None) if previous is None
                        else sys.modules.__setitem__('jihunius_storage', previous))
        self.assertEqual(self.protrusion.shared_folder(), self.share / '돌출량 표')
        self.move()
        self.assertEqual(storage.root(), str(self.share))        # 다시 켜기 전
        self.assertTrue(storage.startup_check(back.AWARE_APP_VERSION, wait=5))        # 다시 켬: 업데이트·설정 없이
        self.assertEqual(storage.root(), str(self.target))
        self.assertEqual(self.protrusion.shared_folder(), self.target / '돌출량 표')
        self.assertEqual(self.protrusion.SharedStore().sync()['state']['values']['memo'], '생산공유폴더에서 고친 메모')
        self.assertEqual(self.special.TableStore().sync()['state']['notes'], '생산공유폴더에서 고친 특이사항')
        self.assertEqual(Path(storage.folder('wash')), self.target / '세척일보')
        self.assertTrue((Path(storage.folder('wash')) / '저장정보.json').is_file())

    def test_share_data_is_set_aside_intact_and_the_personal_folder_is_untouched(self):
        self.move()
        aside = self.share / back.SETASIDE_NAME
        self.assertEqual(snapshot(aside), self.share_before)     # 잠금 파일·표시까지 그대로 모아 둠
        self.assertEqual(sorted(path.name for path in self.share.iterdir()), sorted(FEATURES + [back.SETASIDE_NAME]))
        for name in FEATURES:
            self.assertTrue((self.share / name).is_file(), name)
            self.assertIn('옮겼습니다', (self.share / name).read_text(encoding='utf-8'))
        self.assertFalse(back.marker_valid(self.share))          # 생산공유폴더는 더 이상 '쓰는 위치'가 아님
        self.assertEqual(self.personal_files(), self.personal_before)
        self.assertEqual(sorted(path.name for path in self.personal_folder.iterdir()),
                         sorted(['2026년', 'TwoSeatChat_data', '휴가신청서.xlsx', mover.SETASIDE_NAME,
                                 mover.HANDOVER_NAME, '세척일보', '지후니우스 저장']))

    def test_a_program_that_was_not_updated_cannot_keep_working_in_the_production_share(self):
        self.move()
        with self.assertRaises(OSError):
            self.protrusion.SharedStore(self.share / '돌출량 표').sync()
        with self.assertRaises(OSError):
            self.special.TableStore(self.share / '특수 돌출량').sync()
        host = load_app()
        with self.assertRaises(host.WorkError):
            host.HandoverStore(self.share / '인수인계').load()
        with self.assertRaises(host.WorkError):
            host.HandoverStore(self.share / '인수인계').add('새 메모', '내용')
        wash = load_source('src/wash_log.py', 'wash_' + uuid.uuid4().hex)
        wash.DEFAULT_PARENT, wash.DEFAULT_FOLDER = str(self.share), str(self.share / '세척일보')
        with patch.object(wash, 'HOME_TEST', False), self.assertRaises(OSError):
            wash.Store(self.share / '세척일보')
        for name in FEATURES:
            self.assertTrue((self.share / name).is_file(), name)  # 새 폴더·새 표가 생기지 않음
        # 2026.11.18.2까지의 저장 위치 코드: 생산공유폴더를 기억한 PC는 계속 그 자리를 가리키고(막혀 있음),
        # 처음 켜는 PC는 생산공유폴더의 표시가 없어 그쪽으로 넘어가지 않습니다.
        tree = ast.parse((ROOT / 'releases/jihunius/2026.11.18.2/app.pyw').read_text(encoding='utf-8'))
        source = next(node.value.args[1].value for node in tree.body
                      if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'SuiteStorage')
        released = ModuleType('released_storage')
        exec(compile(source, 'released_storage', 'exec'), released.__dict__)
        released.NEW_ROOT = str(self.share)
        self.assertFalse(released.marker_present())

    def test_things_that_are_not_ours_stay_where_they_are(self):
        (self.share / '누가 넣어 둔 파일.xlsx').write_bytes(b'not ours')
        (self.share / '다른 폴더').mkdir()
        (self.share / '다른 폴더' / 'a.txt').write_text('x', encoding='utf-8')
        report = self.move()
        self.assertEqual((self.share / '누가 넣어 둔 파일.xlsx').read_bytes(), b'not ours')
        self.assertTrue((self.share / '다른 폴더' / 'a.txt').is_file())
        self.assertFalse((self.target / '다른 폴더').exists())
        self.assertIn('옮기지 않고 그대로 둡니다', report)
        self.assertIn('다른 폴더', report)

    def test_a_missing_feature_folder_becomes_an_empty_one(self):
        (self.share / '세척완료').rmdir()
        report = self.move()
        self.assertEqual(list((self.target / '세척완료').iterdir()), [])
        self.assertTrue((self.share / '세척완료').is_file())
        self.assertIn('빈 폴더로 만듭니다', report)

    # ── 하지 않는 경우 ──
    def refused(self, text, source=None, target=None):
        with self.assertRaises(back.MoveError) as caught:
            back.move(source or self.share, target or self.target, log=self.logs.append)
        self.assertIn(text, str(caught.exception))
        return str(caught.exception)

    def test_refuses_when_the_share_is_not_the_place_in_use(self):
        (self.share / back.MARKER_NAME).unlink()
        self.refused('쓰고 있는 곳이 아닙니다')
        self.assertFalse((self.share / back.SETASIDE_NAME).exists())
        self.assertFalse(back.marker_valid(self.target))
        (self.share / back.MARKER_NAME).write_bytes(b'{"version": 1, "moved": tr')
        self.refused('확인할 수 없어')

    def test_refuses_twice_and_when_the_target_marker_cannot_be_read(self):
        self.move()
        self.refused('이미 옮겨져 있습니다')
        (self.target / back.MARKER_NAME).write_bytes(b'{"version": 1, "moved": tr')
        self.refused('확인할 수 없어')

    def test_refuses_while_wash_completion_is_running(self):
        (self.share / '세척완료' / back.RUN_MARKER).write_text('{"pc": "pc8"}', encoding='utf-8')
        self.share_before = snapshot(self.share)
        self.refused('세척완료가 실행 중')
        self.assert_share_untouched()
        self.assertEqual([path.name for path in self.target.iterdir()], [])

    def test_refuses_when_the_target_already_holds_something(self):
        (self.target / '세척일보').mkdir(parents=True)
        (self.target / '세척일보' / '저장정보.json').write_text('{}', encoding='utf-8')
        self.refused('이미 자료가 있어')
        self.assert_share_untouched()
        self.assertEqual((self.target / '세척일보' / '저장정보.json').read_text(encoding='utf-8'), '{}')

    def test_refuses_the_same_place_an_unreachable_parent_and_an_unusable_target(self):
        self.refused('같습니다', target=self.share)
        self.refused('윗폴더를 열 수 없습니다', target=self.base / '없는 곳' / '최지훈' / '지후니우스 저장')
        self.assertFalse((self.base / '없는 곳').exists())
        with patch.object(back, 'range_lock_check', lambda path: '안 됨 · 두 번째 잠금이 막히지 않음'):
            self.refused('옮길 위치에 문제가 있어')
        self.assert_share_untouched()
        self.assertEqual(list(self.target.iterdir()), [])

    def test_a_place_that_was_already_moved_away_is_never_brought_back_to_life(self):
        self.move()
        kept = snapshot(self.share)
        elsewhere = self.base / 'elsewhere' / '지후니우스 저장'
        elsewhere.parent.mkdir(parents=True)
        self.refused('이미 한 폴더로 모아져', target=elsewhere)               # 다른 곳으로 또 옮기려 해도
        (self.target / back.MARKER_NAME).unlink()
        self.refused('이미 한 폴더로 모아져')                                # 옮긴 위치의 표시가 없어져도
        self.assertEqual(snapshot(self.share), kept)                         # 막는 표시·모아 둔 자료 그대로
        for name in FEATURES:
            self.assertTrue((self.share / name).is_file(), name)
        state = self.protrusion.SharedStore(self.target / '돌출량 표').sync()['state']
        self.assertEqual(state['values']['memo'], '생산공유폴더에서 고친 메모')   # 옮긴 위치의 자료도 그대로
        (self.share / back.SETASIDE_NAME).rename(self.base / 'gone')           # 모아 둔 것까지 치운 뒤라면
        self.refused('쓰고 있는 곳이 아닙니다', target=elsewhere)

    # ── 중간에 일이 생겼을 때 ──
    def test_files_changed_while_copying_are_copied_again(self):
        table = self.share / '돌출량 표' / self.protrusion.SHARED_FILENAME
        real_copy = back.copy_file
        state = {'done': False}

        def copy_then_edit(source, destination):
            result = real_copy(source, destination)
            if source == table and not state['done']:
                state['done'] = True
                self.protrusion.SharedStore(self.share / '돌출량 표').sync(
                    [{'key': 'memo', 'base': '생산공유폴더에서 고친 메모', 'value': '복사하는 사이 고친 메모'}])
                (self.share / '인수인계' / ('{:032x}.json'.format(9))).write_text(
                    json.dumps({'version': 1, 'id': '{:032x}'.format(9), 'revision': 'n', 'deleted': True}), encoding='utf-8')
                (self.share / '세척일보' / '공구대.json').unlink()
            return result

        with patch.object(back, 'copy_file', copy_then_edit):
            self.move()
        state = self.protrusion.SharedStore(self.target / '돌출량 표').sync()['state']
        self.assertEqual(state['values']['memo'], '복사하는 사이 고친 메모')
        self.assertTrue((self.target / '인수인계' / '{:032x}.json'.format(9)).is_file())
        self.assertFalse((self.target / '세척일보' / '공구대.json').exists())            # 그 사이 없어진 파일은 남기지 않음

    def test_gives_up_when_the_share_keeps_changing_and_starts_over_next_time(self):
        real_copy = back.copy_file
        counter = {'n': 0}

        def always_edit(source, destination):
            result = real_copy(source, destination)
            if source.name == '공구대.json':
                counter['n'] += 1
                source.write_text(json.dumps({'tools': counter['n'], 'pad': 'x' * counter['n']}), encoding='utf-8')
            return result

        with patch.object(back, 'copy_file', always_edit):
            self.refused('계속 바뀝니다')
        self.assertFalse(back.marker_valid(self.target))
        self.assertFalse((self.share / back.SETASIDE_NAME).exists())
        self.assertTrue(back.marker_valid(self.share))
        self.move()                                              # 다시 누르면 남은 복사본을 지우고 처음부터
        self.assertTrue(back.marker_valid(self.target))
        self.assertIn('지난번에 끝내지 못한 복사본을 지우는 중…', self.logs)

    def test_folder_still_in_use_puts_everything_back(self):
        real_rename = os.rename

        def in_use(source, target):
            if Path(source) == self.share / '세척일보':
                error = PermissionError(13, 'The process cannot access the file', str(source))
                error.winerror = 32
                raise error
            return real_rename(source, target)

        with patch.object(back.os, 'rename', in_use), patch.object(back.time, 'sleep', lambda seconds: None), \
                patch.object(back.time, 'monotonic', side_effect=iter(range(0, 100000, 5)).__next__):
            message = self.refused('아직 켜져 있을 수')
        self.assertIn('"세척일보"', message)
        self.assert_share_untouched()
        self.assertFalse(back.marker_valid(self.target))

    def test_folder_held_only_for_a_moment_is_retried(self):
        real_rename = os.rename
        calls = {'n': 0}

        def briefly_in_use(source, target):
            if Path(source) == self.share / '인수인계':
                calls['n'] += 1
                if calls['n'] <= 2:
                    raise PermissionError(13, 'The process cannot access the file', str(source))
            return real_rename(source, target)

        with patch.object(back.os, 'rename', briefly_in_use), patch.object(back.time, 'sleep', lambda seconds: None):
            self.move()
        self.assertEqual(calls['n'], 3)
        self.assertTrue(back.marker_valid(self.target))

    def test_failing_to_write_the_marker_puts_everything_back(self):
        real_write = back.write_json

        def fail_marker(path, value):
            if path.name == back.MARKER_NAME:
                raise OSError(28, 'No space left on device')
            return real_write(path, value)

        with patch.object(back, 'write_json', fail_marker):
            self.refused('원래대로 되돌렸습니다')
        self.assert_share_untouched()
        self.assertFalse(back.marker_valid(self.target))

    def test_a_run_that_died_half_way_is_put_back_and_the_next_run_finishes(self):
        storage = self.storage()
        real_set_aside = back.set_aside

        def die_after(plan, source_root):
            real_set_aside(plan, source_root)
            raise RuntimeError('전원이 꺼짐')                          # 자료를 모아 둔 직후, 완료 표시 전

        with patch.object(back, 'set_aside', die_after):
            with self.assertRaises(RuntimeError):
                self.move()
        self.assertTrue((self.share / back.SETASIDE_NAME).is_dir())   # 모아 둔 채로 멈춤
        self.assertFalse(back.marker_valid(self.target))
        self.assertTrue(storage.startup_check(wait=5))
        self.assertEqual(storage.root(), str(self.share))             # 표시가 없으니 PC는 넘어가지 않음
        self.move()                                                   # 다시 누르면 되돌린 뒤 처음부터
        self.assertIn('지난번에 멈춘 옮기기를 되돌리는 중…', self.logs)
        self.assertTrue(back.marker_valid(self.target))
        self.assertEqual(snapshot(self.share / back.SETASIDE_NAME), self.share_before)
        state = self.protrusion.SharedStore(self.target / '돌출량 표').sync()['state']
        self.assertEqual(state['values']['memo'], '생산공유폴더에서 고친 메모')

    def test_restoring_a_stopped_run_leaves_the_share_exactly_as_it_was(self):
        real_write = back.write_json

        def die(path, value):
            if path.name == back.MARKER_NAME:
                raise RuntimeError('전원이 꺼짐')
            return real_write(path, value)

        with patch.object(back, 'write_json', die):
            with self.assertRaises(RuntimeError):
                self.move()
        self.assertTrue(back.restore_interrupted(self.share))
        self.assert_share_untouched()
        self.assertFalse(back.restore_interrupted(self.share))

    # ── 예전 자료 지우기 ──
    def test_cleanup_removes_only_what_was_set_aside_in_the_share(self):
        self.move()
        target_before = snapshot(self.target)
        report = back.cleanup(self.share, self.target, log=self.logs.append)
        self.assertFalse((self.share / back.SETASIDE_NAME).exists())
        self.assertEqual(sorted(path.name for path in self.share.iterdir()), sorted(FEATURES))   # 막는 표시만 남음
        self.assertEqual(snapshot(self.target), target_before)
        self.assertEqual(self.personal_files(), self.personal_before)
        self.assertIn('예전 자료를 지웠습니다', report)
        with self.assertRaises(back.MoveError):
            back.cleanup(self.share, self.target)                # 두 번째는 지울 것이 없음

    def test_cleanup_still_works_after_the_program_kept_working_in_the_new_place(self):
        self.move()
        self.protrusion.SharedStore(self.target / '돌출량 표').sync(
            [{'key': 'memo', 'base': '생산공유폴더에서 고친 메모', 'value': '옮긴 뒤 메모'}])
        (self.target / '세척일보' / '백업' / '세척일보' / '2026-11-16' / '070000.json').unlink()
        back.cleanup(self.share, self.target)
        self.assertFalse((self.share / back.SETASIDE_NAME).exists())

    def test_cleanup_refuses_before_the_move_and_when_anything_looks_wrong(self):
        with self.assertRaises(back.MoveError) as caught:
            back.cleanup(self.share, self.target)
        self.assertIn('아직 옮기기가 끝나지 않았습니다', str(caught.exception))
        self.assert_share_untouched()
        self.move()
        aside = self.share / back.SETASIDE_NAME
        (aside / '세척일보' / '공구대.json').write_text('{"changed": true}', encoding='utf-8')
        (aside / '인수인계' / '모르는 파일.txt').write_text('?', encoding='utf-8')
        kept = snapshot(aside)
        with self.assertRaises(back.MoveError) as caught:
            back.cleanup(self.share, self.target)
        self.assertIn('내용이 바뀐 파일', str(caught.exception))
        self.assertIn('옮긴 목록에 없는 파일', str(caught.exception))
        self.assertEqual(snapshot(aside), kept)                  # 하나도 지우지 않음
        (self.target / back.RECORD_NAME / back.MANIFEST_NAME).unlink()
        with self.assertRaises(back.MoveError):
            back.cleanup(self.share, self.target)
        self.assertEqual(snapshot(aside), kept)

    def test_the_first_tools_cleanup_of_the_personal_folder_still_works_from_the_new_place(self):
        # 지난번 옮기기의 '예전 자료 지우기'를 아직 안 했더라도, 옮긴 뒤에는 새 위치를 가리켜 그대로 할 수 있습니다
        # (지난번 기록 폴더와 옮긴 파일 목록이 함께 옮겨지므로).
        self.move()
        self.assertTrue((self.personal_folder / mover.SETASIDE_NAME).is_dir())
        target_before = snapshot(self.target)
        mover.cleanup(self.personal_folder, self.target)
        self.assertFalse((self.personal_folder / mover.SETASIDE_NAME).exists())
        self.assertEqual(snapshot(self.target), target_before)
        self.assertEqual(sorted(path.name for path in self.personal_folder.iterdir()),
                         sorted(['2026년', 'TwoSeatChat_data', '휴가신청서.xlsx', mover.HANDOVER_NAME, '세척일보', '지후니우스 저장']))


if __name__ == '__main__':
    unittest.main()
