"""A temporarily unreachable share must never initialize an empty table."""
import contextlib
import errno
import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import time
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


class ProtrusionStagingTests(unittest.TestCase):
    """A handle left open on one staging file must not block saving for every PC.

    Field report 2026-11-16: "[WinError 32] ... '.jihunius_protrusion_stage_v1.tmp'"
    on every save, so the table never became editable.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = protrusion.SharedStore(Path(self.tmp.name) / 'shared')
        self.store.sync()
        self.names = protrusion.SharedStore.STAGING_NAMES
        self.primary = self.store.folder / self.names[0]
        self.replaced = []

    @staticmethod
    def busy(path):
        error = PermissionError(errno.EACCES, 'The process cannot access the file', str(path))
        error.winerror = 32
        return error

    def held(self, paths, opening=True):
        """Behave like Windows while another process keeps these files open."""
        paths = {Path(path) for path in paths}
        real_open, real_replace, real_unlink = os.open, os.replace, Path.unlink
        stack = contextlib.ExitStack()

        def open_(path, flags, mode=0o777, **options):
            if opening and Path(path) in paths:
                raise self.busy(path)
            return real_open(path, flags, mode, **options)

        def replace(source, target, **options):
            self.replaced.append(Path(source).name)
            if Path(source) in paths:
                raise self.busy(source)
            return real_replace(source, target, **options)

        def unlink(path, *args, **options):
            if Path(path) in paths:
                raise self.busy(path)
            return real_unlink(path, *args, **options)

        stack.enter_context(patch.object(protrusion.os, 'open', open_))
        stack.enter_context(patch.object(protrusion.os, 'replace', replace))
        stack.enter_context(patch.object(Path, 'unlink', unlink))
        return stack

    def staging_files(self):
        return sorted(path.name for path in self.store.folder.iterdir() if path.name.endswith('.tmp'))

    def memo(self):
        return json.loads(self.store.path.read_text(encoding='utf-8'))['values']['memo']

    def save(self, value, base=''):
        return self.store.sync([{'key': 'memo', 'base': base, 'value': value}])

    def test_ordinary_save_uses_the_first_name_and_leaves_nothing_behind(self):
        with self.held([]):
            self.save('first')
        self.assertEqual(self.replaced, [self.names[0]])
        self.assertEqual(self.memo(), 'first')
        self.assertEqual(self.staging_files(), [])

    def test_staging_file_another_process_keeps_open_does_not_block_saving(self):
        self.primary.write_text('left open by a hung helper', encoding='utf-8')
        with self.held([self.primary]):
            result = self.save('saved anyway')
            self.assertEqual(result['conflicts'], [])
            self.assertEqual(self.memo(), 'saved anyway')
            self.save('and again', base='saved anyway')
        self.assertEqual(self.memo(), 'and again')
        # 잡혀 있는 파일은 건드리지 못하고, 예비 이름은 남기지 않습니다.
        self.assertEqual(self.primary.read_text(encoding='utf-8'), 'left open by a hung helper')
        self.assertEqual(self.staging_files(), [self.names[0]])

    def test_staging_file_that_cannot_be_renamed_falls_back_and_is_not_retried_each_save(self):
        with patch.object(protrusion.SharedStore, 'STAGING_RETRY', .05), \
                self.held([self.primary], opening=False):
            self.save('one')
            first = list(self.replaced)
            self.save('two', base='one')
        self.assertEqual(self.memo(), 'two')
        self.assertIn(self.names[0], first)
        self.assertEqual(first[-1], self.names[1])
        # 두 번째 저장은 막힌 이름을 다시 기다리지 않습니다.
        self.assertEqual(self.replaced[len(first):], [self.names[1]])

    def test_abandoned_staging_file_is_removed_once_its_holder_lets_go(self):
        with patch.object(protrusion.SharedStore, 'STAGING_RETRY', .05), \
                self.held([self.primary], opening=False):
            self.save('one')
            self.assertEqual(self.staging_files(), [self.names[0]])
        self.save('two', base='one')
        self.assertEqual(self.memo(), 'two')
        self.assertEqual(self.staging_files(), [])

    def test_every_staging_name_held_reports_the_first_error_and_keeps_the_table(self):
        before = self.store.path.read_bytes()
        with self.held(self.store.folder / name for name in self.names):
            with self.assertRaises(PermissionError) as caught:
                self.save('lost')
        self.assertEqual(caught.exception.winerror, 32)
        self.assertIn(self.names[0], str(caught.exception))
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_busy_table_file_gives_up_within_the_time_limit_and_cleans_up(self):
        before = self.store.path.read_bytes()
        error = self.busy(self.store.path)
        with patch.object(protrusion.SharedStore, 'LOCK_TIMEOUT', .3), \
                patch.object(protrusion.SharedStore, 'STAGING_RETRY', .05), \
                patch.object(protrusion.os, 'replace', side_effect=error) as replace:
            started = time.monotonic()
            with self.assertRaises(PermissionError) as caught:
                self.save('lost')
            elapsed = time.monotonic() - started
        self.assertIs(caught.exception, error)
        self.assertGreater(replace.call_count, 1)
        self.assertLess(elapsed, 2)
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertEqual(self.staging_files(), [])

    def test_cleanup_failure_never_replaces_the_real_error(self):
        denied = PermissionError(errno.EACCES, 'Access is denied', str(self.store.path))
        denied.winerror = 5
        real_unlink = Path.unlink

        def unlink(path, *args, **options):
            if Path(path) == self.primary:
                raise self.busy(path)
            return real_unlink(path, *args, **options)

        with patch.object(protrusion.os, 'replace', side_effect=denied), \
                patch.object(Path, 'unlink', unlink):
            with self.assertRaises(PermissionError) as caught:
                self.save('lost')
        self.assertIs(caught.exception, denied)


if __name__ == '__main__':
    unittest.main()
