"""메인 화면 배치(사용자 요청 2026-11-26).

- 설비 · 소재 사용량 조사 보드와 작업 기록이 자리를 바꿈: 보드는 본문 오른쪽 칸에 세로로, 작업 기록은 맨 아래 한 줄 전체.
- 머신 자리: 1·2 / 3·4 / 5·6 / 7·8 / (머신 알림)·9. 그 밑에 빈 줄 없음(소재 저장 문구는 작업 기록 제목 줄 오른쪽).
- 인수인계를 펼치고 접을 때 창만 왼쪽으로 늘고 줄어들 뿐, 보이던 화면은 제자리에서 움직이지 않음.

명령·바인딩·저장 동작은 그대로이고 자리만 바뀐 것을 확인합니다.
"""
import os
import time
import tkinter as tk
import unittest
from tkinter import font as tkfont
from unittest.mock import patch

import test_main_window_placement as placement

SCALES = (96 / 72, 120 / 72, 2.2)


def box(widget):
    return (widget.winfo_rootx(), widget.winfo_rooty(), widget.winfo_width(), widget.winfo_height())


def right(widget):
    return widget.winfo_rootx() + widget.winfo_width()


def bottom(widget):
    return widget.winfo_rooty() + widget.winfo_height()


class LayoutCase(unittest.TestCase):
    setUp = placement.MainWindowPlacementTests.setUp
    cleanup = placement.MainWindowPlacementTests.cleanup
    close_app = placement.MainWindowPlacementTests.close_app

    def launch(self, scale=None, size=None):
        root = tk.Tk()
        if scale is not None:
            root.tk.call('tk', 'scaling', scale)
        app = self.m.IntegrationApp(root)
        self.apps.append(app)
        if size:
            root.geometry(size)
        root.update()
        return app

    def settle(self, app, seconds=.3):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            app.window.update()
            time.sleep(.01)


