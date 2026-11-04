import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import time
import tkinter as tk
from tkinter import ttk,messagebox,filedialog
import unittest
from unittest.mock import patch
from test_host_stability import load_app


@unittest.skipUnless(os.environ.get('DISPLAY') or os.name=='nt','requires Tk display')
class ErrorHistoryUITests(unittest.TestCase):
    def test_all_pc_default_filter_and_global_clear_without_business_data_loss(self):
        with tempfile.TemporaryDirectory() as tmp:
            m=load_app();e=m.SuiteErrors;root=tk.Tk();errors=[]
            root.report_callback_exception=lambda *args:errors.append(args)
            label=ttk.Label(root,text='지후니우스');label.pack()
            app=SimpleNamespace(window=root,tk=tk,ttk=ttk,title_label=label,messagebox=messagebox,filedialog=filedialog)
            e._recorder=e.Recorder(Path(tmp)/'main.sqlite','지후니우스','test')
            share=Path(tmp)/'share';share.mkdir();(share/'business.json').write_text('keep')
            for i in range(3):
                store=e.LocalStore(Path(tmp)/f'pc{i}.sqlite',f'PC-{i+1}')
                store.record('세척완료','저장 확인 시간 초과',stage='POP 저장',version='test')
                req=store.request();store.accept(req,e.sync_shared(share,req))
            ui=e.HistoryUI(app,share,e.SYNC_SOURCE)
            try:
                ui.open();end=time.monotonic()+4
                while len(ui.tree.get_children())!=3 and time.monotonic()<end:root.update();time.sleep(.02)
                self.assertEqual(len(ui.tree.get_children()),3)
                self.assertEqual(ui.filter.get(),'전체 PC')
                ui.dialog.geometry('820x520');root.update()
                self.assertLessEqual(ui.clear_button.winfo_rooty()+ui.clear_button.winfo_height(),
                                     ui.dialog.winfo_rooty()+ui.dialog.winfo_height(),
                                     'clear-all button is clipped at minimum popup size')
                root.update();ui.details();ui.copy();self.assertIn('POP 저장',root.clipboard_get())
                label=next(x for x in ui.filter_map if x.startswith('PC-1'))
                ui.filter.set(label);ui.render(ui.service.snapshot(),True)
                self.assertEqual(len(ui.tree.get_children()),1)
                with patch.object(messagebox,'askyesno',return_value=True):ui.clear()
                end=time.monotonic()+4
                while time.monotonic()<end:
                    root.update();time.sleep(.02)
                    if ui.service.snapshot()['status']=='전체 PC 기록 삭제 완료':break
                self.assertEqual(ui.service.snapshot()['records'],[])
                self.assertEqual((share/'business.json').read_text(),'keep')
                self.assertEqual(errors,[])
            finally:
                ui.service.close();ui.service.thread.join(7);root.destroy();e._recorder.close()


if __name__=='__main__':unittest.main()
