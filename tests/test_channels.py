# -*- coding: utf-8 -*-
"""Tests for channel registry basics and health checks."""

import json
import shutil
import subprocess
from urllib.error import URLError

from agent_reach.channels import get_all_channels, get_channel
from agent_reach.channels.v2ex import V2EXChannel
from agent_reach.channels.xiaohongshu import XiaoHongShuChannel
from agent_reach.channels.xueqiu import XueqiuChannel


class TestChannelRegistry:
    def test_get_channel_by_name(self):
        ch = get_channel("github")
        assert ch is not None
        assert ch.name == "github"

    def test_get_unknown_channel_returns_none(self):
        assert get_channel("not-exists") is None

    def test_all_channels_registered(self):
        channels = get_all_channels()
        names = [ch.name for ch in channels]
        assert "web" in names
        assert "github" in names
        assert "twitter" in names
        assert "v2ex" in names


class TestV2EXChannel:
    def test_can_handle_v2ex_urls(self):
        ch = V2EXChannel()
        assert ch.can_handle("https://www.v2ex.com/t/1234567")
        assert ch.can_handle("https://v2ex.com/go/python")
        assert not ch.can_handle("https://github.com/user/repo")
        assert not ch.can_handle("https://reddit.com/r/Python")

    def test_check_ok_when_api_reachable(self, monkeypatch):
        import urllib.request

        class FakeResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def read(self):
                return b"[]"

        monkeypatch.setattr(
            urllib.request,
            "urlopen",
            lambda req, timeout=None: FakeResponse(),
        )
        status, msg = V2EXChannel().check()
        assert status == "ok"

    def test_check_warn_when_api_unreachable(self, monkeypatch):
        import urllib.request

        def raise_error(req, timeout=None):
            raise URLError("connection refused")

        monkeypatch.setattr(urllib.request, "urlopen", raise_error)
        status, msg = V2EXChannel().check()
        assert status == "warn"
        assert "unreachable" in msg

    # ------------------------------------------------------------------ #
    # get_hot_topics
    # ------------------------------------------------------------------ #

    def test_get_hot_topics_returns_list(self, monkeypatch):
        import urllib.request

        fake_data = [
            {
                "id": 111,
                "title": "Python 3.13 released",
                "url": "https://www.v2ex.com/t/111",
                "replies": 42,
                "content": "Release announcement content",
                "created": 1700000000,
                "node": {"name": "python", "title": "Python"},
            },
            {
                "id": 222,
                "title": "Is Rust easy to learn?",
                "url": "https://www.v2ex.com/t/222",
                "replies": 10,
                "content": "",
                "created": 1700000001,
                "node": {"name": "rust", "title": "Rust"},
            },
        ]

        class FakeResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

            def read(self):
                return json.dumps(fake_data).encode()

        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResponse())
        topics = V2EXChannel().get_hot_topics(limit=5)
        assert len(topics) == 2
        assert topics[0]["id"] == 111
        assert topics[0]["title"] == "Python 3.13 released"
        assert topics[0]["replies"] == 42
        assert topics[0]["node_name"] == "python"
        assert topics[0]["node_title"] == "Python"
        assert topics[0]["created"] == 1700000000

    def test_get_hot_topics_respects_limit(self, monkeypatch):
        import urllib.request

        fake_data = [
            {"id": i, "title": f"Topic {i}", "url": f"https://v2ex.com/t/{i}", "replies": i,
             "content": "", "created": 1700000000 + i, "node": {"name": "tech", "title": "Tech"}}
            for i in range(10)
        ]

        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self): return json.dumps(fake_data).encode()

        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResponse())
        topics = V2EXChannel().get_hot_topics(limit=3)
        assert len(topics) == 3

    def test_get_hot_topics_truncates_content(self, monkeypatch):
        import urllib.request

        long_content = "A" * 300
        fake_data = [
            {"id": 1, "title": "Long post", "url": "https://v2ex.com/t/1", "replies": 0,
             "content": long_content, "created": 1700000000, "node": {"name": "tech", "title": "Tech"}}
        ]

        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self): return json.dumps(fake_data).encode()

        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResponse())
        topics = V2EXChannel().get_hot_topics(limit=1)
        assert len(topics[0]["content"]) == 200

    # ------------------------------------------------------------------ #
    # get_node_topics
    # ------------------------------------------------------------------ #

    def test_get_node_topics(self, monkeypatch):
        import urllib.request

        fake_data = [
            {
                "id": 333,
                "title": "Flask deployment issues",
                "url": "https://www.v2ex.com/t/333",
                "replies": 5,
                "content": "Help needed",
                "created": 1710000000,
                "node": {"name": "python", "title": "Python"},
            }
        ]

        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self): return json.dumps(fake_data).encode()

        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResponse())
        topics = V2EXChannel().get_node_topics("python")
        assert len(topics) == 1
        assert topics[0]["id"] == 333
        assert topics[0]["node_name"] == "python"
        assert topics[0]["title"] == "Flask deployment issues"
        assert topics[0]["created"] == 1710000000

    # ------------------------------------------------------------------ #
    # get_topic
    # ------------------------------------------------------------------ #

    def test_get_topic_returns_detail_and_replies(self, monkeypatch):
        import urllib.request

        topic_data = [
            {
                "id": 999,
                "title": "Test post",
                "url": "https://www.v2ex.com/t/999",
                "content": "Post body",
                "replies": 2,
                "node": {"name": "qna", "title": "Q&A"},
                "member": {"username": "alice"},
                "created": 1700000000,
            }
        ]
        replies_data = [
            {
                "member": {"username": "bob"},
                "content": "First reply",
                "created": 1700000100,
            },
            {
                "member": {"username": "carol"},
                "content": "Second reply",
                "created": 1700000200,
            },
        ]

        class FakeResponse:
            def __init__(self, payload):
                self._payload = payload

            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self): return json.dumps(self._payload).encode()

        def fake_urlopen(req, timeout=None):
            url = req.full_url
            if "replies" in url:
                return FakeResponse(replies_data)
            return FakeResponse(topic_data)

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        result = V2EXChannel().get_topic(999)

        assert result["id"] == 999
        assert result["title"] == "Test post"
        assert result["author"] == "alice"
        assert result["node_name"] == "qna"
        assert len(result["replies"]) == 2
        assert result["replies"][0]["author"] == "bob"
        assert result["replies"][1]["content"] == "Second reply"

    def test_get_topic_handles_empty_replies(self, monkeypatch):
        import urllib.request

        topic_data = [
            {
                "id": 1,
                "title": "Lonely post",
                "url": "https://www.v2ex.com/t/1",
                "content": "",
                "replies": 0,
                "node": {"name": "offtopic", "title": "Off-topic"},
                "member": {"username": "dave"},
                "created": 0,
            }
        ]

        class FakeResponse:
            def __init__(self, payload): self._payload = payload
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self): return json.dumps(self._payload).encode()

        def fake_urlopen(req, timeout=None):
            if "replies" in req.full_url:
                return FakeResponse([])
            return FakeResponse(topic_data)

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        result = V2EXChannel().get_topic(1)
        assert result["replies"] == []

    # ------------------------------------------------------------------ #
    # get_user
    # ------------------------------------------------------------------ #

    def test_get_user_returns_profile(self, monkeypatch):
        import urllib.request

        fake_user = {
            "id": 42,
            "username": "alice",
            "url": "https://www.v2ex.com/member/alice",
            "website": "https://alice.dev",
            "twitter": "alice_tw",
            "psn": "",
            "github": "alice",
            "btc": "",
            "location": "Shanghai",
            "bio": "Python dev",
            "avatar_large": "https://cdn.v2ex.com/avatars/alice_large.png",
            "created": 1500000000,
        }

        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self): return json.dumps(fake_user).encode()

        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResponse())
        user = V2EXChannel().get_user("alice")

        assert user["id"] == 42
        assert user["username"] == "alice"
        assert user["github"] == "alice"
        assert user["location"] == "Shanghai"
        assert "alice_large.png" in user["avatar"]

    # ------------------------------------------------------------------ #
    # search
    # ------------------------------------------------------------------ #

    def test_search_returns_unavailable_notice(self):
        result = V2EXChannel().search("python asyncio")
        assert len(result) >= 1
        if "error" in result[0]:
            assert "V2EX" in result[0]["error"]