@unittest.skipUnless(os.environ.get('DISPLAY') or os.name == 'nt', 'requires Tk display')
class MachineBoardLayoutTests(LayoutCase):
    def test_machines_stand_two_by_two_with_the_alert_switch_left_of_machine_nine(self):
        self.assertEqual(self.m.MACHINE_BOARD_ROWS, ((1, 2), (3, 4), (5, 6), (7, 8), (None, 9)))
        for scale in SCALES:
            app = self.launch(scale)
            tile = {n: app.machine_tiles[n][0] for n in range(1, 10)}
            with self.subTest(scale=scale):
                self.assertEqual(sorted(tile), list(range(1, 10)))
                left_x, right_x = tile[1].winfo_rootx(), tile[2].winfo_rootx()
                self.assertLess(right(tile[1]), right_x)                                  # 두 줄이 겹치지 않음
                previous = None
                for odd, even in ((1, 2), (3, 4), (5, 6), (7, 8)):
                    self.assertEqual(tile[odd].winfo_rooty(), tile[even].winfo_rooty(), (odd, even))   # 같은 줄
                    self.assertEqual((tile[odd].winfo_rootx(), tile[even].winfo_rootx()), (left_x, right_x))
                    if previous is not None:
                        self.assertGreater(tile[odd].winfo_rooty(), previous)             # 아래로 내려감
                    previous = bottom(app.material_quick.rows[odd]['defect'])
                # 맨 아랫줄: 왼쪽에 머신 알림, 오른쪽에 9호기
                self.assertEqual(tile[9].winfo_rootx(), right_x)
                self.assertGreater(tile[9].winfo_rooty(), previous)
                alert = app.machine_alert_controls
                self.assertEqual(alert.winfo_rootx(), left_x)
                self.assertLess(right(alert), right_x)
                self.assertEqual(alert.winfo_rooty(), tile[9].winfo_rooty())             # 9호기 칸과 윗선이 같음
                self.assertLessEqual(abs(bottom(alert) - bottom(app.material_quick.rows[9]['defect'])), 8)   # 아랫선도 거의 같음
                for widget in (app.machine_alert_toggle, app.machine_alert_settings_button):
                    self.assertTrue(widget.winfo_ismapped())
                    self.assertGreaterEqual(widget.winfo_rootx(), alert.winfo_rootx())
                    self.assertLessEqual(bottom(widget), bottom(alert))
                widths = [tile[n].winfo_width() for n in tile]
                self.assertLessEqual(max(widths) - min(widths), 1)                        # 칸 폭이 모두 같음(홀수 폭이면 1픽셀 차이)
                for n in tile:                                                            # 그 호기의 버튼은 그 칸 바로 아래
                    row = app.material_quick.rows[n]
                    self.assertGreaterEqual(row['defect'].winfo_rooty(), bottom(tile[n]))
                    self.assertLess(row['defect'].winfo_rooty() - bottom(tile[n]), 12)
                    self.assertEqual(row['defect'].winfo_rooty(), row['rotate'].winfo_rooty())
                    self.assertEqual(row['defect'].winfo_rootx(), tile[n].winfo_rootx())
                    self.assertLess(right(row['defect']), row['rotate'].winfo_rootx())
                    self.assertEqual(right(row['rotate']), right(tile[n]))
            self.close_app(app)

    def test_board_takes_the_right_column_and_the_log_runs_along_the_bottom(self):
        for scale in SCALES:
            for width in (1120, 1000):
                app = self.launch(scale)
                app.window.geometry('{}x{}'.format(width, app.minimum_height)); app.window.update()
                board, log_card = app.machine_board, app.log_card
                drive_card, numbers = app.drive_contents.master, app.number_input.master
                with self.subTest(scale=scale, width=width):
                    # 본문 한 줄: 드라이브 정리 | 프로그램 번호 | 설비 보드
                    self.assertEqual({drive_card.winfo_rooty(), numbers.winfo_rooty(), board.winfo_rooty()},
                                     {drive_card.winfo_rooty()})
                    self.assertEqual({bottom(drive_card), bottom(numbers), bottom(board)}, {bottom(board)})
                    self.assertLess(right(drive_card), numbers.winfo_rootx())
                    self.assertLess(right(numbers), board.winfo_rootx())
                    self.assertEqual(right(board), right(app.page_host))
                    # 작업 기록: 본문 아래, 왼쪽 끝부터 오른쪽 끝까지
                    self.assertGreater(log_card.winfo_rooty(), bottom(board))
                    self.assertEqual((log_card.winfo_rootx(), right(log_card)), (drive_card.winfo_rootx(), right(board)))
                    self.assertEqual(log_card.winfo_width(), app.page_host.winfo_width())
                    self.assertLessEqual(bottom(log_card), bottom(app.page_host))
                    for inner in (app.log, app.material_quick.caption) + tuple(t[0] for t in app.machine_tiles.values()):
                        self.assertTrue(inner.winfo_ismapped())
                    # 머신 칸은 가로로 다섯 칸이던 때보다 좁아지지 않음(글자·버튼이 들어가던 폭 그대로)
                    self.assertGreaterEqual(app.machine_tiles[1][0].winfo_width(), (app.page_host.winfo_width() - 72) // 5)
                    # 보드 안의 것이 보드 밖으로 나가지 않음
                    for n in range(1, 10):
                        self.assertLessEqual(right(app.material_quick.rows[n]['rotate']), right(board))
                        self.assertLessEqual(bottom(app.material_quick.rows[n]['rotate']), bottom(board))
                    # 맨 아랫줄(머신 알림·9호기) 밑에는 칸 테두리 여백만 있음 — 빈 줄을 잡아 두지 않음(사용자 요청 2026-11-26)
                    lowest = max(bottom(app.material_quick.rows[9]['rotate']), bottom(app.machine_alert_controls))
                    top_gap = app.machine_tiles[1][0].master.master.winfo_children()[0].winfo_rooty() - board.winfo_rooty()
                    self.assertLessEqual(bottom(board) - lowest, top_gap + 2)
                    self.assertGreaterEqual(bottom(board) - lowest, 8)
                    # 그 문구는 작업 기록 제목 줄에(보드 바로 아래 오른쪽)
                    caption = app.material_quick.caption
                    self.assertGreater(caption.winfo_rooty(), bottom(board))
                    self.assertLess(caption.winfo_rooty(), app.log.winfo_rooty())
                    self.assertEqual(right(caption), right(app.log))
                self.close_app(app)

    def test_every_machine_keeps_its_buttons_and_tile_actions(self):
        app = self.launch()
        with patch.object(app.material_quick, 'submit') as submit, patch.object(app, 'show_machine_details') as details:
            for n in range(1, 10):
                row = app.material_quick.rows[n]
                self.assertEqual((str(row['defect'].cget('text')), str(row['rotate'].cget('text'))), ('불량', '소재교체'))
                self.assertEqual(str(row['defect'].cget('state')), 'disabled')            # 소재 창이 연결되기 전에는 잠김
                row['defect'].configure(state='normal'); row['rotate'].configure(state='normal')
                row['defect'].invoke(); row['rotate'].invoke()
                app.machine_tiles[n][0].event_generate('<Button-1>', x=5, y=5); app.window.update()
            self.assertEqual([call.args for call in submit.call_args_list],
                             [(method, n) for n in range(1, 10) for method in ('defect', 'rotate')])
            self.assertEqual([call.args for call in details.call_args_list], [(n,) for n in range(1, 10)])
        with patch.object(app, 'toggle_machine_alerts') as toggle, patch.object(app, 'show_machine_alert_settings') as settings:
            app.machine_alert_toggle.event_generate('<Button-1>', x=5, y=5); app.window.update()
            self.assertEqual(toggle.call_count, 1)
        self.assertEqual(str(app.machine_alert_settings_button.cget('text')), '알림 설정')

    def test_machine_states_still_fill_their_own_tiles(self):
        app = self.launch()
        app.machine_alert_enabled = False
        app.apply_machine_status({n: {'light': 'green', 'state': 'RUN', 'prm_no': str(6000 + n),
                                      'details': {'tool_number': '0{}0{}'.format(n, n)}} for n in range(1, 10)})
        app.window.update()
        for n in range(1, 10):
            tile, _light, number = app.machine_tiles[n]
            self.assertEqual(tile.itemcget(number, 'text'), str(6000 + n))
            self.assertEqual(tile.itemcget('machine_title', 'text'), '머신{}'.format(n))
            self.assertEqual(tile.itemcget('machine_tool', 'text'), 'T0{}0{}'.format(n, n))

    def test_minimum_size_is_what_the_screen_needs_and_spare_height_goes_to_the_log(self):
        for index, scale in enumerate(SCALES):
            # 배율마다 다른 PC인 것처럼(앞에서 늘린 창 크기가 기억돼 다음 배율로 넘어오지 않게)
            self.stack.enter_context(patch.dict(os.environ, LOCALAPPDATA=os.path.join(self.tmp.name, 'pc{}'.format(index))))
            app = self.launch(scale); root = app.window
            outer = app.body.master
            with self.subTest(scale=scale):
                needed = max(740, outer.winfo_reqheight())
                self.assertEqual(root.minsize(), (1000, needed))                          # 필요한 높이 그대로(더 크게 잡지 않음)
                self.assertEqual(app.minimum_height, needed)
                self.assertEqual((root.winfo_width(), root.winfo_height()), (1120, max(830, needed)))
                line = tkfont.Font(root=root, font=app.log.cget('font')).metrics('linespace')
                self.assertGreaterEqual(app.log.winfo_height(), self.m.LOG_MINIMUM_LINES * line)   # 가장 작을 때 보이는 줄 수
                before = (app.log.winfo_height(), app.drive_contents.winfo_height(), app.number_input.winfo_height(),
                          app.machine_board.winfo_height(), box(app.machine_tiles[9][0]))
                root.geometry('1120x{}'.format(root.winfo_height() + 150)); root.update()
                self.assertEqual(app.log.winfo_height(), before[0] + 150)                 # 늘린 만큼 작업 기록이 늘어남
                self.assertEqual((app.drive_contents.winfo_height(), app.number_input.winfo_height(),
                                  app.machine_board.winfo_height(), box(app.machine_tiles[9][0])), before[1:])
            self.close_app(app)

    def test_material_message_never_moves_the_board(self):
        app = self.launch(size='1000x1100')
        watched = (app.machine_board, app.log_card, app.machine_tiles[9][0], app.material_quick.rows[9]['rotate'],
                   app.machine_alert_controls, app.drive_contents, app.number_input)
        before = (app.window.minsize(), tuple(box(w) for w in watched))
        for message, error in (('3호기 양품 −1 / 불량 +1 저장 완료', False), ('저장 확인 대기 3건', False),
                               ('3호기: 확인 중 소재 정보가 변경되었습니다. 최신 내용을 확인한 뒤 다시 눌러주세요.', True),
                               ('9호기: ' + '저장하지 못했습니다 ' * 9, True), ('', False)):
            app.material_quick.notice(message, error); app.window.update()
            with self.subTest(message=message[:12]):
                self.assertEqual((app.window.minsize(), tuple(box(w) for w in watched)), before)

    def test_single_import_window_opens_clear_of_the_machine_board(self):
        for scale in SCALES[:2]:
            app = self.launch(scale); root = app.window
            root.geometry('+300+40'); root.update()
            app.single_import.toggle(); root.update()
            popup = app.single_import.window
            with self.subTest(scale=scale):
                self.assertTrue(popup.winfo_viewable())
                self.assertLessEqual(right(popup), app.machine_board.winfo_rootx())       # 설비 보드를 가리지 않음
                self.assertLessEqual(bottom(popup), bottom(root))                         # 메인 창 아래로 빠져나가지 않음
                self.assertGreaterEqual(popup.winfo_rootx(), root.winfo_rootx())
                self.assertGreater(popup.winfo_rooty(), app.title_label.winfo_rooty())
            app.single_import.close()
            self.close_app(app)


@unittest.skipUnless(os.environ.get('DISPLAY') or os.name == 'nt', 'requires Tk display')
class HandoverMotionTests(LayoutCase):
    """인수인계 버튼: 창이 왼쪽으로 320 늘어날 뿐, 보이던 것은 화면에서 제자리."""

    def start(self, hold=40):
        self.m.HANDOVER_HOLD_MS = hold
        app = self.launch()
        app.window.geometry('1180x{}+900+60'.format(app.minimum_height + 30)); app.window.update()
        return app

    def seen(self, app):
        return (app.logo_label, app.title_label, app.material_button, app.tab_buttons['cnc'], app.tab_buttons['mes'],
                app.handover_toggle, app.header_status_label, app.header_actions, app.page_host, app.app_pages['cnc'],
                app.drive_contents, app.number_input, app.import_button, app.machine_board, app.machine_tiles[1][0],
                app.machine_tiles[9][0], app.machine_alert_toggle, app.log_card, app.log)

    def test_opening_and_closing_leaves_everything_on_screen_where_it_was(self):
        app = self.start(); root = app.window
        before = [box(widget) for widget in self.seen(app)]
        window = (root.winfo_x(), root.winfo_y(), root.winfo_width(), root.winfo_height())
        app.toggle_handover(); self.settle(app)
        self.assertTrue(app.handover_expanded)
        self.assertEqual((root.winfo_x(), root.winfo_y(), root.winfo_width(), root.winfo_height()),
                         (window[0] - 320, window[1], window[2] + 320, window[3]))        # 창은 왼쪽으로 320
        self.assertEqual([box(widget) for widget in self.seen(app)], before)              # 보이던 것은 제자리·같은 크기
        card = app.handover_card
        self.assertTrue(card.winfo_ismapped())
        self.assertLess(right(card), app.logo_label.winfo_rootx())                        # 새로 늘어난 왼쪽 자리에
        self.assertLessEqual(card.winfo_rooty(), app.title_label.winfo_rooty())           # 머리줄 옆까지 창 높이 전체
        self.assertEqual(bottom(card), bottom(app.page_host))
        self.assertGreaterEqual(card.winfo_width(), 300)
        app.toggle_handover(); self.settle(app)
        self.assertFalse(app.handover_expanded)
        self.assertFalse(card.winfo_ismapped())
        self.assertEqual((root.winfo_x(), root.winfo_y(), root.winfo_width(), root.winfo_height()), window)
        self.assertEqual([box(widget) for widget in self.seen(app)], before)

    def test_screen_is_not_squeezed_or_stretched_on_the_way(self):
        # 예전에는 펼칠 때 화면 전체가 한 번 좁게 눌렸다가(접을 때는 늘어났다가) 다시 그려졌습니다.
        app = self.start(); root = app.window
        sizes = {}

        def watch(name, widget):
            def record(event):
                if event.widget is widget:
                    sizes.setdefault(name, set()).add((event.width, event.height))
            widget.bind('<Configure>', record, add='+')
        watched = dict(page=app.page_host, cnc=app.app_pages['cnc'], drive=app.drive_contents, numbers=app.number_input,
                       board=app.machine_board, log=app.log, tile=app.machine_tiles[5][0], title=app.title_label,
                       tabs=app.tab_buttons['cnc'].master)
        expected = {name: (widget.winfo_width(), widget.winfo_height()) for name, widget in watched.items()}
        for name, widget in watched.items():
            watch(name, widget)
        for _ in range(2):                                                               # 펼치기, 접기
            app.toggle_handover(); self.settle(app)
        for name, seen in sizes.items():
            self.assertEqual(seen, {expected[name]}, name)                                # 다른 크기로 그려진 적이 없음

    def test_width_hold_is_let_go_so_the_window_can_be_resized_afterwards(self):
        app = self.start(hold=60); root = app.window
        column = lambda: (int(app.body.grid_columnconfigure(1)['weight']), int(app.body.grid_columnconfigure(1)['minsize']))
        self.assertEqual(column(), (1, 0))
        width = app.page_host.winfo_width()
        app.toggle_handover()
        self.assertEqual(column(), (0, width))                                            # 펼치는 동안 붙들어 둠
        self.settle(app, .4)
        self.assertEqual(column(), (1, 0))                                                # 자리 잡은 뒤에는 풀림
        self.assertIsNone(app.handover_hold_timer)
        self.assertEqual(root.minsize()[0], 1320)
        root.geometry('1320x{}'.format(root.winfo_height())); root.update()               # 펼친 채로 좁힘
        self.assertEqual(app.page_host.winfo_width(), 1320 - 36 - 320)
        app.toggle_handover(); self.settle(app, .4)
        self.assertEqual(column(), (1, 0))
        self.assertEqual((root.winfo_width(), root.minsize()[0]), (1000, 1000))
        self.assertEqual(app.page_host.winfo_width(), 1000 - 36)

    def test_quick_double_press_ends_closed_and_released(self):
        app = self.start(hold=80); root = app.window
        window = (root.winfo_x(), root.winfo_y(), root.winfo_width(), root.winfo_height())
        before = [box(widget) for widget in self.seen(app)]
        app.toggle_handover(); app.toggle_handover()                                      # 풀리기 전에 다시 누름
        self.settle(app, .4)
        self.assertFalse(app.handover_expanded)
        self.assertEqual((root.winfo_x(), root.winfo_y(), root.winfo_width(), root.winfo_height()), window)
        self.assertEqual([box(widget) for widget in self.seen(app)], before)
        self.assertEqual(int(app.body.grid_columnconfigure(1)['weight']), 1)
        self.assertEqual(int(app.body.grid_columnconfigure(1)['minsize']), 0)

    def test_maximized_window_shares_its_own_width_instead(self):
        app = self.start(); root = app.window
        window = (root.winfo_x(), root.winfo_y(), root.winfo_width(), root.winfo_height())
        page = app.page_host.winfo_width()
        with patch.object(root, 'state', return_value='zoomed'):                           # 최대화: 창 크기는 못 바꿈
            app.toggle_handover(); self.settle(app)
            self.assertEqual(int(app.body.grid_columnconfigure(1)['minsize']), 0)         # 붙들지 않음
            self.assertEqual((root.winfo_x(), root.winfo_y(), root.winfo_height()), (window[0], window[1], window[3]))
            self.assertEqual(app.page_host.winfo_width(), root.winfo_width() - 36 - 320)  # 화면 안에서 나눠 씀
            self.assertTrue(app.handover_card.winfo_ismapped())
            app.toggle_handover(); self.settle(app)
        self.assertEqual(app.page_host.winfo_width(), root.winfo_width() - 36)

    def test_header_keeps_its_place_in_keyboard_order_and_in_other_tabs(self):
        app = self.start()
        children = app.body.winfo_children()
        header = app.title_label.master.master
        self.assertLess(children.index(header), children.index(app.page_host))            # 머리줄 → 탭 화면 순서 그대로
        self.assertLess(children.index(app.page_host), children.index(app.handover_card))
        before = [box(w) for w in (app.title_label, app.handover_toggle, app.header_status_label)]
        for tab in ('stl', 'wash', 'mes', 'cnc'):
            app.select_app_tab(tab); app.window.update()
            app.toggle_handover(); self.settle(app, .15)
            with self.subTest(tab=tab):
                self.assertEqual([box(w) for w in (app.title_label, app.handover_toggle, app.header_status_label)], before)
                self.assertTrue(app.handover_card.winfo_ismapped())
            app.toggle_handover(); self.settle(app, .15)
            self.assertEqual([box(w) for w in (app.title_label, app.handover_toggle, app.header_status_label)], before)


if __name__ == '__main__':
    unittest.main()
