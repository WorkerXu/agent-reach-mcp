# XiaoHongShu Setup Guide

## Overview
Read and search XiaoHongShu notes. Powered by [xhs-cli](https://github.com/jackwener/xiaohongshu-cli) (⭐1.5K, single-line pipx install).

## Prerequisites
- Python 3.10+ (pipx installed)
- Browser logged into xiaohongshu.com (for Cookie export)

## Steps the agent can complete automatically

### 1. Install xhs-cli
```bash
pipx install xiaohongshu-cli
```

### 2. Login (extract Cookie from browser)
```bash
xhs login
```

> This automatically extracts cookies from the browser. If auto-extraction fails, manual import is possible (see below).

### 3. Verify
```bash
agent-reach doctor
```

Should show XiaoHongShu as ✅.

## Steps requiring user action

If `xhs login` auto-extraction fails, manually import cookies:

> **Recommended method: Cookie-Editor browser export (most reliable)**
>
> 1. Install [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) extension in Chrome
> 2. Log into xiaohongshu.com in the browser
> 3. Click Cookie-Editor icon → Export → Header String
> 4. Send the exported string to the agent, run: `agent-reach configure xhs-cookies "exported_cookie_string"`
>
> **Note**: Do not rely on QR code login; Cookie-Editor export is the simplest and most reliable method.

## Usage examples

Search notes:
```bash
xhs search "keyword"
```

Read note details:
```bash
xhs read NOTE_ID
```

View comments:
```bash
xhs comments NOTE_ID
```

## FAQ

**Q: Cookie expired?**
A: Re-run `xhs login` or re-export via Cookie-Editor.

**Q: XiaoHongShu showing IP risk warning?**
A: Use a residential proxy: `export HTTP_PROXY="http://user:pass@ip:port"`.

**Q: xhs-cli doesn't support my system?**
A: Ensure Python 3.10+ and pipx are installed. Run `pipx install xiaohongshu-cli`.

## Alternative: Docker MCP

If you are already using the [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) Docker setup, it also works:

```bash
docker run -d \
  --name xiaohongshu-mcp \
  -p 18060:18060 \
  xpzouying/xiaohongshu-mcp

mcporter config add xiaohongshu http://localhost:18060/mcp
```

xhs-cli is the current recommended solution — no Docker needed, simpler installation.
