"""세척일보: 안 읽은 채팅이 있으면 '채팅 펼치기' 버튼이 깜빡입니다(사용자 요청 2026-11-16). 색만 바뀌고 다른 동작은 없습니다."""
import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location('wash_log_blink_test', ROOT / 'src/wash_log.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Button:
    def __init__(self):
        self.options = {}
        self.paints = []

    def configure(self, **options):
        self.options.update(options)
        self.paints.append(dict(options))


class Screen:
    """세척일보 창 흉내: 타이머와 버튼만 있습니다."""
    def __init__(self, module, notes=3, seen=0, connected=True, expanded=False):
        self.module = module
        self.jobs = {}
        self.sequence = 0
        self.cancelled = []
        self.closing = False
        self.connected = connected
        self.notes_expanded = expanded
        self.note_notice = Button()
        ids = ['n{}'.format(index) for index in range(notes)]
        self.data = {'id': 'store', 'notes': [{'id': note_id} for note_id in ids]}
        self.cfg = {'note_seen_by_store': {'store': ids[:seen]}}

    def after(self, delay, action):
        self.sequence += 1
        self.jobs[self.sequence] = (delay, action)
        return self.sequence

    def after_cancel(self, job):
        self.cancelled.append(job)
        self.jobs.pop(job, None)

    def tick(self):
        """가장 먼저 예약된 타이머 하나를 실행합니다."""
        job = min(self.jobs)
        delay, action = self.jobs.pop(job)
        action()
        return delay

    def visible_note_ids(self):
        return self.module.App.visible_note_ids(self)

    def refresh_note_notice(self):
        return self.module.App.refresh_note_notice(self)

    def blink_note_notice(self, unread=None):
        return self.module.App.blink_note_notice(self, unread)


class ChatBlinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def colours(self, screen):
        return screen.note_notice.options['bg'], screen.note_notice.options['fg']

    def test_unread_chat_makes_the_button_alternate_between_yellow_and_dark(self):
        m, screen = self.m, Screen(self.m, notes=3, seen=1)
        screen.refresh_note_notice()
        self.assertEqual(screen.note_notice.options['text'], '새 메모 2 ▴ 펼치기')
        self.assertEqual(self.colours(screen), (m.YELLOW, m.YTEXT))            # 처음에는 지금처럼 노란색
        self.assertEqual(len(screen.jobs), 1)
        seen = []
        for _ in range(6):
            self.assertEqual(screen.tick(), 550)
            seen.append(self.colours(screen))
            self.assertEqual(len(screen.jobs), 1)                             # 타이머는 늘 하나만
        self.assertEqual(seen, [(m.BUTTON, m.YELLOW), (m.YELLOW, m.YTEXT)] * 3)   # 어두운 색 ↔ 노란색
        self.assertEqual(screen.note_notice.options['text'], '새 메모 2 ▴ 펼치기')   # 글자는 그대로

    def test_no_unread_chat_means_no_timer_and_the_usual_colours(self):
        m, screen = self.m, Screen(self.m, notes=3, seen=3)
        screen.refresh_note_notice()
        self.assertEqual(screen.note_notice.options['text'], '채팅 ▴ 펼치기')
        self.assertEqual(self.colours(screen), (m.BUTTON, m.TEXT))
        self.assertEqual(screen.jobs, {})
        offline = Screen(self.m, notes=3, seen=0, connected=False)             # 연결 전에는 안 읽은 것으로 세지 않음
        offline.refresh_note_notice()
        self.assertEqual(offline.jobs, {})

    def test_reading_the_chat_stops_the_blinking_at_once(self):
        m, screen = self.m, Screen(self.m, notes=2, seen=0)
        screen.refresh_note_notice()
        screen.tick()                                                         # 어두운 색인 순간에
        self.assertEqual(self.colours(screen), (m.BUTTON, m.YELLOW))
        screen.cfg['note_seen_by_store']['store'] = ['n0', 'n1']               # 읽음 처리됨
        screen.refresh_note_notice()
        self.assertEqual(self.colours(screen), (m.BUTTON, m.TEXT))             # 평소 색
        self.assertEqual(screen.jobs, {})
        self.assertEqual(len(screen.cancelled), 1)
        screen.data['notes'].append({'id': 'n2'})                             # 새 채팅이 오면 다시 깜빡임
        screen.refresh_note_notice()
        self.assertEqual(self.colours(screen), (m.YELLOW, m.YTEXT))
        self.assertEqual(len(screen.jobs), 1)

    def test_screen_refresh_does_not_break_the_rhythm_or_stack_timers(self):
        m, screen = self.m, Screen(self.m, notes=2, seen=0)
        screen.refresh_note_notice()
        screen.tick()                                                         # 어두운 색
        for _ in range(5):                                                    # 그 사이 화면 갱신이 여러 번 와도
            screen.refresh_note_notice()
            self.assertEqual(self.colours(screen), (m.BUTTON, m.YELLOW))       # 어두운 색을 유지하고
            self.assertEqual(len(screen.jobs), 1)                             # 타이머가 쌓이지 않음
        screen.tick()
        self.assertEqual(self.colours(screen), (m.YELLOW, m.YTEXT))

    def test_closing_window_stops_the_timer(self):
        screen = Screen(self.m, notes=2, seen=0)
        screen.refresh_note_notice()
        screen.closing = True
        screen.tick()
        self.assertEqual(screen.jobs, {})

    def test_destroyed_button_never_raises_from_the_timer(self):
        m, screen = self.m, Screen(self.m, notes=2, seen=0)
        screen.refresh_note_notice()

        def gone(**options):
            raise m.tk.TclError('invalid command name')
        screen.note_notice.configure = gone
        screen.tick()                                                         # 오류 없이 끝나고 더 예약하지 않음
        self.assertEqual(screen.jobs, {})

    def test_only_colours_are_touched_by_the_blink(self):
        screen = Screen(self.m, notes=2, seen=0)
        screen.refresh_note_notice()
        first = len(screen.note_notice.paints)
        for _ in range(4):
            screen.tick()
        for paint in screen.note_notice.paints[first:]:
            self.assertEqual(set(paint), {'bg', 'fg', 'activebackground', 'activeforeground'})
        self.assertEqual(screen.cfg['note_seen_by_store']['store'], [])       # 읽음 상태는 건드리지 않음


class RealButtonTests(unittest.TestCase):
    """실제 버튼(RoundedButton)과 실제 타이머로 한 번 돌려 봅니다."""

    def test_real_button_alternates_and_keeps_its_text(self):
        import tkinter as tk
        m = load()
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest('화면이 없어 건너뜀: {}'.format(error))
        self.addCleanup(root.destroy)
        root.configure(bg=m.BG)
        button = m.RoundedButton(root, '채팅 ▴', lambda: None)
        button.pack(fill='x')
        ids = ['a', 'b']
        screen = SimpleNamespace(closing=False, connected=True, notes_expanded=False, note_notice=button,
                                 data={'id': 'store', 'notes': [{'id': note_id} for note_id in ids]},
                                 cfg={'note_seen_by_store': {'store': []}}, after=root.after, after_cancel=root.after_cancel)
        screen.visible_note_ids = lambda: m.App.visible_note_ids(screen)
        screen.blink_note_notice = lambda unread=None: m.App.blink_note_notice(screen, unread)
        m.App.refresh_note_notice(screen)
        seen = [button.options['bg']]
        deadline = root.tk.call('clock', 'milliseconds') + 2600
        while root.tk.call('clock', 'milliseconds') < deadline:
            root.update()
            if button.options['bg'] != seen[-1]:
                seen.append(button.options['bg'])
        self.assertGreaterEqual(len(seen), 4, seen)                           # 2.6초 동안 여러 번 바뀜
        self.assertEqual(set(seen), {m.YELLOW, m.BUTTON})
        self.assertTrue(all(one != two for one, two in zip(seen, seen[1:])))
        self.assertEqual(button.options['text'], '새 메모 2 ▴ 펼치기')
        screen.cfg['note_seen_by_store']['store'] = ids                       # 읽으면 멈춤
        m.App.refresh_note_notice(screen)
        self.assertEqual((button.options['bg'], button.options['fg']), (m.BUTTON, m.TEXT))
        root.update()
        self.assertFalse(root.tk.call('after', 'info'))                        # 남은 타이머 없음


if __name__ == '__main__':
    unittest.main()