class TestXueqiuChannel:
    def test_can_handle_xueqiu_urls(self):
        ch = XueqiuChannel()
        assert ch.can_handle("https://xueqiu.com/S/SH600519")
        assert ch.can_handle("https://stock.xueqiu.com/v5/stock/batch/quote.json")
        assert ch.can_handle("https://www.xueqiu.com/1234567890/12345")
        assert not ch.can_handle("https://github.com/user/repo")
        assert not ch.can_handle("https://v2ex.com/t/123")

    def test_check_ok_when_api_reachable(self, monkeypatch):
        import agent_reach.channels.xueqiu as xueqiu_mod

        monkeypatch.setattr(xueqiu_mod, "_cookies_initialized", True)

        fake_response_data = {
            "data": {
                "items": [
                    {"quote": {"symbol": "SH000001", "name": "Shanghai Composite Index", "current": 3200.0}}
                ]
            }
        }

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

            def read(self):
                return json.dumps(fake_response_data).encode()

        monkeypatch.setattr(xueqiu_mod._opener, "open", lambda req, timeout=None: FakeResponse())
        status, msg = XueqiuChannel().check()
        assert status == "ok"
        assert "Public API available" in msg

    def test_check_warn_when_api_unreachable(self, monkeypatch):
        import agent_reach.channels.xueqiu as xueqiu_mod

        monkeypatch.setattr(xueqiu_mod, "_cookies_initialized", True)

        def raise_error(req, timeout=None):
            raise URLError("connection refused")

        monkeypatch.setattr(xueqiu_mod._opener, "open", raise_error)
        status, msg = XueqiuChannel().check()
        assert status == "warn"
        assert "failed" in msg

    # ------------------------------------------------------------------ #
    # get_stock_quote
    # ------------------------------------------------------------------ #

    def test_get_stock_quote(self, monkeypatch):
        import agent_reach.channels.xueqiu as xueqiu_mod

        monkeypatch.setattr(xueqiu_mod, "_cookies_initialized", True)

        fake_data = {
            "data": {
                "items": [
                    {
                        "quote": {
                            "symbol": "SH600519",
                            "name": "Kweichow Moutai",
                            "current": 1800.0,
                            "percent": 1.5,
                            "chg": 26.6,
                            "high": 1810.0,
                            "low": 1770.0,
                            "open": 1775.0,
                            "last_close": 1773.4,
                            "volume": 12345678,
                            "amount": 22000000000,
                            "market_capital": 2260000000000,
                            "turnover_rate": 0.098,
                            "pe_ttm": 30.5,
                            "timestamp": 1700000000000,
                        }
                    }
                ]
            }
        }

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

            def read(self):
                return json.dumps(fake_data).encode()

        monkeypatch.setattr(xueqiu_mod._opener, "open", lambda req, timeout=None: FakeResponse())
        quote = XueqiuChannel().get_stock_quote("SH600519")
        assert quote["symbol"] == "SH600519"
        assert quote["name"] == "Kweichow Moutai"
        assert quote["current"] == 1800.0
        assert quote["percent"] == 1.5
        assert quote["volume"] == 12345678

    # ------------------------------------------------------------------ #
    # search_stock
    # ------------------------------------------------------------------ #

    def test_search_stock(self, monkeypatch):
        import agent_reach.channels.xueqiu as xueqiu_mod

        monkeypatch.setattr(xueqiu_mod, "_cookies_initialized", True)

        fake_data = {
            "stocks": [
                {"code": "SH600519", "name": "Kweichow Moutai", "exchange": "SHA"},
                {"code": "SZ000858", "name": "Wuliangye", "exchange": "SZA"},
            ]
        }

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

            def read(self):
                return json.dumps(fake_data).encode()

        monkeypatch.setattr(xueqiu_mod._opener, "open", lambda req, timeout=None: FakeResponse())
        results = XueqiuChannel().search_stock("Moutai", limit=5)
        assert len(results) == 2
        assert results[0]["symbol"] == "SH600519"
        assert results[0]["name"] == "Kweichow Moutai"
        assert results[1]["exchange"] == "SZA"

    # ------------------------------------------------------------------ #
    # get_hot_posts
    # ------------------------------------------------------------------ #

    def test_get_hot_posts_returns_list(self, monkeypatch):
        import agent_reach.channels.xueqiu as xueqiu_mod

        monkeypatch.setattr(xueqiu_mod, "_cookies_initialized", True)

        # v4 timeline: each item has a JSON-encoded `data` field
        def make_item(id_, title, text, author, likes, target):
            post = {
                "id": id_,
                "title": title,
                "text": text,
                "user": {"screen_name": author},
                "like_count": likes,
                "target": target,
            }
            return {"data": json.dumps(post), "original_status": None}

        fake_data = {
            "list": [
                make_item(111, "Market analysis", "<p>Today's market trend&amp;analysis</p>", "Investor A", 42, "/1234567890/111"),
                make_item(222, "", "Short comment", "Investor B", 10, "/9876543210/222"),
            ]
        }

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

            def read(self):
                return json.dumps(fake_data).encode()

        monkeypatch.setattr(xueqiu_mod._opener, "open", lambda req, timeout=None: FakeResponse())
        posts = XueqiuChannel().get_hot_posts(limit=10)
        assert len(posts) == 2
        assert posts[0]["id"] == 111
        assert posts[0]["author"] == "Investor A"
        assert posts[0]["likes"] == 42
        assert "Today's market trend&analysis" in posts[0]["text"]  # HTML stripped
        assert "<p>" not in posts[0]["text"]
        assert posts[0]["url"] == "https://xueqiu.com/1234567890/111"

    def test_get_hot_posts_respects_limit(self, monkeypatch):
        import agent_reach.channels.xueqiu as xueqiu_mod

        monkeypatch.setattr(xueqiu_mod, "_cookies_initialized", True)

        fake_data = {
            "list": [
                {
                    "data": json.dumps({
                        "id": i,
                        "title": f"Post {i}",
                        "text": f"Content {i}",
                        "user": {"screen_name": f"User {i}"},
                        "like_count": i,
                        "target": f"/user/{i}",
                    }),
                    "original_status": None,
                }
                for i in range(10)
            ]
        }

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

            def read(self):
                return json.dumps(fake_data).encode()

        monkeypatch.setattr(xueqiu_mod._opener, "open", lambda req, timeout=None: FakeResponse())
        posts = XueqiuChannel().get_hot_posts(limit=3)
        assert len(posts) == 3

    # ------------------------------------------------------------------ #
    # get_hot_stocks
    # ------------------------------------------------------------------ #

    def test_get_hot_stocks(self, monkeypatch):
        import agent_reach.channels.xueqiu as xueqiu_mod

        monkeypatch.setattr(xueqiu_mod, "_cookies_initialized", True)

        fake_data = {
            "data": {
                "items": [
                    {"code": "SH600519", "name": "Kweichow Moutai", "current": 1800.0, "percent": 1.5},
                    {"code": "SZ000858", "name": "Wuliangye", "current": 160.0, "percent": -0.8},
                    {"code": "SH601318", "name": "Ping An Insurance", "current": 45.0, "percent": 0.3},
                ]
            }
        }

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

            def read(self):
                return json.dumps(fake_data).encode()

        monkeypatch.setattr(xueqiu_mod._opener, "open", lambda req, timeout=None: FakeResponse())
        stocks = XueqiuChannel().get_hot_stocks(limit=10, stock_type=10)
        assert len(stocks) == 3
        assert stocks[0]["symbol"] == "SH600519"
        assert stocks[0]["rank"] == 1
        assert stocks[1]["percent"] == -0.8
        assert stocks[2]["rank"] == 3

    # ------------------------------------------------------------------ #
    # Cookie loading
    # ------------------------------------------------------------------ #

    def test_ensure_cookies_loads_from_config(self, monkeypatch, tmp_path):
        """_ensure_cookies() should inject cookies from the config file."""
        import agent_reach.channels.xueqiu as xueqiu_mod

        monkeypatch.setattr(xueqiu_mod, "_cookies_initialized", False)

        # Provide a fake Config that returns a cookie string with xq_a_token
        class FakeConfig:
            def get(self, key, default=None):
                if key == "xueqiu_cookie":
                    return "xq_a_token=TESTTOKEN; xq_is_login=1"
                return default

        import agent_reach.channels.xueqiu as xq_mod
        monkeypatch.setattr(
            xq_mod,
            "_load_cookies_from_config",
            lambda: (xq_mod._inject_cookie_string("xq_a_token=TESTTOKEN; xq_is_login=1") or True),
        )
        monkeypatch.setattr(xq_mod, "_load_cookies_from_browser", lambda: False)

        # Patch opener so no real HTTP call is made
        class FakeResp:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self): return b'{"data":{"items":[]}}'

        monkeypatch.setattr(xq_mod._opener, "open", lambda req, timeout=None: FakeResp())

        xq_mod._ensure_cookies()
        assert xq_mod._cookies_initialized is True
        cookie_names = {c.name for c in xq_mod._cookie_jar}
        assert "xq_a_token" in cookie_names

    def test_get_json_sends_referer_and_browser_ua(self, monkeypatch):
        """_get_json() must send Referer and a browser-like User-Agent."""
        import agent_reach.channels.xueqiu as xueqiu_mod

        monkeypatch.setattr(xueqiu_mod, "_cookies_initialized", True)
        captured = {}

        class FakeResp:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self): return b'{"data":{"items":[]}}'

        def fake_open(req, timeout=None):
            captured["ua"] = req.get_header("User-agent")
            captured["referer"] = req.get_header("Referer")
            return FakeResp()

        monkeypatch.setattr(xueqiu_mod._opener, "open", fake_open)
        xueqiu_mod._get_json("https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol=SH000001")

        assert captured["referer"] == "https://xueqiu.com/"
        assert "Mozilla" in captured["ua"]
        assert "agent-reach" not in captured["ua"]


