"""HTTP client for the local-codebase-rag backend.

Uses only the standard library (ADR 0002). Calls are blocking; the server runs
them in a worker thread so the MCP event loop stays responsive.
"""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from typing import Any, Protocol


class RagError(Exception):
    """The backend could not answer. The message is written for the host model to read."""


class RagClient(Protocol):
    def search(self, query: str, top_k: int) -> list[dict[str, Any]]: ...


class HttpRagClient:
    """Calls ``POST {base_url}/search`` (retrieval only, no LLM; see patches/README.md)."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        body = json.dumps({"question": query, "top_k": top_k}).encode()
        request = urllib.request.Request(
            f"{self.base_url}/search",
            data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as exc:
            raise RagError(self._http_error_message(exc)) from exc
        except (TimeoutError, socket.timeout) as exc:
            raise RagError(
                f"local-codebase-rag 在 {self.timeout:g} 秒內沒有回應（CODEBASE_RAG_TIMEOUT）。"
                "Ollama 可能還在載入 embedding 模型，稍後再試。"
            ) from exc
        except urllib.error.URLError as exc:
            raise RagError(
                f"連不到 local-codebase-rag（{self.base_url}）：{exc.reason}。"
                "請確認後端已啟動（docker compose up），且 CODEBASE_RAG_URL 正確。"
            ) from exc
        except json.JSONDecodeError as exc:
            raise RagError(f"local-codebase-rag 回傳的不是 JSON：{exc}") from exc

        if isinstance(payload, dict) and payload.get("indexed") is False:
            raise RagError("local-codebase-rag 還沒有任何索引。請先執行 ./scripts/index.sh 建立索引。")
        sources = payload.get("sources") if isinstance(payload, dict) else None
        if not isinstance(sources, list):
            raise RagError("local-codebase-rag 的回應缺少 sources 欄位，後端版本可能太舊（需要 POST /search）。")
        return sources

    def _http_error_message(self, exc: urllib.error.HTTPError) -> str:
        try:
            detail = json.load(exc).get("detail", "")
        except Exception:
            detail = ""
        if exc.code == 404:
            return (
                "local-codebase-rag 沒有 POST /search 端點。"
                "請先套用 patches/local-codebase-rag-search-endpoint.patch 並重建後端。"
            )
        return f"local-codebase-rag 回傳 HTTP {exc.code}：{detail or exc.reason}"
