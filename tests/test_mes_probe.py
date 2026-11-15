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
    """MES를 새로 켜고 작업지시관리 화면을 띄워 둔 상태(2026-11-16 사용자 화면): 작업지시관리 탭, 표는 기본 순서.

    표는 실제처럼 행 번호 칸 51픽셀, 왼쪽 고정 칸 6개(뒤에 2픽셀 선), 칸 제목 줄 위의 그룹화 칸이 있습니다.
    """
    mes = fake.six(menu=25)
    mes.inner = '작업지시관리'
    mes.allow_clicks = True
    mes.movable = {mes.work}
    mes.work.frozen, mes.work.indent, mes.work.band = set(fake.WORK_FROZEN), fake.WORK_INDENT, fake.WORK_BAND
    for name, value in changes.items():
        setattr(mes, name, value)
    mes.layout()
    return mes


def run(mes, scope, remove='', list_only=False, user=None):
    user = user or fake.FakeUser32(mes)
    L = scope['load'](scope['MES_LAYOUT_SOURCE'], 'probe_layout_for_test')
    api = SimpleNamespace(u=user, target={'handle': 1, 'pid': 1, 'title': 'ROOT MES'}, Input=fake.Input)
    pointer = L.Pointer(api, sleep=user.sleep, clock=user.clock)
    reads = []

    def read(label, wide=False, root=None):
        reads.append((label, wide, root))
        return mes.report(root)

    env = SimpleNamespace(L=L, pointer=pointer, read=read, log=lambda text: None,
                          options={'remove': remove, 'list_only': list_only}, clock=user.clock)
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
        self.assertIn('def mes_layout_reader(module):', scope['WASH_READER_SOURCE'])     # MES 정렬과 같은 판독기 설정

    def test_probe_reads_the_screen_exactly_like_the_product(self):
        text, scope = probe()
        made = []

        class Reader:
            def __init__(self, module):
                made.append(module)
        namespace = {'WashReader': Reader}
        exec(compile(scope['WASH_READER_SOURCE'].split('def mes_layout_reader(module):')[1].join(('def mes_layout_reader(module):', '')),
                     'reader.py', 'exec'), namespace)
        P = scope['load'](scope['WASH_POP_SOURCE'], 'probe_wash_pop_for_test')
        namespace['mes_layout_reader'](P)
        source = made[0].POWERSHELL
        self.assertNotEqual(source, P.POWERSHELL)                             # 사본만 바뀌고
        self.assertIn('if(role!=29 || (CellBoundsMode!=1 && !skipCellBounds)) {', source)      # 모든 종류 항목의 위치
        self.assertIn('Convert.ToString(row["name"])=="데이터 패널"', source)                   # 행은 읽지 않음
        self.assertIn("scope['mes_layout_reader'](P)", text)
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

    def test_fresh_table_is_described_one_column_is_thrown_away_and_a_far_move_is_undone(self):
        mes = screen()
        names = [name for name, _ in mes.work.columns]
        widths = dict(mes.work.columns)
        outcome = run(mes, self.scope)
        text = outcome.text
        self.assertEqual(mes.bad, [], text)
        self.assertEqual((mes.grouped, mes.group_hovers), ([], 0), text)       # 그룹화 칸에는 멈추지도 놓지도 않음
        self.assertEqual(mes.hidden, ['거래처코드'], text)                     # 평소 없애는 칸 하나만 버림
        self.assertEqual([name for name, _ in mes.work.columns], [name for name in names if name != '거래처코드'])
        self.assertEqual(dict(mes.work.columns), {name: width for name, width in widths.items() if name != '거래처코드'})
        self.assertEqual((mes.menu, mes.active, mes.inner, mes.work.scroll), (25, '작업지시관리', '작업지시관리', 0))
        self.assertFalse(outcome.user.down)
        self.assertEqual(outcome.user.cursor, (5, 5))
        self.assertEqual(outcome.user.keys, set())
        for expected in ('■ 작업지시관리 탭의 표', '탭 "작업지시관리"은 이미 선택돼 있음', '칸 제목 61개 · 그중 위치 있는 것 22개',
                         '높이 22 (표 위쪽 끝에서 35 아래) · 첫 칸은 표 왼쪽 끝에서 51 오른쪽',
                         '선택@94+35 | PART-NO@129+110', '프로젝트No|T31수정 +2', '겹쳐 읽힌 칸 없음', '가로로 밀린 흔적 없음',
                         '위치 없는 칸(화면 밖) 39개: 아노다이징, 스크류수량, 소재사용수량, 납기일, 배송업체, 출하일, 진행상태, 특이사항1', '완료구분',
                         '기준(남길 칸 52개)에 없는 칸 — 보이는 것: PART-NO, 품명, T31수정, 작업자코드, 좌석번호, 거래처코드 · 화면 밖 것: 아노다이징, 스크류수량, 소재사용수량',
                         '"거래처코드" 칸 제목 (', '표 위 20픽셀: {}(바뀜)'.format(fake.REMOVING), '표 위 80픽셀: ',
                         '→ Esc → 놓음', '→ 칸 순서·개수 그대로',
                         '"거래처코드" · 위로 · 표 위 20픽셀 · 모양 ', '칸이 없어짐 (칸 제목 61 → 60개)', '나머지 칸 순서: 그대로',
                         '의 왼쪽 1/4에 놓음 · ', '바로 앞으로 옮겨짐', '원래 순서로 돌아옴',
                         '칸 순서: 처음과 같음 (버린 칸 "거래처코드" 제외)', '칸 너비: 처음과 같음', '가로로 밀린 흔적: 없음',
                         '판독 시간(초):', '표만 '):
            self.assertIn(expected, text, expected)
        self.assertNotIn('✗', text, text)
        self.assertNotIn('메뉴로 작업지시관리 앞에 띄우기', text)              # 이미 앞에 있으면 메뉴는 건드리지 않음
        for secret in ('비밀환자', '홍길동치과', 'O1009'):
            self.assertNotIn(secret, text)
        roots = {root for label, wide, root in outcome.reads}
        self.assertIn(1220, roots)                                            # 제품처럼 표 창 아래만 읽음
        self.assertNotIn(7, roots)                                            # 메뉴는 읽지도 않음

    def test_far_move_goes_a_long_way_inside_the_loose_columns_and_comes_back(self):
        mes = screen()
        seen = []
        original = mes.release

        def release(x, y):
            grab = mes.grab
            if grab and grab[0] == 'move':
                seen.append((grab[1].columns[grab[2]][0], grab[3], x, y))
            return original(x, y)
        mes.release = release
        run(mes, self.scope)
        moves = [item for item in seen if item[3] >= mes.rects[mes.work.grid][1] + fake.WORK_BAND]   # 칸 제목 줄에 놓은 것
        self.assertEqual(len(moves), 2)
        name, start, end, _ = moves[0]
        self.assertNotIn(name, fake.WORK_FROZEN)
        self.assertGreater(start - end, 500)                                  # 멀리 왼쪽으로
        self.assertEqual(moves[1][0], name)                                   # 같은 칸을 되돌림
        self.assertGreater(moves[1][2] - moves[1][1], 500)

    def test_column_that_does_not_go_away_is_reported_after_every_way_was_tried(self):
        mes = screen(removal_works=False)
        names = [name for name, _ in mes.work.columns]
        outcome = run(mes, self.scope)
        self.assertEqual([way for _, way in mes.drops], ['위', '아래'])       # 위(끝까지) → 아래
        self.assertIn('"거래처코드" · 위로 · 표 위 80픽셀', outcome.text)
        self.assertIn('"거래처코드" · 아래로 · 칸 제목 아래 140픽셀', outcome.text)
        self.assertEqual(outcome.text.count('그대로 있음'), 2)
        self.assertIn('✗ 어느 방법으로도 없어지지 않음', outcome.text)
        self.assertIn('원래 순서로 돌아옴', outcome.text)                     # 다음 시험은 계속
        self.assertEqual([name for name, _ in mes.work.columns], names)
        self.assertEqual((mes.hidden, mes.grouped, mes.bad), ([], [], []))
        down = run(screen(removal_works=False, removal_down_works=True), self.scope)
        self.assertIn('"거래처코드" · 아래로 · 칸 제목 아래 140픽셀', down.text)
        self.assertIn('칸이 없어짐', down.text)

    def test_named_column_is_used_and_a_missing_one_is_skipped(self):
        mes = screen()
        outcome = run(mes, self.scope, remove='T31수정')
        self.assertEqual(mes.hidden, ['T31수정'])
        self.assertIn('"T31수정" · 위로 · 표 위 20픽셀', outcome.text)
        mes = screen()
        missing = run(mes, self.scope, remove='없는칸')
        self.assertIn('"없는칸" 칸이 지금 화면에 다 보이지 않아 건너뜀', missing.text)
        self.assertIn('버려 볼 칸이 없어 건너뜀', missing.text)
        self.assertIn('원래 순서로 돌아옴', missing.text)                     # 먼 칸 옮기기는 그대로 함
        self.assertEqual((mes.hidden, mes.bad), ([], []))

    def test_already_arranged_table_has_nothing_to_throw_away(self):
        mes = screen()
        mes.work.columns = [item for item in mes.work.columns if item[0] not in fake.WORK_EXTRA]
        mes.layout()
        outcome = run(mes, self.scope)
        self.assertIn('기준에 없는 칸(평소 없애는 칸)이 화면에 보이지 않아 건너뜀', outcome.text)
        self.assertEqual((mes.hidden, mes.bad), ([], []))
        self.assertIn('원래 순서로 돌아옴', outcome.text)

    def test_list_only_reads_the_table_without_any_press(self):
        mes = screen()
        before = mes.snapshot()
        outcome = run(mes, self.scope, list_only=True)
        self.assertEqual(mes.presses, 0)
        self.assertEqual(mes.snapshot(), before)
        self.assertIn('선택@94+35 | PART-NO@129+110', outcome.text)
        self.assertNotIn('칸 버리기', outcome.text)

    def test_document_behind_another_one_is_brought_forward_by_the_menu_first(self):
        # 현장 1판: 설비별공구관리가 앞에 있는데 뒤에 가려진 표의 좌표로 시험했다. 이제는 메뉴로 먼저 앞에 띄운다.
        mes = screen(expanded='설비관리')
        mes.documents.append('설비별공구관리')
        mes.active = '설비별공구관리'
        mes.layout()
        tool = [list(item) for item in mes.tool.columns]
        outcome = run(mes, self.scope)
        self.assertEqual(mes.bad, [], outcome.text)
        self.assertEqual(mes.active, '작업지시관리')
        self.assertEqual(mes.tool.columns, tool)
        for expected in ('■ 메뉴로 작업지시관리 앞에 띄우기', '메뉴 칸 너비 25', '경계를 오른쪽으로 끌어 넓힘 → 너비 200',
                         '묶음 "생산관리"이 접혀 있음 → 이름 줄', '→ 작업지시관리 문서가 앞에 옴', '칸이 없어짐',
                         '메뉴 칸 너비를 처음(25)으로 되돌림 → 25'):
            self.assertIn(expected, outcome.text, expected)
        self.assertEqual(mes.menu, 25)
        self.assertNotIn('✗', outcome.text, outcome.text)

    def test_sideways_scrolled_table_gets_no_drag_at_all(self):
        mes = screen()
        mes.work.scroll = 300
        mes.layout()
        outcome = run(mes, self.scope)
        self.assertIn('✗ 표가 가로로 밀려 있는 것으로 읽혀 조작 시험은 하지 않습니다', outcome.text)
        self.assertIn('가로로 밀린 흔적 있음', outcome.text)
        self.assertEqual((mes.presses, mes.hidden), (0, []))

    def test_escape_that_does_not_cancel_still_changes_nothing_while_looking(self):
        mes = screen(escape_cancels=False)                                    # 올려 보기는 제자리로 돌아와서 놓으므로 그대로
        outcome = run(mes, self.scope)
        self.assertIn('→ 칸 순서·개수 그대로', outcome.text)
        self.assertEqual(mes.hidden, ['거래처코드'])
        self.assertEqual((mes.grouped, mes.bad), ([], []))

    def test_f9_stops_and_releases_everything(self):
        mes = screen()
        user = fake.FakeUser32(mes)
        mes.on_press = lambda model: user.keys.add(0x78) if model.presses == 2 else None
        outcome = run(mes, self.scope, user=user)
        self.assertIn('F9로 중지했습니다', outcome.text)
        self.assertFalse(user.down)
        self.assertIsNone(mes.grab)
        self.assertEqual(mes.grouped, [])

    def test_unreadable_menu_matters_only_when_the_work_screen_is_not_in_front(self):
        def without_menu(mes):
            keep = mes.report
            mes.report = lambda root=None: {**keep(root), 'records': [r for r in keep(root)['records'] if r.get('role') not in (16, 30, 33)]}
        mes = screen()
        without_menu(mes)
        outcome = run(mes, self.scope)
        self.assertEqual(mes.hidden, ['거래처코드'])                           # 메뉴 없이도 그대로 진행
        self.assertNotIn('✗', outcome.text, outcome.text)
        mes = screen()
        mes.documents.append('설비별공구관리')
        mes.active = '설비별공구관리'
        mes.layout()
        without_menu(mes)
        outcome = run(mes, self.scope)
        self.assertIn('왼쪽 메뉴를 읽지 못했습니다', outcome.text)
        self.assertEqual(mes.presses, 0)

    def test_one_failing_experiment_does_not_stop_the_others(self):
        mes = screen()
        original = mes.report
        calls = {'count': 0}

        def flaky(root=None):
            calls['count'] += 1
            if calls['count'] == 5:                                           # '올려 본 뒤' 읽기가 실패
                raise RuntimeError('화면을 충분히 읽지 못해')
            return original(root)
        mes.report = flaky
        outcome = run(mes, self.scope)
        self.assertIn('✗ 이 시험은 중단: 화면을 충분히 읽지 못해', outcome.text)
        self.assertIn('■   칸 버리기 (평소 없애는 칸 하나)', outcome.text)
        self.assertIn('■   끝난 뒤 확인', outcome.text)
        self.assertFalse(outcome.user.down)
        self.assertEqual((mes.grouped, mes.bad), ([], []))


if __name__ == '__main__':
    unittest.main()
