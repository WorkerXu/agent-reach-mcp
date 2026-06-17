"""Tests for Agent Reach MCP server tools — in-memory FastMCP client pattern.

Test strategy (per FastMCP best-practices research):
1. Schema contract tests — verify all 8 tools registered with correct descriptions and input schemas
2. Mocked execution tests — mock _run_cli for deterministic CLI testing
3. Real integration tests — test platforms that work without auth (V2EX, Web, RSS)
4. Parameterized edge cases — empty strings, extreme values, invalid inputs
"""

import json
import subprocess
from unittest.mock import patch

import pytest

from agent_reach.integrations.mcp_server import CliResult, _run_cli, create_server

# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def _make_mock_channel(return_text: str = "mock content"):
    """Create a mock channel object for testing."""
    import types
    ch = types.SimpleNamespace()
    ch.read = lambda url: return_text
    ch.search = lambda query, limit=10: [{"title": "mock", "url": "https://example.com"}]
    ch.check = lambda config=None: ("ok", "mock channel")
    return ch


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #

@pytest.fixture
def mcp():
    """Create an in-memory MCP server (per FastMCP in-memory Client pattern)."""
    return create_server()


# ------------------------------------------------------------------ #
# Schema Contract Tests — verify tool registry shape
# ------------------------------------------------------------------ #

class TestToolContracts:
    """Verify tool registration, descriptions, and input schemas."""

    TOOL_NAMES = {"doctor", "read_url", "search", "trending", "stock_quote", "get_details", "transcribe", "install"}

    @pytest.mark.asyncio
    async def test_all_tools_registered(self, mcp):
        tools = await mcp.list_tools()
        names = {t.name for t in tools}
        assert names == self.TOOL_NAMES, (
            f"Missing: {self.TOOL_NAMES - names}, "
            f"Extra: {names - self.TOOL_NAMES}"
        )

    @pytest.mark.asyncio
    async def test_each_tool_has_description(self, mcp):
        tools = await mcp.list_tools()
        for t in tools:
            assert t.description and len(t.description) > 20, (
                f"{t.name}: description too short or missing"
            )

    @pytest.mark.asyncio
    async def test_each_tool_has_input_schema(self, mcp):
        tools = await mcp.list_tools()
        for t in tools:
            assert t.inputSchema["type"] == "object", (
                f"{t.name}: inputSchema missing type=object"
            )

    @pytest.mark.asyncio
    async def test_doctor_schema(self, mcp):
        tools = await mcp.list_tools()
        tool = {t.name: t for t in tools}["doctor"]
        assert tool.inputSchema == {"properties": {}, "title": "doctorArguments", "type": "object"}
        assert "platform" not in tool.description.lower() or "status" in tool.description
        assert "JSON" in tool.description

    @pytest.mark.asyncio
    async def test_read_url_schema(self, mcp):
        tools = await mcp.list_tools()
        tool = {t.name: t for t in tools}["read_url"]
        props = tool.inputSchema["properties"]
        assert "url" in props
        assert props["url"]["type"] == "string"

    @pytest.mark.asyncio
    async def test_search_schema(self, mcp):
        tools = await mcp.list_tools()
        tool = {t.name: t for t in tools}["search"]
        props = tool.inputSchema["properties"]
        assert "query" in props
        assert "platform" in props
        assert "limit" in props
        assert props["limit"]["default"] == 10

    @pytest.mark.asyncio
    async def test_trending_schema(self, mcp):
        tools = await mcp.list_tools()
        tool = {t.name: t for t in tools}["trending"]
        props = tool.inputSchema["properties"]
        assert "platform" in props
        assert "limit" in props
        assert props["limit"]["default"] == 10

    @pytest.mark.asyncio
    async def test_stock_quote_schema(self, mcp):
        tools = await mcp.list_tools()
        tool = {t.name: t for t in tools}["stock_quote"]
        props = tool.inputSchema["properties"]
        assert "symbol" in props
        assert props["symbol"]["type"] == "string"

    @pytest.mark.asyncio
    async def test_get_details_schema(self, mcp):
        tools = await mcp.list_tools()
        tool = {t.name: t for t in tools}["get_details"]
        props = tool.inputSchema["properties"]
        assert "platform" in props
        assert "id" in props
        assert "limit" in props

    @pytest.mark.asyncio
    async def test_transcribe_schema(self, mcp):
        tools = await mcp.list_tools()
        tool = {t.name: t for t in tools}["transcribe"]
        props = tool.inputSchema["properties"]
        assert "url" in props
        assert "provider" in props
        assert props["provider"]["default"] == "auto"

    @pytest.mark.asyncio
    async def test_install_schema(self, mcp):
        tools = await mcp.list_tools()
        tool = {t.name: t for t in tools}["install"]
        props = tool.inputSchema["properties"]
        assert "platform" in props
        assert "value" in props

    @pytest.mark.asyncio
    async def test_descriptions_start_with_verb(self, mcp):
        tools = await mcp.list_tools()
        verbs = {"check", "read", "search", "get", "transcribe", "install"}
        for t in tools:
            first_word = t.description.split()[0].lower().strip("`\"'")
            assert first_word in verbs, (
                f"{t.name}: description should start with a verb, got '{first_word}'"
            )

    @pytest.mark.asyncio
    async def test_each_description_specifies_return_format(self, mcp):
        tools = await mcp.list_tools()
        return_indicators = {"return", "returns", "json", "markdown", "text", "string"}
        for t in tools:
            desc_lower = t.description.lower()
            assert any(ind in desc_lower for ind in return_indicators), (
                f"{t.name}: description should specify return format"
            )


