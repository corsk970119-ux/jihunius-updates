"""지후니우스.exe(아이콘 하나짜리 실행 파일, 사용자 요청 2026-11-25).

exe 는 안에 든 .pyw 를 %LOCALAPPDATA%\\Jihunius\\app 에 풀고 탐색기의 '열기'로 실행하는 껍데기입니다
(src/launcher/launcher.c, tools/build_launcher.py).

- 앞쪽 테스트는 어디서나 돕니다(아이콘 파일, 버전 줄, 만드는 도구의 입력 확인).
- exe 를 실제로 만드는 테스트는 mingw-w64 가 있을 때만, 만든 exe 를 돌려 보는 테스트는 wine 까지 있을 때만 돕니다
  (Ubuntu: apt-get install gcc-mingw-w64-x86-64 wine64). 없으면 건너뜁니다.
"""
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_launcher  # noqa: E402

APP = ROOT / 'apps/jihunius/app.pyw'
HAS_MINGW = not build_launcher.missing_tools()
HAS_WINE = bool(shutil.which('wine') and shutil.which('wineserver') and os.environ.get('DISPLAY')
                and sys.platform.startswith('linux'))

# .pyw '열기'에 연결해 두는 가짜 Python: 받은 명령줄과 현재 폴더를 파일에 적고 끝납니다.
FAKE_PYTHON = r'''
#include <windows.h>
int WINAPI wWinMain(HINSTANCE a, HINSTANCE b, PWSTR c, int d) {
    wchar_t log[1024], cwd[1024]; DWORD n; HANDLE f;
    (void)a; (void)b; (void)c; (void)d;
    if (!GetEnvironmentVariableW(L"JIHUNIUS_TEST_LOG", log, 1024)) return 2;
    GetCurrentDirectoryW(1024, cwd);
    f = CreateFileW(log, FILE_APPEND_DATA, FILE_SHARE_READ, NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (f == INVALID_HANDLE_VALUE) return 3;
    WriteFile(f, GetCommandLineW(), lstrlenW(GetCommandLineW()) * 2, &n, NULL);
    WriteFile(f, L"\n", 2, &n, NULL);
    WriteFile(f, cwd, lstrlenW(cwd) * 2, &n, NULL);
    WriteFile(f, L"\n", 2, &n, NULL);
    CloseHandle(f);
    return 0;
}
'''

# 트레이로 내려가 있는 지후니우스처럼: 보이지 않는 TkTopLevel 창 '지후니우스'. 보이게 되면 파일에 적고 끝납니다.
HIDDEN_WINDOW = r'''
#include <windows.h>
static void mark(const wchar_t *name) {
    wchar_t path[1024]; HANDLE f;
    if (!GetEnvironmentVariableW(name, path, 1024)) return;
    f = CreateFileW(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (f != INVALID_HANDLE_VALUE) CloseHandle(f);
}
static LRESULT CALLBACK proc(HWND w, UINT m, WPARAM p, LPARAM l) {
    if (m == WM_TIMER) {
        if (IsWindowVisible(w)) { mark(L"JIHUNIUS_TEST_SHOWN"); PostQuitMessage(0); }
        return 0;
    }
    return DefWindowProcW(w, m, p, l);
}
int WINAPI wWinMain(HINSTANCE inst, HINSTANCE b, PWSTR c, int d) {
    WNDCLASSW k; MSG msg; HWND w;
    (void)b; (void)c; (void)d;
    ZeroMemory(&k, sizeof(k));
    k.lpfnWndProc = proc; k.hInstance = inst; k.lpszClassName = L"TkTopLevel";
    RegisterClassW(&k);
    w = CreateWindowW(L"TkTopLevel", L"\xC9C0\xD6C4\xB2C8\xC6B0\xC2A4", WS_OVERLAPPEDWINDOW,
                      10, 10, 300, 200, NULL, NULL, inst, NULL);
    SetTimer(w, 1, 50, NULL);
    mark(L"JIHUNIUS_TEST_READY");
    while (GetMessageW(&msg, NULL, 0, 0) > 0) { TranslateMessage(&msg); DispatchMessageW(&msg); }
    return 0;
}
'''


