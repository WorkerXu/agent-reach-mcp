<h1 align="center">📡 Agent Reach — MCP Fork</h1>

<p align="center">
  <strong>13 Internet Platforms as MCP Tools for Your AI Agent</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-green.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://github.com/Panniantong/Agent-Reach"><img src="https://img.shields.io/badge/Forked%20From-Panniantong%2FAgent--Reach-blue?style=for-the-badge" alt="Forked From"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> · <a href="#mcp-server">MCP Server</a> · <a href="#origin">Origin</a> · <a href="#whats-different">What's Different</a> · <a href="#supported-platforms">Platforms</a>
</p>

---

## Origin

This is a **fork** of [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) (v1.5.0), an excellent project that gives AI agents read/search access to 13+ internet platforms.

The original project focuses on CLI + skill-based access for coding agents. This fork adds a **production-grade MCP (Model Context Protocol) server** as a first-class interface, making all 13 platforms available as MCP tools that any MCP-compatible host (Claude Desktop, Cursor, Windsurf, etc.) can call directly.

## What's Different

| Area | Original (Panniantong) | This Fork |
|------|----------------------|-----------|
| **Primary interface** | CLI (`agent-reach read/search/doctor`) | MCP server (8 tools) + CLI |
| **MCP server** | Basic proof-of-concept | Production-grade, 8 tools, 70+ tests |
| **Web search** | DuckDuckGo via Jina Reader (403 on servers) | Exa via mcporter (works from any IP) |
| **Stock quotes** | Xueqiu-only (needs browser cookies) | yfinance → Yahoo Finance v8 fallback (no auth needed) |
| **Subprocess calls** | 16 ad-hoc blocks | Single `_run_cli()` helper (consistent error handling) |
| **Tool descriptions** | Minimal | Verb-first, return format, negative instructions (per MCP best practices) |
| **Testing** | Subprocess-based | 70 in-memory FastMCP tests (deterministic, fast) |
| **V2EX doctor** | Always reported "ok" | Honest probing, returns "warn" when blocked |
| **Error messages** | Generic | Actionable: suggests alternatives when a platform is blocked |

All upstream credit to [@Neo_Reidlab](https://x.com/Neo_Reidlab) and the Panniantong team for building the channel architecture and CLI tooling.

---

## Why Agent Reach?

AI agents can already write code, edit documents, and manage projects — but ask them to find something online, and they're lost:

- 📺 "Check what this YouTube tutorial says" → **Can't**, can't get captions
- 🐦 "Search what people are saying about this product on Twitter" → **Can't**, Twitter API requires payment
- 📖 "Go check Reddit if anyone had the same bug" → **403 blocked**, server IP rejected
- 📕 "Check this product's reviews on XiaoHongShu" → **Can't open**, must log in to view
- 🔍 "Search online for the latest LLM framework comparison" → **No good search tool**, either paid or low quality
- 🌐 "Check what this webpage says" → **Gets back a mess of HTML tags**, unreadable
- 📡 "Subscribe to these RSS feeds" → Need to install libraries and write code

**Agent Reach turns this into one sentence:** give your Agent the install URL, and minutes later it can read Twitter, search Reddit, watch YouTube, and browse XiaoHongShu.

---

## Supported Platforms

| Platform | Available Via | Auth Needed |
|----------|-------------|-------------|
| 🌐 **Web** | Jina Reader / Direct HTTP | No |
| 📺 **YouTube** | yt-dlp caption extraction | No |
| 📡 **RSS** | feedparser | No |
| 🔍 **Web Search** | Exa via mcporter | No (free tier) |
| 📦 **GitHub** | gh CLI | Optional (for private repos) |
| 🐦 **Twitter/X** | twitter-cli | Cookies |
| 📺 **Bilibili** | bili-cli | No |
| 📖 **Reddit** | OpenCLI / rdt-cli | Cookies |
| 📕 **XiaoHongShu** | xhs-cli / OpenCLI | Cookies |
| 💼 **LinkedIn** | linkedin-scraper-mcp / Jina Reader | Optional |
| 💻 **V2EX** | Web scraping (API often blocked on servers) | No |
| 📈 **Xueqiu** | yfinance (US stocks) / Xueqiu API (Chinese stocks) | Cookies for Chinese stocks |
| 🎙️ **Xiaoyuzhou** | RSS + Whisper | Groq API key |

---

## MCP Server

This is the main feature of this fork. Run the MCP server and your AI host gets 8 tools:

```
agent-reach-mcp
```

### 8 MCP Tools

| Tool | What It Does | Best For |
|------|-------------|----------|
| **doctor** | Check all 13 platforms' status | Diagnosing setup issues |
| **read_url** | Read any web page as clean text | Articles, docs, RSS feeds |
| **search** | Search by keyword across platforms | Finding content by topic |
| **trending** | Hot/trending content | What's popular right now |
| **stock_quote** | Real-time stock prices | AAPL, TSLA, etc. (US stocks work without setup) |
| **get_details** | Deep-dive by ID | V2EX topics, Bilibili videos, GitHub repos |
| **transcribe** | YouTube audio → text transcript | Video summaries |
| **install** | Configure a platform or API key | Setting up auth |

### Register with Claude Desktop

Add to your `claude.json`:

```json
{
  "mcpServers": {
    "agent-reach": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/agent-reach-mcp",
        "python", "-m", "agent_reach.integrations.mcp_server"
      ]
    }
  }
}
```

### Register with OpenCode

Add to your `opencode.json`:

```json
{
  "mcpServers": {
    "agent-reach": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/agent-reach-mcp",
        "python", "-m", "agent_reach.integrations.mcp_server"
      ]
    }
  }
}
```

---

## Quick Start

```bash
# Clone
git clone https://github.com/M0-AR/agent-reach-mcp.git
cd agent-reach-mcp

# Install
pip install -e .

# Check status
agent-reach doctor

# Run MCP server (for AI hosts)
agent-reach-mcp
```

---

## Design Philosophy

This project is a **capability layer**, not a wrapper. It sits one level above any concrete implementation — responsible for **selection, installation, diagnostics, and routing**, not for the underlying reading itself. Reading is done by the AI agent calling upstream tools directly.

### Multi-Backend Routing

Each platform has an ordered list of backends:

```
channels/
├── web.py          → Jina Reader ▸ Direct HTTP
├── twitter.py      → twitter-cli ▸ OpenCLI ▸ bird
├── youtube.py      → yt-dlp
├── bilibili.py     → bili-cli ▸ OpenCLI
├── xueqiu.py       → Xueqiu API ▸ yfinance ▸ Yahoo Finance v8
├── v2ex.py         → API 2.0 ▸ Legacy API ▸ Web scraping
├── rss.py          → feedparser
├── exa_search.py   → Exa via mcporter
└── ...
```

When one backend fails, the next is tried. `agent-reach doctor` shows which backend is active for each platform.

---

## Testing

```bash
# All tests
pytest tests/ -v

# MCP server tests only
pytest tests/test_mcp_server.py -v

# With coverage
pip install pytest-cov
pytest tests/ --cov=agent_reach
```

---

## Contributing

PRs are welcome. This is a fork focused on making the MCP server production-ready.

- Found a bug? Open an [Issue](https://github.com/M0-AR/agent-reach-mcp/issues)
- Want a new channel? Fork the original [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) and contribute there, then we can merge upstream changes here

### Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check .
```

---

## License

MIT — see [LICENSE](LICENSE).

Original work Copyright (c) 2025 Agent Eyes (Panniantong/Agent-Reach).
Fork modifications Copyright (c) 2026 M0-AR.
