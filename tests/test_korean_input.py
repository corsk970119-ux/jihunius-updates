"""한글 입력 보조: Enter·칸 이동 때 조합 중이던 마지막 글자를 치던 입력칸에 넣는다(Windows IME는 가짜로 대체)."""
import importlib.util, os, sys, tkinter as tk, unittest
from pathlib import Path
from tkinter import ttk
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import visual_theme


def fake_windows_ime(pending):
    """조합 중인 글자 pending을 가진 가짜 user32/imm32."""
    state = {'text': pending, 'notify': []}
    def composition(context, kind, buffer, size):
        if buffer is not None: buffer.value = state['text']
        return len(state['text']) * 2
    def notify(context, action, index, value):
        state['notify'].append((action, index)); state['text'] = ''
        return 1
    def set_font(context, logfont):
        state['font'] = (logfont._obj.lfHeight, logfont._obj.lfWeight, logfont._obj.lfFaceName)
        return 1
    user = SimpleNamespace(GetFocus=lambda: 100)
    imm = SimpleNamespace(ImmGetContext=lambda hwnd: 7, ImmReleaseContext=lambda hwnd, context: 1,
                          ImmGetCompositionStringW=composition, ImmNotifyIME=notify, ImmSetCompositionFontW=set_font)
    return state, (lambda name, **kwargs: user if name == 'user32' else imm)


@unittest.skipUnless(os.environ.get('DISPLAY') or os.name == 'nt', 'requires Tk display')
class KoreanInputTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk(); self.addCleanup(self.root.destroy)

    def test_committed_letter_goes_to_the_cursor_and_replaces_a_selection(self):
        entry = tk.Entry(self.root); entry.insert(0, '안녕하세'); entry.icursor('end')
        self.assertTrue(visual_theme.commit_text_into(entry, '요')); self.assertEqual(entry.get(), '안녕하세요')
        entry.selection_range(0, 'end'); visual_theme.commit_text_into(entry, '가')      # 전체 선택 상태에서 첫 글자
        self.assertEqual(entry.get(), '가')
        text = tk.Text(self.root); text.insert('1.0', '교대 인수인'); visual_theme.commit_text_into(text, '계')
        self.assertEqual(text.get('1.0', 'end-1c'), '교대 인수인계')
        themed = ttk.Entry(self.root); themed.insert(0, 'ab'); visual_theme.commit_text_into(themed, '다')
        self.assertEqual(themed.get(), 'ab다')
        locked = tk.Entry(self.root); locked.insert(0, '고정'); locked.configure(state='readonly')
        self.assertFalse(visual_theme.commit_text_into(locked, '요')); self.assertEqual(locked.get(), '고정')
        self.assertFalse(visual_theme.commit_text_into(None, '요')); self.assertFalse(visual_theme.commit_text_into(entry, ''))

    def test_pending_letter_is_taken_into_the_field_once(self):
        import ctypes
        entry = tk.Entry(self.root); entry.insert(0, '안녕하세'); entry.icursor('end')
        state, factory = fake_windows_ime('요')
        with patch('os.name', 'nt'), patch.object(ctypes, 'WinDLL', factory, create=True):
            self.assertEqual(visual_theme.take_pending_ime(entry), '요')
            self.assertEqual(entry.get(), '안녕하세요')
            self.assertEqual(state['notify'], [(0x15, 4)])            # 조합을 끝냄(CPS_CANCEL) → Windows가 같은 글자를 또 넣지 않음
            self.assertEqual(visual_theme.take_pending_ime(entry), '')  # 남은 조합 없음
            self.assertEqual(entry.get(), '안녕하세요')

    def test_nothing_happens_without_a_pending_letter_or_outside_windows(self):
        import ctypes
        entry = tk.Entry(self.root); entry.insert(0, '그대로')
        self.assertEqual(visual_theme.take_pending_ime(entry), '')      # Windows가 아님
        state, factory = fake_windows_ime('')
        with patch('os.name', 'nt'), patch.object(ctypes, 'WinDLL', factory, create=True):
            self.assertEqual(visual_theme.take_pending_ime(entry), '')
        self.assertEqual(entry.get(), '그대로'); self.assertEqual(state['notify'], [])
        self.assertFalse(visual_theme.install_korean_input(self.root))  # Windows가 아니면 아무것도 걸지 않음

    def test_locked_field_leaves_the_composition_alone(self):
        import ctypes
        locked = tk.Entry(self.root); locked.insert(0, '고정'); locked.configure(state='readonly')
        state, factory = fake_windows_ime('요')
        with patch('os.name', 'nt'), patch.object(ctypes, 'WinDLL', factory, create=True):
            self.assertEqual(visual_theme.take_pending_ime(locked), '')
            self.assertEqual(visual_theme.take_pending_ime('.없는.칸'), '')
        self.assertEqual(state['notify'], []); self.assertEqual(state['text'], '요'); self.assertEqual(locked.get(), '고정')

    def windows_input(self, pending=''):
        """가짜 Windows 입력기 위에서 install_korean_input을 건 상태."""
        import ctypes
        state, factory = fake_windows_ime(pending)
        for item in (patch('os.name', 'nt'), patch.object(ctypes, 'WinDLL', factory, create=True)):
            item.start(); self.addCleanup(item.stop)
        self.assertTrue(visual_theme.install_korean_input(self.root))
        return state

    def focus(self, widget):
        widget.pack(); widget.focus_force(); self.root.update()
        if self.root.focus_get() is not widget: self.skipTest('이 화면에서는 포커스를 줄 수 없음')

    def test_enter_puts_the_last_letter_in_before_the_field_handles_enter(self):
        state = self.windows_input(); seen = []
        entry = tk.Entry(self.root, font=('TkFixedFont', 12)); entry.bind('<Return>', lambda event: seen.append(entry.get()))
        self.focus(entry)
        self.assertEqual(entry.bindtags()[0], 'JihuniusKoreanInput')        # 그 칸의 Enter 처리보다 먼저
        entry.insert(0, '안녕하세'); state['text'] = '요'
        entry.event_generate('<Return>'); self.root.update()
        self.assertEqual(seen, ['안녕하세요']); self.assertEqual(entry.get(), '안녕하세요')
        entry.event_generate('<Return>'); self.root.update()                  # 조합 중인 글자가 없으면 그대로
        self.assertEqual(seen, ['안녕하세요', '안녕하세요'])

    def test_enter_in_multiline_text_keeps_the_letter_on_its_own_line(self):
        state = self.windows_input()
        text = tk.Text(self.root, height=4, width=30); self.focus(text)
        text.insert('1.0', '교대 인수인'); state['text'] = '계'
        text.event_generate('<Return>'); self.root.update()
        self.assertEqual(text.get('1.0', 'end-1c'), '교대 인수인계\n')          # 글자가 줄바꿈 뒤(다음 줄)로 밀리지 않음

    def test_moving_to_another_field_leaves_the_letter_where_it_was_typed(self):
        state = self.windows_input()
        first = ttk.Entry(self.root); second = tk.Text(self.root, height=2, width=20); second.pack()
        self.focus(first); first.insert(0, '제'); state['text'] = '목'
        second.focus_force(); self.root.update()
        self.assertEqual(first.get(), '제목'); self.assertEqual(second.get('1.0', 'end-1c'), '')
        first.focus_force(); self.root.update(); first.icursor('end'); state['text'] = '끝'
        first.event_generate('<Tab>'); self.root.update()                     # Tab으로 옮길 때도
        self.assertEqual(first.get(), '제목끝')

    def test_composition_window_font_follows_the_field_and_install_is_once(self):
        state = self.windows_input()
        entry = tk.Entry(self.root, font=('TkFixedFont', -18, 'bold')); self.focus(entry)
        self.assertEqual(state['font'][:2], (-18, 700))
        self.assertFalse(visual_theme.install_korean_input(self.root))        # 두 번 걸지 않음
        self.assertFalse(visual_theme.install_korean_input(tk.Toplevel(self.root)))
        self.assertEqual(entry.bindtags().count('JihuniusKoreanInput'), 1)
        entry.insert(0, '가'); state['text'] = '나'
        entry.event_generate('<Return>'); self.root.update()
        self.assertEqual(entry.get(), '가나'); self.assertEqual(state['notify'], [(0x15, 4)])   # 한 번만 처리

    def test_composition_font_matches_widget_font_size(self):
        self.assertEqual(visual_theme.composition_font_pixels(9, 96 / 72), 12)
        self.assertEqual(visual_theme.composition_font_pixels(11, 2.2), 24)
        self.assertEqual(visual_theme.composition_font_pixels(-14, 1.0), 14)
        self.assertEqual(visual_theme.composition_font_pixels(0, 1.0), 0)


