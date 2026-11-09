import unittest
from types import SimpleNamespace
from unittest.mock import patch,Mock
from test_companion_save import module as m


class Api:
    def __init__(self,call):self.call=call
    def __call__(self,*args):return self.call(*args)


class ProcessHandleTests(unittest.TestCase):
    def backend(self,stamp=123):
        self.closed=[];self.status=258
        def times(handle,created,exited,kernel,user):
            created._obj.dwLowDateTime=stamp;created._obj.dwHighDateTime=2;return 1
        return SimpleNamespace(OpenProcess=Api(lambda access,inherit,pid:987654321),
            GetProcessTimes=Api(times),WaitForSingleObject=Api(lambda handle,timeout:self.status),
            CloseHandle=Api(lambda handle:self.closed.append(handle) or 1))

    def test_native_handle_uses_creation_time_and_closes_only_after_exit(self):
        import ctypes
        kernel=self.backend()
        with patch.object(m,'_cu_os',SimpleNamespace(name='nt')),patch.object(ctypes,'WinDLL',return_value=kernel,create=True):
            process=m._CuExistingProcess(42,str((2<<32)|123))
            self.assertIsNone(process.poll());self.assertEqual(self.closed,[])
            self.status=0
            self.assertEqual(process.poll(),0);self.assertEqual(self.closed,[987654321])
            process.close();self.assertEqual(self.closed,[987654321])

    def test_recycled_pid_closes_handle_and_is_not_adopted(self):
        import ctypes
        kernel=self.backend()
        with patch.object(m,'_cu_os',SimpleNamespace(name='nt')),patch.object(ctypes,'WinDLL',return_value=kernel,create=True):
            with self.assertRaises(ValueError):m._CuExistingProcess(42,'old-creation-time')
        self.assertEqual(self.closed,[987654321])

    def test_denied_process_query_does_not_guess_process_identity(self):
        import ctypes
        kernel=self.backend();kernel.OpenProcess=Api(lambda *args:0)
        with patch.object(m,'_cu_os',SimpleNamespace(name='nt')),patch.object(ctypes,'WinDLL',return_value=kernel,create=True):
            with self.assertRaises(OSError):m._CuExistingProcess(42)
        self.assertEqual(self.closed,[])


if __name__=='__main__':unittest.main()
