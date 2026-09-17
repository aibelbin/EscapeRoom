import json
import sys
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


class ServerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.path = Path(self._tmp.name) / "leaderboard.json"
        self._prev = main.LEADERBOARD_PATH
        main.LEADERBOARD_PATH = self.path
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), main.Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.host, self.port = self.httpd.server_address[:2]

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        main.LEADERBOARD_PATH = self._prev
        self._tmp.cleanup()

    def _conn(self):
        return HTTPConnection(self.host, self.port, timeout=2)

    def test_get_leaderboard_empty(self):
        conn = self._conn()
        conn.request("GET", "/leaderboard")
        res = conn.getresponse()
        body = json.loads(res.read())
        self.assertEqual(res.status, 200)
        self.assertEqual(body, {"entries": []})

    def test_post_finish_saves(self):
        payload = json.dumps({"name": "Ada Lovelace", "time_ms": 492340}).encode()
        conn = self._conn()
        conn.request(
            "POST",
            "/finish",
            body=payload,
            headers={"Content-Type": "application/json"},
        )
        res = conn.getresponse()
        body = json.loads(res.read())
        self.assertEqual(res.status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(body["entries"][0]["name"], "Ada Lovelace")
        self.assertTrue(self.path.is_file())

    def test_post_finish_rejects_empty_name(self):
        payload = json.dumps({"name": "  ", "time_ms": 1000}).encode()
        conn = self._conn()
        conn.request(
            "POST",
            "/finish",
            body=payload,
            headers={"Content-Type": "application/json"},
        )
        res = conn.getresponse()
        body = json.loads(res.read())
        self.assertEqual(res.status, 400)
        self.assertFalse(body["ok"])
        self.assertEqual(body["error"], "Need a name")


if __name__ == "__main__":
    unittest.main()
