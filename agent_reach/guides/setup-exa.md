# Exa Search Setup Guide

## Overview
Exa is an AI semantic search engine. Accessed via MCP, **free, no API Key required**. After setup, unlocks:
- Web-wide semantic search
- Reddit search (via site:reddit.com)
- Twitter search (via site:x.com)

## Steps the agent can complete automatically

`agent-reach install --env=auto` handles the following steps automatically, usually no manual intervention needed.

### 1. Install mcporter
```bash
npm install -g mcporter
```

### 2. Register Exa MCP
```bash
mcporter config add exa https://mcp.exa.ai/mcp
```

### 3. Verify
```bash
agent-reach doctor | grep "Search"
mcporter call 'exa.web_search_exa(query: "test", numResults: 1)'
```

## Steps requiring user action

**None.** Exa is accessed via MCP, free, no registration or API Key needed.

If `agent-reach install` didn't auto-configure Exa due to network issues, manually run the two commands above.

## FAQ

**Q: Are there search rate limits?**
A: The MCP endpoint is provided by Exa (mcp.exa.ai), currently free and unlimited. If this changes in the future, agent-reach updates will adapt.

**Q: What is mcporter?**
A: A CLI bridge tool for the MCP protocol, used to call MCP Servers. Agent Reach uses it to connect to Exa and XiaoHongShu.
