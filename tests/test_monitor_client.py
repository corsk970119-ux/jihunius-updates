"""Machine monitor keeps one connection per machine and recovers from dropped connections."""
import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from test_host_stability import load_app

FIELDS = {"ajax_selector": "callUpdateMachineOne", "ncgateIP": "192.168.0.11"}


def make_server(mode):
    connections = []

    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def setup(self):
            super().setup()
            connections.append(self.client_address)

        def log_message(self, *args):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers.get('Content-Length', 0)))
            body = json.dumps({'ok': True, 'path': self.path}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            if mode == 'close':
                self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(body)
            if mode in ('close', 'drop'):
                # 'drop' closes without announcing it, like a server idle timeout.
                self.close_connection = True

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, connections


class MonitorClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load_app()

    def client(self, server):
        port = server.server_address[1]
        return self.m.MonitorClient(lambda: HTTPConnection('127.0.0.1', port, timeout=2))

    def run_mode(self, mode):
        server, connections = make_server(mode)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        client = self.client(server)
        self.addCleanup(client.close)
        results = [client.request("monitoring_ajax_this_machine.php", FIELDS) for _ in range(4)]
        self.assertEqual(results, [{'ok': True, 'path': '/monitoring_ajax_this_machine.php'}] * 4)
        return connections

    def test_keep_alive_reuses_one_connection(self):
        self.assertEqual(len(self.run_mode('keep')), 1)

    def test_connection_close_server_still_works(self):
        self.assertEqual(len(self.run_mode('close')), 4)

    def test_silently_dropped_connection_is_retried_once(self):
        self.assertGreaterEqual(len(self.run_mode('drop')), 2)

    def test_only_existing_read_requests_are_allowed(self):
        with self.assertRaises(ValueError):
            self.m.MonitorClient(lambda: None).request("monitoring_ajax_this_machine.php",
                                                       {"ajax_selector": "save"})

    def test_unreachable_server_raises_without_retry_loop(self):
        server, _ = make_server('keep')
        port = server.server_address[1]
        server.shutdown()
        server.server_close()
        calls = []

        def factory():
            calls.append(1)
            return HTTPConnection('127.0.0.1', port, timeout=1)
        client = self.m.MonitorClient(factory)
        with self.assertRaises(OSError):
            client.request("monitoring_ajax_this_machine.php", FIELDS)
        self.assertEqual(len(calls), 1)


if __name__ == '__main__':
    unittest.main()
