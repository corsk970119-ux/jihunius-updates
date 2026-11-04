"""돌출량 현황표 (Tkinter)

실행: roll_defect_ui.pyw를 더블클릭 (Windows에서 CMD 창 없이 실행)

- 위·아래 표에 각각 호기 5칸, 각 제목에서 1호기 ~ 10호기를 드롭다운으로 선택
- 추가된 오른쪽 호기 칸은 번호와 O 표시가 비어 있으며 직접 선택해서 사용
- 왼쪽 제품명(네오부터 T1400까지)은 직접 입력/수정
- 호기 아래 표 칸을 클릭하면 O 표시, 다시 클릭하면 O 삭제
- 호기를 바꾸면 그 호기의 O 표시를 불러오며, 같은 호기는 어디서 보든 같은 표시
- 각 호기 세로줄 맨 아래의 초기화 버튼으로 선택한 호기의 O만 일괄 삭제
- 새로고침 옆 전체초기화 버튼은 확인 후 1~10호기의 O 표시를 모두 삭제
- 두 표 바깥쪽에 여러 줄을 자유롭게 입력하는 별도의 메모칸 제공
- 처음 실행 시 예시 이미지의 O 표시를 그대로 보여줌
- 창 크기 조절 가능 (작은 창에서는 세로 스크롤)
- 검정 배경의 다크 테마, O 표시 칸은 파란색으로 강조
- 호기, 제품명, O 표시, 메모를 공유폴더에 자동 저장
- 다른 PC의 변경 사항을 약 2.5초마다 반영
- 같은 항목의 동시 수정은 확인 후 반영
- Python 기본 라이브러리만 사용
"""

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import ctypes
import errno
import hashlib
import json
import multiprocessing
import os
import queue
import stat
import tempfile
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk


PRODUCTS = [
    "네오(35)",
    "멘티움(40)",
    "메가젠(41)",
    "덴티스(42)",
    "오스템(12)",
    "T1300",
    "T1400",
]

MACHINE_OPTIONS = [""] + [f"{num}호기" for num in range(1, 11)]
MACHINE_NUMBERS = {f"{num}호기": num for num in range(1, 11)}

# 지후니우스 인수인계와 같은 폴더를 사용합니다.
# 현황표는 전용 파일로 저장하므로 인수인계 내용과 섞이지 않습니다.
SHARED_PARENT = Path(r"\\192.168.0.254\내부공유폴더\생산관리\일일 업무 보고\최지훈")
SHARED_FOLDER = SHARED_PARENT / "지후니우스_인수인계"
SHARED_FILENAME = "돌출량_현황표.json"
POLL_MS = 2500
SAVE_DELAY_MS = 500
SYNC_TIMEOUT = 10.0


def _diagnostic_error(message,stage):
    import sys
    module=sys.modules.get("jihunius_error_history")
    if module is not None:module.capture(message,stage=stage)


class Theme:
    BACKGROUND = "#0f0f0f"
    SURFACE = "#181a1e"
    CELL = "#191c20"
    CELL_ALT = "#1d2025"
    PRODUCT = "#22262c"
    HEADER = "#242d38"
    LINE = "#343b45"
    TEXT = "#e1e5eb"
    MUTED = "#9ba5b4"
    ACCENT = "#a4c9f5"
    FOCUS = "#2a3a4e"
    MARK = "#263c53"
    MARK_HOVER = "#304c69"
    EMPTY = "#141619"
    DISABLED = "#5e6876"
    RESET_BG = "#30252b"
    RESET_HOVER = "#493039"
    RESET_TEXT = "#dfadb5"
    WARNING = "#d6bb85"
    ERROR = "#ed9c9c"
    SUCCESS = "#98c8ad"

# (제품 행, 호기 열), 각 번호는 0부터 시작합니다.
UPPER_MARKS = {
    (0, 1),
    (1, 1), (1, 3),
    (2, 2),
    (4, 0), (4, 1), (4, 2),
    (5, 1),
}
LOWER_MARKS = {
    (0, 0), (0, 1), (0, 3),
    (1, 0), (1, 1), (1, 2), (1, 3),
    (3, 1),
    (4, 0), (4, 2), (4, 3),
    (5, 1),
    (6, 1),
}

# 기존 네 칸의 호기 선택 순서는 유지하고 오른쪽 빈 칸도 함께 표시합니다.
TABLE_LAYOUTS = (
    ("upper", (1, 2, 3, 7, None), UPPER_MARKS),
    ("lower", (4, 6, 8, 9, None), LOWER_MARKS),
)


def machine_label(number):
    return "" if number is None else f"{number}호기"


def column_values(columns=5):
    """이전 버전의 위치별 저장 형식. 기존 기록을 읽어 옮길 때만 사용합니다."""
    values = {"memo": ""}
    for name, machines, marks in TABLE_LAYOUTS:
        for column, number in enumerate(machines[:columns]):
            values[f"{name}.machine.{column}"] = machine_label(number)
        for row, product in enumerate(PRODUCTS):
            values[f"{name}.product.{row}"] = product
            for column in range(columns):
                values[f"{name}.mark.{row}.{column}"] = (row, column) in marks
    return values


def machine_mark_key(number, row):
    return f"machine.{number}.mark.{row}"


def default_values():
    values = {key: value for key, value in column_values().items() if ".mark." not in key}
    for number in MACHINE_NUMBERS.values():
        for row in range(len(PRODUCTS)):
            values[machine_mark_key(number, row)] = False
    for _name, machines, marks in TABLE_LAYOUTS:
        for row, column in marks:
            values[machine_mark_key(machines[column], row)] = True
    return values