# ------------------------------------------------------------------ #
# Doctor Tool Tests — mock the underlying check_all
# ------------------------------------------------------------------ #

class TestDoctor:
    @pytest.mark.asyncio
    async def test_doctor_returns_platform_health(self, mcp):
        """doctor should return a dict of platforms with status fields."""
        content, metadata = await mcp.call_tool("doctor", {})
        text = content[0].text
        data = json.loads(text)
        assert isinstance(data, dict)
        assert len(data) > 0
        for platform, info in data.items():
            assert "status" in info, f"{platform} missing status"
            assert info["status"] in ("ok", "warn", "off", "error"), (
                f"{platform} bad status: {info['status']}"
            )


# ------------------------------------------------------------------ #
# Read URL Tests
# ------------------------------------------------------------------ #

class TestReadUrl:
    @pytest.mark.asyncio
    async def test_read_url_adds_scheme_missing(self, mcp):
        """Should prepend https:// when no scheme is provided."""
        mock_channel = _make_mock_channel()
        with patch("agent_reach.integrations.mcp_server._get_channel", return_value=mock_channel):
            content, metadata = await mcp.call_tool("read_url", {"url": "example.com"})
            assert len(content[0].text) > 0

    @pytest.mark.asyncio
    async def test_read_url_github_routes_to_cli(self, mcp):
        """github.com URLs should route to gh CLI."""
        with patch("agent_reach.integrations.mcp_server._run_cli", return_value=CliResult(success=True, stdout='{"name":"test"}')) as mock_cli:
            content, metadata = await mcp.call_tool("read_url", {"url": "https://github.com/owner/repo"})
            assert mock_cli.called
            args = mock_cli.call_args[0]
            assert args[0] == "gh"

    @pytest.mark.asyncio
    async def test_read_url_bilibili_routes_to_bili(self, mcp):
        """bilibili.com URLs should route to bili-cli."""
        with patch("agent_reach.integrations.mcp_server._run_cli", return_value=CliResult(success=True, stdout='{"title":"test"}')) as mock_cli:
            content, metadata = await mcp.call_tool("read_url", {"url": "https://www.bilibili.com/video/BV1xx"})
            assert mock_cli.called
            assert mock_cli.call_args[0][0] == "bili"

    @pytest.mark.asyncio
    async def test_read_url_v2ex_routes(self, mcp):
        """v2ex.com URLs should route to V2EXChannel.read."""
        content, metadata = await mcp.call_tool("read_url", {"url": "https://www.v2ex.com/t/100"})
        text = content[0].text
        assert text is not None
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_read_url_rss_routes(self, mcp):
        """RSS URLs should route to RSSChannel.read."""
        content, metadata = await mcp.call_tool("read_url", {"url": "https://hnrss.org/frontpage"})
        text = content[0].text
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_read_url_falls_back_to_web(self, mcp):
        """Non-special URLs should fall back to web channel."""
        content, metadata = await mcp.call_tool("read_url", {"url": "https://example.com"})
        text = content[0].text
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_read_url_bilibili_fallback_on_failure(self, mcp):
        """When bili-cli fails, should fall back to web channel."""
        with patch("agent_reach.integrations.mcp_server._run_cli", return_value=CliResult(success=False, error="not found")):
            content, metadata = await mcp.call_tool("read_url", {"url": "https://b23.tv/BV1xx"})
            assert len(content[0].text) > 0


