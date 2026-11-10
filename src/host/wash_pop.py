SEQUENCE = "06"
SEQUENCE_VALUES = tuple(f'{n:02}' for n in range(1,31)) + ('O',)

def pop_sequence(value=None):
    value=SEQUENCE if value is None else value
    return '완료' if value in ('O','o') else value


def normalize_sequence(value):
    value=str(value).strip()
    if value in ('O','o'):return 'O'
    if value.isascii() and value.isdigit() and 1<=int(value)<=30:return f'{int(value):02}'
    return None

"""POP 세척06 체크 검사. 조회 1회 후 목록을 읽고 MES 세척6 매칭 행만 체크합니다.
검사일·작업자·세척순서를 설정하고 대상만 체크합니다. 통합기에서는 검증 후 저장·확인을 수행합니다. Windows / Python 3.8+.
내장 MSAA 판독기는 읽기 전용입니다.
"""
import base64
import ctypes
from ctypes import wintypes
from datetime import datetime
import json
import os
from pathlib import Path
import queue
import subprocess
import tempfile
import threading
import time
import zipfile
import xml.etree.ElementTree as ET

# MSAA의 읽기 API만 사용합니다. 공급자 등록 단계 없이 선택 창에서 정보를 읽으며,
# 각 행을 즉시 기록합니다. 가상화된 행을 표시하거나 스크롤하지 않습니다.
POWERSHELL = r'''
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$writer = New-Object System.IO.StreamWriter($env:MES_DIAG_OUTPUT, $false, (New-Object System.Text.UTF8Encoding($false)))
$writer.AutoFlush = $true
function Emit($record) { $writer.WriteLine(($record | ConvertTo-Json -Depth 8 -Compress)) }
try {
    Add-Type -AssemblyName Accessibility
    $source = @'
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;
using Accessibility;

public sealed class MesReadOnlyAccessibility {
    [ThreadStatic] public static bool GeometryOnly;
    [ThreadStatic] public static bool VisibleRowsOnly;
    // 0: original geometry; 1: MES cell values; 2: POP hidden-row cell values.
    [ThreadStatic] public static int CellBoundsMode; // 3: final verification, omit hidden-cell names only
    [DllImport("oleacc.dll")]
    static extern int AccessibleObjectFromWindow(IntPtr hwnd, uint objectId, ref Guid iid,
        [MarshalAs(UnmanagedType.Interface)] out IAccessible result);
    [DllImport("oleacc.dll")]
    static extern int AccessibleChildren(IAccessible parent, int start, int count,
        [Out, MarshalAs(UnmanagedType.LPArray, SizeParamIndex=2, ArraySubType=UnmanagedType.Struct)] object[] children,
        out int obtained);
    [DllImport("oleacc.dll")] static extern int WindowFromAccessibleObject(IAccessible acc, out IntPtr hwnd);
    delegate bool EnumProc(IntPtr hwnd, IntPtr data);
    [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr parent, EnumProc callback, IntPtr data);
    [DllImport("user32.dll")] static extern bool IsWindow(IntPtr hwnd);
    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll")] static extern IntPtr GetParent(IntPtr hwnd);
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr hwnd, StringBuilder text, int count);

    readonly Stopwatch clock = Stopwatch.StartNew();
    readonly HashSet<long> seen = new HashSet<long>();
    readonly List<object> retained = new List<object>();
    readonly HashSet<long> nativeHandles = new HashSet<long>();
    readonly Action<object> emit;
    int count, windows, propertyErrors, skippedChrome, deferredWindows;
    bool limited;
    MesReadOnlyAccessibility(Action<object> output) { emit=output; }
    bool AtLimit() {
        if (count>=120000 || clock.Elapsed.TotalSeconds>=300) { limited=true; return true; }
        return false;
    }
    static string Trim(object value, int maxLength=800) {
        string s=value==null ? "" : Convert.ToString(value);
        return s.Length>maxLength ? s.Substring(0,maxLength)+" [truncated]" : s;
    }
    object Read(Func<object> getter) {
        try { return getter(); } catch { propertyErrors++; return null; }
    }
    static string RoleName(int role) {
        switch(role) {
            case 9:return "MSAA.Window"; case 10:return "MSAA.Client";
            case 24:return "MSAA.Table"; case 25:return "MSAA.ColumnHeader";
            case 26:return "MSAA.RowHeader"; case 27:return "MSAA.Column";
            case 28:return "MSAA.Row"; case 29:return "MSAA.Cell";
            case 33:return "MSAA.List"; case 34:return "MSAA.ListItem";
            case 41:return "MSAA.StaticText"; case 42:return "MSAA.Text";
            case 43:return "MSAA.PushButton"; case 44:return "MSAA.CheckBox";
            case 45:return "MSAA.RadioButton"; case 46:return "MSAA.ComboBox";
            default:return "MSAA.Role"+role;
        }
    }
    void Walk(IAccessible acc, int child, int parent, int depth, IntPtr hwnd, bool skipCellBounds=false) {
        if(acc==null || AtLimit())return;
        if(depth>32) { limited=true; return; }
        object roleObject=Read(delegate { return acc.get_accRole(child); });
        int role=0;
        try {if(roleObject!=null)role=Convert.ToInt32(roleObject);}catch{}
        // Skip standard title bars, scroll bars and grips; keep application menus.
        if(role==1 || role==3 || role==4) {skippedChrome++;return;}
        // Read native child windows from their own handles, avoiding repeated deep trees.
        if(role==9 && child==0) {
            IntPtr owner;
            if(WindowFromAccessibleObject(acc,out owner)>=0 && owner!=hwnd && nativeHandles.Contains(owner.ToInt64())) {
                deferredWindows++;
                emit(new Dictionary<string,object>{{"kind","native_reference"},{"parent",parent},{"handle",owner.ToInt64()}});
                return;
            }
        }
        if(child==0) {
            IntPtr identity=Marshal.GetIUnknownForObject(acc);
            bool fresh;
            try { fresh=seen.Add(identity.ToInt64()); }
            finally { Marshal.Release(identity); }
            if(!fresh)return;
            retained.Add(acc);
        }
        int id=count++;
        object stateObject=Read(delegate { return acc.get_accState(child); });
        int state=0;
        bool stateKnown=stateObject!=null;
        if(stateKnown) {
            try { state=Convert.ToInt32(stateObject); } catch {stateKnown=false;}
        }
        // Missing state is treated conservatively: do not read potentially secret text.
        bool secret=!stateKnown || (state & 0x20000000)!=0;
        var row=new Dictionary<string,object>();
        row["kind"]="element";row["engine"]="MSAA";row["id"]=id;row["parent"]=parent;row["depth"]=depth;
        row["handle"]=hwnd.ToInt64();row["child_id"]=child;row["role"]=role;row["type"]=RoleName(role);
        row["state"]=state;row["state_known"]=stateKnown;row["password"]=secret;
        row["enabled"]=(state & 1)==0;row["offscreen"]=(state & 0x18000)!=0;
        row["patterns"]=new string[0];row["name"]="";
        if(!secret) {
            row["name"]=(CellBoundsMode==3 && role==29 && skipCellBounds) ? "" : Trim(Read(delegate {return acc.get_accName(child);}));
            // Row summaries contain many cells; keep them intact for fast value verification.
            row["value"]=Trim(Read(delegate {return acc.get_accValue(child);}), role==28 ? 65536 : 800);

            if(role==24 || role==25 || role==28 || (role==29 && CellBoundsMode!=1 && !skipCellBounds) || role==37 || (role>=41 && role<=47)) {

                try {
                    int x,y,w,h;acc.accLocation(out x,out y,out w,out h,child);
                    row["bounds"]=new int[]{x,y,w,h};
                } catch {propertyErrors++;}
            }
            if(role>=41 && role<=47) {


            }
            if(role==44 || role==45)row["toggle_state"]=(state & 0x10)!=0 ? "Checked" : ((state & 0x20)!=0 ? "Mixed" : "Unchecked");
            row["selected"]=(state & 2)!=0;
        }
        int total=0;
        if(!secret && child==0) {
            object value=Read(delegate {return acc.accChildCount;});
            if(value!=null)try {total=Math.Max(0,Convert.ToInt32(value));}catch{}
        }
        row["child_count"]=total;
        emit(row);
        if(GeometryOnly && role==28 && (Convert.ToString(row["name"]).StartsWith("행 ") || Convert.ToString(row["name"]).StartsWith("Row ")))return;
        if(VisibleRowsOnly && role==28 && (Convert.ToString(row["name"]).StartsWith("행 ") || Convert.ToString(row["name"]).StartsWith("Row "))) {
            int[] b=row.ContainsKey("bounds") ? row["bounds"] as int[] : null;
            if((state & 0x18000)!=0 || b==null || b[2]<=0 || b[3]<=0) {
                row["cells_omitted"]=true;
                return;
            }
        }
        // Preserve geometry for every cell in a visible row: column uniqueness
        // checks also need unexpected or unnamed cells. Hidden rows still retain
        // every cell value, state and child count; final mode omits hidden-cell names.
        if((CellBoundsMode==2 || CellBoundsMode==3) && role==28 && (Convert.ToString(row["name"]).StartsWith("행 ") || Convert.ToString(row["name"]).StartsWith("Row "))) {
            int[] b=row.ContainsKey("bounds") ? row["bounds"] as int[] : null;
            skipCellBounds=(state & 0x18000)!=0 || b==null || b[2]<=0 || b[3]<=0;
        }
        if(secret || child!=0 || total==0 || AtLimit())return;
        if(depth>=32) {limited=true;return;}
        for(int start=0;start<total;start+=32) {
            if(AtLimit())return;
            int size=Math.Min(32,total-start);
            object[] children=new object[size];int obtained=0;int hr;
            try {hr=AccessibleChildren(acc,start,size,children,out obtained);}
            catch(Exception error) {emit(new Dictionary<string,object>{{"kind","element_error"},{"id",id},{"error",Trim(error.Message)}});return;}
            if(hr<0) {emit(new Dictionary<string,object>{{"kind","element_error"},{"id",id},{"hresult",hr}});return;}
            if(obtained<=0)return;
            for(int index=0;index<Math.Min(obtained,size);index++) {
                if(AtLimit())return;
                object item=children[index];
                IAccessible objectChild=item as IAccessible;
                if(objectChild!=null) {Walk(objectChild,0,id,depth+1,hwnd,skipCellBounds);continue;}
                if(item is int) {
                    int childId=(int)item;
                    if(childId<=0)continue;
                    IAccessible expanded=Read(delegate {return acc.get_accChild(childId);}) as IAccessible;
                    if(expanded!=null)Walk(expanded,0,id,depth+1,hwnd,skipCellBounds);
                    else Walk(acc,childId,id,depth+1,hwnd,skipCellBounds);
                }
            }
        }
    }
    void Window(IntPtr hwnd, uint expectedPid) {
        uint pid;GetWindowThreadProcessId(hwnd,out pid);
        if(pid!=expectedPid || AtLimit())return;
        windows++;
        StringBuilder klass=new StringBuilder(256);GetClassName(hwnd,klass,klass.Capacity);
        Guid iid=new Guid("618736E0-3C3D-11CF-810C-00AA00389B71");
        IAccessible acc=null;
        int hr=AccessibleObjectFromWindow(hwnd,0xFFFFFFFC,ref iid,out acc);
        emit(new Dictionary<string,object>{{"kind","native_window"},{"handle",hwnd.ToInt64()},
            {"native_parent",GetParent(hwnd).ToInt64()},{"class",klass.ToString()},{"hresult",hr},{"accessible",acc!=null}});
        if(hr>=0 && acc!=null)Walk(acc,0,-1,0,hwnd);
    }
    public static void Dump(long handle, int expectedPid, Action<object> output) {
        var reader=new MesReadOnlyAccessibility(output);
        IntPtr hwnd=new IntPtr(handle);uint pid;
        GetWindowThreadProcessId(hwnd,out pid);
        if(!IsWindow(hwnd) || pid!=(uint)expectedPid)throw new InvalidOperationException("Selected window changed. Refresh the window list.");
        var handles=new List<IntPtr>();handles.Add(hwnd);
        EnumProc callback=delegate(IntPtr child,IntPtr data) {
            if(handles.Count>=512) {reader.limited=true;return false;}
            uint owner;GetWindowThreadProcessId(child,out owner);
            if(owner==pid && IsWindowVisible(child))handles.Add(child);
            return true;
        };
        EnumChildWindows(hwnd,callback,IntPtr.Zero);
        foreach(IntPtr target in handles)reader.nativeHandles.Add(target.ToInt64());
        output(new Dictionary<string,object>{{"kind","start"},{"engine","MSAA"},{"read_only",true},{"pid",pid}});
        foreach(IntPtr target in handles) {
            if(reader.AtLimit())break;
            try {reader.Window(target,pid);}
            catch(Exception error) {output(new Dictionary<string,object>{{"kind","window_error"},{"handle",target.ToInt64()},{"error",Trim(error.Message)}});}
        }
        output(new Dictionary<string,object>{{"kind","finish"},{"engine","MSAA"},{"elements",reader.count},
            {"windows_read",reader.windows},{"windows_found",handles.Count},{"property_errors",reader.propertyErrors},
            {"skipped_chrome",reader.skippedChrome},{"deferred_windows",reader.deferredWindows},
            {"limited",reader.limited},{"seconds",reader.clock.Elapsed.TotalSeconds}});
        GC.KeepAlive(callback);GC.KeepAlive(reader.retained);
    }
}

'@
    Add-Type -TypeDefinition $source -Language CSharp -ReferencedAssemblies @([Accessibility.IAccessible].Assembly.Location, 'System.dll', 'System.Core.dll')
    $output = [Action[object]] { param($record) Emit $record }
    [MesReadOnlyAccessibility]::Dump([long]$env:MES_DIAG_HANDLE, [int]$env:MES_DIAG_PID, $output)
} catch { Emit @{kind='fatal'; error=$_.Exception.ToString()} }
finally { $writer.Dispose() }
'''


