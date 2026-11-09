"""Update the launch file after a managed version has reached its ready marker.

Concatenated after update_engine.py. Shared-folder work runs in a bounded child
process, never in Tk or the automatic GitHub check thread's network timeout.
"""
import ast

ORIGIN_SYNC_SECONDS = 10

def source_version(data):
    try:
        values = {}
        for node in ast.parse(data).body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                if name in ('SUITE_APP_VERSION', 'SUITE_UPDATE_PROTOCOL'):
                    if name in values: raise ValueError('duplicate')
                    values[name] = ast.literal_eval(node.value)
        if values.get('SUITE_UPDATE_PROTOCOL') != 1: raise ValueError('protocol')
        value = values['SUITE_APP_VERSION']; version(value)
        return value
    except (SyntaxError, ValueError, TypeError, KeyError, UpdateError):
        raise UpdateError('실행 파일의 버전을 확인하지 못해 교체를 보류했습니다.') from None

def _origin_bytes(path):
    if path.is_symlink() or not path.is_file():
        raise UpdateError('실행 파일이 이동되었거나 경로가 달라 교체를 보류했습니다.')
    with path.open('rb') as stream: data = stream.read(MAX_PAYLOAD + 1)
    if len(data) > MAX_PAYLOAD: raise UpdateError('실행 파일 크기가 달라 교체를 보류했습니다.')
    return data

def _origin_atomic(path, data, temporary, before_replace=None):
    if temporary.is_symlink() or (temporary.exists() and not temporary.is_file()):
        raise UpdateError('실행 파일의 임시 저장 경로를 확인해 주세요.')
    try:
        with temporary.open('wb') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        if os.name != 'nt' and path.exists(): os.chmod(temporary, path.stat().st_mode & 0o777)
        if temporary.read_bytes() != data: raise UpdateError('실행 파일 복사 검증에 실패했습니다.')
        if before_replace is not None: before_replace()
        os.replace(str(temporary), str(path))
    finally:
        try: temporary.unlink()
        except FileNotFoundError: pass

def replace_origin(origin, candidate, payload, known_hashes):
    candidate = descriptor(candidate); verify(payload, candidate)
    if source_version(payload) != candidate['version']:
        raise UpdateError('실행 파일과 배포 버전이 달라 교체를 보류했습니다.')
    origin = Path(origin)
    if not origin.is_absolute(): raise UpdateError('실행 파일의 전체 경로를 확인해 주세요.')
    if origin.is_symlink() or not origin.is_file():
        raise UpdateError('실행 파일이 이동되어 원본 교체를 보류했습니다.')
    lock = FileLock(origin.with_name('.' + origin.name + '.update.lock'))
    if not lock.acquire():
        return {'kind': 'busy', 'message': '원본 교체 대기: 다른 PC에서 교체 중입니다. 다시 확인을 눌러 주세요.'}
    try:
        old = _origin_bytes(origin); old_version = source_version(old)
        if old == payload:
            return {'kind': 'current', 'message': '실행 경로의 원본 파일도 최신 버전입니다.'}
        if version(old_version) > version(candidate['version']):
            return {'kind': 'newer', 'message': '공유 원본은 더 새 버전입니다. 다시 실행하면 적용됩니다.'}
        if version(old_version) == version(candidate['version']) or hashlib.sha256(old).hexdigest() not in known_hashes:
            raise UpdateError('원본 파일이 다른 내용으로 변경되어 교체를 보류했습니다. 완전 종료 후 다시 실행해 주세요.')
        backup = origin.with_name('.' + origin.name + '.previous')
        if backup.exists() or backup.is_symlink(): source_version(_origin_bytes(backup))
        _origin_atomic(backup, old, backup.with_name(backup.name + '.tmp'))
        def unchanged():
            if _origin_bytes(origin) != old:
                raise UpdateError('교체 중 원본이 변경되어 기존 파일을 보존했습니다.')
        _origin_atomic(origin, payload, origin.with_name('.' + origin.name + '.update.tmp'), unchanged)
        verify(_origin_bytes(origin), candidate)
        return {'kind': 'updated', 'message': '실행 경로의 원본 파일도 최신 버전으로 교체했습니다.'}
    finally:
        lock.release()