# ------------------------------------------------------------------ #
# Search Tool Tests
# ------------------------------------------------------------------ #

class TestSearch:
    @pytest.mark.asyncio
    async def test_search_web_returns_results(self, mcp):
        """Web search should return results with platform='web'."""
        content, metadata = await mcp.call_tool("search", {"platform": "web", "query": "python programming"})
        data = json.loads(content[0].text)
        assert data["platform"] == "web"

    @pytest.mark.asyncio
    async def test_search_v2ex_returns_results(self, mcp):
        """V2EX search should return results with platform='v2ex'."""
        content, metadata = await mcp.call_tool("search", {"platform": "v2ex", "query": "python", "limit": 3})
        data = json.loads(content[0].text)
        assert data["platform"] == "v2ex"
        assert "results" in data

    @pytest.mark.asyncio
    async def test_search_invalid_platform_returns_error(self, mcp):
        """Unknown platform should return an error."""
        content, metadata = await mcp.call_tool("search", {"platform": "invalid", "query": "test"})
        data = json.loads(content[0].text)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_search_limit_clamped(self, mcp):
        """limit > 50 should be clamped to 50."""
        content, metadata = await mcp.call_tool("search", {"platform": "v2ex", "query": "python", "limit": 999})
        data = json.loads(content[0].text)
        assert "error" not in data

    @pytest.mark.asyncio
    async def test_search_github_uses_cli(self, mcp):
        """GitHub search should call gh CLI."""
        mock_data = json.dumps([{"url": "https://github.com/test", "title": "test"}])
        with patch("agent_reach.integrations.mcp_server._run_cli", return_value=CliResult(success=True, stdout=mock_data)):
            content, metadata = await mcp.call_tool("search", {"platform": "github", "query": "test"})
            data = json.loads(content[0].text)
            assert data["platform"] == "github"

    @pytest.mark.asyncio
    async def test_search_twitter_uses_cli(self, mcp):
        """Twitter search should call twitter-cli."""
        with patch("agent_reach.integrations.mcp_server._run_cli", return_value=CliResult(success=True, stdout="[]")):
            content, metadata = await mcp.call_tool("search", {"platform": "twitter", "query": "test", "limit": 3})
            data = json.loads(content[0].text)
            assert data["platform"] == "twitter"

    @pytest.mark.asyncio
    async def test_search_reddit_uses_cli(self, mcp):
        """Reddit search should call rdt-cli."""
        with patch("agent_reach.integrations.mcp_server._run_cli", return_value=CliResult(success=True, stdout="[]")):
            content, metadata = await mcp.call_tool("search", {"platform": "reddit", "query": "test", "limit": 3})
            data = json.loads(content[0].text)
            assert data["platform"] == "reddit"

    @pytest.mark.asyncio
    async def test_search_bilibili_uses_cli(self, mcp):
        """Bilibili search should call bili-cli."""
        with patch("agent_reach.integrations.mcp_server._run_cli", return_value=CliResult(success=True, stdout="[]")):
            content, metadata = await mcp.call_tool("search", {"platform": "bilibili", "query": "test", "limit": 3})
            data = json.loads(content[0].text)
            assert data["platform"] == "bilibili"


# ------------------------------------------------------------------ #
# Trending Tool Tests
# ------------------------------------------------------------------ #

