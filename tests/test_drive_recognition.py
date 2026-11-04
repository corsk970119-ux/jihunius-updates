"""Drive listing latency and stale-preview regressions; local fixtures only."""
from pathlib import Path
import queue
import tempfile
import threading
import unittest
from unittest.mock import patch

from test_host_stability import load_app, host


class DriveRecognitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_app()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'O1001').write_text('program')

    def test_unrelated_nonremovable_candidate_cannot_delay_the_card(self):
        m = self.module
        first, card = self.root / 'network', self.root / 'card'
        card.mkdir()
        original_resolve = Path.resolve
        def resolve(path, *args, **kwargs):
            if path == first:
                raise AssertionError('non-removable candidate triggered a filesystem probe')
            return original_resolve(path, *args, **kwargs)
        with patch.object(m, 'DESTINATION_CANDIDATES', (str(first), str(card))), \
             patch.object(m, 'get_drive_type', side_effect=lambda p: 4 if p == first else 2), \
             patch.object(Path, 'resolve', resolve):
            self.assertEqual(m.select_destination(), card)

    def test_listing_is_usable_while_modifier_metadata_is_still_blocked(self):
        m = self.module
        app = host(m)
        entered, release = threading.Event(), threading.Event()
        original = m.card_modifier_signature
        def slow_signature(path, names=None):
            entered.set()
            release.wait(2)
            return original(path, names=names)
        with patch.object(m, 'select_destination', return_value=self.root), \
             patch.object(m, 'card_modifier_signature', side_effect=slow_signature):
            try:
                app.refresh_destination()
                self.assertTrue(entered.wait(1))
                app.drain_events()
                self.assertEqual(app.destination, self.root)
                self.assertEqual(app.drive_contents.items, ['O1001'])
                self.assertTrue(app.drive_refresh_loading)
                self.assertFalse(app.busy)
                # Automatic modifier writes must wait for the full identity probe.
                app.check_card_modifier()
                self.assertFalse(app.busy)
            finally:
                release.set()
                event = app.events.get(timeout=2)
                self.assertEqual(event[0], 'drive_refreshed')
                app.finish_drive_refresh(*event[1:])
        self.assertFalse(app.drive_refresh_loading)
        self.assertEqual(app.drive_contents.items, ['O1001'])

    def test_delayed_preview_cannot_reappear_after_invalidation_busy_or_close(self):
        m = self.module
        for state in ('invalidated', 'busy', 'washing', 'closed'):
            with self.subTest(state=state):
                app = host(m)
                entered, release = threading.Event(), threading.Event()
                original = m.card_modifier_signature
                def slow_signature(path, names=None):
                    entered.set(); release.wait(2)
                    return original(path, names=names)
                with patch.object(m, 'select_destination', return_value=self.root), \
                     patch.object(m, 'card_modifier_signature', side_effect=slow_signature):
                    try:
                        app.refresh_destination(); self.assertTrue(entered.wait(1))
                        if state == 'invalidated': app.drive_refresh_generation += 1
                        elif state == 'busy': app.busy = True
                        elif state == 'washing': app.wash_app.busy = True
                        else: app._suite_stopped = True
                        app.drain_events()
                        self.assertIsNone(app.destination)
                        self.assertEqual(app.drive_contents.items, [])
                    finally:
                        release.set()
                        # Retire the worker before patch teardown, including a
                        # queued preview when closed drain_events intentionally stops.
                        while True:
                            event = app.events.get(timeout=2)
                            if event[0] == 'drive_refreshed': break
                        app.finish_drive_refresh(*event[1:])

    def test_waiting_action_uses_early_listing_but_still_checks_before_writing(self):
        m = self.module
        app = host(m)
        entered, release = threading.Event(), threading.Event()
        original = m.card_modifier_signature
        def slow_signature(path, names=None):
            entered.set(); release.wait(2)
            return original(path, names=names)
        with patch.object(m, 'select_destination', return_value=self.root), \
             patch.object(m, 'card_modifier_signature', side_effect=slow_signature), \
             patch.object(m, 'validate_fixed_destination', side_effect=m.WorkError('card removed')):
            try:
                app.start_empty()
                self.assertTrue(entered.wait(1))
                event = app.events.get(timeout=1)
                self.assertEqual(event[0], 'drive_listing')
                app.finish_drive_listing(*event[1:])
                done = app.events.get(timeout=1)
                self.assertEqual(done[0], 'done')
                self.assertIsInstance(done[3], m.WorkError)
                self.assertEqual(str(done[3]), 'card removed')
                self.assertIsNone(app.drive_action_pending)
                self.assertTrue((self.root / 'O1001').exists())
                app.finish_drive_listing(*event[1:])
                self.assertTrue(app.events.empty(), 'duplicate preview must not repeat a destructive action')
            finally:
                release.set()
                while True:
                    event = app.events.get(timeout=2)
                    if event[0] == 'drive_refreshed': break
                app.finish_drive_refresh(*event[1:])


if __name__ == '__main__':
    unittest.main()
