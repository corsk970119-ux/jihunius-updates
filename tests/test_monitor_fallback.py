"""설비 현황의 예비 서버(사용자 요청 2026-11-26).

평소에는 192.168.0.245에서 읽고, 245와 연결이 끊겼거나 머신 값이 하나도 오지 않을 때 192.168.0.252에서 읽습니다.
245가 다시 값을 주면 돌아옵니다. 252에는 245에 보내던 것과 같은 조회 요청 두 가지만 보냅니다.
소재 사용량 조사의 집계는 245만 봅니다(바꾸지 않음).
"""
import json
import os
import queue
import threading
import time
import tkinter as tk
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

import test_main_window_placement as placement
from test_host_stability import load_app

ROOT = Path(__file__).resolve().parents[1]
MAIN, BACKUP = '192.168.0.245', '192.168.0.252'
GATES = ('192.168.0.11', '192.168.0.12', '192.168.0.13')


class FakeServers:
    """두 가공현황 서버. mode: 'up'(값을 줌) / 'cut'(연결 안 됨) / 'silent'(목록은 주는데 머신 값이 안 옴)."""

    def __init__(self, module):
        self.m = module
        self.mode = {MAIN: 'up', BACKUP: 'up'}
        self.gates = {MAIN: list(GATES), BACKUP: list(GATES)}
        self.calls = []
        self.lock = threading.Lock()

    def program(self, host, ip):
        return ('1' if host == MAIN else '2') + ip.rsplit('.', 1)[1].zfill(3)      # 245: 1011…, 252: 2011…

    def request(self, endpoint, fields, host=MAIN):
        assert self.m._MONITOR_ALLOWED.get(endpoint) == fields.get('ajax_selector'), (endpoint, fields)
        with self.lock:
            self.calls.append((host, endpoint, fields.get('ncgateIP')))
            mode, gates = self.mode[host], list(self.gates[host])
        if mode == 'cut':
            raise ConnectionRefusedError('[WinError 10061] 연결 거부')
        if endpoint == 'monitoring_ajax_setting.php':
            return {'ip': gates}
        ip = fields['ncgateIP']
        if mode == 'silent' or ip not in gates:
            return {'message': 'fail'}
        return {'message': 'success', 'machine_name': 'machine {}'.format(int(ip.rsplit('.', 1)[1]) - 10),
                'program_number': self.program(host, ip), 'state': 'RUN', 'tool_number': '0101'}

    def count(self, host, since=0):
        with self.lock:
            return sum(1 for call in self.calls[since:] if call[0] == host)


class Collected:
    def __init__(self, events):
        self.events, self.latest, self.removed, self.notes, self.errors = events, {}, [], [], []

    def drain(self):
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                return
            if event[0] == 'machine_sample':
                _kind, ip, record, _observed, cancel = event
                if cancel is not None and cancel.is_set():
                    continue                                                    # 물러난 조회의 결과는 화면도 버립니다
                if record is None and cancel is None:
                    self.removed.append(ip); self.latest.pop(ip, None)
                elif record is not None:
                    self.latest[ip] = record['prm_no']
            elif event[0] == 'machine_source':
                self.notes.append(event[1])
            elif event[0] == 'machine_connection':
                self.errors.append(event[1])