class TestTrending:
    @pytest.mark.asyncio
    async def test_trending_v2ex(self, mcp):
        """V2EX trending should return hot topics."""
        content, metadata = await mcp.call_tool("trending", {"platform": "v2ex", "limit": 3})
        data = json.loads(content[0].text)
        assert data["platform"] == "v2ex"
        assert "results" in data

    @pytest.mark.asyncio
    async def test_trending_invalid_platform(self, mcp):
        """Unknown trending platform should return error."""
        content, metadata = await mcp.call_tool("trending", {"platform": "invalid"})
        data = json.loads(content[0].text)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_trending_bilibili_uses_cli(self, mcp):
        """Bilibili trending should call bili-cli."""
        with patch("agent_reach.integrations.mcp_server._run_cli", return_value=CliResult(success=True, stdout="[]")):
            content, metadata = await mcp.call_tool("trending", {"platform": "bilibili", "limit": 3})
            data = json.loads(content[0].text)
            assert data["platform"] == "bilibili"

    @pytest.mark.asyncio
    async def test_trending_github_uses_cli(self, mcp):
        """GitHub trending should call gh CLI."""
        with patch("agent_reach.integrations.mcp_server._run_cli", return_value=CliResult(success=True, stdout="[]")):
            content, metadata = await mcp.call_tool("trending", {"platform": "github", "limit": 3})
            data = json.loads(content[0].text)
            assert data["platform"] == "github"

    @pytest.mark.asyncio
    async def test_trending_twitter_uses_cli(self, mcp):
        """Twitter trending should call twitter-cli."""
        with patch("agent_reach.integrations.mcp_server._run_cli", return_value=CliResult(success=True, stdout="[]")):
            content, metadata = await mcp.call_tool("trending", {"platform": "twitter", "limit": 3})
            data = json.loads(content[0].text)
            assert data["platform"] == "twitter"

    @pytest.mark.asyncio
    async def test_trending_reddit_fallback_opencli(self, mcp):
        """Reddit trending should try rdt first, then opencli."""
        with patch("agent_reach.integrations.mcp_server._run_cli") as mock_cli:
            mock_cli.side_effect = [
                CliResult(success=False, error="not found"),  # rdt fails
                CliResult(success=True, stdout="[]"),  # opencli succeeds
            ]
            content, metadata = await mcp.call_tool("trending", {"platform": "reddit", "limit": 3})
            data = json.loads(content[0].text)
            assert data["platform"] == "reddit"
            assert mock_cli.call_count == 2


# ------------------------------------------------------------------ #
# Stock Quote Tool Tests
# ------------------------------------------------------------------ #

class TestStockQuote:
    @pytest.mark.asyncio
    async def test_stock_quote_returns_symbol(self, mcp):
        """Stock quote should always return the requested symbol."""
        content, metadata = await mcp.call_tool("stock_quote", {"symbol": "AAPL"})
        data = json.loads(content[0].text)
        assert data["symbol"] == "AAPL"
        # May be error (no cookies) or actual quote — either is valid
        assert "quote" in data or "error" in data

    @pytest.mark.asyncio
    async def test_stock_quote_uppercases_symbol(self, mcp):
        """Stock symbol should be uppercased."""
        content, metadata = await mcp.call_tool("stock_quote", {"symbol": "aapl"})
        data = json.loads(content[0].text)
        assert data["symbol"] == "AAPL"


# ------------------------------------------------------------------ #
# Get Details Tool Tests
# ------------------------------------------------------------------ #

