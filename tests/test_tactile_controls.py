import unittest
from unittest.mock import Mock
import test_main_window_placement as placement


class TactileControlsTests(unittest.TestCase):
    setUp = placement.MainWindowPlacementTests.setUp
    cleanup = placement.MainWindowPlacementTests.cleanup
    close_app = placement.MainWindowPlacementTests.close_app
    launch = placement.MainWindowPlacementTests.launch

    def test_icons_survive_native_disabled_state_and_invoke_correct_machine(self):
        app = self.launch()
        quick = app.material_quick
        quick.submit = Mock()
        for machine, row in quick.rows.items():
            for action in ('defect', 'rotate'):
                button = row[action]
                self.assertTrue(button.cget('image'))
                self.assertEqual(str(button.cget('compound')), 'left')
                button.state(['disabled'])
                button.invoke()
                quick.submit.assert_not_called()
                button.state(['!disabled'])
                button.invoke()
                quick.submit.assert_called_once_with(action, machine)
                quick.submit.reset_mock()

    def test_full_status_colors_keep_prm_stale_and_offline_semantics(self):
        app = self.launch()
        app.machine_alert_enabled = False
        records = {1: {'light':'green','prm_no':'0007'},
                   2: {'light':'red','prm_no':'1234','_stale':True},
                   3: {'light':'yellow','prm_no':'invalid'}}
        app.apply_machine_status(records)
        for machine, color in ((1,'#2fb36b'),(2,'#e5484d'),(3,'#f0c440'),(4,'#25334b')):
            tile, surface, number = app.machine_tiles[machine]
            self.assertEqual(tile.type(surface), 'polygon')
            self.assertEqual(tile.itemcget(surface,'fill'), color)
        self.assertEqual(app.machine_tiles[1][0].itemcget(app.machine_tiles[1][2],'text'),'0007')
        self.assertIn('?',app.machine_tiles[2][0].itemcget('machine_title','text'))
        self.assertEqual(app.machine_tiles[3][0].itemcget(app.machine_tiles[3][2],'text'),'—')
        before = app.window.tk.call('image','names')
        for _ in range(30):app.apply_machine_status(records)
        self.assertEqual(app.window.tk.call('image','names'),before)
        app.apply_machine_status(records,online=False)
        for tile, surface, number in app.machine_tiles.values():
            self.assertEqual(tile.itemcget(surface,'fill'),'#25334b')
            self.assertEqual(tile.itemcget(number,'text'),'—')
        app.show_machine_details(1)
        self.assertTrue(app.machine_detail_dialog.winfo_exists())
        app.show_machine_details(1)
        self.assertIsNone(app.machine_detail_dialog)


if __name__ == '__main__':unittest.main()
