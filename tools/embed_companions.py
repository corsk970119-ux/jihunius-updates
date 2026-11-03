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
    source = (root / ('src/protrusion.py' if key == 'protrusion' else 'src/wash_log.py')).read_text(encoding='utf-8')
    adapter_name = 'ProtrusionUpdateSave' if key == 'protrusion' else 'WashLogUpdateSave'
    adapter = next(ast.get_source_segment(adapters, node) for node in ast.parse(adapters).body
                   if isinstance(node, ast.ClassDef) and node.name == adapter_name)
    nodes = ast.parse(source).body
    entry = next(node for node in nodes if isinstance(node, ast.If) and '__name__' in ast.unparse(node.test))
    lines = source.splitlines(keepends=True)
    lines[entry.lineno - 1:entry.lineno - 1] = ['\n' + helper + '\n' + adapter + '\n\n']
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
    for key in payloads:
        data = companion_source(root, key)
        payloads[key].update(sha256=hashlib.sha256(data).hexdigest(),
                             compressed=base64.b64encode(zlib.compress(data, 9)).decode('ascii'))
    manager = (root / 'src/companion_update.py').read_text(encoding='utf-8') + '\n' + (root / 'src/companions.py').read_text(encoding='utf-8')
    compile(manager, 'companions', 'exec')
    replacements = {
        'SUITE_COMPANIONS': 'SUITE_COMPANIONS = ' + repr(payloads) + '\n',
        'SuiteCompanionManager': 'SuiteCompanionManager = _suite_load_support("jihunius_suite_companions", ' + repr(manager) + ').CompanionManager\n',
    }
    lines = source.splitlines(keepends=True)
    for name in sorted(replacements, key=lambda name: assignments[name].lineno, reverse=True):
        node = assignments[name]
        lines[node.lineno - 1:node.end_lineno] = [replacements[name]]
    result = ''.join(lines)
    compile(result, str(path), 'exec')
    path.write_text(result, encoding='utf-8')


if __name__ == '__main__': embed()
