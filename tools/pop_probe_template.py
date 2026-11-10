"""POP 점검 — 읽기 전용.

지후니우스 세척완료가 POP 목록을 읽는 세 가지 방식(행 요약 / 보이는 행만 칸까지 / 전체 칸)을
현장 POP에서 실제로 읽어 보고, 걸린 시간과 서로 일치하는지만 글로 정리합니다.
클릭·키 입력·스크롤·저장은 하지 않습니다. 결과에는 프로젝트 번호·이름 같은 실제 값을 넣지 않습니다.

이 파일은 tools/build_pop_probe.py가 만든 결과물로 실행합니다(아래 두 값이 빌드 때 채워짐).
"""
import os
import queue
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

PROBE_VERSION = '2'
APP_VERSION = ...  # build: 지후니우스 버전
WASH_POP_SOURCE = ...  # build: src/host/wash_pop.py
WASH_READER_SOURCE = ...  # build: src/host/jihunius_main.py 의 WashReader

NORMAL_LIMIT = 'count>=40000 || clock.Elapsed.TotalSeconds>=80'
EXTENDED_LIMIT = 'count>=400000 || clock.Elapsed.TotalSeconds>=420'
EXTENDED_WAIT = 450


def load_pop():
    scope = {'__name__': 'pop_probe_wash_pop'}
    exec(compile(WASH_POP_SOURCE, 'wash_pop.py', 'exec'), scope)
    return scope


def mask(text, limit=160):
    """실제 값 대신 모양만: 숫자→9, 한글→가, 영문→a. 구분 기호는 그대로."""
    out = []
    for ch in str(text)[:limit]:
        if ch.isdigit(): out.append('9')
        elif '가' <= ch <= '힣': out.append('가')
        elif ch.isalpha(): out.append('a')
        else: out.append(ch)
    return ''.join(out) + (' …' if len(str(text)) > limit else '')


def finish_stats(report):
    done = [r for r in (report or {}).get('records', []) if r.get('kind') == 'finish']
    return done[-1] if done else {}


def row_shown(P, row):
    b = P['bounds'](row)
    return not row.get('offscreen') and b[2] > 0 and b[3] > 0


def summary_problem(P, row):
    value = row.get('value')
    if not isinstance(value, str) or not value: return '요약값 없음'
    if '[truncated]' in value: return '요약값 잘림'
    if not value.endswith(';'): return "끝에 ';' 없음"
    parts = len(value[:-1].split(';'))
    if parts != row.get('child_count'): return '칸 수 불일치(요약 {} / 칸 {})'.format(parts, row.get('child_count'))
    return ''


def step(lines, title):
    lines.append(''); lines.append('[' + title + ']')


def explain(error):
    return '{}: {}'.format(type(error).__name__, str(error)[:300])


