"""
interview_server.py
Spins up a tiny HTTP server on 127.0.0.1:8765 that serves the static/
directory with correct MIME types (text/html for .html files).

WHY: Streamlit's built-in static file server sends .html as text/plain,
which causes the browser to render raw HTML code instead of executing it.
This server fixes that so VAPI and the interview page work correctly.
"""
from __future__ import annotations

import functools
import os
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

_SERVER = None
_PORT = int(os.getenv("INTERVIEW_HTTP_PORT", "8765"))


class InterviewHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".html": "text/html; charset=utf-8",
        ".js":   "application/javascript",
        ".css":  "text/css",
        ".json": "application/json",
    }

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        # Allow VAPI/Daily.co cross-origin requests
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format, *args):
        pass  # suppress request logs in Streamlit terminal


def ensure_interview_server(directory: str | Path) -> str:
    """
    Start the interview HTTP server if not already running.
    Returns the base URL: http://127.0.0.1:8765
    """
    global _SERVER
    if _SERVER is None:
        directory = str(Path(directory).resolve())
        handler = functools.partial(InterviewHandler, directory=directory)
        _SERVER = ThreadingHTTPServer(("127.0.0.1", _PORT), handler)
        threading.Thread(target=_SERVER.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{_PORT}"
