# CLAUDE.md

> English first. 繁體中文版本在下方。

## Project overview

`codebase-rag-mcp` is a stdio MCP server with one read-only tool, `search_codebase`. It calls the [local-codebase-rag](https://github.com/alelcold/local-codebase-rag) backend's `POST /search` (retrieval only) and returns excerpts with `path:start-end`; the MCP host's model writes the answer (ADR 0001).

| File | What |
| --- | --- |
| `src/codebase_rag_mcp/server.py` | `MCPServer`, tool definition, Markdown rendering |
| `src/codebase_rag_mcp/rag_client.py` | Standard-library HTTP client for `/search` (ADR 0002) |
| `src/codebase_rag_mcp/config.py` | `CODEBASE_RAG_*` environment variables |
| `tests/` | In-memory MCP `Client` tests; HTTP client against a local `http.server` |
| `patches/` | Changes for local-codebase-rag that are not merged yet |

### Common commands

```bash
uv sync --extra dev            # install
uv run pytest                  # tests (no backend needed)
uv run codebase-rag-mcp        # run over stdio (normally started by the host)
npx @modelcontextprotocol/inspector uv run --directory . codebase-rag-mcp  # manual testing
```

## Rules

1. **MCP SDK 2.x.** Use `mcp.server.mcpserver.MCPServer`, not `FastMCP` (1.x). Never write to stdout (it is the JSON-RPC channel); log with `logging`.
2. **Record decisions** the same way as local-codebase-rag: ADR in `docs/decisions/` (next free number, never rewrite an accepted one), devlog in `docs/devlog/YYYY-MM-DD.md` as Problem → Cause → Fix with the exact error, PR section `## 技術決策說明 / Technical decisions`. Never invent numbers; leave `{待填}`.
3. **Learning notes.** When a phase teaches something about MCP, add it to `docs/learning/mcp-notes.md`; tick or add open questions there.
4. **Bilingual docs.** Everything under `docs/` and this file: English first, Traditional Chinese below.
5. **Privacy.** Examples, fixtures, screenshots and PRs use only local-codebase-rag's sample project. No company-internal code, paths or names.

---

# CLAUDE.md（繁體中文）

## 專案簡介

`codebase-rag-mcp` 是一個 stdio MCP Server，只有一個唯讀 tool `search_codebase`。它呼叫 local-codebase-rag 後端的 `POST /search`（只檢索），回傳附 `路徑:起-迄` 的片段，由 MCP host 的模型撰寫回答（ADR 0001）。

檔案說明與常用指令見上方英文段落。

## 規則

1. **MCP SDK 2.x**：使用 `mcp.server.mcpserver.MCPServer`，不要用 `FastMCP`（1.x）。不要寫入 stdout（那是 JSON-RPC 通道），記錄用 `logging`。
2. **記錄決策**，方式與 local-codebase-rag 相同：ADR 放 `docs/decisions/`（編號接續、已接受的不改寫）；devlog 放 `docs/devlog/YYYY-MM-DD.md`，以「問題 → 原因 → 解法」記錄並附完整錯誤訊息；PR 加 `## 技術決策說明 / Technical decisions`。不要編造數字，未量測寫 `{待填}`。
3. **學習筆記**：每個階段學到的 MCP 知識補進 `docs/learning/mcp-notes.md`，並更新待探討問題。
4. **雙語文件**：`docs/` 底下與本檔案，先英文、下方附繁體中文。
5. **隱私**：範例、測試資料、截圖與 PR 只使用 local-codebase-rag 的範例專案，不得出現公司內部程式碼、路徑或名稱。
