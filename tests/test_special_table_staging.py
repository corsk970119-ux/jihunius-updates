"""A handle left open on the one staging file must not block the shared special table.

Same weakness as the protrusion table's field report of 2026-11-16
("[WinError 32] ... '.jihunius_protrusion_stage_v1.tmp'").
"""
import contextlib
import errno
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import special_table as m


class SpecialTableStagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = m.TableStore(Path(self.tmp.name) / 'shared')
        self.store.folder.mkdir()
        self.notes = self.store.sync()['state']['notes']
        self.primary = self.store.folder / '.special_table_pending.tmp'
        self.names = m.staging_names(self.primary)

    @staticmethod
    def busy(path):
        error = PermissionError(errno.EACCES, 'The process cannot access the file', str(path))
        error.winerror = 32
        return error

    def held(self, paths, opening=True):
        paths = {Path(path) for path in paths}
        real_open, real_replace, real_unlink = os.open, os.replace, os.unlink
        stack = contextlib.ExitStack()

        def open_(path, flags, mode=0o777, **options):
            if opening and Path(path) in paths:
                raise self.busy(path)
            return real_open(path, flags, mode, **options)

        def replace(source, target, **options):
            if Path(source) in paths:
                raise self.busy(source)
            return real_replace(source, target, **options)

        def unlink(path, **options):
            if Path(path) in paths:
                raise self.busy(path)
            return real_unlink(path, **options)

        stack.enter_context(patch.object(m.os, 'open', open_))
        stack.enter_context(patch.object(m.os, 'replace', replace))
        stack.enter_context(patch.object(m.os, 'unlink', unlink))
        return stack

    def staging_files(self):
        return sorted(path.name for path in self.store.folder.iterdir() if path.name.endswith('.tmp'))

    def save(self, value):
        reply = self.store.sync([{'kind': 'notes', 'base': self.notes, 'value': value}])
        self.assertEqual(reply['conflicts'], [])
        self.notes = value
        return reply

    def saved_notes(self):
        return m.read_json(self.store.path)['notes']

    def test_spare_names_are_a_small_fixed_set_beside_the_first_name(self):
        self.assertEqual(self.names[0], self.primary)
        self.assertEqual(len(self.names), 8)
        self.assertEqual(self.names[1].name, '.special_table_pending.1.tmp')
        self.assertEqual(len({name.name for name in self.names}), 8)
        self.assertTrue(all(name.parent == self.store.folder for name in self.names))

    def test_ordinary_save_leaves_no_staging_file(self):
        self.save('first')
        self.assertEqual(self.saved_notes(), 'first')
        self.assertEqual(self.staging_files(), [])

    def test_staging_file_another_process_keeps_open_does_not_block_saving(self):
        self.primary.write_text('left open by a hung helper', encoding='utf-8')
        with self.held([self.primary]):
            self.save('saved anyway')
            self.save('and again')
        self.assertEqual(self.saved_notes(), 'and again')
        self.assertEqual(self.primary.read_text(encoding='utf-8'), 'left open by a hung helper')
        self.assertEqual(self.staging_files(), [self.primary.name])

    def test_staging_file_that_cannot_be_renamed_falls_back(self):
        with patch.object(m, 'STAGING_RETRY', .05), self.held([self.primary], opening=False):
            self.save('saved anyway')
        self.assertEqual(self.saved_notes(), 'saved anyway')

    def test_every_staging_name_held_reports_the_first_error_and_keeps_the_table(self):
        before = self.store.path.read_bytes()
        with self.held(self.names):
            with self.assertRaises(PermissionError) as caught:
                self.store.sync([{'kind': 'notes', 'base': self.notes, 'value': 'lost'}])
        self.assertEqual(caught.exception.winerror, 32)
        self.assertIn(self.primary.name, str(caught.exception))
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_other_rename_errors_are_raised_at_once(self):
        denied = PermissionError(errno.EACCES, 'Access is denied', str(self.store.path))
        denied.winerror = 5
        before = self.store.path.read_bytes()
        with patch.object(m.os, 'replace', side_effect=denied) as replace:
            with self.assertRaises(PermissionError) as caught:
                self.store.sync([{'kind': 'notes', 'base': self.notes, 'value': 'lost'}])
        self.assertIs(caught.exception, denied)
        self.assertEqual(replace.call_count, 1)
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertEqual(self.staging_files(), [])


if __name__ == '__main__':
    unittest.main()
