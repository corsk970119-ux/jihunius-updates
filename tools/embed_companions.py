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
    lines[entry.lineno - 1:entry.lineno - 1] = ['\n' + helper + '\n' + adapter + diagnostics + '\n\n']
    result = ''.join(lines)
    compile(result, key, 'exec')
    return result.encode('utf-8')


def embed(root=ROOT):
    path = root / 'apps/jihunius/app.pyw'
    source = path.read_text(encoding='utf-8')
    tree = ast.parse(source)
    assignments = {node.targets[0].id: node for node in tree.body
                   if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)}
    payloads = ast.literal_eval(assignments['SUITE_COMPANIONS'].value)
    payloads.setdefault('material',{})['title']='소재 사용량 조사(Beta)'
    for key in payloads:
        data = companion_source(root, key)
        payloads[key].update(sha256=hashlib.sha256(data).hexdigest(),
                             compressed=base64.b64encode(zlib.compress(data, 9)).decode('ascii'))
    manager = (root / 'src/companion_update.py').read_text(encoding='utf-8') + '\n' + (root / 'src/companions.py').read_text(encoding='utf-8')
    compile(manager, 'companions', 'exec')
    replacements = {
        'SuiteWindowState': 'SuiteWindowState = _suite_load_support("jihunius_window_state", ' + repr((root/'src/companion_update.py').read_text(encoding='utf-8') + '\n' + (root/'src/window_state.py').read_text(encoding='utf-8')) + ')\n',
        'SUITE_COMPANIONS': 'SUITE_COMPANIONS = ' + repr(payloads) + '\n',
        'SuiteCompanionManager': 'SuiteCompanionManager = _suite_load_support("jihunius_suite_companions", ' + repr(manager) + ').CompanionManager\n',
        'SuiteMaterialQuick': 'SuiteMaterialQuick = _suite_load_support("jihunius_material_quick", ' + repr((root/'src/material_quick.py').read_text(encoding='utf8')) + ')\n',
    }
    errors=(root/'src/error_history.py').read_text(encoding='utf-8')
    error_ui=(root/'src/error_history_ui.py').read_text(encoding='utf-8')
    combined=errors+'\nSYNC_SOURCE = '+repr(errors)+'\n'+error_ui
    replacements['SuiteErrors']='SuiteErrors = _suite_load_support("jihunius_error_history", '+repr(combined)+')\n'
    lines = source.splitlines(keepends=True)
    for name in sorted(replacements, key=lambda name: assignments[name].lineno, reverse=True):
        node = assignments[name]
        lines[node.lineno - 1:node.end_lineno] = [replacements[name]]
    result = ''.join(lines)
    compile(result, str(path), 'exec')
    path.write_text(result, encoding='utf-8')


if __name__ == '__main__': embed()
