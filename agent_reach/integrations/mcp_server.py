# -*- coding: utf-8 -*-
"""
Agent Reach MCP Server — expose an approved subset of internet platforms as MCP tools.

Provides 7 task-shaped tools:
  doctor, read_url, search, trending, get_details, transcribe, install

Run: python -m agent_reach.integrations.mcp_server
     agent-reach mcp
     uvx agent-reach mcp
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, Dict
from urllib.parse import urlparse

from agent_reach.channels import get_all_channels
from agent_reach.config import Config
from agent_reach.core import AgentReach

# ------------------------------------------------------------------ #
# MCP imports
# ------------------------------------------------------------------ #
try:
    from mcp.server.fastmcp import FastMCP
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

# ------------------------------------------------------------------ #
# Constants
# ------------------------------------------------------------------ #
MAX_LIMIT = 50
DEFAULT_LIMIT = 10

# This deployment excludes these platforms from every MCP entry point.
EXCLUDED_MCP_PLATFORMS = frozenset({
    "xueqiu",
    "xiaoyuzhou",
    "linkedin",
    "xiaohongshu",
    "twitter",
})
EXCLUDED_MCP_DOMAINS = frozenset({
    "xueqiu.com",
    "xiaoyuzhoufm.com",
    "linkedin.com",
    "xiaohongshu.com",
    "xhslink.com",
    "x.com",
    "twitter.com",
    "t.co",
})


def _is_excluded_domain(domain: str) -> bool:
    hostname = domain.lower().split(":", 1)[0].rstrip(".")
    return any(hostname == blocked or hostname.endswith(f".{blocked}") for blocked in EXCLUDED_MCP_DOMAINS)


def _excluded_url_message(domain: str) -> str:
    return f"Unsupported URL domain in this deployment: {domain}."


# ------------------------------------------------------------------ #
# Structured CLI runner
# ------------------------------------------------------------------ #

@dataclass
class CliResult:
    """Structured result from running a CLI tool."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    error: str = ""


def _run_cli(bin_name: str, args: list, timeout: int = 15) -> CliResult:
    """Run a CLI binary and return a structured result.

    Per Python 3.14 subprocess docs:
    - `check=True` raises CalledProcessError on non-zero exit
    - `capture_output=True` captures both stdout and stderr
    - `timeout=X` raises TimeoutExpired if command hangs
    - Commands passed as list (never shell=True)
    """
    binary = shutil.which(bin_name)
    if not binary:
        return CliResult(success=False, error=f"{bin_name} not found on PATH. Install: uv tool install {bin_name}")
    try:
        r = subprocess.run(
            [binary, *args],
            capture_output=True, text=True, timeout=timeout,
            check=False,  # We handle return codes ourselves for JSON error parsing
        )
        if r.returncode == 0:
            return CliResult(success=True, stdout=r.stdout)
        # Try to parse JSON error from stdout (common CLI pattern: exit 1 but data in stdout)
        trimmed = r.stdout.strip()
        if trimmed and trimmed.startswith("{"):
            try:
                json.loads(trimmed)
                return CliResult(success=True, stdout=trimmed, stderr=r.stderr)
            except json.JSONDecodeError:
                pass
        return CliResult(success=False, stdout=r.stdout, stderr=r.stderr, error=r.stderr.strip() or r.stdout.strip() or f"{bin_name} exited with code {r.returncode}")
    except FileNotFoundError:
        return CliResult(success=False, error=f"{bin_name} not found on PATH")
    except subprocess.TimeoutExpired:
        return CliResult(success=False, error=f"{bin_name} timed out after {timeout}s")
    except Exception as e:
        return CliResult(success=False, error=f"{bin_name} failed: {e}")

# ------------------------------------------------------------------ #
# Lazy-loaded channel singletons (cached after first access)
# ------------------------------------------------------------------ #
_channel_cache: Dict[str, Any] = {}


def _get_channel(name: str):
    if name not in _channel_cache:
        for ch in get_all_channels():
            if ch.name == name:
                # Import all channel modules to get full method sets
                _import_channel_module(name)
                # Re-get channel after module import (class may be redefined)
                for ch2 in get_all_channels():
                    if ch2.name == name:
                        _channel_cache[name] = ch2
                        break
                break
    return _channel_cache.get(name)


