# 0001. A retrieval-only tool that calls the existing backend over HTTP

- **Status**: Accepted
- **Date**: 2026-11-07
- **Related**: local-codebase-rag ADR 0021 (`POST /search`), [devlog 2026-11-07](../devlog/2026-11-07.md)

> English first; 繁體中文版本在下方. Privacy: illustrate only with the sample project.

## Context

local-codebase-rag already has a tuned retrieval pipeline (hybrid search, split retrieval, rerank, glossary; each decided by evaluation runs). We want MCP hosts such as Claude Code to use it. Two questions: **what** the tool returns (an answer or excerpts) and **where** retrieval runs (in this process or in the backend).

## Decision

1. `search_codebase` returns **excerpts with `path:start-end`, not an answer**. The host's model reads the code and answers.
2. The server is a **thin stdio process that calls the backend's `POST /search`** over HTTP. It holds no index, no embedding model and no retrieval logic.

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
| --- | --- | --- | --- |
| Tool returns `/query`'s answer | Works without backend changes | Local 14b model answers first (10–30 s), host model only paraphrases it; errors compound | Wastes time and the stronger model |
| Import `app.rag` in-process | No HTTP hop | Needs LlamaIndex, Qdrant client, `.env` on the host; second writer to Qdrant; two repos move together | Too much coupling for a 1-tool server |
| Rebuild retrieval inside the MCP server | Self-contained | Duplicates 20 ADRs of tuning; results diverge from evaluations | Defeats the point of the evaluated pipeline |

## Consequences

- **Positive**: The server stays ~200 lines and starts instantly. Retrieval switches and evaluation results apply unchanged. The same backend serves the web UI and MCP.
- **Negative / trade-offs**: The backend must be running (Docker + Ollama). Code excerpts now go to the host's model; with a cloud model (Claude) **code leaves the machine**, unlike the web UI (local-codebase-rag ADR 0001). Use only with code you are allowed to send, or with a local MCP host.
- **Follow-ups**: Measure tool latency and answer quality against the web UI on the 10-question set ({待填}); see [roadmap](../roadmap.md).

---

# 0001. 只回傳檢索結果的 tool，透過 HTTP 呼叫現有後端

- **狀態**：已接受
- **日期**：2026-11-07
- **相關**：local-codebase-rag ADR 0021（`POST /search`）、[devlog 2026-11-07](../devlog/2026-11-07.md)

## 背景

local-codebase-rag 已經有調整過的檢索流程（混合檢索、分類取回、rerank、詞彙表，每一項都由評估決定）。我們要讓 Claude Code 等 MCP host 使用它。要決定兩件事：tool **回傳什麼**（回答或片段），以及檢索**在哪裡跑**（這個行程裡或後端）。

## 決策

1. `search_codebase` 回傳**附 `路徑:起-迄` 的片段，不回傳答案**。由 host 的模型閱讀程式碼後回答。
2. Server 是**很薄的 stdio 行程，透過 HTTP 呼叫後端 `POST /search`**，本身不持有索引、embedding 模型或檢索邏輯。

## 替代方案

| 方案 | 優點 | 缺點 | 未採用原因 |
| --- | --- | --- | --- |
| Tool 回傳 `/query` 的答案 | 後端不用改 | 本機 14b 先回答（10–30 秒），host 模型只是轉述；錯誤會疊加 | 浪費時間，也浪費較強的模型 |
| 直接 import `app.rag` | 少一次 HTTP | host 要裝 LlamaIndex、Qdrant client、`.env`；Qdrant 多一個寫入者；兩個倉庫要一起改 | 對一個 tool 的 server 來說耦合太重 |
| 在 MCP Server 裡重做檢索 | 自給自足 | 重複 20 份 ADR 的調整；結果與評估不一致 | 失去經過評估的檢索流程 |

## 後果

- **正面**：Server 約 200 行，啟動很快。檢索開關與評估結果直接沿用。網頁介面與 MCP 共用同一個後端。
- **負面／取捨**：後端必須在執行（Docker + Ollama）。程式碼片段會送進 host 的模型；如果是雲端模型（Claude），**程式碼會離開本機**，這與網頁介面不同（local-codebase-rag ADR 0001）。只在允許傳送的程式碼上使用，或改用本機的 MCP host。
- **後續工作**：用 10 題題組比較 tool 延遲與回答品質（{待填}）；見 [roadmap](../roadmap.md)。
