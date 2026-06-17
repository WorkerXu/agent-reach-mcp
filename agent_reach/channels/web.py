# -*- coding: utf-8 -*-
"""Web — any URL via Jina Reader (primary) or direct HTTP (fallback)."""

import urllib.request
import urllib.error
from .base import Channel

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
_TIMEOUT = 30


class WebChannel(Channel):
    name = "web"
    description = "Any web page"
    backends = ["Jina Reader", "Direct HTTP"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        return True  # Fallback — handles any URL

    def check(self, config=None):
        # Try Jina first; fall back to direct HTTP
        try:
            test_url = "https://r.jina.ai/https://example.com"
            req = urllib.request.Request(
                test_url,
                headers={"User-Agent": _UA, "Accept": "text/plain"},
            )
            with urllib.request.urlopen(req, timeout=5):
                self.active_backend = self.backends[0]
                return "ok", "Read any web page via Jina Reader (curl https://r.jina.ai/URL)"
        except (urllib.error.HTTPError, urllib.error.URLError, OSError):
            self.active_backend = self.backends[1]
            return "ok", "Direct HTTP (Jina Reader unavailable, falling back to direct HTTP request)"

    def read(self, url: str) -> str:
        """Read web page. Prefer Jina Reader, fallback to direct HTTP on failure."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            return self._read_jina(url)
        except (urllib.error.HTTPError, urllib.error.URLError):
            self.active_backend = self.backends[1]
            return self._read_direct(url)

    def _read_jina(self, url: str) -> str:
        jina_url = f"https://r.jina.ai/{url}"
        req = urllib.request.Request(
            jina_url,
            headers={"User-Agent": _UA, "Accept": "text/plain"},
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return resp.read().decode("utf-8")

    def _read_direct(self, url: str) -> str:
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()
            if "charset=" in content_type:
                charset = content_type.split("charset=")[-1].split(";")[0].strip()
                return data.decode(charset, errors="replace")
            return data.decode("utf-8", errors="replace")