class TestRedditChannel:
    """Multi-backend: OpenCLI > rdt-cli, no zero-config path."""

    @staticmethod
    def _isolate(monkeypatch, opencli=None):
        """Isolate OpenCLI candidate (None = not installed), focus on rdt-cli path."""
        from agent_reach.channels.reddit import RedditChannel
        monkeypatch.setattr(RedditChannel, "_check_opencli", lambda self: opencli)

    def test_reports_off_when_nothing_installed(self, monkeypatch):
        self._isolate(monkeypatch)
        monkeypatch.setattr(shutil, "which", lambda _: None)
        from agent_reach.channels.reddit import RedditChannel
        status, msg = RedditChannel().check()
        assert status == "off"
        # Honest message: explicitly say no zero-config path, recommend OpenCLI + rdt git source
        assert "zero-config" in msg
        assert "opencli" in msg
        assert "git+https://github.com/public-clis/rdt-cli.git" in msg

    def test_opencli_ready_wins(self, monkeypatch):
        self._isolate(monkeypatch, opencli=("ok", "OpenCLI available (reuses browser login state)"))
        monkeypatch.setattr(shutil, "which", lambda _: None)
        from agent_reach.channels.reddit import RedditChannel
        ch = RedditChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert ch.active_backend == "OpenCLI"

    def test_reports_ok_when_authenticated(self, monkeypatch):
        self._isolate(monkeypatch)
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/rdt")
        fake_output = json.dumps({
            "ok": True,
            "schema_version": "1",
            "data": {"authenticated": True, "username": "testuser", "cookie_count": 1},
        })

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, fake_output, "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.reddit import RedditChannel
        ch = RedditChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert "testuser" in msg
        assert ch.active_backend == "rdt-cli"

    def test_reports_warn_when_not_authenticated(self, monkeypatch):
        self._isolate(monkeypatch)
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/rdt")
        fake_output = json.dumps({
            "ok": True,
            "schema_version": "1",
            "data": {"authenticated": False, "username": None, "cookie_count": 0},
        })

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, fake_output, "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.reddit import RedditChannel
        ch = RedditChannel()
        status, msg = ch.check()
        assert status == "warn"
        assert "403" in msg
        assert "rdt login" in msg
        assert "Cookie-Editor" in msg
        assert "chromewebstore.google.com" in msg
        # Not logged in is operational state: process alive, backend still usable
        assert ch.active_backend == "rdt-cli"

    def test_reports_error_when_status_check_fails(self, monkeypatch):
        """rdt non-zero exit with unparsable output → tool error, no longer warn."""
        self._isolate(monkeypatch)
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/rdt")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 1, "not valid json{{{", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.reddit import RedditChannel
        ch = RedditChannel()
        status, msg = ch.check()
        assert status == "error"
        assert "rdt exited abnormally" in msg
        assert ch.active_backend is None

    def test_reports_error_with_reinstall_hint_when_broken(self, monkeypatch):
        """which hits but exec throws FileNotFoundError (venv chain broken) → error + reinstall prescription."""
        self._isolate(monkeypatch)
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/rdt")

        def fake_run(cmd, **kwargs):
            raise FileNotFoundError("/usr/local/bin/rdt")

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.reddit import RedditChannel
        ch = RedditChannel()
        status, msg = ch.check()
        assert status == "error"
        assert "cannot execute" in msg
        assert "pipx install --force" in msg  # rdt-specific git source reinstall prescription
        assert "git+https://github.com/public-clis/rdt-cli.git" in msg
        assert ch.active_backend is None

    def test_reports_error_with_reinstall_hint_on_exit_127(self, monkeypatch):
        """Exit code 127 (found but cannot run) treated as broken chain too."""
        self._isolate(monkeypatch)
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/rdt")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 127, "", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.reddit import RedditChannel
        ch = RedditChannel()
        status, msg = ch.check()
        assert status == "error"
        assert "pipx install --force" in msg
        assert ch.active_backend is None

    def test_can_handle_reddit_urls(self):
        from agent_reach.channels.reddit import RedditChannel
        ch = RedditChannel()
        assert ch.can_handle("https://www.reddit.com/r/python/comments/abc123/")
        assert ch.can_handle("https://redd.it/abc123")
        assert not ch.can_handle("https://github.com/user/repo")
        assert not ch.can_handle("https://v2ex.com/t/123")


class TestXiaoHongShuChannel:
    """Multi-backend selection: OpenCLI > xiaohongshu-mcp > xhs-cli, first fully usable one wins."""

    @staticmethod
    def _isolate(monkeypatch, opencli=None, mcp_reachable=False):
        """Isolate OpenCLI / mcp candidates, let tests focus on target backend.

        opencli: None means not installed; otherwise pass (status, message) tuple.
        """
        import agent_reach.channels.xiaohongshu as xhs_mod

        monkeypatch.setattr(
            XiaoHongShuChannel, "_check_opencli", lambda self: opencli
        )
        monkeypatch.setattr(
            xhs_mod, "_mcp_service_reachable", lambda timeout=3: mcp_reachable
        )

    def test_reports_ok_when_cli_authenticated(self, monkeypatch):
        self._isolate(monkeypatch)
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/xhs")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "ok: true\nusername: testuser\n", "")

        monkeypatch.setattr(subprocess, "run", fake_run)

        ch = XiaoHongShuChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert "xhs-cli available" in msg
        assert ch.active_backend == "xhs-cli (xiaohongshu-cli)"

    def test_reports_warn_when_not_authenticated(self, monkeypatch):
        self._isolate(monkeypatch)
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/xhs")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 1, "", "ok: false\nerror:\n  code: not_authenticated\n")

        monkeypatch.setattr(subprocess, "run", fake_run)

        ch = XiaoHongShuChannel()
        status, msg = ch.check()
        assert status == "warn"
        assert "xhs login" in msg
        # Not logged in is operational state: tool process alive, backend still usable
        assert ch.active_backend == "xhs-cli (xiaohongshu-cli)"

    def test_reports_off_when_nothing_installed(self, monkeypatch):
        self._isolate(monkeypatch)
        monkeypatch.setattr(shutil, "which", lambda _: None)
        ch = XiaoHongShuChannel()
        status, msg = ch.check()
        assert status == "off"
        # off guidance recommends modern backends, not the discontinued xhs-cli
        assert "opencli" in msg
        assert "xiaohongshu-mcp" in msg
        assert ch.active_backend is None

    def test_reports_error_with_reinstall_hint_when_broken(self, monkeypatch):
        """which hits but exec throws FileNotFoundError (venv chain broken) → error + reinstall prescription."""
        self._isolate(monkeypatch)
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/xhs")

        def fake_run(cmd, **kwargs):
            raise FileNotFoundError("/usr/local/bin/xhs")

        monkeypatch.setattr(subprocess, "run", fake_run)

        ch = XiaoHongShuChannel()
        status, msg = ch.check()
        assert status == "error"
        assert "cannot execute" in msg
        assert "uv tool install --force xiaohongshu-cli" in msg
        assert "pipx reinstall xiaohongshu-cli" in msg
        assert ch.active_backend is None

    def test_opencli_ready_wins_over_cli(self, monkeypatch):
        """OpenCLI fully usable wins in order, even if xhs-cli is also fully usable."""
        self._isolate(monkeypatch, opencli=("ok", "OpenCLI available (reuses browser login state)"))
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/xhs")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "ok: true\n", "")

        monkeypatch.setattr(subprocess, "run", fake_run)

        ch = XiaoHongShuChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert ch.active_backend == "OpenCLI"

    def test_opencli_warn_loses_to_usable_cli(self, monkeypatch):
        """OpenCLI installed but extension not connected (warn), fully usable xhs-cli wins."""
        self._isolate(monkeypatch, opencli=("warn", "Extension not connected"))
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/xhs")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "ok: true\n", "")

        monkeypatch.setattr(subprocess, "run", fake_run)

        ch = XiaoHongShuChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert ch.active_backend == "xhs-cli (xiaohongshu-cli)"

    def test_mcp_service_wins_when_opencli_absent(self, monkeypatch):
        """Server scenario: OpenCLI not installed, mcp service reachable and mcporter connected → mcp wins."""
        self._isolate(monkeypatch, mcp_reachable=True)

        def fake_which(name):
            return "/usr/local/bin/mcporter" if name == "mcporter" else None

        monkeypatch.setattr(shutil, "which", fake_which)

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "exa\nxiaohongshu\n", "")

        monkeypatch.setattr(subprocess, "run", fake_run)

        ch = XiaoHongShuChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert ch.active_backend == "xiaohongshu-mcp"
        assert "search_feeds" in msg

    def test_mcp_reachable_but_mcporter_unconfigured_warns(self, monkeypatch):
        self._isolate(monkeypatch, mcp_reachable=True)

        def fake_which(name):
            return "/usr/local/bin/mcporter" if name == "mcporter" else None

        monkeypatch.setattr(shutil, "which", fake_which)

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "exa\n", "")

        monkeypatch.setattr(subprocess, "run", fake_run)

        ch = XiaoHongShuChannel()
        status, msg = ch.check()
        assert status == "warn"
        assert "mcporter config add xiaohongshu" in msg
        assert ch.active_backend == "xiaohongshu-mcp"

    def test_backend_override_prefers_cli(self, monkeypatch):
        """When config xiaohongshu_backend=xhs-cli, use xhs-cli even if OpenCLI is ready."""
        self._isolate(monkeypatch, opencli=("ok", "OpenCLI available"))
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/xhs")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "ok: true\n", "")

        monkeypatch.setattr(subprocess, "run", fake_run)

        class _Cfg:
            def get(self, key, default=None):
                return "xhs-cli" if key == "xiaohongshu_backend" else default

        ch = XiaoHongShuChannel()
        status, _ = ch.check(_Cfg())
        assert status == "ok"
        assert ch.active_backend == "xhs-cli (xiaohongshu-cli)"


class TestBilibiliChannel:
    """Multi-backend: bili-cli > OpenCLI > Search API. yt-dlp has left Bilibili (412 confirmed)."""

    @staticmethod
    def _isolate(monkeypatch, opencli=None, api_ok=False):
        import agent_reach.channels.bilibili as bilibili_mod
        monkeypatch.setattr(
            bilibili_mod.BilibiliChannel, "_check_opencli", lambda self: opencli
        )
        monkeypatch.setattr(bilibili_mod, "_search_api_ok", lambda: api_ok)

    def test_bili_cli_ok_is_active_backend(self, monkeypatch):
        self._isolate(monkeypatch)
        monkeypatch.setattr(
            shutil, "which",
            lambda cmd: "/usr/local/bin/bili" if cmd == "bili" else None,
        )

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "bili, version 0.6.2", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.bilibili import BilibiliChannel
        ch = BilibiliChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert "bili-cli available" in msg
        assert ch.active_backend == "bili-cli"

    def test_bili_broken_falls_back_to_api_with_hint_kept(self, monkeypatch):
        """bili broken → API fallback wins, but reinstall prescription must remain in message."""
        self._isolate(monkeypatch, api_ok=True)
        monkeypatch.setattr(
            shutil, "which",
            lambda cmd: "/usr/local/bin/bili" if cmd == "bili" else None,
        )

        def fake_run(cmd, **kwargs):
            raise FileNotFoundError(cmd[0])

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.bilibili import BilibiliChannel
        ch = BilibiliChannel()
        status, msg = ch.check()
        assert status == "ok"  # Search API fallback
        assert ch.active_backend == "Bilibili Search API"
        assert "Alternate backend broken" in msg
        assert "pipx reinstall bilibili-cli" in msg

    def test_bili_broken_and_no_fallback_reports_error(self, monkeypatch):
        self._isolate(monkeypatch, api_ok=False)
        monkeypatch.setattr(
            shutil, "which",
            lambda cmd: "/usr/local/bin/bili" if cmd == "bili" else None,
        )

        def fake_run(cmd, **kwargs):
            raise FileNotFoundError(cmd[0])

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.bilibili import BilibiliChannel
        ch = BilibiliChannel()
        status, msg = ch.check()
        assert status == "error"
        assert "uv tool install --force bilibili-cli" in msg
        assert ch.active_backend is None

    def test_opencli_serves_when_bili_missing(self, monkeypatch):
        self._isolate(monkeypatch, opencli=("ok", "OpenCLI available (subtitles)"), api_ok=True)
        monkeypatch.setattr(shutil, "which", lambda _: None)
        from agent_reach.channels.bilibili import BilibiliChannel
        ch = BilibiliChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert ch.active_backend == "OpenCLI"

    def test_api_only_still_ok_with_install_nudge(self, monkeypatch):
        self._isolate(monkeypatch, api_ok=True)
        monkeypatch.setattr(shutil, "which", lambda _: None)
        from agent_reach.channels.bilibili import BilibiliChannel
        ch = BilibiliChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert ch.active_backend == "Bilibili Search API"
        assert "bilibili-cli" in msg

    def test_off_when_everything_unreachable(self, monkeypatch):
        self._isolate(monkeypatch, api_ok=False)
        monkeypatch.setattr(shutil, "which", lambda _: None)
        from agent_reach.channels.bilibili import BilibiliChannel
        ch = BilibiliChannel()
        status, msg = ch.check()
        assert status == "off"
        assert ch.active_backend is None


class TestYouTubeChannel:
    def test_reports_error_with_reinstall_hint_when_broken(self, monkeypatch):
        """yt-dlp which hits but exec throws FileNotFoundError → error + reinstall prescription."""
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/yt-dlp")

        def fake_run(cmd, **kwargs):
            raise FileNotFoundError(cmd[0])

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.youtube import YouTubeChannel
        ch = YouTubeChannel()
        status, msg = ch.check()
        assert status == "error"
        assert "cannot execute" in msg
        assert "uv tool install --force yt-dlp" in msg
        assert ch.active_backend is None


class TestGitHubChannel:
    def test_reports_error_with_reinstall_hint_when_broken(self, monkeypatch):
        """gh which hits but exec fails → error + brew reinstall prescription (gh is not a pip package)."""
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/gh")

        def fake_run(cmd, **kwargs):
            raise FileNotFoundError(cmd[0])

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.github import GitHubChannel
        ch = GitHubChannel()
        status, msg = ch.check()
        assert status == "error"
        assert "cannot execute" in msg
        assert "brew reinstall gh" in msg
        assert ch.active_backend is None

    def test_active_backend_set_when_authenticated(self, monkeypatch):
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/gh")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "Logged in to github.com", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.github import GitHubChannel
        ch = GitHubChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert ch.active_backend == "gh CLI"

    def test_active_backend_set_when_unauthenticated(self, monkeypatch):
        """gh auth status non-zero exit is normal business state (not logged in): warn but backend available."""
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/gh")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 1, "", "You are not logged in")

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.github import GitHubChannel
        ch = GitHubChannel()
        status, msg = ch.check()
        assert status == "warn"
        assert "gh auth login" in msg
        assert ch.active_backend == "gh CLI"


class TestLinkedInChannel:
    def test_reports_error_with_reinstall_hint_when_broken(self, monkeypatch):
        """mcporter which hits but exec fails → error + npm reinstall prescription."""
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/mcporter")

        def fake_run(cmd, **kwargs):
            raise FileNotFoundError(cmd[0])

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.linkedin import LinkedInChannel
        ch = LinkedInChannel()
        status, msg = ch.check()
        assert status == "error"
        assert "npm install -g mcporter" in msg
        assert ch.active_backend is None

    def test_active_backend_set_when_linkedin_configured(self, monkeypatch):
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/mcporter")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "linkedin  http://localhost:3000/mcp", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.linkedin import LinkedInChannel
        ch = LinkedInChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert ch.active_backend == "linkedin-scraper-mcp"

    def test_off_without_backend_when_linkedin_not_configured(self, monkeypatch):
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/mcporter")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "exa  https://mcp.exa.ai/mcp", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.linkedin import LinkedInChannel
        ch = LinkedInChannel()
        status, msg = ch.check()
        assert status == "off"
        assert ch.active_backend is None


class TestExaSearchChannel:
    def test_reports_error_with_reinstall_hint_when_broken(self, monkeypatch):
        """mcporter which hits but exec fails → error + npm reinstall prescription."""
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/mcporter")

        def fake_run(cmd, **kwargs):
            raise FileNotFoundError(cmd[0])

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.exa_search import ExaSearchChannel
        ch = ExaSearchChannel()
        status, msg = ch.check()
        assert status == "error"
        assert "npm install -g mcporter" in msg
        assert ch.active_backend is None

    def test_active_backend_set_when_exa_configured(self, monkeypatch):
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/mcporter")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "exa  https://mcp.exa.ai/mcp", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.exa_search import ExaSearchChannel
        ch = ExaSearchChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert ch.active_backend == "Exa via mcporter"


class TestXiaoyuzhouChannel:
    def test_reports_error_with_reinstall_hint_when_ffmpeg_broken(self, monkeypatch):
        """ffmpeg which hits but exec fails (pip fake ffmpeg chain broken) → error + reinstall prescription."""
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/ffmpeg")

        def fake_run(cmd, **kwargs):
            raise FileNotFoundError(cmd[0])

        monkeypatch.setattr(subprocess, "run", fake_run)
        from agent_reach.channels.xiaoyuzhou import XiaoyuzhouChannel
        ch = XiaoyuzhouChannel()
        status, msg = ch.check()
        assert status == "error"
        assert "cannot execute" in msg
        assert "brew install ffmpeg" in msg
        assert ch.active_backend is None

    def test_active_backend_set_when_fully_configured(self, monkeypatch):
        monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/ffmpeg")

        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "ffmpeg version 7.0", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr("os.path.isfile", lambda p: True)  # transcribe.sh installed
        monkeypatch.setenv("GROQ_API_KEY", "gsk_test")
        from agent_reach.channels.xiaoyuzhou import XiaoyuzhouChannel
        ch = XiaoyuzhouChannel()
        status, msg = ch.check()
        assert status == "ok"
        assert ch.active_backend == "groq-whisper"
