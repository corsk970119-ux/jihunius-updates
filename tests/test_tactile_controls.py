import unittest
from unittest.mock import Mock
import test_main_window_placement as placement


class TactileControlsTests(unittest.TestCase):
    setUp = placement.MainWindowPlacementTests.setUp
    cleanup = placement.MainWindowPlacementTests.cleanup
    close_app = placement.MainWindowPlacementTests.close_app
    launch = placement.MainWindowPlacementTests.launch

    def test_icons_survive_native_disabled_state_and_invoke_correct_machine(self):
        app = self.launch()
        quick = app.material_quick
        quick.submit = Mock()
        for machine, row in quick.rows.items():
            for action in ('defect', 'rotate'):
                button = row[action]
                self.assertTrue(button.cget('image'))
                self.assertEqual(str(button.cget('compound')), 'left')
                button.state(['disabled'])
                button.invoke()
                quick.submit.assert_not_called()
                button.state(['!disabled'])
                button.invoke()
                quick.submit.assert_called_once_with(action, machine)
                quick.submit.reset_mock()

    def test_full_status_colors_keep_prm_stale_and_offline_semantics(self):
        app = self.launch()
        app.machine_alert_enabled = False
        records = {1: {'light':'green','prm_no':'0007'},
                   2: {'light':'red','prm_no':'1234','_stale':True},
                   3: {'light':'yellow','prm_no':'invalid'}}
        app.apply_machine_status(records)
        for machine, color in ((1,'#2fb36b'),(2,'#e5484d'),(3,'#f0c440'),(4,'#25334b')):
            tile, surface, number = app.machine_tiles[machine]
            self.assertEqual(tile.type(surface), 'polygon')
            self.assertEqual(tile.itemcget(surface,'fill'), color)
        self.assertEqual(app.machine_tiles[1][0].itemcget(app.machine_tiles[1][2],'text'),'0007')
        self.assertIn('?',app.machine_tiles[2][0].itemcget('machine_title','text'))
        self.assertEqual(app.machine_tiles[3][0].itemcget(app.machine_tiles[3][2],'text'),'—')
        before = app.window.tk.call('image','names')
        for _ in range(30):app.apply_machine_status(records)
        self.assertEqual(app.window.tk.call('image','names'),before)
        app.apply_machine_status(records,online=False)
        for tile, surface, number in app.machine_tiles.values():
            self.assertEqual(tile.itemcget(surface,'fill'),'#25334b')
            self.assertEqual(tile.itemcget(number,'text'),'—')
        app.show_machine_details(1)
        self.assertTrue(app.machine_detail_dialog.winfo_exists())
        app.show_machine_details(1)
        self.assertIsNone(app.machine_detail_dialog)


if __name__ == '__main__':unittest.main()


