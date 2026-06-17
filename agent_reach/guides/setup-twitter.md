# Twitter Advanced Features Setup Guide (twitter-cli)

Twitter basic reading is available for free via Jina Reader, no configuration needed.

Advanced features require twitter-cli (@public-clis/twitter-cli):

- Search tweets (`twitter search`)
- Read full tweets and conversation threads (`twitter tweet`, `twitter thread`)
- User timeline (`twitter timeline`)
- Read long-form content (`twitter article`)

twitter-cli is a free open-source tool (pipx install), but requires your Twitter account cookie.

## Quick setup

1. Check if twitter-cli is installed:

```bash
which twitter && echo "installed" || echo "not installed"
```

2. Install twitter-cli:

```bash
pipx install twitter-cli
```

3. Test if configured:

```bash
twitter search "test" -n 1
```

## Get Cookie (Cookie-Editor method, recommended)

1. Install [Cookie-Editor](https://cookie-editor.com/) browser extension
2. Log into x.com
3. Click Cookie-Editor icon → Export → Copy all
4. Run the configuration command:

```bash
agent-reach configure twitter-cookies "pasted cookie JSON"
```

This automatically extracts `auth_token` and `ct0` and writes them to environment variables.

## Manual Cookie setup

If you already know your `auth_token` and `ct0`:

1. Install twitter-cli (if not installed): `pipx install twitter-cli`

2. Set environment variables:

```bash
export AUTH_TOKEN="your_auth_token"
export CT0="your_ct0"
```

3. Test:

```bash
twitter search "test" -n 1
```

## Proxy configuration

> twitter-cli supports proxy via environment variables:

```bash
export HTTP_PROXY="http://user:pass@host:port"
export HTTPS_PROXY="http://user:pass@host:port"
twitter search "test" -n 1
```

You can also use a global proxy tool:

```bash
proxychains twitter search "test" -n 1
```

## Fallback: bird CLI

If you already have [bird CLI](https://www.npmjs.com/package/@steipete/bird) installed (`npm install -g @steipete/bird`), it also works. Agent Reach will auto-detect and use any installed bird. Both have similar functionality; twitter-cli is the current recommended solution.
