"""Temporary local DB/TCP fixture with synthetic machine samples; no company connection."""
import gc,time,unittest
import test_material_full_reset_ui as reset_ui


class DefaultBGradeTests(unittest.TestCase):
    setUp=reset_ui.FullResetUITests.setUp
    pump=reset_ui.FullResetUITests.pump

    def cleanup(self):
        reset_ui.FullResetUITests.cleanup(self)
        self.app.jobs.thread.join(2)
        self.app=None;self.root=None;self.session=None
        gc.collect()

    def test_new_default_uses_b_stock_and_existing_z_setting_is_preserved(self):
        self.app.material_dialog(2);self.root.update()
        dialog=next(w for w in self.root.winfo_children() if w.winfo_class()=='Toplevel')
        combo=next(w for w in dialog.winfo_children() if w.winfo_class()=='TCombobox')
        self.assertEqual(combo.get(),'Ø10 B급')
        next(w for w in dialog.winfo_children() if w.winfo_class()=='Button' and w.cget('text')=='적용').invoke()
        self.pump(lambda:self.app.store.snapshot(2)['material_type']=='10B')
        self.session.command('register_stock',['10B',20],{})
        self.pump(lambda:next(r for r in self.app.store.inventory() if r['type_id']=='10B')['quantity']==20)
        self.session.coordinator.authority.samples.put(('sample','192.168.1.10',1,
            dict(machine=2,program='1003',state='STOP',part_count='0'),time.time(),None,None))
        self.pump(lambda:self.app.store.snapshot(2)['active_material'] is not None)
        row=self.app.store.snapshot(2)
        old_z=next(r for r in self.app.store.inventory() if r['type_id']=='10Z')['quantity']
        self.session.command('rotate',[2,False],row['expected'])
        self.pump(lambda:self.app.store.snapshot(2)['active_material']!=row['active_material'])
        stock={r['type_id']:r['quantity'] for r in self.app.store.inventory()}
        self.assertEqual(stock['10B'],19)
        self.assertEqual(stock['10Z'],old_z)
        self.app.material_dialog(1);self.root.update()
        dialog=next(w for w in self.root.winfo_children() if w.winfo_class()=='Toplevel')
        combo=next(w for w in dialog.winfo_children() if w.winfo_class()=='TCombobox')
        self.assertEqual(combo.get(),'Ø10 Z급')
        dialog.destroy()