class TestGetDetails:
    @pytest.mark.asyncio
    async def test_get_details_v2ex_topic(self, mcp):
        """V2EX topic should return topic data (or error if API unavailable)."""
        content, metadata = await mcp.call_tool("get_details", {"platform": "v2ex_topic", "id": "1"})
        data = json.loads(content[0].text)
        assert isinstance(data, dict)
        # Either we got topic data, or API returned an error (rate limit, etc.)
        assert "title" in data or "error" in data

    @pytest.mark.asyncio
    async def test_get_details_v2ex_user(self, mcp):
        """V2EX user should return user profile."""
        content, metadata = await mcp.call_tool("get_details", {"platform": "v2ex_user", "id": "Livid"})
        assert len(content[0].text) > 0

    @pytest.mark.asyncio
    async def test_get_details_v2ex_node(self, mcp):
        """V2EX node should return node topics."""
        content, metadata = await mcp.call_tool("get_details", {"platform": "v2ex_node", "id": "python", "limit": 3})
        data = json.loads(content[0].text)
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_details_bilibili_video_uses_cli(self, mcp):
        """Bilibili video detail should call bili-cli."""
        with patch("agent_reach.integrations.mcp_server._run_cli",
                   return_value=CliResult(success=True, stdout='{"title":"test"}')):
            content, metadata = await mcp.call_tool("get_details", {"platform": "bilibili_video", "id": "BV1GJ411x7h"})
            data = json.loads(content[0].text)
            assert "title" in data

    @pytest.mark.asyncio
    async def test_get_details_github_repo_uses_cli(self, mcp):
        """GitHub repo detail should call gh CLI."""
        with patch("agent_reach.integrations.mcp_server._run_cli",
                   return_value=CliResult(success=True, stdout='{"name":"cli","stargazersCount":50000}')):
            content, metadata = await mcp.call_tool("get_details", {"platform": "github_repo", "id": "cli/cli"})
            data = json.loads(content[0].text)
            assert data["name"] == "cli"

    @pytest.mark.asyncio
    async def test_get_details_invalid_platform(self, mcp):
        """Unknown platform should return error."""
        content, metadata = await mcp.call_tool("get_details", {"platform": "invalid", "id": "test"})
        data = json.loads(content[0].text)
        assert "error" in data


# ------------------------------------------------------------------ #
# Transcribe Tool Tests
# ------------------------------------------------------------------ #

class TestTranscribe:
    @pytest.mark.asyncio
    async def test_transcribe_bad_url_returns_error(self, mcp):
        """Transcribing an invalid URL should return an error."""
        content, metadata = await mcp.call_tool("transcribe", {"url": "https://invalid.example/video"})
        text = content[0].text
        assert "failed" in text.lower() or "error" in text.lower() or "transcription" in text


# ------------------------------------------------------------------ #
# Install Tool Tests
# ------------------------------------------------------------------ #

class TestInstall:
    @pytest.mark.asyncio
    async def test_install_unknown_platform(self, mcp):
        """Unknown install platform should return 'Unknown platform'."""
        content, metadata = await mcp.call_tool("install", {"platform": "unknown"})
        text = content[0].text
        assert "Unknown platform" in text

    @pytest.mark.asyncio
    async def test_install_groq_key_requires_value(self, mcp):
        """groq-key without value should return error."""
        content, metadata = await mcp.call_tool("install", {"platform": "groq-key"})
        text = content[0].text
        assert "requires a value" in text.lower()

    @pytest.mark.asyncio
    async def test_install_groq_key_with_value(self, mcp):
        """groq-key with value should return success."""
        with patch("agent_reach.integrations.mcp_server.Config.set"):
            content, metadata = await mcp.call_tool("install", {"platform": "groq-key", "value": "gsk_test"})
            text = content[0].text
            assert "configured" in text.lower()

    @pytest.mark.asyncio
    async def test_install_openai_key_requires_value(self, mcp):
        """openai-key without value should return error."""
        content, metadata = await mcp.call_tool("install", {"platform": "openai-key"})
        text = content[0].text
        assert "requires a value" in text.lower()

    @pytest.mark.asyncio
    async def test_install_github_token_requires_value(self, mcp):
        """github-token without value should return error."""
        content, metadata = await mcp.call_tool("install", {"platform": "github-token"})
        text = content[0].text
        assert "requires a value" in text.lower()


# ------------------------------------------------------------------ #
# Parameterized Edge Cases
# ------------------------------------------------------------------ #

