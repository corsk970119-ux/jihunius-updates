"""A temporarily unreachable share must never initialize an empty table."""
import errno
import importlib.util
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('protrusion_store_test', ROOT / 'src/protrusion.py')
protrusion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protrusion)


class ProtrusionStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = protrusion.SharedStore(Path(self.tmp.name) / 'shared')

    def test_network_name_failure_preserves_existing_table(self):
        self.store.sync()
        self.store.sync([{'key': 'memo', 'base': '', 'value': 'Keep this shared memo'}])
        before = self.store.path.read_bytes()
        error = FileNotFoundError(errno.ENOENT, 'Network path not found')
        error.winerror = 53
        original_read = Path.read_text

        def interrupted_read(path, *args, **kwargs):
            if path == self.store.path:
                raise error
            return original_read(path, *args, **kwargs)

        caught = None
        with patch.object(Path, 'read_text', interrupted_read):
            try:
                self.store.sync()
            except OSError as exc:
                caught = exc
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertIs(caught, error)

    def test_transient_missing_path_preserves_existing_table_after_folder_recovers(self):
        self.store.sync()
        self.store.sync([{'key': 'memo', 'base': '', 'value': 'Keep through reconnect'}])
        before = self.store.path.read_bytes()
        error = FileNotFoundError(errno.ENOENT, 'Path temporarily unavailable')
        error.winerror = 3
        with patch.object(Path, 'read_text', side_effect=error):
            with self.assertRaises(FileNotFoundError):
                self.store.sync()
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_only_real_missing_file_errors_allow_initialization(self):
        self.store.folder.mkdir()
        for winerror, number in ((64, errno.ENOENT), (67, errno.ENOENT),
                                 (None, errno.EACCES), (None, None)):
            with self.subTest(winerror=winerror, errno=number):
                error = FileNotFoundError(number, 'Share read failed')
                if winerror is not None:
                    error.winerror = winerror
                with patch.object(Path, 'read_text', side_effect=error):
                    with self.assertRaises(FileNotFoundError):
                        self.store._read()
        self.assertFalse(self.store.path.exists())

    def test_missing_table_initializes_and_persists_on_first_use(self):
        result = self.store.sync()
        saved = json.loads(self.store.path.read_text(encoding='utf-8'))
        self.assertEqual(saved['version'], 3)
        self.assertEqual(saved['revision'], 1)
        self.assertEqual(saved['values']['memo'], '')
        self.assertEqual(result['conflicts'], [])
        self.assertEqual(self.store.sync()['state'], saved)

    def test_windows_missing_file_error_allows_first_use(self):
        self.store.folder.mkdir()
        for code in (2,):
            with self.subTest(winerror=code):
                error = FileNotFoundError(errno.ENOENT, 'File not found')
                error.winerror = code
                with patch.object(Path, 'read_text', side_effect=error):
                    state, created = self.store._read()
                self.assertTrue(created)
                self.assertEqual(state['values']['memo'], '')

    def test_missing_or_inaccessible_folder_cannot_initialize(self):
        self.store.folder.mkdir()
        missing_file = FileNotFoundError(errno.ENOENT, 'File not found')
        original_stat = Path.stat
        for folder_error in (FileNotFoundError(errno.ENOENT, 'Share disappeared'),
                             PermissionError(errno.EACCES, 'Share inaccessible')):
            with self.subTest(error=type(folder_error).__name__):
                def unavailable_folder(path, *args, **kwargs):
                    if path == self.store.folder:
                        raise folder_error
                    return original_stat(path, *args, **kwargs)

                with patch.object(Path, 'read_text', side_effect=missing_file), \
                        patch.object(Path, 'stat', unavailable_folder):
                    with self.assertRaises(type(folder_error)):
                        self.store._read()
        self.assertFalse(self.store.path.exists())

    def test_non_directory_folder_cannot_initialize(self):
        self.store.folder.mkdir()
        missing_file = FileNotFoundError(errno.ENOENT, 'File not found')
        original_stat = Path.stat

        def replaced_folder(path, *args, **kwargs):
            result = original_stat(path, *args, **kwargs)
            if path == self.store.folder:
                return type(result)((stat.S_IFREG,) + tuple(result)[1:])
            return result

        with patch.object(Path, 'read_text', side_effect=missing_file), \
                patch.object(Path, 'stat', replaced_folder):
            with self.assertRaises(NotADirectoryError):
                self.store._read()

    def test_same_field_conflict_keeps_first_saved_edit(self):
        self.store.sync()
        other = protrusion.SharedStore(self.store.folder)
        self.store.sync([{'key': 'memo', 'base': '', 'value': 'First PC'}])
        result = other.sync([{'key': 'memo', 'base': '', 'value': 'Second PC'}])
        self.assertEqual(result['conflicts'], ['memo'])
        self.assertEqual(result['state']['values']['memo'], 'First PC')
        self.assertEqual(json.loads(self.store.path.read_text())['values']['memo'], 'First PC')


if __name__ == '__main__':
    unittest.main()