def origin_worker(source):
    try:
        request = json.loads(sys.stdin.buffer.read(MAX_MANIFEST + 1))
        context = request['context']; current = descriptor(context['current'])
        root = Path(context['root']); origin = Path(context['origin'])
        if root != root_for(origin): raise UpdateError('원본 교체의 실행 경로를 확인하지 못했습니다.')
        session = read_json(root/'session.json'); ready = read_json(root/'ready.json')
        if (session.get('nonce') != context['nonce'] or ready.get('nonce') != context['nonce']
                or session.get('pid') != request['pid'] or not process_alive(request['pid'])
                or session.get('current', {}).get('sha256') != current['sha256']):
            raise UpdateError('새 버전 시작 확인이 끝나지 않아 원본 교체를 보류했습니다.')
        expected = root/'versions'/current['sha256']/'app.pyw'
        if Path(source).resolve() != expected.resolve(): raise UpdateError('원본 교체용 실행 파일 경로가 다릅니다.')
        state = read_json(root/'state.json')
        if state.get('current', {}).get('sha256') != current['sha256']:
            raise UpdateError('적용된 버전이 달라 원본 교체를 보류했습니다.')
        known = [v.get('sha256') for v in (state.get('base'), state.get('previous'), state.get('current')) if isinstance(v, dict)]
        result = replace_origin(origin, current, _origin_bytes(expected), known)
    except Exception as exc:
        result = {'kind': 'failed', 'message': '원본 교체 보류: ' + (str(exc) if isinstance(exc, UpdateError)
                  else '공유폴더 연결·쓰기 권한을 확인하고 다시 확인을 눌러 주세요. 이 PC의 적용 버전은 유지됩니다.')}
    print(json.dumps(result, ensure_ascii=True), flush=True)

_ORIGIN_BOOTSTRAP = '''import ast,sys
from pathlib import Path
data=Path(sys.argv[1]).read_bytes()
if len(data)>8*1024*1024:raise ValueError('size')
for n in ast.parse(data).body:
 if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='SuiteUpdater':
  source=ast.literal_eval(n.value.args[1]);break
else:raise ValueError('updater missing')
scope={'__name__':'jihunius_origin_worker'}
exec(compile(source,'jihunius_origin_worker','exec'),scope)
scope['origin_worker'](sys.argv[1])
'''

def sync_origin_bounded(context):
    process = None
    try:
        current = descriptor(context['current']); root = Path(context['root'])
        source = root/'versions'/current['sha256']/'app.pyw'
        verify(source.read_bytes(), current)
        executable = Path(sys.executable)
        if os.name == 'nt' and executable.with_name('python.exe').is_file(): executable = executable.with_name('python.exe')
        request = {'context': {key: str(context[key]) if key in ('root', 'origin') else context[key]
                              for key in ('root', 'origin', 'nonce', 'current')}, 'pid': os.getpid()}
        options = {'creationflags': 0x08000000} if os.name == 'nt' else {}
        process = subprocess.Popen([str(executable), '-c', _ORIGIN_BOOTSTRAP, str(source)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(root), **options)
        output, error = process.communicate(json.dumps(request).encode('utf-8'), timeout=ORIGIN_SYNC_SECONDS)
        if process.returncode or len(output) > 16384: raise ValueError('worker failed')
        result = json.loads(output)
        if not isinstance(result, dict) or result.get('kind') not in ('current','updated','newer','busy','failed'):
            raise ValueError('worker response')
        return result
    except subprocess.TimeoutExpired:
        process.kill()
        try: process.communicate(timeout=1)
        except subprocess.TimeoutExpired: pass
        return {'kind': 'failed', 'message': '원본 교체 확인 시간이 초과됐습니다. 이 PC의 적용 버전은 유지됩니다. 다시 확인을 눌러 주세요.'}
    except Exception:
        return {'kind': 'failed', 'message': '원본 교체를 확인하지 못했습니다. 이 PC의 적용 버전은 유지됩니다. 다시 확인을 눌러 주세요.'}
