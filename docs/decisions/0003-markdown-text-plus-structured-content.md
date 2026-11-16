# 0003. Return Markdown text for the model plus structured content

- **Status**: Accepted
- **Date**: 2026-11-07
- **Related**: [learning notes §4](../learning/mcp-notes.md)

> English first; 繁體中文版本在下方.

## Context

A tool result has `content` (what the model reads) and, since spec 2025-06-18, optional `structuredContent` validated against the tool's `outputSchema`. When a Python tool returns a Pydantic model, the SDK puts the model's **JSON** in `content`. For code excerpts, JSON escapes every newline and quote (`"export const X = 1;\n..."`), which is harder for the model to read and costs more tokens.

## Decision

The tool returns a `CallToolResult` with both:

- `content`: Markdown, one `## [n] path:start-end \`symbol\`` heading and a fenced code block per excerpt (a longer fence when the excerpt itself contains ```` ``` ````);
- `structuredContent`: the same data as `SearchOutput`, with `outputSchema` declared via `Annotated[CallToolResult, SearchOutput]`.

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
| --- | --- | --- | --- |
| Return the Pydantic model (SDK default) | Least code | Model reads escaped JSON | Readability and tokens |
| Markdown only, no schema | Simple | Programmatic clients (scripts, tests, other agents) must parse Markdown | Loses the typed contract |

## Consequences

- **Positive**: The model reads code as code; clients get a typed result; tests assert on structured data instead of strings.
- **Negative / trade-offs**: Two renderings of one result must stay in step (covered by tests).
- **Follow-ups**: Measure token count of Markdown vs JSON for the 10-question set ({待填}).

---

# 0003. 給模型讀的 Markdown 文字，加上結構化內容

- **狀態**：已接受
- **日期**：2026-11-07
- **相關**：[學習筆記 §4](../learning/mcp-notes.md)

## 背景

Tool 的結果有 `content`（模型讀的內容），以及從規格 2025-06-18 起可選的 `structuredContent`（依 tool 的 `outputSchema` 驗證）。Python tool 直接回傳 Pydantic model 時，SDK 會把 model 的 **JSON** 放進 `content`。對程式碼片段來說，JSON 會跳脫每個換行與引號，模型比較難讀，token 也比較多。

## 決策

Tool 回傳同時包含兩者的 `CallToolResult`：

- `content`：Markdown，每個片段一個 `## [n] 路徑:起-迄 \`符號\`` 標題加程式碼區塊（片段本身含 ```` ``` ```` 時改用較長的圍欄）；
- `structuredContent`：同一份資料的 `SearchOutput`，透過 `Annotated[CallToolResult, SearchOutput]` 宣告 `outputSchema`。

## 替代方案

| 方案 | 優點 | 缺點 | 未採用原因 |
| --- | --- | --- | --- |
| 回傳 Pydantic model（SDK 預設） | 程式最少 | 模型讀的是跳脫過的 JSON | 可讀性與 token |
| 只回傳 Markdown，不宣告 schema | 簡單 | 程式端（腳本、測試、其他 agent）要自己解析 Markdown | 失去有型別的介面 |

## 後果

- **正面**：模型以程式碼的形式閱讀程式碼；程式端拿到有型別的結果；測試可以檢查結構化資料而不是字串。
- **負面／取捨**：同一個結果有兩種呈現，要保持一致（由測試涵蓋）。
- **後續工作**：用 10 題題組比較 Markdown 與 JSON 的 token 數（{待填}）。
