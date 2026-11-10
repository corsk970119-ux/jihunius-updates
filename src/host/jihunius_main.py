#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""파일만 가져오기 / 리스트만 만들기 / 파일 + 리스트 만들기.

Windows / Python 3.8 이상. 추가 패키지 설치 없이 실행합니다.
지후니우스.pyw를 더블클릭하면 콘솔 창 없이 프로그램 화면만 열립니다.
기본 검색 기준: \\srvc5352374b\생산공유폴더\★NC프로그램파일
연도 입력칸에 2026처럼 입력하면 ★ 2026 폴더를 선택합니다. 기본값은 2026입니다.
7.1 또는 07.01, 10.12처럼 날짜 폴더를 지정합니다.
날짜의 월에 맞는 월 폴더를 자동 선택합니다. (예: ★ 2026/10월/10.13)
월·일의 앞자리 0은 생략할 수 있으며, 같은 날짜의 폴더 표기도 인식합니다.
지정한 날짜 폴더와 그 안의 하위폴더만 검색하며, 다른 날짜 폴더는 제외합니다.
기준 경로는 PC별로 설정합니다. 저장은 연결된 이동식 F:\를 우선 사용하고, 없으면 G:\를 사용합니다.
기본 모드는 '파일 + 리스트 만들기'입니다.
리스트 파일명은 O3999 / O3998 탭에서 선택하며, 기본값은 O3999입니다.
선택한 이름의 리스트만 갱신하고 다른 이름의 리스트 파일은 유지합니다.
파일을 가져오는 두 모드에서는 날짜 폴더와 번호를 입력합니다.
파일만 가져오기는 기존 수정 규칙을 적용한 복사본만 저장하고 리스트 파일은 변경하지 않습니다.
리스트만 만들기는 날짜 폴더나 공유폴더 검색 없이 입력한 번호로 선택한 리스트만 저장합니다.
파일 + 리스트 만들기는 수정본 복사와 선택한 리스트 생성을 함께 처리합니다.
'드라이브 비우기'를 누를 때만 화면에 표시된 저장 드라이브 내용을 삭제합니다.
왼쪽 목록에는 저장 드라이브 바로 안의 파일과 폴더를 표시하고 작업 후 자동 갱신합니다.
목록 항목을 더블클릭하면 폴더나 파일을 열고, .py/.pyw는 설치된 Python으로 실행합니다.
파일을 선택하고 F2 또는 우클릭의 이름 변경을 사용하면 드라이브 파일명을 바꿀 수 있습니다.
왼쪽 인수인계사항에서 생성 버튼으로 제목과 내용을 작성합니다.
기본 창 크기는 기존과 같으며 인수인계 버튼으로 왼쪽 목록을 펼치고 접습니다.
펼칠 때 왼쪽으로 늘어나며, 화면 가장자리에서는 목록이 잘리지 않도록 위치를 조정합니다.
접으면 원래 위치로 돌아옵니다.
인수인계가 있으면 접힌 상태에서도 버튼에 작은 표시와 건수가 나타납니다.
목록에는 제목만 표시하며, 제목을 누르면 내용을 확인·수정하고 오른쪽 ×로 삭제할 수 있습니다.
인수인계만 두 PC가 같은 공유폴더에서 읽고 씁니다. 다른 입력과 카드 작업은 각 PC에서 처리합니다.
저장 위치: \\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈\지후니우스_인수인계
기존 지후니우스_인수인계.db의 메모는 공유폴더로 한 번 옮기며 기존 DB는 변경하지 않습니다.
공유폴더 연결이 끊기면 마지막 목록을 유지하고 저장 실패를 안내합니다.
여러 번호를 한 줄 또는 여러 줄로 붙여 넣어도 됩니다.
리스트를 만드는 두 모드에서는 모든 입력 번호를 선택한 리스트에 입력 순서대로 포함합니다.
못 찾은 번호는 가져오기 완료 후 팝업 알람으로 안내합니다.
같은 번호를 반복 입력하면 리스트에서 반복 호출하며, 파일 가져오기는 한 번만 합니다.
파일 + 리스트 모드는 번호를 하나도 찾지 못해도 리스트를 생성합니다.
리스트를 만드는 두 모드에서 마지막 호출은 P9999M198입니다.

검색 폴더의 하위폴더를 재귀 검색하되 파일만 저장 폴더에 모읍니다.
원본 수정 스크립트의 변환 규칙과 알람 조건을 그대로 사용합니다.
알람 없는 파일은 O1234처럼 이름을 줄이고, 알람 파일은 원래 이름과 확장자를 유지합니다.
리스트 내부의 O3020도 기존 생성기와 같습니다.
가져오기 중 저장 드라이브의 다른 파일과 폴더는 유지합니다.
각 모드에서 저장 대상인 프로그램이나 선택한 리스트만 이번 결과로 갱신합니다.
별도 백업 파일이나 작업 기록 파일은 만들지 않습니다.
스크립트는 USB 밖의 PC 폴더에 두고 실행해야 합니다.
Windows가 관리하는 System Volume Information / $RECYCLE.BIN은 제외합니다.
카드 연결·새로고침 시 내장된 수정10.30.py를 없을 때 추가합니다.
새 스크립트 저장을 확인한 뒤 카드 바로 아래의 수정9.7 계열 .py/.pyw만 정리합니다.
드라이브 비우기에서는 수정10.30과 남아 있는 수정9.7 관련 항목을 보존합니다.
원본 파일의 내용과 이름을 변경하지 않으며 원본 파일과 폴더를 삭제하지 않습니다.
수정은 저장할 복사본에만 적용하고, 선택한 모드의 저장 결과를 검증합니다.
"""

import ctypes
from contextlib import contextmanager, redirect_stdout
from datetime import date, datetime, timezone
import errno
import hashlib
import http.client
from http.client import HTTPConnection
from ipaddress import IPv4Address
import json
import os
import queue
import re
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from urllib.parse import urlencode
from pathlib import Path

# Managed versions keep the original program folder for existing data and companions.
if __name__ == "__main__" and os.environ.get("JIHUNIUS_UPDATE_CHILD") == "1":
    __file__ = os.environ.get("JIHUNIUS_UPDATE_ORIGIN") or __file__
APP_DIR = Path(__file__).resolve().parent
# 이전 버전의 백업 폴더가 남아 있어도 검색 대상에 포함하지 않습니다.
LEGACY_BACKUP_DIR = APP_DIR / "_3999통합백업"
TARGET_GAP_LINES = 76
PROGRAM_YEAR = 2026
PROGRAM_BASE_ROOT = r"\\srvc5352374b\생산공유폴더\★NC프로그램파일"
LEGACY_PROGRAM_BASE_ROOT = r"\\192.168.0.254\내부공유폴더\★NC프로그램파일"
HANDOVER_SHARED_PARENT = r"\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈"
HANDOVER_FOLDER_NAME = "지후니우스_인수인계"
DESTINATION_CANDIDATES = ("F:/", "G:/")
LIST_NUMBERS = ("3999", "3998")
DEFAULT_LIST_NUMBER = "3999"
MODE_FILES = "files"
MODE_LIST = "list"
MODE_BOTH = "both"
MODE_LABELS = {
    MODE_FILES: "파일만 가져오기",
    MODE_LIST: "리스트만 만들기",
    MODE_BOTH: "파일 + 리스트 만들기",
}
MODE_DESCRIPTIONS = {
    MODE_FILES: "지정한 날짜 폴더에서 파일을 가져와 수정합니다. 기존 리스트 파일은 그대로 유지합니다.",
    MODE_LIST: "날짜 폴더 지정 없이 입력한 번호로 {list_name}만 만듭니다.",
    MODE_BOTH: "지정한 날짜 폴더에서 파일을 가져와 수정하고, 모든 입력 번호로 {list_name} 리스트를 만듭니다.",
}
SYSTEM_FOLDERS = {"system volume information", "$recycle.bin"}
CARD_MODIFIER_FILENAME = "수정10.30.py"
# 별도 보조 파일 없이 카드에 배치할 독립 실행 스크립트입니다. 실행하지 않고 복사만 합니다.
CARD_MODIFIER_BYTES = ...  # build: tools/build_app.py
PROTECTED_FILENAMES = {"수정9.7변경...py".casefold(), CARD_MODIFIER_FILENAME.casefold()}


def is_protected_drive_name(name):
    """Preserve both modifier utility families, including renamed/downloaded copies."""
    import unicodedata
    normalized = re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(name))).casefold()
    return re.match(r'^수정(?:9\.7|10\.30)(?![0-9])', normalized) is not None



MONITOR_HOST = "192.168.0.245"
MONITOR_INTERVAL = 3.0
MONITOR_TIMEOUT = 4.0
MONITOR_STALE_SECONDS = 8.0
MONITOR_GRACE_SECONDS = 20.0


_MONITOR_ALLOWED = {
    "monitoring_ajax_setting.php": "loadIPlist",
    "monitoring_ajax_this_machine.php": "callUpdateMachineOne",
}


def _monitor_exchange(connection, endpoint, fields):
    """요청 1회를 보내고 (결과, 연결 재사용 가능 여부)를 돌려줍니다."""
    if _MONITOR_ALLOWED.get(endpoint) != fields.get("ajax_selector"):
        raise ValueError("지원하지 않는 가공현황 조회입니다.")
    connection.request("POST", "/" + endpoint, body=urlencode(fields).encode("ascii"),
                       headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                                "Accept": "application/json", "Cache-Control": "no-cache"})
    response = connection.getresponse()
    if response.status != 200:
        raise ValueError("가공현황 서버 응답 오류 ({})".format(response.status))
    raw = response.read(131073)
    if len(raw) > 131072:
        raise ValueError("가공현황 응답이 너무 큽니다.")
    reusable = not response.will_close and response.isclosed()
    result = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(result, dict):
        raise ValueError("가공현황 응답 형식을 확인해 주세요.")
    return result, reusable


def monitor_request(endpoint, fields):
    """NC Gate의 기존 조회 요청만 사용합니다. 이미지나 설정 변경은 요청하지 않습니다."""
    if _MONITOR_ALLOWED.get(endpoint) != fields.get("ajax_selector"):
        raise ValueError("지원하지 않는 가공현황 조회입니다.")
    connection = HTTPConnection(MONITOR_HOST, timeout=MONITOR_TIMEOUT)
    try:
        return _monitor_exchange(connection, endpoint, fields)[0]
    finally:
        connection.close()


class MonitorClient:
    """호기별 조회 연결을 유지해 3초마다 새 TCP 연결을 맺지 않습니다.

    서버가 유지 연결을 지원하지 않거나(Connection: close) 끊으면 기존처럼 매번 새로 연결합니다.
    재사용하던 연결이 끊긴 경우에만 새 연결로 한 번 다시 조회하며, 시간 초과는 재시도하지 않습니다.
    """
    STALE = (ConnectionResetError, ConnectionAbortedError, BrokenPipeError,
             http.client.RemoteDisconnected, http.client.CannotSendRequest,
             http.client.ResponseNotReady, http.client.BadStatusLine)

    def __init__(self, factory=None):
        self.factory = factory or (lambda: HTTPConnection(MONITOR_HOST, timeout=MONITOR_TIMEOUT))
        self.connection = None

    def close(self):
        connection, self.connection = self.connection, None
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass

    def request(self, endpoint, fields):
        if _MONITOR_ALLOWED.get(endpoint) != fields.get("ajax_selector"):
            raise ValueError("지원하지 않는 가공현황 조회입니다.")
        reused = self.connection is not None
        if not reused:
            self.connection = self.factory()
        try:
            result, reusable = _monitor_exchange(self.connection, endpoint, fields)
        except self.STALE:
            self.close()
            if not reused:
                raise
            self.connection = self.factory()
            try:
                result, reusable = _monitor_exchange(self.connection, endpoint, fields)
            except BaseException:
                self.close()
                raise
        except BaseException:
            self.close()
            raise
        if not reusable:
            self.close()
        return result


def machine_state_light(state):
    return {'RUN': 'green', 'ALARM': 'red', 'WAIT': 'yellow', 'HOLD': 'yellow'}.get(state, 'gray')


def monitor_machine_record(result):
    if result.get("message") != "success":
        raise ValueError("머신에서 응답하지 않습니다.")
    match = re.fullmatch(r"machine\s*([0-9]+)", str(result.get("machine_name", "")).strip(), re.IGNORECASE)
    if match is None or not 1 <= int(match.group(1)) <= 9:
        return None
    raw_number = result.get("program_number")
    number = str(raw_number).strip() if isinstance(raw_number, (str, int)) and not isinstance(raw_number, bool) else ""
    if not re.fullmatch(r"[0-9]+", number):
        number = ""
    state = str(result.get("state", "")).strip().upper()
    if state not in ('RUN', 'ALARM', 'WAIT', 'HOLD', 'STOP', 'OFF'):
        raise ValueError("설비 상태 응답이 비어 있거나 올바르지 않습니다.")
    details = {}
    # Fields used by NC Gate's supplied list_machine.js; keep source units/values.
    for key in ("tool_number", "feed_RPM", "spindle_RPM", "part_count", "spindle_load_S1"):
        value = result.get(key)
        details[key] = str(value).strip()[:120] if isinstance(value, (str, int, float)) and not isinstance(value, bool) else ""
        if details[key].lower() in ("null", "undefined", "nan", "inf", "-inf"):
            details[key] = ""
    return {"machine": int(match.group(1)), "prm_no": number, "state": state,
            "details": details, "light": machine_state_light(state)}


MACHINE_ALERT_SETTINGS = Path(os.environ.get('LOCALAPPDATA') or Path.home()) / 'Jihunius' / 'machine_alerts.json'
MACHINE_ALERT_NUMBERS = tuple(range(1, 10))
# Antialiased switch artwork, embedded; no additional packages needed at runtime.
MACHINE_ALERT_SWITCH_PNGS = ...  # build: tools/build_app.py


def normalize_machine_alert_volume(value):
    try:
        return max(0, min(300, round(float(value))))
    except (TypeError, ValueError, OverflowError):
        return 50


def load_machine_alert_settings():
    try:
        data = json.loads(MACHINE_ALERT_SETTINGS.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or not isinstance(data.get('enabled'), bool):
            raise ValueError('알림 설정 형식')
        numbers = data.get('machines')
        if not isinstance(numbers, list) or any(type(n) is not int or n not in MACHINE_ALERT_NUMBERS for n in numbers):
            raise ValueError('호기 설정 형식')
        return data['enabled'], set(numbers), data.get('sound') is True, normalize_machine_alert_volume(data.get('volume', 50)), ('system' if data.get('sound_kind') == 'system' else 'tap')
    except (OSError, ValueError):
        return True, set(MACHINE_ALERT_NUMBERS), False, 50, 'tap'


def save_machine_alert_settings(enabled, numbers, sound=False, volume=50, sound_kind='tap'):
    path = MACHINE_ALERT_SETTINGS
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=str(path.parent),
                                         prefix='.alerts-', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump({'enabled': bool(enabled), 'machines': sorted(numbers), 'sound': bool(sound), 'volume': normalize_machine_alert_volume(volume), 'sound_kind': 'system' if sound_kind == 'system' else 'tap'}, stream, ensure_ascii=False)
        os.replace(str(temporary), str(path))
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


MACHINE_ALERT_SOUND_WAV = ...  # build: tools/build_app.py


def machine_alert_sound_bytes(volume):
    import base64
    import io
    import struct
    import wave
    volume = normalize_machine_alert_volume(volume)
    with wave.open(io.BytesIO(base64.b64decode(MACHINE_ALERT_SOUND_WAV)), 'rb') as source:
        params = source.getparams()
        frames = source.readframes(source.getnframes())
    samples = struct.unpack('<{}h'.format(len(frames) // 2), frames)
    scaled = [max(-32768, min(32767, round(sample * volume / 50))) for sample in samples]
    result = io.BytesIO()
    with wave.open(result, 'wb') as target:
        target.setparams(params)
        target.writeframes(struct.pack('<{}h'.format(len(scaled)), *scaled))
    return result.getvalue()


def play_machine_alert_sound(volume=50, sound_kind='tap'):
    if os.name != 'nt':return
    import winsound
    volume = normalize_machine_alert_volume(volume)
    if sound_kind == 'system':
        winsound.PlaySound('SystemNotification', winsound.SND_ALIAS | winsound.SND_ASYNC)
        return
    if volume == 0:return
    path = MACHINE_ALERT_SETTINGS.with_name('machine_alert_soft_tap_v3_{}.wav'.format(volume))
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='wb', dir=str(path.parent), prefix='.chime-', suffix='.tmp', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(machine_alert_sound_bytes(volume))
            os.replace(str(temporary), str(path))
        finally:
            if temporary is not None and temporary.exists():temporary.unlink()
    # Embedded custom chime; do not fall back to a Windows system sound.
    winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)


class MachineAlertTracker:
    """Keep a short gap from erasing a real transition; missing data never means completion."""
    def __init__(self):
        self.previous = {}
        self.last_seen = {}
        self.sources = {}

    def observe(self, machines, enabled, selected):
        events = []
        now = time.monotonic()
        for number in MACHINE_ALERT_NUMBERS:
            record = machines.get(number)
            if record and record.get("_stale"):
                record = None
            if not record:
                if now - self.last_seen.get(number, now) > 30:
                    self.previous.pop(number, None)
                    self.last_seen.pop(number, None)
                    self.sources.pop(number, None)
                continue
            program = str(record.get('prm_no', ''))
            if not re.fullmatch(r'[0-9]+', program):
                program = ''
            state = record.get('state', '')
            light = machine_state_light(state) if state in ('RUN', 'ALARM', 'WAIT', 'HOLD', 'STOP', 'OFF') else None
            old = self.previous.get(number)
            source = record.get("_source_ip")
            if self.sources.get(number) != source:old = None
            if now - self.last_seen.get(number, now) > 30:old = None
            if not program and light is None:continue
            self.previous[number] = (program or (old[0] if old else ''), light if light is not None else (old[1] if old else None))
            self.last_seen[number] = record.get("_observed_at", now)
            self.sources[number] = source
            if old is None:
                continue
            completed = old[1] == 'green' and light in ('red', 'yellow', 'gray')
            if completed:
                event = {'machine': number, 'completed': completed, 'light': light,
                               'before': '', 'program': program,
                               'state': state, 'time': datetime.now().strftime('%H:%M:%S'), 'count': 1}
                if enabled and number in selected:events.append(event)
        return events


def machine_alert_palette(event):
    color = event.get('light', machine_state_light(event['state'])) if event['completed'] else 'green'
    return {'green': ('#246b48', '#ffffff'), 'red': ('#963e49', '#ffffff'),
            'yellow': ('#d8b54a', '#201b0b'), 'gray': ('#34486a', '#ffffff')}.get(color, ('#34486a', '#ffffff'))


def machine_alert_text(event):
    title = '{}호기 {}'.format(event['machine'], '완료' if event['completed'] else '프로그램 변경')
    body = '{} → {}'.format(event['before'], event['program']) if event['before'] else '프로그램 {}'.format(event['program'] or '미확인')
    state = {'ALARM': '알람', 'WAIT': '대기', 'HOLD': '일시 정지', 'STOP': '정지', 'OFF': '꺼짐', 'RUN': '가공 중'}.get(event['state'], '상태 미확인')
    body += ' · ' + state + ' · ' + event['time']
    if event['count'] > 1:
        body += ' (변경 {}건 묶음)'.format(event['count'])
    return title, body


def primary_monitor_work_area(window):
    if os.name != 'nt':
        return 0, 0, window.winfo_screenwidth(), window.winfo_screenheight()
    from ctypes import wintypes
    class MonitorInfo(ctypes.Structure):
        _fields_ = [('size', wintypes.DWORD), ('monitor', wintypes.RECT),
                    ('work', wintypes.RECT), ('flags', wintypes.DWORD)]
    user = ctypes.WinDLL('user32', use_last_error=True)
    user.MonitorFromPoint.argtypes = [wintypes.POINT, wintypes.DWORD]
    user.MonitorFromPoint.restype = wintypes.HANDLE
    user.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MonitorInfo)]
    user.GetMonitorInfoW.restype = wintypes.BOOL
    info = MonitorInfo(); info.size = ctypes.sizeof(info)
    monitor = user.MonitorFromPoint(wintypes.POINT(0, 0), 1)
    if not monitor or not user.GetMonitorInfoW(monitor, ctypes.byref(info)) or not info.flags & 1:
        raise OSError('주모니터 작업 영역을 확인하지 못했습니다.')
    r = info.work
    return r.left, r.top, r.right, r.bottom


def show_machine_toast_noactivate(dialog, x, y, width, height):
    """Set no-activate before mapping; position on the primary monitor in Win32 coordinates."""
    dialog.geometry('{}x{}+{}+{}'.format(width, height, max(0, x), max(0, y)))
    dialog.update_idletasks()
    if os.name != 'nt':
        dialog.attributes('-topmost', True)
        dialog.deiconify()
        return
    from ctypes import wintypes
    user = ctypes.WinDLL('user32', use_last_error=True)
    user.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]; user.GetAncestor.restype = wintypes.HWND
    hwnd = user.GetAncestor(dialog.winfo_id(), 2)
    if not hwnd:
        raise OSError('알림 창을 확인하지 못했습니다.')
    getter = user.GetWindowLongPtrW if ctypes.sizeof(ctypes.c_void_p) == 8 else user.GetWindowLongW
    setter = user.SetWindowLongPtrW if ctypes.sizeof(ctypes.c_void_p) == 8 else user.SetWindowLongW
    getter.argtypes = [wintypes.HWND, ctypes.c_int]; getter.restype = ctypes.c_ssize_t
    setter.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]; setter.restype = ctypes.c_ssize_t
    flags = (getter(hwnd, -20) | 0x08000000 | 0x80) & ~0x40000  # NOACTIVATE, TOOLWINDOW
    ctypes.set_last_error(0)
    if not setter(hwnd, -20, flags) and ctypes.get_last_error():
        raise ctypes.WinError(ctypes.get_last_error())
    user.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, wintypes.UINT]
    user.SetWindowPos.restype = wintypes.BOOL
    dialog.deiconify()
    dialog.update_idletasks()
    user.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]; user.ShowWindow.restype = wintypes.BOOL
    user.ShowWindow(hwnd, 4)  # SW_SHOWNOACTIVATE, including when the main window is minimized.
    if not user.SetWindowPos(hwnd, -1, x, y, width, height, 0x10 | 0x20 | 0x40):
        raise ctypes.WinError(ctypes.get_last_error())
    user.IsWindowVisible.argtypes = [wintypes.HWND]; user.IsWindowVisible.restype = wintypes.BOOL
    if not user.IsWindowVisible(hwnd):raise OSError('알림 창이 표시되지 않았습니다.')


class MachineMonitor:
    """머신별 독립 조회로 느린 한 대가 다른 머신이나 파일 작업을 막지 않습니다."""
    def __init__(self, events, request=None):
        self.events = events
        self.request = request or monitor_request
        self.stopped = threading.Event()
        self.workers = {}

    def start(self):
        threading.Thread(target=self._discover, daemon=True).start()

    def stop(self):
        self.stopped.set()

    def _discover(self):
        while not self.stopped.is_set():
            delay = MONITOR_INTERVAL
            try:
                result = self.request("monitoring_ajax_setting.php", {"ajax_selector": "loadIPlist"})
                values = result.get("ip")
                if not isinstance(values, list) or len(values) > 64:
                    raise ValueError("머신 목록 응답 형식을 확인해 주세요.")
                addresses = set()
                for value in values:
                    if not isinstance(value, str):
                        raise ValueError("머신 주소 형식을 확인해 주세요.")
                    addresses.add(str(IPv4Address(value.strip())))
                for ip in list(self.workers):
                    cancel, thread = self.workers[ip]
                    if ip not in addresses:
                        cancel.set()
                        del self.workers[ip]
                        self.events.put(("machine_sample", ip, None, time.monotonic(), None))
                for ip in sorted(addresses):
                    if self.stopped.is_set():
                        break
                    if ip not in self.workers:
                        cancel = threading.Event()
                        thread = threading.Thread(target=self._poll_one, args=(ip, cancel), daemon=True)
                        self.workers[ip] = (cancel, thread)
                        thread.start()
                self.events.put(("machine_connection", None))
                delay = 30.0
            except Exception as error:
                if not self.stopped.is_set():
                    self.events.put(("machine_connection", str(error)))
            self.stopped.wait(delay)
        for cancel, thread in self.workers.values():
            cancel.set()

    def _poll_one(self, ip, cancel):
        client = MonitorClient() if self.request is monitor_request else None
        request = client.request if client is not None else self.request
        try:
            while not self.stopped.is_set() and not cancel.is_set():
                record = None
                try:
                    result = request("monitoring_ajax_this_machine.php",
                                     {"ajax_selector": "callUpdateMachineOne", "ncgateIP": ip})
                    record = monitor_machine_record(result)
                except Exception:
                    pass
                if self.stopped.is_set() or cancel.is_set():
                    return
                self.events.put(("machine_sample", ip, record, time.monotonic(), cancel))
                if self.stopped.wait(MONITOR_INTERVAL):
                    return
        finally:
            if client is not None:
                client.close()

# 첨부 로고를 내장합니다. 외부 이미지 파일이나 추가 패키지는 필요하지 않습니다.
APP_USER_MODEL_ID = "Jihunius.NCProgramManager"
APP_ICON_PNGS = ...  # build: tools/build_app.py

PI_VALUE_MAP_A12 = {
    "9.7": "-1.0", "9.8": "-1.0", "9.9": "-1.0", "10.0": "-1.0",
    "10.1": "-1.0", "10.2": "-1.0", "10.3": "-1.0", "10.4": "-1.0",
    "10.5": "-1.0", "10.6": "-1.0", "10.7": "-1.0", "10.8": "-1.0",
    "10.9": "-0.9", "11.0": "-0.8", "11.1": "-0.7", "11.2": "-0.6",
    "11.3": "-0.5", "11.4": "-0.4", "11.5": "-0.3", "11.6": "-0.3",
    "11.7": "-0.3",
}
PI_VALUE_MAP_A14 = {
    "11.8": "-1.0", "11.9": "-1.0", "12.0": "-1.0", "12.1": "-1.0",
    "12.2": "-1.0", "12.3": "-1.0", "12.4": "-1.0", "12.5": "-1.0",
    "12.6": "-1.0", "12.7": "-1.0", "12.8": "-1.0",
    "12.9": "-0.9", "13.0": "-0.8", "13.1": "-0.7", "13.2": "-0.6",
    "13.3": "-0.5", "13.4": "-0.4", "13.5": "-0.3", "13.6": "-0.3",
    "13.7": "-0.3",
}


class WorkError(Exception):
    pass


class LegacyHandoverStore:
    """카드의 NC 자료와 별도로 인수인계 내용만 보관합니다."""
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else APP_DIR / "지후니우스_인수인계.db"

    @contextmanager
    def connection(self, write=False):
        connection = None
        try:
            if write:
                connection = sqlite3.connect(str(self.path), timeout=3)
            else:
                connection = sqlite3.connect(self.path.resolve().as_uri() + "?mode=ro", uri=True, timeout=3)
            connection.row_factory = sqlite3.Row
            with connection:
                if write:
                    connection.execute("BEGIN IMMEDIATE")
                    connection.execute("""CREATE TABLE IF NOT EXISTS handovers (
                        id TEXT PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL,
                        created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
                yield connection
        except (sqlite3.Error, OSError, ValueError) as error:
            verb = "저장" if write else "읽기"
            raise WorkError("인수인계사항 {}에 실패했습니다.\n{}\n{}".format(verb, self.path, error)) from error
        finally:
            if connection is not None:
                connection.close()

    def load(self):
        try:
            self.path.stat()
        except FileNotFoundError:
            return []
        except OSError as error:
            raise WorkError("인수인계사항을 읽지 못했습니다.\n{}\n{}".format(self.path, error)) from error
        with self.connection() as connection:
            rows = connection.execute("""SELECT id, title, content, created_at, updated_at
                FROM handovers ORDER BY created_at DESC, rowid DESC""").fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def validate(title, content):
        title = title.strip()
        if not title:
            raise WorkError("제목을 입력해 주세요.")
        if "\n" in title or "\r" in title:
            raise WorkError("제목은 한 줄로 입력해 주세요.")
        if not content.strip():
            raise WorkError("내용을 입력해 주세요.")
        return title, content

    def add(self, title, content):
        title, content = self.validate(title, content)
        now = datetime.now().astimezone().isoformat(timespec="microseconds")
        note = {"id": uuid.uuid4().hex, "title": title, "content": content,
                "created_at": now, "updated_at": now}
        with self.connection(write=True) as connection:
            connection.execute("INSERT INTO handovers VALUES (:id, :title, :content, :created_at, :updated_at)", note)
        return note

    def update(self, note, title, content):
        title, content = self.validate(title, content)
        updated = dict(note, title=title, content=content,
                       updated_at=datetime.now().astimezone().isoformat(timespec="microseconds"))
        with self.connection(write=True) as connection:
            cursor = connection.execute("""UPDATE handovers SET title=?, content=?, updated_at=?
                WHERE id=? AND title=? AND content=? AND updated_at=?""",
                (title, content, updated["updated_at"], note["id"], note["title"], note["content"], note["updated_at"]))
            if cursor.rowcount != 1:
                raise WorkError("다른 창에서 이 인수인계사항을 변경하거나 삭제했습니다.\n목록에서 다시 열어 주세요.")
        return updated

    def delete(self, note):
        with self.connection(write=True) as connection:
            cursor = connection.execute("""DELETE FROM handovers
                WHERE id=? AND title=? AND content=? AND updated_at=?""",
                (note["id"], note["title"], note["content"], note["updated_at"]))
            if cursor.rowcount != 1:
                raise WorkError("다른 창에서 이 인수인계사항을 변경하거나 삭제했습니다.\n목록을 다시 확인해 주세요.")


class HandoverStore:
    """메모별 파일과 OS의 배타적 잠금으로 공유폴더의 두 PC가 함께 사용합니다."""
    LOCK_TIMEOUT = 4.0

    def __init__(self, path=None, legacy_path=None):
        self.path = Path(path) if path is not None else Path(HANDOVER_SHARED_PARENT) / HANDOVER_FOLDER_NAME
        self.legacy_path = (Path(legacy_path) if legacy_path is not None else
                            APP_DIR / "지후니우스_인수인계.db" if path is None else None)
        self._migration_lock = threading.Lock()
        self._migrated = False

    validate = staticmethod(LegacyHandoverStore.validate)

    @contextmanager
    def _errors(self, operation):
        try:
            yield
        except (OSError, ValueError, UnicodeError) as error:
            raise WorkError("인수인계 공유 {}에 실패했습니다.\n{}\n{}\n"
                            "공유폴더 연결과 읽기·쓰기 권한을 확인해 주세요.".format(
                                operation, self.path, error)) from error

    def _folder(self, create=False):
        import stat
        # is_dir()는 일부 Windows 연결 오류를 False로 숨기므로 직접 확인합니다.
        if not stat.S_ISDIR(self.path.parent.stat().st_mode):
            raise WorkError("인수인계 공유폴더에 연결할 수 없습니다.\n{}".format(self.path.parent))
        if create:
            self.path.mkdir(exist_ok=True)
        try:
            info = self.path.stat()
        except FileNotFoundError as error:
            # WinError 53/64 등도 FileNotFoundError가 될 수 있습니다. 2/3도
            # 상위 폴더를 실제로 열어 해당 이름이 없을 때에만 새 폴더로 봅니다.
            if (getattr(error, "winerror", None) not in (None, 2, 3)
                    or error.errno != errno.ENOENT):
                raise
            with os.scandir(self.path.parent) as entries:
                if any(entry.name.casefold() == self.path.name.casefold() for entry in entries):
                    raise
            return False
        if not stat.S_ISDIR(info.st_mode):
            raise WorkError("인수인계 저장 위치가 폴더가 아닙니다: {}".format(self.path))
        return True

    @staticmethod
    def _note_id(value):
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{32}", value):
            raise WorkError("인수인계 항목의 식별 정보가 올바르지 않습니다.")
        return value

    @contextmanager
    def _record_lock(self, note_id):
        self._note_id(note_id)
        self._folder(create=True)
        locks = self.path / ".locks"
        locks.mkdir(exist_ok=True)
        lock_path = locks / (note_id + ".lock")
        deadline = time.monotonic() + self.LOCK_TIMEOUT
        if os.name == "nt":
            from ctypes import wintypes
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            create = kernel.CreateFileW
            create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                               wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
            create.restype = wintypes.HANDLE
            close = kernel.CloseHandle
            close.argtypes = [wintypes.HANDLE]
            close.restype = wintypes.BOOL
            invalid = ctypes.c_void_p(-1).value
            while True:
                # OPEN_ALWAYS + 공유 금지: SMB 서버에서도 같은 메모의 쓰기를 직렬화합니다.
                handle = create(str(lock_path), 0xC0000000, 0, None, 4, 0x80, None)
                if handle != invalid:
                    break
                code = ctypes.get_last_error()
                if code not in (32, 33):
                    raise ctypes.WinError(code)
                if time.monotonic() >= deadline:
                    raise WorkError("다른 PC에서 이 인수인계사항을 저장 중입니다. 잠시 뒤 다시 시도해 주세요.")
                time.sleep(0.05)
            try:
                yield
            finally:
                close(handle)
        else:
            # 비 Windows 검증 환경에서도 프로세스 사이의 실제 파일 잠금을 사용합니다.
            import fcntl
            with lock_path.open("a+b") as stream:
                while True:
                    try:
                        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except OSError as error:
                        if error.errno not in (errno.EAGAIN, errno.EACCES):
                            raise
                        if time.monotonic() >= deadline:
                            raise WorkError("다른 PC에서 이 인수인계사항을 저장 중입니다. 잠시 뒤 다시 시도해 주세요.")
                        time.sleep(0.05)
                try:
                    yield
                finally:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def _read_record(self, path):
        note = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(note, dict) or note.get("version") != 1:
            raise WorkError("읽을 수 없는 인수인계 파일입니다: {}".format(path))
        self._note_id(note.get("id"))
        if path.stem != note["id"] or not isinstance(note.get("revision"), str):
            raise WorkError("인수인계 파일 정보가 일치하지 않습니다: {}".format(path))
        if not isinstance(note.get("deleted"), bool):
            raise WorkError("인수인계 파일의 삭제 정보가 올바르지 않습니다: {}".format(path))
        if not note["deleted"]:
            if not all(isinstance(note.get(key), str) for key in ("title", "content", "created_at", "updated_at")):
                raise WorkError("인수인계 제목이나 내용이 올바르지 않습니다: {}".format(path))
            self.validate(note["title"], note["content"])
            datetime.fromisoformat(note["created_at"])
            datetime.fromisoformat(note["updated_at"])
        return note

    def _write_record(self, note):
        target = self.path / (self._note_id(note["id"]) + ".json")
        fd, name = tempfile.mkstemp(prefix="." + note["id"] + "_", suffix=".tmp", dir=str(self.path))
        temp = Path(name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(note, stream, ensure_ascii=False, separators=(",", ":"))
                stream.flush()
                os.fsync(stream.fileno())
            deadline = time.monotonic() + self.LOCK_TIMEOUT
            while True:
                try:
                    os.replace(str(temp), str(target))
                    break
                except OSError as error:
                    if getattr(error, "winerror", None) not in (32, 33) or time.monotonic() >= deadline:
                        raise
                    time.sleep(0.05)
        finally:
            try:
                temp.unlink()
            except OSError:
                pass

    def _migrate_legacy(self):
        with self._migration_lock:
            if self._migrated:
                return
            if self.legacy_path is not None:
                # 예전 DB는 읽기만 하고 메모 ID를 유지합니다. 다시 실행해도 중복 생성하지 않습니다.
                for old in LegacyHandoverStore(self.legacy_path).load():
                    note_id = self._note_id(old["id"])
                    with self._record_lock(note_id):
                        target = self.path / (note_id + ".json")
                        if not target.exists():
                            self._write_record(dict(old, version=1, revision=uuid.uuid4().hex, deleted=False))
                        else:
                            self._read_record(target)
            self._migrated = True

    def load(self):
        with self._errors("불러오기"):
            self._folder()
            self._migrate_legacy()
            if not self._folder():
                return []
            notes = []
            with os.scandir(self.path) as entries:
                paths = [self.path / entry.name for entry in entries
                         if re.fullmatch(r"[0-9a-f]{32}\.json", entry.name)]
            for path in paths:
                note = self._read_record(path)
                if not note["deleted"]:
                    notes.append(note)
            return sorted(notes, key=lambda note: (datetime.fromisoformat(note["created_at"]).timestamp(), note["id"]),
                          reverse=True)

    def add(self, title, content, note_id=None):
        title, content = self.validate(title, content)
        with self._errors("저장"):
            self._folder()
            self._migrate_legacy()
            now = datetime.now(timezone.utc).isoformat(timespec="microseconds")
            note = {"version": 1, "id": self._note_id(note_id or uuid.uuid4().hex),
                    "revision": uuid.uuid4().hex, "deleted": False,
                    "title": title, "content": content, "created_at": now, "updated_at": now}
            with self._record_lock(note["id"]):
                if (self.path / (note["id"] + ".json")).exists():
                    existing = self._read_record(self.path / (note["id"] + ".json"))
                    if not existing["deleted"] and existing["title"] == title and existing["content"] == content:
                        return existing
                    raise WorkError("이 작성 요청은 이미 저장되거나 변경되었습니다. 목록을 다시 확인해 주세요.")
                self._write_record(note)
            return note

    def _current_for_change(self, note):
        target = self.path / (self._note_id(note.get("id")) + ".json")
        try:
            current = self._read_record(target)
        except FileNotFoundError:
            raise WorkError("다른 PC에서 이 인수인계사항을 삭제했습니다. 목록을 다시 확인해 주세요.")
        if current["deleted"] or current["revision"] != note.get("revision"):
            raise WorkError("다른 PC에서 이 인수인계사항을 변경하거나 삭제했습니다.\n목록에서 다시 열어 주세요.")
        return current

    def update(self, note, title, content):
        title, content = self.validate(title, content)
        with self._errors("수정"):
            with self._record_lock(note.get("id")):
                current = self._current_for_change(note)
                updated = dict(current, title=title, content=content, revision=uuid.uuid4().hex,
                               updated_at=datetime.now(timezone.utc).isoformat(timespec="microseconds"))
                self._write_record(updated)
            return updated

    def delete(self, note):
        with self._errors("삭제"):
            with self._record_lock(note.get("id")):
                current = self._current_for_change(note)
                # 내용은 지우고 ID만 남겨 예전 로컬 DB의 메모가 재실행 시 되살아나지 않게 합니다.
                self._write_record({"version": 1, "id": current["id"], "revision": uuid.uuid4().hex, "deleted": True})


def contained(path, parent):
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def is_link(path):
    # 심볼릭 링크 / Windows junction을 따라 다른 폴더를 처리하지 않습니다.
    if path.is_symlink():
        return True
    if getattr(path, "is_junction", lambda: False)():
        return True
    if os.name == "nt":
        attrs = getattr(path.lstat(), "st_file_attributes", 0)
        return bool(attrs & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT
    return False


def validate_destination_path(destination):
    destination = Path(destination).expanduser().resolve()
    if not destination.is_dir():
        raise WorkError("저장 폴더를 찾을 수 없습니다: {}".format(destination))
    if contained(destination, LEGACY_BACKUP_DIR):
        raise WorkError("백업 폴더를 저장 폴더로 사용할 수 없습니다.")
    return destination


def validate_paths(roots, destination):
    if not roots:
        raise WorkError("검색 폴더를 하나 이상 등록해 주세요.")
    roots = [Path(root).expanduser() for root in roots]
    for root in roots:
        if not root.is_dir():
            raise WorkError("검색 폴더를 찾을 수 없습니다: {}".format(root))
        if is_link(root):
            raise WorkError("검색 폴더가 링크입니다: {}".format(root))
    roots = [root.resolve() for root in roots]
    destination = validate_destination_path(destination)
    for root in roots:
        if not root.is_dir():
            raise WorkError("검색 폴더를 찾을 수 없습니다: {}".format(root))
        if contained(destination, root) or contained(root, destination):
            raise WorkError("검색 폴더와 저장 폴더는 서로 다른 위치로 지정해 주세요.\n"
                            "한쪽이 다른 쪽의 하위폴더여도 사용할 수 없습니다.")
    if any(contained(root, LEGACY_BACKUP_DIR) for root in roots):
        raise WorkError("백업 폴더를 검색 폴더로 사용할 수 없습니다.")
    return list(dict.fromkeys(roots)), destination


def get_drive_type(destination):
    if os.name != "nt":
        raise WorkError("이 프로그램은 Windows에서 실행해 주세요.")
    return ctypes.windll.kernel32.GetDriveTypeW(str(destination))


def select_destination():
    for candidate in DESTINATION_CANDIDATES:
        destination = Path(candidate)
        # Reject missing/fixed/network roots before resolve/is_dir can wait on
        # their filesystem. Retain the final removable check for the chosen card.
        if get_drive_type(destination) != 2:
            continue
        destination = destination.resolve()
        if destination.is_dir() and get_drive_type(destination) == 2:
            return destination
    raise WorkError("F:\\ 또는 G:\\에 이동식 드라이브를 연결해 주세요.")


def validate_fixed_destination(destination):
    if os.name != "nt":
        raise WorkError("이 프로그램은 Windows에서 실행해 주세요.")
    if not any(destination.resolve() == Path(candidate).resolve() for candidate in DESTINATION_CANDIDATES):
        raise WorkError("저장 위치는 등록된 F:\\ 또는 G:\\ 드라이브만 사용할 수 있습니다.")
    if destination.drive.casefold() == os.environ.get("SystemDrive", "C:").casefold():
        raise WorkError("Windows가 설치된 드라이브는 비울 수 없습니다.")
    if get_drive_type(destination) != 2:
        raise WorkError("{}에 연결된 이동식 드라이브를 확인해 주세요.".format(destination))
    if contained(APP_DIR, destination):
        raise WorkError("스크립트를 USB 밖의 PC 폴더로 옮긴 뒤 실행해 주세요.")


def atomic_write(path, data):
    fd, temp_name = tempfile.mkstemp(prefix=".3999통합_", suffix=".tmp", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temp_path), str(path))
    finally:
        if temp_path.exists():
            temp_path.unlink()


def is_legacy_card_modifier_name(name):
    """자동 교체는 카드 바로 아래의 수정9.7 Python 파일에만 적용합니다."""
    import unicodedata
    normalized = re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(name))).casefold()
    return (re.match(r'^수정9\.7(?![0-9])', normalized) is not None
            and Path(str(name)).suffix.casefold() in {'.py', '.pyw'})