class SharedStore:
    """공유폴더에서 변경한 칸만 병합하고, 같은 칸의 충돌을 확인합니다."""

    LOCK_TIMEOUT = 4.0

    def __init__(self, folder=None):
        self.folder = Path(folder) if folder is not None else SHARED_FOLDER
        self.path = self.folder / SHARED_FILENAME
        self.lock_path = self.folder / "돌출량_현황표.lock"

    def _ensure_folder(self):
        if not self.folder.parent.is_dir():
            raise OSError("공유폴더에 연결할 수 없습니다: " + str(self.folder.parent))
        self.folder.mkdir(exist_ok=True)
        if not self.folder.is_dir():
            raise OSError("저장 위치가 폴더가 아닙니다: " + str(self.folder))

    @contextmanager
    def _lock(self):
        self._ensure_folder()
        deadline = time.monotonic() + self.LOCK_TIMEOUT
        if os.name == "nt":
            from ctypes import wintypes

            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            create = kernel.CreateFileW
            create.argtypes = [
                wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
            ]
            create.restype = wintypes.HANDLE
            close = kernel.CloseHandle
            close.argtypes = [wintypes.HANDLE]
            close.restype = wintypes.BOOL
            invalid = ctypes.c_void_p(-1).value
            while True:
                # 공유 금지로 연 핸들은 SMB에서도 쓰기를 직렬화합니다.
                handle = create(str(self.lock_path), 0xC0000000, 0, None, 4, 0x80, None)
                if handle != invalid:
                    break
                code = ctypes.get_last_error()
                if code not in (32, 33):
                    raise ctypes.WinError(code)
                if time.monotonic() >= deadline:
                    raise OSError("다른 PC에서 저장 중입니다. 잠시 뒤 다시 시도해 주세요.")
                time.sleep(0.05)
            try:
                yield
            finally:
                close(handle)
        else:
            import fcntl

            with self.lock_path.open("a+b") as stream:
                while True:
                    try:
                        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except OSError as error:
                        if error.errno not in (errno.EACCES, errno.EAGAIN):
                            raise
                        if time.monotonic() >= deadline:
                            raise OSError("다른 PC에서 저장 중입니다. 잠시 뒤 다시 시도해 주세요.")
                        time.sleep(0.05)
                try:
                    yield
                finally:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    @staticmethod
    def _validate_value(key, value, defaults=None):
        defaults = default_values() if defaults is None else defaults
        if key not in defaults:
            raise ValueError("알 수 없는 현황표 항목입니다: " + str(key))
        if ".mark." in key:
            valid = type(value) is bool
        elif ".machine." in key:
            valid = isinstance(value, str) and value in MACHINE_OPTIONS
        else:
            valid = isinstance(value, str)
        if not valid:
            raise ValueError("현황표 항목의 값이 올바르지 않습니다: " + key)

    def _read(self):
        try:
            raw = self.path.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            # Windows network-name failures can also appear as FileNotFoundError.
            # Initialize only a genuinely missing file on an accessible share.
            winerror = getattr(error, "winerror", None)
            if winerror is not None:
                if winerror != 2:
                    raise
            elif error.errno != errno.ENOENT:
                raise
            if not stat.S_ISDIR(self.folder.stat().st_mode):
                raise NotADirectoryError("공유 현황표 폴더에 연결할 수 없습니다: " + str(self.folder))
            return {"version": 3, "revision": 0, "values": default_values()}, True
        state = json.loads(raw)
        if (not isinstance(state, dict) or state.get("version") not in (1, 2, 3)
                or type(state.get("revision")) is not int or state["revision"] < 0
                or not isinstance(state.get("values"), dict)):
            raise ValueError("공유 현황표의 형식을 읽을 수 없습니다. 저장 파일을 확인해 주세요.")
        defaults = (default_values() if state["version"] == 3
                    else column_values(4 if state["version"] == 1 else 5))
        if set(state["values"]) != set(defaults):
            raise ValueError("공유 현황표의 항목이 올바르지 않습니다. 저장 파일을 확인해 주세요.")
        for key, value in state["values"].items():
            self._validate_value(key, value, defaults)
        if state["version"] in (1, 2):
            old = dict(state["values"])
            values = default_values()
            # 예시 O 표시를 되살리지 않고, 실제로 저장된 표시만 가져옵니다.
            for key in values:
                if ".mark." in key:
                    values[key] = False
                elif key in old:
                    values[key] = old[key]
            columns = 4 if state["version"] == 1 else 5
            for name, _machines, _marks in TABLE_LAYOUTS:
                for column in range(columns):
                    number = MACHINE_NUMBERS.get(old[f"{name}.machine.{column}"])
                    if number is not None:
                        for row in range(len(PRODUCTS)):
                            key = machine_mark_key(number, row)
                            # 같은 호기가 여러 칸에 있으면 기존 O를 합쳐 보존합니다.
                            values[key] = values[key] or old[f"{name}.mark.{row}.{column}"]
            # 호기가 비어 있던 칸까지 포함해 이전 기록도 그대로 보관합니다.
            state["column_values_before_machine_linking"] = old
            state["version"] = 3
            state["values"] = values
            return state, True
        return state, False

    def _write(self, state):
        # sync() holds the same exclusive lock for every PC throughout this write.
        # A killed SMB helper cannot run finally, so reuse our one staging name
        # on the next attempt rather than accumulating abandoned snapshots.
        temporary = self.folder / '.jihunius_protrusion_stage_v1.tmp'
        descriptor = os.open(str(temporary), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(state, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            deadline = time.monotonic() + self.LOCK_TIMEOUT
            while True:
                try:
                    os.replace(str(temporary), str(self.path))
                    break
                except OSError as error:
                    if getattr(error, "winerror", None) not in (32, 33):
                        raise
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(0.05)
        finally:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass

    def sync(self, operations=()):
        operations = [dict(operation) for operation in operations]
        for operation in operations:
            self._validate_value(operation["key"], operation["value"])
            self._validate_value(operation["key"], operation["base"])
        with self._lock():
            state, created = self._read()
            changed = False
            conflicts = []
            for operation in operations:
                key = operation["key"]
                current = state["values"][key]
                # 재전송된 저장 요청도, 이미 같은 값이면 성공으로 처리합니다.
                if current == operation["value"]:
                    continue
                if current != operation["base"]:
                    conflicts.append(key)
                    continue
                state["values"][key] = operation["value"]
                changed = True
            if created or changed:
                state["revision"] += 1
                state["updated_at"] = datetime.now().isoformat(timespec="seconds")
                self._write(state)
            return {"state": state, "conflicts": conflicts}


def _shared_store_service(connection, folder):
    """Only this disposable process may wait inside a shared-folder OS call."""
    store = SharedStore(folder)
    try:
        while True:
            operations = connection.recv()
            if operations is None:
                return
            try:
                reply = (True, store.sync(operations))
            except Exception as error:
                reply = (False, str(error))
            connection.send(reply)
    except (EOFError, BrokenPipeError, OSError):
        pass
    finally:
        connection.close()


class SharedStoreClient:
    """Reuse one helper for healthy polls; terminate it on timeout or close."""

    def __init__(self, folder=None, timeout=SYNC_TIMEOUT, stop=None):
        self.folder = str(folder if folder is not None else SHARED_FOLDER)
        self.path = Path(self.folder) / SHARED_FILENAME
        self.timeout = timeout
        self.stop = stop
        self.process = None
        self.connection = None

    def close(self):
        connection, self.connection = self.connection, None
        process, self.process = self.process, None
        if process is not None:
            try:
                if process.is_alive():
                    process.terminate()
                process.join(timeout=.3)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=.3)
                if not process.is_alive():
                    process.close()
            except (OSError, ValueError):
                pass
        if connection is not None:
            try:
                connection.close()
            except OSError:
                pass

    def _start(self):
        if self.process is not None and self.process.is_alive():
            return
        self.close()
        context = multiprocessing.get_context('spawn')
        parent, child = context.Pipe()
        process = context.Process(target=_shared_store_service,
                                  args=(child, self.folder), daemon=True)
        try:
            process.start()
        except Exception:
            parent.close()
            child.close()
            process.close()
            raise
        child.close()
        self.process, self.connection = process, parent

    def sync(self, operations=()):
        try:
            if self.stop is not None and self.stop.is_set():
                raise OSError('프로그램 종료 중입니다.')
            deadline = time.monotonic() + self.timeout
            self._start()
            self.connection.send([dict(operation) for operation in operations])
            while True:
                if self.stop is not None and self.stop.is_set():
                    raise OSError('프로그램 종료 중입니다.')
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('공유폴더 응답이 지연되어 대기를 중단했습니다. '
                                       '미저장 내용은 유지하며 연결 후 저장 여부를 다시 확인합니다.')
                if self.connection.poll(min(.1, remaining)):
                    ok, result = self.connection.recv()
                    if not ok:
                        raise OSError(result)
                    return result
                if not self.process.is_alive():
                    raise OSError('공유폴더 처리 응답을 받지 못했습니다.')
        except Exception:
            self.close()
            raise


class PendingRecovery:
    """A single replaced PC-local snapshot, retaining each edit's original base."""

    def __init__(self, shared_path, path=None):
        self.shared_path = os.path.normcase(os.path.abspath(str(shared_path)))
        if path is None:
            local = Path(os.environ.get('LOCALAPPDATA') or
                         (Path.home() / '.local' / 'share'))
            # A redirected profile must not turn recovery into another SMB wait.
            if str(local).startswith(('\\\\', '//')):
                local = Path(tempfile.gettempdir())
            identity = hashlib.sha256(self.shared_path.encode('utf-8')).hexdigest()[:16]
            path = local / 'Jihunius' / 'pending' / ('protrusion-' + identity + '.json')
        self.path = Path(path)

    def load(self):
        try:
            state = json.loads(self.path.read_text(encoding='utf-8'))
        except FileNotFoundError:
            return {}
        if (not isinstance(state, dict) or state.get('version') != 1
                or state.get('shared_path') != self.shared_path
                or not isinstance(state.get('operations'), list)):
            raise ValueError('PC 복구본의 형식 또는 공유 저장 위치를 확인해 주세요.')
        pending = {}
        for sequence, operation in enumerate(state['operations'], 1):
            if (not isinstance(operation, dict)
                    or set(operation) != {'key', 'base', 'value'}
                    or not isinstance(operation['key'], str)
                    or operation['key'] in pending):
                raise ValueError('PC 복구본의 변경 항목을 확인해 주세요.')
            SharedStore._validate_value(operation['key'], operation['base'])
            SharedStore._validate_value(operation['key'], operation['value'])
            pending[operation['key']] = dict(operation, seq=sequence)
        return pending

    def save(self, pending):
        if not pending:
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass
            return
        operations = []
        for key, operation in pending.items():
            if operation['key'] != key:
                raise ValueError('PC 복구본의 변경 항목을 확인해 주세요.')
            SharedStore._validate_value(key, operation['base'])
            SharedStore._validate_value(key, operation['value'])
            operations.append({field: operation[field] for field in ('key', 'base', 'value')})
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix='.pending-', suffix='.tmp',
                                           dir=str(self.path.parent))
        temporary = Path(name)
        try:
            with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as stream:
                json.dump({'version': 1, 'shared_path': self.shared_path,
                           'operations': operations}, stream, ensure_ascii=False)
                stream.write('\n')
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


