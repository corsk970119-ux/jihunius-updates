"""저장 위치 점검 프로그램: 예전 위치는 읽기만 하고, 내용은 결과 글에 담지 않으며, 새 위치에는 흔적을 남기지 않습니다."""
import hashlib
import importlib.util
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('storage_probe_test', ROOT / 'tools/storage_move.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

SECRET = 'SECRET-고객이름-토큰-0123456789'


def snapshot(folder):
    """폴더 안 모든 파일의 경로·내용 해시(바뀐 것이 없는지 비교용)."""
    result = {}
    for path in sorted(Path(folder).rglob('*')):
        if path.is_file():
            result[str(path.relative_to(folder))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


class StorageProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.old = base / 'old' / '최지훈'
        self.new = base / 'new' / '지후니우스 저장'
        self.new.mkdir(parents=True)
        (self.new / '이미 있던 파일.txt').write_text('건드리면 안 됨', encoding='utf-8')
        handover = self.old / probe.HANDOVER_NAME
        (handover / '오류기록').mkdir(parents=True)
        (handover / '소재재고조사').mkdir()
        for number, deleted in enumerate((False, False, True)):
            name = '{:032x}'.format(number + 1)
            (handover / (name + '.json')).write_text(json.dumps(
                {'version': 1, 'id': name, 'revision': 'r', 'deleted': deleted, 'title': SECRET, 'content': SECRET}),
                encoding='utf-8')
        (handover / '돌출량_현황표.json').write_text(json.dumps(
            {'version': 3, 'revision': 41, 'values': {'memo': SECRET, 'a': True}}), encoding='utf-8')
        (handover / '특수_돌출량.json').write_text(json.dumps(
            {'schema': 1, 'revision': 7, 'rows': [{'id': 'x', 'cells': [SECRET, '', '']}], 'notes': SECRET}),
            encoding='utf-8')
        (handover / '돌출량_현황표.lock').write_bytes(b'')
        (handover / '오류기록' / 'generation.json').write_text('{"epoch": "abc"}', encoding='utf-8')
        (handover / '오류기록' / ('pc-' + 'a' * 32 + '.json')).write_text(json.dumps(
            {'epoch': 'abc', 'records': [{'message': SECRET}]}), encoding='utf-8')
        (handover / '소재재고조사' / 'owner.json').write_text(json.dumps({'token': SECRET}), encoding='utf-8')
        # 지금 쓰는 세척일보(프로그램 기본 위치)와, 개인 폴더 바로 아래에 남은 예전 저장 폴더
        active = self.old / '세척일보'
        for day in ('2026-11-15', '2026-11-16', '2026-11-17'):
            path = active / '세척일보' / '2026년' / '11월' / (day + '.json')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({'note': SECRET}), encoding='utf-8')
        (active / '저장정보.json').write_text('{"format": 2, "id": "11112222aaaabbbbccccddddeeeeffff"}', encoding='utf-8')
        (active / '공구대.json').write_text(json.dumps({'x': SECRET}), encoding='utf-8')
        (active / '부서메모.json').write_text(json.dumps({'x': SECRET}), encoding='utf-8')
        (active / '백업' / '세척일보' / '2026-11-16').mkdir(parents=True)
        (active / '백업' / '세척일보' / '2026-11-16' / 'a.json').write_text(SECRET, encoding='utf-8')
        (self.old / '저장정보.json').write_text('{"format": 2, "id": "99998888aaaabbbbccccddddeeeeffff"}', encoding='utf-8')
        (self.old / '공구대.json').write_text('{}', encoding='utf-8')
        (self.old / '휴가신청서.xlsx').write_bytes(b'personal')

    def run_probe(self, **options):
        return probe.run(self.old, self.new, config_folder=options.pop('config_folder', None), **options)

    def test_old_location_is_only_read_and_contents_stay_out_of_the_report(self):
        before = snapshot(self.old)
        report = self.run_probe()
        self.assertEqual(snapshot(self.old), before)
        self.assertNotIn(SECRET, report)
        self.assertNotIn('SECRET', report)
        self.assertNotIn('휴가신청서', report)                      # 개인 파일은 적지 않음

    def test_inventory_counts_what_has_to_move(self):
        report = self.run_probe()
        self.assertIn('인수인계 메모 파일 3개', report)
        self.assertIn('보이는 메모 2 · 삭제 표시 1 · 읽지 못함 0', report)
        self.assertIn('형식 3 · 고친 횟수 41 · 항목 2개', report)
        self.assertIn('형식 1 · 고친 횟수 7 · 줄 1개', report)
        self.assertIn('PC 파일 1개 · 세대 파일(generation.json) 있음', report)
        self.assertIn('연결 파일(owner.json) 있음', report)
        self.assertIn('(내용은 읽지 않음)', report)
        self.assertIn('돌출량_현황표.lock', report)               # 그 밖의 항목으로 이름만
        self.assertIn('날짜별 일보 3일치', report)
        self.assertIn('2026-11-15 ~ 2026-11-17', report)

    def test_two_wash_stores_are_told_apart(self):
        report = self.run_probe()
        self.assertIn('식별 번호 앞 8자 11112222', report)
        self.assertIn('식별 번호 앞 8자 99998888', report)
        self.assertIn('세척일보 저장 폴더가 2곳', report)
        self.assertIn('[세척일보 후보: 프로그램 기본 위치]', report)
        self.assertIn('[세척일보 후보: 개인 폴더 바로 아래]', report)

    def test_this_pc_configured_wash_folder_is_listed_first_and_not_twice(self):
        report = self.run_probe(config_folder=str(self.old / '세척일보'))
        self.assertIn('이 PC의 세척일보가 기억하는 저장 폴더: ' + str(self.old / '세척일보'), report)
        self.assertIn('[세척일보 후보: 이 PC 설정]', report)
        self.assertNotIn('[세척일보 후보: 프로그램 기본 위치]', report)
        self.assertEqual(report.count('식별 번호 앞 8자 11112222'), 1)

    def test_new_location_is_written_checked_and_left_as_it_was(self):
        before = snapshot(self.new)
        report = self.run_probe()
        self.assertEqual(snapshot(self.new), before)
        self.assertEqual(sorted(path.name for path in self.new.iterdir()), ['이미 있던 파일.txt'])
        for line in ('시험 폴더 만들기: 됨', '이름 바꿔 덮어쓰기: 됨', '있는 파일 위로 바꾸기: 됨', '다시 읽어 같은지: 같음',
                     '독점 잠금(인수인계·돌출량 방식): 됨', '바이트 잠금(세척일보·특수 돌출량·오류기록·소재 방식): 됨',
                     '시험 폴더 지우기: 됨', '새 위치 판정: 이 PC에서 쓸 수 있음'):
            self.assertIn(line, report)

    def test_missing_or_unwritable_new_location_is_reported_not_raised(self):
        report = probe.run(self.old, self.new / '없는 폴더', config_folder=None)
        self.assertIn('폴더가 없거나 이 PC에서 열 수 없습니다', report)
        self.assertIn('새 위치 판정: 문제 있음', report)
        real_open = os.open

        def denied(path, flags, mode=0o777, **options):
            if str(path).endswith('시험.tmp'):
                raise PermissionError(13, 'Access is denied', str(path))
            return real_open(path, flags, mode, **options)

        with patch.object(probe.os, 'open', denied):
            report = self.run_probe()
        self.assertIn('시험 중 실패 · PermissionError', report)
        self.assertIn('새 위치 판정: 문제 있음', report)
        self.assertEqual(sorted(path.name for path in self.new.iterdir()), ['이미 있던 파일.txt'])

    def test_a_lock_that_does_not_exclude_is_reported(self):
        with patch.object(probe, 'range_lock_check', lambda path: '안 됨 · 두 번째 잠금이 막히지 않음'):
            report = self.run_probe()
        self.assertIn('바이트 잠금(세척일보·특수 돌출량·오류기록·소재 방식): 안 됨', report)
        self.assertIn('새 위치 판정: 문제 있음', report)

    def test_unreachable_old_location_is_reported_not_raised(self):
        report = probe.run(self.old.parent / '없음', self.new, config_folder=None)
        self.assertIn('열 수 없음', report)
        self.assertIn('새 위치 판정: 이 PC에서 쓸 수 있음', report)

    def test_runs_on_python_3_8_grammar(self):
        import ast
        ast.parse((ROOT / 'tools/storage_move.py').read_text(encoding='utf-8'), feature_version=(3, 8))


# ── 옮기기·지우기 ───────────────────────────────────────────────────────────────

import sys
import uuid
from pathlib import PureWindowsPath

sys.path.insert(0, str(ROOT / 'src'))
mover = probe


def load_source(path, name):
    spec_ = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec_)
    spec_.loader.exec_module(module)
    return module