def visible_windows(include_untitled=False):
    if os.name != 'nt':
        return []
    user = ctypes.WinDLL('user32', use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user.EnumWindows.restype = wintypes.BOOL
    user.IsWindowVisible.argtypes = [wintypes.HWND]
    user.IsWindowVisible.restype = wintypes.BOOL
    user.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user.GetWindowTextLengthW.restype = ctypes.c_int
    user.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user.GetWindowTextW.restype = ctypes.c_int
    user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user.GetWindowThreadProcessId.restype = wintypes.DWORD
    user.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user.GetClassNameW.restype = ctypes.c_int
    result = []
    @callback_type
    def visit(handle, _):
        if not user.IsWindowVisible(handle):
            return True
        pid = wintypes.DWORD()
        user.GetWindowThreadProcessId(handle, ctypes.byref(pid))
        if pid.value == os.getpid():
            return True
        length = min(user.GetWindowTextLengthW(handle), 4096)
        if not length and not include_untitled:
            return True
        title = ctypes.create_unicode_buffer(length + 1)
        user.GetWindowTextW(handle, title, len(title))
        klass = ctypes.create_unicode_buffer(256)
        user.GetClassNameW(handle, klass, len(klass))
        result.append({'handle':int(handle), 'pid':pid.value, 'title':title.value, 'class':klass.value})
        return True
    if not user.EnumWindows(visit, 0):
        raise ctypes.WinError(ctypes.get_last_error())
    return sorted(result, key=lambda w: w['title'].casefold())


def powershell_errors(raw):
    """PowerShell 진행 안내(CLIXML)를 오류로 잘못 분류하지 않습니다."""
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        text = raw.decode('utf-16', errors='replace')
    else:
        text = raw.decode('utf-8-sig', errors='replace')
    if text.lstrip().startswith('#< CLIXML'):
        try:
            xml = ET.fromstring(text[text.index('<Objs'):])
            errors = [node.text or '' for node in xml.iter()
                      if node.attrib.get('S', '').lower() == 'error']
            return '\n'.join(errors)
        except (ValueError, ET.ParseError):
            pass
    return text.strip()


def probe_command(powershell, directory, env):
    """Keep the embedded reader in a private temporary file, below Windows' command limit."""
    opening = "    $source = @'\n"
    start = POWERSHELL.index(opening)
    end = POWERSHELL.index("\n'@", start)
    source = Path(directory)/'reader.cs'
    source.write_text(POWERSHELL[start+len(opening):end], encoding='utf-8-sig')
    env['MES_DIAG_SOURCE'] = str(source)
    script = (POWERSHELL[:start] +
              '    $source = [System.IO.File]::ReadAllText($env:MES_DIAG_SOURCE)' +
              POWERSHELL[end+3:])
    return [str(powershell), '-NoLogo', '-NoProfile', '-NonInteractive', '-STA',
            '-EncodedCommand', base64.b64encode(script.encode('utf-16le')).decode('ascii')]


def inspect_window(target, label, stop):
    """Runs an isolated read-only probe; cancels only the probe, never the MES app."""
    report = {'tool':'MES_POP_화면확인', 'version':4, 'captured_at':datetime.now().isoformat(timespec='seconds'),
              'label':label, 'target':dict(target), 'read_only':True,
              'scope':'선택 창의 노출된 UI 정보. 스크롤·체크·입력·저장·서버 통신 없음.', 'records':[]}
    windir = Path(os.environ.get('SystemRoot', r'C:\Windows'))
    powershell = windir/'System32'/'WindowsPowerShell'/'v1.0'/'powershell.exe'
    if not powershell.is_file():
        raise RuntimeError('Windows PowerShell을 찾지 못했습니다. Windows PC에서 실행해 주세요.')
    with tempfile.TemporaryDirectory(prefix='mes_pop_read_') as tmp:
        output = Path(tmp)/'readout.jsonl'
        stderr = Path(tmp)/'errors.txt'
        env = os.environ.copy()
        env.update(MES_DIAG_HANDLE=str(int(target['handle'])), MES_DIAG_PID=str(int(target['pid'])), MES_DIAG_OUTPUT=str(output))
        command = probe_command(powershell, tmp, env)
        with stderr.open('wb') as errors:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                       stderr=errors, env=env, creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            deadline = time.monotonic()+330
            try:
                while process.poll() is None:
                    if stop.wait(.1) or time.monotonic() >= deadline:
                        report['interrupted'] = '사용자 중지' if stop.is_set() else '330초 제한 시간'
                        process.kill()
                        break
                process.wait(timeout=5)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=5)
        report['exit_code'] = process.returncode
        if output.exists():
            for line in output.read_text(encoding='utf-8-sig',errors='replace').splitlines():
                try:
                    record = json.loads(line)
                    if isinstance(record,dict): report['records'].append(record)
                except ValueError:
                    report['partial_line'] = True
        error_bytes = stderr.read_bytes()[:6000]
        error_text = powershell_errors(error_bytes)
        if error_text:
            report['powershell_error'] = error_text
    return report


def report_summary(report):
    records = report['records']
    elements = [r for r in records if r.get('kind')=='element']
    grids = [r for r in elements if 'grid_rows' in r or r.get('type') == 'MSAA.Table']
    values = [r for r in elements if any(r.get(k) for k in ('value','text','legacy_value'))]
    fatal = [r.get('error','') for r in records if r.get('kind')=='fatal']
    finished = any(r.get('kind')=='finish' for r in records)
    partial = bool(report.get('interrupted') or report.get('partial_line') or not finished
                   or any(r.get('limited') for r in records))
    lines = [f"[{report['label']}] {report['target']['title']}",
             f"읽은 항목 {len(elements)}개 / 표 정보 {len(grids)}개 / 값·텍스트 {len(values)}개",
             '일부 결과: 중지·제한 시간·읽기 제한이 있어 전체 화면을 확인하지 못했습니다.' if partial else '화면 정보 읽기가 끝났습니다.',
             '이 결과만으로 자동 완료 가능 여부를 확정하지 않습니다.']
    if fatal: lines.extend('읽기 오류: '+s for s in fatal)
    providers = [r for r in records if r.get('kind') == 'provider']
    if any(r.get('engine') == 'MSAA' for r in records):
        lines.append('검사 방식: MSAA 직접 읽기 (버튼 실행·선택 변경 없음)')
        finishes = [r for r in records if r.get('kind') == 'finish']
        if finishes and 'windows_found' in finishes[-1]:
            end = finishes[-1]
            lines.append(f"창 검사 {end.get('windows_read', 0)}/{end['windows_found']}개 / 테두리·스크롤 요소 {end.get('skipped_chrome', 0)}개 생략")
        locations = sum(bool(r.get('bounds') and r['bounds'][2]>0 and r['bounds'][3]>0) for r in elements)
        lines.append(f'위치가 읽힌 항목 {locations}개. 표의 열 순서는 화면 순서와 다를 수 있어 별도 대조합니다.')
    if providers:
        lines.append('컨트롤 읽기 연결: ' + ('등록됨' if providers[-1].get('registered') else '등록 실패 — 결과 파일에서 원인 확인'))
    named_only = elements and not any(r.get('patterns') or r.get('value') or r.get('type') in ('MSAA.Cell','MSAA.Row','MSAA.CheckBox') for r in elements if r.get('type') != 'ControlType.Window')
    if named_only:
        lines.append('현재는 창 이름·표시 글자만 읽혔습니다. 표 데이터와 체크박스 조작 정보는 확인되지 않았습니다.')
    if report.get('powershell_error'): lines.append('PowerShell 오류가 있습니다. 결과 파일에 포함됩니다.')
    if not elements: lines.append('대상 창이 열려 있는지 확인하세요. 접근 권한 또는 화면 구조 때문에 읽지 못했을 수 있습니다.')
    return '\n'.join(lines)


def save_reports(path, reports):
    if not reports: raise ValueError('먼저 창을 검사해 주세요.')
    path = Path(path)
    text = ['POP 세척06 체크 검사의 화면 판독 결과', 'POP 조회·스크롤·체크 중 수집한 화면 정보 — 저장·완료 실행 없음', '',
            '선택한 창의 표시 문자열이 포함됩니다. 비밀번호 필드는 수집하지 않습니다.',
            '스크롤 밖의 가상화된 행은 누락될 수 있습니다. 목록 전체 수집 가능 여부는 별도 확인이 필요합니다.', '']
    for index, report in enumerate(reports,1):
        text.extend([f'--- 검사 {index} ---',report_summary(report),''])
        for record in report['records']:
            if record.get('kind')=='element':
                fields = ['  '*min(record.get('depth',0),18)+str(record.get('type','')),
                          'name='+str(record.get('name','')), 'id='+str(record.get('automation_id','')),
                          'class='+str(record.get('class','')), 'patterns='+', '.join(record.get('patterns',[]))]
                for key in ('value','text','legacy_value','grid_rows','grid_columns','row','column','toggle_state','selected','role','state','child_count','default_action','bounds','description','help','shortcut'):
                    if key in record: fields.append(key+'='+str(record[key]))
                text.append(' | '.join(fields))
        text.append('')
    # Save to a sibling temporary file, then atomically replace the chosen output.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix='mes_report_',suffix='.zip',dir=str(path.parent),delete=False) as f:
            temporary = Path(f.name)
        with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('MES_POP_report.json',json.dumps({'schema':1,'captures':reports},ensure_ascii=False,indent=2).encode('utf-8'))
            archive.writestr('MES_POP_report.txt','\n'.join(text).encode('utf-8-sig'))
        os.replace(temporary,path)
    finally:
        if temporary is not None and temporary.exists(): temporary.unlink()


from collections import defaultdict
import re


def nodes(report):
    return [r for r in report['records'] if r.get('kind') == 'element']


def check_capture(report):
    finishes = [r for r in report['records'] if r.get('kind') == 'finish']
    if (report.get('interrupted') or report.get('powershell_error') or report.get('partial_line')
            or report.get('exit_code') != 0 or not finishes or finishes[-1].get('limited')
            or any(r.get('kind') in ('fatal','window_error','element_error') for r in report['records'])):
        last = finishes[-1] if finishes else {}
        if last.get('limited'):
            try:seconds = float(last.get('seconds') or 0)
            except (TypeError, ValueError):seconds = 0.0
            raise RuntimeError('화면 항목이 많아 읽기 한도에 걸려 순회를 중단했습니다(읽은 항목 {}개 · {:.0f}초). '
                               '결과를 저장해 주세요.'.format(last.get('elements', 0), seconds))
        raise RuntimeError('화면을 충분히 읽지 못해 순회를 중단했습니다. 결과를 저장해 주세요.')



class Stopped(Exception):
    pass

