import gc,sys,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import tkinter as tk
from tkinter import ttk
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from material_quick import QuickPanel,QuickChannel,write


class QuickConfirmationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=tk.Tk();self.addCleanup(self.cleanup)
  self.panel=QuickPanel(SimpleNamespace(tk=tk,ttk=ttk,root=self.root,style=ttk.Style(self.root)),self.root)
  self.folder=Path(self.tmp.name);self.row=dict(machine=1,can_rotate=True,can_defect=True,busy=False,
    expected=dict(material=5,next_type='10Z',material_type='10Z'),material_type='10Z',next_type='10Z')
  self.status=dict(nonce='nonce',at=time.time(),quick=dict(connected=True,client='pc',owner='owner',epoch='e',at=time.time(),rows=[self.row]))
  self.save_status()
  manager=SimpleNamespace(sessions={'material':(self.folder,'nonce')},running_keys=lambda:['material'])
  self.panel.channel=QuickChannel(manager,self.folder/'inputs.json');self.panel.poll()
 def save_status(self):write(self.folder/'material-status.json',self.status)
 def cleanup(self):
  self.root.destroy();self.panel=None;self.root=None
  gc.collect()

 def test_cancel_saves_nothing_and_defect_still_inputs_one_without_confirmation(self):
  self.assertEqual(self.panel.rows[1]['defect'].cget('text'),'불량')
  with patch('tkinter.messagebox.askokcancel',return_value=False) as ask:
   self.panel.rows[1]['rotate'].invoke()
   ask.assert_called_once();self.assertIn('1호기',ask.call_args.args[1])
   self.assertEqual(self.panel.channel.pending,{})
   self.assertFalse((self.folder/'inputs.json').exists())
   self.panel.rows[1]['defect'].invoke();ask.assert_called_once()
   requests=list(self.panel.channel.pending.values());self.assertEqual(len(requests),1)
   self.assertEqual(requests[0]['request']['method'],'defect')
   self.assertEqual(requests[0]['request']['args'],[1])

 def test_confirm_saves_once_and_duplicate_click_does_not_open_another_dialog(self):
  with patch('tkinter.messagebox.askokcancel',return_value=True) as ask:
   self.panel.submit('rotate',1);self.panel.submit('rotate',1)
   ask.assert_called_once();self.assertEqual(len(self.panel.channel.pending),1)
   request=next(iter(self.panel.channel.pending.values()))['request']
   self.assertEqual(request['method'],'rotate');self.assertEqual(request['args'],[1,False])
   self.assertEqual(request['expected']['material'],5)

 def test_changed_material_or_disconnection_while_confirming_cannot_rotate(self):
  for change in ('material','next_type','owner','epoch','offline'):
   with self.subTest(change=change):
    def change_then_confirm(*a,**k):
     if change in ('material','next_type'):self.row['expected'][change]='changed'
     elif change=='offline':self.status['quick']['connected']=False
     else:self.status['quick'][change]+='changed'
     self.save_status();return True
    self.status['quick']['connected']=True;self.row['expected'].update(material=5,next_type='10Z')
    self.save_status();self.panel.poll()
    with patch('tkinter.messagebox.askokcancel',side_effect=change_then_confirm):self.panel.submit('rotate',1)
    self.assertEqual(self.panel.channel.pending,{})
    self.assertFalse((self.folder/'inputs.json').exists())
