# 수정10.30 — 기존 수정9.7 규칙 + 시작 구간 G4U2.0 자동 추가 (모든 호기 공통)
import os
import re
import ctypes

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

folder_path = os.path.dirname(os.path.abspath(__file__))

pi_value_map_a12 = {
    "9.7": "-1.0", "9.8": "-1.0", "9.9": "-1.0", "10.0": "-1.0",
    "10.1": "-1.0", "10.2": "-1.0", "10.3": "-1.0", "10.4": "-1.0",
    "10.5": "-1.0", "10.6": "-1.0", "10.7": "-1.0", "10.8": "-1.0",
    "10.9": "-0.9", "11.0": "-0.8", "11.1": "-0.7", "11.2": "-0.6",
    "11.3": "-0.5", "11.4": "-0.4", "11.5": "-0.3", "11.6": "-0.3",
    "11.7": "-0.3"
}

pi_value_map_a14 = {
    "11.8": "-1.0", "11.9": "-1.0", "12.0": "-1.0", "12.1": "-1.0",
    "12.2": "-1.0", "12.3": "-1.0", "12.4": "-1.0", "12.5": "-1.0",
    "12.6": "-1.0", "12.7": "-1.0", "12.8": "-1.0",
    "12.9": "-0.9", "13.0": "-0.8", "13.1": "-0.7", "13.2": "-0.6",
    "13.3": "-0.5", "13.4": "-0.4", "13.5": "-0.3", "13.6": "-0.3",
    "13.7": "-0.3"
}

alarm_log = []
g4_summary = {}

for filename in os.listdir(folder_path):
    # 기존 NC 파일과 지후니우스가 저장한 확장자 없는 O번호 파일을 처리합니다.
    if (os.path.isfile(os.path.join(folder_path, filename))
            and (filename.lower().endswith(".nc")
                 or (not os.path.splitext(filename)[1]
                     and re.fullmatch(r"O[0-9]{4}(?:[^0-9].*)?", filename, re.I)))):
        file_path = os.path.join(folder_path, filename)

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()

        # --- 추가된 부분: 파일 내부의 A9.7을 A10으로 가장 먼저 변경 ---
        content = content.replace("A9.7", "A10.")
        # ---------------------------------------------------------

        content = re.sub(r'X-(1[5-9])(?:\.(\d{1,3}))?', lambda m: f"X-14" + (f".{m.group(2)}" if m.group(2) else ""), content)
        content = re.sub(r'X-14\.[5-9](\d{0,2})', lambda m: f"X-14.4{m.group(1)}", content)
        content = re.sub(r'Y(2[0-5])(?:\.(\d{1,3}))?', lambda m: f"Y19" + (f".{m.group(2)}" if m.group(2) else ""), content)
        content = re.sub(r'Y19\.9(\d{0,2})', lambda m: f"Y19.8{m.group(1)}", content)
        content = re.sub(r'Y-(2[0-5])(?:\.(\d{1,3}))?', lambda m: f"Y-19" + (f".{m.group(2)}" if m.group(2) else ""), content)
        content = re.sub(r'Y-19\.9(\d{0,2})', lambda m: f"Y-19.8{m.group(1)}", content)

        def fix_x_decimal(match):
            return f"X-14.4{match.group(1)}"
        content = re.sub(r'X-14\.[5-9](\d{2})', fix_x_decimal, content)

        pi_match = re.search(r'(\d{1,2}\.\d)', filename)
        pi_value = pi_match.group(1) if pi_match else None
        
        has_pi_a12 = pi_value in pi_value_map_a12
        has_pi_a14 = pi_value in pi_value_map_a14

        if has_pi_a12 and "A12" in content:
            content = re.sub(
                r'X\[#531-(\-?\d+\.\d+)\]F0\.02',
                lambda m: f"X[#531{pi_value_map_a12[pi_value]}]F0.02",
                content
            )
            
        if has_pi_a14 and "A14" in content:
            content = re.sub(
                r'X\[#531-(\-?\d+\.\d+)\]F0\.02',
                lambda m: f"X[#531{pi_value_map_a14[pi_value]}]F0.02",
                content
            )

        # 앞에서 A9.7이 A10으로 변경되었으므로, 이 알람 조건도 정상적으로 검사됩니다.
        if has_pi_a12 and "A10" in content:
            alarm_log.append(f"{filename} → 제목과 파이가 다름 확인필요 (내부에 A10 있음)")
            
        if has_pi_a12 and "A12" not in content:
            alarm_log.append(f"{filename} → 제목과 파이가 다름 확인필요 (제목에 A12 파이 있음, 내부에 A12 없음)")
            
        if "A12" in content and not has_pi_a12:
            alarm_log.append(f"{filename} → 제목과 파이가 다름 확인필요 (내부에 A12 있음, 제목에 A12 파이 없음)")

        if has_pi_a14 and "A14" not in content:
            alarm_log.append(f"{filename} → 제목과 파이가 다름 확인필요 (제목에 A14 파이 있음, 내부에 A14 없음)")
            
        if "A14" in content and not has_pi_a14:
            alarm_log.append(f"{filename} → 제목과 파이가 다름 확인필요 (내부에 A14 있음, 제목에 A14 파이 없음)")

        converted, g4_status, g4_detail = add_g4u2(content.encode('utf-8'))
        content = converted.decode('utf-8')
        g4_summary[g4_status] = g4_summary.get(g4_status, 0) + 1
        if g4_status == '확인 필요' or '확인 필요' in g4_detail:
            alarm_log.append(f"{filename} → G4U2.0 추가 확인 필요: {g4_detail}")

        new_filename = filename[:5]
        new_file_path = os.path.join(folder_path, new_filename)

        with open(new_file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        if new_filename != filename:
            os.remove(file_path)

print("G4U2.0: " + (" / ".join(f"{status} {count}개" for status, count in g4_summary.items()) or "처리 대상 없음"))

if alarm_log:
    message = "\n".join(alarm_log)
    ctypes.windll.user32.MessageBoxW(0, message, "⚠ 알람 발생", 0)
    print("\n[⚠️ 알람 발생 파일 목록]\n")
    for alarm in alarm_log:
        print(alarm)
else:
    print("\n✅ 알람 없이 모든 작업 완료됨.")