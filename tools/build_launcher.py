"""지후니우스.exe 만들기 — 아이콘 하나짜리 실행 파일(사용자 요청 2026-11-25).

    python tools/build_launcher.py                       apps/jihunius/app.pyw 를 넣어 build/지후니우스.exe 로
    python tools/build_launcher.py --app releases/jihunius/2026.11.24.1/app.pyw --output 어딘가/지후니우스.exe

- exe 는 안에 든 .pyw 를 %LOCALAPPDATA%\\Jihunius\\app 에 풀고 탐색기의 '열기'로 실행하는 껍데기입니다
  (src/launcher/launcher.c). 업데이트는 예전처럼 .pyw 가 스스로 받으므로 배포 때마다 exe 를 새로 만들 필요는 없습니다.
- 필요한 것: mingw-w64 (Ubuntu: apt-get install gcc-mingw-w64-x86-64). Windows 에서 만들지 않아도 됩니다.
- 같은 입력이면 같은 바이트가 나옵니다(만든 시각을 넣지 않음).
- 아이콘 assets/app_icon.ico 는 assets/app_icon_*.png 로 한 번 만들어 둔 것입니다:
      convert app_icon_16.png app_icon_24.png app_icon_32.png app_icon_48.png app_icon_64.png app_icon_256.png app_icon.ico
"""
import argparse
import ast
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src/launcher/launcher.c'
ICON = ROOT / 'assets/app_icon.ico'
COMPILER = 'x86_64-w64-mingw32-gcc'
RESOURCES = 'x86_64-w64-mingw32-windres'
PROGRAM_NAME = '지후니우스'
VERSION_LINE = re.compile(rb"^SUITE_APP_VERSION = '([0-9]+(?:\.[0-9]+){0,7})'", re.M)

MANIFEST = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity type="win32" name="Jihunius.Launcher" version="{dotted}" processorArchitecture="amd64"/>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <supportedOS Id="{{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}}"/>
      <supportedOS Id="{{1f676c76-80e1-4239-95bb-83d0f6d0da78}}"/>
      <supportedOS Id="{{35138b9a-5d96-4fbd-8e2d-a2440225f93a}}"/>
    </application>
  </compatibility>
</assembly>
'''

RESOURCE_SCRIPT = '''#include <winver.h>
1 ICON "app_icon.ico"
1 RCDATA "app.pyw"
1 24 "launcher.manifest"
1 VERSIONINFO
FILEVERSION {commas}
PRODUCTVERSION {commas}
FILEOS VOS_NT_WINDOWS32
FILETYPE VFT_APP
BEGIN
  BLOCK "StringFileInfo"
  BEGIN
    BLOCK "041204B0"
    BEGIN
      VALUE "FileDescription", "{name}"
      VALUE "ProductName", "{name}"
      VALUE "InternalName", "Jihunius"
      VALUE "OriginalFilename", "{name}.exe"
      VALUE "FileVersion", "{dotted}"
      VALUE "ProductVersion", "{dotted}"
    END
  END
  BLOCK "VarFileInfo"
  BEGIN
    VALUE "Translation", 0x0412, 1200
  END
END
'''


class BuildError(Exception):
    pass


def payload_version(data):
    """넣을 .pyw 의 버전. exe 는 줄 맨 앞의 SUITE_APP_VERSION = '...' 를 글자로 찾으므로 그 줄이 하나뿐이어야 합니다."""
    try:
        found = [node for node in ast.parse(data).body
                 if isinstance(node, ast.Assign) and len(node.targets) == 1
                 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'SUITE_APP_VERSION']
    except SyntaxError:
        raise BuildError('넣을 파일이 Python 프로그램이 아닙니다.') from None
    if len(found) != 1:
        raise BuildError('넣을 파일에서 SUITE_APP_VERSION 을 하나만 찾지 못했습니다.')
    version = ast.literal_eval(found[0].value)
    lines = VERSION_LINE.findall(data)
    if lines != [str(version).encode('ascii')]:
        raise BuildError('SUITE_APP_VERSION 줄을 exe 가 읽을 수 있는 꼴로 찾지 못했습니다: {}'.format(lines))
    parts = [int(part) for part in version.split('.')]
    if len(parts) != 4 or any(part > 65535 for part in parts):
        raise BuildError('버전은 2026.11.25.1 처럼 숫자 네 묶음이어야 합니다: {}'.format(version))
    return version


def missing_tools():
    return [name for name in (COMPILER, RESOURCES) if shutil.which(name) is None]


def build(app, output, source=SOURCE, icon=ICON):
    """app(.pyw) 을 넣은 exe 를 output 에 쓰고 (버전, 바이트)를 돌려줍니다."""
    missing = missing_tools()
    if missing:
        raise BuildError('mingw-w64 가 필요합니다(없는 것: {}). Ubuntu: apt-get install gcc-mingw-w64-x86-64'
                         .format(', '.join(missing)))
    data = Path(app).read_bytes()
    version = payload_version(data)
    values = {'name': PROGRAM_NAME, 'dotted': version, 'commas': version.replace('.', ',')}
    with tempfile.TemporaryDirectory(prefix='jihunius-launcher-') as folder:
        work = Path(folder)
        (work / 'app.pyw').write_bytes(data)
        shutil.copyfile(str(icon), str(work / 'app_icon.ico'))
        shutil.copyfile(str(source), str(work / 'launcher.c'))
        (work / 'launcher.manifest').write_text(MANIFEST.format(**values), encoding='utf-8')
        (work / 'launcher.rc').write_text(RESOURCE_SCRIPT.format(**values), encoding='utf-8')
        steps = ([RESOURCES, '--codepage=65001', 'launcher.rc', '-O', 'coff', '-o', 'launcher.res.o'],
                 [COMPILER, '-O2', '-s', '-static', '-municode', '-mwindows', '-Wall', '-Wextra', '-Werror',
                  '-finput-charset=UTF-8', '-Wl,--no-insert-timestamp',
                  '-o', 'launcher.exe', 'launcher.c', 'launcher.res.o', '-lshell32', '-luser32', '-lkernel32'])
        for step in steps:
            done = subprocess.run(step, cwd=str(work), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if done.returncode:
                raise BuildError('{} 실패:\n{}'.format(step[0], done.stdout.decode('utf-8', 'replace')))
        built = (work / 'launcher.exe').read_bytes()
    if data not in built:
        raise BuildError('만든 exe 안에서 넣은 프로그램을 찾지 못했습니다.')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(built)
    return version, built


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--app', type=Path, default=ROOT / 'apps/jihunius/app.pyw', help='안에 넣을 .pyw')
    parser.add_argument('--output', type=Path, default=ROOT / 'build' / (PROGRAM_NAME + '.exe'))
    args = parser.parse_args(argv)
    try:
        version, built = build(args.app, args.output)
    except (BuildError, OSError) as error:
        print(error, file=sys.stderr)
        return 1
    print('wrote {} · {} bytes · 안에 든 버전 {} · sha256 {}'.format(
        args.output, len(built), version, hashlib.sha256(built).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
