"""Windows용 STL 파일 찾기 (Python 3.9 이상, 추가 패키지 불필요).

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
DEFAULT_FOLDER = r"\\srvc5352374b\생산공유폴더\★커스텀 오더 2026년"
LEGACY_DEFAULT_FOLDER = r"\\192.168.0.254\내부공유폴더\★커스텀 오더 2026년"
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
    "background": "#0e141d", "card": "#141b28", "field": "#0b0f16",
    "text": "#e7edf7", "muted": "#9fa1a6", "border": "#2d3e5b",
    "accent": "#85b4ff", "selection": "#284a79", "disabled": "#202c41",
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
    """The same charcoal panels and mint accents as the 지후니우스 interface."""
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
              foreground=[("disabled", "#818388")], bordercolor=[("focus", colors["accent"])])
    style.configure("STL.TCombobox", fieldbackground=colors["field"], background="#26344d",
                    foreground=colors["text"], arrowcolor=colors["text"],
                    bordercolor=colors["border"], lightcolor=colors["border"],
                    darkcolor=colors["border"], padding=(8, 6))
    style.map("STL.TCombobox", fieldbackground=[("disabled", colors["disabled"]), ("readonly", colors["field"])],
              foreground=[("disabled", "#818388"), ("readonly", colors["text"])],
              selectbackground=[("readonly", colors["field"])],
              selectforeground=[("readonly", colors["text"])],
              bordercolor=[("focus", colors["accent"])])
    style.configure("STL.TCheckbutton", background=colors["card"], foreground=colors["text"],
                    indicatorbackground=colors["field"], indicatorforeground=colors["text"],
                    bordercolor=colors["border"], padding=(0, 2))
    style.map("STL.TCheckbutton", background=[("active", colors["card"])],
              foreground=[("disabled", "#818388")],
              indicatorforeground=[("selected", colors["background"])],
              indicatorbackground=[("disabled", colors["disabled"]), ("selected", colors["accent"])])
    style.configure("STL.Accent.TButton", background="#1f2b3f", foreground="#ffffff", borderwidth=0,
                    padding=(14, 6), font=("맑은 고딕", 10, "bold"))
    style.map("STL.Accent.TButton", background=[("disabled", "#2d4266"), ("active", "#2f6be0")],
              foreground=[("disabled", "#8e9196")])
    style.configure("STL.Secondary.TButton", background="#26344d", foreground="#ffffff",
                    bordercolor="#7b7d82", lightcolor="#7b7d82", darkcolor="#7b7d82",
                    padding=(10, 6), font=("맑은 고딕", 10, "bold"))
    style.map("STL.Secondary.TButton", background=[("disabled", colors["disabled"]), ("active", "#2f405f")],
              foreground=[("disabled", "#96999e"), ("!disabled", "#ffffff")])
    style.configure("STL.Danger.TButton", background=colors["card"], foreground="#f593a5",
                    bordercolor="#633b4b", lightcolor="#633b4b", darkcolor="#633b4b",
                    padding=(10, 6), font=("맑은 고딕", 10, "bold"))
    style.map("STL.Danger.TButton", background=[("disabled", colors["disabled"]), ("active", "#24324a")],
              foreground=[("disabled", "#7d7f84")])
    style.configure("STL.Treeview", font=("맑은 고딕", 9), rowheight=28,
                    background=colors["field"], fieldbackground=colors["field"], foreground=colors["text"],
                    bordercolor=colors["border"], lightcolor=colors["border"], darkcolor=colors["border"])
    style.configure("STL.Treeview.Heading", font=("맑은 고딕", 10, "bold"), background="#26344d",
                    foreground=colors["text"], bordercolor=colors["border"],
                    lightcolor=colors["border"], darkcolor=colors["border"], padding=(6, 6))
    style.map("STL.Treeview", background=[("selected", colors["selection"])], foreground=[("selected", "#ffffff")])
    style.map("STL.Treeview.Heading", background=[("active", "#2f405f")])
    for name in ("STL.Vertical.TScrollbar", "STL.Horizontal.TScrollbar"):
        style.configure(name, background="#344769", troughcolor=colors["field"], borderwidth=0,
                        bordercolor=colors["field"], lightcolor="#344769", darkcolor="#344769",
                        arrowcolor="#a9abaf", arrowsize=12)
        style.map(name, background=[("active", "#405881")])
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
                              bg=UI_COLORS["accent"] if today else UI_COLORS["card"], fg=UI_COLORS["background"] if today else UI_COLORS["text"],
                              activebackground="#2f405f", activeforeground="#ffffff", cursor="hand2",
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
        self.tree.tag_configure("best_match", background="#382f1e", foreground="#ffd166")
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
        from pathlib import PureWindowsPath
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                folder = data.get("folder", "")
                # Explicit per-PC choices survive changes to the bundled default.
                if isinstance(folder, str) and folder.strip():
                    if (data.get('default_folder') != DEFAULT_FOLDER
                            and PureWindowsPath(folder.strip().strip('"')) == PureWindowsPath(LEGACY_DEFAULT_FOLDER)):
                        folder = DEFAULT_FOLDER
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

