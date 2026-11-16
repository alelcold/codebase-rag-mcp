"""Start the real server as a subprocess over stdio and check the handshake and tool list.

Usage: uv run python scripts/stdio_smoke.py
Exits non-zero on failure. Does not need the backend (it only lists tools,
then calls search_codebase against an unreachable URL and expects isError).
"""

from __future__ import annotations

import os
import sys

import anyio
from mcp import Client, StdioServerParameters


async def main() -> int:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "codebase_rag_mcp.server"],
        # Keep the parent environment (PATH, PYTHONPATH, venv); a bare env would drop them.
        env={**os.environ, "CODEBASE_RAG_URL": "http://127.0.0.1:9", "CODEBASE_RAG_TIMEOUT": "2"},
    )
    async with Client(params) as client:
        names = [t.name for t in (await client.list_tools()).tools]
        print("server:", client.server_info.name, client.server_info.version)
        print("tools:", names)
        if names != ["search_codebase"]:
            print("unexpected tool list", file=sys.stderr)
            return 1
        result = await client.call_tool("search_codebase", {"query": "INVINCIBLE_MS"})
        print("unreachable backend →", "isError" if result.is_error else "ok", "|", result.content[0].text[:80])
        if not result.is_error:
            return 1
    print("stdio smoke test passed")
    return 0


if __name__ == "__main__":
    sys.exit(anyio.run(main))