def card_modifier_volume_id(destination):
    """드라이브 문자가 같아도 카드가 바뀌면 별도로 처리합니다."""
    if os.name == 'nt':
        serial = ctypes.c_ulong()
        if not ctypes.windll.kernel32.GetVolumeInformationW(
                str(destination), None, 0, ctypes.byref(serial), None, None, None, 0):
            raise WorkError('카드 정보를 읽지 못했습니다. 다시 연결한 뒤 새로고침해 주세요.')
        return (str(destination).casefold(), serial.value)
    info = destination.stat()
    return (str(destination), info.st_dev, info.st_ino)


def card_modifier_file_stamp(path):
    info = path.lstat()
    return (info.st_mode, info.st_size, info.st_mtime_ns, info.st_ino,
            getattr(info, 'st_file_attributes', 0), info.st_ctime_ns)


def card_modifier_signature(destination, names=None):
    """변경 감지에는 관련 파일의 이름·속성만 읽고 내용은 읽지 않습니다."""
    destination = Path(destination)
    volume_id = card_modifier_volume_id(destination)
    if names is None:
        with os.scandir(destination) as scan:
            names = [entry.name for entry in scan]
    entries = [(name, card_modifier_file_stamp(destination / name)) for name in names
               if name.casefold() == CARD_MODIFIER_FILENAME.casefold() or is_legacy_card_modifier_name(name)]
    return (volume_id, tuple(sorted(entries)))


def read_drive_snapshot(on_listing=None):
    """Read-only USB probes; called by the single refresh worker, never by Tk."""
    try:
        destination = select_destination()
    except WorkError:
        destination = None
    snapshot = {"destination": destination, "labels": [], "paths": [],
                "status": "드라이브 연결 대기", "modifier_signature": None,
                "modifier_error": None}
    if destination is None:
        return snapshot
    try:
        with os.scandir(destination) as entries:
            items = [(entry.name, entry.is_dir(follow_symlinks=False), entry.is_symlink())
                     for entry in entries]
        items.sort(key=lambda item: (not item[1], item[0].casefold()))
        snapshot["labels"] = [("[링크] " if link else "[폴더] " if folder else "") + name
                              for name, folder, link in items]
        snapshot["paths"] = [destination / name for name, _, _ in items]
        folder_count = sum(folder for _, folder, _ in items)
        status = "파일 {}개 · 폴더 {}개".format(len(items) - folder_count, folder_count) if items else "비어 있음"
        drive_label = destination.drive + "\\" if destination.drive else str(destination)
        snapshot["status"] = "{} 연결됨 · {}".format(drive_label, status)
    except OSError as error:
        snapshot["labels"] = snapshot["paths"] = None
        snapshot["status"] = "목록을 읽지 못했습니다 · 마지막 목록 표시 중"
        snapshot["modifier_error"] = error
        return snapshot
    if on_listing is not None:
        # The directory is already usable; volume/script metadata may still
        # take time. Publish a separate dict so the worker cannot mutate it.
        on_listing(dict(snapshot))
    try:
        # The list and signature share this enumeration; writes still perform
        # their own fresh signature and volume validation in sync_card_modifier.
        snapshot["modifier_signature"] = card_modifier_signature(destination, names=[item[0] for item in items])
    except (WorkError, OSError) as error:
        snapshot["modifier_error"] = error
    return snapshot


def publish_card_modifier(destination, volume_id):
    """검증한 임시 파일을 기존 파일을 덮어쓰지 않는 방식으로 배치합니다."""
    target = destination / CARD_MODIFIER_FILENAME
    fd, staging_name = tempfile.mkstemp(prefix='.수정10.30_', suffix='.tmp', dir=str(destination))
    os.close(fd)
    staging = Path(staging_name)
    try:
        atomic_write(staging, CARD_MODIFIER_BYTES)
        if staging.read_bytes() != CARD_MODIFIER_BYTES:
            raise WorkError('수정10.30.py 임시 저장 검증에 실패했습니다.')
        validate_fixed_destination(destination)
        if card_modifier_volume_id(destination) != volume_id:
            raise WorkError('작업 중 카드가 변경되었습니다. 기존 수정 스크립트는 유지합니다.')
        # Windows rename은 이미 있는 대상을 덮어쓰지 않습니다. POSIX의
        # rename은 덮어쓰므로 로컬 검사에서는 원자적 exclusive link를 씁니다.
        if os.name == 'nt':
            os.rename(str(staging), str(target))
        else:
            os.link(str(staging), str(target))
            staging.unlink()
    finally:
        # 재연결된 다른 카드의 파일은 정리하지 않습니다.
        try:
            if card_modifier_volume_id(destination) == volume_id and staging.exists():
                staging.unlink()
        except (OSError, WorkError):
            pass


def sync_card_modifier(destination, expected_signature=None):
    """새본을 확인한 다음에만 구본을 정리합니다. 기존 새본은 덮어쓰지 않습니다."""
    import stat
    destination = Path(destination)
    result = {'added': False, 'removed': [], 'errors': [], 'signature': None, 'retry': False}
    initial_volume_id = None
    try:
        validate_fixed_destination(destination)
        signature = card_modifier_signature(destination)
        initial_volume_id = signature[0]
        if expected_signature is not None and signature != expected_signature:
            result['retry'] = True
            raise WorkError('작업 준비 중 카드 내용이 바뀌었습니다. 새로고침 후 다시 확인합니다.')
        volume_id, entries = signature
        target_entries = [(name, stamp) for name, stamp in entries
                          if name.casefold() == CARD_MODIFIER_FILENAME.casefold()]
        old_entries = [(name, stamp) for name, stamp in entries
                       if is_legacy_card_modifier_name(name) and stat.S_ISREG(stamp[0])
                       and not (stamp[4] & 0x400)]
        if len(target_entries) > 1:
            raise WorkError('수정10.30.py 이름이 겹칩니다. 기존 수정 스크립트는 유지합니다.')
        if target_entries:
            target_name, target_stamp = target_entries[0]
            target = destination / target_name
            if not stat.S_ISREG(target_stamp[0]) or is_link(target):
                raise WorkError('수정10.30.py 위치에 폴더 또는 링크가 있어 추가하지 않았습니다.')
            if not target_stamp[1]:
                raise WorkError('기존 수정10.30.py가 빈 파일입니다. 기존 수정 스크립트는 유지합니다.')
            # 기존 새본만 있으면 내용을 읽거나 덮어쓰지 않습니다. 구본을
            # 지울 때만 내장된 정상 새본과 일치하는지 확인합니다.
            if old_entries and target.read_bytes() != CARD_MODIFIER_BYTES:
                raise WorkError('기존 수정10.30.py 내용이 내장본과 달라 수정9.7 스크립트는 유지합니다.')
            verified_stamp = target_stamp
            if card_modifier_file_stamp(target) != verified_stamp:
                raise WorkError('확인 중 수정10.30.py가 변경되어 수정9.7 스크립트는 유지합니다.')
        else:
            target = destination / CARD_MODIFIER_FILENAME
            publish_card_modifier(destination, volume_id)
            result['added'] = True
            verified_stamp = card_modifier_file_stamp(target)
            if is_link(target) or target.read_bytes() != CARD_MODIFIER_BYTES:
                raise WorkError('수정10.30.py 저장 검증에 실패해 수정9.7 스크립트는 유지합니다.')
            if card_modifier_file_stamp(target) != verified_stamp:
                raise WorkError('저장 확인 중 수정10.30.py가 변경되어 수정9.7 스크립트는 유지합니다.')

        for name, stamp in old_entries:
            validate_fixed_destination(destination)
            if card_modifier_volume_id(destination) != volume_id:
                raise WorkError('작업 중 카드가 변경되어 나머지 수정9.7 스크립트는 유지합니다.')
            if card_modifier_file_stamp(target) != verified_stamp or is_link(target):
                raise WorkError('수정10.30.py가 변경되어 나머지 수정9.7 스크립트는 유지합니다.')
            old_path = destination / name
            try:
                if card_modifier_file_stamp(old_path) != stamp or is_link(old_path):
                    raise WorkError('작업 중 내용이 바뀌어 유지했습니다: {}'.format(name))
                old_path.unlink()
                result['removed'].append(name)
            except (OSError, WorkError) as error:
                result['errors'].append(str(error))
    except (OSError, WorkError) as error:
        result['errors'].append(str(error))
    finally:
        try:
            result['signature'] = card_modifier_signature(destination)
            if initial_volume_id is not None and result['signature'][0] != initial_volume_id:
                result['retry'] = True
        except (OSError, WorkError):
            pass
    return result


def parse_program_year(value):
    text = str(value).strip()
    if not re.fullmatch(r"[0-9]{4}", text) or not 1000 <= int(text) <= 9999:
        raise WorkError("연도는 2026처럼 네 자리 숫자로 입력해 주세요.")
    return int(text)


def program_settings_path():
    return Path(os.environ.get('LOCALAPPDATA') or Path.home()) / 'Jihunius' / 'program_paths.json'


def load_program_year():
    path = program_settings_path().with_name('program_year.json')
    try:
        with path.open('rb') as stream:
            data = stream.read(33)
        if len(data) <= 32:
            return parse_program_year(json.loads(data))
    except (OSError, ValueError, WorkError):
        pass
    return PROGRAM_YEAR


