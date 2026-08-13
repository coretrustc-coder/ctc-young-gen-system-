"""
CoreTrust System (CTC) -- Live Dashboard Server
===============================================
Serves the live editable dashboard and accepts saves back into your local
database, so edits in the browser round-trip to SQLite.

  GET  /        -> the live editable dashboard (rebuilt from the DB each load)
  POST /save    -> replace the DB with the posted profile JSON, return counts

Local only (binds 127.0.0.1). Single-threaded, so it shares the CLI's DB
connection safely. Stop with Ctrl+C.
"""

from __future__ import annotations

import json
import os
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer

from ctc_dashboard_live import build_editable_payload, render_standalone_live


def _make_handler(db):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, ctype, body: bytes):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                html = render_standalone_live(build_editable_payload(db)).encode("utf-8")
                self._send(200, "text/html; charset=utf-8", html)
            else:
                self._send(404, "text/plain", b"not found")

        def do_POST(self):
            if self.path != "/save":
                self._send(404, "text/plain", b"not found")
                return
            try:
                n = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(n))
                tmp = os.path.join(tempfile.gettempdir(), "ctc_live_import.json")
                with open(tmp, "w", encoding="utf-8") as fh:
                    json.dump(data, fh)
                db.clear_all()                       # mirror the editor exactly
                counts = db.import_from_json(tmp)
                self._send(200, "application/json",
                           json.dumps({"ok": True, "counts": counts}).encode("utf-8"))
            except Exception as ex:  # noqa: BLE001 -- report save errors to the page
                self._send(400, "application/json",
                           json.dumps({"ok": False, "error": str(ex)}).encode("utf-8"))

        def log_message(self, *args):
            pass

    return Handler


def serve(db, port: int = 8799) -> None:
    srv = HTTPServer(("127.0.0.1", port), _make_handler(db))
    print(f"\n  Live editable dashboard running:  http://127.0.0.1:{port}/")
    print("  Open that URL, edit your numbers, and click SAVE to write back here.")
    print("  Press Ctrl+C to stop the server and return to the menu.\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
    finally:
        srv.server_close()
