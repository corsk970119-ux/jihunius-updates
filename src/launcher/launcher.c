/* 지후니우스.exe — 아이콘 하나짜리 실행 파일(사용자 요청 2026-11-25).

   하는 일은 세 가지뿐입니다.
   1) 안에 넣어 둔 지후니우스.pyw 를 %LOCALAPPDATA%\Jihunius\app 에 풉니다.
      그 자리에 파일이 없거나, 버전을 읽을 수 없거나, 안에 든 것이 더 새 버전일 때만 씁니다.
   2) 지후니우스 창이 이미 떠 있으면 그 창을 앞으로 가져오고 끝냅니다.
   3) 아니면 푼 .pyw 를 탐색기에서 더블클릭한 것과 같은 방식(연결 프로그램 '열기')으로 실행합니다.

   그 뒤의 일(업데이트 확인·적용, 중복 실행 방지, 보조창)은 전부 .pyw 가 예전 그대로 합니다.
   업데이트가 남기는 파일도 .pyw 옆, 곧 %LOCALAPPDATA%\Jihunius\app 안에 생깁니다.
   PC 에 Python 이 설치되어 있어야 하는 것은 .pyw 를 직접 실행할 때와 같습니다.

   만들기: python tools/build_launcher.py  (mingw-w64 필요) */
#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <shlobj.h>
#include <stdio.h>
#include <string.h>

#define TITLE L"지후니우스"
#define PROGRAM_NAME L"지후니우스.pyw"
#define WINDOW_CLASS L"TkTopLevel"
#define MAX_PROGRAM (16u * 1024u * 1024u)
#define PATH_CAP 1024
#define VERSION_PARTS 8

static void fail(const wchar_t *text) {
    MessageBoxW(NULL, text, TITLE, MB_OK | MB_ICONERROR | MB_SETFOREGROUND);
}

/* 줄 맨 앞의 SUITE_APP_VERSION = '2026.11.25.1' 을 숫자 묶음으로 읽습니다. 못 읽으면 0. */
static int read_version(const unsigned char *data, DWORD size, unsigned parts[VERSION_PARTS]) {
    static const char key[] = "SUITE_APP_VERSION = '";
    const DWORD length = (DWORD)(sizeof(key) - 1);
    DWORD start, at;
    int count = 0, digits = 0, index;
    unsigned value = 0;
    for (index = 0; index < VERSION_PARTS; index++) parts[index] = 0;
    if (size <= length) return 0;
    for (start = 0; start + length < size; start++) {
        if ((start == 0 || data[start - 1] == '\n') && memcmp(data + start, key, length) == 0) break;
    }
    if (start + length >= size) return 0;
    for (at = start + length; at < size; at++) {
        unsigned char c = data[at];
        if (c >= '0' && c <= '9') {
            if (digits >= 9) return 0;
            value = value * 10u + (unsigned)(c - '0');
            digits++;
        } else if (c == '.' || c == '\'') {
            if (!digits || count >= VERSION_PARTS) return 0;
            parts[count++] = value;
            value = 0;
            digits = 0;
            if (c == '\'') return count;
        } else {
            return 0;
        }
    }
    return 0;
}

static BOOL newer(const unsigned left[VERSION_PARTS], const unsigned right[VERSION_PARTS]) {
    int index;
    for (index = 0; index < VERSION_PARTS; index++) {
        if (left[index] != right[index]) return left[index] > right[index];
    }
    return FALSE;
}

