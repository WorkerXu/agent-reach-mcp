# Social Media & Communities

XiaoHongShu, Twitter/X, Bilibili, V2EX, Reddit.

## XiaoHongShu (Multi-backend)

XiaoHongShu has three backends. **Run `agent-reach doctor --json` first to see xiaohongshu's `active_backend`**, then use the corresponding command group.

### Backend A: OpenCLI (desktop preferred, reuses browser login session)

```bash
# Search notes
opencli xiaohongshu search "query" -f yaml

# Read note body + interaction data (use full URL from search results, includes xsec_token)
opencli xiaohongshu note "NOTE_URL" -f yaml

# Comments (supports nested replies)
opencli xiaohongshu comments NOTE_ID -f yaml

# Home feed
opencli xiaohongshu feed -f yaml

# User profile public notes
opencli xiaohongshu user USER_ID -f yaml
```

> Requires Chrome to be open with the OpenCLI extension installed. AUTH_REQUIRED error means the browser is not logged into XiaoHongShu — ask the user to log in once in Chrome.

### Backend B: xiaohongshu-mcp (server scenario)

```bash
# When not logged in: check status first, then get QR code for the user to scan
mcporter call 'xiaohongshu.check_login_status()' --timeout 120000
mcporter call 'xiaohongshu.get_login_qrcode()' --timeout 120000

# Search
mcporter call 'xiaohongshu.search_feeds(keyword: "query")' --timeout 120000

# Note details + comments (feed_id and xsec_token from search results)
mcporter call 'xiaohongshu.get_feed_detail(feed_id: "...", xsec_token: "...")' --timeout 120000
```

> First call auto-downloads ~150MB headless browser, always include `--timeout 120000`. search hangs when not logged in, check_login_status first.

### Backend C: xhs-cli (legacy fallback, upstream unmaintained since 2026-03)

```bash
xhs search "query"          # Search
xhs read NOTE_ID_OR_URL     # Read note (must use URL/ID from search results, not bare note_id)
xhs comments NOTE_ID_OR_URL # Comments
xhs hot                     # Hot topics
xhs feed                    # Recommended feed
```

> Known unstable: `xhs user` / `xhs user-posts` / `xhs favorites` may return API errors (upstream abandoned). New users should use Backend A/B.

### General notes

> **xsec_token restriction**: XiaoHongShu enforces xsec_token mechanism — **cannot read with bare note_id**. Correct flow: search/feed to get results, then use the full URL/ID from results. Same for all three backends.
>
> **Rate limiting**: High-frequency requests (batch search, deep comments) trigger captchas, platform limitation cannot be bypassed. Wait 2-3 seconds between operations.
>
> **Write operations (post/comment/like)**: Read-only recommended. xhs-cli v0.6.x write operations may return 406 due to signing issues.

## Twitter/X (twitter-cli)

### Stable commands

```bash
# Home timeline (most stable)
twitter feed -n 20

# Read single tweet (with replies)
twitter tweet URL_OR_ID

# Read long form / X Article
twitter article URL_OR_ID

# User timeline
twitter user-posts @username -n 20

# User profile
twitter user @username
```

### Potentially unstable commands

```bash
# Search tweets (Twitter frequently changes GraphQL endpoint, may return 404)
twitter search "query" -n 10

# Likes (can only see own after 2024, platform limitation)
twitter likes
```

### Retry chain on search failure (execute in order, stop on success)

1. Retry once directly (transient failures are common): `twitter search "query" -n 10`
2. Upgrade and retry: `pipx upgrade twitter-cli && twitter search "query" -n 10`
3. Fallback to OpenCLI (desktop, reuses browser session): `opencli twitter search "query" -f yaml`
4. If all else fails, use stable commands like `twitter feed` / `twitter user-posts @somebody`

### Important notes

