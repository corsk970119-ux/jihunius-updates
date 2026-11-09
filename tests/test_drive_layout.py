"""Refresh/card status must not move the host or the user's file viewport."""
from pathlib import PureWindowsPath
import tkinter as tk
from tkinter import font as tkfont
import unittest
from unittest.mock import patch
import test_main_window_placement as placement


class DriveLayoutTests(unittest.TestCase):
    setUp = placement.MainWindowPlacementTests.setUp
    cleanup = placement.MainWindowPlacementTests.cleanup
    close_app = placement.MainWindowPlacementTests.close_app
    launch = placement.MainWindowPlacementTests.launch

    def snapshot(self, status, count=100):
        drive = PureWindowsPath('F:/')
        names = ['O{:04d}_'.format(i) + 'long_name_' * 12 for i in range(count)]
        return dict(destination=drive, labels=names, paths=[drive / n for n in names], status=status)

    def bounds(self, app):
        return (app.window.minsize(), tuple(
            (w.winfo_rootx(), w.winfo_rooty(), w.winfo_width(), w.winfo_height())
            for w in (app.window, app.body, app.handover_toggle, app.header_actions,
                      app.drive_contents.master, app.drive_contents, app.number_input, app.log)))

    def test_refresh_and_card_status_keep_layout_at_both_dpi_and_window_sizes(self):
        for scale in (96 / 72, 120 / 72):
            root = tk.Tk(); root.tk.call('tk', 'scaling', scale)
            app = self.m.IntegrationApp(root); self.apps.append(app)
            for size in ('1120x930', '1000x740'):
                root.geometry(size); root.update()
                before = self.bounds(app)
                for _ in range(3):
                    for status in ('대기 중', '카드 수정 스크립트 준비 중...',
                                   '드라이브 확인 시간 초과 · 연결 상태를 확인하고 다시 눌러 주세요.'):
                        app.set_busy(status != '대기 중', status); root.update()
                        with self.subTest(scale=scale, size=size, status=status):
                            self.assertEqual(self.bounds(app), before)
                    for status in ('F:\\ 연결됨 · 파일 100개 · 폴더 0개',
                                   '목록을 읽지 못했습니다 · 마지막 목록 표시 중', '드라이브 연결 대기'):
                        app.display_drive_snapshot(self.snapshot(status)); root.update()
                        with self.subTest(scale=scale, size=size, status=status):
                            self.assertEqual(self.bounds(app), before)
                app.set_busy(False); root.update()
            self.close_app(app)

    def test_status_only_refresh_does_not_rebuild_list_or_move_viewport(self):
        app = self.launch(); root = app.window
        app.display_drive_snapshot(self.snapshot('연결됨')); root.update()
        listing = app.drive_contents
        listing.selection_set(40); listing.yview_moveto(.3); listing.xview_moveto(.4)
        root.update()
        before = (listing.xview(), listing.yview(), listing.curselection())
        with patch.object(listing, 'delete', wraps=listing.delete) as delete:
            app.apply_drive_contents(self.snapshot('마지막 목록 표시 중')); root.update()
            self.assertEqual(delete.call_count, 0)
        self.assertEqual((listing.xview(), listing.yview(), listing.curselection()), before)
        app.apply_drive_contents(self.snapshot('새 파일 추가', count=101)); root.update()
        self.assertAlmostEqual(listing.xview()[0], before[0][0], places=2)
        self.assertEqual(listing.curselection(), before[2])

    def test_long_status_stays_available_on_hover_without_changing_geometry(self):
        app = self.launch(); root = app.window
        failures = []
        root.report_callback_exception = lambda *error: failures.append(error[1])
        for label, variable in ((app.header_status_label, app.status),
                                (app.drive_status_label, app.drive_contents_status)):
            message = '드라이브 확인 시간 초과 · 연결 상태를 확인하고 다시 눌러 주세요. ' * 2
            variable.set(message); root.update()
            before = self.bounds(app)
            self.assertTrue(str(label.cget('text')).endswith('…'))
            self.assertEqual(variable.get(), message)
            label.event_generate('<Enter>'); root.update()
            tip = label._status_tip
            self.assertIsNotNone(tip)
            self.assertEqual(str(tip.winfo_children()[0].cget('textvariable')), str(variable))
            self.assertEqual(self.bounds(app), before)
            label.event_generate('<Leave>'); root.update()
            self.assertIsNone(label._status_tip)
        # A popup is also retired when the host closes, without Tk callback errors.
        label.event_generate('<Enter>'); root.update()
        self.close_app(app)
        self.assertEqual(failures, [])

    def test_status_text_and_ellipsis_fit_inside_the_styled_badge(self):
        app = self.launch(); label = app.header_status_label
        font = tkfont.Font(root=app.window, font=app.style.lookup('Status.TLabel', 'font'))
        for characters in (12, 30):
            label.configure(width=characters); app.window.update()
            # The current theme has a 6px image border and 8px padding on each side.
            content_width = label.winfo_width() - 2 * (6 + 8)
            for length in range(1, 65):
                app.status.set('M' * length); app.window.update()
                with self.subTest(characters=characters, length=length):
                    self.assertLessEqual(font.measure(str(label.cget('text'))), content_width)


if __name__ == '__main__':
    unittest.main()
