"""Loopback-only demo. Serves an explicit allowlist, never the repo directory."""
import argparse
import json
import logging
import math
from pathlib import Path
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
STATIC = Path(__file__).resolve().parent / "static"
SECTIONS = {"quy_che_dao_tao", "hoc_bong_hoc_phi", "cong_tac_sinh_vien", "tot_nghiep_khen_thuong"}
ASSETS = {"/": ("index.html", "text/html; charset=utf-8"),
          "/app.js": ("app.js", "text/javascript; charset=utf-8"),
          "/styles.css": ("styles.css", "text/css; charset=utf-8")}
LOGGER = logging.getLogger("day06.demo")


class DemoError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


class DemoState:
    def __init__(self, root=ROOT, live=False):
        self.root = Path(root)
        self.live = live
        self.lock = threading.Lock()
        self.last_live = float("-inf")
        self.embedder = None
        self.client = None
        self.data = self._load()

    def _read(self, name):
        return json.loads((self.root / name).read_text(encoding="utf-8"))

    def _load(self):
        manifest = self._read("data/manifest.json")
        summary = self._read("results/benchmark_summary.json")
        questions = self._read("benchmark/benchmark_questions.json")
        traces = {s: self._read(f"results/traces_strategy_{s}.json") for s in "abc"}
        student = (self.root / "STUDENT.md").read_text(encoding="utf-8")
        name = next((line.split(":", 1)[1].strip() for line in student.splitlines()
                     if line.startswith("- Họ và tên:")), "Học viên")
        # Explicit public fields: never serialize environment, clients or local paths.
        public_manifest = {k: manifest.get(k) for k in (
            "title", "total_content_pages", "total_physical_pages", "total_content_characters",
            "sections", "nature_of_corpus", "provenance_limitations", "sha256")}
        from src.ingestion import load_pdf
        from src.chunking import fixed_size, by_paragraph
        pages, _ = load_pdf(self.root / "data/so_tay_sinh_vien_2024.pdf",
                            "so-tay-sinh-vien-2024", "data/so_tay_sinh_vien_2024.pdf")
        all_chunks = {c.chunk_id: c.text for p in pages for fn in (fixed_size, by_paragraph) for c in fn(p)}
        audit = self._read("results/audit_report.json")
        samples = [{**sample, **{strategy: {**sample[strategy], "text": all_chunks[sample[strategy]["chunk_id"]]}
                    for strategy in ("strategy_a", "strategy_b")}}
                   for sample in audit["coherence"]["details"]]
        return {"student": {"name": name, "id": "2A202603534", "class": "K5-L3A"},
                "manifest": public_manifest, "summary": summary, "questions": questions,
                "traces": traces, "audit": audit, "audit_samples": samples,
                "live_enabled": self.live, "mode": "recorded"}

    def search(self, payload):
        if not isinstance(payload, dict) or set(payload) - {"question", "section"}:
            raise DemoError(400, "Dữ liệu truy vấn không hợp lệ.")
        question = payload.get("question")
        section = payload.get("section") or None
        if not isinstance(question, str) or not 3 <= len(question.strip()) <= 500:
            raise DemoError(400, "Câu hỏi cần từ 3 đến 500 ký tự.")
        if section is not None and (not isinstance(section, str) or section not in SECTIONS):
            raise DemoError(400, "Phạm vi tra cứu không hợp lệ.")
        if not self.live:
            raise DemoError(503, "Tra cứu trực tiếp chưa bật. Khởi động với --live để dùng Gemini.")
        if not self.lock.acquire(blocking=False):
            raise DemoError(429, "Một truy vấn đang chạy. Vui lòng đợi kết quả.")
        try:
            if time.monotonic() - self.last_live < 5:
                raise DemoError(429, "Vui lòng đợi 5 giây giữa hai lần tra cứu.")
            self.last_live = time.monotonic()
            if self.embedder is None:
                # Imports and provider initialization are deferred until an explicit live query.
                import chromadb
                from chromadb.config import Settings
                from src.embeddings import GeminiEmbedder
                database = self.root / "results/chroma_db"
                if not (database / "chroma.sqlite3").is_file():
                    raise DemoError(503, "Chưa có vector database. Chạy pipeline trước khi tra cứu trực tiếp.")
                client = chromadb.PersistentClient(path=str(database), settings=Settings(anonymized_telemetry=False))
                for s in "abc":
                    if client.get_collection(f"strategy_{s}").count() == 0:
                        raise DemoError(503, "Vector database chưa đủ ba cấu hình.")
                self.embedder = GeminiEmbedder(max_retries=2, timeout_ms=15000, validate_dimensions=False)
                self.client = client
            vector = self.embedder.embed_query(question.strip())
            if len(vector) != 3072 or not all(math.isfinite(x) for x in vector):
                raise DemoError(502, "Embedding trả về không hợp lệ.")
            output = {}
            for s in "abc":
                args = {"query_embeddings": [vector], "n_results": 3}
                if s == "c" and section:
                    args["where"] = {"section": section}
                r = self.client.get_collection(f"strategy_{s}").query(**args)
                output[s] = [{"rank": i + 1, "chunk_id": cid, "text": r["documents"][0][i],
                              "score": round(1 - r["distances"][0][i], 4),
                              "distance": round(r["distances"][0][i], 4),
                              **{k: r["metadatas"][0][i].get(k) for k in ("page", "section", "source", "document_id")}}
                             for i, cid in enumerate(r["ids"][0])]
            return {"mode": "live", "question": question.strip(), "section": section, "hits": output}
        except DemoError:
            raise
        except Exception as exc:
            # Provider exceptions may contain URLs, credentials or user text.
            LOGGER.warning("Live query failed (%s)", type(exc).__name__)
            raise DemoError(503, "Chưa truy vấn được Gemini/Chroma. Kiểm tra key, kết nối và database ở máy chủ.") from None
        finally:
            self.lock.release()


class DemoServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, state):
        if address[0] != "127.0.0.1":
            raise ValueError("Demo must bind to 127.0.0.1")
        self.state = state
        super().__init__(address, DemoHandler)


class DemoHandler(BaseHTTPRequestHandler):
    server_version = "Day06Demo"
    sys_version = ""

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, *_args):
        # Avoid logging query text, user-controlled URLs or secrets.
        return

    def _guard(self, post=False):
        port = self.server.server_address[1]
        allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        hosts = self.headers.get_all("Host", [])
        if len(hosts) != 1 or hosts[0].lower() not in allowed_hosts:
            raise DemoError(403, "Host không hợp lệ.")
        origins = self.headers.get_all("Origin", [])
        allowed_origins = {"http://" + h for h in allowed_hosts}
        if len(origins) > 1 or (origins and origins[0] not in allowed_origins) or (post and not origins):
            raise DemoError(403, "Nguồn yêu cầu không hợp lệ.")

    def _send(self, status, body, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status, data):
        self._send(status, json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8"))

    def do_GET(self):
        try:
            self._guard()
            parts = urlsplit(self.path)
            if parts.query:
                raise DemoError(404, "Không tìm thấy tài nguyên.")
            path = parts.path
            if path in ASSETS:
                file, mime = ASSETS[path]
                self._send(200, (STATIC / file).read_bytes(), mime)
            elif path == "/api/data":
                self._json(200, self.server.state.data)
            elif path == "/api/document":
                body = (self.server.state.root / "data/so_tay_sinh_vien_2024.pdf").read_bytes()
                self._send(200, body, "application/pdf")
            else:
                raise DemoError(404, "Không tìm thấy tài nguyên.")
        except DemoError as exc:
            self._json(exc.status, {"error": exc.message})
        except (OSError, ValueError):
            self._json(503, {"error": "Không đọc được dữ liệu demo. Kiểm tra các file kết quả trong repo."})

    def do_POST(self):
        try:
            self._guard(post=True)
            if self.path != "/api/search":
                raise DemoError(404, "Không tìm thấy chức năng.")
            lengths = self.headers.get_all("Content-Length", [])
            if self.headers.get("Transfer-Encoding") or len(lengths) != 1:
                raise DemoError(400, "Độ dài yêu cầu không hợp lệ.")
            try:
                length = int(lengths[0])
            except ValueError:
                raise DemoError(400, "Độ dài yêu cầu không hợp lệ.") from None
            if not 0 < length <= 4096:
                raise DemoError(413, "Yêu cầu quá lớn hoặc rỗng.")
            if self.headers.get("Content-Type", "").split(";")[0].lower() != "application/json":
                raise DemoError(415, "Chỉ nhận dữ liệu JSON.")
            try:
                raw = self.rfile.read(length)
                if len(raw) != length:
                    raise ValueError("Incomplete body")
                payload = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeError, RecursionError):
                raise DemoError(400, "Nội dung JSON không hợp lệ.") from None
            self._json(200, self.server.state.search(payload))
        except DemoError as exc:
            self._json(exc.status, {"error": exc.message})
        except (OSError, ValueError):
            self._json(400, {"error": "Không xử lý được yêu cầu."})

    def do_OPTIONS(self):
        self._json(405, {"error": "Phương thức không được hỗ trợ."})

    def do_HEAD(self):
        self.do_GET()


def main():
    parser = argparse.ArgumentParser(description="Day 06 local demo")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--live", action="store_true", help="Enable explicit Gemini searches (uses API quota)")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535")
    try:
        server = DemoServer(("127.0.0.1", args.port), DemoState(live=args.live))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Cannot start demo ({type(exc).__name__}); check artifacts and port.\n")
    print(f"Day 06 demo: http://127.0.0.1:{args.port}", flush=True)
    print("Mode: " + ("recorded + live search" if args.live else "recorded benchmark; no API calls"), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
