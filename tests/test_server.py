"""The MCP layer, through a real in-memory MCP client (initialize → tools/list → tools/call)."""

from __future__ import annotations

import pytest
from mcp import Client

from codebase_rag_mcp.config import Settings
from codebase_rag_mcp.rag_client import RagError
from codebase_rag_mcp.server import create_server

from .conftest import FakeRagClient

pytestmark = pytest.mark.anyio


async def test_lists_one_read_only_tool():
    async with Client(create_server(Settings(), FakeRagClient())) as client:
        tools = (await client.list_tools()).tools
    assert [t.name for t in tools] == ["search_codebase"]
    tool = tools[0]
    assert tool.annotations.read_only_hint is True
    assert tool.annotations.open_world_hint is False
    assert tool.input_schema["required"] == ["query"]
    assert tool.input_schema["properties"]["top_k"]["anyOf"][0]["maximum"] == 30
    assert "results" in tool.output_schema["properties"]


async def test_server_sends_instructions():
    async with Client(create_server(Settings(), FakeRagClient())) as client:
        assert "search_codebase" in (client.instructions or "")


async def test_search_returns_markdown_and_structured_results():
    fake = FakeRagClient()
    async with Client(create_server(Settings(), fake)) as client:
        result = await client.call_tool("search_codebase", {"query": "  無敵時間在哪裡設定  "})
    assert result.is_error is False
    assert fake.calls == [("無敵時間在哪裡設定", 8)]

    text = result.content[0].text
    assert "## [1] src/config/gameConfig.ts:3-9 `INVINCIBLE_MS` (matched by vector, identifier)" in text
    assert "```typescript\nexport const INVINCIBLE_MS = 1500;\n```" in text
    # An excerpt that itself contains ``` gets a longer fence.
    assert "````markdown\n# Player" in text

    data = result.structured_content
    assert data["query"] == "無敵時間在哪裡設定"
    assert [r["location"] for r in data["results"]] == ["src/config/gameConfig.ts:3-9", "docs/guide.md:1-12"]
    assert data["results"][0]["ref"] == 1


async def test_top_k_is_passed_through():
    fake = FakeRagClient()
    async with Client(create_server(Settings(default_top_k=8), fake)) as client:
        result = await client.call_tool("search_codebase", {"query": "ScoreSystem", "top_k": 1})
    assert fake.calls == [("ScoreSystem", 1)]
    assert len(result.structured_content["results"]) == 1


async def test_top_k_out_of_range_is_rejected_before_the_backend():
    fake = FakeRagClient()
    async with Client(create_server(Settings(), fake)) as client:
        result = await client.call_tool("search_codebase", {"query": "x", "top_k": 99})
    assert result.is_error is True
    assert fake.calls == []


async def test_blank_query_is_an_error():
    fake = FakeRagClient()
    async with Client(create_server(Settings(), fake)) as client:
        result = await client.call_tool("search_codebase", {"query": "   "})
    assert result.is_error is True
    assert fake.calls == []


async def test_no_results():
    async with Client(create_server(Settings(), FakeRagClient(sources=[]))) as client:
        result = await client.call_tool("search_codebase", {"query": "multiplayer lobby"})
    assert result.is_error is False
    assert result.content[0].text == "No excerpts found for: multiplayer lobby"
    assert result.structured_content["results"] == []


async def test_backend_error_becomes_a_tool_error_the_model_can_read():
    fake = FakeRagClient(error=RagError("連不到 local-codebase-rag"))
    async with Client(create_server(Settings(), fake)) as client:
        result = await client.call_tool("search_codebase", {"query": "x"})
    assert result.is_error is True
    assert "連不到 local-codebase-rag" in result.content[0].text


async def test_long_excerpts_are_truncated():
    long = dict(FakeRagClient().sources[0], text="a" * 50)
    async with Client(create_server(Settings(max_chars_per_result=10), FakeRagClient([long]))) as client:
        result = await client.call_tool("search_codebase", {"query": "x"})
    r = result.structured_content["results"][0]
    assert r["truncated"] is True
    assert r["text"] == "a" * 10
    assert "… (truncated)" in result.content[0].text
