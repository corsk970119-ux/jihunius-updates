"""Mixed machine states must not move one row's counts out of their columns."""
import gc
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import material_client as client
import material_ui as ui
from test_material_sync import QuietCollector


class MaterialColumnAlignmentTests(unittest.TestCase):
    def check_layout(self, scaling, size):
        import tkinter as tk
        from tkinter import font
        with tempfile.TemporaryDirectory() as tmp:
            root = tk.Tk(); root.tk.call('tk', 'scaling', scaling)
            session = client.ClientSession(Path(tmp)/'pc', Path(tmp)/'share', QuietCollector)
            original_style=ui.core.Application._style
            def style(app):
                # Use a real CJK font in Linux QA instead of the tiny X11 fallback.
                if 'nanumbarungothic' in font.families(root):app.font='nanumbarungothic'
                original_style(app)
            with patch.object(ui.core.Application,'_style',style):
                app = ui.SyncedApplication(root, session)
            try:
                root.geometry(size)
                for n, row in app.rows.items():
                    row['program'].configure(text='O6001' if n == 1 else
                        ('O9020\n양산품 · 집계 중지' if n in (5,7) else 'O113\n집계 제외'))
                    row['total'].configure(text='12345' if n == 5 else str(n))
                    row['material'].configure(text='Ø10 B급\n중간 시작 · 누락 가능' +
                        ('\n보관 Ø14 · 양품 1234 / 불량 12' if n == 7 else ''))
                root.update_idletasks()
                for width in (size.split('x')[0], str(int(size.split('x')[0]) + 160)):
                    root.geometry(width+'x'+size.split('x')[1]); root.update_idletasks()
                    for key in ('state','program','total','defects','material','switch14','mass_mode'):
                        centers = [w[key].winfo_rootx()+w[key].winfo_width()/2 for w in app.rows.values()]
                        self.assertLessEqual(max(centers)-min(centers),1, (key,centers))
                    # Long program state remains readable rather than being clipped.
                    widget=app.rows[5]['program'];f=font.Font(root=root,font=widget.cget('font'))
                    self.assertGreaterEqual(widget.winfo_width(),f.measure('양산품 · 집계 중지')+2)
                    for row in app.rows.values():
                        right=row['mass_mode'].winfo_rootx()+row['mass_mode'].winfo_width()
                        self.assertLessEqual(right,root.winfo_rootx()+root.winfo_width())
            finally:
                app.jobs.close();session.close();session.thread.join(10)
                for timer in root.tk.call('after','info'):root.after_cancel(timer)
                root.destroy();app.jobs.thread.join(2)
                app=None;root=None;gc.collect()

    def test_mixed_states_align_at_original_minimum_size(self):
        self.check_layout(96/72,'1000x790')

    def test_mixed_states_align_at_125_percent_display_scale(self):
        self.check_layout(120/72,'1250x988')
