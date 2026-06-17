# -*- coding: utf-8 -*-
"""GitHub — gh CLI or GH_TOKEN env var."""

import os
from agent_reach.probe import probe_command

from .base import Channel


class GitHubChannel(Channel):
    name = "github"
    description = "GitHub repositories and code"
    backends = ["gh CLI", "GH_TOKEN env var"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        from urllib.parse import urlparse
        return "github.com" in urlparse(url).netloc.lower()

    def check(self, config=None):
        # Check for GH_TOKEN env var first (headless auth)
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if token:
            # Verify token works with a lightweight API call
            probe = probe_command(
                "gh", ["api", "user", "--jq", ".login", "--silent"],
                timeout=10, package="gh"
            )
            if probe.ok or probe.status == "timeout":
                self.active_backend = self.backends[1]
                return "ok", "GH_TOKEN environment variable is set (can perform read-only operations via gh)"
            # gh not available but token is — still useful for direct API calls

        # Fall back to gh auth status
        probe = probe_command("gh", ["auth", "status"], timeout=10, package="gh")
        if probe.status == "missing":
            if token:
                self.active_backend = self.backends[1]
                return "ok", "GH_TOKEN is set (gh CLI not installed, can connect via API directly)"
            self.active_backend = None
            return "warn", "gh CLI not installed. Install: https://cli.github.com"
        if probe.status == "broken":
            self.active_backend = None
            return "error", (
                "gh command exists but cannot execute — installation is corrupted. Reinstall to fix:\n"
                "  brew reinstall gh\n"
                "or reinstall gh CLI from https://cli.github.com"
            )
        if probe.status == "timeout":
            self.active_backend = "gh CLI"
            return "warn", "gh CLI status check timed out, run gh auth status for details"
        if probe.ok:
            self.active_backend = "gh CLI"
            return "ok", "Fully available (read, search, Fork, Issue, PR, etc.)"
        # rc != 0: gh is alive but not authenticated
        if token:
            self.active_backend = self.backends[1]
            return "ok", "gh CLI not logged in, but GH_TOKEN environment variable is set"
        self.active_backend = "gh CLI"
        return "warn", "gh CLI is installed but not authenticated. Run gh auth login to unlock full features"
