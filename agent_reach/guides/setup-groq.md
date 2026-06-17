# Groq Whisper Setup Guide

## Overview
When YouTube/Bilibili videos don't have subtitles, use Groq's Whisper API for speech-to-text. Groq provides free credits.

## Steps the agent can complete automatically

1. Check if already configured:
```bash
agent-reach doctor | grep -i "groq\|whisper"
```

2. If the user provides a key, write the config:
```python
from agent_reach.config import Config
c = Config()
c.set("groq_api_key", "KEY_PROVIDED_BY_USER")
```

3. Test (optional):
```bash
curl -s https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer KEY_PROVIDED_BY_USER" \
  -o /dev/null -w "%{http_code}"
```
Returns 200 = ready

## Steps requiring user action

Tell the user:

> Video speech-to-text requires a Groq API Key (free).
>
> Steps:
> 1. Open https://console.groq.com
> 2. Sign up with Google account or email
> 3. Click "API Keys" on the left
> 4. Click "Create API Key"
> 5. Copy the generated key and send it to me
>
> Groq provides free credits that are sufficient for daily use.

## After the agent receives the key

1. Write config: `config.set("groq_api_key", key)`
2. Test API availability
3. Respond: "✅ Speech-to-text is now enabled! When I encounter videos without subtitles, I can extract the content for you."
