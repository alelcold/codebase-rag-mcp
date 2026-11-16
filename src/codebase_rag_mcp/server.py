"""The MCP server: one read-only tool, ``search_codebase``.

The tool returns retrieved excerpts, not an answer: the host's model (Claude,
...) reads the code and writes the answer itself (ADR 0001).
"""

from __future__ import annotations

import logging
from typing import Annotated

import anyio
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import CallToolResult, TextContent, ToolAnnotations
from pydantic import BaseModel, Field

from . import __version__
from .config import Settings
from .rag_client import HttpRagClient, RagClient, RagError

# stdio transport: stdout carries JSON-RPC, so logs must go to stderr only.
log = logging.getLogger("codebase_rag_mcp")

INSTRUCTIONS = """\
Searches a game front-end codebase (TypeScript / JavaScript / Markdown) indexed by local-codebase-rag.
Use search_codebase before answering questions about where something is defined, configured or handled.
Cite results as path:start-end. If nothing relevant comes back, say so instead of guessing.
"""

SEARCH_DESCRIPTION = """\
Search the indexed game front-end codebase and return the most relevant excerpts
(code and docs) with file paths and line ranges.

Use it to find where a value is configured, where a class / function / constant is
defined, or which files take part in a flow. Queries can be natural language
(English or Chinese) or identifiers (e.g. `INVINCIBLE_MS`, `ScoreSystem`); including
an identifier when you know it improves results. Call it again with a narrower
query if the first results are off target.

Returns excerpts only, not an answer: read them, then answer and cite path:start-end.
"""


class SearchResult(BaseModel):
    ref: int = Field(description="1-based rank in this result list")
    location: str = Field(description="path:start-end, for citations")
    file_path: str
    start_line: int
    end_line: int
    symbol: str = Field(description="Function / class / heading the excerpt belongs to, if known")
    kind: str
    language: str
    score: float = Field(description="Retrieval score; only comparable within one call")
    matched_by: list[str] = Field(description='Retrievers that found it: "vector", "keyword", "identifier"')
    truncated: bool = Field(description="True when text was cut to CODEBASE_RAG_MAX_CHARS")
    text: str


class SearchOutput(BaseModel):
    query: str
    results: list[SearchResult]


def to_result(i: int, source: dict, max_chars: int) -> SearchResult:
    text = str(source.get("text", ""))
    truncated = len(text) > max_chars
    path = str(source.get("file_path", "?"))
    start, end = int(source.get("start_line", 0)), int(source.get("end_line", 0))
    return SearchResult(
        ref=i,
        location=f"{path}:{start}-{end}",
        file_path=path,
        start_line=start,
        end_line=end,
        symbol=str(source.get("symbol") or ""),
        kind=str(source.get("kind") or ""),
        language=str(source.get("language") or ""),
        score=float(source.get("score") or 0.0),
        matched_by=list(source.get("matched_by") or []),
        truncated=truncated,
        text=text[:max_chars] if truncated else text,
    )


def render_markdown(output: SearchOutput) -> str:
    """Text content for the model: one heading + fenced block per excerpt.

    Code stays readable (no JSON-escaped newlines), which costs fewer tokens
    than the JSON form of the same data (ADR 0003).
    """
    if not output.results:
        return f"No excerpts found for: {output.query}"
    parts = [f"{len(output.results)} excerpts for: {output.query}"]
    for r in output.results:
        label = f" `{r.symbol}`" if r.symbol else ""
        found = f" (matched by {', '.join(r.matched_by)})" if r.matched_by else ""
        fence = "````" if "```" in r.text else "```"
        note = "\n… (truncated)" if r.truncated else ""
        parts.append(f"## [{r.ref}] {r.location}{label}{found}\n{fence}{r.language}\n{r.text}\n{fence}{note}")
    return "\n\n".join(parts)


def create_server(settings: Settings | None = None, client: RagClient | None = None) -> MCPServer:
    settings = settings or Settings.from_env()
    client = client or HttpRagClient(settings.rag_url, settings.timeout)
    server = MCPServer("codebase-rag", version=__version__, instructions=INSTRUCTIONS)

    @server.tool(
        name="search_codebase",
        title="Search codebase",
        description=SEARCH_DESCRIPTION,
        annotations=ToolAnnotations(
            readOnlyHint=True,
            idempotentHint=True,
            openWorldHint=False,  # only the local index, never the internet
        ),
    )
    async def search_codebase(
        query: Annotated[str, Field(min_length=1, max_length=4000, description="What to look for")],
        top_k: Annotated[int | None, Field(ge=1, le=30, description="Number of excerpts (default 8)")] = None,
    ) -> Annotated[CallToolResult, SearchOutput]:
        query = query.strip()
        if not query:
            raise ToolError("query must not be blank")
        k = top_k or settings.default_top_k
        try:
            sources = await anyio.to_thread.run_sync(client.search, query, k)
        except RagError as exc:
            log.warning("search failed: %s", exc)
            raise ToolError(str(exc)) from exc
        output = SearchOutput(
            query=query,
            results=[to_result(i, s, settings.max_chars_per_result) for i, s in enumerate(sources, 1)],
        )
        return CallToolResult(
            content=[TextContent(type="text", text=render_markdown(output))],
            structured_content=output.model_dump(),
        )

    return server


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    settings = Settings.from_env()
    log.info("codebase-rag MCP server %s → %s", __version__, settings.rag_url)
    create_server(settings).run("stdio")


if __name__ == "__main__":
    main()
