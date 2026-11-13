"""Build the single-file app (apps/jihunius/app.pyw) from reviewed sources.

The released program stays ONE self-contained .pyw (the updater downloads one file),
but it is now generated. Edit these instead of app.pyw:

  src/host/jihunius_main.py   main window host (lines "NAME = ...  # build:" are filled here)
  src/host/stl_finder.py      STL 찾기 (embedded as STL_FINDER_SOURCE)
  src/host/wash_mes.py        MES 세척완료 판독/조작 (WASH_MES_SOURCE)
  src/host/wash_pop.py        POP 세척완료 저장 (WASH_POP_SOURCE)
  src/host/mes_layout.py      MES 정렬: 판 크기·칸 너비 맞춤 (MES_LAYOUT_SOURCE)
  src/host/card_modifier_10_30.py   카드에 복사하는 수정10.30 스크립트 (CARD_MODIFIER_BYTES)
  src/host/windows_tray.py    시스템 트레이
  src/*.py                    보조창·소재·오류기록·업데이트 (as before)
  assets/*.png, *.wav         아이콘·알림 스위치·알림음

Run:  python tools/build_app.py           (writes apps/jihunius/app.pyw)
      python tools/build_app.py --check   (fails if app.pyw is not the build of the sources)
This command never changes dist/, releases/ or channels/ and never pushes.
"""
import ast
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from embed_companions import companion_lines  # noqa: E402

TEMPLATE = 'src/host/jihunius_main.py'
OUTPUT = 'apps/jihunius/app.pyw'
ICON_SIZES = (256, 64, 48, 32, 24, 16)
COMPANION_TITLES = {'protrusion': '돌출량 현황표', 'wash-log': '세척일보 · 공유 작업장',
                    'special-table': '특수 돌출량', 'material': '소재 사용량 조사(Beta)'}


def _text(root, name):
    return (root / name).read_text(encoding='utf-8')


def _b64(root, name):
    return base64.b64encode((root / name).read_bytes()).decode('ascii')


def _icon_block(root):
    out = ['APP_ICON_PNGS = {\n']
    for size in ICON_SIZES:
        data = _b64(root, 'assets/app_icon_{}.png'.format(size))
        out.append('    {}: (\n'.format(size))
        out.extend('        "{}"\n'.format(data[i:i + 100]) for i in range(0, len(data), 100))
        out.append('    ),\n')
    out.append('}\n')
    return ''.join(out)


def updater_line(root):
    helper = '\n'.join(_text(root, 'src/' + name) for name in ('update_engine.py', 'update_origin.py', 'update_ui.py'))
    return 'SuiteUpdater = _suite_load_support("jihunius_inapp_update", ' + repr(helper) + ')\n'


def host_lines(root):
    stl = _text(root, 'src/host/stl_finder.py')
    if "'''" in stl:
        raise ValueError("stl_finder.py must not contain ''' (embedded as a raw triple-quoted string)")
    switch = {False: _b64(root, 'assets/alert_switch_off.png'), True: _b64(root, 'assets/alert_switch_on.png')}
    return {
        'CARD_MODIFIER_BYTES': 'CARD_MODIFIER_BYTES = ' + repr((root / 'src/host/card_modifier_10_30.py').read_bytes()) + '\n',
        'MACHINE_ALERT_SWITCH_PNGS': 'MACHINE_ALERT_SWITCH_PNGS = ' + repr(switch) + '\n',
        'MACHINE_ALERT_SOUND_WAV': 'MACHINE_ALERT_SOUND_WAV = ' + repr(_b64(root, 'assets/alert_sound.wav')) + '\n',
        'APP_ICON_PNGS': _icon_block(root),
        'STL_FINDER_SOURCE': "STL_FINDER_SOURCE = r'''" + stl + "'''\n",
        'WASH_MES_SOURCE': 'WASH_MES_SOURCE = ' + repr(_text(root, 'src/host/wash_mes.py')) + '\n',
        'WASH_POP_SOURCE': 'WASH_POP_SOURCE = ' + repr(_text(root, 'src/host/wash_pop.py')) + '\n',
        'MES_LAYOUT_SOURCE': 'MES_LAYOUT_SOURCE = ' + repr(_text(root, 'src/host/mes_layout.py')) + '\n',
        'SuiteWindowsTray': "SuiteWindowsTray = _suite_load_support('jihunius_suite_tray', "
                            + repr(_text(root, 'src/host/windows_tray.py')) + ').WindowsTray\n',
        'SuiteUpdater': updater_line(root),
    }


def render(root=ROOT):
    source = _text(root, TEMPLATE)
    replacements = host_lines(root)
    replacements.update(companion_lines(root, COMPANION_TITLES))
    lines = source.splitlines(keepends=True)
    placeholders = {}
    for node in ast.parse(source).body:
        if (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Constant) and node.value.value is Ellipsis):
            placeholders[node.targets[0].id] = node
    missing = set(replacements) ^ set(placeholders)
    if missing:
        raise ValueError('Template placeholders and build items differ: {}'.format(sorted(missing)))
    for name in sorted(placeholders, key=lambda n: placeholders[n].lineno, reverse=True):
        node = placeholders[name]
        lines[node.lineno - 1:node.end_lineno] = [replacements[name]]
    data = ''.join(lines).encode('utf-8')
    compile(data, OUTPUT, 'exec')
    return data


def build(root=ROOT):
    data = render(root)
    (root / OUTPUT).write_bytes(data)
    return data


if __name__ == '__main__':
    built = render(ROOT)
    if '--check' in sys.argv:
        current = (ROOT / OUTPUT).read_bytes()
        if current != built:
            sys.exit('apps/jihunius/app.pyw is not the build of src/ — run python tools/build_app.py')
        print('app.pyw matches sources')
    else:
        (ROOT / OUTPUT).write_bytes(built)
        print('wrote', OUTPUT, len(built), 'bytes')