class WindowsClicks:
    def __init__(self, target):
        self.target = target
        self.u = ctypes.WinDLL('user32',use_last_error=True)
        u=self.u
        specs = {
            'IsWindow':([wintypes.HWND],wintypes.BOOL),
            'IsWindowVisible':([wintypes.HWND],wintypes.BOOL),
            'IsWindowEnabled':([wintypes.HWND],wintypes.BOOL),
            'IsIconic':([wintypes.HWND],wintypes.BOOL),
            'GetAncestor':([wintypes.HWND,wintypes.UINT],wintypes.HWND),
            'GetParent':([wintypes.HWND],wintypes.HWND),
            'GetForegroundWindow':([],wintypes.HWND),
            'SetForegroundWindow':([wintypes.HWND],wintypes.BOOL),
            'GetWindowThreadProcessId':([wintypes.HWND,ctypes.POINTER(wintypes.DWORD)],wintypes.DWORD),
            'GetWindowRect':([wintypes.HWND,ctypes.POINTER(wintypes.RECT)],wintypes.BOOL),
            'GetCursorPos':([ctypes.POINTER(wintypes.POINT)],wintypes.BOOL),
            'WindowFromPoint':([wintypes.POINT],wintypes.HWND),
            'GetWindowTextW':([wintypes.HWND,wintypes.LPWSTR,ctypes.c_int],ctypes.c_int),
            'GetClassNameW':([wintypes.HWND,wintypes.LPWSTR,ctypes.c_int],ctypes.c_int),
            'GetAsyncKeyState':([ctypes.c_int],ctypes.c_short),
            'GetSystemMetrics':([ctypes.c_int],ctypes.c_int),
        }
        for name,(args,result) in specs.items():
            fn=getattr(u,name);fn.argtypes=args;fn.restype=result
        class Mouse(ctypes.Structure):
            _fields_=[('dx',ctypes.c_int32),('dy',ctypes.c_int32),('data',ctypes.c_uint32),
                      ('flags',ctypes.c_uint32),('time',ctypes.c_uint32),('extra',ctypes.c_size_t)]
        class Keyboard(ctypes.Structure):
            _fields_=[('vk',ctypes.c_uint16),('scan',ctypes.c_uint16),('flags',ctypes.c_uint32),
                      ('time',ctypes.c_uint32),('extra',ctypes.c_size_t)]
        class Payload(ctypes.Union):
            _fields_=[('mi',Mouse),('ki',Keyboard)]
        class Input(ctypes.Structure):
            _fields_=[('type',ctypes.c_uint32),('payload',Payload)]
        self.Input=Input
        u.SendInput.argtypes=[wintypes.UINT,ctypes.POINTER(Input),ctypes.c_int];u.SendInput.restype=wintypes.UINT

    def text(self, handle, klass=False):
        buf=ctypes.create_unicode_buffer(512)
        (self.u.GetClassNameW if klass else self.u.GetWindowTextW)(handle,buf,len(buf))
        return buf.value

    def verify(self, handle):
        u=self.u;root=self.target['handle'];pid=wintypes.DWORD()
        u.GetWindowThreadProcessId(handle,ctypes.byref(pid))
        if (not u.IsWindow(handle) or pid.value!=self.target['pid'] or u.GetAncestor(handle,2)!=root
                or u.IsIconic(root) or not u.IsWindowVisible(handle) or not u.IsWindowEnabled(handle)
                or not u.IsWindowEnabled(root)):
            raise RuntimeError('POP 창 또는 버튼 상태가 달라졌습니다. 최소화·팝업 상태를 확인해 주세요.')

    def rect(self, handle):
        r=wintypes.RECT()
        if not self.u.GetWindowRect(handle,ctypes.byref(r)) or r.right<=r.left or r.bottom<=r.top:
            raise RuntimeError('버튼 위치를 확인하지 못했습니다.')
        return r

    def register_query(self, report):
        p=wintypes.POINT();self.u.GetCursorPos(ctypes.byref(p))
        handle=int(self.u.WindowFromPoint(p) or 0);self.verify(handle)
        candidates=[r for r in nodes(report) if r.get('handle')==handle and r.get('parent')==-1 and r.get('role')==43]
        if len(candidates)!=1:
            raise RuntimeError('조회 버튼 자체 위에 마우스를 올려 등록해 주세요.')
        name=candidates[0].get('name','')
        if any(word in name for word in ('저장','삭제','완료','닫기','다운','이동')):
            raise RuntimeError('조회 이외의 동작 버튼은 등록할 수 없습니다.')
        r=self.rect(handle)
        return {'handle':handle,'class':self.text(handle,True),'text':self.text(handle),
                'size':[r.right-r.left,r.bottom-r.top], 'purpose':'query',
                'registered_by':'사용자가 조회 버튼을 가리키고 F8로 지정'}

    def activate(self):
        u=self.u;root=self.target['handle']
        u.ShowWindowAsync.argtypes=[wintypes.HWND,ctypes.c_int];u.ShowWindowAsync.restype=wintypes.BOOL
        if u.IsIconic(root):
            u.ShowWindowAsync(root,9)
            for _ in range(20):
                if not u.IsIconic(root):break
                time.sleep(.05)
        self.verify(root)
        u.SetForegroundWindow(root)
        for _ in range(20):
            if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped('F9 중지')
            if u.GetForegroundWindow()==root:return
            time.sleep(.05)
        raise RuntimeError('Windows가 대상 창을 앞으로 가져오지 못했습니다. MES·POP와 지후니우스를 같은 권한으로 실행하고 다시 시작해 주세요.')

    def click_handle(self, handle, static=False, selection=None, allowed_foreground=None):
        self.verify(handle);u=self.u;root=self.target['handle']
        if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped('F9 중지')
        if u.GetForegroundWindow() not in (allowed_foreground or {root}):
            raise RuntimeError('POP 이외의 창이 앞에 있어 중단했습니다.')
        if any(u.GetAsyncKeyState(k)&0x8000 for k in (1,2,16,17,18,91,92)):
            raise RuntimeError('마우스 버튼 또는 보조 키가 눌려 있어 중단했습니다.')
        r=self.rect(handle);x=(r.left+r.right)//2;y=(r.top+r.bottom)//2
        if selection is not None:
            gb,cb=selection
            if any(abs(a-b)>3 for a,b in zip(gb,[r.left,r.top,r.right-r.left,r.bottom-r.top])):
                raise RuntimeError('표 위치가 바뀌어 체크를 중단했습니다.')
            x=round(cb[0]+cb[2]/2);y=round(cb[1]+cb[3]/2)
            if cb[2]<=0 or cb[3]<=0 or not (r.left<=cb[0] and cb[0]+cb[2]<=r.right and r.top<=cb[1] and cb[1]+cb[3]<=r.bottom):
                raise RuntimeError('체크 칸이 표 안에 완전히 보이지 않습니다.')
        hit=u.WindowFromPoint(wintypes.POINT(x,y))
        allowed=hit==handle or (static and hit==u.GetParent(handle))
        if not allowed:
            raise RuntimeError('버튼이 다른 창에 가려져 있어 중단했습니다.')
        left=u.GetSystemMetrics(76);top=u.GetSystemMetrics(77);w=u.GetSystemMetrics(78);h=u.GetSystemMetrics(79)
        if not(left<=x<left+w and top<=y<top+h) or w<=1 or h<=1:
            raise RuntimeError('버튼이 모니터 표시 범위 밖에 있습니다.')
        items=(self.Input*3)()
        for item in items:item.type=0
        items[0].payload.mi.dx=round((x-left)*65535/(w-1))
        items[0].payload.mi.dy=round((y-top)*65535/(h-1))
        items[0].payload.mi.flags=0x8000|0x4000|0x0001
        items[1].payload.mi.flags=0x0002;items[2].payload.mi.flags=0x0004
        if u.SendInput(3,items,ctypes.sizeof(self.Input))!=3:
            # Release only; never retry a potentially completed click.
            release=self.Input();release.payload.mi.flags=0x0004
            u.SendInput(1,ctypes.byref(release),ctypes.sizeof(self.Input))
            raise RuntimeError('Windows가 클릭 입력을 완료하지 못했습니다. 자동 재시도하지 않습니다.')

    def input_inspection_date(self, field, edit, value, stop):
        value=iso_date(value);handle=edit['handle'];u=self.u
        self.verify(field['handle']);self.verify(handle)
        if u.GetParent(handle)!=field['handle'] or not self.text(handle,True).startswith('WindowsForms10.EDIT.'):
            raise RuntimeError('POP 검사일 입력칸이 달라졌습니다.')
        if stop.is_set():raise Stopped('사용자 중지')
        self.click_handle(handle,selection=(bounds(edit),bounds(edit)))
        if stop.wait(.05):raise Stopped('사용자 중지')
        class GUIInfo(ctypes.Structure):
            _fields_=[('size',ctypes.c_uint32),('flags',ctypes.c_uint32)]+[
                (name,wintypes.HWND) for name in ('active','focus','capture','menu','move','caret')]+[('rect',wintypes.RECT)]
        u.GetGUIThreadInfo.argtypes=[wintypes.DWORD,ctypes.POINTER(GUIInfo)];u.GetGUIThreadInfo.restype=wintypes.BOOL
        info=GUIInfo();info.size=ctypes.sizeof(info)
        if (u.GetForegroundWindow()!=self.target['handle'] or not u.GetGUIThreadInfo(0,ctypes.byref(info))
                or info.focus!=handle or info.flags & 0x1e):
            raise RuntimeError('POP 검사일 입력칸에 초점이 없어 입력을 중단했습니다.')
        if stop.is_set() or u.GetAsyncKeyState(0x78)&0x8000:raise Stopped('사용자 중지')
        if any(u.GetAsyncKeyState(k)&0x8000 for k in (1,2,16,17,18,91,92)):
            raise RuntimeError('마우스 버튼 또는 보조 키가 눌려 있어 중단했습니다.')
        # Select all, type the ISO date, then Tab to commit; never press Enter.
        events=[(17,0,0),(65,0,0),(65,0,2),(17,0,2)]
        for char in value:events.extend(((0,ord(char),4),(0,ord(char),6)))
        events.extend(((9,0,0),(9,0,2)))
        items=(self.Input*len(events))()
        for item,(vk,scan,flags) in zip(items,events):
            item.type=1;item.payload.ki.vk=vk;item.payload.ki.scan=scan;item.payload.ki.flags=flags
        if u.SendInput(len(items),items,ctypes.sizeof(self.Input))!=len(items):
            release=(self.Input*3)()
            for item,key in zip(release,(65,17,9)):
                item.type=1;item.payload.ki.vk=key;item.payload.ki.flags=2
            u.SendInput(3,release,ctypes.sizeof(self.Input))
            raise RuntimeError('POP 검사일 입력이 완료되지 않았습니다. 날짜를 확인해 주세요.')

    def popup_inventory(self):
        return {w['handle'] for w in visible_windows(include_untitled=True) if w['pid']==self.target['pid']}

    def open_sequence(self,report):
        field=field_node(report,'세척순서',42)
        buttons=[e for e in nodes(report) if e.get('parent')==field['id'] and e.get('role')==43
                 and e.get('name')=='오픈' and e.get('enabled') and not e.get('offscreen')]
        if len(buttons)!=1:raise RuntimeError('세척순서 펼침 버튼을 확인하지 못했습니다.')
        self.click_handle(field['handle'],selection=(bounds(field),bounds(buttons[0])))

    def sequence_popups(self,previous,field_bounds):
        result=[];fx,fy,fw,fh=field_bounds
        for w in visible_windows(include_untitled=True):
            if w['pid']!=self.target['pid'] or w['handle'] in previous:continue
            r=self.rect(w['handle']);b=[r.left,r.top,r.right-r.left,r.bottom-r.top]
            # A newly visible window directly above/below the sequence input, same process.
            overlaps=b[0]<fx+fw and b[0]+b[2]>fx
            adjacent=min(abs(b[1]-(fy+fh)),abs(b[1]+b[3]-fy))<=max(30,fh)
            if overlaps and adjacent and b[2]>0 and b[3]>0:
                w=dict(w);w['bounds']=b;w['title']=w['title'] or '세척순서 선택 목록';result.append(w)
        return result

    def select_sequence_option(self,popup,option):
        if popup['pid']!=self.target['pid']:raise RuntimeError('세척순서 목록의 프로그램이 달라졌습니다.')
        self.verify(self.target['handle'])
        nested=WindowsClicks(popup);nested.verify(option['handle'])
        r=nested.rect(popup['handle'])
        if any(abs(a-b)>3 for a,b in zip(popup['bounds'],[r.left,r.top,r.right-r.left,r.bottom-r.top])):
            raise RuntimeError('세척순서 선택 목록이 이동했습니다.')
        if (option.get('value') or option.get('name') or '').strip()!=pop_sequence():raise RuntimeError('설정한 세척순번 이외의 항목은 선택하지 않습니다.')
        r=nested.rect(option['handle']);gb=[r.left,r.top,r.right-r.left,r.bottom-r.top]
        nested.click_handle(option['handle'],selection=(gb,bounds(option)),allowed_foreground={self.target['handle'],popup['handle']})

    def checkbox_click(self, view, key, project):
        row=view['visible'].get(key)
        cell=view['selection_cells'].get(key)
        if not row or row.get('프로젝트No')!=project or row.get('선택')!='선택안됨' or not cell or not cell['enabled']:
            raise RuntimeError('체크할 행이나 현재 선택 상태를 확실히 확인하지 못했습니다.')
        self.click_handle(view['handle'],selection=(view['grid_bounds'],cell['bounds']))

    def query_click(self, binding):
        handle=binding['handle'];self.verify(handle);r=self.rect(handle)
        if (binding.get('purpose')!='query' or self.text(handle,True)!=binding['class']
                or self.text(handle)!=binding['text'] or [r.right-r.left,r.bottom-r.top]!=binding['size']):
            raise RuntimeError('등록한 조회 버튼이 바뀌어 중단했습니다.')
        self.click_handle(handle)

    def custom_scroll_thumb(self,handle,stop=None):
        """Recognize the custom WinForms scrollbar observed in POP diagnostics."""
        u=self.u;grid=self.rect(handle);found=[]
        callback_type=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
        @callback_type
        def visit(hwnd,_):
            if (u.GetParent(hwnd)!=handle or not u.IsWindowVisible(hwnd)
                    or not u.IsWindowEnabled(hwnd) or not self.text(hwnd,True).startswith('WindowsForms10.Window.')):return True
            r=self.rect(hwnd);w=r.right-r.left;h=r.bottom-r.top
            if (10<=w<=40 and h>=w*6 and abs(r.right-grid.right)<=3
                    and grid.top<=r.top and r.bottom<=grid.bottom and h>=(grid.bottom-grid.top)*.5):found.append((hwnd,r))
            return True
        u.EnumChildWindows.argtypes=[wintypes.HWND,callback_type,wintypes.LPARAM];u.EnumChildWindows.restype=wintypes.BOOL
        u.EnumChildWindows(handle,visit,0)
        if len(found)!=1:raise RuntimeError('POP 전용 세로 스크롤바 영역을 구분하지 못했습니다.')
        hwnd,r=found[0];self.verify(hwnd)
        x=(r.left+r.right)//2;w=r.right-r.left
        if u.GetForegroundWindow()!=self.target['handle']:raise RuntimeError('POP 창이 앞에 없습니다.')
        for y in (r.top+w,r.bottom-w-1):
            if u.WindowFromPoint(wintypes.POINT(x,y))!=hwnd:raise RuntimeError('POP 스크롤바가 가려져 있습니다.')
        u.GetDC.argtypes=[wintypes.HWND];u.GetDC.restype=wintypes.HDC
        u.ReleaseDC.argtypes=[wintypes.HWND,wintypes.HDC];u.ReleaseDC.restype=ctypes.c_int
        g=ctypes.WinDLL('gdi32');g.GetPixel.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int];g.GetPixel.restype=wintypes.DWORD
        # One small screen copy: subsequent GetPixel calls read memory only.
        g.CreateCompatibleDC.argtypes=[wintypes.HDC];g.CreateCompatibleDC.restype=wintypes.HDC
        g.CreateCompatibleBitmap.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int];g.CreateCompatibleBitmap.restype=wintypes.HBITMAP
        g.SelectObject.argtypes=[wintypes.HDC,wintypes.HANDLE];g.SelectObject.restype=wintypes.HANDLE
        g.BitBlt.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.HDC,ctypes.c_int,ctypes.c_int,wintypes.DWORD];g.BitBlt.restype=wintypes.BOOL
        g.DeleteObject.argtypes=[wintypes.HANDLE];g.DeleteObject.restype=wintypes.BOOL
        g.DeleteDC.argtypes=[wintypes.HDC];g.DeleteDC.restype=wintypes.BOOL
        dc=u.GetDC(None);memory=None;bitmap=None;old=None
        if not dc:raise RuntimeError('스크롤바 색상을 읽지 못했습니다.')
        try:
            memory=g.CreateCompatibleDC(dc);bitmap=g.CreateCompatibleBitmap(dc,w,r.bottom-r.top)
            if not memory or not bitmap:raise RuntimeError('스크롤바 화면 버퍼 생성 실패')
            old=g.SelectObject(memory,bitmap)
            if not old or old==ctypes.c_void_p(-1).value:raise RuntimeError('스크롤바 화면 버퍼 선택 실패')
            for attempt in range(2):
                if (stop is not None and stop.is_set()) or u.GetAsyncKeyState(0x78)&0x8000:raise Stopped('사용자 중지')
                self.verify(hwnd)
                current=self.rect(hwnd)
                if (current.left,current.top,current.right,current.bottom)!=(r.left,r.top,r.right,r.bottom):
                    raise RuntimeError('POP 스크롤바 위치가 바뀌었습니다.')
                if u.GetForegroundWindow()!=self.target['handle']:raise RuntimeError('POP 창이 앞에 없습니다.')
                for y in (r.top+w,r.bottom-w-1):
                    if u.WindowFromPoint(wintypes.POINT(x,y))!=hwnd:raise RuntimeError('POP 스크롤바가 가려져 있습니다.')
                if not g.BitBlt(memory,0,0,w,r.bottom-r.top,dc,r.left,r.top,0x00CC0020):raise RuntimeError('스크롤바 화면 읽기 실패')
                columns=[[],[],[]]
                for y in range(w,r.bottom-r.top-w):
                    if y%32==0 and ((stop is not None and stop.is_set()) or u.GetAsyncKeyState(0x78)&0x8000):raise Stopped('사용자 중지')
                    for column,xx in zip(columns,(w//3,w//2,w-1-w//3)):
                        color=g.GetPixel(memory,xx,y)
                        if color==0xffffffff:raise RuntimeError('스크롤바 색상 읽기 실패')
                        column.append((color&255,(color>>8)&255,(color>>16)&255))
                try:
                    start,end=custom_thumb_columns(columns)
                except RuntimeError:
                    if attempt:raise
                    # Retry only an uncertain paint, without another MSAA read or click.
                    if stop is not None:
                        if stop.wait(.06):raise Stopped('사용자 중지')
                    else:time.sleep(.06)
                    continue
                return hwnd,r,w,w+start,w+end
        finally:
            if old and old!=ctypes.c_void_p(-1).value:g.SelectObject(memory,old)
            if bitmap:g.DeleteObject(bitmap)
            if memory:g.DeleteDC(memory)
            u.ReleaseDC(None,dc)

    def scroll_result_grid(self,view,direction,stop):
        """Drag the actual vertical scrollbar thumb; never send a wheel event."""
        if direction not in (-1,1):raise ValueError('스크롤 방향 오류')
        handle=view['handle'];self.verify(handle);u=self.u
        class ScrollInfo(ctypes.Structure):
            _fields_=[('size',wintypes.DWORD),('rect',wintypes.RECT),
                      ('button',ctypes.c_int),('thumb_top',ctypes.c_int),
                      ('thumb_bottom',ctypes.c_int),('reserved',ctypes.c_int),
                      ('states',wintypes.DWORD*6)]
        u.GetScrollBarInfo.argtypes=[wintypes.HWND,ctypes.c_long,ctypes.POINTER(ScrollInfo)]
        u.GetScrollBarInfo.restype=wintypes.BOOL
        grid=self.rect(handle);candidates=[]
        def inspect(hwnd,object_id):
            info=ScrollInfo();info.size=ctypes.sizeof(info)
            if not u.GetScrollBarInfo(hwnd,object_id,ctypes.byref(info)):return
            r=info.rect
            if info.states[0] & (1|0x8000|0x10000):return
            if not (0<r.right-r.left<r.bottom-r.top and grid.left<=r.left<r.right<=grid.right+3
                    and grid.top<=r.top<r.bottom<=grid.bottom+3):return
            if not (info.button<=info.thumb_top<info.thumb_bottom<=r.bottom-r.top-info.button):return
            candidates.append((hwnd,info))
        inspect(handle,-5) # OBJID_VSCROLL: native non-client scrollbar
        if not candidates:
            callback_type=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
            @callback_type
            def child(hwnd,_):
                if 'scrollbar' in self.text(hwnd,True).lower() and u.IsWindowVisible(hwnd):inspect(hwnd,-4)
                return True
            u.EnumChildWindows.argtypes=[wintypes.HWND,callback_type,wintypes.LPARAM]
            u.EnumChildWindows.restype=wintypes.BOOL
            u.EnumChildWindows(handle,child,0)
        unique={(v.rect.left,v.rect.top,v.rect.right,v.rect.bottom):(h,v) for h,v in candidates}
        if len(unique)!=1:
            if set(view['visible'])==set(view['keys']):return
            hwnd,r,button,thumb_top,thumb_bottom=self.custom_scroll_thumb(handle,stop)
            info=ScrollInfo();info.rect=r;info.button=button;info.thumb_top=thumb_top;info.thumb_bottom=thumb_bottom
        else:hwnd,info=next(iter(unique.values()))
        self.verify(hwnd)
        r=info.rect;x=(r.left+r.right)//2
        thumb=info.thumb_bottom-info.thumb_top
        travel=r.bottom-r.top-2*info.button-thumb
        start=r.top+(info.thumb_top+info.thumb_bottom)//2
        minimum=r.top+info.button+thumb//2
        maximum=minimum+travel
        if travel<=0:return
        if direction==1:end=minimum
        else:
            # Overlap pages so every row can be observed before moving further.
            visible=max(1,len(view['visible']));total=len(view['keys'])
            step=max(1,int(travel*max(1,visible-2)/max(1,total-visible)))
            end=min(maximum,start+step)
        if end==start:return
        left=u.GetSystemMetrics(76);top=u.GetSystemMetrics(77)
        width=u.GetSystemMetrics(78);height=u.GetSystemMetrics(79)
        def guard():
            if stop.is_set() or u.GetAsyncKeyState(0x78)&0x8000:raise Stopped('사용자 중지')
            self.verify(hwnd)
            if u.GetForegroundWindow()!=self.target['handle']:raise RuntimeError('POP 창이 앞에 없어 스크롤을 중단했습니다.')
        def send(flags,y=None):
            event=self.Input();event.payload.mi.flags=flags
            if y is not None:
                if width<=1 or height<=1 or not(left<=x<left+width and top<=y<top+height):raise RuntimeError('스크롤바가 모니터 밖에 있습니다.')
                event.payload.mi.dx=round((x-left)*65535/(width-1));event.payload.mi.dy=round((y-top)*65535/(height-1))
            if u.SendInput(1,ctypes.byref(event),ctypes.sizeof(self.Input))!=1:raise RuntimeError('Windows가 스크롤바 드래그 입력을 완료하지 못했습니다.')
        guard()
        if any(u.GetAsyncKeyState(k)&0x8000 for k in (1,2,16,17,18,91,92)):raise RuntimeError('키 또는 마우스 버튼이 눌려 있습니다.')
        for y in (start,end):
            hit=u.WindowFromPoint(wintypes.POINT(x,y));visited=set()
            while hit and hit not in visited and hit!=handle:
                visited.add(hit);hit=u.GetParent(hit)
            if hit!=handle:raise RuntimeError('POP 스크롤바가 다른 창에 가려져 있습니다.')
        send(0x8000|0x4000|1,start)
        try:
            send(2)
            if stop.wait(.03):raise Stopped('사용자 중지')
            for i in range(1,4):
                guard();send(0x8000|0x4000|1,round(start+(end-start)*i/3))
                if stop.wait(.02):raise Stopped('사용자 중지')
        finally:
            send(4) # Always release, including F9 or partial input failure.


    def scroll_grid(self,handle,direction,allowed_foreground=None):
        if direction not in (-1,1):raise ValueError('스크롤 방향 오류')
        self.verify(handle);u=self.u
        if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped('F9 중지')
        if u.GetForegroundWindow() not in (allowed_foreground or {self.target['handle']}):
            raise RuntimeError('POP 창이 앞에 있지 않아 스크롤을 중단했습니다.')
        if any(u.GetAsyncKeyState(k)&0x8000 for k in (1,2,16,17,18,91,92)):
            raise RuntimeError('키 또는 마우스 버튼이 눌려 있어 스크롤을 중단했습니다.')
        r=self.rect(handle);x=(r.left+r.right)//2;y=(r.top+r.bottom)//2
        hit=u.WindowFromPoint(wintypes.POINT(x,y));ancestors=set()
        while hit and hit not in ancestors and hit!=handle:
            ancestors.add(hit);hit=u.GetParent(hit)
        if hit!=handle:raise RuntimeError('표가 다른 창에 가려져 있어 스크롤을 중단했습니다.')
        left=u.GetSystemMetrics(76);top=u.GetSystemMetrics(77);w=u.GetSystemMetrics(78);h=u.GetSystemMetrics(79)
        if w<=1 or h<=1 or not(left<=x<left+w and top<=y<top+h):raise RuntimeError('표가 모니터 밖에 있습니다.')
        items=(self.Input*2)()
        items[0].payload.mi.dx=round((x-left)*65535/(w-1));items[0].payload.mi.dy=round((y-top)*65535/(h-1))
        items[0].payload.mi.flags=0x8000|0x4000|1
        items[1].payload.mi.flags=0x0800;items[1].payload.mi.data=(direction*120)&0xffffffff
        if u.SendInput(2,items,ctypes.sizeof(self.Input))!=2:
            raise RuntimeError('Windows가 스크롤 입력을 완료하지 못했습니다.')


def custom_thumb_color(rgb):
    # Accept light/dark neutral thumb states, still separate from the light track.
    return max(rgb)-min(rgb)<=8 and 64<=sum(rgb)/3<=228

def custom_thumb_columns(columns):
    """Require two interior scan lines to agree; a center grip is not a second thumb."""
    if len(columns)!=3 or not columns[0] or len({len(c) for c in columns})!=1:
        raise RuntimeError('POP 스크롤바 표본이 올바르지 않습니다.')
    values=[]
    for samples in zip(*columns):
        thumb=[c for c in samples if custom_thumb_color(c)]
        track=[c for c in samples if min(c)>=230 and max(c)-min(c)<=8]
        if len(thumb)>=2:values.append(thumb[0])
        elif len(track)>=2:values.append(track[0])
        else:raise RuntimeError('POP 스크롤 손잡이와 배경을 구분하지 못했습니다.')
    return custom_thumb_span(values)

def custom_thumb_span(values):
    spans=[];start=None
    for i,rgb in enumerate(values+[(255,255,255)]):
        if custom_thumb_color(rgb):
            if start is None:start=i
        elif start is not None:
            if i-start>=8:spans.append((start,i))
            start=None
    if len(spans)!=1:raise RuntimeError('POP 회색 스크롤 손잡이를 하나로 구분하지 못했습니다.')
    start,end=spans[0]
    outside=values[:start]+values[end:]
    if outside and sum(min(c)>=230 and max(c)-min(c)<=8 for c in outside)<len(outside)*.95:
        raise RuntimeError('POP 스크롤바 배경 색상이 예상과 다릅니다.')
    return start,end

# No positional column assumptions: map visible cells by header geometry.
def bounds(node):
    b=node.get('bounds') or [0,0,0,0]
    return b if len(b)==4 else [0,0,0,0]


def pop_grid(report):
    check_capture(report)
    children=defaultdict(list)
    for e in nodes(report):children[e['parent']].append(e)
    found=[]
    for table in nodes(report):
        if table.get('role')!=24:continue
        headers=[h for group in children[table['id']] for h in children[group['id']] if h.get('role')==25]
        if not {'프로젝트No','선택'}.issubset({h.get('name') for h in headers}):continue
        panels=[p for p in children[table['id']] if p.get('name')=='데이터 패널']
        if len(panels)!=1:raise RuntimeError('POP 데이터 패널을 구분할 수 없습니다.')
        panel=panels[0];rows=[r for r in children[panel['id']] if r.get('role')==28]
        if len(rows)!=panel.get('child_count'):raise RuntimeError('POP 일부 행이 누락되었습니다.')
        found.append((table,headers,rows,children))
    if len(found)!=1:raise RuntimeError('POP 프로젝트 표를 하나로 구분하지 못했습니다.')
    table,headers,rows,children=found[0]
    b=bounds(table)
    if b[2]<=0 or b[3]<=0:raise RuntimeError('POP 표의 위치를 읽지 못했습니다. 창을 복원해 주세요.')
    return table,headers,rows,children


class SummaryUnavailable(RuntimeError):
    """화면 밖 행을 행 요약값으로 확인할 수 없는 화면. 이때는 예전의 전체 셀 판독으로 되돌아갑니다."""


# 화면을 다시 그리는 순간에 읽으면 잠깐 나타나는 어긋남. 판독은 읽기 전용이라 다시 읽어도 안전합니다.
TRANSIENT_VIEW_ERRORS=('셀 위치를 확실히 구분하지 못했습니다','POP 행의 일부 셀이 누락되었습니다',
                       'POP 일부 행이 누락되었습니다','POP 행 요약값과 셀 값이 일치하지 않습니다')
# 체크 클릭 뒤 POP가 반영할 때까지 다시 읽으며 기다리는 최대 시간(클릭을 더 하지는 않습니다).
CHECK_SETTLE_SECONDS=4.0
# False: 목록을 예전과 똑같이 모든 줄·모든 칸을 하나씩 읽습니다(현장에서 써 온 방식).
# True : 화면 밖 줄은 행 요약값으로 읽습니다. 현장 POP에서 POP점검.pyw로 '요약값 사용 가능·값 일치'가
#        확인된 뒤에만 켭니다(2026-11-11 사용자 결정: 안전한 쪽으로).
LARGE_LIST_SUMMARY_READING=False


def describe_cover(api,view,key):
    """체크 칸 자리를 실제로 차지한 창이 무엇인지(오류 기록용 글). 입력은 보내지 않으며, 알아내지 못하면 빈 글."""
    try:
        cell=view['selection_cells'][key]['bounds']
        u=api.u;hit=u.WindowFromPoint(wintypes.POINT(round(cell[0]+cell[2]/2),round(cell[1]+cell[3]/2)))
        if not hit:return '창 없음'
        def text(function,handle):
            buffer=ctypes.create_unicode_buffer(256);function(wintypes.HWND(handle),buffer,256)
            return buffer.value.strip()[:60]
        parts=['종류 '+(text(u.GetClassNameW,hit) or '?')]
        pid=wintypes.DWORD();u.GetWindowThreadProcessId(wintypes.HWND(hit),ctypes.byref(pid))
        if u.IsChild(wintypes.HWND(view['handle']),wintypes.HWND(hit)):parts.append('POP 표 안쪽 창')
        elif pid.value==api.target.get('pid'):parts.append('POP의 다른 창')
        else:parts.append('다른 프로그램')
        root=u.GetAncestor(wintypes.HWND(hit),2)
        title=text(u.GetWindowTextW,root) if root else ''
        if title:parts.append('창 제목 '+title)
        return ' · '.join(parts)
    except Exception:return ''


def summary_values(row):
    """행 요약값 'a;b;c;'를 셀 값 목록으로 바꿉니다. 형식이 확실하지 않으면 None."""
    value=row.get('value')
    if not isinstance(value,str) or '[truncated]' in value or not value.endswith(';'):return None
    parts=value[:-1].split(';')
    return parts if parts and len(parts)==row.get('child_count') else None


def read_settled(read_once,stop,tries=3,wait=.4):
    """일시적인 화면 어긋남일 때만 잠깐 기다렸다 다시 읽습니다. 그 밖의 오류는 그대로 올립니다."""
    for attempt in range(tries):
        try:return read_once()
        except (Stopped,SummaryUnavailable):raise
        except RuntimeError as error:
            if attempt==tries-1 or not any(mark in str(error) for mark in TRANSIENT_VIEW_ERRORS):raise
            if stop.wait(wait):raise Stopped('사용자 중지')


def pop_view(report, map_visible=True, baseline_raw=None, summary_rows=False):
    table,headers,rows,children=pop_grid(report)
    b=bounds(table);bottom=max((bounds(h)[1]+bounds(h)[3] for h in headers if bounds(h)[3]>0),default=b[1])
    keys=[];raw=[];visible={};selection_cells={};fast_supported=True;omitted=[]
    wanted=('선택','프로젝트No','설비명','지시일')
    for i,row in enumerate(rows,1):
        match=re.fullmatch(r'(?:행|Row)\s*(\d+)',row.get('name','').strip(),re.I)
        if not match or int(match.group(1))!=i:raise RuntimeError('POP 행 번호가 연속되지 않아 전체 범위를 확인할 수 없습니다.')
        key=str(i);keys.append(key)
        cells=[c for c in children[row['id']] if c.get('role')==29]
        if row.get('cells_omitted') and summary_rows and baseline_raw is None:
            # 화면 밖 행: 칸을 하나씩 읽지 않고 행 요약값으로 값을 얻습니다(건수와 무관하게 빠름).
            values=summary_values(row)
            if values is None or cells:raise SummaryUnavailable('POP 화면 밖 행의 요약값 형식을 확인하지 못했습니다.')
            omitted.append(key)
        elif row.get('cells_omitted'):
            if (baseline_raw is None or i>len(baseline_raw) or cells
                    or row.get('child_count')!=len(baseline_raw[i-1])
                    or row.get('value')!=';'.join(baseline_raw[i-1])+';'):
                raise RuntimeError('POP 화면 밖 행의 값이 바뀌었거나 요약값을 확인하지 못했습니다.')
            values=list(baseline_raw[i-1]);omitted.append(key)
        else:
            if len(cells)!=row.get('child_count'):raise RuntimeError('POP 행의 일부 셀이 누락되었습니다.')
            values=[c.get('value','') for c in cells]
        summary_ok=(row.get('value')==';'.join(values)+';' and '[truncated]' not in row.get('value',''))
        fast_supported=fast_supported and summary_ok
        if baseline_raw is not None and not summary_ok:raise RuntimeError('POP 행 요약값과 셀 값이 일치하지 않습니다.')
        raw.append(values)
        rb=bounds(row)
        if row.get('offscreen') or rb[2]<=0 or rb[3]<=0 or rb[1]<bottom or rb[1]+rb[3]>b[1]+b[3]:continue
        if not map_visible:continue
        mapped={}
        for name in wanted:
            hs=[h for h in headers if h.get('name')==name and bounds(h)[2]>0 and bounds(h)[3]>0]
            if len(hs)!=1:raise RuntimeError('POP '+name+' 열이 보이지 않거나 중복됩니다. 가로 스크롤을 왼쪽으로 맞춰 주세요.')
            hb=bounds(hs[0]);cs=[]
            for c in cells:
                cb=bounds(c)
                if (not c.get('offscreen') and cb[2]>0 and cb[3]>0 and abs(cb[0]-hb[0])<=3
                        and abs(cb[2]-hb[2])<=3 and cb[1]>=rb[1]-2 and cb[1]+cb[3]<=rb[1]+rb[3]+2):cs.append(c)
            if len(cs)!=1:raise RuntimeError('POP '+name+' 셀 위치를 확실히 구분하지 못했습니다. 화면을 확인해 주세요.'
                                             f' ({i}번째 줄 · 맞는 칸 {len(cs)}개 · 이 줄의 칸 {len(cells)}개)')
            cell=cs[0];cn=cell.get('name','').strip()
            if cn and not (cn==name or re.match(re.escape(name)+r'\s+(?:row|행)\s*\d+',cn,re.I)):
                raise RuntimeError('POP 열 이름과 셀 위치가 일치하지 않습니다: '+name)
            mapped[name]=cell.get('value','').strip()
            if name=='선택':
                selection_cells[key]={'index':cells.index(cell),'bounds':bounds(cell),
                                      'enabled':bool(cell.get('enabled') and cell.get('state_known'))}
        visible[key]=mapped
    # 요약값에 의존하려면 화면에 보이는 모든 행에서 '요약값 = 셀 값'이 확인되어야 합니다.
    if summary_rows and omitted and not fast_supported:raise SummaryUnavailable('POP 행 요약값이 셀 값과 달라 요약 판독을 쓸 수 없습니다.')
    return {'handle':table['handle'],'grid_bounds':b,'keys':keys,'raw':raw,'visible':visible,'selection_cells':selection_cells,
            'fast_supported':fast_supported,'omitted':omitted}


def field_node(report,label,role):
    # Link a visible label to the nearest native input on its right, on the same line.
    elements=nodes(report);found={}
    for lab in elements:
        if lab.get('role')!=41 or lab.get('name')!=label:continue
        lb=bounds(lab)
        if lb[2]<=0 or lb[3]<=0:continue
        choices=[]
        for e in elements:
            if e.get('parent')!=-1 or e.get('role')!=role or e.get('offscreen'):continue
            eb=bounds(e);gap=eb[0]-(lb[0]+lb[2])
            if eb[2]>0 and eb[3]>0 and 0<=gap<=lb[3] and abs(eb[1]+eb[3]/2-lb[1]-lb[3]/2)<=lb[3]/3:
                choices.append((gap,e))
        if choices:
            choices.sort(key=lambda x:x[0]);e=choices[0][1];found[e['handle']]=e
    if len(found)!=1:raise RuntimeError(label+' 입력칸을 확실히 읽지 못했습니다.')
    return next(iter(found.values()))


def iso_date(value):
    m=re.search(r'(\d{4})\s*(?:년|[-/.])\s*(\d{1,2})\s*(?:월|[-/.])\s*(\d{1,2})',value)
    if not m:raise ValueError('날짜는 YYYY-MM-DD 형식으로 입력해 주세요.')
    return datetime(*map(int,m.groups())).strftime('%Y-%m-%d')


def inspection_screen_ready(report,api):
    check_capture(report)
    titles=[n for n in nodes(report) if n.get('role')==10
            and n.get('name','').strip()=='공정검사(커스텀)' and api.u.IsWindowVisible(n['handle'])]
    if len({n['handle'] for n in titles})!=1:return False
    try:
        fields=[field_node(report,label,role) for label,role in
                (('검사일',47),('작업자',42),('세척순서',42),('프로젝트No',42))]
    except RuntimeError:return False
    return all(api.u.IsWindowVisible(n['handle']) and api.u.IsWindowEnabled(n['handle']) for n in fields)


def inspection_menu_button(report,api):
    check_capture(report)
    native={n['handle']:n for n in report['records'] if n.get('kind')=='native_window'}
    def usable(n):
        return (n.get('parent')==-1 and n.get('state_known') and n.get('enabled')
                and not n.get('offscreen') and api.u.IsWindowVisible(n['handle']))
    found={}
    for label in nodes(report):
        if label.get('name','').strip()!='공정검사(커스텀)' or not usable(label):continue
        if label.get('role')==43:
            found[label['handle']]=label;continue
        if label.get('role')!=41:continue
        lb=bounds(label);parent=native.get(label['handle'],{}).get('native_parent')
        if not parent or lb[2]<=0 or lb[3]<=0:continue
        for button in nodes(report):
            if button.get('role')!=43 or not usable(button):continue
            if button.get('name','').strip() not in ('','공정검사(커스텀)'):continue
            if native.get(button['handle'],{}).get('native_parent')!=parent:continue
            b=bounds(button);gap=lb[1]-(b[1]+b[3])
            # The supplied main menu has a square icon immediately above its label.
            if (b[2]>40 and b[3]>40 and 0<=gap<=max(30,lb[3])
                    and abs(b[0]+b[2]/2-lb[0]-lb[2]/2)<=lb[3]/2
                    and .6*lb[2]<=b[2]<=1.5*lb[2] and .65*b[2]<=b[3]<=1.5*b[2]):
                found[button['handle']]=button
    if len(found)!=1:raise RuntimeError('POP 공정검사(커스텀) 메뉴를 하나로 찾지 못했습니다. POP 메인 메뉴를 열어 주세요.')
    return next(iter(found.values()))


def ensure_inspection_screen(target,api,capture,stop,emit,initial_report):
    if stop.is_set():raise Stopped('사용자 중지')
    # Reuse the existing initial POP capture: no extra capture or wait when ready.
    if inspection_screen_ready(initial_report,api):return initial_report
    button=inspection_menu_button(initial_report,api)
    if stop.is_set():raise Stopped('사용자 중지')
    api.click_handle(button['handle'],selection=(bounds(button),bounds(button)))
    emit('log','POP 공정검사(커스텀) 메뉴 클릭 · 화면 전환 확인 중')
    deadline=time.monotonic()+8
    for _ in range(8):
        if stop.wait(.2):raise Stopped('사용자 중지')
        report=capture({**target,'mode':'mes_rows'},'POP 공정검사 화면 전환 확인',stop)
        if inspection_screen_ready(report,api):
            emit('log','POP 공정검사(커스텀) 화면 확인 완료')
            return report
        if time.monotonic()>=deadline:break
    raise RuntimeError('POP 공정검사(커스텀) 화면 전환을 확인하지 못했습니다. 추가 클릭 없이 중단했습니다.')


def read_conditions(report):
    check_capture(report)
    return {'date':iso_date(field_node(report,'검사일',47).get('value','')),
            'worker':field_node(report,'작업자',42).get('value','').strip(),
            'sequence':field_node(report,'세척순서',42).get('value','').strip(),
            'project_filter':field_node(report,'프로젝트No',42).get('value','').strip()}


def inspection_date_edit(report):
    field=field_node(report,'검사일',47);fb=bounds(field)
    handles={r['handle'] for r in report['records'] if r.get('kind')=='native_window'
             and r.get('native_parent')==field['handle'] and r.get('class','').startswith('WindowsForms10.EDIT.')}
    matches=[]
    for n in nodes(report):
        b=bounds(n)
        if (n.get('handle') in handles and n.get('parent')==-1 and n.get('role') in (42,47)
                and n.get('enabled') and n.get('state_known') and not n.get('offscreen')
                and b[2]>0 and b[3]>0 and fb[0]<=b[0] and fb[1]<=b[1]
                and b[0]+b[2]<=fb[0]+fb[2] and b[1]+b[3]<=fb[1]+fb[3]):matches.append(n)
    if len(matches)!=1:raise RuntimeError('POP 검사일의 날짜 입력칸을 구분하지 못했습니다.')
    return field,matches[0]


def ensure_inspection_date(target,value,api,capture,stop,emit,initial_report):
    value=iso_date(value);before=read_conditions(initial_report)
    if stop.is_set():raise Stopped('사용자 중지')
    if before['project_filter']:raise RuntimeError('POP 프로젝트No 검색칸을 비워 전체 목록을 조회해 주세요.')
    if before['date']==value:return initial_report
    field,edit=inspection_date_edit(initial_report)
    api.input_inspection_date(field,edit,value,stop)
    for attempt in range(2):
        if stop.wait(.15 if attempt==0 else .2):raise Stopped('사용자 중지')
        after=capture({**target,'mode':'mes_rows'},'POP 검사일 변경 확인',stop)
        actual=read_conditions(after)
        if any(actual[key]!=before[key] for key in ('worker','sequence','project_filter')):
            raise RuntimeError('검사일 입력 중 다른 POP 조건이 바뀌어 중단했습니다.')
        if actual['date']==value:
            emit('log',f"POP 검사일 변경 확인: {before['date']} → {value}")
            return after
    raise RuntimeError(f"POP 검사일 반영 불일치: 요청 [{value}] / 화면 [{actual['date']}]. 조회 전에 중단했습니다.")


def validate_conditions(report,expected,check_sequence=True):
    actual=read_conditions(report)
    for key,label in [('date','POP 검사일'),('worker','작업자'),('sequence','세척순서')]:
        if key=='sequence' and not check_sequence:continue
        wanted=pop_sequence(expected[key]) if key=='sequence' else expected[key]
        if actual[key]!=wanted:raise RuntimeError(f"{label} 불일치: 화면 [{actual[key] or '빈칸'}] / 검사 설정 [{wanted}]. POP에서 맞춰 주세요.")
    if actual['project_filter']:raise RuntimeError('POP 프로젝트No 검색칸을 비워 전체 목록을 조회해 주세요.')
    return actual


def validate_query(report,binding):
    table,_,_,_=pop_grid(report)
    field=field_node(report,'프로젝트No',42);fb=bounds(field)
    candidates=[e for e in nodes(report) if e.get('parent')==-1 and e.get('handle')==binding['handle'] and e.get('role')==43]
    if len(candidates)!=1:raise RuntimeError('등록한 POP 조회 버튼을 다시 확인할 수 없습니다.')
    e=candidates[0];b=bounds(e)
    if (e.get('offscreen') or not e.get('enabled') or b[2]<=0 or b[3]<=0
            or not 0<=b[0]-fb[0]-fb[2]<=fb[3]*2
            or abs(b[1]+b[3]/2-fb[1]-fb[3]/2)>fb[3]/2
            or b[1]+b[3]>bounds(table)[1]):
        raise RuntimeError('프로젝트No 검색칸 오른쪽의 조회 버튼만 지정할 수 있습니다.')


def load_mes(path):
    with zipfile.ZipFile(path) as z:
        info=z.getinfo('MES_cycle.json')
        if info.file_size>20_000_000:raise ValueError('MES 결과 파일이 너무 큽니다.')
        data=json.loads(z.read(info))
    steps=data.get('steps',[])
    requested=data.get('selected_numbers') if data.get('version')==3 else list(range(1,11))
    if (data.get('version') not in (2,3) or not isinstance(requested,list) or not requested
            or any(type(n) is not int or not 1<=n<=10 for n in requested)
            or requested!=sorted(set(requested)) or [s.get('number') for s in steps]!=requested):
        raise ValueError('선택한 호기의 검사가 모두 끝나지 않은 MES 결과입니다.')
    group=data.get('context',{}).get('group',{})
    if group.get('label')!='위쪽 왼쪽의 1~10 버튼':raise ValueError('왼쪽 위 1~10 검사 결과만 사용할 수 있습니다.')
    candidates=[];skipped_blank_program=[];dates=set()
    for step in steps:
        cov=step.get('scroll_coverage',{});rows=step.get('data',{}).get('rows',[])
        verified=(cov.get('all_rows_verified') is True and cov.get('snapshot_checks')==2) if cov.get('method')=='direct_rows' else all(cov.get(k) for k in ('top_verified','bottom_verified'))
        if not step.get('stable') or not cov.get('complete') or not verified or cov.get('seen_rows')!=len(rows) or cov.get('declared_rows')!=len(rows):
            raise ValueError('MES 전체 행 검사가 끝나지 않은 결과입니다.')
        dates.update(step['data'].get('dates',[]))
        for row_position,row in enumerate(rows,1):
            if normalize_sequence(row.get('세척',''))==SEQUENCE:
                number=(row.get('P/No.') or '').strip()
                if not number:
                    skipped_blank_program.append({'number':step['number'],'row':row.get('No.',''),
                                                  'row_position':row_position,'sequence':SEQUENCE})
                    continue
                candidates.append({'project':number,'number':step['number'],'row':row.get('No.',''),
                                   'equipment':[f"CNC 자동선반 {step['number']}호기"],
                                   'equipment_basis':'왼쪽 위에서 실제 선택한 1~10 호기 버튼',
                                   'panel_equipment_label':step['data'].get('equipment_names',[]),'dates':step['data'].get('dates',[])})
    return {'filename':Path(path).name,'candidates':candidates,'skipped_blank_program':skipped_blank_program,'dates':sorted(dates),'scope':group['label'],'sequence':SEQUENCE,'selected_numbers':requested}


def match_rows(source,rows):
    # Exact P/No strings only; never convert letter O to digit 0 or drop leading zeroes.
    a=defaultdict(list);b=defaultdict(list)
    for r in source['candidates']:a[r['project']].append(r)
    for ordinal,r in rows.items():b[r['프로젝트No']].append({'row':ordinal,**r})
    result={'matched':[],'missing':[],'ambiguous':[],'equipment_mismatch':[],'already_selected':[]}
    for project,mes in sorted(a.items()):
        pop=b.get(project,[])
        if len(mes)!=1 or len(pop)>1:result['ambiguous'].append({'project':project,'mes':mes,'pop':pop});continue
        if not pop:result['missing'].append(project);continue
        pair={'project':project,'mes':mes[0],'pop':pop[0]}
        if not mes[0]['equipment'] or pop[0]['설비명'] not in mes[0]['equipment']:
            result['equipment_mismatch'].append(pair);continue
        if pop[0]['선택']!='선택안됨':result['already_selected'].append(pair);continue
        result['matched'].append(pair)
    result['note']='번호와 설비명의 대조 결과입니다. POP 지시일은 MES 생산일·POP 날짜와 동일하다고 가정하지 않습니다. 체크 전 대조 결과이며 저장·완료는 수행하지 않습니다.'
    return result


def match_requested(rows):
    """User-requested checkbox-only test, independent of MES source files."""
    result={'matched':[],'missing':[],'ambiguous':[],'equipment_mismatch':[],'already_selected':[]}
    for project in ('O2026','O2027','O2028'):
        candidates=[{'row':key,**row} for key,row in rows.items() if row.get('프로젝트No')==project]
        if not candidates:result['missing'].append(project);continue
        if len(candidates)!=1:
            result['ambiguous'].append({'project':project,'pop':candidates});continue
        pair={'project':project,'pop':candidates[0],'basis':'사용자가 직접 지정한 체크 시험 번호'}
        if candidates[0]['선택']!='선택안됨':result['already_selected'].append(pair);continue
        result['matched'].append(pair)
    result['note']='O2026·O2027·O2028만 직접 지정해 체크하는 시험. MES 결과와 무관. 저장·완료 없음.'
    return result


def collect_pop(target,initial,expected,api,capture,stop,emit,summary_rows=False):
    """Read all declared rows once, using visible cells to resolve column order."""
    validate_conditions(initial,expected)
    view=pop_view(initial,summary_rows=summary_rows);table,headers,rows,children=pop_grid(initial)
    omitted=set(view.get('omitted',()))
    wanted=('선택','프로젝트No','설비명','지시일');columns={};enabled={};inset=None
    for key in view['visible']:
        row=rows[int(key)-1];cells=[c for c in children[row['id']] if c.get('role')==29]
        for name in wanted:
            hs=[h for h in headers if h.get('name')==name and bounds(h)[2]>0]
            if len(hs)!=1:raise RuntimeError('POP 열을 구분하지 못했습니다: '+name)
            hb=bounds(hs[0])
            indices=[i for i,c in enumerate(cells) if bounds(c)[2]>0 and abs(bounds(c)[0]-hb[0])<=3 and abs(bounds(c)[2]-hb[2])<=3]
            if len(indices)!=1 or (name in columns and columns[name]!=indices[0]):raise RuntimeError('POP 행마다 열 순서가 달라 중단했습니다.')
            columns[name]=indices[0]
            if name=='선택':
                cb=bounds(cells[indices[0]]);rb=bounds(row)
                offsets=[cb[0]-hb[0],cb[1]-rb[1],cb[2]-hb[2],cb[3]-rb[3]]
                if inset is not None and inset!=offsets:raise RuntimeError('POP 체크 칸의 행별 위치가 일정하지 않습니다.')
                inset=offsets
    if rows and set(columns)!=set(wanted):raise RuntimeError('POP 표에서 열을 확인할 수 있는 행이 보이지 않습니다.')
    mapped={};width=len(view['raw'][0]) if rows else 0
    for key,row,values in zip(view['keys'],rows,view['raw']):
        cells=[c for c in children[row['id']] if c.get('role')==29]
        if len(values)!=width or any(i>=len(values) for i in columns.values()):raise RuntimeError('POP 일부 행의 열 개수가 다릅니다.')
        if key in omitted:
            # 값은 요약값으로 확인했습니다. 체크 칸의 열·사용 가능 여부는 이 행이 화면에 보일 때
            # 셀 단위로 확인한 뒤에만 클릭합니다(check_matched의 confirm_cells).
            mapped[key]={name:values[index].strip() for name,index in columns.items()};enabled[key]=None
            continue
        for name,index in columns.items():
            cn=cells[index].get('name','').strip()
            if cn and not (cn==name or re.fullmatch(re.escape(name)+r'\s+(?:row|행)\s*\d+',cn,re.I)):
                raise RuntimeError('POP 화면 밖 행의 열 정보가 다릅니다: '+name)
        mapped[key]={name:values[index].strip() for name,index in columns.items()}
        cell=cells[columns['선택']];enabled[key]=bool(cell.get('enabled') and cell.get('state_known'))
        if key in view['visible'] and mapped[key]!=view['visible'][key]:raise RuntimeError('POP 행 매핑이 화면과 일치하지 않습니다.')
    emit('log',f'POP {len(rows)}행 판독 · 맨 위부터 아래까지 확인 예정')
    return {'complete':not rows,'declared_rows':len(rows),'seen_rows':len(rows),'rows':mapped,
            'raw':view['raw'],'keys':view['keys'],'handle':view['handle'],'columns':columns,
            'enabled':enabled,'selection_inset':inset,'headers':[h.get('name','') for h in headers],
            'row_names':[r.get('name','') for r in rows], 'summary_supported':view['fast_supported'],
            'current_view':view,'wheel_moves':0,'omitted':sorted(omitted,key=int),
            'basis':'MSAA 보이는 행 셀 판독 + 화면 밖 행 요약값' if omitted else 'MSAA 전체 행과 셀 직접 판독'}


def pop_batch_view(report,coverage,expected_raw,allowed_changes=()):
    """Read only the grid; compare every row summary, locate checkbox by geometry."""
    table,headers,rows,children=pop_grid(report)
    if (table['handle']!=coverage['handle'] or [h.get('name','') for h in headers]!=coverage['headers']
            or [r.get('name','') for r in rows]!=coverage['row_names'] or len(rows)!=len(expected_raw)):
        raise RuntimeError('POP 체크 중 표 구조 또는 행 순서가 바뀌었습니다.')
    b=bounds(table);columns=coverage['columns'];allowed=set(allowed_changes)
    checkbox=[h for h in headers if h.get('name')=='선택' and bounds(h)[2]>0 and bounds(h)[3]>0]
    if len(checkbox)!=1:raise RuntimeError('POP 선택 열이 보이지 않습니다.')
    hb=bounds(checkbox[0]);header_bottom=max((bounds(h)[1]+bounds(h)[3] for h in headers if bounds(h)[3]>0),default=b[1])
    visible={};cells={};raw=[]
    for i,(row,expected) in enumerate(zip(rows,expected_raw)):
        key=str(i+1);proposed=list(expected);proposed[columns['선택']]='선택'
        if coverage['summary_supported']:
            value=row.get('value')
            if value==';'.join(expected)+';':actual=list(expected)
            elif key in allowed and value==';'.join(proposed)+';':actual=proposed
            else:raise RuntimeError('POP 체크 중 예상 외의 행 또는 값이 바뀌었습니다. 추가 클릭을 중단합니다.')
        else:
            cs=[c for c in children[row['id']] if c.get('role')==29]
            if len(cs)!=row.get('child_count'):raise RuntimeError('POP 전체 셀을 확인하지 못했습니다.')
            actual=[c.get('value','') for c in cs]
            if actual!=expected and not(key in allowed and actual==proposed):raise RuntimeError('POP 체크 중 예상 외의 값 변경이 감지되었습니다.')
        raw.append(actual);rb=bounds(row)
        if row.get('offscreen') or rb[2]<=0 or rb[3]<=0 or rb[1]<header_bottom or rb[1]+rb[3]>b[1]+b[3]:continue
        dx,dy,dw,dh=coverage['selection_inset']
        cb=[hb[0]+dx,rb[1]+dy,hb[2]+dw,rb[3]+dh]
        if cb[2]<=0 or cb[3]<=0:raise RuntimeError('POP 체크 칸의 크기가 올바르지 않습니다.')
        if not(b[0]<=cb[0] and cb[0]+cb[2]<=b[0]+b[2]):raise RuntimeError('POP 체크 칸이 화면 밖입니다.')
        visible[key]={name:actual[index].strip() for name,index in columns.items()}
        cells[key]={'index':columns['선택'],'bounds':cb,
                    'enabled':coverage['enabled'][key] and bool(row.get('enabled') and row.get('state_known'))}
    return {'handle':table['handle'],'grid_bounds':b,'keys':coverage['keys'],'raw':raw,'visible':visible,'selection_cells':cells}


def check_matched(target,expected,coverage,matches,api,capture,stop,emit):
    """Click a visible page as a batch; verify that batch before moving on."""
    expected_raw=[list(r) for r in coverage['raw']]
    targets={str(p['pop']['row']):p['project'] for p in matches}
    if len(targets)!=len(matches):raise RuntimeError('체크 대상 행이 중복됩니다.')
    current=coverage['current_view'];pending=set(targets);done=[];moves=0;stalled=0
    grid_target={'handle':coverage['handle'],'pid':target.get('pid',0),'title':'POP 결과표',
                 'mode':'mes_rows' if coverage['summary_supported'] else 'pop_full'}
    select=coverage['columns']['선택'];cover_notes={}
    def read(label,allowed=()):
        if stop.is_set():raise Stopped('사용자 중지 — 이미 체크된 행은 그대로 유지됩니다.')
        r=capture(grid_target,label,stop);emit('capture',r)
        return pop_batch_view(r,coverage,expected_raw,allowed)
    def click(keys,view,clicks):
        """실제로 누른 행은 clicks에 세고, 체크 칸이 잠깐 가려져 누르지 못한 행을 돌려줍니다."""
        covered=[]
        for key in keys:
            if stop.is_set():raise Stopped('사용자 중지')
            row=view['visible'].get(key)
            if not row or row['프로젝트No']!=targets[key] or row['선택']!='선택안됨':raise RuntimeError('체크할 프로젝트 또는 상태가 달라졌습니다.')
            try:api.checkbox_click(view,key,targets[key])
            except Stopped:raise
            except RuntimeError as error:
                # 가림 검사는 입력을 보내기 전에 하므로 이 행은 아직 눌리지 않았습니다.
                if '가려져' not in str(error):raise
                cover_notes[key]=describe_cover(api,view,key)
                emit('log',f'{key}번째 줄 체크 칸이 가려짐'+(' — '+cover_notes[key] if cover_notes[key] else ''))
                covered.append(key);continue
            clicks[key]+=1
            emit('check',{'row':key,'project':targets[key],'status':'attempt'})
            if stop.wait(.04):raise Stopped('사용자 중지 — 마지막 클릭 상태를 확인해 주세요.')
        return covered
    def settle(batch,label):
        """POP가 체크를 반영할 때까지 다시 읽으며 기다립니다. 클릭을 더 하지는 않습니다."""
        nonlocal current
        deadline=time.monotonic()+CHECK_SETTLE_SECONDS
        while True:
            current=read(label,batch)
            unchanged=[k for k in batch if current['raw'][int(k)-1][select]=='선택안됨']
            if not unchanged or time.monotonic()>=deadline:return unchanged
            if stop.wait(.25):raise Stopped('사용자 중지')
    def confirm_cells(keys):
        """요약값으로만 읽은 행은, 화면에 보일 때 셀 단위로 열·값·체크 칸 상태를 확인한 뒤에만 누릅니다."""
        def once():
            if stop.is_set():raise Stopped('사용자 중지')
            r=capture({**grid_target,'mode':'pop_fast'},'POP 대상 행 셀 확인',stop);emit('capture',r)
            return pop_view(r,baseline_raw=expected_raw)
        view=read_settled(once,stop)
        if view['handle']!=coverage['handle'] or view['keys']!=coverage['keys']:
            raise RuntimeError('POP 체크 중 표 구조 또는 행 순서가 바뀌었습니다.')
        for key in keys:
            cell=view['selection_cells'].get(key);planned=current['selection_cells'].get(key)
            wanted={name:expected_raw[int(key)-1][index].strip() for name,index in coverage['columns'].items()}
            if (not cell or not planned or view['visible'].get(key)!=wanted or cell['index']!=select
                    or any(abs(a-b)>3 for a,b in zip(cell['bounds'],planned['bounds']))):
                raise RuntimeError('체크할 행의 셀을 화면에서 확실히 확인하지 못했습니다. 추가 클릭을 중단합니다.')
            coverage['enabled'][key]=bool(cell['enabled'])
    def signature(view):
        return tuple((k,tuple(view['selection_cells'][k]['bounds'])) for k in view['visible'])
    def move(direction,label):
        nonlocal current,moves
        if stop.is_set():raise Stopped('사용자 중지')
        if moves>=max(180,len(coverage['keys'])*3):
            raise RuntimeError('POP 전체 스크롤 확인 한도를 초과했습니다.')
        old=signature(current)
        api.scroll_result_grid(current,direction,stop);moves+=1
        if stop.wait(.06):raise Stopped('사용자 중지')
        current=read(label+' '+str(moves))
        if signature(current)==old:
            # Only a stationary frame needs the longer paint-settle check.
            if stop.wait(.2):raise Stopped('사용자 중지')
            current=read(label+' 반영 재확인')
        return signature(current)!=old
    first=coverage['keys'][0];last=coverage['keys'][-1]
    emit('log','POP 맨 위로 이동 · 첫 행과 스크롤 정지 확인')
    while True:
        changed=move(1,'POP 맨 위 이동')
        if not changed and first in current['visible']:break
        stalled=0 if changed else stalled+1
        if stalled>=3:raise RuntimeError('POP 맨 위 첫 행을 확인하지 못했습니다. 스크롤을 확인해 주세요.')
    coverage['top_verified']=True
    seen=set();stalled=0
    emit('log','POP 맨 위 확인 · 아래로 내려가며 전체 행 검사')
    while True:
        seen.update(current['visible'])
        batch=sorted(pending & set(current['visible']),key=int)
        if batch:
            unknown=[k for k in batch if coverage['enabled'].get(k) is None]
            if unknown:
                confirm_cells(unknown)
                current=read('POP 대상 행 확인 후 화면')
            emit('log',f'화면 안 대상 {len(batch)}개 연속 체크')
            clicks={k:0 for k in batch};remaining=list(batch);covers=0;rounds=0
            while remaining:
                covered=click(remaining,current,clicks);rounds+=1
                if stop.wait(.12):raise Stopped('사용자 중지')
                unchanged=settle(batch,'POP 화면 단위 체크 확인' if rounds==1 else 'POP 미반영 항목 재확인')
                if covered and unchanged:
                    covers+=1
                    if covers>3:
                        seen_covers=sorted({note for note in cover_notes.values() if note})
                        raise RuntimeError('체크 칸이 다른 창에 계속 가려져 있어 중단했습니다. POP 화면을 확인해 주세요.'
                                           +(' (가린 창: '+' / '.join(seen_covers)+')' if seen_covers else ''))
                    emit('log',f'체크 칸이 잠시 가려져 있어 기다렸다 다시 확인합니다({covers}/3).')
                    if stop.wait(1.0):raise Stopped('사용자 중지')
                    # 기다리는 동안 늦게 반영됐을 수 있으므로, 다시 누르기 직전의 화면으로 판단합니다.
                    current=read('POP 미반영 항목 재확인',batch)
                    unchanged=[k for k in batch if current['raw'][int(k)-1][select]=='선택안됨']
                # 같은 행은 두 번까지만 누릅니다(기존 기준 유지).
                remaining=[k for k in unchanged if clicks[k]<2]
                if remaining and not covered:emit('log',f'체크 미반영 {len(remaining)}개 · 한 번 더 클릭')
            for key in batch:
                if current['raw'][int(key)-1][coverage['columns']['선택']]!='선택':raise RuntimeError('두 번 이내의 클릭으로 체크되지 않았습니다. 추가 클릭하지 않습니다.')
                expected_raw[int(key)-1][coverage['columns']['선택']]='선택'
                pending.remove(key)
                event={'row':key,'project':targets[key],'status':'verified','at':datetime.now().isoformat(timespec='seconds')}
                done.append(event);emit('check',event)
            emit('log',f'체크 확인 {len(done)}/{len(targets)}개')
            stalled=0
            continue
        if stop.is_set():raise Stopped('사용자 중지')
        changed=move(-1,'POP 아래로 확인')
        seen.update(current['visible'])
        if not changed and last in current['visible']:
            if pending:
                raise RuntimeError('POP 맨 아래에 도달했지만 체크하지 못한 대상 행이 있습니다: '+', '.join(sorted(pending,key=int)))
            if seen!=set(coverage['keys']):
                raise RuntimeError('POP 위에서 아래까지 확인하지 못한 행이 있습니다. 완료 처리하지 않습니다.')
            coverage.update(bottom_verified=True,complete=True,seen_rows=len(seen),wheel_moves=moves)
            emit('log',f'POP 맨 아래 도달 확인 · 전체 {len(seen)}행 검사 · 대상 {len(done)}개 체크 확인')
            break
        stalled=0 if changed else stalled+1
        if stalled>=3:raise RuntimeError('POP 맨 아래에 도달하기 전에 스크롤이 멈췄습니다. 완료 처리하지 않습니다.')
    if stop.is_set():raise Stopped('사용자 중지')
    if coverage.get('omitted'):
        # 화면 밖 행은 요약값이 예상과 한 글자도 다르지 않은지, 보이는 행은 셀 단위로 다시 확인합니다.
        def final_once():
            report=capture({**target,'mode':'pop_fast'},'체크 검사 최종 상태 확인',stop);emit('capture',report);validate_conditions(report,expected)
            return report,pop_view(report,baseline_raw=expected_raw)
        final,final_view=read_settled(final_once,stop)
        coverage['final_baseline']=[list(r) for r in expected_raw]
    else:
        final=capture({**target,'mode':'pop_final'},'체크 검사 최종 상태 확인',stop);emit('capture',final);validate_conditions(final,expected)
        final_view=pop_view(final)
    if final_view['handle']!=coverage['handle'] or final_view['keys']!=coverage['keys'] or final_view['raw']!=expected_raw:
        raise RuntimeError('최종 체크 결과가 예상과 다릅니다. POP 화면을 확인해 주세요.')
    coverage['final_report']=final
    return done


def sequence_column_items(report):
    """Validate the whole code column, including zero-height offscreen cells.

    DevExpress retains all codes in MSAA, but the last page can contain only
    29/30 plus tool names. Visibility is required separately before clicking.
    """
    check_capture(report)
    items=[n for n in nodes(report) if n.get('role') in (29,34,41)
           and n.get('enabled') and n.get('state_known') and bounds(n)[2]>0]
    known=[n for n in items if (n.get('value') or n.get('name') or '').strip() in (*SEQUENCE_VALUES,'완료')]
    columns={}
    for n in known:
        b=bounds(n)
        aligned=[other for other in items if other.get('handle')==n.get('handle')
                 and abs(bounds(other)[0]-b[0])<=4 and abs(bounds(other)[2]-b[2])<=4]
        codes={(e.get('value') or e.get('name') or '').strip() for e in aligned}
        codes.intersection_update(SEQUENCE_VALUES)
        if len(codes)>=3 and any({f'{v:02}',f'{v+1:02}'}.issubset(codes) for v in range(1,30)):
            for e in aligned:columns[e['id']]=e
    return list(columns.values())


def sequence_option(report):
    candidates=[]
    for e in sequence_column_items(report):
        b=bounds(e)
        if e.get('offscreen') or b[2]<=0 or b[3]<=0:continue
        if (e.get('value') or e.get('name') or '').strip()==pop_sequence():candidates.append(e)
    unique={tuple(bounds(e)):e for e in candidates}
    if len(unique)!=1:raise RuntimeError('세척순서 목록에서 선택할 항목을 확실히 구분하지 못했습니다. 검사 기록을 보내 주세요.')
    return next(iter(unique.values()))


def find_sequence_option(popups,api,capture,stop,emit):
    def read(popup):
        if stop.is_set():raise Stopped('사용자 중지')
        r=capture(popup,'세척순서 선택 목록 후보 '+str(popup['handle']),stop);emit('capture',r)
        if stop.is_set():raise Stopped('사용자 중지')
        try:check_capture(r)
        except RuntimeError:
            emit('log','세척순서 후보 창을 읽지 못했습니다: '+str(popup['handle']))
            return None
        # Shadow/helper windows can appear with the dropdown. Inspect their
        # contents instead of treating every new window as a separate list.
        if popup.get('bounds'):
            import copy
            r=copy.deepcopy(r);pb=popup['bounds']
            for n in nodes(r):
                b=bounds(n)
                if not(pb[0]<=b[0] and pb[1]<=b[1] and b[0]+b[2]<=pb[0]+pb[2] and b[1]+b[3]<=pb[1]+pb[3]):n['offscreen']=True
        columns=sequence_column_items(r)
        visible=[n for n in columns if not n.get('offscreen') and bounds(n)[3]>0]
        if not visible:return None
        signature=tuple(sorted({((n.get('value') or n.get('name') or '').strip(),tuple(bounds(n))) for n in visible}))
        codes={v for v,b in signature}
        option=sequence_option(r) if pop_sequence() in codes else None
        # Full MSAA item order is available even for zero-height hidden items.
        # Head toward the target immediately; no forced trip to the top.
        positions=[i for i,n in enumerate(columns) if (n.get('value') or n.get('name') or '').strip()==pop_sequence()]
        visible_ids={n['id'] for n in visible}
        visible_positions=[i for i,n in enumerate(columns) if n['id'] in visible_ids]
        direction=0
        if len(positions)==1 and visible_positions:
            if positions[0]<min(visible_positions):direction=1
            elif positions[0]>max(visible_positions):direction=-1
        return option,signature,direction

    candidates=[];seen=set()
    emit('sequence',{'action':'popup_candidates','windows':popups})
    for popup in popups:
        if popup['handle'] in seen:continue
        seen.add(popup['handle'])
        result=read(popup)
        if result is not None:candidates.append((popup,*result))
    if not candidates:raise RuntimeError('세척순서 목록 구조를 확인하지 못했습니다. 검사 기록을 보내 주세요.')
    if len(candidates)!=1:raise RuntimeError('실제 세척순서 목록이 여러 개여서 구분하지 못했습니다. 검사 기록을 보내 주세요.')
    popup,option,signature,preferred=candidates[0]
    if option:return popup,option
    emit('log',f'세척순번 {pop_sequence()} 항목이 있는 방향으로 목록을 스크롤합니다.')
    nested=WindowsClicks(popup)
    for direction in ((preferred,-preferred) if preferred else (1,-1)):
        for _ in range(40):
            if stop.is_set():raise Stopped('사용자 중지')
            nested.scroll_grid(popup['handle'],direction,allowed_foreground={api.target['handle'],popup['handle']})
            if stop.wait(.15):raise Stopped('사용자 중지')
            result=read(popup)
            if result is None:raise RuntimeError('스크롤 중 세척순서 목록을 읽지 못했습니다. 검사 기록을 보내 주세요.')
            option,current,_=result
            if option:return popup,option
            if current==signature:break
            signature=current
        else:raise RuntimeError('세척순서 목록 스크롤 한도를 초과했습니다.')
    raise RuntimeError(f'POP 목록에서 세척순번 {pop_sequence()} 항목을 찾지 못했습니다. 검사 기록을 보내 주세요.')


def ensure_sequence(target,expected,api,capture,stop,emit,initial_report=None):
    if stop.is_set():raise Stopped('사용자 중지')
    before=initial_report if initial_report is not None else capture({**target,'mode':'mes_rows'},'세척순서 자동 설정 전',stop)
    if initial_report is None:emit('capture',before)
    actual=validate_conditions(before,expected,check_sequence=False)
    if actual['sequence']==pop_sequence():
        emit('log',f'POP 세척순서 {pop_sequence()} 확인 — 그대로 사용합니다.');return before
    field=field_node(before,'세척순서',42)
    if stop.is_set():raise Stopped('사용자 중지')
    previous=api.popup_inventory()
    emit('log',f'POP 세척순서 목록에서 {pop_sequence()} 항목을 찾습니다.')
    api.open_sequence(before)
    if stop.wait(.5):raise Stopped('사용자 중지')
    popups=api.sequence_popups(previous,bounds(field))
    if not popups:raise RuntimeError('세척순서 선택 목록을 찾지 못했습니다. POP 화면과 화면을 확인해 주세요.')
    popup,option=find_sequence_option(popups,api,capture,stop,emit)
    if stop.is_set():raise Stopped('사용자 중지')
    emit('log',f'세척순번 {pop_sequence()} 항목 확인 → 해당 번호를 클릭합니다.')
    api.select_sequence_option(popup,option)
    emit('sequence',{'action':'select','value':pop_sequence(),'mes_sequence':SEQUENCE,'previous':actual['sequence']})
    if stop.wait(.5):raise Stopped('사용자 중지')
    after=capture({**target,'mode':'mes_rows'},f'세척순서 {pop_sequence()} 설정 후 확인',stop);emit('capture',after)
    validate_conditions(after,expected)
    emit('sequence',{'action':'verified','value':pop_sequence(),'mes_sequence':SEQUENCE})
    emit('log',f'POP 세척순서 {pop_sequence()} 자동 설정 확인 완료. 조회를 진행합니다.')
    return after


def pop_save_button(report):
    validate_conditions(report,read_conditions(report))
    field=field_node(report,'검사일',47);limit=bounds(field)[1]
    buttons=[n for n in nodes(report) if n.get('parent')==-1 and n.get('role')==43
             and n.get('enabled') and n.get('state_known') and not n.get('offscreen')
             and bounds(n)[2]>0 and bounds(n)[3]>0 and bounds(n)[1]+bounds(n)[3]<=limit]
    named=[n for n in buttons if n.get('name','').strip()=='저장']
    if len(named)==1:return named[0]
    # Observed POP toolbar: two unnamed sibling buttons, Save then Close.
    native={n['handle']:n for n in report['records'] if n.get('kind')=='native_window'}
    if len(buttons)!=2:raise RuntimeError('POP 상단 저장 버튼을 구분하지 못했습니다.')
    left,right=sorted(buttons,key=lambda n:bounds(n)[0]);a=bounds(left);b=bounds(right)
    lp=native.get(left['handle'],{}).get('native_parent');rp=native.get(right['handle'],{}).get('native_parent')
    if (not lp or lp!=rp or any(n.get('name','').strip() for n in buttons)
            or abs(a[1]-b[1])>2 or a[2:]!=b[2:] or not 0<b[0]-a[0]-a[2]<=a[2]*.15):
        raise RuntimeError('POP 저장·닫기 버튼 배치가 달라 저장을 중단했습니다.')
    return left


def save_dialog_messages(report):
    # Static labels are read, not clicked: a provider can expose their text
    # without an enabled/known state. Name and value may repeat the same text.
    return {re.sub(r'\s+','',str(n.get(key) or ''))
            for n in nodes(report) if not n.get('offscreen') and n.get('role') in (10,41)
            for key in ('name','value') if str(n.get(key) or '').strip()}


def save_dialog_button(report,phase,allow_pending=False):
    check_capture(report)
    visible=[n for n in nodes(report) if not n.get('offscreen') and n.get('enabled') and n.get('state_known')]
    messages=save_dialog_messages(report)
    expected='저장하시겠습니까?' if phase=='confirm' else '완료되었습니다.'
    if expected not in messages:
        if allow_pending and not messages:return None
        raise RuntimeError('POP '+('저장 확인' if phase=='confirm' else '저장 완료')+' 문구가 예상과 다릅니다: '+' / '.join(sorted(messages))[:250])
    labels={'예(YES)'} if phase=='confirm' else {'닫기'}
    buttons=[n for n in visible if n.get('role')==43 and re.sub(r'\s+','',n.get('name','')) in labels and bounds(n)[2]>0 and bounds(n)[3]>0]
    unique={(n['handle'],tuple(bounds(n))):n for n in buttons}
    if allow_pending and not unique:return None
    if len(unique)!=1:raise RuntimeError('POP '+('예(YES)' if phase=='confirm' else '닫기')+' 버튼을 하나로 구분하지 못했습니다.')
    return next(iter(unique.values()))


def save_checked_pop(target,expected,result,api,capture,stop,emit):
    result['save_status']='not_started';result['save_performed']=False
    matching=result['matching'];pairs=matching['matched']+matching['already_selected']
    allowed={str(p['pop']['row']) for p in pairs}
    if not allowed:
        result['save_status']='no_targets';emit('log','저장할 매칭 대상이 없어 저장을 생략했습니다.');return
    coverage=result['coverage']
    if result.get('check_status')!='verified' or not all(coverage.get(k) for k in ('complete','top_verified','bottom_verified')):
        raise RuntimeError('전체 행 체크 검증이 끝나지 않아 저장하지 않았습니다.')
    report=coverage.pop('final_report',None)
    if report is None:raise RuntimeError('저장 전 최종 검증 화면이 없습니다.')
    validate_conditions(report,expected);baseline=coverage.pop('final_baseline',None)
    # 요약 판독으로 최종 확인한 경우에만, 그때의 예상값으로 화면 밖 행을 다시 대조합니다.
    view=pop_view(report) if baseline is None else pop_view(report,baseline_raw=baseline)
    selected={k for k,row in zip(view['keys'],view['raw']) if row[coverage['columns']['선택']].strip()=='선택'}
    if selected!=allowed:raise RuntimeError('POP에 매칭 대상 외 체크 또는 누락이 있어 저장하지 않았습니다. 체크 상태를 확인해 주세요.')
    button=pop_save_button(report);previous=api.popup_inventory()
    if stop.is_set():raise Stopped('사용자 중지 — 저장 전')
    result['save_status']='save_click_attempted';emit('result',result)
    api.click_handle(button['handle']);result['save_performed']=True;result['save_status']='waiting_confirmation'
    emit('log','POP 저장 버튼 1회 클릭 · 저장 확인창 대기')
    popup=None
    for _ in range(50):
        if stop.wait(.1):raise Stopped('사용자 중지 — 저장 확인창 상태를 확인해 주세요.')
        fresh=[w for w in visible_windows(include_untitled=True) if w['pid']==target['pid'] and w['handle'] not in previous]
        fresh=[w for w in fresh if api.u.GetForegroundWindow()==w['handle']]
        if len(fresh)==1:popup=fresh[0];break
    if popup is None:raise RuntimeError('저장 확인창을 찾지 못했습니다. 저장 버튼을 다시 누르지 않았습니다.')
    api.u.GetWindow.argtypes=[wintypes.HWND,wintypes.UINT];api.u.GetWindow.restype=wintypes.HWND
    owner=api.u.GetWindow(popup['handle'],4);seen=set()
    while owner and owner!=target['handle'] and owner not in seen:
        seen.add(owner);owner=api.u.GetWindow(owner,4)
    if owner!=target['handle']:raise RuntimeError('POP에서 띄운 저장 확인창인지 확인하지 못했습니다.')
    dialog=capture(popup,'POP 저장 확인창',stop);choice=save_dialog_button(dialog,'confirm')
    nested=WindowsClicks(popup)
    if stop.is_set():raise Stopped('사용자 중지 — 확인 클릭 전')
    result['save_status']='confirmation_click_attempted';emit('result',result)
    nested.click_handle(choice['handle'])
    result['confirmation_clicked']=True;result['save_status']='waiting_completion'
    emit('log','POP 예(YES) 클릭 · 완료 메시지 대기')
    completed=None;deadline=time.monotonic()+30
    while time.monotonic()<deadline:
        if stop.wait(.1):raise Stopped('사용자 중지 — 저장 처리 중입니다. POP 완료 여부를 확인해 주세요.')
        dialogs=[w for w in visible_windows(include_untitled=True) if w['pid']==target['pid']
                 and w['handle']!=target['handle'] and (w['handle'] not in previous or w['handle']==popup['handle'])
                 and api.u.GetForegroundWindow()==w['handle']]
        if len(dialogs)!=1:continue
        current=dialogs[0]
        owner=api.u.GetWindow(current['handle'],4);seen=set()
        while owner and owner!=target['handle'] and owner not in seen:
            seen.add(owner);owner=api.u.GetWindow(owner,4)
        if owner!=target['handle']:raise RuntimeError('POP 저장 완료창의 소유자를 확인하지 못했습니다.')
        report=capture(current,'POP 저장 완료창',stop)
        messages=save_dialog_messages(report)
        if '저장하시겠습니까?' in messages:
            # The affirmative click is never repeated while the old dialog is closing.
            continue
        choice=save_dialog_button(report,'complete',allow_pending=True)
        # A newly visible dialog may not expose its labels/close control yet.
        # Re-read within the existing deadline; never repeat Save or Yes.
        if choice is None:continue
        completed=current
        result['pop_success_reported']=True;result['save_status']='completion_close_attempted'
        if stop.is_set():raise Stopped('사용자 중지 — POP 완료 메시지 확인, 닫기 전')
        WindowsClicks(current).click_handle(choice['handle'])
        break
    if completed is None:raise RuntimeError('POP 완료 메시지를 기다리다 중단했습니다. 저장·예를 다시 누르지 않았습니다.')
    for _ in range(50):
        if stop.wait(.1):raise Stopped('사용자 중지 — POP 완료창 닫기 후 상태를 확인해 주세요.')
        if not api.u.IsWindowVisible(completed['handle']) and api.u.IsWindowEnabled(target['handle']):
            result['save_status']='confirmed';result['completion_performed']=True;result['completion_closed']=True
            emit('log','POP 저장 → 예 → 완료 메시지 → 닫기 완료');emit('result',result);return
    raise RuntimeError('저장 완료창 닫기를 확인하지 못했습니다. 추가 클릭하지 않았습니다.')



def pop_steps(target,binding,expected,source,api,capture,stop,emit,initial_report=None):
    if expected.get('sequence')!=SEQUENCE:raise RuntimeError('요청한 세척순번과 실행 설정이 다릅니다.')
    if source and source.get('sequence')!=SEQUENCE:raise RuntimeError('MES 대상의 세척순번이 실행 설정과 다릅니다.')
    def read(label):
        if stop.is_set():raise Stopped('사용자 중지')
        report=capture({**target,'mode':'pop_full'},label,stop);emit('capture',report);validate_conditions(report,expected)
        return report
    before=ensure_sequence(target,expected,api,capture,stop,emit,initial_report=initial_report);validate_query(before,binding)
    if stop.is_set():raise Stopped('사용자 중지')
    api.query_click(binding);emit('log','POP 조회 완료 · 2초 대기 후 목록을 한 번 읽습니다.')
    emit('query',{'click_count':1,'wait_seconds':2.0,'server_refresh_confirmed':False})
    if stop.wait(2.0):raise Stopped('사용자 중지')
    def read_list():
        # 보이는 행은 셀까지, 화면 밖 행은 요약값으로 읽어 건수가 많아도 읽기 시간이 한도에 걸리지 않게 합니다.
        if stop.is_set():raise Stopped('사용자 중지')
        report=capture({**target,'mode':'pop_fast'},'POP 조회 후 전체 목록 1회 판독',stop);emit('capture',report);validate_conditions(report,expected)
        return report,collect_pop(target,report,expected,api,capture,stop,emit,summary_rows=True)
    def read_all_cells():
        report=read('POP 조회 후 전체 목록 1회 판독')
        return report,collect_pop(target,report,expected,api,capture,stop,emit)
    for attempt in range(3):
        if not LARGE_LIST_SUMMARY_READING:
            # 예전 방식 그대로. 화면을 다시 그리는 순간의 판독 어긋남일 때만 한 번 더 읽습니다.
            last,coverage=read_settled(read_all_cells,stop,tries=2);break
        try:last,coverage=read_settled(read_list,stop)
        except SummaryUnavailable:
            emit('log','행 요약값을 쓸 수 없는 화면이라 전체 셀 판독으로 진행합니다.')
            last,coverage=read_all_cells()
        if not coverage['keys'] or not coverage['summary_supported']:break
        # 조회 결과가 아직 채워지는 중(또는 다른 PC가 같은 목록을 바꾸는 중)인지 클릭 전에 한 번 더 확인합니다.
        if stop.wait(.6):raise Stopped('사용자 중지')
        probe=capture({'handle':coverage['handle'],'pid':target.get('pid',0),'title':'POP 결과표','mode':'mes_rows'},'POP 목록 안정 확인',stop)
        try:pop_batch_view(probe,coverage,[list(r) for r in coverage['raw']]);break
        except Stopped:raise
        except RuntimeError as error:
            if '바뀌었습니다' not in str(error):raise
            if attempt==2:raise RuntimeError('POP 목록이 계속 바뀌어 시작하지 않았습니다. 다른 PC에서 같은 목록을 작업 중인지 확인해 주세요.')
            emit('log','POP 목록이 아직 바뀌는 중이라 다시 읽습니다.')
            if stop.wait(1.5):raise Stopped('사용자 중지')
    result={'conditions':expected,'query_click_count':1,'post_query_reads':1,'query_wait_seconds':2.0,
            'server_refresh_confirmed':False,'coverage':coverage,'mes_source':source,
            'matching':match_rows(source,coverage['rows']),
            'requested_projects':[r['project'] for r in source['candidates']],
            'checks_performed':False,'completion_performed':False}
    emit('result',result)
    if coverage['keys']:
        result['check_status']='in_progress';result['checks_performed']=None
        checks=check_matched(target,expected,coverage,result['matching']['matched'],api,capture,stop,emit)
        result['checks_performed']=bool(checks);result['verified_checks']=checks;result['check_status']='verified'
        emit('result',result)
        emit('log',f'세척{SEQUENCE} 체크 {len(checks)}개 확인 완료. 최종 체크 검증 완료.')
        return result
    emit('log','검사 종료. POP 목록이 비어 있어 매칭 검증은 보류합니다.' if not coverage['rows'] else '체크할 매칭 대상이 없습니다. 화면을 확인해 주세요.')
    return result




def worker_button(report):
    field=field_node(report,'작업자',42); fb=bounds(field)
    candidates=[]
    for n in nodes(report):
        b=bounds(n)
        if (n.get('parent')==-1 and n.get('role')==43 and n.get('enabled')
            and not n.get('offscreen') and 0<=b[0]-fb[0]-fb[2]<=fb[3]/2
            and abs(b[1]+b[3]/2-fb[1]-fb[3]/2)<fb[3]/3
            and 0<b[2]<=fb[3]*1.5 and 0<b[3]<=fb[3]*1.5
            and not any(s in n.get('name','') for s in ('완료','저장','삭제','닫기'))):
            candidates.append(n)
    if len(candidates)!=1:raise RuntimeError('작업자 옆 돋보기를 하나로 구분하지 못했습니다. 화면을 확인해 주세요.')
    return candidates[0]


def worker_choice(report,name):
    check_capture(report)
    children=defaultdict(list)
    for n in nodes(report):children[n['parent']].append(n)
    tables=[]
    for table in nodes(report):
        if table.get('role')!=24:continue
        headers=[h for g in children[table['id']] for h in children[g['id']] if h.get('role')==25]
        if {'선택','사용자ID','작업자'}.issubset({h.get('name') for h in headers}):tables.append((table,headers))
    if len(tables)!=1:raise RuntimeError('작업자 표를 구분하지 못했습니다. 화면을 확인해 주세요.')
    table,headers=tables[0];tb=bounds(table)
    panels=[p for p in children[table['id']] if p.get('name')=='데이터 패널']
    if len(panels)!=1:raise RuntimeError('작업자 목록 데이터 패널을 확인하지 못했습니다.')
    panel=panels[0];rows=[r for r in children[panel['id']] if r.get('role')==28]
    if len(rows)!=panel.get('child_count'):raise RuntimeError('작업자 목록의 일부 행을 읽지 못했습니다.')
    # Count every returned row, including offscreen rows, to reject duplicate names.
    hits=[]
    for row in rows:
        cells=[c for c in children[row['id']] if c.get('role')==29]
        if len(cells)!=row.get('child_count'):raise RuntimeError('작업자 행의 일부 칸을 읽지 못했습니다.')
        if any(str(c.get('value','')).strip()==name for c in cells):hits.append((row,cells))
    if len(hits)!=1:raise RuntimeError(f'이름 [{name}] 검색 결과 {len(hits)}개입니다. 이름과 목록을 확인하고 화면을 확인해 주세요.')
    row,cells=hits[0];rb=bounds(row)
    if row.get('offscreen') or rb[2]<=0 or rb[3]<=0:raise RuntimeError('대상 작업자가 화면 밖에 있습니다. 목록이 보이도록 한 뒤 다시 시험해 주세요.')
    mapped={}
    for title in ('선택','사용자ID','작업자'):
        hs=[h for h in headers if h.get('name')==title and bounds(h)[2]>0]
        if len(hs)!=1:raise RuntimeError('작업자 열을 구분하지 못했습니다: '+title)
        hb=bounds(hs[0])
        cs=[c for c in cells if not c.get('offscreen') and bounds(c)[3]>0 and abs(bounds(c)[0]-hb[0])<=3 and abs(bounds(c)[2]-hb[2])<=3]
        if len(cs)!=1:raise RuntimeError('작업자 선택 칸을 구분하지 못했습니다: '+title)
        mapped[title]=cs[0]
    if str(mapped['작업자'].get('value','')).strip()!=name:raise RuntimeError('작업자 이름과 열 위치가 일치하지 않습니다.')
    cell=mapped['선택'];cb=bounds(cell)
    if not cell.get('enabled') or not cell.get('state_known'):raise RuntimeError('선택 버튼 상태를 확인하지 못했습니다.')
    if not(tb[0]<=cb[0] and cb[0]+cb[2]<=tb[0]+tb[2] and tb[1]<=cb[1] and cb[1]+cb[3]<=tb[1]+tb[3]):raise RuntimeError('선택 칸이 완전히 보이지 않습니다.')
    return {'handle':table['handle'],'grid_bounds':tb,'cell_bounds':cb,'name':name,'user_id':mapped['사용자ID'].get('value','')}


def ensure_worker(target,name,capture,stop,emit):
    def pause(seconds):
        if stop.wait(seconds):raise Stopped('사용자 중지')
    api=WindowsClicks(target);api.activate();pause(.25)
    before=capture({**target,'mode':'mes_rows'},'작업자 변경 전',stop)
    old=field_node(before,'작업자',42).get('value','').strip()
    emit('log',f'현재 작업자: {old or "빈칸"} → 선택할 이름: {name}')
    if old==name:
        emit('log','작업자가 이미 '+name+'입니다. 선택창을 건너뜁니다.')
        return {'success':True,'before':old,'after':old,'selection_clicked':False,'report':before}
    previous=api.popup_inventory();button=worker_button(before)
    if stop.is_set():raise Stopped('사용자 중지')
    api.click_handle(button['handle']);emit('log','작업자 돋보기 클릭')
    popup=None
    for _ in range(30):
        pause(.1)
        matches=[w for w in visible_windows(True) if w['pid']==target['pid'] and w['handle'] not in previous and w['title'].strip()=='작업자']
        if len(matches)>1:raise RuntimeError('작업자 선택창이 여러 개입니다.')
        if matches:popup=matches[0];break
    if popup is None:raise RuntimeError('작업자 선택창을 확인하지 못했습니다. 창이 열린 상태로 화면을 확인해 주세요.')
    nested=WindowsClicks(popup);nested.activate();pause(.15)
    report=capture(popup,'작업자 선택 목록',stop);choice=worker_choice(report,name)
    emit('log',f"이름 일치: {name} / 사용자ID: {choice['user_id']}")
    if stop.is_set():raise Stopped('사용자 중지')
    nested.click_handle(choice['handle'],selection=(choice['grid_bounds'],choice['cell_bounds']))
    emit('log','해당 행의 초록색 선택 버튼 1회 클릭')
    for _ in range(30):
        pause(.1)
        if not nested.u.IsWindowVisible(popup['handle']):break
    else:
        capture(popup,'선택 클릭 후 창이 남아 있음',stop)
        raise RuntimeError('선택창이 닫히지 않아 멈췄습니다. 추가 클릭하지 않았습니다. 화면을 확인해 주세요.')
    after=capture({**target,'mode':'mes_rows'},'작업자 변경 후',stop)
    actual=field_node(after,'작업자',42).get('value','').strip()
    if actual!=name:raise RuntimeError(f'작업자 반영 불일치: 요청 [{name}] / 화면 [{actual}]')
    return {'success':True,'before':old,'requested':name,'after':actual,'user_id':choice['user_id'],
            'selection_clicked':True,'query_clicked':False,'completion_performed':False,'save_performed':False,'report':after}
