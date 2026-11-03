import importlib.util,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from test_engine import e,descriptor

class LaunchTests(unittest.TestCase):
    def run_flow(self,fail=False):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);root=Path(tmp.name)
        origin=root/'original'/'지후니우스.pyw';origin.parent.mkdir()
        engine=Path(e.__file__).resolve()
        preamble="import importlib.util, pathlib, os, json\ns=importlib.util.spec_from_file_location('engine',"+repr(str(engine))+");e=importlib.util.module_from_spec(s);s.loader.exec_module(e)\n"
        new=preamble+("raise SystemExit(8)\n" if fail else "c=e.managed_context();assert c is not None\ne.mark_ready(c)\np=pathlib.Path(os.environ['JIHUNIUS_UPDATE_ORIGIN']).parent/'trace.txt'\np.open('a').write('new\\n')\n")
        offered=descriptor(new.encode())
        text=preamble+"c=e.managed_context();assert c is not None\ne.mark_ready(c)\nroot=pathlib.Path(os.environ['JIHUNIUS_UPDATE_ORIGIN']).parent\nassert pathlib.Path.cwd()==root\n(root/'trace.txt').open('a').write('base\\n')\ns=e.Store(c['root'],c['origin'],c['base_version'])\nv="+repr(offered)+"\ns.stage(v,"+repr(new.encode())+")\ns.request(v,c['nonce'])\n"
        origin.write_text(text)
        (origin.parent/'settings.json').write_text('user-data')
        env=os.environ.copy();env['LOCALAPPDATA']=str(root/'local')
        for k in list(env):
            if k.startswith('JIHUNIUS_UPDATE_'):del env[k]
        driver=preamble+"raise SystemExit(e.launch("+repr(str(origin))+",'2026.11.03.2'))"
        result=subprocess.run([sys.executable,'-c',driver],env=env,capture_output=True,timeout=15)
        trace=(origin.parent/'trace.txt').read_text()
        self.assertEqual((origin.parent/'settings.json').read_text(),'user-data')
        key=e.hashlib.sha256(os.path.normcase(str(origin.resolve())).encode()).hexdigest()[:24]
        state=e.read_json(root/'local'/'JihuniusTools'/'desktop-v1'/key/'state.json')
        return result,trace,state

    def test_real_python_child_restarts_only_after_explicit_update_exit(self):
        result,trace,state=self.run_flow()
        self.assertEqual(result.returncode,0,result.stderr.decode())
        self.assertEqual(trace,'base\nnew\n')
        self.assertEqual(state['current']['version'],'2026.11.03.3')

    def test_early_crash_restores_previous_without_rerunning_work(self):
        result,trace,state=self.run_flow(fail=True)
        self.assertEqual(result.returncode,8,result.stderr.decode())
        self.assertEqual(trace,'base\n')
        self.assertEqual(state['current']['version'],'2026.11.03.2')
        self.assertTrue(state['rejected_sha'])

if __name__=='__main__':unittest.main()
