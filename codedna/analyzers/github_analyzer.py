"""GitHub Analyzer — fetches community stats for GitHub repositories."""

from __future__ import annotations

import json
import urllib.request
import urllib.parse
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

        try:
            parsed = urllib.parse.urlparse(source)
        except Exception:
            return stats

        if parsed.scheme not in ("http", "https") or parsed.hostname != "github.com":
            return stats

        # Extract owner/repo from path (e.g., /owner/repo)
        path_parts = [p for p in parsed.path.split("/") if p]
        if len(path_parts) >= 2:
            owner, repo = path_parts[0], path_parts[1]
            if repo.endswith(".git"):
                repo = repo[:-4]

            # Validate that owner and repo are safe strings
            def is_valid_identifier(s):
                return s and s not in ("..", ".") and all(c.isalnum() or c in "-_." for c in s)

            if not is_valid_identifier(owner) or not is_valid_identifier(repo):
                return stats

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
