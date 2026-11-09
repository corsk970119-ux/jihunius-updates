import hashlib, importlib.util, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('origin_engine',ROOT/'src/update_engine.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
if (ROOT/'src/update_origin.py').exists():
    exec(compile((ROOT/'src/update_origin.py').read_bytes(),'update_origin.py','exec'),e.__dict__)

def source(v):
    return ("SUITE_APP_VERSION = %r\nSUITE_UPDATE_PROTOCOL = 1\n" % v).encode()
def item(data,v):
    return dict(version=v,path='releases/jihunius/'+v+'/app.pyw',sha256=hashlib.sha256(data).hexdigest(),size=len(data),update_protocol=1,min_python=[3,8])

class OriginTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.origin=Path(self.tmp.name)/'공유 지후니우스.pyw'
        self.old=source('2026.11.09.2');self.new=source('2026.11.09.3')
        self.origin.write_bytes(self.old);self.candidate=item(self.new,'2026.11.09.3')
        self.known=[hashlib.sha256(self.old).hexdigest()]
    def replace(self,data=None,candidate=None):
        self.assertTrue(callable(getattr(e,'replace_origin',None)),'원본 교체 기능이 필요합니다')
        return e.replace_origin(self.origin,candidate or self.candidate,self.new if data is None else data,self.known)
    def test_replaces_same_named_origin_and_retains_one_previous_copy(self):
        result=self.replace()
        self.assertEqual(result['kind'],'updated');self.assertEqual(self.origin.read_bytes(),self.new)
        self.assertEqual(self.origin.with_name('.'+self.origin.name+'.previous').read_bytes(),self.old)
        self.assertEqual(self.replace()['kind'],'current')
        self.assertEqual(self.origin.with_name('.'+self.origin.name+'.previous').read_bytes(),self.old)
    def test_older_pc_never_downgrades_newer_shared_origin(self):
        newest=source('2026.11.09.4');self.origin.write_bytes(newest)
        self.assertEqual(self.replace()['kind'],'newer');self.assertEqual(self.origin.read_bytes(),newest)
    def test_unknown_edit_or_same_version_different_hash_is_preserved(self):
        for data in (self.old+b'# local edit\n',self.new+b'# other bytes\n',b'print(123)\n'):
            with self.subTest(data=data):
                self.origin.write_bytes(data)
                with self.assertRaises(e.UpdateError):self.replace()
                self.assertEqual(self.origin.read_bytes(),data)
    def test_invalid_candidate_is_rejected_before_origin_change(self):
        with self.assertRaises(e.UpdateError):self.replace(self.new+b'# damaged')
        self.assertEqual(self.origin.read_bytes(),self.old)
    def test_payload_version_must_match_descriptor(self):
        with self.assertRaises(e.UpdateError):self.replace(self.old,item(self.old,'2026.11.09.3'))
        self.assertEqual(self.origin.read_bytes(),self.old)
    def test_failed_final_replace_preserves_original_and_leaves_no_partial_file(self):
        real=e.os.replace
        def fail(src,dst):
            if Path(dst)==self.origin:raise PermissionError('in use')
            return real(src,dst)
        with patch.object(e.os,'replace',side_effect=fail):
            with self.assertRaises(OSError):self.replace()
        self.assertEqual(self.origin.read_bytes(),self.old)
        self.assertFalse(self.origin.with_name('.'+self.origin.name+'.update.tmp').exists())
    def test_concurrent_writer_is_deferred_without_modifying_any_bytes(self):
        lock=e.FileLock(self.origin.with_name('.'+self.origin.name+'.update.lock'))
        self.assertTrue(lock.acquire())
        try:self.assertEqual(self.replace()['kind'],'busy')
        finally:lock.release()
        self.assertEqual(self.origin.read_bytes(),self.old)
        self.assertEqual(self.replace()['kind'],'updated')

if __name__=='__main__':unittest.main()
