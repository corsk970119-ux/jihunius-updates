"""전체 테스트를 여러 프로세스로 나눠 동시에 돌립니다(테스트 파일 단위).

    python tools/run_tests.py              전체
    python tools/run_tests.py storage mes  파일 이름에 'storage'나 'mes'가 든 것만
    python tools/run_tests.py -j 2         동시에 2개만

- 테스트 파일 하나를 프로세스 하나에서 돌립니다. Linux에서는 프로세스 줄마다 가상 화면(Xvfb)과 임시 HOME을
  따로 줘서 창·설정 파일이 서로 섞이지 않게 합니다(xvfb-run을 앞에 붙일 필요 없음).
- 지난번에 걸린 시간(tests/.durations.json, 저장소에 올리지 않음)을 보고 오래 걸리는 파일부터 시작합니다.
- 하나라도 실패하면 그 파일의 출력을 그대로 보여 주고 종료 코드 1로 끝납니다.
- 한 줄로 차례대로 돌리는 예전 방법도 그대로 됩니다:
      xvfb-run -a -s "-screen 0 3840x1200x24" python -m unittest discover -s tests -p "test_*.py"
"""
import argparse
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / 'tests'
DURATIONS = TESTS / '.durations.json'
SCREEN = '3840x1200x24'
MODULE_TIMEOUT = 600
RAN = re.compile(r'^Ran (\d+) tests? in ([\d.]+)s', re.M)
SKIPPED = re.compile(r'skipped=(\d+)')


def test_modules(filters=()):
    names = sorted(path.stem for path in TESTS.glob('test_*.py'))
    if filters:
        names = [name for name in names if any(word in name for word in filters)]
    return names


def load_durations():
    try:
        value = json.loads(DURATIONS.read_text(encoding='utf-8'))
        return {str(name): float(seconds) for name, seconds in value.items()}
    except (OSError, ValueError, TypeError, AttributeError):
        return {}


def ordered(names, durations):
    """오래 걸리는 파일부터. 처음 보는 파일은 맨 앞(얼마나 걸릴지 모르므로)."""
    return sorted(names, key=lambda name: (-durations.get(name, float('inf')), name))


def parse(output, code):
    """unittest 출력에서 (돌린 수, 건너뛴 수, 통과 여부)."""
    found = RAN.findall(output)
    ran = int(found[-1][0]) if found else 0
    skipped = sum(int(count) for count in SKIPPED.findall(output.rsplit('\n----', 1)[-1]))
    return ran, skipped, code == 0 and bool(found)