class MonitorFallbackTests(unittest.TestCase):
    def setUp(self):
        self.m = load_app()
        self.m.MONITOR_INTERVAL, self.m.MONITOR_RECHECK_SECONDS, self.m.MONITOR_GRACE_SECONDS = .02, .05, .25
        self.servers = FakeServers(self.m)
        self.seen = Collected(queue.Queue())
        self.monitor = self.m.MachineMonitor(self.seen.events, request=self.servers.request)
        self.addCleanup(self.monitor.stop)

    def wait(self, condition, seconds=5, message='시간 안에 바뀌지 않았습니다'):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self.seen.drain()
            if condition():
                return
            time.sleep(.01)
        self.fail('{}: {} / {}'.format(message, self.seen.latest, self.seen.notes))

    def reading(self, host):
        return lambda: (len(self.seen.latest) == len(self.servers.gates[host]) and
                        all(value == self.servers.program(host, ip) for ip, value in self.seen.latest.items()))

    def test_hosts_are_245_first_and_252_as_the_backup(self):
        self.assertEqual(self.m.MONITOR_HOSTS, (MAIN, BACKUP))
        self.assertEqual((self.m.MONITOR_HOST, self.m.MONITOR_FALLBACK_HOST), (MAIN, BACKUP))
        self.assertEqual(self.m.MachineMonitor(queue.Queue()).hosts, (MAIN, BACKUP))
        self.assertEqual(sorted(self.m._MONITOR_ALLOWED), ['monitoring_ajax_setting.php', 'monitoring_ajax_this_machine.php'])

    def test_reads_from_245_and_leaves_252_alone_while_245_works(self):
        self.monitor.start()
        self.wait(self.reading(MAIN))
        time.sleep(.5); self.seen.drain()                                       # 여러 번 다시 확인하는 동안
        self.assertTrue(self.reading(MAIN)())
        self.assertEqual(self.servers.count(BACKUP), 0)                         # 252에는 아무것도 보내지 않음
        self.assertEqual(self.seen.notes, [])
        self.assertEqual(set(self.seen.errors), {None})
        self.assertEqual(self.monitor.active, MAIN)

    def test_cut_connection_to_245_switches_to_252_and_back_when_245_returns(self):
        self.monitor.start()
        self.wait(self.reading(MAIN))
        self.servers.mode[MAIN] = 'cut'
        self.wait(self.reading(BACKUP), message='252로 넘어가지 않았습니다')
        self.assertEqual(self.seen.notes, ['가공현황: 192.168.0.245에서 값이 오지 않아 192.168.0.252에서 읽습니다.'])
        self.assertEqual(self.seen.removed, [])                                 # 같은 머신 주소는 화면에서 내리지 않고 값만 바뀜
        self.assertEqual(self.monitor.active, BACKUP)
        self.assertEqual(self.seen.errors[-1], None)                            # 252에서 읽는 동안은 오류로 알리지 않음
        self.servers.mode[MAIN] = 'up'
        self.wait(self.reading(MAIN), message='245로 돌아오지 않았습니다')
        self.assertEqual(self.seen.notes[1:], ['가공현황: 192.168.0.245에서 다시 읽습니다.'])
        self.assertEqual(self.seen.removed, [])
        time.sleep(.2)                                                          # 물러난 조회가 다 끝난 뒤
        mark = len(self.servers.calls)
        time.sleep(.4); self.seen.drain()
        self.assertEqual(self.servers.count(BACKUP, mark), 0)                   # 돌아온 뒤에는 252에 묻지 않음
        self.assertTrue(self.reading(MAIN)())

    def test_starting_while_245_is_cut_reads_from_252_right_away(self):
        self.servers.mode[MAIN] = 'cut'
        self.monitor.start()
        self.wait(self.reading(BACKUP))
        self.assertEqual(len(self.seen.notes), 1)
        self.servers.mode[MAIN] = 'up'
        self.wait(self.reading(MAIN))

    def test_245_answering_without_machine_values_also_switches_to_252(self):
        self.monitor.start()
        self.wait(self.reading(MAIN))
        self.servers.mode[MAIN] = 'silent'                                       # 목록은 주는데 머신 값이 안 옴
        self.wait(self.reading(BACKUP), message='값이 안 오는데 252로 넘어가지 않았습니다')
        self.assertEqual(len(self.seen.notes), 1)
        time.sleep(.4); self.seen.drain()
        self.assertEqual(self.monitor.active, BACKUP)                           # 245가 값을 줄 때까지 252에 머묾(왔다 갔다 하지 않음)
        self.assertEqual(len(self.seen.notes), 1)
        self.servers.mode[MAIN] = 'up'
        self.wait(self.reading(MAIN))
        self.assertEqual(len(self.seen.notes), 2)

    def test_stays_on_245_when_252_has_no_values_either(self):
        self.servers.mode[MAIN] = self.servers.mode[BACKUP] = 'silent'
        self.monitor.start()
        time.sleep(.8); self.seen.drain()
        self.assertEqual(self.monitor.active, MAIN)
        self.assertEqual(self.seen.notes, [])
        self.assertEqual(self.seen.latest, {})
        self.assertGreater(self.servers.count(BACKUP), 0)                       # 252에도 값이 있는지 물어는 봄
        self.servers.mode[MAIN] = 'up'
        self.wait(self.reading(MAIN))
        self.assertEqual(self.seen.notes, [])

    def test_both_cut_reports_the_245_error_and_recovers_by_itself(self):
        self.servers.mode[MAIN] = self.servers.mode[BACKUP] = 'cut'
        self.monitor.start()
        self.wait(lambda: len(self.seen.errors) >= 2)
        self.assertEqual(set(self.seen.errors), {'[WinError 10061] 연결 거부'})
        self.assertEqual((self.seen.latest, self.seen.notes, self.monitor.active), ({}, [], None))
        self.servers.mode[BACKUP] = 'up'
        self.wait(self.reading(BACKUP))
        self.servers.mode[MAIN] = 'up'
        self.wait(self.reading(MAIN))

    def test_both_cut_after_reading_keeps_the_machines_until_one_returns(self):
        self.monitor.start()
        self.wait(self.reading(MAIN))
        self.servers.mode[MAIN] = self.servers.mode[BACKUP] = 'cut'
        self.wait(lambda: self.seen.errors and self.seen.errors[-1] is not None)
        self.assertEqual(self.seen.removed, [])                                 # 목록에서 내리지 않음(화면에는 '?'로 남음)
        self.assertEqual(self.monitor.active, MAIN)
        self.servers.mode[MAIN] = 'up'
        self.wait(lambda: self.seen.errors[-1] is None)
        self.assertEqual(self.seen.notes, [])

    def test_machine_that_only_245_lists_is_taken_down_when_252_takes_over(self):
        self.servers.gates[BACKUP] = [GATES[0], GATES[1], '192.168.0.19']        # 252의 머신 목록이 조금 다름
        self.monitor.start()
        self.wait(self.reading(MAIN))
        self.servers.mode[MAIN] = 'cut'
        self.wait(self.reading(BACKUP))
        self.assertEqual(self.seen.removed, [GATES[2]])
        self.assertIn('192.168.0.19', self.seen.latest)
        self.servers.mode[MAIN] = 'up'
        self.wait(self.reading(MAIN))
        self.assertEqual(self.seen.removed, [GATES[2], '192.168.0.19'])

    def test_stop_ends_every_query(self):
        self.monitor.start()
        self.wait(self.reading(MAIN))
        self.monitor.stop()
        time.sleep(.2)
        mark = len(self.servers.calls)
        time.sleep(.3)
        self.assertEqual(len(self.servers.calls), mark)

    def test_material_survey_still_reads_only_245(self):
        counter = (ROOT / 'src/material_counter.py').read_text(encoding='utf-8')
        self.assertIn("HOST = '192.168.0.245'", counter)
        for path in sorted((ROOT / 'src').glob('material_*.py')):
            self.assertNotIn(BACKUP, path.read_text(encoding='utf-8'), path.name)   # 집계는 예비 서버로 넘어가지 않음