def save_program_year(value):
    year = parse_program_year(value)
    path = program_settings_path().with_name('program_year.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=str(path.parent),
                                         prefix='.program-year-', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(year, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(path))
    finally:
        if temporary is not None:
            try: temporary.unlink()
            except FileNotFoundError: pass
    return year


def normalize_program_base_root(value):
    from pathlib import PureWindowsPath
    if not isinstance(value, str):
        raise WorkError('NC프로그램 기본 폴더 경로를 입력해 주세요.')
    text = value.strip().strip('"')
    if not text or any(ord(character) < 32 for character in text):
        raise WorkError('NC프로그램 기본 폴더 경로를 입력해 주세요.')
    try:
        text = str(Path(text).expanduser())
    except RuntimeError:
        raise WorkError('사용자 폴더를 확인할 수 없습니다. 전체 폴더 경로를 입력해 주세요.') from None
    if not (Path(text).is_absolute() or PureWindowsPath(text).is_absolute()):
        raise WorkError('드라이브 또는 서버 이름부터 시작하는 전체 폴더 경로를 입력해 주세요.')
    return text


def load_program_base_root():
    from pathlib import PureWindowsPath
    try:
        with program_settings_path().open('rb') as stream:
            data = stream.read(32769)
        if len(data) > 32768: return PROGRAM_BASE_ROOT
        value = json.loads(data)
        if isinstance(value, dict):
            selected = normalize_program_base_root(value.get('base_root'))
            if (value.get('default_base_root') != PROGRAM_BASE_ROOT
                    and PureWindowsPath(selected) == PureWindowsPath(LEGACY_PROGRAM_BASE_ROOT)):
                return PROGRAM_BASE_ROOT
            return selected
    except (OSError, ValueError, WorkError):
        pass
    return PROGRAM_BASE_ROOT


def save_program_base_root(value):
    value = normalize_program_base_root(value)
    path = program_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=str(path.parent),
                                         prefix='.program-path-', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump({'base_root': value, 'default_base_root': PROGRAM_BASE_ROOT}, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(path))
    finally:
        if temporary is not None:
            try: temporary.unlink()
            except FileNotFoundError: pass
    return value


def year_search_root(year=PROGRAM_YEAR, base_root=None):
    return Path(PROGRAM_BASE_ROOT if base_root is None else base_root) / "★ {}".format(parse_program_year(year))


def date_search_folders(text, year=None, base_root=None):
    """입력한 날짜의 월 폴더 아래에서 해당 날짜 폴더만 검색 대상으로 만듭니다."""
    year = parse_program_year(PROGRAM_YEAR if year is None else year)
    if not text.strip():
        raise WorkError("가져올 날짜 폴더를 입력해 주세요. (예: 7.1 또는 07.01, 10.12)")
    names = [name for name in re.split(r"[\s,;]+", text.strip()) if name]
    if not names:
        raise WorkError("가져올 날짜 폴더를 입력해 주세요. (예: 7.1 또는 07.01, 10.12)")
    for name in names:
        if not re.fullmatch(r"[0-9]{1,2}\.[0-9]{1,2}", name):
            raise WorkError("잘못된 날짜 폴더: {} (예: 7.1 또는 07.01)".format(name))
        month, day = map(int, name.split("."))
        try:
            date(year, month, day)
        except ValueError:
            raise WorkError("잘못된 날짜 폴더: {} ({}년 날짜를 확인해 주세요.)".format(name, year))
    return [year_search_root(year, base_root) / "{}월".format(int(name.split(".")[0])) / name
            for name in dict.fromkeys(names)]


def resolve_date_search_folders(roots):
    """작업 스레드에서 같은 월·일의 앞자리 0 표기만 확인합니다."""
    resolved = []
    for root in roots:
        root = Path(root).expanduser()
        match = re.fullmatch(r"([0-9]{1,2})\.([0-9]{1,2})", root.name)
        if not match or root.exists() or root.is_symlink():
            resolved.append(root)
            continue
        month, day = map(int, match.groups())
        if root.parent.name != "{}월".format(month):
            resolved.append(root)
            continue
        aliases = dict.fromkeys(("{}.{}".format(month, day),
                                 "{:02d}.{:02d}".format(month, day),
                                 "{}.{:02d}".format(month, day),
                                 "{:02d}.{}".format(month, day)))
        candidates = [root.parent / name for name in aliases if (root.parent / name).is_dir()]
        if len(candidates) > 1:
            raise WorkError("같은 날짜의 폴더가 여러 개 있습니다:\n{}\n"
                            "가져올 폴더 이름을 그대로 입력해 주세요.".format(
                                "\n".join(str(path) for path in candidates)))
        resolved.append(candidates[0] if candidates else root)
    return list(dict.fromkeys(resolved))


def selected_list_name(list_number):
    if list_number not in LIST_NUMBERS:
        raise WorkError("리스트 파일명은 O3999 또는 O3998 중에서 선택해 주세요.")
    return "O" + list_number


def parse_numbers(line):
    numbers = []
    for token in re.split(r"[\s,;]+", line.strip()):
        if not token:
            continue
        match = re.fullmatch(r"[oO]?([0-9]{1,4})", token)
        if not match:
            raise WorkError("잘못된 번호: {} (예: O1234 또는 1234)".format(token))
        number = match.group(1).zfill(4)
        if number in LIST_NUMBERS:
            raise WorkError("O3999와 O3998은 리스트 파일 이름이므로 가져올 번호로 사용할 수 없습니다.")
        numbers.append(number)
    if not numbers:
        raise WorkError("프로그램 번호를 입력해 주세요.")
    return numbers


def filename_number(name):
    match = re.match(r"^[oO]([0-9]{4})(?!\d)", name)
    if match and (name.lower().endswith(".nc") or re.fullmatch(r"[oO][0-9]{4}", name)):
        return match.group(1)
    return None


def find_candidates(roots, numbers):
    wanted = set(numbers)
    found = {number: [] for number in numbers}
    seen = set()

    def scan_error(error):
        raise WorkError("검색 중 폴더를 읽을 수 없습니다: {}".format(error))

    for root in roots:
        for directory, subdirs, filenames in os.walk(str(root), followlinks=False, onerror=scan_error):
            base = Path(directory)
            subdirs[:] = sorted(name for name in subdirs
                                if not is_link(base / name)
                                and not contained(base / name, LEGACY_BACKUP_DIR))
            for name in sorted(filenames):
                number = filename_number(name)
                if number not in wanted:
                    continue
                path = base / name
                if is_link(path):
                    continue
                resolved = path.resolve()
                if resolved in seen or contained(resolved, LEGACY_BACKUP_DIR):
                    continue
                seen.add(resolved)
                found[number].append(resolved)
    return found


def select_candidates(roots, numbers, chooser=None, create_list=True, list_number=DEFAULT_LIST_NUMBER):
    found = find_candidates(roots, numbers)
    missing = ["O" + number for number in numbers if not found[number]]
    if missing:
        print("찾지 못한 프로그램: {}".format(", ".join(missing)))
        if create_list:
            print("이 번호들은 파일 가져오기를 건너뛰고 {}의 호출 목록에는 포함합니다.".format(
                selected_list_name(list_number)))
        else:
            print("찾지 못한 번호는 건너뛰고 나머지 파일만 가져옵니다.")
    selected = []
    for number in numbers:
        candidates = found[number]
        if not candidates:
            continue
        if len(candidates) == 1:
            selected.append((number, candidates[0]))
            continue
        if chooser is not None:
            selected_path = chooser(number, candidates)
            if selected_path is None:
                raise WorkError("이번 작업을 취소했습니다.")
            if selected_path not in candidates:
                raise WorkError("검색 결과에 없는 파일입니다.")
            selected.append((number, selected_path))
            continue
        print("\nO{}가 여러 개입니다. 가져올 파일을 하나 선택하세요.".format(number))
        for index, path in enumerate(candidates, 1):
            print("  {}. {}".format(index, path))
        while True:
            raw = input("선택 번호 (Q: 이번 작업 취소): ").strip()
            if raw.lower() == "q":
                raise WorkError("이번 작업을 취소했습니다.")
            if raw.isdigit() and 1 <= int(raw) <= len(candidates):
                selected.append((number, candidates[int(raw) - 1]))
                break
            print("목록에 있는 선택 번호를 입력해 주세요.")
    return selected


def decode_program(raw):
    encodings = ["utf-8-sig"] if raw.startswith(b"\xef\xbb\xbf") else ["utf-8", "cp949"]
    for encoding in encodings:
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            pass
    raise WorkError("파일 인코딩을 읽을 수 없습니다. UTF-8 / CP949 파일인지 확인해 주세요.")


G4U2_ADD_LINE = b'G4U2.0'

G4U2_M11 = re.compile(rb'M0*11')

G4U2_MOVE = re.compile(rb'G0+Z\+?10(?:\.0*)?T0+')

G4U2_DWELL = re.compile(rb'G0*4(?![0-9.])')

G4U2_SAME_DWELL = re.compile(rb'G0*4U\+?2(?:\.0*)?')

G4U2_MARKER = re.compile(rb'-{5,}[ \t]*$')

G4U2_NUMBER = re.compile(rb'O[0-9]+')

def g4u2_line_body(line):
    return line.rstrip(b'\r\n')

def g4u2_line_ending(line):
    return line[len(g4u2_line_body(line)):]

def g4u2_code_lines(lines):
    """인코딩을 바꾸지 않고 주석/공백/행번호를 제외한 명령을 비교합니다."""
    entries = []
    depth = 0
    for index, line in enumerate(lines):
        raw = g4u2_line_body(line)
        if index == 0 and raw.startswith(b'\xef\xbb\xbf'):
            raw = raw[3:]
        code = bytearray()
        for char in raw:
            if char == 40:
                depth += 1
            elif char == 41 and depth:
                depth -= 1
            elif not depth:
                if char == 59:  # ; 이후 주석
                    break
                code.append(char)
        clean = re.sub(rb'[ \t]', b'', bytes(code)).upper()
        clean = re.sub(rb'^N[0-9]+', b'', clean)
        if clean:
            entries.append((index, clean))
    return entries

def g4u2_initial_mode(code):
    words = re.findall(rb'[GM][0-9]+', code)
    return (b''.join(words) == code and len(words) == 4
            and {(word[:1], int(word[1:])) for word in words}
            == {(b'G', 99), (b'G', 40), (b'G', 97), (b'M', 9)})

def add_g4u2(data):
    """(결과 바이트, 상태, 설명). 일치하는 시작 구간 하나만 변경합니다."""
    if b'\x00' in data:
        return data, '건너뜀', '바이너리 또는 UTF-16 파일'
    # 판별 대상은 앞 200행이며 나머지 바이트는 그대로 이어 붙입니다.
    lines = data.splitlines(keepends=True)[:200]
    entries = g4u2_code_lines(lines)
    meaningful = [(i, c) for i, c in entries if c != b'%']
    if not meaningful or not G4U2_NUMBER.fullmatch(meaningful[0][1]):
        return data, '건너뜀', '시작 부분에 NC 프로그램 O번호가 없음'
    # 하나의 프로그램만 있는 일반 NC 파일을 대상으로 합니다.
    if sum(bool(G4U2_NUMBER.fullmatch(c)) for _, c in entries) != 1:
        return data, '건너뜀', '시작 부분에 여러 프로그램이 있어 위치 확인 필요'
    matches = []
    for k, (index, code) in enumerate(entries):
        if not G4U2_M11.fullmatch(code) or k < 3:
            continue
        if not (re.fullmatch(rb'G0*300', entries[k-3][1])
                and g4u2_initial_mode(entries[k-2][1])
                and re.fullmatch(rb'M0*5', entries[k-1][1])):
            continue
        j = k + 1
        dwell_index = None
        dwell_code = None
        if j < len(entries) and G4U2_DWELL.match(entries[j][1]):
            dwell_index, dwell_code = entries[j]
            j += 1
        if j + 3 >= len(entries):
            continue
        if (G4U2_MOVE.fullmatch(entries[j][1])
                and re.fullmatch(rb'M0*200', entries[j+1][1])
                and re.fullmatch(rb'M0*20', entries[j+2][1])
                and re.fullmatch(rb'M0*10', entries[j+3][1])):
            matches.append((index, dwell_index, dwell_code))
    if len(matches) != 1:
        reason = '대상 시작 구간 없음' if not matches else '대상 구간이 여러 개라 위치 확인 필요'
        return data, '건너뜀', reason
    index, dwell_index, dwell_code = matches[0]
    if dwell_index is not None:
        if G4U2_SAME_DWELL.fullmatch(dwell_code):
            return data, '기존 있음', 'G4U2.0이 이미 있음'
        # 참고 파일처럼 명령 뒤에 붙인 표시만 제거합니다.
        body = g4u2_line_body(lines[dwell_index])
        marker = G4U2_MARKER.search(body)
        plain = G4U2_MARKER.sub(b'', dwell_code)
        if marker and G4U2_SAME_DWELL.fullmatch(plain):
            offset = sum(len(line) for line in lines[:dwell_index])
            new_line = body[:marker.start()] + g4u2_line_ending(lines[dwell_index])
            result = data[:offset] + new_line + data[offset+len(lines[dwell_index]):]
            return result, '표시 제거', 'G4U2.0 뒤의 ----- 표시만 제거'
        return data, '확인 필요', '대상 위치에 다른 대기 명령이 있어 유지함'
    end = sum(len(line) for line in lines[:index+1])
    newline = g4u2_line_ending(lines[index]) or b'\r\n'
    indent = re.match(rb'[ \t]*', lines[index]).group()
    result = data[:end] + indent + G4U2_ADD_LINE + newline + data[end:]
    return result, '추가 완료', 'M11 다음에 G4U2.0 한 줄 추가'

def modify_program(content, filename):
    """업로드한 수정9.7변경 스크립트의 처리 순서/정규식/알람 유지."""
    alarms = []
    content = content.replace("A9.7", "A10.")
    content = re.sub(r'X-(1[5-9])(?:\.(\d{1,3}))?', lambda m: "X-14" + ("." + m.group(2) if m.group(2) else ""), content)
    content = re.sub(r'X-14\.[5-9](\d{0,2})', lambda m: "X-14.4" + m.group(1), content)
    content = re.sub(r'Y(2[0-5])(?:\.(\d{1,3}))?', lambda m: "Y19" + ("." + m.group(2) if m.group(2) else ""), content)
    content = re.sub(r'Y19\.9(\d{0,2})', lambda m: "Y19.8" + m.group(1), content)
    content = re.sub(r'Y-(2[0-5])(?:\.(\d{1,3}))?', lambda m: "Y-19" + ("." + m.group(2) if m.group(2) else ""), content)
    content = re.sub(r'Y-19\.9(\d{0,2})', lambda m: "Y-19.8" + m.group(1), content)
    content = re.sub(r'X-14\.[5-9](\d{2})', lambda m: "X-14.4" + m.group(1), content)

    pi_match = re.search(r'(\d{1,2}\.\d)', filename)
    pi_value = pi_match.group(1) if pi_match else None
    has_pi_a12 = pi_value in PI_VALUE_MAP_A12
    has_pi_a14 = pi_value in PI_VALUE_MAP_A14
    if has_pi_a12 and "A12" in content:
        content = re.sub(r'X\[#531-(\-?\d+\.\d+)\]F0\.02',
                         lambda m: "X[#531{}]F0.02".format(PI_VALUE_MAP_A12[pi_value]), content)
    if has_pi_a14 and "A14" in content:
        content = re.sub(r'X\[#531-(\-?\d+\.\d+)\]F0\.02',
                         lambda m: "X[#531{}]F0.02".format(PI_VALUE_MAP_A14[pi_value]), content)
    if has_pi_a12 and "A10" in content:
        alarms.append("{} → 제목과 파이가 다름 확인필요 (내부에 A10 있음)".format(filename))
    if has_pi_a12 and "A12" not in content:
        alarms.append("{} → 제목과 파이가 다름 확인필요 (제목에 A12 파이 있음, 내부에 A12 없음)".format(filename))
    if "A12" in content and not has_pi_a12:
        alarms.append("{} → 제목과 파이가 다름 확인필요 (내부에 A12 있음, 제목에 A12 파이 없음)".format(filename))
    if has_pi_a14 and "A14" not in content:
        alarms.append("{} → 제목과 파이가 다름 확인필요 (제목에 A14 파이 있음, 내부에 A14 없음)".format(filename))
    if "A14" in content and not has_pi_a14:
        alarms.append("{} → 제목과 파이가 다름 확인필요 (내부에 A14 있음, 제목에 A14 파이 없음)".format(filename))
    return content, alarms


def generate_o3999(numbers):
    lines = ["%", "O3020", "", "", ""]
    # O9999를 함께 가져오는 경우에도 마지막의 고정 호출은 한 번만 넣습니다.
    lines.extend("P{}M198".format(number) for number in numbers if number != "9999")
    lines.append("P9999M198")
    lines.extend([""] * (TARGET_GAP_LINES - 1))
    lines.extend(["M11111", "", "M99", "%"])
    return ("\r\n".join(lines) + "\r\n").encode("utf-8")


def prepare_items(selected, destination):
    items = []
    for number, source in selected:
        raw = source.read_bytes()
        if not raw:
            raise WorkError("빈 프로그램 파일입니다: {}".format(source))
        try:
            content, encoding = decode_program(raw)
        except WorkError as error:
            raise WorkError("{}: {}".format(source, error))
        # 파이 값은 이름을 O1234로 줄이기 전에 원본 파일명에서 찾습니다.
        modified, alarms = modify_program(content, source.name)
        # 모든 호기에 공통 적용. 원본이 아닌 저장할 수정본에만 추가합니다.
        modified_bytes, g4_status, g4_detail = add_g4u2(modified.encode(encoding))
        if g4_status == "확인 필요" or "확인 필요" in g4_detail:
            alarms.append("{} → G4U2.0 추가 확인 필요: {}".format(source.name, g4_detail))
        target_name = source.name if alarms else "O" + number
        items.append({"number": number, "source": source, "original": raw,
                      "target": destination / target_name,
                      "modified": modified_bytes, "alarms": alarms,
                      "g4_status": g4_status, "g4_detail": g4_detail})
    return items


def output_snapshot(target):
    if (target.exists() or target.is_symlink()) and is_link(target):
        raise WorkError("저장할 위치가 링크입니다: {}".format(target))
    if target.exists():
        if not target.is_file():
            raise WorkError("파일을 저장할 위치에 폴더가 있습니다: {}".format(target))
        return target.read_bytes()
    return None


def execute_items(items, roots, destination, allow_overwrite=False, requested_numbers=None, create_list=True,
                  list_number=DEFAULT_LIST_NUMBER):
    """모드에 해당하는 결과만 저장/검증합니다. 원본은 그대로 유지합니다."""
    numbers = ([item["number"] for item in items] if requested_numbers is None
               else list(requested_numbers))
    if not numbers:
        raise WorkError("처리할 번호가 없습니다.")
    list_name = selected_list_name(list_number)
    if roots or items:
        _, destination = validate_paths(roots, destination)
    else:
        destination = validate_destination_path(destination)
    outputs = [(item["target"], item["modified"]) for item in items]
    list_target = destination / list_name
    if create_list:
        if any(target == list_target for target, _ in outputs):
            raise WorkError("가져올 파일 이름이 리스트 파일 이름과 겹칩니다: {}".format(list_name))
        outputs.append((list_target, generate_o3999(numbers)))
    # 오류가 나면 복구할 기존 내용은 작업 중 메모리에만 유지합니다.
    previous = {target: output_snapshot(target) for target, _ in outputs}
    conflicts = [str(path) for path, data in previous.items()
                 if data is not None and not (create_list and path == list_target)]
    if conflicts and not allow_overwrite:
        raise WorkError("이미 존재하는 결과 파일: {}".format(", ".join(conflicts)))
    for item in items:
        if item["source"].read_bytes() != item["original"]:
            raise WorkError("작업 중 원본이 변경되었습니다: {}".format(item["source"]))

    written = []
    try:
        for target, data in outputs:
            if output_snapshot(target) != previous[target]:
                raise WorkError("작업 중 저장 폴더 파일이 변경되었습니다: {}".format(target))
            atomic_write(target, data)
            written.append(target)
        for target, data in outputs:
            if target.read_bytes() != data:
                raise WorkError("저장 결과 검증 실패: {}".format(target))
        for item in items:
            if item["source"].read_bytes() != item["original"]:
                raise WorkError("작업 중 원본이 변경되었습니다: {}".format(item["source"]))
    except BaseException as error:
        rollback_errors = []
        for target in reversed(written):
            try:
                if previous[target] is None:
                    target.unlink()
                else:
                    atomic_write(target, previous[target])
            except OSError as rollback_error:
                rollback_errors.append("{}: {}".format(target, rollback_error))
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            raise
        suffix = "\n복원하지 못한 결과 파일: " + "; ".join(rollback_errors) if rollback_errors else ""
        raise WorkError("저장 실패. 원본은 그대로 유지됩니다.\n{}{}".format(error, suffix))

    alarms = [alarm for item in items for alarm in item["alarms"]]
    return {"alarms": alarms, "copied_sources": [item["source"] for item in items],
            "list_created": create_list, "list_number": list_number}


def destination_snapshot(destination):
    """삭제할 파일/폴더 목록만 확인합니다. 파일 내용은 읽거나 복사하지 않습니다."""
    snapshot = {}

    def visit(folder):
        contains_protected = False
        for path in sorted(folder.iterdir()):
            if folder == destination and path.name.casefold() in SYSTEM_FOLDERS:
                continue
            relative = path.relative_to(destination)
            if is_protected_drive_name(path.name):
                contains_protected = True
                continue
            if is_link(path):
                raise WorkError("드라이브에 링크가 있어 변경하지 않고 중단합니다: {}".format(path))
            if path.is_dir():
                snapshot[relative] = ("directory", None)
                if visit(path):
                    # 보존할 파일이 들어 있는 상위폴더도 남겨 둡니다.
                    snapshot.pop(relative)
                    contains_protected = True
            elif path.is_file():
                stat = path.stat()
                snapshot[relative] = ("file", (stat.st_size, stat.st_mtime_ns))
            else:
                raise WorkError("읽을 수 없는 드라이브 항목입니다: {}".format(path))
        return contains_protected
    visit(destination)
    return snapshot


def clear_destination(destination, snapshot):
    deleted = 0
    errors = []
    for relative, (kind, _) in snapshot.items():
        if kind != "file":
            continue
        # Recheck at deletion time, including protected parent directories.
        if any(is_protected_drive_name(part) for part in relative.parts):
            continue
        try:
            (destination / relative).unlink()
            deleted += 1
        except OSError as error:
            errors.append("{}: {}".format(relative, error))
    directories = [path for path, (kind, _) in snapshot.items() if kind == "directory"]
    for relative in sorted(directories, key=lambda path: len(path.parts), reverse=True):
        if any(is_protected_drive_name(part) for part in relative.parts):
            continue
        try:
            (destination / relative).rmdir()
            deleted += 1
        except OSError as error:
            errors.append("{}: {}".format(relative, error))
    remaining = destination_snapshot(destination)
    if remaining and not errors:
        errors.append("정리 중 새 항목이 생겼습니다: " + ", ".join(str(path) for path in remaining))
    return deleted, errors


def empty_destination(destination):
    """버튼으로 요청한 드라이브만 비웁니다. 백업이나 작업 기록은 만들지 않습니다."""
    destination = Path(destination).resolve()
    if not destination.is_dir():
        raise WorkError("저장 드라이브를 찾을 수 없습니다: {}".format(destination))
    print("드라이브 비우기 대상: {}".format(destination))
    snapshot = destination_snapshot(destination)
    if not snapshot:
        print("지울 자료가 없습니다. 보존 대상 파일은 유지됩니다.")
        return {"cleared_entries": 0}
    print("보존 대상 파일을 제외하고 드라이브의 기존 자료를 삭제합니다.")
    try:
        deleted, errors = clear_destination(destination, snapshot)
    except (KeyboardInterrupt, SystemExit):
        print("비우기를 중단했습니다. 이미 삭제된 내용은 복원하지 않습니다.")
        raise
    if errors:
        raise WorkError("{}개 파일/폴더 삭제 완료. 다음 항목은 지우지 못했습니다:\n{}".format(
            deleted, "\n".join(errors)))
    print("완료: {}개 파일/폴더를 비웠습니다.".format(deleted))
    return {"cleared_entries": deleted}


def empty_fixed_drive(destination=None):
    destination = select_destination() if destination is None else Path(destination).resolve()
    validate_fixed_destination(destination)
    modifier = sync_card_modifier(destination)
    changes = []
    if modifier["added"]:
        changes.append("수정10.30.py 추가")
    if modifier["removed"]:
        changes.append("기존 수정9.7 스크립트 {}개 정리".format(len(modifier["removed"])))
    if changes:
        print("카드: " + " · ".join(changes))
    if modifier["errors"]:
        raise WorkError("수정 스크립트 확인 후 비우기를 다시 실행해 주세요.\n" + "\n".join(modifier["errors"]))
    return empty_destination(destination)


def show_alarms(alarms, popup=True):
    if not alarms:
        return
    print("\n[알람 발생 - 프로그램 확인 필요]")
    for alarm in alarms:
        print("  " + alarm)
    if popup and os.name == "nt":
        ctypes.windll.user32.MessageBoxW(0, "\n".join(alarms), "알람 발생 - 프로그램 확인 필요", 0x30)


def missing_program_warnings(numbers, list_created=True, list_number=DEFAULT_LIST_NUMBER):
    if not numbers:
        return []
    detail = ("해당 번호는 {}에 포함했지만 프로그램 파일은 가져오지 못했습니다.".format(
                  selected_list_name(list_number))
              if list_created else "해당 번호의 프로그램 파일은 가져오지 못했습니다.")
    return ["검색 폴더에서 매칭되는 파일을 찾지 못했습니다:\n{}\n{}".format(
        ", ".join("O" + number for number in numbers), detail)]


def run_batch(roots, destination, numbers, chooser=None, popup=True, mode=MODE_BOTH,
              list_number=DEFAULT_LIST_NUMBER):
    if mode not in MODE_LABELS:
        raise WorkError("올바른 작업 모드를 선택해 주세요.")
    list_name = selected_list_name(list_number)
    import_files = mode != MODE_LIST
    create_list = mode != MODE_FILES
    if import_files:
        roots = resolve_date_search_folders(roots)
        roots, destination = validate_paths(roots, destination)
    else:
        roots = []
        destination = validate_destination_path(destination)
    validate_fixed_destination(destination)
    print("\n작업 모드: " + MODE_LABELS[mode])
    # 호출 순서는 입력 그대로 유지하고, 같은 번호의 파일은 한 번만 가져옵니다.
    requested_numbers = list(numbers)
    items = []
    if import_files:
        print("검색 중...")
        selected = select_candidates(roots, list(dict.fromkeys(requested_numbers)),
                                     chooser=chooser, create_list=create_list, list_number=list_number)
        items = prepare_items(selected, destination)
        print("\n[가져오기 / 수정 목록]")
        for item in items:
            print("  {} → {}".format(item["source"], item["target"]))
    # 번호를 가져올 때는 같은 이름의 결과 파일만 갱신합니다.
    result = execute_items(items, roots, destination, allow_overwrite=True,
                           requested_numbers=requested_numbers, create_list=create_list, list_number=list_number)
    matched_numbers = {item["number"] for item in items}
    result["missing_numbers"] = ([number for number in dict.fromkeys(requested_numbers)
                                  if number not in matched_numbers] if import_files else [])
    result["mode"] = mode
    if import_files:
        g4_summary = {}
        for item in items:
            status = item["g4_status"]
            g4_summary[status] = g4_summary.get(status, 0) + 1
        result["g4_summary"] = g4_summary
        print("G4U2.0: " + (" / ".join("{} {}개".format(status, count)
                                      for status, count in g4_summary.items()) or "처리 대상 없음"))
    if mode == MODE_FILES:
        print("\n완료: {}개 수정본 저장".format(len(items)))
    elif mode == MODE_LIST:
        print("\n완료: {} 저장 (입력한 {}개 번호 포함)".format(list_name, len(requested_numbers)))
    else:
        print("\n완료: {}개 수정본 + {} 저장 (입력한 {}개 번호 포함)".format(
            len(items), list_name, len(requested_numbers)))
    print("저장 위치: " + str(destination))
    print("원본 파일과 폴더는 그대로 유지했습니다.")
    warnings = missing_program_warnings(result["missing_numbers"], create_list, list_number) + result["alarms"]
    show_alarms(warnings, popup=popup)
    if not warnings:
        print("알람 없이 모든 작업을 완료했습니다.")
    return result


def open_drive_path(path):
    """파일은 연결 프로그램으로 열고, Python 스크립트는 해당 폴더에서 실행합니다."""
    if path.is_file() and path.suffix.casefold() in {".py", ".pyw"}:
        interpreter = Path(sys.executable)
        executable_name = "pythonw.exe" if path.suffix.casefold() == ".pyw" else "python.exe"
        preferred = interpreter.with_name(executable_name)
        if preferred.is_file():
            interpreter = preferred
        return subprocess.Popen([str(interpreter), str(path)], cwd=str(path.parent))
    os.startfile(str(path))


def validate_drive_filename(name):
    if not name or name in {".", ".."}:
        raise WorkError("새 파일 이름을 입력해 주세요.")
    if re.search(r'[<>:"/\\|?*\x00-\x1f]', name) or name.endswith((".", " ")):
        raise WorkError("파일 이름에 사용할 수 없는 문자나 끝의 공백·마침표가 있습니다.")
    stem = name.split(".", 1)[0].rstrip(" ")
    if re.fullmatch(r"CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³]", stem, re.IGNORECASE):
        raise WorkError("Windows에서 예약된 이름은 사용할 수 없습니다.")
    if len(name.encode("utf-16-le")) // 2 > 255:
        raise WorkError("파일 이름이 너무 깁니다.")
    return name


def rename_drive_file(path, destination, new_name):
    """지정한 드라이브 바로 안의 파일명만 바꿉니다. 내용은 수정하지 않습니다."""
    new_name = validate_drive_filename(new_name)
    if path.parent != destination:
        raise WorkError("현재 드라이브 목록의 파일만 이름을 변경할 수 있습니다.")
    validate_fixed_destination(destination)
    if not path.is_file() or is_link(path):
        raise WorkError("이름 변경은 현재 드라이브의 일반 파일에서 사용할 수 있습니다.")
    if is_protected_drive_name(path.name):
        raise WorkError("보존 대상인 수정 스크립트는 이름을 유지합니다.")
    target = path.with_name(new_name)
    if target.name == path.name:
        return path
    # Windows의 대소문자 구분 없는 이름 충돌도 덮어쓰지 않습니다.
    for entry in path.parent.iterdir():
        if entry.name.casefold() == new_name.casefold() and entry.name != path.name:
            raise WorkError("같은 이름의 파일이나 폴더가 이미 있습니다: {}".format(new_name))
    # Windows에서는 os.rename도 기존 대상 파일을 덮어쓰지 않습니다.
    path.rename(target)
    return target


def drive_file_snapshot(path):
    if not path.is_file() or is_link(path):
        raise WorkError("일반 파일만 추가하거나 삭제할 수 있습니다: {}".format(path.name))
    info = path.stat()
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def drive_target_snapshot(path, destination):
    if path.parent != destination:
        raise WorkError("현재 드라이브 바로 안의 파일만 변경할 수 있습니다.")
    if is_protected_drive_name(path.name):
        raise WorkError("보존 대상인 수정 스크립트는 변경하거나 삭제하지 않습니다.")
    if not os.path.lexists(path):
        return None
    return drive_file_snapshot(path)


def prepare_drive_add(paths, destination):
    """복사 전 전체 목록을 확인하고, 덮어쓸 대상의 상태도 기억합니다."""
    validate_fixed_destination(destination)
    existing = {path.name.casefold(): path for path in destination.iterdir()}
    names, plan = set(), []
    for value in paths:
        source = Path(value).absolute()
        validate_drive_filename(source.name)
        key = source.name.casefold()
        if key in names:
            raise WorkError("추가할 파일끼리 이름이 같습니다: {}".format(source.name))
        names.add(key)
        target = existing.get(key, destination / source.name)
        source_state = drive_file_snapshot(source)
        target_state = drive_target_snapshot(target, destination)
        if source.resolve() == target.resolve() or (target_state is not None and os.path.samefile(source, target)):
            raise WorkError("이미 같은 드라이브에 있는 파일입니다: {}".format(source.name))
        plan.append((source, target, source_state, target_state))
    return plan


def require_drive_state(path, destination, expected):
    if drive_target_snapshot(path, destination) != expected:
        raise WorkError("확인 후 파일이 변경되었습니다. 새로고침한 뒤 다시 시도해 주세요: {}".format(path.name))
    # 대소문자만 다른 새 항목도 승인 없이 덮어쓰지 않습니다.
    if expected is None and any(item.name.casefold() == path.name.casefold() for item in destination.iterdir()):
        raise WorkError("같은 이름의 항목이 새로 생겼습니다. 다시 추가해 주세요: {}".format(path.name))


def add_drive_files(plan, destination):
    """변환 없는 복사. 한 파일의 복사가 검증된 뒤에만 기존 대상을 교체합니다."""
    completed = 0
    try:
        validate_fixed_destination(destination)
        for source, target, source_state, target_state in plan:
            if drive_file_snapshot(source) != source_state:
                raise WorkError("추가할 원본 파일이 변경되었습니다: {}".format(source.name))
            require_drive_state(target, destination, target_state)
        for source, target, source_state, target_state in plan:
            validate_fixed_destination(destination)
            temp_path = None
            try:
                fd, temp_name = tempfile.mkstemp(prefix=".지후니우스_추가_", suffix=".tmp", dir=str(destination))
                temp_path = Path(temp_name)
                digest = hashlib.sha256()
                with os.fdopen(fd, "wb") as output, source.open("rb") as incoming:
                    while True:
                        block = incoming.read(1024 * 1024)
                        if not block:
                            break
                        output.write(block)
                        digest.update(block)
                    output.flush()
                    os.fsync(output.fileno())
                if drive_file_snapshot(source) != source_state:
                    raise WorkError("복사 중 원본 파일이 변경되었습니다: {}".format(source.name))
                copied = hashlib.sha256()
                with temp_path.open("rb") as check:
                    for block in iter(lambda: check.read(1024 * 1024), b""):
                        copied.update(block)
                if copied.digest() != digest.digest():
                    raise WorkError("복사한 파일의 내용 검증에 실패했습니다: {}".format(source.name))
                validate_fixed_destination(destination)
                require_drive_state(target, destination, target_state)
                os.replace(str(temp_path), str(target))
                completed += 1
                print("파일 추가: " + target.name)
            finally:
                if temp_path is not None and temp_path.exists():
                    temp_path.unlink()
    except (WorkError, OSError) as error:
        raise WorkError("파일 추가 중단 · {}개 완료\n{}".format(completed, error)) from error
    print("파일 {}개 추가 완료. 원본 파일은 그대로 유지했습니다.".format(completed))
    return completed


def prepare_drive_delete(paths, destination):
    validate_fixed_destination(destination)
    plan = []
    for path in dict.fromkeys(paths):
        state = drive_target_snapshot(path, destination)
        if state is None:
            raise WorkError("선택한 파일이 없어졌습니다: {}".format(path.name))
        plan.append((path, state))
    return plan


def delete_drive_files(plan, destination):
    completed = 0
    try:
        validate_fixed_destination(destination)
        for path, state in plan:
            require_drive_state(path, destination, state)
        for path, state in plan:
            validate_fixed_destination(destination)
            require_drive_state(path, destination, state)
            path.unlink()
            completed += 1
            print("선택 파일 삭제: " + path.name)
    except (WorkError, OSError) as error:
        raise WorkError("선택 삭제 중단 · {}개 삭제됨\n{}".format(completed, error)) from error
    print("선택한 파일 {}개 삭제 완료.".format(completed))
    return completed


class WindowsFileDrop:
    """별도 설치 없이 탐색기의 파일 드롭을 Tk 이벤트 큐에 전달합니다."""
    def __init__(self, hwnd, events, context):
        from ctypes import wintypes
        self.hwnd = hwnd
        self.events = events
        self.context = context
        self.subclass_id = id(self)
        self.installed = False
        self.shell = ctypes.WinDLL("shell32", use_last_error=True)
        self.controls = ctypes.WinDLL("comctl32", use_last_error=True)
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT,
                                           ctypes.c_size_t, ctypes.c_ssize_t,
                                           ctypes.c_size_t, ctypes.c_size_t)
        self.callback = callback_type(self.handle_message)
        self.controls.SetWindowSubclass.argtypes = [wintypes.HWND, callback_type, ctypes.c_size_t, ctypes.c_size_t]
        self.controls.SetWindowSubclass.restype = wintypes.BOOL
        self.controls.RemoveWindowSubclass.argtypes = [wintypes.HWND, callback_type, ctypes.c_size_t]
        self.controls.RemoveWindowSubclass.restype = wintypes.BOOL
        self.controls.DefSubclassProc.argtypes = [wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_ssize_t]
        self.controls.DefSubclassProc.restype = ctypes.c_ssize_t
        self.shell.DragAcceptFiles.argtypes = [wintypes.HWND, wintypes.BOOL]
        self.shell.DragAcceptFiles.restype = None
        self.shell.DragQueryFileW.argtypes = [wintypes.HANDLE, wintypes.UINT, wintypes.LPWSTR, wintypes.UINT]
        self.shell.DragQueryFileW.restype = wintypes.UINT
        self.shell.DragFinish.argtypes = [wintypes.HANDLE]
        self.shell.DragFinish.restype = None
        if not self.controls.SetWindowSubclass(hwnd, self.callback, self.subclass_id, 0):
            raise OSError("파일 드래그 입력을 연결하지 못했습니다.")
        self.installed = True
        self.shell.DragAcceptFiles(hwnd, True)

    def handle_message(self, hwnd, message, wparam, lparam, subclass_id, reference):
        if message == 0x0233:  # WM_DROPFILES
            try:
                paths = []
                count = self.shell.DragQueryFileW(wparam, 0xffffffff, None, 0)
                for index in range(count):
                    length = self.shell.DragQueryFileW(wparam, index, None, 0)
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    if not self.shell.DragQueryFileW(wparam, index, buffer, length + 1):
                        raise OSError("드래그한 파일 경로를 읽지 못했습니다.")
                    paths.append(buffer.value)
                destination, busy = self.context()
                self.events.put(("drive_drop", tuple(paths), destination, busy))
            except Exception as error:
                self.events.put(("drive_drop_error", str(error)))
            finally:
                self.shell.DragFinish(wparam)
            return 0
        if message == 0x0082:  # WM_NCDESTROY
            self.close()
        return self.controls.DefSubclassProc(hwnd, message, wparam, lparam)

    def close(self):
        if self.installed:
            self.shell.DragAcceptFiles(self.hwnd, False)
            self.controls.RemoveWindowSubclass(self.hwnd, self.callback, self.subclass_id)
            self.installed = False


def main_console():
    print("=== 지후니우스 ===")
    print("파일만 가져오기 / 리스트만 만들기 / 파일 + 리스트 만들기 (원본 보존)")
    while True:
        destination = select_destination()
        validate_fixed_destination(destination)
        print("\n검색 기준: " + PROGRAM_BASE_ROOT)
        print("저장 폴더: " + str(destination))
        mode_text = input("모드 1: 파일만 / 2: 리스트만 / 3 또는 Enter: 파일 + 리스트\n"
                          "C: 드라이브 비우기 / Q: 종료\n> ").strip().lower()
        if mode_text == "q":
            return
        if mode_text == "c":
            try:
                empty_fixed_drive(destination)
            except (WorkError, OSError) as error:
                print("\n비우기 중단: " + str(error))
            continue
        mode = {"1": MODE_FILES, "2": MODE_LIST, "3": MODE_BOTH, "": MODE_BOTH}.get(mode_text)
        if mode is None:
            print("작업 모드는 1, 2, 3 중에서 선택해 주세요.")
            continue
        list_number = DEFAULT_LIST_NUMBER
        if mode != MODE_FILES:
            list_text = input("리스트 파일명: 3999 또는 3998 (Enter: 3999) / Q: 종료\n> ").strip()
            if list_text.lower() == "q":
                return
            match = re.fullmatch(r"[oO]?(3999|3998)", list_text or DEFAULT_LIST_NUMBER)
            if match is None:
                print("리스트 파일명은 O3999 또는 O3998 중에서 선택해 주세요.")
                continue
            list_number = match.group(1)
        roots = []
        if mode != MODE_LIST:
            year_text = input("연도 (예: 2026 / Enter: 2026) / Q: 종료\n> ").strip()
            if year_text.lower() == "q":
                return
            try:
                selected_year = parse_program_year(year_text or PROGRAM_YEAR)
            except WorkError as error:
                print(str(error))
                continue
            folder_text = input("날짜 폴더 (예: 7.1, 07.01, 10.12) / Q: 종료\n> ").strip()
            if folder_text.lower() == "q":
                return
            try:
                roots = date_search_folders(folder_text, selected_year)
            except WorkError as error:
                print(str(error))
                continue
            print("\n검색 폴더:")
            for root in roots:
                print("  " + str(root))
        print("작업 모드: " + MODE_LABELS[mode])
        print("저장 폴더: " + str(destination))
        print("번호 입력: O1234 또는 1234 / 여러 번호 가능")
        print(MODE_DESCRIPTIONS[mode].format(list_name=selected_list_name(list_number)))
        print("빈 줄: 선택한 모드 실행 / C: 표시된 드라이브 비우기 / Q: 종료")
        numbers = []
        while True:
            line = input("> ").strip()
            if line.lower() == "q":
                return
            if line.lower() == "c":
                try:
                    empty_fixed_drive(destination)
                except (WorkError, OSError) as error:
                    print("\n비우기 중단: " + str(error))
                break
            if not line:
                if not numbers:
                    continue
                try:
                    run_batch(roots, destination, numbers, mode=mode, list_number=list_number)
                except (WorkError, OSError) as error:
                    print("\n작업 중단: " + str(error))
                break
            try:
                added = parse_numbers(line)
            except WorkError as error:
                print(str(error))
                continue
            for number in added:
                numbers.append(number)
            print("대기: " + " / ".join("O" + number for number in numbers))


class QueueWriter:
    def __init__(self, events):
        self.events = events

    def write(self, text):
        if text:
            self.events.put(("text", text))
        return len(text)

    def flush(self):
        pass


def configure_windows_app_identity():
    # Tk 창을 만들기 전에 Python 대신 이 앱의 작업표시줄 그룹을 지정합니다.
    if os.name != "nt":
        return
    try:
        set_app_id = ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID
        set_app_id.argtypes = [ctypes.c_wchar_p]
        set_app_id.restype = ctypes.c_long
        set_app_id(APP_USER_MODEL_ID)
    except (AttributeError, OSError):
        # 아이콘 그룹 설정이 불가능해도 파일 작업은 계속 사용할 수 있습니다.
        pass


def load_app_icons(window):
    import tkinter as tk
    icons = {size: tk.PhotoImage(master=window, data=data, format="png")
             for size, data in APP_ICON_PNGS.items()}
    # 창 제목줄 · 작업표시줄 · 이후 열리는 파일 선택창에 같은 로고를 사용합니다.
    window.iconphoto(True, *icons.values())
    return icons