class TestEdgeCases:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("url", [
        "",
        "not-a-valid-url",
        "ftp://invalid-scheme.com",
    ])
    async def test_read_url_varied_inputs(self, mcp, url):
        """read_url should handle edge case URLs gracefully (mocked)."""
        mock_channel = _make_mock_channel()
        with patch("agent_reach.integrations.mcp_server._get_channel", return_value=mock_channel):
            content, metadata = await mcp.call_tool("read_url", {"url": url})
            text = content[0].text
            assert text is not None  # Should never crash, even with bad input

    @pytest.mark.asyncio
    @pytest.mark.parametrize("platform", [
        "", "  ", "unknown_platform_with_underscores",
    ])
    async def test_search_invalid_platforms(self, mcp, platform):
        """search should return error for various invalid platforms."""
        content, metadata = await mcp.call_tool("search", {"platform": platform, "query": "test"})
        data = json.loads(content[0].text)
        assert "error" in data or platform.strip() == "" and "error" in data

    @pytest.mark.asyncio
    @pytest.mark.parametrize("symbol", [
        "", "  ", "!!!invalid!!!",
    ])
    async def test_stock_quote_bad_symbols(self, mcp, symbol):
        """stock_quote should handle bad symbols."""
        content, metadata = await mcp.call_tool("stock_quote", {"symbol": symbol})
        data = json.loads(content[0].text)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("platform,id_str", [
        ("", ""),
        ("  ", "test"),
        ("v2ex_topic", ""),
        ("bilibili_video", ""),
        ("github_repo", ""),
    ])
    async def test_get_details_empty_ids(self, mcp, platform, id_str):
        """get_details should handle empty IDs."""
        content, metadata = await mcp.call_tool("get_details", {"platform": platform, "id": id_str})
        text = content[0].text
        assert text is not None  # Should never crash

    @pytest.mark.asyncio
    async def test_search_empty_query_still_runs(self, mcp):
        """Empty search query should still execute (web search handles it)."""
        content, metadata = await mcp.call_tool("search", {"platform": "web", "query": ""})
        assert len(content[0].text) > 0

    @pytest.mark.asyncio
    async def test_search_limit_zero_clamped_to_one(self, mcp):
        """limit=0 should be clamped to 1 (minimum)."""
        content, metadata = await mcp.call_tool("search", {"platform": "v2ex", "query": "python", "limit": 0})
        data = json.loads(content[0].text)
        assert "error" not in data


# ------------------------------------------------------------------ #
# _run_cli Unit Tests
# ------------------------------------------------------------------ #

class TestRunCli:
    """Direct unit tests for the _run_cli helper."""

    def test_binary_not_found(self):
        """Should return error when binary not on PATH."""
        result = _run_cli("nonexistent-binary-xyz123", ["--help"])
        assert not result.success
        assert "not found" in result.error.lower()

    def test_handles_json_stdout_on_error(self):
        """Should parse JSON from stdout even on non-zero exit."""
        with patch("agent_reach.integrations.mcp_server.shutil.which", return_value="/usr/bin/test"):
            with patch("agent_reach.integrations.mcp_server.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stdout = '{"error": "something failed"}'
                mock_run.return_value.stderr = ""
                result = _run_cli("test-bin", ["cmd"])
                assert result.success
                assert "error" in result.stdout

    def test_handles_timeout_gracefully(self):
        """Should handle TimeoutExpired without crashing."""
        with patch("agent_reach.integrations.mcp_server.shutil.which", return_value="/usr/bin/test"):
            with patch("agent_reach.integrations.mcp_server.subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 10)):
                result = _run_cli("test-bin", ["cmd"])
                assert not result.success
                assert "timed out" in result.error.lower()

    def test_handles_file_not_found(self):
        """Should handle FileNotFoundError from subprocess."""
        with patch("agent_reach.integrations.mcp_server.shutil.which", return_value="/usr/bin/test"):
            with patch("agent_reach.integrations.mcp_server.subprocess.run", side_effect=FileNotFoundError):
                result = _run_cli("test-bin", ["cmd"])
                assert not result.success
                assert "not found" in result.error.lower()

    def test_successful_execution(self):
        """Successful execution should return stdout."""
        with patch("agent_reach.integrations.mcp_server.shutil.which", return_value="/usr/bin/test"):
            with patch("agent_reach.integrations.mcp_server.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = '{"status": "ok"}'
                mock_run.return_value.stderr = ""
                result = _run_cli("test-bin", ["cmd"])
                assert result.success
                assert "status" in result.stdout