/* 1: 읽음, 0: 파일 없음, -1: 있는데 읽지 못함(이때는 건드리지 않습니다). */
static int read_program(const wchar_t *path, unsigned char **data, DWORD *size) {
    HANDLE file = CreateFileW(path, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                              NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    LARGE_INTEGER length;
    DWORD done = 0, step = 0;
    unsigned char *buffer;
    if (file == INVALID_HANDLE_VALUE) {
        DWORD error = GetLastError();
        return (error == ERROR_FILE_NOT_FOUND || error == ERROR_PATH_NOT_FOUND) ? 0 : -1;
    }
    if (!GetFileSizeEx(file, &length) || length.QuadPart > (LONGLONG)MAX_PROGRAM) {
        CloseHandle(file);
        return -1;
    }
    buffer = (unsigned char *)HeapAlloc(GetProcessHeap(), 0, (SIZE_T)length.QuadPart + 1);
    if (buffer == NULL) {
        CloseHandle(file);
        return -1;
    }
    while (done < (DWORD)length.QuadPart) {
        if (!ReadFile(file, buffer + done, (DWORD)length.QuadPart - done, &step, NULL) || step == 0) {
            HeapFree(GetProcessHeap(), 0, buffer);
            CloseHandle(file);
            return -1;
        }
        done += step;
    }
    CloseHandle(file);
    *data = buffer;
    *size = done;
    return 1;
}

/* 임시 파일에 다 쓴 뒤 이름을 바꿉니다(쓰다 만 파일이 실행 파일 자리에 놓이지 않게). */
static BOOL write_program(const wchar_t *target, const wchar_t *temporary, const unsigned char *data, DWORD size) {
    HANDLE file = CreateFileW(temporary, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    DWORD done = 0, step = 0;
    BOOL written = TRUE;
    if (file == INVALID_HANDLE_VALUE) return FALSE;
    while (written && done < size) {
        written = WriteFile(file, data + done, size - done, &step, NULL) && step != 0;
        done += step;
    }
    if (written) written = FlushFileBuffers(file);
    CloseHandle(file);
    if (written) written = MoveFileExW(temporary, target, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH);
    if (!written) DeleteFileW(temporary);
    return written;
}

static BOOL directory(const wchar_t *path) {
    DWORD attributes;
    if (CreateDirectoryW(path, NULL)) return TRUE;
    attributes = GetFileAttributesW(path);
    return attributes != INVALID_FILE_ATTRIBUTES && (attributes & FILE_ATTRIBUTE_DIRECTORY);
}

/* %LOCALAPPDATA%\Jihunius\app — .pyw 가 설정을 두는 %LOCALAPPDATA% 와 같은 값을 씁니다. */
static BOOL program_folder(wchar_t *folder) {
    wchar_t base[MAX_PATH];
    DWORD length = GetEnvironmentVariableW(L"LOCALAPPDATA", base, MAX_PATH);
    if (length == 0 || length >= MAX_PATH) {
        if (FAILED(SHGetFolderPathW(NULL, CSIDL_LOCAL_APPDATA, NULL, SHGFP_TYPE_CURRENT, base))) return FALSE;
    }
    length = (DWORD)lstrlenW(base);
    if (length == 0 || length > 200) return FALSE;
    if (base[length - 1] == L'\\') base[length - 1] = 0;
    _snwprintf(folder, PATH_CAP, L"%ls\\Jihunius", base);
    folder[PATH_CAP - 1] = 0;
    if (!directory(folder)) return FALSE;
    _snwprintf(folder, PATH_CAP, L"%ls\\Jihunius\\app", base);
    folder[PATH_CAP - 1] = 0;
    return directory(folder);
}

/* 이미 떠 있는(트레이로 내려가 있는 것 포함) 지후니우스 창을 앞으로. .pyw 의 중복 실행 처리와 같은 동작입니다. */
static BOOL show_running(void) {
    HWND window = FindWindowW(WINDOW_CLASS, TITLE);
    if (window == NULL) return FALSE;
    ShowWindow(window, SW_RESTORE);
    SetForegroundWindow(window);
    return TRUE;
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous, PWSTR arguments, int show) {
    wchar_t folder[PATH_CAP], target[PATH_CAP], temporary[PATH_CAP];
    unsigned carried[VERSION_PARTS], installed[VERSION_PARTS];
    unsigned char *existing = NULL;
    const unsigned char *payload;
    DWORD payload_size, existing_size = 0;
    HRSRC found;
    HGLOBAL loaded;
    SHELLEXECUTEINFOW run;
    BOOL replace = FALSE;
    int state;
    (void)previous;
    (void)show;

    found = FindResourceW(instance, MAKEINTRESOURCEW(1), (LPCWSTR)RT_RCDATA);
    loaded = found ? LoadResource(instance, found) : NULL;
    payload = loaded ? (const unsigned char *)LockResource(loaded) : NULL;
    payload_size = found ? SizeofResource(instance, found) : 0;
    if (payload == NULL || payload_size == 0 || !read_version(payload, payload_size, carried)) {
        fail(L"실행 파일이 손상되었습니다. 지후니우스.exe 를 다시 받아 주세요.");
        return 1;
    }
    if (!program_folder(folder)) {
        fail(L"프로그램을 둘 폴더를 만들지 못했습니다.\n%LOCALAPPDATA%\\Jihunius 폴더의 권한과 저장 공간을 확인해 주세요.");
        return 1;
    }
    _snwprintf(target, PATH_CAP, L"%ls\\%ls", folder, PROGRAM_NAME);
    target[PATH_CAP - 1] = 0;
    _snwprintf(temporary, PATH_CAP, L"%ls\\%ls.launcher.tmp", folder, PROGRAM_NAME);
    temporary[PATH_CAP - 1] = 0;

    state = read_program(target, &existing, &existing_size);
    if (state == 0) {
        replace = TRUE;
    } else if (state == 1) {
        replace = !read_version(existing, existing_size, installed) || newer(carried, installed);
        HeapFree(GetProcessHeap(), 0, existing);
    }
    if (replace && !write_program(target, temporary, payload, payload_size)
            && GetFileAttributesW(target) == INVALID_FILE_ATTRIBUTES) {
        fail(L"프로그램 파일을 준비하지 못했습니다.\n%LOCALAPPDATA%\\Jihunius\\app 폴더의 권한과 저장 공간을 확인해 주세요.");
        return 1;
    }

    if (show_running()) return 0;

    ZeroMemory(&run, sizeof(run));
    run.cbSize = sizeof(run);
    run.fMask = SEE_MASK_FLAG_NO_UI | SEE_MASK_NOASYNC;
    run.lpVerb = L"open";
    run.lpFile = target;
    run.lpParameters = (arguments != NULL && arguments[0] != 0) ? arguments : NULL;
    run.lpDirectory = folder;
    run.nShow = SW_SHOWNORMAL;
    if (!ShellExecuteExW(&run)) {
        fail(L"지후니우스를 시작하지 못했습니다.\n"
             L"이 PC 에 Python(3.8 이상)이 설치되어 있고 .pyw 파일이 Python 으로 열리는지 확인해 주세요.");
        return 1;
    }
    return 0;
}
