# -*- coding: utf-8 -*-
"""RSS — read and search RSS/Atom feeds via feedparser.

Usage:
    ch = RSSChannel()
    markdown = ch.read("https://hnrss.org/frontpage", limit=5)
    results = ch.search("python")  # returns guidance note, RSS has no search
"""

from html import unescape
from io import BytesIO
from urllib.parse import urlparse

from .base import Channel

_USER_AGENT = "agent-reach/1.5 +https://github.com/Panniantong/Agent-Reach"
_REQUEST_TIMEOUT = 15


class RSSChannel(Channel):
    name = "rss"
    description = "RSS/Atom feeds"
    backends = ["feedparser"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        return any(x in url.lower() for x in ["/feed", "/rss", ".xml", "atom"])

    def check(self, config=None):
        try:
            import feedparser  # noqa: F401
        except ImportError:
            self.active_backend = None
            return "off", "feedparser not installed. Install: pip install feedparser"
        except Exception as e:
            self.active_backend = None
            return "error", f"feedparser import failed: {e}\nFix: pip install --force-reinstall feedparser"
        self.active_backend = self.backends[0]
        return "ok", "Can read RSS/Atom feeds"

    def read(self, url: str, limit: int = 20) -> str:
        """Fetch and parse an RSS/Atom feed, return entries as markdown text.

        Uses requests for HTTP (timeout, custom UA), feedparser for parsing.
        Validates URL first, handles network errors and malformed XML gracefully.
        """
        import feedparser
        import requests

        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return f"(Invalid URL: {url} — must include scheme and hostname)"

        try:
            resp = requests.get(
                url,
                headers={"User-Agent": _USER_AGENT},
                timeout=_REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
        except requests.exceptions.Timeout:
            return f"(Timeout reading RSS feed: {url})"
        except requests.exceptions.ConnectionError as exc:
            return f"(Connection error for RSS feed {url}: {exc})"
        except requests.exceptions.HTTPError as exc:
            return f"(HTTP {exc.response.status_code} for RSS feed: {url})"
        except requests.exceptions.RequestException as exc:
            return f"(Failed to fetch RSS feed {url}: {exc})"

        feed = feedparser.parse(
            BytesIO(resp.content),
            agent=_USER_AGENT,
        )

        if feed.bozo and not feed.entries:
            reason = getattr(feed, "bozo_exception", "unknown parse error")
            return f"(RSS parse error: {reason})"

        lines = []
        feed_title = feed.feed.get("title", url)
        feed_subtitle = feed.feed.get("subtitle", "")
        lines.append(f"# {feed_title}")
        if feed_subtitle:
            lines.append(f"> {feed_subtitle}")
        lines.append("")

        for entry in feed.entries[:limit]:
            entry_title = unescape(entry.get("title", "Untitled"))
            entry_link = entry.get("link", "")
            published = entry.get("published", entry.get("updated", ""))
            author = ""
            if "author" in entry:
                author = f" by {entry.author}"

            raw_summary = unescape(entry.get("summary", ""))
            clean_summary = _strip_html(raw_summary).strip()

            lines.append(f"## [{entry_title}]({entry_link})")
            if published:
                lines.append(f"_{published}_{author}")
            if clean_summary:
                lines.append("")
                lines.append(clean_summary[:500])  # cap summary length
            lines.append("")

        if len(lines) <= 3:
            return "(No entries found in feed)"

        return "\n".join(lines)

    def search(self, query: str, limit: int = 10) -> list:
        """RSS is a pull protocol — no native search.

        Returns a guidance message directing the agent to use the web channel
        or read known feeds directly.
        """
        return [{
            "note": "RSS feeds do not support search. "
                    "Try reading known feeds with read(url) or "
                    "use the web channel for web search.",
            "query": query,
        }]


def _strip_html(text: str) -> str:
    """Remove HTML tags from text, replacing block-level tags with newlines."""
    import re
    text = re.sub(r"(?i)</?(?:p|br|div|tr|li|h[1-6])[^>]*>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