def configure_app_style(window):
    from tkinter import ttk
    style = ttk.Style(window)
    style.theme_use("clam")
    window.configure(background="#060b16")
    style.configure(".", font=("맑은 고딕", 10), foreground="#eaf0fc")
    style.configure("TFrame", background="#060b16")
    style.configure("Card.TFrame", background="#060b16", borderwidth=1, relief="solid",
                    bordercolor="#060b16", lightcolor="#060b16", darkcolor="#060b16")
    style.configure("TLabel", background="#060b16")
    style.configure("Title.TLabel", font=("맑은 고딕", 22, "bold"))
    style.configure("Subtitle.TLabel", foreground="#9fb2d6")
    style.configure("Section.TLabel", background="#060b16", font=("맑은 고딕", 11, "bold"))
    style.configure("Card.TLabel", background="#060b16")
    style.configure("Caption.TLabel", background="#060b16", foreground="#9fb2d6", font=("맑은 고딕", 9))
    style.configure("Drive.TLabel", background="#060b16", foreground="#8db3ff", font=("맑은 고딕", 12, "bold"))
    style.configure("AlarmNotice.TLabel", background="#060b16", foreground="#ffd166",
                    font=("맑은 고딕", 15, "bold"))
    style.configure("Status.TLabel", background="#10234a", foreground="#a7c9ff", padding=(14, 8),
                    font=("맑은 고딕", 10, "bold"))
    style.configure("TSeparator", background="#22355c")
    style.configure("TEntry", fieldbackground="#050a14", bordercolor="#2e333d", padding=(12, 10))
    style.map("TEntry", fieldbackground=[("disabled", "#0f1a30")],
              foreground=[("disabled", "#818388")], bordercolor=[("focus", "#2a66f2")])
    style.configure("Accent.TButton", background="#2a66f2", foreground="#ffffff", borderwidth=0,
                    padding=(22, 12), font=("맑은 고딕", 11, "bold"))
    style.map("Accent.TButton", background=[("disabled", "#22355c"), ("active", "#2257d0")],
              foreground=[("disabled", "#8e9196")])
    style.configure("Secondary.TButton", background="#0e1a35", foreground="#ffffff",
                    bordercolor="#4a515e", lightcolor="#4a515e", darkcolor="#4a515e",
                    padding=(22, 12), font=("맑은 고딕", 11, "bold"))
    style.map("Secondary.TButton", background=[("disabled", "#0f1a30"), ("active", "#15264a")],
              foreground=[("disabled", "#96999e"), ("!disabled", "#ffffff")])
    style.configure("DriveSmall.TButton", background="#0e1a35", foreground="#ffffff", borderwidth=0,
                    padding=(6, 3), font=("맑은 고딕", 9))
    style.map("DriveSmall.TButton", background=[("disabled", "#0f1a30"), ("active", "#15264a")],
              foreground=[("disabled", "#96999e")])
    style.configure("Danger.TButton", background="#060b16", foreground="#ffb7c5", bordercolor="#8a3b4e",
                    lightcolor="#8a3b4e", darkcolor="#8a3b4e", padding=(14, 10), font=("맑은 고딕", 10, "bold"))
    style.map("Danger.TButton", background=[("disabled", "#0f1a30"), ("active", "#15254a")],
              foreground=[("disabled", "#7d7f84")])
    style.layout("Mode.TRadiobutton", style.layout("TButton"))
    style.configure("Mode.TRadiobutton", background="#060b16", foreground="#aebcd8", borderwidth=0,
                    padding=(14, 11), font=("맑은 고딕", 10, "bold"))
    style.map("Mode.TRadiobutton", background=[("disabled", "#0f1a30"), ("selected", "#2a66f2"),
                                               ("active", "#15254a")],
              foreground=[("disabled", "#84868b"), ("selected", "#ffffff")])
    style.configure("Handover.TNotebook", background="#060b16", borderwidth=0, tabmargins=(0, 0, 0, 12))
    style.configure("Handover.TNotebook.Tab", background="#0e1a35", foreground="#aebcd8",
                    padding=(14, 9), font=("맑은 고딕", 11, "bold"))
    style.map("Handover.TNotebook.Tab", background=[("selected", "#2a66f2")],
              foreground=[("selected", "#ffffff")])
    style.configure("Handover.Treeview", background="#050a14", fieldbackground="#050a14",
                    foreground="#eaf0fc", borderwidth=0, rowheight=38, font=("맑은 고딕", 10))
    style.map("Handover.Treeview", background=[("selected", "#1d3f86")],
              foreground=[("selected", "#ffffff")])
    style.configure("HandoverToggle.TButton", background="#0e1a35", foreground="#a7c9ff", borderwidth=0,
                    padding=(14, 9), font=("맑은 고딕", 10, "bold"))
    style.map("HandoverToggle.TButton", background=[("active", "#15264a")])
    style.configure("HandoverNotice.TButton", background="#4a3b10", foreground="#ffd166", borderwidth=0,
                    padding=(14, 9), font=("맑은 고딕", 10, "bold"))
    style.map("HandoverNotice.TButton", background=[("active", "#5a4815")])
    for scrollbar_style in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
        style.configure(scrollbar_style, background="#3a404b", troughcolor="#050a14", borderwidth=0,
                        bordercolor="#050a14", lightcolor="#3a404b", darkcolor="#3a404b", arrowcolor="#aebcd8",
                        arrowsize=12)
    return style


# STL 검색 엔진은 별도 이름공간에 보존합니다. 검색·매칭·설정 로직은 원본과 같습니다.
def complete_windows_ime():
    """Commit pending composition in this UI thread, without inserting text twice."""
    if os.name != 'nt':
        return False
    from ctypes import wintypes as W
    user = ctypes.WinDLL('user32')
    imm = ctypes.WinDLL('imm32')
    user.GetFocus.argtypes = []; user.GetFocus.restype = W.HWND
    imm.ImmGetContext.argtypes = [W.HWND]; imm.ImmGetContext.restype = W.HANDLE
    imm.ImmReleaseContext.argtypes = [W.HWND, W.HANDLE]; imm.ImmReleaseContext.restype = W.BOOL
    imm.ImmGetCompositionStringW.argtypes = [W.HANDLE, W.DWORD, W.LPVOID, W.DWORD]
    imm.ImmGetCompositionStringW.restype = ctypes.c_long
    imm.ImmNotifyIME.argtypes = [W.HANDLE, W.DWORD, W.DWORD, W.DWORD]
    imm.ImmNotifyIME.restype = W.BOOL
    hwnd = user.GetFocus()  # GetFocus is limited to the current thread, not MES/POP.
    if not hwnd:
        return False
    context = imm.ImmGetContext(hwnd)
    if not context:
        return False
    try:
        if imm.ImmGetCompositionStringW(context, 8, None, 0) <= 0:
            return False
        if not imm.ImmNotifyIME(context, 0x15, 1, 0):  # NI_COMPOSITIONSTR / CPS_COMPLETE
            raise RuntimeError('한글 입력을 확정하지 못했어요. 입력칸에서 오른쪽 방향키를 누른 뒤 다시 실행해 주세요.')
        return True
    finally:
        imm.ImmReleaseContext(hwnd, context)


def defer_ime_commit(window, action):
    """Run an input-consuming action after Tk processes the IME result message."""
    if getattr(window, '_ime_replaying', False):
        return False
    if getattr(window, '_ime_pending', False):
        return True
    if not complete_windows_ime():
        return False
    window._ime_pending = True
    def resume():
        window._ime_pending = False
        if not window.winfo_exists():
            return
        window._ime_replaying = True
        try:
            action()
        finally:
            window._ime_replaying = False
    window.after(20, resume)
    return True


STL_FINDER_SOURCE = ...  # build: tools/build_app.py

_STL_MODULE = None


def load_stl_finder():
    global _STL_MODULE
    if _STL_MODULE is None:
        import types
        module = types.ModuleType(__name__ + "._stl_finder")
        module.__file__ = __file__
        module.defer_ime_commit = defer_ime_commit
        sys.modules[module.__name__] = module
        try:
            exec(compile(STL_FINDER_SOURCE, __file__ + " [STL찾기]", "exec"), module.__dict__)
        except Exception:
            sys.modules.pop(module.__name__, None)
            raise
        _STL_MODULE = module
    return _STL_MODULE



WASH_MES_SOURCE = ...  # build: tools/build_app.py
WASH_POP_SOURCE = ...  # build: tools/build_app.py
def load_wash_module(source, name):
    import types
    module = types.ModuleType(name)
    module.__file__ = __file__
    exec(compile(source, __file__ + ' [' + name + ']', 'exec'), module.__dict__)
    return module