def with_version(data, version):
    """같은 프로그램에서 버전 줄만 바꾼 것."""
    current = build_launcher.payload_version(data)
    old = "SUITE_APP_VERSION = '{}'".format(current).encode('ascii')
    assert data.count(old) == 1
    return data.replace(old, "SUITE_APP_VERSION = '{}'".format(version).encode('ascii'))


class LauncherInputTests(unittest.TestCase):
    def test_icon_file_holds_every_size_of_the_app_icon(self):
        data = build_launcher.ICON.read_bytes()
        reserved, kind, count = struct.unpack_from('<HHH', data, 0)
        self.assertEqual((reserved, kind), (0, 1))
        sizes = []
        for index in range(count):
            width, height, _colors, _zero, _planes, bits, length, offset = struct.unpack_from('<BBBBHHII', data, 6 + 16 * index)
            sizes.append((width or 256, height or 256))
            self.assertEqual(bits, 32)                                   # 투명 바탕이 살아 있는 32비트
            self.assertLessEqual(offset + length, len(data))
        self.assertEqual(sizes, [(size, size) for size in (16, 24, 32, 48, 64, 256)])
        for size in (16, 24, 32, 48, 64, 256):
            self.assertTrue((ROOT / 'assets/app_icon_{}.png'.format(size)).is_file())

    def test_program_has_exactly_one_version_line_the_exe_can_read(self):
        # exe 는 줄 맨 앞의 SUITE_APP_VERSION = '...' 를 글자로 찾습니다. 그 줄이 늘거나 꼴이 바뀌면 여기서 잡힙니다.
        data = APP.read_bytes()
        version = build_launcher.payload_version(data)
        self.assertRegex(version, r'^\d{4}\.\d{1,2}\.\d{1,2}\.\d+$')
        self.assertEqual(data.count(b"\nSUITE_APP_VERSION = '"), 1)
        self.assertIn("\nSUITE_APP_VERSION = '{}'\n".format(version).encode('ascii'), data)

    def test_build_refuses_a_program_it_could_not_read_back(self):
        data = APP.read_bytes()
        version = build_launcher.payload_version(data)
        line = "SUITE_APP_VERSION = '{}'".format(version).encode('ascii')
        for broken in (b'not python (', data.replace(line, b'SUITE_APP_VERSION="' + version.encode() + b'"'),
                       data.replace(line, b'RENAMED = 1'), data + b'\n' + line + b'\n',
                       with_version(data, '2026.11.25'), with_version(data, '2026.11.25.70000')):
            with self.assertRaises(build_launcher.BuildError):
                build_launcher.payload_version(broken)

    def test_launcher_source_only_shows_or_starts_the_program(self):
        source = build_launcher.SOURCE.read_text(encoding='utf-8')
        for name in ('URLDownload', 'InternetOpen', 'WinHttp', 'socket', 'CreateRemoteThread', 'WriteProcessMemory',
                     'RegSetValue', 'RegCreateKey', 'DeleteFileW(target', 'system('):
            self.assertNotIn(name, source, name)
        self.assertIn('L"%ls\\\\Jihunius\\\\app"', source)
        self.assertIn('#define PROGRAM_NAME L"지후니우스.pyw"', source)
        self.assertIn('#define WINDOW_CLASS L"TkTopLevel"', source)
        self.assertIn('run.lpVerb = L"open";', source)


