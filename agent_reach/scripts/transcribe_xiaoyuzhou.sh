#!/usr/bin/env bash
# Xiaoyuzhou podcast transcription script
# Usage: bash transcribe.sh [--polish] <xiaoyuzhou-url> [output-file-path]
# Env vars: GROQ_API_KEY (required)
#
# --polish: After transcription, call Groq Llama 3.3 70B to add Chinese
#           punctuation + sensible paragraph breaks
#           (Whisper's Chinese punctuation is weak; enabling this gives
#           much better readability)

set -euo pipefail
export LC_ALL=C

SCRIPT_NAME="${0##*/}"

die() {
    printf '%s: ERROR: %s\n' "$SCRIPT_NAME" "$1" >&2
    exit 1
}

info() {
    printf '%s\n' "$1"
}

POLISH=0
while [ $# -gt 0 ]; do
    case "$1" in
        --polish) POLISH=1; shift ;;
        --) shift; break ;;
        -h|--help)
            printf 'Usage: bash transcribe.sh [--polish] <xiaoyuzhou-url> [output-file-path]\n'
            exit 0 ;;
        --*)
            die "Unknown option: $1"
            ;;
        *) break ;;
    esac
done

if [ $# -lt 1 ]; then
    die "Missing URL argument. Usage: bash transcribe.sh [--polish] <xiaoyuzhou-url> [output-file-path]"
fi
URL="$1"
OUTPUT="${2:-/tmp/podcast_transcript.txt}"
TMPDIR="/tmp/xiaoyuzhou_$$"

# Try env var first, then agent-reach config.yaml
GROQ_API_KEY="${GROQ_API_KEY:-}"
if [ -z "$GROQ_API_KEY" ]; then
    CONFIG_FILE="$HOME/.agent-reach/config.yaml"
    if [ -f "$CONFIG_FILE" ]; then
        GROQ_API_KEY=$(python3 -c "
import yaml
print((yaml.safe_load(open('$CONFIG_FILE')) or {}).get('groq_api_key',''))" 2>/dev/null || printf '')
    fi
fi
if [ -z "$GROQ_API_KEY" ]; then
    die "GROQ_API_KEY not set. Run: agent-reach configure groq-key"
fi

# Groq API limit: 25MB per file
MAX_CHUNK_SIZE_MB=20
AUDIO_BITRATE="64k"

cleanup() {
    rm -rf "$TMPDIR"
}
trap cleanup EXIT

mkdir -p "$TMPDIR"

info "Xiaoyuzhou Podcast Transcriber"
info "=============================="

# Step 1: Extract audio URL and title
info "[1/6] Parsing page..."
PAGE=$(curl -s "$URL") || die "Failed to fetch page: $URL"
AUDIO_URL=$(printf '%s' "$PAGE" | perl -ne 'while (/(https:\/\/media\.xyzcdn\.net\/[^"]*\.(?:m4a|mp3))/gi) { print "$1\n" }' | head -1)
TITLE=$(printf '%s' "$PAGE" | perl -ne 'if (/"title":"([^"]*)"/) { print "$1\n"; last }' | head -1)

if [ -z "$AUDIO_URL" ]; then
    die "Could not extract audio URL from page"
fi

printf '  Title: %s\n' "$TITLE"
printf '  Audio: %s\n' "$AUDIO_URL"

# Step 2: Download audio
info "[2/6] Downloading audio..."
EXT="${AUDIO_URL##*.}"
curl -sL -o "$TMPDIR/original.$EXT" "$AUDIO_URL"
FILE_SIZE=$(ls -lh "$TMPDIR/original.$EXT" | awk '{print $5}')
printf '  File size: %s\n' "$FILE_SIZE"

# Step 3: Get duration
DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$TMPDIR/original.$EXT" 2>/dev/null | cut -d. -f1)
DURATION_MIN=$((DURATION / 60))
DURATION_SEC=$((DURATION % 60))
printf '  Duration: %dm%ds\n' "$DURATION_MIN" "$DURATION_SEC"

# Step 4: Convert to low-bitrate mono MP3
info "[3/6] Converting audio..."
ffmpeg -y -i "$TMPDIR/original.$EXT" -b:a "$AUDIO_BITRATE" -ac 1 "$TMPDIR/mono.mp3" 2>/dev/null
MONO_SIZE=$(stat -c%s "$TMPDIR/mono.mp3" 2>/dev/null || stat -f%z "$TMPDIR/mono.mp3" 2>/dev/null || die "Cannot determine file size")
printf '  After conversion: %dMB\n' "$((MONO_SIZE / 1024 / 1024))"

# Step 5: Split by size
MAX_BYTES=$((MAX_CHUNK_SIZE_MB * 1024 * 1024))

if [ "$MONO_SIZE" -le "$MAX_BYTES" ]; then
    cp "$TMPDIR/mono.mp3" "$TMPDIR/chunk_0.mp3"
    NUM_CHUNKS=1
    info "  No splitting needed"
else
    NUM_CHUNKS=$(( (MONO_SIZE / MAX_BYTES) + 1 ))
    CHUNK_DURATION=$(( DURATION / NUM_CHUNKS + 10 ))
    printf '  Splitting into %d chunks (~%d min each)...\n' "$NUM_CHUNKS" "$((CHUNK_DURATION / 60))"

    for i in $(seq 0 $((NUM_CHUNKS - 1))); do
        START=$((i * CHUNK_DURATION))
        ffmpeg -y -i "$TMPDIR/mono.mp3" -ss "$START" -t "$CHUNK_DURATION" -c copy "$TMPDIR/chunk_${i}.mp3" 2>/dev/null
        CHUNK_SIZE=$(ls -lh "$TMPDIR/chunk_${i}.mp3" | awk '{print $5}')
        printf '    Chunk %d/%d: %s\n' "$((i+1))" "$NUM_CHUNKS" "$CHUNK_SIZE"
    done
fi

# Step 6: Transcribe via Groq Whisper API
info "[4/6] Transcribing (Groq Whisper large-v3)..."

for i in $(seq 0 $((NUM_CHUNKS - 1))); do
    printf '  Chunk %d/%d... ' "$((i+1))" "$NUM_CHUNKS"

    RESPONSE=$(curl -s -w "\n%{http_code}" \
        https://api.groq.com/openai/v1/audio/transcriptions \
        -H "Authorization: Bearer $GROQ_API_KEY" \
        -F file="@$TMPDIR/chunk_${i}.mp3" \
        -F model="whisper-large-v3" \
        -F language="zh" \
        -F prompt="The following is a Mandarin Chinese podcast recording. Please output a transcript with full Chinese punctuation." \
        -F response_format="text") || die "curl failed for chunk $((i+1))"

    HTTP_CODE=$(printf '%s' "$RESPONSE" | tail -1)
    BODY=$(printf '%s' "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" != "200" ]; then
        printf 'ERROR (HTTP %s)\n' "$HTTP_CODE" >&2
        printf '%s\n' "$BODY" >&2

        if [ "$HTTP_CODE" = "429" ]; then
            WAIT_MIN=$(printf '%s' "$BODY" | perl -ne 'if (/in (\d+)m/) { print "$1\n"; exit }')
            WAIT_SEC="${WAIT_MIN:-2}"
            WAIT_SEC=$((WAIT_SEC * 60 + 30))
            printf '  Rate limited, waiting %ds before retry...\n' "$WAIT_SEC" >&2
            sleep "$WAIT_SEC"
            RESPONSE=$(curl -s -w "\n%{http_code}" \
                https://api.groq.com/openai/v1/audio/transcriptions \
                -H "Authorization: Bearer $GROQ_API_KEY" \
                -F file="@$TMPDIR/chunk_${i}.mp3" \
                -F model="whisper-large-v3" \
                -F language="zh" \
                -F prompt="The following is a Mandarin Chinese podcast recording. Please output a transcript with full Chinese punctuation." \
                -F response_format="text") || die "curl failed on retry for chunk $((i+1))"
            HTTP_CODE=$(printf '%s' "$RESPONSE" | tail -1)
            BODY=$(printf '%s' "$RESPONSE" | sed '$d')

            if [ "$HTTP_CODE" != "200" ]; then
                die "Retry failed for chunk $((i+1)) (HTTP $HTTP_CODE)"
            fi
        else
            die "Transcription failed for chunk $((i+1)) (HTTP $HTTP_CODE)"
        fi
    fi

    printf '%s' "$BODY" > "$TMPDIR/transcript_${i}.txt"
    CHARS=$(wc -m < "$TMPDIR/transcript_${i}.txt")
    printf 'OK (%d chars)\n' "$CHARS"
done

# Step 6.5 (optional): Polishing with Llama 3.3 70B
if [ "$POLISH" = "1" ]; then
    info "[5/6] Polishing transcript (Llama 3.3 70B punctuation + paragraph breaks)..."
    for i in $(seq 0 $((NUM_CHUNKS - 1))); do
        printf '  Chunk %d/%d... ' "$((i+1))" "$NUM_CHUNKS"
        IN_FILE="$TMPDIR/transcript_${i}.txt" \
        OUT_FILE="$TMPDIR/polished_${i}.txt" \
        GROQ_API_KEY="$GROQ_API_KEY" \
        python3 <<'PY'
import json, os, sys, urllib.request, urllib.error

KEY = os.environ["GROQ_API_KEY"]
IN = os.environ["IN_FILE"]
OUT = os.environ["OUT_FILE"]

MODEL = "llama-3.3-70b-versatile"
MAX_DEPTH = 3
PROMPT_TMPL = (
    "Below is a Mandarin Chinese podcast transcription segment. Whisper produces "
    "weak Chinese punctuation — the text is almost unpunctuated.\n\n"
    "Your ONLY task: add proper Chinese punctuation （，。！？：；）at appropriate "
    "places, and break into reasonable paragraphs.\n\n"
    "STRICT RULES:\n"
    "- Do NOT change, delete, or add any Chinese/English/digit characters\n"
    "- Do NOT rewrite, polish, or summarize\n"
    "- Do NOT add any explanation, preface, or postscript\n"
    "- Output only the punctuated+paragraphed text\n\n"
    "Original text:\n{}"
)

def call_groq(text):
    body = json.dumps({
        "model": MODEL,
        "temperature": 0.2,
        "max_completion_tokens": 8192,
        "messages": [{"role": "user", "content": PROMPT_TMPL.format(text)}],
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "User-Agent": "agent-reach-xiaoyuzhou/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.load(r)
    return (
        resp["choices"][0]["message"]["content"].strip(),
        resp["choices"][0].get("finish_reason"),
    )

def polish(text, depth=0):
    try:
        out, fr = call_groq(text)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"polish HTTP {e.code}: {e.read().decode(errors='replace')[:200]}\n")
        return text
    except Exception as e:
        sys.stderr.write(f"polish error: {e}\n")
        return text
    if fr != "length" or depth >= MAX_DEPTH:
        return out
    mid = len(text) // 2
    return polish(text[:mid], depth + 1) + polish(text[mid:], depth + 1)

content = open(IN, encoding="utf-8").read().strip()
result = polish(content)
open(OUT, "w", encoding="utf-8").write(result + "\n")
print(f"OK ({len(result)} chars)")
PY
    done
fi

# Step 7: Merge output
info "[6/6] Merging transcript..."

{
    printf '# %s\n' "$TITLE"
    printf '\n'
    printf 'Source: %s\n' "$URL"
    printf 'Duration: %dm%ds\n' "$DURATION_MIN" "$DURATION_SEC"
    printf 'Transcribed: %s\n' "$(date '+%Y-%m-%d %H:%M')"
    if [ "$POLISH" = "1" ]; then
        printf 'Polished: Groq Llama 3.3 70B\n'
    fi
    printf '\n'
    printf '---\n'
    printf '\n'

    for i in $(seq 0 $((NUM_CHUNKS - 1))); do
        if [ "$POLISH" = "1" ] && [ -f "$TMPDIR/polished_${i}.txt" ]; then
            cat "$TMPDIR/polished_${i}.txt"
        else
            cat "$TMPDIR/transcript_${i}.txt"
        fi
        printf '\n'
    done
} > "$OUTPUT"

TOTAL_CHARS=$(wc -m < "$OUTPUT")
printf '\n'
info 'Done!'
printf 'Output: %s\n' "$OUTPUT"
printf 'Total chars: %d\n' "$TOTAL_CHARS"
info "===================="