class RealConnectionTests(unittest.TestCase):
    """진짜 연결로: 주 서버의 문이 닫히면(연결 거부) 예비 서버에 같은 요청을 보냅니다."""

    def serve(self, marker, port=0):
        requests = []

        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'

            def log_message(self, *args):
                pass

            def do_POST(self):
                fields = {k: v[0] for k, v in parse_qs(self.rfile.read(int(self.headers.get('Content-Length', 0))).decode()).items()}
                requests.append((self.path, fields))
                if self.path == '/monitoring_ajax_setting.php':
                    reply = {'ip': ['192.168.0.11']}
                else:
                    reply = {'message': 'success', 'machine_name': 'machine 1', 'program_number': marker, 'state': 'RUN'}
                body = json.dumps(reply).encode()
                self.send_response(200); self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)

        ThreadingHTTPServer.allow_reuse_address = True
        server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        return server, requests

    def close(self, server):
        server.shutdown(); server.server_close()

    def test_refused_connection_to_the_first_server_is_answered_by_the_second(self):
        m = load_app()
        m.MONITOR_INTERVAL, m.MONITOR_RECHECK_SECONDS, m.MONITOR_GRACE_SECONDS, m.MONITOR_TIMEOUT = .03, .08, .4, 1.0
        main, main_requests = self.serve('1001')
        backup, backup_requests = self.serve('2002')
        self.addCleanup(self.close, backup)
        port = main.server_address[1]
        hosts = ('127.0.0.1:{}'.format(port), '127.0.0.1:{}'.format(backup.server_address[1]))
        seen = Collected(queue.Queue())
        monitor = m.MachineMonitor(seen.events, hosts=hosts)                    # 실제 요청 함수(monitor_request·MonitorClient)
        self.addCleanup(monitor.stop)
        monitor.start()

        def wait(value):
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline:
                seen.drain()
                if seen.latest.get('192.168.0.11') == value:
                    return
                time.sleep(.01)
            self.fail('{} 을 받지 못했습니다: {} {}'.format(value, seen.latest, seen.notes))

        wait('1001')
        self.assertEqual(backup_requests, [])
        self.close(main)                                                        # 주 서버 꺼짐
        wait('2002')
        self.assertEqual({path for path, _fields in backup_requests},
                         {'/monitoring_ajax_setting.php', '/monitoring_ajax_this_machine.php'})
        self.assertEqual({fields['ajax_selector'] for _path, fields in backup_requests}, {'loadIPlist', 'callUpdateMachineOne'})
        self.assertEqual(len(seen.notes), 1)
        again, _requests = self.serve('1001', port)                             # 주 서버 다시 켜짐(같은 주소)
        self.addCleanup(self.close, again)
        wait('1001')
        self.assertEqual(len(seen.notes), 2)


