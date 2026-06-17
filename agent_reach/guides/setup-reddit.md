# Reddit Setup Guide

## Overview

Reddit blocks almost all non-browser direct access (including datacenter and ISP proxy IPs), JSON API returns 403.

Agent Reach provides Reddit search and reading via **rdt-cli**:
- **Search**: `rdt search "keyword"`
- **Read full posts + comments**: `rdt read POST_ID`

Free, no proxy needed, no API Key required. Needs login authentication (`rdt login`, auto-extracts Cookie from browser).

## Steps the agent can complete automatically

1. Check if rdt-cli is available:
```bash
which rdt && echo "installed" || echo "not installed"
```

2. If not installed, auto-install (PyPI version is outdated, install the latest from GitHub):
```bash
pipx install 'git+https://github.com/public-clis/rdt-cli.git'
```

Or one-click install:
```bash
agent-reach install --env=auto --channels=reddit
```

## Usage examples

Search Reddit content:
```bash
rdt search "python best practices" -n 5
```

Read full posts and comments:
```bash
rdt read POST_ID
```

## Steps requiring user action

None. rdt-cli is automatically installed via `agent-reach install --env=auto`.

## Fallback: Exa search

If you already have Exa configured (via mcporter), you can also search Reddit content through Exa:

```bash
mcporter call 'exa.web_search_exa(query: "python best practices", numResults: 5, includeDomains: ["reddit.com"])'
```

rdt-cli is the current recommended solution, usable with no additional configuration.