class HeaderAndBoardRegressionTests(unittest.TestCase):
    """Design A-3a must not hide notices or mislabel machine states."""
    setUp = placement.MainWindowPlacementTests.setUp
    cleanup = placement.MainWindowPlacementTests.cleanup
    close_app = placement.MainWindowPlacementTests.close_app
    launch = placement.MainWindowPlacementTests.launch

    def test_update_notices_stay_fully_visible(self):
        app = self.launch()
        notices = [app.ttk.Button(app.header_actions, text=text, style='HandoverNotice.TButton')
                   for text in ('새 버전 있음', '원본 교체 확인')]
        for button in notices:
            button.pack(side='right', padx=(6, 0))
        for size in ('1120x900', '1000x760'):
            app.window.geometry(size); app.window.update()
            for button in notices:
                self.assertGreaterEqual(button.winfo_width(), button.winfo_reqwidth(), (size, button.cget('text')))

    def test_typing_cursor_is_visible_in_every_main_input(self):
        """날짜 폴더·세척완료 작업자 등 입력칸의 깜박이는 커서가 칸 바탕색에 묻히지 않는다."""
        app = self.launch()
        def brightness(color):
            red, green, blue = app.window.winfo_rgb(color)
            return (red * 299 + green * 587 + blue * 114) / 1000 / 65535.0
        def inputs(widget):
            for child in widget.winfo_children():
                if child.winfo_class() in ('TEntry', 'TCombobox', 'TSpinbox') and str(child.cget('state')) == 'normal':
                    yield child
                for found in inputs(child):
                    yield found
        found = list(inputs(app.window))
        self.assertIn(app.folder_input, found); self.assertIn(app.year_input, found)
        for entry in found:
            style = str(entry.cget('style')) or entry.winfo_class()
            caret = app.style.lookup(style, 'insertcolor'); field = app.style.lookup(style, 'fieldbackground')
            self.assertTrue(caret, style)
            self.assertGreater(abs(brightness(caret) - brightness(field)), 0.6, (style, caret, field))
            self.assertGreaterEqual(int(str(app.style.lookup(style, 'insertwidth') or 1)), 2, style)

    def test_material_caption_has_room_for_the_whole_message(self):
        """소재 저장 문구는 작업 기록 제목 줄 오른쪽(설비 보드 바로 아래)에 한 줄로, 잘리지 않게 보인다."""
        from tkinter import font as tkfont
        app = self.launch()
        app.window.geometry('1000x{}'.format(app.minimum_height)); app.window.update()   # 가장 좁은 창
        caption = app.material_quick.caption
        title = next(w for w in app.log_card.winfo_children()
                     if w.winfo_class() == 'TLabel' and str(w.cget('text')).startswith('작업 기록'))
        self.assertIs(caption.master, app.log_card)
        self.assertGreater(caption.winfo_rootx(), title.winfo_rootx() + title.winfo_width())       # 제목 오른쪽
        self.assertLess(abs((caption.winfo_rooty() + caption.winfo_height() // 2)
                            - (title.winfo_rooty() + title.winfo_height() // 2)), 4)                # 같은 줄
        self.assertEqual(caption.winfo_rootx() + caption.winfo_width(), app.log.winfo_rootx() + app.log.winfo_width())
        self.assertLess(caption.winfo_rooty() + caption.winfo_height(), app.log.winfo_rooty() + 2)  # 기록 글 위
        font = tkfont.Font(root=app.window, font=caption.cget('font'))
        # 프로그램에 들어 있는 가장 긴 안내 문구에 호기 이름이 붙은 것도 한 줄에 다 들어감
        longest = '3호기: 확인 중 소재 정보가 변경되었습니다. 최신 내용을 확인한 뒤 다시 눌러주세요.'
        app.material_quick.notice(longest, True); app.window.update()
        self.assertLessEqual(font.measure(longest), caption.winfo_width())
        self.assertEqual(str(caption.cget('anchor')), 'e')                                          # 오른쪽(보드 아래)에 붙음
        app.material_quick.notice('9호기: ' + '저장하지 못했습니다 ' * 9, True); app.window.update()
        self.assertEqual(str(caption.cget('anchor')), 'w')                                          # 칸보다 길면 앞부분부터
        app.material_quick.notice('3호기 양품 −1 / 불량 +1 저장 완료'); app.window.update()
        self.assertEqual(str(caption.cget('anchor')), 'e')

    def test_machine_tile_shows_current_tool_number(self):
        app = self.launch()
        app.machine_alert_enabled = False
        app.apply_machine_status({1: {'light': 'green', 'state': 'RUN', 'prm_no': '6001', 'details': {'tool_number': '12'}},
                                  2: {'light': 'yellow', 'state': 'WAIT', 'prm_no': '6002', 'details': {'tool_number': 'T0303'}},
                                  3: {'light': 'green', 'state': 'RUN', 'prm_no': '6003', 'details': {'tool_number': ''}},
                                  4: {'light': 'green', 'state': 'RUN', 'prm_no': '6004'}})
        tool = lambda n: app.machine_tiles[n][0].itemcget('machine_tool', 'text')
        self.assertEqual([tool(n) for n in (1, 2, 3, 4, 5)], ['T12', 'T0303', '', '', ''])
        # 프로그램 번호·상태 표시는 그대로.
        self.assertEqual(app.machine_tiles[1][0].itemcget(app.machine_tiles[1][2], 'text'), '6001')
        self.assertEqual(app.machine_tiles[2][0].itemcget('machine_state', 'text'), '대기')
        app.apply_machine_status({}, online=False)
        self.assertEqual([tool(n) for n in (1, 2)], ['', ''])

    def test_machine_state_word_follows_state_not_color(self):
        app = self.launch()
        app.machine_alert_enabled = False
        app.apply_machine_status({1: {'light': 'yellow', 'state': 'HOLD', 'prm_no': '1'},
                                  2: {'light': 'yellow', 'state': 'WAIT', 'prm_no': '2'}})
        words = {n: app.machine_tiles[n][0].itemcget('machine_state', 'text') for n in (1, 2, 3)}
        self.assertEqual(words, {1: '일시정지', 2: '대기', 3: ''})
