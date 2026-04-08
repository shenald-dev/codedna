"""Developer Analyzer — analyzes Git commit history for contributor behavior patterns."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path


class DeveloperAnalyzer:
    """Analyzes developer contribution patterns from Git history."""

    def analyze(self, repo_path: Path, max_commits: int = 500) -> dict:
        """Analyze developer behavior from Git history.

        Returns:
            Dict with contributors, hotspots, collaboration data, and commit patterns.
        """
        from git import Repo
        from git.exc import InvalidGitRepositoryError

        try:
            repo = Repo(str(repo_path))
        except InvalidGitRepositoryError:
            return {"error": "Not a Git repository", "contributors": []}

        contributors: Counter = Counter()
        file_changes: Counter = Counter()
        monthly_commits: defaultdict = defaultdict(int)
        contributor_files: defaultdict = defaultdict(set)
        commit_count = 0

        for commit in repo.iter_commits(max_count=max_commits):
            author = commit.author.name or commit.author.email
            contributors[author] += 1
            commit_count += 1

            # Track monthly activity
            month_key = commit.committed_datetime.strftime("%Y-%m")
            monthly_commits[month_key] += 1

            # Track file changes
            try:
                for file_path in commit.stats.files:
                    file_changes[file_path] += 1
                    contributor_files[author].add(file_path)
            except Exception:
                pass

        # Build contributor profiles
        total_commits = sum(contributors.values()) or 1
        contributor_list = []
        for author, count in contributors.most_common():
            role = self._classify_role(count, total_commits, len(contributor_files.get(author, set())))  # noqa: E501
            contributor_list.append({
                "name": author,
                "commits": count,
                "percentage": round((count / total_commits) * 100, 1),
                "files_touched": len(contributor_files.get(author, set())),
                "role": role,
            })

        # Hotspots (most changed files)
        hotspots = [
            {"file": f, "changes": c}
            for f, c in file_changes.most_common(15)
        ]

        # Collaboration pairs (authors who modify the same files)
        collaboration = self._detect_collaboration(contributor_files)

        return {
            "total_commits": commit_count,
            "total_contributors": len(contributors),
            "contributors": contributor_list[:20],
            "hotspots": hotspots,
            "collaboration_pairs": collaboration[:10],
            "monthly_activity": dict(sorted(monthly_commits.items())[-12:]),
            "bus_factor": self._compute_bus_factor(contributors, total_commits),
        }

    def _classify_role(self, commits: int, total: int, files: int) -> str:
        """Classify a contributor's role based on activity."""
        pct = (commits / total) * 100
        if pct > 50:
            return "Primary Architect"
        elif pct > 20:
            return "Core Maintainer"
        elif pct > 5:
            return "Regular Contributor"
        elif commits > 1:
            return "Occasional Contributor"
        return "Drive-by Contributor"

    def _detect_collaboration(self, contributor_files: dict) -> list[dict]:
        """Find pairs of developers who work on the same files."""
        authors = list(contributor_files.keys())
        pairs = []

        for i, a1 in enumerate(authors):
            for a2 in authors[i + 1:]:
                shared = contributor_files[a1] & contributor_files[a2]
                if len(shared) > 2:
                    pairs.append({
                        "pair": [a1, a2],
                        "shared_files": len(shared),
                    })

        pairs.sort(key=lambda x: x["shared_files"], reverse=True)
        return pairs

    def _compute_bus_factor(self, contributors: Counter, total: int) -> int:
        """Estimate bus factor — minimum contributors responsible for 50% of commits."""
        cumulative = 0
        for i, (_, count) in enumerate(contributors.most_common(), 1):
            cumulative += count
            if cumulative >= total * 0.5:
                return i
        return len(contributors)
