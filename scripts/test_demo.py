"""HTTP security and offline demo checks; no calls to Gemini."""
import copy
import http.client
import json
from pathlib import Path
import sys
import threading
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from demo.server import DemoError, DemoServer, DemoState


class DemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = DemoState()
        cls.server = DemoServer(("127.0.0.1", 0), cls.state)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, method="GET", path="/", body=None, headers=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        c.request(method, path, body=body, headers=headers or {})
        response = c.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        c.close()
        return result

    def post(self, payload, headers=None):
        return self.request("POST", "/api/search", json.dumps(payload), headers or {
            "Origin": f"http://127.0.0.1:{self.port}", "Content-Type": "application/json"})

    def test_page_and_security_headers(self):
        status, headers, body = self.request()
        self.assertEqual(status, 200)
        self.assertIn('lang="vi"', body.decode())
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertNotIn("Python", headers["Server"])

    def test_static_assets(self):
        for path in ("/app.js", "/styles.css"):
            self.assertEqual(self.request(path=path)[0], 200)

    def test_snapshot_has_all_results(self):
        status, _, body = self.request(path="/api/data")
        data = json.loads(body)
        self.assertEqual(status, 200)
        self.assertFalse(data["live_enabled"])
        self.assertEqual(sum(len(t["hits"]) for traces in data["traces"].values() for t in traces), 180)
        self.assertEqual(len(data["audit_samples"]), 10)
        self.assertNotIn("GEMINI_API_KEY", body.decode())
        self.assertNotIn(str(ROOT), body.decode())

    def test_pdf_route(self):
        status, headers, body = self.request(path="/api/document")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/pdf")
        self.assertTrue(body.startswith(b"%PDF"))

    def test_private_files_and_traversal(self):
        for path in ("/.env", "/.git/config", "/../STUDENT.md", "/%2e%2e/.env", "/src/embeddings.py",
                     "/api/document?path=.env", "/api/data?file=.env"):
            self.assertEqual(self.request(path=path)[0], 404, path)

    def test_dns_rebinding_host(self):
        self.assertEqual(self.request(headers={"Host": f"attacker.test:{self.port}"})[0], 403)

    def test_cross_origin_requests(self):
        self.assertEqual(self.request(path="/api/data", headers={"Origin": "https://attacker.test"})[0], 403)
        self.assertEqual(self.post({"question": "test"}, {"Origin": "null", "Content-Type": "application/json"})[0], 403)

    def test_post_requires_origin(self):
        self.assertEqual(self.post({"question": "test"}, {"Content-Type": "application/json"})[0], 403)

    def test_invalid_inputs(self):
        for payload in ([], None, {"question": 123}, {"question": "a"}, {"question": "x" * 501},
                        {"question": "hello", "section": {"$ne": "x"}}, {"question": "hello", "path": ".env"}):
            self.assertEqual(self.post(payload)[0], 400, payload)

    def test_size_and_content_type(self):
        h = {"Origin": f"http://127.0.0.1:{self.port}", "Content-Type": "application/json"}
        self.assertEqual(self.request("POST", "/api/search", "x" * 4097, h)[0], 413)
        h["Content-Type"] = "text/plain"
        self.assertEqual(self.request("POST", "/api/search", "{}", h)[0], 415)
        h["Content-Type"] = "application/json"
        self.assertEqual(self.request("POST", "/api/search", "{broken", h)[0], 400)
        self.assertEqual(self.request("POST", "/api/search", "[" * 1100 + "]" * 1100, h)[0], 400)

    def test_offline_search_never_calls_provider(self):
        self.assertEqual(self.post({"question": "Sinh viên học bao lâu?"})[0], 503)
        self.assertIsNone(self.state.embedder)

    def test_provider_errors_are_redacted(self):
        state = copy.copy(self.state)
        state.live = True
        state.lock = threading.Lock()
        class BrokenProvider:
            def embed_query(self, _question):
                raise RuntimeError("private-test-value in provider URL")
        state.embedder = BrokenProvider()
        with self.assertLogs("day06.demo", level="WARNING") as logs:
            with self.assertRaises(DemoError) as error:
                state.search({"question": "Một câu hỏi thử"})
        self.assertEqual(error.exception.status, 503)
        self.assertNotIn("private-test-value", str(logs.output) + error.exception.message)

    def test_live_concurrency_is_bounded(self):
        state = copy.copy(self.state)
        state.live = True
        state.lock = threading.Lock()
        state.lock.acquire()
        try:
            with self.assertRaises(DemoError) as error:
                state.search({"question": "Một câu hỏi thử"})
            self.assertEqual(error.exception.status, 429)
        finally:
            state.lock.release()

    def test_cannot_bind_public_interface(self):
        with self.assertRaises(ValueError):
            DemoServer(("0.0.0.0", 0), self.state)


if __name__ == "__main__":
    unittest.main(verbosity=2)