@unittest.skipUnless(HAS_MINGW, 'mingw-w64 가 있어야 exe 를 만들 수 있습니다')
class LauncherBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.output = Path(cls.tmp.name) / '지후니우스.exe'
        cls.version, cls.built = build_launcher.build(APP, cls.output)

    def test_exe_is_a_64bit_windows_program_that_carries_the_whole_program(self):
        data = self.output.read_bytes()
        self.assertEqual(data, self.built)
        self.assertEqual(data[:2], b'MZ')
        header = struct.unpack_from('<I', data, 0x3c)[0]
        self.assertEqual(data[header:header + 4], b'PE\0\0')
        machine, = struct.unpack_from('<H', data, header + 4)
        self.assertEqual(machine, 0x8664)                                # x86-64
        subsystem, = struct.unpack_from('<H', data, header + 24 + 68)
        self.assertEqual(subsystem, 2)                                   # 창 프로그램(검은 명령창 없음)
        self.assertEqual(self.version, build_launcher.payload_version(APP.read_bytes()))
        self.assertEqual(data.count(APP.read_bytes()), 1)
        self.assertLess(len(data), len(APP.read_bytes()) + 400 * 1024)   # 껍데기는 작게

    def test_exe_shows_the_app_icon_and_its_name_in_properties(self):
        data = self.built
        icon = build_launcher.ICON.read_bytes()
        count, = struct.unpack_from('<H', icon, 4)
        for index in range(count):
            length, offset = struct.unpack_from('<II', icon, 6 + 16 * index + 8)
            self.assertIn(icon[offset:offset + length], data, index)      # 아이콘 그림 여섯 장이 그대로
        for text in ('지후니우스', '지후니우스.exe', self.version, 'FileDescription', 'ProductName'):
            self.assertIn(text.encode('utf-16-le'), data, text)
        self.assertIn(b'requestedExecutionLevel level="asInvoker"', data)  # 관리자 권한을 묻지 않음

    def test_exe_uses_only_basic_windows_libraries(self):
        dump = shutil.which('x86_64-w64-mingw32-objdump')
        if dump is None:
            self.skipTest('objdump 없음')
        listing = subprocess.run([dump, '-p', str(self.output)], stdout=subprocess.PIPE, check=True).stdout.decode('ascii', 'replace')
        libraries = sorted(line.split(':', 1)[1].strip().lower() for line in listing.splitlines() if 'DLL Name' in line)
        self.assertEqual(libraries, ['kernel32.dll', 'msvcrt.dll', 'shell32.dll', 'user32.dll'])

    def test_same_input_gives_the_same_bytes(self):
        again = Path(self.tmp.name) / 'again.exe'
        self.assertEqual(build_launcher.build(APP, again)[1], self.built)

    def test_command_line_writes_the_file_and_reports_a_missing_program(self):
        target = Path(self.tmp.name) / 'cli' / '지후니우스.exe'
        self.assertEqual(build_launcher.main(['--output', str(target)]), 0)
        self.assertEqual(target.read_bytes(), self.built)
        self.assertEqual(build_launcher.main(['--app', str(Path(self.tmp.name) / 'none.pyw'), '--output', str(target)]), 1)
        self.assertEqual(target.read_bytes(), self.built)                # 실패하면 있던 파일은 그대로


