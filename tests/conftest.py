from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

# Same shape as local-codebase-rag's Source (backend/app/rag.py), sample project only.
PLAYER_SOURCE = {
    "ref": 1,
    "file_path": "src/config/gameConfig.ts",
    "start_line": 3,
    "end_line": 9,
    "symbol": "INVINCIBLE_MS",
    "kind": "variable",
    "language": "typescript",
    "score": 0.031,
    "text": "export const INVINCIBLE_MS = 1500;",
    "matched_by": ["vector", "identifier"],
    "vector_score": 0.61,
    "rerank_score": None,
}

DOC_SOURCE = {
    "ref": 2,
    "file_path": "docs/guide.md",
    "start_line": 1,
    "end_line": 12,
    "symbol": "Player",
    "kind": "section",
    "language": "markdown",
    "score": 0.016,
    "text": "# Player\n\nAfter a hit the player is invincible for a short time.\n```ts\nx\n```",
    "matched_by": ["vector"],
}


class FakeRagClient:
    def __init__(self, sources=None, error: Exception | None = None):
        self.sources = sources if sources is not None else [PLAYER_SOURCE, DOC_SOURCE]
        self.error = error
        self.calls: list[tuple[str, int]] = []

    def search(self, query: str, top_k: int):
        self.calls.append((query, top_k))
        if self.error:
            raise self.error
        return self.sources[:top_k]


@pytest.fixture
def anyio_backend():
    return "asyncio"


class FakeBackend:
    """A real HTTP server on 127.0.0.1 standing in for local-codebase-rag."""

    def __init__(self) -> None:
        self.status = 200
        # Response shape of POST /search (local-codebase-rag ADR 0021).
        self.body: object = {"indexed": True, "no_relevant": False, "sources": [PLAYER_SOURCE]}
        self.requests: list[dict] = []
        backend = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                length = int(self.headers.get("Content-Length", 0))
                backend.requests.append({"path": self.path, "json": json.loads(self.rfile.read(length))})
                raw = backend.body if isinstance(backend.body, bytes) else json.dumps(backend.body).encode()
                self.send_response(backend.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def __enter__(self):
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *exc):
        self.httpd.shutdown()
        self.httpd.server_close()


@pytest.fixture
def fake_backend() -> Iterator[FakeBackend]:
    with FakeBackend() as backend:
        yield backend
