from __future__ import annotations

import json
from datetime import datetime
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlparse
import webbrowser

from leaderboard import LeaderboardError, add_finish, load, ranked

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
LEADERBOARD_PATH = ROOT / "leaderboard.json"
HOST = "127.0.0.1"
PORT = 8766

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path in ("/", "/index.html"):
            return self._send_file(WEB / "index.html")
        if path == "/leaderboard":
            entries = ranked(load(LEADERBOARD_PATH)["entries"])
            return self._send_json(200, {"entries": entries})
        rel = path.lstrip("/")
        candidate = (WEB / rel).resolve()
        if WEB.resolve() in candidate.parents and candidate.is_file():
            return self._send_file(candidate)
        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/finish":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            return self._send_json(400, {"ok": False, "error": "Could not save"})
        name = payload.get("name", "")
        time_ms = payload.get("time_ms", 0)
        try:
            result = add_finish(
                LEADERBOARD_PATH,
                name=str(name),
                time_ms=int(time_ms),
                finished_at=datetime.now().isoformat(timespec="seconds"),
            )
        except LeaderboardError as exc:
            return self._send_json(400, {"ok": False, "error": str(exc)})
        except (TypeError, ValueError):
            return self._send_json(400, {"ok": False, "error": "Start the clock first"})
        except OSError:
            return self._send_json(500, {"ok": False, "error": "Could not save"})
        return self._send_json(200, {"ok": True, "entries": result["entries"]})

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        if not path.is_file():
            self.send_error(404, "Not found")
            return
        data = path.read_bytes()
        ctype = MIME.get(path.suffix.lower(), "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"Leaderboard at {url}")
    print("Ctrl+C to stop")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")
        server.server_close()


if __name__ == "__main__":
    main()
