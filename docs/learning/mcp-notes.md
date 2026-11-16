# MCP learning notes

> English first; 繁體中文版本在下方. A living document: add what each phase teaches, link devlogs and ADRs, and keep the open questions honest.

## 1. What an MCP server is

MCP (Model Context Protocol) standardizes how an AI application talks to tools and data. Like LSP for editors, it turns M apps × N tools integrations into M + N.

| Role | In this project |
| --- | --- |
| Host | Claude Code / Claude Desktop |
| Client | Inside the host, one per server |
| Server | `codebase-rag-mcp` (this repo) |

A server can offer **tools** (model-controlled functions), **resources** (app-controlled data with URIs) and **prompts** (user-invoked templates). Phase 1 uses one tool.

## 2. One call on the wire

```text
host → server  initialize            (protocol version, capabilities, client info)
server → host  result                (capabilities: tools; instructions; server info)
host → server  notifications/initialized
host → server  tools/list            → name, description, inputSchema, outputSchema, annotations
host → server  tools/call {name: "search_codebase", arguments: {query: "..."}}
server → host  result {content: [text], structuredContent: {...}, isError: false}
```

All messages are JSON-RPC 2.0. With stdio, each message is one line on stdin/stdout, which is why stdout must never carry logs.

## 3. Designing a tool for a model

- **Description = prompt.** The model decides *whether* to call and *what to send* only from the name, description and schema. Ours says when to use it, that identifiers help, that it may be called again with a narrower query, and that it returns excerpts, not answers.
- **Server `instructions`** are sent once at `initialize`; hosts may add them to the system prompt. Good place for "cite as `path:start-end`, say so when nothing is found".
- **Schema as guard-rail.** `min_length`, `ge=1, le=30` are enforced before the function runs; the model sees the validation error and can retry.
- **Annotations** (`readOnlyHint`, `idempotentHint`, `openWorldHint`) let hosts skip confirmation prompts for safe tools. They are hints, not security.
- **Errors the model can act on.** `ToolError("連不到 ... 請確認後端已啟動")` becomes `isError: true` text; the model can tell the user how to fix it.

## 4. Results: `content` vs `structuredContent`

`content` is what the model reads; `structuredContent` (validated by `outputSchema`) is for programs. We send Markdown for the model and typed data for programs ([ADR 0003](../decisions/0003-markdown-text-plus-structured-content.md)).

## 5. Transports

| Transport | Process model | Use when |
| --- | --- | --- |
| stdio | Host spawns the server; one client | Local tools (phase 1) |
| Streamable HTTP | Server is a web service; many clients; auth (OAuth) | Team-shared server (phase 3) |

## 6. Testing an MCP server

- In-memory: `mcp.Client(server)` runs the real protocol without a subprocess (`tests/test_server.py`).
- Manual: MCP Inspector (`npx @modelcontextprotocol/inspector ...`) shows every message.
- End-to-end: a real host (Claude Code `/mcp`).

## 7. Open questions to explore

- [ ] Does the host model write better answers from excerpts than the local 14b does from the same excerpts? Measure on the 10-question set.
- [ ] How many times does the model call the tool per question? Does it refine queries on its own?
- [ ] Is `top_k=8` right when the model can call again? Fewer, more focused results may be better.
- [ ] Would a `read_file(path, start, end)` tool or `file://` resources help the model follow up on a hit?
- [ ] Privacy: with a cloud host, excerpts leave the machine. Is a local MCP host (with an Ollama model) good enough to keep the original guarantee?
- [ ] What should a team-shared (HTTP) server authenticate and log?

---

# MCP 學習筆記

> 持續更新的文件：每個階段學到的東西都補進來，連到 devlog 與 ADR，並老實記錄還沒弄懂的問題。

## 1. MCP Server 是什麼

MCP（Model Context Protocol）規範 AI 應用與工具、資料之間的溝通方式。就像編輯器的 LSP，把 M 個應用 × N 個工具的整合變成 M + N。

| 角色 | 在本專案中 |
| --- | --- |
| Host | Claude Code／Claude Desktop |
| Client | 在 host 內，每個 server 一個 |
| Server | `codebase-rag-mcp`（本倉庫） |

Server 可以提供 **tools**（由模型決定呼叫的函式）、**resources**（由應用決定讀取、以 URI 識別的資料）與 **prompts**（使用者觸發的範本）。第 1 階段只用一個 tool。

## 2. 一次呼叫的訊息往返

見上方英文段落的訊息序列。所有訊息都是 JSON-RPC 2.0；stdio 傳輸下每則訊息是 stdin/stdout 上的一行，所以 stdout 絕對不能拿來寫 log。

## 3. 為模型設計 tool

- **描述就是 prompt**：模型只靠名稱、描述與 schema 決定要不要呼叫、送什麼。我們的描述寫了何時使用、識別字有幫助、可以換更精確的查詢再問一次、回傳的是片段而不是答案。
- **Server 的 `instructions`** 在 `initialize` 時送一次，host 可能放進 system prompt。適合寫「以 `路徑:起-迄` 引用、找不到就直說」。
- **Schema 是護欄**：`min_length`、`ge=1, le=30` 在函式執行前就檢查；模型看得到驗證錯誤並可重試。
- **Annotations**（`readOnlyHint`、`idempotentHint`、`openWorldHint`）讓 host 對安全的 tool 省略確認。它們只是提示，不是安全機制。
- **模型能處理的錯誤**：`ToolError("連不到 ... 請確認後端已啟動")` 會變成 `isError: true` 的文字，模型可以告訴使用者怎麼修。

## 4. 結果：`content` 與 `structuredContent`

`content` 給模型讀；`structuredContent`（以 `outputSchema` 驗證）給程式用。我們給模型 Markdown、給程式有型別的資料（[ADR 0003](../decisions/0003-markdown-text-plus-structured-content.md)）。

## 5. 傳輸方式

| 傳輸 | 行程模型 | 適用 |
| --- | --- | --- |
| stdio | Host 啟動 server 子行程；一個 client | 本機工具（第 1 階段） |
| Streamable HTTP | Server 是網路服務；多個 client；驗證（OAuth） | 團隊共用（第 3 階段） |

## 6. 測試 MCP Server

- 記憶體內：`mcp.Client(server)` 不開子行程就走完整協定（`tests/test_server.py`）。
- 手動：MCP Inspector 顯示每一則訊息。
- 端到端：真正的 host（Claude Code 的 `/mcp`）。

## 7. 待探討的問題

- [ ] 同樣的片段，host 模型寫的回答是否比本機 14b 好？用 10 題題組量測。
- [ ] 每個問題模型會呼叫 tool 幾次？會不會自己改寫查詢？
- [ ] 模型可以再查一次時，`top_k=8` 還合適嗎？少而精準的結果可能更好。
- [ ] 加一個 `read_file(path, start, end)` tool 或 `file://` resources，能否幫模型追查命中的片段？
- [ ] 隱私：用雲端 host 時片段會離開本機。本機 MCP host（搭配 Ollama 模型）是否夠好，能保留原本的保證？
- [ ] 團隊共用的 HTTP server 該驗證什麼、記錄什麼？