class DefectTable(tk.Frame):
    """제품명은 직접 입력, 호기별 칸은 클릭으로 O를 표시/초기화합니다."""

    LABEL_WIDTH = 105
    MACHINE_WIDTH = 64
    CELL_HEIGHT = 32
    LINE_COLOR = Theme.LINE
    BG_COLOR = Theme.CELL
    FOCUS_COLOR = Theme.FOCUS

    def __init__(self, master, machine_numbers, initial_marks):
        super().__init__(master, bg=self.LINE_COLOR, padx=1, pady=1)

        self.machine_vars = []
        self.product_vars = []
        self.data_vars = {}
        self.machine_boxes = []
        self.data_buttons = {}
        self.product_entries = []
        self.reset_buttons = []

        self.grid_columnconfigure(0, weight=2, minsize=self.LABEL_WIDTH)
        for column in range(1, len(machine_numbers) + 1):
            self.grid_columnconfigure(column, weight=1, minsize=self.MACHINE_WIDTH)
        for row in range(len(PRODUCTS) + 2):
            self.grid_rowconfigure(row, weight=1, minsize=28)

        self._cell(0, 0, self.LABEL_WIDTH, header=True, text="돌출량 현황표")

        for col, num in enumerate(machine_numbers, start=1):
            host = self._cell(0, col, self.MACHINE_WIDTH, header=True)
            var = tk.StringVar(master=self, value=machine_label(num))
            combo = ttk.Combobox(
                host,
                textvariable=var,
                values=MACHINE_OPTIONS,
                state="readonly",
                justify="center",
                width=8,
                font=("맑은 고딕", 10),
                cursor="hand2",
                style="Machine.TCombobox",
            )
            combo.pack(fill="both", expand=True, padx=2, pady=3)
            self.machine_vars.append(var)
            self.machine_boxes.append(combo)

        for row, product in enumerate(PRODUCTS, start=1):
            # 왼쪽의 '네오(35)' 이하 제품명도 직접 수정할 수 있습니다.
            label_host = self._cell(row, 0, self.LABEL_WIDTH)
            label_var = tk.StringVar(master=self, value=product)
            label_entry = self._entry(label_host, label_var, is_product=True)
            self.product_vars.append(label_var)
            self.product_entries.append(label_entry)

            for col in range(1, len(machine_numbers) + 1):
                cell_host = self._cell(row, col, self.MACHINE_WIDTH)
                initial_value = "O" if (row - 1, col - 1) in initial_marks else ""
                var = tk.StringVar(master=self, value=initial_value)
                mark_button = tk.Button(
                    cell_host,
                    textvariable=var,
                    command=lambda mark=var: self._toggle_mark(mark),
                    font=("맑은 고딕", 11, "bold"),
                    fg=Theme.ACCENT,
                    bg=cell_host.cget("bg"),
                    activeforeground=Theme.ACCENT,
                    activebackground=self.FOCUS_COLOR,
                    disabledforeground=Theme.DISABLED,
                    borderwidth=0,
                    relief="flat",
                    highlightthickness=0,
                    cursor="hand2",
                )
                # 버튼을 칸 전체에 채워 어느 부분을 눌러도 작동합니다.
                mark_button.pack(fill="both", expand=True)
                key = (row - 1, col - 1)
                self.data_vars[key] = var
                self.data_buttons[key] = mark_button

        # 각 호기 열의 맨 아래에 초기화 버튼을 한 개씩 배치합니다.
        # 왼쪽 제품명 열의 버튼은 만들지 않습니다.
        reset_row = len(PRODUCTS) + 1
        label_host = self._cell(reset_row, 0, self.LABEL_WIDTH)
        tk.Label(
            label_host,
            text="호기별 초기화",
            bg=label_host.cget("bg"),
            fg=Theme.MUTED,
            font=("맑은 고딕", 9),
        ).pack(fill="both", expand=True)

        for col in range(len(machine_numbers)):
            cell_host = self._cell(reset_row, col + 1, self.MACHINE_WIDTH)
            reset_button = tk.Button(
                cell_host,
                text="초기화",
                command=lambda index=col: self._reset_column(index),
                font=("맑은 고딕", 9, "bold"),
                fg=Theme.RESET_TEXT,
                bg=Theme.RESET_BG,
                activeforeground=Theme.TEXT,
                activebackground=Theme.RESET_HOVER,
                disabledforeground=Theme.DISABLED,
                borderwidth=0,
                relief="flat",
                highlightthickness=0,
                cursor="hand2",
            )
            reset_button.pack(fill="both", expand=True, padx=3, pady=3)
            self.reset_buttons.append(reset_button)

    def _reset_column(self, column_index):
        """선택한 호기의 표시를 지웁니다. 같은 호기의 다른 표시 칸에도 반영됩니다."""
        for row_index in range(len(PRODUCTS)):
            self.data_vars[(row_index, column_index)].set("")

    def set_editable(self, editable):
        for combo in self.machine_boxes:
            combo.configure(state="readonly" if editable else "disabled")
        for widget in self.product_entries + list(self.data_buttons.values()) + self.reset_buttons:
            widget.configure(state="normal" if editable else "disabled")

    @staticmethod
    def _toggle_mark(variable):
        """빈칸이면 O를, O가 있으면 빈칸을 표시합니다."""
        variable.set("" if variable.get() == "O" else "O")

    def _cell(self, row, col, width, header=False, text=None):
        background = (Theme.HEADER if header else Theme.PRODUCT if col == 0
                      else Theme.CELL if row % 2 else Theme.CELL_ALT)
        host = tk.Frame(
            self,
            bg=background,
            width=width,
            height=self.CELL_HEIGHT,
            borderwidth=0,
            highlightthickness=0,
        )
        host.grid(row=row, column=col, padx=(0, 1), pady=(0, 1), sticky="nsew")
        host.pack_propagate(False)

        if text is not None:
            tk.Label(
                host,
                text=text,
                bg=background,
                fg=Theme.ACCENT if header else Theme.TEXT,
                font=("맑은 고딕", 10, "bold"),
            ).pack(fill="both", expand=True)
        return host

    def _entry(self, parent, variable, is_product=False):
        background = parent.cget("bg")
        entry = tk.Entry(
            parent,
            textvariable=variable,
            justify="center",
            font=("맑은 고딕", 10),
            bg=background,
            fg=Theme.TEXT,
            disabledbackground=background,
            disabledforeground=Theme.MUTED,
            selectbackground=Theme.FOCUS,
            selectforeground=Theme.TEXT,
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            insertbackground=Theme.ACCENT,
        )
        entry.pack(fill="both", expand=True, padx=4, pady=3)
        entry.bind("<FocusIn>", lambda _e: entry.configure(bg=self.FOCUS_COLOR))
        entry.bind("<FocusOut>", lambda _e: entry.configure(bg=background))
        return entry

    def paint_mark(self, row, column):
        button = self.data_buttons[(row, column)]
        marked = self.data_vars[(row, column)].get() == "O"
        disabled = str(button.cget("state")) == "disabled"
        background = (Theme.EMPTY if disabled else Theme.MARK if marked
                      else Theme.CELL if (row + 1) % 2 else Theme.CELL_ALT)
        button.configure(bg=background,
                         activebackground=Theme.MARK_HOVER if marked else Theme.FOCUS)


