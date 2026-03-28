"""
interview_server.py
Serves interview HTML files with correct MIME types AND accepts POST /submit
so the interview page can send results back without navigating the Streamlit tab.

Flow:
  1. Interview page completes → POST /submit with JSON transcript
  2. Server writes transcript to static/iv_result_{id}.json
  3. Streamlit polls for that file every 3s via st.rerun()
  4. When file found → read transcript → evaluate → show report
  5. No URL navigation → no session loss → no login redirect
"""
from __future__ import annotations

import functools
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

_SERVER   = None
_PORT     = int(os.getenv("INTERVIEW_HTTP_PORT", "8765"))
_STATIC   = ""   # set when server starts


class InterviewHandler(BaseHTTPRequestHandler):

    # ── MIME types ────────────────────────────────────────────────
    _MIME = {
        ".html": "text/html; charset=utf-8",
        ".js":   "application/javascript",
        ".css":  "text/css",
        ".json": "application/json",
        ".png":  "image/png",
        ".jpg":  "image/jpeg",
        ".svg":  "image/svg+xml",
        ".ico":  "image/x-icon",
    }

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")

    # ── OPTIONS (preflight) ───────────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    # ── GET — serve static files ──────────────────────────────────
    def do_GET(self):
        path = self.path.split("?")[0].lstrip("/")
        filepath = os.path.join(_STATIC, path)

        if not os.path.isfile(filepath):
            self.send_response(404)
            self.end_headers()
            return

        ext  = os.path.splitext(filepath)[1].lower()
        mime = self._MIME.get(ext, "application/octet-stream")

        with open(filepath, "rb") as f:
            data = f.read()

        self.send_response(200)
        self.send_header("Content-Type",   mime)
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    # ── POST /submit — receive transcript from interview page ─────
    def do_POST(self):
        if self.path != "/submit":
            self.send_response(404)
            self.end_headers()
            return

        length  = int(self.headers.get("Content-Length", 0))
        body    = self.rfile.read(length)

        try:
            payload = json.loads(body)
            iv_id   = int(payload.get("interview_id", 0))
            msgs    = payload.get("messages", [])

            if iv_id and msgs:
                out = os.path.join(_STATIC, f"iv_result_{iv_id}.json")
                with open(out, "w", encoding="utf-8") as f:
                    json.dump(msgs, f)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

        except Exception as e:
            self.send_response(500)
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, fmt, *args):
        pass  # keep Streamlit terminal clean


def ensure_interview_server(directory: str | Path) -> str:
    """Start server once, return base URL http://127.0.0.1:8765"""
    global _SERVER, _STATIC
    if _SERVER is None:
        _STATIC = str(Path(directory).resolve())
        _SERVER = ThreadingHTTPServer(("127.0.0.1", _PORT), InterviewHandler)
        threading.Thread(target=_SERVER.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{_PORT}"
