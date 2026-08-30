#!/usr/bin/env python3
"""Static OIDC endpoint for the authorization recipe.

Serves the two documents Spice fetches during OIDC discovery at startup:
  GET /.well-known/openid-configuration
  GET /jwks.json

Start this BEFORE `spice run` — Spice performs discovery when it boots.

    python3 serve-jwks.py      # listens on http://127.0.0.1:9999

Uses only the Python standard library.
"""

import http.server
import os
import socketserver

HOST = "127.0.0.1"
PORT = 9999
JWKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jwks")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=JWKS_DIR, **kwargs)

    # Both documents are JSON; the discovery file has no extension.
    def guess_type(self, path):
        return "application/json"

    def log_message(self, fmt, *args):  # keep the console quiet
        pass


with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
    print(f"Serving OIDC discovery + JWKS on http://{HOST}:{PORT}  (Ctrl-C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