class WashReader:
    """One isolated STA reader per run; compile once, fresh accessibility tree per request."""
    def __init__(self, module):
        import tempfile, subprocess, threading
        self.module = module
        self.tmp = tempfile.TemporaryDirectory(prefix='jihuni_wash_')
        self.process = None
        self.lines = queue.Queue()
        self.requests = 0
        self.elapsed = 0
        try:
            source = module.POWERSHELL.split("    $source = @'\n",1)[1].split("\n'@",1)[0]
            # Serialize once inside C#, avoiding thousands of PowerShell callbacks per screen.
            pos=source.rfind('}')
            source=source[:pos]+'''public static string Snapshot(long handle, int pid, bool geometryOnly, bool visibleRowsOnly, string mode) {
                GeometryOnly = geometryOnly;
                VisibleRowsOnly = visibleRowsOnly;
                CellBoundsMode = mode == "mes_full" ? 1 : (mode == "pop_full" ? 2 : (mode == "pop_final" ? 3 : 0));
                List<object> records = new List<object>();
                Dump(handle, pid, records.Add);
                var serializer = new System.Web.Script.Serialization.JavaScriptSerializer();
                serializer.MaxJsonLength = 67108864;
                return serializer.Serialize(records);
            }
            '''+source[pos:]
            directory = Path(self.tmp.name)
            (directory/'reader.cs').write_text(source,encoding='utf-8-sig')
            script = r'''
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
[Console]::OutputEncoding=New-Object System.Text.UTF8Encoding($false)
try {
 Add-Type -AssemblyName Accessibility
 $source=[System.IO.File]::ReadAllText($env:JIHUNI_READER_SOURCE)
 Add-Type -TypeDefinition $source -Language CSharp -ReferencedAssemblies @([Accessibility.IAccessible].Assembly.Location,'System.dll','System.Core.dll','System.Web.Extensions.dll')
 [Console]::WriteLine('{"kind":"ready"}')
 while ($null -ne ($line=[Console]::ReadLine())) {
  try {
   $request=$line | ConvertFrom-Json
   [Console]::WriteLine([MesReadOnlyAccessibility]::Snapshot([long]$request.handle,[int]$request.pid,($request.mode -eq 'mes_rows'),($request.mode -eq 'pop_fast'),[string]$request.mode))
  } catch { [Console]::WriteLine((@{kind='fatal';error=$_.Exception.ToString()} | ConvertTo-Json -Compress)) }
  [Console]::WriteLine('{"kind":"request_done"}')
  [Console]::Out.Flush()
  [GC]::Collect()
 }
} catch { [Console]::WriteLine((@{kind='fatal';error=$_.Exception.ToString()} | ConvertTo-Json -Compress)) }
'''
            (directory/'reader.ps1').write_text(script,encoding='utf-8-sig')
            powershell=Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32/WindowsPowerShell/v1.0/powershell.exe'
            env=os.environ.copy();env['JIHUNI_READER_SOURCE']=str(directory/'reader.cs')
            self.errors=(directory/'errors.txt').open('wb')
            self.process=subprocess.Popen([str(powershell),'-NoLogo','-NoProfile','-NonInteractive','-STA','-EncodedCommand',module.base64.b64encode(script.encode('utf-16le')).decode('ascii')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.errors,env=env,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            def drain():
                try:
                    for line in self.process.stdout:self.lines.put(line)
                finally:self.lines.put(None)
            self.thread=threading.Thread(target=drain,daemon=True);self.thread.start()
            self.ready=False
        except Exception:
            self.close();raise

    def record(self,stop,deadline):
        import json
        while True:
            if stop.is_set():raise RuntimeError('사용자 중지')
            if time.monotonic()>deadline:raise RuntimeError('화면 판독 제한 시간을 초과했습니다.')
            try:line=self.lines.get(timeout=.05)
            except queue.Empty:continue
            if line is None:raise RuntimeError('화면 판독기가 종료되었습니다.')
            try:return json.loads(line.decode('utf-8-sig'))
            except (ValueError,UnicodeError):raise RuntimeError('화면 판독 응답이 올바르지 않습니다.')

    def capture(self,target,label,stop):
        import json
        start=time.monotonic();deadline=start+330
        if not self.ready:
            ready=self.record(stop,deadline)
            if ready.get('kind')!='ready':raise RuntimeError('화면 판독기 초기화 실패: '+str(ready.get('error','')))
            self.ready=True
        self.process.stdin.write((json.dumps({'handle':int(target['handle']),'pid':int(target['pid']),'mode':target.get('mode','full')})+'\n').encode('ascii'))
        self.process.stdin.flush()
        report={'target':dict(target),'label':label,'read_only':True,'exit_code':0,'records':[]}
        while True:
            record=self.record(stop,deadline)
            if isinstance(record,list):report['records'].extend(record)
            elif record.get('kind')=='request_done':break
            else:report['records'].append(record)
        self.module.check_capture(report)
        report['capture_seconds']=round(time.monotonic()-start,3);report['capture_mode']=target.get('mode','full')
        self.requests+=1;self.elapsed+=time.monotonic()-start
        return report

    def close(self):
        if self.process is not None:
            if self.process.poll() is None:self.process.kill()
            self.process.wait(timeout=5)
            if getattr(self,'thread',None):self.thread.join(timeout=2)
            self.process.stdin.close();self.process.stdout.close()
        if getattr(self,'errors',None):self.errors.close()
        self.tmp.cleanup()


def wash_query_binding(module,report,api,pop=False):
    candidates=[]
    for e in module.nodes(report):
        if e.get('parent')!=-1 or e.get('role')!=43 or e.get('offscreen') or not e.get('enabled'):continue
        name=e.get('name','')
        if any(w in name for w in ('저장','완료','삭제','닫기')):continue
        if pop:
            try:module.validate_query(report,{'handle':e['handle']})
            except RuntimeError:continue
        elif name.strip() not in ('조회','simpleButton1'):continue
        candidates.append(e)
    if len(candidates)!=1:raise RuntimeError('조회 버튼을 하나로 구분하지 못했습니다. 검사 기록을 보내 주세요.')
    e=candidates[0];handle=e['handle'];api.verify(handle);r=api.rect(handle)
    return {'handle':handle,'class':api.text(handle,True),'text':api.text(handle),
            'size':[r.right-r.left,r.bottom-r.top],'purpose':'query','registered_by':'현재 화면 구조 자동 확인'}


def wash_source(module,steps,group,sequence,production_date=None,selected_numbers=None):
    """Use the proven import validation without an intermediate user ZIP."""
    import tempfile,zipfile,json
    selected_numbers=list(range(1,11)) if selected_numbers is None else list(selected_numbers)
    if (not selected_numbers or any(type(n) is not int or not 1<=n<=10 for n in selected_numbers)
            or selected_numbers!=sorted(set(selected_numbers)) or [s.get('number') for s in steps]!=selected_numbers):
        raise RuntimeError('선택한 호기의 수집이 모두 끝나지 않았습니다.')
    module.SEQUENCE=sequence
    with tempfile.TemporaryDirectory(prefix='jihuni_mes_source_') as temp:
        path=Path(temp)/'MES_current.zip'
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('MES_cycle.json',json.dumps({'version':3,'selected_numbers':selected_numbers,'context':{'group':group},'steps':steps},ensure_ascii=False))
        result=module.load_mes(path)
    result['sequence']=sequence
    return result


WASH_MES_QUERY_PROFILE = {'layout': [['', 80, 36, 64, 28], ['simpleButton1', 0, 2, 64, 28], ['simpleButton1', 0, 36, 64, 28], ['simpleButton1', 80, 0, 64, 28], ['simpleButton1', 181, 34, 76, 28], ['simpleButton1', 262, 0, 76, 28], ['simpleButton1', 262, 34, 76, 28], ['simpleButton1', 360, 34, 76, 28], ['simpleButton1', 451, 34, 76, 28], ['simpleButton1', 571, 34, 78, 28], ['simpleButton1', 662, 34, 78, 28], ['simpleButton1', 764, 34, 58, 28], ['simpleButton1', 828, 34, 58, 28], ['simpleButton1', 916, 34, 76, 28], ['simpleButton1', 1020, 34, 76, 28], ['simpleButton1', 1115, 7, 38, 52]], 'index': 1}

def wash_ensure_mes_production(module,api,report,capture,stop,emit):
    def tab(r):
        module.check_capture(r)
        candidates=[n for n in module.nodes(r) if n.get('role')==37
                    and n.get('name','').strip()=='생산일보관리' and not n.get('offscreen')
                    and n.get('enabled') and n.get('state_known')]
        if len(candidates)!=1:raise RuntimeError('MES 생산일보관리 탭을 하나로 구분하지 못했습니다. 작업지시관리 화면을 열어 주세요.')
        return candidates[0]
    item=tab(report)
    if item.get('selected'):return report
    b=item.get('bounds') or [0,0,0,0]
    if b[2]<=0 or b[3]<=0:raise RuntimeError('MES 생산일보관리 탭의 위치를 읽지 못했습니다.')
    if stop.is_set():raise module.Stopped('사용자 중지')
    api.click_handle(item['handle'],selection=b)
    emit('log','MES 생산일보관리 탭 클릭 · 화면 전환 확인')
    for _ in range(8):
        if stop.wait(.1):raise module.Stopped('사용자 중지')
        report=capture({**api.target,'mode':'mes_rows'},'MES 생산일보관리 전환 확인',stop)
        if tab(report).get('selected'):
            wash_production_group(module,report)
            return report
    raise RuntimeError('MES 생산일보관리 화면으로 전환되지 않았습니다.')


def wash_production_group(module, report):
    native={r['handle']:r for r in report['records'] if r.get('kind')=='native_window'}
    names={}
    for n in module.nodes(report):
        if n.get('parent')==-1:names.setdefault(n['handle'],set()).add(n.get('name',''))
    def in_production(handle):
        seen=set()
        while handle and handle not in seen:
            seen.add(handle)
            if '생산일보관리' in names.get(handle,set()):return True
            handle=native.get(handle,{}).get('native_parent')
        return False
    groups=[g for g in module.number_groups(report) if in_production(g['panel'])]
    if not groups:raise RuntimeError('MES 생산일보관리 안에서 1~10 버튼을 찾지 못했습니다. 생산일보관리 화면을 열어 주세요.')
    top=min(g['y'] for g in groups);row=sorted((g for g in groups if abs(g['y']-top)<10),key=lambda g:g['x'])
    if len(row)>1 and abs(row[0]['x']-row[1]['x'])<10:raise RuntimeError('생산일보관리 왼쪽 위 칸이 중복됩니다. 해당 화면을 하나만 열어 주세요.')
    return {**row[0],'label':'위쪽 왼쪽의 1~10 버튼'}


def wash_toolbar_profiles(module, report):
    native={r['handle']:r for r in report['records'] if r.get('kind')=='native_window'}
    groups={}
    for n in module.nodes(report):
        if n.get('parent')!=-1 or n.get('role')!=43 or n.get('offscreen'):continue
        b=n.get('bounds') or [0,0,0,0]
        if b[2]<=0 or b[3]<=0:continue
        parent=native.get(n['handle'],{}).get('native_parent')
        if not parent or native.get(parent,{}).get('native_parent')!=report['target']['handle']:continue
        groups.setdefault(parent,[]).append(n)
    result=[]
    for parent,items in groups.items():
        if len(items)<3:continue
        x=min(n['bounds'][0] for n in items);y=min(n['bounds'][1] for n in items)
        def descriptor(n):
            b=n['bounds'];return [n.get('name',''),b[0]-x,b[1]-y,b[2],b[3]]
        ordered=sorted(items,key=descriptor)
        result.append((ordered,[descriptor(n) for n in ordered]))
    return result


def wash_profile_path():
    return Path(os.environ.get('LOCALAPPDATA') or Path.home())/'Jihunius'/'mes_query_button.json'


def wash_save_query_profile(module,report,binding):
    import json,tempfile
    matches=[(items,layout) for items,layout in wash_toolbar_profiles(module,report) if any(n['handle']==binding['handle'] for n in items)]
    if len(matches)!=1:raise RuntimeError('지정 버튼이 MES 상단 도구모음에 없습니다. 상단 조회 버튼을 지정해 주세요.')
    items,layout=matches[0];profile={'layout':layout,'index':next(i for i,n in enumerate(items) if n['handle']==binding['handle'])}
    path=wash_profile_path();path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,delete=False) as f:
        json.dump(profile,f,ensure_ascii=False);tmp=f.name
    os.replace(tmp,path)


def wash_mes_query(module,report,api):
    import json
    profiles=[WASH_MES_QUERY_PROFILE]
    path=wash_profile_path()
    if path.exists():
        try:
            saved=json.loads(path.read_text(encoding='utf-8'))
            if isinstance(saved,dict) and isinstance(saved.get('layout'),list) and type(saved.get('index')) is int:
                profiles.append(saved)
        except (OSError,ValueError):pass
    found={}
    for items,layout in wash_toolbar_profiles(module,report):
        for profile in profiles:
            if layout==profile['layout'] and 0<=profile['index']<len(items):
                n=items[profile['index']];found[n['handle']]=n
    if len(found)!=1:raise RuntimeError('MES 최대화 후 조회 버튼 배치를 확인하지 못했습니다. 생산일보관리 화면을 확인해 주세요.')
    n=next(iter(found.values()))
    if not n.get('enabled'):raise RuntimeError('MES 조회 버튼이 비활성화되어 있습니다. 생산일보관리 화면을 확인해 주세요.')
    h=n['handle'];api.verify(h);r=api.rect(h)
    return {'handle':h,'class':api.text(h,True),'text':api.text(h),'size':[r.right-r.left,r.bottom-r.top],
            'purpose':'query','registered_by':'검증된 도구모음 배치에서 조회 버튼 자동 확인'}


def wash_prepare_window(api,stop):
    """Maximize main MES/POP windows only, then wait for stable geometry."""
    from ctypes import wintypes
    u=api.u;root=api.target['handle']
    u.IsZoomed.argtypes=[wintypes.HWND];u.IsZoomed.restype=wintypes.BOOL
    u.ShowWindowAsync.argtypes=[wintypes.HWND,ctypes.c_int];u.ShowWindowAsync.restype=wintypes.BOOL
    if stop.is_set():raise RuntimeError('사용자 중지')
    api.activate()
    if not u.IsZoomed(root):u.ShowWindowAsync(root,3)
    previous=None;stable=0
    for _ in range(50):
        if stop.is_set() or u.GetAsyncKeyState(0x78)&0x8000:raise RuntimeError('사용자 중지')
        if u.IsZoomed(root) and not u.IsIconic(root):
            r=api.rect(root);current=(r.left,r.top,r.right,r.bottom)
            stable=stable+1 if current==previous else 0
            previous=current
            if stable>=2:
                api.verify(root)
                if u.GetForegroundWindow()!=root:raise RuntimeError('최대화한 창이 다른 창에 가려졌습니다. 다시 시작해 주세요.')
                return {'title':api.target.get('title',''),'handle':root,'maximized':True,'bounds':list(current)}
        else:previous=None;stable=0
        if stop.wait(.1):raise RuntimeError('사용자 중지')
    raise RuntimeError(api.target.get('title','대상')+' 창을 최대화하지 못했습니다. 열린 팝업을 닫고 다시 시작해 주세요.')


def wash_verify_front_group(api,group):
    from ctypes import wintypes
    h=group['buttons'][1];api.verify(h);r=api.rect(h)
    hit=api.u.WindowFromPoint(wintypes.POINT((r.left+r.right)//2,(r.top+r.bottom)//2))
    if hit not in (h,api.u.GetParent(h)):
        raise RuntimeError('MES 생산일보관리의 왼쪽 위 칸이 다른 화면에 가려져 있습니다. MES 안에서 생산일보관리 탭을 선택해 주세요.')


def wash_completion_brief(result,elapsed,error=None):
    """Summarize returned checks only; an interrupted run is never complete."""
    lines=[f'소요 시간: {elapsed:.1f}초']
    if error:
        lines.extend(['','중단 사유: '+str(error),'전체 검사가 끝나지 않았습니다. 현재 체크 상태를 확인해 주세요.'])
    if result:
        matching=result['matching'];source=result.get('mes_source',{})
        skipped=source.get('skipped_blank_program',[])
        matching_issues=sum(len(matching.get(key,[])) for key in ('missing','ambiguous','equipment_mismatch'))
        issues=matching_issues+len(skipped)
        lines.extend(['',f"체크 확인 {len(result.get('verified_checks',[]))}개 · 이미 선택 {len(matching['already_selected'])}개",
                      f'MES↔POP 매칭 확인 필요 {matching_issues}개'])
        if skipped:lines.append(f'MES 프로그램 번호 빈칸 제외 {len(skipped)}개')
        if not source.get('candidates'):
            lines.append('프로그램 번호가 빈 행을 제외하면 MES 매칭 대상이 없습니다.' if skipped else '선택한 MES 호기·세척순번에 해당하는 대상이 없습니다.')
        elif not issues and not error:lines.append('MES 대상이 모두 POP와 매칭됐습니다.')
        if issues and not error and result.get('save_status')=='confirmed':
            lines.append('매칭된 항목은 저장까지 완료했습니다. 아래 제외·미매칭 항목만 별도로 확인해 주세요.')
        def machines(items):
            return ', '.join(dict.fromkeys(f"{r['number']}호기" for r in items if r.get('number') is not None)) or '호기 정보 없음'
        if skipped:
            lines.extend(['','[MES 프로그램 번호 빈칸 · 자동 처리 제외]'])
            for row in skipped:
                displayed=str(row.get('row') or '').strip()
                position=f"표의 {row['row_position']}번째 행"
                if displayed:position+=f' (No. {displayed})'
                lines.append(f"• {row['number']}호기 | {position} | 세척 {row['sequence']} | P/No. 빈칸")
        if matching['missing']:
            lines.extend(['','[POP 목록에 없음]'])
            for project in matching['missing']:
                mes=[r for r in source.get('candidates',[]) if r['project']==project]
                lines.append(f"• {project} | MES {machines(mes)} → POP 조회 결과에 없음")
        if matching['ambiguous']:
            lines.extend(['','[중복으로 자동 체크 제외]'])
            for pair in matching['ambiguous']:
                lines.append(f"• {pair['project']} | MES {len(pair['mes'])}건 ({machines(pair['mes'])}) / POP {len(pair['pop'])}건")
        if matching['equipment_mismatch']:
            lines.extend(['','[호기 불일치로 자동 체크 제외]'])
            for pair in matching['equipment_mismatch']:
                lines.append(f"• {pair['project']} | MES {machines([pair['mes']])} / POP {pair['pop'].get('설비명') or '설비명 없음'}")
    else:issues=0
    save_status=(result or {}).get('save_status','not_started')
    if save_status=='confirmed':lines.extend(['','POP 저장 완료 메시지 확인 · 완료창 닫기 완료'])
    elif save_status=='no_targets':lines.extend(['','저장할 매칭 대상이 없어 저장을 생략했습니다.'])
    elif save_status!='not_started':lines.extend(['','저장 단계가 완료되지 않았습니다. POP 상태를 직접 확인해 주세요.'])
    else:lines.extend(['','POP 저장 버튼은 누르지 않았습니다.'])
    title='작업 중단' if error else ('자동완료 · 확인 필요' if issues else '자동완료')
    return title,'\n'.join(lines)


def append_bounded_log(widget, text, max_lines=100, max_chars=250000):
    """Keep recent on-screen history bounded, and render each event batch once."""
    widget.configure(state='normal')
    try:
        widget.insert('end', text[-max_chars:])
        lines = int(widget.index('end-1c').split('.')[0]) - 1
        if lines > max_lines:
            widget.delete('1.0', '{}.0'.format(lines - max_lines + 1))
        size = (widget.count('1.0', 'end-1c', 'chars') or (0,))[0]
        if size > max_chars:
            widget.delete('1.0', '1.0+{}c'.format(size - max_chars))
        widget.see('end')
    finally:
        widget.configure(state='disabled')


WASH_RUN_MARKER_NAME = "세척완료_실행중.json"
WASH_RUN_MARKER_STALE_SECONDS = 30 * 60


def run_bounded(action, seconds=3.0):
    """공유폴더처럼 느릴 수 있는 확인을 정해진 시간만 기다립니다. 시간 초과·실패는 None."""
    box = {}

    def work():
        try:
            box["value"] = action()
        except Exception:
            box["value"] = None
    thread = threading.Thread(target=work, daemon=True)
    thread.start()
    thread.join(seconds)
    return box.get("value")


class WashRunMarker:
    """여러 PC에서 세척완료를 동시에 실행하는지 알려 주는 공유폴더 표시 파일.

    확인용일 뿐 작업을 막지 않습니다. 공유폴더에 닿지 않거나 파일이 오래되었으면(30분) 없는 것으로 봅니다.
    """

    def __init__(self, folder, pc=None, clock=time.time):
        self.path = Path(folder) / WASH_RUN_MARKER_NAME
        self.pc = pc or os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "이 PC"
        self.clock = clock
        self.token = hashlib.sha1("{}-{}-{}".format(self.pc, os.getpid(), time.monotonic()).encode()).hexdigest()
        self.owned = False

    def other(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError):
            return None
        if not isinstance(data, dict) or data.get("pc") == self.pc:
            return None
        try:
            started = float(data.get("at", 0))
        except (TypeError, ValueError):
            return None
        if not 0 <= self.clock() - started <= WASH_RUN_MARKER_STALE_SECONDS:
            return None
        return data

    def write(self):
        if not self.path.parent.is_dir():
            return False
        temporary = self.path.with_name(self.path.name + "." + self.token[:12] + ".tmp")
        try:
            temporary.write_text(json.dumps({"pc": self.pc, "at": self.clock(), "token": self.token},
                                            ensure_ascii=False), encoding="utf-8")
            os.replace(str(temporary), str(self.path))
            self.owned = True
        except OSError:
            try:
                temporary.unlink()
            except OSError:
                pass
            self.owned = False
        return self.owned

    def release(self):
        if not self.owned:
            return False
        self.owned = False
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("token") == self.token:
                self.path.unlink()
                return True
        except (OSError, ValueError, UnicodeError):
            pass
        return False


class WashApp:
    def __init__(self,host,parent):
        import tkinter as tk
        from tkinter import ttk
        from datetime import date
        self.host=host;self.root=host.window;self.busy=False;self.stop=threading.Event();self.events=queue.Queue()
        self.trail=[];self.reads=[];self.progress={};self.last_result=None;self.started=time.monotonic()
        self.result=None;self.started=0;self.mes_binding=None;self.mes_target=None
        self.capture_stage=None;self.capture_status=None
        self.mes=load_wash_module(WASH_MES_SOURCE,'jihuni_wash_mes')
        self.pop=load_wash_module(WASH_POP_SOURCE,'jihuni_wash_pop')
        style=ttk.Style(self.root)
        style.configure('Wash.TCombobox',fieldbackground='#060b16',background='#0e1a35',foreground='#ffffff',padding=6)
        style.map('Wash.TCombobox',fieldbackground=[('readonly','#060b16')],foreground=[('readonly','#ffffff')],selectbackground=[('readonly','#060b16')],selectforeground=[('readonly','#ffffff')])
        body=ttk.Frame(parent,padding=18);body.pack(fill='both',expand=True)
        ttk.Label(body,text='세척완료',style='Title.TLabel').pack(anchor='w')
        ttk.Label(body,text='MES 1~10호기 전체 확인 → POP 조회·체크 → 저장',font=('맑은 고딕',12,'bold')).pack(anchor='w',pady=(8,6))
        ttk.Label(body,text='체크 검증 후 저장 → 예 → 완료창 닫기까지 자동 진행합니다. 중지: F9',foreground='#93c5fd').pack(anchor='w')
        ttk.Label(body,text='MES 생산일보·POP를 열고 POP 검사일과 작업자 이름을 확인하세요. 시작할 때 두 창을 최대화하고 필요한 창을 자동으로 앞으로 가져옵니다.',wraplength=900).pack(anchor='w',pady=(6,16))
        fields=ttk.Frame(body);fields.pack(fill='x')
        self.pop_date=tk.StringVar(value=date.today().isoformat())
        self.worker=tk.StringVar();self.sequence=tk.StringVar(value='06')
        self.entries=[]
        for i,(label,var,width) in enumerate((('POP 검사일',self.pop_date,12),('작업자',self.worker,10),('세척순번',self.sequence,5))):
            ttk.Label(fields,text=label).grid(row=0,column=i*2,padx=(0,8))
            widget=ttk.Combobox(fields,textvariable=var,values=self.pop.SEQUENCE_VALUES,width=width,state='readonly',style='Wash.TCombobox') if i==2 else ttk.Entry(fields,textvariable=var,width=width)
            widget.grid(row=0,column=i*2+1,padx=(0,16));self.entries.append(widget)
        self.input=self.entries[0]
        actions=ttk.Frame(body);actions.pack(fill='x',pady=18)
        self.run_button=ttk.Button(actions,text='START',command=lambda:self.launch(True),style='Accent.TButton');self.run_button.pack(side='left',padx=10)
        ttk.Button(actions,text='중지 (F9)',command=lambda:self.stop.set(),style='Secondary.TButton').pack(side='left')
        self.status=tk.StringVar(value='대기 중 · 세척순번 기본값 06')
        ttk.Label(body,textvariable=self.status,wraplength=900,foreground='#93c5fd').pack(anchor='w',pady=(0,10))
        self.root.after(80,self.poll)

    def note(self,text):
        """오류가 났을 때 함께 남길 진행 기록. 자동 작업에는 영향을 주지 않습니다."""
        try:
            trail=self.trail
            trail.append('{:7.1f}초  {}'.format(time.monotonic()-self.started,str(text).replace('\n',' ')[:160]))
            del trail[8:-400]    # 처음 8줄과 최근 400줄만 보관
        except Exception:pass

    def diagnostics(self):
        """세척완료가 멈춘 순간의 상황 요약. 오류 기록의 [진단] 자리에 들어갑니다."""
        try:
            lines=['경과 {:.1f}초 · 세척순번 {}'.format(time.monotonic()-self.started,getattr(self,'run_sequence','?'))]
            result=getattr(self,'last_result',None) or {}
            coverage=result.get('coverage') or {}
            if coverage:
                raw=coverage.get('raw') or []
                lines.append('POP 표: 한 줄 {}칸 · 화면에 보이는 줄 {}'.format(
                    len(raw[0]) if raw else '?',len((coverage.get('current_view') or {}).get('visible',()))))
                lines.append('POP 목록 {}줄 · 행 요약값 {} · 맨 위 확인 {} · 맨 아래 확인 {} · 아래로 이동 {}회'.format(
                    coverage.get('declared_rows','?'),'사용' if coverage.get('summary_supported') else '미사용',
                    '예' if coverage.get('top_verified') else '아니오','예' if coverage.get('bottom_verified') else '아니오',
                    sum(1 for item in self.reads if str(item[0]).startswith('POP 아래로 확인'))))
                lines.append('판독 방식: '+str(coverage.get('basis','?')))
            matching=result.get('matching') or {}
            if matching:
                lines.append('매칭 대상 {}개 · 이미 선택 {}개'.format(len(matching.get('matched',())),len(matching.get('already_selected',()))))
            lines.append('체크 클릭 {}회 · 체크 확인 {}개'.format(self.progress.get('attempt',0),self.progress.get('verified',0)))
            if self.reads:
                label,mode,seconds,elements=max(self.reads,key=lambda item:item[2])
                lines.append('화면 판독 {}회 · 합계 {:.1f}초 · 가장 오래: {} ({} · {:.1f}초 · 항목 {}개)'.format(
                    len(self.reads),sum(item[2] for item in self.reads),label,mode,seconds,elements))
                lines.append('마지막 판독: '+' → '.join('{} ({} · {:.1f}초)'.format(item[0],item[1],item[2]) for item in self.reads[-3:]))
            if os.name=='nt':
                try:
                    user=ctypes.windll.user32;front=user.GetForegroundWindow();title=ctypes.create_unicode_buffer(200)
                    user.GetWindowTextW(front,title,200)
                    lines.append('멈춘 순간 맨 앞 창: '+(title.value.strip()[:80] or '(제목 없음)'))
                except Exception:pass
            trail=list(self.trail)
            if len(trail)>40:trail=trail[:8]+['   … {}줄 생략 …'.format(len(trail)-40)]+trail[-32:]
            lines.append('[진행 기록 · 처음 8줄 + 최근 32줄]' if len(self.trail)>40 else '[진행 기록 · {}줄]'.format(len(trail)))
            return '\n'.join(lines+trail)
        except Exception as error:return '진단 정보를 만들지 못했습니다: '+str(error)

    def emit(self,kind,value):
        if kind=='log':self._error_stage=str(value)[:300];self.note(value)
        elif kind=='reading':self._error_stage=str(value[0])[:300]
        elif kind=='check':
            try:self.progress[value.get('status')]=self.progress.get(value.get('status'),0)+1
            except Exception:pass
        elif kind=='result':self.last_result=value
        elif kind=='error' and not self.stop.is_set():
            import traceback
            self.note('중단: '+str(value))
            SuiteErrors.capture(value,feature='세척완료',stage=getattr(self,'_error_stage','처리'),
                                detail=traceback.format_exc(),work=str(self.started),context=self.diagnostics())
        if kind in ('log','error','result','reading','reading_done','done','binding'):
            self.events.put((kind,value))

    def controls(self):
        for button in (self.run_button,):button.configure(state='disabled' if self.busy else 'normal')
        for i,entry in enumerate(self.entries):entry.configure(state='disabled' if self.busy else ('readonly' if i==2 else 'normal'))

    def launch(self,run):
        if defer_ime_commit(self.root, lambda: self.launch(run)):return
        if self.busy:return
        if os.name!='nt':return self.host.messagebox.showinfo('Windows 전용','MES·POP가 실행 중인 Windows PC에서 사용해 주세요.',parent=self.root)
        try:
            expected={'date':self.pop.iso_date(self.pop_date.get()),'worker':self.worker.get().strip(),'sequence':self.sequence.get()}
            if expected['sequence'] not in self.pop.SEQUENCE_VALUES:raise ValueError('세척순번은 01~30 또는 대문자 O를 선택해 주세요.')
            selected_numbers=list(range(1,11))
            if run is True and not expected['worker']:raise ValueError('작업자 이름을 입력해 주세요.')
        except Exception as e:return self.host.messagebox.showerror('조건 확인',str(e),parent=self.root)
        if self.host.busy:return self.host.messagebox.showinfo('작업 중','현재 파일 작업이 끝난 뒤 실행해 주세요.',parent=self.root)
        self.busy=True;self.stop=threading.Event();self.result=None;self.controls();self.started=time.monotonic()
        self.trail=[];self.reads=[];self.progress={};self.last_result=None;self.run_sequence=expected['sequence']
        self.host.suspend_machine_alerts()
        self.capture_stage=None;self.capture_status=None
        self.status.set('창과 조건 확인 중…')
        threading.Thread(target=self.work,args=(run,expected,selected_numbers),daemon=True).start()

    def confirm_other_pc_run(self,other):
        try:at=time.strftime('%H:%M',time.localtime(float(other.get('at',0))))
        except (TypeError,ValueError,OverflowError,OSError):at='조금 전'
        message=('다른 PC({})에서 {}부터 세척완료를 실행 중입니다.\n'
                 '같이 실행하면 같은 항목이 두 번 처리될 수 있습니다.\n\n그래도 진행할까요?').format(other.get('pc','알 수 없음'),at)
        return self.host.messagebox.askyesno('세척완료 동시 실행 확인',message,parent=self.root)

    def work(self,run,expected,selected_numbers):
        reader=None;finished_result=None;failure=None;marker=None
        try:
            if run is True:
                # 여러 PC 동시 실행 확인(공유폴더). 닿지 않으면 확인 없이 그대로 진행합니다.
                marker=WashRunMarker(Path(HANDOVER_SHARED_PARENT)/HANDOVER_FOLDER_NAME)
                other=run_bounded(marker.other)
                if other and not self.host.request_ui(self.confirm_other_pc_run,other):
                    marker=None
                    raise RuntimeError('다른 PC에서 실행 중이라 시작하지 않았습니다.')
                run_bounded(marker.write)
            windows=self.pop.visible_windows()
            def target(title):
                matches=[w for w in windows if w['title']==title]
                if len(matches)!=1:raise RuntimeError(title+' 창을 하나만 실행해 주세요.')
                return matches[0]
            mes_target=target('ROOT MES');pop_target=target('현장관리')
            ma=self.mes.WindowsClicks(mes_target);pa=self.pop.WindowsClicks(pop_target)
            self.pop.SEQUENCE=expected['sequence']
            # Start compilation while the two windows finish maximizing.
            reader=WashReader(self.pop)
            for api in (pa,ma):
                self.emit('log',api.target['title']+' 최대화 상태 확인 중…')
                state=wash_prepare_window(api,self.stop)
                self.emit('log',state['title']+' 최대화 확인 완료')
            def capture(t,label,stop):
                started=time.monotonic()
                self.emit('reading',(label,started))
                try:
                    report=reader.capture(t,label,stop)
                    try:
                        finish=[r for r in report.get('records',()) if isinstance(r,dict) and r.get('kind')=='finish']
                        self.reads.append((label,t.get('mode','full'),time.monotonic()-started,finish[-1].get('elements','?') if finish else '?'))
                        if time.monotonic()-started>=5:self.note('판독 {:.1f}초 · {} · {}'.format(time.monotonic()-started,label,t.get('mode','full')))
                    except Exception:pass
                    return report
                except Exception as error:
                    elapsed=time.monotonic()-started
                    self.note('판독 실패 {:.1f}초 · {} · {}'.format(elapsed,label,t.get('mode','full')))
                    raise RuntimeError(f'{label} · {elapsed:.1f}초 경과 · {error}') from error
                finally:
                    self.emit('reading_done',None)
            ma.activate()
            mr=capture({**mes_target,'mode':'mes_rows'},'MES 구조',self.stop)
            mr=wash_ensure_mes_production(self.mes,ma,mr,capture,self.stop,self.emit)
            group=wash_production_group(self.mes,mr)
            wash_verify_front_group(ma,group)
            pa.activate()
            pr=capture({**pop_target,'mode':'mes_rows'},'POP 조건',self.stop)
            pr=self.pop.ensure_inspection_screen(pop_target,pa,capture,self.stop,self.emit,initial_report=pr)
            actual=self.pop.read_conditions(pr)
            self.pop.validate_conditions(pr,{**expected,'date':actual['date'],'worker':actual['worker']},check_sequence=False)
            mb=wash_mes_query(self.mes,mr,ma)
            pb=wash_query_binding(self.pop,pr,pa,True)
            self.emit('log','조회 버튼 자동 확인 완료. 시작합니다. 실행 중에는 마우스·키보드 조작을 멈춰 주세요.')
            ma.activate()
            wash_verify_front_group(ma,group)
            if self.stop.is_set():raise RuntimeError('사용자 중지')
            original_number=ma.selected_number(group)
            self.emit('log',f'MES 시작 전 선택 번호 {original_number}번 기억')
            steps=[]
            def mes_emit(kind,value):
                if kind=='step':
                    steps.append(value);self.emit('log',f"{value['number']}호기 · {value['scroll_coverage']['seen_rows']}행 전체 확인")
                if kind!='capture':self.emit(kind,value)
            try:
                self.mes.cycle_steps(mes_target,group,mb,ma,capture,self.stop,mes_emit,numbers=selected_numbers)
            except Exception:
                # A stop request must stop all input, including restoration clicks.
                if not self.stop.is_set() and not ma.u.GetAsyncKeyState(0x78)&0x8000:
                    try:
                        ma.restore_number(group,original_number,self.stop)
                        self.emit('log',f'MES 원래 선택 번호 {original_number}번 복귀 완료')
                    except Exception as restore_error:self.emit('log','MES 원래 번호 복귀 보류: '+str(restore_error))
                raise
            ma.restore_number(group,original_number,self.stop)
            self.emit('log',f'MES 원래 선택 번호 {original_number}번 복귀 완료')
            source=wash_source(self.pop,steps,group,expected['sequence'],selected_numbers=selected_numbers)
            self.emit('log',f"세척{expected['sequence']} 대상 {len(source['candidates'])}개 수집 완료")
            # ensure_worker activates POP and waits before reading its conditions.
            # Always query POP, even when MES has no candidates.
            def pop_emit(kind,value):
                if kind!='capture':self.emit(kind,value)
            worker_result=self.pop.ensure_worker(pop_target,expected['worker'],capture,self.stop,pop_emit)
            date_report=self.pop.ensure_inspection_date(pop_target,expected['date'],pa,capture,self.stop,pop_emit,initial_report=worker_result['report'])
            result=self.pop.pop_steps(pop_target,pb,expected,source,pa,capture,self.stop,pop_emit,initial_report=date_report)
            matching=result['matching']
            self.emit('log',f"매칭 대상 체크 {len(result.get('verified_checks',[]))}개 · 이미 선택 {len(matching['already_selected'])}개 · 저장 단계 진행")
            finished_result=result
            self.pop.save_checked_pop(pop_target,expected,result,pa,capture,self.stop,pop_emit)
        except Exception as e:
            failure=str(e);self.emit('error',failure)
        finally:
            if reader:
                try:reader.close()
                except Exception as e:self.emit('log','판독기 종료: '+str(e))
            if marker is not None:run_bounded(marker.release)
            self.emit('done',{'elapsed':time.monotonic()-self.started,'result':finished_result,'error':failure})

    def show_completion(self,title,brief):
        import tkinter as tk
        from tkinter import ttk
        dialog=tk.Toplevel(self.root);dialog.title(title);dialog.configure(bg='#050a14')
        dialog.transient(self.root)
        width=min(760,dialog.winfo_screenwidth()-80);height=min(540,dialog.winfo_screenheight()-100)
        x=max(0,(dialog.winfo_screenwidth()-width)//2);y=max(0,(dialog.winfo_screenheight()-height)//2)
        dialog.geometry(f'{width}x{height}+{x}+{y}');dialog.minsize(min(520,width),min(320,height))
        body=ttk.Frame(dialog,padding=18);body.pack(fill='both',expand=True)
        ttk.Label(body,text=title,font=('맑은 고딕',17,'bold')).pack(anchor='w',pady=(0,12))
        area=ttk.Frame(body);area.pack(fill='both',expand=True)
        text=tk.Text(area,bg='#050a14',fg='#eaf0fc',font=('맑은 고딕',11),wrap='word',relief='flat',padx=8,pady=8)
        scroll=ttk.Scrollbar(area,orient='vertical',command=text.yview);text.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y');text.pack(side='left',fill='both',expand=True)
        text.insert('1.0',brief);text.configure(state='disabled')
        button=ttk.Button(body,text='확인',command=dialog.destroy,style='Accent.TButton')
        button.pack(side='right',pady=(14,0));dialog.bind('<Escape>',lambda e:dialog.destroy())
        dialog.lift();dialog.attributes('-topmost',True)
        dialog.after(300,lambda:dialog.winfo_exists() and dialog.attributes('-topmost',False))
        dialog.grab_set();button.focus_set()

    def poll(self):
        if self.busy and os.name=='nt' and ctypes.windll.user32.GetAsyncKeyState(0x78)&0x8000:self.stop.set()
        completion=None;deadline=time.monotonic()+.012
        try:
            for _ in range(200):
                if time.monotonic()>=deadline:break
                kind,value=self.events.get_nowait()
                if kind=='binding':self.mes_target,self.mes_binding=value
                elif kind=='result':self.result=value
                elif kind=='reading':self.capture_stage=value;self.capture_status=None
                elif kind=='reading_done':self.capture_stage=None;self.capture_status=None
                elif kind in ('log','error'):
                    line=('중단: ' if kind=='error' else '')+str(value)
                    self.status.set(line)
                elif kind=='done':
                    self.busy=False;self.controls();self.capture_stage=None
                    title,brief=wash_completion_brief(value['result'] or self.result,value['elapsed'],value['error'])
                    self.status.set(title+f" · {value['elapsed']:.1f}초")
                    self.result=None
                    completion=(title,brief)
        except queue.Empty:pass
        finally:
            self.root.after(80,self.poll)
        if self.busy and self.capture_stage:
            label,started=self.capture_stage
            elapsed=int(time.monotonic()-started)
            state=(label,elapsed,self.stop.is_set())
            if state!=self.capture_status:
                self.capture_status=state
                self.status.set(('중지 요청 처리 중' if state[2] else '화면 읽는 중')+f' · {label} · {elapsed}초')
        if completion:self.show_completion(*completion)




# Separate companion processes preserve their original Tk styles and save paths.
def _suite_load_support(name, text):
    import types
    module = types.ModuleType(name)
    exec(compile(text, __file__ + ' [' + name + ']', 'exec'), module.__dict__)
    return module

SuiteWindowState = ...  # build: tools/build_app.py
SuiteCompanionManager = ...  # build: tools/build_app.py
SuiteWindowsTray = ...  # build: tools/build_app.py
SUITE_COMPANIONS = ...  # build: tools/build_app.py

def suite_companion_payloads():
    import base64
    import zlib
    return {key: {'title': value['title'], 'sha256': value['sha256'],
                  'data': zlib.decompress(base64.b64decode(value['compressed']))}
            for key, value in SUITE_COMPANIONS.items()}


SuiteVisualTheme = ...  # build: tools/build_app.py

SuiteErrors = ...  # build: tools/build_app.py

SuiteMaterialQuick = ...  # build: tools/build_app.py

class IntegrationApp:
    def __init__(self, window):
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog

        self.tk = tk
        self.ttk = ttk
        self.messagebox = messagebox
        self.filedialog = filedialog
        self.window = window
        self.destination = None
        self.program_base_root = load_program_base_root()
        self.program_path_dialog = None
        self.events = queue.Queue()
        self.busy = False
        self.card_modifier_pending = False
        self.card_modifier_signature = None
        self.drive_refresh_loading = False
        self.drive_refresh_generation = 0
        self.drive_refresh_pending = False
        self.drive_snapshot = None
        self.drive_select_path = None
        self.drive_action_pending = None
        self.machine_samples = {}
        self.machine_failures = set()
        self.machine_conflicts = set()
        self.machine_alert_enabled, self.machine_alert_selected, self.machine_alert_sound, self.machine_alert_volume, self.machine_alert_sound_kind = load_machine_alert_settings()
        self.machine_alert_tracker = MachineAlertTracker()
        self.machine_alert_pending = {}
        self.machine_alert_toast = None
        self.machine_alert_timer = None
        self.machine_alert_displayed = []
        self.machine_alert_settings_dialog = None
        self.machine_alert_retry_at = 0
        self.machine_alert_last_error = None
        self.machine_alert_test_index = 0
        self.machine_monitor_error = None
        self.machine_monitor = MachineMonitor(self.events)
        self.handover_store = HandoverStore()
        self.handover_notes = {}
        self.handover_dialog = None
        self.handover_signature = None
        self.handover_expanded = False
        self.handover_read_error = False
        self.handover_added_width = 0
        self.handover_left_shift = 0
        self.handover_loading = False
        self.handover_refresh_pending = False
        self.handover_writing = False
        self.style = configure_app_style(window)
        self.app_icons = load_app_icons(window)
        self.logo_image = self.app_icons[32]

        window.title("지후니우스")
        window.geometry("1120x830")
        window.minsize(1000, 740)
        window.protocol("WM_DELETE_WINDOW", self.close)
        frame = ttk.Frame(window, padding=18)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        outer_frame = frame
        frame.rowconfigure(1, weight=1)

        header = ttk.Frame(frame)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)
        title_row = ttk.Frame(header)
        title_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.logo_label = ttk.Label(title_row, image=self.logo_image)
        self.logo_label.pack(side="left", padx=(0, 12))
        self.title_label = ttk.Label(title_row, text="지후니우스", style="Title.TLabel")
        self.title_label.pack(side="left")
        ttk.Separator(title_row, orient="vertical").pack(side="left", fill="y", padx=14, pady=4)
        self._suite_buttons = {}
        for key, label in (("wash-log", "세척일보"), ("protrusion", "돌출량"), ("special-table", "특수 돌출량"), ("material", "소재 사용량 조사(Beta)")):
            button = ttk.Button(title_row, text=label, style="Popup.TButton",
                                command=lambda selected=key: self.open_companion(selected))
            button.pack(side="left", padx=(0, 2))
            self._suite_buttons[key] = button
        self.material_button = self._suite_buttons['material']

        navigation_row = ttk.Frame(header)
        navigation_row.grid(row=1, column=0, sticky="ew")
        navigation_row.columnconfigure(1, weight=1, minsize=170)
        navigation_row.rowconfigure(0, minsize=46)
        tabs = ttk.Frame(navigation_row, style="NavRail.TFrame", padding=3)
        tabs.grid(row=0, column=0, sticky="w")
        self.active_tab = "cnc"
        self.tab_focus = {}
        self.tab_buttons = {}
        for key, label in (("cnc", "지후니우스"), ("stl", "STL찾기"), ("wash", "세척완료")):
            button = ttk.Button(tabs, text=label, style="AppTab.TButton",
                                command=lambda selected=key: self.select_app_tab(selected))
            button.pack(side="left", padx=1)
            self.tab_buttons[key] = button
        self.status = tk.StringVar(value="대기 중")
        self.handover_toggle = ttk.Button(navigation_row, text="인수인계 ▸", command=self.toggle_handover,
                                          style="HandoverToggle.TButton")
        self.handover_toggle.place(relx=0.7, rely=0.5, anchor="center")
        # 오류 기록·업데이트 알림 버튼은 제목 줄 오른쪽. before=로 왼쪽 버튼들보다 먼저 자리를 받아
        # 창이 좁아도 잘리지 않습니다. 상태 표시는 탭 줄 오른쪽에 둡니다.
        self.header_actions = ttk.Frame(title_row)
        self.header_actions.pack(side="right", before=self.logo_label)
        self.header_status_label = self.make_stable_status_label(
            navigation_row, self.status, "Status.TLabel", width=24, anchor="center")
        self.header_status_label.grid(row=0, column=2, sticky="e", padx=(12, 0))
        for widget in (navigation_row, tabs, self.header_actions, self.header_status_label, self.handover_toggle,
                       self.material_button):
            widget.bind("<Configure>", lambda event: self.window.after_idle(self.position_handover_button), add="+")
        self.window.after_idle(self.position_handover_button)


        # 공통 인수인계 영역은 두 탭 밖에 두어 어느 화면에서도 사용할 수 있습니다.
        common_body = ttk.Frame(outer_frame)
        common_body.grid(row=1, column=0, sticky="nsew")
        common_body.columnconfigure(1, weight=1)
        common_body.rowconfigure(0, weight=1)
        self.body = common_body
        page_host = ttk.Frame(common_body)
        page_host.grid(row=0, column=1, sticky="nsew")
        page_host.rowconfigure(0, weight=1)
        page_host.columnconfigure(0, weight=1)
        self.app_pages = {key: ttk.Frame(page_host) for key in ("cnc", "stl", "wash")}
        frame = self.app_pages["cnc"]
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        self.stl_app = None

        modes = ttk.Frame(frame, style="Card.TFrame", padding=15)
        modes.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(modes, text="작업 모드", style="Section.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 18))
        self.mode = tk.StringVar(value=MODE_BOTH)
        self.mode_buttons = []
        for column, (value, label) in enumerate(MODE_LABELS.items(), 1):
            modes.columnconfigure(column, weight=1)
            button = ttk.Radiobutton(modes, text=label, variable=self.mode, value=value,
                                     command=self.update_mode, style="Mode.TRadiobutton")
            button.grid(row=0, column=column, sticky="ew", padx=(0, 8 if column < 3 else 0))
            self.mode_buttons.append(button)
        list_options = ttk.Frame(modes, style="Card.TFrame", borderwidth=0)
        list_options.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        list_options.columnconfigure(1, weight=1)
        list_choices = ttk.Frame(list_options, style="Card.TFrame", borderwidth=0)
        list_choices.grid(row=0, column=0, sticky="w")
        date_options = ttk.Frame(list_options, style="Card.TFrame", borderwidth=0)
        date_options.grid(row=0, column=1, sticky="w", padx=(18, 0))
        ttk.Label(list_choices, text="리스트 파일명", style="Caption.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 14))
        self.list_number = tk.StringVar(value=DEFAULT_LIST_NUMBER)
        self.list_buttons = []
        for column, number in enumerate(LIST_NUMBERS, 1):
            button = ttk.Radiobutton(list_choices, text="O" + number, variable=self.list_number, value=number,
                                     command=self.update_mode, style="Mode.TRadiobutton", width=7)
            button.grid(row=0, column=column, padx=(0, 8))
            self.list_buttons.append(button)
        ttk.Label(date_options, text="연도", style="Caption.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 10))
        self.saved_program_year = load_program_year()
        self.year_value = tk.StringVar(value=str(self.saved_program_year))
        self.year_input = ttk.Entry(date_options, textvariable=self.year_value, width=6, font=("Consolas", 12))
        self.year_input.grid(row=0, column=1, sticky="w")
        ttk.Label(date_options, text="날짜 폴더", style="Caption.TLabel").grid(
            row=0, column=2, sticky="w", padx=(18, 10))
        self.folder_input = ttk.Entry(date_options, width=8, font=("Consolas", 12))
        self.folder_input.grid(row=0, column=3, sticky="w")
        # 오늘 날짜를 미리 넣어 둡니다(예: 11.10). 입력칸에 들어가면 전체 선택되어 바로 고쳐 쓸 수 있습니다.
        today = datetime.now()
        self.folder_input.insert(0, "{}.{:02d}".format(today.month, today.day))
        self.folder_input.bind("<FocusIn>", lambda event: event.widget.select_range(0, "end"), add="+")
        self.program_path_button = ttk.Button(date_options, text="경로설정", style="Secondary.TButton",
                                              command=self.configure_program_path)
        self.program_path_button.grid(row=0, column=4, sticky="w", padx=(12, 0))
        options_layout = [None]

        def arrange_program_options(event):
            # Keep date and path controls together when display scaling narrows the row.
            stacked = event.width < list_choices.winfo_reqwidth() + date_options.winfo_reqwidth() + 18
            if options_layout[0] == stacked: return
            options_layout[0] = stacked
            date_options.grid_configure(row=1 if stacked else 0, column=0 if stacked else 1,
                columnspan=2 if stacked else 1, padx=(0 if stacked else 18, 0),
                pady=(6 if stacked else 0, 0))

        list_options.bind('<Configure>', arrange_program_options, add='+')
        self.mode_help = tk.StringVar()

        body = ttk.Frame(frame)
        self.cnc_body = body
        body.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        body.columnconfigure(0, weight=0, minsize=0)
        body.columnconfigure(1, weight=1, minsize=250)
        body.columnconfigure(2, weight=1, minsize=250)
        body.columnconfigure(3, weight=3, minsize=350)
        body.rowconfigure(0, weight=1)
        drive_card = self.build_drive_card(body)

        inputs = ttk.Frame(body, style="Card.TFrame", padding=15)
        inputs.grid(row=0, column=2, sticky="nsew", padx=(0, 14))
        inputs.columnconfigure(0, weight=1)
        inputs.rowconfigure(1, weight=1)
        ttk.Label(inputs, text="프로그램 번호", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6))
        self.number_input = tk.Text(inputs, width=12, height=8, font=("Consolas", 12), wrap="word", undo=True,
                                    background="#050a14", foreground="#eaf0fc", insertbackground="#8db3ff",
                                    selectbackground="#1d3f86", selectforeground="#eaf0fc", relief="flat",
                                    highlightthickness=1, highlightbackground="#2e333d", highlightcolor="#2a66f2",
                                    padx=10, pady=6)
        self.number_input.grid(row=1, column=0, sticky="nsew")
        number_scrollbar = ttk.Scrollbar(inputs, orient="vertical", command=self.number_input.yview)
        number_scrollbar.grid(row=1, column=1, sticky="ns")
        self.number_input.configure(yscrollcommand=number_scrollbar.set)
        self.number_input.bind("<Control-Return>", self.import_shortcut)
        self.folder_input.bind("<Control-Return>", self.import_shortcut)
        self.year_input.bind("<Control-Return>", self.import_shortcut)

        actions = ttk.Frame(inputs, style="Card.TFrame", borderwidth=0)
        actions.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.import_button = ttk.Button(actions, text=MODE_LABELS[MODE_BOTH], command=self.start_import,
                                        style="Accent.TButton")
        self.import_button.pack(fill="x")

        self.build_machine_board(frame)

        log_card = ttk.Frame(body, style="Card.TFrame", padding=15)
        self.log_card = log_card
        log_card.grid(row=0, column=3, sticky="nsew")
        log_card.columnconfigure(0, weight=1)
        log_card.rowconfigure(1, weight=1)
        ttk.Label(log_card, text="작업 기록 · 최근 100줄", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.log = tk.Text(log_card, width=30, height=10, font=("맑은 고딕", 9), wrap="word", state="disabled",
                           background="#050a14", foreground="#aebcd8", relief="flat", borderwidth=0,
                           highlightthickness=1, highlightbackground="#2e333d", highlightcolor="#2e333d",
                           padx=10, pady=6)
        self.log.grid(row=1, column=0, sticky="nsew")
        log_scrollbar = ttk.Scrollbar(log_card, orient="vertical", command=self.log.yview)
        log_scrollbar.grid(row=1, column=1, sticky="ns")
        self.log.configure(yscrollcommand=log_scrollbar.set)
        self.handover_card = self.build_handover_panel(common_body)
        self.handover_card.grid_remove()
        self.append_log("번호 입력 후 실행(Ctrl+Enter) · 날짜 폴더는 월 폴더 자동 선택(예: 10.13 → 10월/10.13)\n"
                        "F 드라이브 우선(없으면 G) · 드라이브는 '드라이브 비우기'를 눌렀을 때만 비웁니다.\n")
        self.update_mode()
        self.refresh_destination()
        self.refresh_handover()
        window.update_idletasks()
        self.drive_drop = None
        if os.name == "nt":
            try:
                self.drive_drop = WindowsFileDrop(self.drive_contents.winfo_id(), self.events,
                                                  lambda: (self.destination, self.busy))
            except (OSError, AttributeError) as error:
                self.drive_hint.set("추가 버튼으로 파일 선택 · Delete: 삭제\n더블클릭: 열기 · F2: 이름 변경\n수정10.30 자동 추가 · 비우기 시 보존")
                self.append_log("파일 드래그 연결 실패: {}\n추가 버튼으로 파일을 추가할 수 있습니다.\n".format(error))
        body_minimum = max(drive_card.winfo_reqheight(), inputs.winfo_reqheight(), log_card.winfo_reqheight())
        body.rowconfigure(0, minsize=body_minimum)
        frame.rowconfigure(2, minsize=body_minimum)
        minimum_height = outer_frame.winfo_reqheight()
        self.minimum_height = max(740, minimum_height)
        window.minsize(1000, self.minimum_height)
        window.geometry("1120x{}".format(max(830, minimum_height)))
        self.stl_app = load_stl_finder().App(window, self.app_pages["stl"])
        self.wash_app = WashApp(self, self.app_pages["wash"])
        self.apply_visual_theme()
        window.update_idletasks()
        body_minimum = max(drive_card.winfo_reqheight(), inputs.winfo_reqheight(), log_card.winfo_reqheight())
        body.rowconfigure(0, minsize=body_minimum)
        frame.rowconfigure(2, minsize=body_minimum)
        self.minimum_height = max(740, outer_frame.winfo_reqheight())
        window.minsize(1000, self.minimum_height)
        window.geometry("1120x{}".format(max(830, self.minimum_height)))
        # Recalculate for real header geometry changes (font/theme/resize),
        # while transient status messages retain a fixed one-line footprint.
        layout_pending = [None]
        def sync_visual_height():
            layout_pending[0] = None
            if not window.winfo_exists():
                return
            required = max(740, outer_frame.winfo_reqheight())
            if required != self.minimum_height:
                self.minimum_height = required
                minimum_width, unused_height = window.minsize()
                window.minsize(minimum_width, required)
        def schedule_visual_height(event=None):
            if layout_pending[0] is None:
                layout_pending[0] = window.after_idle(sync_visual_height)
        header.bind("<Configure>", schedule_visual_height, add="+")
        self.select_app_tab("cnc")
        self.folder_input.focus_set()
        window.after(80, self.drain_events)
        window.after(1000, self.poll_destination)
        window.after(2500, self.poll_handover)
        self.machine_monitor.start()
        window.after(1000, self.expire_machine_status)
        window.after(200, self.poll_machine_alerts)
        self.initialize_suite()
        self._window_state = SuiteWindowState.CompanionWindowState(window, 'jihunius')

    def make_stable_status_label(self, parent, variable, style, **options):
        """One-line status with fixed requested width and full text on hover."""
        from tkinter import font as tkfont
        label = self.ttk.Label(parent, style=style, wraplength=0, **options)
        cache = {}
        label._status_tip = None

        def hide_tip(event=None):
            if label._status_tip is not None:
                label._status_tip.destroy()
                label._status_tip = None

        def fit_text(*unused):
            raw = variable.get()
            text = " ".join(raw.splitlines())
            font_spec = self.style.lookup(style, 'font') or 'TkDefaultFont'
            width = label.winfo_width()
            requested = label.winfo_reqwidth()
            key = (raw, width, requested, str(font_spec))
            if cache.get('key') == key:
                return
            cache['key'] = key
            font = tkfont.Font(root=self.window, font=font_spec)
            # Positive ttk label widths count zero-glyph cells. The remaining
            # requested width is the theme's actual border and padding budget.
            insets = max(0, requested - int(label.cget('width')) * font.measure('0'))
            width = max(0, width - insets)
            if font.measure(text) > width:
                low, high = 0, len(text)
                while low < high:
                    middle = (low + high + 1) // 2
                    if font.measure(text[:middle] + '…') <= width:
                        low = middle
                    else:
                        high = middle - 1
                text = text[:low] + '…'
            label.configure(text=text)
            cache['shortened'] = text != raw
            if not cache['shortened']:
                hide_tip()

        def show_tip(event=None):
            if not cache.get('shortened') or label._status_tip is not None:
                return
            tip = self.tk.Toplevel(label)
            label._status_tip = tip
            tip.withdraw(); tip.overrideredirect(True)
            self.ttk.Label(tip, textvariable=variable, style=style,
                           wraplength=420, justify='left', padding=10).pack()
            tip.update_idletasks()
            left = label.winfo_vrootx()
            right = left + label.winfo_vrootwidth()
            bottom = label.winfo_vrooty() + label.winfo_vrootheight()
            x = max(left, min(label.winfo_rootx(), right - tip.winfo_reqwidth()))
            y = label.winfo_rooty() + label.winfo_height() + 4
            if y + tip.winfo_reqheight() > bottom:
                y = max(label.winfo_vrooty(), label.winfo_rooty() - tip.winfo_reqheight() - 4)
            tip.geometry('+{}+{}'.format(x, y)); tip.deiconify()

        trace = variable.trace_add('write', fit_text)
        def dispose(event):
            if event.widget == label:
                hide_tip()
                variable.trace_remove('write', trace)
        label.bind('<Configure>', fit_text, add='+')
        label.bind('<Enter>', show_tip, add='+')
        for event in ('<Leave>', '<ButtonPress>', '<Unmap>'):
            label.bind(event, hide_tip, add='+')
        label.bind('<Destroy>', dispose, add='+')
        fit_text()
        return label

    def select_app_tab(self, selected):
        if defer_ime_commit(self.window, lambda: self.select_app_tab(selected)):return
        if selected not in self.app_pages:
            return
        focused = self.window.focus_get()
        current_page = self.app_pages[self.active_tab]
        if focused is not None and str(focused).startswith(str(current_page) + "."):
            self.tab_focus[self.active_tab] = focused
        for key, page in self.app_pages.items():
            if key == selected:
                page.grid(row=0, column=0, sticky="nsew")
            else:
                page.grid_remove()
            self.tab_buttons[key].configure(style="Selected.AppTab.TButton" if key == selected else "AppTab.TButton")
        self.active_tab = selected
        target = self.tab_focus.get(selected)
        if target is None or not target.winfo_exists():
            target = self.folder_input if selected == "cnc" else (self.stl_app.input if selected == "stl" else self.wash_app.input)
        target.focus_set()

    def refresh_active_tab(self, event=None):
        if self.active_tab == "cnc":
            return self.refresh_drive_manual(event)

    def machine_alert_toggle_layout(self):
        """글자 폭·높이에 맞춘 스위치 위치. 100% 배율에서는 기존 좌표(81, 8 / 14, 34)와 같습니다."""
        layout = getattr(self, '_machine_alert_layout', None)
        if layout is not None:
            return layout
        try:
            from tkinter import font as tkfont
            bold = tkfont.Font(root=self.window, family='맑은 고딕', size=10, weight='bold')
            small = tkfont.Font(root=self.window, family='맑은 고딕', size=9)
            label_w = max(bold.measure('머신 알림'), small.measure('9대 선택'))
            line1, line2 = bold.metrics('linespace'), small.metrics('linespace')
            switch_x = max(81, 4 + label_w + 10)
            height = max(48, line1 + line2 + 8)
            top = (height - line1 - line2) / 2
            layout = dict(switch_x=switch_x, switch_y=max(8, (height - 32) // 2), width=max(174, switch_x + 93),
                          height=height, label_y=max(14, top + line1 / 2), count_y=max(34, top + line1 + line2 / 2))
        except Exception:
            layout = dict(switch_x=81, switch_y=8, width=174, height=48, label_y=14, count_y=34)
        self._machine_alert_layout = layout
        return layout

    def update_machine_alert_toggle(self):
        canvas = self.machine_alert_toggle
        enabled = self.machine_alert_enabled
        layout = self.machine_alert_toggle_layout()
        if int(canvas.cget('width')) != layout['width'] or int(canvas.cget('height')) != layout['height']:
            canvas.configure(width=layout['width'], height=layout['height'])
        canvas.delete('all')
        x, y = layout['switch_x'], layout['switch_y']
        canvas.create_text(4, layout['label_y'], text='머신 알림', anchor='w', fill='#eaf0fc', font=('맑은 고딕', 10, 'bold'))
        canvas.create_text(4, layout['count_y'], text='{}대 선택'.format(len(self.machine_alert_selected)), anchor='w',
                           fill='#9fb2d6', font=('맑은 고딕', 9))
        canvas.create_image(x, y, anchor='nw', image=self.machine_alert_switch_images[enabled])
        canvas.create_text(x + (31 if enabled else 56), y + 16, text='ON' if enabled else 'OFF',
                           fill='#ffffff', font=('맑은 고딕', 10, 'bold'))

    def commit_machine_alert_settings(self, enabled, selected, sound=None, volume=None, sound_kind=None):
        sound = self.machine_alert_sound if sound is None else bool(sound)
        volume = self.machine_alert_volume if volume is None else normalize_machine_alert_volume(volume)
        sound_kind = self.machine_alert_sound_kind if sound_kind is None else sound_kind
        sound_kind = 'system' if sound_kind == 'system' else 'tap'
        try:
            save_machine_alert_settings(enabled, selected, sound, volume, sound_kind)
        except OSError as error:
            self.messagebox.showerror('알림 설정 저장 실패', str(error), parent=self.window)
            return False
        if enabled != self.machine_alert_enabled or set(selected) != self.machine_alert_selected:
            self.suspend_machine_alerts()
            self.machine_alert_pending = {n:e for n,e in self.machine_alert_pending.items() if enabled and n in selected}
            if enabled and not self.machine_alert_enabled:
                self.machine_alert_tracker.previous.clear()
                self.machine_alert_tracker.last_seen.clear()
                self.machine_alert_tracker.sources.clear()
                self.machine_alert_tracker.observe(self.current_machines, False, selected)
            self.machine_alert_retry_at = 0
        self.machine_alert_enabled = enabled
        self.machine_alert_selected = set(selected)
        self.machine_alert_sound = sound
        self.machine_alert_volume = volume
        self.machine_alert_sound_kind = sound_kind
        self.update_machine_alert_toggle()
        return True

    def toggle_machine_alerts(self):
        self.commit_machine_alert_settings(not self.machine_alert_enabled, self.machine_alert_selected)

    def show_machine_alert_settings(self):
        existing = self.machine_alert_settings_dialog
        if existing is not None and existing.winfo_exists():
            existing.lift(); return
        dialog = self.tk.Toplevel(self.window)
        self.machine_alert_settings_dialog = dialog
        dialog.title('머신 알림 설정'); dialog.transient(self.window)
        dialog.configure(background='#060b16'); dialog.resizable(False, False)
        frame = self.ttk.Frame(dialog, padding=22); frame.pack(fill='both', expand=True)
        self.ttk.Label(frame, text='알림 받을 호기', style='Subtitle.TLabel').pack(anchor='w')
        self.ttk.Label(frame, text='초록 → 빨강·노랑·회색일 때 호기 완료 알림\n프로그램번호 변경·초록 복귀 시 알림 없음',
                       justify='left').pack(anchor='w', pady=(8, 16))
        enabled = self.tk.BooleanVar(value=self.machine_alert_enabled)
        sound = self.tk.BooleanVar(value=self.machine_alert_sound)
        self.machine_alert_sound_var = sound
        self.tk.Checkbutton(frame, text='머신 알림 켜기', variable=enabled, background='#060b16',
                            foreground='#eaf0fc', selectcolor='#0e1a35', activebackground='#060b16',
                            activeforeground='#ffffff', font=('맑은 고딕', 10),
                            highlightthickness=0).pack(anchor='w', pady=(0, 10))
        self.tk.Checkbutton(frame, text='알림 소리 켜기', variable=sound, background='#060b16',
                            foreground='#eaf0fc', selectcolor='#0e1a35', activebackground='#060b16',
                            activeforeground='#ffffff', font=('맑은 고딕', 10),
                            highlightthickness=0).pack(anchor='w', pady=(0, 10))
        sound_kind = self.tk.StringVar(value=self.machine_alert_sound_kind)
        sound_choices = self.ttk.Frame(frame); sound_choices.pack(fill='x', pady=(0, 10))
        for label, value in (('기본 시스템 소리', 'system'), ('톡 소리', 'tap')):
            self.tk.Radiobutton(sound_choices, text=label, value=value, variable=sound_kind,
                                background='#060b16', foreground='#eaf0fc', selectcolor='#0e1a35',
                                activebackground='#060b16', activeforeground='#ffffff', highlightthickness=0,
                                command=lambda: update_volume_state()).pack(side='left', padx=(0, 16))
        volume = self.tk.DoubleVar(value=self.machine_alert_volume)
        volume_text = self.tk.StringVar(value='음량 {}%'.format(self.machine_alert_volume))
        volume_row = self.ttk.Frame(frame); volume_row.pack(fill='x', pady=(0, 14))
        self.ttk.Label(volume_row, textvariable=volume_text, width=12).pack(side='left')
        volume_scale = self.ttk.Scale(volume_row, from_=0, to=300, variable=volume,
                       command=lambda value: volume_text.set('음량 {}%'.format(normalize_machine_alert_volume(value))))
        volume_scale.pack(side='left', fill='x', expand=True, padx=8)
        volume_hint = self.tk.StringVar()
        self.ttk.Label(frame, textvariable=volume_hint).pack(anchor='w', pady=(0, 12))
        def update_volume_state():
            system = sound_kind.get() == 'system'
            volume_scale.configure(state='disabled' if system else 'normal')
            volume_hint.set('시스템 소리는 Windows 음량 설정을 따릅니다.' if system else '톡 소리: 기존 최대 100% → 최대 300%')
        update_volume_state()
        def preview_sound():
            try:
                play_machine_alert_sound(volume.get(), sound_kind.get())
            except Exception as error:
                self.messagebox.showerror('소리 재생 실패', str(error), parent=dialog)
        self.ttk.Button(volume_row, text='미리 듣기', command=preview_sound,
                        style='DriveSmall.TButton').pack(side='left')
        grid = self.ttk.Frame(frame); grid.pack(fill='x')
        variables = {}
        for row, numbers in enumerate(((1, 3, 5, 7), (2, 4, 6, 8, 9))):
            for column, number in enumerate(numbers):
                var = self.tk.BooleanVar(value=number in self.machine_alert_selected); variables[number] = var
                self.tk.Checkbutton(grid, text='{}호기'.format(number), variable=var, background='#060b16',
                                    foreground='#eaf0fc', selectcolor='#0e1a35', activebackground='#060b16',
                                    activeforeground='#ffffff', font=('맑은 고딕', 11), padx=14, pady=9,
                                    highlightthickness=0).grid(row=row, column=column, sticky='w')
        self.machine_alert_setting_vars = variables
        actions = self.ttk.Frame(frame); actions.pack(fill='x', pady=(14, 12))
        self.ttk.Button(actions, text='전체 선택', style='DriveSmall.TButton',
                        command=lambda: [v.set(True) for v in variables.values()]).pack(side='left')
        self.ttk.Button(actions, text='전체 해제', style='DriveSmall.TButton',
                        command=lambda: [v.set(False) for v in variables.values()]).pack(side='left', padx=8)
        self.ttk.Label(frame, text='주모니터 오른쪽 아래 · 5초 표시\n세척완료 작업 중 발생한 알림은 작업 후 표시합니다.',
                       style='Subtitle.TLabel', justify='left').pack(anchor='w', pady=(0, 16))
        def save():
            if self.commit_machine_alert_settings(enabled.get(), {n for n,v in variables.items() if v.get()}, sound.get(), volume.get(), sound_kind.get()):
                dialog.destroy()
        self.ttk.Button(frame, text='저장', command=save, style='Accent.TButton').pack(side='right')
        self.ttk.Button(frame, text='취소', command=dialog.destroy, style='Secondary.TButton').pack(side='right', padx=8)
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        dialog.update_idletasks()
        dialog.geometry('+{}+{}'.format(max(0,self.window.winfo_rootx()+80), max(0,self.window.winfo_rooty()+80)))

    def queue_machine_alert(self, event):
        number = event['machine']
        previous = self.machine_alert_pending.get(number)
        if previous:
            event = dict(event, completed=previous['completed'] or event['completed'],
                         light=event.get('light') if event['completed'] else previous.get('light', event.get('light')),
                         before=previous['before'] or event['before'], count=previous['count']+event['count'])
        self.machine_alert_pending[number] = event

    def dismiss_machine_toast(self):
        if self.machine_alert_timer is not None:
            self.window.after_cancel(self.machine_alert_timer); self.machine_alert_timer = None
        if self.machine_alert_toast is not None:
            self.machine_alert_toast.destroy(); self.machine_alert_toast = None
        self.machine_alert_displayed = []

    def suspend_machine_alerts(self):
        # Called before the automation worker starts so an existing toast cannot cover POP.
        pending = list(self.machine_alert_pending.values())
        self.machine_alert_pending.clear()
        for event in self.machine_alert_displayed + pending:
            if not event.get('test'):
                self.queue_machine_alert(event)
        self.dismiss_machine_toast()

    def test_machine_alert(self, sound=None):
        washing = getattr(self, 'wash_app', None)
        if washing is not None and washing.busy:
            self.messagebox.showinfo('알림 테스트', '세척완료 자동 작업이 끝난 뒤 테스트해 주세요.', parent=self.window)
            return
        self.suspend_machine_alerts()
        self.display_machine_alerts(preview=True, sound=sound)

    def open_machine_alert_details(self, number):
        self.dismiss_machine_toast()
        self.window.deiconify(); self.window.lift()
        self.show_machine_details(number)

    def poll_machine_alerts(self):
        if self.machine_monitor.stopped.is_set():return
        try:
            washing = getattr(self, 'wash_app', None)
            if washing is not None and washing.busy:
                if self.machine_alert_toast is not None:self.suspend_machine_alerts()
            elif (self.machine_alert_enabled and self.machine_alert_pending and self.machine_alert_toast is None
                  and time.monotonic() >= self.machine_alert_retry_at):
                self.display_machine_alerts()
        finally:
            self.window.after(200, self.poll_machine_alerts)

    def display_machine_alerts(self, preview=False, sound=None):
        test_state = ('RUN', 'ALARM', 'HOLD', 'STOP')[self.machine_alert_test_index % 4]
        batch = ([{'machine': 1, 'completed': test_state != 'RUN', 'before': '0100' if test_state=='RUN' else '',
                   'program': '0235', 'state': test_state, 'light': machine_state_light(test_state),
                   'time': datetime.now().strftime('%H:%M:%S'), 'count': 1, 'test': True}]
                 if preview else list(self.machine_alert_pending.values())[:1])
        if preview:self.machine_alert_test_index += 1
        dialog = None
        try:
            left, top, right, bottom = primary_monitor_work_area(self.window)
            width = min(300, right-left-24)
            dialog = self.tk.Toplevel(self.window); dialog.withdraw()
            background, foreground = machine_alert_palette(batch[0])
            dialog.overrideredirect(True); dialog.configure(background=background)
            self.machine_alert_toast = dialog
            frame = self.tk.Frame(dialog, background=background, padx=10, pady=8)
            frame.pack(fill='both', expand=True, padx=1, pady=1)
            header = self.tk.Frame(frame, background=background); header.pack(fill='x')
            self.tk.Label(header, text='지후니우스 · '+('테스트 알림' if preview else '머신 알림'), background=background, foreground=foreground,
                          font=('맑은 고딕',9)).pack(side='left')
            self.tk.Button(header, text='×', command=self.dismiss_machine_toast, background=background,
                           foreground=foreground, activebackground=background, activeforeground=foreground, relief='flat', bd=0,
                           takefocus=False, font=('맑은 고딕',10)).pack(side='right')
            for event in batch:
                title, body = machine_alert_text(event)
                event_background, event_foreground = machine_alert_palette(event)
                card = self.tk.Frame(frame, background=event_background, padx=2, pady=2)
                card.pack(fill='x', pady=(2,0))
                for text, color, size in ((title, event_foreground,11), (body, event_foreground,9)):
                    label = self.tk.Label(card, text=text, background=event_background, foreground=color,
                                          font=('맑은 고딕', size, 'bold' if size==11 else 'normal'),
                                          wraplength=width-28, justify='left', anchor='w', cursor='hand2')
                    label.pack(fill='x', pady=(3 if size==11 else 2,0))
                    if preview:
                        label.bind('<Button-1>', lambda e: self.dismiss_machine_toast())
                    else:
                        label.bind('<Button-1>', lambda e,n=event['machine']: self.open_machine_alert_details(n))
            dialog.update_idletasks()
            height = dialog.winfo_reqheight()
            show_machine_toast_noactivate(dialog, right-width-12, max(top+12,bottom-height-12), width, height)
            if not preview:
                for event in batch:self.machine_alert_pending.pop(event['machine'], None)
            self.machine_alert_displayed = batch
            self.machine_alert_timer = self.window.after(5000, self.dismiss_machine_toast)
            self.machine_alert_retry_at = 0
            self.machine_alert_last_error = None
            if self.machine_alert_sound if sound is None else sound:
                try:
                    play_machine_alert_sound(self.machine_alert_volume, self.machine_alert_sound_kind)
                except (OSError, RuntimeError, ImportError) as error:
                    self.append_log('[머신 알림] 소리 재생 실패: '+str(error)+'\n')
        except (OSError, self.tk.TclError) as error:
            if dialog is not None:dialog.destroy()
            self.machine_alert_toast = None
            self.machine_alert_retry_at = time.monotonic() + 5
            if preview or self.machine_alert_last_error != str(error):
                self.append_log('[머신 알림] 표시 실패: '+str(error)+(' · 5초 후 재시도' if not preview else '')+'\n')
            self.machine_alert_last_error = str(error)

    MACHINE_TILE_COLORS = {"green": ("#2fb36b", "#03150a", "가동"), "red": ("#e5484d", "#ffffff", "알람"),
                           "yellow": ("#f0c440", "#2a2100", "대기")}
    MACHINE_STATE_WORDS = {"RUN": "가동", "ALARM": "알람", "WAIT": "대기", "HOLD": "일시정지", "STOP": "정지", "OFF": "꺼짐"}
    MACHINE_TILE_IDLE = ("#25334b", "#b6bdc8", "")

    def build_machine_monitor(self, parent):
        """머신별 칸(상태색으로 꽉 채움·PRM 번호)과 그 아래 소재 버튼 자리를 만듭니다.

        윗줄 1·3·5·7, 아랫줄 2·4·6·8·9. 반환값은 호기별 버튼 자리 프레임입니다."""
        self.machine_tiles = {}
        self.current_machines = {}
        self.machine_detail_dialog = None
        cells = {}
        # 글자 크기(화면 배율)에 맞춰 칸 높이와 글자 위치를 정합니다. 100%에서는 기존과 같은 56px입니다.
        try:
            from tkinter import font as tkfont
            title_h = tkfont.Font(root=parent, family="맑은 고딕", size=10, weight="bold").metrics("linespace")
            number_h = tkfont.Font(root=parent, family="Consolas", size=16, weight="bold").metrics("linespace")
            title_y, number_y = 6 + title_h / 2, 6 + title_h + number_h / 2 - 1
            tile_height = max(56, int(round(12 + title_h + number_h - 1)))
        except Exception:
            title_y, number_y, tile_height = 15, 38, 56
        for row, machines in enumerate(((1, 3, 5, 7), (2, 4, 6, 8, 9))):
            for column, machine in enumerate(machines):
                cell = self.ttk.Frame(parent, style="Card.TFrame", borderwidth=0)
                cell.grid(row=row + 1, column=column, sticky="ew", padx=(0, 10 if column < 4 else 0),
                          pady=(0, 10 if row == 0 else 0))
                cell.columnconfigure(0, weight=1)
                tile = self.tk.Canvas(cell, width=150, height=tile_height, background="#060b16",
                                      highlightthickness=0, borderwidth=0,
                                      takefocus=True, cursor="hand2")
                tile.grid(row=0, column=0, sticky="ew", pady=(0, 6))
                fill, ink, _ = self.MACHINE_TILE_IDLE
                light = tile.create_polygon(0, 0, 0, 0, 0, 0, smooth=True, splinesteps=12,
                                            fill=fill, outline=fill, tags=("machine_surface",))
                tile.create_text(12, title_y, text="머신{}".format(machine), anchor="w", tags=('machine_title',),
                                 fill=ink, font=("맑은 고딕", 10, "bold"))
                tile.create_text(0, title_y, text="", anchor="e", tags=('machine_state',),
                                 fill=ink, font=("맑은 고딕", 9, "bold"))
                number = tile.create_text(12, number_y, text="—", anchor="w", fill=ink, font=("Consolas", 16, "bold"))
                tile.bind("<Configure>", lambda event, c=tile, l=light: self.shape_machine_tile(c, l, event.width, event.height))
                self.machine_tiles[machine] = (tile, light, number)
                tile.bind("<Button-1>", lambda event, n=machine: self.show_machine_details(n))
                tile.bind("<Return>", lambda event, n=machine: self.show_machine_details(n))
                tile.bind("<space>", lambda event, n=machine: self.show_machine_details(n))
                buttons = self.ttk.Frame(cell, style="Card.TFrame", borderwidth=0)
                buttons.grid(row=1, column=0, sticky="ew")
                cells[machine] = buttons
        self.machine_panel = parent
        return cells

    @staticmethod
    def shape_machine_tile(canvas, light, width, height):
        w, h, r = max(width, 24) - 1, max(height, 24) - 1, 4
        canvas.coords(light, 1 + r, 1, w - r, 1, w, 1, w, 1 + r, w, h - r, w, h, w - r, h,
                      1 + r, h, 1, h, 1, h - r, 1, 1 + r, 1, 1)
        title = canvas.coords('machine_title')
        canvas.coords('machine_state', w - 11, title[1] if title else 15)

    def apply_machine_status(self, machines, online=True):
        """읽기 결과는 GUI 스레드에서 반영. 알 수 없는 상태는 회색으로 표시합니다."""
        self.current_machines = dict(machines) if online else {}
        fresh = {n:r for n,r in self.current_machines.items() if not r.get('_stale')}
        for event in self.machine_alert_tracker.observe(fresh, self.machine_alert_enabled, self.machine_alert_selected):
            self.queue_machine_alert(event)
        for machine, (tile, light, number) in self.machine_tiles.items():
            record = machines.get(machine, {}) if online else {}
            fill, ink, _ = self.MACHINE_TILE_COLORS.get(record.get("light"), self.MACHINE_TILE_IDLE)
            # 글자는 색이 아니라 실제 상태에서: 같은 노란색이라도 WAIT=대기, HOLD=일시정지.
            word = self.MACHINE_STATE_WORDS.get(record.get("state"), "") if record else ""
            uncertain = not record or record.get('_stale', False)
            tile.itemconfigure('machine_title', text='머신{}{}'.format(machine, ' ?' if uncertain else ''), fill=ink)
            tile.itemconfigure('machine_state', text=word, fill=ink)
            value = str(record.get("prm_no", ""))
            # 사이트 PRM NO. 뒤의 숫자를 그대로 사용하고 앞자리 0도 유지합니다.
            if not re.fullmatch(r"[0-9]+", value):
                value = "—"
            tile.itemconfigure(light, fill=fill, outline=fill)
            tile.itemconfigure(number, text=value, fill=ink)
        self.refresh_machine_details()

    def build_drive_card(self, body):
        """드라이브 정리 칸(목록·추가·새로고침·비우기·삭제)을 만듭니다."""
        tk, ttk, window = self.tk, self.ttk, self.window
        drive_card = ttk.Frame(body, style="Card.TFrame", padding=15)
        drive_card.grid(row=0, column=1, sticky="nsew", padx=(0, 14))
        drive_card.columnconfigure(0, weight=1)
        drive_card.rowconfigure(2, weight=1)
        drive_header = ttk.Frame(drive_card, style="Card.TFrame", borderwidth=0)
        drive_header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        drive_header.columnconfigure(0, weight=1, uniform="drive_tools")
        drive_header.columnconfigure(1, weight=1, uniform="drive_tools")
        ttk.Label(drive_header, text="드라이브 정리", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        self.drive_add_button = ttk.Button(drive_header, text="추가", width=0, style="DriveSmall.TButton",
                                            command=self.choose_drive_files)
        self.drive_add_button.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=(10, 0))
        self.drive_refresh_button = ttk.Button(drive_header, text="새로고침", width=0, style="DriveSmall.TButton",
                                                command=self.refresh_drive_manual)
        self.drive_refresh_button.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=(10, 0))
        self.drive_contents_status = tk.StringVar(value="드라이브 연결 대기")
        self.drive_status_label = self.make_stable_status_label(
            drive_card, self.drive_contents_status, "Caption.TLabel", width=1, anchor="w")
        self.drive_status_label.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        self.drive_contents = tk.Listbox(drive_card, width=20, height=8, font=("맑은 고딕", 9),
                                         background="#050a14", foreground="#eaf0fc", relief="flat",
                                         borderwidth=0, highlightthickness=1, highlightbackground="#2e333d",
                                         highlightcolor="#2a66f2", selectbackground="#1d3f86",
                                         selectforeground="#eaf0fc", exportselection=False, selectmode="extended")
        self.drive_contents.grid(row=2, column=0, sticky="nsew")
        drive_scrollbar = ttk.Scrollbar(drive_card, orient="vertical", command=self.drive_contents.yview)
        drive_scrollbar.grid(row=2, column=1, sticky="ns")
        drive_horizontal = ttk.Scrollbar(drive_card, orient="horizontal", command=self.drive_contents.xview)
        drive_horizontal.grid(row=3, column=0, sticky="ew")
        self.drive_contents.configure(yscrollcommand=drive_scrollbar.set, xscrollcommand=drive_horizontal.set)
        self.drive_contents.bind("<Double-Button-1>", self.open_drive_item)
        self.drive_contents.bind("<Return>", self.open_drive_item)
        self.drive_contents.bind("<F2>", self.start_rename)
        self.drive_contents.bind("<Button-3>", self.show_drive_menu)
        self.drive_contents.bind("<Delete>", self.start_drive_delete)
        window.bind("<F5>", self.refresh_active_tab)
        self.drive_menu = tk.Menu(window, tearoff=False, background="#060b16", foreground="#ffffff",
                                  activebackground="#2a66f2", activeforeground="#ffffff",
                                  disabledforeground="#818388", font=("맑은 고딕", 10))
        self.drive_menu.add_command(label="이름 변경", accelerator="F2", command=self.start_rename)
        self.drive_menu.add_command(label="선택 파일 삭제", accelerator="Delete", command=self.start_drive_delete)
        self.drive_menu.add_separator()
        self.drive_menu.add_command(label="파일 추가…", command=self.choose_drive_files)
        self.drive_menu.add_command(label="새로고침", accelerator="F5", command=self.refresh_drive_manual)
        self.drive_item_paths = []
        self.drive_contents_signature = None
        self.drive_hint = tk.StringVar(value="파일을 끌어놓아 추가 · Delete: 삭제\n더블클릭: 열기 · F2: 이름 변경\n수정10.30 자동 추가 · 비우기 시 보존")
        drive_actions = ttk.Frame(drive_card, style="Card.TFrame", borderwidth=0)
        drive_actions.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        drive_actions.columnconfigure(0, weight=1)
        self.empty_button = ttk.Button(drive_actions, text="드라이브 비우기", command=self.start_empty,
                                       style="Danger.TButton")
        self.empty_button.grid(row=0, column=0, sticky="ew")
        self.drive_delete_button = ttk.Button(drive_actions, text="삭제", width=4, command=self.start_drive_delete,
                                               style="Danger.TButton")
        self.drive_delete_button.grid(row=0, column=1, padx=(6, 0), sticky="ns")
        return drive_card

    def build_machine_board(self, frame):
        """설비 · 소재 사용량 조사 보드(머신 칸, 불량·소재교체, 머신 알림)를 만듭니다."""
        tk, ttk, window = self.tk, self.ttk, self.window
        # A-3: 머신 상태 칸 아래에 같은 호기의 불량/소재교체를 붙인 한 장의 설비 보드.
        details = ttk.Frame(frame, style="RoundedCard.TFrame", padding=(16, 12))
        details.grid(row=3, column=0, sticky="ew")
        for column in range(5):
            details.columnconfigure(column, weight=1, uniform="machine-cell")
        self.search_root_text = tk.StringVar(value=str(year_search_root(self.saved_program_year)))
        self.year_value.trace_add("write", self.update_year_display)
        self.destination_text = tk.StringVar(value="F:\\ / G:\\ 연결 대기")
        board_header = ttk.Frame(details, style="Card.TFrame", borderwidth=0)
        board_header.grid(row=0, column=0, columnspan=5, sticky="ew", pady=(0, 8))
        ttk.Label(board_header, text="설비 · 소재 사용량 조사", style="Section.TLabel").pack(side="left")
        quick_cells = self.build_machine_monitor(details)
        # N3: 머신 알림 스위치와 알림 설정은 윗줄 7호기 옆 빈 칸에 둡니다(명령·바인딩은 그대로).
        alert_controls = ttk.Frame(details, style="Card.TFrame", padding=(10, 6))
        alert_controls.grid(row=1, column=4, sticky="nsew", pady=(0, 10))
        alert_controls.columnconfigure(0, weight=1)
        self.machine_alert_controls = alert_controls
        self.machine_alert_toggle = tk.Canvas(alert_controls, width=174, height=48, background="#060b16",
                                             highlightthickness=1, highlightbackground="#060b16",
                                             highlightcolor="#8db3ff", borderwidth=0, takefocus=True, cursor="hand2")
        self.machine_alert_toggle.grid(row=0, column=0, sticky="w")
        self.machine_alert_switch_images = {enabled: tk.PhotoImage(master=window, data=data, format="png")
                                            for enabled, data in MACHINE_ALERT_SWITCH_PNGS.items()}
        def switch_alert(event=None):
            self.machine_alert_toggle.focus_set()
            self.toggle_machine_alerts()
            return 'break'
        self.machine_alert_toggle.bind('<Button-1>', switch_alert)
        self.machine_alert_toggle.bind('<space>', switch_alert)
        self.machine_alert_toggle.bind('<Return>', switch_alert)
        self.machine_alert_settings_button = ttk.Button(alert_controls, text="알림 설정",
                                                        command=self.show_machine_alert_settings, style="Secondary.TButton")
        self.machine_alert_settings_button.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.update_machine_alert_toggle()

        self.material_quick = SuiteMaterialQuick.QuickPanel(self, details, cells=quick_cells, header=board_header)

    def apply_visual_theme(self):
        """모양만 입힙니다(둥근/테두리 요소, 아이콘, 제목 막대). 위젯 명령·값은 그대로입니다."""
        window = self.window
        visual = SuiteVisualTheme.install_visual_theme(window, self.style)
        self.material_quick.set_icons(visual["images"])
        self.reserve_empty_button_width()
        for button in self._suite_buttons.values():
            button.configure(image=visual["popup_icon"], compound="right")
        self.apply_n3_marks(visual["images"])
        # Keep the wash form compact within the same card surface as other pages.
        wash_body = self.app_pages["wash"].winfo_children()[0]
        wash_body.configure(style="RoundedCard.TFrame", padding=20)
        wash_body.pack_configure(fill="x", expand=False)
        wash_widgets = list(wash_body.winfo_children())
        while wash_widgets:
            widget = wash_widgets.pop()
            wash_widgets.extend(widget.winfo_children())
            if widget.winfo_class() == "TFrame" and not str(widget.cget("style")):
                widget.configure(style="Card.TFrame", borderwidth=0)
            elif widget.winfo_class() == "TLabel":
                if not str(widget.cget("style")):
                    widget.configure(style="Card.TLabel")
                elif str(widget.cget("style")) == "Title.TLabel":
                    widget.configure(style="CardTitle.TLabel")
        # Round only outer cards; nested Card frames keep their seamless fill.
        pending = list(self.body.winfo_children())
        while pending:
            widget = pending.pop()
            pending.extend(widget.winfo_children())
            if widget.winfo_class() == "TFrame":
                card_style = str(widget.cget("style"))
                if card_style in ("Card.TFrame", "STL.Card.TFrame") and str(widget.cget("borderwidth")) != "0":
                    widget.configure(style="RoundedCard.TFrame")

    def apply_n3_marks(self, images):
        """N3 화면 표시만 더합니다: 작업 모드 선택 표시, 고정 제목 앞 막대. 명령·값은 그대로입니다."""
        try:
            for button in self.mode_buttons:
                button.configure(image=(images["radio_off"], "selected", images["radio_on"]), compound="left")
            pending = [self.window]
            while pending:
                widget = pending.pop()
                pending.extend(widget.winfo_children())
                if (widget.winfo_class() == "TLabel" and str(widget.cget("style")) in ("Section.TLabel", "STL.Section.TLabel")
                        and not str(widget.cget("textvariable")) and str(widget.cget("text"))
                        and not str(widget.cget("image"))):
                    widget.configure(image=images["heading_bar"], compound="left")
        except Exception:
            # 표시 장식이 실패해도 작업 기능에는 영향이 없어야 합니다.
            pass

    def position_handover_button(self):
        if not self.handover_toggle.winfo_exists():
            return
        header = self.handover_toggle.master
        anchor_button = getattr(self, 'material_button', None)
        if anchor_button is not None and anchor_button.winfo_ismapped() and anchor_button.winfo_width() > 1:
            # 위 줄 '소재 사용량 조사' 버튼과 왼쪽·오른쪽 끝을 맞춥니다.
            left = anchor_button.winfo_rootx() - header.winfo_rootx()
            self.handover_toggle.place(relx=0, x=left, width=anchor_button.winfo_width(), rely=0.5, anchor="w")
            return
        last_tab = self.tab_buttons['wash']
        left = last_tab.winfo_rootx() + last_tab.winfo_width() - header.winfo_rootx()
        right = header.winfo_width()
        self.handover_toggle.place(relx=0, x=round((left + right) / 2), rely=0.5, anchor="center")

    def show_machine_details(self, machine):
        dialog = self.machine_detail_dialog
        if dialog is not None and dialog.winfo_exists():
            if self.machine_detail_selected == machine:
                dialog.destroy()
                self.machine_detail_dialog = None
                return
            self.machine_detail_selected = machine
            self.refresh_machine_details();dialog.lift()
            return
        self.machine_detail_selected = machine
        dialog = self.tk.Toplevel(self.window)
        self.machine_detail_dialog = dialog
        dialog.transient(self.window);dialog.configure(background="#060b16")
        dialog.geometry("460x530");dialog.minsize(400, 510)
        frame = self.ttk.Frame(dialog, padding=20);frame.pack(fill="both", expand=True)
        self.machine_detail_title = self.tk.StringVar()
        self.ttk.Label(frame, textvariable=self.machine_detail_title, style="Title.TLabel").pack(anchor="w")
        self.machine_detail_status = self.tk.StringVar()
        self.machine_detail_status_label = self.tk.Label(frame, textvariable=self.machine_detail_status,
                                                         background="#22355c", foreground="#ffffff",
                                                         font=("맑은 고딕", 11, "bold"), padx=14, pady=8)
        self.machine_detail_status_label.pack(anchor="w", pady=(8, 16))
        table = self.ttk.Frame(frame, style="Card.TFrame", padding=16);table.pack(fill="both", expand=True)
        table.columnconfigure(1, weight=1)
        self.machine_detail_values = {}
        fields = (("prm_no", "프로그램 번호"), ("tool_number", "공구 번호"),
                  ("feed_RPM", "FEED"), ("spindle_RPM", "스핀들 RPM"),
                  ("part_count", "누적 가공 수량"), ("spindle_load_S1", "스핀들 부하"))
        for row, (key, label) in enumerate(fields):
            value = self.tk.StringVar(value="—");self.machine_detail_values[key] = value
            self.ttk.Label(table, text=label, style="Caption.TLabel").grid(row=row, column=0, sticky="w", pady=12, padx=(0, 22))
            self.ttk.Label(table, textvariable=value, style="Section.TLabel", wraplength=220).grid(row=row, column=1, sticky="e", pady=12)
        self.ttk.Label(frame, text="약 3초마다 자동 갱신 · 값과 단위는 설비 표시 기준\n누적 수량은 설비 카운터 값입니다.",
                       style="Caption.TLabel").pack(anchor="w", pady=(12, 8))
        dialog.bind("<Escape>", lambda event: dialog.destroy())
        self.refresh_machine_details()
        dialog.update_idletasks()
        x = max(0, self.window.winfo_rootx() + (self.window.winfo_width() - dialog.winfo_width()) // 2)
        y = max(0, self.window.winfo_rooty() + (self.window.winfo_height() - dialog.winfo_height()) // 2)
        dialog.geometry(f"+{x}+{y}");dialog.lift()

    def refresh_machine_details(self):
        dialog = getattr(self, 'machine_detail_dialog', None)
        if dialog is None or not dialog.winfo_exists():
            return
        machine = self.machine_detail_selected
        record = self.current_machines.get(machine, {})
        title = f"머신{machine} · 가공 상세정보"
        dialog.title(title);self.machine_detail_title.set(title)
        states = {"RUN": "가공 중", "ALARM": "알람", "WAIT": "대기", "HOLD": "일시 정지", "STOP": "정지", "OFF": "꺼짐"}
        state = record.get('state', '')
        self.machine_detail_status_label.configure(background={"RUN": "#246b48", "ALARM": "#963e49", "WAIT": "#a88830", "HOLD": "#a88830"}.get(state, "#22355c"))
        status = (states.get(state, '상태 미확인') + (f" · {state}" if state else '')) if record else '최신 응답 없음 · 연결 확인 중'
        if record.get('_stale'):
            status = '연결 확인 중 · 마지막 확인 상태: ' + states.get(state, state)
        if machine in self.machine_conflicts:
            status = '같은 호기 번호의 응답이 중복됨 · 서버 설정 확인 필요'
        self.machine_detail_status.set(status)
        for key, value in self.machine_detail_values.items():
            raw = record.get('prm_no', '') if key == 'prm_no' else record.get('details', {}).get(key, '')
            value.set(raw if raw != '' and raw is not None else '—')

    def receive_machine_sample(self, ip, record, observed, cancel):
        if cancel is not None and cancel.is_set():
            return
        previous = self.machine_samples.get(ip)
        if previous is not None and observed < previous[1]:
            return
        if record is None:
            if cancel is None:  # Explicit removal from the server's machine list.
                self.machine_samples.pop(ip, None)
                self.machine_failures.discard(ip)
            elif previous is not None:
                self.machine_failures.add(ip)
        else:
            self.machine_samples[ip] = (record, observed)
            self.machine_failures.discard(ip)
        self.refresh_machine_status()

    def refresh_machine_status(self):
        now = time.monotonic()
        machines = {}
        duplicated = set()
        for ip, (record, observed) in list(self.machine_samples.items()):
            age = now - observed
            if record is None or age > MONITOR_GRACE_SECONDS:
                self.machine_samples.pop(ip, None)
                self.machine_failures.discard(ip)
                continue
            machine = record["machine"]
            if machine in machines:
                duplicated.add(machine)
            else:
                machines[machine] = dict(record, _observed_at=observed, _source_ip=ip,
                                         _stale=ip in self.machine_failures or age > MONITOR_STALE_SECONDS)
        self.machine_conflicts = duplicated
        for machine in duplicated:
            machines.pop(machine, None)
            self.machine_alert_tracker.previous.pop(machine, None)
            self.machine_alert_tracker.last_seen.pop(machine, None)
            self.machine_alert_tracker.sources.pop(machine, None)
        self.apply_machine_status(machines)

    def expire_machine_status(self):
        if not self.machine_monitor.stopped.is_set():
            self.refresh_machine_status()
            self.window.after(1000, self.expire_machine_status)

    def update_handover_toggle(self):
        if not hasattr(self, "handover_toggle"):
            return
        arrow = "▸" if self.handover_expanded else "◂"
        count = len(self.handover_notes)
        if self.handover_read_error:
            text = "인수인계 ! " + arrow
        elif count:
            text = "● 인수인계 {}건 {}".format(count, arrow)
        else:
            text = "인수인계 " + arrow
        self.handover_toggle.configure(text=text, style="HandoverNotice.TButton"
                                        if count or self.handover_read_error else "HandoverToggle.TButton")

    def toggle_handover(self):
        self.window.update_idletasks()
        width, height = self.window.winfo_width(), self.window.winfo_height()
        x, y = self.window.winfo_x(), self.window.winfo_y()
        normal = self.window.state() == "normal"
        self.handover_expanded = not self.handover_expanded
        if self.handover_expanded:
            self.handover_card.grid()
            self.body.columnconfigure(0, weight=0, minsize=320)
            self.window.minsize(1320, self.minimum_height)
            self.handover_added_width = max(1320, width + 320) - width if normal else 0
            if normal:
                left = x - self.handover_added_width
                desktop_left = self.window.winfo_vrootx()
                if x >= desktop_left:
                    left = max(desktop_left, left)
                self.handover_left_shift = x - left
                self.window.geometry("{}x{}+{}+{}".format(
                    width + self.handover_added_width, height, left, y))
        else:
            self.handover_card.grid_remove()
            self.body.columnconfigure(0, weight=0, minsize=0)
            self.window.minsize(1000, self.minimum_height)
            if normal and self.handover_added_width:
                target_width = max(1000, width - self.handover_added_width)
                self.window.geometry("{}x{}+{}+{}".format(target_width, height, x + self.handover_left_shift, y))
            self.handover_added_width = 0
            self.handover_left_shift = 0
        self.update_handover_toggle()

    def build_handover_panel(self, parent):
        card = self.ttk.Frame(parent, style="Card.TFrame", padding=14)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(0, weight=1)
        notebook = self.ttk.Notebook(card, style="Handover.TNotebook")
        notebook.grid(row=0, column=0, sticky="nsew")
        page = self.ttk.Frame(notebook, style="Card.TFrame", borderwidth=0)
        notebook.add(page, text="인수인계사항")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(2, weight=1)
        self.handover_create = self.ttk.Button(page, text="생성", command=self.create_handover,
                                              style="Accent.TButton")
        self.handover_create.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.ttk.Label(page, text="제목을 눌러 내용 확인 · ×로 삭제", style="Caption.TLabel").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self.handover_tree = self.ttk.Treeview(page, columns=("delete",), show="tree", selectmode="browse",
                                              height=6, style="Handover.Treeview", cursor="hand2")
        self.handover_tree.column("#0", width=180, minwidth=100, stretch=True)
        self.handover_tree.column("delete", width=32, minwidth=32, stretch=False, anchor="center")
        self.handover_tree.grid(row=2, column=0, sticky="nsew")
        scrollbar = self.ttk.Scrollbar(page, orient="vertical", command=self.handover_tree.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.handover_tree.configure(yscrollcommand=scrollbar.set)
        self.handover_tree.bind("<ButtonRelease-1>", self.handover_clicked)
        self.handover_tree.bind("<Return>", self.open_selected_handover)
        self.handover_tree.bind("<Delete>", self.delete_selected_handover)
        self.handover_tree.bind("<F5>", lambda event: self.refresh_handover(force=True))
        self.handover_status = self.tk.StringVar(value="공유 인수인계 확인 중...")
        self.ttk.Label(page, textvariable=self.handover_status, style="Caption.TLabel", wraplength=240).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        return card

    def refresh_handover(self, force=False):
        if self.handover_loading:
            if force:
                self.handover_refresh_pending = True
            return
        self.handover_loading = True
        store = self.handover_store

        def load():
            notes, error = None, None
            try:
                notes = store.load()
            except Exception as caught:
                error = caught
            self.events.put(("handover_loaded", store, notes, error))
        threading.Thread(target=load, daemon=True).start()

    def finish_handover_load(self, store, notes, error):
        self.handover_loading = False
        if store is not self.handover_store or self.handover_refresh_pending:
            self.handover_refresh_pending = False
            self.refresh_handover()
            return
        if error is not None:
            SuiteErrors.capture(error,feature='인수인계',stage='공유 목록 읽기')
            self.handover_status.set("공유폴더 연결을 확인해 주세요.\n마지막으로 불러온 {}건 표시 중".format(len(self.handover_notes)))
            self.handover_signature = None
            self.handover_read_error = True
            self.update_handover_toggle()
            return
        self.handover_read_error = False
        signature = tuple((note["id"], note["title"], note["content"], note["updated_at"]) for note in notes)
        if signature != self.handover_signature:
            selection = self.handover_tree.selection()
            children = self.handover_tree.get_children()
            if children:
                self.handover_tree.delete(*children)
            self.handover_notes = {note["id"]: note for note in notes}
            for note in notes:
                self.handover_tree.insert("", "end", iid=note["id"], text=note["title"], values=("×",))
            if selection and selection[0] in self.handover_notes:
                self.handover_tree.selection_set(selection[0])
            self.handover_signature = signature
        self.handover_status.set("총 {}건".format(len(notes)) if notes else "등록된 사항이 없습니다.")
        self.update_handover_toggle()

    def poll_handover(self):
        if self.handover_dialog is None:
            self.refresh_handover()
        self.window.after(2500, self.poll_handover)

    def update_handover_controls(self):
        if hasattr(self, "handover_create"):
            state = "disabled" if self.busy or getattr(self, "handover_writing", False) else "normal"
            self.handover_create.configure(state=state)

    def run_handover_action(self, action, callback):
        if self.handover_writing:
            return False
        self.handover_writing = True
        self.update_handover_controls()

        def work():
            result, error = None, None
            try:
                result = action()
            except Exception as caught:
                error = caught
            self.events.put(("handover_saved", callback, result, error))
        threading.Thread(target=work, daemon=True).start()
        return True

    def handover_clicked(self, event):
        if self.busy or self.handover_dialog is not None or self.handover_writing:
            return "break"
        item = self.handover_tree.identify_row(event.y)
        if not item:
            return "break"
        self.handover_tree.selection_set(item)
        if self.handover_tree.identify_column(event.x) == "#1":
            self.delete_handover(item)
        else:
            self.show_handover_dialog(item)
        return "break"

    def open_selected_handover(self, event=None):
        selected = self.handover_tree.selection()
        if selected:
            self.show_handover_dialog(selected[0])
        return "break"

    def delete_selected_handover(self, event=None):
        selected = self.handover_tree.selection()
        if selected:
            self.delete_handover(selected[0])
        return "break"

    def create_handover(self):
        self.show_handover_dialog()

    def current_handover(self, note_id):
        if note_id in self.handover_notes:
            return dict(self.handover_notes[note_id])
        raise WorkError("이 인수인계사항이 이미 삭제되었습니다. 목록을 다시 확인해 주세요.")

    def delete_handover(self, note_id):
        if self.busy or self.handover_dialog is not None or self.handover_writing:
            return
        try:
            note = self.current_handover(note_id)
            if not self.messagebox.askyesno("인수인계사항 삭제", "‘{}’\n\n삭제할까요?".format(note["title"]),
                                          parent=self.window, default="no"):
                return
        except WorkError as error:
            self.messagebox.showerror("인수인계사항 삭제", str(error), parent=self.window)
            self.refresh_handover(force=True)
            return

        def done(result, error):
            if error is not None:
                self.messagebox.showerror("인수인계사항 삭제", str(error), parent=self.window)
            self.refresh_handover(force=True)
        self.handover_status.set("공유 인수인계사항을 삭제하는 중...")
        self.run_handover_action(lambda: self.handover_store.delete(note), done)

    def show_handover_dialog(self, note_id=None):
        if self.busy or self.handover_dialog is not None or self.handover_writing:
            return
        try:
            # 읽기는 캐시로 즉시 열고, 저장 시 서버의 최신 버전과 비교합니다.
            note = self.current_handover(note_id) if note_id is not None else None
        except WorkError as error:
            self.messagebox.showerror("인수인계사항 확인", str(error), parent=self.window)
            self.refresh_handover(force=True)
            return
        dialog = self.tk.Toplevel(self.window)
        self.handover_dialog = dialog
        dialog.title("인수인계사항 작성" if note is None else "인수인계사항 보기")
        dialog.configure(background="#060b16")
        dialog.transient(self.window)
        dialog.geometry("640x530")
        dialog.minsize(480, 400)
        frame = self.ttk.Frame(dialog, padding=22)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)
        self.ttk.Label(frame, text="제목", font=("맑은 고딕", 11, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8))
        title = self.ttk.Entry(frame, font=("맑은 고딕", 12))
        title.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        self.ttk.Label(frame, text="내용", font=("맑은 고딕", 11, "bold")).grid(
            row=2, column=0, sticky="w", pady=(0, 8))
        content_frame = self.ttk.Frame(frame)
        content_frame.grid(row=3, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        content = self.tk.Text(content_frame, font=("맑은 고딕", 11), wrap="word", undo=True,
                               background="#050a14", foreground="#eaf0fc", insertbackground="#ffffff",
                               selectbackground="#1d3f86", relief="flat", padx=12, pady=12,
                               highlightthickness=1, highlightbackground="#4a515e", highlightcolor="#8db3ff")
        content.grid(row=0, column=0, sticky="nsew")
        scrollbar = self.ttk.Scrollbar(content_frame, orient="vertical", command=content.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        content.configure(yscrollcommand=scrollbar.set)
        if note is not None:
            title.insert(0, note["title"])
            content.insert("1.0", note["content"])
        buttons = self.ttk.Frame(frame)
        buttons.grid(row=4, column=0, sticky="ew", pady=(18, 0))
        editing = [note is None]
        saving = [False]
        creation_id = uuid.uuid4().hex
        initial = [(note["title"], note["content"]) if note else ("", "")]

        def close():
            if defer_ime_commit(dialog, close):return
            if saving[0]:
                return
            current = (title.get(), content.get("1.0", "end-1c"))
            if editing[0] and current != initial[0]:
                if not self.messagebox.askyesno("작성 중인 내용", "저장하지 않고 닫을까요?",
                                               parent=dialog, default="no"):
                    return
            dialog.destroy()

        def save_or_edit():
            if defer_ime_commit(dialog, save_or_edit):return
            if saving[0]:
                return
            if not editing[0]:
                editing[0] = True
                initial[0] = (title.get(), content.get("1.0", "end-1c"))
                title.configure(state="normal")
                content.configure(state="normal")
                primary.configure(text="저장")
                secondary.configure(text="취소")
                dialog.title("인수인계사항 수정")
                title.focus_set()
                return
            try:
                new_title, new_content = HandoverStore.validate(title.get(), content.get("1.0", "end-1c"))
            except WorkError as error:
                self.messagebox.showerror("인수인계사항 저장", str(error), parent=dialog)
                return
            saving[0] = True
            title.configure(state="disabled")
            content.configure(state="disabled")
            primary.configure(state="disabled", text="저장 중...")
            secondary.configure(state="disabled")

            def done(result, error):
                saving[0] = False
                if error is not None:
                    title.configure(state="normal")
                    content.configure(state="normal")
                    primary.configure(state="normal", text="저장")
                    secondary.configure(state="normal")
                    self.messagebox.showerror("인수인계사항 저장", str(error), parent=dialog)
                    return
                dialog.destroy()

            if note is None:
                action = lambda: self.handover_store.add(new_title, new_content, note_id=creation_id)
            else:
                action = lambda: self.handover_store.update(note, new_title, new_content)
            self.run_handover_action(action, done)

        primary = self.ttk.Button(buttons, text="저장" if editing[0] else "수정", command=save_or_edit,
                                  style="Accent.TButton")
        primary.pack(side="left", padx=(0, 10))
        secondary = self.ttk.Button(buttons, text="취소" if editing[0] else "닫기", command=close,
                                    style="Secondary.TButton")
        secondary.pack(side="left")
        dialog.protocol("WM_DELETE_WINDOW", close)
        dialog.bind("<Escape>", lambda event: close())
        if not editing[0]:
            title.configure(state="readonly")
            content.configure(state="disabled")
        dialog.update_idletasks()
        x = self.window.winfo_rootx() + max(0, (self.window.winfo_width() - dialog.winfo_width()) // 2)
        y = self.window.winfo_rooty() + max(0, (self.window.winfo_height() - dialog.winfo_height()) // 2)
        dialog.geometry("+{}+{}".format(x, y))
        dialog.grab_set()
        title.focus_set() if editing[0] else content.focus_set()
        try:
            self.window.wait_window(dialog)
        finally:
            self.handover_dialog = None
            self.refresh_handover(force=True)

    def update_year_display(self, *args):
        try:
            year = parse_program_year(self.year_value.get())
            self.search_root_text.set(str(year_search_root(year)))
        except WorkError:
            self.search_root_text.set("연도 4자리를 입력해 주세요.")
            return
        if year != self.saved_program_year:
            try:
                self.saved_program_year = save_program_year(year)
            except OSError:
                self.status.set('연도 설정을 저장하지 못했습니다. PC 저장 공간과 권한을 확인해 주세요.')

    def configure_program_path(self):
        self.cancel_drive_action()
        if self.busy: return
        existing = self.program_path_dialog
        if existing is not None and existing.winfo_exists():
            existing.lift(); existing.focus_set(); return
        tk, ttk = self.tk, self.ttk
        dialog = tk.Toplevel(self.window)
        self.program_path_dialog = dialog
        dialog.title('NC프로그램 경로 설정')
        dialog.configure(bg='#060b16')
        dialog.transient(self.window)
        dialog.geometry('680x190')
        dialog.minsize(520, 190)
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill='both', expand=True)
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text='★ 연도 폴더가 들어 있는 NC프로그램 기본 폴더',
                  style='Section.TLabel').grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 12))
        value = tk.StringVar(value=self.program_base_root)
        entry = ttk.Entry(frame, textvariable=value)
        entry.grid(row=1, column=0, sticky='ew')

        def browse():
            selected = self.filedialog.askdirectory(parent=dialog, title='NC프로그램 기본 폴더 선택',
                initialdir=value.get().strip().strip('"') or str(Path.home()))
            if selected: value.set(selected)

        def apply_path():
            if defer_ime_commit(dialog, apply_path): return
            if self.busy:
                self.messagebox.showinfo('작업 중', '파일 작업이 끝난 뒤 저장해 주세요.', parent=dialog)
                return
            try:
                selected = save_program_base_root(value.get())
            except (OSError, WorkError) as error:
                self.messagebox.showerror('경로 설정 저장 실패', str(error), parent=dialog)
                return
            self.program_base_root = selected
            self.status.set('NC프로그램 경로 저장 완료')
            dialog.destroy()

        ttk.Button(frame, text='찾아보기', command=browse, style='Secondary.TButton').grid(
            row=1, column=1, padx=(10, 0))
        controls = ttk.Frame(frame)
        controls.grid(row=2, column=0, columnspan=2, sticky='e', pady=(18, 0))
        ttk.Button(controls, text='취소', command=dialog.destroy, style='Secondary.TButton').pack(side='left', padx=(0, 8))
        ttk.Button(controls, text='저장', command=apply_path, style='Accent.TButton').pack(side='left')
        dialog.bind('<Escape>', lambda event: dialog.destroy())
        entry.bind('<Return>', lambda event: (apply_path(), 'break')[1])
        dialog.grab_set()
        entry.focus_set()
        entry.icursor('end')

    def update_mode(self):
        mode = self.mode.get()
        self.folder_input.configure(state="disabled" if self.busy or mode == MODE_LIST else "normal")
        self.year_input.configure(state="disabled" if self.busy or mode == MODE_LIST else "normal")
        self.import_button.configure(text=MODE_LABELS[mode])
        for button in self.list_buttons:
            button.configure(state="disabled" if self.busy or mode == MODE_FILES else "normal")
        self.mode_help.set(MODE_DESCRIPTIONS[mode].format(list_name=selected_list_name(self.list_number.get())))

    def refresh_destination(self, invalidate=False):
        # One outstanding worker/result at most. Periodic ticks reuse an in-flight
        # read; explicit changes invalidate it and coalesce into one replacement.
        if invalidate:
            self.cancel_drive_action()
            self.drive_refresh_generation += 1
            self.drive_refresh_pending = True
        if getattr(self, "_suite_stopped", False):
            return
        washing = getattr(self, "wash_app", None)
        if self.busy or (washing is not None and washing.busy) or self.drive_refresh_loading:
            return
        generation = self.drive_refresh_generation
        self.drive_refresh_loading = True
        self.drive_refresh_pending = False

        def read():
            snapshot, error = None, None
            try:
                snapshot = read_drive_snapshot(
                    on_listing=lambda listing: self.events.put(("drive_listing", generation, listing)))
            except Exception as caught:
                error = caught
            self.events.put(("drive_refreshed", generation, snapshot, error))

        try:
            threading.Thread(target=read, daemon=True).start()
        except RuntimeError as error:
            self.finish_drive_refresh(generation, None, error)

    def finish_drive_refresh(self, generation, snapshot, error):
        self.drive_refresh_loading = False
        if getattr(self, "_suite_stopped", False):
            return
        washing = getattr(self, "wash_app", None)
        if self.busy or (washing is not None and washing.busy):
            self.cancel_drive_action("다른 작업이 진행 중입니다 · 끝난 뒤 다시 눌러 주세요.")
            self.drive_refresh_pending = True
            return
        if generation != self.drive_refresh_generation:
            if self.drive_refresh_pending:
                self.refresh_destination()
            return
        if error is not None:
            SuiteErrors.capture(error,feature='드라이브 정리',stage='드라이브 읽기')
            self.drive_contents_status.set("목록을 읽지 못했습니다 · 마지막 목록 표시 중")
            self.finish_drive_action(generation, error)
            return
        snapshot["generation"] = generation
        self.drive_snapshot = snapshot
        self.display_drive_snapshot(snapshot)
        # The requested drive is displayed before a deferred action may begin.
        # User work retains precedence over the idle modifier synchronization.
        self.finish_drive_action(generation)
        self.queue_card_modifier_check()

    def finish_drive_listing(self, generation, snapshot):
        # A preview is still owned by the one outstanding worker. It never
        # releases that worker or authorizes automatic modifier writes.
        if (getattr(self, "_suite_stopped", False) or getattr(self, "_suite_exit_pending", False)
                or generation != self.drive_refresh_generation or self.busy):
            return
        washing = getattr(self, "wash_app", None)
        if washing is not None and washing.busy:
            return
        self.display_drive_snapshot(snapshot)
        self.finish_drive_action(generation)

    def display_drive_snapshot(self, snapshot):
        self.destination = snapshot["destination"]
        if self.destination is None:
            self.destination_text.set("F:\\ / G:\\ 연결 대기")
            self.empty_button.configure(text="드라이브 비우기")
            self.card_modifier_signature = None
        else:
            self.destination_text.set(str(self.destination))
            self.empty_button.configure(text="{} 드라이브 비우기".format(self.destination.drive or self.destination))
        self.reserve_empty_button_width()
        self.apply_drive_contents(snapshot)

    def reserve_empty_button_width(self):
        """Keep the drive column width independent of the 'F: 드라이브 비우기' label.

        Display-only: any failure leaves the layout exactly as before.
        """
        button = getattr(self, "empty_button", None)
        try:
            text = button.cget("text")
            holder = button.master
        except Exception:
            return
        labels = ["드라이브 비우기"] + ["{} 드라이브 비우기".format(item[:2]) for item in DESTINATION_CANDIDATES]
        if text not in labels:
            labels.append(text)
        widest = 0
        try:
            for label in labels:
                button.configure(text=label)
                widest = max(widest, int(button.winfo_reqwidth()))
            if widest > int(holder.grid_columnconfigure(0, "minsize") or 0):
                holder.grid_columnconfigure(0, minsize=widest)
        except Exception:
            pass
        finally:
            try:
                button.configure(text=text)
            except Exception:
                pass

    def cancel_drive_action(self, message=None):
        pending = getattr(self, "drive_action_pending", None)
        self.drive_action_pending = None
        if pending is None:
            return
        if pending["timer"] is not None:
            try:
                self.window.after_cancel(pending["timer"])
            except self.tk.TclError:
                pass
        if self.status.get() == "저장 드라이브 확인 중...":
            self.status.set(pending["previous_status"] if message is None else message)

    def run_with_current_drive(self, action):
        self.cancel_drive_action()
        if self.busy or getattr(self, "_suite_stopped", False) or getattr(self, "_suite_exit_pending", False):
            return
        if self.destination is not None:
            action(self.destination)
            return
        pending = {"generation": self.drive_refresh_generation,
                   "deadline": time.monotonic() + 3.0, "action": action,
                   "previous_status": self.status.get(), "timer": None}
        self.drive_action_pending = pending
        self.status.set("저장 드라이브 확인 중...")

        def expire():
            if self.drive_action_pending is pending:
                self.cancel_drive_action("드라이브 확인 시간 초과 · 연결 상태를 확인하고 다시 눌러 주세요.")

        pending["timer"] = self.window.after(3000, expire)
        self.refresh_destination()

    def finish_drive_action(self, generation, error=None):
        pending = getattr(self, "drive_action_pending", None)
        if pending is None:
            return
        if time.monotonic() >= pending["deadline"]:
            self.cancel_drive_action("드라이브 확인 시간 초과 · 연결 상태를 확인하고 다시 눌러 주세요.")
            return
        if generation != pending["generation"]:
            self.cancel_drive_action()
            return
        action = pending["action"]
        self.cancel_drive_action()
        if error is not None:
            self.status.set("드라이브 확인 실패 · 연결 상태를 확인하고 다시 눌러 주세요.")
            return
        if self.destination is None:
            self.status.set("드라이브 연결 대기")
            self.messagebox.showerror("저장 드라이브 확인", "F:\\ 또는 G:\\에 이동식 드라이브를 연결해 주세요.",
                                      parent=self.window)
            return
        action(self.destination)

    def queue_card_modifier_check(self):
        # 연결/새로고침 직후의 사용자 작업을 먼저 시작하게 합니다.
        if self.card_modifier_pending:
            return
        self.card_modifier_pending = True
        self.window.after_idle(self.check_card_modifier)

    def check_card_modifier(self):
        self.card_modifier_pending = False
        washing = getattr(self, "wash_app", None)
        if self.busy or self.drive_refresh_loading or (washing is not None and washing.busy):
            return
        destination = self.destination
        if destination is None:
            self.card_modifier_signature = None
            return
        snapshot = self.drive_snapshot
        if (snapshot is None or snapshot["destination"] != destination
                or snapshot["generation"] != self.drive_refresh_generation):
            self.refresh_destination()
            return
        error = snapshot["modifier_error"]
        if error is not None:
            signature = (str(destination), "read-error", str(error))
            if signature != self.card_modifier_signature:
                self.card_modifier_signature = signature
                self.append_log("수정10.30 확인 보류: {}\n".format(error))
            return
        signature = snapshot["modifier_signature"]
        if signature == self.card_modifier_signature:
            return
        self.card_modifier_signature = signature
        previous_status = self.status.get()
        self.set_busy(True, "카드 수정 스크립트 준비 중...")

        def work():
            result, error = None, None
            try:
                result = sync_card_modifier(destination, expected_signature=signature)
            except Exception as caught:
                error = caught
            self.events.put(("modifier_done", destination, result, error, previous_status))

        try:
            threading.Thread(target=work, daemon=True).start()
        except RuntimeError as error:
            self.finish_card_modifier(destination, None, error, previous_status)

    def finish_card_modifier(self, destination, result, error, previous_status):
        self.set_busy(False, previous_status)
        if result is not None:
            if (destination == self.destination and result.get("signature") is not None
                    and not result.get("retry")):
                self.card_modifier_signature = result["signature"]
            changes = []
            if result.get("added"):
                changes.append("수정10.30.py 추가")
            if result.get("removed"):
                changes.append("기존 수정9.7 스크립트 {}개 정리".format(len(result["removed"])))
            if changes:
                self.append_log("카드: " + " · ".join(changes) + "\n")
            errors = result.get("errors", [])
            if errors:
                self.append_log("수정10.30 확인 필요: " + " / ".join(str(item) for item in errors) + "\n")
        if error is not None:
            self.append_log("수정10.30 준비 보류: {} · 새로고침하면 다시 시도합니다.\n".format(error))
        self.refresh_drive_contents()


    def refresh_drive_contents(self):
        self.refresh_destination(invalidate=True)

    def apply_drive_contents(self, snapshot):
        destination = snapshot["destination"]
        labels, paths, status = snapshot["labels"], snapshot["paths"], snapshot["status"]
        if labels is None:
            if self.drive_contents_signature is not None and self.drive_contents_signature[0] == str(destination):
                self.drive_contents_status.set(status)
                return
            labels, paths = [], []
        signature = (str(destination), tuple(labels), tuple(paths))
        if signature != self.drive_contents_signature:
            selected = {self.drive_item_paths[index] for index in self.drive_contents.curselection()
                        if 0 <= index < len(self.drive_item_paths)}
            scroll = self.drive_contents.yview()[0]
            horizontal = self.drive_contents.xview()[0]
            self.drive_contents.delete(0, "end")
            if labels:
                self.drive_contents.insert("end", *labels)
                for index, path in enumerate(paths):
                    if path in selected:
                        self.drive_contents.selection_set(index)
                self.drive_contents.yview_moveto(scroll)
                self.drive_contents.xview_moveto(horizontal)
            self.drive_item_paths = paths
            self.drive_contents_signature = signature
        self.drive_contents_status.set(status)
        if self.drive_select_path is not None:
            if self.drive_select_path in paths:
                index = paths.index(self.drive_select_path)
                self.drive_contents.selection_clear(0, "end")
                self.drive_contents.selection_set(index)
                self.drive_contents.activate(index)
                self.drive_contents.see(index)
            self.drive_select_path = None

    def refresh_drive_manual(self, event=None):
        if event is not None and getattr(event, "widget", None) is getattr(self, "handover_tree", None):
            return "break"
        if not self.busy:
            self.card_modifier_signature = None
            self.refresh_destination(invalidate=True)
        return "break"

    def require_current_drive(self, destination):
        if destination is None:
            raise WorkError("F:\\ 또는 G:\\에 이동식 드라이브를 연결해 주세요.")
        if destination != self.destination:
            raise WorkError("드라이브가 변경되었습니다. 현재 목록을 확인한 뒤 다시 시도해 주세요.")
        validate_fixed_destination(destination)
        return destination

    @staticmethod
    def drive_names_summary(paths):
        names = [path.name for path in paths]
        text = "\n".join("• " + name for name in names[:15])
        if len(names) > 15:
            text += "\n외 {}개".format(len(names) - 15)
        return text

    def choose_drive_files(self):
        self.cancel_drive_action()
        if self.busy:
            return
        destination = self.destination
        paths = ()
        try:
            self.require_current_drive(destination)
            self.set_busy(True, "추가할 파일 선택 중...")
            paths = self.filedialog.askopenfilenames(title="드라이브에 추가할 파일 선택", parent=self.window,
                                                     filetypes=[("모든 파일", "*.*")])
        except (WorkError, OSError) as error:
            self.messagebox.showerror("파일 추가", str(error), parent=self.window)
        finally:
            self.set_busy(False)
        if paths:
            self.start_drive_add(paths, destination)

    def start_drive_add(self, paths, destination=None):
        self.cancel_drive_action()
        if self.busy or not paths:
            return
        destination = self.destination if destination is None else destination
        plan = None
        try:
            self.require_current_drive(destination)
            self.set_busy(True, "파일 추가 확인 중...")
            candidate = prepare_drive_add(paths, destination)
            collisions = [target for _, target, _, state in candidate if state is not None]
            if not collisions or self.messagebox.askyesno(
                    "같은 이름의 파일 확인", "{}\n\n위 파일 {}개를 덮어쓸까요?\n취소하면 아무 파일도 추가하지 않습니다.".format(
                        self.drive_names_summary(collisions), len(collisions)), parent=self.window, default="no", icon="warning"):
                plan = candidate
        except (WorkError, OSError, UnicodeError) as error:
            self.messagebox.showerror("파일 추가", str(error), parent=self.window)
        finally:
            self.set_busy(False)
        if plan:
            self.start_job("파일 추가", lambda: add_drive_files(plan, destination))

    def receive_drive_drop(self, paths, destination, was_busy):
        self.cancel_drive_action()
        if self.busy or was_busy:
            self.messagebox.showinfo("작업 중", "진행 중인 작업이 끝난 뒤 파일을 다시 끌어놓아 주세요.", parent=self.window)
            return
        if destination is None:
            self.messagebox.showerror("파일 추가", "드래그할 때 연결된 드라이브가 없습니다. 연결 후 다시 시도해 주세요.", parent=self.window)
            return
        self.start_drive_add(paths, destination)

    def start_drive_delete(self, event=None):
        self.cancel_drive_action()
        if self.busy:
            return "break"
        selected = self.drive_contents.curselection()
        paths = [self.drive_item_paths[index] for index in selected if 0 <= index < len(self.drive_item_paths)]
        if not paths:
            self.messagebox.showinfo("선택 파일 삭제", "목록에서 삭제할 파일을 선택해 주세요.\nCtrl 또는 Shift로 여러 파일을 선택할 수 있습니다.",
                                     parent=self.window)
            return "break"
        destination = self.destination
        plan = None
        try:
            self.require_current_drive(destination)
            self.set_busy(True, "선택 삭제 확인 중...")
            candidate = prepare_drive_delete(paths, destination)
            if self.messagebox.askyesno("선택 파일 삭제", "{}\n\n선택한 파일 {}개를 삭제할까요?\n휴지통으로 이동하지 않고 바로 삭제됩니다.".format(
                    self.drive_names_summary(paths), len(paths)), parent=self.window, default="no", icon="warning"):
                plan = candidate
        except (WorkError, OSError) as error:
            self.messagebox.showerror("선택 파일 삭제", str(error), parent=self.window)
        finally:
            self.set_busy(False)
        if plan:
            self.start_job("선택 파일 삭제", lambda: delete_drive_files(plan, destination))
        return "break"

    def open_drive_item(self, event=None):
        self.cancel_drive_action()
        if self.busy:
            return "break"
        if event is not None and getattr(event, "num", None) == 1:
            index = self.drive_contents.nearest(event.y)
            bounds = self.drive_contents.bbox(index)
            if bounds is None or not bounds[1] <= event.y < bounds[1] + bounds[3]:
                return "break"
        else:
            selected = self.drive_contents.curselection()
            if not selected:
                return "break"
            index = selected[0]
        if not 0 <= index < len(self.drive_item_paths):
            return "break"
        path = self.drive_item_paths[index]
        try:
            if self.destination is None or path.parent != self.destination:
                raise WorkError("드라이브 목록이 변경되었습니다. 목록을 확인한 뒤 다시 열어 주세요.")
            validate_fixed_destination(self.destination)
            if not path.exists():
                raise WorkError("선택한 파일이나 폴더가 없어졌습니다: {}".format(path))
            open_drive_path(path)
        except (WorkError, OSError, AttributeError) as error:
            self.messagebox.showerror("파일 열기", "선택한 항목을 열지 못했습니다.\n\n{}".format(error),
                                      parent=self.window)
            self.refresh_drive_contents()
        return "break"

    def show_drive_menu(self, event):
        if self.busy:
            return "break"
        index = self.drive_contents.nearest(event.y)
        bounds = self.drive_contents.bbox(index)
        on_item = (bounds is not None and bounds[1] <= event.y < bounds[1] + bounds[3]
                   and 0 <= index < len(self.drive_item_paths))
        if not on_item:
            self.drive_contents.selection_clear(0, "end")
        elif index not in self.drive_contents.curselection():
            self.drive_contents.selection_clear(0, "end")
            self.drive_contents.selection_set(index)
            self.drive_contents.activate(index)
        self.drive_contents.focus_set()
        try:
            selected = self.drive_contents.curselection()
            paths = [self.drive_item_paths[item] for item in selected if 0 <= item < len(self.drive_item_paths)]
            can_delete = bool(paths) and all(path.is_file() and not is_link(path)
                                            and not is_protected_drive_name(path.name) for path in paths)
            can_rename = can_delete and len(paths) == 1
        except (OSError, IndexError):
            can_rename = False
            can_delete = False
        self.drive_menu.entryconfigure(0, state="normal" if can_rename else "disabled")
        self.drive_menu.entryconfigure(1, state="normal" if can_delete else "disabled")
        try:
            self.drive_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.drive_menu.grab_release()
        return "break"

    def ask_rename_name(self, path):
        dialog = self.tk.Toplevel(self.window)
        dialog.title("파일 이름 변경")
        dialog.configure(background="#060b16")
        dialog.transient(self.window)
        dialog.grab_set()
        frame = self.ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        self.ttk.Label(frame, text="새 파일 이름", font=("맑은 고딕", 11, "bold")).pack(anchor="w", pady=(0, 12))
        entry = self.ttk.Entry(frame, width=48, font=("맑은 고딕", 11))
        entry.pack(fill="x")
        entry.insert(0, path.name)
        entry.selection_range(0, len(path.stem) if path.suffix else len(path.name))
        answer = {}

        def accept():
            if defer_ime_commit(dialog, accept):return
            try:
                name = validate_drive_filename(entry.get())
            except (WorkError, UnicodeError) as error:
                self.messagebox.showerror("이름 확인", str(error), parent=dialog)
                entry.focus_set()
                return
            answer["name"] = name
            dialog.destroy()

        buttons = self.ttk.Frame(frame)
        buttons.pack(fill="x", pady=(16, 0))
        self.ttk.Button(buttons, text="변경", command=accept, style="Accent.TButton").pack(side="left", padx=(0, 10))
        self.ttk.Button(buttons, text="취소", command=dialog.destroy, style="Secondary.TButton").pack(side="left")
        entry.bind("<Return>", lambda event: (accept(), "break")[1])
        dialog.bind("<Escape>", lambda event: dialog.destroy())
        dialog.after_idle(entry.focus_set)
        self.window.wait_window(dialog)
        return answer.get("name")

    def start_rename(self, event=None):
        self.cancel_drive_action()
        if self.busy:
            return "break"
        selected = self.drive_contents.curselection()
        if len(selected) != 1 or not 0 <= selected[0] < len(self.drive_item_paths):
            return "break"
        path = self.drive_item_paths[selected[0]]
        destination = self.destination
        started = False
        renamed = None
        outcome = "이름 변경 취소"
        try:
            if destination is None or path.parent != destination:
                raise WorkError("드라이브 목록이 변경되었습니다. 목록을 확인한 뒤 다시 선택해 주세요.")
            validate_fixed_destination(destination)
            if not path.is_file() or is_link(path):
                raise WorkError("이름 변경은 파일 항목에서 사용할 수 있습니다.")
            if is_protected_drive_name(path.name):
                raise WorkError("보존 대상인 수정 스크립트는 이름을 유지합니다.")
            self.set_busy(True, "이름 변경 중...")
            started = True
            new_name = self.ask_rename_name(path)
            if new_name is not None:
                renamed = rename_drive_file(path, destination, new_name)
                outcome = "이름 변경 완료"
                self.append_log("이름 변경: {} → {}\n".format(path.name, renamed.name))
        except (WorkError, OSError, UnicodeError) as error:
            outcome = "이름 변경 중단"
            self.messagebox.showerror("이름 변경", str(error), parent=self.window)
        finally:
            if started:
                self.set_busy(False, outcome)
            self.drive_select_path = renamed
            self.refresh_drive_contents()
            if renamed is not None and renamed in self.drive_item_paths:
                index = self.drive_item_paths.index(renamed)
                self.drive_contents.selection_clear(0, "end")
                self.drive_contents.selection_set(index)
                self.drive_contents.activate(index)
                self.drive_contents.see(index)
        return "break"

    def poll_destination(self):
        try:
            washing = getattr(self, 'wash_app', None)
            if not self.busy and not (washing is not None and washing.busy):
                self.refresh_destination()
        finally:
            self.window.after(1000, self.poll_destination)

    def append_log(self, text):
        append_bounded_log(self.log, text)

    def set_busy(self, value, label="대기 중"):
        if value:
            self.cancel_drive_action()
        if value and not self.busy:
            # Reads started before a file operation cannot overwrite its outcome.
            self.drive_refresh_generation += 1
            self.drive_refresh_pending = True
        self.busy = value
        state = "disabled" if value else "normal"
        self.update_handover_controls()
        for button in (self.import_button, self.empty_button):
            button.configure(state=state)
        for name in ("drive_add_button", "drive_refresh_button", "drive_delete_button", "program_path_button"):
            button = getattr(self, name, None)
            if button is not None:
                button.configure(state=state)
        for button in self.mode_buttons:
            button.configure(state=state)
        for button in self.list_buttons:
            button.configure(state="disabled" if value or self.mode.get() == MODE_FILES else "normal")
        self.number_input.configure(state=state)
        self.folder_input.configure(state="disabled" if value or self.mode.get() == MODE_LIST else "normal")
        self.year_input.configure(state="disabled" if value or self.mode.get() == MODE_LIST else "normal")
        self.status.set(label)

    def request_ui(self, callback, *args):
        ready = threading.Event()
        response = {}
        self.events.put(("request", callback, args, ready, response))
        ready.wait()
        if "error" in response:
            raise response["error"]
        return response.get("value")

    def start_job(self, name, action):
        if self.busy:
            return
        self.set_busy(True, name + " 중...")
        self.append_log("\n=== " + name + " ===\n")

        def work():
            result, error = None, None
            try:
                with redirect_stdout(QueueWriter(self.events)):
                    result = action()
            except BaseException as caught:
                error = caught
            self.events.put(("done", name, result, error))
        threading.Thread(target=work, daemon=True).start()

    def start_import(self):
        self.cancel_drive_action()
        if defer_ime_commit(self.window, self.start_import):return
        if self.busy:
            return
        mode = self.mode.get()
        list_number = self.list_number.get()
        text = self.number_input.get("1.0", "end").strip()
        if not text:
            self.messagebox.showinfo("번호 입력", "프로그램 번호를 입력해 주세요.", parent=self.window)
            return
        try:
            numbers = parse_numbers(text)
        except WorkError as error:
            self.messagebox.showerror("번호 확인", str(error), parent=self.window)
            return
        roots = []
        if mode != MODE_LIST:
            try:
                selected_year = parse_program_year(self.year_input.get())
            except WorkError as error:
                self.messagebox.showerror("연도 확인", str(error), parent=self.window)
                return
            try:
                roots = date_search_folders(self.folder_input.get(), selected_year, base_root=self.program_base_root)
            except WorkError as error:
                self.messagebox.showerror("날짜 폴더 확인", str(error), parent=self.window)
                return
        chooser = lambda number, paths: self.request_ui(self.choose_candidate, number, paths)

        def input_state():
            return (self.mode.get(), self.list_number.get(), self.number_input.get("1.0", "end").strip(),
                    self.year_input.get(), self.folder_input.get(), self.program_base_root)

        requested_inputs = input_state()

        def begin(destination):
            # Inputs remain usable during the short drive check. Never run an
            # older request and then clear text typed while that check waited.
            if input_state() != requested_inputs:
                self.status.set("입력 내용이 바뀌어 작업을 취소했습니다 · 다시 눌러 주세요.")
                return
            self.start_job(MODE_LABELS[mode], lambda: run_batch(
                roots, destination, numbers, chooser=chooser, popup=False, mode=mode, list_number=list_number))

        self.run_with_current_drive(begin)

    def import_shortcut(self, event):
        self.start_import()
        return "break"

    def start_empty(self):
        # 번호 처리 함수와 연결하지 않는 별도의 버튼 동작입니다.
        self.cancel_drive_action()
        if self.busy:
            return
        self.run_with_current_drive(lambda destination: self.start_job(
            "드라이브 비우기", lambda: empty_fixed_drive(destination)))

    def choose_candidate(self, number, paths):
        dialog = self.tk.Toplevel(self.window)
        dialog.title("O{} 파일 선택".format(number))
        dialog.configure(background="#060b16")
        dialog.transient(self.window)
        dialog.grab_set()
        frame = self.ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        self.ttk.Label(frame, text="같은 번호가 여러 곳에 있습니다. 가져올 파일을 선택하세요.",
                       font=("맑은 고딕", 11, "bold")).pack(anchor="w", pady=(0, 12))
        listing = self.tk.Listbox(frame, width=110, height=min(12, len(paths)), exportselection=False,
                                  font=("맑은 고딕", 10), background="#050a14", foreground="#eaf0fc",
                                  selectbackground="#2a66f2", selectforeground="#ffffff", relief="flat",
                                  highlightthickness=1, highlightbackground="#4a515e", highlightcolor="#8db3ff")
        listing.pack(fill="both", expand=True)
        horizontal = self.ttk.Scrollbar(frame, orient="horizontal", command=listing.xview)
        horizontal.pack(fill="x")
        listing.configure(xscrollcommand=horizontal.set)
        for path in paths:
            listing.insert("end", str(path))
        listing.selection_set(0)
        answer = {}

        def choose():
            selected = listing.curselection()
            if selected:
                answer["path"] = paths[selected[0]]
                dialog.destroy()
        buttons = self.ttk.Frame(frame)
        buttons.pack(fill="x", pady=(10, 0))
        self.ttk.Button(buttons, text="선택", command=choose, style="Accent.TButton").pack(side="left", padx=(0, 10))
        self.ttk.Button(buttons, text="취소", command=dialog.destroy, style="Secondary.TButton").pack(side="left")
        listing.bind("<Double-Button-1>", lambda event: choose())
        self.window.wait_window(dialog)
        return answer.get("path")

    def drain_events(self):
        deadline = time.monotonic() + .012
        for _ in range(200):
            if time.monotonic() >= deadline:
                break
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break
            if event[0] == "text":
                self.append_log(event[1])
            elif event[0] == "machine_sample":
                _, ip, record, observed, cancel = event
                self.receive_machine_sample(ip, record, observed, cancel)
            elif event[0] == "machine_connection":
                error = event[1]
                if error != self.machine_monitor_error:
                    if error:
                        SuiteErrors.capture(error,feature='설비 모니터링',stage='연결')
                        self.append_log('가공현황 연결 오류: '+error+'\n')
                    self.machine_monitor_error = error
            elif event[0] == "drive_drop":
                self.receive_drive_drop(*event[1:])
            elif event[0] == "drive_drop_error":
                self.messagebox.showerror("파일 드래그", event[1], parent=self.window)
            elif event[0] == "handover_loaded":
                _, store, notes, error = event
                self.finish_handover_load(store, notes, error)
            elif event[0] == "handover_saved":
                _, callback, result, error = event
                self.handover_writing = False
                self.update_handover_controls()
                callback(result, error)
            elif event[0] == "request":
                _, callback, args, ready, response = event
                try:
                    response["value"] = callback(*args)
                except BaseException as error:
                    response["error"] = error
                finally:
                    ready.set()
            elif event[0] == "drive_listing":
                self.finish_drive_listing(*event[1:])
            elif event[0] == "drive_refreshed":
                self.finish_drive_refresh(*event[1:])
            elif event[0] == "modifier_done":
                self.finish_card_modifier(*event[1:])
            elif event[0] == "done":
                _, name, result, error = event
                self.set_busy(False, name + (" 중단" if error else " 완료"))
                self.refresh_drive_contents()
                if error is not None:
                    self.append_log("작업 중단: " + str(error) + "\n")
                    self.messagebox.showerror("작업 중단", str(error), parent=self.window)
                elif name in MODE_LABELS.values():
                    self.number_input.delete("1.0", "end")
                    warnings = (missing_program_warnings(result["missing_numbers"], result["list_created"],
                                                         result["list_number"])
                                + result["alarms"])
                    if warnings:
                        self.messagebox.showwarning("프로그램 확인 필요", "\n".join(warnings), parent=self.window)
                if getattr(self, "active_tab", "cnc") == "cnc":
                    self.number_input.focus_set()
        self.window.after(80, self.drain_events)

    def initialize_suite(self):
        self._suite_stopped = False
        self._suite_exit_pending = False
        self._suite_exit_timer = None
        self._suite_timer = None
        self._suite_states = {}
        self._suite_events = queue.Queue(maxsize=32)
        self._suite_children = SuiteCompanionManager(suite_companion_payloads(), APP_DIR)
        self.material_quick.connect(self._suite_children)
        self.window.after_idle(self._start_material_owner)
        try:
            owner = int(self.window.wm_frame(), 0) if os.name == 'nt' else None
        except (ValueError, self.tk.TclError):
            owner = None
        def enqueue(action):
            try: self._suite_events.put_nowait(action)
            except queue.Full: pass
        self._suite_tray = SuiteWindowsTray(enqueue, title='지후니우스', owner_hwnd=owner)
        if not self._suite_tray.start() and os.name == 'nt':
            self.status.set('트레이 연결 실패 · Ctrl+Shift+Q: 완전 종료')
        self.window.bind('<Control-Shift-Q>', lambda event: self.request_complete_exit(), add='+')
        self.window.bind('<Control-Shift-q>', lambda event: self.request_complete_exit(), add='+')
        self._suite_timer = self.window.after(200, self.poll_suite)

    def _start_material_owner(self):
        if self._suite_stopped:return
        try:self._suite_children.start_material_client()
        except Exception as error:
            self.status.set('소재 수집 시작 확인 필요')
            self.messagebox.showerror('소재 사용량 조사(Beta)',str(error),parent=self.window)

    def open_companion(self, key):
        if defer_ime_commit(self.window, lambda: self.open_companion(key)): return
        self._suite_exit_pending = False
        try:
            self._suite_children.toggle(key)
        except Exception as error:
            self.restore_from_tray()
            self.messagebox.showerror('보조창 열기·닫기', str(error), parent=self.window)

    def restore_from_tray(self, cancel_exit=True):
        if self._suite_stopped: return
        if cancel_exit: self._suite_exit_pending = False
        self.window.deiconify()
        self.window.lift()
        try: self.window.focus_force()
        except self.tk.TclError: pass

    def poll_suite(self):
        if self._suite_stopped: return
        for _ in range(32):
            try: action = self._suite_events.get_nowait()
            except queue.Empty: break
            if action == 'show': self.restore_from_tray()
            elif action in ('protrusion', 'wash-log'): self.open_companion(action)
            elif action == 'quit': self.request_complete_exit()
            elif action == 'failed':
                self.restore_from_tray()
                self.status.set('트레이 연결이 끊겼습니다 · Ctrl+Shift+Q: 완전 종료')
            if self._suite_stopped: return
        running = set(self._suite_children.running_keys())
        material_error=self._suite_children.pop_material_error()
        if isinstance(material_error,str) and material_error:
            self.status.set('소재 조사 연결 확인 필요')
            self.messagebox.showerror('소재 사용량 조사(Beta)',material_error,parent=self.window)
        for key, button in self._suite_buttons.items():
            opened = self._suite_children.material_visible() if key == 'material' else key in running
            if self._suite_states.get(key) != opened:
                button.configure(style='Open.Popup.TButton' if opened else 'Popup.TButton')
                self._suite_states[key] = opened
        self.material_quick.poll()
        self._suite_timer = self.window.after(200, self.poll_suite)

    def close(self):
        self.cancel_drive_action()
        if self._suite_stopped or self._suite_exit_pending: return
        if defer_ime_commit(self.window, self.close): return
        current = getattr(self, '_suite_close_dialog', None)
        if current is not None and current.winfo_exists():
            current.lift()
            current.focus_set()
            return
        grabbed = self.window.grab_current()
        if grabbed is not None:
            grabbed.lift()
            grabbed.focus_set()
            return
        previous_focus = self.window.focus_get()
        dialog = self.tk.Toplevel(self.window)
        self._suite_close_dialog = dialog
        dialog.withdraw()
        dialog.title('지후니우스 종료')
        dialog.configure(background='#060b16')
        dialog.transient(self.window)
        dialog.resizable(False, False)
        frame = self.ttk.Frame(dialog, padding=22)
        frame.pack(fill='both', expand=True)
        self.ttk.Label(frame, text='프로그램을 어떻게 닫을까요?',
                       font=('맑은 고딕', 12, 'bold')).pack(anchor='w')
        self.ttk.Label(frame, text='시스템 트레이로 보내면 백그라운드에서 계속 실행됩니다.').pack(
            anchor='w', pady=(10, 20))
        buttons = self.ttk.Frame(frame)
        buttons.pack(fill='x')

        def choose(action=None):
            if getattr(self, '_suite_close_dialog', None) is not dialog: return
            self._suite_close_dialog = None
            dialog.grab_release()
            dialog.destroy()
            if action == 'exit':
                self.request_complete_exit()
            elif action == 'tray':
                self._hide_to_tray()
            else:
                try:
                    if previous_focus is not None and previous_focus.winfo_exists():
                        previous_focus.focus_set()
                    else:
                        self.window.focus_set()
                except self.tk.TclError: pass

        self.ttk.Button(buttons, text='완전 종료', style='Danger.TButton',
                        command=lambda: choose('exit')).pack(side='left', padx=(0, 10))
        self.ttk.Button(buttons, text='시스템 트레이로 보내기', style='Accent.TButton',
                        command=lambda: choose('tray')).pack(side='left', padx=(0, 10))
        cancel = self.ttk.Button(buttons, text='취소', style='Secondary.TButton', command=choose)
        cancel.pack(side='right')
        dialog.protocol('WM_DELETE_WINDOW', choose)
        dialog.bind('<Escape>', lambda event: (choose(), 'break')[1])
        dialog.update_idletasks()
        x = self.window.winfo_rootx() + max(0, (self.window.winfo_width() - dialog.winfo_reqwidth()) // 2)
        y = self.window.winfo_rooty() + max(0, (self.window.winfo_height() - dialog.winfo_reqheight()) // 2)
        dialog.geometry('+{}+{}'.format(x, y))
        dialog.deiconify()
        dialog.grab_set()
        cancel.focus_set()

    def _hide_to_tray(self):
        placement = getattr(self, '_window_state', None)
        if placement is not None: placement.flush()
        self.cancel_drive_action()
        self._suite_exit_pending = False
        if self._suite_tray.available:
            self.window.withdraw()
        else:
            # A failed notification icon must not make the application unreachable.
            self.status.set('작업표시줄로 최소화 · Ctrl+Shift+Q: 완전 종료')
            self.window.iconify()

    def _suite_shutdown_allowed(self):
        if getattr(self, 'wash_app', None) is not None and self.wash_app.busy:
            self.wash_app.stop.set()
            self.messagebox.showinfo('중지 중', '세척 체크를 중지하고 있습니다. 종료 후 완전 종료를 다시 눌러 주세요.', parent=self.window)
            return False
        if getattr(self, 'handover_dialog', None) is not None:
            self.handover_dialog.lift()
            self.handover_dialog.focus_set()
            return False
        if self.handover_writing:
            self.messagebox.showinfo('인수인계 저장 중', '인수인계 저장이 끝난 뒤 완전 종료해 주세요.', parent=self.window)
            return False
        if self.busy:
            self.messagebox.showinfo('작업 중', '진행 중인 작업이 끝난 뒤 완전 종료해 주세요.', parent=self.window)
            return False
        return True

    def request_complete_exit(self):
        self.cancel_drive_action()
        if self._suite_stopped or self._suite_exit_pending: return
        if defer_ime_commit(self.window, self.request_complete_exit): return
        self.restore_from_tray(cancel_exit=False)
        if not self._suite_shutdown_allowed(): return
        try:
            self._suite_children.request_close_all()
        except Exception as error:
            self.status.set('열린 창 확인 후 완전 종료를 다시 눌러 주세요.')
            self.append_log('완전 종료 보류: ' + str(error) + '\n')
            return
        self._suite_exit_pending = True
        self._suite_exit_deadline = time.monotonic() + (20.0 if 'material' in self._suite_children.running_keys() else 2.0)
        self._poll_suite_exit()

    def _poll_suite_exit(self):
        if not self._suite_exit_pending or self._suite_stopped: return
        if not self._suite_children.running_keys():
            self._suite_exit_pending = False
            self._finish_suite_shutdown()
        elif time.monotonic() >= self._suite_exit_deadline:
            # A child's Cancel is indistinguishable from a slow save without
            # changing that app. Expire this attempt; never quit hours later.
            self._suite_exit_pending = False
            self.status.set('보조창의 저장·종료 확인 후 완전 종료를 다시 눌러 주세요.')
            self.append_log('열린 보조창이 있어 지후니우스를 유지합니다. 저장·종료 확인 후 완전 종료를 다시 눌러 주세요.\n')
        else:
            self._suite_exit_timer = self.window.after(100, self._poll_suite_exit)

    def _finish_suite_shutdown(self):
        self.cancel_drive_action()
        if self._suite_stopped or not self._suite_shutdown_allowed(): return
        if self._suite_children.running_keys(): return
        if getattr(self, 'stl_app', None) is not None:
            self.stl_app.close(destroy=False)
        if getattr(self, 'drive_drop', None) is not None:
            self.drive_drop.close()
        if getattr(self, 'machine_monitor', None) is not None:
            self.machine_monitor.stop()
        self.dismiss_machine_toast()
        self._suite_stopped = True
        for timer in (self._suite_timer, self._suite_exit_timer):
            if timer is not None:
                try: self.window.after_cancel(timer)
                except self.tk.TclError: pass
        self._suite_tray.stop()
        self.window.destroy()




SUITE_APP_VERSION = '2026.11.11.4'
SUITE_UPDATE_PROTOCOL = 1
SuiteUpdater = ...  # build: tools/build_app.py
def main():
    if "--console" in sys.argv:
        return main_console()
    context = SuiteUpdater.managed_context(SUITE_APP_VERSION)
    if context is None:
        code = SuiteUpdater.launch(Path(__file__).resolve(), SUITE_APP_VERSION, sys.argv[1:])
        if code:
            raise SystemExit(code)
        return
    lease = SuiteUpdater.managed_lease(context)
    try:
        SuiteErrors.install('지후니우스',SUITE_APP_VERSION)
        configure_windows_app_identity()
        import tkinter as tk
        window = tk.Tk()
        app = IntegrationApp(window)
        SuiteUpdater.attach(app, context, SUITE_APP_VERSION)
        SuiteErrors.attach(app,Path(HANDOVER_SHARED_PARENT)/HANDOVER_FOLDER_NAME/'오류기록')
        SuiteUpdater.mark_ready(context)
        window.mainloop()
    finally:
        lease.release()


def report_gui_startup_error(error):
    message = "프로그램을 실행하지 못했습니다.\n\n{}".format(error)
    if os.name == "nt":
        ctypes.windll.user32.MessageBoxW(0, message, "지후니우스 실행 오류", 0x10)
    else:
        print(message, file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n종료했습니다.")
    except Exception as error:
        if "--console" in sys.argv:
            print("\n실행 오류: " + str(error))
            try:
                input("Enter를 누르면 닫힙니다.")
            except (EOFError, KeyboardInterrupt):
                pass
        else:
            report_gui_startup_error(error)
        sys.exit(1)
