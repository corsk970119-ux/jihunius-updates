"""MES 조작 점검 프로그램을 한 파일로 만듭니다.

    python tools/build_mes_probe.py [출력 경로]

제품과 똑같은 코드(src/host/mes_layout.py의 마우스 조작, 세척완료의 화면 판독기)를 그대로 넣어,
'MES 정렬'이 쓰려는 조작이 현장 MES에서 어떻게 먹히는지 작게 해 보고 되돌리며 확인합니다.
"""
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'tools/mes_probe_template.py'


def reader_source():
    text = (ROOT / 'src/host/jihunius_main.py').read_text(encoding='utf-8')
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.ClassDef) and n.name == 'WashReader')
    return ''.join(text.splitlines(True)[node.lineno - 1:node.end_lineno])


def app_version():
    text = (ROOT / 'src/host/jihunius_main.py').read_text(encoding='utf-8')
    return re.search(r"^SUITE_APP_VERSION = '([^']+)'", text, re.M).group(1)


def build():
    template = TEMPLATE.read_text(encoding='utf-8')
    values = {'APP_VERSION': app_version(),
              'WASH_POP_SOURCE': (ROOT / 'src/host/wash_pop.py').read_text(encoding='utf-8'),
              'WASH_MES_SOURCE': (ROOT / 'src/host/wash_mes.py').read_text(encoding='utf-8'),
              'WASH_READER_SOURCE': reader_source(),
              'MES_LAYOUT_SOURCE': (ROOT / 'src/host/mes_layout.py').read_text(encoding='utf-8')}
    for name, value in values.items():
        pattern = re.compile(r'^' + name + r' = \.\.\.  # build:[^\n]*$', re.M)
        if len(pattern.findall(template)) != 1:
            raise SystemExit('템플릿에서 {} 자리를 찾지 못했습니다.'.format(name))
        template = pattern.sub(lambda match: '{} = {!r}'.format(name, value), template)
    ast.parse(template, feature_version=(3, 8))
    return template


if __name__ == '__main__':
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build' / 'MES조작점검.pyw'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build(), encoding='utf-8')
    print('wrote', output, output.stat().st_size, 'bytes')
