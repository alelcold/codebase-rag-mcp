"""HttpRagClient against a real local HTTP server."""

from __future__ import annotations

import socket

import pytest

from codebase_rag_mcp.config import Settings
from codebase_rag_mcp.rag_client import HttpRagClient, RagError

from .conftest import PLAYER_SOURCE


def test_posts_question_and_top_k_to_search(fake_backend):
    sources = HttpRagClient(fake_backend.url, timeout=5).search("INVINCIBLE_MS", 3)
    assert sources == [PLAYER_SOURCE]
    assert fake_backend.requests == [{"path": "/search", "json": {"question": "INVINCIBLE_MS", "top_k": 3}}]


def test_trailing_slash_in_url(fake_backend):
    HttpRagClient(fake_backend.url + "/", timeout=5).search("x", 1)
    assert fake_backend.requests[0]["path"] == "/search"


def test_404_explains_the_missing_endpoint(fake_backend):
    fake_backend.status, fake_backend.body = 404, {"detail": "Not Found"}
    with pytest.raises(RagError, match="POST /search"):
        HttpRagClient(fake_backend.url, timeout=5).search("x", 1)


def test_http_error_includes_backend_detail(fake_backend):
    fake_backend.status, fake_backend.body = 504, {"detail": "Ollama 產生向量（embedding）逾時"}
    with pytest.raises(RagError, match="HTTP 504.*embedding"):
        HttpRagClient(fake_backend.url, timeout=5).search("x", 1)


def test_non_json_response(fake_backend):
    fake_backend.body = b"<html>oops</html>"
    with pytest.raises(RagError, match="不是 JSON"):
        HttpRagClient(fake_backend.url, timeout=5).search("x", 1)


def test_missing_sources_field(fake_backend):
    fake_backend.body = {"answer": "hi"}
    with pytest.raises(RagError, match="sources"):
        HttpRagClient(fake_backend.url, timeout=5).search("x", 1)


def test_not_indexed_yet(fake_backend):
    fake_backend.body = {"indexed": False, "no_relevant": False, "sources": []}
    with pytest.raises(RagError, match="index.sh"):
        HttpRagClient(fake_backend.url, timeout=5).search("x", 1)


def test_connection_refused():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]  # closed again before the request: nothing listens
    with pytest.raises(RagError, match="連不到"):
        HttpRagClient(f"http://127.0.0.1:{port}", timeout=5).search("x", 1)


def test_settings_from_env():
    s = Settings.from_env(
        {
            "CODEBASE_RAG_URL": "http://mac.local:8000/",
            "CODEBASE_RAG_TIMEOUT": "12.5",
            "CODEBASE_RAG_TOP_K": "4",
            "CODEBASE_RAG_MAX_CHARS": "2000",
        }
    )
    assert s == Settings(rag_url="http://mac.local:8000", timeout=12.5, default_top_k=4, max_chars_per_result=2000)
    assert Settings.from_env({}) == Settings()
