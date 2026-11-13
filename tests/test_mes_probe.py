"""MES 조작 점검 프로그램: 제품 코드를 그대로 싣고, 가짜 MES에서 조작을 해 보고 원래대로 되돌리는지 확인합니다."""
import ast
import sys
import unittest
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_mes_probe
import test_mes_layout as fake

LONG = fake.COLUMNS + (('치과명', 70), ('납기일', 80), ('배송업체', 70), ('진행상태', 80), ('길이', 50))


def probe():
    text = build_mes_probe.build()
    scope = {'__name__': 'mes_probe_under_test'}
    exec(compile(text, 'MES조작점검.pyw', 'exec'), scope)
    return text, scope


def screen(**changes):
    mes = fake.six(widths=[LONG] * 6, menu=200)
    mes.allow_moves = True
    mes.allow_clicks = True
    for name, value in changes.items():
        setattr(mes, name, value)
    return mes


def run(mes, scope, remove='', menu=True, user=None):
    user = user or fake.FakeUser32(mes)
    L = scope['load'](scope['MES_LAYOUT_SOURCE'], 'probe_layout_for_test')
    api = SimpleNamespace(u=user, target={'handle': 1, 'pid': 1, 'title': 'ROOT MES'}, Input=fake.Input)
    pointer = L.Pointer(api, sleep=user.sleep, clock=user.clock)
    reads = []

    def read(label, wide=False):
        reads.append((label, wide))
        return mes.report()

    env = SimpleNamespace(L=L, pointer=pointer, read=read, log=lambda text: None,
                          options={'remove': remove, 'menu': menu}, clock=user.clock)
    lines = scope['experiments'](env)
    return SimpleNamespace(text='\n'.join(lines), reads=reads, user=user, pointer=pointer)


def snapshot(mes):
    return ([list(map(tuple, leaf.columns)) for leaf in mes.all_leaves], [leaf.scroll for leaf in mes.all_leaves],
            mes.menu, [(split.handle, split.position) for split in mes.splits], mes.active)


class BuildTests(unittest.TestCase):
    def test_build_embeds_the_product_code_and_stays_python38(self):
        text, scope = probe()
        ast.parse(text, feature_version=(3, 8))
        self.assertEqual(scope['MES_LAYOUT_SOURCE'], (ROOT / 'src/host/mes_layout.py').read_text(encoding='utf-8'))
        self.assertEqual(scope['WASH_POP_SOURCE'], (ROOT / 'src/host/wash_pop.py').read_text(encoding='utf-8'))
        self.assertEqual(scope['WASH_MES_SOURCE'], (ROOT / 'src/host/wash_mes.py').read_text(encoding='utf-8'))
        self.assertIn('class WashReader', scope['WASH_READER_SOURCE'])
        self.assertEqual(scope['WASH_POP_SOURCE'].count(scope['NARROW_BOUNDS']), 1)     # 넓게 읽기용 바꿔치기 자리
        self.assertTrue(scope['APP_VERSION'].startswith('2026.'))

    def test_probe_never_touches_rows_or_saves(self):
        template = (ROOT / 'tools/mes_probe_template.py').read_text(encoding='utf-8')
        for word in ('query_click', 'save_checked', 'number_click', 'click_handle', 'scroll_grid', 'cycle_steps'):
            self.assertNotIn(word, template, word)


class ExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = probe()[1]

    def test_every_operation_is_tried_reported_and_put_back(self):
        mes = screen()
        before = snapshot(mes)
        outcome = run(mes, self.scope)
        text = outcome.text
        self.assertEqual(mes.bad, [], text)
        self.assertEqual(snapshot(mes), before, text)                         # 전부 원래대로
        self.assertFalse(outcome.user.down)
        self.assertEqual(outcome.user.cursor, (5, 5))
        self.assertEqual(outcome.user.keys, set())
        for expected in ('■ 처음 화면 읽기', '[표]', '시험에 쓰는 칸: "P/No." 과 그 오른쪽 "거래처명"',
                         '-2◆', '+7·', '경계를 오른쪽으로 12 끎 → "P/No." 너비 47 → 59 (+12)',
                         '바로 뒤 칸 "거래처명" 위치 +12 · 다른 칸 너비 변화 없음', '되돌린 뒤 너비 47 (처음 47) → 원래대로',
                         '세로 경계(좌우로 나눔)', '가로 경계(위아래로 나눔)', '14만큼 끎 → 경계가 +14 움직임', '되돌림 → 원래대로',
                         '메뉴 칸 너비 200', '왼쪽 끝까지 끎 → 메뉴 칸 너비 200 → 25 (가장 줄어든 너비)', '되돌림 → 메뉴 칸 너비 200 (원래대로)',
                         '두 칸이 자리를 바꿈', '원래 순서로 돌아옴', '순서 그대로(Esc로 끌기가 취소됨)',
                         '가로 휠 3칸: 표가 가로로 120픽셀 움직임', '반대로 굴림 → 원래 자리',
                         '표가 가로로 90픽셀 움직임', '휠로 원래 자리로 되돌림',
                         '칸 순서: 처음과 같음', '칸 너비: 처음과 같음',
                         '"설비관리"를 누르니 "설비별공구관리"가 보임', '화면이 열림', '문서 탭 "작업지시관리"를 눌러 돌아옴', '처음 표 다시 보임'):
            self.assertIn(expected, text, expected)
        self.assertNotIn('✗', text, text)
        self.assertIn('설비별공구관리', mes.documents)
        for secret in ('비밀환자', '홍길동치과', 'O1009'):
            self.assertNotIn(secret, text)
        self.assertTrue(all(wide for label, wide in outcome.reads if label in ('처음 화면', '메뉴 읽기')))

    def test_optional_column_removal_drops_the_header_into_the_table(self):
        mes = screen()
        outcome = run(mes, self.scope, remove='Fixture', menu=False)
        self.assertEqual(mes.bad, [], outcome.text)
        self.assertEqual(mes.hidden, ['Fixture'])
        self.assertIn('"Fixture" 칸 제목을 아래(표 안쪽)로 140 끌어다 놓음', outcome.text)
        self.assertIn('→ 칸이 없어짐 · 나머지 순서 그대로', outcome.text)
        self.assertIn('칸 순서: 처음과 같음', outcome.text)                      # 없앤 칸을 빼고 비교
        self.assertNotIn('왼쪽 메뉴로 화면 열기', outcome.text)
        self.assertNotIn('설비별공구관리', mes.documents)
        hidden = run(screen(), self.scope, remove='없는칸', menu=False)
        self.assertIn('"없는칸" 칸이 지금 화면에 다 보이지 않아 건너뜀', hidden.text)

    def test_escape_that_does_not_cancel_is_noticed_and_the_order_is_restored(self):
        mes = screen(escape_cancels=False)
        order = [name for name, _ in mes.leaves[0].columns]
        outcome = run(mes, self.scope, menu=False)
        self.assertIn('✗ 순서가 바뀜(Esc로 취소되지 않음)', outcome.text)
        self.assertIn('원래 순서로 되돌림', outcome.text)
        self.assertIn('Esc로 끌기 취소가 확인되지 않아 건너뜀', outcome.text)
        self.assertEqual([name for name, _ in mes.leaves[0].columns], order)
        self.assertEqual(mes.bad, [])

    def test_shift_wheel_is_tried_when_the_side_wheel_does_nothing(self):
        mes = screen(hwheel_works=False)
        outcome = run(mes, self.scope, menu=False)
        self.assertIn('가로 휠 3칸: 표가 움직이지 않음', outcome.text)
        self.assertIn('Shift+세로 휠 3칸: 표가 가로로 120픽셀 움직임', outcome.text)
        self.assertEqual([leaf.scroll for leaf in mes.leaves], [0] * 6)
        self.assertEqual(outcome.user.keys, set())                            # Shift를 눌린 채 두지 않음
        none = run(screen(hwheel_works=False, shift_wheel_works=False), self.scope, menu=False)
        self.assertIn('Shift+세로 휠 3칸: 표가 움직이지 않음', none.text)
        self.assertIn('✗ 표가 가로로 밀린 채입니다', none.text)                     # 자동 스크롤로 밀렸는데 되돌릴 방법이 없음

    def test_frozen_screen_presses_nothing_and_says_so(self):
        mes = screen()
        before = snapshot(mes)
        outcome = run(mes, self.scope, menu=False, user=fake.FakeUser32(mes, frozen=True))
        self.assertIn('✗ 경계에서 크기 조절 모양을 확인하지 못해 누르지 않음', outcome.text)
        self.assertIn('✗ 크기 조절 모양을 확인하지 못해 누르지 않음', outcome.text)
        self.assertEqual((before[2], before[3]), (mes.menu, [(split.handle, split.position) for split in mes.splits]))

    def test_f9_stops_and_releases_everything(self):
        mes = screen()
        user = fake.FakeUser32(mes)
        mes.on_press = lambda model: user.keys.add(0x78) if model.presses == 4 else None
        outcome = run(mes, self.scope, user=user)
        self.assertIn('F9로 중지했습니다', outcome.text)
        self.assertFalse(user.down)
        self.assertIsNone(mes.grab)

    def test_screen_without_a_table_is_explained(self):
        mes = screen()
        mes.active = '설비별공구관리'
        mes.documents.append('설비별공구관리')
        mes.layout()
        outcome = run(mes, self.scope)
        self.assertIn('✗ 시험할 표(칸이 4개 이상 보이는 표)를 찾지 못했습니다', outcome.text)
        self.assertEqual(mes.presses, 0)

    def test_one_failing_experiment_does_not_stop_the_others(self):
        mes = screen()
        outcome = None
        original = mes.report
        calls = {'count': 0}
        def flaky():
            calls['count'] += 1
            if calls['count'] == 2:
                raise RuntimeError('화면을 충분히 읽지 못해')
            return original()
        mes.report = flaky
        outcome = run(mes, self.scope, menu=False)
        self.assertIn('✗ 이 시험은 오류로 중단: RuntimeError: 화면을 충분히 읽지 못해', outcome.text)
        self.assertIn('■ 칸 제목을 끌어 순서 바꾸기', outcome.text)
        self.assertIn('■ 끝난 뒤 확인', outcome.text)
        self.assertFalse(outcome.user.down)


if __name__ == '__main__':
    unittest.main()
