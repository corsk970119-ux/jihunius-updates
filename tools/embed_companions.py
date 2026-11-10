"""Rebuild the embedded companion manager and applications from reviewed sources."""
import ast
import base64
import hashlib
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[1]


def companion_source(root, key):
    helper = (root / 'src/companion_update.py').read_text(encoding='utf-8')
    helper += '\n' + (root / 'src/window_state.py').read_text(encoding='utf-8')
    adapters = (root / 'src/companion_adapters.py').read_text(encoding='utf-8')
    filenames = {'protrusion': 'protrusion.py', 'wash-log': 'wash_log.py', 'special-table': 'special_table.py', 'material': 'material_counter.py'}
    source = (root / 'src' / filenames[key]).read_text(encoding='utf-8')
    adapter = ''
    if key not in ('special-table','material'):
        adapter_name = 'ProtrusionUpdateSave' if key == 'protrusion' else 'WashLogUpdateSave'
        adapter = next(ast.get_source_segment(adapters, node) for node in ast.parse(adapters).body
                       if isinstance(node, ast.ClassDef) and node.name == adapter_name)
    nodes = ast.parse(source).body
    entry = next(node for node in nodes if isinstance(node, ast.If) and '__name__' in ast.unparse(node.test))
    lines = source.splitlines(keepends=True)
    errors=(root/'src/error_history.py').read_text(encoding='utf-8')
    label={'protrusion':'돌출량','wash-log':'세척일보','special-table':'특수 돌출량','material':'소재 사용량 조사(Beta)'}[key]
    diagnostics=("\nimport types as _err_types\nimport sys as _err_sys\n"
        "_err_module = _err_types.ModuleType('jihunius_error_history')\n"
        "_err_sys.modules['jihunius_error_history'] = _err_module\n"
        "exec(compile("+repr(errors)+", '<error_history>', 'exec'), _err_module.__dict__)\n"
        "if __name__ == '__main__':\n"
        "    _err_module.install("+repr(label)+", os.environ.get('JIHUNIUS_APP_VERSION',''))\n")
    if key == 'material':
        adapter = "\nimport sys as _material_sys, types as _material_types\n_material_sys.modules['material_counter'] = _material_sys.modules[__name__]\n"
        for name in ('material_sync','material_client','material_quick','material_ui'):
            module_source=(root/'src'/(name+'.py')).read_text(encoding='utf-8')
            adapter += "_m = _material_types.ModuleType("+repr(name)+")\n_material_sys.modules["+repr(name)+"] = _m\nexec(compile("+repr(module_source)+", "+repr('<'+name+'>')+", 'exec'), _m.__dict__)\n"
        adapter += "def main():\n    return _material_sys.modules['material_ui'].boot()\n"
    visual_support = ''
    if key in ('protrusion', 'special-table'):
        visual=(root/'src/visual_theme.py').read_text(encoding='utf-8')
        visual_support=("\nimport types as _visual_types, sys as _visual_sys\n"
                    "_visual_module = _visual_types.ModuleType('visual_theme')\n"
                    "_visual_sys.modules['visual_theme'] = _visual_module\n"
                    "exec(compile("+repr(visual)+", '<visual_theme>', 'exec'), _visual_module.__dict__)\n")
    if key in ('wash-log', 'material'):
        # 얇은 스크롤바 한 함수만 공용으로 싣습니다(visual_theme 전체를 싣지 않아 용량 그대로).
        visual=(root/'src/visual_theme.py').read_text(encoding='utf-8')
        scroll=next(ast.get_source_segment(visual, node) for node in ast.parse(visual).body
                    if isinstance(node, ast.FunctionDef) and node.name == 'install_thin_scrollbars')
        visual_support=("\nimport types as _scroll_types, sys as _scroll_sys\n"
                    "_scroll_module = _scroll_types.ModuleType('jihunius_scrollbars')\n"
                    "_scroll_sys.modules['jihunius_scrollbars'] = _scroll_module\n"
                    "exec(compile("+repr(scroll)+", '<jihunius_scrollbars>', 'exec'), _scroll_module.__dict__)\n")
    lines[entry.lineno - 1:entry.lineno - 1] = ['\n' + helper + '\n' + adapter + diagnostics + visual_support + '\n\n']
    result = ''.join(lines)
    compile(result, key, 'exec')
    return result.encode('utf-8')


def _inflate(compressed):
    try:
        return zlib.decompress(base64.b64decode(compressed))
    except Exception:
        return None


def _previous_payloads(root):
    path = root / 'apps/jihunius/app.pyw'
    try:
        tree = ast.parse(path.read_text(encoding='utf-8'))
    except (OSError, SyntaxError, ValueError):
        return {}
    for node in tree.body:
        if (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == 'SUITE_COMPANIONS'):
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                return {}
            return value if isinstance(value, dict) else {}
    return {}


def companion_lines(root, titles):
    """Generated assignment lines for the companion manager, apps and shared modules."""
    payloads = {}
    previous = _previous_payloads(root)
    for key, title in titles.items():
        data = companion_source(root, key)
        digest = hashlib.sha256(data).hexdigest()
        old = previous.get(key, {})
        compressed = old.get('compressed') if old.get('sha256') == digest else None
        # zlib output differs between builds of zlib; reuse the committed blob when the
        # source is unchanged so rebuilding on another PC does not create a noisy diff.
        if compressed is None or _inflate(compressed) != data:
            compressed = base64.b64encode(zlib.compress(data, 9)).decode('ascii')
        payloads[key] = {'title': title, 'sha256': digest, 'compressed': compressed}
    manager = (root / 'src/companion_update.py').read_text(encoding='utf-8') + '\n' + (root / 'src/companions.py').read_text(encoding='utf-8')
    compile(manager, 'companions', 'exec')
    replacements = {
        'SuiteWindowState': 'SuiteWindowState = _suite_load_support("jihunius_window_state", ' + repr((root/'src/companion_update.py').read_text(encoding='utf-8') + '\n' + (root/'src/window_state.py').read_text(encoding='utf-8')) + ')\n',
        'SUITE_COMPANIONS': 'SUITE_COMPANIONS = ' + repr(payloads) + '\n',
        'SuiteCompanionManager': 'SuiteCompanionManager = _suite_load_support("jihunius_suite_companions", ' + repr(manager) + ').CompanionManager\n',
        'SuiteMaterialQuick': 'SuiteMaterialQuick = _suite_load_support("jihunius_material_quick", ' + repr((root/'src/material_quick.py').read_text(encoding='utf8')) + ')\n',
    }
    replacements['SuiteVisualTheme']='SuiteVisualTheme = _suite_load_support("jihunius_visual_theme", '+repr((root/'src/visual_theme.py').read_text(encoding='utf-8'))+')\n'
    errors=(root/'src/error_history.py').read_text(encoding='utf-8')
    error_ui=(root/'src/error_history_ui.py').read_text(encoding='utf-8')
    combined=errors+'\nSYNC_SOURCE = '+repr(errors)+'\n'+error_ui
    replacements['SuiteErrors']='SuiteErrors = _suite_load_support("jihunius_error_history", '+repr(combined)+')\n'
    return replacements


def embed(root=ROOT):
    """Kept for existing tools/tests: rebuild apps/jihunius/app.pyw from all sources."""
    from build_app import build
    build(root)


if __name__ == '__main__': embed()
