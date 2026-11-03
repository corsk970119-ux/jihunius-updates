"""Publish preparation only: rebuild embedded updater, version, notes and stable manifest.

Run: python tools/prepare_release.py 2026.11.03.3 --notes docs/changes.txt
Then test and commit ALL changed files together. This command never pushes to GitHub.
"""
import argparse,ast,hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def prepare(root,version,notes):
    if not re.fullmatch(r'\d{4}\.\d{1,2}\.\d{1,2}\.[1-9]\d{0,5}',version):raise ValueError('Invalid version')
    from datetime import date
    parts=tuple(map(int,version.split('.')));date(*parts[:3])
    source_path=root/'apps/jihunius/app.pyw';source=source_path.read_text(encoding='utf-8')
    lines=source.splitlines(keepends=True);edits=[]
    helper=(root/'src/update_engine.py').read_text(encoding='utf-8')+'\n'+(root/'src/update_ui.py').read_text(encoding='utf-8')
    for node in ast.parse(source).body:
        if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name):
            name=node.targets[0].id
            if name=='SUITE_APP_VERSION':edits.append((node.lineno-1,node.end_lineno,'SUITE_APP_VERSION = '+repr(version)+'\n'))
            elif name=='SuiteUpdater':edits.append((node.lineno-1,node.end_lineno,'SuiteUpdater = _suite_load_support("jihunius_inapp_update", '+repr(helper)+')\n'))
    if len(edits)!=2:raise ValueError('Updater integration not found')
    for start,end,value in sorted(edits,reverse=True):lines[start:end]=[value]
    data=''.join(lines).encode('utf-8');compile(data,str(source_path),'exec')
    item={'version':version,'path':'releases/jihunius/'+version+'/app.pyw','size':len(data),
          'sha256':hashlib.sha256(data).hexdigest(),'min_python':[3,8],'update_protocol':1,'notes':notes[:10000]}
    target=root/item['path'];channel=root/'channels/stable.json'
    previous=json.loads(channel.read_text(encoding='utf-8')) if channel.exists() else {'schema':1,'apps':{}}
    old=previous['apps'].get('jihunius')
    if old and parts<tuple(map(int,old['version'].split('.'))):raise ValueError('Release version cannot go backwards')
    if target.exists() and target.read_bytes()!=data:raise ValueError('Published version is immutable; use a new version')
    for path in (target,source_path,root/'dist/지후니우스.pyw'):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    previous['apps']['jihunius']=item;channel.parent.mkdir(parents=True,exist_ok=True)
    channel.write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return item

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('version');parser.add_argument('--notes',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(prepare(ROOT,args.version,args.notes.read_text(encoding='utf-8')),ensure_ascii=False,indent=2))