@unittest.skipUnless(HAS_MINGW and HAS_WINE, 'mingw-w64 와 wine 이 있어야 exe 를 돌려 볼 수 있습니다')
class LauncherRunTests(unittest.TestCase):
    """만든 exe 를 wine 에서 실제로 실행합니다. Python 자리는 받은 명령줄을 적는 가짜 프로그램이 대신합니다."""

    @classmethod
    def setUpClass(cls):
        runtime = Path('/run/user') / str(os.getuid())                   # Ubuntu 의 wine 은 이 폴더가 없으면 죽습니다
        try:
            runtime.mkdir(mode=0o700, parents=True, exist_ok=True)
        except OSError:
            raise unittest.SkipTest('{} 를 만들 수 없어 wine 을 쓸 수 없습니다'.format(runtime))
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.work = Path(cls.tmp.name)
        cls.environment = dict(os.environ, WINEPREFIX=str(cls.work / 'prefix'), WINEARCH='win64', WINEDEBUG='-all',
                               WINEDLLOVERRIDES='mscoree,mshtml=', LC_ALL='C.UTF-8',
                               JIHUNIUS_TEST_LOG=cls.windows(cls.work / 'log.txt'),
                               JIHUNIUS_TEST_READY=cls.windows(cls.work / 'ready'),
                               JIHUNIUS_TEST_SHOWN=cls.windows(cls.work / 'shown'))
        cls.addClassCleanup(lambda: subprocess.run(['wineserver', '-k'], env=cls.environment,
                                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        cls.app = APP.read_bytes()
        cls.version = build_launcher.payload_version(cls.app)
        cls.exe = cls.work / '지후니우스.exe'
        build_launcher.build(APP, cls.exe)
        for name, source in (('fakepython', FAKE_PYTHON), ('hiddenwindow', HIDDEN_WINDOW)):
            (cls.work / (name + '.c')).write_text(source, encoding='utf-8')
            subprocess.run([build_launcher.COMPILER, '-O1', '-s', '-static', '-municode', '-mwindows', '-o', name + '.exe',
                            name + '.c', '-luser32'], cwd=str(cls.work), check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        started = cls.wine(['wineboot', '--init'], timeout=240)
        if started.returncode or not (cls.work / 'prefix' / 'drive_c').is_dir():
            raise unittest.SkipTest('이 환경에서는 wine 이 시작되지 않습니다')
        cls.wine(['wine', 'reg', 'add', 'HKCR\\.pyw', '/ve', '/d', 'Python.NoConFile', '/f'])
        cls.associate(True)
        local = sorted((cls.work / 'prefix' / 'drive_c' / 'users').glob('*/AppData/Local'))
        local = [path for path in local if path.parts[-3].lower() != 'public']
        if len(local) != 1:
            raise unittest.SkipTest('wine 의 %LOCALAPPDATA% 를 찾지 못했습니다')
        cls.home = local[0] / 'Jihunius' / 'app'
        cls.program = cls.home / '지후니우스.pyw'

    @staticmethod
    def windows(path):
        return 'Z:' + str(path).replace('/', '\\')

    @classmethod
    def wine(cls, command, timeout=60):
        return subprocess.run(command, env=cls.environment, cwd=str(cls.work), timeout=timeout,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @classmethod
    def associate(cls, enabled):
        key = 'HKCR\\Python.NoConFile\\shell\\open\\command'
        if enabled:
            cls.wine(['wine', 'reg', 'add', key, '/ve', '/d',
                      '"{}" "%L" %*'.format(cls.windows(cls.work / 'fakepython.exe')), '/f'])
        else:
            cls.wine(['wine', 'reg', 'delete', 'HKCR\\Python.NoConFile', '/f'])

    def setUp(self):
        shutil.rmtree(str(self.home.parent), ignore_errors=True)
        for name in ('log.txt', 'ready', 'shown'):
            try: (self.work / name).unlink()
            except FileNotFoundError: pass

    def wait_for(self, condition, seconds=20):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if condition():
                return True
            time.sleep(.05)
        return False

    def started(self):
        """가짜 Python 이 적은 (명령줄, 현재 폴더) 목록."""
        log = self.work / 'log.txt'
        if not log.exists():
            return []
        lines = log.read_bytes().decode('utf-16-le').splitlines()
        return list(zip(lines[0::2], lines[1::2]))

    def run_exe(self, *arguments, expect_start=True):
        before = len(self.started())
        done = self.wine(['wine', str(self.exe)] + list(arguments))
        self.assertEqual(done.returncode, 0)
        if expect_start:
            self.assertTrue(self.wait_for(lambda: len(self.started()) == before + 1), '프로그램이 실행되지 않았습니다')
            return self.started()[-1]
        time.sleep(1.0)
        self.assertEqual(len(self.started()), before, '프로그램이 또 실행되었습니다')
        return None

    def test_first_run_unpacks_the_program_and_opens_it_like_a_double_click(self):
        self.assertFalse(self.home.exists())
        command, folder = self.run_exe()
        self.assertEqual(self.program.read_bytes(), self.app)             # 넣은 것과 같은 바이트
        self.assertEqual(sorted(path.name for path in self.home.iterdir()), ['지후니우스.pyw'])   # 임시 파일이 남지 않음
        self.assertEqual(sorted(path.name for path in self.home.parent.iterdir()), ['app'])
        expected = 'C:\\users\\{}\\AppData\\Local\\Jihunius\\app'.format(self.home.parts[-5])
        self.assertEqual(folder, expected)                                # 현재 폴더 = .pyw 가 있는 폴더
        self.assertEqual(command, '"{}" "{}\\지후니우스.pyw" '.format(self.windows(self.work / 'fakepython.exe'), expected))
        self.assertEqual(sorted(path.name for path in self.work.iterdir() if path.suffix == '.exe'),
                         ['fakepython.exe', 'hiddenwindow.exe', '지후니우스.exe'])   # exe 옆에는 아무것도 생기지 않음

    def test_arguments_are_passed_on_unchanged(self):
        command, _folder = self.run_exe('--hidden', '두 번째 인자', 'a"b')
        self.assertTrue(command.endswith('\\지후니우스.pyw" --hidden "두 번째 인자" a\\"b'), command)

    def test_second_run_leaves_the_program_file_alone(self):
        self.run_exe()
        marked = self.app + b'\n# changed by the updater on this PC\n'     # 같은 버전, 다른 바이트(업데이트가 손댄 파일)
        self.program.write_bytes(marked)
        self.run_exe()
        self.assertEqual(self.program.read_bytes(), marked)

    def test_newer_program_on_the_pc_is_kept(self):
        self.home.mkdir(parents=True)
        newer = with_version(self.app, '2099.1.1.1')                      # 업데이트로 더 새 버전이 된 PC
        self.program.write_bytes(newer)
        self.run_exe()
        self.assertEqual(self.program.read_bytes(), newer)
        year, month, day, serial = self.version.split('.')
        same_day = with_version(self.app, '{}.{}.{}.{}'.format(year, month, day, int(serial) + 1))
        self.program.write_bytes(same_day)                                # 같은 날의 다음 번호도 더 새것
        self.run_exe()
        self.assertEqual(self.program.read_bytes(), same_day)

    def test_older_program_on_the_pc_is_replaced_by_the_one_inside_the_exe(self):
        self.home.mkdir(parents=True)
        for old in ('2026.11.24.1', '2026.9.30.99', '2025.12.31.5'):       # 숫자로 비교(글자 순서로는 9월이 11월보다 뒤)
            with self.subTest(old=old):
                self.program.write_bytes(with_version(self.app, old))
                self.run_exe()
                self.assertEqual(self.program.read_bytes(), self.app)

    def test_broken_program_file_is_repaired(self):
        self.home.mkdir(parents=True)
        for broken in (b'', b'garbage', self.app[:5000], self.app.replace(b"\nSUITE_APP_VERSION = '", b"\nSUITE_APP_VERSION = 'x")):
            with self.subTest(size=len(broken)):
                self.program.write_bytes(broken)
                self.run_exe()
                self.assertEqual(self.program.read_bytes(), self.app)

    def test_running_window_is_brought_up_instead_of_starting_twice(self):
        window = subprocess.Popen(['wine', str(self.work / 'hiddenwindow.exe')], env=self.environment, cwd=str(self.work),
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            self.assertTrue(self.wait_for((self.work / 'ready').exists), '시험용 창이 뜨지 않았습니다')
            time.sleep(.3)
            self.assertFalse((self.work / 'shown').exists())              # 아직 숨어 있음(트레이 상태)
            self.run_exe(expect_start=False)                              # 또 실행하지 않고
            self.assertTrue(self.wait_for((self.work / 'shown').exists), '떠 있던 창을 앞으로 가져오지 않았습니다')
            self.assertEqual(self.program.read_bytes(), self.app)         # 프로그램 파일은 준비해 둠
            window.wait(timeout=20)
        finally:
            if window.poll() is None:
                window.kill()
        self.run_exe()                                                    # 창이 없어지면 다시 평소대로 실행

    def test_pc_without_python_gets_a_message_and_nothing_else(self):
        self.associate(False)
        try:
            process = subprocess.Popen(['wine', str(self.exe)], env=self.environment, cwd=str(self.work),
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                with self.assertRaises(subprocess.TimeoutExpired):        # 안내 창을 띄운 채 기다림
                    process.wait(timeout=4)
            finally:
                process.kill(); process.wait(timeout=20)
                self.wine(['wineserver', '-k'])
            self.assertEqual(self.started(), [])
            self.assertEqual(self.program.read_bytes(), self.app)
        finally:
            self.associate(True)


if __name__ == '__main__':
    unittest.main()
