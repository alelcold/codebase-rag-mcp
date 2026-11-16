"""Settings, read from environment variables.

The MCP host (Claude Code, Claude Desktop, ...) starts this server as a child
process, so the usual place to set these is the ``env`` block of the host's
MCP configuration (see README).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_RAG_URL = "http://localhost:8000"


@dataclass(frozen=True)
class Settings:
    # Base URL of the local-codebase-rag backend (docker-compose binds it to 127.0.0.1:8000).
    rag_url: str = DEFAULT_RAG_URL
    # Seconds to wait for /search. Retrieval only embeds the query (no LLM), so
    # this is far shorter than the backend's LLM timeouts (local-codebase-rag ADR 0009).
    timeout: float = 30.0
    # Excerpts returned when the model does not ask for a number.
    default_top_k: int = 8
    # Each excerpt's text is cut to this many characters, to keep tool results
    # small in the host model's context window. The backend's chunks are at most
    # CHUNK_MAX_CHARS (3000 by default), so the default rarely cuts anything.
    max_chars_per_result: int = 4000

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        env = os.environ if env is None else env
        return cls(
            rag_url=env.get("CODEBASE_RAG_URL", DEFAULT_RAG_URL).rstrip("/"),
            timeout=float(env.get("CODEBASE_RAG_TIMEOUT", cls.timeout)),
            default_top_k=int(env.get("CODEBASE_RAG_TOP_K", cls.default_top_k)),
            max_chars_per_result=int(env.get("CODEBASE_RAG_MAX_CHARS", cls.max_chars_per_result)),
        )