> **Installation**: `pipx install twitter-cli` (ensure v0.8.5+)
>
> **Authentication**: Recommended to use Cookie-Editor export then set environment variables `TWITTER_AUTH_TOKEN` + `TWITTER_CT0`. Auto-extraction not available in SSH/Docker/headless environments.
>
> **IP risk**: Do not call frequently from VPS/datacenter IPs, especially followers/following, risk of account suspension. Use residential proxy or local environment.
>
> **OpenCLI fallback**: If OpenCLI is installed on desktop, `opencli twitter search/article/user-posts -f yaml` all work (browser session, no cookie env vars needed).
>
> **Output format**: Use `--yaml` or `--json` for structured output, more AI agent friendly.

## Bilibili

> ⚠️ **Do not use yt-dlp for Bilibili** (anti-bot now blocks with 412, no workaround). Use bili-cli / OpenCLI.

```bash
# Search / Hot / Video detail (bili-cli, read-only no login needed)
bili search "query" --type video -n 5
bili hot -n 10
bili video BVxxx

# Subtitles (OpenCLI, requires desktop Chrome)
opencli bilibili subtitle BVxxx
```

> Detailed commands (audio transcription, direct API fallback) see [references/video.md](video.md).

## V2EX (Public API)

No authentication needed, directly call the public API.

### Hot topics

```bash
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"
```

### Node topics

```bash
# node_name e.g.: python, tech, jobs, qna, programmers
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1" -H "User-Agent: agent-reach/1.0"
```

### Topic details

```bash
# topic_id from URL, e.g. https://www.v2ex.com/t/1234567
curl -s "https://www.v2ex.com/api/topics/show.json?id=TOPIC_ID" -H "User-Agent: agent-reach/1.0"
```

### Topic replies

```bash
curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=TOPIC_ID&page=1" -H "User-Agent: agent-reach/1.0"
```

### User info

```bash
curl -s "https://www.v2ex.com/api/members/show.json?username=USERNAME" -H "User-Agent: agent-reach/1.0"
```

### Python example

```python
from agent_reach.channels.v2ex import V2EXChannel

ch = V2EXChannel()

# Get hot topics
topics = ch.get_hot_topics(limit=10)
for t in topics:
    print(f"[{t['node_title']}] {t['title']} ({t['replies']} replies)")

# Get node topics
node_topics = ch.get_node_topics("python", limit=5)

# Get topic details + replies
topic = ch.get_topic(1234567)
print(topic["title"], "—", topic["author"])

# Get user info
user = ch.get_user("Livid")
```

> **Node list**: https://www.v2ex.com/planes

## Reddit (multi-backend, login required)

**Reddit has no zero-config path**: anonymous `.json` endpoints are blocked (403), official API has stopped approving personal apps since 2025-11. Both backends require login. Run `agent-reach doctor --json` to see reddit's `active_backend`. Access from mainland China requires a proxy.

### Backend A: OpenCLI (desktop preferred, reuses browser login session)

```bash
# Search posts
opencli reddit search "query" -f yaml

# Read post full text + comments
opencli reddit read POST_ID -f yaml

# Browse subreddit / Hot / Popular
opencli reddit subreddit LocalLLaMA -f yaml
opencli reddit hot -f yaml
opencli reddit popular -f yaml

# Subreddit meta info (subscriber count, description)
opencli reddit subreddit-info LocalLLaMA -f yaml
```

> Requires Chrome to be open and logged into reddit.com in the browser.

### Backend B: rdt-cli (legacy/server fallback, upstream unmaintained since 2026-03)

```bash
rdt search "query" --limit 10   # Search posts
rdt read POST_ID                # Read post full text + comments
rdt sub python --limit 20       # Browse subreddit
rdt popular --limit 10          # Browse popular
rdt all --limit 10              # Browse /r/all
```

> **Installation**: `pipx install 'git+https://github.com/public-clis/rdt-cli.git'` (PyPI version is outdated, install from GitHub v0.4.2+). Run `rdt login` before searching and reading (manual cookie setup on server without browser, see doctor prompt).
> Use `--yaml` output for AI agent friendly format.

### Advanced option: Official API + PRAW (existing credential users only)

Users who registered a Reddit script app (have client_id/client_secret) before 2025-11 can use PRAW with the official API (100 QPM free). New applications require manual approval and personal projects are generally rejected — **do not recommend this path to new users**.
