# 0002. Standard-library HTTP client, MCP SDK 2.x as the only dependency

- **Status**: Accepted
- **Date**: 2026-11-07
- **Related**: [devlog 2026-11-07](../devlog/2026-11-07.md)

> English first; 繁體中文版本在下方.

## Context

The server makes one kind of request: a JSON `POST /search` to localhost. MCP hosts start the server as a child process, often through `uvx` / `uv run`, so every dependency adds install time on first start and a chance of version conflicts. The MCP Python SDK is at 2.x (`FastMCP` was renamed `MCPServer`), and 1.x code does not run on it.

## Decision

- Use `urllib.request` for the backend call, run in a worker thread (`anyio.to_thread.run_sync`) so the MCP event loop is not blocked.
- Depend only on `mcp>=2.3,<3`; write against the 2.x API (`mcp.server.mcpserver.MCPServer`, `mcp.Client` for tests).

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
| --- | --- | --- | --- |
| `httpx.AsyncClient` | Native async, nicer API | Extra dependency; the SDK 2.x already pulls in `httpx2`, so two HTTP stacks | One localhost request does not need it |
| `requests` | Familiar | Extra dependency, still blocking | No gain over urllib |
| Pin `mcp<2` and use `FastMCP` | Matches most tutorials | Old API, stops getting fixes | New project should start on the current major |

## Consequences

- **Positive**: Install = one package. Tests run a real HTTP server from `http.server`, no mocking library.
- **Negative / trade-offs**: Slightly more code for error handling (`HTTPError` vs `URLError` vs timeout). Most online examples are 1.x and need translating.
- **Follow-ups**: If the server later calls several endpoints concurrently or streams, switch to an async client in a new ADR.

---

# 0002. 使用標準函式庫的 HTTP client，唯一依賴是 MCP SDK 2.x

- **狀態**：已接受
- **日期**：2026-11-07
- **相關**：[devlog 2026-11-07](../devlog/2026-11-07.md)

## 背景

Server 只發一種請求：對 localhost 的 JSON `POST /search`。MCP host 會以子行程啟動 server，常透過 `uvx`／`uv run`，所以每多一個依賴，第一次啟動就多一段安裝時間，也多一個版本衝突的可能。MCP Python SDK 已經是 2.x（`FastMCP` 改名為 `MCPServer`），1.x 的程式碼在 2.x 上無法執行。

## 決策

- 呼叫後端用 `urllib.request`，放在 worker thread（`anyio.to_thread.run_sync`）執行，不卡住 MCP 的 event loop。
- 只依賴 `mcp>=2.3,<3`，依 2.x API 撰寫（`mcp.server.mcpserver.MCPServer`，測試用 `mcp.Client`）。

## 替代方案

| 方案 | 優點 | 缺點 | 未採用原因 |
| --- | --- | --- | --- |
| `httpx.AsyncClient` | 原生 async、API 好用 | 多一個依賴；SDK 2.x 已經依賴 `httpx2`，會有兩套 HTTP 套件 | 一個 localhost 請求不需要 |
| `requests` | 大家熟悉 | 多一個依賴，一樣是阻塞式 | 沒有比 urllib 好 |
| 鎖定 `mcp<2` 用 `FastMCP` | 跟多數教學一致 | 舊 API，之後不再修正 | 新專案應從目前的主版本開始 |

## 後果

- **正面**：安裝只需一個套件。測試用 `http.server` 起真正的 HTTP server，不需要 mock 套件。
- **負面／取捨**：錯誤處理要多寫一點（`HTTPError`、`URLError`、逾時分開處理）。網路上的範例多半是 1.x，要自己轉換。
- **後續工作**：如果之後要同時呼叫多個端點或串流，另寫 ADR 改用 async client。
