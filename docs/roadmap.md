# Roadmap

> English first; 繁體中文版本在下方. Each phase ends with an ADR for any real choice, a devlog, and measured numbers (or `{待填}`).

| Phase | Goal | MCP concept learned | Done when |
| --- | --- | --- | --- |
| **1. One tool, stdio** (now) | `search_codebase` over the backend's `POST /search` | Tools, schemas, annotations, stdio, in-memory tests | Works in Claude Code on the sample project; backend PR merged |
| **2. Evaluate** | Run local-codebase-rag's 10 + 5 questions through Claude Code with the tool; compare with the web UI | How models use tools (call count, query rewriting) | Table in `docs/metrics.md`: correctness /30, tool calls per question, latency |
| **3. Follow-up tools & resources** | `read_file(path, start, end)`; `file://` resources for indexed files; `index_status` | Resources vs tools; resource templates | Model can open the lines around a hit without a new search |
| **4. Prompts** | `/explain-flow`, `/where-is` prompt templates | Prompts (user-invoked) | Shown as slash commands in the host |
| **5. Team server** | Streamable HTTP transport, auth, request log | HTTP transport, OAuth, multi-client | Two people use one server; access is logged |
| **6. Write-ups** | Articles and resume line from the devlogs and numbers | — | Published post (sample project only) |

Ideas not scheduled: a local MCP host with an Ollama model (keeps code on the machine), `git blame` / history tools, Unity project support.

---

# 發展路線

> 每個階段結束時：有真正的選擇就寫 ADR、寫 devlog、附上量測數字（沒量到就寫 `{待填}`）。

| 階段 | 目標 | 學到的 MCP 概念 | 完成條件 |
| --- | --- | --- | --- |
| **1. 一個 tool、stdio**（目前） | 透過後端 `POST /search` 提供 `search_codebase` | Tools、schema、annotations、stdio、記憶體內測試 | 在 Claude Code 對範例專案可用；後端 PR 合併 |
| **2. 評估** | 用 Claude Code + tool 跑 local-codebase-rag 的 10 + 5 題，與網頁介面比較 | 模型怎麼使用 tool（呼叫次數、改寫查詢） | `docs/metrics.md` 有表格：正確性 /30、每題 tool 呼叫次數、延遲 |
| **3. 追查用的 tools 與 resources** | `read_file(path, start, end)`；已索引檔案的 `file://` resources；`index_status` | Resources 與 tools 的差別；resource template | 模型不用重新搜尋就能打開命中片段前後的程式碼 |
| **4. Prompts** | `/explain-flow`、`/where-is` 等 prompt 範本 | Prompts（使用者觸發） | 在 host 中以 slash command 出現 |
| **5. 團隊共用 server** | Streamable HTTP、驗證、請求記錄 | HTTP 傳輸、OAuth、多 client | 兩個人共用一個 server，存取有記錄 |
| **6. 整理成文章** | 從 devlog 與數據寫文章、履歷 | — | 發表文章（只用範例專案） |

尚未排入的想法：搭配 Ollama 模型的本機 MCP host（程式碼不離開本機）、`git blame`／歷史查詢 tool、支援 Unity 專案。
