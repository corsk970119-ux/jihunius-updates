"""Manual edits remain synchronized independently of telemetry collection."""
import time
import unittest
import test_material_sync as service


class ManualMaterialServiceTests(unittest.TestCase):
    setUp = service.ServiceTests.setUp
    feed = service.ServiceTests.feed
    command = service.ServiceTests.command

    def prepare(self):
        self.a.set_collection(True)
        for program in ('1001', '1002', '1003'):
            self.feed(program)
        self.other = service.sync.RPCClient('127.0.0.1', self.a.port, 'a' * 64)
        self.assertTrue(self.c.call('command', self.command('register_stock', ['14', 3]))['ok'])

    def apply(self, method, args=None, other=False):
        result = (self.other if other else self.c).call('command', self.command(method, args))
        self.assertTrue(result['ok'], result)
        return result

    def row(self):
        return self.c.call('state')['rows'][0]

    def test_both_pcs_can_edit_while_owner_collection_off_without_resuming_mass_counts(self):
        self.prepare()
        original = self.row()['active_material']
        self.a.set_collection(False)
        self.apply('defect', other=True)
        self.apply('switch_14')
        self.assertEqual(self.row()['parked']['material_id'], original)
        self.apply('switch_14', other=True)
        self.assertEqual((self.row()['active_material'], self.row()['good']), (original, 1))
        self.apply('toggle_mass_mode', other=True)
        self.apply('defect')
        self.apply('switch_14')
        self.assertTrue(self.row()['mass_mode'])
        self.apply('switch_14',other=True)
        self.assertTrue(self.row()['mass_mode'])
        self.apply('rotate', [1, False], other=True)
        self.assertTrue(self.row()['mass_mode'])
        self.assertEqual(self.row()['good'], 0)
        self.assertTrue(self.row()['gap'])
        self.apply('toggle_mass_mode')
        state = self.other.call('state')
        self.assertFalse(state['collection'])
        self.assertFalse(state['rows'][0]['mass_mode'])
        self.assertEqual([r['quantity'] for r in state['inventory']], [9, None, None, 2])
        self.assertFalse(self.c.call('command', self.command('defect'))['ok'])
        self.assertEqual(self.row()['good'], 0)
        self.a.set_collection(True)
        self.feed('8001')
        self.assertEqual(self.row()['good'],0)
        self.feed('8002')
        self.assertEqual(self.row()['good'],1)

    def test_off_competing_pcs_and_retry_debit_only_one_new_14_rod(self):
        self.prepare()
        self.a.set_collection(False)
        first = self.command('switch_14')
        competing = self.command('switch_14')
        competing['client'] = 'another-pc'
        accepted = self.c.call('command', first)
        self.assertTrue(accepted['ok'], accepted)
        self.assertEqual(self.other.call('command', first), accepted)
        self.assertFalse(self.other.call('command', competing)['ok'])
        self.assertEqual(self.c.call('state')['inventory'][3]['quantity'], 2)
        self.assertEqual(self.row()['material_type'], '14')

    def test_unavailable_source_allows_manual_boundary_and_drops_pre_boundary_requests(self):
        self.prepare()
        before = time.monotonic()
        def unavailable(*args):
            raise ValueError('source unavailable')
        self.a.collector.checkpoint = unavailable
        self.apply('rotate', [1, False])
        new = self.row()['active_material']
        self.assertTrue(self.row()['gap'])
        self.assertEqual(self.row()['good'], 0)
        for program in ('2001', '2002'):
            self.a.samples.put(('sample', '192.168.1.10', 1,
                dict(machine=1, program=program, state='RUN', part_count='0',
                     _requested_monotonic=before), time.time(), None, None))
        for program, expected in (('3001', 0), ('3002', 1)):
            self.a.samples.put(('sample', '192.168.1.10', 1,
                dict(machine=1, program=program, state='RUN', part_count='0',
                     _requested_monotonic=time.monotonic()), time.time(), None, None))
            end = time.monotonic() + 2
            while time.monotonic() < end and self.row()['program'] != program:
                time.sleep(.01)
            self.assertEqual(self.row()['program'], program)
            self.assertEqual((self.row()['active_material'], self.row()['good']), (new, expected))

    def test_healthy_running_checkpoint_counts_before_manual_rotation_then_keeps_collecting(self):
        self.prepare()
        def running(n, token):
            self.a.samples.put(('sample', '192.168.1.10', 1,
                dict(machine=n, program='1004', state='RUN', part_count='0'),
                time.time(), token, None))
        self.a.collector.checkpoint = running
        previous = self.row()['active_material']
        self.apply('rotate', [1, False])
        self.assertNotEqual(self.row()['active_material'], previous)
        history = self.c.call('read', dict(name='history', args=[1, 10]))
        ended = next(r for r in history if r['id'] == previous)
        self.assertEqual(ended['good'], 3)
        self.assertEqual(self.row()['good'], 0)
        self.assertTrue(self.c.call('state')['collection'])

    def test_paused_manual_edits_can_be_undone_without_crossing_mode_boundary(self):
        self.prepare()
        self.apply('defect')
        original=self.row()['active_material']
        self.a.set_collection(False)
        self.apply('toggle_mass_mode')
        self.assertEqual(self.row()['undo_label'],'')
        self.assertFalse(self.c.call('command',self.command('undo'))['ok'])
        for method,args in (('defect',[1]),('rotate',[1,False]),('switch_14',[1])):
            with self.subTest(method=method):
                self.apply(method,args,other=True)
                self.assertTrue(self.row()['undo_label'])
                self.apply('undo')
                row=self.row()
                self.assertTrue(row['mass_mode'])
                self.assertEqual((row['active_material'],row['good']),(original,1))
                self.assertEqual([r['quantity'] for r in self.c.call('state')['inventory']],[10,None,None,3])
                self.assertEqual(row['undo_label'],'')
        self.apply('toggle_mass_mode')
        self.assertFalse(self.c.call('command',self.command('undo'))['ok'])


class CollectorBoundaryStampTests(unittest.TestCase):
    def test_sample_request_stamp_precedes_network_response(self):
        import queue
        import material_counter as core
        output=queue.Queue();began=[]
        def request(endpoint,fields):
            if endpoint=='monitoring_ajax_setting.php':return dict(ip=['192.168.1.10'])
            began.append(time.monotonic())
            return dict(message='success',machine_name='machine 1',program_number='1001',state='RUN')
        collector=core.Collector(output,request=request)
        self.addCleanup(collector.close);collector.start()
        deadline=time.monotonic()+3;sample=None
        while time.monotonic()<deadline:
            event=output.get(timeout=3)
            if event[0]=='sample':sample=event[3];break
        self.assertIsNotNone(sample)
        self.assertLessEqual(sample['_requested_monotonic'],began[0])
        self.assertEqual(sample['program'],'1001')
