"""MES 조작 점검 프로그램: 제품 코드를 그대로 싣고, 가짜 MES(현장 구조를 본뜸)에서 조작을 해 보고 원래대로 되돌리는지 확인합니다."""
import ast
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_mes_probe
import mes_fake as fake


def probe():
    text = build_mes_probe.build()
    scope = {'__name__': 'mes_probe_under_test'}
    exec(compile(text, 'MES조작점검.pyw', 'exec'), scope)
    return text, scope


def screen(**changes):
    """평소 쓰던 상태: 메뉴 칸은 접혀 있고(25), 생산일보관리 탭이 떠 있으며, 메뉴는 설비관리 묶음이 펼쳐져 있음."""
    mes = fake.six(menu=25)
    mes.expanded = '설비관리'
    mes.allow_moves = True
    mes.allow_clicks = True
    for name, value in changes.items():
        setattr(mes, name, value)
    mes.layout()
    return mes


def run(mes, scope, remove='', tool=True, list_only=False, user=None):
    user = user or fake.FakeUser32(mes)
    L = scope['load'](scope['MES_LAYOUT_SOURCE'], 'probe_layout_for_test')
    api = SimpleNamespace(u=user, target={'handle': 1, 'pid': 1, 'title': 'ROOT MES'}, Input=fake.Input)
    pointer = L.Pointer(api, sleep=user.sleep, clock=user.clock)
    reads = []

    def read(label, wide=False, root=None):
        reads.append((label, wide, root))
        return mes.report(root)

    env = SimpleNamespace(L=L, pointer=pointer, read=read, log=lambda text: None,
                          options={'remove': remove, 'tool': tool, 'list_only': list_only}, clock=user.clock)
    lines = scope['experiments'](env)
    return SimpleNamespace(text='\n'.join(lines), reads=reads, user=user, pointer=pointer)


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

    def test_every_press_in_the_probe_goes_through_a_window_check(self):
        # 1판은 뒤에 가려진 표의 좌표를 그대로 눌렀다. 누르기는 held/tap(그 자리 맨 위 창 확인)이나 경계 확인(find_edge)을 거쳐야 한다.
        template = (ROOT / 'tools/mes_probe_template.py').read_text(encoding='utf-8')
        body = template[template.index('def experiments(env):'):template.index('# --- Windows 실행부')]
        self.assertEqual(body.count('pointer.hold('), 1)                      # held() 안의 한 곳
        self.assertEqual(body.count('pointer.click('), 1)                     # tap() 안의 한 곳
        self.assertNotIn('pointer.double_click(', body)


class ExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = probe()[1]

    def test_it_finds_its_own_way_tries_every_operation_and_puts_everything_back(self):
        mes = screen()
        before = mes.snapshot()
        outcome = run(mes, self.scope)
        text = outcome.text
        self.assertEqual(mes.bad, [], text)
        self.assertEqual(mes.snapshot(), before, text)                        # 칸·판·메뉴 칸·탭 모두 처음대로
        self.assertFalse(outcome.user.down)
        self.assertEqual(outcome.user.cursor, (5, 5))
        self.assertEqual(outcome.user.keys, set())
        for expected in ('메뉴 칸 너비 25', '경계를 오른쪽으로 끌어 넓힘 → 너비 200',
                         '묶음 "생산관리"이 접혀 있음 → 이름 줄', '→ 묶음이 펼쳐짐 · "작업지시관리"', '→ 작업지시관리 문서가 앞에 옴 (탭 창201)',
                         '■ 작업지시관리 탭의 표', '탭 "작업지시관리" (', '칸 제목 31개(표 안 ', '▷특이사항3 100',
                         '시험에 쓰는 칸: "품명" 과 그 오른쪽 "지시일"',
                         '-2◆', '+7·', '그 자리 맨 위 창 이 표',
                         '경계를 오른쪽으로 12 끎 → "품명" 너비 130 → 142 (+12)', '되돌린 뒤 너비 130 (처음 130) → 원래대로',
                         '두 칸이 자리를 바꿈', '원래 순서로 돌아옴', '순서 그대로(Esc로 끌기가 취소됨)',
                         '가로 휠 3칸: 표가 가로로 120픽셀 움직임', '반대로 굴림 → 원래 자리',
                         '표가 가로로 90픽셀 움직임', '휠로 원래 자리로 되돌림',
                         '■ 생산일보관리 탭의 표', '판 6개 · 표 너비', '시험에 쓰는 칸: "P/No." 과 그 오른쪽 "거래처명"',
                         '경계를 오른쪽으로 12 끎 → "P/No." 너비 47 → 59 (+12)',
                         '묶음 "설비관리"이 접혀 있음', '→ 설비별공구관리 문서가 앞에 옴', '→ 작업지시관리 문서가 다시 앞에 옴',
                         '메뉴 칸 너비를 처음(25)으로 되돌림 → 25', '판독 시간(초):'):
            self.assertIn(expected, text, expected)
        self.assertNotIn('✗', text, text)
        self.assertEqual(text.count('칸 순서: 처음과 같음'), 2)
        self.assertEqual(text.count('칸 너비: 처음과 같음'), 2)
        self.assertEqual(mes.documents, ['작업지시관리', '설비별공구관리'])    # 설비별공구관리는 열어 둔 채
        for secret in ('비밀환자', '홍길동치과', 'O1009'):
            self.assertNotIn(secret, text)
        roots = {root for label, wide, root in outcome.reads}
        self.assertIn(201, roots)                                             # 문서 아래만 읽기
        self.assertIn(7, roots)                                               # 메뉴 창만 읽기

    def test_document_behind_another_one_is_brought_forward_before_anything_is_pressed(self):
        # 현장 1판 결과: 설비별공구관리가 앞에 있는데 뒤에 가려진 표의 좌표로 시험했다. 이제는 메뉴로 먼저 앞에 띄운다.
        mes = screen()
        mes.documents.append('설비별공구관리')
        mes.active = '설비별공구관리'
        mes.layout()
        tool = [list(item) for item in mes.tool.columns]
        outcome = run(mes, self.scope, tool=False)
        self.assertEqual(mes.bad, [], outcome.text)
        self.assertEqual(mes.active, '작업지시관리')
        self.assertEqual(mes.tool.columns, tool)
        self.assertIn('→ 작업지시관리 문서가 앞에 옴', outcome.text)
        self.assertNotIn('✗', outcome.text, outcome.text)

    def test_optional_column_removal_drops_the_header_into_the_table(self):
        mes = screen()
        outcome = run(mes, self.scope, remove='T31수정', tool=False)
        self.assertEqual(mes.bad, [], outcome.text)
        self.assertEqual(mes.hidden, ['T31수정'])
        self.assertIn('"T31수정" 칸 제목을 아래(표 안쪽)로 140 끌어다 놓음', outcome.text)
        self.assertIn('→ 칸이 없어짐 · 나머지 순서 그대로', outcome.text)
        self.assertEqual(outcome.text.count('칸 순서: 처음과 같음'), 2)         # 없앤 칸을 빼고 비교
        self.assertNotIn('설비별공구관리 문서가 앞에', outcome.text)
        missing = run(screen(), self.scope, remove='없는칸', tool=False)
        self.assertIn('"없는칸" 칸이 지금 화면에 다 보이지 않아 건너뜀', missing.text)

    def test_list_only_reads_the_tables_without_any_drag_and_without_touching_the_menu(self):
        mes = screen()
        before = mes.snapshot()
        outcome = run(mes, self.scope, list_only=True)
        self.assertEqual(mes.bad, [])
        self.assertEqual(mes.snapshot(), before)
        self.assertEqual(mes.menu, 25)
        self.assertLessEqual(mes.presses, 2)                                  # 탭 두 번(작업지시관리로 갔다가 돌아오기)뿐
        self.assertIn('PART-NO 90 | 품명 130', outcome.text)
        self.assertIn('거래처명120', outcome.text)
        self.assertNotIn('칸 너비 끌기', outcome.text)
        self.assertNotIn('메뉴 칸 넓히기', outcome.text)
        behind = screen()
        behind.documents.append('설비별공구관리')
        behind.active = '설비별공구관리'
        behind.layout()
        outcome = run(behind, self.scope, list_only=True)                     # 문서가 뒤에 있으면 메뉴로 앞에 띄운 뒤 읽음
        self.assertIn('PART-NO 90 | 품명 130', outcome.text)
        self.assertEqual(behind.bad, [])

    def test_escape_that_does_not_cancel_is_noticed_and_the_order_is_restored(self):
        mes = screen(escape_cancels=False)
        order = [name for name, _ in mes.work.columns]
        outcome = run(mes, self.scope, tool=False)
        self.assertIn('✗ 순서가 바뀜(Esc로 취소되지 않음)', outcome.text)
        self.assertIn('원래 순서로 되돌림', outcome.text)
        self.assertIn('Esc로 끌기 취소가 확인되지 않아 건너뜀', outcome.text)
        self.assertEqual([name for name, _ in mes.work.columns], order)
        self.assertEqual(mes.bad, [])

    def test_shift_wheel_is_tried_when_the_side_wheel_does_nothing(self):
        mes = screen(hwheel_works=False)
        outcome = run(mes, self.scope, tool=False)
        self.assertIn('가로 휠 3칸: 표가 움직이지 않음', outcome.text)
        self.assertIn('Shift+세로 휠 3칸: 표가 가로로 120픽셀 움직임', outcome.text)
        self.assertEqual(mes.work.scroll, 0)
        self.assertEqual(outcome.user.keys, set())                            # Shift를 눌린 채 두지 않음
        none = run(screen(hwheel_works=False, shift_wheel_works=False), self.scope, tool=False)
        self.assertIn('Shift+세로 휠 3칸: 표가 움직이지 않음', none.text)
        self.assertIn('✗ 표가 가로로 밀린 채입니다', none.text)                     # 자동 스크롤로 밀렸는데 되돌릴 방법이 없음

    def test_frozen_screen_presses_nothing_on_edges_and_says_so(self):
        mes = screen()
        outcome = run(mes, self.scope, tool=False, user=fake.FakeUser32(mes, frozen=True))
        self.assertIn('메뉴 칸 경계에서 크기 조절 모양을 확인하지 못해 누르지 않았습니다', outcome.text)
        self.assertEqual(mes.presses, 0)                                      # 메뉴 칸을 넓히지 못하면 그 뒤는 하지 않음
        self.assertEqual(mes.menu, 25)

    def test_f9_stops_and_releases_everything(self):
        mes = screen()
        user = fake.FakeUser32(mes)
        mes.on_press = lambda model: user.keys.add(0x78) if model.presses == 6 else None
        outcome = run(mes, self.scope, user=user)
        self.assertIn('F9로 중지했습니다', outcome.text)
        self.assertFalse(user.down)
        self.assertIsNone(mes.grab)

    def test_missing_menu_stops_before_any_press(self):
        mes = screen()
        keep = mes.report
        mes.report = lambda root=None: {**keep(root), 'records': [r for r in keep(root)['records'] if r.get('role') not in (16, 30, 33)]}
        outcome = run(mes, self.scope)
        self.assertIn('✗ 왼쪽 메뉴를 읽지 못했습니다', outcome.text)
        self.assertEqual(mes.presses, 0)

    def test_one_failing_experiment_does_not_stop_the_others(self):
        mes = screen()
        original = mes.report
        calls = {'count': 0}
        def flaky(root=None):
            calls['count'] += 1
            if calls['count'] == 9:
                raise RuntimeError('화면을 충분히 읽지 못해')
            return original(root)
        mes.report = flaky
        outcome = run(mes, self.scope, tool=False)
        self.assertIn('✗ 이 시험은 중단: 화면을 충분히 읽지 못해', outcome.text)
        self.assertIn('■ 생산일보관리 탭의 표', outcome.text)
        self.assertIn('■ 처음 상태로 되돌리기', outcome.text)
        self.assertFalse(outcome.user.down)
        self.assertEqual(mes.menu, 25)


if __name__ == '__main__':
    unittest.main()
