# Video / Podcast

Subtitles and transcripts for YouTube, Bilibili, Xiaoyuzhou Podcast.

## YouTube (yt-dlp)

### Get video metadata

```bash
yt-dlp --dump-json "URL"
```

### Download subtitles

```bash
# Download subtitles (do not download video)
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"

# Then read the .vtt file
cat /tmp/VIDEO_ID.*.vtt
```

### Get comments

```bash
# Extract comments (best-effort, not guaranteed complete)
yt-dlp --write-comments --skip-download --write-info-json \
  --extractor-args "youtube:max_comments=20" \
  -o "/tmp/%(id)s" "URL"
# Comments are in the comments field of .info.json
```

### Search videos

```bash
yt-dlp --dump-json "ytsearch5:query"
```

> **Subtitle note**: Manually uploaded subtitles are reliable; auto-generated subtitles may have line repetition and need post-processing.
> **Comments note**: `--write-comments` is based on web scraping (not YouTube Data API), some comments may be missing.

### No-subtitle fallback: Whisper audio transcription

```bash
# Fallback when video has no subtitles: download audio and transcribe with Whisper (Groq free key is sufficient)
agent-reach transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
agent-reach transcribe ./local_audio.mp3 -o /tmp/transcript.txt
```

> Requires configuring a key first: `agent-reach configure groq-key gsk_xxx` (free, console.groq.com)
> or `agent-reach configure openai-key sk-xxx`. Default auto mode: groq falls back to openai on failure.

## Bilibili (bili-cli primary, OpenCLI for subtitles)

> ⚠️ **Do not use yt-dlp for Bilibili**: Bilibili anti-bot now blocks yt-dlp with 412 (tested with latest version, direct/proxy/with cookies all ineffective). yt-dlp is for YouTube only.

### Video details/search/hot/rankings (bili-cli, read-only no login needed)

```bash
# Video details (title/uploader/duration/play interaction data/subtitle availability)
bili video BVxxx

# Search videos
bili search "query" --type video -n 5

# Hot videos / Rankings
bili hot -n 10
bili rank -n 10

# Download audio and split into ASR-ready WAV (use with agent-reach transcribe when no subtitles)
bili audio BVxxx
```

### Subtitles (OpenCLI, requires desktop Chrome)

```bash
# Subtitles with per-line timestamps
opencli bilibili subtitle BVxxx

# OpenCLI can also search/read video metadata (fallback)
opencli bilibili search "query" -f yaml
opencli bilibili video BVxxx -f yaml
```

### Zero-config fallback: direct search API

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
curl -s -c /tmp/bili_ck.txt -o /dev/null -A "$UA" "https://www.bilibili.com/"
curl -s -b /tmp/bili_ck.txt -A "$UA" -e "https://www.bilibili.com/" \
  "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=QUERY&page=1"
```

> **Install bili-cli**: `pipx install bilibili-cli` (upstream unmaintained since 2026-03 but tested working; read-only mode needs no login, `bili login` with QR scan unlocks personal features like feeds/bookmarks).

## Xiaoyuzhou Podcast

### Transcribe a single episode (optional --polish for better punctuation)

```bash
# Outputs Markdown file to /tmp/. --polish uses Llama 3.3 70B to add punctuation and proper paragraphing
~/.agent-reach/tools/xiaoyuzhou/transcribe.sh --polish "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"
```

> The transcription prompt already requests Chinese punctuation from Whisper; if punctuation quality is still not ideal, add `--polish` to use Groq's free Llama 3.3 70B for punctuation and paragraphing (adds ~7s for a 9-minute podcast). Each transcription costs one extra LLM call, use as needed.

### Prerequisites

1. **ffmpeg**: `brew install ffmpeg`
2. **Groq API Key** (free): https://console.groq.com/keys
3. **Configure Key**: `agent-reach configure groq-key YOUR_KEY`
4. **First run**: `agent-reach install --env=auto` to install tools

### Check status

```bash
agent-reach doctor
```

> Output Markdown files are saved to `/tmp/` by default.

## Selection guide

| Scenario | Recommended tool |
|-----|---------|
| YouTube subtitles | yt-dlp |
| Bilibili video details/search | bili-cli |
| Bilibili subtitles | opencli bilibili subtitle |
| Podcast transcription | Xiaoyuzhou transcribe.sh |
| Audio/video without subtitles | agent-reach transcribe (for Bilibili audio, run `bili audio` first) |
