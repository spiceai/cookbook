#!/usr/bin/env python3
"""
Fast test server for the Spice HTTP rate-control recipe.

Runs a minimal async HTTP server that responds as fast as possible.
Server-side rate limiting is intentionally absent — rate control is
tested at the Spice layer.

  - Exposes GET /items  — list of sample items
  - Exposes GET /status — request counter

Usage:
    uv run test-server/main.py          # default: port 8080
    uv run test-server/main.py 9090     # custom port
"""

# /// script
# dependencies = ["aiohttp"]
# ///

from __future__ import annotations

import asyncio
import json
import sys
from aiohttp import web

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------
ITEMS = [{"id": i, "name": f"item-{i}"} for i in range(1, 6)]
ITEMS_PAYLOAD = json.dumps(ITEMS).encode()

_requests_total: int = 0


async def handle_items(request: web.Request) -> web.Response:
    global _requests_total
    _requests_total += 1
    return web.Response(body=ITEMS_PAYLOAD, content_type="application/json")


async def handle_status(request: web.Request) -> web.Response:
    return web.Response(
        body=json.dumps({"requests_total": _requests_total}).encode(),
        content_type="application/json",
    )


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    app = web.Application()
    app.router.add_get("/items", handle_items)
    app.router.add_get("/status", handle_status)
    print(f"Fast test server listening on http://0.0.0.0:{port}")
    print(f"  GET /items   — returns {len(ITEMS)} sample items")
    print(f"  GET /status  — returns request counter")
    print("Press Ctrl+C to stop.\n")
    web.run_app(app, host="0.0.0.0", port=port, print=None)


if __name__ == "__main__":
    main()