@unittest.skipUnless(os.environ.get('DISPLAY') or os.name == 'nt', 'requires Tk display')
class BoardWithBackupServerTests(unittest.TestCase):
    setUp = placement.MainWindowPlacementTests.setUp
    cleanup = placement.MainWindowPlacementTests.cleanup
    close_app = placement.MainWindowPlacementTests.close_app

    def test_board_keeps_showing_machines_from_252_and_the_log_says_so(self):
        self.m.MONITOR_INTERVAL, self.m.MONITOR_RECHECK_SECONDS, self.m.MONITOR_GRACE_SECONDS = .03, .06, .3
        self.m.MONITOR_STALE_SECONDS = .25
        root = tk.Tk(); app = self.m.IntegrationApp(root); self.apps.append(app)
        app.machine_alert_enabled = False
        servers = FakeServers(self.m)
        monitor = self.m.MachineMonitor(app.events, request=servers.request)
        self.addCleanup(monitor.stop)
        threading.Thread(target=monitor._discover, daemon=True).start()          # start 는 이 테스트 틀에서 막아 둠

        def shown():
            return [app.machine_tiles[n][0].itemcget(app.machine_tiles[n][2], 'text') for n in (1, 2, 3)]

        def titles():
            return [app.machine_tiles[n][0].itemcget('machine_title', 'text') for n in (1, 2, 3)]

        def wait(values, seconds=6):
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                root.update()
                if shown() == values and titles() == ['머신1', '머신2', '머신3']:
                    return
                time.sleep(.01)
            self.fail('{} 이 아니라 {} {}'.format(values, shown(), titles()))

        wait(['1011', '1012', '1013'])
        servers.mode[MAIN] = 'cut'
        wait(['2011', '2012', '2013'])                                          # 252의 값으로, '?' 없이
        self.assertEqual(app.machine_conflicts, set())                          # 두 서버 값이 겹친 것으로 보지 않음
        log = app.log.get('1.0', 'end')
        self.assertIn('가공현황: 192.168.0.245에서 값이 오지 않아 192.168.0.252에서 읽습니다.', log)
        self.assertNotIn('가공현황 연결 오류', log)
        servers.mode[MAIN] = 'up'
        wait(['1011', '1012', '1013'])
        self.assertIn('가공현황: 192.168.0.245에서 다시 읽습니다.', app.log.get('1.0', 'end'))
        self.assertEqual([app.machine_tiles[n][0].itemcget(app.machine_tiles[n][2], 'text') for n in range(4, 10)], ['—'] * 6)


if __name__ == '__main__':
    unittest.main()
