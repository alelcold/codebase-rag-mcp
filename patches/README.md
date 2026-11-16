# Patches for local-codebase-rag

> English first; 繁體中文版本在下方.

## `local-codebase-rag-search-endpoint.patch`

Adds `POST /search` (retrieval only, no LLM) to the local-codebase-rag backend, with tests and its ADR 0021. `codebase-rag-mcp` needs it.

```bash
cd /path/to/local-codebase-rag
git checkout -b feat/search-endpoint
git apply /path/to/codebase-rag-mcp/patches/local-codebase-rag-search-endpoint.patch
cd backend && pytest
docker compose up -d --build backend
```

The patch was written against `main` at `7abceea`. Its backend tests were **not** run where it was written (FastAPI and LlamaIndex were not installed there); run `pytest` before opening the PR. Once merged, delete this patch.

---

# 要套用到 local-codebase-rag 的修改

## `local-codebase-rag-search-endpoint.patch`

在 local-codebase-rag 後端新增 `POST /search`（只檢索、不呼叫 LLM），包含測試與 ADR 0021。`codebase-rag-mcp` 需要這個端點。

指令如上。patch 以 `main` 的 `7abceea` 為基準。撰寫時的環境沒有安裝 FastAPI 與 LlamaIndex，**後端測試尚未執行**，開 PR 前請先跑 `pytest`。合併後刪除這個 patch。
