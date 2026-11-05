"""Produce a review-only single .pyw; never change the stable manifest or publish."""
import ast
from pathlib import Path
from embed_companions import embed
ROOT=Path(__file__).resolve().parents[1]
PRIVATE_MAIN='''def main():
    if "--console" in sys.argv:
        return main_console()
    # Review artifact runs this exact source; public updater cannot replace it.
    lease = SuiteUpdater.FileLock(Path(os.environ.get('LOCALAPPDATA') or Path.home()) / 'JihuniusSuite' / 'material-beta.lock')
    if not lease.acquire():
        SuiteUpdater.show_message('소재사용량조사 Beta 검토용 지후니우스가 이미 실행 중입니다. 트레이에서 열어주세요.')
        return
    try:
        SuiteErrors.install('지후니우스', SUITE_APP_VERSION + ' / 소재 Beta 검토용')
        configure_windows_app_identity()
        import tkinter as tk
        window = tk.Tk()
        app = IntegrationApp(window)
        SuiteErrors.attach(app, Path(HANDOVER_SHARED_PARENT) / HANDOVER_FOLDER_NAME / '오류기록')
        window.mainloop()
    finally:
        lease.release()
'''
def build(destination,root=ROOT):
    embed(root)
    source=(root/'apps/jihunius/app.pyw').read_text(encoding='utf8')
    node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='main')
    lines=source.splitlines(keepends=True);lines[node.lineno-1:node.end_lineno]=[PRIVATE_MAIN+'\n']
    data=''.join(lines).encode('utf8');compile(data,str(destination),'exec')
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
    return destination
if __name__=='__main__':
    import sys
    print(build(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'private/지후니우스_소재사용량조사_Beta.pyw'))
