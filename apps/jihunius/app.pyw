#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""파일만 가져오기 / 리스트만 만들기 / 파일 + 리스트 만들기.

Windows / Python 3.8 이상. 추가 패키지 설치 없이 실행합니다.
지후니우스.pyw를 더블클릭하면 콘솔 창 없이 프로그램 화면만 열립니다.
검색 기준: \\192.168.0.254\내부공유폴더\★NC프로그램파일
연도 입력칸에 2026처럼 입력하면 ★ 2026 폴더를 선택합니다. 기본값은 2026입니다.
7.1 또는 07.01, 10.12처럼 날짜 폴더를 지정합니다.
날짜의 월에 맞는 월 폴더를 자동 선택합니다. (예: ★ 2026/10월/10.13)
월·일의 앞자리 0은 생략할 수 있으며, 같은 날짜의 폴더 표기도 인식합니다.
지정한 날짜 폴더와 그 안의 하위폴더만 검색하며, 다른 날짜 폴더는 제외합니다.
기준 경로는 고정합니다. 저장은 연결된 이동식 F:\를 우선 사용하고, 없으면 G:\를 사용합니다.
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
PROGRAM_BASE_ROOT = r"\\192.168.0.254\내부공유폴더\★NC프로그램파일"
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
CARD_MODIFIER_BYTES = b'# \xec\x88\x98\xec\xa0\x9510.30 \xe2\x80\x94 \xea\xb8\xb0\xec\xa1\xb4 \xec\x88\x98\xec\xa0\x959.7 \xea\xb7\x9c\xec\xb9\x99 + \xec\x8b\x9c\xec\x9e\x91 \xea\xb5\xac\xea\xb0\x84 G4U2.0 \xec\x9e\x90\xeb\x8f\x99 \xec\xb6\x94\xea\xb0\x80 (\xeb\xaa\xa8\xeb\x93\xa0 \xed\x98\xb8\xea\xb8\xb0 \xea\xb3\xb5\xed\x86\xb5)\nimport os\nimport re\nimport ctypes\n\nG4U2_ADD_LINE = b\'G4U2.0\'\n\nG4U2_M11 = re.compile(rb\'M0*11\')\n\nG4U2_MOVE = re.compile(rb\'G0+Z\\+?10(?:\\.0*)?T0+\')\n\nG4U2_DWELL = re.compile(rb\'G0*4(?![0-9.])\')\n\nG4U2_SAME_DWELL = re.compile(rb\'G0*4U\\+?2(?:\\.0*)?\')\n\nG4U2_MARKER = re.compile(rb\'-{5,}[ \\t]*$\')\n\nG4U2_NUMBER = re.compile(rb\'O[0-9]+\')\n\ndef g4u2_line_body(line):\n    return line.rstrip(b\'\\r\\n\')\n\ndef g4u2_line_ending(line):\n    return line[len(g4u2_line_body(line)):]\n\ndef g4u2_code_lines(lines):\n    """\xec\x9d\xb8\xec\xbd\x94\xeb\x94\xa9\xec\x9d\x84 \xeb\xb0\x94\xea\xbe\xb8\xec\xa7\x80 \xec\x95\x8a\xea\xb3\xa0 \xec\xa3\xbc\xec\x84\x9d/\xea\xb3\xb5\xeb\xb0\xb1/\xed\x96\x89\xeb\xb2\x88\xed\x98\xb8\xeb\xa5\xbc \xec\xa0\x9c\xec\x99\xb8\xed\x95\x9c \xeb\xaa\x85\xeb\xa0\xb9\xec\x9d\x84 \xeb\xb9\x84\xea\xb5\x90\xed\x95\xa9\xeb\x8b\x88\xeb\x8b\xa4."""\n    entries = []\n    depth = 0\n    for index, line in enumerate(lines):\n        raw = g4u2_line_body(line)\n        if index == 0 and raw.startswith(b\'\\xef\\xbb\\xbf\'):\n            raw = raw[3:]\n        code = bytearray()\n        for char in raw:\n            if char == 40:\n                depth += 1\n            elif char == 41 and depth:\n                depth -= 1\n            elif not depth:\n                if char == 59:  # ; \xec\x9d\xb4\xed\x9b\x84 \xec\xa3\xbc\xec\x84\x9d\n                    break\n                code.append(char)\n        clean = re.sub(rb\'[ \\t]\', b\'\', bytes(code)).upper()\n        clean = re.sub(rb\'^N[0-9]+\', b\'\', clean)\n        if clean:\n            entries.append((index, clean))\n    return entries\n\ndef g4u2_initial_mode(code):\n    words = re.findall(rb\'[GM][0-9]+\', code)\n    return (b\'\'.join(words) == code and len(words) == 4\n            and {(word[:1], int(word[1:])) for word in words}\n            == {(b\'G\', 99), (b\'G\', 40), (b\'G\', 97), (b\'M\', 9)})\n\ndef add_g4u2(data):\n    """(\xea\xb2\xb0\xea\xb3\xbc \xeb\xb0\x94\xec\x9d\xb4\xed\x8a\xb8, \xec\x83\x81\xed\x83\x9c, \xec\x84\xa4\xeb\xaa\x85). \xec\x9d\xbc\xec\xb9\x98\xed\x95\x98\xeb\x8a\x94 \xec\x8b\x9c\xec\x9e\x91 \xea\xb5\xac\xea\xb0\x84 \xed\x95\x98\xeb\x82\x98\xeb\xa7\x8c \xeb\xb3\x80\xea\xb2\xbd\xed\x95\xa9\xeb\x8b\x88\xeb\x8b\xa4."""\n    if b\'\\x00\' in data:\n        return data, \'\xea\xb1\xb4\xeb\x84\x88\xeb\x9c\x80\', \'\xeb\xb0\x94\xec\x9d\xb4\xeb\x84\x88\xeb\xa6\xac \xeb\x98\x90\xeb\x8a\x94 UTF-16 \xed\x8c\x8c\xec\x9d\xbc\'\n    # \xed\x8c\x90\xeb\xb3\x84 \xeb\x8c\x80\xec\x83\x81\xec\x9d\x80 \xec\x95\x9e 200\xed\x96\x89\xec\x9d\xb4\xeb\xa9\xb0 \xeb\x82\x98\xeb\xa8\xb8\xec\xa7\x80 \xeb\xb0\x94\xec\x9d\xb4\xed\x8a\xb8\xeb\x8a\x94 \xea\xb7\xb8\xeb\x8c\x80\xeb\xa1\x9c \xec\x9d\xb4\xec\x96\xb4 \xeb\xb6\x99\xec\x9e\x85\xeb\x8b\x88\xeb\x8b\xa4.\n    lines = data.splitlines(keepends=True)[:200]\n    entries = g4u2_code_lines(lines)\n    meaningful = [(i, c) for i, c in entries if c != b\'%\']\n    if not meaningful or not G4U2_NUMBER.fullmatch(meaningful[0][1]):\n        return data, \'\xea\xb1\xb4\xeb\x84\x88\xeb\x9c\x80\', \'\xec\x8b\x9c\xec\x9e\x91 \xeb\xb6\x80\xeb\xb6\x84\xec\x97\x90 NC \xed\x94\x84\xeb\xa1\x9c\xea\xb7\xb8\xeb\x9e\xa8 O\xeb\xb2\x88\xed\x98\xb8\xea\xb0\x80 \xec\x97\x86\xec\x9d\x8c\'\n    # \xed\x95\x98\xeb\x82\x98\xec\x9d\x98 \xed\x94\x84\xeb\xa1\x9c\xea\xb7\xb8\xeb\x9e\xa8\xeb\xa7\x8c \xec\x9e\x88\xeb\x8a\x94 \xec\x9d\xbc\xeb\xb0\x98 NC \xed\x8c\x8c\xec\x9d\xbc\xec\x9d\x84 \xeb\x8c\x80\xec\x83\x81\xec\x9c\xbc\xeb\xa1\x9c \xed\x95\xa9\xeb\x8b\x88\xeb\x8b\xa4.\n    if sum(bool(G4U2_NUMBER.fullmatch(c)) for _, c in entries) != 1:\n        return data, \'\xea\xb1\xb4\xeb\x84\x88\xeb\x9c\x80\', \'\xec\x8b\x9c\xec\x9e\x91 \xeb\xb6\x80\xeb\xb6\x84\xec\x97\x90 \xec\x97\xac\xeb\x9f\xac \xed\x94\x84\xeb\xa1\x9c\xea\xb7\xb8\xeb\x9e\xa8\xec\x9d\xb4 \xec\x9e\x88\xec\x96\xb4 \xec\x9c\x84\xec\xb9\x98 \xed\x99\x95\xec\x9d\xb8 \xed\x95\x84\xec\x9a\x94\'\n    matches = []\n    for k, (index, code) in enumerate(entries):\n        if not G4U2_M11.fullmatch(code) or k < 3:\n            continue\n        if not (re.fullmatch(rb\'G0*300\', entries[k-3][1])\n                and g4u2_initial_mode(entries[k-2][1])\n                and re.fullmatch(rb\'M0*5\', entries[k-1][1])):\n            continue\n        j = k + 1\n        dwell_index = None\n        dwell_code = None\n        if j < len(entries) and G4U2_DWELL.match(entries[j][1]):\n            dwell_index, dwell_code = entries[j]\n            j += 1\n        if j + 3 >= len(entries):\n            continue\n        if (G4U2_MOVE.fullmatch(entries[j][1])\n                and re.fullmatch(rb\'M0*200\', entries[j+1][1])\n                and re.fullmatch(rb\'M0*20\', entries[j+2][1])\n                and re.fullmatch(rb\'M0*10\', entries[j+3][1])):\n            matches.append((index, dwell_index, dwell_code))\n    if len(matches) != 1:\n        reason = \'\xeb\x8c\x80\xec\x83\x81 \xec\x8b\x9c\xec\x9e\x91 \xea\xb5\xac\xea\xb0\x84 \xec\x97\x86\xec\x9d\x8c\' if not matches else \'\xeb\x8c\x80\xec\x83\x81 \xea\xb5\xac\xea\xb0\x84\xec\x9d\xb4 \xec\x97\xac\xeb\x9f\xac \xea\xb0\x9c\xeb\x9d\xbc \xec\x9c\x84\xec\xb9\x98 \xed\x99\x95\xec\x9d\xb8 \xed\x95\x84\xec\x9a\x94\'\n        return data, \'\xea\xb1\xb4\xeb\x84\x88\xeb\x9c\x80\', reason\n    index, dwell_index, dwell_code = matches[0]\n    if dwell_index is not None:\n        if G4U2_SAME_DWELL.fullmatch(dwell_code):\n            return data, \'\xea\xb8\xb0\xec\xa1\xb4 \xec\x9e\x88\xec\x9d\x8c\', \'G4U2.0\xec\x9d\xb4 \xec\x9d\xb4\xeb\xaf\xb8 \xec\x9e\x88\xec\x9d\x8c\'\n        # \xec\xb0\xb8\xea\xb3\xa0 \xed\x8c\x8c\xec\x9d\xbc\xec\xb2\x98\xeb\x9f\xbc \xeb\xaa\x85\xeb\xa0\xb9 \xeb\x92\xa4\xec\x97\x90 \xeb\xb6\x99\xec\x9d\xb8 \xed\x91\x9c\xec\x8b\x9c\xeb\xa7\x8c \xec\xa0\x9c\xea\xb1\xb0\xed\x95\xa9\xeb\x8b\x88\xeb\x8b\xa4.\n        body = g4u2_line_body(lines[dwell_index])\n        marker = G4U2_MARKER.search(body)\n        plain = G4U2_MARKER.sub(b\'\', dwell_code)\n        if marker and G4U2_SAME_DWELL.fullmatch(plain):\n            offset = sum(len(line) for line in lines[:dwell_index])\n            new_line = body[:marker.start()] + g4u2_line_ending(lines[dwell_index])\n            result = data[:offset] + new_line + data[offset+len(lines[dwell_index]):]\n            return result, \'\xed\x91\x9c\xec\x8b\x9c \xec\xa0\x9c\xea\xb1\xb0\', \'G4U2.0 \xeb\x92\xa4\xec\x9d\x98 ----- \xed\x91\x9c\xec\x8b\x9c\xeb\xa7\x8c \xec\xa0\x9c\xea\xb1\xb0\'\n        return data, \'\xed\x99\x95\xec\x9d\xb8 \xed\x95\x84\xec\x9a\x94\', \'\xeb\x8c\x80\xec\x83\x81 \xec\x9c\x84\xec\xb9\x98\xec\x97\x90 \xeb\x8b\xa4\xeb\xa5\xb8 \xeb\x8c\x80\xea\xb8\xb0 \xeb\xaa\x85\xeb\xa0\xb9\xec\x9d\xb4 \xec\x9e\x88\xec\x96\xb4 \xec\x9c\xa0\xec\xa7\x80\xed\x95\xa8\'\n    end = sum(len(line) for line in lines[:index+1])\n    newline = g4u2_line_ending(lines[index]) or b\'\\r\\n\'\n    indent = re.match(rb\'[ \\t]*\', lines[index]).group()\n    result = data[:end] + indent + G4U2_ADD_LINE + newline + data[end:]\n    return result, \'\xec\xb6\x94\xea\xb0\x80 \xec\x99\x84\xeb\xa3\x8c\', \'M11 \xeb\x8b\xa4\xec\x9d\x8c\xec\x97\x90 G4U2.0 \xed\x95\x9c \xec\xa4\x84 \xec\xb6\x94\xea\xb0\x80\'\n\nfolder_path = os.path.dirname(os.path.abspath(__file__))\n\npi_value_map_a12 = {\n    "9.7": "-1.0", "9.8": "-1.0", "9.9": "-1.0", "10.0": "-1.0",\n    "10.1": "-1.0", "10.2": "-1.0", "10.3": "-1.0", "10.4": "-1.0",\n    "10.5": "-1.0", "10.6": "-1.0", "10.7": "-1.0", "10.8": "-1.0",\n    "10.9": "-0.9", "11.0": "-0.8", "11.1": "-0.7", "11.2": "-0.6",\n    "11.3": "-0.5", "11.4": "-0.4", "11.5": "-0.3", "11.6": "-0.3",\n    "11.7": "-0.3"\n}\n\npi_value_map_a14 = {\n    "11.8": "-1.0", "11.9": "-1.0", "12.0": "-1.0", "12.1": "-1.0",\n    "12.2": "-1.0", "12.3": "-1.0", "12.4": "-1.0", "12.5": "-1.0",\n    "12.6": "-1.0", "12.7": "-1.0", "12.8": "-1.0",\n    "12.9": "-0.9", "13.0": "-0.8", "13.1": "-0.7", "13.2": "-0.6",\n    "13.3": "-0.5", "13.4": "-0.4", "13.5": "-0.3", "13.6": "-0.3",\n    "13.7": "-0.3"\n}\n\nalarm_log = []\ng4_summary = {}\n\nfor filename in os.listdir(folder_path):\n    # \xea\xb8\xb0\xec\xa1\xb4 NC \xed\x8c\x8c\xec\x9d\xbc\xea\xb3\xbc \xec\xa7\x80\xed\x9b\x84\xeb\x8b\x88\xec\x9a\xb0\xec\x8a\xa4\xea\xb0\x80 \xec\xa0\x80\xec\x9e\xa5\xed\x95\x9c \xed\x99\x95\xec\x9e\xa5\xec\x9e\x90 \xec\x97\x86\xeb\x8a\x94 O\xeb\xb2\x88\xed\x98\xb8 \xed\x8c\x8c\xec\x9d\xbc\xec\x9d\x84 \xec\xb2\x98\xeb\xa6\xac\xed\x95\xa9\xeb\x8b\x88\xeb\x8b\xa4.\n    if (os.path.isfile(os.path.join(folder_path, filename))\n            and (filename.lower().endswith(".nc")\n                 or (not os.path.splitext(filename)[1]\n                     and re.fullmatch(r"O[0-9]{4}(?:[^0-9].*)?", filename, re.I)))):\n        file_path = os.path.join(folder_path, filename)\n\n        with open(file_path, \'r\', encoding=\'utf-8\', errors=\'ignore\') as file:\n            content = file.read()\n\n        # --- \xec\xb6\x94\xea\xb0\x80\xeb\x90\x9c \xeb\xb6\x80\xeb\xb6\x84: \xed\x8c\x8c\xec\x9d\xbc \xeb\x82\xb4\xeb\xb6\x80\xec\x9d\x98 A9.7\xec\x9d\x84 A10\xec\x9c\xbc\xeb\xa1\x9c \xea\xb0\x80\xec\x9e\xa5 \xeb\xa8\xbc\xec\xa0\x80 \xeb\xb3\x80\xea\xb2\xbd ---\n        content = content.replace("A9.7", "A10.")\n        # ---------------------------------------------------------\n\n        content = re.sub(r\'X-(1[5-9])(?:\\.(\\d{1,3}))?\', lambda m: f"X-14" + (f".{m.group(2)}" if m.group(2) else ""), content)\n        content = re.sub(r\'X-14\\.[5-9](\\d{0,2})\', lambda m: f"X-14.4{m.group(1)}", content)\n        content = re.sub(r\'Y(2[0-5])(?:\\.(\\d{1,3}))?\', lambda m: f"Y19" + (f".{m.group(2)}" if m.group(2) else ""), content)\n        content = re.sub(r\'Y19\\.9(\\d{0,2})\', lambda m: f"Y19.8{m.group(1)}", content)\n        content = re.sub(r\'Y-(2[0-5])(?:\\.(\\d{1,3}))?\', lambda m: f"Y-19" + (f".{m.group(2)}" if m.group(2) else ""), content)\n        content = re.sub(r\'Y-19\\.9(\\d{0,2})\', lambda m: f"Y-19.8{m.group(1)}", content)\n\n        def fix_x_decimal(match):\n            return f"X-14.4{match.group(1)}"\n        content = re.sub(r\'X-14\\.[5-9](\\d{2})\', fix_x_decimal, content)\n\n        pi_match = re.search(r\'(\\d{1,2}\\.\\d)\', filename)\n        pi_value = pi_match.group(1) if pi_match else None\n        \n        has_pi_a12 = pi_value in pi_value_map_a12\n        has_pi_a14 = pi_value in pi_value_map_a14\n\n        if has_pi_a12 and "A12" in content:\n            content = re.sub(\n                r\'X\\[#531-(\\-?\\d+\\.\\d+)\\]F0\\.02\',\n                lambda m: f"X[#531{pi_value_map_a12[pi_value]}]F0.02",\n                content\n            )\n            \n        if has_pi_a14 and "A14" in content:\n            content = re.sub(\n                r\'X\\[#531-(\\-?\\d+\\.\\d+)\\]F0\\.02\',\n                lambda m: f"X[#531{pi_value_map_a14[pi_value]}]F0.02",\n                content\n            )\n\n        # \xec\x95\x9e\xec\x97\x90\xec\x84\x9c A9.7\xec\x9d\xb4 A10\xec\x9c\xbc\xeb\xa1\x9c \xeb\xb3\x80\xea\xb2\xbd\xeb\x90\x98\xec\x97\x88\xec\x9c\xbc\xeb\xaf\x80\xeb\xa1\x9c, \xec\x9d\xb4 \xec\x95\x8c\xeb\x9e\x8c \xec\xa1\xb0\xea\xb1\xb4\xeb\x8f\x84 \xec\xa0\x95\xec\x83\x81\xec\xa0\x81\xec\x9c\xbc\xeb\xa1\x9c \xea\xb2\x80\xec\x82\xac\xeb\x90\xa9\xeb\x8b\x88\xeb\x8b\xa4.\n        if has_pi_a12 and "A10" in content:\n            alarm_log.append(f"{filename} \xe2\x86\x92 \xec\xa0\x9c\xeb\xaa\xa9\xea\xb3\xbc \xed\x8c\x8c\xec\x9d\xb4\xea\xb0\x80 \xeb\x8b\xa4\xeb\xa6\x84 \xed\x99\x95\xec\x9d\xb8\xed\x95\x84\xec\x9a\x94 (\xeb\x82\xb4\xeb\xb6\x80\xec\x97\x90 A10 \xec\x9e\x88\xec\x9d\x8c)")\n            \n        if has_pi_a12 and "A12" not in content:\n            alarm_log.append(f"{filename} \xe2\x86\x92 \xec\xa0\x9c\xeb\xaa\xa9\xea\xb3\xbc \xed\x8c\x8c\xec\x9d\xb4\xea\xb0\x80 \xeb\x8b\xa4\xeb\xa6\x84 \xed\x99\x95\xec\x9d\xb8\xed\x95\x84\xec\x9a\x94 (\xec\xa0\x9c\xeb\xaa\xa9\xec\x97\x90 A12 \xed\x8c\x8c\xec\x9d\xb4 \xec\x9e\x88\xec\x9d\x8c, \xeb\x82\xb4\xeb\xb6\x80\xec\x97\x90 A12 \xec\x97\x86\xec\x9d\x8c)")\n            \n        if "A12" in content and not has_pi_a12:\n            alarm_log.append(f"{filename} \xe2\x86\x92 \xec\xa0\x9c\xeb\xaa\xa9\xea\xb3\xbc \xed\x8c\x8c\xec\x9d\xb4\xea\xb0\x80 \xeb\x8b\xa4\xeb\xa6\x84 \xed\x99\x95\xec\x9d\xb8\xed\x95\x84\xec\x9a\x94 (\xeb\x82\xb4\xeb\xb6\x80\xec\x97\x90 A12 \xec\x9e\x88\xec\x9d\x8c, \xec\xa0\x9c\xeb\xaa\xa9\xec\x97\x90 A12 \xed\x8c\x8c\xec\x9d\xb4 \xec\x97\x86\xec\x9d\x8c)")\n\n        if has_pi_a14 and "A14" not in content:\n            alarm_log.append(f"{filename} \xe2\x86\x92 \xec\xa0\x9c\xeb\xaa\xa9\xea\xb3\xbc \xed\x8c\x8c\xec\x9d\xb4\xea\xb0\x80 \xeb\x8b\xa4\xeb\xa6\x84 \xed\x99\x95\xec\x9d\xb8\xed\x95\x84\xec\x9a\x94 (\xec\xa0\x9c\xeb\xaa\xa9\xec\x97\x90 A14 \xed\x8c\x8c\xec\x9d\xb4 \xec\x9e\x88\xec\x9d\x8c, \xeb\x82\xb4\xeb\xb6\x80\xec\x97\x90 A14 \xec\x97\x86\xec\x9d\x8c)")\n            \n        if "A14" in content and not has_pi_a14:\n            alarm_log.append(f"{filename} \xe2\x86\x92 \xec\xa0\x9c\xeb\xaa\xa9\xea\xb3\xbc \xed\x8c\x8c\xec\x9d\xb4\xea\xb0\x80 \xeb\x8b\xa4\xeb\xa6\x84 \xed\x99\x95\xec\x9d\xb8\xed\x95\x84\xec\x9a\x94 (\xeb\x82\xb4\xeb\xb6\x80\xec\x97\x90 A14 \xec\x9e\x88\xec\x9d\x8c, \xec\xa0\x9c\xeb\xaa\xa9\xec\x97\x90 A14 \xed\x8c\x8c\xec\x9d\xb4 \xec\x97\x86\xec\x9d\x8c)")\n\n        converted, g4_status, g4_detail = add_g4u2(content.encode(\'utf-8\'))\n        content = converted.decode(\'utf-8\')\n        g4_summary[g4_status] = g4_summary.get(g4_status, 0) + 1\n        if g4_status == \'\xed\x99\x95\xec\x9d\xb8 \xed\x95\x84\xec\x9a\x94\' or \'\xed\x99\x95\xec\x9d\xb8 \xed\x95\x84\xec\x9a\x94\' in g4_detail:\n            alarm_log.append(f"{filename} \xe2\x86\x92 G4U2.0 \xec\xb6\x94\xea\xb0\x80 \xed\x99\x95\xec\x9d\xb8 \xed\x95\x84\xec\x9a\x94: {g4_detail}")\n\n        new_filename = filename[:5]\n        new_file_path = os.path.join(folder_path, new_filename)\n\n        with open(new_file_path, \'w\', encoding=\'utf-8\') as file:\n            file.write(content)\n\n        if new_filename != filename:\n            os.remove(file_path)\n\nprint("G4U2.0: " + (" / ".join(f"{status} {count}\xea\xb0\x9c" for status, count in g4_summary.items()) or "\xec\xb2\x98\xeb\xa6\xac \xeb\x8c\x80\xec\x83\x81 \xec\x97\x86\xec\x9d\x8c"))\n\nif alarm_log:\n    message = "\\n".join(alarm_log)\n    ctypes.windll.user32.MessageBoxW(0, message, "\xe2\x9a\xa0 \xec\x95\x8c\xeb\x9e\x8c \xeb\xb0\x9c\xec\x83\x9d", 0)\n    print("\\n[\xe2\x9a\xa0\xef\xb8\x8f \xec\x95\x8c\xeb\x9e\x8c \xeb\xb0\x9c\xec\x83\x9d \xed\x8c\x8c\xec\x9d\xbc \xeb\xaa\xa9\xeb\xa1\x9d]\\n")\n    for alarm in alarm_log:\n        print(alarm)\nelse:\n    print("\\n\xe2\x9c\x85 \xec\x95\x8c\xeb\x9e\x8c \xec\x97\x86\xec\x9d\xb4 \xeb\xaa\xa8\xeb\x93\xa0 \xec\x9e\x91\xec\x97\x85 \xec\x99\x84\xeb\xa3\x8c\xeb\x90\xa8.")'
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


def monitor_request(endpoint, fields):
    """NC Gate의 기존 조회 요청만 사용합니다. 이미지나 설정 변경은 요청하지 않습니다."""
    allowed = {
        "monitoring_ajax_setting.php": "loadIPlist",
        "monitoring_ajax_this_machine.php": "callUpdateMachineOne",
    }
    if allowed.get(endpoint) != fields.get("ajax_selector"):
        raise ValueError("지원하지 않는 가공현황 조회입니다.")
    connection = HTTPConnection(MONITOR_HOST, timeout=MONITOR_TIMEOUT)
    try:
        connection.request("POST", "/" + endpoint, body=urlencode(fields).encode("ascii"),
                           headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                                    "Accept": "application/json", "Cache-Control": "no-cache"})
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError("가공현황 서버 응답 오류 ({})".format(response.status))
        raw = response.read(131073)
        if len(raw) > 131072:
            raise ValueError("가공현황 응답이 너무 큽니다.")
        result = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(result, dict):
            raise ValueError("가공현황 응답 형식을 확인해 주세요.")
        return result
    finally:
        connection.close()


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
MACHINE_ALERT_SWITCH_PNGS = {True: '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', False: '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'}


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


MACHINE_ALERT_SOUND_WAV = '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IwAcABUADgAIAAEA+v/z/+3/5v/f/9n/0//N/8j/xP/B/8D/wP/C/8b/y//T/9z/5v/x//z/CAATAB4AJwAvADYAOwA+AD8APgA8ADkANQAwACoAJAAdABcAEAAKAAMA/f/3//D/6v/k/93/1//S/83/yf/F/8T/w//E/8f/zP/S/9r/4//t//j/AwAOABgAIgAqADEANgA5ADsAOwA6ADcANAAvACoAJAAeABgAEgAMAAYAAAD6//T/7f/n/+L/3P/W/9H/zf/K/8f/xv/H/8n/zf/S/9n/4f/q//T///8JABMAHAAlACwAMQA1ADgAOAA4ADYAMgAuACoAJAAfABkAEwANAAgAAgD8//f/8f/r/+X/4P/b/9b/0f/O/8v/yv/K/8v/zv/S/9j/3//o//H/+/8FAA4AFwAgACcALQAxADQANQA1ADQAMQAuACkAJAAfABoAFAAPAAkABAD///n/9P/u/+n/5P/f/9r/1f/S/8//zf/M/83/z//T/9j/3v/m/+7/9/8BAAoAEwAbACIAKAAtADAAMgAyADIAMAAtACkAJAAgABsAFQAQAAsABgABAPz/9//x/+z/5//i/97/2f/V/9L/0P/P/8//0f/U/9j/3v/k/+z/9P/9/wYADgAWAB4AJAApAC0ALwAwAC8ALgArACgAJAAgABsAFgARAAwACAADAP7/+f/0/+//6v/m/+H/3f/Z/9b/1P/S/9L/0//V/9j/3f/j/+r/8v/6/wIACgASABkAIAAlACkALAAtAC0ALAAqACcAJAAgABsAFwASAA4ACQAEAAAA+//3//L/7f/p/+X/4P/d/9n/1//V/9T/1f/W/9n/3f/i/+j/7//3////BwAOABUAHAAhACUAKAAqACsAKgApACYAIwAgABwAFwATAA8ACgAGAAIA/f/5//X/8P/s/+j/5P/g/93/2v/Y/9f/1//Y/9r/3f/i/+f/7f/0//z/AwALABIAGAAdACIAJQAnACgAKAAnACUAIwAfABwAGAAUABAACwAHAAMA///7//f/8//v/+v/5//j/+D/3f/b/9n/2f/Z/9v/3v/h/+b/7P/y//n/AAAHAA4AFAAaAB4AIgAlACYAJgAmACQAIgAfABwAGAAUABAADAAIAAUAAQD9//n/9f/x/+3/6f/m/+P/4P/d/9z/2//b/9z/3v/i/+b/6//x//f//v8EAAsAEQAWABsAHwAiACQAJAAkACMAIQAfABwAGAAVABEADQAKAAYAAgD+//v/9//z//D/7P/p/+X/4v/g/97/3f/d/97/3//i/+X/6v/v//X/+/8BAAgADgATABgAHAAfACEAIgAiACIAIAAeABsAGAAVABEADgAKAAcAAwAAAPz/+f/1//L/7//r/+j/5f/j/+H/3//f/9//4P/i/+X/6f/u//P/+f///wUACwAQABUAGQAcAB8AIAAhACAAHwAdABsAGAAVABIADwALAAgABQABAP7/+//3//T/8f/u/+r/6P/l/+P/4f/h/+H/4f/j/+b/6f/t//L/9//9/wIACAANABIAFgAaABwAHgAfAB8AHgAcABoAGAAVABIADwAMAAkABgACAP///P/5//b/8//w/+3/6v/n/+X/5P/j/+L/4//k/+b/6f/s//H/9v/7/wAABQALAA8AFAAXABoAHAAdAB0AHQAcABoAGAAVABIADwAMAAkABgAEAAEA/v/7//j/9f/y/+//7P/q/+j/5v/k/+T/5P/l/+b/6f/s//D/9P/5//7/AwAIAA0AEQAVABcAGgAbABwAGwAbABkAFwAVABIAEAANAAoABwAEAAIA///8//n/9v/0//H/7v/s/+r/6P/m/+b/5f/m/+f/6f/s/+//8//4//z/AQAGAAoADwASABUAGAAZABoAGgAaABgAFwAVABIAEAANAAsACAAFAAMAAAD9//v/+P/1//P/8P/u/+z/6v/o/+f/5//n/+j/6f/s/+//8v/2//v///8EAAgADAAQABMAFQAXABgAGQAYABgAFgAUABIAEAAOAAsACQAGAAQAAQD+//z/+f/3//T/8v/w/+7/7P/q/+n/6P/o/+n/6v/s/+7/8v/1//n//f8CAAYACgAOABEAEwAVABcAFwAXABcAFgAUABIAEAAOAAsACQAHAAQAAgAAAP3/+//4//b/9P/x/+//7f/s/+r/6v/p/+r/6//s/+7/8f/0//j//P8AAAQACAAMAA8AEQAUABUAFgAWABYAFQAUABIAEAAOAAwACgAHAAUAAwAAAP7//P/6//f/9f/z//H/7//t/+z/6//r/+v/6//s/+7/8f/0//f/+//+/wIABgAKAA0AEAASABMAFAAVABUAFAATABIAEAAOAAwACgAIAAYAAwABAP///f/7//n/9//1//P/8f/v/+7/7f/s/+z/7P/t/+//8f/z//b/+f/9/wEABAAIAAsADgAQABIAEwAUABQAEwATABEAEAAOAAwACgAIAAYABAACAAAA/v/8//r/+P/2//T/8v/x/+//7v/u/+3/7f/u/+//8f/z//b/+f/8////AwAGAAkACwANAA8AEAARABEAEQAQAA8ADgANAAsACQAIAAYABAACAAEA///9//z/+v/4//f/9f/0//P/8v/x//H/8f/x//L/8//1//f/+f/8//7/AQAEAAYACAAKAAwADQAOAA4ADgAOAA0ADAALAAoACAAHAAUABAADAAEAAAD+//3//P/6//n/+P/3//b/9f/0//T/9P/0//T/9f/2//j/+v/8//7/AAACAAQABgAIAAkACgALAAsACwALAAoACgAJAAgABwAGAAUABAACAAEAAAD///7//f/8//v/+v/5//j/+P/3//f/9v/2//f/9//4//n/+//8//7///8BAAMABAAFAAYABwAIAAgACQAIAAgACAAHAAYABgAFAAQAAwACAAEAAQAAAP///v/9//3//P/7//r/+v/5//n/+f/5//n/+f/6//v//P/9//7///8AAAEAAwAEAAQABQAGAAYABgAGAAYABgAFAAUABAAEAAMAAgACAAEAAQAAAP/////+//7//f/9//z//P/8//v/+//7//v/+//8//z//f/9//7///8AAAEAAQACAAMAAwAEAAQABAAEAAQABAADAAMAAwACAAIAAgABAAEAAQAAAAAA/////////v/+//7//v/9//3//f/9//3//f/9//7//v/+//////8AAAAAAQABAAEAAgACAAIAAgACAAIAAgACAAIAAQABAAEAAQABAAAAAAAAAAAAAAAAAAAA/////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='


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
            'yellow': ('#d8b54a', '#201b0b'), 'gray': ('#4b5563', '#ffffff')}.get(color, ('#4b5563', '#ffffff'))


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
        while not self.stopped.is_set() and not cancel.is_set():
            record = None
            try:
                result = self.request("monitoring_ajax_this_machine.php",
                                      {"ajax_selector": "callUpdateMachineOne", "ncgateIP": ip})
                record = monitor_machine_record(result)
            except Exception:
                pass
            if self.stopped.is_set() or cancel.is_set():
                return
            self.events.put(("machine_sample", ip, record, time.monotonic(), cancel))
            if self.stopped.wait(MONITOR_INTERVAL):
                return

# 첨부 로고를 내장합니다. 외부 이미지 파일이나 추가 패키지는 필요하지 않습니다.
APP_USER_MODEL_ID = "Jihunius.NCProgramManager"
APP_ICON_PNGS = {
    256: (
        "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"
    ),
    64: (
        "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"
    ),
    48: (
        "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"
        "AElFTkSuQmCC"
    ),
    32: (
        "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAImklEQVR42rVXe2yV5Rn/ve/7fed+Tg9t6ZViW6XUAgVSCgLKKY6l"
        "uE3YhocYtWzLxqpS4yaLLttcAUeyGBPnNtE5JEMJzl6CC1Gn1NEDTChCEbmUAoWW1tIL7enpuX+X99kfFrO4aqlkz59vnjz35/f8"
        "XmASQiAmuII6PwkArLaWuM/nUwCw/1LjnHP8P8U25uXzB8YY/PALAIIxDgDuFQU//GNx1gLfZxp+cVMex4xjYd4967bc+Wb36vyf"
        "/xmA987ZlTtn55c/9nnqTABATs2K3x9vrSb66ew/tABgVEs3V5LrBqrnvnDw7EaiT15N0vr7H2+5d9G6T3c82USLiu9+LWdq/vMA"
        "imse+GVTx/txam+Iaq9u/MAAMJMxBgDjBnFDpfndoa1EJLHqnjUb564qTjdcQWPJnLunn+k44fJYMmR+9m3z8tIL7khPzbrvR2sf"
        "LrXZ7NJUk0jJtCofn/3oo96BnpM+n090dXXJL9q+kdJcHzDhyJQWRWU8GTEEEcn1D9awtr4jwsLscmHxcnNOYVmW3WqHJJNLnWBX"
        "PMiZmpcNABUVFeMan0xvGAzOSQJMAIlkgmtBjjWVD+Fqop1f7G4TST1O4X4diYgOxhgYYxBMVb/K6I0EQIahMwZmGKYRJRDsdge0"
        "iMTlU71IsaXhJw/W4JrehdLSUmZXPIiEYlBUgXgihv7hgU8BoLm5+WsHwAAwAk073/tJv91mR0dXO1k9HLOWFoCsGkxd4tF1T6C8"
        "dAk8uQJpOW6yW53iwpUzicMnmw7U1tbyQCAgv6q/Xyo+X60SCGw2lub6t5UWzasy04dtPO5UDB7DA2t+gLysfMSTUUhJMKUJl8OF"
        "gcF+/PWNP4FAkf5zsVPtQwc3dIUunhhLWE6qAtdHx2axXrg/51eu2dq9SFKEFnyjhDoix+Th1oMYHg4iEdcgmIrOzi60XGiSpjts"
        "fsf9pOvbt1Uv7gr1DHH29aGAjQGM5aGirZ3nniE639FmEhGFRkfoqaeepFde3CG3PbddPv3EVtq9s072DfZKIjLerOqQBc65Wxhj"
        "8PvrxNcGoTKUqfcWPfzS66vO0b+rySSdyNANGugfoMbGRtJ0jWKJKDXuqadIJEJERAMtJJv9RBuXbA+qUGcTERuv4sqEA7gZdBzH"
        "7anGbEvH6IlT/cPDcwo/XIisZQKpqWmoqKhAY30jzpw5i0cfeQROpxNmUtKBnR3UevXDWGfo9EvpSL+0iW1iAOhmD5G1vGDFmepv"
        "/Zqa3m8yBof7KaHFqf3COQqFRygUDtLRYy3yxS07tbV3bKCULMcuABjLflxRbnANaeXKx6xN77+cbBs6sm9lQWVJ7IKL/n7kXXJ4"
        "VeZN9eB44jRGrkXIaqZgwUyfmDfzDuS+nV7y/GubHQASn1/0yayh3+8XDQ0NJhGBcw4ppfe3jz53ek1lVa6qKEQSLBaLI6klIISA"
        "w+aE1WaBpidhtznNoZFB8fjvqqpbTh16xefzKYFAwJgMELH6+nqTiFLKysocUkosX1i5/nvffCBXFYqR1DSmmxqsDgGX2wmLaoHk"
        "OpJGAqHICHoHupE9NYd85ZXrxpBQ3jAS1tbWcsYYlRXd9ePbp8+vb21tjQFgi0qXrfK4vKQZGguFgwjHQgj2xNFxrB89bcO4dHwQ"
        "RoShZ6ATV3ovcc4FK5heNB9AthBCjudvvAD4M1uekUSUVzxt3vbbp8+f4Xak1ABQMtKzC4kkE1zw0dgwDjZ/iGuX4tA1A0LhiIeS"
        "6D49hNFrUdjtDqbpmszLusWRlpI5U0oJP/xswgB8Ph+XJLGsfMXaW/KnU1yPWEajI42FmYVT3A5PmiQJXdeRPTUPo6MhGFIDIwY9"
        "YUBYOKRJ6L7ci1RvKgxDJ4fdRZnpGZ4xajXxFjQ3NxNjDHOLFi5Y/2ANO9l+bEqSIqv+dfSdeqvFxokAU5pwOJxwp9oRS0Thdrsg"
        "LBwioSAUGYbilEjzZkA3NBaLR9nV/p5hAKivn8QaCkWxGoaJ4oI51qc3PPtydkZuVSg8YnLGVMM0GGccqqJC6iaIAC1uQBUWXIv0"
        "obCkEF53mlSEwt85sKcrGAmeJCLGGJMTV2BTMwOAcHQ0KEkiGovIjLQs9ptHnl26p2k3dFNH1tRshOMhDF0bxrRMJwgEq12AJRX0"
        "9HXik74rSPdmyoud5/nre175JwML19fXCwDmhJwwH/k80BWQU1zewoqFlSstqkXGEzHhcDjNKz2dfFfjDsTjUezY/RdkewqQnzET"
        "sVgUyYgBQzcwZaoXwXg/Aoc+YCPhYba0vGLG/qPv7m5oaBgZmzmaCIg4Y0za7fb5f9u6t7W0uEyGIyHudqXgwNEmtF9sA3SB/IIC"
        "lMyYBZeaitFgFCCAC4b0HC+gSOi6Bo/La4RGg0rNlqrqllMHxgWj8WZASik5Y+zEB0fe2b9o7l3LI7GwbpqmmtTjuH/1OqR602Ca"
        "JhLJBCRJZHg9ICIwMJimDmYyKEJFLBaF0+GmovyS4pZTB1BRsQmBwPKJh5AxBiJiVmbdUJRfcvi+yqoUwzQMIRTWN9grrKoNST0J"
        "IQRIEqmqRapCYUQEkhqZpik45yBJYGCMC269Tm423+C/gLAZfD/bP/jeoX/sc9hciwtyb8222xx8aGTQLJkxR+qaJk3TlE67U4Sj"
        "o7y7r5NFY2GW4p7CVVWVST0pvSlTZDwZwRt7t2/runr5ZCc6+Rf/BhNxwusczjr/9sVriwtnfTcUCn1/3eqHMX3aLSjMuxVvN78l"
        "X9uz7RdnL338kc3msi+e61u9fu3PNpTcVorT505i73tv4dW9L6xK6KG9RPQ/mzDROZYAOBFpjLHXT7QdPpeq5CVaDrfos0pLaHH5"
        "ErZnX13T+cund32mPojuq5f3hcLBoUXz71r2Rt2uBIvaY27V44lrIzdFRJjP51O+7Ntd66tVxtop6upoUtzvP7GHMptbH33VAAAA"
        "AElFTkSuQmCC"
    ),
    24: (
        "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"
    ),
    16: (
        "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAC8UlEQVR42nWT20tUURTGv7Vn65Ga5mKOOXmZKTWPM6SZt8EXxyyT"
        "blR0LDOyi3QxI1+i6MWsP6Cg8MWX6qHIeRAioiClyKwgNYykkkTDbtaojZqZc/buYWoqtfW0N6z17W99Pzbw/2Iz7koer/CEjpLm"
        "nNC0JgMAVLnPb7i0t6Nze8m+xl1FtedsZtuKxpM3r12peTwRHR1tIiIAoFmvVLtsBACJHsVVWrkyq3LboaplTnft9qKajuXZ6Tsy"
        "ShLnrcndlCmlhKZpDAD4XE4ibcHRKfZdLDYmT6vpkzzyLRnEBBeCSyKjPv537z8CXngFAPR1fMq6od9gFouVZ2fkGdQ0VX77Nok7"
        "rbemPz/TkwB0uXwuOTuontBeNn+2xWFKRVw+ZPe7NgwM9dJXY59w23MiHTzPDQJQ6GUzBQguSKRA+TLxni1zpmB18RqWmh8Hszso"
        "i9Z5KGJ8/nd/4EM/gdAT+1mGk/xdEpIgASKKKvMeeFp7otolo6aEkAJiOIr5rjf3XvSdSWPEpJBiNmsCSQJha/Fe+56K/fELfiRI"
        "MWglGrQxM7frVRWHUo/sPLleSIGmX8hZiL9mAIACV+nRBGtyTf5Kjzd9aaZ5YLBPH+mfoq8DOl696JU/pqeQqeauAwBbtUZhCk2u"
        "JkkgbCzZcmzwY3/7+FjgtaIociwwhslPk7CaYzAcCCDXEwslIsI0CyM/ywUALFczxreUlJW3PLo9OuT/QEIKLoSEPh3El8B7dL/s"
        "wv0nLa0AcO/e6T8Z3G0JcgAYeNf3ymq2cId9ifVq82UMj/hhT4oViokHnUsd0u/3I8Wp5gCA231ahh00NJRJIsLj5w8vZKg5ZTEL"
        "Yw2b12p6tDWGuMHAOI9gwWASLCaj3tbZnhXKDSIs4PP59Lq6OlZfX99mnG9am+ZQT3GKLCzMX43uN897RgL+R3Ex8cUpSarzQXvr"
        "UGgGDIA+4zeGaACIsjJ7+UHteDmARQBQkF2UvLv06GEFC1eFqQP4CeXqEUuoPcnYAAAAAElFTkSuQmCC"
    ),
}

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
        # 상위 보고 폴더를 자동 생성하거나 연결 오류를 빈 목록으로 취급하지 않습니다.
        if not self.path.parent.is_dir():
            raise WorkError("인수인계 공유폴더에 연결할 수 없습니다.\n{}".format(self.path.parent))
        if create:
            self.path.mkdir(exist_ok=True)
        try:
            self.path.stat()
        except FileNotFoundError:
            return False
        if not self.path.is_dir():
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
        destination = Path(candidate).resolve()
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


def card_modifier_signature(destination):
    """변경 감지에는 관련 파일의 이름·속성만 읽고 내용은 읽지 않습니다."""
    destination = Path(destination)
    volume_id = card_modifier_volume_id(destination)
    entries = []
    with os.scandir(destination) as scan:
        for entry in scan:
            if (entry.name.casefold() == CARD_MODIFIER_FILENAME.casefold()
                    or is_legacy_card_modifier_name(entry.name)):
                entries.append((entry.name, card_modifier_file_stamp(destination / entry.name)))
    return (volume_id, tuple(sorted(entries)))


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


def year_search_root(year=PROGRAM_YEAR):
    return Path(PROGRAM_BASE_ROOT) / "★ {}".format(parse_program_year(year))


def date_search_folders(text, year=None):
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
    return [year_search_root(year) / "{}월".format(int(name.split(".")[0])) / name
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
    window.configure(background="#111722")
    style.configure(".", font=("맑은 고딕", 10), foreground="#e7edf7")
    style.configure("TFrame", background="#111722")
    style.configure("Card.TFrame", background="#1b2433", borderwidth=1, relief="solid",
                    bordercolor="#36455e", lightcolor="#36455e", darkcolor="#36455e")
    style.configure("TLabel", background="#111722")
    style.configure("Title.TLabel", font=("맑은 고딕", 22, "bold"))
    style.configure("Subtitle.TLabel", foreground="#93a3bc")
    style.configure("Section.TLabel", background="#1b2433", font=("맑은 고딕", 11, "bold"))
    style.configure("Card.TLabel", background="#1b2433")
    style.configure("Caption.TLabel", background="#1b2433", foreground="#93a3bc", font=("맑은 고딕", 9))
    style.configure("Drive.TLabel", background="#1b2433", foreground="#85b4ff", font=("맑은 고딕", 12, "bold"))
    style.configure("AlarmNotice.TLabel", background="#1b2433", foreground="#f5c26b",
                    font=("맑은 고딕", 15, "bold"))
    style.configure("Status.TLabel", background="#203657", foreground="#a7c9ff", padding=(14, 8),
                    font=("맑은 고딕", 10, "bold"))
    style.configure("TSeparator", background="#334157")
    style.configure("TEntry", fieldbackground="#131c2b", bordercolor="#36455e", padding=(12, 10))
    style.map("TEntry", fieldbackground=[("disabled", "#263144")],
              foreground=[("disabled", "#75849c")], bordercolor=[("focus", "#2563eb")])
    style.configure("Accent.TButton", background="#2563eb", foreground="#ffffff", borderwidth=0,
                    padding=(22, 12), font=("맑은 고딕", 11, "bold"))
    style.map("Accent.TButton", background=[("disabled", "#2d4266"), ("active", "#1d4ed8")],
              foreground=[("disabled", "#8092ad")])
    style.configure("Secondary.TButton", background="#2b3b52", foreground="#ffffff",
                    bordercolor="#6b7e9a", lightcolor="#6b7e9a", darkcolor="#6b7e9a",
                    padding=(22, 12), font=("맑은 고딕", 11, "bold"))
    style.map("Secondary.TButton", background=[("disabled", "#263144"), ("active", "#354966")],
              foreground=[("disabled", "#879ab7"), ("!disabled", "#ffffff")])
    style.configure("DriveSmall.TButton", background="#2b3b52", foreground="#ffffff", borderwidth=0,
                    padding=(6, 3), font=("맑은 고딕", 9))
    style.map("DriveSmall.TButton", background=[("disabled", "#263144"), ("active", "#354966")],
              foreground=[("disabled", "#879ab7")])
    style.configure("Danger.TButton", background="#1b2433", foreground="#f593a5", bordercolor="#633b4b",
                    lightcolor="#633b4b", darkcolor="#633b4b", padding=(14, 10), font=("맑은 고딕", 10, "bold"))
    style.map("Danger.TButton", background=[("disabled", "#263144"), ("active", "#392736")],
              foreground=[("disabled", "#718098")])
    style.layout("Mode.TRadiobutton", style.layout("TButton"))
    style.configure("Mode.TRadiobutton", background="#111722", foreground="#a0aec3", borderwidth=0,
                    padding=(14, 11), font=("맑은 고딕", 10, "bold"))
    style.map("Mode.TRadiobutton", background=[("disabled", "#263144"), ("selected", "#2563eb"),
                                               ("active", "#29384e")],
              foreground=[("disabled", "#78879f"), ("selected", "#ffffff")])
    style.configure("Handover.TNotebook", background="#1b2433", borderwidth=0, tabmargins=(0, 0, 0, 12))
    style.configure("Handover.TNotebook.Tab", background="#26364d", foreground="#a0aec3",
                    padding=(14, 9), font=("맑은 고딕", 11, "bold"))
    style.map("Handover.TNotebook.Tab", background=[("selected", "#2563eb")],
              foreground=[("selected", "#ffffff")])
    style.configure("Handover.Treeview", background="#131c2b", fieldbackground="#131c2b",
                    foreground="#e7edf7", borderwidth=0, rowheight=38, font=("맑은 고딕", 10))
    style.map("Handover.Treeview", background=[("selected", "#284a79")],
              foreground=[("selected", "#ffffff")])
    style.configure("HandoverToggle.TButton", background="#203047", foreground="#a7c9ff", borderwidth=0,
                    padding=(14, 9), font=("맑은 고딕", 10, "bold"))
    style.map("HandoverToggle.TButton", background=[("active", "#2b4261")])
    style.configure("HandoverNotice.TButton", background="#352e25", foreground="#f5c26b", borderwidth=0,
                    padding=(14, 9), font=("맑은 고딕", 10, "bold"))
    style.map("HandoverNotice.TButton", background=[("active", "#4b3c27")])
    for scrollbar_style in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
        style.configure(scrollbar_style, background="#40506b", troughcolor="#131c2b", borderwidth=0,
                        bordercolor="#131c2b", lightcolor="#40506b", darkcolor="#40506b", arrowcolor="#a0aec3",
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


STL_FINDER_SOURCE = r'''"""Windows용 STL 파일 찾기 (Python 3.9 이상, 추가 패키지 불필요).

1. 더블클릭해서 실행한다. 알려준 공유폴더가 기본 검색 경로로 입력된다.
   다른 경로를 쓰려면 '폴더 선택'을 누른다.
2. 검색 기간을 고른다. 기본값은 최근 3일이며 달력으로 기간을 지정할 수 있다.
3. 엑셀의 '기공소 / 시스템 / 규격 / 환자명 / #치번' 행을 붙여넣는다.
   '홍길동 #42' 또는 '홍길동'만 입력해도 된다. 치번은 생략 가능하다.
   치번 열이 비어 있거나 '-' 또는 '없음'인 제품도 지원한다. 여러 행도 지원한다.
   '파일 찾기'를 누르면 입력칸이 비워지고, 검색한 원문은 중간의 '입력 주문' 칸에 표시된다.
   입력 주문 칸은 기본 한 줄이며, 검색한 주문의 행 수에 맞춰 높이가 늘어난다.
4. 검색 결과를 더블클릭하거나 Enter를 누르면 연결된 프로그램으로 STL 파일을 연다.
5. 다중 검색에서는 각 주문의 노란색 최상위 후보를 결과 맨 위에 모아서 표시한다.

하위 폴더까지 검색하되 Tempedent 폴더와 그 하위 폴더는 제외한다.
날짜 없는 일반 폴더도 하위를 확인한다. 기간은 날짜 폴더, 파일명 날짜,
파일 수정일 순서로 판단하며 수정일을 사용한 결과에는 그 기준을 표시한다.
파일명과 가까운 환자명 폴더로 후보를 찾으며 파일 내용은
읽거나 변환하지 않는다. 검색 확장자는 .stl로 고정되어 있다.
환자명이 정확히 맞으면 치번이 불일치하거나 확인되지 않아도 표시한다.
같은 환자의 결과에서는 치번이 맞는 파일을 우선하며 나머지는 후보로 표시한다.
기공소 이름의 표현 차이는 정리해서 경로와 비교한다. 비슷한 환자명도
별도 후보로 표시한다. 명확한 시스템/규격 표기는 보조 순위에만 사용하며,
정보가 없거나 달라도 결과에서 제외하지 않는다.
검색 설정은 LOCALAPPDATA/DentalFileFinder에 저장한다.
"""

import csv
import calendar
from datetime import date, datetime, timedelta
import io
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import threading
import time
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
import tkinter as tk
from tkinter import filedialog, font as tkfont, messagebox, ttk


APP_NAME = "STL 파일 찾기"
SEARCH_EXTENSIONS = frozenset({".stl"})
EXCLUDED_FOLDER_NAMES = frozenset({"tempedent"})
DEFAULT_FOLDER = r"\\192.168.0.254\내부공유폴더\★커스텀 오더 2026년"
CONFIG_DIR = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "DentalFileFinder"
CONFIG_FILE = CONFIG_DIR / "settings.json"
TOOTH_MATCH_PRIORITY = {"individual": 0, "filename": 0, "patient_only": 0,
                        "suffix_candidate": 1, "candidate": 2, "unknown": 3, "mismatch": 4}
FDI_TEETH = {str(q * 10 + t) for q in range(1, 5) for t in range(1, 9)} | {str(t) for t in range(0, 11)}
TOOTH_NUMBER = r"(?:[1-4][1-8]|10|[0-9])"
TOOTH_LIST = re.compile(r"#?\d{1,3}(?:[\s,;/]+#?\d{1,3})*")
NO_TOOTH_VALUES = {"", "#", "-", "—", "–", "없음", "(없음)", "치번없음", "n/a", "na"}
LETTERS = r"[^\W\d_]"
MODEL_MARKER = re.compile(r"(?:^|[-_\s])(?:(?:(?:m[-_\s]*center|x)[-_\s]*)?abutment(?:[-_\s]*cad)?|어버트먼트)(?=$|[-_\s])", re.I)
# Narrow family observed in the filename inventory; its last number is
# not proven to be an index. Favor the preceding tooth, keep both visible.
TIMESTAMPED_NAME = re.compile(r"^20\d{6}_\d{4}_")
TOOTH_SUFFIX = re.compile(rf"_#?({TOOTH_NUMBER})_(\d+)$")
SEARCH_PERIODS = ("최근 3일", "오늘", "지정 기간", "전체")
UI_COLORS = {
    "background": "#111722", "card": "#1b2433", "field": "#131c2b",
    "text": "#e7edf7", "muted": "#93a3bc", "border": "#36455e",
    "accent": "#2563eb", "selection": "#284a79", "disabled": "#263144",
}


def configure_app_icon(window):
    """Set the embedded magnifying-glass icon without creating files."""
    image = tk.PhotoImage(master=window, data=(
        "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"
        "ov8PhAz3B8txiPYAAAAASUVORK5CYII="
    ))
    window.iconphoto(True, image)
    window._stl_finder_icon = image


def configure_app_style(window):
    """The same navy panels and blue accents as the 지후니우스 interface."""
    colors = UI_COLORS
    window.configure(background=colors["background"])
    window.option_add("*TCombobox*Listbox.background", colors["field"])
    window.option_add("*TCombobox*Listbox.foreground", colors["text"])
    window.option_add("*TCombobox*Listbox.selectBackground", colors["selection"])
    window.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
    style = ttk.Style(window)
    style.configure("STL", font=("맑은 고딕", 10), foreground=colors["text"],
                    background=colors["background"])
    style.configure("STL.TFrame", background=colors["background"])
    style.configure("STL.Card.TFrame", background=colors["card"], borderwidth=1, relief="solid",
                    bordercolor=colors["border"], lightcolor=colors["border"], darkcolor=colors["border"])
    style.configure("STL.CardBody.TFrame", background=colors["card"])
    style.configure("STL.TLabel", background=colors["background"], foreground=colors["text"])
    style.configure("STL.Title.TLabel", font=("맑은 고딕", 18, "bold"))
    style.configure("STL.Subtitle.TLabel", foreground=colors["muted"], font=("맑은 고딕", 9))
    style.configure("STL.Section.TLabel", background=colors["card"], font=("맑은 고딕", 11, "bold"))
    style.configure("STL.Card.TLabel", background=colors["card"])
    style.configure("STL.Caption.TLabel", background=colors["card"], foreground=colors["muted"],
                    font=("맑은 고딕", 9))
    style.configure("STL.Badge.TLabel", background="#203657", foreground="#a7c9ff",
                    padding=(12, 6), font=("맑은 고딕", 9, "bold"))
    style.configure("STL.Status.TLabel", background="#203657", foreground="#a7c9ff",
                    padding=(10, 6), font=("맑은 고딕", 9))
    style.configure("STL.TEntry", fieldbackground=colors["field"], foreground=colors["text"],
                    insertcolor=colors["text"], bordercolor=colors["border"],
                    lightcolor=colors["border"], darkcolor=colors["border"], padding=(8, 6))
    style.map("STL.TEntry", fieldbackground=[("disabled", colors["disabled"])],
              foreground=[("disabled", "#75849c")], bordercolor=[("focus", colors["accent"])])
    style.configure("STL.TCombobox", fieldbackground=colors["field"], background="#2b3b52",
                    foreground=colors["text"], arrowcolor=colors["text"],
                    bordercolor=colors["border"], lightcolor=colors["border"],
                    darkcolor=colors["border"], padding=(8, 6))
    style.map("STL.TCombobox", fieldbackground=[("disabled", colors["disabled"]), ("readonly", colors["field"])],
              foreground=[("disabled", "#75849c"), ("readonly", colors["text"])],
              selectbackground=[("readonly", colors["field"])],
              selectforeground=[("readonly", colors["text"])],
              bordercolor=[("focus", colors["accent"])])
    style.configure("STL.TCheckbutton", background=colors["card"], foreground=colors["text"],
                    indicatorbackground=colors["field"], indicatorforeground=colors["text"],
                    bordercolor=colors["border"], padding=(0, 2))
    style.map("STL.TCheckbutton", background=[("active", colors["card"])],
              foreground=[("disabled", "#75849c")],
              indicatorbackground=[("disabled", colors["disabled"]), ("selected", colors["accent"])])
    style.configure("STL.Accent.TButton", background=colors["accent"], foreground="#ffffff", borderwidth=0,
                    padding=(14, 6), font=("맑은 고딕", 10, "bold"))
    style.map("STL.Accent.TButton", background=[("disabled", "#2d4266"), ("active", "#1d4ed8")],
              foreground=[("disabled", "#8092ad")])
    style.configure("STL.Secondary.TButton", background="#2b3b52", foreground="#ffffff",
                    bordercolor="#6b7e9a", lightcolor="#6b7e9a", darkcolor="#6b7e9a",
                    padding=(10, 6), font=("맑은 고딕", 10, "bold"))
    style.map("STL.Secondary.TButton", background=[("disabled", colors["disabled"]), ("active", "#354966")],
              foreground=[("disabled", "#879ab7"), ("!disabled", "#ffffff")])
    style.configure("STL.Danger.TButton", background=colors["card"], foreground="#f593a5",
                    bordercolor="#633b4b", lightcolor="#633b4b", darkcolor="#633b4b",
                    padding=(10, 6), font=("맑은 고딕", 10, "bold"))
    style.map("STL.Danger.TButton", background=[("disabled", colors["disabled"]), ("active", "#392736")],
              foreground=[("disabled", "#718098")])
    style.configure("STL.Treeview", font=("맑은 고딕", 9), rowheight=28,
                    background=colors["field"], fieldbackground=colors["field"], foreground=colors["text"],
                    bordercolor=colors["border"], lightcolor=colors["border"], darkcolor=colors["border"])
    style.configure("STL.Treeview.Heading", font=("맑은 고딕", 10, "bold"), background="#2b3b52",
                    foreground=colors["text"], bordercolor=colors["border"],
                    lightcolor=colors["border"], darkcolor=colors["border"], padding=(6, 6))
    style.map("STL.Treeview", background=[("selected", colors["selection"])], foreground=[("selected", "#ffffff")])
    style.map("STL.Treeview.Heading", background=[("active", "#354966")])
    for name in ("STL.Vertical.TScrollbar", "STL.Horizontal.TScrollbar"):
        style.configure(name, background="#40506b", troughcolor=colors["field"], borderwidth=0,
                        bordercolor=colors["field"], lightcolor="#40506b", darkcolor="#40506b",
                        arrowcolor="#a0aec3", arrowsize=12)
        style.map(name, background=[("active", "#536781")])
    return style


def normalized(value):
    return unicodedata.normalize("NFKC", value).casefold()


def compact(value):
    return "".join(normalized(value).split())


def lab_key(value):
    return re.sub(r"[\W_]+", "", normalized(value))


@dataclass(frozen=True)
class Request:
    lab: str
    patient: str
    tooth: str
    line: int
    system: str = ""
    size: str = ""


@dataclass(frozen=True)
class Match:
    request: Request
    path: Path
    reason: str
    strong: bool
    patient_score: int
    lab_score: int
    tooth_status: str = ""
    date_source: str = ""
    file_date: str = ""
    product_score: int = 0
    name_source: str = "filename"


def parse_requests(text):
    """Read copied Excel rows; a missing tooth means a patient-name search."""
    requests, seen, errors = [], set(), []
    for number, raw in enumerate(text.splitlines(), 1):
        # Preserve trailing tabs: an empty fifth column is an omitted tooth,
        # not a reason to shift the patient/system columns to the left.
        raw = unicodedata.normalize("NFKC", raw).strip(" \r\n").lstrip("\ufeff")
        if not raw.strip():
            continue
        try:
            system = size = ""
            if "\t" in raw:
                cells = [cell.strip() for cell in next(csv.reader(io.StringIO(raw), delimiter="\t"))]
                if len(cells) >= 5:
                    if any(cells[5:]):
                        raise ValueError("기공소·시스템·규격·환자명·치번의 5개 열을 붙여넣어 주세요.")
                    lab, system, size, patient, tooth_text = cells[:5]
                elif len(cells) >= 2 and (TOOTH_LIST.fullmatch(cells[-1]) or compact(cells[-1]) in NO_TOOTH_VALUES or cells[-1].startswith("#")):
                    patient, tooth_text = cells[-2], cells[-1]
                    lab = cells[0] if len(cells) >= 3 else ""
                else:
                    patient, tooth_text = cells[-1], ""
                    lab = cells[0] if len(cells) >= 2 else ""
            else:
                tail = re.search(r"(?:^|\s)(#?\d{1,3}(?:[\s,;/]+#?\d{1,3})*)$", raw)
                if tail:
                    prefix, tooth_text = raw[:tail.start()].split(), tail.group(1)
                else:
                    prefix, tooth_text = raw.split(), ""
                    if prefix and compact(prefix[-1]) in NO_TOOTH_VALUES:
                        missing_label = compact(prefix.pop())
                        if missing_label == "없음" and prefix and prefix[-1] == "치번":
                            prefix.pop()
                if not prefix:
                    raise ValueError("환자명을 입력해 주세요.")
                patient = prefix[-1]
                lab = prefix[0] if len(prefix) >= 2 else ""
            if not patient or "#" in patient or compact(patient) in NO_TOOTH_VALUES:
                raise ValueError("환자명 열을 확인해 주세요.")
            missing_tooth = compact(tooth_text) in NO_TOOTH_VALUES
            if not missing_tooth and not TOOTH_LIST.fullmatch(tooth_text):
                raise ValueError("치번은 #42처럼 입력하거나, 없는 제품은 치번 열을 비워 주세요.")
            teeth = [""] if missing_tooth else re.findall(r"\d+", tooth_text)
            invalid = [tooth for tooth in teeth if tooth and tooth not in FDI_TEETH]
            if invalid:
                raise ValueError("지원하는 치번은 0~10, 영구치 11~18, 21~28, 31~38, 41~48입니다: " + ", ".join(invalid))
            for tooth in teeth:
                key = (lab_key(lab), compact(patient), tooth, lab_key(system), lab_key(size))
                if key not in seen:
                    requests.append(Request(lab, patient, tooth, number, system, size))
                    seen.add(key)
        except (ValueError, csv.Error) as exc:
            errors.append(f"{number}행: {exc}")
    if errors:
        raise ValueError("\n".join(errors[:12]) + ("\n그 외 오류 행도 있습니다." if len(errors) > 12 else ""))
    if not requests:
        raise ValueError("검색할 텍스트를 먼저 붙여넣어 주세요.")
    return requests


def patient_pattern(patient):
    # The known Korean-name + A3/A3.5 family has no delimiter before the code.
    # Permit only this bounded family, never arbitrary letters after a name.
    name = compact(patient)
    letters = r"[\s_-]*".join(re.escape(letter) for letter in name)
    code = (r"(?:a\d{1,2}(?:[.,]\d{1,2})?(?=$|[-_\s(),\[\]]))?"
            if re.fullmatch(r"[가-힣]+", name) else "")
    return re.compile(rf"(?<!{LETTERS}){letters}(?:님|씨)?{code}(?!{LETTERS})")

def name_candidates(stem):
    """Return name-like spans; comparisons remain candidates, not identities."""
    candidates = list(re.finditer(r"[가-힣]{2,12}|[a-z]+(?:[ '\-][a-z]+){0,2}", stem))
    return candidates


def comparable_name(value):
    value = compact(value)
    return re.sub(r"(?:님|씨)$", "", value) if len(value) > 2 else value


def lab_identity(value):
    value = normalized(value)
    qualifiers = [lab_key(part) for part in re.findall(r"\(([^)]*)\)", value) if lab_key(part)]
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"^(?:주식회사|유한회사|㈜)\s*", "", value)
    value = re.sub(r"(?:(?:치과\s*)?기공(?:소|실)?|dental\s*lab|덴탈\s*랩)\s*$", "", value.strip(" _-"))
    return lab_key(value), qualifiers


def lab_similarity(lab, parent):
    """Compare each folder; lab names only affect order and annotations."""
    if not lab:
        return 0
    whole_path = lab_key(str(parent))
    if lab_key(lab) in whole_path:
        return 100
    core, qualifiers = lab_identity(lab)
    if not core:
        return 0
    qualifier_found = bool(qualifiers) and all(qualifier in whole_path for qualifier in qualifiers)
    best = 0
    for part in parent.parts:
        folder_core, _ = lab_identity(part)
        if not folder_core:
            continue
        ratio = SequenceMatcher(None, core, folder_core, autojunk=False).ratio()
        score = round(95 * ratio)
        if len(core) >= 2 and core in folder_core:
            score = max(score, 85)
        if qualifiers and not qualifier_found:
            score = min(score, 85)
        elif qualifier_found and core in folder_core:
            score = max(score, 95)
        best = max(best, score)
    return best


def classify_tooth(stem, patient_match, tooth):
    """Prefer the individual tooth before '-abutment'; never use the case list
    to override a conflicting individual tooth. Unknown naming stays a candidate.
    """
    # A whole patient folder provides no filename span. Use the full
    # stem for explicit CAD teeth; generic numbers remain weak.
    tail = stem[patient_match.end():] if patient_match is not None else stem
    markers = list(MODEL_MARKER.finditer(tail))
    if markers:
        before_marker = tail[:markers[-1].start()]
        # The marker's leading delimiter is outside before_marker. Permit the
        # number at its end, but require its own leading '-' or '_'.
        designated = re.search(rf"(?:^|[-_])#?({TOOTH_NUMBER})\s*$", before_marker)
        if designated:
            return ("individual", True) if designated.group(1) == tooth else ("mismatch", False)
    explicit = re.findall(rf"(?:tooth|치아|치번)[-_\s:#]*({TOOTH_NUMBER})(?!\d)", tail, flags=re.I)
    if explicit:
        distinct = set(explicit)
        if tooth not in distinct:
            return ("mismatch", False)
        return ("individual", True) if len(distinct) == 1 else ("candidate", True)
    if TIMESTAMPED_NAME.match(stem):
        suffix = TOOTH_SUFFIX.search(tail)
        if suffix and suffix.group(1) == tooth:
            return ("suffix_candidate", True)
    # Do not count the date/case numbers before the patient's name.
    tokens = re.findall(rf"(?<!\d)({TOOTH_NUMBER})(?!\d)", tail)
    if tooth not in tokens:
        return ("mismatch", False) if tokens else ("unknown", False)
    # A lone (1), revision1 or product code is not a confirmed tooth.
    return ("candidate", True)


def product_profile(text):
    """Only explicit filename words/codes; absent or mixed clues stay unknown."""
    text = normalized(text)
    brands = set()
    for key, pattern in (
        ('osstem', r'(?<![가-힣a-z])(?:오스템|osstem)(?![가-힣a-z])'),
        ('dentium', r'(?<![가-힣a-z])(?:덴티움|dentium)(?![가-힣a-z])'),
        ('neo', r'(?<![가-힣a-z])(?:네오|neo)(?![가-힣a-z])'),
        ('megagen', r'(?<![가-힣a-z])(?:메가젠|megagen)(?![가-힣a-z])'),
    ):
        if re.search(pattern, text):
            brands.add(key)
    sizes = set()
    if re.search(r'(?<![가-힣a-z])(?:레귤러|레귤라|regular)(?![가-힣a-z])', text):
        sizes.add('regular')
    if re.search(r'(?<![가-힣a-z])(?:미니|mini)(?![가-힣a-z])', text):
        sizes.add('mini')
    # Only a code attached to a recognizable product label is a size clue.
    for found in re.finditer(
            r'(?<![가-힣a-z])(?:오스템|덴티움|네오|메가젠|osstem|dentium|neo|megagen|ts)'
            r'[-_\s]*(r|m)(?:\s*[,/]\s*(r|m))?(?![가-힣a-z0-9])', text):
        for value in found.groups():
            if value:
                sizes.add('regular' if value == 'r' else 'mini')
    return frozenset(brands), frozenset(sizes)


def product_similarity(request_profile, file_profile):
    """Soft tie-break only; conflicting/missing metadata never removes a file."""
    score, notes = 0, []
    for requested, actual, label, weight in zip(request_profile, file_profile,
                                               ('시스템', '규격'), (2, 1)):
        # Mixed labels cannot establish which product belongs to this STL.
        if len(requested) == 1 and len(actual) == 1:
            if requested == actual:
                score += weight
                notes.append(label + ' 표기 일치')
            else:
                score -= weight
    return score, ' · '.join(notes)


def match_files(paths, requests, prefer_lab=True, fuzzy_names=True, stop_event=None, date_sources=None):
    from functools import lru_cache

    matches = []
    by_patient = {}
    for request in requests:
        by_patient.setdefault(compact(request.patient), []).append(request)
    patterns = []
    for items in by_patient.values():
        name = items[0].patient
        letters = r'[\s_-]*'.join(re.escape(letter) for letter in compact(name))
        whole_folder = re.compile(rf'{letters}(?:님|씨)?')
        patterns.append((patient_pattern(name), whole_folder, comparable_name(name), items))
    profiles = {request: product_profile(request.system + ' ' + request.size) for request in requests}
    labels = {'individual': '개별 치번 일치', 'filename': '파일명 치번 일치',
              'suffix_candidate': '끝 두 번호 중 앞 번호 일치 · 치번 후보',
              'candidate': '번호 후보 · 확인 필요', 'patient_only': '환자명 일치 · 치번 미지정',
              'mismatch': '치번 불일치 · 환자명 일치', 'unknown': '치번 미확인 · 환자명 일치'}

    # Search-local bounded caches: repeated names/folders don't require repeated
    # normalization or similarity calculations, and nothing survives the search.
    @lru_cache(maxsize=2048)
    def parent_names(parent):
        return (normalized(parent.name).strip(), normalized(parent.parent.name).strip())

    @lru_cache(maxsize=4096)
    def name_ratio(requested, candidate):
        return SequenceMatcher(None, requested, comparable_name(candidate), autojunk=False).ratio()

    @lru_cache(maxsize=2048)
    def folder_score(lab, parent):
        return lab_similarity(lab, parent)

    for index, path in enumerate(paths):
        if index % 128 == 0 and stop_event is not None and stop_event.is_set():
            return []
        if path.suffix.casefold() not in SEARCH_EXTENSIONS:
            continue
        stem = normalized(path.stem)
        possible_names = file_profile = None
        for pattern, whole_folder, requested_name, items in patterns:
            found = pattern.search(stem)
            folder_found = found is None and any(whole_folder.fullmatch(name) for name in parent_names(path.parent))
            exact = found is not None or folder_found
            fuzzy_choices = []
            if not exact and fuzzy_names:
                if possible_names is None:
                    possible_names = name_candidates(stem)
                for candidate in possible_names:
                    ratio = name_ratio(requested_name, candidate.group())
                    if ratio >= 0.66:
                        fuzzy_choices.append((ratio, candidate))
                fuzzy_choices.sort(key=lambda item: item[0], reverse=True)
            if not exact and not fuzzy_choices:
                continue
            for request in items:
                patient_score = 100
                classification = None
                name_source = 'filename' if found is not None else 'folder' if folder_found else 'fuzzy'
                if exact:
                    classification = ('patient_only', True) if not request.tooth else classify_tooth(stem, found, request.tooth)
                else:
                    for ratio, candidate in fuzzy_choices:
                        result = ('patient_only', True) if not request.tooth else classify_tooth(stem, candidate, request.tooth)
                        if result[1]:
                            patient_score = round(ratio * 100)
                            classification = result
                            break
                # Exact filename/folder names remain visible even with a
                # conflicting tooth. Similar names still require tooth support.
                if classification is None:
                    continue
                kind = classification[0]
                if name_source == 'fuzzy':
                    suffix = '치번 미지정' if kind == 'patient_only' else '번호 후보' if kind in {'candidate', 'suffix_candidate'} else '치번 일치'
                    reason = f'환자명 유사 {patient_score}% · {suffix}'
                else:
                    reason = labels[kind]
                    if name_source == 'folder':
                        reason = '환자 폴더명 일치 · ' + reason
                if file_profile is None:
                    file_profile = product_profile(stem)
                product_score, product_note = product_similarity(profiles[request], file_profile)
                if product_note:
                    reason += ' · ' + product_note
                if request.system or request.size:
                    reason += f' · 입력 {request.line}행'
                date_info = date_sources.get(path, {}) if date_sources is not None else {}
                if date_info.get('source') == 'modified_time':
                    reason = '수정일 기준 · ' + reason
                strong = name_source == 'filename' and classification[1] and kind not in {'candidate', 'suffix_candidate'}
                matches.append(Match(request, path, reason, strong, patient_score,
                                     folder_score(request.lab, path.parent), tooth_status=kind,
                                     date_source=date_info.get('source', ''), file_date=date_info.get('date', ''),
                                     product_score=product_score, name_source=name_source))
    matches.sort(key=lambda match: (
        match.request.line, match.request.tooth, match.name_source == 'fuzzy',
        -match.patient_score, TOOTH_MATCH_PRIORITY.get(match.tooth_status, 4),
        -match.lab_score if prefer_lab else 0, -match.product_score,
        match.name_source == 'folder', normalized(str(match.path)),
    ))
    return matches

def folder_date_info(name, year, month=None):
    """Read common date folder labels, without treating arbitrary IDs as dates.
    Supports 2026-10-09, 2026.10.9, 20261009, 10.9, 10월9일,
    and a hierarchy such as 2026년/10월/9일. A trailing note is permitted.
    """
    name = unicodedata.normalize("NFKC", name).strip()
    patterns = [
        (r"^(20\d{2})[.\-_ ]+(\d{1,2})[.\-_ ]+(\d{1,2})(?!\d)", "full"),
        (r"^(20\d{2})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일", "full"),
        (r"^(20\d{2})(\d{2})(\d{2})(?!\d)", "full"),
        (r"^(\d{1,2})\s*월\s*(\d{1,2})\s*일", "short"),
        (r"^(\d{1,2})[.\-_ ]+(\d{1,2})(?!\d)", "short"),
    ]
    for pattern, kind in patterns:
        found = re.match(pattern, name)
        if found:
            numbers = [int(number) for number in found.groups()]
            try:
                return "date", date(*numbers) if kind == "full" else date(year, *numbers)
            except ValueError:
                return "invalid", None
    found = re.fullmatch(r"(20\d{2})(?:\s*년)?", name)
    if found:
        return "year", int(found.group(1))
    found = re.match(r"^(20\d{2})\s*년\s*(\d{1,2})\s*월", name)
    if not found:
        found = re.fullmatch(r"(20\d{2})[.\-_ ]+(\d{1,2})", name)
    if found:
        y, m = map(int, found.groups())
        return ("month", (y, m)) if 1 <= m <= 12 else ("invalid", None)
    found = re.fullmatch(r"(\d{1,2})\s*월", name)
    if found:
        m = int(found.group(1))
        return ("month", (year, m)) if 1 <= m <= 12 else ("invalid", None)
    if month is not None:
        found = re.fullmatch(r"(\d{1,2})\s*일", name)
        if found:
            try:
                return "date", date(year, month, int(found.group(1)))
            except ValueError:
                return "invalid", None
    return "unknown", None


def root_date_context(root, fallback_year):
    year, month, active_date = fallback_year, None, None
    for part in root.parts:
        # The supplied root contains a year in its descriptive title.
        title_year = re.search(r"(?<!\d)(20\d{2})\s*년", part)
        if title_year:
            year = int(title_year.group(1))
        kind, value = folder_date_info(part, year, month)
        if kind == "year":
            year, month = value, None
        elif kind == "month":
            year, month = value
        elif kind == "date":
            year, month, active_date = value.year, value.month, value
    return year, month, active_date


def period_overlaps(kind, value, start, end):
    if kind == "date":
        return start <= value <= end
    if kind == "year":
        return date(value, 1, 1) <= end and date(value, 12, 31) >= start
    if kind == "month":
        y, m = value
        return date(y, m, 1) <= end and date(y, m, calendar.monthrange(y, m)[1]) >= start
    return True


def scan_files(root, extensions, stop_event, progress=None, date_range=None, scope_report=None, date_sources=None):
    paths, errors, folders = [], [], 0
    last_update = 0.0
    if not root.is_dir():
        raise ValueError("검색 폴더가 없거나 연결되지 않았습니다. 폴더 경로를 확인해 주세요.")
    if any(normalized(part).strip() in EXCLUDED_FOLDER_NAMES for part in root.absolute().parts):
        raise ValueError("Tempedent 폴더와 그 하위 폴더는 검색 대상에서 제외됩니다. 다른 검색 폴더를 선택해 주세요.")

    def onerror(error):
        errors.append(f"{error.filename or '알 수 없는 폴더'}: {error.strerror or str(error)}")

    report = scope_report if scope_report is not None else {}
    report.update(skipped_dates=0, unknown_folders=[], selected_dates=0, filename_dates=0,
                  modified_dates=0, undated_folders=0, skipped_file_dates=0)
    contexts = {}
    if date_range:
        start, end = date_range
        initial = root_date_context(root, start.year)
        contexts[root] = initial
        if initial[2] is not None:
            if not start <= initial[2] <= end:
                report["skipped_dates"] += 1
                return paths, errors, folders
            report["selected_dates"] += 1

    for directory, subdirs, files in os.walk(root, topdown=True, onerror=onerror, followlinks=False):
        if stop_event.is_set():
            return [], errors, folders
        folders += 1
        here = Path(directory)
        # Prune before date filtering so excluded trees are never visited,
        # including in '전체' mode and beneath an accepted date folder.
        subdirs[:] = [name for name in subdirs if normalized(name).strip() not in EXCLUDED_FOLDER_NAMES]
        active_date = None
        if date_range:
            year, month, active_date = contexts.pop(here)
            kept = []
            for name in subdirs:
                child = here / name
                if active_date is not None:
                    kept.append(name)
                    contexts[child] = (year, month, active_date)
                    continue
                kind, value = folder_date_info(name, year, month)
                if kind in ("date", "year", "month") and not period_overlaps(kind, value, start, end):
                    report["skipped_dates"] += 1
                    continue
                if kind == "date":
                    contexts[child] = (value.year, value.month, value)
                    report["selected_dates"] += 1
                elif kind == "year":
                    contexts[child] = (value, None, None)
                elif kind == "month":
                    contexts[child] = (*value, None)
                else:
                    # Lab, sample and grouping folders may appear at any depth.
                    # Search through them to reach dated folders or STL files.
                    contexts[child] = (year, month, None)
                    report["undated_folders"] += 1
                kept.append(name)
            subdirs[:] = kept
        for name in files:
            if stop_event.is_set():
                return [], errors, folders
            now = time.monotonic()
            if progress and now - last_update >= 0.4:
                progress(f"검색 중… {folders:,}개 폴더 / {len(paths):,}개 대상 파일")
                last_update = now
            if Path(name).suffix.casefold() not in extensions:
                continue
            path = here / name
            if date_range:
                source, file_date = "folder", active_date
                if active_date is None:
                    kind, value = folder_date_info(path.stem, year, month)
                    if kind == "date":
                        source, file_date = "filename", value
                    else:
                        try:
                            file_date = datetime.fromtimestamp(path.stat().st_mtime).date()
                        except (OSError, ValueError, OverflowError) as exc:
                            errors.append(f"파일 날짜 확인 불가: {path}: {exc}")
                            continue
                        source = "modified_time"
                    if not start <= file_date <= end:
                        report["skipped_file_dates"] += 1
                        continue
                    report["filename_dates" if source == "filename" else "modified_dates"] += 1
                if date_sources is not None:
                    date_sources[path] = {"source": source, "date": file_date.isoformat()}
            paths.append(path)
        now = time.monotonic()
        if progress and now - last_update >= 0.4:
            progress(f"검색 중… {folders:,}개 폴더 / {len(paths):,}개 대상 파일")
            last_update = now
    return paths, errors, folders


def parse_ui_date(value):
    value = value.strip()
    if not re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}", value):
        raise ValueError("날짜는 2026-10-09 형식으로 입력해 주세요.")
    try:
        return date(*map(int, value.split("-")))
    except ValueError:
        raise ValueError("실제 달력에 있는 날짜를 입력해 주세요.") from None


def selected_period(mode, start_text, end_text, today=None):
    today = today or date.today()
    if mode == "전체":
        return None, "전체 날짜"
    if mode == "오늘":
        start = end = today
    elif mode == "최근 3일":
        start, end = today - timedelta(days=2), today
    elif mode == "지정 기간":
        start, end = parse_ui_date(start_text), parse_ui_date(end_text)
    else:
        raise ValueError("검색 기간을 선택해 주세요.")
    if start > end:
        raise ValueError("시작 날짜는 종료 날짜보다 늦을 수 없습니다.")
    return (start, end), f"{start.isoformat()} ~ {end.isoformat()}"


class DatePicker:
    def __init__(self, parent, value, on_select):
        self.on_select = on_select
        try:
            initial = parse_ui_date(value)
        except ValueError:
            initial = date.today()
        self.year, self.month = initial.year, initial.month
        self.window = tk.Toplevel(parent)
        self.window.title("날짜 선택")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.configure(bg=UI_COLORS["background"])
        header = tk.Frame(self.window, bg=UI_COLORS["background"])
        header.pack(fill="x", padx=12, pady=12)
        App.button(header, "◀", lambda: self.move(-1)).pack(side="left")
        self.heading = tk.Label(header, bg=UI_COLORS["background"], fg=UI_COLORS["text"], font=("맑은 고딕", 12, "bold"))
        self.heading.pack(side="left", expand=True, padx=20)
        App.button(header, "▶", lambda: self.move(1)).pack(side="right")
        self.grid = tk.Frame(self.window, bg=UI_COLORS["background"])
        self.grid.pack(padx=12, pady=(0, 12))
        self.draw()
        self.window.grab_set()

    def move(self, delta):
        count = self.year * 12 + self.month - 1 + delta
        year, month = count // 12, count % 12 + 1
        if 1 <= year <= 9999:
            self.year, self.month = year, month
            self.draw()

    def draw(self):
        self.heading.configure(text=f"{self.year}년 {self.month}월")
        for child in self.grid.winfo_children():
            child.destroy()
        for column, name in enumerate(("월", "화", "수", "목", "금", "토", "일")):
            tk.Label(self.grid, text=name, bg=UI_COLORS["background"], fg=UI_COLORS["muted"],
                     font=("맑은 고딕", 10)).grid(row=0, column=column, pady=5)
        for row, week in enumerate(calendar.Calendar(firstweekday=0).monthdayscalendar(self.year, self.month), 1):
            for column, day in enumerate(week):
                if day:
                    value = date(self.year, self.month, day)
                    today = value == date.today()
                    tk.Button(self.grid, text=str(day), width=4, pady=6, relief="flat", font=("맑은 고딕", 10),
                              bg=UI_COLORS["accent"] if today else UI_COLORS["card"], fg=UI_COLORS["text"],
                              activebackground="#354966", activeforeground="#ffffff", cursor="hand2",
                              highlightthickness=0,
                              command=lambda d=value: self.choose(d)).grid(row=row, column=column, padx=2, pady=2)

    def choose(self, value):
        self.on_select(value.isoformat())
        self.window.destroy()


def open_location(path):
    if not path.is_file():
        raise FileNotFoundError("파일이 이동되거나 삭제됐습니다. 다시 검색해 주세요.")
    if sys.platform == "win32":
        subprocess.Popen(["explorer.exe", "/select,", str(path.resolve())])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-R", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path.parent)])


class App:
    def __init__(self, root, parent):
        self.root = root
        self.parent = parent
        self.messages = queue.Queue()
        self.stop_event = threading.Event()
        self.worker = None
        self.rows = {}
        self.access_errors = []
        self.closing = False
        self.style = configure_app_style(root)
        self.folder = tk.StringVar(value=DEFAULT_FOLDER)
        self.prefer_lab = tk.BooleanVar(value=True)
        self.fuzzy_names = tk.BooleanVar(value=True)
        self.period_mode = tk.StringVar(value="최근 3일")
        self.start_date = tk.StringVar(value=(date.today() - timedelta(days=2)).isoformat())
        self.end_date = tk.StringVar(value=date.today().isoformat())
        self.status = tk.StringVar(value="기본 검색 기간은 최근 3일입니다. 이전 작업은 '지정 기간'에서 날짜를 선택해 주세요.")
        self.load_settings()
        self.build_ui()
        self.update_date_controls()
        root.after(100, self.poll)

    @staticmethod
    def button(parent, text, command, primary=False, danger=False):
        style = "STL.Accent.TButton" if primary else ("STL.Danger.TButton" if danger else "STL.Secondary.TButton")
        return ttk.Button(parent, text=text, command=command, cursor="hand2", style=style)

    def build_ui(self):
        body = ttk.Frame(self.parent, padding=0, style="STL.TFrame")
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(5, weight=1)
        settings = ttk.Frame(body, style="STL.Card.TFrame", padding=12)
        settings.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        settings.columnconfigure(0, weight=1)
        settings_heading = ttk.Frame(settings, style="STL.CardBody.TFrame")
        settings_heading.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Label(settings_heading, text="검색 설정", style="STL.Section.TLabel").pack(side="left")
        ttk.Label(settings_heading, text=".stl 파일만 검색  ·  Tempedent 폴더 제외",
                  style="STL.Caption.TLabel").pack(side="right")
        folder_row = ttk.Frame(settings, style="STL.CardBody.TFrame")
        folder_row.grid(row=1, column=0, sticky="ew")
        folder_row.columnconfigure(1, weight=1)
        ttk.Label(folder_row, text="검색 폴더", style="STL.Card.TLabel").grid(row=0, column=0, padx=(0, 12))
        self.folder_entry = ttk.Entry(folder_row, textvariable=self.folder, style="STL.TEntry")
        self.folder_entry.grid(row=0, column=1, sticky="ew")
        self.browse_button = self.button(folder_row, "폴더 선택", self.choose_folder)
        self.browse_button.grid(row=0, column=2, padx=(10, 0))
        options = ttk.Frame(settings, style="STL.CardBody.TFrame")
        options.grid(row=3, column=0, sticky="w", pady=(6, 0))
        self.option_widgets = []
        ttk.Label(options, text="검색 옵션", style="STL.Card.TLabel").pack(side="left", padx=(0, 14))
        for label, variable in [("기공소가 비슷한 경로 우선", self.prefer_lab), ("환자명도 비슷한 이름까지 찾기", self.fuzzy_names)]:
            check = ttk.Checkbutton(options, text=label, variable=variable, style="STL.TCheckbutton")
            check.pack(side="left", padx=(0, 20))
            self.option_widgets.append(check)
        period_row = ttk.Frame(settings, style="STL.CardBody.TFrame")
        period_row.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        ttk.Label(period_row, text="검색 기간", style="STL.Card.TLabel").pack(side="left", padx=(0, 12))
        self.period_combo = ttk.Combobox(period_row, textvariable=self.period_mode, values=SEARCH_PERIODS,
                                         state="readonly", width=11, style="STL.TCombobox")
        self.period_combo.pack(side="left", padx=(0, 16))
        self.period_combo.bind("<<ComboboxSelected>>", lambda _event: self.update_date_controls())
        ttk.Label(period_row, text="시작", style="STL.Card.TLabel").pack(side="left", padx=(0, 5))
        self.start_entry = ttk.Entry(period_row, textvariable=self.start_date, width=12, style="STL.TEntry")
        self.start_entry.pack(side="left")
        self.start_calendar = self.button(period_row, "달력", lambda: self.pick_date(self.start_date))
        self.start_calendar.pack(side="left", padx=(5, 12))
        ttk.Label(period_row, text="종료", style="STL.Card.TLabel").pack(side="left", padx=(0, 5))
        self.end_entry = ttk.Entry(period_row, textvariable=self.end_date, width=12, style="STL.TEntry")
        self.end_entry.pack(side="left")
        self.end_calendar = self.button(period_row, "달력", lambda: self.pick_date(self.end_date))
        self.end_calendar.pack(side="left", padx=5)
        ttk.Label(period_row, text="  시작·종료 날짜 모두 포함", style="STL.Caption.TLabel").pack(side="left")

        inputs = ttk.Frame(body, style="STL.Card.TFrame", padding=12)
        inputs.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        inputs.columnconfigure(0, weight=1)
        label_row = ttk.Frame(inputs, style="STL.CardBody.TFrame")
        label_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(label_row, text="주문 정보 붙여넣기", style="STL.Section.TLabel").pack(side="left")
        ttk.Label(label_row, text="기공소 → 시스템 → 규격 → 환자명 → 치번(생략 가능)",
                  style="STL.Caption.TLabel").pack(side="left", padx=(18, 0))
        text_row = ttk.Frame(inputs, style="STL.CardBody.TFrame")
        text_row.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        text_row.columnconfigure(0, weight=1)
        self.input = tk.Text(text_row, height=2, wrap="none", undo=True,
                             bg=UI_COLORS["field"], fg=UI_COLORS["text"],
                             insertbackground=UI_COLORS["accent"], selectbackground=UI_COLORS["selection"],
                             selectforeground=UI_COLORS["text"], relief="flat", bd=0,
                             highlightthickness=1, highlightbackground=UI_COLORS["border"],
                             highlightcolor=UI_COLORS["accent"], padx=10, pady=8, font=("맑은 고딕", 11))
        self.input.grid(row=0, column=0, sticky="ew")
        text_scroll = ttk.Scrollbar(text_row, command=self.input.yview, style="STL.Vertical.TScrollbar")
        text_scroll.grid(row=0, column=1, sticky="ns")
        text_horizontal = ttk.Scrollbar(text_row, orient="horizontal", command=self.input.xview, style="STL.Horizontal.TScrollbar")
        text_horizontal.grid(row=1, column=0, sticky="ew")
        self.input.configure(yscrollcommand=text_scroll.set, xscrollcommand=text_horizontal.set)
        self.input.bind("<Control-Return>", lambda _event: (self.start_search(), "break")[1])
        action_row = ttk.Frame(inputs, style="STL.CardBody.TFrame")
        action_row.grid(row=3, column=0, sticky="ew")
        self.search_button = self.button(action_row, "파일 찾기  (Ctrl+Enter)", self.start_search, True)
        self.search_button.pack(side="left")
        self.stop_button = self.button(action_row, "중지", self.cancel, danger=True)
        self.stop_button.pack(side="left", padx=8)
        self.stop_button.configure(state="disabled")
        self.paste_button = self.button(action_row, "클립보드 붙여넣기", self.paste)
        self.paste_button.pack(side="left", padx=(8, 0))
        self.clear_button = self.button(action_row, "전체 지우기", self.clear_input, danger=True)
        self.clear_button.pack(side="left", padx=8)
        ttk.Label(action_row, text="더블클릭 / Enter: STL 파일 열기",
                  style="STL.Caption.TLabel").pack(side="right")

        orders = ttk.Frame(body, style="STL.Card.TFrame", padding=(12, 8))
        orders.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        orders.columnconfigure(1, weight=1)
        self.order_label = ttk.Label(orders, text="입력 주문", style="STL.Section.TLabel")
        self.order_label.grid(row=0, column=0, sticky="nw", padx=(0, 12), pady=(4, 0))
        self.order_text = tk.Text(orders, height=1, width=1, wrap="none",
                                  bg=UI_COLORS["field"], fg=UI_COLORS["text"],
                                  selectbackground=UI_COLORS["selection"], selectforeground="#ffffff",
                                  relief="flat", bd=0, highlightthickness=1,
                                  highlightbackground=UI_COLORS["border"], padx=10, pady=4,
                                  font=("맑은 고딕", 9))
        self.order_text.grid(row=0, column=1, sticky="ew")
        order_vertical = ttk.Scrollbar(orders, command=self.order_text.yview, style="STL.Vertical.TScrollbar")
        order_vertical.grid(row=0, column=2, sticky="ns")
        order_horizontal = ttk.Scrollbar(orders, orient="horizontal", command=self.order_text.xview, style="STL.Horizontal.TScrollbar")
        order_horizontal.grid(row=1, column=1, sticky="ew")
        self.order_text.configure(yscrollcommand=order_vertical.set, xscrollcommand=order_horizontal.set)
        self.order_text.insert("1.0", "검색한 주문 정보가 여기에 표시됩니다.")
        self.order_text.configure(state="disabled")

        results = ttk.Frame(body, style="STL.Card.TFrame", padding=12)
        results.grid(row=5, column=0, sticky="nsew")
        results.columnconfigure(0, weight=1)
        results.rowconfigure(1, weight=1)
        results_heading = ttk.Frame(results, style="STL.CardBody.TFrame")
        results_heading.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(results_heading, text="검색 결과", style="STL.Section.TLabel").pack(side="left")
        ttk.Label(results_heading, text="노란색: 항목별 최상위 후보 · 위쪽에 우선 표시",
                  style="STL.Caption.TLabel").pack(side="right")
        result_frame = ttk.Frame(results, style="STL.CardBody.TFrame")
        result_frame.grid(row=1, column=0, sticky="nsew")
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        columns = ("patient", "tooth", "file", "reason", "lab", "path")
        self.result_font = tkfont.Font(root=self.root, family="맑은 고딕", size=9)
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", selectmode="browse", height=6, style="STL.Treeview")
        specs = [("patient", "환자명", 70), ("tooth", "치번", 40), ("file", "파일명", 540),
                 ("reason", "검색 결과", 150), ("lab", "기공소 경로", 90), ("path", "폴더 위치", 180)]
        for key, label, width in specs:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, minwidth=width, stretch=key == "file")
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview, style="STL.Vertical.TScrollbar")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll = ttk.Scrollbar(result_frame, orient="horizontal", command=self.tree.xview, style="STL.Horizontal.TScrollbar")
        xscroll.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.tag_configure("best_match", background="#382f1e", foreground="#f5c26b")
        self.tree.tag_configure("missing", foreground=UI_COLORS["muted"])
        self.tree.bind("<Double-1>", self.double_click)
        self.tree.bind("<Return>", lambda _event: self.open_file())
        footer = ttk.Frame(results, style="STL.CardBody.TFrame")
        footer.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.button(footer, "선택한 파일 위치 열기", self.show_location).pack(side="left")
        self.button(footer, "파일 열기", self.open_file).pack(side="left", padx=8)
        self.button(footer, "전체 경로 복사", self.copy_path).pack(side="left")
        self.button(footer, "제외·접근 불가 폴더", self.show_errors).pack(side="right")
        self.status_label = ttk.Label(body, textvariable=self.status, style="STL.Status.TLabel", wraplength=1050)
        self.status_label.grid(row=6, column=0, sticky="ew", pady=(8, 4))
        self.status_label.bind("<Configure>", lambda event: self.status_label.configure(wraplength=max(200, event.width - 28)))
        ttk.Label(body, text="환자명이 같으면 치번이 달라도 표시합니다. 치번 일치 파일 우선 · 시스템·규격 표기는 후보 순위에 참고합니다.",
                  style="STL.Subtitle.TLabel").grid(row=7, column=0, sticky="w")


    def load_settings(self):
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                folder = data.get("folder", "")
                # Adopt the newly supplied shared root once; afterwards retain
                # a folder that the user explicitly chooses in this version.
                if data.get("default_folder") == DEFAULT_FOLDER and isinstance(folder, str) and folder.strip():
                    self.folder.set(folder)
                for key, variable in [("prefer_lab", self.prefer_lab), ("fuzzy_names", self.fuzzy_names)]:
                    if isinstance(data.get(key), bool):
                        variable.set(data[key])
                if data.get("period_mode") in SEARCH_PERIODS:
                    self.period_mode.set(data["period_mode"])
                if self.period_mode.get() == "지정 기간":
                    for key, variable in [("start_date", self.start_date), ("end_date", self.end_date)]:
                        value = data.get(key)
                        if isinstance(value, str):
                            try:
                                variable.set(parse_ui_date(value).isoformat())
                            except ValueError:
                                pass
        except (OSError, ValueError):
            pass

    def save_settings(self):
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            data = {"folder": self.folder.get().strip(), "default_folder": DEFAULT_FOLDER,
                    "prefer_lab": self.prefer_lab.get(), "fuzzy_names": self.fuzzy_names.get(),
                    "period_mode": self.period_mode.get(),
                    "start_date": self.start_date.get(), "end_date": self.end_date.get()}
            temporary = CONFIG_FILE.with_suffix(".tmp")
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(CONFIG_FILE)
        except OSError:
            pass

    def choose_folder(self):
        current = self.folder.get().strip()
        selected = filedialog.askdirectory(title="STL 파일이 있는 최상위 폴더 선택", initialdir=current or str(Path.home()))
        if selected:
            self.folder.set(selected)
            self.save_settings()

    def paste(self):
        try:
            value = self.root.clipboard_get()
        except tk.TclError:
            messagebox.showinfo(APP_NAME, "클립보드에 텍스트가 없습니다.", parent=self.root)
            return
        self.input.delete("1.0", "end")
        self.input.insert("1.0", value)
        self.input.focus_set()

    def clear_input(self):
        self.input.edit_separator()
        self.input.delete("1.0", "end")
        self.input.edit_separator()
        self.input.focus_set()

    def show_order_snapshot(self, raw_input):
        orders = [line for line in raw_input.splitlines() if line.strip()]
        lines = max(1, len(orders))
        self.order_text.configure(state="normal", height=lines)
        self.order_text.delete("1.0", "end")
        self.order_text.insert("1.0", "\n".join(orders))
        self.order_text.configure(state="disabled")
        self.order_label.configure(text=f"입력 주문 ({len(orders)}행)")

    def update_date_controls(self, busy=False):
        mode = self.period_mode.get()
        if mode in ("오늘", "최근 3일"):
            selected, _label = selected_period(mode, "", "")
            self.start_date.set(selected[0].isoformat())
            self.end_date.set(selected[1].isoformat())
        state = "normal" if mode == "지정 기간" and not busy else "disabled"
        for widget in (self.start_entry, self.end_entry, self.start_calendar, self.end_calendar):
            widget.configure(state=state)
        self.period_combo.configure(state="disabled" if busy else "readonly")

    def pick_date(self, variable):
        DatePicker(self.root, variable.get(), variable.set)

    def busy(self, value):
        state = "disabled" if value else "normal"
        for widget in [self.search_button, self.browse_button, self.paste_button, self.clear_button, self.folder_entry, self.input] + self.option_widgets:
            widget.configure(state=state)
        self.update_date_controls(busy=value)
        self.stop_button.configure(state="normal" if value else "disabled")

    def start_search(self):
        if defer_ime_commit(self.root, self.start_search):return
        if self.worker is not None and self.worker.is_alive():
            return
        raw_input = self.input.get("1.0", "end").rstrip("\n")
        try:
            requests = parse_requests(raw_input)
            folder_text = self.folder.get().strip().strip('"')
            if not folder_text:
                raise ValueError("먼저 검색 폴더를 선택해 주세요.")
            extensions = SEARCH_EXTENSIONS
            date_range, scope_label = selected_period(self.period_mode.get(), self.start_date.get(), self.end_date.get())
        except ValueError as exc:
            messagebox.showerror("입력 확인", str(exc), parent=self.root)
            return
        self.show_order_snapshot(raw_input)
        self.clear_input()
        self.save_settings()
        self.rows.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.access_errors = []
        self.stop_event = threading.Event()
        self.busy(True)
        self.status.set(f"{scope_label}: 검색을 시작합니다…")
        root = Path(folder_text).expanduser()
        prefer_lab, fuzzy_names = self.prefer_lab.get(), self.fuzzy_names.get()
        self.worker = threading.Thread(target=self.search_worker,
                                       args=(root, extensions, requests, prefer_lab, fuzzy_names, date_range, scope_label), daemon=True)
        self.worker.start()

    def search_worker(self, root, extensions, requests, prefer_lab, fuzzy_names, date_range, scope_label):
        try:
            report = {}
            date_sources = {}
            paths, errors, _folders = scan_files(root, extensions, self.stop_event,
                                                 lambda text: self.messages.put(("progress", scope_label + " | " + text)),
                                                 date_range=date_range, scope_report=report, date_sources=date_sources)
            if self.stop_event.is_set():
                self.messages.put(("cancelled", None))
                return
            self.messages.put(("progress", f"{len(paths):,}개 파일의 환자명·치번 비교 중…"))
            matches = match_files(paths, requests, prefer_lab=prefer_lab, fuzzy_names=fuzzy_names,
                                  stop_event=self.stop_event, date_sources=date_sources)
            if self.stop_event.is_set():
                self.messages.put(("cancelled", None))
            else:
                self.messages.put(("result", (requests, matches, len(paths), errors, report, scope_label)))
        except Exception as exc:
            self.messages.put(("error", str(exc)))

    def poll(self):
        if self.closing:
            return
        try:
            while True:
                kind, value = self.messages.get_nowait()
                if kind == "progress":
                    self.status.set(value)
                elif kind == "result":
                    self.worker = None
                    self.busy(False)
                    self.display_results(*value)
                elif kind == "cancelled":
                    self.worker = None
                    self.busy(False)
                    self.status.set("검색을 중지했습니다. 파일은 변경되지 않았습니다.")
                elif kind == "error":
                    self.worker = None
                    self.busy(False)
                    self.status.set("검색 오류: " + value)
                    messagebox.showerror(APP_NAME, value, parent=self.root)
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def display_results(self, requests, matches, total, errors, report, scope_label):
        # Size the filename column from the actual text, leaving room for the
        # complete longest name. Only this column takes extra window space.
        file_width = max(540, max((self.result_font.measure(match.path.name) for match in matches), default=0) + 30)
        self.tree.column("file", width=file_width, minwidth=file_width)
        unknown_folders = report.get("unknown_folders", [])
        self.access_errors = (["날짜 형식 미확인 · 기간 검색에서 제외: " + folder for folder in unknown_folders]
                              + ["접근 불가: " + error for error in errors])
        found = {}
        for match in matches:
            found.setdefault(match.request, []).append(match)
        strong_queries = candidate_queries = missing = 0
        top_result_rows = []
        for request in requests:
            tooth_label = "#" + request.tooth if request.tooth else "없음"
            items = found.get(request, [])
            if not items:
                missing += 1
                reason = "미확인 폴더 있음" if unknown_folders else "기간 내 찾지 못함"
                item = self.tree.insert("", "end", values=(request.patient, tooth_label, "", reason, request.lab or "입력 없음", ""), tags=("missing",))
                continue
            if any(item.strong for item in items):
                strong_queries += 1
            else:
                candidate_queries += 1
            # match_files already sorts each request's results by confidence,
            # patient similarity and the selected lab-preference option.
            for index, match in enumerate(items):
                if not request.lab:
                    lab = "입력 없음"
                elif match.lab_score == 100:
                    lab = "경로에 포함"
                elif match.lab_score >= 60:
                    lab = f"경로 유사 {match.lab_score}%"
                else:
                    lab = "확인 안 됨"
                item = self.tree.insert("", "end", values=(request.patient, tooth_label, match.path.name,
                                                          match.reason, lab, str(match.path.parent)),
                                        tags=("best_match",) if index == 0 else ())
                self.rows[item] = match.path
                if index == 0:
                    top_result_rows.append(item)
        # Show every order's best candidate first, preserving input order.
        for position, item in enumerate(top_result_rows):
            self.tree.move(item, "", position)
        self.status.set(f"{scope_label} | 대상 파일 {total:,}개 / 일치 {strong_queries}건 · 후보만 {candidate_queries}건 · 미발견 {missing}건 / 결과 파일 {len(matches):,}개"
                        + (f" | 기간 밖 폴더 {report['skipped_dates']:,}개 건너뜀" if report.get("skipped_dates") else "")
                        + (f" | 수정일 기준 포함 {report['modified_dates']:,}개" if report.get("modified_dates") else "")
                        + (f" | 날짜 미확인 {len(unknown_folders)}개 제외: '제외·접근 불가 폴더'를 확인해 주세요." if unknown_folders else "")
                        + (f" | 접근 불가 {len(errors)}개: 결과 누락 가능" if errors else ""))
        if unknown_folders and not matches:
            messagebox.showwarning("날짜 폴더 확인 필요",
                                   f"날짜를 인식하지 못한 폴더 {len(unknown_folders)}개를 제외했습니다.\n"
                                   "검색 범위의 일부를 확인하지 못했으므로 파일이 없다고 단정할 수 없습니다.\n\n"
                                   "'제외·접근 불가 폴더'에서 폴더 이름을 확인해 주세요.\n"
                                   "그 폴더를 직접 선택하고 기간을 '전체'로 지정하면 해당 폴더를 검색할 수 있습니다.", parent=self.root)

    def cancel(self):
        self.stop_event.set()
        self.stop_button.configure(state="disabled")
        self.status.set("검색 중지 요청 중…")

    def selected_path(self):
        selection = self.tree.selection()
        path = self.rows.get(selection[0]) if selection else None
        if path is None:
            messagebox.showinfo(APP_NAME, "결과 목록에서 파일을 선택해 주세요.", parent=self.root)
        return path

    def double_click(self, event):
        if self.tree.identify_region(event.x, event.y) not in ("cell", "tree"):
            return
        item = self.tree.identify_row(event.y)
        if item and item in self.rows:
            self.tree.selection_set(item)
            self.open_file()

    def show_location(self):
        path = self.selected_path()
        if path is not None:
            try:
                open_location(path)
            except (OSError, ValueError) as exc:
                messagebox.showerror(APP_NAME, str(exc), parent=self.root)

    def open_file(self):
        path = self.selected_path()
        if path is None:
            return
        try:
            if not path.is_file():
                raise FileNotFoundError("파일이 이동되거나 삭제됐습니다. 다시 검색해 주세요.")
            if sys.platform == "win32":
                os.startfile(str(path))
            else:
                subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(path)])
        except OSError as exc:
            messagebox.showerror(APP_NAME, "연결된 프로그램으로 파일을 열지 못했습니다.\n" + str(exc), parent=self.root)

    def copy_path(self):
        path = self.selected_path()
        if path is not None:
            self.root.clipboard_clear()
            self.root.clipboard_append(str(path))
            self.root.update_idletasks()

    def show_errors(self):
        if not self.access_errors:
            messagebox.showinfo(APP_NAME, "이번 검색에서 날짜 미확인이나 접근 불가 폴더는 없었습니다.", parent=self.root)
            return
        window = tk.Toplevel(self.root)
        window.title("날짜 미확인·접근 불가 폴더")
        window.geometry("880x400")
        window.transient(self.root)
        window.configure(bg=UI_COLORS["background"])
        text = tk.Text(window, wrap="word", bg=UI_COLORS["field"], fg=UI_COLORS["text"],
                       selectbackground=UI_COLORS["selection"], selectforeground=UI_COLORS["text"],
                       relief="flat", bd=0, highlightthickness=1, highlightbackground=UI_COLORS["border"],
                       padx=12, pady=12)
        text.pack(fill="both", expand=True, padx=16, pady=16)
        text.insert("1.0", "아래 폴더는 이번 검색에 포함되지 않았습니다. 날짜 폴더 이름을 확인해 주세요.\n"
                    "날짜 형식: 2026-10-09 / 2026.10.9 / 20261009 / 10.9 / 10월9일\n"
                    "전체 검색을 선택하거나 해당 폴더를 직접 선택해 검색할 수 있습니다.\n\n" + "\n\n".join(self.access_errors))
        text.configure(state="disabled")

    def close(self, destroy=True):
        self.closing = True
        self.stop_event.set()
        self.save_settings()
        if destroy:
            self.root.destroy()

'''

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



WASH_MES_SOURCE = '"""MES 호기 순회 테스트. 사용자가 지정한 숫자 버튼과 조회만 클릭합니다.\n체크박스·저장·완료·값 입력 기능은 없습니다. Windows / Python 3.8+.\n내장 MSAA 판독기는 읽기 전용입니다.\n"""\nimport base64\nimport ctypes\nfrom ctypes import wintypes\nfrom datetime import datetime\nimport json\nimport os\nfrom pathlib import Path\nimport queue\nimport subprocess\nimport tempfile\nimport threading\nimport time\nimport zipfile\nimport xml.etree.ElementTree as ET\n\n# MSAA의 읽기 API만 사용합니다. 공급자 등록 단계 없이 선택 창에서 정보를 읽으며,\n# 각 행을 즉시 기록합니다. 가상화된 행을 표시하거나 스크롤하지 않습니다.\nPOWERSHELL = r\'\'\'\n$ErrorActionPreference = \'Stop\'\n$ProgressPreference = \'SilentlyContinue\'\n$writer = New-Object System.IO.StreamWriter($env:MES_DIAG_OUTPUT, $false, (New-Object System.Text.UTF8Encoding($false)))\n$writer.AutoFlush = $true\nfunction Emit($record) { $writer.WriteLine(($record | ConvertTo-Json -Depth 8 -Compress)) }\ntry {\n    Add-Type -AssemblyName Accessibility\n    $source = @\'\nusing System;\nusing System.Collections.Generic;\nusing System.Diagnostics;\nusing System.Runtime.InteropServices;\nusing System.Text;\nusing Accessibility;\n\npublic sealed class MesReadOnlyAccessibility {\n    [DllImport("oleacc.dll")]\n    static extern int AccessibleObjectFromWindow(IntPtr hwnd, uint objectId, ref Guid iid,\n        [MarshalAs(UnmanagedType.Interface)] out IAccessible result);\n    [DllImport("oleacc.dll")]\n    static extern int AccessibleChildren(IAccessible parent, int start, int count,\n        [Out, MarshalAs(UnmanagedType.LPArray, SizeParamIndex=2, ArraySubType=UnmanagedType.Struct)] object[] children,\n        out int obtained);\n    [DllImport("oleacc.dll")] static extern int WindowFromAccessibleObject(IAccessible acc, out IntPtr hwnd);\n    delegate bool EnumProc(IntPtr hwnd, IntPtr data);\n    [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr parent, EnumProc callback, IntPtr data);\n    [DllImport("user32.dll")] static extern bool IsWindow(IntPtr hwnd);\n    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr hwnd);\n    [DllImport("user32.dll")] static extern IntPtr GetParent(IntPtr hwnd);\n    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);\n    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr hwnd, StringBuilder text, int count);\n\n    readonly Stopwatch clock = Stopwatch.StartNew();\n    readonly HashSet<long> seen = new HashSet<long>();\n    readonly List<object> retained = new List<object>();\n    readonly HashSet<long> nativeHandles = new HashSet<long>();\n    readonly Action<object> emit;\n    int count, windows, propertyErrors, skippedChrome, deferredWindows;\n    bool limited;\n    MesReadOnlyAccessibility(Action<object> output) { emit=output; }\n    bool AtLimit() {\n        if (count>=15000 || clock.Elapsed.TotalSeconds>=35) { limited=true; return true; }\n        return false;\n    }\n    static string Trim(object value, int maxLength=800) {\n        string s=value==null ? "" : Convert.ToString(value);\n        return s.Length>maxLength ? s.Substring(0,maxLength)+" [truncated]" : s;\n    }\n    object Read(Func<object> getter) {\n        try { return getter(); } catch { propertyErrors++; return null; }\n    }\n    static string RoleName(int role) {\n        switch(role) {\n            case 9:return "MSAA.Window"; case 10:return "MSAA.Client";\n            case 24:return "MSAA.Table"; case 25:return "MSAA.ColumnHeader";\n            case 26:return "MSAA.RowHeader"; case 27:return "MSAA.Column";\n            case 28:return "MSAA.Row"; case 29:return "MSAA.Cell";\n            case 33:return "MSAA.List"; case 34:return "MSAA.ListItem";\n            case 41:return "MSAA.StaticText"; case 42:return "MSAA.Text";\n            case 43:return "MSAA.PushButton"; case 44:return "MSAA.CheckBox";\n            case 45:return "MSAA.RadioButton"; case 46:return "MSAA.ComboBox";\n            default:return "MSAA.Role"+role;\n        }\n    }\n    void Walk(IAccessible acc, int child, int parent, int depth, IntPtr hwnd) {\n        if(acc==null || AtLimit())return;\n        if(depth>32) { limited=true; return; }\n        object roleObject=Read(delegate { return acc.get_accRole(child); });\n        int role=0;\n        try {if(roleObject!=null)role=Convert.ToInt32(roleObject);}catch{}\n        // Skip standard title bars, scroll bars and grips; keep application menus.\n        if(role==1 || role==3 || role==4) {skippedChrome++;return;}\n        // Read native child windows from their own handles, avoiding repeated deep trees.\n        if(role==9 && child==0) {\n            IntPtr owner;\n            if(WindowFromAccessibleObject(acc,out owner)>=0 && owner!=hwnd && nativeHandles.Contains(owner.ToInt64())) {\n                deferredWindows++;\n                emit(new Dictionary<string,object>{{"kind","native_reference"},{"parent",parent},{"handle",owner.ToInt64()}});\n                return;\n            }\n        }\n        if(child==0) {\n            IntPtr identity=Marshal.GetIUnknownForObject(acc);\n            bool fresh;\n            try { fresh=seen.Add(identity.ToInt64()); }\n            finally { Marshal.Release(identity); }\n            if(!fresh)return;\n            retained.Add(acc);\n        }\n        int id=count++;\n        object stateObject=Read(delegate { return acc.get_accState(child); });\n        int state=0;\n        bool stateKnown=stateObject!=null;\n        if(stateKnown) {\n            try { state=Convert.ToInt32(stateObject); } catch {stateKnown=false;}\n        }\n        // Missing state is treated conservatively: do not read potentially secret text.\n        bool secret=!stateKnown || (state & 0x20000000)!=0;\n        var row=new Dictionary<string,object>();\n        row["kind"]="element";row["engine"]="MSAA";row["id"]=id;row["parent"]=parent;row["depth"]=depth;\n        row["handle"]=hwnd.ToInt64();row["child_id"]=child;row["role"]=role;row["type"]=RoleName(role);\n        row["state"]=state;row["state_known"]=stateKnown;row["password"]=secret;\n        row["enabled"]=(state & 1)==0;row["offscreen"]=(state & 0x18000)!=0;\n        row["patterns"]=new string[0];row["name"]="";\n        if(!secret) {\n            row["name"]=Trim(Read(delegate {return acc.get_accName(child);}));\n            // Row summaries contain many cells; keep them intact for fast value verification.\n            row["value"]=Trim(Read(delegate {return acc.get_accValue(child);}), role==28 ? 65536 : 800);\n            row["default_action"]=Trim(Read(delegate {return acc.get_accDefaultAction(child);}));\n            if(role==24 || role==25 || role==28 || role==29 || role==37 || (role>=41 && role<=47)) {\n                row["description"]=Trim(Read(delegate {return acc.get_accDescription(child);}));\n                try {\n                    int x,y,w,h;acc.accLocation(out x,out y,out w,out h,child);\n                    row["bounds"]=new int[]{x,y,w,h};\n                } catch {propertyErrors++;}\n            }\n            if(role>=41 && role<=47) {\n                row["help"]=Trim(Read(delegate {return acc.get_accHelp(child);}));\n                row["shortcut"]=Trim(Read(delegate {return acc.get_accKeyboardShortcut(child);}));\n            }\n            if(role==44 || role==45)row["toggle_state"]=(state & 0x10)!=0 ? "Checked" : ((state & 0x20)!=0 ? "Mixed" : "Unchecked");\n            row["selected"]=(state & 2)!=0;\n        }\n        int total=0;\n        if(!secret && child==0) {\n            object value=Read(delegate {return acc.accChildCount;});\n            if(value!=null)try {total=Math.Max(0,Convert.ToInt32(value));}catch{}\n        }\n        row["child_count"]=total;\n        emit(row);\n        if(secret || child!=0 || total==0 || AtLimit())return;\n        if(depth>=32) {limited=true;return;}\n        for(int start=0;start<total;start+=32) {\n            if(AtLimit())return;\n            int size=Math.Min(32,total-start);\n            object[] children=new object[size];int obtained=0;int hr;\n            try {hr=AccessibleChildren(acc,start,size,children,out obtained);}\n            catch(Exception error) {emit(new Dictionary<string,object>{{"kind","element_error"},{"id",id},{"error",Trim(error.Message)}});return;}\n            if(hr<0) {emit(new Dictionary<string,object>{{"kind","element_error"},{"id",id},{"hresult",hr}});return;}\n            if(obtained<=0)return;\n            for(int index=0;index<Math.Min(obtained,size);index++) {\n                if(AtLimit())return;\n                object item=children[index];\n                IAccessible objectChild=item as IAccessible;\n                if(objectChild!=null) {Walk(objectChild,0,id,depth+1,hwnd);continue;}\n                if(item is int) {\n                    int childId=(int)item;\n                    if(childId<=0)continue;\n                    IAccessible expanded=Read(delegate {return acc.get_accChild(childId);}) as IAccessible;\n                    if(expanded!=null)Walk(expanded,0,id,depth+1,hwnd);\n                    else Walk(acc,childId,id,depth+1,hwnd);\n                }\n            }\n        }\n    }\n    void Window(IntPtr hwnd, uint expectedPid) {\n        uint pid;GetWindowThreadProcessId(hwnd,out pid);\n        if(pid!=expectedPid || AtLimit())return;\n        windows++;\n        StringBuilder klass=new StringBuilder(256);GetClassName(hwnd,klass,klass.Capacity);\n        Guid iid=new Guid("618736E0-3C3D-11CF-810C-00AA00389B71");\n        IAccessible acc=null;\n        int hr=AccessibleObjectFromWindow(hwnd,0xFFFFFFFC,ref iid,out acc);\n        emit(new Dictionary<string,object>{{"kind","native_window"},{"handle",hwnd.ToInt64()},\n            {"native_parent",GetParent(hwnd).ToInt64()},{"class",klass.ToString()},{"hresult",hr},{"accessible",acc!=null}});\n        if(hr>=0 && acc!=null)Walk(acc,0,-1,0,hwnd);\n    }\n    public static void Dump(long handle, int expectedPid, Action<object> output) {\n        var reader=new MesReadOnlyAccessibility(output);\n        IntPtr hwnd=new IntPtr(handle);uint pid;\n        GetWindowThreadProcessId(hwnd,out pid);\n        if(!IsWindow(hwnd) || pid!=(uint)expectedPid)throw new InvalidOperationException("Selected window changed. Refresh the window list.");\n        var handles=new List<IntPtr>();handles.Add(hwnd);\n        EnumProc callback=delegate(IntPtr child,IntPtr data) {\n            if(handles.Count>=512) {reader.limited=true;return false;}\n            uint owner;GetWindowThreadProcessId(child,out owner);\n            if(owner==pid && IsWindowVisible(child))handles.Add(child);\n            return true;\n        };\n        EnumChildWindows(hwnd,callback,IntPtr.Zero);\n        foreach(IntPtr target in handles)reader.nativeHandles.Add(target.ToInt64());\n        output(new Dictionary<string,object>{{"kind","start"},{"engine","MSAA"},{"read_only",true},{"pid",pid}});\n        foreach(IntPtr target in handles) {\n            if(reader.AtLimit())break;\n            try {reader.Window(target,pid);}\n            catch(Exception error) {output(new Dictionary<string,object>{{"kind","window_error"},{"handle",target.ToInt64()},{"error",Trim(error.Message)}});}\n        }\n        output(new Dictionary<string,object>{{"kind","finish"},{"engine","MSAA"},{"elements",reader.count},\n            {"windows_read",reader.windows},{"windows_found",handles.Count},{"property_errors",reader.propertyErrors},\n            {"skipped_chrome",reader.skippedChrome},{"deferred_windows",reader.deferredWindows},\n            {"limited",reader.limited},{"seconds",reader.clock.Elapsed.TotalSeconds}});\n        GC.KeepAlive(callback);GC.KeepAlive(reader.retained);\n    }\n}\n\n\'@\n    Add-Type -TypeDefinition $source -Language CSharp -ReferencedAssemblies @([Accessibility.IAccessible].Assembly.Location, \'System.dll\', \'System.Core.dll\')\n    $output = [Action[object]] { param($record) Emit $record }\n    [MesReadOnlyAccessibility]::Dump([long]$env:MES_DIAG_HANDLE, [int]$env:MES_DIAG_PID, $output)\n} catch { Emit @{kind=\'fatal\'; error=$_.Exception.ToString()} }\nfinally { $writer.Dispose() }\n\'\'\'\n\n\ndef visible_windows():\n    if os.name != \'nt\':\n        return []\n    user = ctypes.WinDLL(\'user32\', use_last_error=True)\n    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)\n    user.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]\n    user.EnumWindows.restype = wintypes.BOOL\n    user.IsWindowVisible.argtypes = [wintypes.HWND]\n    user.IsWindowVisible.restype = wintypes.BOOL\n    user.GetWindowTextLengthW.argtypes = [wintypes.HWND]\n    user.GetWindowTextLengthW.restype = ctypes.c_int\n    user.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]\n    user.GetWindowTextW.restype = ctypes.c_int\n    user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]\n    user.GetWindowThreadProcessId.restype = wintypes.DWORD\n    user.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]\n    user.GetClassNameW.restype = ctypes.c_int\n    result = []\n    @callback_type\n    def visit(handle, _):\n        if not user.IsWindowVisible(handle):\n            return True\n        pid = wintypes.DWORD()\n        user.GetWindowThreadProcessId(handle, ctypes.byref(pid))\n        if pid.value == os.getpid():\n            return True\n        length = min(user.GetWindowTextLengthW(handle), 4096)\n        if not length:\n            return True\n        title = ctypes.create_unicode_buffer(length + 1)\n        user.GetWindowTextW(handle, title, len(title))\n        klass = ctypes.create_unicode_buffer(256)\n        user.GetClassNameW(handle, klass, len(klass))\n        result.append({\'handle\':int(handle), \'pid\':pid.value, \'title\':title.value, \'class\':klass.value})\n        return True\n    if not user.EnumWindows(visit, 0):\n        raise ctypes.WinError(ctypes.get_last_error())\n    return sorted(result, key=lambda w: w[\'title\'].casefold())\n\n\ndef powershell_errors(raw):\n    """PowerShell 진행 안내(CLIXML)를 오류로 잘못 분류하지 않습니다."""\n    if raw.startswith((b\'\\xff\\xfe\', b\'\\xfe\\xff\')):\n        text = raw.decode(\'utf-16\', errors=\'replace\')\n    else:\n        text = raw.decode(\'utf-8-sig\', errors=\'replace\')\n    if text.lstrip().startswith(\'#< CLIXML\'):\n        try:\n            xml = ET.fromstring(text[text.index(\'<Objs\'):])\n            errors = [node.text or \'\' for node in xml.iter()\n                      if node.attrib.get(\'S\', \'\').lower() == \'error\']\n            return \'\\n\'.join(errors)\n        except (ValueError, ET.ParseError):\n            pass\n    return text.strip()\n\n\ndef probe_command(powershell, directory, env):\n    """Keep the embedded reader in a private temporary file, below Windows\' command limit."""\n    opening = "    $source = @\'\\n"\n    start = POWERSHELL.index(opening)\n    end = POWERSHELL.index("\\n\'@", start)\n    source = Path(directory)/\'reader.cs\'\n    source.write_text(POWERSHELL[start+len(opening):end], encoding=\'utf-8-sig\')\n    env[\'MES_DIAG_SOURCE\'] = str(source)\n    script = (POWERSHELL[:start] +\n              \'    $source = [System.IO.File]::ReadAllText($env:MES_DIAG_SOURCE)\' +\n              POWERSHELL[end+3:])\n    return [str(powershell), \'-NoLogo\', \'-NoProfile\', \'-NonInteractive\', \'-STA\',\n            \'-EncodedCommand\', base64.b64encode(script.encode(\'utf-16le\')).decode(\'ascii\')]\n\n\ndef inspect_window(target, label, stop):\n    """Runs an isolated read-only probe; cancels only the probe, never the MES app."""\n    report = {\'tool\':\'MES_POP_화면확인\', \'version\':4, \'captured_at\':datetime.now().isoformat(timespec=\'seconds\'),\n              \'label\':label, \'target\':dict(target), \'read_only\':True,\n              \'scope\':\'선택 창의 노출된 UI 정보. 스크롤·체크·입력·저장·서버 통신 없음.\', \'records\':[]}\n    windir = Path(os.environ.get(\'SystemRoot\', r\'C:\\Windows\'))\n    powershell = windir/\'System32\'/\'WindowsPowerShell\'/\'v1.0\'/\'powershell.exe\'\n    if not powershell.is_file():\n        raise RuntimeError(\'Windows PowerShell을 찾지 못했습니다. Windows PC에서 실행해 주세요.\')\n    with tempfile.TemporaryDirectory(prefix=\'mes_pop_read_\') as tmp:\n        output = Path(tmp)/\'readout.jsonl\'\n        stderr = Path(tmp)/\'errors.txt\'\n        env = os.environ.copy()\n        env.update(MES_DIAG_HANDLE=str(int(target[\'handle\'])), MES_DIAG_PID=str(int(target[\'pid\'])), MES_DIAG_OUTPUT=str(output))\n        command = probe_command(powershell, tmp, env)\n        with stderr.open(\'wb\') as errors:\n            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,\n                                       stderr=errors, env=env, creationflags=getattr(subprocess,\'CREATE_NO_WINDOW\',0))\n            deadline = time.monotonic()+45\n            try:\n                while process.poll() is None:\n                    if stop.wait(.1) or time.monotonic() >= deadline:\n                        report[\'interrupted\'] = \'사용자 중지\' if stop.is_set() else \'45초 제한 시간\'\n                        process.kill()\n                        break\n                process.wait(timeout=5)\n            finally:\n                if process.poll() is None:\n                    process.kill()\n                    process.wait(timeout=5)\n        report[\'exit_code\'] = process.returncode\n        if output.exists():\n            for line in output.read_text(encoding=\'utf-8-sig\',errors=\'replace\').splitlines():\n                try:\n                    record = json.loads(line)\n                    if isinstance(record,dict): report[\'records\'].append(record)\n                except ValueError:\n                    report[\'partial_line\'] = True\n        error_bytes = stderr.read_bytes()[:6000]\n        error_text = powershell_errors(error_bytes)\n        if error_text:\n            report[\'powershell_error\'] = error_text\n    return report\n\n\ndef report_summary(report):\n    records = report[\'records\']\n    elements = [r for r in records if r.get(\'kind\')==\'element\']\n    grids = [r for r in elements if \'grid_rows\' in r or r.get(\'type\') == \'MSAA.Table\']\n    values = [r for r in elements if any(r.get(k) for k in (\'value\',\'text\',\'legacy_value\'))]\n    fatal = [r.get(\'error\',\'\') for r in records if r.get(\'kind\')==\'fatal\']\n    finished = any(r.get(\'kind\')==\'finish\' for r in records)\n    partial = bool(report.get(\'interrupted\') or report.get(\'partial_line\') or not finished\n                   or any(r.get(\'limited\') for r in records))\n    lines = [f"[{report[\'label\']}] {report[\'target\'][\'title\']}",\n             f"읽은 항목 {len(elements)}개 / 표 정보 {len(grids)}개 / 값·텍스트 {len(values)}개",\n             \'일부 결과: 중지·제한 시간·읽기 제한이 있어 전체 화면을 확인하지 못했습니다.\' if partial else \'화면 정보 읽기가 끝났습니다.\',\n             \'이 결과만으로 자동 완료 가능 여부를 확정하지 않습니다.\']\n    if fatal: lines.extend(\'읽기 오류: \'+s for s in fatal)\n    providers = [r for r in records if r.get(\'kind\') == \'provider\']\n    if any(r.get(\'engine\') == \'MSAA\' for r in records):\n        lines.append(\'검사 방식: MSAA 직접 읽기 (버튼 실행·선택 변경 없음)\')\n        finishes = [r for r in records if r.get(\'kind\') == \'finish\']\n        if finishes and \'windows_found\' in finishes[-1]:\n            end = finishes[-1]\n            lines.append(f"창 검사 {end.get(\'windows_read\', 0)}/{end[\'windows_found\']}개 / 테두리·스크롤 요소 {end.get(\'skipped_chrome\', 0)}개 생략")\n        locations = sum(bool(r.get(\'bounds\') and r[\'bounds\'][2]>0 and r[\'bounds\'][3]>0) for r in elements)\n        lines.append(f\'위치가 읽힌 항목 {locations}개. 표의 열 순서는 화면 순서와 다를 수 있어 별도 대조합니다.\')\n    if providers:\n        lines.append(\'컨트롤 읽기 연결: \' + (\'등록됨\' if providers[-1].get(\'registered\') else \'등록 실패 — 결과 파일에서 원인 확인\'))\n    named_only = elements and not any(r.get(\'patterns\') or r.get(\'value\') or r.get(\'type\') in (\'MSAA.Cell\',\'MSAA.Row\',\'MSAA.CheckBox\') for r in elements if r.get(\'type\') != \'ControlType.Window\')\n    if named_only:\n        lines.append(\'현재는 창 이름·표시 글자만 읽혔습니다. 표 데이터와 체크박스 조작 정보는 확인되지 않았습니다.\')\n    if report.get(\'powershell_error\'): lines.append(\'PowerShell 오류가 있습니다. 결과 파일에 포함됩니다.\')\n    if not elements: lines.append(\'대상 창이 열려 있는지 확인하세요. 접근 권한 또는 화면 구조 때문에 읽지 못했을 수 있습니다.\')\n    return \'\\n\'.join(lines)\n\n\ndef save_reports(path, reports):\n    if not reports: raise ValueError(\'먼저 창을 검사해 주세요.\')\n    path = Path(path)\n    text = [\'MES 호기 순회 테스트의 화면 판독 결과\', \'호기 선택·조회 중 수집한 화면 정보 — 저장·완료 실행 없음\', \'\',\n            \'선택한 창의 표시 문자열이 포함됩니다. 비밀번호 필드는 수집하지 않습니다.\',\n            \'스크롤 밖의 가상화된 행은 누락될 수 있습니다. 목록 전체 수집 가능 여부는 별도 확인이 필요합니다.\', \'\']\n    for index, report in enumerate(reports,1):\n        text.extend([f\'--- 검사 {index} ---\',report_summary(report),\'\'])\n        for record in report[\'records\']:\n            if record.get(\'kind\')==\'element\':\n                fields = [\'  \'*min(record.get(\'depth\',0),18)+str(record.get(\'type\',\'\')),\n                          \'name=\'+str(record.get(\'name\',\'\')), \'id=\'+str(record.get(\'automation_id\',\'\')),\n                          \'class=\'+str(record.get(\'class\',\'\')), \'patterns=\'+\', \'.join(record.get(\'patterns\',[]))]\n                for key in (\'value\',\'text\',\'legacy_value\',\'grid_rows\',\'grid_columns\',\'row\',\'column\',\'toggle_state\',\'selected\',\'role\',\'state\',\'child_count\',\'default_action\',\'bounds\',\'description\',\'help\',\'shortcut\'):\n                    if key in record: fields.append(key+\'=\'+str(record[key]))\n                text.append(\' | \'.join(fields))\n        text.append(\'\')\n    # Save to a sibling temporary file, then atomically replace the chosen output.\n    temporary = None\n    try:\n        with tempfile.NamedTemporaryFile(prefix=\'mes_report_\',suffix=\'.zip\',dir=str(path.parent),delete=False) as f:\n            temporary = Path(f.name)\n        with zipfile.ZipFile(temporary,\'w\',zipfile.ZIP_DEFLATED) as archive:\n            archive.writestr(\'MES_POP_report.json\',json.dumps({\'schema\':1,\'captures\':reports},ensure_ascii=False,indent=2).encode(\'utf-8\'))\n            archive.writestr(\'MES_POP_report.txt\',\'\\n\'.join(text).encode(\'utf-8-sig\'))\n        os.replace(temporary,path)\n    finally:\n        if temporary is not None and temporary.exists(): temporary.unlink()\n\n\nfrom collections import defaultdict\nimport re\n\n\ndef nodes(report):\n    return [r for r in report[\'records\'] if r.get(\'kind\') == \'element\']\n\n\ndef check_capture(report):\n    finishes = [r for r in report[\'records\'] if r.get(\'kind\') == \'finish\']\n    if (report.get(\'interrupted\') or report.get(\'powershell_error\') or report.get(\'partial_line\')\n            or report.get(\'exit_code\') != 0 or not finishes or finishes[-1].get(\'limited\')\n            or any(r.get(\'kind\') in (\'fatal\',\'window_error\',\'element_error\') for r in report[\'records\'])):\n        raise RuntimeError(\'화면을 충분히 읽지 못해 순회를 중단했습니다. 결과를 저장해 주세요.\')\n\n\ndef number_groups(report):\n    native = {r[\'handle\']: r for r in report[\'records\'] if r.get(\'kind\') == \'native_window\'}\n    groups = defaultdict(dict)\n    for r in nodes(report):\n        if r.get(\'parent\') != -1 or r.get(\'role\') != 41 or r.get(\'name\') not in {str(i) for i in range(1,11)}:\n            continue\n        if r.get(\'offscreen\') or not r.get(\'enabled\'):\n            continue\n        n = native.get(r[\'handle\'], {})\n        parent = n.get(\'native_parent\')\n        if parent:\n            group = groups[parent]\n            if r[\'name\'] in group:\n                group[r[\'name\']] = None\n            else:\n                group[r[\'name\']] = r\n    result = []\n    for parent, group in groups.items():\n        if len(group) != 10 or any(v is None for v in group.values()):\n            continue\n        first = group[\'1\']; bounds = first.get(\'bounds\', [])\n        panel = native.get(parent, {}).get(\'native_parent\')\n        if len(bounds) != 4 or bounds[2] <= 0 or bounds[3] <= 0 or not panel:\n            continue\n        result.append({\'parent\': parent, \'panel\': panel,\n                       \'buttons\': {i: group[str(i)][\'handle\'] for i in range(1,11)},\n                       \'x\': bounds[0], \'y\': bounds[1]})\n    result.sort(key=lambda g: (g[\'y\'], g[\'x\']))\n    for i, group in enumerate(result, 1):\n        group[\'label\'] = f"묶음 {i} — 1번 위치: 가로 {group[\'x\']}, 세로 {group[\'y\']}"\n    if len(result)==6 and abs(result[0][\'y\']-result[2][\'y\'])<10 and abs(result[3][\'y\']-result[5][\'y\'])<10 and result[3][\'y\']-result[0][\'y\']>30:\n        for group,label in zip(result,(\'위쪽 왼쪽\',\'위쪽 가운데\',\'위쪽 오른쪽\',\'아래쪽 왼쪽\',\'아래쪽 가운데\',\'아래쪽 오른쪽\')):\n            group[\'label\']=label+\'의 1~10 버튼\'\n    return result\n\n\ndef panel_data(report):\n    """MES only: require a matching header schema and corroborate visible cell names."""\n    check_capture(report)\n    elements = nodes(report); children = defaultdict(list)\n    for r in elements:\n        children[r[\'parent\']].append(r)\n    tables = []\n    for table in elements:\n        if table.get(\'role\') != 24:\n            continue\n        headers = [h for group in children[table[\'id\']] for h in children[group[\'id\']] if h.get(\'role\') == 25]\n        names = [h.get(\'name\',\'\') for h in headers]\n        if \'P/No.\' not in names or \'세척\' not in names:\n            continue\n        if len(set(names)) != len(names):\n            raise RuntimeError(\'중복된 열 이름 때문에 표를 구분할 수 없습니다.\')\n        rows = []\n        for container in children[table[\'id\']]:\n            data_rows = [r for r in children[container[\'id\']] if r.get(\'role\') == 28]\n            if (data_rows or container.get(\'name\')==\'데이터 패널\') and len(data_rows) != container.get(\'child_count\'):\n                raise RuntimeError(\'일부 행이 누락되어 중단했습니다.\')\n            for row in data_rows:\n                cells = [r for r in children[row[\'id\']] if r.get(\'role\') == 29]\n                if len(cells) != len(headers) or len(cells) != row.get(\'child_count\'):\n                    raise RuntimeError(\'표의 열 개수가 맞지 않아 중단했습니다.\')\n                for header, cell in zip(headers, cells):\n                    name = cell.get(\'name\',\'\')\n                    if name and name.split(\' row\')[0] != header[\'name\']:\n                        raise RuntimeError(\'표의 열 순서가 달라 중단했습니다.\')\n                rows.append({name: cell.get(\'value\',\'\') for name,cell in zip(names,cells)})\n        tables.append({\'rows\':rows, \'columns\':names})\n    if len(tables) != 1:\n        raise RuntimeError(f\'선택한 묶음에서 생산일보 표가 {len(tables)}개 발견되어 중단했습니다.\')\n    equipment = sorted({r.get(\'value\',\'\') for r in elements\n                        if r.get(\'role\') == 42 and re.fullmatch(r\'M\\d{4}\',r.get(\'value\',\'\'))})\n    equipment_names = sorted({r.get(\'value\',\'\') for r in elements\n                              if r.get(\'role\') == 42 and \'호기\' in r.get(\'value\',\'\')})\n    dates = sorted({r.get(\'value\',\'\') for r in elements if r.get(\'role\') == 47 and \'년\' in r.get(\'value\',\'\')})\n    return {\'equipment\':equipment, \'equipment_names\':equipment_names, \'dates\':dates,\n            \'rows\':tables[0][\'rows\']}\n\n\nclass Stopped(Exception):\n    pass\n\n\ndef table_view(report):\n    data=panel_data(report)\n    children=defaultdict(list)\n    for row in nodes(report):children[row[\'parent\']].append(row)\n    targets=[]\n    for table in nodes(report):\n        if table.get(\'role\')!=24:continue\n        headers=[h for group in children[table[\'id\']] for h in children[group[\'id\']] if h.get(\'role\')==25]\n        names=[h.get(\'name\',\'\') for h in headers]\n        if \'P/No.\' not in names or \'세척\' not in names:continue\n        rows=[r for group in children[table[\'id\']] for r in children[group[\'id\']] if r.get(\'role\')==28]\n        targets.append((table,headers,rows))\n    if len(targets)!=1:raise RuntimeError(\'스크롤할 표를 하나로 구분하지 못했습니다.\')\n    table,headers,rows=targets[0]\n    bounds=table.get(\'bounds\',[0,0,0,0])\n    if bounds[2]<=0 or bounds[3]<=0:raise RuntimeError(\'표가 최소화되었거나 화면 위치를 읽지 못했습니다.\')\n    # Track actual row positions, independently of the displayed No. values.\n    keys=[str(i) for i in range(1,len(rows)+1)]\n    if len(rows)!=len(data[\'rows\']):raise RuntimeError(\'표의 실제 행 개수가 일치하지 않습니다.\')\n    visible=[]\n    header_bottom=max((h.get(\'bounds\',[0,0,0,0])[1]+h.get(\'bounds\',[0,0,0,0])[3] for h in headers),default=bounds[1])\n    for key,row in zip(keys,rows):\n        b=row.get(\'bounds\',[0,0,0,0])\n        # Count only fully shown rows, never a clipped last line.\n        if (not row.get(\'offscreen\') and b[2]>0 and b[3]>0 and b[1]>=header_bottom\n                and b[1]+b[3]<=bounds[1]+bounds[3]):visible.append(key)\n    summaries=[r.get(\'value\') for r in rows]\n    summary_supported=all(isinstance(value,str) and \'[truncated]\' not in value\n                          and value==\';\'.join(record[h.get(\'name\',\'\')] for h in headers)+\';\'\n                          for value,record in zip(summaries,data[\'rows\']))\n    return {\'row_summaries\':summaries,\'summary_supported\':summary_supported,\'data\':data,\'handle\':table[\'handle\'],\'keys\':keys,\'visible\':visible,\'row_names\':[r.get(\'name\',\'\') for r in rows],\'header_names\':[h.get(\'name\',\'\') for h in headers]}\n\n\ndef row_geometry(report, expected_view):\n    check_capture(report)\n    children=defaultdict(list)\n    for n in nodes(report):children[n[\'parent\']].append(n)\n    tables=[]\n    for table in nodes(report):\n        if table.get(\'role\')!=24:continue\n        headers=[h for g in children[table[\'id\']] for h in children[g[\'id\']] if h.get(\'role\')==25]\n        if [h.get(\'name\',\'\') for h in headers]!=expected_view[\'header_names\']:continue\n        rows=[r for g in children[table[\'id\']] for r in children[g[\'id\']] if r.get(\'role\')==28]\n        tables.append((table,headers,rows))\n    if len(tables)!=1:raise RuntimeError(\'스크롤 중 표 구조를 확인하지 못했습니다.\')\n    table,headers,rows=tables[0];b=table.get(\'bounds\',[0,0,0,0])\n    if table[\'handle\']!=expected_view[\'handle\'] or len(rows)!=len(expected_view[\'keys\']) or b[2]<=0 or b[3]<=0:\n        raise RuntimeError(\'스크롤 중 표 또는 행 개수가 바뀌었습니다.\')\n    for container in children[table[\'id\']]:\n        if container.get(\'name\')==\'데이터 패널\' and len([r for r in children[container[\'id\']] if r.get(\'role\')==28])!=container.get(\'child_count\'):\n            raise RuntimeError(\'MES 전체 행 수를 확인하지 못했습니다.\')\n    if expected_view.get(\'summary_supported\') and [r.get(\'value\') for r in rows]!=expected_view[\'row_summaries\']:\n        raise RuntimeError(\'MES 전체 행 재확인 중 값이 바뀌었습니다.\')\n    for field,role in ((\'dates\',47),(\'equipment_names\',42)):\n        values=sorted({n.get(\'value\',\'\') for n in nodes(report) if n.get(\'role\')==role and (\'년\' if role==47 else \'호기\') in n.get(\'value\',\'\')})\n        if values!=expected_view[\'data\'][field]:raise RuntimeError(\'MES 재확인 중 생산일 또는 설비 정보가 바뀌었습니다.\')\n    names=[r.get(\'name\',\'\') for r in rows]\n    if names!=expected_view[\'row_names\']:raise RuntimeError(\'스크롤 중 실제 행 구조가 바뀌었습니다.\')\n    header_bottom=max((h.get(\'bounds\',[0,0,0,0])[1]+h.get(\'bounds\',[0,0,0,0])[3] for h in headers),default=b[1])\n    visible=[]\n    for key,row in zip(expected_view[\'keys\'],rows):\n        rb=row.get(\'bounds\',[0,0,0,0])\n        if not row.get(\'offscreen\') and rb[2]>0 and rb[3]>0 and rb[1]>=header_bottom and rb[1]+rb[3]<=b[1]+b[3]:visible.append(key)\n    return {**expected_view,\'visible\':visible}\n\n\ndef collect_scrolled(target, initial, api, capture, stop, emit, number):\n    """Require visible coverage of every declared row plus a stationary bottom page."""\n    start=table_view(initial);expected=start[\'data\'];all_keys=set(start[\'keys\'])\n    if start[\'summary_supported\']:\n        if stop.wait(.08):raise Stopped(\'사용자 중지\')\n        report=capture({**target,\'mode\':\'mes_rows\'},f\'{number}번 전체 행 요약 대조\',stop);emit(\'capture\',report)\n        row_geometry(report,start)\n        emit(\'log\',f\'{number}호기 · {len(all_keys)}행 일괄 판독·대조 완료 · 전체 스크롤 생략\')\n        return {\'method\':\'direct_rows\',\'complete\':True,\'declared_rows\':len(all_keys),\'seen_rows\':len(all_keys),\n                \'all_rows_verified\':True,\'snapshot_checks\':2,\'wheel_moves\':0,\'pages\':[],\n                \'basis\':\'전체 셀 1회 판독 후 모든 행 요약값·행 개수·열 구조·생산일 재대조\'}\n    seen=set();pages=[];current=start;started=time.monotonic();moves=0\n    def scroll(direction,phase):\n        nonlocal moves\n        if stop.is_set():raise Stopped(\'사용자 중지\')\n        if moves>=100 or time.monotonic()-started>180:\n            raise RuntimeError(\'스크롤 검사 한도에 도달했습니다. 끝까지 확인되지 않아 중단했습니다.\')\n        api.scroll_grid(current[\'handle\'],direction);moves+=1\n        if stop.wait(.12):raise Stopped(\'사용자 중지\')\n        report=capture({**target,\'mode\':\'mes_rows\'},f\'{number}번 {phase} {moves}\',stop);emit(\'capture\',report)\n        view=row_geometry(report,start)\n        if view[\'handle\']!=start[\'handle\'] or view[\'data\']!=expected:\n            raise RuntimeError(\'스크롤 중 표 내용 또는 행 개수가 바뀌어 중단했습니다.\')\n        pages.append({\'phase\':phase,\'direction\':direction,\'visible_rows\':view[\'visible\']})\n        emit(\'log\',f"{number}번 · {phase} · 보이는 행 {\',\'.join(view[\'visible\']) or \'없음\'}")\n        return view\n    # The fresh initial capture already proves the top when row 1 is visible.\n    unchanged=0\n    while all_keys and \'1\' not in current[\'visible\']:\n        previous=current[\'visible\'];current=scroll(1,\'맨 위 확인\')\n        if not all_keys or \'1\' in current[\'visible\']:break\n        unchanged=unchanged+1 if current[\'visible\']==previous else 0\n        if unchanged>=2:raise RuntimeError(\'맨 위 행에 도달하지 못했습니다. 표 스크롤 동작을 확인해 주세요.\')\n    seen.update(current[\'visible\']);unchanged=0\n    while True:\n        previous=current[\'visible\'];current=scroll(-1,\'아래로 확인\');seen.update(current[\'visible\'])\n        if current[\'visible\']==previous:\n            unchanged+=1\n            if seen==all_keys and (not all_keys or start[\'keys\'][-1] in current[\'visible\']):\n                final_report=capture(target,f\'{number}번 전체 값 최종 확인\',stop);emit(\'capture\',final_report)\n                final_view=table_view(final_report)\n                if final_view[\'handle\']!=start[\'handle\'] or final_view[\'data\']!=expected or final_view[\'row_names\']!=start[\'row_names\']:\n                    raise RuntimeError(\'스크롤 전후 표 내용이 달라 중단했습니다.\')\n                return {\'complete\':True,\'declared_rows\':len(all_keys),\'seen_rows\':len(seen),\n                        \'top_verified\':True,\'bottom_verified\':True,\'pages\':pages,\'wheel_moves\':moves,\n                        \'basis\':\'표의 실제 행 위치 전체를 화면에서 확인하고 마지막 행에서 추가 스크롤 후 위치 유지 확인\'}\n            if unchanged>=2:\n                missing=sorted(all_keys-seen,key=int)\n                raise RuntimeError(\'스크롤이 진행되지 않거나 확인하지 못한 행이 있습니다: \'+\',\'.join(missing))\n        else:unchanged=0\n\n\ndef cycle_steps(target, group, query_binding, api, capture, stop, emit, numbers=None):\n    """Only two click purposes exist: a numbered selector, then the registered query."""\n    numbers=list(range(1,11)) if numbers is None else list(numbers)\n    if not numbers or any(type(n) is not int or not 1<=n<=10 for n in numbers) or numbers!=sorted(set(numbers)):\n        raise ValueError(\'검사할 호기를 1개 이상 올바르게 선택해 주세요.\')\n    def pause(seconds):\n        if stop.wait(seconds):\n            raise Stopped(\'사용자 중지\')\n    focused = {\'handle\':group[\'panel\'], \'pid\':target[\'pid\'], \'title\':\'MES 선택 묶음\', \'mode\':\'mes_full\'}\n    previous = None\n    if stop.is_set(): raise Stopped(\'사용자 중지\')\n    emit(\'log\', \'순회 시작 전 조회 1회 → 선택 호기 \'+\', \'.join(map(str,numbers)))\n    api.query_click(query_binding)\n    emit(\'log\',\'MES 조회 후 2초 대기합니다.\')\n    pause(2.0)\n    for progress,number in enumerate(numbers,1):\n        if stop.is_set(): raise Stopped(\'사용자 중지\')\n        emit(\'log\', f\'{progress}/{len(numbers)} · {number}호기 선택 → 전체 행 일괄 판독·대조\')\n        api.number_click(group, number)\n        pause(.3)\n        first = capture(focused, f\'{number}번 선택 후 1차\', stop)\n        emit(\'capture\',first)\n        first_data = panel_data(first)\n        coverage=collect_scrolled(focused,first,api,capture,stop,emit,number)\n        second_data=first_data\n        stable=True  # All values are corroborated by a second snapshot or the full scroll fallback.\n        step = {\'number\':number, \'stable\':stable, \'changed_from_previous\':second_data != previous,\n                \'data\':second_data, \'wash_1_count\':sum(r.get(\'세척\') in (\'1\',\'01\') for r in second_data[\'rows\']),\n                \'scroll_coverage\':coverage,\n                \'refresh_confirmed\':False,\n                \'note\':\'처음 조회 1회 후 번호 선택·전체 행 일괄 판독·요약값 대조. 요약 미지원 시 스크롤 대조. 서버 응답의 최신성은 별도 검증 대상입니다.\'}\n        emit(\'step\',step)\n        previous = second_data\n    emit(\'log\',\'선택 호기 순회 수집 완료. 실제 전환·갱신 여부는 저장한 결과로 대조합니다.\')\n\n\nclass WindowsClicks:\n    def __init__(self, target):\n        self.target = target\n        self.u = ctypes.WinDLL(\'user32\',use_last_error=True)\n        u=self.u\n        specs = {\n            \'IsWindow\':([wintypes.HWND],wintypes.BOOL),\n            \'IsWindowVisible\':([wintypes.HWND],wintypes.BOOL),\n            \'IsWindowEnabled\':([wintypes.HWND],wintypes.BOOL),\n            \'IsIconic\':([wintypes.HWND],wintypes.BOOL),\n            \'GetAncestor\':([wintypes.HWND,wintypes.UINT],wintypes.HWND),\n            \'GetParent\':([wintypes.HWND],wintypes.HWND),\n            \'GetForegroundWindow\':([],wintypes.HWND),\n            \'SetForegroundWindow\':([wintypes.HWND],wintypes.BOOL),\n            \'GetWindowThreadProcessId\':([wintypes.HWND,ctypes.POINTER(wintypes.DWORD)],wintypes.DWORD),\n            \'GetWindowRect\':([wintypes.HWND,ctypes.POINTER(wintypes.RECT)],wintypes.BOOL),\n            \'GetCursorPos\':([ctypes.POINTER(wintypes.POINT)],wintypes.BOOL),\n            \'WindowFromPoint\':([wintypes.POINT],wintypes.HWND),\n            \'GetWindowTextW\':([wintypes.HWND,wintypes.LPWSTR,ctypes.c_int],ctypes.c_int),\n            \'GetClassNameW\':([wintypes.HWND,wintypes.LPWSTR,ctypes.c_int],ctypes.c_int),\n            \'GetAsyncKeyState\':([ctypes.c_int],ctypes.c_short),\n            \'GetSystemMetrics\':([ctypes.c_int],ctypes.c_int),\n        }\n        for name,(args,result) in specs.items():\n            fn=getattr(u,name);fn.argtypes=args;fn.restype=result\n        class Mouse(ctypes.Structure):\n            _fields_=[(\'dx\',ctypes.c_int32),(\'dy\',ctypes.c_int32),(\'data\',ctypes.c_uint32),\n                      (\'flags\',ctypes.c_uint32),(\'time\',ctypes.c_uint32),(\'extra\',ctypes.c_size_t)]\n        class Payload(ctypes.Union):\n            _fields_=[(\'mi\',Mouse)]\n        class Input(ctypes.Structure):\n            _fields_=[(\'type\',ctypes.c_uint32),(\'payload\',Payload)]\n        self.Input=Input\n        u.SendInput.argtypes=[wintypes.UINT,ctypes.POINTER(Input),ctypes.c_int];u.SendInput.restype=wintypes.UINT\n\n    def text(self, handle, klass=False):\n        buf=ctypes.create_unicode_buffer(512)\n        (self.u.GetClassNameW if klass else self.u.GetWindowTextW)(handle,buf,len(buf))\n        return buf.value\n\n    def verify(self, handle):\n        u=self.u;root=self.target[\'handle\'];pid=wintypes.DWORD()\n        u.GetWindowThreadProcessId(handle,ctypes.byref(pid))\n        if (not u.IsWindow(handle) or pid.value!=self.target[\'pid\'] or u.GetAncestor(handle,2)!=root\n                or u.IsIconic(root) or not u.IsWindowVisible(handle) or not u.IsWindowEnabled(handle)\n                or not u.IsWindowEnabled(root)):\n            raise RuntimeError(\'MES 창 또는 버튼 상태가 달라졌습니다. 최소화·팝업 상태를 확인해 주세요.\')\n\n    def rect(self, handle):\n        r=wintypes.RECT()\n        if not self.u.GetWindowRect(handle,ctypes.byref(r)) or r.right<=r.left or r.bottom<=r.top:\n            raise RuntimeError(\'버튼 위치를 확인하지 못했습니다.\')\n        return r\n\n    def register_query(self, report):\n        p=wintypes.POINT();self.u.GetCursorPos(ctypes.byref(p))\n        handle=int(self.u.WindowFromPoint(p) or 0);self.verify(handle)\n        candidates=[r for r in nodes(report) if r.get(\'handle\')==handle and r.get(\'parent\')==-1 and r.get(\'role\')==43]\n        if len(candidates)!=1:\n            raise RuntimeError(\'조회 버튼 자체 위에 마우스를 올려 등록해 주세요.\')\n        name=candidates[0].get(\'name\',\'\')\n        if any(word in name for word in (\'저장\',\'삭제\',\'완료\',\'닫기\',\'다운\',\'이동\')):\n            raise RuntimeError(\'조회 이외의 동작 버튼은 등록할 수 없습니다.\')\n        r=self.rect(handle)\n        return {\'handle\':handle,\'class\':self.text(handle,True),\'text\':self.text(handle),\n                \'size\':[r.right-r.left,r.bottom-r.top], \'purpose\':\'query\',\n                \'registered_by\':\'사용자가 조회 버튼을 가리키고 F8로 지정\'}\n\n    def activate(self):\n        u=self.u;root=self.target[\'handle\']\n        u.ShowWindowAsync.argtypes=[wintypes.HWND,ctypes.c_int];u.ShowWindowAsync.restype=wintypes.BOOL\n        if u.IsIconic(root):\n            u.ShowWindowAsync(root,9)\n            for _ in range(20):\n                if not u.IsIconic(root):break\n                time.sleep(.05)\n        self.verify(root)\n        u.SetForegroundWindow(root)\n        for _ in range(20):\n            if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped(\'F9 중지\')\n            if u.GetForegroundWindow()==root:return\n            time.sleep(.05)\n        raise RuntimeError(\'Windows가 대상 창을 앞으로 가져오지 못했습니다. MES·POP와 지후니우스를 같은 권한으로 실행하고 다시 시작해 주세요.\')\n\n    def click_handle(self, handle, static=False, selection=None):\n        self.verify(handle);u=self.u;root=self.target[\'handle\']\n        if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped(\'F9 중지\')\n        if u.GetForegroundWindow()!=root:\n            raise RuntimeError(\'MES 이외의 창이 앞에 있어 중단했습니다.\')\n        if any(u.GetAsyncKeyState(k)&0x8000 for k in (1,2,16,17,18,91,92)):\n            raise RuntimeError(\'마우스 버튼 또는 보조 키가 눌려 있어 중단했습니다.\')\n        r=self.rect(handle);x=(r.left+r.right)//2;y=(r.top+r.bottom)//2\n        if selection is not None:\n            bx,by,bw,bh=selection\n            if bw<=0 or bh<=0 or not(r.left<=bx and bx+bw<=r.right and r.top<=by and by+bh<=r.bottom):\n                raise RuntimeError(\'MES 탭 위치가 현재 창 범위와 맞지 않습니다.\')\n            x=round(bx+bw/2);y=round(by+bh/2)\n        hit=u.WindowFromPoint(wintypes.POINT(x,y))\n        allowed=hit==handle or (static and hit==u.GetParent(handle))\n        if not allowed:\n            raise RuntimeError(\'버튼이 다른 창에 가려져 있어 중단했습니다.\')\n        left=u.GetSystemMetrics(76);top=u.GetSystemMetrics(77);w=u.GetSystemMetrics(78);h=u.GetSystemMetrics(79)\n        if not(left<=x<left+w and top<=y<top+h) or w<=1 or h<=1:\n            raise RuntimeError(\'버튼이 모니터 표시 범위 밖에 있습니다.\')\n        items=(self.Input*3)()\n        for item in items:item.type=0\n        items[0].payload.mi.dx=round((x-left)*65535/(w-1))\n        items[0].payload.mi.dy=round((y-top)*65535/(h-1))\n        items[0].payload.mi.flags=0x8000|0x4000|0x0001\n        items[1].payload.mi.flags=0x0002;items[2].payload.mi.flags=0x0004\n        if u.SendInput(3,items,ctypes.sizeof(self.Input))!=3:\n            # Release only; never retry a potentially completed click.\n            release=self.Input();release.payload.mi.flags=0x0004\n            u.SendInput(1,ctypes.byref(release),ctypes.sizeof(self.Input))\n            raise RuntimeError(\'Windows가 클릭 입력을 완료하지 못했습니다. 자동 재시도하지 않습니다.\')\n\n    def selected_number(self, group):\n        # Read six background pixels inside each known number control, not its text.\n        u=self.u\n        if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped(\'F9 중지\')\n        if u.GetForegroundWindow()!=self.target[\'handle\']:raise RuntimeError(\'MES 선택 번호 확인 중 다른 창이 앞에 있습니다.\')\n        g=ctypes.WinDLL(\'gdi32\',use_last_error=True)\n        u.GetDC.argtypes=[wintypes.HWND];u.GetDC.restype=wintypes.HDC\n        u.ReleaseDC.argtypes=[wintypes.HWND,wintypes.HDC];u.ReleaseDC.restype=ctypes.c_int\n        g.GetPixel.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int];g.GetPixel.restype=ctypes.c_uint32\n        dc=u.GetDC(None)\n        if not dc:raise RuntimeError(\'MES 선택 번호의 색상을 읽지 못했습니다.\')\n        selected=[]\n        try:\n            for number,handle in group[\'buttons\'].items():\n                self.verify(handle);r=self.rect(handle);hits=0\n                for fx in (.18,.82):\n                    for fy in (.25,.5,.75):\n                        x=r.left+round((r.right-r.left-1)*fx);y=r.top+round((r.bottom-r.top-1)*fy)\n                        if u.WindowFromPoint(wintypes.POINT(x,y)) not in (handle,u.GetParent(handle)):\n                            raise RuntimeError(\'MES 숫자 버튼이 다른 화면에 가려져 있습니다.\')\n                        color=g.GetPixel(dc,x,y)\n                        if color==0xffffffff:raise RuntimeError(\'MES 선택 번호의 색상을 읽지 못했습니다.\')\n                        red=color&255;green=(color>>8)&255;blue=(color>>16)&255\n                        hits+=red>=190 and green>=190 and blue<=110 and min(red,green)-blue>=90\n                if hits>=4:selected.append(number)\n        finally:u.ReleaseDC(None,dc)\n        if len(selected)!=1:raise RuntimeError(\'MES 왼쪽 위의 노란색 선택 번호를 하나로 확인하지 못했습니다.\')\n        return selected[0]\n\n    def restore_number(self,group,number,stop):\n        if stop.is_set():raise Stopped(\'사용자 중지\')\n        if self.selected_number(group)==number:return\n        self.number_click(group,number)\n        for _ in range(6):\n            if stop.wait(.05):raise Stopped(\'사용자 중지\')\n            if self.selected_number(group)==number:return\n        raise RuntimeError(f\'MES 원래 선택 번호 {number}번 복귀를 확인하지 못했습니다.\')\n\n    def number_click(self, group, number):\n        handle=group[\'buttons\'][number]\n        if self.u.GetParent(handle)!=group[\'parent\'] or self.text(handle)!=str(number) or \'STATIC\' not in self.text(handle,True):\n            raise RuntimeError(\'숫자 버튼의 내용이 바뀌어 중단했습니다.\')\n        self.click_handle(handle,static=True)\n\n    def query_click(self, binding):\n        handle=binding[\'handle\'];self.verify(handle);r=self.rect(handle)\n        if (binding.get(\'purpose\')!=\'query\' or self.text(handle,True)!=binding[\'class\']\n                or self.text(handle)!=binding[\'text\'] or [r.right-r.left,r.bottom-r.top]!=binding[\'size\']):\n            raise RuntimeError(\'등록한 조회 버튼이 바뀌어 중단했습니다.\')\n        self.click_handle(handle)\n\n    def scroll_grid(self,handle,direction):\n        if direction not in (-1,1):raise ValueError(\'스크롤 방향 오류\')\n        self.verify(handle);u=self.u\n        if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped(\'F9 중지\')\n        if u.GetForegroundWindow()!=self.target[\'handle\']:\n            raise RuntimeError(\'MES 창이 앞에 있지 않아 스크롤을 중단했습니다.\')\n        if any(u.GetAsyncKeyState(k)&0x8000 for k in (1,2,16,17,18,91,92)):\n            raise RuntimeError(\'키 또는 마우스 버튼이 눌려 있어 스크롤을 중단했습니다.\')\n        r=self.rect(handle);x=(r.left+r.right)//2;y=(r.top+r.bottom)//2\n        hit=u.WindowFromPoint(wintypes.POINT(x,y));ancestors=set()\n        while hit and hit not in ancestors and hit!=handle:\n            ancestors.add(hit);hit=u.GetParent(hit)\n        if hit!=handle:raise RuntimeError(\'표가 다른 창에 가려져 있어 스크롤을 중단했습니다.\')\n        left=u.GetSystemMetrics(76);top=u.GetSystemMetrics(77);w=u.GetSystemMetrics(78);h=u.GetSystemMetrics(79)\n        if w<=1 or h<=1 or not(left<=x<left+w and top<=y<top+h):raise RuntimeError(\'표가 모니터 밖에 있습니다.\')\n        items=(self.Input*2)()\n        items[0].payload.mi.dx=round((x-left)*65535/(w-1));items[0].payload.mi.dy=round((y-top)*65535/(h-1))\n        items[0].payload.mi.flags=0x8000|0x4000|1\n        items[1].payload.mi.flags=0x0800;items[1].payload.mi.data=(direction*120)&0xffffffff\n        if u.SendInput(2,items,ctypes.sizeof(self.Input))!=2:\n            raise RuntimeError(\'Windows가 스크롤 입력을 완료하지 못했습니다.\')\n\n\n'
WASH_POP_SOURCE = 'SEQUENCE = "06"\nSEQUENCE_VALUES = tuple(f\'{n:02}\' for n in range(1,31)) + (\'O\',)\n\ndef pop_sequence(value=None):\n    value=SEQUENCE if value is None else value\n    return \'완료\' if value in (\'O\',\'o\') else value\n\n\ndef normalize_sequence(value):\n    value=str(value).strip()\n    if value in (\'O\',\'o\'):return \'O\'\n    if value.isascii() and value.isdigit() and 1<=int(value)<=30:return f\'{int(value):02}\'\n    return None\n\n"""POP 세척06 체크 검사. 조회 1회 후 목록을 읽고 MES 세척6 매칭 행만 체크합니다.\n검사일·작업자·세척순서를 설정하고 대상만 체크합니다. 통합기에서는 검증 후 저장·확인을 수행합니다. Windows / Python 3.8+.\n내장 MSAA 판독기는 읽기 전용입니다.\n"""\nimport base64\nimport ctypes\nfrom ctypes import wintypes\nfrom datetime import datetime\nimport json\nimport os\nfrom pathlib import Path\nimport queue\nimport subprocess\nimport tempfile\nimport threading\nimport time\nimport zipfile\nimport xml.etree.ElementTree as ET\n\n# MSAA의 읽기 API만 사용합니다. 공급자 등록 단계 없이 선택 창에서 정보를 읽으며,\n# 각 행을 즉시 기록합니다. 가상화된 행을 표시하거나 스크롤하지 않습니다.\nPOWERSHELL = r\'\'\'\n$ErrorActionPreference = \'Stop\'\n$ProgressPreference = \'SilentlyContinue\'\n$writer = New-Object System.IO.StreamWriter($env:MES_DIAG_OUTPUT, $false, (New-Object System.Text.UTF8Encoding($false)))\n$writer.AutoFlush = $true\nfunction Emit($record) { $writer.WriteLine(($record | ConvertTo-Json -Depth 8 -Compress)) }\ntry {\n    Add-Type -AssemblyName Accessibility\n    $source = @\'\nusing System;\nusing System.Collections.Generic;\nusing System.Diagnostics;\nusing System.Runtime.InteropServices;\nusing System.Text;\nusing Accessibility;\n\npublic sealed class MesReadOnlyAccessibility {\n    [ThreadStatic] public static bool GeometryOnly;\n    [ThreadStatic] public static bool VisibleRowsOnly;\n    // 0: original geometry; 1: MES cell values; 2: POP hidden-row cell values.\n    [ThreadStatic] public static int CellBoundsMode; // 3: final verification, omit hidden-cell names only\n    [DllImport("oleacc.dll")]\n    static extern int AccessibleObjectFromWindow(IntPtr hwnd, uint objectId, ref Guid iid,\n        [MarshalAs(UnmanagedType.Interface)] out IAccessible result);\n    [DllImport("oleacc.dll")]\n    static extern int AccessibleChildren(IAccessible parent, int start, int count,\n        [Out, MarshalAs(UnmanagedType.LPArray, SizeParamIndex=2, ArraySubType=UnmanagedType.Struct)] object[] children,\n        out int obtained);\n    [DllImport("oleacc.dll")] static extern int WindowFromAccessibleObject(IAccessible acc, out IntPtr hwnd);\n    delegate bool EnumProc(IntPtr hwnd, IntPtr data);\n    [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr parent, EnumProc callback, IntPtr data);\n    [DllImport("user32.dll")] static extern bool IsWindow(IntPtr hwnd);\n    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr hwnd);\n    [DllImport("user32.dll")] static extern IntPtr GetParent(IntPtr hwnd);\n    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);\n    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr hwnd, StringBuilder text, int count);\n\n    readonly Stopwatch clock = Stopwatch.StartNew();\n    readonly HashSet<long> seen = new HashSet<long>();\n    readonly List<object> retained = new List<object>();\n    readonly HashSet<long> nativeHandles = new HashSet<long>();\n    readonly Action<object> emit;\n    int count, windows, propertyErrors, skippedChrome, deferredWindows;\n    bool limited;\n    MesReadOnlyAccessibility(Action<object> output) { emit=output; }\n    bool AtLimit() {\n        if (count>=15000 || clock.Elapsed.TotalSeconds>=35) { limited=true; return true; }\n        return false;\n    }\n    static string Trim(object value, int maxLength=800) {\n        string s=value==null ? "" : Convert.ToString(value);\n        return s.Length>maxLength ? s.Substring(0,maxLength)+" [truncated]" : s;\n    }\n    object Read(Func<object> getter) {\n        try { return getter(); } catch { propertyErrors++; return null; }\n    }\n    static string RoleName(int role) {\n        switch(role) {\n            case 9:return "MSAA.Window"; case 10:return "MSAA.Client";\n            case 24:return "MSAA.Table"; case 25:return "MSAA.ColumnHeader";\n            case 26:return "MSAA.RowHeader"; case 27:return "MSAA.Column";\n            case 28:return "MSAA.Row"; case 29:return "MSAA.Cell";\n            case 33:return "MSAA.List"; case 34:return "MSAA.ListItem";\n            case 41:return "MSAA.StaticText"; case 42:return "MSAA.Text";\n            case 43:return "MSAA.PushButton"; case 44:return "MSAA.CheckBox";\n            case 45:return "MSAA.RadioButton"; case 46:return "MSAA.ComboBox";\n            default:return "MSAA.Role"+role;\n        }\n    }\n    void Walk(IAccessible acc, int child, int parent, int depth, IntPtr hwnd, bool skipCellBounds=false) {\n        if(acc==null || AtLimit())return;\n        if(depth>32) { limited=true; return; }\n        object roleObject=Read(delegate { return acc.get_accRole(child); });\n        int role=0;\n        try {if(roleObject!=null)role=Convert.ToInt32(roleObject);}catch{}\n        // Skip standard title bars, scroll bars and grips; keep application menus.\n        if(role==1 || role==3 || role==4) {skippedChrome++;return;}\n        // Read native child windows from their own handles, avoiding repeated deep trees.\n        if(role==9 && child==0) {\n            IntPtr owner;\n            if(WindowFromAccessibleObject(acc,out owner)>=0 && owner!=hwnd && nativeHandles.Contains(owner.ToInt64())) {\n                deferredWindows++;\n                emit(new Dictionary<string,object>{{"kind","native_reference"},{"parent",parent},{"handle",owner.ToInt64()}});\n                return;\n            }\n        }\n        if(child==0) {\n            IntPtr identity=Marshal.GetIUnknownForObject(acc);\n            bool fresh;\n            try { fresh=seen.Add(identity.ToInt64()); }\n            finally { Marshal.Release(identity); }\n            if(!fresh)return;\n            retained.Add(acc);\n        }\n        int id=count++;\n        object stateObject=Read(delegate { return acc.get_accState(child); });\n        int state=0;\n        bool stateKnown=stateObject!=null;\n        if(stateKnown) {\n            try { state=Convert.ToInt32(stateObject); } catch {stateKnown=false;}\n        }\n        // Missing state is treated conservatively: do not read potentially secret text.\n        bool secret=!stateKnown || (state & 0x20000000)!=0;\n        var row=new Dictionary<string,object>();\n        row["kind"]="element";row["engine"]="MSAA";row["id"]=id;row["parent"]=parent;row["depth"]=depth;\n        row["handle"]=hwnd.ToInt64();row["child_id"]=child;row["role"]=role;row["type"]=RoleName(role);\n        row["state"]=state;row["state_known"]=stateKnown;row["password"]=secret;\n        row["enabled"]=(state & 1)==0;row["offscreen"]=(state & 0x18000)!=0;\n        row["patterns"]=new string[0];row["name"]="";\n        if(!secret) {\n            row["name"]=(CellBoundsMode==3 && role==29 && skipCellBounds) ? "" : Trim(Read(delegate {return acc.get_accName(child);}));\n            // Row summaries contain many cells; keep them intact for fast value verification.\n            row["value"]=Trim(Read(delegate {return acc.get_accValue(child);}), role==28 ? 65536 : 800);\n\n            if(role==24 || role==25 || role==28 || (role==29 && CellBoundsMode!=1 && !skipCellBounds) || role==37 || (role>=41 && role<=47)) {\n\n                try {\n                    int x,y,w,h;acc.accLocation(out x,out y,out w,out h,child);\n                    row["bounds"]=new int[]{x,y,w,h};\n                } catch {propertyErrors++;}\n            }\n            if(role>=41 && role<=47) {\n\n\n            }\n            if(role==44 || role==45)row["toggle_state"]=(state & 0x10)!=0 ? "Checked" : ((state & 0x20)!=0 ? "Mixed" : "Unchecked");\n            row["selected"]=(state & 2)!=0;\n        }\n        int total=0;\n        if(!secret && child==0) {\n            object value=Read(delegate {return acc.accChildCount;});\n            if(value!=null)try {total=Math.Max(0,Convert.ToInt32(value));}catch{}\n        }\n        row["child_count"]=total;\n        emit(row);\n        if(GeometryOnly && role==28 && (Convert.ToString(row["name"]).StartsWith("행 ") || Convert.ToString(row["name"]).StartsWith("Row ")))return;\n        if(VisibleRowsOnly && role==28 && (Convert.ToString(row["name"]).StartsWith("행 ") || Convert.ToString(row["name"]).StartsWith("Row "))) {\n            int[] b=row.ContainsKey("bounds") ? row["bounds"] as int[] : null;\n            if((state & 0x18000)!=0 || b==null || b[2]<=0 || b[3]<=0) {\n                row["cells_omitted"]=true;\n                return;\n            }\n        }\n        // Preserve geometry for every cell in a visible row: column uniqueness\n        // checks also need unexpected or unnamed cells. Hidden rows still retain\n        // every cell value, state and child count; final mode omits hidden-cell names.\n        if((CellBoundsMode==2 || CellBoundsMode==3) && role==28 && (Convert.ToString(row["name"]).StartsWith("행 ") || Convert.ToString(row["name"]).StartsWith("Row "))) {\n            int[] b=row.ContainsKey("bounds") ? row["bounds"] as int[] : null;\n            skipCellBounds=(state & 0x18000)!=0 || b==null || b[2]<=0 || b[3]<=0;\n        }\n        if(secret || child!=0 || total==0 || AtLimit())return;\n        if(depth>=32) {limited=true;return;}\n        for(int start=0;start<total;start+=32) {\n            if(AtLimit())return;\n            int size=Math.Min(32,total-start);\n            object[] children=new object[size];int obtained=0;int hr;\n            try {hr=AccessibleChildren(acc,start,size,children,out obtained);}\n            catch(Exception error) {emit(new Dictionary<string,object>{{"kind","element_error"},{"id",id},{"error",Trim(error.Message)}});return;}\n            if(hr<0) {emit(new Dictionary<string,object>{{"kind","element_error"},{"id",id},{"hresult",hr}});return;}\n            if(obtained<=0)return;\n            for(int index=0;index<Math.Min(obtained,size);index++) {\n                if(AtLimit())return;\n                object item=children[index];\n                IAccessible objectChild=item as IAccessible;\n                if(objectChild!=null) {Walk(objectChild,0,id,depth+1,hwnd,skipCellBounds);continue;}\n                if(item is int) {\n                    int childId=(int)item;\n                    if(childId<=0)continue;\n                    IAccessible expanded=Read(delegate {return acc.get_accChild(childId);}) as IAccessible;\n                    if(expanded!=null)Walk(expanded,0,id,depth+1,hwnd,skipCellBounds);\n                    else Walk(acc,childId,id,depth+1,hwnd,skipCellBounds);\n                }\n            }\n        }\n    }\n    void Window(IntPtr hwnd, uint expectedPid) {\n        uint pid;GetWindowThreadProcessId(hwnd,out pid);\n        if(pid!=expectedPid || AtLimit())return;\n        windows++;\n        StringBuilder klass=new StringBuilder(256);GetClassName(hwnd,klass,klass.Capacity);\n        Guid iid=new Guid("618736E0-3C3D-11CF-810C-00AA00389B71");\n        IAccessible acc=null;\n        int hr=AccessibleObjectFromWindow(hwnd,0xFFFFFFFC,ref iid,out acc);\n        emit(new Dictionary<string,object>{{"kind","native_window"},{"handle",hwnd.ToInt64()},\n            {"native_parent",GetParent(hwnd).ToInt64()},{"class",klass.ToString()},{"hresult",hr},{"accessible",acc!=null}});\n        if(hr>=0 && acc!=null)Walk(acc,0,-1,0,hwnd);\n    }\n    public static void Dump(long handle, int expectedPid, Action<object> output) {\n        var reader=new MesReadOnlyAccessibility(output);\n        IntPtr hwnd=new IntPtr(handle);uint pid;\n        GetWindowThreadProcessId(hwnd,out pid);\n        if(!IsWindow(hwnd) || pid!=(uint)expectedPid)throw new InvalidOperationException("Selected window changed. Refresh the window list.");\n        var handles=new List<IntPtr>();handles.Add(hwnd);\n        EnumProc callback=delegate(IntPtr child,IntPtr data) {\n            if(handles.Count>=512) {reader.limited=true;return false;}\n            uint owner;GetWindowThreadProcessId(child,out owner);\n            if(owner==pid && IsWindowVisible(child))handles.Add(child);\n            return true;\n        };\n        EnumChildWindows(hwnd,callback,IntPtr.Zero);\n        foreach(IntPtr target in handles)reader.nativeHandles.Add(target.ToInt64());\n        output(new Dictionary<string,object>{{"kind","start"},{"engine","MSAA"},{"read_only",true},{"pid",pid}});\n        foreach(IntPtr target in handles) {\n            if(reader.AtLimit())break;\n            try {reader.Window(target,pid);}\n            catch(Exception error) {output(new Dictionary<string,object>{{"kind","window_error"},{"handle",target.ToInt64()},{"error",Trim(error.Message)}});}\n        }\n        output(new Dictionary<string,object>{{"kind","finish"},{"engine","MSAA"},{"elements",reader.count},\n            {"windows_read",reader.windows},{"windows_found",handles.Count},{"property_errors",reader.propertyErrors},\n            {"skipped_chrome",reader.skippedChrome},{"deferred_windows",reader.deferredWindows},\n            {"limited",reader.limited},{"seconds",reader.clock.Elapsed.TotalSeconds}});\n        GC.KeepAlive(callback);GC.KeepAlive(reader.retained);\n    }\n}\n\n\'@\n    Add-Type -TypeDefinition $source -Language CSharp -ReferencedAssemblies @([Accessibility.IAccessible].Assembly.Location, \'System.dll\', \'System.Core.dll\')\n    $output = [Action[object]] { param($record) Emit $record }\n    [MesReadOnlyAccessibility]::Dump([long]$env:MES_DIAG_HANDLE, [int]$env:MES_DIAG_PID, $output)\n} catch { Emit @{kind=\'fatal\'; error=$_.Exception.ToString()} }\nfinally { $writer.Dispose() }\n\'\'\'\n\n\ndef visible_windows(include_untitled=False):\n    if os.name != \'nt\':\n        return []\n    user = ctypes.WinDLL(\'user32\', use_last_error=True)\n    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)\n    user.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]\n    user.EnumWindows.restype = wintypes.BOOL\n    user.IsWindowVisible.argtypes = [wintypes.HWND]\n    user.IsWindowVisible.restype = wintypes.BOOL\n    user.GetWindowTextLengthW.argtypes = [wintypes.HWND]\n    user.GetWindowTextLengthW.restype = ctypes.c_int\n    user.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]\n    user.GetWindowTextW.restype = ctypes.c_int\n    user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]\n    user.GetWindowThreadProcessId.restype = wintypes.DWORD\n    user.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]\n    user.GetClassNameW.restype = ctypes.c_int\n    result = []\n    @callback_type\n    def visit(handle, _):\n        if not user.IsWindowVisible(handle):\n            return True\n        pid = wintypes.DWORD()\n        user.GetWindowThreadProcessId(handle, ctypes.byref(pid))\n        if pid.value == os.getpid():\n            return True\n        length = min(user.GetWindowTextLengthW(handle), 4096)\n        if not length and not include_untitled:\n            return True\n        title = ctypes.create_unicode_buffer(length + 1)\n        user.GetWindowTextW(handle, title, len(title))\n        klass = ctypes.create_unicode_buffer(256)\n        user.GetClassNameW(handle, klass, len(klass))\n        result.append({\'handle\':int(handle), \'pid\':pid.value, \'title\':title.value, \'class\':klass.value})\n        return True\n    if not user.EnumWindows(visit, 0):\n        raise ctypes.WinError(ctypes.get_last_error())\n    return sorted(result, key=lambda w: w[\'title\'].casefold())\n\n\ndef powershell_errors(raw):\n    """PowerShell 진행 안내(CLIXML)를 오류로 잘못 분류하지 않습니다."""\n    if raw.startswith((b\'\\xff\\xfe\', b\'\\xfe\\xff\')):\n        text = raw.decode(\'utf-16\', errors=\'replace\')\n    else:\n        text = raw.decode(\'utf-8-sig\', errors=\'replace\')\n    if text.lstrip().startswith(\'#< CLIXML\'):\n        try:\n            xml = ET.fromstring(text[text.index(\'<Objs\'):])\n            errors = [node.text or \'\' for node in xml.iter()\n                      if node.attrib.get(\'S\', \'\').lower() == \'error\']\n            return \'\\n\'.join(errors)\n        except (ValueError, ET.ParseError):\n            pass\n    return text.strip()\n\n\ndef probe_command(powershell, directory, env):\n    """Keep the embedded reader in a private temporary file, below Windows\' command limit."""\n    opening = "    $source = @\'\\n"\n    start = POWERSHELL.index(opening)\n    end = POWERSHELL.index("\\n\'@", start)\n    source = Path(directory)/\'reader.cs\'\n    source.write_text(POWERSHELL[start+len(opening):end], encoding=\'utf-8-sig\')\n    env[\'MES_DIAG_SOURCE\'] = str(source)\n    script = (POWERSHELL[:start] +\n              \'    $source = [System.IO.File]::ReadAllText($env:MES_DIAG_SOURCE)\' +\n              POWERSHELL[end+3:])\n    return [str(powershell), \'-NoLogo\', \'-NoProfile\', \'-NonInteractive\', \'-STA\',\n            \'-EncodedCommand\', base64.b64encode(script.encode(\'utf-16le\')).decode(\'ascii\')]\n\n\ndef inspect_window(target, label, stop):\n    """Runs an isolated read-only probe; cancels only the probe, never the MES app."""\n    report = {\'tool\':\'MES_POP_화면확인\', \'version\':4, \'captured_at\':datetime.now().isoformat(timespec=\'seconds\'),\n              \'label\':label, \'target\':dict(target), \'read_only\':True,\n              \'scope\':\'선택 창의 노출된 UI 정보. 스크롤·체크·입력·저장·서버 통신 없음.\', \'records\':[]}\n    windir = Path(os.environ.get(\'SystemRoot\', r\'C:\\Windows\'))\n    powershell = windir/\'System32\'/\'WindowsPowerShell\'/\'v1.0\'/\'powershell.exe\'\n    if not powershell.is_file():\n        raise RuntimeError(\'Windows PowerShell을 찾지 못했습니다. Windows PC에서 실행해 주세요.\')\n    with tempfile.TemporaryDirectory(prefix=\'mes_pop_read_\') as tmp:\n        output = Path(tmp)/\'readout.jsonl\'\n        stderr = Path(tmp)/\'errors.txt\'\n        env = os.environ.copy()\n        env.update(MES_DIAG_HANDLE=str(int(target[\'handle\'])), MES_DIAG_PID=str(int(target[\'pid\'])), MES_DIAG_OUTPUT=str(output))\n        command = probe_command(powershell, tmp, env)\n        with stderr.open(\'wb\') as errors:\n            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,\n                                       stderr=errors, env=env, creationflags=getattr(subprocess,\'CREATE_NO_WINDOW\',0))\n            deadline = time.monotonic()+45\n            try:\n                while process.poll() is None:\n                    if stop.wait(.1) or time.monotonic() >= deadline:\n                        report[\'interrupted\'] = \'사용자 중지\' if stop.is_set() else \'45초 제한 시간\'\n                        process.kill()\n                        break\n                process.wait(timeout=5)\n            finally:\n                if process.poll() is None:\n                    process.kill()\n                    process.wait(timeout=5)\n        report[\'exit_code\'] = process.returncode\n        if output.exists():\n            for line in output.read_text(encoding=\'utf-8-sig\',errors=\'replace\').splitlines():\n                try:\n                    record = json.loads(line)\n                    if isinstance(record,dict): report[\'records\'].append(record)\n                except ValueError:\n                    report[\'partial_line\'] = True\n        error_bytes = stderr.read_bytes()[:6000]\n        error_text = powershell_errors(error_bytes)\n        if error_text:\n            report[\'powershell_error\'] = error_text\n    return report\n\n\ndef report_summary(report):\n    records = report[\'records\']\n    elements = [r for r in records if r.get(\'kind\')==\'element\']\n    grids = [r for r in elements if \'grid_rows\' in r or r.get(\'type\') == \'MSAA.Table\']\n    values = [r for r in elements if any(r.get(k) for k in (\'value\',\'text\',\'legacy_value\'))]\n    fatal = [r.get(\'error\',\'\') for r in records if r.get(\'kind\')==\'fatal\']\n    finished = any(r.get(\'kind\')==\'finish\' for r in records)\n    partial = bool(report.get(\'interrupted\') or report.get(\'partial_line\') or not finished\n                   or any(r.get(\'limited\') for r in records))\n    lines = [f"[{report[\'label\']}] {report[\'target\'][\'title\']}",\n             f"읽은 항목 {len(elements)}개 / 표 정보 {len(grids)}개 / 값·텍스트 {len(values)}개",\n             \'일부 결과: 중지·제한 시간·읽기 제한이 있어 전체 화면을 확인하지 못했습니다.\' if partial else \'화면 정보 읽기가 끝났습니다.\',\n             \'이 결과만으로 자동 완료 가능 여부를 확정하지 않습니다.\']\n    if fatal: lines.extend(\'읽기 오류: \'+s for s in fatal)\n    providers = [r for r in records if r.get(\'kind\') == \'provider\']\n    if any(r.get(\'engine\') == \'MSAA\' for r in records):\n        lines.append(\'검사 방식: MSAA 직접 읽기 (버튼 실행·선택 변경 없음)\')\n        finishes = [r for r in records if r.get(\'kind\') == \'finish\']\n        if finishes and \'windows_found\' in finishes[-1]:\n            end = finishes[-1]\n            lines.append(f"창 검사 {end.get(\'windows_read\', 0)}/{end[\'windows_found\']}개 / 테두리·스크롤 요소 {end.get(\'skipped_chrome\', 0)}개 생략")\n        locations = sum(bool(r.get(\'bounds\') and r[\'bounds\'][2]>0 and r[\'bounds\'][3]>0) for r in elements)\n        lines.append(f\'위치가 읽힌 항목 {locations}개. 표의 열 순서는 화면 순서와 다를 수 있어 별도 대조합니다.\')\n    if providers:\n        lines.append(\'컨트롤 읽기 연결: \' + (\'등록됨\' if providers[-1].get(\'registered\') else \'등록 실패 — 결과 파일에서 원인 확인\'))\n    named_only = elements and not any(r.get(\'patterns\') or r.get(\'value\') or r.get(\'type\') in (\'MSAA.Cell\',\'MSAA.Row\',\'MSAA.CheckBox\') for r in elements if r.get(\'type\') != \'ControlType.Window\')\n    if named_only:\n        lines.append(\'현재는 창 이름·표시 글자만 읽혔습니다. 표 데이터와 체크박스 조작 정보는 확인되지 않았습니다.\')\n    if report.get(\'powershell_error\'): lines.append(\'PowerShell 오류가 있습니다. 결과 파일에 포함됩니다.\')\n    if not elements: lines.append(\'대상 창이 열려 있는지 확인하세요. 접근 권한 또는 화면 구조 때문에 읽지 못했을 수 있습니다.\')\n    return \'\\n\'.join(lines)\n\n\ndef save_reports(path, reports):\n    if not reports: raise ValueError(\'먼저 창을 검사해 주세요.\')\n    path = Path(path)\n    text = [\'POP 세척06 체크 검사의 화면 판독 결과\', \'POP 조회·스크롤·체크 중 수집한 화면 정보 — 저장·완료 실행 없음\', \'\',\n            \'선택한 창의 표시 문자열이 포함됩니다. 비밀번호 필드는 수집하지 않습니다.\',\n            \'스크롤 밖의 가상화된 행은 누락될 수 있습니다. 목록 전체 수집 가능 여부는 별도 확인이 필요합니다.\', \'\']\n    for index, report in enumerate(reports,1):\n        text.extend([f\'--- 검사 {index} ---\',report_summary(report),\'\'])\n        for record in report[\'records\']:\n            if record.get(\'kind\')==\'element\':\n                fields = [\'  \'*min(record.get(\'depth\',0),18)+str(record.get(\'type\',\'\')),\n                          \'name=\'+str(record.get(\'name\',\'\')), \'id=\'+str(record.get(\'automation_id\',\'\')),\n                          \'class=\'+str(record.get(\'class\',\'\')), \'patterns=\'+\', \'.join(record.get(\'patterns\',[]))]\n                for key in (\'value\',\'text\',\'legacy_value\',\'grid_rows\',\'grid_columns\',\'row\',\'column\',\'toggle_state\',\'selected\',\'role\',\'state\',\'child_count\',\'default_action\',\'bounds\',\'description\',\'help\',\'shortcut\'):\n                    if key in record: fields.append(key+\'=\'+str(record[key]))\n                text.append(\' | \'.join(fields))\n        text.append(\'\')\n    # Save to a sibling temporary file, then atomically replace the chosen output.\n    temporary = None\n    try:\n        with tempfile.NamedTemporaryFile(prefix=\'mes_report_\',suffix=\'.zip\',dir=str(path.parent),delete=False) as f:\n            temporary = Path(f.name)\n        with zipfile.ZipFile(temporary,\'w\',zipfile.ZIP_DEFLATED) as archive:\n            archive.writestr(\'MES_POP_report.json\',json.dumps({\'schema\':1,\'captures\':reports},ensure_ascii=False,indent=2).encode(\'utf-8\'))\n            archive.writestr(\'MES_POP_report.txt\',\'\\n\'.join(text).encode(\'utf-8-sig\'))\n        os.replace(temporary,path)\n    finally:\n        if temporary is not None and temporary.exists(): temporary.unlink()\n\n\nfrom collections import defaultdict\nimport re\n\n\ndef nodes(report):\n    return [r for r in report[\'records\'] if r.get(\'kind\') == \'element\']\n\n\ndef check_capture(report):\n    finishes = [r for r in report[\'records\'] if r.get(\'kind\') == \'finish\']\n    if (report.get(\'interrupted\') or report.get(\'powershell_error\') or report.get(\'partial_line\')\n            or report.get(\'exit_code\') != 0 or not finishes or finishes[-1].get(\'limited\')\n            or any(r.get(\'kind\') in (\'fatal\',\'window_error\',\'element_error\') for r in report[\'records\'])):\n        raise RuntimeError(\'화면을 충분히 읽지 못해 순회를 중단했습니다. 결과를 저장해 주세요.\')\n\n\n\nclass Stopped(Exception):\n    pass\n\nclass WindowsClicks:\n    def __init__(self, target):\n        self.target = target\n        self.u = ctypes.WinDLL(\'user32\',use_last_error=True)\n        u=self.u\n        specs = {\n            \'IsWindow\':([wintypes.HWND],wintypes.BOOL),\n            \'IsWindowVisible\':([wintypes.HWND],wintypes.BOOL),\n            \'IsWindowEnabled\':([wintypes.HWND],wintypes.BOOL),\n            \'IsIconic\':([wintypes.HWND],wintypes.BOOL),\n            \'GetAncestor\':([wintypes.HWND,wintypes.UINT],wintypes.HWND),\n            \'GetParent\':([wintypes.HWND],wintypes.HWND),\n            \'GetForegroundWindow\':([],wintypes.HWND),\n            \'SetForegroundWindow\':([wintypes.HWND],wintypes.BOOL),\n            \'GetWindowThreadProcessId\':([wintypes.HWND,ctypes.POINTER(wintypes.DWORD)],wintypes.DWORD),\n            \'GetWindowRect\':([wintypes.HWND,ctypes.POINTER(wintypes.RECT)],wintypes.BOOL),\n            \'GetCursorPos\':([ctypes.POINTER(wintypes.POINT)],wintypes.BOOL),\n            \'WindowFromPoint\':([wintypes.POINT],wintypes.HWND),\n            \'GetWindowTextW\':([wintypes.HWND,wintypes.LPWSTR,ctypes.c_int],ctypes.c_int),\n            \'GetClassNameW\':([wintypes.HWND,wintypes.LPWSTR,ctypes.c_int],ctypes.c_int),\n            \'GetAsyncKeyState\':([ctypes.c_int],ctypes.c_short),\n            \'GetSystemMetrics\':([ctypes.c_int],ctypes.c_int),\n        }\n        for name,(args,result) in specs.items():\n            fn=getattr(u,name);fn.argtypes=args;fn.restype=result\n        class Mouse(ctypes.Structure):\n            _fields_=[(\'dx\',ctypes.c_int32),(\'dy\',ctypes.c_int32),(\'data\',ctypes.c_uint32),\n                      (\'flags\',ctypes.c_uint32),(\'time\',ctypes.c_uint32),(\'extra\',ctypes.c_size_t)]\n        class Keyboard(ctypes.Structure):\n            _fields_=[(\'vk\',ctypes.c_uint16),(\'scan\',ctypes.c_uint16),(\'flags\',ctypes.c_uint32),\n                      (\'time\',ctypes.c_uint32),(\'extra\',ctypes.c_size_t)]\n        class Payload(ctypes.Union):\n            _fields_=[(\'mi\',Mouse),(\'ki\',Keyboard)]\n        class Input(ctypes.Structure):\n            _fields_=[(\'type\',ctypes.c_uint32),(\'payload\',Payload)]\n        self.Input=Input\n        u.SendInput.argtypes=[wintypes.UINT,ctypes.POINTER(Input),ctypes.c_int];u.SendInput.restype=wintypes.UINT\n\n    def text(self, handle, klass=False):\n        buf=ctypes.create_unicode_buffer(512)\n        (self.u.GetClassNameW if klass else self.u.GetWindowTextW)(handle,buf,len(buf))\n        return buf.value\n\n    def verify(self, handle):\n        u=self.u;root=self.target[\'handle\'];pid=wintypes.DWORD()\n        u.GetWindowThreadProcessId(handle,ctypes.byref(pid))\n        if (not u.IsWindow(handle) or pid.value!=self.target[\'pid\'] or u.GetAncestor(handle,2)!=root\n                or u.IsIconic(root) or not u.IsWindowVisible(handle) or not u.IsWindowEnabled(handle)\n                or not u.IsWindowEnabled(root)):\n            raise RuntimeError(\'POP 창 또는 버튼 상태가 달라졌습니다. 최소화·팝업 상태를 확인해 주세요.\')\n\n    def rect(self, handle):\n        r=wintypes.RECT()\n        if not self.u.GetWindowRect(handle,ctypes.byref(r)) or r.right<=r.left or r.bottom<=r.top:\n            raise RuntimeError(\'버튼 위치를 확인하지 못했습니다.\')\n        return r\n\n    def register_query(self, report):\n        p=wintypes.POINT();self.u.GetCursorPos(ctypes.byref(p))\n        handle=int(self.u.WindowFromPoint(p) or 0);self.verify(handle)\n        candidates=[r for r in nodes(report) if r.get(\'handle\')==handle and r.get(\'parent\')==-1 and r.get(\'role\')==43]\n        if len(candidates)!=1:\n            raise RuntimeError(\'조회 버튼 자체 위에 마우스를 올려 등록해 주세요.\')\n        name=candidates[0].get(\'name\',\'\')\n        if any(word in name for word in (\'저장\',\'삭제\',\'완료\',\'닫기\',\'다운\',\'이동\')):\n            raise RuntimeError(\'조회 이외의 동작 버튼은 등록할 수 없습니다.\')\n        r=self.rect(handle)\n        return {\'handle\':handle,\'class\':self.text(handle,True),\'text\':self.text(handle),\n                \'size\':[r.right-r.left,r.bottom-r.top], \'purpose\':\'query\',\n                \'registered_by\':\'사용자가 조회 버튼을 가리키고 F8로 지정\'}\n\n    def activate(self):\n        u=self.u;root=self.target[\'handle\']\n        u.ShowWindowAsync.argtypes=[wintypes.HWND,ctypes.c_int];u.ShowWindowAsync.restype=wintypes.BOOL\n        if u.IsIconic(root):\n            u.ShowWindowAsync(root,9)\n            for _ in range(20):\n                if not u.IsIconic(root):break\n                time.sleep(.05)\n        self.verify(root)\n        u.SetForegroundWindow(root)\n        for _ in range(20):\n            if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped(\'F9 중지\')\n            if u.GetForegroundWindow()==root:return\n            time.sleep(.05)\n        raise RuntimeError(\'Windows가 대상 창을 앞으로 가져오지 못했습니다. MES·POP와 지후니우스를 같은 권한으로 실행하고 다시 시작해 주세요.\')\n\n    def click_handle(self, handle, static=False, selection=None, allowed_foreground=None):\n        self.verify(handle);u=self.u;root=self.target[\'handle\']\n        if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped(\'F9 중지\')\n        if u.GetForegroundWindow() not in (allowed_foreground or {root}):\n            raise RuntimeError(\'POP 이외의 창이 앞에 있어 중단했습니다.\')\n        if any(u.GetAsyncKeyState(k)&0x8000 for k in (1,2,16,17,18,91,92)):\n            raise RuntimeError(\'마우스 버튼 또는 보조 키가 눌려 있어 중단했습니다.\')\n        r=self.rect(handle);x=(r.left+r.right)//2;y=(r.top+r.bottom)//2\n        if selection is not None:\n            gb,cb=selection\n            if any(abs(a-b)>3 for a,b in zip(gb,[r.left,r.top,r.right-r.left,r.bottom-r.top])):\n                raise RuntimeError(\'표 위치가 바뀌어 체크를 중단했습니다.\')\n            x=round(cb[0]+cb[2]/2);y=round(cb[1]+cb[3]/2)\n            if cb[2]<=0 or cb[3]<=0 or not (r.left<=cb[0] and cb[0]+cb[2]<=r.right and r.top<=cb[1] and cb[1]+cb[3]<=r.bottom):\n                raise RuntimeError(\'체크 칸이 표 안에 완전히 보이지 않습니다.\')\n        hit=u.WindowFromPoint(wintypes.POINT(x,y))\n        allowed=hit==handle or (static and hit==u.GetParent(handle))\n        if not allowed:\n            raise RuntimeError(\'버튼이 다른 창에 가려져 있어 중단했습니다.\')\n        left=u.GetSystemMetrics(76);top=u.GetSystemMetrics(77);w=u.GetSystemMetrics(78);h=u.GetSystemMetrics(79)\n        if not(left<=x<left+w and top<=y<top+h) or w<=1 or h<=1:\n            raise RuntimeError(\'버튼이 모니터 표시 범위 밖에 있습니다.\')\n        items=(self.Input*3)()\n        for item in items:item.type=0\n        items[0].payload.mi.dx=round((x-left)*65535/(w-1))\n        items[0].payload.mi.dy=round((y-top)*65535/(h-1))\n        items[0].payload.mi.flags=0x8000|0x4000|0x0001\n        items[1].payload.mi.flags=0x0002;items[2].payload.mi.flags=0x0004\n        if u.SendInput(3,items,ctypes.sizeof(self.Input))!=3:\n            # Release only; never retry a potentially completed click.\n            release=self.Input();release.payload.mi.flags=0x0004\n            u.SendInput(1,ctypes.byref(release),ctypes.sizeof(self.Input))\n            raise RuntimeError(\'Windows가 클릭 입력을 완료하지 못했습니다. 자동 재시도하지 않습니다.\')\n\n    def input_inspection_date(self, field, edit, value, stop):\n        value=iso_date(value);handle=edit[\'handle\'];u=self.u\n        self.verify(field[\'handle\']);self.verify(handle)\n        if u.GetParent(handle)!=field[\'handle\'] or not self.text(handle,True).startswith(\'WindowsForms10.EDIT.\'):\n            raise RuntimeError(\'POP 검사일 입력칸이 달라졌습니다.\')\n        if stop.is_set():raise Stopped(\'사용자 중지\')\n        self.click_handle(handle,selection=(bounds(edit),bounds(edit)))\n        if stop.wait(.05):raise Stopped(\'사용자 중지\')\n        class GUIInfo(ctypes.Structure):\n            _fields_=[(\'size\',ctypes.c_uint32),(\'flags\',ctypes.c_uint32)]+[\n                (name,wintypes.HWND) for name in (\'active\',\'focus\',\'capture\',\'menu\',\'move\',\'caret\')]+[(\'rect\',wintypes.RECT)]\n        u.GetGUIThreadInfo.argtypes=[wintypes.DWORD,ctypes.POINTER(GUIInfo)];u.GetGUIThreadInfo.restype=wintypes.BOOL\n        info=GUIInfo();info.size=ctypes.sizeof(info)\n        if (u.GetForegroundWindow()!=self.target[\'handle\'] or not u.GetGUIThreadInfo(0,ctypes.byref(info))\n                or info.focus!=handle or info.flags & 0x1e):\n            raise RuntimeError(\'POP 검사일 입력칸에 초점이 없어 입력을 중단했습니다.\')\n        if stop.is_set() or u.GetAsyncKeyState(0x78)&0x8000:raise Stopped(\'사용자 중지\')\n        if any(u.GetAsyncKeyState(k)&0x8000 for k in (1,2,16,17,18,91,92)):\n            raise RuntimeError(\'마우스 버튼 또는 보조 키가 눌려 있어 중단했습니다.\')\n        # Select all, type the ISO date, then Tab to commit; never press Enter.\n        events=[(17,0,0),(65,0,0),(65,0,2),(17,0,2)]\n        for char in value:events.extend(((0,ord(char),4),(0,ord(char),6)))\n        events.extend(((9,0,0),(9,0,2)))\n        items=(self.Input*len(events))()\n        for item,(vk,scan,flags) in zip(items,events):\n            item.type=1;item.payload.ki.vk=vk;item.payload.ki.scan=scan;item.payload.ki.flags=flags\n        if u.SendInput(len(items),items,ctypes.sizeof(self.Input))!=len(items):\n            release=(self.Input*3)()\n            for item,key in zip(release,(65,17,9)):\n                item.type=1;item.payload.ki.vk=key;item.payload.ki.flags=2\n            u.SendInput(3,release,ctypes.sizeof(self.Input))\n            raise RuntimeError(\'POP 검사일 입력이 완료되지 않았습니다. 날짜를 확인해 주세요.\')\n\n    def popup_inventory(self):\n        return {w[\'handle\'] for w in visible_windows(include_untitled=True) if w[\'pid\']==self.target[\'pid\']}\n\n    def open_sequence(self,report):\n        field=field_node(report,\'세척순서\',42)\n        buttons=[e for e in nodes(report) if e.get(\'parent\')==field[\'id\'] and e.get(\'role\')==43\n                 and e.get(\'name\')==\'오픈\' and e.get(\'enabled\') and not e.get(\'offscreen\')]\n        if len(buttons)!=1:raise RuntimeError(\'세척순서 펼침 버튼을 확인하지 못했습니다.\')\n        self.click_handle(field[\'handle\'],selection=(bounds(field),bounds(buttons[0])))\n\n    def sequence_popups(self,previous,field_bounds):\n        result=[];fx,fy,fw,fh=field_bounds\n        for w in visible_windows(include_untitled=True):\n            if w[\'pid\']!=self.target[\'pid\'] or w[\'handle\'] in previous:continue\n            r=self.rect(w[\'handle\']);b=[r.left,r.top,r.right-r.left,r.bottom-r.top]\n            # A newly visible window directly above/below the sequence input, same process.\n            overlaps=b[0]<fx+fw and b[0]+b[2]>fx\n            adjacent=min(abs(b[1]-(fy+fh)),abs(b[1]+b[3]-fy))<=max(30,fh)\n            if overlaps and adjacent and b[2]>0 and b[3]>0:\n                w=dict(w);w[\'bounds\']=b;w[\'title\']=w[\'title\'] or \'세척순서 선택 목록\';result.append(w)\n        return result\n\n    def select_sequence_option(self,popup,option):\n        if popup[\'pid\']!=self.target[\'pid\']:raise RuntimeError(\'세척순서 목록의 프로그램이 달라졌습니다.\')\n        self.verify(self.target[\'handle\'])\n        nested=WindowsClicks(popup);nested.verify(option[\'handle\'])\n        r=nested.rect(popup[\'handle\'])\n        if any(abs(a-b)>3 for a,b in zip(popup[\'bounds\'],[r.left,r.top,r.right-r.left,r.bottom-r.top])):\n            raise RuntimeError(\'세척순서 선택 목록이 이동했습니다.\')\n        if (option.get(\'value\') or option.get(\'name\') or \'\').strip()!=pop_sequence():raise RuntimeError(\'설정한 세척순번 이외의 항목은 선택하지 않습니다.\')\n        r=nested.rect(option[\'handle\']);gb=[r.left,r.top,r.right-r.left,r.bottom-r.top]\n        nested.click_handle(option[\'handle\'],selection=(gb,bounds(option)),allowed_foreground={self.target[\'handle\'],popup[\'handle\']})\n\n    def checkbox_click(self, view, key, project):\n        row=view[\'visible\'].get(key)\n        cell=view[\'selection_cells\'].get(key)\n        if not row or row.get(\'프로젝트No\')!=project or row.get(\'선택\')!=\'선택안됨\' or not cell or not cell[\'enabled\']:\n            raise RuntimeError(\'체크할 행이나 현재 선택 상태를 확실히 확인하지 못했습니다.\')\n        self.click_handle(view[\'handle\'],selection=(view[\'grid_bounds\'],cell[\'bounds\']))\n\n    def query_click(self, binding):\n        handle=binding[\'handle\'];self.verify(handle);r=self.rect(handle)\n        if (binding.get(\'purpose\')!=\'query\' or self.text(handle,True)!=binding[\'class\']\n                or self.text(handle)!=binding[\'text\'] or [r.right-r.left,r.bottom-r.top]!=binding[\'size\']):\n            raise RuntimeError(\'등록한 조회 버튼이 바뀌어 중단했습니다.\')\n        self.click_handle(handle)\n\n    def custom_scroll_thumb(self,handle,stop=None):\n        """Recognize the custom WinForms scrollbar observed in POP diagnostics."""\n        u=self.u;grid=self.rect(handle);found=[]\n        callback_type=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)\n        @callback_type\n        def visit(hwnd,_):\n            if (u.GetParent(hwnd)!=handle or not u.IsWindowVisible(hwnd)\n                    or not u.IsWindowEnabled(hwnd) or not self.text(hwnd,True).startswith(\'WindowsForms10.Window.\')):return True\n            r=self.rect(hwnd);w=r.right-r.left;h=r.bottom-r.top\n            if (10<=w<=40 and h>=w*6 and abs(r.right-grid.right)<=3\n                    and grid.top<=r.top and r.bottom<=grid.bottom and h>=(grid.bottom-grid.top)*.5):found.append((hwnd,r))\n            return True\n        u.EnumChildWindows.argtypes=[wintypes.HWND,callback_type,wintypes.LPARAM];u.EnumChildWindows.restype=wintypes.BOOL\n        u.EnumChildWindows(handle,visit,0)\n        if len(found)!=1:raise RuntimeError(\'POP 전용 세로 스크롤바 영역을 구분하지 못했습니다.\')\n        hwnd,r=found[0];self.verify(hwnd)\n        x=(r.left+r.right)//2;w=r.right-r.left\n        if u.GetForegroundWindow()!=self.target[\'handle\']:raise RuntimeError(\'POP 창이 앞에 없습니다.\')\n        for y in (r.top+w,r.bottom-w-1):\n            if u.WindowFromPoint(wintypes.POINT(x,y))!=hwnd:raise RuntimeError(\'POP 스크롤바가 가려져 있습니다.\')\n        u.GetDC.argtypes=[wintypes.HWND];u.GetDC.restype=wintypes.HDC\n        u.ReleaseDC.argtypes=[wintypes.HWND,wintypes.HDC];u.ReleaseDC.restype=ctypes.c_int\n        g=ctypes.WinDLL(\'gdi32\');g.GetPixel.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int];g.GetPixel.restype=wintypes.DWORD\n        # One small screen copy: subsequent GetPixel calls read memory only.\n        g.CreateCompatibleDC.argtypes=[wintypes.HDC];g.CreateCompatibleDC.restype=wintypes.HDC\n        g.CreateCompatibleBitmap.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int];g.CreateCompatibleBitmap.restype=wintypes.HBITMAP\n        g.SelectObject.argtypes=[wintypes.HDC,wintypes.HANDLE];g.SelectObject.restype=wintypes.HANDLE\n        g.BitBlt.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.HDC,ctypes.c_int,ctypes.c_int,wintypes.DWORD];g.BitBlt.restype=wintypes.BOOL\n        g.DeleteObject.argtypes=[wintypes.HANDLE];g.DeleteObject.restype=wintypes.BOOL\n        g.DeleteDC.argtypes=[wintypes.HDC];g.DeleteDC.restype=wintypes.BOOL\n        dc=u.GetDC(None);memory=None;bitmap=None;old=None\n        if not dc:raise RuntimeError(\'스크롤바 색상을 읽지 못했습니다.\')\n        try:\n            memory=g.CreateCompatibleDC(dc);bitmap=g.CreateCompatibleBitmap(dc,w,r.bottom-r.top)\n            if not memory or not bitmap:raise RuntimeError(\'스크롤바 화면 버퍼 생성 실패\')\n            old=g.SelectObject(memory,bitmap)\n            if not old or old==ctypes.c_void_p(-1).value:raise RuntimeError(\'스크롤바 화면 버퍼 선택 실패\')\n            for attempt in range(2):\n                if (stop is not None and stop.is_set()) or u.GetAsyncKeyState(0x78)&0x8000:raise Stopped(\'사용자 중지\')\n                self.verify(hwnd)\n                current=self.rect(hwnd)\n                if (current.left,current.top,current.right,current.bottom)!=(r.left,r.top,r.right,r.bottom):\n                    raise RuntimeError(\'POP 스크롤바 위치가 바뀌었습니다.\')\n                if u.GetForegroundWindow()!=self.target[\'handle\']:raise RuntimeError(\'POP 창이 앞에 없습니다.\')\n                for y in (r.top+w,r.bottom-w-1):\n                    if u.WindowFromPoint(wintypes.POINT(x,y))!=hwnd:raise RuntimeError(\'POP 스크롤바가 가려져 있습니다.\')\n                if not g.BitBlt(memory,0,0,w,r.bottom-r.top,dc,r.left,r.top,0x00CC0020):raise RuntimeError(\'스크롤바 화면 읽기 실패\')\n                columns=[[],[],[]]\n                for y in range(w,r.bottom-r.top-w):\n                    if y%32==0 and ((stop is not None and stop.is_set()) or u.GetAsyncKeyState(0x78)&0x8000):raise Stopped(\'사용자 중지\')\n                    for column,xx in zip(columns,(w//3,w//2,w-1-w//3)):\n                        color=g.GetPixel(memory,xx,y)\n                        if color==0xffffffff:raise RuntimeError(\'스크롤바 색상 읽기 실패\')\n                        column.append((color&255,(color>>8)&255,(color>>16)&255))\n                try:\n                    start,end=custom_thumb_columns(columns)\n                except RuntimeError:\n                    if attempt:raise\n                    # Retry only an uncertain paint, without another MSAA read or click.\n                    if stop is not None:\n                        if stop.wait(.06):raise Stopped(\'사용자 중지\')\n                    else:time.sleep(.06)\n                    continue\n                return hwnd,r,w,w+start,w+end\n        finally:\n            if old and old!=ctypes.c_void_p(-1).value:g.SelectObject(memory,old)\n            if bitmap:g.DeleteObject(bitmap)\n            if memory:g.DeleteDC(memory)\n            u.ReleaseDC(None,dc)\n\n    def scroll_result_grid(self,view,direction,stop):\n        """Drag the actual vertical scrollbar thumb; never send a wheel event."""\n        if direction not in (-1,1):raise ValueError(\'스크롤 방향 오류\')\n        handle=view[\'handle\'];self.verify(handle);u=self.u\n        class ScrollInfo(ctypes.Structure):\n            _fields_=[(\'size\',wintypes.DWORD),(\'rect\',wintypes.RECT),\n                      (\'button\',ctypes.c_int),(\'thumb_top\',ctypes.c_int),\n                      (\'thumb_bottom\',ctypes.c_int),(\'reserved\',ctypes.c_int),\n                      (\'states\',wintypes.DWORD*6)]\n        u.GetScrollBarInfo.argtypes=[wintypes.HWND,ctypes.c_long,ctypes.POINTER(ScrollInfo)]\n        u.GetScrollBarInfo.restype=wintypes.BOOL\n        grid=self.rect(handle);candidates=[]\n        def inspect(hwnd,object_id):\n            info=ScrollInfo();info.size=ctypes.sizeof(info)\n            if not u.GetScrollBarInfo(hwnd,object_id,ctypes.byref(info)):return\n            r=info.rect\n            if info.states[0] & (1|0x8000|0x10000):return\n            if not (0<r.right-r.left<r.bottom-r.top and grid.left<=r.left<r.right<=grid.right+3\n                    and grid.top<=r.top<r.bottom<=grid.bottom+3):return\n            if not (info.button<=info.thumb_top<info.thumb_bottom<=r.bottom-r.top-info.button):return\n            candidates.append((hwnd,info))\n        inspect(handle,-5) # OBJID_VSCROLL: native non-client scrollbar\n        if not candidates:\n            callback_type=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)\n            @callback_type\n            def child(hwnd,_):\n                if \'scrollbar\' in self.text(hwnd,True).lower() and u.IsWindowVisible(hwnd):inspect(hwnd,-4)\n                return True\n            u.EnumChildWindows.argtypes=[wintypes.HWND,callback_type,wintypes.LPARAM]\n            u.EnumChildWindows.restype=wintypes.BOOL\n            u.EnumChildWindows(handle,child,0)\n        unique={(v.rect.left,v.rect.top,v.rect.right,v.rect.bottom):(h,v) for h,v in candidates}\n        if len(unique)!=1:\n            if set(view[\'visible\'])==set(view[\'keys\']):return\n            hwnd,r,button,thumb_top,thumb_bottom=self.custom_scroll_thumb(handle,stop)\n            info=ScrollInfo();info.rect=r;info.button=button;info.thumb_top=thumb_top;info.thumb_bottom=thumb_bottom\n        else:hwnd,info=next(iter(unique.values()))\n        self.verify(hwnd)\n        r=info.rect;x=(r.left+r.right)//2\n        thumb=info.thumb_bottom-info.thumb_top\n        travel=r.bottom-r.top-2*info.button-thumb\n        start=r.top+(info.thumb_top+info.thumb_bottom)//2\n        minimum=r.top+info.button+thumb//2\n        maximum=minimum+travel\n        if travel<=0:return\n        if direction==1:end=minimum\n        else:\n            # Overlap pages so every row can be observed before moving further.\n            visible=max(1,len(view[\'visible\']));total=len(view[\'keys\'])\n            step=max(1,int(travel*max(1,visible-2)/max(1,total-visible)))\n            end=min(maximum,start+step)\n        if end==start:return\n        left=u.GetSystemMetrics(76);top=u.GetSystemMetrics(77)\n        width=u.GetSystemMetrics(78);height=u.GetSystemMetrics(79)\n        def guard():\n            if stop.is_set() or u.GetAsyncKeyState(0x78)&0x8000:raise Stopped(\'사용자 중지\')\n            self.verify(hwnd)\n            if u.GetForegroundWindow()!=self.target[\'handle\']:raise RuntimeError(\'POP 창이 앞에 없어 스크롤을 중단했습니다.\')\n        def send(flags,y=None):\n            event=self.Input();event.payload.mi.flags=flags\n            if y is not None:\n                if width<=1 or height<=1 or not(left<=x<left+width and top<=y<top+height):raise RuntimeError(\'스크롤바가 모니터 밖에 있습니다.\')\n                event.payload.mi.dx=round((x-left)*65535/(width-1));event.payload.mi.dy=round((y-top)*65535/(height-1))\n            if u.SendInput(1,ctypes.byref(event),ctypes.sizeof(self.Input))!=1:raise RuntimeError(\'Windows가 스크롤바 드래그 입력을 완료하지 못했습니다.\')\n        guard()\n        if any(u.GetAsyncKeyState(k)&0x8000 for k in (1,2,16,17,18,91,92)):raise RuntimeError(\'키 또는 마우스 버튼이 눌려 있습니다.\')\n        for y in (start,end):\n            hit=u.WindowFromPoint(wintypes.POINT(x,y));visited=set()\n            while hit and hit not in visited and hit!=handle:\n                visited.add(hit);hit=u.GetParent(hit)\n            if hit!=handle:raise RuntimeError(\'POP 스크롤바가 다른 창에 가려져 있습니다.\')\n        send(0x8000|0x4000|1,start)\n        try:\n            send(2)\n            if stop.wait(.03):raise Stopped(\'사용자 중지\')\n            for i in range(1,4):\n                guard();send(0x8000|0x4000|1,round(start+(end-start)*i/3))\n                if stop.wait(.02):raise Stopped(\'사용자 중지\')\n        finally:\n            send(4) # Always release, including F9 or partial input failure.\n\n\n    def scroll_grid(self,handle,direction,allowed_foreground=None):\n        if direction not in (-1,1):raise ValueError(\'스크롤 방향 오류\')\n        self.verify(handle);u=self.u\n        if u.GetAsyncKeyState(0x78)&0x8000:raise Stopped(\'F9 중지\')\n        if u.GetForegroundWindow() not in (allowed_foreground or {self.target[\'handle\']}):\n            raise RuntimeError(\'POP 창이 앞에 있지 않아 스크롤을 중단했습니다.\')\n        if any(u.GetAsyncKeyState(k)&0x8000 for k in (1,2,16,17,18,91,92)):\n            raise RuntimeError(\'키 또는 마우스 버튼이 눌려 있어 스크롤을 중단했습니다.\')\n        r=self.rect(handle);x=(r.left+r.right)//2;y=(r.top+r.bottom)//2\n        hit=u.WindowFromPoint(wintypes.POINT(x,y));ancestors=set()\n        while hit and hit not in ancestors and hit!=handle:\n            ancestors.add(hit);hit=u.GetParent(hit)\n        if hit!=handle:raise RuntimeError(\'표가 다른 창에 가려져 있어 스크롤을 중단했습니다.\')\n        left=u.GetSystemMetrics(76);top=u.GetSystemMetrics(77);w=u.GetSystemMetrics(78);h=u.GetSystemMetrics(79)\n        if w<=1 or h<=1 or not(left<=x<left+w and top<=y<top+h):raise RuntimeError(\'표가 모니터 밖에 있습니다.\')\n        items=(self.Input*2)()\n        items[0].payload.mi.dx=round((x-left)*65535/(w-1));items[0].payload.mi.dy=round((y-top)*65535/(h-1))\n        items[0].payload.mi.flags=0x8000|0x4000|1\n        items[1].payload.mi.flags=0x0800;items[1].payload.mi.data=(direction*120)&0xffffffff\n        if u.SendInput(2,items,ctypes.sizeof(self.Input))!=2:\n            raise RuntimeError(\'Windows가 스크롤 입력을 완료하지 못했습니다.\')\n\n\ndef custom_thumb_color(rgb):\n    # Accept light/dark neutral thumb states, still separate from the light track.\n    return max(rgb)-min(rgb)<=8 and 64<=sum(rgb)/3<=228\n\ndef custom_thumb_columns(columns):\n    """Require two interior scan lines to agree; a center grip is not a second thumb."""\n    if len(columns)!=3 or not columns[0] or len({len(c) for c in columns})!=1:\n        raise RuntimeError(\'POP 스크롤바 표본이 올바르지 않습니다.\')\n    values=[]\n    for samples in zip(*columns):\n        thumb=[c for c in samples if custom_thumb_color(c)]\n        track=[c for c in samples if min(c)>=230 and max(c)-min(c)<=8]\n        if len(thumb)>=2:values.append(thumb[0])\n        elif len(track)>=2:values.append(track[0])\n        else:raise RuntimeError(\'POP 스크롤 손잡이와 배경을 구분하지 못했습니다.\')\n    return custom_thumb_span(values)\n\ndef custom_thumb_span(values):\n    spans=[];start=None\n    for i,rgb in enumerate(values+[(255,255,255)]):\n        if custom_thumb_color(rgb):\n            if start is None:start=i\n        elif start is not None:\n            if i-start>=8:spans.append((start,i))\n            start=None\n    if len(spans)!=1:raise RuntimeError(\'POP 회색 스크롤 손잡이를 하나로 구분하지 못했습니다.\')\n    start,end=spans[0]\n    outside=values[:start]+values[end:]\n    if outside and sum(min(c)>=230 and max(c)-min(c)<=8 for c in outside)<len(outside)*.95:\n        raise RuntimeError(\'POP 스크롤바 배경 색상이 예상과 다릅니다.\')\n    return start,end\n\n# No positional column assumptions: map visible cells by header geometry.\ndef bounds(node):\n    b=node.get(\'bounds\') or [0,0,0,0]\n    return b if len(b)==4 else [0,0,0,0]\n\n\ndef pop_grid(report):\n    check_capture(report)\n    children=defaultdict(list)\n    for e in nodes(report):children[e[\'parent\']].append(e)\n    found=[]\n    for table in nodes(report):\n        if table.get(\'role\')!=24:continue\n        headers=[h for group in children[table[\'id\']] for h in children[group[\'id\']] if h.get(\'role\')==25]\n        if not {\'프로젝트No\',\'선택\'}.issubset({h.get(\'name\') for h in headers}):continue\n        panels=[p for p in children[table[\'id\']] if p.get(\'name\')==\'데이터 패널\']\n        if len(panels)!=1:raise RuntimeError(\'POP 데이터 패널을 구분할 수 없습니다.\')\n        panel=panels[0];rows=[r for r in children[panel[\'id\']] if r.get(\'role\')==28]\n        if len(rows)!=panel.get(\'child_count\'):raise RuntimeError(\'POP 일부 행이 누락되었습니다.\')\n        found.append((table,headers,rows,children))\n    if len(found)!=1:raise RuntimeError(\'POP 프로젝트 표를 하나로 구분하지 못했습니다.\')\n    table,headers,rows,children=found[0]\n    b=bounds(table)\n    if b[2]<=0 or b[3]<=0:raise RuntimeError(\'POP 표의 위치를 읽지 못했습니다. 창을 복원해 주세요.\')\n    return table,headers,rows,children\n\n\ndef pop_view(report, map_visible=True, baseline_raw=None):\n    table,headers,rows,children=pop_grid(report)\n    b=bounds(table);bottom=max((bounds(h)[1]+bounds(h)[3] for h in headers if bounds(h)[3]>0),default=b[1])\n    keys=[];raw=[];visible={};selection_cells={};fast_supported=True\n    wanted=(\'선택\',\'프로젝트No\',\'설비명\',\'지시일\')\n    for i,row in enumerate(rows,1):\n        match=re.fullmatch(r\'(?:행|Row)\\s*(\\d+)\',row.get(\'name\',\'\').strip(),re.I)\n        if not match or int(match.group(1))!=i:raise RuntimeError(\'POP 행 번호가 연속되지 않아 전체 범위를 확인할 수 없습니다.\')\n        key=str(i);keys.append(key)\n        cells=[c for c in children[row[\'id\']] if c.get(\'role\')==29]\n        if row.get(\'cells_omitted\'):\n            if (baseline_raw is None or i>len(baseline_raw) or cells\n                    or row.get(\'child_count\')!=len(baseline_raw[i-1])\n                    or row.get(\'value\')!=\';\'.join(baseline_raw[i-1])+\';\'):\n                raise RuntimeError(\'POP 화면 밖 행의 값이 바뀌었거나 요약값을 확인하지 못했습니다.\')\n            values=list(baseline_raw[i-1])\n        else:\n            if len(cells)!=row.get(\'child_count\'):raise RuntimeError(\'POP 행의 일부 셀이 누락되었습니다.\')\n            values=[c.get(\'value\',\'\') for c in cells]\n        summary_ok=(row.get(\'value\')==\';\'.join(values)+\';\' and \'[truncated]\' not in row.get(\'value\',\'\'))\n        fast_supported=fast_supported and summary_ok\n        if baseline_raw is not None and not summary_ok:raise RuntimeError(\'POP 행 요약값과 셀 값이 일치하지 않습니다.\')\n        raw.append(values)\n        rb=bounds(row)\n        if row.get(\'offscreen\') or rb[2]<=0 or rb[3]<=0 or rb[1]<bottom or rb[1]+rb[3]>b[1]+b[3]:continue\n        if not map_visible:continue\n        mapped={}\n        for name in wanted:\n            hs=[h for h in headers if h.get(\'name\')==name and bounds(h)[2]>0 and bounds(h)[3]>0]\n            if len(hs)!=1:raise RuntimeError(\'POP \'+name+\' 열이 보이지 않거나 중복됩니다. 가로 스크롤을 왼쪽으로 맞춰 주세요.\')\n            hb=bounds(hs[0]);cs=[]\n            for c in cells:\n                cb=bounds(c)\n                if (not c.get(\'offscreen\') and cb[2]>0 and cb[3]>0 and abs(cb[0]-hb[0])<=3\n                        and abs(cb[2]-hb[2])<=3 and cb[1]>=rb[1]-2 and cb[1]+cb[3]<=rb[1]+rb[3]+2):cs.append(c)\n            if len(cs)!=1:raise RuntimeError(\'POP \'+name+\' 셀 위치를 확실히 구분하지 못했습니다. 화면을 확인해 주세요.\')\n            cell=cs[0];cn=cell.get(\'name\',\'\').strip()\n            if cn and not (cn==name or re.match(re.escape(name)+r\'\\s+(?:row|행)\\s*\\d+\',cn,re.I)):\n                raise RuntimeError(\'POP 열 이름과 셀 위치가 일치하지 않습니다: \'+name)\n            mapped[name]=cell.get(\'value\',\'\').strip()\n            if name==\'선택\':\n                selection_cells[key]={\'index\':cells.index(cell),\'bounds\':bounds(cell),\n                                      \'enabled\':bool(cell.get(\'enabled\') and cell.get(\'state_known\'))}\n        visible[key]=mapped\n    return {\'handle\':table[\'handle\'],\'grid_bounds\':b,\'keys\':keys,\'raw\':raw,\'visible\':visible,\'selection_cells\':selection_cells,\'fast_supported\':fast_supported}\n\n\ndef field_node(report,label,role):\n    # Link a visible label to the nearest native input on its right, on the same line.\n    elements=nodes(report);found={}\n    for lab in elements:\n        if lab.get(\'role\')!=41 or lab.get(\'name\')!=label:continue\n        lb=bounds(lab)\n        if lb[2]<=0 or lb[3]<=0:continue\n        choices=[]\n        for e in elements:\n            if e.get(\'parent\')!=-1 or e.get(\'role\')!=role or e.get(\'offscreen\'):continue\n            eb=bounds(e);gap=eb[0]-(lb[0]+lb[2])\n            if eb[2]>0 and eb[3]>0 and 0<=gap<=lb[3] and abs(eb[1]+eb[3]/2-lb[1]-lb[3]/2)<=lb[3]/3:\n                choices.append((gap,e))\n        if choices:\n            choices.sort(key=lambda x:x[0]);e=choices[0][1];found[e[\'handle\']]=e\n    if len(found)!=1:raise RuntimeError(label+\' 입력칸을 확실히 읽지 못했습니다.\')\n    return next(iter(found.values()))\n\n\ndef iso_date(value):\n    m=re.search(r\'(\\d{4})\\s*(?:년|[-/.])\\s*(\\d{1,2})\\s*(?:월|[-/.])\\s*(\\d{1,2})\',value)\n    if not m:raise ValueError(\'날짜는 YYYY-MM-DD 형식으로 입력해 주세요.\')\n    return datetime(*map(int,m.groups())).strftime(\'%Y-%m-%d\')\n\n\ndef inspection_screen_ready(report,api):\n    check_capture(report)\n    titles=[n for n in nodes(report) if n.get(\'role\')==10\n            and n.get(\'name\',\'\').strip()==\'공정검사(커스텀)\' and api.u.IsWindowVisible(n[\'handle\'])]\n    if len({n[\'handle\'] for n in titles})!=1:return False\n    try:\n        fields=[field_node(report,label,role) for label,role in\n                ((\'검사일\',47),(\'작업자\',42),(\'세척순서\',42),(\'프로젝트No\',42))]\n    except RuntimeError:return False\n    return all(api.u.IsWindowVisible(n[\'handle\']) and api.u.IsWindowEnabled(n[\'handle\']) for n in fields)\n\n\ndef inspection_menu_button(report,api):\n    check_capture(report)\n    native={n[\'handle\']:n for n in report[\'records\'] if n.get(\'kind\')==\'native_window\'}\n    def usable(n):\n        return (n.get(\'parent\')==-1 and n.get(\'state_known\') and n.get(\'enabled\')\n                and not n.get(\'offscreen\') and api.u.IsWindowVisible(n[\'handle\']))\n    found={}\n    for label in nodes(report):\n        if label.get(\'name\',\'\').strip()!=\'공정검사(커스텀)\' or not usable(label):continue\n        if label.get(\'role\')==43:\n            found[label[\'handle\']]=label;continue\n        if label.get(\'role\')!=41:continue\n        lb=bounds(label);parent=native.get(label[\'handle\'],{}).get(\'native_parent\')\n        if not parent or lb[2]<=0 or lb[3]<=0:continue\n        for button in nodes(report):\n            if button.get(\'role\')!=43 or not usable(button):continue\n            if button.get(\'name\',\'\').strip() not in (\'\',\'공정검사(커스텀)\'):continue\n            if native.get(button[\'handle\'],{}).get(\'native_parent\')!=parent:continue\n            b=bounds(button);gap=lb[1]-(b[1]+b[3])\n            # The supplied main menu has a square icon immediately above its label.\n            if (b[2]>40 and b[3]>40 and 0<=gap<=max(30,lb[3])\n                    and abs(b[0]+b[2]/2-lb[0]-lb[2]/2)<=lb[3]/2\n                    and .6*lb[2]<=b[2]<=1.5*lb[2] and .65*b[2]<=b[3]<=1.5*b[2]):\n                found[button[\'handle\']]=button\n    if len(found)!=1:raise RuntimeError(\'POP 공정검사(커스텀) 메뉴를 하나로 찾지 못했습니다. POP 메인 메뉴를 열어 주세요.\')\n    return next(iter(found.values()))\n\n\ndef ensure_inspection_screen(target,api,capture,stop,emit,initial_report):\n    if stop.is_set():raise Stopped(\'사용자 중지\')\n    # Reuse the existing initial POP capture: no extra capture or wait when ready.\n    if inspection_screen_ready(initial_report,api):return initial_report\n    button=inspection_menu_button(initial_report,api)\n    if stop.is_set():raise Stopped(\'사용자 중지\')\n    api.click_handle(button[\'handle\'],selection=(bounds(button),bounds(button)))\n    emit(\'log\',\'POP 공정검사(커스텀) 메뉴 클릭 · 화면 전환 확인 중\')\n    deadline=time.monotonic()+8\n    for _ in range(8):\n        if stop.wait(.2):raise Stopped(\'사용자 중지\')\n        report=capture({**target,\'mode\':\'mes_rows\'},\'POP 공정검사 화면 전환 확인\',stop)\n        if inspection_screen_ready(report,api):\n            emit(\'log\',\'POP 공정검사(커스텀) 화면 확인 완료\')\n            return report\n        if time.monotonic()>=deadline:break\n    raise RuntimeError(\'POP 공정검사(커스텀) 화면 전환을 확인하지 못했습니다. 추가 클릭 없이 중단했습니다.\')\n\n\ndef read_conditions(report):\n    check_capture(report)\n    return {\'date\':iso_date(field_node(report,\'검사일\',47).get(\'value\',\'\')),\n            \'worker\':field_node(report,\'작업자\',42).get(\'value\',\'\').strip(),\n            \'sequence\':field_node(report,\'세척순서\',42).get(\'value\',\'\').strip(),\n            \'project_filter\':field_node(report,\'프로젝트No\',42).get(\'value\',\'\').strip()}\n\n\ndef inspection_date_edit(report):\n    field=field_node(report,\'검사일\',47);fb=bounds(field)\n    handles={r[\'handle\'] for r in report[\'records\'] if r.get(\'kind\')==\'native_window\'\n             and r.get(\'native_parent\')==field[\'handle\'] and r.get(\'class\',\'\').startswith(\'WindowsForms10.EDIT.\')}\n    matches=[]\n    for n in nodes(report):\n        b=bounds(n)\n        if (n.get(\'handle\') in handles and n.get(\'parent\')==-1 and n.get(\'role\') in (42,47)\n                and n.get(\'enabled\') and n.get(\'state_known\') and not n.get(\'offscreen\')\n                and b[2]>0 and b[3]>0 and fb[0]<=b[0] and fb[1]<=b[1]\n                and b[0]+b[2]<=fb[0]+fb[2] and b[1]+b[3]<=fb[1]+fb[3]):matches.append(n)\n    if len(matches)!=1:raise RuntimeError(\'POP 검사일의 날짜 입력칸을 구분하지 못했습니다.\')\n    return field,matches[0]\n\n\ndef ensure_inspection_date(target,value,api,capture,stop,emit,initial_report):\n    value=iso_date(value);before=read_conditions(initial_report)\n    if stop.is_set():raise Stopped(\'사용자 중지\')\n    if before[\'project_filter\']:raise RuntimeError(\'POP 프로젝트No 검색칸을 비워 전체 목록을 조회해 주세요.\')\n    if before[\'date\']==value:return initial_report\n    field,edit=inspection_date_edit(initial_report)\n    api.input_inspection_date(field,edit,value,stop)\n    for attempt in range(2):\n        if stop.wait(.15 if attempt==0 else .2):raise Stopped(\'사용자 중지\')\n        after=capture({**target,\'mode\':\'mes_rows\'},\'POP 검사일 변경 확인\',stop)\n        actual=read_conditions(after)\n        if any(actual[key]!=before[key] for key in (\'worker\',\'sequence\',\'project_filter\')):\n            raise RuntimeError(\'검사일 입력 중 다른 POP 조건이 바뀌어 중단했습니다.\')\n        if actual[\'date\']==value:\n            emit(\'log\',f"POP 검사일 변경 확인: {before[\'date\']} → {value}")\n            return after\n    raise RuntimeError(f"POP 검사일 반영 불일치: 요청 [{value}] / 화면 [{actual[\'date\']}]. 조회 전에 중단했습니다.")\n\n\ndef validate_conditions(report,expected,check_sequence=True):\n    actual=read_conditions(report)\n    for key,label in [(\'date\',\'POP 검사일\'),(\'worker\',\'작업자\'),(\'sequence\',\'세척순서\')]:\n        if key==\'sequence\' and not check_sequence:continue\n        wanted=pop_sequence(expected[key]) if key==\'sequence\' else expected[key]\n        if actual[key]!=wanted:raise RuntimeError(f"{label} 불일치: 화면 [{actual[key] or \'빈칸\'}] / 검사 설정 [{wanted}]. POP에서 맞춰 주세요.")\n    if actual[\'project_filter\']:raise RuntimeError(\'POP 프로젝트No 검색칸을 비워 전체 목록을 조회해 주세요.\')\n    return actual\n\n\ndef validate_query(report,binding):\n    table,_,_,_=pop_grid(report)\n    field=field_node(report,\'프로젝트No\',42);fb=bounds(field)\n    candidates=[e for e in nodes(report) if e.get(\'parent\')==-1 and e.get(\'handle\')==binding[\'handle\'] and e.get(\'role\')==43]\n    if len(candidates)!=1:raise RuntimeError(\'등록한 POP 조회 버튼을 다시 확인할 수 없습니다.\')\n    e=candidates[0];b=bounds(e)\n    if (e.get(\'offscreen\') or not e.get(\'enabled\') or b[2]<=0 or b[3]<=0\n            or not 0<=b[0]-fb[0]-fb[2]<=fb[3]*2\n            or abs(b[1]+b[3]/2-fb[1]-fb[3]/2)>fb[3]/2\n            or b[1]+b[3]>bounds(table)[1]):\n        raise RuntimeError(\'프로젝트No 검색칸 오른쪽의 조회 버튼만 지정할 수 있습니다.\')\n\n\ndef load_mes(path):\n    with zipfile.ZipFile(path) as z:\n        info=z.getinfo(\'MES_cycle.json\')\n        if info.file_size>20_000_000:raise ValueError(\'MES 결과 파일이 너무 큽니다.\')\n        data=json.loads(z.read(info))\n    steps=data.get(\'steps\',[])\n    requested=data.get(\'selected_numbers\') if data.get(\'version\')==3 else list(range(1,11))\n    if (data.get(\'version\') not in (2,3) or not isinstance(requested,list) or not requested\n            or any(type(n) is not int or not 1<=n<=10 for n in requested)\n            or requested!=sorted(set(requested)) or [s.get(\'number\') for s in steps]!=requested):\n        raise ValueError(\'선택한 호기의 검사가 모두 끝나지 않은 MES 결과입니다.\')\n    group=data.get(\'context\',{}).get(\'group\',{})\n    if group.get(\'label\')!=\'위쪽 왼쪽의 1~10 버튼\':raise ValueError(\'왼쪽 위 1~10 검사 결과만 사용할 수 있습니다.\')\n    candidates=[];skipped_blank_program=[];dates=set()\n    for step in steps:\n        cov=step.get(\'scroll_coverage\',{});rows=step.get(\'data\',{}).get(\'rows\',[])\n        verified=(cov.get(\'all_rows_verified\') is True and cov.get(\'snapshot_checks\')==2) if cov.get(\'method\')==\'direct_rows\' else all(cov.get(k) for k in (\'top_verified\',\'bottom_verified\'))\n        if not step.get(\'stable\') or not cov.get(\'complete\') or not verified or cov.get(\'seen_rows\')!=len(rows) or cov.get(\'declared_rows\')!=len(rows):\n            raise ValueError(\'MES 전체 행 검사가 끝나지 않은 결과입니다.\')\n        dates.update(step[\'data\'].get(\'dates\',[]))\n        for row_position,row in enumerate(rows,1):\n            if normalize_sequence(row.get(\'세척\',\'\'))==SEQUENCE:\n                number=(row.get(\'P/No.\') or \'\').strip()\n                if not number:\n                    skipped_blank_program.append({\'number\':step[\'number\'],\'row\':row.get(\'No.\',\'\'),\n                                                  \'row_position\':row_position,\'sequence\':SEQUENCE})\n                    continue\n                candidates.append({\'project\':number,\'number\':step[\'number\'],\'row\':row.get(\'No.\',\'\'),\n                                   \'equipment\':[f"CNC 자동선반 {step[\'number\']}호기"],\n                                   \'equipment_basis\':\'왼쪽 위에서 실제 선택한 1~10 호기 버튼\',\n                                   \'panel_equipment_label\':step[\'data\'].get(\'equipment_names\',[]),\'dates\':step[\'data\'].get(\'dates\',[])})\n    return {\'filename\':Path(path).name,\'candidates\':candidates,\'skipped_blank_program\':skipped_blank_program,\'dates\':sorted(dates),\'scope\':group[\'label\'],\'sequence\':SEQUENCE,\'selected_numbers\':requested}\n\n\ndef match_rows(source,rows):\n    # Exact P/No strings only; never convert letter O to digit 0 or drop leading zeroes.\n    a=defaultdict(list);b=defaultdict(list)\n    for r in source[\'candidates\']:a[r[\'project\']].append(r)\n    for ordinal,r in rows.items():b[r[\'프로젝트No\']].append({\'row\':ordinal,**r})\n    result={\'matched\':[],\'missing\':[],\'ambiguous\':[],\'equipment_mismatch\':[],\'already_selected\':[]}\n    for project,mes in sorted(a.items()):\n        pop=b.get(project,[])\n        if len(mes)!=1 or len(pop)>1:result[\'ambiguous\'].append({\'project\':project,\'mes\':mes,\'pop\':pop});continue\n        if not pop:result[\'missing\'].append(project);continue\n        pair={\'project\':project,\'mes\':mes[0],\'pop\':pop[0]}\n        if not mes[0][\'equipment\'] or pop[0][\'설비명\'] not in mes[0][\'equipment\']:\n            result[\'equipment_mismatch\'].append(pair);continue\n        if pop[0][\'선택\']!=\'선택안됨\':result[\'already_selected\'].append(pair);continue\n        result[\'matched\'].append(pair)\n    result[\'note\']=\'번호와 설비명의 대조 결과입니다. POP 지시일은 MES 생산일·POP 날짜와 동일하다고 가정하지 않습니다. 체크 전 대조 결과이며 저장·완료는 수행하지 않습니다.\'\n    return result\n\n\ndef match_requested(rows):\n    """User-requested checkbox-only test, independent of MES source files."""\n    result={\'matched\':[],\'missing\':[],\'ambiguous\':[],\'equipment_mismatch\':[],\'already_selected\':[]}\n    for project in (\'O2026\',\'O2027\',\'O2028\'):\n        candidates=[{\'row\':key,**row} for key,row in rows.items() if row.get(\'프로젝트No\')==project]\n        if not candidates:result[\'missing\'].append(project);continue\n        if len(candidates)!=1:\n            result[\'ambiguous\'].append({\'project\':project,\'pop\':candidates});continue\n        pair={\'project\':project,\'pop\':candidates[0],\'basis\':\'사용자가 직접 지정한 체크 시험 번호\'}\n        if candidates[0][\'선택\']!=\'선택안됨\':result[\'already_selected\'].append(pair);continue\n        result[\'matched\'].append(pair)\n    result[\'note\']=\'O2026·O2027·O2028만 직접 지정해 체크하는 시험. MES 결과와 무관. 저장·완료 없음.\'\n    return result\n\n\ndef collect_pop(target,initial,expected,api,capture,stop,emit):\n    """Read all declared rows once, using visible cells to resolve column order."""\n    validate_conditions(initial,expected)\n    view=pop_view(initial);table,headers,rows,children=pop_grid(initial)\n    wanted=(\'선택\',\'프로젝트No\',\'설비명\',\'지시일\');columns={};enabled={};inset=None\n    for key in view[\'visible\']:\n        row=rows[int(key)-1];cells=[c for c in children[row[\'id\']] if c.get(\'role\')==29]\n        for name in wanted:\n            hs=[h for h in headers if h.get(\'name\')==name and bounds(h)[2]>0]\n            if len(hs)!=1:raise RuntimeError(\'POP 열을 구분하지 못했습니다: \'+name)\n            hb=bounds(hs[0])\n            indices=[i for i,c in enumerate(cells) if bounds(c)[2]>0 and abs(bounds(c)[0]-hb[0])<=3 and abs(bounds(c)[2]-hb[2])<=3]\n            if len(indices)!=1 or (name in columns and columns[name]!=indices[0]):raise RuntimeError(\'POP 행마다 열 순서가 달라 중단했습니다.\')\n            columns[name]=indices[0]\n            if name==\'선택\':\n                cb=bounds(cells[indices[0]]);rb=bounds(row)\n                offsets=[cb[0]-hb[0],cb[1]-rb[1],cb[2]-hb[2],cb[3]-rb[3]]\n                if inset is not None and inset!=offsets:raise RuntimeError(\'POP 체크 칸의 행별 위치가 일정하지 않습니다.\')\n                inset=offsets\n    if rows and set(columns)!=set(wanted):raise RuntimeError(\'POP 표에서 열을 확인할 수 있는 행이 보이지 않습니다.\')\n    mapped={};width=len(view[\'raw\'][0]) if rows else 0\n    for key,row,values in zip(view[\'keys\'],rows,view[\'raw\']):\n        cells=[c for c in children[row[\'id\']] if c.get(\'role\')==29]\n        if len(values)!=width or any(i>=len(values) for i in columns.values()):raise RuntimeError(\'POP 일부 행의 열 개수가 다릅니다.\')\n        for name,index in columns.items():\n            cn=cells[index].get(\'name\',\'\').strip()\n            if cn and not (cn==name or re.fullmatch(re.escape(name)+r\'\\s+(?:row|행)\\s*\\d+\',cn,re.I)):\n                raise RuntimeError(\'POP 화면 밖 행의 열 정보가 다릅니다: \'+name)\n        mapped[key]={name:values[index].strip() for name,index in columns.items()}\n        cell=cells[columns[\'선택\']];enabled[key]=bool(cell.get(\'enabled\') and cell.get(\'state_known\'))\n        if key in view[\'visible\'] and mapped[key]!=view[\'visible\'][key]:raise RuntimeError(\'POP 행 매핑이 화면과 일치하지 않습니다.\')\n    emit(\'log\',f\'POP {len(rows)}행 판독 · 맨 위부터 아래까지 확인 예정\')\n    return {\'complete\':not rows,\'declared_rows\':len(rows),\'seen_rows\':len(rows),\'rows\':mapped,\n            \'raw\':view[\'raw\'],\'keys\':view[\'keys\'],\'handle\':view[\'handle\'],\'columns\':columns,\n            \'enabled\':enabled,\'selection_inset\':inset,\'headers\':[h.get(\'name\',\'\') for h in headers],\n            \'row_names\':[r.get(\'name\',\'\') for r in rows], \'summary_supported\':view[\'fast_supported\'],\n            \'current_view\':view,\'wheel_moves\':0,\'basis\':\'MSAA 전체 행과 셀 직접 판독\'}\n\n\ndef pop_batch_view(report,coverage,expected_raw,allowed_changes=()):\n    """Read only the grid; compare every row summary, locate checkbox by geometry."""\n    table,headers,rows,children=pop_grid(report)\n    if (table[\'handle\']!=coverage[\'handle\'] or [h.get(\'name\',\'\') for h in headers]!=coverage[\'headers\']\n            or [r.get(\'name\',\'\') for r in rows]!=coverage[\'row_names\'] or len(rows)!=len(expected_raw)):\n        raise RuntimeError(\'POP 체크 중 표 구조 또는 행 순서가 바뀌었습니다.\')\n    b=bounds(table);columns=coverage[\'columns\'];allowed=set(allowed_changes)\n    checkbox=[h for h in headers if h.get(\'name\')==\'선택\' and bounds(h)[2]>0 and bounds(h)[3]>0]\n    if len(checkbox)!=1:raise RuntimeError(\'POP 선택 열이 보이지 않습니다.\')\n    hb=bounds(checkbox[0]);header_bottom=max((bounds(h)[1]+bounds(h)[3] for h in headers if bounds(h)[3]>0),default=b[1])\n    visible={};cells={};raw=[]\n    for i,(row,expected) in enumerate(zip(rows,expected_raw)):\n        key=str(i+1);proposed=list(expected);proposed[columns[\'선택\']]=\'선택\'\n        if coverage[\'summary_supported\']:\n            value=row.get(\'value\')\n            if value==\';\'.join(expected)+\';\':actual=list(expected)\n            elif key in allowed and value==\';\'.join(proposed)+\';\':actual=proposed\n            else:raise RuntimeError(\'POP 체크 중 예상 외의 행 또는 값이 바뀌었습니다. 추가 클릭을 중단합니다.\')\n        else:\n            cs=[c for c in children[row[\'id\']] if c.get(\'role\')==29]\n            if len(cs)!=row.get(\'child_count\'):raise RuntimeError(\'POP 전체 셀을 확인하지 못했습니다.\')\n            actual=[c.get(\'value\',\'\') for c in cs]\n            if actual!=expected and not(key in allowed and actual==proposed):raise RuntimeError(\'POP 체크 중 예상 외의 값 변경이 감지되었습니다.\')\n        raw.append(actual);rb=bounds(row)\n        if row.get(\'offscreen\') or rb[2]<=0 or rb[3]<=0 or rb[1]<header_bottom or rb[1]+rb[3]>b[1]+b[3]:continue\n        dx,dy,dw,dh=coverage[\'selection_inset\']\n        cb=[hb[0]+dx,rb[1]+dy,hb[2]+dw,rb[3]+dh]\n        if cb[2]<=0 or cb[3]<=0:raise RuntimeError(\'POP 체크 칸의 크기가 올바르지 않습니다.\')\n        if not(b[0]<=cb[0] and cb[0]+cb[2]<=b[0]+b[2]):raise RuntimeError(\'POP 체크 칸이 화면 밖입니다.\')\n        visible[key]={name:actual[index].strip() for name,index in columns.items()}\n        cells[key]={\'index\':columns[\'선택\'],\'bounds\':cb,\n                    \'enabled\':coverage[\'enabled\'][key] and bool(row.get(\'enabled\') and row.get(\'state_known\'))}\n    return {\'handle\':table[\'handle\'],\'grid_bounds\':b,\'keys\':coverage[\'keys\'],\'raw\':raw,\'visible\':visible,\'selection_cells\':cells}\n\n\ndef check_matched(target,expected,coverage,matches,api,capture,stop,emit):\n    """Click a visible page as a batch; verify that batch before moving on."""\n    expected_raw=[list(r) for r in coverage[\'raw\']]\n    targets={str(p[\'pop\'][\'row\']):p[\'project\'] for p in matches}\n    if len(targets)!=len(matches):raise RuntimeError(\'체크 대상 행이 중복됩니다.\')\n    current=coverage[\'current_view\'];pending=set(targets);done=[];moves=0;stalled=0\n    grid_target={\'handle\':coverage[\'handle\'],\'pid\':target.get(\'pid\',0),\'title\':\'POP 결과표\',\n                 \'mode\':\'mes_rows\' if coverage[\'summary_supported\'] else \'pop_full\'}\n    def read(label,allowed=()):\n        if stop.is_set():raise Stopped(\'사용자 중지 — 이미 체크된 행은 그대로 유지됩니다.\')\n        r=capture(grid_target,label,stop);emit(\'capture\',r)\n        return pop_batch_view(r,coverage,expected_raw,allowed)\n    def click(keys,view):\n        for key in keys:\n            if stop.is_set():raise Stopped(\'사용자 중지\')\n            row=view[\'visible\'].get(key)\n            if not row or row[\'프로젝트No\']!=targets[key] or row[\'선택\']!=\'선택안됨\':raise RuntimeError(\'체크할 프로젝트 또는 상태가 달라졌습니다.\')\n            api.checkbox_click(view,key,targets[key])\n            emit(\'check\',{\'row\':key,\'project\':targets[key],\'status\':\'attempt\'})\n            if stop.wait(.04):raise Stopped(\'사용자 중지 — 마지막 클릭 상태를 확인해 주세요.\')\n    def signature(view):\n        return tuple((k,tuple(view[\'selection_cells\'][k][\'bounds\'])) for k in view[\'visible\'])\n    def move(direction,label):\n        nonlocal current,moves\n        if stop.is_set():raise Stopped(\'사용자 중지\')\n        if moves>=max(180,len(coverage[\'keys\'])*3):\n            raise RuntimeError(\'POP 전체 스크롤 확인 한도를 초과했습니다.\')\n        old=signature(current)\n        api.scroll_result_grid(current,direction,stop);moves+=1\n        if stop.wait(.06):raise Stopped(\'사용자 중지\')\n        current=read(label+\' \'+str(moves))\n        if signature(current)==old:\n            # Only a stationary frame needs the longer paint-settle check.\n            if stop.wait(.2):raise Stopped(\'사용자 중지\')\n            current=read(label+\' 반영 재확인\')\n        return signature(current)!=old\n    first=coverage[\'keys\'][0];last=coverage[\'keys\'][-1]\n    emit(\'log\',\'POP 맨 위로 이동 · 첫 행과 스크롤 정지 확인\')\n    while True:\n        changed=move(1,\'POP 맨 위 이동\')\n        if not changed and first in current[\'visible\']:break\n        stalled=0 if changed else stalled+1\n        if stalled>=3:raise RuntimeError(\'POP 맨 위 첫 행을 확인하지 못했습니다. 스크롤을 확인해 주세요.\')\n    coverage[\'top_verified\']=True\n    seen=set();stalled=0\n    emit(\'log\',\'POP 맨 위 확인 · 아래로 내려가며 전체 행 검사\')\n    while True:\n        seen.update(current[\'visible\'])\n        batch=sorted(pending & set(current[\'visible\']),key=int)\n        if batch:\n            emit(\'log\',f\'화면 안 대상 {len(batch)}개 연속 체크\')\n            click(batch,current)\n            if stop.wait(.12):raise Stopped(\'사용자 중지\')\n            current=read(\'POP 화면 단위 체크 확인\',batch)\n            unchanged=[k for k in batch if current[\'raw\'][int(k)-1][coverage[\'columns\'][\'선택\']]==\'선택안됨\']\n            if unchanged:\n                if stop.wait(.2):raise Stopped(\'사용자 중지\')\n                current=read(\'POP 미반영 항목 재확인\',batch)\n                unchanged=[k for k in unchanged if current[\'raw\'][int(k)-1][coverage[\'columns\'][\'선택\']]==\'선택안됨\']\n                if unchanged:\n                    click(unchanged,current)\n                    if stop.wait(.12):raise Stopped(\'사용자 중지\')\n                    current=read(\'POP 추가 클릭 결과 확인\',batch)\n            for key in batch:\n                if current[\'raw\'][int(key)-1][coverage[\'columns\'][\'선택\']]!=\'선택\':raise RuntimeError(\'두 번 이내의 클릭으로 체크되지 않았습니다. 추가 클릭하지 않습니다.\')\n                expected_raw[int(key)-1][coverage[\'columns\'][\'선택\']]=\'선택\'\n                pending.remove(key)\n                event={\'row\':key,\'project\':targets[key],\'status\':\'verified\',\'at\':datetime.now().isoformat(timespec=\'seconds\')}\n                done.append(event);emit(\'check\',event)\n            emit(\'log\',f\'체크 확인 {len(done)}/{len(targets)}개\')\n            stalled=0\n            continue\n        if stop.is_set():raise Stopped(\'사용자 중지\')\n        changed=move(-1,\'POP 아래로 확인\')\n        seen.update(current[\'visible\'])\n        if not changed and last in current[\'visible\']:\n            if pending:\n                raise RuntimeError(\'POP 맨 아래에 도달했지만 체크하지 못한 대상 행이 있습니다: \'+\', \'.join(sorted(pending,key=int)))\n            if seen!=set(coverage[\'keys\']):\n                raise RuntimeError(\'POP 위에서 아래까지 확인하지 못한 행이 있습니다. 완료 처리하지 않습니다.\')\n            coverage.update(bottom_verified=True,complete=True,seen_rows=len(seen),wheel_moves=moves)\n            emit(\'log\',f\'POP 맨 아래 도달 확인 · 전체 {len(seen)}행 검사 · 대상 {len(done)}개 체크 확인\')\n            break\n        stalled=0 if changed else stalled+1\n        if stalled>=3:raise RuntimeError(\'POP 맨 아래에 도달하기 전에 스크롤이 멈췄습니다. 완료 처리하지 않습니다.\')\n    if stop.is_set():raise Stopped(\'사용자 중지\')\n    final=capture({**target,\'mode\':\'pop_final\'},\'체크 검사 최종 상태 확인\',stop);emit(\'capture\',final);validate_conditions(final,expected)\n    final_view=pop_view(final)\n    if final_view[\'handle\']!=coverage[\'handle\'] or final_view[\'keys\']!=coverage[\'keys\'] or final_view[\'raw\']!=expected_raw:\n        raise RuntimeError(\'최종 체크 결과가 예상과 다릅니다. POP 화면을 확인해 주세요.\')\n    coverage[\'final_report\']=final\n    return done\n\n\ndef sequence_column_items(report):\n    """Validate the whole code column, including zero-height offscreen cells.\n\n    DevExpress retains all codes in MSAA, but the last page can contain only\n    29/30 plus tool names. Visibility is required separately before clicking.\n    """\n    check_capture(report)\n    items=[n for n in nodes(report) if n.get(\'role\') in (29,34,41)\n           and n.get(\'enabled\') and n.get(\'state_known\') and bounds(n)[2]>0]\n    known=[n for n in items if (n.get(\'value\') or n.get(\'name\') or \'\').strip() in (*SEQUENCE_VALUES,\'완료\')]\n    columns={}\n    for n in known:\n        b=bounds(n)\n        aligned=[other for other in items if other.get(\'handle\')==n.get(\'handle\')\n                 and abs(bounds(other)[0]-b[0])<=4 and abs(bounds(other)[2]-b[2])<=4]\n        codes={(e.get(\'value\') or e.get(\'name\') or \'\').strip() for e in aligned}\n        codes.intersection_update(SEQUENCE_VALUES)\n        if len(codes)>=3 and any({f\'{v:02}\',f\'{v+1:02}\'}.issubset(codes) for v in range(1,30)):\n            for e in aligned:columns[e[\'id\']]=e\n    return list(columns.values())\n\n\ndef sequence_option(report):\n    candidates=[]\n    for e in sequence_column_items(report):\n        b=bounds(e)\n        if e.get(\'offscreen\') or b[2]<=0 or b[3]<=0:continue\n        if (e.get(\'value\') or e.get(\'name\') or \'\').strip()==pop_sequence():candidates.append(e)\n    unique={tuple(bounds(e)):e for e in candidates}\n    if len(unique)!=1:raise RuntimeError(\'세척순서 목록에서 선택할 항목을 확실히 구분하지 못했습니다. 검사 기록을 보내 주세요.\')\n    return next(iter(unique.values()))\n\n\ndef find_sequence_option(popups,api,capture,stop,emit):\n    def read(popup):\n        if stop.is_set():raise Stopped(\'사용자 중지\')\n        r=capture(popup,\'세척순서 선택 목록 후보 \'+str(popup[\'handle\']),stop);emit(\'capture\',r)\n        if stop.is_set():raise Stopped(\'사용자 중지\')\n        try:check_capture(r)\n        except RuntimeError:\n            emit(\'log\',\'세척순서 후보 창을 읽지 못했습니다: \'+str(popup[\'handle\']))\n            return None\n        # Shadow/helper windows can appear with the dropdown. Inspect their\n        # contents instead of treating every new window as a separate list.\n        if popup.get(\'bounds\'):\n            import copy\n            r=copy.deepcopy(r);pb=popup[\'bounds\']\n            for n in nodes(r):\n                b=bounds(n)\n                if not(pb[0]<=b[0] and pb[1]<=b[1] and b[0]+b[2]<=pb[0]+pb[2] and b[1]+b[3]<=pb[1]+pb[3]):n[\'offscreen\']=True\n        columns=sequence_column_items(r)\n        visible=[n for n in columns if not n.get(\'offscreen\') and bounds(n)[3]>0]\n        if not visible:return None\n        signature=tuple(sorted({((n.get(\'value\') or n.get(\'name\') or \'\').strip(),tuple(bounds(n))) for n in visible}))\n        codes={v for v,b in signature}\n        option=sequence_option(r) if pop_sequence() in codes else None\n        # Full MSAA item order is available even for zero-height hidden items.\n        # Head toward the target immediately; no forced trip to the top.\n        positions=[i for i,n in enumerate(columns) if (n.get(\'value\') or n.get(\'name\') or \'\').strip()==pop_sequence()]\n        visible_ids={n[\'id\'] for n in visible}\n        visible_positions=[i for i,n in enumerate(columns) if n[\'id\'] in visible_ids]\n        direction=0\n        if len(positions)==1 and visible_positions:\n            if positions[0]<min(visible_positions):direction=1\n            elif positions[0]>max(visible_positions):direction=-1\n        return option,signature,direction\n\n    candidates=[];seen=set()\n    emit(\'sequence\',{\'action\':\'popup_candidates\',\'windows\':popups})\n    for popup in popups:\n        if popup[\'handle\'] in seen:continue\n        seen.add(popup[\'handle\'])\n        result=read(popup)\n        if result is not None:candidates.append((popup,*result))\n    if not candidates:raise RuntimeError(\'세척순서 목록 구조를 확인하지 못했습니다. 검사 기록을 보내 주세요.\')\n    if len(candidates)!=1:raise RuntimeError(\'실제 세척순서 목록이 여러 개여서 구분하지 못했습니다. 검사 기록을 보내 주세요.\')\n    popup,option,signature,preferred=candidates[0]\n    if option:return popup,option\n    emit(\'log\',f\'세척순번 {pop_sequence()} 항목이 있는 방향으로 목록을 스크롤합니다.\')\n    nested=WindowsClicks(popup)\n    for direction in ((preferred,-preferred) if preferred else (1,-1)):\n        for _ in range(40):\n            if stop.is_set():raise Stopped(\'사용자 중지\')\n            nested.scroll_grid(popup[\'handle\'],direction,allowed_foreground={api.target[\'handle\'],popup[\'handle\']})\n            if stop.wait(.15):raise Stopped(\'사용자 중지\')\n            result=read(popup)\n            if result is None:raise RuntimeError(\'스크롤 중 세척순서 목록을 읽지 못했습니다. 검사 기록을 보내 주세요.\')\n            option,current,_=result\n            if option:return popup,option\n            if current==signature:break\n            signature=current\n        else:raise RuntimeError(\'세척순서 목록 스크롤 한도를 초과했습니다.\')\n    raise RuntimeError(f\'POP 목록에서 세척순번 {pop_sequence()} 항목을 찾지 못했습니다. 검사 기록을 보내 주세요.\')\n\n\ndef ensure_sequence(target,expected,api,capture,stop,emit,initial_report=None):\n    if stop.is_set():raise Stopped(\'사용자 중지\')\n    before=initial_report if initial_report is not None else capture({**target,\'mode\':\'mes_rows\'},\'세척순서 자동 설정 전\',stop)\n    if initial_report is None:emit(\'capture\',before)\n    actual=validate_conditions(before,expected,check_sequence=False)\n    if actual[\'sequence\']==pop_sequence():\n        emit(\'log\',f\'POP 세척순서 {pop_sequence()} 확인 — 그대로 사용합니다.\');return before\n    field=field_node(before,\'세척순서\',42)\n    if stop.is_set():raise Stopped(\'사용자 중지\')\n    previous=api.popup_inventory()\n    emit(\'log\',f\'POP 세척순서 목록에서 {pop_sequence()} 항목을 찾습니다.\')\n    api.open_sequence(before)\n    if stop.wait(.5):raise Stopped(\'사용자 중지\')\n    popups=api.sequence_popups(previous,bounds(field))\n    if not popups:raise RuntimeError(\'세척순서 선택 목록을 찾지 못했습니다. POP 화면과 화면을 확인해 주세요.\')\n    popup,option=find_sequence_option(popups,api,capture,stop,emit)\n    if stop.is_set():raise Stopped(\'사용자 중지\')\n    emit(\'log\',f\'세척순번 {pop_sequence()} 항목 확인 → 해당 번호를 클릭합니다.\')\n    api.select_sequence_option(popup,option)\n    emit(\'sequence\',{\'action\':\'select\',\'value\':pop_sequence(),\'mes_sequence\':SEQUENCE,\'previous\':actual[\'sequence\']})\n    if stop.wait(.5):raise Stopped(\'사용자 중지\')\n    after=capture({**target,\'mode\':\'mes_rows\'},f\'세척순서 {pop_sequence()} 설정 후 확인\',stop);emit(\'capture\',after)\n    validate_conditions(after,expected)\n    emit(\'sequence\',{\'action\':\'verified\',\'value\':pop_sequence(),\'mes_sequence\':SEQUENCE})\n    emit(\'log\',f\'POP 세척순서 {pop_sequence()} 자동 설정 확인 완료. 조회를 진행합니다.\')\n    return after\n\n\ndef pop_save_button(report):\n    validate_conditions(report,read_conditions(report))\n    field=field_node(report,\'검사일\',47);limit=bounds(field)[1]\n    buttons=[n for n in nodes(report) if n.get(\'parent\')==-1 and n.get(\'role\')==43\n             and n.get(\'enabled\') and n.get(\'state_known\') and not n.get(\'offscreen\')\n             and bounds(n)[2]>0 and bounds(n)[3]>0 and bounds(n)[1]+bounds(n)[3]<=limit]\n    named=[n for n in buttons if n.get(\'name\',\'\').strip()==\'저장\']\n    if len(named)==1:return named[0]\n    # Observed POP toolbar: two unnamed sibling buttons, Save then Close.\n    native={n[\'handle\']:n for n in report[\'records\'] if n.get(\'kind\')==\'native_window\'}\n    if len(buttons)!=2:raise RuntimeError(\'POP 상단 저장 버튼을 구분하지 못했습니다.\')\n    left,right=sorted(buttons,key=lambda n:bounds(n)[0]);a=bounds(left);b=bounds(right)\n    lp=native.get(left[\'handle\'],{}).get(\'native_parent\');rp=native.get(right[\'handle\'],{}).get(\'native_parent\')\n    if (not lp or lp!=rp or any(n.get(\'name\',\'\').strip() for n in buttons)\n            or abs(a[1]-b[1])>2 or a[2:]!=b[2:] or not 0<b[0]-a[0]-a[2]<=a[2]*.15):\n        raise RuntimeError(\'POP 저장·닫기 버튼 배치가 달라 저장을 중단했습니다.\')\n    return left\n\n\ndef save_dialog_button(report,phase):\n    check_capture(report)\n    visible=[n for n in nodes(report) if not n.get(\'offscreen\') and n.get(\'enabled\') and n.get(\'state_known\')]\n    messages={re.sub(r\'\\s+\',\'\',str(n.get(\'name\',\'\'))+str(n.get(\'value\',\'\')))\n              for n in visible if n.get(\'role\') in (10,41)}\n    expected=\'저장하시겠습니까?\' if phase==\'confirm\' else \'완료되었습니다.\'\n    if expected not in messages:\n        raise RuntimeError(\'POP \'+(\'저장 확인\' if phase==\'confirm\' else \'저장 완료\')+\' 문구가 예상과 다릅니다: \'+\' / \'.join(sorted(messages))[:250])\n    labels={\'예(YES)\'} if phase==\'confirm\' else {\'닫기\'}\n    buttons=[n for n in visible if n.get(\'role\')==43 and re.sub(r\'\\s+\',\'\',n.get(\'name\',\'\')) in labels and bounds(n)[2]>0 and bounds(n)[3]>0]\n    unique={(n[\'handle\'],tuple(bounds(n))):n for n in buttons}\n    if len(unique)!=1:raise RuntimeError(\'POP \'+(\'예(YES)\' if phase==\'confirm\' else \'닫기\')+\' 버튼을 하나로 구분하지 못했습니다.\')\n    return next(iter(unique.values()))\n\n\ndef save_checked_pop(target,expected,result,api,capture,stop,emit):\n    result[\'save_status\']=\'not_started\';result[\'save_performed\']=False\n    matching=result[\'matching\'];pairs=matching[\'matched\']+matching[\'already_selected\']\n    allowed={str(p[\'pop\'][\'row\']) for p in pairs}\n    if not allowed:\n        result[\'save_status\']=\'no_targets\';emit(\'log\',\'저장할 매칭 대상이 없어 저장을 생략했습니다.\');return\n    coverage=result[\'coverage\']\n    if result.get(\'check_status\')!=\'verified\' or not all(coverage.get(k) for k in (\'complete\',\'top_verified\',\'bottom_verified\')):\n        raise RuntimeError(\'전체 행 체크 검증이 끝나지 않아 저장하지 않았습니다.\')\n    report=coverage.pop(\'final_report\',None)\n    if report is None:raise RuntimeError(\'저장 전 최종 검증 화면이 없습니다.\')\n    validate_conditions(report,expected);view=pop_view(report)\n    selected={k for k,row in zip(view[\'keys\'],view[\'raw\']) if row[coverage[\'columns\'][\'선택\']].strip()==\'선택\'}\n    if selected!=allowed:raise RuntimeError(\'POP에 매칭 대상 외 체크 또는 누락이 있어 저장하지 않았습니다. 체크 상태를 확인해 주세요.\')\n    button=pop_save_button(report);previous=api.popup_inventory()\n    if stop.is_set():raise Stopped(\'사용자 중지 — 저장 전\')\n    result[\'save_status\']=\'save_click_attempted\';emit(\'result\',result)\n    api.click_handle(button[\'handle\']);result[\'save_performed\']=True;result[\'save_status\']=\'waiting_confirmation\'\n    emit(\'log\',\'POP 저장 버튼 1회 클릭 · 저장 확인창 대기\')\n    popup=None\n    for _ in range(50):\n        if stop.wait(.1):raise Stopped(\'사용자 중지 — 저장 확인창 상태를 확인해 주세요.\')\n        fresh=[w for w in visible_windows(include_untitled=True) if w[\'pid\']==target[\'pid\'] and w[\'handle\'] not in previous]\n        fresh=[w for w in fresh if api.u.GetForegroundWindow()==w[\'handle\']]\n        if len(fresh)==1:popup=fresh[0];break\n    if popup is None:raise RuntimeError(\'저장 확인창을 찾지 못했습니다. 저장 버튼을 다시 누르지 않았습니다.\')\n    api.u.GetWindow.argtypes=[wintypes.HWND,wintypes.UINT];api.u.GetWindow.restype=wintypes.HWND\n    owner=api.u.GetWindow(popup[\'handle\'],4);seen=set()\n    while owner and owner!=target[\'handle\'] and owner not in seen:\n        seen.add(owner);owner=api.u.GetWindow(owner,4)\n    if owner!=target[\'handle\']:raise RuntimeError(\'POP에서 띄운 저장 확인창인지 확인하지 못했습니다.\')\n    dialog=capture(popup,\'POP 저장 확인창\',stop);choice=save_dialog_button(dialog,\'confirm\')\n    nested=WindowsClicks(popup)\n    if stop.is_set():raise Stopped(\'사용자 중지 — 확인 클릭 전\')\n    result[\'save_status\']=\'confirmation_click_attempted\';emit(\'result\',result)\n    nested.click_handle(choice[\'handle\'])\n    result[\'confirmation_clicked\']=True;result[\'save_status\']=\'waiting_completion\'\n    emit(\'log\',\'POP 예(YES) 클릭 · 완료 메시지 대기\')\n    completed=None;deadline=time.monotonic()+30\n    while time.monotonic()<deadline:\n        if stop.wait(.1):raise Stopped(\'사용자 중지 — 저장 처리 중입니다. POP 완료 여부를 확인해 주세요.\')\n        dialogs=[w for w in visible_windows(include_untitled=True) if w[\'pid\']==target[\'pid\']\n                 and w[\'handle\']!=target[\'handle\'] and (w[\'handle\'] not in previous or w[\'handle\']==popup[\'handle\'])\n                 and api.u.GetForegroundWindow()==w[\'handle\']]\n        if len(dialogs)!=1:continue\n        current=dialogs[0]\n        owner=api.u.GetWindow(current[\'handle\'],4);seen=set()\n        while owner and owner!=target[\'handle\'] and owner not in seen:\n            seen.add(owner);owner=api.u.GetWindow(owner,4)\n        if owner!=target[\'handle\']:raise RuntimeError(\'POP 저장 완료창의 소유자를 확인하지 못했습니다.\')\n        report=capture(current,\'POP 저장 완료창\',stop)\n        messages={re.sub(r\'\\s+\',\'\',str(n.get(\'name\',\'\'))+str(n.get(\'value\',\'\'))) for n in nodes(report) if not n.get(\'offscreen\') and n.get(\'role\') in (10,41)}\n        if \'저장하시겠습니까?\' in messages:\n            # The affirmative click is never repeated while the old dialog is closing.\n            continue\n        choice=save_dialog_button(report,\'complete\');completed=current\n        result[\'pop_success_reported\']=True;result[\'save_status\']=\'completion_close_attempted\'\n        if stop.is_set():raise Stopped(\'사용자 중지 — POP 완료 메시지 확인, 닫기 전\')\n        WindowsClicks(current).click_handle(choice[\'handle\'])\n        break\n    if completed is None:raise RuntimeError(\'POP 완료 메시지를 기다리다 중단했습니다. 저장·예를 다시 누르지 않았습니다.\')\n    for _ in range(50):\n        if stop.wait(.1):raise Stopped(\'사용자 중지 — POP 완료창 닫기 후 상태를 확인해 주세요.\')\n        if not api.u.IsWindowVisible(completed[\'handle\']) and api.u.IsWindowEnabled(target[\'handle\']):\n            result[\'save_status\']=\'confirmed\';result[\'completion_performed\']=True;result[\'completion_closed\']=True\n            emit(\'log\',\'POP 저장 → 예 → 완료 메시지 → 닫기 완료\');emit(\'result\',result);return\n    raise RuntimeError(\'저장 완료창 닫기를 확인하지 못했습니다. 추가 클릭하지 않았습니다.\')\n\n\n\ndef pop_steps(target,binding,expected,source,api,capture,stop,emit,initial_report=None):\n    if expected.get(\'sequence\')!=SEQUENCE:raise RuntimeError(\'요청한 세척순번과 실행 설정이 다릅니다.\')\n    if source and source.get(\'sequence\')!=SEQUENCE:raise RuntimeError(\'MES 대상의 세척순번이 실행 설정과 다릅니다.\')\n    def read(label):\n        if stop.is_set():raise Stopped(\'사용자 중지\')\n        report=capture({**target,\'mode\':\'pop_full\'},label,stop);emit(\'capture\',report);validate_conditions(report,expected)\n        return report\n    before=ensure_sequence(target,expected,api,capture,stop,emit,initial_report=initial_report);validate_query(before,binding)\n    if stop.is_set():raise Stopped(\'사용자 중지\')\n    api.query_click(binding);emit(\'log\',\'POP 조회 완료 · 2초 대기 후 목록을 한 번 읽습니다.\')\n    emit(\'query\',{\'click_count\':1,\'wait_seconds\':2.0,\'server_refresh_confirmed\':False})\n    if stop.wait(2.0):raise Stopped(\'사용자 중지\')\n    last=read(\'POP 조회 후 전체 목록 1회 판독\')\n    coverage=collect_pop(target,last,expected,api,capture,stop,emit)\n    result={\'conditions\':expected,\'query_click_count\':1,\'post_query_reads\':1,\'query_wait_seconds\':2.0,\n            \'server_refresh_confirmed\':False,\'coverage\':coverage,\'mes_source\':source,\n            \'matching\':match_rows(source,coverage[\'rows\']),\n            \'requested_projects\':[r[\'project\'] for r in source[\'candidates\']],\n            \'checks_performed\':False,\'completion_performed\':False}\n    emit(\'result\',result)\n    if coverage[\'keys\']:\n        result[\'check_status\']=\'in_progress\';result[\'checks_performed\']=None\n        checks=check_matched(target,expected,coverage,result[\'matching\'][\'matched\'],api,capture,stop,emit)\n        result[\'checks_performed\']=bool(checks);result[\'verified_checks\']=checks;result[\'check_status\']=\'verified\'\n        emit(\'result\',result)\n        emit(\'log\',f\'세척{SEQUENCE} 체크 {len(checks)}개 확인 완료. 최종 체크 검증 완료.\')\n        return result\n    emit(\'log\',\'검사 종료. POP 목록이 비어 있어 매칭 검증은 보류합니다.\' if not coverage[\'rows\'] else \'체크할 매칭 대상이 없습니다. 화면을 확인해 주세요.\')\n    return result\n\n\n\n\ndef worker_button(report):\n    field=field_node(report,\'작업자\',42); fb=bounds(field)\n    candidates=[]\n    for n in nodes(report):\n        b=bounds(n)\n        if (n.get(\'parent\')==-1 and n.get(\'role\')==43 and n.get(\'enabled\')\n            and not n.get(\'offscreen\') and 0<=b[0]-fb[0]-fb[2]<=fb[3]/2\n            and abs(b[1]+b[3]/2-fb[1]-fb[3]/2)<fb[3]/3\n            and 0<b[2]<=fb[3]*1.5 and 0<b[3]<=fb[3]*1.5\n            and not any(s in n.get(\'name\',\'\') for s in (\'완료\',\'저장\',\'삭제\',\'닫기\'))):\n            candidates.append(n)\n    if len(candidates)!=1:raise RuntimeError(\'작업자 옆 돋보기를 하나로 구분하지 못했습니다. 화면을 확인해 주세요.\')\n    return candidates[0]\n\n\ndef worker_choice(report,name):\n    check_capture(report)\n    children=defaultdict(list)\n    for n in nodes(report):children[n[\'parent\']].append(n)\n    tables=[]\n    for table in nodes(report):\n        if table.get(\'role\')!=24:continue\n        headers=[h for g in children[table[\'id\']] for h in children[g[\'id\']] if h.get(\'role\')==25]\n        if {\'선택\',\'사용자ID\',\'작업자\'}.issubset({h.get(\'name\') for h in headers}):tables.append((table,headers))\n    if len(tables)!=1:raise RuntimeError(\'작업자 표를 구분하지 못했습니다. 화면을 확인해 주세요.\')\n    table,headers=tables[0];tb=bounds(table)\n    panels=[p for p in children[table[\'id\']] if p.get(\'name\')==\'데이터 패널\']\n    if len(panels)!=1:raise RuntimeError(\'작업자 목록 데이터 패널을 확인하지 못했습니다.\')\n    panel=panels[0];rows=[r for r in children[panel[\'id\']] if r.get(\'role\')==28]\n    if len(rows)!=panel.get(\'child_count\'):raise RuntimeError(\'작업자 목록의 일부 행을 읽지 못했습니다.\')\n    # Count every returned row, including offscreen rows, to reject duplicate names.\n    hits=[]\n    for row in rows:\n        cells=[c for c in children[row[\'id\']] if c.get(\'role\')==29]\n        if len(cells)!=row.get(\'child_count\'):raise RuntimeError(\'작업자 행의 일부 칸을 읽지 못했습니다.\')\n        if any(str(c.get(\'value\',\'\')).strip()==name for c in cells):hits.append((row,cells))\n    if len(hits)!=1:raise RuntimeError(f\'이름 [{name}] 검색 결과 {len(hits)}개입니다. 이름과 목록을 확인하고 화면을 확인해 주세요.\')\n    row,cells=hits[0];rb=bounds(row)\n    if row.get(\'offscreen\') or rb[2]<=0 or rb[3]<=0:raise RuntimeError(\'대상 작업자가 화면 밖에 있습니다. 목록이 보이도록 한 뒤 다시 시험해 주세요.\')\n    mapped={}\n    for title in (\'선택\',\'사용자ID\',\'작업자\'):\n        hs=[h for h in headers if h.get(\'name\')==title and bounds(h)[2]>0]\n        if len(hs)!=1:raise RuntimeError(\'작업자 열을 구분하지 못했습니다: \'+title)\n        hb=bounds(hs[0])\n        cs=[c for c in cells if not c.get(\'offscreen\') and bounds(c)[3]>0 and abs(bounds(c)[0]-hb[0])<=3 and abs(bounds(c)[2]-hb[2])<=3]\n        if len(cs)!=1:raise RuntimeError(\'작업자 선택 칸을 구분하지 못했습니다: \'+title)\n        mapped[title]=cs[0]\n    if str(mapped[\'작업자\'].get(\'value\',\'\')).strip()!=name:raise RuntimeError(\'작업자 이름과 열 위치가 일치하지 않습니다.\')\n    cell=mapped[\'선택\'];cb=bounds(cell)\n    if not cell.get(\'enabled\') or not cell.get(\'state_known\'):raise RuntimeError(\'선택 버튼 상태를 확인하지 못했습니다.\')\n    if not(tb[0]<=cb[0] and cb[0]+cb[2]<=tb[0]+tb[2] and tb[1]<=cb[1] and cb[1]+cb[3]<=tb[1]+tb[3]):raise RuntimeError(\'선택 칸이 완전히 보이지 않습니다.\')\n    return {\'handle\':table[\'handle\'],\'grid_bounds\':tb,\'cell_bounds\':cb,\'name\':name,\'user_id\':mapped[\'사용자ID\'].get(\'value\',\'\')}\n\n\ndef ensure_worker(target,name,capture,stop,emit):\n    def pause(seconds):\n        if stop.wait(seconds):raise Stopped(\'사용자 중지\')\n    api=WindowsClicks(target);api.activate();pause(.25)\n    before=capture({**target,\'mode\':\'mes_rows\'},\'작업자 변경 전\',stop)\n    old=field_node(before,\'작업자\',42).get(\'value\',\'\').strip()\n    emit(\'log\',f\'현재 작업자: {old or "빈칸"} → 선택할 이름: {name}\')\n    if old==name:\n        emit(\'log\',\'작업자가 이미 \'+name+\'입니다. 선택창을 건너뜁니다.\')\n        return {\'success\':True,\'before\':old,\'after\':old,\'selection_clicked\':False,\'report\':before}\n    previous=api.popup_inventory();button=worker_button(before)\n    if stop.is_set():raise Stopped(\'사용자 중지\')\n    api.click_handle(button[\'handle\']);emit(\'log\',\'작업자 돋보기 클릭\')\n    popup=None\n    for _ in range(30):\n        pause(.1)\n        matches=[w for w in visible_windows(True) if w[\'pid\']==target[\'pid\'] and w[\'handle\'] not in previous and w[\'title\'].strip()==\'작업자\']\n        if len(matches)>1:raise RuntimeError(\'작업자 선택창이 여러 개입니다.\')\n        if matches:popup=matches[0];break\n    if popup is None:raise RuntimeError(\'작업자 선택창을 확인하지 못했습니다. 창이 열린 상태로 화면을 확인해 주세요.\')\n    nested=WindowsClicks(popup);nested.activate();pause(.15)\n    report=capture(popup,\'작업자 선택 목록\',stop);choice=worker_choice(report,name)\n    emit(\'log\',f"이름 일치: {name} / 사용자ID: {choice[\'user_id\']}")\n    if stop.is_set():raise Stopped(\'사용자 중지\')\n    nested.click_handle(choice[\'handle\'],selection=(choice[\'grid_bounds\'],choice[\'cell_bounds\']))\n    emit(\'log\',\'해당 행의 초록색 선택 버튼 1회 클릭\')\n    for _ in range(30):\n        pause(.1)\n        if not nested.u.IsWindowVisible(popup[\'handle\']):break\n    else:\n        capture(popup,\'선택 클릭 후 창이 남아 있음\',stop)\n        raise RuntimeError(\'선택창이 닫히지 않아 멈췄습니다. 추가 클릭하지 않았습니다. 화면을 확인해 주세요.\')\n    after=capture({**target,\'mode\':\'mes_rows\'},\'작업자 변경 후\',stop)\n    actual=field_node(after,\'작업자\',42).get(\'value\',\'\').strip()\n    if actual!=name:raise RuntimeError(f\'작업자 반영 불일치: 요청 [{name}] / 화면 [{actual}]\')\n    return {\'success\':True,\'before\':old,\'requested\':name,\'after\':actual,\'user_id\':choice[\'user_id\'],\n            \'selection_clicked\':True,\'query_clicked\':False,\'completion_performed\':False,\'save_performed\':False,\'report\':after}\n'
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
        start=time.monotonic();deadline=start+45
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


class WashApp:
    def __init__(self,host,parent):
        import tkinter as tk
        from tkinter import ttk
        from datetime import date
        self.host=host;self.root=host.window;self.busy=False;self.stop=threading.Event();self.events=queue.Queue()
        self.result=None;self.started=0;self.mes_binding=None;self.mes_target=None
        self.capture_stage=None;self.capture_status=None
        self.mes=load_wash_module(WASH_MES_SOURCE,'jihuni_wash_mes')
        self.pop=load_wash_module(WASH_POP_SOURCE,'jihuni_wash_pop')
        style=ttk.Style(self.root)
        style.configure('Wash.TCombobox',fieldbackground='#182436',background='#2b3b52',foreground='#ffffff',padding=6)
        style.map('Wash.TCombobox',fieldbackground=[('readonly','#182436')],foreground=[('readonly','#ffffff')],selectbackground=[('readonly','#182436')],selectforeground=[('readonly','#ffffff')])
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

    def emit(self,kind,value):
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
        self.host.suspend_machine_alerts()
        self.capture_stage=None;self.capture_status=None
        self.status.set('창과 조건 확인 중…')
        threading.Thread(target=self.work,args=(run,expected,selected_numbers),daemon=True).start()

    def work(self,run,expected,selected_numbers):
        reader=None;finished_result=None;failure=None
        try:
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
                    return report
                except Exception as error:
                    elapsed=time.monotonic()-started
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
            self.emit('done',{'elapsed':time.monotonic()-self.started,'result':finished_result,'error':failure})

    def show_completion(self,title,brief):
        import tkinter as tk
        from tkinter import ttk
        dialog=tk.Toplevel(self.root);dialog.title(title);dialog.configure(bg='#131c2b')
        dialog.transient(self.root)
        width=min(760,dialog.winfo_screenwidth()-80);height=min(540,dialog.winfo_screenheight()-100)
        x=max(0,(dialog.winfo_screenwidth()-width)//2);y=max(0,(dialog.winfo_screenheight()-height)//2)
        dialog.geometry(f'{width}x{height}+{x}+{y}');dialog.minsize(min(520,width),min(320,height))
        body=ttk.Frame(dialog,padding=18);body.pack(fill='both',expand=True)
        ttk.Label(body,text=title,font=('맑은 고딕',17,'bold')).pack(anchor='w',pady=(0,12))
        area=ttk.Frame(body);area.pack(fill='both',expand=True)
        text=tk.Text(area,bg='#131c2b',fg='#e7edf7',font=('맑은 고딕',11),wrap='word',relief='flat',padx=8,pady=8)
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

SuiteCompanionManager = _suite_load_support("jihunius_suite_companions", '"""Bounded, two-phase save handshake for parent-owned companion processes.\n\nEmbedded into each companion so the released Python file stays self-contained.\nNo network calls, business actions, or accumulated event log live here.\n"""\nimport json as _cu_json\nimport os as _cu_os\nfrom pathlib import Path as _CuPath\nimport time as _cu_time\nimport uuid as _cu_uuid\n\n\ndef _cu_write(path, value):\n    path = _CuPath(path)\n    path.parent.mkdir(parents=True, exist_ok=True)\n    temp = path.with_name(path.name + \'.\' + _cu_uuid.uuid4().hex + \'.tmp\')\n    try:\n        with temp.open(\'w\', encoding=\'utf-8\') as stream:\n            _cu_json.dump(value, stream, ensure_ascii=False)\n            stream.flush()\n            _cu_os.fsync(stream.fileno())\n        _cu_os.replace(str(temp), str(path))\n    finally:\n        try: temp.unlink()\n        except FileNotFoundError: pass\n\n\ndef _cu_read(path):\n    try:\n        with _CuPath(path).open(\'rb\') as stream:\n            data = stream.read(16385)\n        if len(data) > 16384: return {}\n        value = _cu_json.loads(data)\n        return value if isinstance(value, dict) else {}\n    except (OSError, ValueError):\n        return {}\n\n\nclass CompanionUpdateBridge:\n    def __init__(self, root, adapter):\n        self.root, self.adapter = root, adapter\n        self.path = _cu_os.environ.get(\'JIHUNIUS_UPDATE_SESSION\', \'\')\n        self.nonce = _cu_os.environ.get(\'JIHUNIUS_UPDATE_NONCE\', \'\')\n        self.request_id = None\n        self.active = False\n        self.ready = False\n        self.started = False\n        self.overlay = None\n        self.error = \'\'\n        if self.path and len(self.nonce) == 32:\n            self.path = _CuPath(self.path)\n            self.root.after(500, self.poll)\n\n    def reply(self, status, message=\'\'):\n        _cu_write(self.path / \'response.json\', {\n            \'nonce\': self.nonce, \'id\': self.request_id,\n            \'status\': status, \'message\': message[:1000],\n        })\n\n    def release(self):\n        self.active = False\n        self.ready = False\n        self.started = False\n        if self.overlay is not None:\n            try:\n                self.overlay.grab_release()\n                self.overlay.destroy()\n            except Exception: pass\n            self.overlay = None\n\n    def fail(self, message):\n        self.error = str(message)\n        try: self.reply(\'error\', self.error)\n        finally: self.release()\n\n    def modal_open(self):\n        if self.root.grab_current() is not None:\n            return True\n        if _cu_os.name == \'nt\':\n            import ctypes\n            from ctypes import wintypes\n            user = ctypes.WinDLL(\'user32\', use_last_error=True)\n            user.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]\n            user.GetAncestor.restype = wintypes.HWND\n            user.IsWindowEnabled.argtypes = [wintypes.HWND]\n            user.IsWindowEnabled.restype = wintypes.BOOL\n            return not user.IsWindowEnabled(user.GetAncestor(self.root.winfo_id(), 2))\n        return False\n\n    def start(self, request):\n        if self.modal_open():\n            raise RuntimeError(\'열린 확인창을 처리한 뒤 업데이트를 다시 눌러 주세요.\')\n        import tkinter as tk\n        from tkinter import ttk\n        self.active = True\n        self.error = \'\'\n        self.started = False\n        self.ready = False\n        dialog = tk.Toplevel(self.root)\n        self.overlay = dialog\n        dialog.title(\'업데이트 전 저장\')\n        dialog.transient(self.root)\n        dialog.resizable(False, False)\n        ttk.Label(dialog, text=\'변경 내용을 저장하고 있습니다…\', padding=20).pack()\n        ttk.Button(dialog, text=\'업데이트 취소\', command=lambda: self.fail(\'사용자가 업데이트를 취소했습니다.\')).pack(pady=(0, 16))\n        dialog.protocol(\'WM_DELETE_WINDOW\', lambda: self.fail(\'사용자가 업데이트를 취소했습니다.\'))\n        dialog.grab_set()\n        # A focus change plus an event-loop turn commits the last Korean IME syllable.\n        dialog.focus_set()\n        self.begin_after = _cu_time.monotonic() + .15\n        self.reply(\'saving\')\n\n    def poll(self):\n        try:\n            request = _cu_read(self.path / \'request.json\')\n            valid = (request.get(\'nonce\') == self.nonce\n                     and isinstance(request.get(\'id\'), str)\n                     and isinstance(request.get(\'expires\'), (int, float))\n                     and _cu_time.time() < request[\'expires\'])\n            if self.active and (not valid or request.get(\'id\') != self.request_id\n                                or request.get(\'phase\') == \'cancel\'):\n                self.fail(\'업데이트 저장 요청이 취소되거나 연결이 종료됐습니다.\')\n            if valid and request[\'id\'] != self.request_id and request.get(\'phase\') == \'prepare\':\n                self.request_id = request[\'id\']\n                self.start(request)\n            if self.active and not self.started and _cu_time.monotonic() >= self.begin_after:\n                self.adapter.begin()\n                self.started = True\n            if self.active and self.started and not self.ready:\n                if self.adapter.saved():\n                    self.ready = True\n                    self.reply(\'ready\')\n            if self.active and self.ready and request.get(\'phase\') == \'close\':\n                # Recheck immediately before close; no edit can enter through the grab.\n                if self.adapter.saved():\n                    self.adapter.finish()\n                    self.reply(\'closed\')\n                    self.active = False\n                    return\n        except Exception as exc:\n            try: self.fail(str(exc))\n            except Exception: self.release()\n        try: self.root.after(250 if self.active else 750, self.poll)\n        except Exception: pass\n\n"""Original companion applications in separate processes, with graceful ownership.\n\nNo UI code or shared-data logic is rewritten. Native calls address only the\nknown main window of a live process started by this manager.\n"""\nimport ctypes\nimport hashlib\nimport os\nfrom pathlib import Path\nimport re\nimport subprocess\nimport sys\nimport tempfile\nimport threading\nimport time\nimport uuid\n\n\nclass CompanionWindows:\n    def __init__(self):\n        if os.name != "nt":\n            self.user = None\n            return\n        from ctypes import wintypes\n        self.w = wintypes\n        self.user = ctypes.WinDLL("user32", use_last_error=True)\n        self.callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)\n        declarations = {\n            "EnumWindows": ([self.callback_type, wintypes.LPARAM], wintypes.BOOL),\n            "GetWindowThreadProcessId": ([wintypes.HWND, ctypes.POINTER(wintypes.DWORD)], wintypes.DWORD),\n            "GetWindowTextLengthW": ([wintypes.HWND], ctypes.c_int),\n            "GetWindowTextW": ([wintypes.HWND, wintypes.LPWSTR, ctypes.c_int], ctypes.c_int),\n            "GetClassNameW": ([wintypes.HWND, wintypes.LPWSTR, ctypes.c_int], ctypes.c_int),\n            "IsWindow": ([wintypes.HWND], wintypes.BOOL),\n            "IsWindowEnabled": ([wintypes.HWND], wintypes.BOOL),\n            "IsWindowVisible": ([wintypes.HWND], wintypes.BOOL),\n            "IsIconic": ([wintypes.HWND], wintypes.BOOL),\n            "ShowWindowAsync": ([wintypes.HWND, ctypes.c_int], wintypes.BOOL),\n            "SetForegroundWindow": ([wintypes.HWND], wintypes.BOOL),\n            "GetLastActivePopup": ([wintypes.HWND], wintypes.HWND),\n            "PostMessageW": ([wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM], wintypes.BOOL),\n        }\n        for name, (arguments, result) in declarations.items():\n            function = getattr(self.user, name)\n            function.argtypes = arguments\n            function.restype = result\n\n    def _owns(self, hwnd, pid):\n        if not self.user or not self.user.IsWindow(hwnd):\n            return False\n        actual = self.w.DWORD()\n        self.user.GetWindowThreadProcessId(hwnd, ctypes.byref(actual))\n        return actual.value == pid\n\n    def _main_window(self, pid, title):\n        if self.user is None:\n            return None\n        matches = []\n\n        def visit(hwnd, ignored):\n            if not self._owns(hwnd, pid):\n                return True\n            length = self.user.GetWindowTextLengthW(hwnd)\n            if length != len(title):\n                return True\n            text = ctypes.create_unicode_buffer(length + 1)\n            self.user.GetWindowTextW(hwnd, text, length + 1)\n            if text.value != title:\n                return True\n            class_name = ctypes.create_unicode_buffer(128)\n            self.user.GetClassNameW(hwnd, class_name, len(class_name))\n            if class_name.value == "TkTopLevel":\n                matches.append(hwnd)\n            return True\n\n        callback = self.callback_type(visit)\n        if not self.user.EnumWindows(callback, 0):\n            raise OSError("열린 프로그램 창을 확인하지 못했습니다.")\n        # Ambiguity must never result in addressing a similarly named dialog.\n        return matches[0] if len(matches) == 1 else None\n\n    def focus(self, pid, title):\n        hwnd = self._main_window(pid, title)\n        if not hwnd or not self._owns(hwnd, pid):\n            return False\n        if self.user.IsIconic(hwnd):\n            self.user.ShowWindowAsync(hwnd, 9)  # SW_RESTORE; keeps saved geometry.\n        elif not self.user.IsWindowVisible(hwnd):\n            self.user.ShowWindowAsync(hwnd, 5)  # SW_SHOW, without resizing.\n        popup = self.user.GetLastActivePopup(hwnd)\n        if popup and self._owns(popup, pid) and self.user.IsWindowVisible(popup):\n            hwnd = popup\n        return bool(self.user.SetForegroundWindow(hwnd))\n\n    def close(self, pid, title):\n        if self.user is None:\n            raise RuntimeError("이 환경에서는 열린 창을 직접 닫은 뒤 완전 종료해 주세요.")\n        hwnd = self._main_window(pid, title)\n        if not hwnd or not self._owns(hwnd, pid):\n            raise RuntimeError(title + " 창이 준비 중이거나 종료 중입니다. 잠시 후 다시 시도해 주세요.")\n        if not self.user.IsWindowEnabled(hwnd):\n            self.focus(pid, title)\n            raise RuntimeError(title + "의 열린 확인창을 먼저 처리해 주세요.")\n        if not self.user.PostMessageW(hwnd, 0x0010, 0, 0):  # WM_CLOSE; original save/cancel flow.\n            raise OSError(title + "에 정상 종료 요청을 전달하지 못했습니다.")\n        return True\n\n\nclass CompanionManager:\n    def __init__(self, payloads, origin, _backend=None, _popen=None):\n        self.payloads = dict(payloads)\n        self.origin = Path(origin).resolve()\n        self.backend = _backend if _backend is not None else CompanionWindows()\n        self._popen = _popen if _popen is not None else subprocess.Popen\n        self.processes = {}\n        self.sessions = {}\n        self.update_save = None\n        self._lock = threading.RLock()\n        base = Path(os.environ.get("LOCALAPPDATA") or str(Path.home()))\n        self.cache = base / "JihuniusSuite" / "companions"\n\n    def _descriptor(self, key):\n        if key not in ("protrusion", "wash-log") or key not in self.payloads:\n            raise ValueError("알 수 없는 프로그램입니다.")\n        item = self.payloads[key]\n        data, digest = item.get("data"), item.get("sha256")\n        if (not isinstance(data, bytes) or not data or len(data) > 2 * 1024 * 1024\n                or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)\n                or hashlib.sha256(data).hexdigest() != digest):\n            raise ValueError("내장 프로그램 파일 검증에 실패했습니다.")\n        if not isinstance(item.get("title"), str) or not item["title"]:\n            raise ValueError("프로그램 창 이름이 올바르지 않습니다.")\n        return item\n\n    def _extract(self, key, item):\n        destination = self.cache / key / item["sha256"] / "app.pyw"\n        try:\n            if destination.read_bytes() == item["data"]:\n                return destination\n        except FileNotFoundError:\n            pass\n        destination.parent.mkdir(parents=True, exist_ok=True)\n        descriptor, temporary = tempfile.mkstemp(prefix=".app-", suffix=".tmp", dir=str(destination.parent))\n        try:\n            with os.fdopen(descriptor, "wb") as stream:\n                stream.write(item["data"])\n                stream.flush()\n                os.fsync(stream.fileno())\n            os.replace(temporary, str(destination))\n        finally:\n            try:\n                os.unlink(temporary)\n            except FileNotFoundError:\n                pass\n        if hashlib.sha256(destination.read_bytes()).hexdigest() != item["sha256"]:\n            raise ValueError("프로그램 파일 저장 후 검증에 실패했습니다.")\n        return destination\n\n    def running_keys(self):\n        with self._lock:\n            ended = [key for key, process in self.processes.items() if process.poll() is not None]\n            for key in ended:\n                del self.processes[key]\n                if self.update_save is None or key not in self.update_save[\'keys\']:\n                    self._clear_session(key)\n            return list(self.processes)\n\n    def _clear_session(self, key):\n        session = self.sessions.pop(key, None)\n        if session is None: return\n        try:\n            for name in (\'request.json\', \'response.json\'):\n                try: (session[0] / name).unlink()\n                except FileNotFoundError: pass\n            session[0].rmdir()\n        except OSError: pass\n\n    def focus(self, key):\n        with self._lock:\n            if key not in self.running_keys():\n                return False\n            return self.backend.focus(self.processes[key].pid, self.payloads[key]["title"])\n\n    def open(self, key):\n        with self._lock:\n            if self.update_save is not None:\n                raise RuntimeError(\'업데이트 전 저장을 진행 중입니다. 잠시 기다려 주세요.\')\n            item = self._descriptor(key)\n            if key in self.running_keys():\n                self.focus(key)\n                return False\n            payload = self._extract(key, item)\n            executable = Path(sys.executable)\n            if os.name == "nt":\n                windowed = executable.with_name("pythonw.exe")\n                if windowed.is_file():\n                    executable = windowed\n            environment = os.environ.copy()\n            environment["JIHUNIUS_LAUNCH_DIR"] = str(self.origin)\n            session = self.cache / \'control\' / uuid.uuid4().hex\n            session.mkdir(parents=True)\n            nonce = uuid.uuid4().hex\n            environment[\'JIHUNIUS_UPDATE_SESSION\'] = str(session)\n            environment[\'JIHUNIUS_UPDATE_NONCE\'] = nonce\n            # Keep a real script file for multiprocessing spawn in the wash log.\n            process = self._popen([str(executable), str(payload)], cwd=str(self.origin), env=environment)\n            self.processes[key] = process\n            self.sessions[key] = (session, nonce)\n            return True\n\n    def _update_command(self, key, phase):\n        session, nonce = self.sessions[key]\n        _cu_write(session / \'request.json\', {\n            \'id\': self.update_save[\'id\'], \'nonce\': nonce, \'phase\': phase,\n            \'expires\': time.time() + 10,\n        })\n\n    def begin_update_save(self):\n        with self._lock:\n            if self.update_save is not None:\n                raise RuntimeError(\'업데이트 저장 요청이 이미 진행 중입니다.\')\n            keys = self.running_keys()\n            if any(key not in self.sessions for key in keys):\n                raise RuntimeError(\'이전 버전의 보조창을 저장하고 닫은 뒤 다시 눌러 주세요.\')\n            self.update_save = {\'id\': uuid.uuid4().hex, \'keys\': keys,\n                                \'phase\': \'prepare\', \'start\': time.monotonic(), \'heartbeat\': 0}\n            try:\n                for key in keys: self._update_command(key, \'prepare\')\n            except Exception:\n                self.cancel_update_save()\n                raise\n\n    def cancel_update_save(self):\n        with self._lock:\n            if self.update_save is not None:\n                for key in self.update_save[\'keys\']:\n                    try: self._update_command(key, \'cancel\')\n                    except OSError: pass\n                self.update_save = None\n\n    def poll_update_save(self):\n        with self._lock:\n            state = self.update_save\n            if state is None: raise RuntimeError(\'업데이트 저장 요청이 없습니다.\')\n            if time.monotonic() - state[\'start\'] > 90:\n                raise RuntimeError(\'보조창 저장 확인이 지연돼 업데이트를 보류했습니다. 현재 입력을 확인해 주세요.\')\n            statuses = []\n            for key in state[\'keys\']:\n                session, nonce = self.sessions[key]\n                response = _cu_read(session / \'response.json\')\n                status = response.get(\'status\') if response.get(\'nonce\') == nonce and response.get(\'id\') == state[\'id\'] else None\n                if status == \'error\':\n                    raise RuntimeError(self.payloads[key][\'title\'] + \': \' + response.get(\'message\', \'저장 확인 실패\'))\n                process = self.processes.get(key)\n                exited = process is None or process.poll() is not None\n                if state[\'phase\'] == \'prepare\' and exited:\n                    raise RuntimeError(self.payloads[key][\'title\'] + \' 창이 저장 확인 전에 종료됐습니다.\')\n                if state[\'phase\'] == \'close\' and exited and status != \'closed\':\n                    raise RuntimeError(self.payloads[key][\'title\'] + \'의 정상 종료를 확인하지 못했습니다.\')\n                statuses.append((status, exited))\n            if state[\'phase\'] == \'prepare\' and all(status == \'ready\' for status, _ in statuses):\n                state[\'phase\'] = \'close\'\n                for key in state[\'keys\']: self._update_command(key, \'close\')\n                state[\'heartbeat\'] = time.monotonic()\n            elif state[\'phase\'] == \'close\' and all(status == \'closed\' and exited for status, exited in statuses):\n                self.update_save = None\n                self.running_keys()\n                for key in state[\'keys\']: self._clear_session(key)\n                return True\n            if time.monotonic() - state[\'heartbeat\'] > 2:\n                for key in state[\'keys\']: self._update_command(key, state[\'phase\'])\n                state[\'heartbeat\'] = time.monotonic()\n            return False\n\n    def request_close_all(self):\n        with self._lock:\n            for key in self.running_keys():\n                process = self.processes[key]\n                # Reap immediately before addressing native windows (PID ownership).\n                if process.poll() is None:\n                    self.backend.close(process.pid, self.payloads[key]["title"])\n            return self.running_keys()\n').CompanionManager
SuiteWindowsTray = _suite_load_support('jihunius_suite_tray', '"""Windows notification-area lifecycle. Callbacks enqueue work; they never touch Tk."""\nimport ctypes\nimport os\nimport threading\n\n\nclass WindowsTray:\n    def __init__(self, callback, title=\'지후니우스\', owner_hwnd=None):\n        self.callback = callback\n        self.title = str(title)\n        self.owner_hwnd = owner_hwnd\n        self._ready = threading.Event()\n        self._stopping = threading.Event()\n        self._available = False\n        self._thread = None\n        self._backend = None\n        self._lock = threading.RLock()\n\n    @property\n    def available(self):\n        return self._available and not self._stopping.is_set()\n\n    def start(self, timeout=2.0):\n        with self._lock:\n            if self._thread is None or not self._thread.is_alive():\n                self._ready.clear()\n                self._stopping.clear()\n                self._available = False\n                self._backend = None\n                self._thread = threading.Thread(target=self._worker, name=\'JihuniusTray\', daemon=True)\n                self._thread.start()\n        if not self._ready.wait(max(0.0, float(timeout))):\n            self.stop()\n            return False\n        return self.available\n\n    def _dispatch(self, action):\n        if self._stopping.is_set():\n            return\n        if action == \'ready\':\n            self._available = True\n            return  # Internal recovery signal; no Tk work is necessary.\n        if action == \'failed\':\n            self._available = False\n        if action not in (\'show\', \'protrusion\', \'wash-log\', \'quit\', \'failed\'):\n            return\n        try:\n            self.callback(action)\n        except Exception:\n            # A destroyed UI must not unwind through a ctypes window callback.\n            pass\n\n    def _worker(self):\n        backend = None\n        was_available = False\n        try:\n            backend = _NativeTrayBackend(self._dispatch, self.title, self.owner_hwnd)\n            self._backend = backend\n            ready = bool(backend.setup())\n            self._available = ready and not self._stopping.is_set()\n            was_available = self._available\n            self._ready.set()\n            if self._available:\n                backend.run()\n        except Exception:\n            pass\n        finally:\n            self._available = False\n            self._ready.set()\n            if backend is not None:\n                try:\n                    backend.close()\n                except Exception:\n                    pass\n            if was_available and not self._stopping.is_set():\n                self._dispatch(\'failed\')\n\n    def stop(self):\n        self._stopping.set()\n        self._available = False\n        backend = self._backend\n        if backend is not None:\n            try:\n                backend.request_stop()\n            except Exception:\n                pass\n        thread = self._thread\n        if thread is not None and thread is not threading.current_thread():\n            thread.join(.15)\n\n\nclass _NativeTrayBackend:\n    CALLBACK_MESSAGE = 0x8000 + 61\n    STOP_MESSAGE = 0x8000 + 62\n    ICON_ID = 1\n    COMMANDS = {1: \'show\', 2: \'protrusion\', 3: \'wash-log\', 4: \'quit\'}\n\n    def __init__(self, callback, title, owner_hwnd):\n        self.callback = callback\n        self.title = title\n        self.owner_hwnd = owner_hwnd\n        self.hwnd = None\n        self.icon = None\n        self.atom = None\n        self.icon_added = False\n        self._stop_requested = threading.Event()\n        self._native_ready = False\n        self._menu_open = False\n\n    def _load_api(self):\n        if os.name != \'nt\':\n            return False\n        from ctypes import wintypes\n        self.w = wintypes\n        self.u = ctypes.WinDLL(\'user32\', use_last_error=True)\n        self.s = ctypes.WinDLL(\'shell32\', use_last_error=True)\n        self.k = ctypes.WinDLL(\'kernel32\', use_last_error=True)\n        HANDLE = ctypes.c_void_p\n        DWORD = ctypes.c_uint32\n        UINT = ctypes.c_uint32\n        BOOL = ctypes.c_int\n        LPARAM = ctypes.c_ssize_t\n        WPARAM = ctypes.c_size_t\n        LRESULT = ctypes.c_ssize_t\n        self.WNDPROC = ctypes.WINFUNCTYPE(LRESULT, HANDLE, UINT, WPARAM, LPARAM)\n\n        class GUID(ctypes.Structure):\n            _fields_ = [(\'Data1\', DWORD), (\'Data2\', ctypes.c_uint16),\n                        (\'Data3\', ctypes.c_uint16), (\'Data4\', ctypes.c_ubyte * 8)]\n\n        class NOTIFYICONDATAW(ctypes.Structure):\n            _fields_ = [(\'cbSize\', DWORD), (\'hWnd\', HANDLE), (\'uID\', UINT),\n                        (\'uFlags\', UINT), (\'uCallbackMessage\', UINT), (\'hIcon\', HANDLE),\n                        (\'szTip\', ctypes.c_wchar * 128), (\'dwState\', DWORD),\n                        (\'dwStateMask\', DWORD), (\'szInfo\', ctypes.c_wchar * 256),\n                        (\'uVersion\', UINT), (\'szInfoTitle\', ctypes.c_wchar * 64),\n                        (\'dwInfoFlags\', DWORD), (\'guidItem\', GUID), (\'hBalloonIcon\', HANDLE)]\n\n        class WNDCLASSEXW(ctypes.Structure):\n            _fields_ = [(\'cbSize\', UINT), (\'style\', UINT), (\'lpfnWndProc\', self.WNDPROC),\n                        (\'cbClsExtra\', ctypes.c_int), (\'cbWndExtra\', ctypes.c_int),\n                        (\'hInstance\', HANDLE), (\'hIcon\', HANDLE), (\'hCursor\', HANDLE),\n                        (\'hbrBackground\', HANDLE), (\'lpszMenuName\', ctypes.c_wchar_p),\n                        (\'lpszClassName\', ctypes.c_wchar_p), (\'hIconSm\', HANDLE)]\n\n        self.NOTIFYICONDATAW = NOTIFYICONDATAW\n        self.WNDCLASSEXW = WNDCLASSEXW\n\n        def api(dll, name, result, arguments):\n            function = getattr(dll, name)\n            function.restype = result\n            function.argtypes = arguments\n            return function\n\n        api(self.k, \'GetModuleHandleW\', HANDLE, [ctypes.c_wchar_p])\n        api(self.u, \'RegisterClassExW\', ctypes.c_uint16, [ctypes.POINTER(WNDCLASSEXW)])\n        api(self.u, \'UnregisterClassW\', BOOL, [ctypes.c_wchar_p, HANDLE])\n        api(self.u, \'CreateWindowExW\', HANDLE, [DWORD, ctypes.c_wchar_p, ctypes.c_wchar_p,\n                                             DWORD, ctypes.c_int, ctypes.c_int,\n                                             ctypes.c_int, ctypes.c_int, HANDLE, HANDLE,\n                                             HANDLE, ctypes.c_void_p])\n        api(self.u, \'DefWindowProcW\', LRESULT, [HANDLE, UINT, WPARAM, LPARAM])\n        api(self.u, \'DestroyWindow\', BOOL, [HANDLE])\n        api(self.u, \'PostMessageW\', BOOL, [HANDLE, UINT, WPARAM, LPARAM])\n        api(self.u, \'PostQuitMessage\', None, [ctypes.c_int])\n        api(self.u, \'GetMessageW\', BOOL, [ctypes.POINTER(wintypes.MSG), HANDLE, UINT, UINT])\n        api(self.u, \'TranslateMessage\', BOOL, [ctypes.POINTER(wintypes.MSG)])\n        api(self.u, \'DispatchMessageW\', LRESULT, [ctypes.POINTER(wintypes.MSG)])\n        api(self.u, \'RegisterWindowMessageW\', UINT, [ctypes.c_wchar_p])\n        api(self.u, \'LoadIconW\', HANDLE, [HANDLE, ctypes.c_void_p])\n        api(self.u, \'CopyIcon\', HANDLE, [HANDLE])\n        api(self.u, \'DestroyIcon\', BOOL, [HANDLE])\n        api(self.u, \'SendMessageTimeoutW\', LRESULT, [HANDLE, UINT, WPARAM, LPARAM,\n                                                   UINT, UINT, ctypes.POINTER(WPARAM)])\n        class_name = \'GetClassLongPtrW\' if ctypes.sizeof(HANDLE) == 8 else \'GetClassLongW\'\n        self.get_class_icon = api(self.u, class_name, WPARAM, [HANDLE, ctypes.c_int])\n        api(self.s, \'Shell_NotifyIconW\', BOOL, [DWORD, ctypes.POINTER(NOTIFYICONDATAW)])\n        api(self.u, \'CreatePopupMenu\', HANDLE, [])\n        api(self.u, \'AppendMenuW\', BOOL, [HANDLE, UINT, WPARAM, ctypes.c_wchar_p])\n        api(self.u, \'SetMenuDefaultItem\', BOOL, [HANDLE, UINT, UINT])\n        api(self.u, \'SetForegroundWindow\', BOOL, [HANDLE])\n        api(self.u, \'SetWindowPos\', BOOL, [HANDLE, HANDLE, ctypes.c_int, ctypes.c_int,\n                                         ctypes.c_int, ctypes.c_int, UINT])\n        api(self.u, \'GetCursorPos\', BOOL, [ctypes.POINTER(wintypes.POINT)])\n        api(self.u, \'TrackPopupMenu\', BOOL, [HANDLE, UINT, ctypes.c_int, ctypes.c_int,\n                                          ctypes.c_int, HANDLE, ctypes.c_void_p])\n        api(self.u, \'DestroyMenu\', BOOL, [HANDLE])\n        api(self.u, \'EndMenu\', BOOL, [])\n        self._native_ready = True\n        return True\n\n    def _copy_icon(self):\n        candidates = []\n        if self.owner_hwnd:\n            # Timeout protects startup if Tk is waiting for this worker\'s readiness.\n            value = ctypes.c_size_t()\n            if self.u.SendMessageTimeoutW(self.owner_hwnd, 0x007F, 2, 0,\n                                          0x0002, 80, ctypes.byref(value)) and value.value:\n                candidates.append(value.value)\n            for index in (-34, -14):  # GCLP_HICONSM, GCLP_HICON\n                candidate = self.get_class_icon(self.owner_hwnd, index)\n                if candidate:\n                    candidates.append(candidate)\n        candidates.append(self.u.LoadIconW(None, ctypes.c_void_p(32512)))\n        for candidate in candidates:\n            if candidate:\n                copied = self.u.CopyIcon(candidate)\n                if copied:\n                    return copied\n        return None\n\n    def setup(self):\n        if not self._load_api() or self._stop_requested.is_set():\n            return False\n        self.instance = self.k.GetModuleHandleW(None)\n        self.class_name = \'JihuniusTray_{}_{}\'.format(os.getpid(), id(self))\n        self.window_proc = self.WNDPROC(self._window_proc)\n        window_class = self.WNDCLASSEXW()\n        window_class.cbSize = ctypes.sizeof(window_class)\n        window_class.lpfnWndProc = self.window_proc\n        window_class.hInstance = self.instance\n        window_class.lpszClassName = self.class_name\n        self.atom = self.u.RegisterClassExW(ctypes.byref(window_class))\n        if not self.atom:\n            return False\n        self.taskbar_created = self.u.RegisterWindowMessageW(\'TaskbarCreated\')\n        # Hidden top-level windows receive Explorer\'s TaskbarCreated broadcast;\n        # message-only windows do not.\n        # A temporary tool popup can own an active menu without adding a taskbar\n        # button. It stays hidden except while the tray menu is being tracked.\n        self.hwnd = self.u.CreateWindowExW(0x00000080, self.class_name, self.title, 0x80000000,\n                                           0, 0, 0, 0, None, None, self.instance, None)\n        if not self.hwnd:\n            return False\n        self.icon = self._copy_icon()\n        if not self.icon:\n            return False\n        self.nid = self.NOTIFYICONDATAW()\n        self.nid.cbSize = ctypes.sizeof(self.nid)\n        self.nid.hWnd = self.hwnd\n        self.nid.uID = self.ICON_ID\n        self.nid.uFlags = 0x0001 | 0x0002 | 0x0004 | 0x0080\n        self.nid.uCallbackMessage = self.CALLBACK_MESSAGE\n        self.nid.hIcon = self.icon\n        # A wide-char tooltip allows Korean labels without an ANSI conversion.\n        self.nid.szTip = self.title[:127]\n        if self._stop_requested.is_set():\n            return False\n        return self._add_icon()\n\n    def _add_icon(self):\n        self.icon_added = bool(self.s.Shell_NotifyIconW(0, ctypes.byref(self.nid)))\n        if self.icon_added:\n            self.nid.uVersion = 4\n            self.s.Shell_NotifyIconW(4, ctypes.byref(self.nid))\n        return self.icon_added\n\n    def _popup_menu(self, wparam):\n        if self._menu_open or self._stop_requested.is_set() or not self.hwnd:\n            return\n        self._menu_open = True\n        owner = self.hwnd\n        menu = None\n        selected = 0\n        presented = False\n        try:\n            menu = self.u.CreatePopupMenu()\n            if not menu:\n                self.callback(\'show\')\n                return\n            for identifier, label in ((1, \'열기\'), (2, \'돌출량\'), (3, \'세척일보\')):\n                self.u.AppendMenuW(menu, 0, identifier, label)\n            self.u.AppendMenuW(menu, 0x0800, 0, None)\n            self.u.AppendMenuW(menu, 0, 4, \'완전 종료\')\n            self.u.SetMenuDefaultItem(menu, 1, 0)\n            point = self.w.POINT()\n            if not self.u.GetCursorPos(ctypes.byref(point)):\n                point.x = ctypes.c_int16(wparam & 0xffff).value\n                point.y = ctypes.c_int16((wparam >> 16) & 0xffff).value\n            # Explorer\'s hidden-icons panel is topmost. Promote only this tiny\n            # menu owner, not the main app or companion windows. A visible popup\n            # can be activated; the previous hidden 0x0 window could not reliably\n            # bring its menu ahead of that panel.\n            presented = True\n            self.u.SetWindowPos(owner, -1, point.x, point.y, 1, 1, 0x0040 | 0x0010)\n            self.u.SetForegroundWindow(owner)\n            selected = self.u.TrackPopupMenu(menu, 0x0100 | 0x0002 | 0x0020 | 0x0008 | 0x4000,\n                                             point.x, point.y, 0, owner, None)\n        finally:\n            try:\n                if menu:\n                    try:\n                        # WM_CLOSE may destroy the owner inside the native menu\n                        # loop. Do not act on its stale handle in that case.\n                        if presented and self.hwnd == owner:\n                            self.u.PostMessageW(owner, 0, 0, 0)  # WM_NULL\n                            self.u.SetWindowPos(owner, -2, 0, 0, 0, 0,\n                                                0x0080 | 0x0010 | 0x0001 | 0x0002)\n                    finally:\n                        self.u.DestroyMenu(menu)\n            finally:\n                self._menu_open = False\n        # Finish native menu cleanup before any main-thread exit/save dialogs.\n        if self._stop_requested.is_set() or not self.hwnd:\n            return\n        if selected in self.COMMANDS:\n            self.callback(self.COMMANDS[selected])\n        else:\n            self.s.Shell_NotifyIconW(3, ctypes.byref(self.nid))  # NIM_SETFOCUS\n\n    def _window_proc(self, hwnd, message, wparam, lparam):\n        try:\n            if message == self.STOP_MESSAGE or message == 0x0010:  # WM_CLOSE\n                self.u.EndMenu()\n                self.u.DestroyWindow(hwnd)\n                return 0\n            if message == 0x0002:  # WM_DESTROY\n                self.hwnd = None\n                self.u.PostQuitMessage(0)\n                return 0\n            if message == self.CALLBACK_MESSAGE:\n                event = int(lparam) & 0xffff\n                if event in (0x0203, 0x0400, 0x0401):\n                    self.callback(\'show\')  # double-click, select, keyboard select\n                elif event in (0x007B, 0x0205):\n                    self._popup_menu(int(wparam))\n                return 0\n            if getattr(self, \'taskbar_created\', None) and message == self.taskbar_created:\n                self.icon_added = False\n                if not self._stop_requested.is_set():\n                    self.callback(\'ready\' if self._add_icon() else \'failed\')\n                return 0\n        except Exception:\n            self.callback(\'failed\')\n            return 0\n        return self.u.DefWindowProcW(hwnd, message, wparam, lparam)\n\n    def run(self):\n        if self._stop_requested.is_set():\n            return\n        message = self.w.MSG()\n        while True:\n            result = self.u.GetMessageW(ctypes.byref(message), None, 0, 0)\n            if result <= 0:\n                break\n            self.u.TranslateMessage(ctypes.byref(message))\n            self.u.DispatchMessageW(ctypes.byref(message))\n\n    def request_stop(self):\n        self._stop_requested.set()\n        hwnd = self.hwnd\n        if hwnd and self._native_ready:\n            self.u.PostMessageW(hwnd, self.STOP_MESSAGE, 0, 0)\n\n    def close(self):\n        if not self._native_ready:\n            return\n        if self.icon_added:\n            self.s.Shell_NotifyIconW(2, ctypes.byref(self.nid))\n            self.icon_added = False\n        if self.hwnd:\n            self.u.DestroyWindow(self.hwnd)\n            self.hwnd = None\n        if self.icon:\n            self.u.DestroyIcon(self.icon)\n            self.icon = None\n        if self.atom:\n            self.u.UnregisterClassW(self.class_name, self.instance)\n            self.atom = None\n').WindowsTray
SUITE_COMPANIONS = {'protrusion': {'title': '돌출량 현황표', 'sha256': 'ecf6f6ee93a6875fbd481a87a4ee92ab8e015c2639ac1ca749efae31568a10ce', 'compressed': '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'}, 'wash-log': {'title': '세척일보 · 공유 작업장', 'sha256': 'ee259404f24bc90d4a8c3597c46ebb0d070b131eef8df04e02b56cacf4063506', 'compressed': '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'}}

def suite_companion_payloads():
    import base64
    import zlib
    return {key: {'title': value['title'], 'sha256': value['sha256'],
                  'data': zlib.decompress(base64.b64decode(value['compressed']))}
            for key, value in SUITE_COMPANIONS.items()}


SuiteVisualTheme = _suite_load_support('jihunius_visual_theme', '"""Visual-only ttk refinements; existing widgets keep their commands and states."""\n\n\n_PALETTES = {\n    \'secondary\': (\'#253247\', \'#526782\', \'#30415a\', \'#1d2b3e\'),\n    \'accent\': (\'#2563eb\', \'#3575f3\', \'#2f6ff0\', \'#1d4ed8\'),\n    \'danger\': (\'#1b2433\', \'#633b4b\', \'#392736\', \'#2c202a\'),\n    \'tab\': (\'#1d2a3e\', \'#3d516b\', \'#2b3b52\', \'#203047\'),\n    \'popup\': (\'#1b2739\', \'#637b9b\', \'#2b3b52\', \'#203047\'),\n    \'popup_open\': (\'#22374e\', \'#85b4ff\', \'#2b4261\', \'#203047\'),\n    \'mode\': (\'#111722\', \'#26364d\', \'#29384e\', \'#203047\'),\n    \'handover\': (\'#203047\', \'#526782\', \'#2b4261\', \'#203047\'),\n    \'handover_notice\': (\'#352e25\', \'#8e7041\', \'#4b3c27\', \'#352e25\'),\n}\n\n\ndef install_visual_theme(window, style):\n    """Install rounded ttk elements once, preserving every underlying control.\n\n    Call after main, STL and wash styles have been initialized. Image references\n    belong to the Tk root for the entire GUI lifetime. No external dependency is\n    needed: the small antialiased PNG assets are embedded below.\n    """\n    import tkinter as tk\n\n    previous = getattr(window, \'_jihunius_visual_theme\', None)\n    if previous is not None:\n        return previous\n    images = {key: tk.PhotoImage(master=window, data=data, format=\'png\')\n              for key, data in _TILE_DATA.items()}\n    # Ttk tiles the center; large flat tiles avoid thousands of tiny image blits.\n    # Explicit24pxminimum keeps originalwidgetgeometry despite the largerassets.\n    elements = set(style.element_names())\n\n    def element(token, image_key, states=(), inset=0):\n        name = \'JihuniusVisual.\' + token\n        if name not in elements:\n            style.element_create(name, \'image\', images[image_key],\n                                 *[(spec, images[key]) for spec, key in states],\n                                 border=8, padding=inset, width=24, height=24, sticky=\'nsew\')\n            elements.add(name)\n        return name\n\n    def button(name, palette, *, selected=False):\n        states = [\n            (\'disabled\', palette + \'_disabled\'),\n            (\'pressed\', palette + \'_pressed\'),\n            ((\'active\', \'focus\'), palette + \'_focus_active\'),\n            (\'focus\', palette + \'_focus\'),\n            (\'active\', palette + \'_active\'),\n        ]\n        if selected:\n            states = [(\'disabled\', palette + \'_disabled\'),\n                      ((\'selected\', \'pressed\'), \'accent_pressed\'),\n                      ((\'selected\', \'focus\'), \'accent_focus\'),\n                      ((\'selected\', \'active\'), \'accent_active\'),\n                      (\'selected\', \'accent_normal\')] + states[1:]\n        border = element(name.replace(\'.\', \'_\') + \'.border\', palette + \'_normal\', states)\n        style.layout(name, [(border, {\'sticky\': \'nsew\', \'children\': [\n            (\'Button.padding\', {\'sticky\': \'nsew\', \'children\': [\n                (\'Button.label\', {\'sticky\': \'nsew\'})]})]})])\n        style.configure(name, borderwidth=0, relief=\'flat\')\n\n    for name, palette in (\n        (\'TButton\', \'secondary\'),\n        (\'Accent.TButton\', \'accent\'),\n        (\'Secondary.TButton\', \'secondary\'),\n        (\'Danger.TButton\', \'danger\'),\n        (\'DriveSmall.TButton\', \'secondary\'),\n        (\'AppTab.TButton\', \'tab\'),\n        (\'Selected.AppTab.TButton\', \'accent\'),\n        (\'Popup.TButton\', \'popup\'),\n        (\'Open.Popup.TButton\', \'popup_open\'),\n        (\'HandoverToggle.TButton\', \'handover\'),\n        (\'HandoverNotice.TButton\', \'handover_notice\'),\n        (\'STL.Accent.TButton\', \'accent\'),\n        (\'STL.Secondary.TButton\', \'secondary\'),\n        (\'STL.Danger.TButton\', \'danger\'),\n    ):\n        button(name, palette)\n    button(\'Mode.TRadiobutton\', \'mode\', selected=True)\n\n    # Existing foreground semantics, notably notice amber and radio selection,\n    # remain inherited from the original style definitions.\n    style.configure(\'TButton\', padding=(14, 7), foreground=\'#e7edf7\')\n    style.configure(\'Title.TLabel\', font=(\'맑은 고딕\', 20, \'bold\'))\n    style.map(\'TButton\', foreground=[(\'disabled\', \'#879ab7\')])\n    for name in (\'AppTab.TButton\', \'Selected.AppTab.TButton\'):\n        style.configure(name, padding=(18, 7), font=(\'맑은 고딕\', 10, \'bold\'))\n    style.configure(\'AppTab.TButton\', foreground=\'#a7c9ff\')\n    style.configure(\'Selected.AppTab.TButton\', foreground=\'#ffffff\')\n    for name in (\'Popup.TButton\', \'Open.Popup.TButton\'):\n        style.configure(name, padding=(14, 7), foreground=\'#cbd9ed\',\n                        font=(\'맑은 고딕\', 10, \'bold\'))\n        style.map(name, foreground=[(\'disabled\', \'#879ab7\')])\n    style.configure(\'Open.Popup.TButton\', foreground=\'#dbeafe\')\n    style.configure(\'HandoverToggle.TButton\', background=\'#203047\', foreground=\'#a7c9ff\', padding=(16, 7))\n    style.configure(\'HandoverNotice.TButton\', background=\'#352e25\', foreground=\'#f5c26b\', padding=(16, 7))\n    style.map(\'HandoverToggle.TButton\', background=[(\'active\', \'#2b4261\')])\n    style.map(\'HandoverNotice.TButton\', background=[(\'active\', \'#4b3c27\')])\n\n    def field(name, kind):\n        border = element(name.replace(\'.\', \'_\') + \'.field\', \'field_normal\', (\n            (\'disabled\', \'field_disabled\'), (\'focus\', \'field_focus\')))\n        if kind == \'entry\':\n            children = [(\'Entry.padding\', {\'sticky\': \'nsew\', \'children\': [\n                (\'Entry.textarea\', {\'sticky\': \'nsew\'})]})]\n        else:\n            children = [\n                (\'Combobox.downarrow\', {\'side\': \'right\', \'sticky\': \'ns\'}),\n                (\'Combobox.padding\', {\'sticky\': \'nsew\', \'children\': [\n                    (\'Combobox.textarea\', {\'sticky\': \'nsew\'})]})]\n        style.layout(name, [(border, {\'sticky\': \'nsew\', \'children\': children})])\n        style.configure(name, borderwidth=0, relief=\'flat\', bordercolor=\'#526782\',\n                        lightcolor=\'#526782\', darkcolor=\'#526782\')\n\n    field(\'TEntry\', \'entry\')\n    field(\'STL.TEntry\', \'entry\')\n    for name in (\'TCombobox\', \'Wash.TCombobox\', \'STL.TCombobox\'):\n        field(name, \'combo\')\n        style.configure(name, arrowcolor=\'#b8c8df\', arrowsize=13,\n                        background=\'#253247\', fieldbackground=\'#131c2b\')\n        style.map(name, fieldbackground=[(\'disabled\', \'#263144\'), (\'readonly\', \'#131c2b\')],\n                  foreground=[(\'disabled\', \'#75849c\'), (\'readonly\', \'#e7edf7\')],\n                  selectbackground=[(\'readonly\', \'#131c2b\')],\n                  selectforeground=[(\'readonly\', \'#e7edf7\')])\n\n    for name, key in ((\'RoundedCard.TFrame\', \'card\'), (\'NavRail.TFrame\', \'nav\')):\n        border = element(name.replace(\'.\', \'_\') + \'.border\', key)\n        style.layout(name, [(border, {\'sticky\': \'nsew\'})])\n        style.configure(name, background=\'#1b2433\' if key == \'card\' else \'#1d2a3e\', borderwidth=0)\n    # Flat Card.TFrame remains untouched, including inner borderwidth=0 frames.\n    badge = element(\'status.border\', \'status\', inset=6)\n    style.layout(\'Status.TLabel\', [(badge, {\'sticky\': \'nsew\', \'children\': [\n        (\'Label.padding\', {\'sticky\': \'nsew\', \'children\': [\n            (\'Label.label\', {\'sticky\': \'nsew\'})]})]})])\n    style.configure(\'Status.TLabel\', background=\'#203657\', foreground=\'#a7c9ff\',\n                    padding=(8, 1), borderwidth=0)\n    style.configure(\'CardTitle.TLabel\', background=\'#1b2433\', foreground=\'#e7edf7\',\n                    font=(\'맑은 고딕\', 20, \'bold\'))\n    for name in (\'Vertical.TScrollbar\', \'Horizontal.TScrollbar\'):\n        style.map(name, background=[(\'pressed\', \'#607690\'), (\'active\', \'#536781\')])\n    result = {\'popup_icon\': images[\'popup_icon\'], \'images\': images}\n    window._jihunius_visual_theme = result\n    return result\n\n\n# Generated by qa/design-refresh/generate_theme_assets.py; no Pillow at runtime.\n_TILE_DATA = {\n    \'secondary_normal\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAC7ElEQVR4nO3dX0/bVhiA8ec4xzZpyb8mFUjVqpYgQaQhqCr1+3+BqtLG6DpRMg0ymjQkwcGZYhu/u0hBu9rNWmXlfX+35+ZI5/GxffW6Z7uvBcA5x22RI0Crs0WjvUUYRogI5vsmIiTTMZPRJUW+JIzi+3N1z3Zfi3OOPFtSb3XY6b0i2qiySG/Iswzn3Jq3b/4TEYJKhUebNUA4Pz3h00Wf6EsE/u7wt593ebl/xHDwB+MPv1DkOWBP/8PgCIKARrvDi71D6q02p8dv8WGEvy0K6q0OL/cP6X84ZnY1Jopjwiha967NVzYdj7i5ntE7ekM6T/jz99/wgrDTe8VocM711ZiNapWyLO3d/wCFYUyRZ3z89We6ez8yHV0StNpbRHGV0acBYRxTluW692m+EZESH4akyYzFImX7eZeg2dlisbjhtsjtg08J5xzz2YTGk6cEPozIswzsylfEkWVLAu8JRMSefIWcc6tfxHVvxKyXBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaCcBaDcKgAbFqHPlzMPRISg4gEbGqFJ4D0iQpBMxzx6vImrBHYRKCFSUqs3SZMpwWR0CU5otp5SFBkusM+Ch8o5R1mWRBtVavUmw4s+vsiXnJ+e8GLvkJtkSpFneB+ue6/mGyjLktsip7t/wNVowPXkMz6MYobnfWqtNvtHbzh7/xPpPAF3N1ho3ds2X4NISRRvsNM7wDnH2cm71ehYESGMYz4ev+WveUK3d8AiTZnPJuTZEmyi2PdNhErFs9loUms0uRoOOHv/7v5V7/45Pj7PllQfb7L9wy71Jx0qFc/qCvi3CGz9/72+Gh+fJlOGF/27a/9+7W+dFhDP6ukq/QAAAABJRU5ErkJggg==\',\n    \'secondary_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACx0lEQVR4nO3dSU8bMRiA4dfOzISEJYSUTWwloqiFC4j//xdaLqhIhZKyrwlkAZKZyddDIOqpJ9SUfN9zjBXJkl97fLNbWNsRAOccaZIAQqE0y2RphiAMERHMe+YQ6dKo3VG7vSTutAmjbH9dA+gtftzpMFEssfp5i5HRcdrtZ9IkweH4WwIObPw/HgfB+wyluSWWk4STgz2uzir9CILe4reZWyqzurHN/V2V658HL6eBGRbOe8YmCpQ3dxgvljjc+0oQRgRpkjBR/EB5Y5uL01Oa9fveQBgOes7mDYkIjYcaT60mH9fWeWzWOa/8IBCE1S9b1KpVmvWH/tFg3/7hEwQhaZJwdlxhaW2T6vUFfrI0y0hunPu7W7v0DTkRIRMEPLVaxJ2YueUyfrI0Q+f1wufcoOdo/gHnHK1Wk0JxGh+EIbFd+NR4PeGTOMYHIV5EbOcr5JwDEfygJ2IGywJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzgJQzosI3lsH2njvERF8vXZHNjuCe/nBDDfnHCJCLj9Kq17D124u6aYdxiYKpKk9HDXsut0uYRSRy+e5Oqvgk7jNyeF3Zubm++/KOefAQhgezvV3fjdNmV9c5vbimHr1hiCMslydHjE+OcXK2jrnvyo8PbZ6fxr0xM2bEHqvhUVRxMLKKkn8zNH+bu+FWBEhjLIc7n3jsVFn+dMmnTih1WyQxrGdBO+dCD6TIZcfJZfPc3txzNH+bv9T7/58Pj7utMmNjjG7WKYwNU0mCLB74fvm6O3+Zr3G9VmFh96x3x//DaF7E+PaDz6YAAAAAElFTkSuQmCC\',\n    \'secondary_pressed\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADD0lEQVR4nO3dzU8bRxiA8WdmZ9cmtI4NG0GJGoogKUUiKCLKKf//qWmkprLSigQUQ8CuWfxRJO8HMz1QkvTgpIdGTvy+v+tIuyPNI+3O6TV3t/YDgDGGq6okAK10lebyCi5JCN5jjGGaEIKuf8HrAMF7hhd9st4pVZkTJzVCCACYu1v7wRhDWeQ0WimbO4+IkjqX4xFFPsFYA2HKk2/eq+tf7noIRJFj8dvbWGvoHLQ5O35NktQJIeBuDn/13iYb23scH72i+/YNVVkQpj1YfV0M2ChiaXmFHx48pNFKOfjtZ1yc4K6qkkYrZWN7j99f/ELW75LU6sRJbdbbVv+z894po0HG3pOnrK3f5+ToD1wANncecXz0iqzfpb5wC+/9u2+Emh9xrUZVFLx88YyfHj7mvHeKbaWrREmd7ts3JLU63vtZ71N9JsF7XJwwHlzw13jI2vomtpmucDkeUZXFJ/8m1Ty4vjUMsz6NpTvYOE4o8on+8EliIM8n2Mhh/8s9Us0fYwyEgJ31RtRsaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCaQDCWUDnAwl0c+Y2BI9z7v0MOiWCc+56YMQw67PYuE1ko6nzB9V8CT7QaC5zOR5gs94p1hha6QpVkWOt/hbMK2MM3l9RW1ig2Uo56xziqjKnc9Bm48Euo0FGWRS4OJ71XtVn4L2nqiq2dx+T9U4YZD1cnNTodg5ptFL2njzl5a/PGI8uMBiMMQT9MHzVDNdnGLynVr/Fj7v7xM7Rbj8njpP3w6OrsmBt/T7fb+0wHo8YZn+STyZYaz6agGH67GJdn/06IRC5mEZziWYrJeud8Lr9HPPPp958OD6+LHIWFr/hu3tbNJbuEEVOr4hzIXA5GnDWOWRw3v3XXOi/ASp9QpkIT4IvAAAAAElFTkSuQmCC\',\n    \'secondary_disabled\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACe0lEQVR4nO3dzXLaMBSG4VeysPkrUEgmTbrtHfT+76bNdBoaiAFjbCx14TQ30GmZcL5nCwvNnFce7Y77/OVrAsA5UtcBUIynDEdTfJZB/6u8Vw5SSjTHimNVEmOHzwKkfrCh/5Mjns8UozGLm8+EQU53bomxw+EueXz5S4mEc57xZM4s3VE+/+RQPveXGwjQD386X7G4eeB03FPuNqQYSbr+V8LhnCMvRny8faAYjtk8fcP5jJBiRzGasLh54FD+ojkd8T7Dea+7f2WauqJta+bLe9qmZrdd44HXm797HX649DnlH3Hek2Jkv31itvxEyHN8MZ4yGOTU1Q7vM/Tqu27Oedr2ROzOTGcr/HA0fX3wxUufTf4T5xxtU1OMJnjvg4ZvUIwdznm8Pvm2+UsfQC5LARinAIxTAMYpAOMUgHEKwDgFYJwCME4BGKcAjFMAxikA4xSAcQrAOAVgnAIwTgEYpwCMUwDGKQDjFIBxCsA4BWCcAjBOARinAIxTAMYpAOMUgHEKwDgFYJwCME4BGKcAjFMAxikA4xSAcQrAOAVgnAIwTgEYpwCMUwDGKQDjFIBxCsA4BWCcTynhnPaDWfNn5v5UH8hCrggMSSkxGBT9lri62hFTJC/GpKTdQdcvkWWBMCj6DaKx6yiffzD+sOj3yimCq5VSIsbIdLai2m85HfcEnwUO5YZiOGG+vGf/subc1IBDq0OvROp3CGdZYDK/JcbIdv2IzwIBEj4LbJ6+0zY1s+UdsTvTNjWx60Bvg/ct9cujQ14wGBRU+y3b9ePbXF/3xCac9+xe1hyrkulsRTGaEPLh25pxea8ckGhOR7brR07Hw9vmcIDf5rLckVmhXHEAAAAASUVORK5CYII=\',\n    \'secondary_focus\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAD8ElEQVR4nO3dT0ybdRzH8ffv97S0pe3YmHHyZ8wglDA8iJDODCSe3DKNgZglO3iYOxoPHnbQg8aTXrzsogcvBpeoMerigtFlIXPRuS3YZrhEYRtgli2Aiy2hQIH2+XqA1h3gZtza3/d1aA+/5smT/D55nj6f5/A1TW09AmA9j7WVHGBpau+mse1pQpE44gPGsCWRjW9df3jXDfjFInMz17g9+Sv5pQyR6E58vwhAAMBaj5XFDA2t3fQPvc6+rmeJxMDYrY+rKozAWh5mpye4PPIxf1z5lnB0JyI+Zm/HAVlZzNB18GWeP/42O+oj/HUny8z1n8ll57A2gCBbHtdsfur6w7su4hMMRWnpfIbG1haKRfjl7GkufvkeNeEY5tGW/bKnpYtjbw4TDIW5duFr0qOnWcrOI+JveWBVYYwhFI7RkXyB5OETxHfHOPvRu4z/+BkBg6F/6CTx+jBXRs5w4Yv3icR2EY7WPejTVv8hEZ/U+WFWlxc5dPwt+gbf4M/ffyLQ1N7Lvq5e7t3Jkh4dJhLfhfUC5T8JqkoYQ7z+MW6kfqC95wiJnm46ky9hG9t6iMQsM9cvsZSdx/OCiK+X/qojAiKI73Mz/T0iQnMiiQ3VxjEWFrOzes+vcoJgrMfSwj38giEU3YGVzUu99QIP+PTU/0MwngcGxC9iSw8T5VJBVb/yXhu06nGcBsBxGgDHaQAcpwFw3H0B2OaVoqpC/+61pfQmSfffHeW9Fu0BnKQ9gCrRADhOA+A4DYDjNACO0x7ASdoDuE17AMdpD6BKNACO0wA4TgPgOA2A47QHcJL2AG7THsBx2gOoEg2A4zQAjtMAOE4D4DjtAZykPYDbtAdwnPYAqkQD4DgNgOM0AI7TADhOewAnaQ/gNu0BHKc9gCrRADhOA+A4DYDjNACO0x7ASff3AJsz50R0RIwryoNBjMH6xQIiQk0oil4FXCAEQxGMAb+wjp2bGWc9b2jpPEgoEsMXf/tJlKqiWePhF4s8vn8ALwiz0+MEbk9cZXZ6iuZEKx3JF0md/4R4fQOyOWRILwoVTgBDeVZQQ2s3id4Bcn+vMzn2HYF8LsPlkQ8ZeuIDkodfZXV5gRupcxtjRY0H20ylVJVDEKTo09j6FANHTxKrC3Hxq0+5eyuF2ZtIykouw3PH3qF/8BUK6zD121VupkdZWpjX0bEVvi7iE6ypZV9XH4neQ8TqDBNjab45dQKMxTS19YgxlrV8jif7j9I3+Bq7G/cgAn4BvQVUAWPAC0Ius0p69HMunTm18QRgNwOw8SNLfnmBukda6DxwhOaOJOHaOnSGZGUzBorFArNTKSbHznH3VpqaSAxrLSLCP0Mqo6DUbLbvAAAAAElFTkSuQmCC\',\n    \'secondary_focus_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAD8UlEQVR4nO3dTUxcVRjG8f85d4a5zECHqplqh1JLB0wLYpuphQQW+BEXmpiiUVmYmLgz2sSFCzcaV67cNCa6cKcmmrSNRls/EmNspYjSlrYBKyQVCElL05IRGBg+Zu7rYqawEVaNwJz3t32TuTeZ586c89zFMclUWgCs57GUywKWZMNBdqbSRKLVSAEwrE10vpnnBgiCPJNjl5kYvsDCXIbKWA1BUAAgBGCtR242wwP1B+l47ii793fgx8DYdS6stg6BpUW4OTpM3+lP+Ov3b/BjNYgEmF0PtUpuNkNT+/M89co7VG+vZOrGDBPD/cxP38J4XjFl/8WsXkDnm3MuQUA4UkkylWbHg0mCPPx26nPOHn+fCr8Kk6jbLzvqmuh++1PCEZ8/e79nqPckczO3Qdb6ZLVllEJS4ceob3mCA491U31PjG8/fo8rZ74gZDB0dL1F9XafCz/9QN+pD/GjcSLRbRt74+quEgkYOneCpYU5Ol98g/YjbzJ+tYdQsuEQu5sOMXVjmqHeE/ixONYLIaVFgioTxhCLJxgdPMOehx9nb0sz+1qfxe5MpfFjlonh88zP3MZ6YSQINvp21d0mgiAQFBgf/AURobbhMDYSrcZYmJ++pf/55U4ErMd8doogb4jE4tg7P/XGC23w3an/h2CMV9ohFLAry0R9+h1y57s2aNXjOA2A4zQAjtMAOE4D4DgNgOPsypbArPfSWZWX1deI2gM4SXsAVaIBcJwGwHEaAMdpABynAXCc9gBO0h7AcdoDqBINgOM0AI7TADhOA+A4DYDjtAdwkvYAjtMeQJVoABynAXCcBsBxGgDHaQAcpz2Ak7QHcJz2AKpEA+A4DYDjNACO0wA4TgPgOO0BnKQ9gOO0B1AlGgDHaQAcpwFwnAbAcRoAx61sA0X0lBBXiKx2P1aCPCJCOBJd/4BCVR4EwhU+xkCQX8ZOjl1hedGQTKUJ+zGQQFvBMmWshwQFko1teGGYHLtMaGL4D26O/k2yoZ69jzzJYM9xquIJxIi2g+XCgDGW3OwUid3N1Le0ks0sM9L/HaGFbIa+0x/RdfQDDnS+xFJulrHBswRSwBqveNKU2rIMxedYggKJuibannmNqniEX09+xvVrFzG7Gg9LLpuhs/td2o+8TGEZxq9eYmyoh9zMFMZ6bOqzUXW+7lwkIFzhU9vwKHtaOonVGEbOD/DVsVfBWEwylRZjLEsLWZo7XqC963XuvT+BCBQKui7c6oTiki4Uhuw/i1z6+UvOfX2suAOwpQBA8T9iYX6a+H117Gt7mtrGVvzoNopnSK4Vg9W3SjrfnHNjoFDIMzk6wEj/j1y/NkBFZRXWWkSEfwHk1XzjQrbkhgAAAABJRU5ErkJggg==\',\n    \'accent_normal\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAC00lEQVR4nO3dvW4TaRSH8ee8M54h2CYWJpEQFHxKKRIB8W7BPSAh7S1Q7krsFXAHVHRwCdCCuAQEBYoIHSJJiSDBTjyJ58Pv2cKhRFQLwef8WluWpXkk+/1PMXLh2kABkARtCgDypXXy5XVCdgbiFITvU/z1k/w6ArGh3H3H5NMbYjki5D3QKQDp7D0JsRqS99dYvHGftD9gGltE/cFnuxNPARFYuD5Fi4/sv39Csf38OIJI+u3ity/fpffnA8oqZ//rEI0R/WFd7sQ7voYiQrZwid7th2T9VYZvHyKtDqk2BXl/jd4fDygOItXkCyFpISHxaz9nqsMD6smYxZV7NPtbHHx4SgDo3fyXss6pJgUhaf3q7+n+JxISNMJ4b8SZtX9I2xcJ+dI6ydlbTMZDv/gGSAjU1YRpco72lTuEU8vrTGNGjPFXfzf3kwhCXdXkSwOCZN3Znz1nSowRaXUJ386DziCdEvycZ5nMTgHOLg/AOA/AOA/AOA/AOA/AuDC7XeRsUt8BbPMdwDwPwDgPwDgPwDgPwDgPwDjfAUzzHcA43wHM8wCM8wCM8wCM8wCM8wCM8x3ANN8BjPMdwDwPwDgPwDgPwDgPwDgPwDjfAUzzHcA43wHM8wCM8wCM8wCM8wCM8wCM8x3ANN8BjPMdwDwPwDgPwDgPwDgPwDgPwDg/BpomBGKDeAPmiADaEMrdTZIQEa/ADEVpZTn13iZh8uk1WnwkW+ig0R8fM/dUSZKUVI4odl4SYjli//1jTndOIUFQf3rY3FJVYmxon+1zuPWU8vMGach7FNsvyPqrLK7cY7w3oimPQPyAME9UlSRNaZ87j+6+YrTxiJB1kQvXBooEYj2me/Uvuqt/E9Ml6qomTqMfEuaACKRZRkuOONx6xnDj0ew2kITjAAAkEKsRaeci7Ut3yJcHhFYXVf9J+L0JaEO9t0mx85Ly8wYh6zCbgJT/AFwG8ga1BkQQAAAAAElFTkSuQmCC\',\n    \'accent_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAC0ElEQVR4nO3dzU4TYRSA4fc77cwQ2vITqC5wgUY3RCTQ4FUQF94CS030DrgCV+408QZkS+IduNDEoJC4sJGwI4QIhUI7nZnjYmriBl0pP+c8my6+ZDpJ3850ThdfmLnbUgBCBc26QCBpLpI0l5C4gWoOBM6nvn6p1wHNSQ++0Nv7SJEeIvEEaA5AFYBQoUgPSabmGV94RjTdAkmGB/7TG+jw1dcv9zrUycg6bY63X9Pd2UCSCdCCMHPvoRbpIbXbj5hcXqOQUbJeB1UF1XMO7K6UAIGAxDWiKOLk6xsOP70gRHWqmnVJpuaZXF4jy4W894MgVUIIf72yuKslT7sUA6jPrTLofOfk2zoCgfGF5xRhlHxwRpDqRZ+n+0dCEFBIT7uMzT+lWp9BkuYi0fQSWa/jH74FQSiyHjJyg9HZFSRuLoEkqBYXfWrufwlCkWckzRYicQO/2dujqkjcQH49DzqDNC9/BDqrAnLRp+AulgdgnAdgnAdgnAdgnAdgnPz+l6GzRn0OYJvPAczzAIzzAIzzAIzzAIzzAIzzOYBpPgcwzucA5nkAxnkAxnkAxnkAxnkAxvkcwDSfAxjncwDzPADjPADjPADjPADjPADjfA5gms8BjPM5gHkegHEegHEegHEegHEegHE+BzDN5wDG+RzAPA/AOA/AOA/AOA/AOA/AOH8MNC0gaIYPg4zSDOkfbBHIy23inA2qSCWif7CFpHsfyDptKnFtuE2su9603B0u73K2+w7J+0ccb7+iGkUEgu8edq0pWmTEtTFO22/p729SlWSc7s4G8dR96nOrpGddikEf/JZwvWj5zU8a0wz23nP0+SUSNwgzd1tKEHRwQu3OY8YePCGM3KTIMyjUHxKuCamUl/3T9jpHn19SPgDKMAAoNxNMj6jWb1GbXSFutpCoUW4z/qergaqvX+Z1GG4fv8Xp7jv6+5tIXKccASk/AfEQCwe/rq7xAAAAAElFTkSuQmCC\',\n    \'accent_pressed\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADB0lEQVR4nO3dzW4bVRTA8f8545kxxI5NSFOkIgRt6SoKKiNeoyx4gy5hAS/QB0Bi1SW8AYuuKvUNWFSCVpWyQUJOqECRGux8eHDm614WTpeEDVJSn/PbXslj6f5nxj6bKzduFxEASYhNCUB+vaC/VaDZEGIHCP8u+vpVXheIoaM+fMHi4CmhOkbz8fm+gty4XUQkIVRH5Js7jO9+ja5/QlNB1wZEZHmNCy7g61d3PRJRFdJ+gtS/c7L7A+Xk8XkEgd7rzR/c+pxR8YD5tKX87Q9C2/3Hld2bQxAV+qMNRp99S765zfTn79B0QC+2JfnmDqNPHzB9ecTZyYwkzdG0d9nf2v2fIixmf1HNj9i6c5/h8YTTX3+kR4Tx3W+YzzrOTo5Isj7E6Df/CtI0JbQt0719Nra/YvHnT2j/eoGu71AeHpCk2XLz3WqKEe0l1OUpTbvO4NY9NN8qaCqW7/yLfmy61SFCdVqSXytQzYaEJuLPfCMigNA1DZIOUKLf+SaJQOxQ333LBL3sr+AulwdgnAdgnAdgnAdgnAdgnPoAyLLocwDbfA5gngdgnAdgnAdgnAdgnAdgnM8BTPM5gHE+BzDPAzDOAzDOAzDOAzDOAzDO5wCm+RzAOJ8DmOcBGOcBGOcBGOcBGOcBGOdzANN8DmCczwHM8wCM8wCM8wCM8wCM8wCM8zmAaT4HMM7nAOZ5AMZ5AMZ5AMZ5AMZ5AMb530DTBI2xRfw5YI6oQGzR+vDF8lBB9aGgCQLEQL62Rj3bRRcHT5H6Jf3RBqFr/Y2w4mKIJFlO/nagnDxBQ3XMye73jN7bRHsJse2W58l4CKtDABFijMSu4Z0PPuRs/xHVq2f0NB9TTh6Tv7vN1p37TPf2qMv5MgKvYHXEQJLljD+6iS5+Yfb8IZoNXx8erYR6zvDjLxhuf0nTrlOd/k3XNuenS13wwVf88GTz64CqkA3WyN8KnO0/YvbsISIKoucBAIgSqmN6w/cZ3LxHfq1A0oEfH//GrwOxo57tUk6eUL16jmYDliOgyD+GHytU4v9dDQAAAABJRU5ErkJggg==\',\n    \'accent_disabled\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACe0lEQVR4nO3dzXLaMBSG4VeysPkrUEgmTbrtHfT+76bNdBoaiAFjbCx14TQ30GmZcL5nCwvNnFce7Y77/OVrAsA5UtcBUIynDEdTfJZB/6u8Vw5SSjTHimNVEmOHzwKkfrCh/5Mjns8UozGLm8+EQU53bomxw+EueXz5S4mEc57xZM4s3VE+/+RQPveXGwjQD386X7G4eeB03FPuNqQYSbr+V8LhnCMvRny8faAYjtk8fcP5jJBiRzGasLh54FD+ojkd8T7Dea+7f2WauqJta+bLe9qmZrdd44HXm797HX649DnlH3Hek2Jkv31itvxEyHN8MZ4yGOTU1Q7vM/Tqu27Oedr2ROzOTGcr/HA0fX3wxUufTf4T5xxtU1OMJnjvg4ZvUIwdznm8Pvm2+UsfQC5LARinAIxTAMYpAOMUgHEKwDgFYJwCME4BGKcAjFMAxikA4xSAcQrAOAVgnAIwTgEYpwCMUwDGKQDjFIBxCsA4BWCcAjBOARinAIxTAMYpAOMUgHEKwDgFYJwCME4BGKcAjFMAxikA4xSAcQrAOAVgnAIwTgEYpwCMUwDGKQDjFIBxCsA4BWCcTynhnPaDWfNn5v5UH8hCrggMSSkxGBT9lri62hFTJC/GpKTdQdcvkWWBMCj6DaKx6yiffzD+sOj3yimCq5VSIsbIdLai2m85HfcEnwUO5YZiOGG+vGf/subc1IBDq0OvROp3CGdZYDK/JcbIdv2IzwIBEj4LbJ6+0zY1s+UdsTvTNjWx60Bvg/ct9cujQ14wGBRU+y3b9ePbXF/3xCac9+xe1hyrkulsRTGaEPLh25pxea8ckGhOR7brR07Hw9vmcIDf5rLckVmhXHEAAAAASUVORK5CYII=\',\n    \'accent_focus\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADp0lEQVR4nO3dT2ibZRzA8e/z5M/bpM0ycW4u7fpH25Q6GWi3VmwdnvTioZsgOwiCV1HwIl4UT548KAgePDoQFPzDCt5Eh2hHXeMGWtttts3G6KhQtEmbxLzPz0PbCbLtpKzN7/c5JIcH3gTeb3jz/gJ5XGf/sAD4RILGRgXwdA48SqH/KFE2hwTAOW5JZPPZ1nfuuoMQx9xY/Imrc9PUqqtk2vcSQgxAEsD7BBtrqxx84BHGT75Cz9DjZLLutsc1u4xAowHL5XmmJj/k13Nf0ta+F5GAOzQ4Khtrqxwee5anXniDPfkMKyuBxWs1Kusx3v8T2r9tB2LrO3ddBFJJR3ehjcL9SWKBHyZPc/bTt0m3deD2dx+WA90Pcer1j0ilIy78XKE0V6dajbnNcc0uFKU9g71pRo60k7snwZkP3uLitx+TdMD4ydfI5SPOna/wzY/rZCJPW+Tv9ns2/yERmJmtUW8ITx/PMXbiVZZ++Y5k58BReoaG+X0lpjRbJxN5vIdgH/+Wk2v3XFpqMLDUoDiQZ+ixCXxh4BiZrGPxWp3qekziDtd8s8sJCMLlch0JQtfgKD7K7sE5WFu3a36rE8A5R3VDCMERZXN42bof9HbLp8bNu4cQ48HOvF4O+6qvnAWgnAWgnAWgnAWgnAWgnMfGP4qJzQF0szmAehaAchaAchaAchaAchaAcjYHUM3mAMrZHEA9C0A5C0A5C0A5C0A5C0A5mwOoZnMA5WwOoJ4FoJwFoJwFoJwFoJwFoJzNAVSzOYByNgdQzwJQzgJQzgJQzgJQzgJQzuYAqtkcQDmbA6hnAShnAShnAShnAShnASjnt/883nYJ0ePmuXYOH+ImIkI6ZfMALVIphwNCs4m/sXCBvxqb+8pFKU+42+/O/G+8gxCE3kKKRAqWFy6SvDo3xXJ5ka4HexnsSzMzWyPX7u2S0GKcg2otcHBfimJfROXPJvPTZ0jWKqtMTb7PiZffYeRIlnpDuFRubG47a1eFliACIkJhX4rjx7J05BOc/ew016/M4A4VR2SjssqTp95kfOJ5mnX4rVzjcrlOdT1sbR176xKck60XsPWdur69dWxPIU2xL0tHHubOl/j8vRfBeVxn/7A452nUKjz8xHOMTbzEvQfuQwKEGPutqAU4IJGEylqN0tef8P0X727eAfitAACc89Sqf5Df383Q6DN0FUdpy+YId9w+fuvB1nfsunMQx02WF0rMT3/F9Ssl0tkOvPOICH8DhXucbAmY3N0AAAAASUVORK5CYII=\',\n    \'accent_focus_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADm0lEQVR4nO3dT2ibZRzA8e/z5M2bP22zMVnLltTNdF0pDpx2s5NM2GknYX8E8TAYeBURL7tNb5487ODNqyjooYgFj+JQVimzM27iykq6FbLsUIM2aZI3yfN4SOMua69r8/t9Dr08kBaeb9637y+Qx2SPzXgAG4sRNWqAJTv5GocnT5FIjeAdYAzP5Ld+6PquXTcGnOtQKd1h7f4izXqV1NB+nOsCEABYG6OxUeVQ/lXOXv6QI9NvkEwZrNn6HWrPMvT2MIrgyaNlFua/4K9fvyM5tB/vHWZ8atY3Nqq8XHib81evM5JJsb7uWKtE1Jtuxwj63en67l13HsLAkB2NMzYa4Dzcmv+Sm99+SpgcJmg1ahzKv8L5q58QDxPcLm5yr9Sh3nDbvKzaSzy9EIoPIiayASenkhQuXOHvxw8o/vQ1gQHOXr7GSCbB7WKDW3dbJENLItzmvqL2nP6V4O5KRNSGc6dTFC59xMM/fybITp7iyPQM6+td7pXaJEOLteD15j8w+ls5lLaUym1eKseZOLqP6TMXsYcnT5NMGdYqbeoNp5s/wLwHB6yWI7zz5KZmsYl0BmOg3tR7vgQG2Gx6nDMk0iNYv/U8uN2jpBo8/b32rot9+jCh5DHY5/0nqOdLAxBOAxBOAxBOAxBOAxDO6ge+knmdA8imcwDxNADhNADhNADhNADhNADhdA4gms4BhNM5gHgagHAagHAagHAagHAagHA6BxBN5wDC6RxAPA1AOA1AOA1AOA1AOA1AOJ0DiKZzAOF0DiCeBiCcBiCcBiCcBiCcBiCczgFE0zmAcDoHEE8DEE4DEE4DEE4DEE4DEM72vzxeTwmR4/+9Ngbrux2898QDnQdIEQ9M7yCpTgdbKf1Ou907Vy6MawSDzJjeuz83FhCLQ6VUJFi7v8CTR6tk80eZyAb8sRIxnLI6IB4wxkCj6Rk7ECOfC6n922F58XuCZq3KwvznXPrgM05OJWi1PauPOziHniA2QLyHsQMxzpwIGc5Ybs59RXnlN8z48dd9o1bl3LsfU7hwhW4LHpZbrJY7bLZc73/E3Xw2qq7vuO59756fOxiQH08ylIHlpSXmbrwHxmKyx2a8MZaoWePEm+9QuPg+L4wexDvoOv2oaK/z9C7/QQC1jSZ3fvyGX+Zu9J4A7FYAAMZYmvV/2Df6ItOzb5E7PksyncE5dq7A6/puXjdAt9uhUlpiefEHyitLhOlhrLF47/kPSodj9PyNChYAAAAASUVORK5CYII=\',\n    \'danger_normal\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACrklEQVR4nO3du2vbUBSA8e9eSVfGj9hEcTJkSptCKc0UCN3y/6dDoVszlHopbh5+EMWRrux7OzhuM7VDCyE+5zdaMgj06XK2Yw6PTyOAAZYxEoH9PGc/z8mMJaJeMgMEIrfeM64qfAjk9vd7TTc3+RDYdY6T/oDMGOZNQxVWGMyzPbz6d5FIaizHnS5vuz0uy5Jvi/tfEaQGqEPgqNPhXW+Hy7JktLjHh6Bf/5YwQGIMB60W73f67LqMT7MZzlrSZYwUzvGut8PH6YRxVdFKEnJrn/u51X/2/eGBSe05Hw551e3ytSxJI3DS73NZ3jGuKtpJQgD9+rdQy1p8DFxMJnwoCn5UFXYz7I0WC1qPL19tpwA4Y5g2npn3HHU66wDmTYMPQcc9ATYn+7WvKTKHzYyl0oFPFAM8rFakxmDj4w9KFsP6NNBRXzgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgNQDgLuh9Ios07t+u9crodUJrMmPXCiFvvGWQZidEEpAhA4XLmywY7ripSYzjIW9Qh6FCwxQywItJOEoZ5zmixIG1C4Et5x0m/z6Tx+BDI9DTYOpvd0MsYOSsGXNUVN3VN6ux6Z+Cuyznf2+NiOmXq/fpPm81C6sULQDtJOBsMaNmEi8kEZy3m8Pg0GsDHwOt2lzfdHrPGc13XPISVDocvXAQyYylyx9DlXNU1n+cz7OMpb56uj/ch0ElTjtodCudIrCHGP6+V+9vaOb3+vNc398yXDaPFgpu6xj3ZC/0TQ1rmUzFUIjMAAAAASUVORK5CYII=\',\n    \'danger_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACnklEQVR4nO3dP0/bQBiA8efe2Oc2f0mgSzsgoUowwNTv/yVQWVoJRCuGUihxSYJ9NncdDAgGtkpt8r6/JZJtRZHusX2ZXvfh46cE4IA2JQB2ioJ3viAXoTti1lkkcRMCl1VFiBH/bF0z6BY/xMjUe47GE/o9oWpa2hhx8GoE7uHTzv+/5xPQc8L74Yj94YiviwXfVsunCLLHxd8dDDgcjblaLbm4u6ON8ZWvNetInGNSFByORkx9znE5J3dC1qbEzHuORmPOy5J5qPEi5CL/+jebv+ymqliEhoPZjNv+kNPVonsFHI4n/FwtKUPNGxEirz9WzPrKRWhT5LQs2d+a8KOukB1f0O8JV3d35A+LbzZT9853LJtA3bTs9gfITlG82PCZzedw3IbAtveIF6GxDZ8uDpoYyZxDEtidr9DjX0Tb6itnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnASgnKSXE2cgIbcS5bmDErxB4m2dPB8zmSykxzHPKpkEu64p7uqGCbUo2PmaDOSACvtdj4D3fVyuykCJfFrccjcYsQkObumFC0M2UsSDW2/M1jClxnxJ70xkXdcV1qMm8E85XK6besz+bcVbOWTYNAM72BhsikVJ35++NJzTOcVKW5CJkCShEOC7n/O4POdjaom5abkOgifc4ewasuYQ4YehzBt5zUdWclPOnmzvrLoHcCWfLBZd1xW5/wHZRMLSN4UZIQNk0fL654bquX8yF/gOG1emmATJQHAAAAABJRU5ErkJggg==\',\n    \'danger_pressed\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACv0lEQVR4nO3dT08TQRiA8Wem093FXVIo/4xw4OBBCif8/h+CaNRwMNGQgFgord12d7Y746EQvXAzVvu+v+t2k0nmyez09JrD128jgAEWMRKB/TRlN81IrCXGiPqfGQKRe++5reb4EJb7+vjULX8CPgT6ScJZb4vMQOkr/KLBrG7l6g/pWMt+vsGbouByOuXLrCR9jMA9bf5xXnC6ucnV+J5P5YQmtBBBC1gP1hh2spzB9i79JOHiYUTXWtwiRvpJyulmwcfhNXfzkrTjSKxb9ZrVHxUZzqeMfcX5wRGTouDzdIqLwFmvx9V4xN28ZMN1CTES0W//uulaR9O2fBjecLJ3yLeqwu6nKZmB63JC2nEEvfStrUikaztMfMXMzznOc+xemlH6iia0GP3gi2AwjKoZO0mK7RqDb9tVr0n9NcsTvm5bnDFYvejLZFimYFe9ELVaGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwGoBwFtDpQAI97bldzo7Tg0AaZ5ZzA+29r8mTFGusTgoTwRCJ9LKMcdNgb6oKrGMne0ETWqwOkFlbBggxkHa6bGU5X2clrgmBy+kPBtu7jH1F07Y420FvBuvGEGJgEQOD/kuu65q7usYl1vJlVtJPEs4PjvgwvGHiKx0ht2ZijGTOMei/xHRT3n2/XY6OjUBqLRcPIyZFwcn+K2Z1xaia4dsFBvPsWfCUiD7/d59HIh1r6aUbbGUvuK4977/fYs3ybfP7+HgfArlzHOcFO0mCM89vvvp/RCLjZsHXWcmwrknsr399PwE/SPRDrornqAAAAABJRU5ErkJggg==\',\n    \'danger_disabled\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACe0lEQVR4nO3dzXLaMBSG4VeysPkrUEgmTbrtHfT+76bNdBoaiAFjbCx14TQ30GmZcL5nCwvNnFce7Y77/OVrAsA5UtcBUIynDEdTfJZB/6u8Vw5SSjTHimNVEmOHzwKkfrCh/5Mjns8UozGLm8+EQU53bomxw+EueXz5S4mEc57xZM4s3VE+/+RQPveXGwjQD386X7G4eeB03FPuNqQYSbr+V8LhnCMvRny8faAYjtk8fcP5jJBiRzGasLh54FD+ojkd8T7Dea+7f2WauqJta+bLe9qmZrdd44HXm797HX649DnlH3Hek2Jkv31itvxEyHN8MZ4yGOTU1Q7vM/Tqu27Oedr2ROzOTGcr/HA0fX3wxUufTf4T5xxtU1OMJnjvg4ZvUIwdznm8Pvm2+UsfQC5LARinAIxTAMYpAOMUgHEKwDgFYJwCME4BGKcAjFMAxikA4xSAcQrAOAVgnAIwTgEYpwCMUwDGKQDjFIBxCsA4BWCcAjBOARinAIxTAMYpAOMUgHEKwDgFYJwCME4BGKcAjFMAxikA4xSAcQrAOAVgnAIwTgEYpwCMUwDGKQDjFIBxCsA4BWCcTynhnPaDWfNn5v5UH8hCrggMSSkxGBT9lri62hFTJC/GpKTdQdcvkWWBMCj6DaKx6yiffzD+sOj3yimCq5VSIsbIdLai2m85HfcEnwUO5YZiOGG+vGf/subc1IBDq0OvROp3CGdZYDK/JcbIdv2IzwIBEj4LbJ6+0zY1s+UdsTvTNjWx60Bvg/ct9cujQ14wGBRU+y3b9ePbXF/3xCac9+xe1hyrkulsRTGaEPLh25pxea8ckGhOR7brR07Hw9vmcIDf5rLckVmhXHEAAAAASUVORK5CYII=\',\n    \'danger_focus\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAEAUlEQVR4nO3dT2jbZRzH8ffzJE2TNmmLUYdNW7VdO9pu6Kxk1laZoDsIstYx2EFE8OYUPHjQgyIedvOww3CCB1FxgqJzoyvu4J8x/7TW1umhXVk7R6F/Jia6ZDbW/J6vh6xVYd1prE2f7+sQCA95eOD55Jf8Pr/DY1KbuwTAhkIsLeYBS6p1O/Ut91BZlcA5MKxO0PH1PI4BFwQs/HKGmckfKFzOEquuw7kAgDCAtSEWc1lua95Ob/+z3L71AariYOy1ZlblQgSWCjA3PcHQwFtMDB0jWl2HiMM0btkhi7ksnffvYddTL1OTjHFxJsPUj1+Qy8xhbRhBrjqxufKq4+t33DlHJBaneduDNLTeSbEI3x5/j1MfHiASjWNubeqQTU2d7HvxHSKVUUZOvs/w4JvkMnOIXH1iVWYMRGM1dPbuobfvORLJBMffeJWfvjpC2GDo6X+BmmSU0x8f4bO3X6IqkSSWuKl07VDlzxjEBQwNHKaQv8Tu/Qfo6XueC+OnCadau7ij815+nckwPHiYqkQSGw7jguJaL1tdT8ZQk6xnfOhTOrofp/2+NO3px7D1LV1UJSznxr4kl5kjFK5AnFvr5arrTQREEOeYGD6KiNDQlsZWViUwFi5lZ/U3f4MTBGND5LMLuKKhsroWK1fuB20ovMbLUzeGYEJhMCAuwK7UCPrt98fKXhu06vGcBsBzGgDPaQA8pwHw3H8CcM2HimpD+XevLctPknT//bGy16I9gJe0B1DLNACe0wB4TgPgOQ2A57QH8JL2AH7THsBz2gOoZRoAz2kAPKcB8JwGwHPaA3hJewC/aQ/gOe0B1DINgOc0AJ7TAHhOA+A57QG8pD2A37QH8Jz2AGqZBsBzGgDPaQA8pwHwnPYAXtIewG/aA3hOewC1TAPgOQ2A5zQAntMAeE57AC/9rwcovREJ1mo16gZb2WtjsM4VEREi0TgYvQpseCJEKqsxBlzxb+zChZ9ZKhiat+0kGksg4jQIG5Q1IZwENN/9CKEKmD9/hvDM2WHmpqdp3NJMZ89ehk4coiaZKh0wtMqBhKrcGKy15H+/SENbmo7uh8n9tsTkyCDhQj7L0MAh6ltep7d/P4U/s4x/dwwRh7UhPUiq3BlABBcENLSl2fXka8Tropz66F1mp0YxjW1pWcxn2bnvFXr7nqBYhHOjXzMxfIJ8dh4bCq8eAmOuzK/j63VcXEAkWk3LXQ/R3r2beJ3h7PdjfHLw6dLnU5u7xBjLUiHP1t699PQ9w82pTYhAUNS/A+VOBKyFUAXkMn8x9vkHfHP0YOkOwNpSAACMsRQu/0HtLU2073iUhrY00epa9AzJ8maAICgyf36UyZGTzE6NEYnFsdYiIvwDE/qofnBrXLIAAAAASUVORK5CYII=\',\n    \'danger_focus_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAEBElEQVR4nO3dTWhcVRjG8f85czO5mY82ZVqbZtoMtklKk1CI0aSmKSqiC6Ga+AFddCG48WvhwoUgShfizkUXUoquqlBFoZJaQxXEStXGtImpC5uBGstg0gjORJtkYjJzXxeTiQqpq9Ikc97f9oU7B84zlzPPLI5JNnYIgA2FWMjPAJZkUzv1jXfh18QJAtQ6ZgwExSLXfxklk77E/GyOmmgtQVAEwAOwNkT+Ro5tO9vp6XuRVOsB/DgYu6prV7eICCzmYWr8ChfOvMuVwX78aC0iAWbH7i7J38jR2v0EDz/9GrFEDdlMlsnRc8xlJ7AhDxFZ8cHGmKUP0PlanUtQxPNj1LUdYEvTnUgBvjv9Pl9/9CZhP4a5o6FFtja0cuiVE1RV+4x9cZL02XfIZycRBFZ+tlovShkhXLOBVPfjtDz2AvFEnNPHjnD53Ek8g6Gn72ViCZ/Lpz5k+MSrVMcThGObVnfh6tZZehOMDRxnYe5P7n32Dfb3vsS1n87jJZs6SLXeTS6TI332ONXxBNbzkKVDgqoQxhBJ1JMZ7Kehq5dUVyd7Og9i63d14MctE6Nfkc9OYr0qRI/+lUcEEUGCgMxQPxII25u7sNWROMbCXHbipocJVSkEY0Pkp6cICgY/ugFbftWbkLfKi1O3h5T22oAERezyMVG//e5Y3muDVj2O0wA4TgPgOA2A4zQAjvtXAMzqrULdZv/stV3+t0f33x3Ley3aAzhJewBVpgFwnAbAcRoAx2kAHKc9gJO0B3Cb9gCO0x5AlWkAHKcBcJwGwHEaAMdpD+Ak7QHcpj2A47QHUGUaAMdpABynAXCcBsBx2gM4SXsAt2kP4DjtAVSZBsBxGgDHaQAcpwFwnPYATtIewG3aAzhOewBVpgFwnAbAcRoAx2kAHKc9gJP+0wOUb57SK2JcsbzXxmAlKCAiVPmx0i2DqrKJ4FVHShdKFhax16/9yGLeUNd2H+FIHCTQIFQoY0IEUmTb3ocIhWFyfBQvM/Y9U+M/k9y9k1T3k4x9doxIon7p/iBtByuDwVjL/PRvbG7uJLXvQWZ/XyB9cQBvfibHhTNv07frLVoefY6F2RyZwU8RKWJsSCvi9c4YkICgWGRz0z20Hz5CtNbn/MfvMXF1GLOjuVPyMznuP/Q6+3sPUyjAryPfkhkaID89hbWh0g2iKz27fIDU+ZqdSxDg+RHq9j5Aat9BorWG9NAIp44+A8Zgko0dYoxlYX6Gtp6n6Ol9nk3JrUgAQZHSj4SbvQTKRwWdr925lC4BD3kwm/uLH778gG8+OVr6BWBtKQAAxljmZ/9g45YG9nQ9wvbmTvzoRoLg/xsCQedreQ4QFAtMjg+Tvvg5E1dHCNfEsNYiIvwNztmxo0eL49YAAAAASUVORK5CYII=\',\n    \'tab_normal\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACyklEQVR4nO3dy27TQBSA4X8uDrVzgzYtKaQgYIHEQ/D+bxFEETIlJa0dOw7xeFg4dIdYQnPOt53IiTS/x87qmKsPHyOAMYYQAhDJRhOy4QTrHcQIGP5M1//vdYgx0tQbqvKeEFq8T4gxAuCh3/y2bUmzIbPLBdY6ds2W0O4PF+/+cOnfX6zr/+96xFjH09kFzy4uWX/PKdcrrPMAeIyhbfdMn51z9vwF61VOsb4lhLaPSz1+BoyxDMcTZvMFaTrk5utnrHP4LgTSbMTZ8xfkX5ZU5R3eD3A++cvBoh6TGGFT3NHUFYu375menXN3e9M/AmbzBetVTlXckwxOiLGDGPUAODLeJ4S2Jb9ecvnqHXVZYLPRGOs8xfoWnyT95qujFGPEeU+zrdhtK6an59hsOGHX1ITQYowe+hIYDHW14SQbYq3zhP1PfeET4vDvj7D/ibEWCxH0zpfnsOf2H/8M9Y9pAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMJpAMLZGCPW2r/NHlRHxtj+3rdNveHJyRBr7MM0SXW8jOmHR6XZiF2zxVblPcZasvFUB0cdPUPXdSSDAdloTPFjhQ+hZb3Kmc1f0tQbQmhxzvczpPRAOA7mMAC46+i6wPzqDVVZsK1LvHMJxXpFmg5ZvH1Pfr2kqav+JOhHz6ojEGPEDwbMr97g/YD8eolzHg8R5xJuvn5menbB5et37LY19aag3e/1kfDIxRixzpFmI9LRmHpTkF8vH/bVHz6GdY672xvq8p7J6Yzx9PThTVE9frum5tuXT2yrEneYHA7wCw0pB+gT8xmSAAAAAElFTkSuQmCC\',\n    \'tab_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACfUlEQVR4nO3dXXLaMBSG4VeyjQGHTChJQyfJBrqI7n8fTSa0ECBAjPmR1Iu4nS4gLZOc77n1jWb0StbdcXdfvyUA5xwhBAD61YBedYbPMuT9SynR1C/UmxUxBLI8J6UEQA7t5h+PdPsVo+sbik5JCAdiiCdduLwN5xzV+ZBPMbCYTlgv538Od067+YPhiMvxLU29Yfn0kxgjkE67cnkjDuccZbfH5Zc7ur2K6eQ73mfkMQS6/YrL8S3r5Zx9s8VnGd77U69a3lizrdnvGoZXY/a7huV8igcYXd/QvGzazc9PvU75R7z3pBhZLWYMr8Z0OiW+Xw0oypJtvWn/C7r2PzLnPYf9jhAD58MRvledcTwc2n++2OA4NA3d/hneZzlJDz5THBBjwHmP18bbpqe+cQrAOAVgnAIwTgEYpwCMUwDGKQDjFIBxCsA4BWCcAjBOARinAIxTAMYpAOMUgHEKwDgFYJwCME4BGKcAjFMAxikA4xSAcQrAOAVgnAIwTgEYpwCMUwDGKQDjFIBxCsA4BWCcAjBOARinAIxTAMYpAOMUgHEKwDgFYJwCME4BGKcAjFMAxikA43xKCefcqdch/9nvPfdN/UJWdHBOl4EViURRluyaGl9v1qQYKLu9dnaQfGgpkWU5eVGyXszxIRxZTCdU5xe4dq6cfEwpJWKKDC5GvDwv2NZr8izLWS3nlP2K4dWY1WLGYb8DHHoZfByJ15M/uLgihiOzHw+vNwHth9njPYemYfh5TDgGDvuG2E4Tl/fNeU/RKSmKDpvVgqfJw59HYDsnNuG953k+pd6sGAxH9PpnFJ0OSVPl3jXH6+nfbWtmj/ds6zXZX+OBfwGDW9lz2SQofwAAAABJRU5ErkJggg==\',\n    \'tab_pressed\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACwklEQVR4nO3dTVPaUBSA4fd+UCFBrYoKfsy47o/o//8XnbF+VUWEmEAw4XQRyrSL1oULLOc828MMmblvbu7uuvMvXwXAOUdd1wAk3W2SdBsfAiKA4+9s/qHnDhARZkVOno2p65oYIyICQIRm8auqopOk9PpnhBiZlyVVXeHcv/79jYez+drnguC95/Nhn73DPqPHO7LREB8iABHnqKuK3b0eB/0Txk9PZJPn1W5g/nfNFuGcI0m77B+d0u50ebi5xIdAXNQ17STloH/K/e01Rf5CjJEQY7N9rPv5zbus1lCE/CWjnE0ZnF+we3DI8/C++QT0+meMR0OK/IVWq9V8H0Rs8TfA72sYY6Sua+5vrzk+OaXIJviku02ILbLx8x+HA7N5RAQfAuVsyrws2dnv4TvpNvNy1nzz3zrwmY3gnGNa5HSSLt6HaAc+TZY7fP36ivMeb8c8pZa7vV/zY5g1swCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCU8yKC89aBNn655n5WvLC1tdVcEGkXRm0+5xAR2p2Eclbgi2wCNNfF2sVRm08WC2KrRTtJmDwN8XVdMXr8wX7viBgji1UEFsImccs3f7FY0DseUEzGTIuMGEKLyWhIu5MyOL/g/vaacjZtlt92gw0hiAgxfuJocIZ3joe7K0KIRBBCiDzcXLJ7cMjx4JT5vGRa5FRV9fbZwOYfei40B752J6GTJOSTMY93V6tLweOvn/kQeB4+UGQTdvZ7pGmK84G1339u83fOARHK2ZS779+Y5hlheXM4wE9WOyAiwofwzgAAAABJRU5ErkJggg==\',\n    \'tab_disabled\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACaElEQVR4nO3dy47aQBBG4dPVHrcZJsBcFrPJC+Qh8v6PEimThKuNbdydBSRS1rmgUP+3BaSS+hjbqwrvP3wsABAoZQIgNfekNMMsApeP5b9VCgxDx7FryTn/cq7V+SuBnE/Uacbq8YUYI9NpJE8TIYTrTS6/rRQIFmhmTyyWT2w332gPO8wMuASQ88T8Ycly9Uzf7jh0e0rOFAqgAP5v5zMMIVCnhtXqmZQa1l8/E8yoSsnUqWG5euaw/cLQd5hFgpmO/sYMx45x7Fk+vTKOA/vdGqPA6vGFvt1dDr+69pzylwQzSs7sN2+8WzxSVTWWZvfEGDl2ez30ORCCMQ4DeRqYPyyw1MyYTgM552vPJv9ICDD2/eVNL5z/FsSXnM9veHbtQeS6FIBzCsA5BeCcAnBOATinAJxTAM4pAOcUgHMKwDkF4JwCcE4BOKcAnFMAzikA5xSAcwrAOQXgnAJwTgE4pwCcUwDOKQDnFIBzCsA5BeCcAnBOATinAJxTAM4pAOcUgHMKwDkF4JwCcE4BOKcAnFMAzikA5xSAcwrAOQXgnAJwTgE4pwCcUwDOKQDnrFC0G9ChH2duQ38kVrUicKQUuKsTw9hjfddSgDo1lKLdQbevEGOkqhva/Rab8sR28437h0dCMEVww0op5JyZL57o2gN931GZRdrDlpQals+v7NdvnMbh/AvdFW5DgUIhxor54oVCYL1+wyyedwebRdZfPzOOA++WL+TTyDgcyXm69ujyB4RgVHXi7i7Rdgc26zfC5er+uSc2mLHfbTh2LfOHBSnNCBa0SPQGFArjMLDdfKK/7Ib+4TtKftC67nw/agAAAABJRU5ErkJggg==\',\n    \'tab_focus\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAD7ElEQVR4nO3dS2icVRjG8f85803mkskYxhZMmpDmUknSi9XEEBKJF9RFYYLFRRfdahERN4IuXIgLceO+0EJ14cIrFqmxDejCKL0kxsZWbJJW0xLIxICTNpdOk5nzukhnWsGIiJjLeX+74YVvBs4z8808s3hNbWuPAFgbYim3AMZS3bCH6sYHiMQSOAcGw18TBJ2v5zkGXKHA9LWLTI7/QG5hllh5Jc4VAAhg5fBvLsxy3/Y9dPceoq6li1gCrF3lumpDEYGlHGQmxjl78j1Gh/qIxisRcZi6XY/LzYVZWjuf4amDr5JMRZmZzHLlxwHmshmsDSGrXLiYO52v37kTR1mknPpd3WxrqqOwDGf6PmTgs3coiyYwVU0dsrW2mQOvHCEciTD81UcM9r/LXHYaEfkHT6Hz9T+HaLyC1s5eutMvUHFvghNH3+bCtx8TgKG792WSqQjfff4J/e+/STyRIlZeucpF1UYk4jh36hi3FudIH3qDrvSLXLt0mqC6cS91LQ8yM5llsP8Y8YoUNhSUviSoTcIYkqkqfh78guaONM0Pt9Pcvg9b3biXWMLevudPEQqFEefW+uWq/5oIiCDOMTrUh4hQs6MNG4lVYC3cyGbuuuerzUgQjA1YmJ3G5Q2ReBIrtz/qbShY45en/h+CCQVgQFwBW/qmqO9+f5TO2qBVj+c0AJ7TAHhOA+A5DYDn7grAan8pqs3nzlnb0h8Jev7+KJ21aA/gJe0BVJEGwHMaAM9pADynAfCc9gBe0h7Ab9oDeE57AFWkAfCcBsBzGgDPaQA8pz2Al7QH8Jv2AJ7THkAVaQA8pwHwnAbAcxoAz2kP4CXtAfymPYDntAdQRRoAz2kAPKcB8JwGwHPaA3hJewC/aQ/gOe0BVJEGwHMaAM9pADynAfCc9gBe+lMPsPJARFfE+KJ01sZgncsjIpRFy9FPAR8I4UgcY8Dll7HTV39iKWeo3/kI0XgFThwYDcJmZE0IV8jTsPsJgjBkrl4kmBwfIjMxQc3922nt3M+5U0dIpqpXFgytuo9ObSwGay3z12eoaWqjpeMx5rLLjA33E+QWr3P25FGq6t+iO/0cucUslwa/XNkn8zdbQ9XGYAARwbkCNU0P8eTB10lURhk4/gFTv4zcWR376LOv0dV7gEIeLp8/w+hQP/Ozv2FtiLXffKnzfzsXcYQjcRp299DSsY9EpWHs+xGOH34JMJja1h4xxrKUm2dn13660s+zpWorIlDQHwabgjEQhGHu91uc/+ZTTp84TPG2YIrr442x5BZvcM+WGprbn2bbjjai8aSuj9/g85X18XkyEyOMDX/N1K8jlMUSWGMREf4A4ICv4I2qxnUAAAAASUVORK5CYII=\',\n    \'tab_focus_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAD8ElEQVR4nO3dz2tcVRjG8e85M5P5mWZaLE1jQoKZtmnUNGlItQlUpLWI2FZBKFRciljQhYL+BeJG3BbsxpWkiBLQaikEaROplRjNxNLa0DgppU1qipmYSSY/5rwuMs100exKk8x5P5tZvMOdC/eZOXeeuzimrvmAAFgbYCGfA2OpaWyh5qk9hKOViAMMDyfFV52v37kBVygwcXOYWyO/k89NEY0nca4AQBCWL/5cborqhha6jr5D/e79ROJg7SoHVhuKCCzmYXxshMvnvuSvgR+IxJKIOEz9My/KXG6K5udf46U3P6Jyc4R7t7OMXbtMLnsXawOIPPzAxpQ+QOfrcy7OEQrHqN3ZQXVDLa4Av/x4hr5vP6MiksBsT+2TrXVNHP/wC0LhMMP93zHcd4Zc9h9ktSOrDSccTZBqO0z7obeo3BLn7OlPSfd/vbwEdB19n8rNYQbOn+Xnns+JxJJEYlVrfc7qERJxpC90szA3w8ETH7D/yEnGrl0iWNPYRv3uNiZvZ0n3dROJJbHB4MpNgioTxpBIbuNGupfGPYdJtbbQ1PEKtqaxlWjccvPq8pofCIYQ59b6dNWjJgII4oTR4V5EhNod7dhwrBJjIZe9q2t+mRMRjAkwOz2JWzKEY5uwUvypN4HgGp+eejwEYwNgQFwBu9Ii6LffI6UGSasez2kAPKcB8JwGwHMaAM89EIDVnimq8lO61nblL4Fefw+J9gB+0h5AFWkAPKcB8JwGwHMaAM9pD+Al7QEUoD2At7QHUEUaAM9pADynAfCcBsBz2gN4SXsABWgP4C3tAVSRBsBzGgDPaQA8pwHwnPYAXtIeQAHaA3hLewBVpAHwnAbAcxoAz2kAPKc9gJe0B1CA9gDe0h5AFWkAPKcB8JwGwHMaAM9pD+ClB3uA4tZTIrpFjC9EijvCGIN1hSVEhFA4trZnpR4TIVQRwRhwS4vYicwVFuYNdTv3EY4kcOJKG9KpsmJtAOcK1O3qIhCC8cyfBG+NDDCRyfBkqoEde19m6MJXJJLbECPaDpYLA8YEyP13j+0NLaRaO5mZWuT64HmC+dksv547zbF3P2HvoRPMz2W5kf4JcQ5jS48K1AZlABHEOaobnqXz2HvEk2H6e7q5MzpU2jr2hTc+pvPV4xSWIHPlN0aHLzI7Pbm8wdCqKbi/VOh8vc5FHKGKKHW7niPVepB4lWFkME3PqZOAxdQ1HxBjLAv5GZ7ufJ2uI2+zpXorIlAo6J/DcmAMBEIw8+88f1z8hkvfnwIM1hYDsPwmS352mqonamnqOExtqp1wbFNx+/hVYnD/HkHn63duDK6wyHgmzfXBXu78PURFNIE1FhHhf2X0nU1mJTZDAAAAAElFTkSuQmCC\',\n    \'popup_normal\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADUElEQVR4nO3d0U9TVxzA8e/v9La3LWVEWaEVRIJoskRdnFHHthiWZSaOtz35r+1/2MNeXJbsYfiyxMHMHmgMQwEdtEArHYm2vbU9Zw/Am+xJA/L7fZI+/W5uT3K/uTn36ciZ0akA4Jyjm3QAKE1MUzp/kTjO4YNHEN4uEMDmJ3iOCL7fp157QXV9maTdIs4PELwHQM6MTgVxjqT9mmL5AjfuzBHnC+w1G3RaLZwTQnj77eXgf21+cufBB6JMmqGzRZwIlYV5nlYWyeYGCCEQHT786Ss3uf7VPVaWHrO+skQ36RCOurP5oIhAKpWmND7JtZm7fFya4I/ffiIT54jeJB2K5Qtc//IeCw9/YWtjlWy+QJzNH/e6zTsV2Hz+lJc7VWbn7nN5d5vlv34nArhxZ46VymNqG6sMDA7h+31C8Me9YvOOZXN5ukmHR/M/8/nX31FdW8aVJ6aJ8wXW/14ily/g+/3jXqd5T7z3ZOIsu40t/t19yaWrt3Cl8xfZazbodjuIuONeo3nPQgAB6rUXjIxN4jJxnk6rZRs+NQIiQrv1miidwYXgETnqO9KcViJCCAF75ytnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnASjnQOywCIUOn7nzvk86nbFDI5RJpzP7B0bUa88ZGi6SSkWAvQlOPRG89wyPjtGs13DV9WWcQGl8kqTTxjnbFpxWIkK/1yNf+IiR8hjPKotESbtFZWGeazN3aexU6SYd0nH26PNIzQdJROj1erzpJtyenWNj9Qnbm2vI2fJ0SFqvuP3N94xNfcKj+Qc0G1uAIM5ZCKeE9558YZDPvviWKIr49ccfcC51cHi0CN2kzeVPZ7hyc5a93QY7tX9ot17hxB25MzjcNtr85M5DCESZDMMj5yiWx9lcfcKfDx8gzu3/Do+PFxGSTovBoWEuXb1F8dwk0cFO8f8+EELA5id4vn9NoFmv8ayyyPbm2v650CIQAv8Bi2Zr08r/F1sAAAAASUVORK5CYII=\',\n    \'popup_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADMUlEQVR4nO3dwW8TRxSA8W/Ga6/XTuMkOHVoCKIh6qVWDybAIRCpVXsJf24lzpGQ6CHCFBGCKCSKU7CLg3EIxPHu2jM9mPSEj1Vw3vtdn7xeaT6t16dnZivLHsBYS5rE4D0LS9epXFkml4/wzoExfJkHj86/4rnB4NyQw9YBrcZL4tMeYaE4OlfAzFaWvbGW+PSE+ctXqd3ZoFCa4+TjMUncx4y9uJoMnkwmoDhdwg9Strc22dupE0YFvPcEZ4e/8uNNanc3eN3Y5cXOn6RJMoqLUWRfYv77Cp1/rfOzM7SZDOXKIrX1e5QXltja/J1cmCdI45jy5avU1jd4/mSLd2+bhPmIXJgfc1k1qdqtvznqHLJ651c+vG/z4skfBOC5cXeD1/u7vPunSVScwrkh3o/rSk2qMMyTJDHbjx5SvfULzf2/sAtL1ylOz9Fs7BJGBZwbnvd9qv+Jc45sLuTDUYfeySdWqqvYypVlPn08Jh0k418m1cXhPcYYup0284vfY3P5Aknc10e+IAZD3D8lm81hvXf6V08gYwzee+x534g6XxqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBqAcBaMLosQ6OzMrXdDgiDAoEsjJAmC7GhhxGGrwdT0DDZjx+6fUxeL847SXJnuYRPbbLxkOEgof7tIGsdYq68FF5UxBjccEkVFZmbL7O3UCZJ+j2dbm9TW73H0vk2axATZkPH7KNVkMjg3YJCmVG+scfDqKW/f7BOEUZG9nTrlhSVW135j+/FDjrsdMGa0TEo7mGyf98c6PyQfTVGtreEGMfUH9wnz0efl0caQxH1++Ok21Zs/0+ud0O20ifunulFs0nlPJshSmiszM3uJg1fb1B/cxxiLsXYUAIx+H+J+j29Kl1iprjL/3TWy2RDvdX38RM8xeO/otlvsPa/TfrNPLh+NPuM9/wINKVWvmc97jgAAAABJRU5ErkJggg==\',\n    \'popup_pressed\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADIklEQVR4nO3dUU/bVhTA8f+9cWI7pCAaAsk6oqqgvQx1bRHbVIG0VdsL1fZh99BXqlVDWqswTRrRihSUZtRtEigQaSE22HcPGfsC7RrBOb9Xv5zo/u3YT8fMLtxxANZakngEQHVxieriEoUgxGUZ6uoyxpBlKf2oQ/Rqj/hsiF+c+u9czezCHWesJT77m0qtzoONx4SlGQanJ8SjIcbYCf8E9T6cc3iex/TsTUyW8seLp7SaDYJwanzt8vCXP1/j/sYm+3tNOs9/IYljwE16fvWB5HIeC58scm99k0qtzvOtnyj4Ad55ElOp1bm/sclvv/5MN/qLICziB8GkZ1Yf2JuDNu/6b1n//kdOjnq8/H0bD+d4sPGY/b0m3ahDsTRNlqY4p3f/deMHIUkc09jeYvXrb4jaL7HV+hJhaYbO/p+ExRJZmk56TvU/ybKMgu9zfNRjMBiwvLKGrX66xOD0hCRJJj2f+giccxhjOOxFzN+6jS34AfHoDPSRL4cxjM6GePkC9rIIJYsxBucc+pEvnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAV0P5BAl2duXZbh5fOgSyNE8fL58cKI/tsO0zOz5HK5Sc+kPgqDyzLKc1VO+hE2au9hXMpCbZE4HmGtvhZcV8YYsvSCcKpEuTJPq7mDF4+G7L54yhfrm7w77JLEMXnf1yVS140xZBcXnJ8nrD58xEFrl+7rNp4fTtFq7jBXq7P+3Q80trc4PuphjBkvFpr04Oq9GMYLgLM0pVi6werDR+RMRuPZE/wg/Hd5tDEk8YjP7n7FypffMjg95bD3htFwiLH6cniVOefw8nnKc1XKlXkOWrs0nj3BGIuxdhwAjP8f4tGQGzNlllfWmL91Gy/v45yuj7/KDOMIjvsRreYO3ddt/CAcf/U5xz91qA529G30hwAAAABJRU5ErkJggg==\',\n    \'popup_disabled\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACj0lEQVR4nO3dyU4bQRCA4b8Xb4ztjGWQcUKibEJ5/9eBQw6OwJAYvDJepisHG5RTLiRxcNV3nUtL9c+o51Su0/soAM45ynIDQNbqcNTsEGJERDAvnAiL+YT5ZERZromx8jTXCNvhbzZrGlmb3tlnqvWMtNmQUgnO7fXs5rkE5zzt7inlZs33q6+MR1eEUAWEyG74ebfP6dtzimLGZDTcDt8cDOcctXpG/90XGlmb4eAC7yMxlRsa2St6b8+ZTUasijk+RLwP+z6z+cOKhxmr5QP58WuWxYK72wEeoHf2iWUx2w2/su9zmr/E+4CkxPT+lpP+e6q1Bv6o1aFazyjmE3yIgF36DpnznvWqIEki7/bxWbNDKjeklPZ9NvPPONbLgkYzx/sYbfjKOEBSub3rYf/5isn2Emj0sgCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCU8yKCs92A6jjnQAT/MJ8QQsUiUEQQYrVOsZji59PtOtFqPUNsWeThEyGESIxVxqNr/OM60ayV43xAxBZIHSoRIUmimZ8wvhuymI6JIVYYj65pZG3y4zdM729Yrwocbrdeat/HNs+ym6GwffNbeY/VquBmcEmIkYgIIVYYDi5YFnNO+h+QlFivCsqytN3RL5wAznkq1drusz/k5tvl053PPa6PB7e9C9Qa5N0+R80cH8J2q9zvIrDn//dzABGKxZTxj2sW83vCL+uBfwKb7u78POo39wAAAABJRU5ErkJggg==\',\n    \'popup_focus\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAECUlEQVR4nO3dS0ycVRjG8f858wHDwHDXVgpSp6HolEBMSqBSQyVGNxoak6Y2aqKJC+LaLky0C13gRjduNK0xajReGtKkml7UeMGKQNDUKK0WTNqUkpIwJQzlIjPndQEDXUhXxAHO+1vMLM5kcpLzfJNvnm/xmtItMQGwoYD5mSTGWKrv3U11XTN5kSLEARj+myy96/q6XTfg0mnGRga5PPQzM9MTRKLluHQKgAAWD39maoJttU20HzpMrKGdSBRsCERW+W61cQjMz8G14T/o6X6L33/8nPzCMkQcprxyp8wkJ2hse4rHO7soqogwfiXByPkfSCbGsKHQqiEwS8HT9fW77pwjN1xArP5BqnZuJ5WCnuPH+OrDl8mLRDGFJXfJ1nsaeO61E+SGwwyc/YSBM++STIwhyMqvjNqYzOJLOD/Krgf209rxAsUVUY6/eZjBr98jwED7oVcorgjT0/0ZZz84QiRaRn5haba3rtaKAXGOvlNHmZtJ0tH5Kg8dfIm/f/uWoLquhR2Ne7h+5Qb9Z44SiZZhgwDn0tnetlpLxlBUXsmFvpPEmzu4r7mJ+r0HsHfXtZBfaBk5/z3JxBihIAdxLtvbVWtNBEQQ57jYfxIRoSbeis0rKMZYmEqMIXrLv6kJgrEhpiev41KGcEEJVtzi/0EbCrK8PfX/EEwoWLwvSKewyyWCXv3+yJy1Mdjs7kRlmwbAcxoAz2kAPKcB8NwtAVjtkaLafFbO2i4/7dHz90fmrEW0B/CS9gAqQwPgOQ2A5zQAntMAeE57AC9pD+A37QE8pz2AytAAeE4D4DkNgOc0AJ7THsBL2gP4TXsAz2kPoDI0AJ7TAHhOA+A5DYDntAfwkvYAftMewHPaA6gMDYDnNACe0wB4TgPgOe0BvKQ9gN+0B/Cc9gAqQwPgOQ2A5zQAntMAeE57AC/d2gMsjZ4S0RExvlg+a2OwLp1CRMgNF6zMIVOblwi5eRGMEVxqAXtt5BcW5gyx+jbCkSgiToOwSVkTwkmaWOPDhHIMo8ODBJeHzjE6fImaeC279jxB36l3KCqvXBwwpEMDNwmDtZbpyXGqapuIt7STTPzDUO8Jgtlkgp7uN6iqfZvWjk7mbk5yof9LRNJYG9JBUhudMSAOl05TVbubR545QrQ0zDcfHePqX32Y8spamZlK8Oizr7Pv4POkF+DSrz9xceA0yRvj2NBtBgivh9moun7bdXGOnHCEHQ1txFseI1pqGeod4OOuA1hjMaVbYmKMZX42yf3tT7PvyRe5Y9tWRCCd0tuBzcAYCHJgKjHHwOn3+e7TLjAWa5cCsPghy+zNSUrv3E793v3UxFvJLyjB6fj4jb1uDC61wOhIP0O9X3D1z37CkSKMtYgI/wLkFaubPeSSvQAAAABJRU5ErkJggg==\',\n    \'popup_focus_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAD+ElEQVR4nO3dTWjcRRzG8e/M7nZfsnkHk4YkpDFvIkmaSmwwiqatLxcRD6UvKih48OJFfAERLx7iQXrw5KEgIoQWtVTsoaC11qTaNERwY1KVJDTQpmi7sckmm7fd+XlIlvaQ4CWYJvP7HPYyyzDwf/a/zDOHMcVltQJgA0EW0ymMsVQ1tVPV+DCRWAHOAcawJln90PF7dtwYyGYz3BgbZGLkEunZJLH8Ulw2A0AQVh5+eiZJZX07XUfeprali2gcjF17XrW1iMDyAkyOjdB76mN+6/uCaLwEEYcprWiQdCpJ6+Mv8Oxr3eSXxEhen2bi937mbv+NDQQQkTUnNhgw6Pg9PO7EsSMco7KhnZ27Kslmofer43z7+XuEY/mYeNFOKd/VwisfnCYUjjDU9w1DvSeZm7657sRq6wlH49S1PcVDB16ioDSPL4+9xeB3nxLEwL4j71NQEmHg7Bkufn2MSKyISKxws9esNpCII3HhBEvzs+w/+gZdh95lPHGeYHVjB7UtHdy6Pk2i7wSRWBE2GMS57GavWW0kY4gXlTGWOMf9rU9S19ZK86MHsVVNHUTjlokr/cxN3yQQDCHObfZy1UYTAQRxwnjiHCJC9YOd2HBeIcbC3PRf+p+/zYkIxgRIzyRxGUMkrwgrbmU/aALBTV6e+n8IJhBY2T1kM1hYLRH01++P3LM2Bq16PKcB8JwGwHMaAM9pADx3VwDWOVJU25pdPVTW5+8Tc2frrz2Aj7QHUDkaAM9pADynAfCcBsBz2gN4TnsAH2kP4DntAVSOBsBzGgDPaQA8pwHwnPYAntMewEfaA3hOewCVowHwnAbAcxoAz2kAPKc9gOe0B/CR9gCe0x5A5WgAPKcB8JwGwHMaAM9pD+A57QF8pD2A57QHUDkaAM9pADynAfCcBsBz2gN4zub2hCJ6RYwv5O5toMtkEBFC4Rj6FvCBENoRwRjBZZaxN8Z+YXnBUNWwl3AkDydu/Zso1ZZmbQDnslQ1dRIIGSZHBwleHbnI5Ngo1U111O95hl8v9BAvKkOMaDu4XRgwJsBcKkl5TQt1ux9hdmqJ4Z9OE5xPTdF76iMOv/MJew4cZXF+mrHEecQ5jL1zVKC2KAOIIM5RXtNM53OvEy8O833Pca792Y8praiX9MwUT7/8IU8cepXMElwdHmR86EfSM7cwNrD+m8D8xzmCjm/6uDhHKBylqnEvdbv3Ey82XLk0QE/3QayxmOKyWjHGsjifom3fi3QdfpPSinJEQO+O3B6MgWAIUv8sMHD2M3442Q3GYu1qAFa+ZJmfu03xfTU0P/Y81Q90Es0r1Ovjt/j4yvXxy0yOXmb45zNc++MykVgBxlpEhH8BApbQEfm1X30AAAAASUVORK5CYII=\',\n    \'popup_open_normal\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADrUlEQVR4nO3dS2hcVRzH8e8592YyyUycPBrzNNgMNLbQ+CC0+MCANUEpuBIULNYqLlzVndBKQEEKuhNEFLT4ABEs3UTUSkDaYoPWpmgjbVrMQyShTWoyzUwn6dz7dzHNsnVjSMz//9keGA7Mb+79z+8sjqtr6hQAH4QsFXKIQPbeXjZv76UqXYtEgOPWxNbX9bqDuFRi6vyPXDwzROHaHKnMJuKoVF6ua+oUH4TkF2bpuGcnT+x7k1RdM7PTk+RzV3E+uM2nm/VO4phEZRWNbZ14F3P8q3cZGfqU6swmJI4JfRCSz83S07ePvr0D/PLDl/x2apClwgIi8Vrv3/wXnKOiIsnd2x5k156D3NW1k8EP9pNM1+LStc3Smr2f514/yjefD/DH6AnSmUa8/fI3FBHhen6e6pp6nn31MCePvM3w4Pu4VKZJXnrreyYunmb4uw/JNLQTlZbXer9mFfiggmJ+njvbu9i99xAfH3gcn+1+jFRdM+dOHSWdabIvfwOLoxskUxmmJ88xO32Jnv4X8Z3dvcxOX6JYyOG9X+s9mtUmgnOeqbHTdGx9CJ9M15HPzdnAp4SI4FxAfuEyiWQKL1HJ/uqpI7ggRCTC4xzlNsGoIuUGyV76ylkAlLMAKGcBUM4CoJwFQK3yGbJf+TtglHEAYj2AWtYDGLAZQD0LgHIWAOUsAMpZANSyHkA36wGUsx7AgM0A6lkAlLMAKGcBUM4CoJb1ALpZD6Cc9QAGbAZQzwKgnAVAOQuAchYAtawH0M16AOWsBzBgM4B6FgDlLADKWQCUswCoZT2AbtYDKGc9gAGbAdSzAChnAVDOAqCcBUCtlR7AObssQiGRCAAfl26QqKzGOSuD9BASlSlEYvyf54dpbN1CWJFExAqhjc55TxyVaMvex8z4r/ixM8fwwOZtj3A9/zc+qFjrPZpV4nxAablITX0L7dkHGBn6jLBwbY7jR95h1543+Gv8LMX8PMlUpvw0ECnPCrd6MKy8NWx9/a7fPOpxzlNaLrJUXGT3C4e48PPXjI+ewDW0bpH8wmWeeuU9unb0M/jJADOTv+Ocw/ubZ0Xm/8sBIkRRiTvqW+h75jUSYYqPDvYRhGH58mjnPcXFeXY8+TKPPr2fK9MTTI2dZTF3pXyF7HpOuK3fdr18eXQ1bdnttGe7ufDTMb49fAAfhHjvywGA8nBQyF2loSVLT//zdGx9mEQyhcRufV+Pbuv/epovccTMxAgjQ18wMXqSqppanPOICP8AEc9sVAgXvBUAAAAASUVORK5CYII=\',\n    \'popup_open_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADsElEQVR4nO3dQWgcVRzH8e97M9nsdpNNYlbTpNgtK7apVj0EDCq2iEmDCEJBBA+1oXjowUNPHrQHheKleCgIgqAIOYiHnKxaquylShoqjahpEkpr4lLTpE1idrubTTIzz0M2Jxs9xaT7/38Oe/nD7IP5MfPmd3mmpS3rAKzns1wu4BxknzxI9omDJBqaiSIAw8aczrfx3BgIg1XyE0Ncu5KjXJwj2ZQmCoO1eUtb1lnPp7R4h92d3fT1v09j6y7mZ6cpFxew1sfh7n3x6q/Ot+88chF1sQTpnQ/johUuDp5lJDfAjlQaF0WY1o69rlS4Q1dPP4ePvcevQ+e4evkCy0t3cS6654XV/cUYg+/Xk+nsoruvn4lL33Luk5PEG5rxl8sFdu/r5vCxD8gNfsjU+DDJVCuJhibMvz561P3CATjHjd+GmJ4c48iJs8zmxxj++mNMsqnNHT99gen8BD/lBkg90EEYrGz1mtUmsJ5PpbTIgx2P0vPa23z6zovY7FMvkErvYuzyNyRTab35NSwKA+LJFDP5MeZv5+nqPY7NHjjE3MwUlaUi1tqtXqPabA6Mtdy8/jOZ/c9i4w0tlIsLOPdfnxuqFjjnMMZSKswRiyexLgww1tvqdan/mfE8nAuxGAMbfEeqGlZ94utLXzgNgHAaAOE0AMJpAITTAAhn0QJIpurnv/YAUmkPoED3AOJpAITTAAinARBOAyCc9gBSaQ8gnPYACnQPIJ4GQDgNgHAaAOE0AMJpDyCV9gDCaQ+gQPcA4mkAhNMACKcBEE4DIJz2AFJpDyCc9gAKdA8gngZAOA2AcBoA4TQAwmkPIJX2AMJpD6BA9wDiaQCE0wAIpwEQTgMgnMUYPR1MoPV7bqNglbpYAmO0DJIkVr8DF0XY/MQl0u1Z/LqYPgkEMNYShqvs3HOA6clfsNeufIcLAzL7uqmUFrGev9VrVJvEGEuwUqGxuY2OzOOM5Abwl4rzXBw8Q88bp5meHKVSLhBPNK4dR6oNcc0wxhCsLrNSKdP7+inGh79iavSH6tGxi7O8cuIjOp95me+/PMPMHxMYazDGQ1NQCxxhENLY8hCHjryFdZbPTvXh+f7a4dHGWip3/+Lpl97k+VdPsnD7T25ev0qpMIf1vOqRcv+0vnHU+fadR1FErD5Be2Y/7Xv2Mj58nvOfv4u1PtbatQDA2uagXJintf0RunqPknnsOWLxJFG08QnC63+r8+07NwaiKOTW7yOM5L5gavRHEo3NGGNxzvE30eScptVQY0QAAAAASUVORK5CYII=\',\n    \'popup_open_pressed\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADz0lEQVR4nO3dTWhcVRjG8f8592Zm2jt2JiRNbOwETEJsoKQqqYVKqURCRdSNu1Yqartx051ggggu3JRuBFFBKxTpyhYXCSJtNjGQSm0jCZU0pabGhlanH/mcSZO593UxiatEV8mMc97fYjYvzD1wHuaeee7imur6JgGwns+j3Cwi0LznIE3tB9kSVBNFAsawJln50HnZzo2BMFxmcmyIG1cukpu7T5CqJQoLAJjq+iaxns/CzD0ad+3jpbc/IkjVkZ36nYWZexjPB5G1L7B6YZ2X7VyikFh8K3WZFqwVBr79hKv9ZwhStUgU4a9ufkfXW3Qd/YCf+88yMvgdi7lZRCIMIP9yAZ2X9xwRjLVUVSV4cvfzdB7pJvPUPnq/OEEimcYk049LQ/MzHOk5T9/X7/Pb6ADJ9Has9db+UvW/JAj5uYds3VbL4fe+YfD8SS71foYJUvXyzscXmPh1iKG+z0lt30m4vFTq9aoNYP0qFucfUpdp49Xjpzjd/SK2eU8nQaqe0cFzJNP1uvkVLCoskwjS3JkYITs1TsehY9im9hfITo2Tz81grS31GtVGkwhjPCbHfqKxbT82kaxmYSaLRFGpl6Y2gQDGesxN/0ksHmAlLGCsX+p1qU0lWM9HJMQW/0uu8zdCVS4RwKA3fcdpABynAXCcBsBxGgDHrQRgnceJqoIV99yu+yhRVTYDINoDOEt7AAV6CHSeBsBxGgDHaQAcpz2As7QHcJv2AI7THkCBHgKdpwFwnAbAcRoAx2kP4CztAdymPYDjtAdQoIdA52kAHKcBcJwGwHHaAzhLewC3aQ/gOO0BFOgh0HkaAMdpABynAXCc9gDO0h7AbdoDOE57AAV6CHSeBsBxGgDHaQAcpz2As1Z7AGMQCUu8GLXZVvfcRoVlYvEAY/Ru4AwRYokkIhH2j7FL1GV24ccS679/TlUMYyxhuMzOlme5e2sEO37lB6y1NO0+QH7+AZ5fVeo1qg1irEdhKU+qpoFM616GL57Bz83dZ+DcSToPf8jUzV/Iz02TSKaKvwYiej6sEMZYCkuLPMov8MqxU1y/3MfEtR8xNQ2tsjD9F6+9+ymte7vo/bKbOxOjGGsx1v7TGa9t9Zah8/KdF5/1hIUCqZoddL3RQzy2ja96uvB8v/jyaGMti/PTPPfycQ68foLs7ZtMXr/K/HQW63nrng3MysuLdV6+8yiKiCcCnmhpJ9P6NOOXL/D96W6s52OtLQYAwFhLbvYBNTua6Tj0Jo1t+4nFA0QM5Z1wnf/XXCTi7sQww/1nuXVtkC2PpTHGIiL8DYEn3ENtKQitAAAAAElFTkSuQmCC\',\n    \'popup_open_disabled\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACj0lEQVR4nO3dyU4bQRCA4b8Xb4ztjGWQcUKibEJ5/9eBQw6OwJAYvDJepisHG5RTLiRxcNV3nUtL9c+o51Su0/soAM45ynIDQNbqcNTsEGJERDAvnAiL+YT5ZERZromx8jTXCNvhbzZrGlmb3tlnqvWMtNmQUgnO7fXs5rkE5zzt7inlZs33q6+MR1eEUAWEyG74ebfP6dtzimLGZDTcDt8cDOcctXpG/90XGlmb4eAC7yMxlRsa2St6b8+ZTUasijk+RLwP+z6z+cOKhxmr5QP58WuWxYK72wEeoHf2iWUx2w2/su9zmr/E+4CkxPT+lpP+e6q1Bv6o1aFazyjmE3yIgF36DpnznvWqIEki7/bxWbNDKjeklPZ9NvPPONbLgkYzx/sYbfjKOEBSub3rYf/5isn2Emj0sgCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCU8yKCs92A6jjnQAT/MJ8QQsUiUEQQYrVOsZji59PtOtFqPUNsWeThEyGESIxVxqNr/OM60ayV43xAxBZIHSoRIUmimZ8wvhuymI6JIVYYj65pZG3y4zdM729Yrwocbrdeat/HNs+ym6GwffNbeY/VquBmcEmIkYgIIVYYDi5YFnNO+h+QlFivCsqytN3RL5wAznkq1drusz/k5tvl053PPa6PB7e9C9Qa5N0+R80cH8J2q9zvIrDn//dzABGKxZTxj2sW83vCL+uBfwKb7u78POo39wAAAABJRU5ErkJggg==\',\n    \'popup_open_focus\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAEDklEQVR4nO3dS2hcZRjG8f/3nZnMPZkYsTEhzUXrJFgS09I2aMQmoFXBhUKpwTu4cOnCKoi4cREXxYUrFwURNSLWUkVEaEtToza2prZeBmwyViGmaJqYZpr7zHldTKZ2kbgK5vK9v0WyeOFw4HvmcOaZxWvKNzUIgPUCzE1nMcZS07iDmtROwtFSfB8whiXJ4h+dr9m5MZDP57iUGeD3dD/TV8eIJirw8zkAAlA4/OnJMaq37KCz60UamjuIxsHYpa+r1hcRmJ+FkUyavsNv8tNXHxGJ34CIj6mouk2ms2O03PMYDz3XTWlFlNHhCS6m+8lO/IX1vMIVlmTAoPM1PBfxCYai1KZ2Un1LDfk89B06yNF3XyEUTWDiyZulsr6ZZ147QkkozNkvP+H7kx+QnRhl8RmjNoBQJE7jtvvZtecpyipiHHpjPwPH3iaAgc6uVymtCHPq80858fEBIrEkkVjZat+zWkEiPgO97zM7k+XBJ/fTse9lfv3hBIHNqTYamtsYHZ5g4GQPkXgS6wXw/fxq37NaScaQSFYyeO4YmdY9NG6/g63te7E1jW1E4paL6X6uXhnF84KI76/27aqVJgIIIj6D548ivlB7+13YUKwMayE78ed/vEyojUBEMMZj6soYfs4QjiWx4he+D1ovsMq3p/4fgvE8MCD5HLbwPQL99LukeNbGoFWP4zQAjtMAOE4D4DgNgOOuC8AyPymqDejfs7bXfvDR83dH8axFtAdwkvYAqkgD4DgNgOM0AI7TADhOewAnaQ/gNu0BHKc9gCrSADhOA+A4DYDjNACO0x7ASdoDuE17AMdpD6CKNACO0wA4TgPgOA2A47QHcJL2AG7THsBx2gOoIg2A4zQAjtMAOE4D4DjtAZykPYDbtAdwnPYAqkgD4DgNgOM0AI7TADhOewAnXd8DLO6cE9EVMa4QWdwIYwzWz+UQEUpCMfQp4IZgKIwxgp9bwF7KnGV+1lCb2kVJOIYv/vKbKNW6Zq2H7+epb2rHCxr+GBog8Fv6a0YyQ2xuupWm7Q8w0PseiWQlGEFEFhcTLnPFa5WiztfsXAr/jfGYyl6mqq6F1LZ2suPzpL85QmAmO07f4QN0vfQWbfc9wdzMJBfOHS+sFbVWK+L1zhhEBPHzVNW1sPuR50kkQxzvOcjwhW8xFVVbZHpynD1Pv87ufc+SW4DMj98xeL6XqcnLWOsVngTLXLywuVTna3Uuvk8wFKG+qY1U670kyg3p/jP0dO/FGosp39QgxljmZrK0dj5Ox6MvcGN1JeJDPq+vheudUHilCwQh+/csZ754h94Pu8FYrF0MAIAxlpmpCcpvqmPr3Q9T23QnkVhS18ev83lhffwCI0On+fnUZwz/cppwtBRjLSLCPzbU3tQDUI4qAAAAAElFTkSuQmCC\',\n    \'popup_open_focus_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAD7klEQVR4nO3dz2vbdRzH8efnk2+ab9M0/cVcV5Ywa7rVjWZaqT+ourYePIgHhWqHHhQ97A/wB4h48VAP4sGTwkBEGIhuVkRQCipktdNSZatpKbRlhZEdbOtIltS2+X4+HpJOL70V0/bzfhxyeR++H8jrm08+r8tHtRzutAA65LFRKqCUJtHdR+LEg/jRJoyxoBQ7sjLfy3MFBKbMzYVplmevULq9SrSxDROUAfCg8uWX8qsc7epj8OwbdKYHqY+B0oDd+dlif7AWtjYgtzhL5tKH/HH5C+pjrVhrUG0dx22psMrpMy/w9LlRGlujrObyLM9PU8yvoLWH3SEFqvop8707N9ZQVxflaOo+jhzrIAggc/E845+9TSTaiIo1H7Htd6d5+d0xwhGfmZ+/Z2bya4r5VayV1/9AUIqIHyWVHuCBgWHibVG+/OB1psc/wUPB0Nl3iLf6TI2PM/Htx/jROH40Xutli11kjeHaxFdsrhd54rlzDI68xdLMj3jJ7kfoTD/MSi7Ptckx/IY4WnsYE9R6zWJXKWJNh1jMZrhn7gyp06foeXQYnTjxEPUNmuX53yjmVwiFwlhrar1asesq27k1hqXZDNZYkif70ZGGOEpDMf+n7PkHnLUWpTWl/BomUPgNzWhb/alXIa/GyxP/F6VDoMAGZfT2YQJ5+x1S/a6VQtd2IaLWJACOkwA4TgLgOAmA4yQAjtP/PRIIV/x79JcewEnSA4gqCYDjJACOkwA4TgLgOAmA46QHcJL0AI6THkBUSQAcJwFwnATAcRIAx0kAHCc9gJOkB3Cc9ACiSgLgOAmA4yQAjpMAOE4C4DjpAZwkPYDjpAcQVRIAx0kAHCcBcJwEwHESAMdJD+Ak6QEcJz2AqJIAOE4C4DgJgOMkAI6TADhOb5//5ZYQd9y5GEQptAnKWGsJ19VLGeQCC+E6H6UspryFvrn4O1sbikSql4gfxdiAO+WQOFC01hgTkOjqI+QpcgvTeNezl8ktLpDsTtGVHuLqxEViTYcqXZG0gweDAqU0xcIa7clTpNJ93P5rk+zkGN56YY3MpfcZefMjegeeZWO9wGK2cquU0nJ37P6nwFqsDWhPnqT/qVeINUf44cJ5bsz/gmrr6LKl/BpPvvQeA8+/SnkTrs9dZSk7SamwVrlgaMcQbG8VMt+rc2sN4bBP4ngvqZ7HibUo5q5McWF0GK00quVwp1VKs7Fe4P6hFxkceY22jnasASN/B/Y/W7kE3POgcOtvpr77lJ8+HwWl0boaAKjsEevFW7TcdYyex54heW8/9Q1NGMPOpwO7/QSZ79W5UhAEW+QWpshOfsON+V/xo3GU1lhr+QeeOKyvRkHLggAAAABJRU5ErkJggg==\',\n    \'mode_normal\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACkklEQVR4nO3dwW7TQBCA4X/WaztO44oIqRJB4kLfgPd/F7gFJGhpjR2v7R0ODoEL4koz813XUQ777yY+jby9/6CcqSqgxKohVhtECuCy7F4oBZZpZB57VDMi4bIWLw/lTFHW1Ls9qplpHMjLAAh/j0D++Apf/y/XVZFQUNYNVXNLGp6Yhg4JawQRQDVTNi1V09I9HDl1D+S8gPrpvw6CBKFuWnavDxRlzen5KyKBqKoUsabatjweP5L6J0IsCSH+Dsy9fAqn/olp7Nm/uadqWtLwTARls9vTfTuum1/WoHn9hF8AVyUUkbzMfP/yif3hPXMaCLFqyKqcugdCLM+b766SKlJEpnEgDR1V0xJitWEae/KygPidb4IoaegoYk0QCeQl4fe9EQqCkJcJRDi/EPrJt2fd8/CPp9yV8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCM8wCMC6DnQYI+NMKSX3MDwzwlys0WCeJzAi2QdUJsubkhz4kwjz1FUVE3LeqDo66cQM4UsaLe3pJOP4iqmTQ8sXt9OE8Pm5EinmdIKf7T8NKd91DW8cCaM6/u3qFzYpkGokhgOnUUZc3+cM/3z5+Yxh5EfOuvyDohtqK9e0e1uaF/PCJSrLODRQKn569UTcv+8J40dKShW0eLeQYvnCJSUDU31Ntbljnx4/HIr+N9mR4uEkj9M/M4UG1bdq/u/P/AFcnzxNg9MKfT5Q0A4CfV1vARPl00VAAAAABJRU5ErkJggg==\',\n    \'mode_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAB2UlEQVR4nO3dQY6cMBCF4Vdlg0dM1FGk2WWbG+T+h2qU6W6wcWXBNNJcINHw3rc1C6T6sdiV/fz1O/AhImAAfChIeYS5A8epfFWBQG8rtroiYoOZH2f5eCg6Uh4xTt+Rx/LpIfn6IgJbq6j3GXW5HfPN+2HHUF5Rvv1ASg5EQJ/+uZgBPoxI+Q2eZ6zvV8AMHhFIuezD9+fw5ZwCboEyXZBfXhERcAMwTpd9+PrqKRgC43SBe4L7UJDGF2j4XDxl5DLBUx7hZv/7feQfcwBpKHD97fMyc2j65BQAOQVATgGQUwDkFAA5BUBOAZBTAOQUADkFQE4BkFMA5BQAOQVATgGQUwDkFAA5BUBOAZBTAOQUADkFQE4BkFMA5BQAOQVATgGQUwDkFAA5BUBOAZBTAOQUADkFQE4BkFMA5BQAOQVATgGQUwDkFAA5BUBOAZBTAOQUADkFQE4BkFMA5BQAOd/agtCqODoBYGsLfKsrtlYBaHEUk9472nKHR3TU+4yuS4BGwFAff7C1FW5mqMsN631G1y1wegFHXR9YbzPMbN8dbOZY3q/oW0OZLvC075RWDufwvNx776iPK9bbfJwd28PNPq6F9YFcJqRBG8TP4rk+vi13bG35NNe/2MqK7uNmzQ8AAAAASUVORK5CYII=\',\n    \'mode_pressed\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACFklEQVR4nO3du27bQBCF4TOzFzqSYMNu0+YN8v7vZMOWTXK5OymkKEmVJkBgnvNVgpaFgPkpStXY12/fA1cRAQOQyoRUJpg5Ardj+cR6W9HbjIgBM7+9n3++iBhIeUI9PsBTuYxds98HA/J0AsaG9eMVbTnfIsjAZfhlOmI6PaKPgdYaIjT9PTEzuDum0xNSrpjPzzAz5IhAyhOm0yO2tqGPDjODmf3vzyz/2Ogd6xioX04ovaHNb3AAqMcH9D5uw5edus62rSvq4R7uGZ7KBE8FvW8aPokxBgBHvjvAU6kIQM98MmMMpDLBzVy/9smYXf/ym8P/frnsmQIgpwDIKQByCoCcAiCnAMgpAHIKgJwCIKcAyCkAcgqAnAIgpwDIKQByCoCcAiCnAMgpAHIKgJwCIKcAyCkAcgqAnAIgpwDIKQByCoCcAiCnAMgpAHIKgJwCIKcAyCkAcgqAnAIgpwDIKQByCoCcAiCnAMgpAHIKgJwCIKcAyCkAcgqAnAIg570tWhNHJgLw5Ohtgfe2IsYG93Q5kd0zMxiAbfmAR3S0j1fknK975RTBnkUESq3Ylnf0bUE2c7TljJQr6t0Jra3XvXK3PYPy2cXltnYzlDohtob1/QVmftkdbOaYz88ovaEe7hHIiDH0RNgJs8uM3YC2nLG+v9zO8q+LDG1+Q19nlLsjUql/rBmXTyyA0WYs16/93+f6AzMwru9iYJfqAAAAAElFTkSuQmCC\',\n    \'mode_disabled\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACe0lEQVR4nO3dzXLaMBSG4VeysPkrUEgmTbrtHfT+76bNdBoaiAFjbCx14TQ30GmZcL5nCwvNnFce7Y77/OVrAsA5UtcBUIynDEdTfJZB/6u8Vw5SSjTHimNVEmOHzwKkfrCh/5Mjns8UozGLm8+EQU53bomxw+EueXz5S4mEc57xZM4s3VE+/+RQPveXGwjQD386X7G4eeB03FPuNqQYSbr+V8LhnCMvRny8faAYjtk8fcP5jJBiRzGasLh54FD+ojkd8T7Dea+7f2WauqJta+bLe9qmZrdd44HXm797HX649DnlH3Hek2Jkv31itvxEyHN8MZ4yGOTU1Q7vM/Tqu27Oedr2ROzOTGcr/HA0fX3wxUufTf4T5xxtU1OMJnjvg4ZvUIwdznm8Pvm2+UsfQC5LARinAIxTAMYpAOMUgHEKwDgFYJwCME4BGKcAjFMAxikA4xSAcQrAOAVgnAIwTgEYpwCMUwDGKQDjFIBxCsA4BWCcAjBOARinAIxTAMYpAOMUgHEKwDgFYJwCME4BGKcAjFMAxikA4xSAcQrAOAVgnAIwTgEYpwCMUwDGKQDjFIBxCsA4BWCcTynhnPaDWfNn5v5UH8hCrggMSSkxGBT9lri62hFTJC/GpKTdQdcvkWWBMCj6DaKx6yiffzD+sOj3yimCq5VSIsbIdLai2m85HfcEnwUO5YZiOGG+vGf/subc1IBDq0OvROp3CGdZYDK/JcbIdv2IzwIBEj4LbJ6+0zY1s+UdsTvTNjWx60Bvg/ct9cujQ14wGBRU+y3b9ePbXF/3xCac9+xe1hyrkulsRTGaEPLh25pxea8ckGhOR7brR07Hw9vmcIDf5rLckVmhXHEAAAAASUVORK5CYII=\',\n    \'mode_focus\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAEHUlEQVR4nO3dS2xUVRzH8e85d9qZznQ6TRgk0gdKS6VQ1FpSElsJxAQTCQnEV2NYmLgwMca4aIwbdecKiSwMG2PiY0GQSAMSExY+oKhAQyOQ2DbhlWpLE4badnRKmXv+LjpTq6HiAm3p+X+2/8m9Jzm/Se793cUxVfUtAmCDgKlcFrBUrWpmed0jRONJnAPD3ASdL+Q5gHN5Ri6fZXCgh8nffqUsUYlzIQARAGsDchOj3LuymbYdr3B/02OUJcHa21xZ3RVE4EYOhi/2cfLIB/SdPEQsUYmIw9Q8sEFyE6OsffQptrzwJql0GSNXMvT3HGXs2s8EQQQRueWFjTGFG+h8oc6dC4mWJalvfpza1fXkb8L3hz/l2GfvUBorx9xTu0aW1a6l442PKY3F+OGLD+nueo/xa0OFC9/64uruYDBgIBZP8dDm59nc8ToVSyo4vPdtzn67j4jB0Lajk1Q6xtf7PuLQ3leJVywlXrFkvteu7iBxju7Pd5PLjvFs5x7atr/GlZ9OEKla1cJ9TesZuZKhu2s3iYo0QaQEF+bne83qDjLGkFpaw/nj+3lwYwdN7W00tm7DLq9rIZ609J8+yvi1XwhKojNPiGrxKD4niIScP7EfcUJ1Qys2Gk9iLYxlBhFx87xM9V8SEUwQIXt9mDBviCZSWCn824OgZJ6Xp/4XhRAYA+JCbLFGmOtVQi1CM3tt0KrHcxoAz2kAPKcB8JwGwHOzAnC7j4pq8fhzr23xY4/R/ffHzF6L9gBe0h5AFWkAPKcB8JwGwHMaAM9pD+Al7QH8pj2A57QHUEUaAM9pADynAfCcBsBz2gN4SXsAv2kP4DntAVSRBsBzGgDPaQA8pwHwnPYAXtIewG/aA3hOewBVpAHwnAbAcxoAz2kAPKc9gJe0B/Cb9gCe0x5AFWkAPKcB8JwGwHMaAM9pD+Clv/QAhddAPSXEGyKFvTYG61weESEaL585hkwtXiJCaSyBMYLL38SOXD7HjZyhvnkL0UQKcaEGYZGyNsCFeRpathIpNVy99CORwYFTDF+8SO3qlTy8aSfdB3eRStdixCH/6mBStdAZwNiAidFhVqxpZ93GrYxnphjo+ZLIZHaUk0feZ3ndu2zu6GQym+Hc8QPTx4raYLo2nCsDMusOOl+Yc2MQcTgXsqKxjW0v7aK8MsaxA58wdOEMpqahVXLZUTY99xbtO3YShtB36hvOn+hiIjOEDSKz7vR3ZtaddL4Q5yKO0miChvVPsG7j0yQrLX2nezm450UwBlNV3yLGWKYmszS1P0Pb9pdJVy9DHLg8c6dL3TWMgUgJjF+/Qe9X+/iua8/0G4C10wGY/pFl8vcxUulaGjc8SXVDK7FEChfKP38rFp0v5LkBwvAmVy/10t9zlOELvZSWlWOtRUT4A/I4yZBwm315AAAAAElFTkSuQmCC\',\n    \'mode_focus_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAD9UlEQVR4nO3dTWhcVRjG8f85d5KZyUyaIUpNmiatdSZpjdDmg0TILFxo/FhIgwhdVApuRVBQcKO4ctVNN7pwpy0VxK+WKkiVNBXb2tgmUaoJpGMoLYkNTKaZ6SRN5rwukhm7MLtiPs77W8zmLObAee6de59ZvKYp2SUANgi4V8wDlqZUBzuSnYSjtYgDjOE/yeqHrm/cdQPOLTOTGeXGxK8sFLJEYwmcKwEQArA2oDifpXFPB+mB19nVniYaB2PLX6I2MxFYWoTpzDgXz3zMn5dOEYklEHGY5rZeKc5nae97if4j71JbH2X2Zo6paxco5P7G2mDNDJRzp+sbd13EURWuobmth4ZHm3EluHD6OEOff0B1JI7Z3vK4PNLSzqF3PqEqHOG3898weu4khbnbiF7+W0Y4GifV+Rzd/UfYVh/j1EfvM3buJCGDIT3wFrX1ES5/d5rzXx4lEksQidWt957VAyTiGBk8wWJxnqcPv03fwTeY+uMnQk2pbna1dzN7c47RoRNEYglsKFR5SFBbhDHUJhqYHDlL8sCzpDoPsK/nReyOZBfRuGXq2iUKudsEoSrEufXernrQRABBxDE5dhZxws7WHmy4phZjoJCbQUR/87cyEcGYgLu5WVzJEI5tw8rqrd4EoXXenvp/CCYIwIC4ErbyMqFXvz8qZ22w67oRte40AJ7TAHhOA+A5DYDn7gvAGn8pqi3o37O2lf+S9Pz9UTlr0R7AS9oDqDINgOc0AJ7TAHhOA+A57QG8pD2A37QH8Jz2AKpMA+A5DYDnNACe0wB4TnsAL2kP4DftATynPYAq0wB4TgPgOQ2A5zQAntMewEvaA/hNewDPaQ+gyjQAntMAeE4D4DkNgOe0B/CS9gB+0x7Ac9oDqDINgOc0AJ7TAHhOA+A57QG8dH8PsDpzTkRHxPhCZHUijDFYV1pGRKgO16B3AT9UhaMYA255CTvz1xhLi4bm1l7CkRhO3NqTKNWmZm2AcyVa9qYJQjCdGSN0Y/wXpjPXaWrdQ6rreUYHjxNPNCBGtB3cKgwYE1CYn6Vx935SHX3ks0tMDH9LaCGf5eKZDxl47Cjd/a+wWLzD5MgPK2NFrdUQbHbGgAjOlWjcvZ/0wJvEE2GGvviUW5NXMM2tPVLMZ3nq0HukDx5meQkyvw9zfWyQwp3ZldGxa4TAVB4gdX2jrotzVIWjtOx9kmTHM8QThvHhq3x17FUwFtOU7BJjLPcW8jyRfpm+gdd4qHE74qBU0seBTU9WhoAHIcjPLXL1x8/4+etjK28AdjUAAMZYFu7mqHu4hX29L7CzrYdITR06Q3JzMwZKpWWmM1eYuPw9tyavUh2NY61FRPgH9SuipQDHx4YAAAAASUVORK5CYII=\',\n    \'handover_normal\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADFUlEQVR4nO3dy28TVxSA8e+O52G7iR/EkWl5LBKRUEKLLJCQ8H/fBasiJCq3JgVFYBw3sRMnDjjxzHBPFybqptBNkYPP+S19pPGV/I01szqu3twQAOcC8iwFhLXmTdaaN4jiBC+C4/MEbH6F5+AQ+ch49BejQY90dkGclBDx82m9uSHOBaSzc+qN69xtPSEpV5hOP5CmKc65T1/z7xf/5xg2v5JzEQqFAuWVFfAfed15Rn+vS5wUERHCyx//1uY9tltt9vs9Dnd3ybMM+eyFzbfE4XBBwLXGOtutNrVGk99//YUoTgjzPKXeuM52q82ff3QYHx0SJ0WiOF70uc3/7Gh4wORkzE8PH/P+9Jg3u78RIsLdVptBv8f46JBiqYz3HhG7+5dNFCXkWcpu5wVbO48YDt4SrDVvkpQrHOy/I05KeO8XfU7zlYh4wijmbHLCdHrO7c17BGvNG0yn78mzDPflx0mzFATnHKcnR9TWvyeI4oQ0ndkDnyIORzqbEYYRgYh8etUzmjjnEBGCRR/ELJYFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoFwA2H4ghS5/80DEUyiE/Nf6QbNcwjCcL4wYjw74bmWVQhBgfwQ6ePGsVuucjUcEw8Fb8Dn1xjp5luICeyxYVs45vPckxRKVao3+Xpcwm13wuvOM7VabycmYPEsJw2jRZzVfgfeePM/Y2nnAYe8Vx8MBYZyU6O91qTWa/PzwMS87LzibnOLAlkktCWG+MzApltjaeYDzGd3nT4ni5HJ5tCNLZ9y+c5/NnUdMp+ecjo9J0wucC7jSy5Ft/sW5iFAIC1SqdSrVGge9V7x8/nR+c7tgHgDM7/Z0dkF5tcqtjR+pr/9AGEX2ivjNcyCeyXhEf6/L8XCfKC7OP0f4G/WVNKg7NCjvAAAAAElFTkSuQmCC\',\n    \'handover_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAC9klEQVR4nO3dTU8bVxSA4fde5t4BozoBJ8aQD6XBC6hYRJGyyCI/v8oKKYsWCaqWALEAGcfuCBs8X6cL1+kqyaYq1Oc8Sx9pZqR558q749Y2XgqAc56yzEFgfWOLVnuLEFOkFnB8nWDz+zzHIXXFaHDJ1cUn8uktMV1BpJ5N1zZeinOefHrDw0cddl69pdFscTstKKsK5/6+ydevb/N7PBfAe8dymlLnE34/2Kd3fEhMlxER3HqnK8X0hifbu+y+fsfVMOPz1YCyqr9zZ/N/4r2n2Wyy2WlzfvwrB/s/E2IkKcucB4867L5+x1nvkizLCCEQQnLXz2z+RSLCaDRiPL6m293j+s8hJ7/9QoLAzqu3DIYZWZYRY0REELGvf9GEECjLktPTM7b33tA/P8O3NrZYabYYDD4TQrAXv8BEhCRJGI8n5CU8297Br7e3mOYFZVni3Df/TpoF4Zzjejxm7fEmPsSUsqju+pnMf2R+whdFQZJEvIhgH74+zjlEBH/XD2LulgWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnAWgnBep8d42RmjjvZ8tjBhdXZKm8csPZrHNN4WsNhpkwz6+f/GJKr+h2WxSlZUtjlpwdV0TY6SxEul9PMIX01v+ONhns9MmCUtftodZB4vDuX++/KqqePrsCRcnRwz75yQxXaF3fMjDVptud4+T0zMm44mdBAtGRIgx8uLFc8rJiMMP7wkxnS+PdhR5zvPuT2zvvSEv4Xo8pijmuwTv8XZkm39zLgJLS57V1QaN5cjFyRGHH97P3qvzswBgdkTk01saPzzg6Y87rD/eZCnM1sje5+3oNv/u9nikFrJhn97H2bEfYso8nL8AkOY9Xi2MMiMAAAAASUVORK5CYII=\',\n    \'handover_pressed\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADFUlEQVR4nO3dy28TVxSA8e+O52G7iR/EkWl5LBKRUEKLLJCQ8H/fBasiJCq3JgVFYBw3sRMnDjjxzHBPFybqptBNkYPP+S19pPGV/I01szqu3twQAOcC8iwFhLXmTdaaN4jiBC+C4/MEbH6F5+AQ+ch49BejQY90dkGclBDx82m9uSHOBaSzc+qN69xtPSEpV5hOP5CmKc65T1/z7xf/5xg2v5JzEQqFAuWVFfAfed15Rn+vS5wUERHCyx//1uY9tltt9vs9Dnd3ybMM+eyFzbfE4XBBwLXGOtutNrVGk99//YUoTgjzPKXeuM52q82ff3QYHx0SJ0WiOF70uc3/7Gh4wORkzE8PH/P+9Jg3u78RIsLdVptBv8f46JBiqYz3HhG7+5dNFCXkWcpu5wVbO48YDt4SrDVvkpQrHOy/I05KeO8XfU7zlYh4wijmbHLCdHrO7c17BGvNG0yn78mzDPflx0mzFATnHKcnR9TWvyeI4oQ0ndkDnyIORzqbEYYRgYh8etUzmjjnEBGCRR/ELJYFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoJwFoFwA2H4ghS5/80DEUyiE/Nf6QbNcwjCcL4wYjw74bmWVQhBgfwQ6ePGsVuucjUcEw8Fb8Dn1xjp5luICeyxYVs45vPckxRKVao3+Xpcwm13wuvOM7VabycmYPEsJw2jRZzVfgfeePM/Y2nnAYe8Vx8MBYZyU6O91qTWa/PzwMS87LzibnOLAlkktCWG+MzApltjaeYDzGd3nT4ni5HJ5tCNLZ9y+c5/NnUdMp+ecjo9J0wucC7jSy5Ft/sW5iFAIC1SqdSrVGge9V7x8/nR+c7tgHgDM7/Z0dkF5tcqtjR+pr/9AGEX2ivjNcyCeyXhEf6/L8XCfKC7OP0f4G/WVNKg7NCjvAAAAAElFTkSuQmCC\',\n    \'handover_disabled\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACj0lEQVR4nO3dyU4bQRCA4b8Xb4ztjGWQcUKibEJ5/9eBQw6OwJAYvDJepisHG5RTLiRxcNV3nUtL9c+o51Su0/soAM45ynIDQNbqcNTsEGJERDAvnAiL+YT5ZERZromx8jTXCNvhbzZrGlmb3tlnqvWMtNmQUgnO7fXs5rkE5zzt7inlZs33q6+MR1eEUAWEyG74ebfP6dtzimLGZDTcDt8cDOcctXpG/90XGlmb4eAC7yMxlRsa2St6b8+ZTUasijk+RLwP+z6z+cOKhxmr5QP58WuWxYK72wEeoHf2iWUx2w2/su9zmr/E+4CkxPT+lpP+e6q1Bv6o1aFazyjmE3yIgF36DpnznvWqIEki7/bxWbNDKjeklPZ9NvPPONbLgkYzx/sYbfjKOEBSub3rYf/5isn2Emj0sgCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCU8yKCs92A6jjnQAT/MJ8QQsUiUEQQYrVOsZji59PtOtFqPUNsWeThEyGESIxVxqNr/OM60ayV43xAxBZIHSoRIUmimZ8wvhuymI6JIVYYj65pZG3y4zdM729Yrwocbrdeat/HNs+ym6GwffNbeY/VquBmcEmIkYgIIVYYDi5YFnNO+h+QlFivCsqytN3RL5wAznkq1drusz/k5tvl053PPa6PB7e9C9Qa5N0+R80cH8J2q9zvIrDn//dzABGKxZTxj2sW83vCL+uBfwKb7u78POo39wAAAABJRU5ErkJggg==\',\n    \'handover_focus\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAEC0lEQVR4nO3dy0+cVRjH8e85M3QuzIwDqKUlgNDWDrRBSZwG26otLppQXbioluiiXhb+AdWoMW5c4MK4cOWiiZeaRqNiE11UBWuCpZVbo0ESCBBNb/YCmXboQMvM+7iYmdpF6YrI5Tyfxbs5yTsnOb+8mff3Lh5TtrZeAKzPz41MGmMs1Ykk1Zu3EQjHEA8whjuSwkXXl++6AS+X5cLEIH+PnCIzM0U4WoGXywLgh/zhZ65NUbUpSWv769Q37SYcBWPvfF+1sojAzTk4Pz5CT+eHDP/6FaFIOSIepmL9g5JJT/HQE8/z9KsdxCrCXD6TYnL4BOnURaz1U4jaAoyuL+N18TzWBEupbWihamMNuSz0fHOInw6/TSAcxUTi66SyrokX3z3KmkCQoeOdDHR/zkzqIiJ3+2G1UhhjCIQiNCT38mjbS8TujfD1B68x2PUxfgy0tr9DrCJI73ff0vVFB+FIGaHS+FLvWy0iEY/+rs+Yy6TZ+/Kb7N7/FpN/HMdfs7mFDU0tXD6TYqD7MOFoGdbnx/NyS71ntZiMIVZeyejQDyQeaSORbGbrzn3Y6kQLoahlcriXmdQlfL4SxPOWertqsYmACOJ5jJ0+hohQ27gDGyi9B2MhnfoHET341UwQrPVxPXUFL2sIRuJY8fLvg9bnX+Ltqf+HYHw+MCC5LDb/GkH+EaHcUDxrY9Cqx3EaAMdpABynAXCcBsBxtwVggU+KahX676ztrS9Jev7uKJ61iPYATtIeQBVpABynAXCcBsBxGgDHaQ/gJO0B3KY9gOO0B1BFGgDHaQAcpwFwnAbAcdoDOEl7ALdpD+A47QFUkQbAcRoAx2kAHKcBcJz2AE7SHsBt2gM4TnsAVaQBcJwGwHEaAMdpABynPYCTtAdwm/YAjtMeQBVpABynAXCcBsBxGgDHaQ/gpNt7gMLMOREdEeOKW4NBjMF62SwiwppAKfoUWP0EoSQQwhjBy85jL0wMMT9nqG3YTiAUyadjoUmUakWzxoeXy1G35XF8JYZz44P4/xo5wbnxcWoaNtK47SkGuj4hWr4uP2BIRB8Kq4SxPmauXqGqvplE8jHS0zcZ6T2KfzY9TU/n+7S/8REtbQeYy1xldOhHxPOw1sfdp1aqlUAK08KqNjzMk88eJBoP0n3kEGfHfsNUrN8kmWvT7DnwHruee4XsPEz83sfY6Z+ZSV3KD5Na6DuBKVx0fdmui+dREghTt2UHieQeonHDyKl+jnTswxqLKVtbL8ZYbsymaW59gV37D3JfVSXiQS6nfwdWOpH8EHB/CaSn5+g/9im/fNkBxmJtIQAAxlhmr6cou/8Btu58htrG7YRK43g6Pn5FrxsDudw858f7+PPk95wd7SMYjmGsRUT4FzkDuSF/050lAAAAAElFTkSuQmCC\',\n    \'handover_focus_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAD7klEQVR4nO3dz2vbdRzH8efnk2+ab9M0/cVcV5Ywa7rVjWZaqT+ourYePIgHhWqHHhQ97A/wB4h48VAP4sGTwkBEGIhuVkRQCipktdNSZatpKbRlhZEdbOtIltS2+X4+HpJOL70V0/bzfhxyeR++H8jrm08+r8tHtRzutAA65LFRKqCUJtHdR+LEg/jRJoyxoBQ7sjLfy3MFBKbMzYVplmevULq9SrSxDROUAfCg8uWX8qsc7epj8OwbdKYHqY+B0oDd+dlif7AWtjYgtzhL5tKH/HH5C+pjrVhrUG0dx22psMrpMy/w9LlRGlujrObyLM9PU8yvoLWH3SEFqvop8707N9ZQVxflaOo+jhzrIAggc/E845+9TSTaiIo1H7Htd6d5+d0xwhGfmZ+/Z2bya4r5VayV1/9AUIqIHyWVHuCBgWHibVG+/OB1psc/wUPB0Nl3iLf6TI2PM/Htx/jROH40Xutli11kjeHaxFdsrhd54rlzDI68xdLMj3jJ7kfoTD/MSi7Ptckx/IY4WnsYE9R6zWJXKWJNh1jMZrhn7gyp06foeXQYnTjxEPUNmuX53yjmVwiFwlhrar1asesq27k1hqXZDNZYkif70ZGGOEpDMf+n7PkHnLUWpTWl/BomUPgNzWhb/alXIa/GyxP/F6VDoMAGZfT2YQJ5+x1S/a6VQtd2IaLWJACOkwA4TgLgOAmA4yQAjtP/PRIIV/x79JcewEnSA4gqCYDjJACOkwA4TgLgOAmA46QHcJL0AI6THkBUSQAcJwFwnATAcRIAx0kAHCc9gJOkB3Cc9ACiSgLgOAmA4yQAjpMAOE4C4DjpAZwkPYDjpAcQVRIAx0kAHCcBcJwEwHESAMdJD+Ak6QEcJz2AqJIAOE4C4DgJgOMkAI6TADhOb5//5ZYQd9y5GEQptAnKWGsJ19VLGeQCC+E6H6UspryFvrn4O1sbikSql4gfxdiAO+WQOFC01hgTkOjqI+QpcgvTeNezl8ktLpDsTtGVHuLqxEViTYcqXZG0gweDAqU0xcIa7clTpNJ93P5rk+zkGN56YY3MpfcZefMjegeeZWO9wGK2cquU0nJ37P6nwFqsDWhPnqT/qVeINUf44cJ5bsz/gmrr6LKl/BpPvvQeA8+/SnkTrs9dZSk7SamwVrlgaMcQbG8VMt+rc2sN4bBP4ngvqZ7HibUo5q5McWF0GK00quVwp1VKs7Fe4P6hFxkceY22jnasASN/B/Y/W7kE3POgcOtvpr77lJ8+HwWl0boaAKjsEevFW7TcdYyex54heW8/9Q1NGMPOpwO7/QSZ79W5UhAEW+QWpshOfsON+V/xo3GU1lhr+QeeOKyvRkHLggAAAABJRU5ErkJggg==\',\n    \'handover_notice_normal\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADIklEQVR4nO3dTW8TVxSA4ffcGdvjsXA+XMUxC6JGWaSrqoI0QmKHWAELfikLllS0m1ZCIARS1BaQAqGEfBNTJ+OZkefeLpxU3VhdEuecZ+PFlcaW5r3j642PzHWXA4BzQl5WAKxcTVnpNUkbDh8wU877wPv9nNcfM7Lc00oifBjfWJnrLgcnwmk+Yqnb5P56h9k04vOgJCsqnMCkBuTs1dYv7roPUIuFTruBD/DkVZ9nbwa0EkcIEDsHp8OKH1dnuLc2z8a7L/zy8oSi9ISJlzbTRIA4cix1m9xdm+PaQsLD3w5o1h1xXnqWugn31ub5+eUBW3tDWklEs+H+LcxMt/NtvLmTsXNU8ODWInvHM/z6e58Y4P56h413X9jaG9JOYyofCGHyo8VMp2bDkZcVP7044PYPC/z5V4ZbuZoym0b88eGEVhJR2anv0vIekrpj77igf1KyvtrGrfSafB6U5OX4wGcuuQAiwvZhznI3waUNR1ZU9rhXIjA+FJ7mFfWa4HwAsZ2vjgiEAO5rfxDzdVkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAyjlh/L/xRpfze+4qH6jFYhPClKnHMh4Y8X4/p9NuEEdiY2MUEKAKgcVOwvZRgXv9McMHWOqm5IXH2ang0hKBURW40ozpzSc8fzsgzoqKJ6/63L0xx85RQV5WJDVnT4NLRhBG3lOOAndudNjYytjcHRK3kohnb/7m2kLCg1s9Hr/YZ/+4QETGw6SshOl2dg8rH7iSxty5/g0Bx6Onu6SNaDw8WgTy0nPzuxlufz9L/6Rk+zDnNB/hZPLZ4CIMR7b1/xseHajHjsVOQm8+YWMr49HTQ5wIzp1ND4fx90OWezrtGuurbb7tJjRqgg9M/IUQ/vNGtn4x188niH86Knj+dsDm7nC888/W/wEGKyl6wFo6VwAAAABJRU5ErkJggg==\',\n    \'handover_notice_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAC9ElEQVR4nO3dPW/TUBSA4fdeO7GTKKnSlIYsIChSUSe6hIwMbAiJv8rCyIRAKh8qU0VBlEpEgTaB0FDHH829DC4jsCBRcs6znsGR/Dq+no5pd697AGsNae4Az41enY1ejVpkcQ4w/JrX+UWeG2DhPIdHKfvDhCR1NOIA5305b3eve2sMp9kZV9dj7vXXuNQMmCUFWbHA/O7i6sLzHsLA0GpUSQt4/HrKi7czGrEtZ9bC6XxBf3OF+7dX+TCa8eT9d/Izh/9jfuri8xgM1hp6nZgHg1WurMc8fHZMXLWEae642o25f3uV3f0Jo8mcWhQQVe2//uXqLxsezxl/y7izfZnPX1d4ujclBLjX73A4OmE0mdOohTjnOX9FqCUSVy1Z4Xi+N+burTXefEywG706l5oB70en1KIA5/TOLyvnIapYJic58yynv9nCbvRqzJKconB64BPAA8bAeJpxrRtja1H5t6DPvRwGSLMFUcVgvUeffIGMKT8R9agvnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAYgnAV0P5BAP++5dc4TBkaXwwkThgbnwR4epbTqVaw16N4YGZyHzkrEcJJh94cJ6Rn0OjFZ4bB6KlhaxpRrZOtRQLsZ8/LdjDDJFjx+PeXBYJXxt5wsX1CtaAXLaOE8xZljsLXG7kHCwac5YSMOePH2hCvrMXe2u+zsjflykmOMLo1dJs556rWQwdYa33PLo50x9Sgol0cbA2nuGNxscfdWmzQrOJ6mzLMFViv4r3kgDCydlYh2M2L34JRHOxOMMVh7vj0cyvdDkjk6zQr9zRbXujFRpTwp/qqBn2dGnV/cuTHgHAwnGa/ezTj4VO6GNufzH9DYFN7StTAzAAAAAElFTkSuQmCC\',\n    \'handover_notice_pressed\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADIklEQVR4nO3dTW8TVxSA4ffcGdvjsXA+XMUxC6JGWaSrqoI0QmKHWAELfikLllS0m1ZCIARS1BaQAqGEfBNTJ+OZkefeLpxU3VhdEuecZ+PFlcaW5r3j642PzHWXA4BzQl5WAKxcTVnpNUkbDh8wU877wPv9nNcfM7Lc00oifBjfWJnrLgcnwmk+Yqnb5P56h9k04vOgJCsqnMCkBuTs1dYv7roPUIuFTruBD/DkVZ9nbwa0EkcIEDsHp8OKH1dnuLc2z8a7L/zy8oSi9ISJlzbTRIA4cix1m9xdm+PaQsLD3w5o1h1xXnqWugn31ub5+eUBW3tDWklEs+H+LcxMt/NtvLmTsXNU8ODWInvHM/z6e58Y4P56h413X9jaG9JOYyofCGHyo8VMp2bDkZcVP7044PYPC/z5V4ZbuZoym0b88eGEVhJR2anv0vIekrpj77igf1KyvtrGrfSafB6U5OX4wGcuuQAiwvZhznI3waUNR1ZU9rhXIjA+FJ7mFfWa4HwAsZ2vjgiEAO5rfxDzdVkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAylkAyjlh/L/xRpfze+4qH6jFYhPClKnHMh4Y8X4/p9NuEEdiY2MUEKAKgcVOwvZRgXv9McMHWOqm5IXH2ang0hKBURW40ozpzSc8fzsgzoqKJ6/63L0xx85RQV5WJDVnT4NLRhBG3lOOAndudNjYytjcHRK3kohnb/7m2kLCg1s9Hr/YZ/+4QETGw6SshOl2dg8rH7iSxty5/g0Bx6Onu6SNaDw8WgTy0nPzuxlufz9L/6Rk+zDnNB/hZPLZ4CIMR7b1/xseHajHjsVOQm8+YWMr49HTQ5wIzp1ND4fx90OWezrtGuurbb7tJjRqgg9M/IUQ/vNGtn4x188niH86Knj+dsDm7nC888/W/wEGKyl6wFo6VwAAAABJRU5ErkJggg==\',\n    \'handover_notice_disabled\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACj0lEQVR4nO3dyU4bQRCA4b8Xb4ztjGWQcUKibEJ5/9eBQw6OwJAYvDJepisHG5RTLiRxcNV3nUtL9c+o51Su0/soAM45ynIDQNbqcNTsEGJERDAvnAiL+YT5ZERZromx8jTXCNvhbzZrGlmb3tlnqvWMtNmQUgnO7fXs5rkE5zzt7inlZs33q6+MR1eEUAWEyG74ebfP6dtzimLGZDTcDt8cDOcctXpG/90XGlmb4eAC7yMxlRsa2St6b8+ZTUasijk+RLwP+z6z+cOKhxmr5QP58WuWxYK72wEeoHf2iWUx2w2/su9zmr/E+4CkxPT+lpP+e6q1Bv6o1aFazyjmE3yIgF36DpnznvWqIEki7/bxWbNDKjeklPZ9NvPPONbLgkYzx/sYbfjKOEBSub3rYf/5isn2Emj0sgCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCUswCU8yKCs92A6jjnQAT/MJ8QQsUiUEQQYrVOsZji59PtOtFqPUNsWeThEyGESIxVxqNr/OM60ayV43xAxBZIHSoRIUmimZ8wvhuymI6JIVYYj65pZG3y4zdM729Yrwocbrdeat/HNs+ym6GwffNbeY/VquBmcEmIkYgIIVYYDi5YFnNO+h+QlFivCsqytN3RL5wAznkq1drusz/k5tvl053PPa6PB7e9C9Qa5N0+R80cH8J2q9zvIrDn//dzABGKxZTxj2sW83vCL+uBfwKb7u78POo39wAAAABJRU5ErkJggg==\',\n    \'handover_notice_focus\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAEBUlEQVR4nO3dS2hcVRzH8e85M+NM5xE7mWBMato0bYymJCKk0bYBbUBFqiAUMaEuFLpw66OIoCsXEcFS6cZFoRShIn2gdSOklUCUKmlaX2mopmLTZOpm4rRJJ2kyc/4uJleLpK6CeZz/Z3Fh+MNw4fzuPXN/s7gmXd0gADYU5lZhEmMsdQ+0UdfUTixegXNgMCxE5o86X75zY8CVimQvn+fKxW8pTOWIpzK4UhGAMJQXv3Ajx7rGrXR276OhtZNYCqxd8HvVCiMCczOQHRmi/+RBfv76GGuSlYg4TKb2filM5njosT08+0oPqUyc3NUc4z/1UsiPY20Ymc/av5n5o86X71ycIxxLUtPcSfXmzbgi9J84RO/HbxONpzDJtTVy78ZWXn73MyKxGMNnDnPp9EFu5sfL0VGrwl3xu6lv76Zl1xtUVFVwfP8+Bk8fJoyBzu53SGVifH/qCOc+eZVosopoIrPU56wWkYhjuPcAs4U8HXsPsLPrLX77sY/w+qZHaWjdRu5qjuEzHxJNZbChCOKKS33OajEZQ6LyPq4MHmdDWxcN7dtp6diNrWt6hFjKlvf8P8exoSjiSkt9umqxiZR3dOcYvXAMEWFD8w5sLFGBtVDIj+mev+oJxoaYzl/DFQ3RRBobXO0mFFnik1P/D8GEwmBASkVs8DChV79HgrU2Bq16PKcB8JwGwHMaAM9pADx3WwAW/ktRrUb/rLUN/lXW9fdIsNYi2gN4SXsAFdAAeE4D4DkNgOc0AJ7THsBL2gP4TXsAz2kPoAIaAM9pADynAfCcBsBz2gN4SXsAv2kP4DntAVRAA+A5DYDnNACe0wB4TnsAL2kP4DftATynPYAKaAA8pwHwnAbAcxoAz2kP4CXtAfymPYDntAdQAQ2A5zQAntMAeE4D4DntAbx0ew9gyh9E9C0hvvh7rY3BulIRESESTaJ3AQ+IEIkmMEZwxTls9vIF5mYMNc1PEIlXgJQI7gpqdTEmhHMlarfsIhQxZEfOEf794jdkR36l7sFGNrbvYbh3P4nKOkRcuTHSMKxwAhiMDTFz/Q+qNm2nfuvTTE3MMnT2c8LTkxP0n/yArjc/ouWZ15gt5BgdPIE4h7EhuMNbKdVKYRARxBWp2rSNtq73SaZjfHX0EGO/fIfJ1DZK4cYET730Ho+/sJfiHIz+0Mfo4Cmmr1/D2tB/vJp0/gekzpftXMQRjiao3fIk9e27SaYtw2cHONrzPNZYTLq6QYyx3Jqe5OHOF9nZ9TqZdTWIQKmoO8CKJ4CFcASmJmYY+PIIfZ/2gLFYOx8AAGMs0zfzpO+pp6XjOdY372BNYi3OwZ2fDoLk6Xy5zo2BUmmO7MgAQ2e/YOzSALF4BcZaRIS/AJGltSPgauyIAAAAAElFTkSuQmCC\',\n    \'handover_notice_focus_active\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAAEDklEQVR4nO3dTWhcVRjG8f85M8lMZ/LRmRGTpo1NKmMi2rQBv2IVbVJRBEUokrS6UHDhVksRQVcuogsr2o2Lgl9QENNixYXSgtVErcYPaEyIbSPWmERSJ3YSO8mkd+7rYuZiwUY3waRz3t/ibl64HDjP5c48d3FMom6TANhQmHxuDmMsja030dhyC9FYLeILGMNlSemi89U7N+AXPCbHvuPsyAlyf2aIVafwCx4AYShufm42w/r0zXTt2ktzWyeRKjD28vdVVxYR8BZgamyY/sP7+WHgPdZUJRHxMamG6yQ3l2HLXY/wwJO9xJMxzk9kyIweJZ+dxNgwUozaP5jSVeerdy7iE4pUkUp3kmy+FilA/6EDHH3nOSKxakzV2nVS39zG4y+8T0UkytmBNxkf2E8+O1mMjioDhvCaGurae2ju2kN1qoa+fXv59tgbhDHQtet54skopz5+m9NHnqYydhUVsdRKr1otIxGf8c9exctluXH3PrZ3P8tPJ48TvqblNpraOshOZPh14DUq4ylMqALxvZVes1pOxhCp3cD0UB/Tw92sb+9g8x07sY2ttxKtsvw+eox8dgITiiB+YaWXq5Zb6XUuvs+5oT58ETbesA0bjddgLCxkJ/SdX+5EMDZEfnYK8QzReAIbPO0mFF7h1an/hxT32oAUPGzwZ0KffocEe20MWvU4TgPgOA2A4zQAjtMAOO6SACzxSVGVob/32hJ8SdL9d0ew1yLaAzhJewAV0AA4TgPgOA2A4zQAjtMewEnaA7hNewDHaQ+gAhoAx2kAHKcBcJwGwHHaAzhJewC3aQ/gOO0BVEAD4DgNgOM0AI7TADhOewAnaQ/gNu0BHKc9gApoABynAXCcBsBxGgDHaQ/gJO0B3KY9gOO0B1ABDYDjNACO0wA4TgPgOO0BnHRpD1A6c05ETwlxRrDXxmB9z0NECEeqlj6AUJUPEWxlHIzgexexk2Pf4y0YkukdhKM1xXRoEMqSsSHEL5BqvZ9whWHizDeEfx75nKmx02xoTVO3dTe/9L9CtLYRjF9qjDQMV7bS0bImRH7uN2qbbqd+y31cmFlk5IsjhOfnZug//DI9z7xO046n8BZmmD55CPF9jA0VQ/BvGfivjOh8ZecYEEF8j9qmDtIPvkQ8EeWTgwcYP/UVJtWQltzsDPc+9iJ3dz/B4iJMD3/KuaEPyM9OFQ8YWvI7gQnOJ9X5Kp2LFAhVxkm13EP91p3EE5bRE4Mc7H0YaywmUbdJjLHk5+do73yU7T17SDaswxfwPf05UBYMhCog98cCgx+9xfF3e8FYrC0FAMAYy/yF8ySubmLznQ+x8fptRONr8X0wS6RASsnT+eqdGwOFwkUmzwwy8uWHjP/4NdFYDcZaRIS/AMGY3Iv5Ju0oAAAAAElFTkSuQmCC\',\n    \'field_normal\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADEElEQVR4nO3dTW8bVRSA4ffc+XCcpm6ndoibRCRS0kRQNUgptBJiAQt2/GMWZYNUhISqIKpCm7Ykcuo4HtcOkGQ+PJdF0qq7LFCx6nOe7cjyte57NderI0vrdz2AiDAuC7yHZL5NMt8mjGK895gPlyBUvuJ4cER6eEBZZERx7e2+ytL6XS8iFHlGI2mxdnsbF4Qcv07Jzk4QcRP+CeY/8Z4gimhcbxJFMfu7j3m1t0tcm8F7T/hm829+vM7K5h1ePNmh8/IpRZ7Z6Z8SIoILAlrtZTa37tFIWvzx689EUUw4LksaSYvVzTs8evgD/e4+tZlZ4toMIIBFMC16nT8ZpT3uffMdS6sbdF78Tui9Z+32Ns+f7NB/tU/9ylWqanxx+m3zp0ltpk6eZ+w8fMD2V98y6B3gkvk2QRDSefmUWn2WqhpPep3mPamqiiiuMRr0GaZH3FxZPw9g9DqlyDNEZNJrNO+b9yCQHh1wLZnHhVFMdnZqFz5FRITs9AQXhjjvvZ18hUQEvMf+5CtnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnAShnASjnABsWodCbPXfeV4RRZEMjlAmj6HxgxPGgz7XrTYIgmPSazP9CqKqKpNnm77+GuPSwQxjFNNvL5NkZztm1YFqJCNW4pD47R3Nhke7ec8KyyNnffczm1heM0h55fj5bFrsXTBcRqrKkLAu27n/NsN9lmPaQ5Vuf+yI7Y+Oz+zRufMTOTw8YDfoXn3HY8MjpUFUV9dk5Pt3+kvrcVR79+D3OuXeGRxc5S6sbLK99wig9Iu0dkJ2eIO6yCC4bL2vPJ/nce08YxiStBZoLiwz7XZ799svbV728Oz6+yDPqV+ZYXNmgcaOFc+ElX24+BB7453hId2+XYXp4/oq/8C96VRPSdFRt5AAAAABJRU5ErkJggg==\',\n    \'field_disabled\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACe0lEQVR4nO3dzXLaMBSG4VeysPkrUEgmTbrtHfT+76bNdBoaiAFjbCx14TQ30GmZcL5nCwvNnFce7Y77/OVrAsA5UtcBUIynDEdTfJZB/6u8Vw5SSjTHimNVEmOHzwKkfrCh/5Mjns8UozGLm8+EQU53bomxw+EueXz5S4mEc57xZM4s3VE+/+RQPveXGwjQD386X7G4eeB03FPuNqQYSbr+V8LhnCMvRny8faAYjtk8fcP5jJBiRzGasLh54FD+ojkd8T7Dea+7f2WauqJta+bLe9qmZrdd44HXm797HX649DnlH3Hek2Jkv31itvxEyHN8MZ4yGOTU1Q7vM/Tqu27Oedr2ROzOTGcr/HA0fX3wxUufTf4T5xxtU1OMJnjvg4ZvUIwdznm8Pvm2+UsfQC5LARinAIxTAMYpAOMUgHEKwDgFYJwCME4BGKcAjFMAxikA4xSAcQrAOAVgnAIwTgEYpwCMUwDGKQDjFIBxCsA4BWCcAjBOARinAIxTAMYpAOMUgHEKwDgFYJwCME4BGKcAjFMAxikA4xSAcQrAOAVgnAIwTgEYpwCMUwDGKQDjFIBxCsA4BWCcTynhnPaDWfNn5v5UH8hCrggMSSkxGBT9lri62hFTJC/GpKTdQdcvkWWBMCj6DaKx6yiffzD+sOj3yimCq5VSIsbIdLai2m85HfcEnwUO5YZiOGG+vGf/subc1IBDq0OvROp3CGdZYDK/JcbIdv2IzwIBEj4LbJ6+0zY1s+UdsTvTNjWx60Bvg/ct9cujQ14wGBRU+y3b9ePbXF/3xCac9+xe1hyrkulsRTGaEPLh25pxea8ckGhOR7brR07Hw9vmcIDf5rLckVmhXHEAAAAASUVORK5CYII=\',\n    \'field_focus\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADkUlEQVR4nO3dT28bRRjH8e8zO2vnj51YCZT86wESoKIQKAHUAwguIERBfRfNpYdK3HpAvAFuSFRCgYpzD5woQqJ9ARwKBUqltKUIAk4jQW1obGe983DwJgWJlktVJ57nc7NmtTvS/LS78/NhZXZhSQGQBLq3QAQ3voirLSK+ApoDwp2pje/mcQFCTvjzB/I/LqBZE0nHi3UF3zsoQbMGyfhB0vll/ORhpDR29+uavUNBux3yxndk10/TrX9RhCDgtxffT79B+YmTuOEHyJvX2PrpDKFdB/G9M/wnuX0FG9+d45ojfpR034ukE0sktafYurZCtvo++FFk5uGDmlQfZ+j5U4gfpXX1E1pXPia06nc5sdlrJK0ytP8owweO44am6Fw8Sbb2KV5ESBeWccMPsnn5FH998y6uNIGUav2es7mXNLC5ukLIGlSfe490/hj571/hk/FF/ORh8uaPtK58hCtNgPM7LwlmUAhuZJrO2meU596kPPM6ydRrOFdbREpjbNXPE1rr4FLQ0O/ZmntOQRWC0lk7CwSS2jM4fAWE3gufPfMHnIIkhNYNNORIWsXt3OrF93du5j7RYq17OwT3/1sJM3i211pwfZ2H6TsLQOQsAJGzAETOAhC5fwTA/vqLx+21drb9i5laDxAn6wFMwQIQOQtA5CwAkbMARM56gChZD2AA6wGiZT2AKVgAImcBiJwFIHIWgMhZDxAl6wEMYD1AtKwHMAULQOQsAJGzAETOAhA56wGiZD2AAawHiJb1AKZgAYicBSByFoDIWQAiZz1AlKwHMID1ANGyHsAULACRswBEzgIQOQtA5KwHiNK/eoDih30iJh47ay04tFt8Q2C0r3My94sifgREQLu40LyMdtuk+15C0ioQsMfBgJIENKc09QriPHnzEj6/eYG88T3p5CGG9h9lc3UFNzLd+8CQtYMDQkAc2t7ATz5Lee4Iob1Bvn4Or1mD7PppktqTDB84TsgadH452/tymNgmYTAoaI6fXKLy9Du48gSd1Q/IGxeR2UdfUM1uUnrsBKWFZQgZW7+do/Pr54T2jeK2cYc7gWy/QNr4rh3XgPgRSg+9THnuCK48QVY/T+frt0EEmV1YUsSh3VukM2+Rzh8jqTwCKBoy7H1gAIhDXEJob5D9fIbs6odFeFwRgOIgzZq44VmSqVdJaoeQdMy2h3udCBq6hOYl8vUvyRvfIr5CrwJS/gZD4FOZzHjCswAAAABJRU5ErkJggg==\',\n    \'card\': \'iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAF6klEQVR4nO3ZzW9U5wHF4XPHM7YJYHD4cJCq8qGqkCJ1QUOW7b9fiXaFkiwAkUBSwMEYTCzwjJnbhVPUDVm1gXCeZ3s8M+/m/mbu9bC5dWVMkmGY5PBwniQ5ffZCTp29kOlsLRmXSYa822i32z/UfUjG5TJ7u9vZffJDDhcHma2uZRzHo3lz68o4DEMW84NsbJ7LpetfZnXtWF7t72Uxf51hGI4+4x1v/vYMdrv9w9vHMZOVaY6dOJVhSB7euZ3tB3cyXVtPxjHTYZhkMX+VrYt/zKXPv8j2w3vZefRdDhfzX3hn4LdjyGRlJRufbuXitRvZ2DyXe7f/nulsNdM3h/Oc3DyfS59/kW+/+WdePH2S1bX1zFbX3vepgf+h50//lf0XO7l646/Zf/k8j+5/k+k4Jpevf5nth/ey9/Rx1o8dz3K5fHuPAHwcZqvrOZzPc//rf+Ty9ZvZ3f4+k9PnLmR17Vh2Hn2X2dqxLJfL931O4P9gXC4zna1mf+9ZXv20l89+fzWT02cv5NX+Xg4X86MHfsBHbMwwDHn5/MdsnDmfyXS2lsXB63jgBy2GzA9eZzKdZTKOo29+KHP07/0xk/d9EOD9EQAoJgBQTACgmABAMQGAYgIAxQQAigkAFBMAKCYAUEwAoJgAQDEBgGICAMUEAIoJABQTACgmAFBMAKCYAEAxAYBiAgDFBACKCQAUEwAoJgBQTACgmABAMQGAYgIAxQQAigkAFBMAKCYAUEwAoJgAQDEBgGICAMUEAIoJABQTACgmAFBMAKCYAEAxAYBiAgDFBACKCQAUEwAoJgBQTACgmABAMQGAYgIAxQQAigkAFBMAKCYAUEwAoJgAQDEBgGICAMUEAIoJABQTACgmAFBMAKCYAEAxAYBiAgDFBACKCQAUEwAoJgBQTACgmABAMQGAYgIAxQQAigkAFBMAKCYAUEwAoJgAQDEBgGICAMUEAIoJABQTACgmAFBMAKCYAEAxAYBiAgDFBACKCQAUEwAoJgBQTACgmABAMQGAYgIAxQQAigkAFBMAKCYAUEwAoJgAQDEBgGICAMUEAIoJABQTACgmAFBMAKCYAEAxAYBiAgDFBACKCQAUEwAoJgBQTACgmABAMQGAYgIAxQQAigkAFBMAKCYAUEwAoJgAQDEBgGICAMUEAIoJABQTACgmAFBMAKCYAEAxAYBiAgDFBACKCQAUEwAoJgBQTACgmABAMQGAYgIAxQQAigkAFBMAKCYAUEwAoJgAQDEBgGICAMUEAIoJABQTACgmAFBMAKCYAEAxAYBiAgDFBACKCQAUEwAoJgBQTACgmABAMQGAYgIAxQQAigkAFBMAKCYAUEwAoJgAQDEBgGICAMUEAIoJABQTACgmAFBMAKCYAEAxAYBiAgDFBACKCQAUEwAoJgBQTACgmABAMQGAYgIAxQQAigkAFBMAKCYAUEwAoJgAQDEBgGICAMUEAIoJABQTACgmAFBMAKCYAEAxAYBiAgDFBACKCQAUEwAoJgBQTACgmABAMQGAYgIAxQQAigkAFBMAKCYAUEwAoJgAQDEBgGICAMUEAIoJABQTACgmAFBMAKCYAEAxAYBiAgDFjgIwju/5GMCv6udrfjKOy0ym0yTD+z0Q8KuZTKfJOGayt7udYydOZTJZ8UMACozjMic2zmT/xbNMdp/8kCHJqTNbOVwcZJh4LAAfo2EYsly+yer6Jzm5eTZPHt7N9HBxkId3b+fitRv56cVODhfzTKezJMkYNwbwW/bf1/By+SZvDhe5/Kebefb4QfaePc50trqe7Qd3cnLzXK7+5W+5/9Wt7O/tHr1ocPnDx2Acl1ld/ySXr9/MZLKS+1/dynS2lmFz68o4DEMOF/NcuHQtv/vDn/Nqfy8vd3/MYv46wzDkXY8G/pMHu93+Ye7jOGZlZZrjp8/k5Omz2Xn8IN9+fSvDMCSZHAUgObo/WMwPsn78ZD67eDUbn57Pysos47j85V8C42i32z/U/ee/2X/xLE8e3s3ezuNMV9feTv8GE2KRE15vXH0AAAAASUVORK5CYII=\',\n    \'nav\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAADB0lEQVR4nO3dzU8bRxiA8WfGs2sTf2ATE0CqwIkCqEShl7j//zVKTkkbJYrbFBwEGLBhXTv27jKTg01yqKJeEhH8vr/rWPZI+6x39vSaxtqjAGCMJc9TAOrNDZbvr+PiIiF4DIZvCQRd/4nXAULwJP0zBmdH5OmUKC4SQgDANNYeBWMMWTql1lil9aRNXKowGf9LlqUYY2D+4f8w5uYXdP0nXQ8hUCgUWLpXgeDpvn9N7+N7XFyCEHDGWLJ0wtrmNq29NufHXQ47b8nz7NtfrO4Yg7WW2kqTrb1nVFea/P36OS6Kcdd5SrWxysO9Zxx0/iTpnxPFRaIovu1dq+8oAFcXPUbJJdv7bcbDS44/vMUF4OGTNmfHH0n658SlJYL3X54RanG4qEiepxy8+4OtnX0GvSNsvblBXCpzcXo0Oxx4f9v7VD9ICB7nIkbDSybjMeubO9h6c53JeESeZ7MDn1p4xhiGVwNqKw+wLiqSpVM98Akxf+cnS6dYF2FDCHrnC3Tzem9veyPqdmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAwmkAws0C0GER8syvuQ3BYwsO/mf4oFos1jlCCNhkcMZSuYItWP0jEMAAwXvK1WXGSR876B1B8NQaq1znKcbosWBhGYP3nri0RKVW57TbweXplG7nFa1f24ySAXme4lwEzAcMqTvv5uHuvec6z2jtPqV/ckDSP8VFcYneYYdqY5Xt/d85ePeK0TCZjaXVYVKLIcxmBsbFElu7TzHB8+HNS1xU/Do8Os9SNlq7/PL4Nyafxgyv+mTpVCeK3XGz4dGOcq1OpbbMxckh/7x5Mb+udhYAzMaIZemUUrnK+uYOtZUHFFykI2QXQmB01ee0+xfJxQkuLn5Z+QxpVjyHbs+OcAAAAABJRU5ErkJggg==\',\n    \'status\': \'iVBORw0KGgoAAAANSUhEUgAAAIAAAABACAYAAADS1n9/AAACJ0lEQVR4nO3dwU7bQBCH8W/Wi2MoSQWCciqVyqXv/0SIgoREUWhIiY3tnR6cVDwAEmrm/7smh5Xms7U+jZ1cfHcAMNxHAHKzIDdzLGVg+7P8pwzcGbpnhs0KLz2WDtjNNe/+5GUgz45pTi/JzWcspY87s7w/d8bXF9qnW17XD9uHG/I0/J56/oWjsyssVXgZ8TJ88InlvVX1EZ8uflDNjtk8XmMpk91Hqtmco7MrMMPHAcwA++jzyjtzH8ELzclXSr+hW92TAA5Pv2GpglK2w5f9NM3Wy0BzcknKDSnPFuTDOV5GDT8KL6RcU8/PSflwjlmFbvuRTF8GuVmQdrdBicdSJunJj8zRx35wCiA4BRCcAghOAQSnAIJTAMEpgOAUQHAKIDgFEJwCCE4BBKcAglMAwSmA4BRAcAogOAUQnAIITgEEpwCCUwDBKYDgFEBwCiA4BRCcAghOAQSnAIJTAMEpgOAUQHAKIDgFEJwCCE4BBKcAglMAwSmA4BRAcAogOAUQnAIITgEEpwCCUwDBKYDgEq6FEXE5aWj/4F7QmrhIHMwY2jVp6H5T+g1mCa2PicLwMtKvH0k+DrTL2zfLIhXBXnPHqgO61T1Dt5q2hr2uH2if7rDqAPQm2FPTTC3XDC9L2uXNtDoWHEuZzeM1pd9sN0rW6HK4Z2x67bfLn7TLG3Z3vn9LAy1lutU9/eaJ+vic3Cy0Pn5fuDN0a/r1L4bumbe7Iv8CKVemgl12RfMAAAAASUVORK5CYII=\',\n    \'popup_icon\': \'iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAACIklEQVR4nJWSTWsTURiFz7n3TibJJE3SVmxFQYstqBulapGKoC7EH6D/wZ0rceFCf4JQVyKu3Alil4LUnaaSjWLTLywVpGKmH5NmMpPMzH1d1ErpzrN/eM97ziEOSERIUj4t+wO16tDVdquFjKDWWrQ2oNLphbHSOwDgQegxwJsrG0NFFN7mcu75OI4sAQUAAtiCV3TiqPu8Mz54n/vQCpD7+QGZO+LfLrrubBh1Thp6nYInNgDg9NLMUN+gyBvlsGYAgKQA6AFAvbmz0U+ScPrcsXUcUn2xtUswFKvEAMCX9Z2a0HmQxD3HZunpYtHz6k1/plQu9+Pd9qvJM0caIsLG6paRTBQAcG5tLV/ql98XCt6JqBtugswItEVQdVw3l2XJCG12bXV8aOnU8tYtiLymo0ZNFdV8IumVsBNMT50d+XjY3vyibwV69C65UP/2u0OthABMZkUAdo3jVERENQA9CVgA8vVHUOlFaay0TH1e8JXJ56eSJHaA7b2oCSgRsSTt9z3IkrRBEABkrKieQHHWMfohqe9Njo219zsSpajnREwJMA3AzIkYXa1QIF6/l9ypDA8ebW3+On5povaCpBitSAuYKOr518kUQHrgxa35JR8guxPDbP/tXJG0ZifspyXHbA9Uqo/mm61VKqVkz4QYx3EpzGXoByJCAIpk9m9y9WbrYsErPe1FXVdECBIEbNErM+y2n12eGH65f+lw6v+tP8xkBANpN+2TAAAAAElFTkSuQmCC\',\n}\n')

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
        self.events = queue.Queue()
        self.busy = False
        self.card_modifier_pending = False
        self.card_modifier_signature = None
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
        self.logo_image = self.app_icons[48]

        window.title("지후니우스")
        window.geometry("1120x900")
        window.minsize(1000, 820)
        window.protocol("WM_DELETE_WINDOW", self.close)
        frame = ttk.Frame(window, padding=24)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        outer_frame = frame
        frame.rowconfigure(1, weight=1)

        header = ttk.Frame(frame)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)
        title_row = ttk.Frame(header)
        title_row.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.logo_label = ttk.Label(title_row, image=self.logo_image)
        self.logo_label.pack(side="left", padx=(0, 12))
        self.title_label = ttk.Label(title_row, text="지후니우스", style="Title.TLabel")
        self.title_label.pack(side="left")
        ttk.Separator(title_row, orient="vertical").pack(side="left", fill="y", padx=20, pady=10)
        self._suite_buttons = {}
        for key, label in (("protrusion", "돌출량"), ("wash-log", "세척일보")):
            button = ttk.Button(title_row, text=label, style="Popup.TButton",
                                command=lambda selected=key: self.open_companion(selected))
            button.pack(side="left", padx=(0, 10))
            self._suite_buttons[key] = button

        navigation_row = ttk.Frame(header)
        navigation_row.grid(row=1, column=0, sticky="ew")
        navigation_row.columnconfigure(1, weight=1, minsize=170)
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
        self.header_status_label = ttk.Label(navigation_row, textvariable=self.status,
                                             style="Status.TLabel", wraplength=220, justify="center")
        self.header_status_label.grid(row=0, column=2, sticky="e")
        for widget in (navigation_row, tabs, self.header_status_label, self.handover_toggle):
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

        modes = ttk.Frame(frame, style="Card.TFrame", padding=18)
        modes.grid(row=1, column=0, sticky="ew", pady=(0, 16))
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
        list_options.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(12, 0))
        list_options.columnconfigure(7, weight=1)
        ttk.Label(list_options, text="리스트 파일명", style="Caption.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 14))
        self.list_number = tk.StringVar(value=DEFAULT_LIST_NUMBER)
        self.list_buttons = []
        for column, number in enumerate(LIST_NUMBERS, 1):
            button = ttk.Radiobutton(list_options, text="O" + number, variable=self.list_number, value=number,
                                     command=self.update_mode, style="Mode.TRadiobutton", width=7)
            button.grid(row=0, column=column, padx=(0, 8))
            self.list_buttons.append(button)
        ttk.Label(list_options, text="연도", style="Caption.TLabel").grid(
            row=0, column=3, sticky="w", padx=(18, 10))
        self.year_value = tk.StringVar(value=str(PROGRAM_YEAR))
        self.year_input = ttk.Entry(list_options, textvariable=self.year_value, width=6, font=("Consolas", 14))
        self.year_input.grid(row=0, column=4, sticky="w")
        ttk.Label(list_options, text="날짜 폴더", style="Caption.TLabel").grid(
            row=0, column=5, sticky="w", padx=(18, 10))
        self.folder_input = ttk.Entry(list_options, width=8, font=("Consolas", 14))
        self.folder_input.grid(row=0, column=6, sticky="w")
        self.mode_help = tk.StringVar()

        body = ttk.Frame(frame)
        self.cnc_body = body
        body.grid(row=2, column=0, sticky="nsew", pady=(0, 16))
        body.columnconfigure(0, weight=0, minsize=0)
        body.columnconfigure(1, weight=1, minsize=250)
        body.columnconfigure(2, weight=1, minsize=250)
        body.columnconfigure(3, weight=3, minsize=350)
        body.rowconfigure(0, weight=1)
        drive_card = ttk.Frame(body, style="Card.TFrame", padding=18)
        drive_card.grid(row=0, column=1, sticky="nsew", padx=(0, 14))
        drive_card.columnconfigure(0, weight=1)
        drive_card.rowconfigure(2, weight=1)
        drive_header = ttk.Frame(drive_card, style="Card.TFrame", borderwidth=0)
        drive_header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        drive_header.columnconfigure(0, weight=1, uniform="drive_tools")
        drive_header.columnconfigure(1, weight=1, uniform="drive_tools")
        ttk.Label(drive_header, text="드라이브 정리", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        self.drive_add_button = ttk.Button(drive_header, text="추가", width=0, style="DriveSmall.TButton",
                                            command=self.choose_drive_files)
        self.drive_add_button.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=(8, 0))
        self.drive_refresh_button = ttk.Button(drive_header, text="새로고침", width=0, style="DriveSmall.TButton",
                                                command=self.refresh_drive_manual)
        self.drive_refresh_button.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=(8, 0))
        self.drive_contents_status = tk.StringVar(value="드라이브 연결 대기")
        ttk.Label(drive_card, textvariable=self.drive_contents_status, style="Caption.TLabel", wraplength=210).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self.drive_contents = tk.Listbox(drive_card, width=20, height=14, font=("맑은 고딕", 9),
                                         background="#131c2b", foreground="#e7edf7", relief="flat",
                                         borderwidth=0, highlightthickness=1, highlightbackground="#36455e",
                                         highlightcolor="#2563eb", selectbackground="#284a79",
                                         selectforeground="#e7edf7", exportselection=False, selectmode="extended")
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
        self.drive_menu = tk.Menu(window, tearoff=False, background="#1b2433", foreground="#ffffff",
                                  activebackground="#2563eb", activeforeground="#ffffff",
                                  disabledforeground="#75849c", font=("맑은 고딕", 10))
        self.drive_menu.add_command(label="이름 변경", accelerator="F2", command=self.start_rename)
        self.drive_menu.add_command(label="선택 파일 삭제", accelerator="Delete", command=self.start_drive_delete)
        self.drive_menu.add_separator()
        self.drive_menu.add_command(label="파일 추가…", command=self.choose_drive_files)
        self.drive_menu.add_command(label="새로고침", accelerator="F5", command=self.refresh_drive_manual)
        self.drive_item_paths = []
        self.drive_contents_signature = None
        self.drive_hint = tk.StringVar(value="파일을 끌어놓아 추가 · Delete: 삭제\n더블클릭: 열기 · F2: 이름 변경\n수정10.30 자동 추가 · 비우기 시 보존")
        drive_actions = ttk.Frame(drive_card, style="Card.TFrame", borderwidth=0)
        drive_actions.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        drive_actions.columnconfigure(0, weight=1)
        self.empty_button = ttk.Button(drive_actions, text="드라이브 비우기", command=self.start_empty,
                                       style="Danger.TButton")
        self.empty_button.grid(row=0, column=0, sticky="ew")
        self.drive_delete_button = ttk.Button(drive_actions, text="삭제", width=4, command=self.start_drive_delete,
                                               style="Danger.TButton")
        self.drive_delete_button.grid(row=0, column=1, padx=(6, 0), sticky="ns")

        inputs = ttk.Frame(body, style="Card.TFrame", padding=18)
        inputs.grid(row=0, column=2, sticky="nsew", padx=(0, 14))
        inputs.columnconfigure(0, weight=1)
        inputs.rowconfigure(1, weight=1)
        ttk.Label(inputs, text="프로그램 번호", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        self.number_input = tk.Text(inputs, width=12, height=12, font=("Consolas", 14), wrap="word", undo=True,
                                    background="#131c2b", foreground="#e7edf7", insertbackground="#2563eb",
                                    selectbackground="#284a79", selectforeground="#e7edf7", relief="flat",
                                    highlightthickness=1, highlightbackground="#36455e", highlightcolor="#2563eb",
                                    padx=12, pady=10)
        self.number_input.grid(row=1, column=0, sticky="nsew")
        number_scrollbar = ttk.Scrollbar(inputs, orient="vertical", command=self.number_input.yview)
        number_scrollbar.grid(row=1, column=1, sticky="ns")
        self.number_input.configure(yscrollcommand=number_scrollbar.set)
        self.number_input.bind("<Control-Return>", self.import_shortcut)
        self.folder_input.bind("<Control-Return>", self.import_shortcut)
        self.year_input.bind("<Control-Return>", self.import_shortcut)

        actions = ttk.Frame(inputs, style="Card.TFrame", borderwidth=0)
        actions.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self.import_button = ttk.Button(actions, text=MODE_LABELS[MODE_BOTH], command=self.start_import,
                                        style="Accent.TButton")
        self.import_button.pack(fill="x")

        details = ttk.Frame(frame, style="Card.TFrame", padding=18)
        details.grid(row=3, column=0, sticky="ew")
        details.columnconfigure(0, weight=0)
        details.columnconfigure(1, weight=1)
        self.search_root_text = tk.StringVar(value=str(year_search_root(PROGRAM_YEAR)))
        self.year_value.trace_add("write", self.update_year_display)
        self.destination_text = tk.StringVar(value="F:\\ / G:\\ 연결 대기")
        self.build_machine_monitor(details).grid(row=0, column=0, sticky="w")
        alert_controls = ttk.Frame(details, style="Card.TFrame", borderwidth=0)
        alert_controls.grid(row=0, column=1, sticky="w", padx=(32, 0))
        self.machine_alert_toggle = tk.Canvas(alert_controls, width=174, height=48, background="#1b2433",
                                             highlightthickness=1, highlightbackground="#1b2433",
                                             highlightcolor="#85b4ff", borderwidth=0, takefocus=True, cursor="hand2")
        self.machine_alert_toggle.pack(side="left", padx=(0, 16))
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
        self.machine_alert_settings_button.pack(side="left")
        self.update_machine_alert_toggle()

        log_card = ttk.Frame(body, style="Card.TFrame", padding=18)
        self.log_card = log_card
        log_card.grid(row=0, column=3, sticky="nsew")
        log_card.columnconfigure(0, weight=1)
        log_card.rowconfigure(1, weight=1)
        ttk.Label(log_card, text="작업 기록 · 최근 100줄", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.log = tk.Text(log_card, width=30, height=22, font=("맑은 고딕", 9), wrap="word", state="disabled",
                           background="#131c2b", foreground="#a0aec3", relief="flat", borderwidth=0,
                           highlightthickness=0, padx=12, pady=10)
        self.log.grid(row=1, column=0, sticky="nsew")
        log_scrollbar = ttk.Scrollbar(log_card, orient="vertical", command=self.log.yview)
        log_scrollbar.grid(row=1, column=1, sticky="ns")
        self.log.configure(yscrollcommand=log_scrollbar.set)
        self.handover_card = self.build_handover_panel(common_body)
        self.handover_card.grid_remove()
        self.append_log("작업 모드를 선택하고 번호를 입력한 뒤 실행하세요. Ctrl+Enter도 가능합니다.\n"
                        "파일을 가져오는 모드에서는 연도와 날짜 폴더를 지정합니다.\n"
                        "날짜에 맞는 월 폴더를 자동 선택합니다. (예: 10.13 → 10월/10.13)\n"
                        "지정한 날짜 폴더와 그 안의 하위폴더만 검색하고, 원본 파일과 폴더는 유지합니다.\n"
                        "F 드라이브를 우선 사용하며, F가 없으면 G 드라이브에 저장합니다.\n"
                        "저장 드라이브는 '드라이브 비우기' 버튼을 눌렀을 때만 비웁니다.\n")
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
        self.minimum_height = max(820, minimum_height)
        window.minsize(1000, self.minimum_height)
        window.geometry("1120x{}".format(max(900, minimum_height)))
        self.stl_app = load_stl_finder().App(window, self.app_pages["stl"])
        self.wash_app = WashApp(self, self.app_pages["wash"])
        visual = SuiteVisualTheme.install_visual_theme(window, self.style)
        for button in self._suite_buttons.values():
            button.configure(image=visual["popup_icon"], compound="right")
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
        window.update_idletasks()
        body_minimum = max(drive_card.winfo_reqheight(), inputs.winfo_reqheight(), log_card.winfo_reqheight())
        body.rowconfigure(0, minsize=body_minimum)
        frame.rowconfigure(2, minsize=body_minimum)
        self.minimum_height = max(820, outer_frame.winfo_reqheight())
        window.minsize(1000, self.minimum_height)
        window.geometry("1120x{}".format(max(900, self.minimum_height)))
        # Wrapped status text can make the header taller. Keep all body controls
        # visible without shrinking a window the user has already enlarged.
        layout_pending = [None]
        def sync_visual_height():
            layout_pending[0] = None
            if not window.winfo_exists():
                return
            required = max(820, outer_frame.winfo_reqheight())
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

    def update_machine_alert_toggle(self):
        canvas = self.machine_alert_toggle
        enabled = self.machine_alert_enabled
        canvas.delete('all')
        canvas.create_text(4, 14, text='머신 알림', anchor='w', fill='#e7edf7', font=('맑은 고딕', 10, 'bold'))
        canvas.create_text(4, 34, text='{}대 선택'.format(len(self.machine_alert_selected)), anchor='w',
                           fill='#93a3bc', font=('맑은 고딕', 9))
        canvas.create_image(81, 8, anchor='nw', image=self.machine_alert_switch_images[enabled])
        canvas.create_text(112 if enabled else 137, 24, text='ON' if enabled else 'OFF',
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
        dialog.configure(background='#111722'); dialog.resizable(False, False)
        frame = self.ttk.Frame(dialog, padding=22); frame.pack(fill='both', expand=True)
        self.ttk.Label(frame, text='알림 받을 호기', style='Subtitle.TLabel').pack(anchor='w')
        self.ttk.Label(frame, text='초록 → 빨강·노랑·회색일 때 호기 완료 알림\n프로그램번호 변경·초록 복귀 시 알림 없음',
                       justify='left').pack(anchor='w', pady=(8, 16))
        enabled = self.tk.BooleanVar(value=self.machine_alert_enabled)
        sound = self.tk.BooleanVar(value=self.machine_alert_sound)
        self.machine_alert_sound_var = sound
        self.tk.Checkbutton(frame, text='머신 알림 켜기', variable=enabled, background='#111722',
                            foreground='#e7edf7', selectcolor='#203047', activebackground='#111722',
                            activeforeground='#ffffff', font=('맑은 고딕', 10)).pack(anchor='w', pady=(0, 10))
        self.tk.Checkbutton(frame, text='알림 소리 켜기', variable=sound, background='#111722',
                            foreground='#e7edf7', selectcolor='#203047', activebackground='#111722',
                            activeforeground='#ffffff', font=('맑은 고딕', 10)).pack(anchor='w', pady=(0, 10))
        sound_kind = self.tk.StringVar(value=self.machine_alert_sound_kind)
        sound_choices = self.ttk.Frame(frame); sound_choices.pack(fill='x', pady=(0, 10))
        for label, value in (('기본 시스템 소리', 'system'), ('톡 소리', 'tap')):
            self.tk.Radiobutton(sound_choices, text=label, value=value, variable=sound_kind,
                                background='#111722', foreground='#e7edf7', selectcolor='#203047',
                                activebackground='#111722', activeforeground='#ffffff',
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
                self.tk.Checkbutton(grid, text='{}호기'.format(number), variable=var, background='#111722',
                                    foreground='#e7edf7', selectcolor='#203047', activebackground='#111722',
                                    activeforeground='#ffffff', font=('맑은 고딕', 11), padx=14, pady=9
                                    ).grid(row=row, column=column, sticky='w')
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

    def build_machine_monitor(self, parent):
        """PRM 번호와 상태를 둥근 카드의 배경색으로 표시하는 두 줄 패널."""
        panel = self.ttk.Frame(parent, style="Card.TFrame", borderwidth=0)
        self.machine_tiles = {}
        self.current_machines = {}
        self.machine_detail_dialog = None
        for row, machines in enumerate(((1, 3, 5, 7), (2, 4, 6, 8, 9))):
            for column, machine in enumerate(machines):
                tile = self.tk.Canvas(panel, width=72, height=44, background="#1b2433",
                                      highlightthickness=0, borderwidth=0,
                                      takefocus=True, cursor="hand2")
                tile.grid(row=row, column=column, padx=(0, 6 if column < 4 else 0),
                          pady=(0, 6 if row == 0 else 0))
                light = tile.create_polygon(11, 1, 61, 1, 71, 1, 71, 11,
                                            71, 33, 71, 43, 61, 43, 11, 43,
                                            1, 43, 1, 33, 1, 11, 1, 1,
                                            smooth=True, splinesteps=24, fill="#344156", outline="")
                tile.create_text(36, 13, text="머신{}".format(machine), tags=('machine_title',),
                                 fill="#ffffff", font=("맑은 고딕", 9))
                number = tile.create_text(36, 32, text="—", fill="#d3dce9", font=("Consolas", 11, "bold"))
                self.machine_tiles[machine] = (tile, light, number)
                tile.bind("<Button-1>", lambda event, n=machine: self.show_machine_details(n))
                tile.bind("<Return>", lambda event, n=machine: self.show_machine_details(n))
                tile.bind("<space>", lambda event, n=machine: self.show_machine_details(n))
        self.machine_panel = panel
        return panel

    def apply_machine_status(self, machines, online=True):
        """읽기 결과는 GUI 스레드에서 반영. 알 수 없는 상태는 회색으로 표시합니다."""
        colors = {"green": "#246b48", "red": "#963e49", "yellow": "#a88830"}
        self.current_machines = dict(machines) if online else {}
        fresh = {n:r for n,r in self.current_machines.items() if not r.get('_stale')}
        for event in self.machine_alert_tracker.observe(fresh, self.machine_alert_enabled, self.machine_alert_selected):
            self.queue_machine_alert(event)
        for machine, (tile, light, number) in self.machine_tiles.items():
            record = machines.get(machine, {}) if online else {}
            color = colors.get(record.get("light"), "#344156")
            uncertain = not record or record.get('_stale', False)
            tile.itemconfigure('machine_title', text='머신{}{}'.format(machine, ' ?' if uncertain else ''))
            value = str(record.get("prm_no", ""))
            # 사이트 PRM NO. 뒤의 숫자를 그대로 사용하고 앞자리 0도 유지합니다.
            if not re.fullmatch(r"[0-9]+", value):
                value = "—"
            tile.itemconfigure(light, fill=color)
            tile.itemconfigure(number, text=value, fill="#ffffff" if value != "—" else "#d3dce9")
        self.refresh_machine_details()

    def position_handover_button(self):
        if not self.handover_toggle.winfo_exists():
            return
        header = self.handover_toggle.master
        last_tab = self.tab_buttons['wash']
        left = last_tab.winfo_rootx() + last_tab.winfo_width() - header.winfo_rootx()
        right = self.header_status_label.winfo_rootx() - header.winfo_rootx()
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
        dialog.transient(self.window);dialog.configure(background="#111824")
        dialog.geometry("460x530");dialog.minsize(400, 510)
        frame = self.ttk.Frame(dialog, padding=20);frame.pack(fill="both", expand=True)
        self.machine_detail_title = self.tk.StringVar()
        self.ttk.Label(frame, textvariable=self.machine_detail_title, style="Title.TLabel").pack(anchor="w")
        self.machine_detail_status = self.tk.StringVar()
        self.machine_detail_status_label = self.tk.Label(frame, textvariable=self.machine_detail_status,
                                                         background="#344156", foreground="#ffffff",
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
        self.machine_detail_status_label.configure(background={"RUN": "#246b48", "ALARM": "#963e49", "WAIT": "#a88830", "HOLD": "#a88830"}.get(state, "#344156"))
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
        dialog.configure(background="#111722")
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
                               background="#131c2b", foreground="#e7edf7", insertbackground="#ffffff",
                               selectbackground="#284a79", relief="flat", padx=12, pady=12,
                               highlightthickness=1, highlightbackground="#536781", highlightcolor="#85b4ff")
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
            self.search_root_text.set(str(year_search_root(self.year_value.get())))
        except WorkError:
            self.search_root_text.set("연도 4자리를 입력해 주세요.")

    def update_mode(self):
        mode = self.mode.get()
        self.folder_input.configure(state="disabled" if self.busy or mode == MODE_LIST else "normal")
        self.year_input.configure(state="disabled" if self.busy or mode == MODE_LIST else "normal")
        self.import_button.configure(text=MODE_LABELS[mode])
        for button in self.list_buttons:
            button.configure(state="disabled" if self.busy or mode == MODE_FILES else "normal")
        self.mode_help.set(MODE_DESCRIPTIONS[mode].format(list_name=selected_list_name(self.list_number.get())))

    def refresh_destination(self):
        try:
            self.destination = select_destination()
        except (WorkError, OSError):
            self.destination = None
        if self.destination is None:
            self.destination_text.set("F:\\ / G:\\ 연결 대기")
            self.empty_button.configure(text="드라이브 비우기")
        else:
            self.destination_text.set(str(self.destination))
            self.empty_button.configure(text="{} 드라이브 비우기".format(self.destination.drive or self.destination))
        if self.destination is None:
            self.card_modifier_signature = None
        self.refresh_drive_contents()
        self.queue_card_modifier_check()

    def queue_card_modifier_check(self):
        # 연결/새로고침 직후의 사용자 작업을 먼저 시작하게 합니다.
        if self.card_modifier_pending:
            return
        self.card_modifier_pending = True
        self.window.after_idle(self.check_card_modifier)

    def check_card_modifier(self):
        self.card_modifier_pending = False
        washing = getattr(self, "wash_app", None)
        if self.busy or (washing is not None and washing.busy):
            return
        destination = self.destination
        if destination is None:
            self.card_modifier_signature = None
            return
        try:
            # 파일 내용은 읽지 않습니다. 변동된 카드/스크립트만 별도 스레드에서 처리합니다.
            signature = card_modifier_signature(destination)
        except (WorkError, OSError) as error:
            signature = (str(destination), "read-error", str(error))
            if signature != self.card_modifier_signature:
                self.card_modifier_signature = signature
                self.append_log("수정10.30 확인 보류: {}\n".format(error))
            return
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
        destination = self.destination
        labels = []
        paths = []
        if destination is None:
            status = "드라이브 연결 대기"
        else:
            try:
                with os.scandir(destination) as entries:
                    items = [(entry.name, entry.is_dir(follow_symlinks=False), entry.is_symlink())
                             for entry in entries]
                items.sort(key=lambda item: (not item[1], item[0].casefold()))
                labels = [("[링크] " if link else "[폴더] " if folder else "") + name
                          for name, folder, link in items]
                paths = [destination / name for name, _, _ in items]
                folder_count = sum(folder for _, folder, _ in items)
                status = "파일 {}개 · 폴더 {}개".format(len(items) - folder_count, folder_count) if items else "비어 있음"
                drive_label = destination.drive + "\\" if destination.drive else str(destination)
                status = "{} 연결됨 · {}".format(drive_label, status)
            except OSError:
                status = "목록을 읽지 못했습니다"
        signature = (str(destination), tuple(labels), status)
        if signature != self.drive_contents_signature:
            selected = {self.drive_item_paths[index] for index in self.drive_contents.curselection()
                        if 0 <= index < len(self.drive_item_paths)}
            scroll = self.drive_contents.yview()[0]
            self.drive_contents.delete(0, "end")
            if labels:
                self.drive_contents.insert("end", *labels)
                for index, path in enumerate(paths):
                    if path in selected:
                        self.drive_contents.selection_set(index)
                self.drive_contents.yview_moveto(scroll)
            self.drive_contents_status.set(status)
            self.drive_item_paths = paths
            self.drive_contents_signature = signature

    def refresh_drive_manual(self, event=None):
        if event is not None and getattr(event, "widget", None) is getattr(self, "handover_tree", None):
            return "break"
        if not self.busy:
            self.card_modifier_signature = None
            self.refresh_destination()
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
        if self.busy or was_busy:
            self.messagebox.showinfo("작업 중", "진행 중인 작업이 끝난 뒤 파일을 다시 끌어놓아 주세요.", parent=self.window)
            return
        if destination is None:
            self.messagebox.showerror("파일 추가", "드래그할 때 연결된 드라이브가 없습니다. 연결 후 다시 시도해 주세요.", parent=self.window)
            return
        self.start_drive_add(paths, destination)

    def start_drive_delete(self, event=None):
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
        dialog.configure(background="#111722")
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
        self.busy = value
        state = "disabled" if value else "normal"
        self.update_handover_controls()
        for button in (self.import_button, self.empty_button):
            button.configure(state=state)
        for name in ("drive_add_button", "drive_refresh_button", "drive_delete_button"):
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
                roots = date_search_folders(self.folder_input.get(), selected_year)
            except WorkError as error:
                self.messagebox.showerror("날짜 폴더 확인", str(error), parent=self.window)
                return
        if self.destination is None:
            self.refresh_destination()
        destination = self.destination
        if destination is None:
            self.messagebox.showerror("저장 드라이브 확인", "F:\\ 또는 G:\\에 이동식 드라이브를 연결해 주세요.",
                                      parent=self.window)
            return
        chooser = lambda number, paths: self.request_ui(self.choose_candidate, number, paths)
        self.start_job(MODE_LABELS[mode], lambda: run_batch(
            roots, destination, numbers, chooser=chooser, popup=False, mode=mode, list_number=list_number))

    def import_shortcut(self, event):
        self.start_import()
        return "break"

    def start_empty(self):
        # 번호 처리 함수와 연결하지 않는 별도의 버튼 동작입니다.
        if self.busy:
            return
        if self.destination is None:
            self.refresh_destination()
        destination = self.destination
        if destination is None:
            self.messagebox.showerror("저장 드라이브 확인", "F:\\ 또는 G:\\에 이동식 드라이브를 연결해 주세요.",
                                      parent=self.window)
            return
        self.start_job("드라이브 비우기", lambda: empty_fixed_drive(destination))

    def choose_candidate(self, number, paths):
        dialog = self.tk.Toplevel(self.window)
        dialog.title("O{} 파일 선택".format(number))
        dialog.configure(background="#111722")
        dialog.transient(self.window)
        dialog.grab_set()
        frame = self.ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        self.ttk.Label(frame, text="같은 번호가 여러 곳에 있습니다. 가져올 파일을 선택하세요.",
                       font=("맑은 고딕", 11, "bold")).pack(anchor="w", pady=(0, 12))
        listing = self.tk.Listbox(frame, width=110, height=min(12, len(paths)), exportselection=False,
                                  font=("맑은 고딕", 10), background="#131c2b", foreground="#e7edf7",
                                  selectbackground="#2563eb", selectforeground="#ffffff", relief="flat",
                                  highlightthickness=1, highlightbackground="#536781", highlightcolor="#85b4ff")
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
                    if error:self.append_log('가공현황 연결 오류: '+error+'\n')
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

    def open_companion(self, key):
        if defer_ime_commit(self.window, lambda: self.open_companion(key)): return
        self._suite_exit_pending = False
        try:
            self._suite_children.open(key)
        except Exception as error:
            self.restore_from_tray()
            self.messagebox.showerror('프로그램 열기', str(error), parent=self.window)

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
        for key, button in self._suite_buttons.items():
            opened = key in running
            if self._suite_states.get(key) != opened:
                button.configure(style='Open.Popup.TButton' if opened else 'Popup.TButton')
                self._suite_states[key] = opened
        self._suite_timer = self.window.after(200, self.poll_suite)

    def close(self):
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
        dialog.configure(background='#111722')
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
        self._suite_exit_deadline = time.monotonic() + 2.0
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




SUITE_APP_VERSION = '2026.11.03.7'
SUITE_UPDATE_PROTOCOL = 1
SuiteUpdater = _suite_load_support("jihunius_inapp_update", '"""Public GitHub update transport and local Python version selection. Python 3.8+."""\nimport ctypes\nfrom datetime import date\nimport hashlib\nimport json\nimport os\nfrom pathlib import Path\nimport queue\nimport re\nimport shutil\nimport subprocess\nimport sys\nimport tempfile\nimport threading\nimport time\nimport urllib.error\nimport urllib.parse\nimport urllib.request\nimport uuid\n\nOWNER = \'corsk970119-ux\'\nREPO = \'jihunius-updates\'\nCHANNEL = \'channels/stable.json\'\nMAX_PAYLOAD = 8 * 1024 * 1024\nMAX_MANIFEST = 128 * 1024\nSHA = re.compile(r\'[0-9a-f]{64}\')\n\nclass UpdateError(Exception):\n    pass\n\ndef version(value):\n    if not isinstance(value,str) or not re.fullmatch(r\'\\d{4}\\.\\d{1,2}\\.\\d{1,2}\\.[1-9]\\d{0,5}\',value):\n        raise UpdateError(\'배포 버전 형식을 확인해 주세요.\')\n    parts=tuple(int(x) for x in value.split(\'.\'))\n    try:date(*parts[:3])\n    except ValueError:raise UpdateError(\'배포 날짜가 올바르지 않습니다.\') from None\n    return parts\n\ndef descriptor(value, require_protocol=True):\n    if not isinstance(value,dict):raise UpdateError(\'배포 정보가 올바르지 않습니다.\')\n    v=value.get(\'version\');version(v)\n    if not SHA.fullmatch(str(value.get(\'sha256\',\'\'))):raise UpdateError(\'배포 검증 값이 올바르지 않습니다.\')\n    size=value.get(\'size\')\n    if type(size) is not int or not 0 < size <= MAX_PAYLOAD:raise UpdateError(\'배포 파일 크기를 확인해 주세요.\')\n    if value.get(\'path\')!=\'releases/jihunius/{}/app.pyw\'.format(v):raise UpdateError(\'지후니우스 배포 경로가 아닙니다.\')\n    minimum=value.get(\'min_python\',[3,8])\n    if not isinstance(minimum,list) or len(minimum)!=2 or any(type(x) is not int or not 0<=x<100 for x in minimum):\n        raise UpdateError(\'실행 환경 정보가 올바르지 않습니다.\')\n    if tuple(sys.version_info[:2])<tuple(minimum):raise UpdateError(\'이 버전은 더 새로운 Python이 필요합니다.\')\n    if require_protocol and value.get(\'update_protocol\')!=1:raise UpdateError(\'현재 실행기에서 지원하지 않는 배포입니다.\')\n    result={k:value[k] for k in (\'version\',\'path\',\'sha256\',\'size\')}\n    result.update(min_python=minimum,update_protocol=value.get(\'update_protocol\',0),notes=str(value.get(\'notes\',\'\'))[:10000])\n    return result\n\ndef verify(data, value):\n    if len(data)!=value[\'size\'] or hashlib.sha256(data).hexdigest()!=value[\'sha256\']:\n        raise UpdateError(\'받은 파일의 크기 또는 검증 값이 맞지 않습니다. 기존 버전을 유지합니다.\')\n    try:compile(data,\'지후니우스.pyw\',\'exec\')\n    except (SyntaxError,ValueError,TypeError):raise UpdateError(\'받은 파일의 Python 문법을 확인하지 못했습니다.\') from None\n\ndef atomic(path, data):\n    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)\n    fd,name=tempfile.mkstemp(prefix=\'.update-\',suffix=\'.tmp\',dir=str(path.parent))\n    try:\n        with os.fdopen(fd,\'wb\') as f:f.write(data);f.flush();os.fsync(f.fileno())\n        os.replace(name,str(path))\n    finally:\n        try:os.unlink(name)\n        except FileNotFoundError:pass\n\ndef read_json(path):\n    try:\n        p=Path(path)\n        if p.stat().st_size>MAX_MANIFEST:return {}\n        value=json.loads(p.read_text(encoding=\'utf-8\'))\n        return value if isinstance(value,dict) else {}\n    except (OSError,ValueError):return {}\n\ndef write_json(path,value):\n    atomic(path,json.dumps(value,ensure_ascii=False,indent=2).encode(\'utf-8\'))\n\nclass FileLock:\n    def __init__(self,path):self.path=Path(path);self.stream=None\n    def acquire(self):\n        self.path.parent.mkdir(parents=True,exist_ok=True)\n        self.stream=self.path.open(\'a+b\');self.stream.seek(0,2)\n        if not self.stream.tell():self.stream.write(b\'0\');self.stream.flush()\n        self.stream.seek(0)\n        try:\n            if os.name==\'nt\':\n                import msvcrt\n                msvcrt.locking(self.stream.fileno(),msvcrt.LK_NBLCK,1)\n            else:\n                import fcntl\n                fcntl.flock(self.stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)\n            return True\n        except OSError:self.stream.close();self.stream=None;return False\n    def release(self):\n        if self.stream is None:return\n        try:\n            self.stream.seek(0)\n            if os.name==\'nt\':\n                import msvcrt\n                msvcrt.locking(self.stream.fileno(),msvcrt.LK_UNLCK,1)\n            else:\n                import fcntl\n                fcntl.flock(self.stream.fileno(),fcntl.LOCK_UN)\n        finally:self.stream.close();self.stream=None\n\nclass NoRedirect(urllib.request.HTTPRedirectHandler):\n    def redirect_request(self,*args,**kwargs):raise UpdateError(\'배포 응답 경로가 달라 확인을 보류했습니다.\')\n\ndef public_fetch(path,maximum,seconds):\n    if not isinstance(path,str) or \'\\\\\' in path or any(x in (\'\',\'..\',\'.\') for x in path.split(\'/\')):\n        raise UpdateError(\'잘못된 배포 경로입니다.\')\n    # Public raw content avoids per-PC authentication and API rate limits.\n    url=\'https://raw.githubusercontent.com/{}/{}/main/{}\'.format(OWNER,REPO,urllib.parse.quote(path,safe=\'/\'))\n    def read():\n        request=urllib.request.Request(url,headers={\'User-Agent\':\'Jihunius-Updater/1\',\'Cache-Control\':\'no-cache\'})\n        with urllib.request.build_opener(NoRedirect()).open(request,timeout=seconds) as response:\n            if response.geturl()!=url:raise UpdateError(\'예상하지 못한 배포 응답입니다.\')\n            data=response.read(maximum+1)\n            if len(data)>maximum:raise UpdateError(\'배포 파일이 허용 크기를 초과했습니다.\')\n            return data\n    # Limit total wall time as well as socket read time. At most one fetch is in flight per UI.\n    result=queue.Queue(maxsize=1)\n    def worker():\n        try:result.put((True,read()))\n        except Exception as exc:result.put((False,exc))\n    threading.Thread(target=worker,daemon=True).start()\n    try:ok,value=result.get(timeout=seconds)\n    except queue.Empty:raise UpdateError(\'업데이트 확인 시간이 초과됐습니다. 현재 버전은 계속 사용할 수 있습니다.\') from None\n    if not ok:\n        if isinstance(value,UpdateError):raise value\n        if isinstance(value,urllib.error.HTTPError) and value.code==404:\n            raise UpdateError(\'공개 배포 정보를 아직 찾을 수 없습니다. 현재 버전은 계속 사용할 수 있습니다.\') from None\n        raise UpdateError(\'GitHub에 연결하지 못했습니다. 현재 버전은 계속 사용할 수 있습니다.\') from None\n    return value\n\ndef check_offer(current,fetch=public_fetch,rejected_sha=None):\n    try:manifest=json.loads(fetch(CHANNEL,MAX_MANIFEST,12).decode(\'utf-8-sig\'))\n    except (ValueError,UnicodeError):raise UpdateError(\'배포 목록을 읽지 못했습니다.\') from None\n    if not isinstance(manifest,dict) or manifest.get(\'schema\')!=1 or not isinstance(manifest.get(\'apps\'),dict):\n        raise UpdateError(\'배포 목록 형식을 확인해 주세요.\')\n    offered=descriptor(manifest[\'apps\'].get(\'jihunius\'),require_protocol=False)\n    if version(offered[\'version\'])<version(current[\'version\']):return {\'kind\':\'current\'}\n    if version(offered[\'version\'])==version(current[\'version\']):\n        if offered[\'sha256\']!=current[\'sha256\']:raise UpdateError(\'같은 버전의 내용이 달라 업데이트를 보류했습니다.\')\n        return {\'kind\':\'current\'}\n    offered=descriptor(offered)\n    if offered[\'sha256\']==rejected_sha:return {\'kind\':\'rejected\',\'offered\':offered}\n    return {\'kind\':\'available\',\'offered\':offered}\n\nclass Store:\n    def __init__(self,root,origin,base_version):\n        self.root=Path(root);self.origin=Path(origin).resolve();self.base_version=base_version\n    def state(self):return read_json(self.root/\'state.json\')\n    def save(self,state):write_json(self.root/\'state.json\',state)\n    def path(self,value):\n        if not isinstance(value,dict) or not SHA.fullmatch(str(value.get(\'sha256\',\'\'))):raise UpdateError(\'캐시 정보가 올바르지 않습니다.\')\n        return self.root/\'versions\'/value[\'sha256\']/\'app.pyw\'\n    def valid(self,value):\n        try:\n            value=descriptor(value);p=self.path(value)\n            if p.is_symlink() or p.parent.is_symlink() or p.stat().st_size!=value[\'size\']:return None\n            verify(p.read_bytes(),value);return value\n        except (OSError,ValueError,TypeError,KeyError,UpdateError):return None\n    def prepare(self):\n        data=self.origin.read_bytes()\n        base=descriptor({\'version\':self.base_version,\'path\':\'releases/jihunius/{}/app.pyw\'.format(self.base_version),\n                         \'sha256\':hashlib.sha256(data).hexdigest(),\'size\':len(data),\'min_python\':[3,8],\'update_protocol\':1})\n        verify(data,base)\n        if not self.valid(base):atomic(self.path(base),data)\n        state=self.state();current=self.valid(state.get(\'current\'));previous=self.valid(state.get(\'previous\'))\n        if current is None:current=previous\n        if current is None or version(current[\'version\'])<version(base[\'version\']):current=base\n        state.update(current=current,previous=previous,base=base)\n        self.save(state);self.cancel_request();self.prune(state)\n        return current\n    def stage(self,value,data):\n        value=descriptor(value);verify(data,value)\n        atomic(self.path(value),data)\n        return value\n    def request(self,value,nonce):\n        value=self.valid(value)\n        if value is None:raise UpdateError(\'준비된 업데이트 파일을 확인하지 못했습니다.\')\n        current=self.state().get(\'current\')\n        if version(value[\'version\'])<=version(current[\'version\']):raise UpdateError(\'더 새로운 버전만 적용할 수 있습니다.\')\n        write_json(self.root/\'request.json\',{\'nonce\':nonce,\'offered\':value})\n    def cancel_request(self):\n        try:(self.root/\'request.json\').unlink()\n        except FileNotFoundError:pass\n    def consume_request(self,nonce,returncode):\n        request=read_json(self.root/\'request.json\');self.cancel_request()\n        if returncode!=0 or request.get(\'nonce\')!=nonce:return False\n        offered=self.valid(request.get(\'offered\'));state=self.state();current=self.valid(state.get(\'current\'))\n        if offered is None or current is None or version(offered[\'version\'])<=version(current[\'version\']):return False\n        state.update(previous=current,current=offered,rejected_sha=None,trial=offered[\'sha256\'])\n        self.save(state);return True\n    def restore_failed(self,current):\n        state=self.state()\n        if state.get(\'trial\')!=current[\'sha256\']:return False\n        previous=self.valid(state.get(\'previous\'))\n        if previous is None:return False\n        state.update(current=previous,previous=None,trial=None,rejected_sha=current[\'sha256\'])\n        self.save(state);return True\n    def confirm(self,current):\n        state=self.state()\n        if state.get(\'trial\')==current[\'sha256\']:state[\'trial\']=None;self.save(state)\n    def prune(self,state):\n        keep={x[\'sha256\'] for x in (state.get(\'base\'),state.get(\'current\'),state.get(\'previous\')) if isinstance(x,dict) and SHA.fullmatch(str(x.get(\'sha256\',\'\')))}\n        for p in (self.root/\'versions\').glob(\'*\'):\n            if SHA.fullmatch(p.name) and p.name not in keep and p.is_dir() and not p.is_symlink():shutil.rmtree(p,ignore_errors=True)\n\ndef root_for(origin):\n    key=hashlib.sha256(os.path.normcase(str(Path(origin).resolve())).encode(\'utf-8\')).hexdigest()[:24]\n    return Path(os.environ.get(\'LOCALAPPDATA\') or Path.home())/\'JihuniusTools\'/\'desktop-v1\'/key\n\ndef show_message(text):\n    if os.name==\'nt\':ctypes.windll.user32.MessageBoxW(0,text,\'지후니우스 업데이트\',0x40)\n    else:print(text,file=sys.stderr)\n\ndef focus_process(pid):\n    if os.name!=\'nt\' or type(pid) is not int or pid<=0:return False\n    from ctypes import wintypes as w\n    u=ctypes.WinDLL(\'user32\',use_last_error=True);cb=ctypes.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)\n    u.EnumWindows.argtypes=[cb,w.LPARAM];u.EnumWindows.restype=w.BOOL\n    u.GetWindowThreadProcessId.argtypes=[w.HWND,ctypes.POINTER(w.DWORD)];u.GetWindowThreadProcessId.restype=w.DWORD\n    u.GetWindowTextW.argtypes=[w.HWND,w.LPWSTR,ctypes.c_int];u.GetWindowTextW.restype=ctypes.c_int\n    u.ShowWindow.argtypes=[w.HWND,ctypes.c_int];u.ShowWindow.restype=w.BOOL\n    u.SetForegroundWindow.argtypes=[w.HWND];u.SetForegroundWindow.restype=w.BOOL\n    found=[]\n    def visit(hwnd,lparam):\n        actual=w.DWORD();u.GetWindowThreadProcessId(hwnd,ctypes.byref(actual))\n        if actual.value==pid:\n            title=ctypes.create_unicode_buffer(128);u.GetWindowTextW(hwnd,title,128)\n            if title.value==\'지후니우스\':found.append(hwnd)\n        return True\n    u.EnumWindows(cb(visit),0)\n    if not found:return False\n    u.ShowWindow(found[0],9);u.SetForegroundWindow(found[0]);return True\n\ndef managed_context():\n    if os.environ.get(\'JIHUNIUS_UPDATE_CHILD\')!=\'1\':return None\n    origin=os.environ.get(\'JIHUNIUS_UPDATE_ORIGIN\',\'\');nonce=os.environ.get(\'JIHUNIUS_UPDATE_NONCE\',\'\')\n    if not origin or not re.fullmatch(r\'[0-9a-f]{32}\',nonce):return None\n    root=root_for(origin);session=read_json(root/\'session.json\')\n    if session.get(\'nonce\')!=nonce or session.get(\'pid\') not in (None,os.getpid()):return None\n    value=descriptor(session.get(\'current\'))\n    if Path(sys.argv[0]).resolve()!=root/\'versions\'/value[\'sha256\']/\'app.pyw\':return None\n    return {\'origin\':origin,\'nonce\':nonce,\'root\':root,\'current\':value,\'base_version\':session[\'base_version\'],\n            \'supervisor_pid\':session.get(\'supervisor_pid\')}\n\ndef process_alive(pid):\n    if type(pid) is not int or pid<=0:return False\n    if os.name==\'nt\':\n        from ctypes import wintypes as w\n        kernel=ctypes.WinDLL(\'kernel32\',use_last_error=True)\n        kernel.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];kernel.OpenProcess.restype=w.HANDLE\n        kernel.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD];kernel.WaitForSingleObject.restype=w.DWORD\n        kernel.CloseHandle.argtypes=[w.HANDLE];kernel.CloseHandle.restype=w.BOOL\n        handle=kernel.OpenProcess(0x00100000,False,pid)\n        if not handle:return False\n        try:return kernel.WaitForSingleObject(handle,0)==258\n        finally:kernel.CloseHandle(handle)\n    try:os.kill(pid,0);return True\n    except OSError:return False\n\ndef managed_lease(context):\n    lease=FileLock(context[\'root\']/\'active-app.lock\')\n    if not lease.acquire():raise UpdateError(\'이미 실행 중인 지후니우스 창을 먼저 확인해 주세요.\')\n    return lease\n\ndef native_dialog_open(root, allowed_grab=None):\n    try:\n        grabbed=root.grab_current()\n        if grabbed is not None and grabbed is not allowed_grab:return True\n        if os.name!=\'nt\':return False\n        from ctypes import wintypes as w\n        u=ctypes.WinDLL(\'user32\',use_last_error=True)\n        u.GetAncestor.argtypes=[w.HWND,w.UINT];u.GetAncestor.restype=w.HWND\n        u.IsWindowEnabled.argtypes=[w.HWND];u.IsWindowEnabled.restype=w.BOOL\n        owner=u.GetAncestor(root.winfo_id(),2)\n        return bool(owner) and not bool(u.IsWindowEnabled(owner))\n    except Exception:\n        # If the native state cannot be checked, do not assume it is safe to exit.\n        return True\n\ndef mark_ready(context):\n    if context:\n        # Older installed launchers check this marker before creating a shortcut.\n        # Keep them disabled when they start a newer cached version.\n        atomic(context[\'root\']/\'shortcut-created\',b\'disabled\')\n        write_json(context[\'root\']/\'ready.json\',{\'nonce\':context[\'nonce\']})\n\ndef launch(origin,base_version,argv=None,icon_bytes=None):\n    origin=Path(origin).resolve();store=Store(root_for(origin),origin,base_version)\n    lock=FileLock(store.root/\'instance.lock\')\n    if not lock.acquire():\n        if not focus_process(read_json(store.root/\'session.json\').get(\'pid\')):\n            show_message(\'지후니우스가 이미 실행 중입니다. 트레이 아이콘에서 열어 주세요.\')\n        return 0\n    try:\n        active=FileLock(store.root/\'active-app.lock\')\n        if not active.acquire():\n            if not focus_process(read_json(store.root/\'session.json\').get(\'pid\')):\n                show_message(\'지후니우스가 실행 중입니다. 트레이에서 열거나 완전 종료한 뒤 다시 실행하세요.\')\n            return 0\n        active.release()\n        current=store.prepare()\n        while True:\n            nonce=uuid.uuid4().hex\n            session={\'nonce\':nonce,\'current\':current,\'base_version\':base_version,\'supervisor_pid\':os.getpid()}\n            write_json(store.root/\'session.json\',session)\n            try:(store.root/\'ready.json\').unlink()\n            except FileNotFoundError:pass\n            environment=os.environ.copy()\n            environment.update(JIHUNIUS_UPDATE_CHILD=\'1\',JIHUNIUS_UPDATE_ORIGIN=str(origin),JIHUNIUS_UPDATE_NONCE=nonce,\n                               JIHUNIUS_LAUNCH_DIR=str(origin.parent))\n            executable=Path(sys.executable)\n            if os.name==\'nt\' and executable.with_name(\'pythonw.exe\').is_file():executable=executable.with_name(\'pythonw.exe\')\n            try:\n                process=subprocess.Popen([str(executable),str(store.path(current))]+list(argv or []),cwd=str(origin.parent),env=environment)\n            except OSError:\n                store.restore_failed(current)\n                raise UpdateError(\'프로그램을 시작하지 못했습니다. 기존 버전과 Python 설치를 확인해 주세요.\') from None\n            session[\'pid\']=process.pid;write_json(store.root/\'session.json\',session)\n            code=process.wait()\n            ready=read_json(store.root/\'ready.json\').get(\'nonce\')==nonce\n            if not ready:\n                if store.restore_failed(current):\n                    show_message(\'새 버전이 시작되지 않아 이전 버전으로 복구했습니다. 같은 파일을 다시 실행해 주세요.\')\n                else:show_message(\'지후니우스가 시작을 완료하지 못했습니다. 표시된 실행 오류를 확인해 주세요.\')\n                store.cancel_request();return code or 1\n            store.confirm(current)\n            if not store.consume_request(nonce,code):return code\n            current=store.state()[\'current\']\n    except (OSError,ValueError,UpdateError) as exc:\n        show_message(str(exc) if isinstance(exc,UpdateError) else \'업데이트 저장 공간을 확인해 주세요. 업무 파일은 변경하지 않았습니다.\')\n        return 1\n    finally:lock.release()\n\n"""In-app controls. Concatenated with engine.py by the distribution builder."""\nimport queue\nimport threading\nimport time\n\nAUTO_CHECK_SECONDS = 60\n\ndef block_reason(app, update_window=None, allow_companions=False):\n    if \'native_dialog_open\' in globals() and native_dialog_open(app.window,update_window):\n        return \'파일 선택 또는 확인 창을 먼저 닫은 뒤 다시 눌러 주세요.\'\n    if getattr(getattr(app,\'wash_app\',None),\'busy\',False):\n        return \'세척완료 작업 중입니다. 작업이 끝난 뒤 다시 눌러 주세요.\'\n    if getattr(app,\'busy\',False) or getattr(app,\'card_modifier_pending\',False):\n        return \'파일 작업 중입니다. 작업이 끝난 뒤 다시 눌러 주세요.\'\n    if getattr(app,\'handover_writing\',False) or getattr(app,\'handover_dialog\',None) is not None:\n        return \'인수인계 내용을 저장하고 창을 닫은 뒤 다시 눌러 주세요.\'\n    stl=getattr(app,\'stl_app\',None)\n    worker=getattr(stl,\'worker\',None)\n    if getattr(stl,\'busy\',False) is True or (worker is not None and worker.is_alive()):\n        return \'STL 검색 중입니다. 검색이 끝난 뒤 다시 눌러 주세요.\'\n    if not allow_companions and app._suite_children.running_keys():\n        return \'돌출량·세척일보 보조창을 저장하고 닫은 뒤 다시 눌러 주세요.\'\n    if getattr(app,\'_suite_exit_pending\',False):return \'종료 처리가 진행 중입니다.\'\n    if app.number_input.get(\'1.0\',\'end-1c\').strip():\n        return \'프로그램 번호 입력 내용이 남아 있습니다. 필요한 내용을 보관하고 입력칸을 비운 뒤 다시 눌러 주세요.\'\n    stl_input=getattr(stl,\'input\',None)\n    if stl_input is not None and stl_input.get(\'1.0\',\'end-1c\').strip():\n        return \'STL 주문 입력 내용이 남아 있습니다. 내용을 보관하고 입력칸을 비운 뒤 다시 눌러 주세요.\'\n    for window in app.window.winfo_children():\n        if window is not update_window and window.winfo_class()==\'Toplevel\' and window.winfo_exists():\n            return \'열린 설정·입력 창을 먼저 닫아 주세요.\'\n    return \'\'\n\nclass Controller:\n    def __init__(self,app,context,app_version):\n        self.app=app;self.root=app.window;self.context=context;self.app_version=app_version\n        self.current=context[\'current\'] if context else None\n        self.store=Store(context[\'root\'],context[\'origin\'],context[\'base_version\']) if context else None\n        self.events=queue.Queue(maxsize=4);self.busy=False;self.closed=False;self.last_check=None\n        self.dialog=None;self.offered=None;self.staged=None;self.applying=False;self.timer=None;self.check_timer=None\n        self.save_timer=None\n        self._download_apply=False\n        self.message=\'시작할 때와 실행 중 1분마다 새 버전을 자동 확인합니다.\'\n        self.label=app.tk.StringVar(value=\'업데이트\')\n        self.button=app.ttk.Button(app.title_label.master,textvariable=self.label,style=\'Popup.TButton\',command=self.open)\n        self.button.pack(side=\'right\',padx=(12,0))\n        self._restore=app.restore_from_tray\n        def restore(cancel_exit=True):\n            self._restore(cancel_exit=cancel_exit)\n            self.check()\n        app.restore_from_tray=restore\n        self._exit=app.request_complete_exit\n        def complete_exit():\n            if self.applying:\n                self.message=\'업데이트 전 저장 중입니다. 업데이트 창을 닫아 취소한 뒤 종료해 주세요.\'\n                self.open();self.refresh();return\n            self._exit()\n        app.request_complete_exit=complete_exit\n        self._finish=app._finish_suite_shutdown\n        def finish():\n            if self.applying:\n                reason=block_reason(app,self.dialog)\n                if reason:self.abort_apply(reason);return\n                try:self.store.request(self.staged,self.context[\'nonce\'])\n                except Exception:\n                    self.abort_apply(\'업데이트 적용 요청을 저장하지 못했습니다. 현재 프로그램을 유지합니다.\');return\n            try:self._finish()\n            except Exception:\n                if self.applying:\n                    self.store.cancel_request();self.abort_apply(\'종료하지 못했습니다. 현재 프로그램을 유지합니다.\')\n                raise\n            if app._suite_stopped:\n                self.closed=True\n                for name in (\'timer\',\'check_timer\',\'save_timer\'):\n                    timer=getattr(self,name)\n                    if timer is not None:\n                        try:self.root.after_cancel(timer)\n                        except app.tk.TclError:pass\n                        setattr(self,name,None)\n            elif self.applying:\n                self.store.cancel_request();self.abort_apply(\'종료 조건이 바뀌어 업데이트를 보류했습니다.\')\n        app._finish_suite_shutdown=finish\n        self.schedule_check(500)\n\n    def schedule_check(self,delay_ms=AUTO_CHECK_SECONDS*1000):\n        if self.check_timer is not None:\n            try:self.root.after_cancel(self.check_timer)\n            except self.app.tk.TclError:pass\n            self.check_timer=None\n        if not self.closed and self.current is not None:\n            self.check_timer=self.root.after(delay_ms,self.auto_check)\n\n    def auto_check(self):\n        self.check_timer=None\n        if self.closed:return\n        if not self.check():self.schedule_check()\n\n    def task(self,kind,action):\n        if self.busy or self.closed:return False\n        self.busy=True;self.refresh()\n        def worker():\n            try:self.events.put((kind,True,action()))\n            except Exception as exc:\n                msg=str(exc) if isinstance(exc,UpdateError) else \'업데이트 처리에 실패했습니다. 기존 버전은 계속 사용할 수 있습니다.\'\n                self.events.put((kind,False,msg))\n        threading.Thread(target=worker,daemon=True).start()\n        self.timer=self.root.after(100,self.poll)\n        return True\n\n    def check(self,force=False):\n        if self.closed or self.busy or self.applying or self.current is None:return False\n        if not force and self.last_check is not None and time.monotonic()-self.last_check<AUTO_CHECK_SECONDS:return False\n        self.last_check=time.monotonic();self.message=\'새 버전을 확인하고 있습니다…\'\n        if not self.offered:self.label.set(\'업데이트 확인 중\')\n        started=self.task(\'check\',lambda:check_offer(self.current,rejected_sha=self.store.state().get(\'rejected_sha\')))\n        if started:self.schedule_check()\n        return started\n\n    def poll(self):\n        self.timer=None\n        if self.closed:return\n        try:kind,ok,value=self.events.get_nowait()\n        except queue.Empty:\n            if self.busy:self.timer=self.root.after(100,self.poll)\n            return\n        self.busy=False\n        if not ok:\n            self.message=value\n            self.label.set(\'새 버전 있음\' if self.offered else \'업데이트 확인\')\n        elif kind==\'check\':\n            if value[\'kind\']==\'available\':\n                self.offered=value[\'offered\'];self.label.set(\'새 버전 있음\')\n                self.message=\'새 버전이 있습니다. 변경 내용을 확인하고 적용해 주세요.\'\n            elif value[\'kind\']==\'rejected\':\n                self.offered=None;self.label.set(\'업데이트\')\n                self.message=\'시작에 실패해 복구한 버전입니다. 수정된 새 배포를 기다립니다.\'\n            else:\n                self.offered=None;self.label.set(\'업데이트\');self.message=\'현재 사용할 수 있는 최신 버전입니다.\'\n        elif kind==\'download\':\n            self.staged=value;self.message=\'새 버전 검증을 마쳤습니다.\'\n            resume=self._download_apply;self._download_apply=False\n            self.refresh()\n            if resume:self.apply()\n            return\n        self.refresh()\n\n    def open(self):\n        if self.closed:return\n        if self.dialog is not None and self.dialog.winfo_exists():\n            self.dialog.deiconify();self.dialog.lift();return\n        tk,ttk=self.app.tk,self.app.ttk\n        dialog=tk.Toplevel(self.root);self.dialog=dialog\n        dialog.title(\'지후니우스 업데이트\');dialog.configure(bg=\'#101722\')\n        dialog.geometry(\'640x460\');dialog.minsize(560,430)\n        dialog.transient(self.root);dialog.protocol(\'WM_DELETE_WINDOW\',self.close_dialog)\n        frame=ttk.Frame(dialog,padding=22);frame.pack(fill=\'both\',expand=True)\n        frame.columnconfigure(0,weight=1);frame.rowconfigure(2,weight=1)\n        ttk.Label(frame,text=\'지후니우스 업데이트\',style=\'Title.TLabel\').grid(row=0,column=0,sticky=\'w\',pady=(0,12))\n        self.versions=tk.StringVar();ttk.Label(frame,textvariable=self.versions).grid(row=1,column=0,sticky=\'w\',pady=(0,10))\n        self.notes=tk.Text(frame,height=8,wrap=\'word\',bg=\'#172131\',fg=\'#e6edf5\',relief=\'flat\',padx=12,pady=12,\n                           font=(\'맑은 고딕\',10),highlightthickness=0)\n        self.notes.grid(row=2,column=0,sticky=\'nsew\')\n        self.status=tk.StringVar();ttk.Label(frame,textvariable=self.status,wraplength=585,justify=\'left\').grid(row=3,column=0,sticky=\'ew\',pady=(12,10))\n        controls=ttk.Frame(frame);controls.grid(row=4,column=0,sticky=\'ew\')\n        self.check_button=ttk.Button(controls,text=\'다시 확인\',style=\'Popup.TButton\',command=lambda:self.check(force=True));self.check_button.pack(side=\'left\')\n        self.apply_button=ttk.Button(controls,text=\'업데이트 후 다시 시작\',style=\'Selected.Mode.TButton\',command=self.apply);self.apply_button.pack(side=\'right\')\n        dialog.bind(\'<Configure>\',lambda event:self.status_label_wrap(frame),add=\'+\')\n        self.refresh()\n\n    def status_label_wrap(self,frame):\n        # Fixed initial size is ample; resize only the line wrapping, never poll layout.\n        for widget in frame.grid_slaves(row=3,column=0):widget.configure(wraplength=max(300,frame.winfo_width()-44))\n\n    def close_dialog(self):\n        self._download_apply=False\n        if self.applying:\n            self.abort_apply(\'업데이트를 취소했습니다. 현재 버전을 계속 사용할 수 있습니다.\')\n            return\n        if self.dialog is not None:self.dialog.destroy();self.dialog=None\n\n    def refresh(self):\n        if self.closed:return\n        self.button.configure(style=\'HandoverNotice.TButton\' if self.offered else \'Popup.TButton\')\n        if self.offered:self.label.set(\'새 버전 있음\')\n        if self.dialog is None or not self.dialog.winfo_exists():return\n        current=self.current[\'version\'] if self.current else self.app_version\n        self.versions.set(\'현재 \'+current+(\'   →   새 버전 \'+self.offered[\'version\'] if self.offered else \'\'))\n        notes=self.offered.get(\'notes\',\'\') if self.offered else \'\'\n        text=notes or (\'변경 내용이 등록되지 않았습니다.\' if self.offered else \'새 버전이 있으면 변경 내용과 사용 안내가 여기에 표시됩니다.\')\n        if self.notes.get(\'1.0\',\'end-1c\')!=text:\n            self.notes.configure(state=\'normal\');self.notes.delete(\'1.0\',\'end\');self.notes.insert(\'1.0\',text);self.notes.configure(state=\'disabled\')\n        self.status.set(self.message)\n        self.check_button.configure(state=\'disabled\' if self.busy or self.applying else \'normal\')\n        self.apply_button.configure(state=\'normal\' if self.offered and not self.busy and not self.applying else \'disabled\')\n\n    def apply(self):\n        if self.closed or self.busy or self.applying or not self.offered or self.context is None:return\n        if not process_alive(self.context.get(\'supervisor_pid\')):\n            self.message=\'재시작 실행기 연결이 종료됐습니다. 지후니우스를 완전 종료하고 기존 실행 파일을 다시 열어 주세요.\'\n            self.refresh();return\n        reason=block_reason(self.app,self.dialog,allow_companions=True)\n        if reason:self.message=reason;self.refresh();return\n        if self.staged is None or self.staged[\'sha256\']!=self.offered[\'sha256\']:\n            offered=dict(self.offered);self.message=\'새 버전을 내려받고 검증하고 있습니다…\'\n            self._download_apply=True\n            self.task(\'download\',lambda:self.store.stage(offered,public_fetch(offered[\'path\'],offered[\'size\'],20)))\n            return\n        self.open()\n        self.applying=True;self.message=\'세척일보·돌출량표를 저장하고 있습니다…\';self.refresh()\n        self.dialog.grab_set()\n        try:self.app._suite_children.begin_update_save()\n        except Exception as exc:self.abort_apply(str(exc));return\n        self.save_timer=self.root.after(100,self.poll_companion_save)\n\n    def abort_apply(self,message):\n        self._download_apply=False\n        self.app._suite_children.cancel_update_save()\n        if self.save_timer is not None:\n            try:self.root.after_cancel(self.save_timer)\n            except self.app.tk.TclError:pass\n            self.save_timer=None\n        if self.dialog is not None and self.dialog.winfo_exists():self.dialog.grab_release()\n        self.applying=False;self.message=message;self.refresh()\n\n    def poll_companion_save(self):\n        self.save_timer=None\n        if self.closed or not self.applying:return\n        reason=block_reason(self.app,self.dialog,allow_companions=True)\n        if reason:self.abort_apply(reason);return\n        try:done=self.app._suite_children.poll_update_save()\n        except Exception as exc:self.abort_apply(str(exc));return\n        if done:\n            self.message=\'저장을 확인했습니다. 업데이트 후 다시 시작합니다…\';self.refresh()\n            self.app._finish_suite_shutdown()\n        else:self.save_timer=self.root.after(100,self.poll_companion_save)\n\ndef attach(app,context,app_version,icon_bytes=None):\n    controller=Controller(app,context,app_version)\n    app.updates=controller\n    return controller\n')
def main():
    if "--console" in sys.argv:
        return main_console()
    context = SuiteUpdater.managed_context()
    if context is None:
        code = SuiteUpdater.launch(Path(__file__).resolve(), SUITE_APP_VERSION, sys.argv[1:])
        if code:
            raise SystemExit(code)
        return
    lease = SuiteUpdater.managed_lease(context)
    try:
        configure_windows_app_identity()
        import tkinter as tk
        window = tk.Tk()
        app = IntegrationApp(window)
        SuiteUpdater.attach(app, context, SUITE_APP_VERSION)
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
