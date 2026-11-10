"""POP 점검(읽기 전용) 프로그램을 한 파일로 만듭니다.

    python tools/build_pop_probe.py [출력 경로]

제품과 똑같은 판독 코드(src/host/wash_pop.py, jihunius_main.py의 WashReader)를 그대로 넣어,
현장 POP에서 '새 방식 판독'이 '예전 방식 판독'과 같은 값을 내는지 클릭 없이 확인합니다.
"""
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'tools/pop_probe_template.py'


def reader_source():
    text = (ROOT / 'src/host/jihunius_main.py').read_text(encoding='utf-8')
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.ClassDef) and n.name == 'WashReader')
    source = ''.join(text.splitlines(True)[node.lineno - 1:node.end_lineno])
    # 점검의 '전체 칸 읽기'만 더 오래 기다릴 수 있게: 기본값은 제품과 같은 95초.
    wait = 'deadline=start+95'
    if source.count(wait) != 1:
        raise SystemExit('WashReader의 대기 시간 위치가 바뀌었습니다.')
    return source.replace(wait, "deadline=start+getattr(self,'wait_seconds',95)")


def app_version():
    text = (ROOT / 'src/host/jihunius_main.py').read_text(encoding='utf-8')
    return re.search(r"^SUITE_APP_VERSION = '([^']+)'", text, re.M).group(1)


def build():
    template = TEMPLATE.read_text(encoding='utf-8')
    values = {'APP_VERSION': app_version(),
              'WASH_POP_SOURCE': (ROOT / 'src/host/wash_pop.py').read_text(encoding='utf-8'),
              'WASH_READER_SOURCE': reader_source()}
    for name, value in values.items():
        pattern = re.compile(r'^' + name + r' = \.\.\.  # build:[^\n]*$', re.M)
        if len(pattern.findall(template)) != 1:
            raise SystemExit('템플릿에서 {} 자리를 찾지 못했습니다.'.format(name))
        template = pattern.sub(lambda match: '{} = {!r}'.format(name, value), template)
    ast.parse(template, feature_version=(3, 8))
    return template


if __name__ == '__main__':
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build' / 'POP점검.pyw'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build(), encoding='utf-8')
    print('wrote', output, output.stat().st_size, 'bytes')
