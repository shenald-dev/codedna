"""GitHub Analyzer — fetches community stats for GitHub repositories."""

from __future__ import annotations

import json
import urllib.request
from urllib.error import URLError, HTTPError


class GitHubAnalyzer:
    """Fetches metadata and community stats from GitHub API."""

    def analyze(self, source: str) -> dict:
        """Fetch repository stats if the source is a GitHub URL.

        Args:
            source: The repository source (local path or URL).

        Returns:
            Dict containing GitHub stats if available, otherwise empty.
        """
        stats = {
            "is_github": False,
            "stars": 0,
            "forks": 0,
            "issues": 0,
            "description": "",
            "homepage": "",
        }

        if not source.startswith(("http://github.com", "https://github.com")):
            return stats

        # Extract owner/repo
        parts = source.rstrip("/").split("/")
        if len(parts) >= 2:
            owner, repo = parts[-2], parts[-1]
            if repo.endswith(".git"):
                repo = repo[:-4]

            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            
            try:
                req = urllib.request.Request(
                    api_url,
                    headers={"User-Agent": "CodeDNA-Analyzer"}
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    
                    stats.update({
                        "is_github": True,
                        "stars": data.get("stargazers_count", 0),
                        "forks": data.get("forks_count", 0),
                        "issues": data.get("open_issues_count", 0),
                        "description": data.get("description", "") or "",
                        "homepage": data.get("homepage", "") or "",
                    })
            except (URLError, HTTPError):
                # Fail gracefully if offline or rate limited
                pass

        return stats