def _import_channel_module(name: str):
    try:
        __import__(f"agent_reach.channels.{name}", fromlist=["Channel"])
    except ImportError:
        pass


# ------------------------------------------------------------------ #
# Server
# ------------------------------------------------------------------ #

def create_server(
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    json_response: bool = False,
    stateless_http: bool = False,
) -> FastMCP:
    mcp = FastMCP(
        "agent-reach",
        host=host,
        port=port,
        json_response=json_response,
        stateless_http=stateless_http,
    )

    config = Config()
    eyes = AgentReach(config)

    def _doctor_results() -> Dict[str, Any]:
        return {
            name: result
            for name, result in eyes.doctor().items()
            if name.lower() not in EXCLUDED_MCP_PLATFORMS
        }

    def _platforms_summary() -> str:
        results = _doctor_results()
        ok = sum(1 for r in results.values() if r["status"] == "ok")
        total = len(results)
        return f"{ok}/{total} platforms available"

    # ------------------------------------------------------------------ #
    # Tool 1: doctor
    # ------------------------------------------------------------------ #
    @mcp.tool(
        name="doctor",
        description="""Check which internet platforms are installed, authenticated, and ready to use.

Scans the platforms exposed by this MCP deployment and returns a structured health report. Each entry
shows status ('ok'|'warn'|'off'|'error'), which backend is active, and actionable
next steps if a platform is unavailable.

When to use:
- Before making a platform-specific call to verify the tool is ready
- Diagnosing setup or authentication issues
- After running install to confirm everything works

Negative: Does NOT install or configure anything — use install() for that.

Returns JSON dict keyed by platform name, each value contains:
  status (str), name (str), message (str), tier (int),
  backends (list[str]), active_backend (str|null)
""",
    )
    def doctor() -> str:
        results = _doctor_results()
        return json.dumps(results, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------ #
    # Tool 2: read_url
    # ------------------------------------------------------------------ #
    @mcp.tool(
        name="read_url",
        description="""Read web page content from any accessible URL as clean markdown text.

Smart auto-routing by domain:
  - v2ex.com — fetches full topic with all replies via V2EX API
  - URLs containing /feed, /rss, .xml, atom — parses RSS/Atom feed via feedparser
  - bilibili.com or b23.tv — returns video metadata via bili-cli
  - github.com/owner/repo — returns repo metadata via gh CLI
  - Everything else — Jina Reader AI (primary) or direct HTTP fetch (fallback)

When to use:
- Reading news articles, blog posts, documentation pages
- Getting V2EX discussions with replies
- Subscribing to RSS/Atom feeds
- Fetching video metadata from Bilibili or repo info from GitHub

Negative: Does NOT search — use search() for finding content.
Does NOT work on pages behind login walls or CAPTCHAs.

url: Full URL including scheme (http:// or https://). If missing, https:// is prepended.

Returns: Clean markdown-formatted content text (stripped of ads, navigation, cruft)
""",
    )
    def read_url(url: str) -> str:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        if _is_excluded_domain(domain):
            return _excluded_url_message(domain)

        # V2EX routing — fallback to web channel if V2EX API/scraping is unreachable
        if "v2ex.com" in domain:
            try:
                ch = _get_channel("v2ex")
                if ch and hasattr(ch, "read"):
                    result = ch.read(url)
                    if "unreachable" not in result:
                        return result
                from agent_reach.channels.v2ex import V2EXChannel
                result = V2EXChannel().read(url)
                if "unreachable" not in result:
                    return result
            except Exception:
                pass
            # Fallback to web channel
            ch = _get_channel("web")
            if ch and hasattr(ch, "read"):
                try:
                    text = ch.read(url)
                    return text
                except Exception:
                    pass
            return "(V2EX unreachable from this server — try search(platform='web') to find V2EX content via Exa)"

        # RSS routing
        if any(x in url.lower() for x in ["/feed", "/rss", ".xml", "atom"]):
            ch = _get_channel("rss")
            if ch and hasattr(ch, "read"):
                return ch.read(url)
            from agent_reach.channels.rss import RSSChannel
            return RSSChannel().read(url)

        # Bilibili routing — use _run_cli helper
        if "bilibili.com" in domain or "b23.tv" in domain:
            result = _run_cli("bili", ["video", url, "--json"], timeout=20)
            if result.success:
                return result.stdout
            # fallback to web channel

        # GitHub routing — use _run_cli helper
        if "github.com" in domain:
            parsed_path = parsed.path.strip("/").split("/")
            if len(parsed_path) >= 2:
                owner, repo = parsed_path[0], parsed_path[1]
                result = _run_cli("gh", [
                    "repo", "view", f"{owner}/{repo}",
                    "--json", "name,owner,description,url,stargazersCount,forkCount,primaryLanguage,createdAt,updatedAt,homepageUrl,isPrivate,issues,licenseInfo,pullRequests,repositoryTopics",
                ], timeout=15)
                if result.success:
                    return result.stdout
            # fallback to web channel

        # Default: web channel (Jina Reader or direct HTTP)
        ch = _get_channel("web")
        if ch and hasattr(ch, "read"):
            return ch.read(url)
        from agent_reach.channels.web import WebChannel
        return WebChannel().read(url)

    # ------------------------------------------------------------------ #
    # Tool 3: search
    # ------------------------------------------------------------------ #
    @mcp.tool(
        name="search",
        description="""Search for content across supported internet platforms by keyword.

Supported platforms (5):
  - "web": General web search via DuckDuckGo → Jina Reader
  - "v2ex": Chinese tech forum topics
  - "github": Repositories, code, and issues (requires gh CLI + auth)
  - "reddit": Posts and comments (requires rdt-cli + auth cookies)
  - "bilibili": Videos (requires bili-cli)

When to use:
- Finding web pages about a topic (platform="web")
- Searching tech discussions (platform="v2ex")
- Finding GitHub repos (platform="github")
- Looking up discussions and videos (reddit, bilibili)

Negative: Does NOT read full content of a URL — use read_url() for that.
Does NOT get detailed info by ID — use get_details() for that.

query: Search keywords (2-100 chars)
platform: Target platform (web, v2ex, github, reddit, bilibili)
limit: Max results, clamped to 1-50 (default 10)

Returns JSON: {"results": [...], "platform": str, "query": str}
""",
    )
    def search(platform: str, query: str, limit: int = DEFAULT_LIMIT) -> str:
        platform = platform.lower().strip()
        limit = min(max(1, limit), MAX_LIMIT)

        if platform == "web":
            # Try Exa via mcporter first (works from server IPs), fallback to DuckDuckGo
            exa_result = _run_cli("mcporter", [
                "call", f'exa.web_search_exa(query: "{query}", numResults: {str(limit)})'
            ], timeout=20)
            if exa_result.success and exa_result.stdout.strip():
                return json.dumps({"results": exa_result.stdout, "platform": "web", "query": query}, ensure_ascii=False)
            # Fallback
            return json.dumps({"error": "Web search unavailable from this server. Try Exa: mcporter config add exa https://mcp.exa.ai/mcp", "platform": "web", "query": query})

        if platform == "v2ex":
            from agent_reach.channels.v2ex import V2EXChannel
            results = V2EXChannel().search(query, limit=limit)
            return json.dumps({"results": results, "platform": "v2ex", "query": query}, ensure_ascii=False)

        if platform == "github":
            result = _run_cli("gh", ["search", query, "--limit", str(limit), "--json", "url,title"], timeout=15)
            if result.success:
                results = json.loads(result.stdout) if result.stdout.strip() else []
            else:
                results = [{"error": result.error}]
            return json.dumps({"results": results, "platform": "github", "query": query}, ensure_ascii=False)

        if platform == "reddit":
            # rdt-cli 0.4.x uses --json and wraps structured payloads in
            # {"ok": true, "data": ...}; older releases returned the list directly.
            result = _run_cli("rdt", ["search", query, "--limit", str(limit), "--compact", "--json"], timeout=20)
            if result.success:
                payload = json.loads(result.stdout) if result.stdout.strip() else []
                results = payload.get("data", payload) if isinstance(payload, dict) else payload
            else:
                results = [{"error": result.error or "rdt-cli not installed or not authenticated. Install: uv tool install rdt-cli"}]
            return json.dumps({"results": results, "platform": "reddit", "query": query}, ensure_ascii=False)

        if platform == "bilibili":
            result = _run_cli("bili", ["search", query, "--type", "video", "-n", str(limit), "--json"], timeout=20)
            if result.success:
                results = json.loads(result.stdout) if result.stdout.strip() else []
            else:
                results = [{"error": result.error or "bili-cli not installed or not configured. Install: uv tool install bilibili-cli"}]
            return json.dumps({"results": results, "platform": "bilibili", "query": query}, ensure_ascii=False)

        return json.dumps({"error": f"Unknown search platform: {platform}. Supported: web, v2ex, github, reddit, bilibili", "platform": platform, "query": query})

    # ------------------------------------------------------------------ #
    # Tool 4: trending
    # ------------------------------------------------------------------ #
    @mcp.tool(
        name="trending",
        description="""Get hot, trending, or popular content from supported internet platforms.

Supported platforms (4):
  - "v2ex": Hot topics on Chinese tech forum V2EX (no auth needed)
  - "bilibili": Trending videos (requires bili-cli)
  - "reddit": Hot posts across Reddit (requires rdt-cli + auth)
  - "github": Trending repos sorted by stars (requires gh CLI)

When to use:
- Finding what's popular right now on a platform
- Discovering trending tech discussions (v2ex)
- Browsing popular videos (bilibili)

Negative: Does NOT read full content — use read_url() for that.
Does NOT search by keyword — use search() for that.

platform: Target platform (v2ex, bilibili, reddit, github)
limit: Max results, clamped to 1-50 (default 10)

Returns JSON: {"results": [...], "platform": str}
""",
    )
    def trending(platform: str, limit: int = DEFAULT_LIMIT) -> str:
        platform = platform.lower().strip()
        limit = min(max(1, limit), MAX_LIMIT)

        if platform == "v2ex":
            from agent_reach.channels.v2ex import V2EXChannel
            results = V2EXChannel().get_hot_topics(limit=limit)
            return json.dumps({"results": results, "platform": platform}, ensure_ascii=False)

        if platform == "bilibili":
            result = _run_cli("bili", ["hot", "--limit", str(limit), "-f", "json"], timeout=15)
            if result.success:
                results = json.loads(result.stdout) if result.stdout.strip() else []
            else:
                results = [{"error": result.error}]
            return json.dumps({"results": results, "platform": platform}, ensure_ascii=False)

        if platform == "reddit":
            rdt_result = _run_cli("rdt", ["popular", "--limit", str(limit), "--compact", "--json"], timeout=20)
            if rdt_result.success:
                payload = json.loads(rdt_result.stdout) if rdt_result.stdout.strip() else []
                results = payload.get("data", payload) if isinstance(payload, dict) else payload
            else:
                opencli_result = _run_cli("opencli", ["reddit", "hot", "--limit", str(limit)], timeout=20)
                if opencli_result.success:
                    results = json.loads(opencli_result.stdout) if opencli_result.stdout.strip() else [{"error": opencli_result.error}]
                else:
                    results = [{"error": "No Reddit CLI available. Install: uv tool install rdt-cli"}]
            return json.dumps({"results": results, "platform": platform}, ensure_ascii=False)

        if platform == "github":
            result = _run_cli("gh", ["search", "stars:>1000", "--sort", "stars", "--limit", str(limit), "--json", "url,name,description,language,stargazersCount"], timeout=15)
            if result.success:
                results = json.loads(result.stdout) if result.stdout.strip() else []
            else:
                results = [{"error": result.error}]
            return json.dumps({"results": results, "platform": platform}, ensure_ascii=False)

        return json.dumps({"error": f"Unknown trending platform: {platform}. Supported: v2ex, bilibili, reddit, github"})

    # ------------------------------------------------------------------ #
    # Tool 5: get_details
    # ------------------------------------------------------------------ #
    @mcp.tool(
        name="get_details",
        description="""Get detailed information from a platform by ID, name, or URL.

Supported platforms (5):
  - "v2ex_topic": Full V2EX topic with all replies. id: topic number (e.g. 100)
  - "v2ex_user": V2EX user profile. id: username (e.g. Livid)
  - "v2ex_node": Topics in a V2EX node. id: node name (e.g. python, go, apple)
  - "bilibili_video": Bilibili video details. id: BV number or URL (e.g. BV1GJ411x7h)
  - "github_repo": GitHub repo details. id: owner/repo (e.g. cli/cli)

When to use:
- Reading a V2EX discussion with all replies
- Looking up a V2EX user's profile
- Getting Bilibili video metadata (title, views, likes, uploader)
- Getting GitHub repo details (stars, forks, language, license, topics)

Negative: Does NOT search by keyword — use search() for that.
Does NOT fetch GitHub code or issues — use read_url() for deeper content.

platform: v2ex_topic, v2ex_user, v2ex_node, bilibili_video, github_repo
id: Platform-specific identifier (topic number, username, node name, BV number, owner/repo)
limit: Max results for list queries, clamped to 1-50 (default 20, used by v2ex_node)

Returns: Platform-specific JSON detail
""",
    )
    def get_details(platform: str, id: str, limit: int = 20) -> str:
        platform = platform.lower().strip()
        limit = min(max(1, limit), MAX_LIMIT)

        if platform == "v2ex_topic":
            try:
                from agent_reach.channels.v2ex import V2EXChannel
                topic_id = int(id) if id.isdigit() else 0
                result = V2EXChannel().get_topic(topic_id)
            except Exception as e:
                return json.dumps({"error": f"V2EX topic lookup failed: {e}"})
            return json.dumps(result, ensure_ascii=False)

        if platform == "v2ex_user":
            try:
                from agent_reach.channels.v2ex import V2EXChannel
                result = V2EXChannel().get_user(id)
            except Exception as e:
                return json.dumps({"error": f"V2EX user lookup failed: {e}"})
            return json.dumps(result, ensure_ascii=False)

        if platform == "v2ex_node":
            try:
                from agent_reach.channels.v2ex import V2EXChannel
                results = V2EXChannel().get_node_topics(id, limit=limit)
            except Exception as e:
                return json.dumps({"error": f"V2EX node lookup failed: {e}"})
            return json.dumps(results, ensure_ascii=False)

        if platform == "bilibili_video":
            result = _run_cli("bili", ["video", id, "--json"], timeout=20)
            if result.success:
                data = json.loads(result.stdout)
                return json.dumps(data, ensure_ascii=False)
            return json.dumps({"error": result.error})

        if platform == "github_repo":
            result = _run_cli("gh", [
                "repo", "view", id,
                "--json", "name,owner,description,url,stargazersCount,forkCount,primaryLanguage,createdAt,updatedAt,licenseInfo,repositoryTopics",
            ], timeout=15)
            if result.success:
                data = json.loads(result.stdout)
                return json.dumps(data, ensure_ascii=False)
            return json.dumps({"error": result.error})

        return json.dumps({"error": f"Unknown detail platform: {platform}. Supported: v2ex_topic, v2ex_user, v2ex_node, bilibili_video, github_repo"})

    # ------------------------------------------------------------------ #
    # Tool 6: transcribe
    # ------------------------------------------------------------------ #
    @mcp.tool(
        name="transcribe",
        description="""Transcribe audio from a YouTube video URL or a local audio file.

Uses yt-dlp to download audio + Whisper API (Groq → OpenAI fallback) for
transcription. Supports long videos (auto-chunked).

Requirements:
  - yt-dlp installed (pip install yt-dlp)
  - ffmpeg installed
  - Groq API key (free at https://console.groq.com) or OpenAI API key
  - Configure provider key: agent-reach configure groq-key gsk_xxxxx

Provider options:
  - "auto": Try Groq first, fall back to OpenAI
  - "groq": Use Groq's free whisper-large-v3 (recommended)
  - "openai": Use OpenAI's whisper-1

Returns: Full transcript text
""",
    )
    def transcribe(url: str, provider: str = "auto") -> str:
        if _is_excluded_domain(urlparse(url).netloc.lower()):
            return _excluded_url_message(urlparse(url).netloc.lower())
        from agent_reach.transcribe import transcribe as _transcribe

        try:
            text = _transcribe(url, provider=provider, config=config)
            return text
        except Exception as e:
            return f"Transcription failed: {e}"

    # ------------------------------------------------------------------ #
    # Tool 7: install
    # ------------------------------------------------------------------ #
    @mcp.tool(
        name="install",
        description="""Install or configure a platform tool for Agent Reach.

Available platforms:
  - "system": Install system deps (gh CLI, Node.js, yt-dlp JS runtime)
  - "reddit": Install rdt-cli or OpenCLI for Reddit
  - "bilibili": Install bili-cli for Bilibili search/hot
  - "opencli": Install OpenCLI (cross-platform browser session backend)
  - "mcporter": Install mcporter + Exa search
  - "all": Install all optional platforms

Also supports configuring API keys:
  - "groq-key": Set Groq API key (for transcription)
  - "openai-key": Set OpenAI API key (for transcription)
  - "github-token": Set GitHub token

Use this when:
- A platform shows as "off" or "warn" in doctor
- You need transcription capability
- You're setting up Agent Reach for the first time

platform: system, reddit, bilibili, opencli, mcporter, all,
         groq-key, openai-key, github-token
value: Optional value for configuration keys (e.g. API key)

Returns: Installation progress and status
""",
    )
    def install(platform: str, value: str = "") -> str:
        platform = platform.lower().strip()

        # Handle API key configuration
        if platform == "groq-key":
            if not value:
                return "Error: groq-key requires a value argument. Get a free key at https://console.groq.com"
            config.set("groq_api_key", value)
            return "Groq API key configured. You can now use transcribe()."

        if platform == "openai-key":
            if not value:
                return "Error: openai-key requires a value argument."
            config.set("openai_api_key", value)
            return "OpenAI API key configured."

        if platform == "github-token":
            if not value:
                return "Error: github-token requires a value argument."
            config.set("github_token", value)
            return "GitHub token configured."

        # System install
        if platform == "system":
            import io

            from agent_reach.cli import _install_system_deps
            old_stdout = sys.stdout
            sys.stdout = buf = io.StringIO()
            try:
                _install_system_deps()
            finally:
                sys.stdout = old_stdout
            return buf.getvalue()

        # Platform installs
        INSTALL_MAP = {
            "reddit": "_install_reddit_deps",
            "bilibili": "_install_bili_deps",
            "opencli": "_install_opencli_deps",
            "mcporter": "_install_mcporter",
        }

        if platform in INSTALL_MAP:
            func_name = INSTALL_MAP[platform]
            mod = sys.modules.get("agent_reach.cli")
            if not mod:
                return f"Error: cannot import installer for {platform}"
            func = getattr(mod, func_name, None)
            if not func:
                return f"Error: installer function {func_name} not found"
            import io
            old_stdout = sys.stdout
            sys.stdout = buf = io.StringIO()
            try:
                func()
            finally:
                sys.stdout = old_stdout
            return buf.getvalue()

        if platform == "all":
            import io
            old_stdout = sys.stdout
            sys.stdout = buf = io.StringIO()
            try:
                for ch_name in ["reddit", "bilibili", "opencli", "mcporter"]:
                    func_name = f"_install_{ch_name}_deps" if ch_name != "mcporter" else "_install_mcporter"
                    func = getattr(sys.modules.get("agent_reach.cli"), func_name, None)
                    if func:
                        func()
            finally:
                sys.stdout = old_stdout
            return buf.getvalue()

        return f"Unknown platform: {platform}. Supported: system, reddit, bilibili, opencli, mcporter, all, groq-key, openai-key, github-token"

    return mcp


def main():
    if not HAS_MCP:
        msg = (
            "MCP not installed.\n"
            "  Install: uv add 'mcp[cli]>=1.5.0'  or  pip install 'mcp[cli]>=1.5.0'\n"
            "  Run: python -m agent_reach.integrations.mcp_server"
        )
        print(msg, file=sys.stderr)
        sys.exit(1)

    transport = os.environ.get("AGENT_REACH_MCP_TRANSPORT", "stdio").strip().lower()
    if transport == "streamable-http":
        host = os.environ.get("AGENT_REACH_MCP_HOST", "127.0.0.1")
        port = int(os.environ.get("AGENT_REACH_MCP_PORT", "18420"))
        mcp = create_server(
            host=host,
            port=port,
            json_response=True,
            stateless_http=True,
        )
        mcp.run(transport="streamable-http")
        return
    if transport != "stdio":
        print("AGENT_REACH_MCP_TRANSPORT must be stdio or streamable-http", file=sys.stderr)
        sys.exit(2)
    mcp = create_server()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
