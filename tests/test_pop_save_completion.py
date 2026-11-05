"""Synthetic accessibility reports; the Windows POP application is not contacted."""
import ast,re,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[1]

def load_save_functions():
    tree=ast.parse((ROOT/'apps/jihunius/app.pyw').read_text())
    source=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign)
        and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='WASH_POP_SOURCE'))
    names={'nodes','bounds','check_capture','Stopped','save_dialog_messages','save_dialog_button','save_checked_pop'}
    parts=[n for n in ast.parse(source).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
    scope={'re':re,'wintypes':SimpleNamespace(HWND=int,UINT=int)}
    exec(compile(ast.Module(body=parts,type_ignores=[]),'<POP save functions>','exec'),scope)
    return scope

def report(message='',label='닫기',handle=13,**text_options):
    text=dict(kind='element',role=41,name=message,value='',enabled=True,state_known=True,offscreen=False,
              handle=30,bounds=[10,10,200,25])
    text.update(text_options)
    button=dict(kind='element',role=43,name=label,value='',enabled=True,state_known=True,offscreen=False,
                handle=handle,bounds=[20,60,80,30])
    return dict(exit_code=0,records=[text,button,dict(kind='finish',limited=False)])

class SaveFixture:
    def __init__(self,completions):
        self.ns=load_save_functions();self.completions=list(completions);self.reads=0
        self.clock=0.;self.stage='main';self.actions=[];self.cancel=False
        self.target={'handle':1,'pid':99}
        self.confirm={'handle':20,'pid':99};self.complete={'handle':21,'pid':99}
        user=SimpleNamespace(GetWindow=Mock(return_value=1),GetForegroundWindow=lambda:20 if self.stage=='confirm' else 21,
                             IsWindowVisible=lambda h:self.stage!='closed',IsWindowEnabled=lambda h:True)
        self.api=SimpleNamespace(u=user,popup_inventory=lambda:{1},click_handle=self.click)
        self.ns.update(time=SimpleNamespace(monotonic=lambda:self.clock),WindowsClicks=lambda target:self.api,
            visible_windows=lambda **kwargs:[self.confirm if self.stage=='confirm' else self.complete],
            validate_conditions=lambda *args:None,pop_save_button=lambda r:{'handle':11},
            pop_view=lambda r:{'keys':['1'],'raw':[['선택']]})
        self.stop=SimpleNamespace(wait=self.wait,is_set=lambda:self.cancel)
        self.result=dict(matching={'matched':[{'pop':{'row':'1'}}],'already_selected':[]},check_status='verified',
            coverage={'complete':True,'top_verified':True,'bottom_verified':True,'final_report':{},'columns':{'선택':0}})
    def click(self,handle):
        self.actions.append(handle)
        self.stage={11:'confirm',12:'complete',13:'closed'}[handle]
    def wait(self,seconds):self.clock+=seconds;return self.cancel
    def capture(self,target,label,stop):
        if self.stage=='confirm':return report('저장하시겠습니까?','예(YES)',12)
        item=self.completions[min(self.reads,len(self.completions)-1)]
        self.reads+=1
        return item
    def run(self):self.ns['save_checked_pop'](self.target,{},self.result,self.api,self.capture,self.stop,lambda *args:None)

class PopSaveCompletionTests(unittest.TestCase):
    def test_empty_message_is_retried_without_repeating_save_or_yes(self):
        f=SaveFixture([report(),report(),report('완료되었습니다.')])
        try:f.run()
        except RuntimeError as e:self.fail('A not-yet-readable completion window aborted saving: '+str(e))
        self.assertEqual(f.actions,[11,12,13]);self.assertEqual(f.reads,3)
        self.assertEqual(f.result['save_status'],'confirmed')

    def test_readable_static_text_does_not_need_clickable_state(self):
        for options in ({'enabled':False},{'state_known':False},{'value':'완료되었습니다.'}):
            with self.subTest(options=options):
                f=SaveFixture([report('완료되었습니다.',**options)])
                try:f.run()
                except RuntimeError as e:self.fail('Readable completion text was rejected: '+str(e))
                self.assertEqual(f.actions,[11,12,13]);self.assertTrue(f.result['pop_success_reported'])

    def test_real_error_message_is_not_closed_or_reported_as_success(self):
        f=SaveFixture([report('저장에 실패했습니다.')])
        with self.assertRaisesRegex(RuntimeError,'실패'):f.run()
        self.assertEqual(f.actions,[11,12]);self.assertFalse(f.result.get('pop_success_reported'))

    def test_forever_blank_times_out_without_claiming_success(self):
        f=SaveFixture([report()])
        with self.assertRaises(RuntimeError):f.run()
        self.assertGreaterEqual(f.clock,30);self.assertLess(f.clock,31)
        self.assertEqual(f.actions,[11,12]);self.assertFalse(f.result.get('pop_success_reported'))

    def test_close_button_must_be_enabled_and_unique(self):
        pending=report('완료되었습니다.');pending['records'][1]['enabled']=False
        f=SaveFixture([pending,report('완료되었습니다.')])
        try:f.run()
        except RuntimeError as e:self.fail('Completion close control was not ready yet: '+str(e))
        self.assertEqual(f.reads,2);self.assertEqual(f.actions,[11,12,13])
        ambiguous=report('완료되었습니다.')
        ambiguous['records'].append(dict(ambiguous['records'][1],handle=14,bounds=[120,60,80,30]))
        f=SaveFixture([ambiguous])
        with self.assertRaises(RuntimeError):f.run()
        self.assertEqual(f.actions,[11,12])

    def test_ready_completion_has_no_extra_delay(self):
        f=SaveFixture([report('완료되었습니다.')]);f.run()
        self.assertEqual(f.reads,1);self.assertLess(f.clock,.5)
        self.assertEqual(f.result['save_status'],'confirmed')

    def test_old_confirmation_is_not_clicked_again_while_closing(self):
        f=SaveFixture([report('저장하시겠습니까?','예(YES)',12),report('완료되었습니다.')]);f.run()
        self.assertEqual(f.actions,[11,12,13])

    def test_malformed_or_hidden_report_is_not_accepted(self):
        malformed=report('완료되었습니다.');malformed['partial_line']=True
        f=SaveFixture([malformed])
        with self.assertRaises(RuntimeError):f.run()
        self.assertEqual(f.actions,[11,12])
        f=SaveFixture([report('완료되었습니다.',offscreen=True)])
        with self.assertRaises(RuntimeError):f.run()
        self.assertEqual(f.actions,[11,12]);self.assertFalse(f.result.get('pop_success_reported'))
