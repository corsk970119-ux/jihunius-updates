"""MES 호기 순회 테스트. 사용자가 지정한 숫자 버튼과 조회만 클릭합니다.
체크박스·저장·완료·값 입력 기능은 없습니다. Windows / Python 3.8+.
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
        if (count>=40000 || clock.Elapsed.TotalSeconds>=80) { limited=true; return true; }
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
    void Walk(IAccessible acc, int child, int parent, int depth, IntPtr hwnd) {
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
            row["name"]=Trim(Read(delegate {return acc.get_accName(child);}));
            // Row summaries contain many cells; keep them intact for fast value verification.
            row["value"]=Trim(Read(delegate {return acc.get_accValue(child);}), role==28 ? 65536 : 800);
            row["default_action"]=Trim(Read(delegate {return acc.get_accDefaultAction(child);}));
            if(role==24 || role==25 || role==28 || role==29 || role==37 || (role>=41 && role<=47)) {
                row["description"]=Trim(Read(delegate {return acc.get_accDescription(child);}));
                try {
                    int x,y,w,h;acc.accLocation(out x,out y,out w,out h,child);
                    row["bounds"]=new int[]{x,y,w,h};
                } catch {propertyErrors++;}
            }
            if(role>=41 && role<=47) {
                row["help"]=Trim(Read(delegate {return acc.get_accHelp(child);}));
                row["shortcut"]=Trim(Read(delegate {return acc.get_accKeyboardShortcut(child);}));
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
                if(objectChild!=null) {Walk(objectChild,0,id,depth+1,hwnd);continue;}
                if(item is int) {
                    int childId=(int)item;
                    if(childId<=0)continue;
                    IAccessible expanded=Read(delegate {return acc.get_accChild(childId);}) as IAccessible;
                    if(expanded!=null)Walk(expanded,0,id,depth+1,hwnd);
                    else Walk(acc,childId,id,depth+1,hwnd);
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


def visible_windows():
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
        if not length:
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
            deadline = time.monotonic()+95
            try:
                while process.poll() is None:
                    if stop.wait(.1) or time.monotonic() >= deadline:
                        report['interrupted'] = '사용자 중지' if stop.is_set() else '95초 제한 시간'
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
    text = ['MES 호기 순회 테스트의 화면 판독 결과', '호기 선택·조회 중 수집한 화면 정보 — 저장·완료 실행 없음', '',
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
        raise RuntimeError('화면을 충분히 읽지 못해 순회를 중단했습니다. 결과를 저장해 주세요.')


def number_groups(report):
    native = {r['handle']: r for r in report['records'] if r.get('kind') == 'native_window'}
    groups = defaultdict(dict)
    for r in nodes(report):
        if r.get('parent') != -1 or r.get('role') != 41 or r.get('name') not in {str(i) for i in range(1,11)}:
            continue
        if r.get('offscreen') or not r.get('enabled'):
            continue
        n = native.get(r['handle'], {})
        parent = n.get('native_parent')
        if parent:
            group = groups[parent]
            if r['name'] in group:
                group[r['name']] = None
            else:
                group[r['name']] = r
    result = []
    for parent, group in groups.items():
        if len(group) != 10 or any(v is None for v in group.values()):
            continue
        first = group['1']; bounds = first.get('bounds', [])
        panel = native.get(parent, {}).get('native_parent')
        if len(bounds) != 4 or bounds[2] <= 0 or bounds[3] <= 0 or not panel:
            continue
        result.append({'parent': parent, 'panel': panel,
                       'buttons': {i: group[str(i)]['handle'] for i in range(1,11)},
                       'x': bounds[0], 'y': bounds[1]})
    result.sort(key=lambda g: (g['y'], g['x']))
    for i, group in enumerate(result, 1):
        group['label'] = f"묶음 {i} — 1번 위치: 가로 {group['x']}, 세로 {group['y']}"
    if len(result)==6 and abs(result[0]['y']-result[2]['y'])<10 and abs(result[3]['y']-result[5]['y'])<10 and result[3]['y']-result[0]['y']>30:
        for group,label in zip(result,('위쪽 왼쪽','위쪽 가운데','위쪽 오른쪽','아래쪽 왼쪽','아래쪽 가운데','아래쪽 오른쪽')):
            group['label']=label+'의 1~10 버튼'
    return result


def panel_data(report):
    """MES only: require a matching header schema and corroborate visible cell names."""
    check_capture(report)
    elements = nodes(report); children = defaultdict(list)
    for r in elements:
        children[r['parent']].append(r)
    tables = []
    for table in elements:
        if table.get('role') != 24:
            continue
        headers = [h for group in children[table['id']] for h in children[group['id']] if h.get('role') == 25]
        names = [h.get('name','') for h in headers]
        if 'P/No.' not in names or '세척' not in names:
            continue
        if len(set(names)) != len(names):
            raise RuntimeError('중복된 열 이름 때문에 표를 구분할 수 없습니다.')
        rows = []
        for container in children[table['id']]:
            data_rows = [r for r in children[container['id']] if r.get('role') == 28]
            if (data_rows or container.get('name')=='데이터 패널') and len(data_rows) != container.get('child_count'):
                raise RuntimeError('일부 행이 누락되어 중단했습니다.')
            for row in data_rows:
                cells = [r for r in children[row['id']] if r.get('role') == 29]
                if len(cells) != len(headers) or len(cells) != row.get('child_count'):
                    raise RuntimeError('표의 열 개수가 맞지 않아 중단했습니다.')
                for header, cell in zip(headers, cells):
                    name = cell.get('name','')
                    if name and name.split(' row')[0] != header['name']:
                        raise RuntimeError('표의 열 순서가 달라 중단했습니다.')
                rows.append({name: cell.get('value','') for name,cell in zip(names,cells)})
        tables.append({'rows':rows, 'columns':names})
    if len(tables) != 1:
        raise RuntimeError(f'선택한 묶음에서 생산일보 표가 {len(tables)}개 발견되어 중단했습니다.')
    equipment = sorted({r.get('value','') for r in elements
                        if r.get('role') == 42 and re.fullmatch(r'M\d{4}',r.get('value',''))})
    equipment_names = sorted({r.get('value','') for r in elements
                              if r.get('role') == 42 and '호기' in r.get('value','')})
    dates = sorted({r.get('value','') for r in elements if r.get('role') == 47 and '년' in r.get('value','')})
    return {'equipment':equipment, 'equipment_names':equipment_names, 'dates':dates,
            'rows':tables[0]['rows']}


class Stopped(Exception):
    pass


def table_view(report):
    data=panel_data(report)
    children=defaultdict(list)
    for row in nodes(report):children[row['parent']].append(row)
    targets=[]
    for table in nodes(report):
        if table.get('role')!=24:continue
        headers=[h for group in children[table['id']] for h in children[group['id']] if h.get('role')==25]
        names=[h.get('name','') for h in headers]
        if 'P/No.' not in names or '세척' not in names:continue
        rows=[r for group in children[table['id']] for r in children[group['id']] if r.get('role')==28]
        targets.append((table,headers,rows))
    if len(targets)!=1:raise RuntimeError('스크롤할 표를 하나로 구분하지 못했습니다.')
    table,headers,rows=targets[0]
    bounds=table.get('bounds',[0,0,0,0])
    if bounds[2]<=0 or bounds[3]<=0:raise RuntimeError('표가 최소화되었거나 화면 위치를 읽지 못했습니다.')
    # Track actual row positions, independently of the displayed No. values.
    keys=[str(i) for i in range(1,len(rows)+1)]
    if len(rows)!=len(data['rows']):raise RuntimeError('표의 실제 행 개수가 일치하지 않습니다.')
    visible=[]
    header_bottom=max((h.get('bounds',[0,0,0,0])[1]+h.get('bounds',[0,0,0,0])[3] for h in headers),default=bounds[1])
    for key,row in zip(keys,rows):
        b=row.get('bounds',[0,0,0,0])
        # Count only fully shown rows, never a clipped last line.
        if (not row.get('offscreen') and b[2]>0 and b[3]>0 and b[1]>=header_bottom
                and b[1]+b[3]<=bounds[1]+bounds[3]):visible.append(key)
    summaries=[r.get('value') for r in rows]
    summary_supported=all(isinstance(value,str) and '[truncated]' not in value
                          and value==';'.join(record[h.get('name','')] for h in headers)+';'
                          for value,record in zip(summaries,data['rows']))
    return {'row_summaries':summaries,'summary_supported':summary_supported,'data':data,'handle':table['handle'],'keys':keys,'visible':visible,'row_names':[r.get('name','') for r in rows],'header_names':[h.get('name','') for h in headers]}


def row_geometry(report, expected_view):
    check_capture(report)
    children=defaultdict(list)
    for n in nodes(report):children[n['parent']].append(n)
    tables=[]
    for table in nodes(report):
        if table.get('role')!=24:continue
        headers=[h for g in children[table['id']] for h in children[g['id']] if h.get('role')==25]
        if [h.get('name','') for h in headers]!=expected_view['header_names']:continue
        rows=[r for g in children[table['id']] for r in children[g['id']] if r.get('role')==28]
        tables.append((table,headers,rows))
    if len(tables)!=1:raise RuntimeError('스크롤 중 표 구조를 확인하지 못했습니다.')
    table,headers,rows=tables[0];b=table.get('bounds',[0,0,0,0])
    if table['handle']!=expected_view['handle'] or len(rows)!=len(expected_view['keys']) or b[2]<=0 or b[3]<=0:
        raise RuntimeError('스크롤 중 표 또는 행 개수가 바뀌었습니다.')
    for container in children[table['id']]:
        if container.get('name')=='데이터 패널' and len([r for r in children[container['id']] if r.get('role')==28])!=container.get('child_count'):
            raise RuntimeError('MES 전체 행 수를 확인하지 못했습니다.')
    if expected_view.get('summary_supported') and [r.get('value') for r in rows]!=expected_view['row_summaries']:
        raise RuntimeError('MES 전체 행 재확인 중 값이 바뀌었습니다.')
    for field,role in (('dates',47),('equipment_names',42)):
        values=sorted({n.get('value','') for n in nodes(report) if n.get('role')==role and ('년' if role==47 else '호기') in n.get('value','')})
        if values!=expected_view['data'][field]:raise RuntimeError('MES 재확인 중 생산일 또는 설비 정보가 바뀌었습니다.')
    names=[r.get('name','') for r in rows]
    if names!=expected_view['row_names']:raise RuntimeError('스크롤 중 실제 행 구조가 바뀌었습니다.')
    header_bottom=max((h.get('bounds',[0,0,0,0])[1]+h.get('bounds',[0,0,0,0])[3] for h in headers),default=b[1])
    visible=[]
    for key,row in zip(expected_view['keys'],rows):
        rb=row.get('bounds',[0,0,0,0])
        if not row.get('offscreen') and rb[2]>0 and rb[3]>0 and rb[1]>=header_bottom and rb[1]+rb[3]<=b[1]+b[3]:visible.append(key)
    return {**expected_view,'visible':visible}


def collect_scrolled(target, initial, api, capture, stop, emit, number):
    """Require visible coverage of every declared row plus a stationary bottom page."""
    start=table_view(initial);expected=start['data'];all_keys=set(start['keys'])
    if start['summary_supported']:
        if stop.wait(.08):raise Stopped('사용자 중지')
        report=capture({**target,'mode':'mes_rows'},f'{number}번 전체 행 요약 대조',stop);emit('capture',report)
        row_geometry(report,start)
        emit('log',f'{number}호기 · {len(all_keys)}행 일괄 판독·대조 완료 · 전체 스크롤 생략')
        return {'method':'direct_rows','complete':True,'declared_rows':len(all_keys),'seen_rows':len(all_keys),
                'all_rows_verified':True,'snapshot_checks':2,'wheel_moves':0,'pages':[],
                'basis':'전체 셀 1회 판독 후 모든 행 요약값·행 개수·열 구조·생산일 재대조'}
    seen=set();pages=[];current=start;started=time.monotonic();moves=0
    def scroll(direction,phase):
        nonlocal moves
        if stop.is_set():raise Stopped('사용자 중지')
        if moves>=100 or time.monotonic()-started>180:
            raise RuntimeError('스크롤 검사 한도에 도달했습니다. 끝까지 확인되지 않아 중단했습니다.')
        api.scroll_grid(current['handle'],direction);moves+=1
        if stop.wait(.12):raise Stopped('사용자 중지')
        report=capture({**target,'mode':'mes_rows'},f'{number}번 {phase} {moves}',stop);emit('capture',report)
        view=row_geometry(report,start)
        if view['handle']!=start['handle'] or view['data']!=expected:
            raise RuntimeError('스크롤 중 표 내용 또는 행 개수가 바뀌어 중단했습니다.')
        pages.append({'phase':phase,'direction':direction,'visible_rows':view['visible']})
        emit('log',f"{number}번 · {phase} · 보이는 행 {','.join(view['visible']) or '없음'}")
        return view
    # The fresh initial capture already proves the top when row 1 is visible.
    unchanged=0
    while all_keys and '1' not in current['visible']:
        previous=current['visible'];current=scroll(1,'맨 위 확인')
        if not all_keys or '1' in current['visible']:break
        unchanged=unchanged+1 if current['visible']==previous else 0
        if unchanged>=2:raise RuntimeError('맨 위 행에 도달하지 못했습니다. 표 스크롤 동작을 확인해 주세요.')
    seen.update(current['visible']);unchanged=0
    while True:
        previous=current['visible'];current=scroll(-1,'아래로 확인');seen.update(current['visible'])
        if current['visible']==previous:
            unchanged+=1
            if seen==all_keys and (not all_keys or start['keys'][-1] in current['visible']):
                final_report=capture(target,f'{number}번 전체 값 최종 확인',stop);emit('capture',final_report)
                final_view=table_view(final_report)
                if final_view['handle']!=start['handle'] or final_view['data']!=expected or final_view['row_names']!=start['row_names']:
                    raise RuntimeError('스크롤 전후 표 내용이 달라 중단했습니다.')
                return {'complete':True,'declared_rows':len(all_keys),'seen_rows':len(seen),
                        'top_verified':True,'bottom_verified':True,'pages':pages,'wheel_moves':moves,
                        'basis':'표의 실제 행 위치 전체를 화면에서 확인하고 마지막 행에서 추가 스크롤 후 위치 유지 확인'}
            if unchanged>=2:
                missing=sorted(all_keys-seen,key=int)
                raise RuntimeError('스크롤이 진행되지 않거나 확인하지 못한 행이 있습니다: '+','.join(missing))
        else:unchanged=0


def cycle_steps(target, group, query_binding, api, capture, stop, emit, numbers=None):
    """Only two click purposes exist: a numbered selector, then the registered query."""
    numbers=list(range(1,11)) if numbers is None else list(numbers)
    if not numbers or any(type(n) is not int or not 1<=n<=10 for n in numbers) or numbers!=sorted(set(numbers)):
        raise ValueError('검사할 호기를 1개 이상 올바르게 선택해 주세요.')
    def pause(seconds):
        if stop.wait(seconds):
            raise Stopped('사용자 중지')
    focused = {'handle':group['panel'], 'pid':target['pid'], 'title':'MES 선택 묶음', 'mode':'mes_full'}
    previous = None
    if stop.is_set(): raise Stopped('사용자 중지')
    emit('log', '순회 시작 전 조회 1회 → 선택 호기 '+', '.join(map(str,numbers)))
    api.query_click(query_binding)
    emit('log','MES 조회 후 2초 대기합니다.')
    pause(2.0)
    for progress,number in enumerate(numbers,1):
        if stop.is_set(): raise Stopped('사용자 중지')
        emit('log', f'{progress}/{len(numbers)} · {number}호기 선택 → 전체 행 일괄 판독·대조')
        api.number_click(group, number)
        pause(.3)
        first = capture(focused, f'{number}번 선택 후 1차', stop)
        emit('capture',first)
        first_data = panel_data(first)
        coverage=collect_scrolled(focused,first,api,capture,stop,emit,number)
        second_data=first_data
        stable=True  # All values are corroborated by a second snapshot or the full scroll fallback.
        step = {'number':number, 'stable':stable, 'changed_from_previous':second_data != previous,
                'data':second_data, 'wash_1_count':sum(r.get('세척') in ('1','01') for r in second_data['rows']),
                'scroll_coverage':coverage,
                'refresh_confirmed':False,
                'note':'처음 조회 1회 후 번호 선택·전체 행 일괄 판독·요약값 대조. 요약 미지원 시 스크롤 대조. 서버 응답의 최신성은 별도 검증 대상입니다.'}
        emit('step',step)
        previous = second_data
    emit('log','선택 호기 순회 수집 완료. 실제 전환·갱신 여부는 저장한 결과로 대조합니다.')


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
        class Payload(ctypes.Union):
            _fields_=[('mi',Mouse)]
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
            raise RuntimeError('MES 창 또는 버튼 상태가 달라졌습니다. 최소화·팝업 상태를 확인해 주세요.')

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

    def click_handle(self, handle, static=False, selection=None):
        self.verify(handle);u=self.u;root=self.target['handle']
        if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped('F9 중지')
        if u.GetForegroundWindow()!=root:
            raise RuntimeError('MES 이외의 창이 앞에 있어 중단했습니다.')
        if any(u.GetAsyncKeyState(k)&0x8000 for k in (1,2,16,17,18,91,92)):
            raise RuntimeError('마우스 버튼 또는 보조 키가 눌려 있어 중단했습니다.')
        r=self.rect(handle);x=(r.left+r.right)//2;y=(r.top+r.bottom)//2
        if selection is not None:
            bx,by,bw,bh=selection
            if bw<=0 or bh<=0 or not(r.left<=bx and bx+bw<=r.right and r.top<=by and by+bh<=r.bottom):
                raise RuntimeError('MES 탭 위치가 현재 창 범위와 맞지 않습니다.')
            x=round(bx+bw/2);y=round(by+bh/2)
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

    def selected_number(self, group):
        # Read six background pixels inside each known number control, not its text.
        u=self.u
        if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped('F9 중지')
        if u.GetForegroundWindow()!=self.target['handle']:raise RuntimeError('MES 선택 번호 확인 중 다른 창이 앞에 있습니다.')
        g=ctypes.WinDLL('gdi32',use_last_error=True)
        u.GetDC.argtypes=[wintypes.HWND];u.GetDC.restype=wintypes.HDC
        u.ReleaseDC.argtypes=[wintypes.HWND,wintypes.HDC];u.ReleaseDC.restype=ctypes.c_int
        g.GetPixel.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int];g.GetPixel.restype=ctypes.c_uint32
        dc=u.GetDC(None)
        if not dc:raise RuntimeError('MES 선택 번호의 색상을 읽지 못했습니다.')
        selected=[]
        try:
            for number,handle in group['buttons'].items():
                self.verify(handle);r=self.rect(handle);hits=0
                for fx in (.18,.82):
                    for fy in (.25,.5,.75):
                        x=r.left+round((r.right-r.left-1)*fx);y=r.top+round((r.bottom-r.top-1)*fy)
                        if u.WindowFromPoint(wintypes.POINT(x,y)) not in (handle,u.GetParent(handle)):
                            raise RuntimeError('MES 숫자 버튼이 다른 화면에 가려져 있습니다.')
                        color=g.GetPixel(dc,x,y)
                        if color==0xffffffff:raise RuntimeError('MES 선택 번호의 색상을 읽지 못했습니다.')
                        red=color&255;green=(color>>8)&255;blue=(color>>16)&255
                        hits+=red>=190 and green>=190 and blue<=110 and min(red,green)-blue>=90
                if hits>=4:selected.append(number)
        finally:u.ReleaseDC(None,dc)
        if len(selected)!=1:raise RuntimeError('MES 왼쪽 위의 노란색 선택 번호를 하나로 확인하지 못했습니다.')
        return selected[0]

    def restore_number(self,group,number,stop):
        if stop.is_set():raise Stopped('사용자 중지')
        if self.selected_number(group)==number:return
        self.number_click(group,number)
        for _ in range(6):
            if stop.wait(.05):raise Stopped('사용자 중지')
            if self.selected_number(group)==number:return
        raise RuntimeError(f'MES 원래 선택 번호 {number}번 복귀를 확인하지 못했습니다.')

    def number_click(self, group, number):
        handle=group['buttons'][number]
        if self.u.GetParent(handle)!=group['parent'] or self.text(handle)!=str(number) or 'STATIC' not in self.text(handle,True):
            raise RuntimeError('숫자 버튼의 내용이 바뀌어 중단했습니다.')
        self.click_handle(handle,static=True)

    def query_click(self, binding):
        handle=binding['handle'];self.verify(handle);r=self.rect(handle)
        if (binding.get('purpose')!='query' or self.text(handle,True)!=binding['class']
                or self.text(handle)!=binding['text'] or [r.right-r.left,r.bottom-r.top]!=binding['size']):
            raise RuntimeError('등록한 조회 버튼이 바뀌어 중단했습니다.')
        self.click_handle(handle)

    def scroll_grid(self,handle,direction):
        if direction not in (-1,1):raise ValueError('스크롤 방향 오류')
        self.verify(handle);u=self.u
        if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped('F9 중지')
        if u.GetForegroundWindow()!=self.target['handle']:
            raise RuntimeError('MES 창이 앞에 있지 않아 스크롤을 중단했습니다.')
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