def analyze(P, read, target, full=True, log=lambda text: None):
    """read(mode, label, extended) → (report 또는 None, 초, 오류 문구). 결과 글 줄 목록을 돌려줍니다."""
    lines = []
    stop = SimpleNamespace(is_set=lambda: False, wait=lambda seconds: False)
    quiet = lambda *args, **kwargs: None
    original_validate = P['validate_conditions']
    P['validate_conditions'] = lambda *args, **kwargs: {}
    verdict = {'summary': None, 'fast_view': None, 'equal': None, 'stable': None}
    row_count = None
    try:
        # 1) 행 요약만 읽기 ----------------------------------------------------
        step(lines, '1. 행 요약만 읽기(mes_rows)'); log('1/4 행 요약 읽는 중…')
        first, seconds, error = read('mes_rows', '점검: 행 요약', False)
        lines.append('걸린 시간 {:.1f}초 · 읽은 항목 {}개{}'.format(
            seconds, finish_stats(first).get('elements', '?'), ' · 오류: ' + error if error else ''))
        base_summaries = None
        if first is not None:
            try:
                table, headers, rows, children = P['pop_grid'](first)
                shown = [r for r in rows if row_shown(P, r)]
                names = [h.get('name', '') for h in headers if P['bounds'](h)[2] > 0]
                problems = {}
                for row in rows:
                    reason = summary_problem(P, row)
                    if reason: problems[reason] = problems.get(reason, 0) + 1
                base_summaries = [r.get('value') for r in rows]
                row_count = len(rows)
                widths = sorted({r.get('child_count') for r in rows})
                lines.append('목록 {}줄 · 화면에 보이는 줄 {} · 한 줄의 칸 수 {}'.format(len(rows), len(shown), widths))
                lines.append('보이는 열 제목({}개): {}'.format(len(names), ', '.join(names)))
                lines.append('요약값 형식이 맞는 줄 {}/{}'.format(len(rows) - sum(problems.values()), len(rows)))
                for reason, count in sorted(problems.items()):
                    lines.append('  - {}: {}줄'.format(reason, count))
                if rows:
                    lines.append('첫 줄 요약값 모양(값은 가림): ' + mask(rows[0].get('value') or ''))
                # 줄이 없으면 요약값을 주는지 알 수 없습니다(아니오가 아니라 '확인 못함').
                verdict['summary'] = (not problems) if rows else None
            except Exception as failure:
                lines.append('표 확인 실패 — ' + explain(failure))

        # 2) 보이는 줄만 칸까지 읽기(새 방식) ----------------------------------
        step(lines, '2. 보이는 줄만 칸까지 읽기(pop_fast, 새 방식)'); log('2/4 보이는 줄 읽는 중…')
        fast, seconds, error = read('pop_fast', '점검: 보이는 줄', False)
        lines.append('걸린 시간 {:.1f}초 · 읽은 항목 {}개{}'.format(
            seconds, finish_stats(fast).get('elements', '?'), ' · 오류: ' + error if error else ''))
        fast_view = fast_coverage = None
        if fast is not None:
            try:
                fast_view = P['pop_view'](fast, summary_rows=True)
                lines.append('새 방식 판독 성공 · 칸까지 읽은 줄 {} · 요약값으로 읽은 줄 {} · 보이는 줄의 요약=칸 {}'.format(
                    len(fast_view['keys']) - len(fast_view['omitted']), len(fast_view['omitted']),
                    '일치' if fast_view['fast_supported'] else '불일치'))
                verdict['fast_view'] = True
            except Exception as failure:
                verdict['fast_view'] = False
                lines.append('새 방식 판독 실패 — ' + explain(failure))
            try:
                fast_coverage = P['collect_pop'](target, fast, {}, None, None, stop, quiet, summary_rows=True)
                state = list(fast_coverage['enabled'].values())
                lines.append('열 위치(요약값 안의 순서): ' + ', '.join(
                    '{}={}'.format(name, index + 1) for name, index in sorted(fast_coverage['columns'].items(), key=lambda kv: kv[1])))
                lines.append('체크 칸 상태 — 사용 가능 {} · 사용 불가 {} · 화면에 보일 때 확인 {}'.format(
                    state.count(True), state.count(False), state.count(None)))
                chosen = sum(1 for row in fast_coverage['rows'].values() if row.get('선택') == '선택')
                lines.append("'선택' 값 — 선택 {}줄 · 선택안됨 {}줄 · 그 밖 {}줄".format(
                    chosen, sum(1 for row in fast_coverage['rows'].values() if row.get('선택') == '선택안됨'),
                    sum(1 for row in fast_coverage['rows'].values() if row.get('선택') not in ('선택', '선택안됨'))))
            except Exception as failure:
                lines.append('새 방식 목록 정리 실패 — ' + explain(failure))
            try:
                conditions = P['read_conditions'](fast)
                lines.append('POP 조건 칸 읽기 — ' + ', '.join(
                    '{} {}'.format(label, '읽음' if conditions.get(key) else '빈칸')
                    for key, label in (('date', '검사일'), ('worker', '작업자'), ('sequence', '세척순서'))))
            except Exception as failure:
                lines.append('POP 조건 칸 읽기 실패 — ' + explain(failure))

        # 3) 전체 칸 읽기(예전 방식)와 대조 ------------------------------------
        step(lines, '3. 전체 칸 읽기(pop_full, 예전 방식)와 대조')
        if not full:
            lines.append('건너뜀(선택 해제)')
        else:
            log('3/4 전체 칸 읽는 중… 줄이 많으면 몇 분 걸립니다.')
            whole, seconds, error = read('pop_full', '점검: 전체 칸', True)
            stats = finish_stats(whole)
            lines.append('걸린 시간 {:.1f}초 · 읽은 항목 {}개{}{}'.format(
                seconds, stats.get('elements', '?'), ' · 판독기 한도에 걸림' if stats.get('limited') else '',
                ' · 오류: ' + error if error else ''))
            if seconds > 80:
                lines.append('→ 지금 배포본(2026.11.10.3)의 80초 한도를 넘는 목록입니다.')
            if whole is not None and not stats.get('limited'):
                try:
                    full_view = P['pop_view'](whole)
                    lines.append('예전 방식 판독 성공 · {}줄 · 줄당 {:.2f}초'.format(
                        len(full_view['keys']), seconds / max(1, len(full_view['keys']))))
                    if fast_view is not None:
                        if full_view['keys'] != fast_view['keys']:
                            lines.append('대조 불가 — 두 판독의 줄 수가 다름(새 {} / 예전 {})'.format(
                                len(fast_view['keys']), len(full_view['keys'])))
                        else:
                            different = [i for i, (a, b) in enumerate(zip(fast_view['raw'], full_view['raw']), 1) if a != b]
                            verdict['equal'] = (not different) if full_view['keys'] else None
                            lines.append('새 방식 값 = 예전 방식 값: ' + ('비교할 줄 없음(0줄)' if not full_view['keys'] else
                                         '전부 일치({}줄 × 모든 칸)'.format(len(full_view['keys']))
                                         if not different else '{}줄 불일치'.format(len(different))))
                            for number in different[:10]:
                                a, b = fast_view['raw'][number - 1], full_view['raw'][number - 1]
                                columns = [str(i + 1) for i in range(max(len(a), len(b))) if (a[i:i + 1] != b[i:i + 1])]
                                lines.append('  - {}번째 줄: 다른 칸 번호 {} · 새 방식 칸 {}개 / 예전 {}개'.format(
                                    number, ','.join(columns[:12]), len(a), len(b)))
                    old_coverage = P['collect_pop'](target, whole, {}, None, None, stop, quiet)
                    disabled = [key for key, value in old_coverage['enabled'].items() if not value]
                    lines.append('예전 방식 목록 정리 성공 · 체크 칸 사용 불가 {}줄{}'.format(
                        len(disabled), ' (줄 번호 ' + ', '.join(disabled[:20]) + ')' if disabled else ''))
                    if fast_coverage is not None:
                        same = (old_coverage['rows'] == fast_coverage['rows'] and old_coverage['columns'] == fast_coverage['columns'])
                        lines.append('체크에 쓰는 열(선택·프로젝트No·설비명·지시일) 값: ' + ('두 방식 일치' if same else '두 방식 불일치'))
                        if not same and full_view['keys']: verdict['equal'] = False
                except Exception as failure:
                    lines.append('예전 방식 판독 실패 — ' + explain(failure))

        # 4) 점검하는 동안 목록이 바뀌었는지 ------------------------------------
        step(lines, '4. 점검 중 목록 변동'); log('4/4 목록 변동 확인 중…')
        last, seconds, error = read('mes_rows', '점검: 변동 확인', False)
        if last is None or base_summaries is None:
            lines.append('확인 못함' + (' — ' + error if error else ''))
        else:
            try:
                _, _, rows, _ = P['pop_grid'](last)
                verdict['stable'] = [r.get('value') for r in rows] == base_summaries
                lines.append('바뀌지 않음' if verdict['stable'] else '바뀜 — 점검 도중 목록이 달라져 3번 대조 결과는 참고만 하세요.')
            except Exception as failure:
                lines.append('확인 실패 — ' + explain(failure))
    finally:
        P['validate_conditions'] = original_validate

    head = ['POP 점검 결과 (읽기 전용 · 실제 값 없음)',
            '점검 프로그램 {} · 지후니우스 {} · {}'.format(PROBE_VERSION, APP_VERSION, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            '', '[요약]']
    if row_count == 0:
        head += ['※ POP 목록이 0줄입니다. 프로그램은 정상 실행됐지만 줄이 없어 아래 항목은 확인할 수 없습니다.',
                 '   목록에 줄이 떠 있을 때(세척완료를 누르기 전) 다시 실행해 주세요.']
    head += [
            '행 요약값 사용 가능: ' + {True: '예', False: '아니오', None: '확인 못함'}[verdict['summary']],
            '새 방식(보이는 줄 칸 + 화면 밖 줄 요약값) 판독: ' + {True: '성공', False: '실패', None: '확인 못함'}[verdict['fast_view']],
            '새 방식 값과 예전 방식 값: ' + {True: '일치', False: '불일치', None: '비교 못함'}[verdict['equal']],
            '점검 중 목록: ' + {True: '그대로', False: '바뀜', None: '확인 못함'}[verdict['stable']]]
    return head + lines


# --- Windows 실행부 -----------------------------------------------------------
def make_reader(P, extended):
    scope = {'queue': queue, 'time': time, 'os': os, 'Path': Path}
    exec(compile(WASH_READER_SOURCE, 'wash_reader.py', 'exec'), scope)
    powershell = P['POWERSHELL']
    if extended:
        if NORMAL_LIMIT not in powershell: raise RuntimeError('판독기 한도 위치를 찾지 못했습니다.')
        powershell = powershell.replace(NORMAL_LIMIT, EXTENDED_LIMIT)
    module = SimpleNamespace(POWERSHELL=powershell, base64=P['base64'], check_capture=lambda report: None)
    reader = scope['WashReader'](module)
    reader.wait_seconds = EXTENDED_WAIT if extended else 95
    return reader


def run_probe(full, log):
    P = load_pop()
    windows = [w for w in P['visible_windows']() if w['title'] == '현장관리']
    if len(windows) != 1:
        raise RuntimeError("'현장관리'(POP) 창을 하나만 켜 주세요. 지금 {}개입니다.".format(len(windows)))
    target = windows[0]
    stop = threading.Event()
    readers = {}

    def read(mode, label, extended):
        started = time.monotonic()
        try:
            if extended not in readers: readers[extended] = make_reader(P, extended)
            report = readers[extended].capture({**target, 'mode': mode}, label, stop)
            return report, time.monotonic() - started, ''
        except Exception as failure:
            return None, time.monotonic() - started, explain(failure)

    try:
        return analyze(P, read, target, full=full, log=log)
    finally:
        for reader in readers.values():
            try: reader.close()
            except Exception: pass


def main():
    import tkinter as tk
    from tkinter import ttk, messagebox
    root = tk.Tk(); root.title('POP 점검 (읽기 전용)'); root.geometry('760x560')
    body = ttk.Frame(root, padding=16); body.pack(fill='both', expand=True)
    ttk.Label(body, text='POP 점검 (읽기 전용)', font=('맑은 고딕', 15, 'bold')).pack(anchor='w')
    ttk.Label(body, justify='left', wraplength=720, text=(
        '1) POP(현장관리)에서 평소 세척완료 하듯이 조회해서 목록이 떠 있게 해 주세요. 줄이 많은 날이 좋습니다.\n'
        '2) POP 창은 최소화하지 말고, 점검이 끝날 때까지 POP를 건드리지 말아 주세요.\n'
        '3) 이 프로그램은 화면을 읽기만 합니다. 클릭·입력·스크롤·저장을 하지 않습니다.\n'
        '4) 끝나면 결과 글이 이 파일 옆에 저장되고 복사됩니다. 그 글을 그대로 보내 주세요(실제 값은 들어가지 않습니다).')).pack(anchor='w', pady=(8, 10))
    full = tk.BooleanVar(value=True)
    ttk.Checkbutton(body, text='전체 칸 읽기와 대조하기(줄이 많으면 몇 분 걸림) — 켜 두는 것을 권합니다', variable=full).pack(anchor='w')
    bar = ttk.Frame(body); bar.pack(fill='x', pady=10)
    status = tk.StringVar(value='준비됨')
    start = ttk.Button(bar, text='점검 시작'); start.pack(side='left')
    copy = ttk.Button(bar, text='결과 복사', state='disabled'); copy.pack(side='left', padx=8)
    ttk.Label(bar, textvariable=status).pack(side='left', padx=8)
    output = tk.Text(body, wrap='word', font=('맑은 고딕', 10)); output.pack(fill='both', expand=True)
    events = queue.Queue(); result = {'text': ''}

    def put_clipboard():
        root.clipboard_clear(); root.clipboard_append(result['text']); status.set('결과를 복사했습니다. 그대로 붙여넣어 보내 주세요.')
    copy.configure(command=put_clipboard)

    def work(with_full):
        try:
            if os.name != 'nt': raise RuntimeError('POP가 실행 중인 Windows PC에서 실행해 주세요.')
            lines = run_probe(with_full, lambda text: events.put(('log', text)))
        except Exception as failure:
            lines = ['POP 점검 결과 (읽기 전용)', '점검을 시작하지 못했습니다 — ' + explain(failure), '',
                     traceback.format_exc()[-1500:]]
        events.put(('done', '\n'.join(lines)))

    def begin():
        start.configure(state='disabled'); copy.configure(state='disabled'); output.delete('1.0', 'end')
        status.set('점검 중… POP를 건드리지 말아 주세요.')
        threading.Thread(target=work, args=(full.get(),), daemon=True).start()
    start.configure(command=begin)

    def poll():
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == 'log': status.set(value)
                else:
                    result['text'] = value; output.insert('1.0', value)
                    name = 'POP점검결과_{}.txt'.format(datetime.now().strftime('%Y%m%d-%H%M%S'))
                    saved = ''
                    for folder in (Path(sys.argv[0]).resolve().parent, Path.home() / 'Desktop', Path.home()):
                        try:
                            (folder / name).write_text(value, encoding='utf-8'); saved = str(folder / name); break
                        except OSError: continue
                    try: put_clipboard()
                    except tk.TclError: pass
                    status.set('끝났습니다. 결과를 복사했습니다' + (' · 저장: ' + saved if saved else '') + ' — 이 글을 보내 주세요.')
                    start.configure(state='normal'); copy.configure(state='normal')
        except queue.Empty:
            pass
        root.after(150, poll)
    poll(); root.mainloop()


if __name__ == '__main__':
    main()
