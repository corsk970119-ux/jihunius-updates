import os,time,unittest
from pathlib import Path
from unittest.mock import patch
import test_material_companion as fixture
from test_companion_save import module as m


class ReopenTests(unittest.TestCase):
    setUp=fixture.MaterialCompanionTests.setUp

    def existing(self,registry=True):
        pid=int(Path('/proc/self').resolve().name) if os.name!='nt' else os.getpid()
        observer=m._CuExistingProcess(pid);self.addCleanup(observer.close)
        folder=self.manager.cache/'control'/('a'*32);folder.mkdir(parents=True)
        nonce='b'*32
        record=dict(pid=pid,started=observer.started,session=str(folder),nonce=nonce,at=time.time())
        m._cu_write(Path(self.tmp.name)/'MaterialCounter/sync-settings.json',dict(pc_id='c'*32))
        m._cu_write(folder/'material-status.json',dict(nonce=nonce,at=time.time(),visible=False,quick=dict(client='c'*32)))
        if registry:m._cu_write(Path(self.tmp.name)/'MaterialCounter/ui-instance.json',record)
        self.backend.material_pid.return_value=pid
        return record,folder,nonce

    def test_new_parent_reuses_live_hidden_window_and_control_session(self):
        record,folder,nonce=self.existing()
        self.manager.toggle('material')
        self.assertFalse(self.spawn.called)
        self.assertEqual(self.manager.sessions['material'],(folder,nonce))
        self.assertEqual(m._cu_read(folder/'material-control.json')['action'],'show')
        self.manager.toggle('material')
        self.assertEqual(m._cu_read(folder/'material-control.json')['action'],'toggle')
        self.assertEqual(self.manager.running_keys(),['material'])
        self.addCleanup(self.manager.processes['material'].close)

    def test_hidden_start_reuses_without_opening_or_changing_collection(self):
        record,folder,nonce=self.existing()
        settings=Path(self.tmp.name)/'MaterialCounter/sync-settings.json';before=settings.read_bytes()
        self.manager.start_material_client()
        self.assertFalse(self.spawn.called);self.assertFalse((folder/'material-control.json').exists())
        self.assertEqual(settings.read_bytes(),before)
        self.addCleanup(self.manager.processes['material'].close)

    def test_unique_fresh_legacy_session_recovers_without_registry(self):
        record,folder,nonce=self.existing(registry=False)
        self.manager.toggle('material')
        self.assertFalse(self.spawn.called);self.assertEqual(self.manager.sessions['material'],(folder,nonce))
        self.addCleanup(self.manager.processes['material'].close)

    def test_stale_or_ambiguous_legacy_sessions_are_not_attached(self):
        record,folder,nonce=self.existing(registry=False)
        status=m._cu_read(folder/'material-status.json');status['at']=time.time()-30
        m._cu_write(folder/'material-status.json',status)
        self.assertFalse(self.manager._reuse_material(False))
        status['at']=time.time();m._cu_write(folder/'material-status.json',status)
        other=folder.parent/('d'*32);m._cu_write(other/'material-status.json',dict(status,nonce='e'*32))
        self.assertFalse(self.manager._reuse_material(False))

    def test_wrong_process_lifetime_does_not_attach_recycled_pid(self):
        record,folder,nonce=self.existing()
        record['started']='wrong';m._cu_write(Path(self.tmp.name)/'MaterialCounter/ui-instance.json',record)
        self.backend.material_pid.return_value=None
        self.assertFalse(self.manager._reuse_material(False))

    def test_duplicate_child_exit_reconnects_and_preserves_user_show_request(self):
        self.backend.material_pid.return_value=None
        self.manager.open('material',hidden=True)
        unused=self.manager.sessions['material'][0]
        self.manager.toggle('material')
        record,folder,nonce=self.existing()
        self.process.poll.return_value=73
        self.assertEqual(self.manager.running_keys(),['material'])
        self.assertEqual(self.manager.sessions['material'],(folder,nonce))
        self.assertEqual(m._cu_read(folder/'material-control.json')['action'],'show')
        self.assertFalse(unused.exists())
        self.addCleanup(self.manager.processes['material'].close)

    def test_two_parents_cannot_start_update_on_a_shared_recovered_session(self):
        record,folder,nonce=self.existing()
        self.manager.open('material',hidden=True)
        process=self.manager.processes['material'];self.addCleanup(process.close)
        # The original .6 manager can delete the same response during child exit.
        # Reject before initiating that race; retain its files and pending inputs.
        original=m.CompanionManager(self.payload,self.tmp.name,_backend=self.backend,_popen=self.spawn)
        original.processes['material']=self.process;original.sessions['material']=(folder,nonce)
        pending=folder/'material-quick-pending.json';pending.write_text('{"preserve": true}')
        with self.assertRaisesRegex(RuntimeError,'완전 종료'):self.manager.begin_update_save()
        self.assertIsNone(self.manager.update_save)
        self.assertFalse((folder/'request.json').exists());self.assertEqual(pending.read_text(),'{"preserve": true}')
        # Graceful full exit remains available, without a kill or data deletion.
        self.manager.request_close_all()
        self.assertEqual(m._cu_read(folder/'material-control.json')['action'],'exit')
        self.assertEqual(original.running_keys(),['material'])


    def test_quick_input_uses_recovered_session_nonce_and_existing_queue(self):
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
        from material_quick import QuickChannel
        record,folder,nonce=self.existing()
        quick=dict(connected=True,client='c'*32,owner='owner',epoch='e',at=time.time(),
                   rows=[dict(machine=1,expected={'material':1},can_defect=True)])
        m._cu_write(folder/'material-status.json',dict(nonce=nonce,at=time.time(),visible=False,quick=quick))
        self.manager.start_material_client();self.addCleanup(self.manager.processes['material'].close)
        channel=QuickChannel(self.manager,Path(self.tmp.name)/'pending.json')
        channel.poll();token=channel.submit('defect',1);channel.poll()
        request=m._cu_read(folder/('material-quick-'+token+'.json'))
        self.assertEqual(request['nonce'],nonce);self.assertEqual(request['request']['args'],[1])
        self.assertEqual(request['request']['id'],token)

    def test_unresolved_duplicate_surfaces_one_actionable_error(self):
        self.backend.material_pid.return_value=None
        self.manager.open('material',hidden=True);self.process.poll.return_value=73
        self.assertEqual(self.manager.running_keys(),[])
        self.assertIn('이미 실행 중',self.manager.pop_material_error())
        self.assertEqual(self.manager.pop_material_error(),'')


if __name__=='__main__':unittest.main()
