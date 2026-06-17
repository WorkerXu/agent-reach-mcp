# -*- coding: utf-8 -*-
"""V2EX — API 2.0 (token) -> legacy API -> web scraping fallback."""

import json
import os
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from typing import Any, Optional

from .base import Channel

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
_TIMEOUT = 15


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def _headers(token: Optional[str] = None) -> dict:
    h = {"User-Agent": _UA, "Accept": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _fetch(url: str, token: Optional[str] = None) -> bytes:
    req = urllib.request.Request(url, headers=_headers(token))
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return resp.read()


def _fetch_json(url: str, token: Optional[str] = None) -> Any:
    return json.loads(_fetch(url, token).decode("utf-8"))


def _fetch_page(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = resp.read()
            ct = resp.headers.get("Content-Type", "")
            if "charset=" in ct:
                cs = ct.split("charset=")[-1].split(";")[0].strip()
                return data.decode(cs, errors="replace")
            return data.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return ""
        raise


def _get_token(config=None) -> Optional[str]:
    if config:
        t = config.get("v2ex_token")
        if t:
            return t
    return os.environ.get("V2EX_TOKEN")


# ------------------------------------------------------------------ #
# Minimal HTML scraping (no BeautifulSoup dependency)
# ------------------------------------------------------------------ #

class _TopicParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.topics: list[dict] = []
        self._in_topic = False
        self._in_title = False
        self._in_content = False
        self._in_replies = False
        self._topic: dict = {}
        self._tag_stack: list[str] = []
        self._text_buf: list[str] = []

    def _flush_text(self):
        t = "".join(self._text_buf).strip()
        self._text_buf = []
        if self._in_title and t:
            self._topic["title"] = t
            self._in_title = False
        elif self._in_content and t:
            self._topic.setdefault("content", "")
            self._topic["content"] += t + " "
        elif self._in_replies and t:
            self._topic.setdefault("replies", 0)
            try:
                self._topic["replies"] = int(t)
            except ValueError:
                pass
            self._in_replies = False

    def handle_starttag(self, tag, attrs):
        self._tag_stack.append(tag)
        attrs_d = dict(attrs)
        classes = attrs_d.get("class", "").split()

        if tag == "a" and "topic-link" in classes:
            self._in_topic = True
            self._topic = {"url": attrs_d.get("href", ""), "title": ""}
            if self._topic["url"] and not self._topic["url"].startswith("http"):
                self._topic["url"] = "https://www.v2ex.com" + self._topic["url"]
        if self._in_topic:
            if "topic-link" in classes:
                self._in_title = True
            if tag == "span" and "topic_info" in classes:
                self._in_content = True

        # Parse reply count: <a class="count_livid" ...> reply count </a>
        if tag == "a" and "count_livid" in classes:
            self._in_replies = True

    def handle_data(self, data):
        self._text_buf.append(data)

    def handle_endtag(self, tag):
        self._flush_text()
        if self._tag_stack:
            self._tag_stack.pop()
        if tag == "a" and self._in_topic:
            self._in_topic = False
            self._in_title = False
            self._in_content = False
            if self._topic.get("title"):
                self.topics.append(self._topic)
            self._topic = {}


class _TopicDetailParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.content = ""
        self.author = ""
        self.node_name = ""
        self.node_title = ""
        self.replies: list[dict] = []
        self._in_title = False
        self._in_content = False
        self._in_author = False
        self._in_reply = False
        self._reply: dict = {}
        self._in_reply_author = False
        self._in_reply_content = False
        self._tag_stack: list[str] = []
        self._text_buf: list[str] = []

    def _flush_text(self):
        t = "".join(self._text_buf).strip()
        self._text_buf = []
        if not t:
            return
        if self._in_title:
            self.title = t
            self._in_title = False
        elif self._in_author:
            self.author = t
            self._in_author = False
        elif self._in_content and not self._in_reply:
            self.content += t + " "
        elif self._in_reply_author:
            self._reply["author"] = t
            self._in_reply_author = False
        elif self._in_reply_content:
            self._reply.setdefault("content", "")
            self._reply["content"] += t + "\n"

    def handle_starttag(self, tag, attrs):
        self._tag_stack.append(tag)
        attrs_d = dict(attrs)
        classes = attrs_d.get("class", "").split()

        if tag == "h1":
            self._in_title = True
        if "header" in classes:
            for c in classes:
                if c.startswith("node-"):
                    self.node_name = c[5:]

        if tag == "div" and "topic_content" in classes:
            self._in_content = True
        if tag == "div" and "reply_content" in classes:
            self._in_reply_content = True
        if tag == "strong" and self._in_reply:
            self._in_reply_author = True

        # detect reply start
        if tag == "div" and "reply" in classes and "reply_item" not in classes:
            self._in_reply = True
            self._reply = {"author": "", "content": ""}

    def handle_data(self, data):
        self._text_buf.append(data)

    def handle_endtag(self, tag):
        self._flush_text()
        if self._tag_stack:
            self._tag_stack.pop()
        if tag == "div" and self._in_reply_content:
            if self._reply.get("author"):
                self.replies.append(self._reply)
            self._in_reply = False
            self._in_reply_author = False
            self._in_reply_content = False
            self._reply = {}
        if tag == "div" and self._in_content:
            self._in_content = False


# ------------------------------------------------------------------ #
# Channel
# ------------------------------------------------------------------ #

_API_V2 = "https://www.v2ex.com/api/v2"
_API_LEGACY = "https://www.v2ex.com/api"


class V2EXChannel(Channel):
    name = "v2ex"
    description = "V2EX nodes, topics, and replies"
    backends = ["V2EX API 2.0", "V2EX API (legacy)", "Web scraping"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        from urllib.parse import urlparse
        return "v2ex.com" in urlparse(url).netloc.lower()

    # ------------------------------------------------------------------ #
    # Health check
    # ------------------------------------------------------------------ #

    def check(self, config=None):
        token = _get_token(config)
        # Try API 2.0
        if token:
            try:
                _fetch_json(f"{_API_V2}/member", token)
                self.active_backend = self.backends[0]
                return "ok", "API 2.0 available (Personal Access Token)"
            except Exception:
                pass
        # Try legacy API
        try:
            _fetch_json(f"{_API_LEGACY}/topics/show.json?node_name=python&page=1")
            self.active_backend = self.backends[1]
            return "ok", "Legacy API available"
        except Exception:
            pass
        # Fallback: web scraping — verify it actually works
        try:
            html = _fetch_page("https://www.v2ex.com/?tab=hot")
            if html and "topic-link" in html:
                self.active_backend = self.backends[2]
                return "ok", "Web scraping fallback (scrape HTML when no API available)"
        except Exception:
            pass
        # Everything failed — server IP may be blocked by V2EX
        self.active_backend = None
        return "warn", "V2EX unreachable (server IP blocked or rate-limited). Use search(platform='web') to find V2EX content via web search."

    # ------------------------------------------------------------------ #
    # Routing: try backends in priority order
    # ------------------------------------------------------------------ #

    def _api_json(self, path: str) -> Optional[Any]:
        """Try API 2.0 first, then legacy."""
        token = _get_token()
        if token:
            try:
                return _fetch_json(f"{_API_V2}/{path.lstrip('/')}", token)
            except Exception:
                pass
        return None

    def _legacy_json(self, path: str) -> Optional[Any]:
        try:
            return _fetch_json(f"{_API_LEGACY}/{path.lstrip('/')}")
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    # Data-fetching methods
    # ------------------------------------------------------------------ #

    def get_hot_topics(self, limit: int = 20) -> list:
        data = self._api_json("nodes/python/topics?p=1") or self._legacy_json("topics/hot.json")
        if data:
            results = []
            for item in (data if isinstance(data, list) else data.get("topics", data.get("result", [])))[:limit]:
                node = item.get("node") or {}
                results.append({
                    "id": item.get("id", 0),
                    "title": item.get("title", ""),
                    "url": item.get("url", f"https://www.v2ex.com/t/{item.get('id', '')}"),
                    "replies": item.get("replies", item.get("reply_count", 0)),
                    "node_name": node.get("name", node.get("slug", "")),
                    "node_title": node.get("title", ""),
                    "content": (item.get("content", "") or "")[:200],
                    "created": item.get("created", 0),
                })
            return results
        # Fallback: scrape hot page
        html = _fetch_page("https://www.v2ex.com/?tab=hot")
        if not html:
            return [{"error": "V2EX unreachable (server IP blocked). Try search(platform='web', query='site:v2ex.com TOPIC') to find via Exa."}]
        parser = _TopicParser()
        parser.feed(html)
        return parser.topics[:limit]

    def get_node_topics(self, node_name: str, limit: int = 20) -> list:
        data = self._api_json(f"nodes/{node_name}/topics?p=1")
        if not data:
            data = self._legacy_json(f"topics/show.json?node_name={node_name}&page=1")
        if data:
            results = []
            items = data if isinstance(data, list) else data.get("topics", data.get("result", []))
            for item in items[:limit]:
                node = item.get("node") or {}
                results.append({
                    "id": item.get("id", 0),
                    "title": item.get("title", ""),
                    "url": item.get("url", f"https://www.v2ex.com/t/{item.get('id', '')}"),
                    "replies": item.get("replies", item.get("reply_count", 0)),
                    "node_name": node.get("name", node.get("slug", node_name)),
                    "node_title": node.get("title", ""),
                    "content": (item.get("content", "") or "")[:200],
                    "created": item.get("created", 0),
                })
            return results
        # Fallback: scrape node page
        html = _fetch_page(f"https://www.v2ex.com/go/{node_name}")
        if not html:
            return [{"error": f"Node {node_name} unreachable"}]
        parser = _TopicParser()
        parser.feed(html)
        return parser.topics[:limit]

    def get_topic(self, topic_id: int) -> dict:
        data = self._api_json(f"topics/{topic_id}")
        if not data:
            legacy = self._legacy_json(f"topics/show.json?id={topic_id}")
            if legacy:
                data = legacy[0] if isinstance(legacy, list) else legacy
        if data:
            node = data.get("node") or {}
            member = data.get("member") or {}
            # replies via API
            replies_data = self._api_json(f"topics/{topic_id}/replies")
            if not replies_data:
                try:
                    replies_data = _fetch_json(
                        f"{_API_LEGACY}/replies/show.json?topic_id={topic_id}&page=1"
                    )
                except Exception:
                    replies_data = []
            replies = [
                {
                    "author": (r.get("member") or {}).get("username", r.get("member_username", "")),
                    "content": r.get("content", ""),
                    "created": r.get("created", 0),
                }
                for r in (replies_data if isinstance(replies_data, list) else replies_data.get("replies", replies_data.get("result", [])))
            ]
            return {
                "id": data.get("id", topic_id),
                "title": data.get("title", ""),
                "url": data.get("url", f"https://www.v2ex.com/t/{topic_id}"),
                "content": data.get("content", ""),
                "replies_count": data.get("replies", data.get("reply_count", len(replies))),
                "node_name": node.get("name", node.get("slug", "")),
                "node_title": node.get("title", ""),
                "author": member.get("username", data.get("member_username", "")),
                "created": data.get("created", 0),
                "replies": replies,
            }
        # Fallback: scrape topic page
        html = _fetch_page(f"https://www.v2ex.com/t/{topic_id}")
        if not html:
            return {"error": f"Topic {topic_id} unreachable"}
        parser = _TopicDetailParser()
        parser.feed(html)
        return {
            "id": topic_id,
            "title": parser.title,
            "url": f"https://www.v2ex.com/t/{topic_id}",
            "content": parser.content.strip(),
            "replies_count": len(parser.replies),
            "node_name": parser.node_name,
            "node_title": "",
            "author": parser.author,
            "created": 0,
            "replies": parser.replies,
        }

    def get_user(self, username: str) -> dict:
        data = self._api_json(f"members/{username}") or self._legacy_json(f"members/show.json?username={username}")
        if data and isinstance(data, dict):
            return {
                "id": data.get("id", 0),
                "username": data.get("username", username),
                "url": data.get("url", f"https://www.v2ex.com/member/{username}"),
                "website": data.get("website", ""),
                "twitter": data.get("twitter", ""),
                "psn": data.get("psn", ""),
                "github": data.get("github", ""),
                "btc": data.get("btc", ""),
                "location": data.get("location", ""),
                "bio": data.get("bio", ""),
                "avatar": data.get("avatar_large", data.get("avatar_normal", data.get("avatar", ""))),
                "created": data.get("created", 0),
            }
        return {"error": f"User {username} unreachable"}

    def read(self, url: str) -> str:
        """Read a V2EX page as markdown-formatted text."""
        html = _fetch_page(url)
        if not html:
            return "(V2EX unreachable)"
        # Strip HTML — return plain text
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def search(self, query: str, limit: int = 10) -> list:
        try:
            from urllib.parse import quote
            html = _fetch_page(f"https://www.v2ex.com/?q={quote(query)}")
            if not html:
                return [{"error": "V2EX search unreachable (server IP blocked). Try search(platform='web', query='site:v2ex.com QUERY')."}]
            parser = _TopicParser()
            parser.feed(html)
            return parser.topics[:limit]
        except Exception as e:
            return [{"error": f"V2EX search failed: {e}"}]
