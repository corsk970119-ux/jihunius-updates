import errno
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import material_counter as core


class InstanceLockTests(unittest.TestCase):
    def test_windows_lock_never_reads_or_writes_a_locked_byte_before_acquiring(self):
        stream=Mock()
        stream.read.side_effect=PermissionError(errno.EACCES,'Permission denied')
        stream.write.side_effect=PermissionError(errno.EACCES,'Permission denied')
        api=SimpleNamespace(LK_NBLCK=2,locking=Mock())
        with patch.object(core,'open',return_value=stream,create=True),patch.object(core,'os',SimpleNamespace(name='nt')),patch.dict(sys.modules,msvcrt=api):
            lock=core.InstanceLock('sync-ui.lock')
            api.locking.assert_called_once_with(stream.fileno(),2,1)
            stream.read.assert_not_called();stream.write.assert_not_called()
            lock.close();stream.close.assert_called_once()

    def test_lock_conflict_is_typed_and_closes_handle(self):
        stream=Mock();stream.read.return_value=b'0'
        api=SimpleNamespace(LK_NBLCK=2,locking=Mock(side_effect=PermissionError(errno.EACCES,'Permission denied')))
        with patch.object(core,'open',return_value=stream,create=True),patch.object(core,'os',SimpleNamespace(name='nt')),patch.dict(sys.modules,msvcrt=api):
            with self.assertRaises(core.InstanceAlreadyRunning):core.InstanceLock('sync-ui.lock')
        stream.close.assert_called_once()

    def test_real_open_permission_denied_is_not_labeled_already_running(self):
        error=PermissionError(errno.EACCES,'Permission denied','sync-ui.lock')
        with patch.object(core,'open',side_effect=error,create=True):
            with self.assertRaises(PermissionError) as found:core.InstanceLock('sync-ui.lock')
        self.assertIs(found.exception,error)


if __name__=='__main__':unittest.main()