class WashLogEnterTests(unittest.TestCase):
    """세척일보: Enter·칸 이동 전에 마지막 글자를 그 입력칸에 넣고 나서 동작한다."""

    def load(self):
        spec = importlib.util.spec_from_file_location('wash_log_ime_test', ROOT / 'src/wash_log.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module

    def test_after_ime_takes_the_letter_first_then_runs_the_action(self):
        module = self.load(); order = []
        fake = SimpleNamespace(after=lambda delay, action: order.append(('after', delay, action)),
                               after_idle=lambda action: order.append(('idle', action)))
        action = lambda: None; widget = object()
        with patch.object(visual_theme, 'take_pending_ime', lambda target: order.append(('take', target))):
            module.App.after_ime(fake, action, widget)
            self.assertEqual(order, [('take', widget), ('idle', action)])          # Linux: 예전과 같은 시점
            del order[:]
            with patch.object(module.os, 'name', 'nt'):
                module.App.after_ime(fake, action, widget)
            self.assertEqual(order, [('take', widget), ('after', 40, action)])     # Windows: 글자가 들어올 시간을 둠

    def test_enter_paths_use_the_field_being_typed_in(self):
        source = (ROOT / 'src/wash_log.py').read_text(encoding='utf-8')
        self.assertIn('self.after_ime(self.post_note,self.note_input)', source)                          # 채팅 Enter
        self.assertIn('self.after_ime(save,entry)', source)                                              # 판 칸 Enter·다른 칸 클릭
        self.assertIn("ent.bind('<Return>',lambda e:self.after_ime(self.daily.focus_set,e.widget))", source)  # 공구대 Enter
        self.assertNotIn('self.after_idle(self.post_note)', source)

    def test_helper_failure_never_blocks_the_action(self):
        module = self.load(); ran = []
        fake = SimpleNamespace(after=lambda delay, action: ran.append(action), after_idle=lambda action: ran.append(action))
        def broken(target): raise RuntimeError('IME 오류')
        with patch.object(visual_theme, 'take_pending_ime', broken):
            module.App.after_ime(fake, 'ACTION', None)
        self.assertEqual(ran, ['ACTION'])


if __name__ == '__main__':
    unittest.main()
