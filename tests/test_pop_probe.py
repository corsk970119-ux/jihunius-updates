"""POP 점검(읽기 전용) 프로그램: 제품 판독 코드를 그대로 싣고, 결과에 실제 값을 넣지 않는지 확인합니다."""
import ast, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_pop_probe
from test_wash_large_list import FakePop, TOP


def probe():
    text = build_pop_probe.build()
    scope = {'__name__': 'pop_probe_under_test'}
    exec(compile(text, 'POP점검.pyw', 'exec'), scope)
    return text, scope


def reader_for(pop):
    def read(mode, label, extended):
        return pop.capture({'handle': TOP, 'pid': 1, 'mode': mode}, label, None), 0.5, ''
    return read


class PopProbeTests(unittest.TestCase):
    def test_build_embeds_current_reader_code_and_stays_python38(self):
        text, scope = probe()
        ast.parse(text, feature_version=(3, 8))
        self.assertEqual(scope['WASH_POP_SOURCE'], (ROOT / 'src/host/wash_pop.py').read_text(encoding='utf-8'))
        self.assertIn('class WashReader', scope['WASH_READER_SOURCE'])
        self.assertIn("getattr(self,'wait_seconds',330)", scope['WASH_READER_SOURCE'])
        self.assertIn(scope['NORMAL_LIMIT'], scope['WASH_POP_SOURCE'])

    def test_probe_never_sends_input(self):
        # 점검 코드 자체에는 클릭·키 입력·스크롤·앞으로 가져오기 호출이 없어야 합니다.
        template = (ROOT / 'tools/pop_probe_template.py').read_text(encoding='utf-8')
        for word in ('click', 'SendInput', 'scroll_', 'activate', 'SetForegroundWindow', 'query_click', 'save_checked'):
            self.assertNotIn(word, template, word)

    def test_matching_screen_reports_agreement_without_real_values(self):
        _, scope = probe()
        pop = FakePop(60, page=15)
        lines = scope['analyze'](scope['load_pop'](), reader_for(pop), {'handle': TOP, 'pid': 1})
        text = '\n'.join(lines)
        self.assertIn('행 요약값 사용 가능: 예', text)
        self.assertIn('판독: 성공', text)
        self.assertIn('새 방식 값과 예전 방식 값: 일치', text)
        self.assertIn('점검 중 목록: 그대로', text)
        self.assertIn('목록 60줄 · 화면에 보이는 줄 15', text)
        for secret in ('P0001', 'P0060', '홍길동', '품목1'):
            self.assertNotIn(secret, text)
        self.assertEqual(pop.clicks, [])
        self.assertEqual({mode for mode, _, _ in pop.captures}, {'mes_rows', 'pop_fast', 'pop_full'})

    def test_screen_without_summaries_is_reported_as_unusable(self):
        _, scope = probe()
        lines = scope['analyze'](scope['load_pop'](), reader_for(FakePop(60, page=15, summaries=False)), {'handle': TOP, 'pid': 1})
        text = '\n'.join(lines)
        self.assertIn('행 요약값 사용 가능: 아니오', text)
        self.assertIn('판독: 실패', text)
        self.assertIn('요약값 없음: 60줄', text)

    def test_semicolon_inside_a_value_is_flagged(self):
        _, scope = probe()
        pop = FakePop(60, page=15); pop.rows[50]['비고'] = '가;나'
        text = '\n'.join(scope['analyze'](scope['load_pop'](), reader_for(pop), {'handle': TOP, 'pid': 1}))
        self.assertIn('칸 수 불일치', text)
        self.assertIn('행 요약값 사용 가능: 아니오', text)

    def test_empty_list_is_reported_as_not_checked_rather_than_no(self):
        _, scope = probe()
        text = '\n'.join(scope['analyze'](scope['load_pop'](), reader_for(FakePop(0, page=15)), {'handle': TOP, 'pid': 1}))
        self.assertIn('POP 목록이 0줄입니다', text)
        self.assertIn('행 요약값 사용 가능: 확인 못함', text)
        self.assertIn('새 방식 값과 예전 방식 값: 비교 못함', text)
        self.assertNotIn('사용 가능: 아니오', text)

    def test_list_changing_during_probe_is_reported(self):
        _, scope = probe()
        pop = FakePop(40, page=15)
        base = reader_for(pop)
        def read(mode, label, extended):
            if label == '점검: 변동 확인': pop.rows[3]['선택'] = '선택'
            return base(mode, label, extended)
        text = '\n'.join(scope['analyze'](scope['load_pop'](), read, {'handle': TOP, 'pid': 1}))
        self.assertIn('점검 중 목록: 바뀜', text)


if __name__ == '__main__':
    unittest.main()