class DefectApp:
    def __init__(self, root, store=None, recovery=None):
        self.root = root
        self.store = store if store is not None else SharedStore()
        self.stop = threading.Event()
        # Explicit test/custom stores remain injectable without spawning them.
        self._io = (SharedStoreClient(self.store.folder, stop=self.stop)
                    if type(self.store) is SharedStore else self.store)
        self.recovery = (recovery if recovery is not None
                         else PendingRecovery(self.store.path))
        self.server_values = default_values()
        self.pending = {}
        self.sequence = 0
        self.inflight_keys = set()
        self._update_sync_sequence = 0
        self._update_error_sequence = 0
        self.events = queue.Queue()
        self.ready = False
        self.busy = False
        self.applying = False
        self.closed = False
        self.closing = False
        self.sync_again = False
        self.resolving_conflicts = False
        self.last_error = ""
        self.last_synced = ""
        self.save_job = None
        self.draft_job = None
        self.draft_dirty = False
        self.local_error = ""
        self._recovery_load_error = ""
        self.field_vars = {}
        self.tables = {}
        self.timer_ids = set()
        try:
            self.pending = self.recovery.load()
            self.sequence = max((op['seq'] for op in self.pending.values()), default=0)
        except (OSError, ValueError) as error:
            self.local_error = self._recovery_load_error = str(error)
        self._build_ui()
        # Restore only local input; keep its recorded base for the first merge.
        self.applying = True
        try:
            for key, operation in self.pending.items():
                if key in self.field_vars:
                    self.field_vars[key].set(operation['value'])
                elif key == 'memo':
                    self.memo_text.delete('1.0', 'end')
                    self.memo_text.insert('1.0', operation['value'])
                    self.memo_text.edit_modified(False)
        finally:
            self.applying = False
        self._set_editable(False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._later(0, self._start_sync)
        self._later(100, self._poll_events)
        self._later(POLL_MS, self._periodic_sync)
        self._update_bridge = CompanionUpdateBridge(self.root, ProtrusionUpdateSave(self))
        self._window_state = CompanionWindowState(self.root, 'protrusion')

    def _later(self, delay, callback):
        if self.closed:
            return None
        holder = {}

        def run():
            self.timer_ids.discard(holder["id"])
            if not self.closed:
                callback()

        job = self.root.after(delay, run)
        holder["id"] = job
        self.timer_ids.add(job)
        return job

    def _cancel_timer(self, job):
        if job is not None:
            self.root.after_cancel(job)
            self.timer_ids.discard(job)

    def _set_table_icon(self):
        """외부 이미지 파일 없이 여러 크기의 표 모양 창 아이콘을 만듭니다."""
        self._window_icons = []
        for size in (16, 32, 48, 64):
            icon = tk.PhotoImage(master=self.root, width=size, height=size)

            def rectangle(color, x1, y1, x2, y2):
                bounds = tuple(round(value * size / 32) for value in (x1, y1, x2, y2))
                icon.put(color, to=bounds)

            rectangle("#1e4f7a", 2, 4, 30, 28)
            rectangle("#ffffff", 4, 6, 28, 26)
            rectangle("#377fbd", 4, 6, 28, 12)
            rectangle("#e4eff8", 4, 12, 12, 26)
            for x in (12, 20):
                rectangle("#8aa7be", x, 12, x + 2, 26)
            for y in (12, 16, 22):
                rectangle("#8aa7be", 4, y, 28, y + 2)
            self._window_icons.append(icon)
        self.root.iconphoto(True, *self._window_icons)

    def _setup_theme(self):
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.style.configure("Machine.TCombobox", background=Theme.HEADER,
                             fieldbackground=Theme.HEADER, foreground=Theme.TEXT,
                             arrowcolor=Theme.ACCENT, bordercolor=Theme.HEADER,
                             lightcolor=Theme.HEADER, darkcolor=Theme.HEADER,
                             selectbackground=Theme.HEADER, selectforeground=Theme.TEXT,
                             padding=(2, 2), arrowsize=12)
        self.style.map("Machine.TCombobox",
                       fieldbackground=[("disabled", Theme.SURFACE), ("readonly", Theme.HEADER)],
                       foreground=[("disabled", Theme.DISABLED), ("readonly", Theme.TEXT)],
                       selectbackground=[("readonly", Theme.HEADER)],
                       selectforeground=[("disabled", Theme.DISABLED), ("readonly", Theme.TEXT)],
                       background=[("active", Theme.FOCUS)],
                       bordercolor=[("focus", Theme.ACCENT), ("!focus", Theme.HEADER)])
        self.style.configure("ComboboxPopdownFrame", background=Theme.LINE,
                             bordercolor=Theme.LINE, lightcolor=Theme.LINE, darkcolor=Theme.LINE)
        for name in ("Vertical.TScrollbar", "App.Vertical.TScrollbar"):
            self.style.configure(name, background=Theme.LINE, troughcolor=Theme.BACKGROUND,
                                 bordercolor=Theme.BACKGROUND, lightcolor=Theme.LINE,
                                 darkcolor=Theme.LINE, arrowcolor=Theme.MUTED,
                                 arrowsize=12, width=12, relief="flat", borderwidth=0)
            self.style.map(name, background=[("pressed", Theme.DISABLED),
                                             ("active", Theme.DISABLED)])
        self.style.configure("App.TButton", background=Theme.PRODUCT,
                             foreground=Theme.TEXT, bordercolor=Theme.LINE,
                             lightcolor=Theme.PRODUCT, darkcolor=Theme.PRODUCT,
                             padding=(10, 5), font=("맑은 고딕", 9),
                             relief="flat", focusthickness=0)
        self.style.map("App.TButton", background=[("pressed", Theme.FOCUS),
                                                 ("active", Theme.HEADER)],
                       foreground=[("disabled", Theme.DISABLED)])
        self.style.configure("Reset.App.TButton", background=Theme.RESET_BG,
                             foreground=Theme.RESET_TEXT, bordercolor=Theme.RESET_BG,
                             lightcolor=Theme.RESET_BG, darkcolor=Theme.RESET_BG)
        self.style.map("Reset.App.TButton",
                       background=[("pressed", Theme.RESET_HOVER), ("active", Theme.RESET_HOVER)],
                       foreground=[("disabled", Theme.DISABLED), ("active", Theme.TEXT)])
        for option, value in (("background", Theme.SURFACE), ("foreground", Theme.TEXT),
                              ("selectBackground", Theme.FOCUS),
                              ("selectForeground", Theme.TEXT),
                              ("highlightThickness", 0), ("font", "{맑은 고딕} 10")):
            self.root.option_add("*TCombobox*Listbox." + option, value)

    def _dark_titlebar(self):
        if os.name != "nt":
            return
        try:
            from ctypes import wintypes
            user = ctypes.WinDLL("user32", use_last_error=True)
            user.GetAncestor.argtypes = (wintypes.HWND, wintypes.UINT)
            user.GetAncestor.restype = wintypes.HWND
            window = user.GetAncestor(self.root.winfo_id(), 2) or self.root.winfo_id()
            dwm = ctypes.WinDLL("dwmapi")
            dwm.DwmSetWindowAttribute.argtypes = (
                wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD)
            dwm.DwmSetWindowAttribute.restype = wintypes.LONG
            enabled = ctypes.c_int(1)
            for attribute in (20, 19):
                if dwm.DwmSetWindowAttribute(window, attribute, ctypes.byref(enabled),
                                             ctypes.sizeof(enabled)) == 0:
                    break
        except (AttributeError, OSError, tk.TclError):
            pass

    def _build_ui(self):
        root = self.root
        root.title("돌출량 현황표")
        self._set_table_icon()
        self._setup_theme()
        root.configure(bg=Theme.BACKGROUND)
        root.resizable(True, True)
        root.minsize(480, 500)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        viewport = tk.Frame(root, bg=Theme.BACKGROUND)
        viewport.grid(row=0, column=0, sticky="nsew")
        viewport.grid_rowconfigure(0, weight=1)
        viewport.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(viewport, bg=Theme.BACKGROUND, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        page_scroll = ttk.Scrollbar(viewport, orient="vertical", command=self.canvas.yview,
                                    style="App.Vertical.TScrollbar")
        page_scroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=page_scroll.set)
        self.content = tk.Frame(self.canvas, bg=Theme.BACKGROUND)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=2)
        self.content.grid_rowconfigure(1, weight=2)
        self.content.grid_rowconfigure(2, weight=1)
        self.content_window = self.canvas.create_window(0, 0, window=self.content, anchor="nw")
        self.canvas.bind("<Configure>", self._fit_content)
        self.content.bind("<Configure>", self._update_scrollregion)
        root.bind("<MouseWheel>", self._mousewheel, add="+")
        root.bind("<Button-4>", self._mousewheel, add="+")
        root.bind("<Button-5>", self._mousewheel, add="+")

        for index, (name, machines, marks) in enumerate(TABLE_LAYOUTS):
            table = DefectTable(self.content, machines, marks)
            table.grid(row=index, column=0, sticky="nsew", padx=12,
                       pady=(14 if index == 0 else 22, 0))
            self.tables[name] = table
            for column, variable in enumerate(table.machine_vars):
                self._track(f"{name}.machine.{column}", variable)
            for row, variable in enumerate(table.product_vars):
                self._track(f"{name}.product.{row}", variable)
            for (row, column), variable in table.data_vars.items():
                self._track_mark(name, row, column, variable)

        memo_section = tk.Frame(self.content, bg=Theme.BACKGROUND)
        memo_section.grid(row=2, column=0, sticky="nsew", padx=12, pady=(20, 14))
        memo_section.grid_columnconfigure(0, weight=1)
        memo_section.grid_rowconfigure(1, weight=1)
        tk.Label(memo_section, text="메모", anchor="w", bg=Theme.BACKGROUND, fg=Theme.MUTED,
                 font=("맑은 고딕", 11, "bold")).grid(row=0, column=0, sticky="ew", pady=(0, 8))
        memo_border = tk.Frame(memo_section, bg=Theme.SURFACE, highlightbackground=Theme.LINE,
                               highlightthickness=1)
        memo_border.grid(row=1, column=0, sticky="nsew")
        memo_scrollbar = ttk.Scrollbar(memo_border, orient="vertical", style="App.Vertical.TScrollbar")
        memo_scrollbar.pack(side="right", fill="y")
        self.memo_text = tk.Text(
            memo_border, height=6, width=35, wrap="word", undo=True,
            font=("맑은 고딕", 10), bg=Theme.SURFACE, fg=Theme.TEXT,
            selectbackground=Theme.FOCUS, selectforeground=Theme.TEXT,
            insertbackground=Theme.ACCENT, relief="flat", borderwidth=0, highlightthickness=0,
            padx=10, pady=10, yscrollcommand=memo_scrollbar.set,
        )
        self.memo_text.pack(side="left", fill="both", expand=True)
        memo_scrollbar.configure(command=self.memo_text.yview)
        self.memo_text.bind("<<Modified>>", self._memo_changed)

        status_bar = tk.Frame(root, bg=Theme.SURFACE)
        status_bar.grid(row=1, column=0, sticky="ew")
        status_bar.grid_columnconfigure(0, weight=1)
        self.status_var = tk.StringVar(master=root, value="공유폴더 연결 중…")
        self.status_label = tk.Label(
            status_bar, textvariable=self.status_var, anchor="w", bg=Theme.SURFACE,
            fg=Theme.WARNING, font=("맑은 고딕", 9), cursor="hand2",
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
        self.status_label.bind("<Button-1>", self._show_connection)
        self.refresh_button = ttk.Button(status_bar, text="새로고침", command=self._start_sync,
                                         style="App.TButton")
        self.refresh_button.grid(row=0, column=1, padx=(4, 6), pady=6)
        self.reset_all_button = ttk.Button(
            status_bar, text="전체초기화", command=self._reset_all_marks,
            style="Reset.App.TButton", state="disabled",
        )
        self.reset_all_button.grid(row=0, column=2, padx=(0, 12), pady=6)

        root.update_idletasks()
        width = min(500, max(480, root.winfo_screenwidth() - 80))
        height = min(940, max(500, root.winfo_screenheight() - 100))
        x = max(0, (root.winfo_screenwidth() - width) // 2)
        y = max(0, (root.winfo_screenheight() - height) // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        self._later(0, self._fit_content)
        self._later(0, self._dark_titlebar)

    def _fit_content(self, _event=None):
        if self.closed:
            return
        width = max(1, self.canvas.winfo_width())
        height = max(self.canvas.winfo_height(), self.content.winfo_reqheight())
        self.canvas.itemconfigure(self.content_window, width=width, height=height)
        self._update_scrollregion()

    def _update_scrollregion(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _mousewheel(self, event):
        if event.widget.winfo_class() in ("Text", "TCombobox", "Scrollbar", "TScrollbar"):
            return
        if getattr(event, "num", None) == 4:
            units = -3
        elif getattr(event, "num", None) == 5:
            units = 3
        else:
            units = -int(event.delta / 120) if abs(event.delta) >= 120 else (-1 if event.delta > 0 else 1)
        self.canvas.yview_scroll(units, "units")
        return "break"

    def _track(self, key, variable):
        self.field_vars[key] = variable

        def changed(*_args):
            self._changed(key, variable.get())
            if ".machine." in key and self.ready and not self.applying:
                self._refresh_marks()

        variable.trace_add("write", changed)

    def _mark_key_at(self, name, row, column):
        label = self.tables[name].machine_vars[column].get()
        number = MACHINE_NUMBERS.get(label)
        return machine_mark_key(number, row) if number is not None else None

    def _track_mark(self, name, row, column, variable):
        def changed(*_args):
            if self.applying or not self.ready or self.closed:
                return
            key = self._mark_key_at(name, row, column)
            if key is not None:
                # 편집한 순간의 호기를 기록하므로, 저장 전에 호기를 바꿔도 섞이지 않습니다.
                self._changed(key, variable.get() == "O")
            self._refresh_marks()

        variable.trace_add("write", changed)

    def _refresh_marks(self):
        applying = self.applying
        self.applying = True
        try:
            for name, table in self.tables.items():
                for (row, column), variable in table.data_vars.items():
                    key = self._mark_key_at(name, row, column)
                    value = (self.pending[key]["value"] if key in self.pending
                             else self.server_values[key]) if key is not None else False
                    text = "O" if value else ""
                    if variable.get() != text:
                        variable.set(text)
                    table.data_buttons[(row, column)].configure(
                        state="normal" if self.ready and key is not None else "disabled"
                    )
                    table.paint_mark(row, column)
                for column, button in enumerate(table.reset_buttons):
                    key = self._mark_key_at(name, 0, column)
                    button.configure(state="normal" if self.ready and key is not None else "disabled")
        finally:
            self.applying = applying

    def _memo_changed(self, _event=None):
        if self.memo_text.edit_modified():
            self.memo_text.edit_modified(False)
            self._changed("memo", self.memo_text.get("1.0", "end-1c"))

    def _changed(self, key, value):
        if self.applying or not self.ready or self.closed:
            return
        self.sequence += 1
        if key not in self.inflight_keys and value == self.server_values[key]:
            self.pending.pop(key, None)
        else:
            base = self.pending[key]["base"] if key in self.pending else self.server_values[key]
            self.pending[key] = {"seq": self.sequence, "key": key, "base": base, "value": value}
        self.draft_dirty = True
        if self.draft_job is not None:
            self._cancel_timer(self.draft_job)
        self.draft_job = self._later(SAVE_DELAY_MS, self._flush_pending)
        self._update_status()
        if self.save_job is not None:
            self._cancel_timer(self.save_job)
        self.save_job = self._later(SAVE_DELAY_MS, self._save_now)

    def _flush_pending(self):
        """Flush at debounce, before network requests, and before any exit."""
        if self.draft_job is not None:
            self._cancel_timer(self.draft_job)
            self.draft_job = None
        if self._recovery_load_error:
            # Do not silently replace an unreadable recovery file with defaults.
            return False
        if not self.draft_dirty:
            return not self.local_error
        try:
            self.recovery.save(self.pending)
        except (OSError, ValueError) as error:
            self.local_error = str(error)
            self._update_status()
            return False
        self.local_error = ""
        self.draft_dirty = False
        self._update_status()
        return True

    def _save_now(self):
        self.save_job = None
        self._start_sync()

    def _reset_all_marks(self):
        if not self.ready or self.closed or self.closing:
            return
        if not messagebox.askokcancel(
            "전체초기화 확인",
            "1~10호기의 O 표시를 모두 지울까요?\n\n"
            "제품명, 호기 선택, 메모는 유지됩니다.\n"
            "초기화 내용은 다른 PC에도 공유됩니다.",
            parent=self.root, icon="warning", default="cancel",
        ):
            return
        if self.closed or self.closing:
            return
        # 현재 표에서 선택하지 않은 호기도 포함해 호기별 원본 표시를 지웁니다.
        for number in MACHINE_NUMBERS.values():
            for row in range(len(PRODUCTS)):
                self._changed(machine_mark_key(number, row), False)
        self._refresh_marks()
        self._start_sync()

    def _set_editable(self, editable):
        for table in self.tables.values():
            table.set_editable(editable)
        self.memo_text.configure(state="normal" if editable else "disabled")
        self._refresh_marks()

    def _apply_values(self):
        self.applying = True
        try:
            for key, variable in self.field_vars.items():
                if key in self.pending:
                    continue
                value = self.server_values[key]
                if variable.get() != value:
                    variable.set(value)
            if "memo" not in self.pending:
                value = self.server_values["memo"]
                if self.memo_text.get("1.0", "end-1c") != value:
                    self.memo_text.configure(state="normal")
                    self.memo_text.delete("1.0", "end")
                    self.memo_text.insert("1.0", value)
                    self.memo_text.edit_reset()
                    self.memo_text.edit_modified(False)
                    self.memo_text.configure(state="normal" if self.ready else "disabled")
        finally:
            self.applying = False
        self._refresh_marks()

    def _start_sync(self):
        if self.closed:
            return
        # The update-save bridge calls this even when an older save is running.
        self._flush_pending()
        if self.busy or self.resolving_conflicts:
            self.sync_again = True
            return
        if self.save_job is not None:
            self._cancel_timer(self.save_job)
            self.save_job = None
        operations = [dict(operation) for operation in self.pending.values()]
        self.inflight_keys = {operation["key"] for operation in operations}
        self.busy = True
        self.sync_again = False
        self._update_status()

        def work():
            try:
                result = self._io.sync(operations)
                self.events.put((True, operations, result))
            except Exception as error:
                self.events.put((False, operations, str(error)))

        threading.Thread(target=work, daemon=True).start()

    def _periodic_sync(self):
        if not self.closed:
            if not getattr(getattr(self, '_update_bridge', None), 'active', False):
                self._start_sync()
            self._later(POLL_MS, self._periodic_sync)

    def _poll_events(self):
        if self.closed:
            return
        try:
            while True:
                ok, operations, result = self.events.get_nowait()
                self.busy = False
                self.inflight_keys = set()
                if ok:
                    self._sync_succeeded(operations, result)
                else:
                    self._sync_failed(result)
                if self.closed:
                    return
        except queue.Empty:
            pass
        self._later(100, self._poll_events)

    def _sync_succeeded(self, operations, result):
        self._update_sync_sequence += 1
        self.server_values = dict(result["state"]["values"])
        self.last_error = ""
        self.last_synced = datetime.now().strftime("%H:%M:%S")
        if not self.ready:
            self.ready = True
            self._set_editable(True)
        conflicts = []
        for sent in operations:
            key = sent["key"]
            current = self.pending.get(key)
            if current is None:
                continue
            if key in result["conflicts"]:
                if current["value"] == self.server_values[key]:
                    self.pending.pop(key, None)
                else:
                    conflicts.append(key)
            elif current["seq"] == sent["seq"]:
                self.pending.pop(key, None)
            else:
                # 저장 중에 계속 입력한 값은 지우지 않고 다음 저장에 이어갑니다.
                current["base"] = self.server_values[key]
        self._apply_values()
        if conflicts:
            self._resolve_conflicts(conflicts)
        if operations:
            self.draft_dirty = True
        self._flush_pending()
        self._update_status()
        if self.closing and not self.pending:
            self._destroy()
        elif self.pending or self.sync_again:
            self._later(0, self._start_sync)

    @staticmethod
    def _field_name(key):
        if key == "memo":
            return "메모"
        parts = key.split(".")
        if parts[0] == "machine":
            return f"{parts[1]}호기 {int(parts[3]) + 1}번째 제품 표시"
        table = "위쪽 표" if parts[0] == "upper" else "아래쪽 표"
        if parts[1] == "machine":
            return f"{table} {int(parts[2]) + 1}번째 호기 선택"
        if parts[1] == "product":
            return f"{table} {int(parts[2]) + 1}번째 제품명"
        return f"{table} {int(parts[2]) + 1}행 {int(parts[3]) + 1}열 표시"

    def _resolve_conflicts(self, keys):
        details = []
        for key in keys[:6]:
            local = str(self.pending[key]["value"])
            remote = str(self.server_values[key])
            details.append(self._field_name(key) + "\n공유 값: " + remote[:100]
                           + "\n내 수정: " + local[:100])
        if len(keys) > 6:
            details.append(f"외 {len(keys) - 6}개 항목")
        self.resolving_conflicts = True
        try:
            use_local = messagebox.askyesno(
                "동시 수정 확인",
                "다른 PC에서도 같은 항목을 수정했습니다.\n\n" + "\n\n".join(details)
                + "\n\n내 수정 내용으로 저장할까요?\n예: 내 수정 저장 / 아니요: 공유 값 사용",
                parent=self.root, default="no",
            )
        finally:
            self.resolving_conflicts = False
        for key in keys:
            if use_local:
                self.sequence += 1
                self.pending[key]["seq"] = self.sequence
                self.pending[key]["base"] = self.server_values[key]
            else:
                self.pending.pop(key, None)
        self._apply_values()

    def _sync_failed(self, error):
        _diagnostic_error(error, "공유 저장/연결")
        self._update_error_sequence += 1
        self.last_error = error
        self.sync_again = False
        self._update_status()
        if self.closing:
            self.closing = False
            preserved = self._flush_pending()
            if messagebox.askyesno(
                "저장하지 못한 변경 사항",
                "공유폴더에 저장하지 못했습니다.\n" + error
                + ("\n\n미저장 내용은 이 PC에 보관했으며 다음 실행에서 다시 확인합니다. 종료할까요?"
                   if preserved else "\n\nPC 복구본도 저장하지 못했습니다. 창을 유지하고 저장 위치를 확인해 주세요."),
                parent=self.root, default="no",
            ) and preserved:
                self._destroy()

    def _update_status(self):
        if self.local_error:
            text, color = "PC 복구본 저장 실패 · 상태를 눌러 확인해 주세요", Theme.ERROR
        elif self.last_error:
            text = "공유 연결 실패 · " + (f"미저장 {len(self.pending)}건" if self.pending else "다시 연결해 주세요")
            if self.pending and not self.draft_dirty:
                text += " · PC 보관됨"
            color = Theme.ERROR
        elif self.closing:
            text, color = "변경 사항 저장 후 종료 중…", Theme.WARNING
        elif not self.ready:
            text, color = "공유폴더 연결 중…", Theme.WARNING
        elif self.pending:
            text = ("공유 저장 중" if self.busy else "저장 대기") + f" · {len(self.pending)}건"
            color = Theme.WARNING
        else:
            text, color = "PC 간 공유 · 자동 저장 · " + self.last_synced, Theme.SUCCESS
        self.status_var.set(text)
        self.status_label.configure(fg=color)
        self.refresh_button.configure(text="다시 연결" if self.last_error else "새로고침")
        self.reset_all_button.configure(state="normal" if self.ready and not self.closing else "disabled")

    def _show_connection(self, _event=None):
        if self.local_error:
            messagebox.showwarning(
                "PC 복구본 상태", "복구본 위치: " + str(self.recovery.path)
                + "\n\n" + self.local_error + "\n\n공유 저장 여부와 PC 저장 공간·권한을 확인해 주세요.",
                parent=self.root,
            )
        elif self.last_error:
            messagebox.showwarning(
                "공유 연결 상태", "저장 위치: " + str(self.store.path) + "\n\n" + self.last_error
                + "\n\n공유폴더 연결과 읽기·쓰기 권한을 확인해 주세요.\n"
                "미저장 내용은 이 PC의 복구본에 보관하며, 연결되면 저장 여부와 충돌을 확인합니다.",
                parent=self.root,
            )
        else:
            messagebox.showinfo("공유 저장 위치", str(self.store.path), parent=self.root)

    def _on_close(self):
        if getattr(getattr(self, '_update_bridge', None), 'active', False):
            self._update_bridge.fail('업데이트를 취소했습니다. 돌출량표를 계속 사용할 수 있습니다.')
            return
        # 종료 버튼 직전의 마지막 메모 입력도 저장 목록에 반영합니다.
        if self.ready:
            self._memo_changed()
        if not self._flush_pending() and self.pending:
            self._show_connection()
            return
        if not self.pending:
            self._destroy()
            return
        if self.closing:
            if messagebox.askyesno(
                "저장 대기 중", "아직 저장하지 못한 변경 사항이 있습니다.\n"
                "미저장 내용은 이 PC에 보관했으며 다음 실행에서 다시 확인합니다. 종료할까요?",
                parent=self.root, default="no",
            ):
                self._destroy()
            return
        self.closing = True
        self._start_sync()
        self._update_status()

    def _destroy(self):
        if self.closed:
            return
        if not self._flush_pending() and self.pending:
            self.closing = False
            self._show_connection()
            return
        self.closed = True
        self.stop.set()
        if isinstance(self._io, SharedStoreClient):
            self._io.close()
        for job in list(self.timer_ids):
            self._cancel_timer(job)
        self.save_job = None
        self.draft_job = None
        self.root.destroy()


def main():
    if os.name == "nt":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Jihunius.RollDefectTable")
        except (AttributeError, OSError):
            pass
    root = tk.Tk()
    DefectApp(root)
    root.mainloop()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