class Display:
    """프로세스 줄 하나가 쓰는 가상 화면. Xvfb가 없거나 Windows면 아무것도 하지 않습니다."""

    def __init__(self, number):
        self.number = number
        self.process = None
        self.name = None

    def start(self):
        if os.name == 'nt' or shutil.which('Xvfb') is None:
            return self
        for number in range(self.number, self.number + 400, 8):
            if Path('/tmp/.X11-unix/X{}'.format(number)).exists() or Path('/tmp/.X{}-lock'.format(number)).exists():
                continue
            process = subprocess.Popen(['Xvfb', ':{}'.format(number), '-screen', '0', SCREEN, '-nolisten', 'tcp'],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline and process.poll() is None:
                if Path('/tmp/.X11-unix/X{}'.format(number)).exists():
                    self.process, self.name = process, ':{}'.format(number)
                    return self
                time.sleep(0.05)
            process.kill()
        raise RuntimeError('가상 화면(Xvfb)을 시작하지 못했습니다.')

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(5)
            except subprocess.TimeoutExpired:
                self.process.kill()


def run_module(name, display, home):
    environment = os.environ.copy()
    environment['PYTHONPATH'] = os.pathsep.join(filter(None, [str(TESTS), environment.get('PYTHONPATH')]))
    environment['PYTHONDONTWRITEBYTECODE'] = '1'
    if display.name:
        environment['DISPLAY'] = display.name
        environment.pop('XAUTHORITY', None)
    if os.name != 'nt':
        environment['HOME'] = home
    started = time.monotonic()
    try:
        done = subprocess.run([sys.executable, '-m', 'unittest', name], cwd=str(ROOT), env=environment,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=MODULE_TIMEOUT)
        output, code = done.stdout.decode('utf-8', 'replace'), done.returncode
    except subprocess.TimeoutExpired as error:
        output = (error.stdout or b'').decode('utf-8', 'replace') + '\n{}초 안에 끝나지 않아 멈췄습니다.'.format(MODULE_TIMEOUT)
        code = 1
    ran, skipped, passed = parse(output, code)
    return {'name': name, 'seconds': time.monotonic() - started, 'ran': ran, 'skipped': skipped,
            'passed': passed, 'output': output}


def run(names, jobs, show=print):
    """names를 jobs개 줄로 나눠 돌리고 결과 목록을 돌려줍니다(끝난 순서)."""
    pending = queue.Queue()
    for name in names:
        pending.put(name)
    results = []
    lock = threading.Lock()
    displays = []
    homes = []
    try:
        for index in range(max(1, min(jobs, len(names)))):
            displays.append(Display(91 + index).start())
            homes.append(tempfile.mkdtemp(prefix='jihunius-tests-home-'))

        def line(index):
            while True:
                try:
                    name = pending.get_nowait()
                except queue.Empty:
                    return
                result = run_module(name, displays[index], homes[index])
                with lock:
                    results.append(result)
                    if not result['passed']:
                        show('실패: {} ({:.1f}초)'.format(name, result['seconds']))

        threads = [threading.Thread(target=line, args=(index,), daemon=True) for index in range(len(displays))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    finally:
        for display in displays:
            display.stop()
        for home in homes:
            shutil.rmtree(home, ignore_errors=True)
    return results


def summarize(results, wall):
    total = sum(result['ran'] for result in results)
    skipped = sum(result['skipped'] for result in results)
    failed = [result for result in results if not result['passed']]
    lines = []
    for result in sorted(failed, key=lambda value: value['name']):
        lines += ['', '=' * 70, '실패한 파일: tests/{}.py'.format(result['name']), '=' * 70, result['output'].rstrip()]
    slowest = sorted(results, key=lambda value: -value['seconds'])[:5]
    lines += ['', '오래 걸린 파일: ' + ', '.join('{} {:.0f}초'.format(value['name'], value['seconds']) for value in slowest),
              '-' * 70,
              'Ran {} tests in {:.1f}s ({}개 파일)'.format(total, wall, len(results)), '',
              ('FAILED (파일 {}개: {})'.format(len(failed), ', '.join(sorted(value['name'] for value in failed)))
               if failed else 'OK') + (' (skipped={})'.format(skipped) if skipped else '')]
    return '\n'.join(lines), not failed


def main(argv=None):
    parser = argparse.ArgumentParser(description='지후니우스 테스트를 파일 단위로 나눠 동시에 돌립니다.')
    parser.add_argument('filters', nargs='*', help="이 글자가 이름에 든 테스트 파일만(예: storage)")
    parser.add_argument('-j', '--jobs', type=int, default=os.cpu_count() or 2, help='동시에 돌릴 수(기본: 프로세서 수)')
    options = parser.parse_args(argv)
    names = test_modules(options.filters)
    if not names:
        print('돌릴 테스트 파일이 없습니다.')
        return 1
    durations = load_durations()
    started = time.monotonic()
    results = run(ordered(names, durations), options.jobs)
    text, passed = summarize(results, time.monotonic() - started)
    print(text)
    durations.update({result['name']: round(result['seconds'], 2) for result in results if result['passed']})
    try:
        DURATIONS.write_text(json.dumps(durations, ensure_ascii=False, indent=0, sort_keys=True), encoding='utf-8')
    except OSError:
        pass
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
