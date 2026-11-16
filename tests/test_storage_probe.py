"""저장 위치 점검 프로그램: 예전 위치는 읽기만 하고, 내용은 결과 글에 담지 않으며, 새 위치에는 흔적을 남기지 않습니다."""
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('storage_probe_test', ROOT / 'tools/storage_probe.py')
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
        ast.parse((ROOT / 'tools/storage_probe.py').read_text(encoding='utf-8'), feature_version=(3, 8))


if __name__ == '__main__':
    unittest.main()