class StorageMoveTests(unittest.TestCase):
    """실제 지후니우스 저장 코드로 만든 자료를 옮기고, 옮긴 뒤에도 같은 코드로 그대로 읽히는지 봅니다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.base = base
        self.old = base / 'old' / '최지훈'
        self.new = base / 'new' / '지후니우스 저장'
        self.new.mkdir(parents=True)
        environment = patch.dict(os.environ, {'LOCALAPPDATA': str(base / 'pc'),
                                              'JIHUNIUS_STORAGE_STATE': str(base / 'pc' / 'storage_location.json')})
        environment.start()
        self.addCleanup(environment.stop)
        self.protrusion = load_source('src/protrusion.py', 'protrusion_' + uuid.uuid4().hex)
        self.special = load_source('src/special_table.py', 'special_' + uuid.uuid4().hex)
        self.errors = load_source('src/error_history.py', 'errors_' + uuid.uuid4().hex)
        handover = self.old / mover.HANDOVER_NAME
        handover.mkdir(parents=True)
        # 돌출량 표·특수 돌출량: 제품 코드로 만들고 한 번씩 고침
        store = self.protrusion.SharedStore(handover)
        store.sync()
        store.sync([{'key': 'memo', 'base': '', 'value': '옮기기 전 메모'}])
        table = self.special.TableStore(handover)
        notes = table.sync()['state']['notes']
        table.sync([{'kind': 'notes', 'base': notes, 'value': '옮기기 전 특이사항'}])
        # 인수인계 메모(보이는 것 1, 삭제 표시 1)와 메모별 잠금 폴더
        (handover / '.locks').mkdir()
        for number, deleted in enumerate((False, True)):
            name = '{:032x}'.format(number + 1)
            note = {'version': 1, 'id': name, 'revision': 'r' + str(number), 'deleted': deleted}
            if not deleted:
                note.update(title='교대 전달', content='3호기 소재 확인', created_at='2026-11-17T07:00:00',
                            updated_at='2026-11-17T07:00:00')
            (handover / (name + '.json')).write_text(json.dumps(note, ensure_ascii=False), encoding='utf-8')
            (handover / '.locks' / (name + '.lock')).write_bytes(b'')
        # 오류기록(세대가 '0'이 아닌 상태) · 소재 연결 파일
        self.pc = 'a' * 32
        (handover / '오류기록').mkdir()
        (handover / '오류기록' / 'generation.json').write_text('{"epoch": "after-clear"}', encoding='utf-8')
        self.record = {'id': 'r1', 'pc_id': self.pc, 'epoch': 'after-clear', 'last': time.time(), 'count': 1, 'message': '예전 오류'}
        (handover / '오류기록' / ('pc-' + self.pc + '.json')).write_text(
            json.dumps({'epoch': 'after-clear', 'records': [self.record]}), encoding='utf-8')
        (handover / '오류기록' / 'history.lock').write_bytes(b'0')
        (handover / '소재재고조사').mkdir()
        self.owner = {'owner_id': 'b' * 32, 'owner_name': 'PC-A', 'token': 'c' * 64, 'host': '192.168.0.10', 'port': 5123}
        (handover / '소재재고조사' / 'owner.json').write_text(json.dumps(self.owner), encoding='utf-8')
        (handover / '소재재고조사' / 'owner.lock').write_bytes(b'0')
        # 지금 쓰는 세척일보 + 개인 폴더 바로 아래에 남은 예전 흔적
        wash = self.old / '세척일보'
        for day in ('2026-11-16', '2026-11-17'):
            path = wash / '세척일보' / '2026년' / '11월' / (day + '.json')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({'day': day, 'rows': ['세척 기록']}, ensure_ascii=False), encoding='utf-8')
        (wash / '저장정보.json').write_text('{"format": 2, "id": "ed54f5c1aaaabbbbccccddddeeeeffff"}', encoding='utf-8')
        (wash / '공구대.json').write_text('{"tools": 1}', encoding='utf-8')
        (wash / '부서메모.json').write_text('[]', encoding='utf-8')
        (wash / 'wash_log_data.json').write_text('{"format": 2}', encoding='utf-8')
        (wash / 'wash_log_data.lock').write_bytes(b'0')
        (wash / '백업' / '세척일보' / '2026-11-16').mkdir(parents=True)
        (wash / '백업' / '세척일보' / '2026-11-16' / '070000.json').write_text('{"b": 1}', encoding='utf-8')
        (wash / '2026년' / '10월').mkdir(parents=True)          # 예전 흔적이 남긴 날짜 파일(지금 폴더 안에 섞여 있음)
        (wash / '2026년' / '10월' / '2026-10-23.json').write_text('{"stray": 1}', encoding='utf-8')
        (self.old / '저장정보.json').write_text('{"format": 2, "id": "610080b4aaaabbbbccccddddeeeeffff"}', encoding='utf-8')
        (self.old / '공구대.json').write_text('{}', encoding='utf-8')
        (self.old / '부서메모.json').write_text('[]', encoding='utf-8')
        (self.old / 'wash_log_data.json').write_text('{"format": 2}', encoding='utf-8')
        (self.old / 'wash_log_data.lock').write_bytes(b'0')
        (self.old / '백업' / '부서메모' / '기록').mkdir(parents=True)
        (self.old / '백업' / '부서메모' / '기록' / 'x.json').write_text('[]', encoding='utf-8')
        (self.old / '이전통합백업').mkdir()
        # 개인 파일(절대 건드리면 안 됨)
        (self.old / '휴가신청서.xlsx').write_bytes(b'personal-1')
        (self.old / '2026년').mkdir()
        (self.old / '2026년' / '일일 업무 보고.xlsx').write_bytes(b'personal-2')
        (self.old / 'TwoSeatChat_data').mkdir()
        (self.old / 'TwoSeatChat_data' / 'chat.db').write_bytes(b'personal-3')
        self.personal = {name: digest for name, digest in snapshot(self.old).items()
                         if name.split(os.sep)[0] in ('휴가신청서.xlsx', '2026년', 'TwoSeatChat_data')}
        self.before = snapshot(self.old)
        self.logs = []

    def move(self, **options):
        options.setdefault('require_version', None)
        return mover.move(self.old, self.new, log=self.logs.append, **options)

    def assert_old_untouched(self):
        self.assertEqual(snapshot(self.old), self.before)
        self.assertFalse((self.old / mover.SETASIDE_NAME).exists())
        self.assertTrue((self.old / mover.HANDOVER_NAME).is_dir())
        self.assertTrue((self.old / '세척일보').is_dir())

    def personal_files(self):
        return {name: digest for name, digest in snapshot(self.old).items() if name in self.personal}

    # ── 이름·표시가 제품과 같은지 ──
    def test_folder_names_marker_and_paths_match_the_product(self):
        storage = load_source('src/storage_location.py', 'storage_' + uuid.uuid4().hex)
        self.assertEqual(mover.NEW_NAMES, storage.NEW_NAMES)
        self.assertEqual(mover.MARKER_NAME, storage.MARKER_NAME)
        self.assertEqual(mover.NEW_ROOT, storage.NEW_ROOT)
        self.assertEqual(mover.OLD_PARENT, storage.OLD_PARENT)
        window = PureWindowsPath
        self.assertEqual(window(storage.OLD_FOLDERS['handover']), window(mover.OLD_PARENT) / mover.HANDOVER_NAME)
        self.assertEqual(window(storage.OLD_FOLDERS['wash']), window(mover.OLD_PARENT) / mover.WASH_NAME)
        # 옮기기 프로그램이 요구하는 버전은 새 위치를 아는 버전이어야 하고, 지금 소스는 그 이상이어야 합니다.
        import re
        main = (ROOT / 'src/host/jihunius_main.py').read_text(encoding='utf-8')
        current = re.search(r"^SUITE_APP_VERSION = '([^']+)'", main, re.M).group(1)
        self.assertGreaterEqual(mover.version_tuple(current), mover.version_tuple(mover.REQUIRED_APP_VERSION))
        self.assertGreaterEqual(mover.version_tuple(mover.REQUIRED_APP_VERSION), (2026, 11, 17, 2))
        self.assertEqual(main.count('SuiteStorage.startup_check(SUITE_APP_VERSION)'), 1)

    # ── 옮기기 ──
    def test_everything_lands_in_its_feature_folder_and_the_product_reads_it(self):
        report = self.move()
        new = self.new
        self.assertEqual(sorted(path.name for path in new.iterdir()),
                         sorted(list(mover.NEW_NAMES.values()) + [mover.RECORD_NAME, mover.MARKER_NAME]))
        self.assertEqual(sorted(path.name for path in (new / '인수인계').iterdir()),
                         ['{:032x}.json'.format(1), '{:032x}.json'.format(2)])           # 잠금 폴더는 옮기지 않음
        self.assertEqual(sorted(path.name for path in (new / '오류기록').iterdir()),
                         ['generation.json', 'pc-' + self.pc + '.json'])
        self.assertEqual([path.name for path in (new / '소재 사용량 조사').iterdir()], ['owner.json'])
        self.assertEqual(list((new / '세척완료').iterdir()), [])
        wash_before = {name[len('세척일보' + os.sep):]: digest for name, digest in self.before.items()
                       if name.startswith('세척일보' + os.sep) and not name.endswith('.lock')}
        self.assertEqual(snapshot(new / '세척일보'), wash_before)
        leftover = new / mover.RECORD_NAME / mover.LEFTOVER_NAME
        self.assertEqual(sorted(str(path.relative_to(leftover)) for path in leftover.rglob('*') if path.is_file()),
                         sorted(['저장정보.json', '공구대.json', '부서메모.json', 'wash_log_data.json',
                                 os.path.join('백업', '부서메모', '기록', 'x.json')]))
        # 제품 코드가 새 폴더에서 그대로 읽는지
        state = self.protrusion.SharedStore(new / '돌출량 표').sync()['state']
        self.assertEqual(state['values']['memo'], '옮기기 전 메모')
        self.assertEqual(state['revision'], 2)
        table = self.special.TableStore(new / '특수 돌출량').sync()['state']
        self.assertEqual((table['notes'], table['revision']), ('옮기기 전 특이사항', 2))
        synced = self.errors.sync_shared(new / '오류기록', {'pc_id': self.pc, 'epoch': 'after-clear',
                                                            'records': [self.record], 'pending': None})
        self.assertEqual(synced['epoch'], 'after-clear')                               # 세대가 이어져 지난 기록이 남음
        self.assertEqual([row['id'] for row in synced['records']], ['r1'])
        import material_sync
        self.assertEqual(material_sync.Discovery(new / '소재 사용량 조사').exchange('read'), self.owner)
        storage = load_source('src/storage_location.py', 'storage_' + uuid.uuid4().hex)
        storage.NEW_ROOT = str(new)
        self.assertTrue(storage.check())                                               # 제품이 완료 표시를 알아봄
        self.assertEqual(Path(storage.folder('wash')), new / '세척일보')
        self.assertIn('옮긴 파일', report)
        self.assertIn(str(self.old / mover.SETASIDE_NAME), report)
        self.assertFalse((new / mover.RECORD_NAME / mover.JOURNAL_NAME).exists())
        self.assertEqual(list(new.rglob('*.옮기는중')) + list(new.rglob('*.쓰는중')), [])

    def test_old_data_is_set_aside_intact_and_personal_files_are_untouched(self):
        self.move()
        aside = self.old / mover.SETASIDE_NAME
        expected = {}
        for name, digest in self.before.items():
            top = name.split(os.sep)[0]
            if top in (mover.HANDOVER_NAME, '세척일보'):
                expected[name] = digest
            elif name not in self.personal:
                expected[os.path.join(mover.LEFTOVER_NAME, name)] = digest
        self.assertEqual(snapshot(aside), expected)                     # 잠금 파일까지 그대로 모아 둠
        self.assertEqual(self.personal_files(), self.personal)
        self.assertEqual(sorted(path.name for path in self.old.iterdir()),
                         sorted(['2026년', 'TwoSeatChat_data', '휴가신청서.xlsx', mover.SETASIDE_NAME,
                                 mover.HANDOVER_NAME, '세척일보']))
        for name in mover.TOMBSTONES:
            self.assertTrue((self.old / name).is_file())
            self.assertIn('옮겼습니다', (self.old / name).read_text(encoding='utf-8'))

    def test_a_program_that_was_not_updated_cannot_quietly_start_over_in_the_old_place(self):
        self.move()
        with self.assertRaises(OSError):
            self.protrusion.SharedStore(self.old / mover.HANDOVER_NAME).sync()
        with self.assertRaises(OSError):
            self.special.TableStore(self.old / mover.HANDOVER_NAME).sync()
        self.assertTrue((self.old / mover.HANDOVER_NAME).is_file())     # 새 폴더·새 표가 생기지 않음

    def test_a_personal_folder_that_only_looks_like_ours_is_left_alone(self):
        (self.old / '백업' / '내 자료').mkdir()
        (self.old / '백업' / '내 자료' / '중요.txt').write_text('mine', encoding='utf-8')
        report = self.move()
        self.assertIn('건드리지 않습니다', report)
        self.assertEqual((self.old / '백업' / '내 자료' / '중요.txt').read_text(encoding='utf-8'), 'mine')
        self.assertTrue((self.old / '백업' / '부서메모' / '기록' / 'x.json').is_file())

    def test_pcs_that_started_the_new_version_are_listed_before_and_after_the_move(self):
        storage = load_source('src/storage_location.py', 'storage_' + uuid.uuid4().hex)
        storage.NEW_ROOT = str(self.new)
        report = mover.run(self.old, self.new, config_folder=None)
        self.assertIn('아직 없음', report)
        self.assertTrue(storage.announce('2026.11.17.2'))
        report = mover.run(self.old, self.new, config_folder=None)
        self.assertIn('[새 버전으로 켜진 적 있는 PC]', report)
        self.assertIn(' · 2026.11.17.2 · ', report)
        self.assertIn('다 있는지 확인', report)
        moved = self.move()
        self.assertIn(' · 2026.11.17.2 · ', moved)
        self.assertFalse((self.new / mover.READY_NAME).exists())           # 옮긴 뒤에는 기록 폴더로
        self.assertTrue((self.new / mover.RECORD_NAME / mover.READY_NAME).is_dir())
        self.assertEqual(mover.READY_NAME, storage.READY_NAME)
        self.assertIn('이미 옮겨져 있습니다', mover.run(self.old, self.new, config_folder=None))

    # ── 하지 않는 경우: 예전 위치는 원래대로 ──
    def test_refuses_while_wash_completion_is_running(self):
        (self.old / mover.HANDOVER_NAME / '세척완료_실행중.json').write_text('{}', encoding='utf-8')
        self.before = snapshot(self.old)
        with self.assertRaises(mover.MoveError) as caught:
            self.move()
        self.assertIn('세척완료가 실행 중', str(caught.exception))
        self.assert_old_untouched()
        self.assertEqual(list(self.new.iterdir()), [])

    def test_refuses_until_this_pc_has_started_a_version_that_knows_the_new_place(self):
        storage = load_source('src/storage_location.py', 'storage_' + uuid.uuid4().hex)
        storage.NEW_ROOT = str(self.new)
        state = self.base / 'pc' / 'JihuniusTools' / 'desktop-v1' / 'abc' / 'state.json'
        state.parent.mkdir(parents=True)
        state.write_text(json.dumps({'current': {'version': '2026.11.17.1'}}), encoding='utf-8')
        with self.assertRaises(mover.MoveError) as caught:                # 새 버전을 켠 적이 없음
            self.move(require_version=mover.REQUIRED_APP_VERSION)
        self.assertIn('켠 기록이 새 위치에 없습니다', str(caught.exception))
        self.assertIn('2026.11.17.1', str(caught.exception))
        self.assert_old_untouched()
        storage.announce('2026.11.17.1')                                  # 예전 번호로는 부족
        with self.assertRaises(mover.MoveError):
            self.move(require_version=mover.REQUIRED_APP_VERSION)
        self.assert_old_untouched()
        with patch.object(storage.os, 'getpid', return_value=1), \
                patch('socket.gethostname', return_value='다른-PC'):
            storage.announce(mover.REQUIRED_APP_VERSION)                  # 다른 PC만 준비된 경우
        with self.assertRaises(mover.MoveError):
            self.move(require_version=mover.REQUIRED_APP_VERSION)
        self.assert_old_untouched()
        storage.announce(mover.REQUIRED_APP_VERSION)
        self.move(require_version=mover.REQUIRED_APP_VERSION)
        self.assertTrue(mover.marker_valid(self.new))

    def test_refuses_when_the_new_place_already_holds_something(self):
        (self.new / '인수인계').mkdir()
        (self.new / '인수인계' / '누군가의 파일.json').write_text('{}', encoding='utf-8')
        with self.assertRaises(mover.MoveError) as caught:
            self.move()
        self.assertIn('이미 자료가 있어', str(caught.exception))
        self.assert_old_untouched()
        self.assertTrue((self.new / '인수인계' / '누군가의 파일.json').is_file())

    def test_refuses_twice_and_when_the_marker_cannot_be_read(self):
        self.move()
        with self.assertRaises(mover.MoveError) as caught:
            self.move()
        self.assertIn('이미 옮겨져', str(caught.exception))
        (self.new / mover.MARKER_NAME).write_text('{"version": 1, "moved": tr', encoding='utf-8')
        aside = snapshot(self.old / mover.SETASIDE_NAME)
        with self.assertRaises(mover.MoveError) as caught:
            self.move()
        self.assertIn('확인할 수 없어', str(caught.exception))
        self.assertEqual(snapshot(self.old / mover.SETASIDE_NAME), aside)   # 모아 둔 것을 되돌리지 않음

    def test_files_changed_while_copying_are_copied_again(self):
        target = self.old / mover.HANDOVER_NAME / '돌출량_현황표.json'
        real_copy = mover.copy_file
        state = {'done': False}

        def copy_then_edit(source, destination):
            result = real_copy(source, destination)
            if source == target and not state['done']:
                state['done'] = True
                self.protrusion.SharedStore(self.old / mover.HANDOVER_NAME).sync(
                    [{'key': 'memo', 'base': '옮기기 전 메모', 'value': '복사하는 사이 고친 메모'}])
                (self.old / mover.HANDOVER_NAME / ('{:032x}.json'.format(9))).write_text(
                    json.dumps({'version': 1, 'id': '{:032x}'.format(9), 'revision': 'n', 'deleted': True}), encoding='utf-8')
            return result

        with patch.object(mover, 'copy_file', copy_then_edit):
            self.move()
        state = self.protrusion.SharedStore(self.new / '돌출량 표').sync()['state']
        self.assertEqual(state['values']['memo'], '복사하는 사이 고친 메모')
        self.assertTrue((self.new / '인수인계' / '{:032x}.json'.format(9)).is_file())

    def test_gives_up_when_the_old_place_keeps_changing(self):
        real_copy = mover.copy_file
        counter = {'n': 0}

        def always_edit(source, destination):
            result = real_copy(source, destination)
            if source.name == '공구대.json' and source.parent.name == '세척일보':
                counter['n'] += 1
                source.write_text(json.dumps({'tools': counter['n'], 'pad': 'x' * counter['n']}), encoding='utf-8')
            return result

        with patch.object(mover, 'copy_file', always_edit):
            with self.assertRaises(mover.MoveError) as caught:
                self.move()
        self.assertIn('계속 바뀝니다', str(caught.exception))
        self.assertFalse(mover.marker_valid(self.new))
        self.assertFalse((self.old / mover.SETASIDE_NAME).exists())
        self.assertTrue((self.old / '세척일보' / '저장정보.json').is_file())
        self.move()                                                       # 다시 누르면 남은 복사본을 지우고 처음부터
        self.assertTrue(mover.marker_valid(self.new))
        self.assertIn('지난번에 끝내지 못한 복사본을 지우는 중…', self.logs)

    def test_folder_still_in_use_puts_everything_back(self):
        real_rename = os.rename

        def in_use(source, target):
            if Path(source) == self.old / '세척일보':
                error = PermissionError(13, 'The process cannot access the file', str(source))
                error.winerror = 32
                raise error
            return real_rename(source, target)

        with patch.object(mover.os, 'rename', in_use):
            with self.assertRaises(mover.MoveError) as caught:
                self.move()
        self.assertIn('아직 켜져 있을 수', str(caught.exception))
        self.assert_old_untouched()
        self.assertFalse(mover.marker_valid(self.new))

    def test_failing_to_write_the_marker_puts_everything_back(self):
        real_write = mover.write_json

        def fail_marker(path, value):
            if path.name == mover.MARKER_NAME:
                raise OSError(28, 'No space left on device')
            return real_write(path, value)

        with patch.object(mover, 'write_json', fail_marker):
            with self.assertRaises(mover.MoveError) as caught:
                self.move()
        self.assertIn('원래대로 되돌렸습니다', str(caught.exception))
        self.assert_old_untouched()
        self.assertFalse(mover.marker_valid(self.new))

    def test_a_run_that_died_half_way_is_put_back_before_starting_again(self):
        real_write = mover.write_json

        def die(path, value):
            if path.name == mover.MARKER_NAME:
                raise RuntimeError('전원이 꺼짐')
            return real_write(path, value)

        with patch.object(mover, 'write_json', die):
            with self.assertRaises(RuntimeError):
                self.move()
        self.assertTrue((self.old / mover.SETASIDE_NAME).is_dir())        # 모아 둔 채로 멈춤
        self.assertFalse(mover.marker_valid(self.new))
        self.assertEqual(mover.restore_interrupted(self.old), True)
        self.assert_old_untouched()

    def test_unusable_new_place_is_refused_before_anything_is_copied(self):
        with patch.object(mover, 'range_lock_check', lambda path: '안 됨 · 두 번째 잠금이 막히지 않음'):
            with self.assertRaises(mover.MoveError) as caught:
                self.move()
        self.assertIn('새 위치에 문제가 있어', str(caught.exception))
        self.assert_old_untouched()
        self.assertEqual(list(self.new.iterdir()), [])

    # ── 예전 자료 지우기 ──
    def test_cleanup_removes_only_what_was_set_aside(self):
        self.move()
        new_before = snapshot(self.new)
        report = mover.cleanup(self.old, self.new, log=self.logs.append)
        self.assertFalse((self.old / mover.SETASIDE_NAME).exists())
        self.assertEqual(self.personal_files(), self.personal)
        self.assertEqual(sorted(path.name for path in self.old.iterdir()),
                         sorted(['2026년', 'TwoSeatChat_data', '휴가신청서.xlsx', mover.HANDOVER_NAME, '세척일보']))
        self.assertEqual(snapshot(self.new), new_before)
        self.assertIn('예전 자료를 지웠습니다', report)
        with self.assertRaises(mover.MoveError):
            mover.cleanup(self.old, self.new)                             # 두 번째는 지울 것이 없음

    def test_cleanup_still_works_after_the_program_kept_working_in_the_new_place(self):
        self.move()
        self.protrusion.SharedStore(self.new / '돌출량 표').sync([{'key': 'memo', 'base': '옮기기 전 메모', 'value': '옮긴 뒤 메모'}])
        (self.new / '세척일보' / '백업' / '세척일보' / '2026-11-16' / '070000.json').unlink()   # 프로그램이 오래된 백업을 정리
        mover.cleanup(self.old, self.new)
        self.assertFalse((self.old / mover.SETASIDE_NAME).exists())

    def test_cleanup_refuses_before_the_move_and_when_anything_looks_wrong(self):
        with self.assertRaises(mover.MoveError) as caught:
            mover.cleanup(self.old, self.new)
        self.assertIn('아직 옮기기가 끝나지 않았습니다', str(caught.exception))
        self.assert_old_untouched()
        self.move()
        aside = self.old / mover.SETASIDE_NAME
        (aside / '세척일보' / '공구대.json').write_text('{"changed": true}', encoding='utf-8')
        (aside / mover.HANDOVER_NAME / '모르는 파일.txt').write_text('?', encoding='utf-8')
        kept = snapshot(aside)
        with self.assertRaises(mover.MoveError) as caught:
            mover.cleanup(self.old, self.new)
        self.assertIn('내용이 바뀐 파일', str(caught.exception))
        self.assertIn('옮긴 목록에 없는 파일', str(caught.exception))
        self.assertEqual(snapshot(aside), kept)                           # 하나도 지우지 않음

    def test_cleanup_refuses_without_the_list_of_moved_files(self):
        self.move()
        (self.new / mover.RECORD_NAME / mover.MANIFEST_NAME).unlink()
        kept = snapshot(self.old / mover.SETASIDE_NAME)
        with self.assertRaises(mover.MoveError):
            mover.cleanup(self.old, self.new)
        self.assertEqual(snapshot(self.old / mover.SETASIDE_NAME), kept)


if __name__ == '__main__':
    unittest.main()
