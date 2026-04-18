"""Evolution Engine — tracks how the codebase architecture changed over time."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from git import Repo
from git.exc import InvalidGitRepositoryError


class EvolutionEngine:
    """Analyzes codebase evolution across Git commit history."""

    def analyze(self, repo_path: Path, snapshots: int = 6) -> dict:
        """Track how the codebase evolved over time.

        Args:
            repo_path: Path to the repository.
            snapshots: Number of time-points to analyze.

        Returns:
            Dict with growth timeline, churn hotspots, and evolution patterns.
        """
        try:
            repo = Repo(str(repo_path))
        except InvalidGitRepositoryError:
            return {"error": "Not a Git repository", "timeline": []}

        commits = list(repo.iter_commits(max_count=500))
        if not commits:
            return {"timeline": [], "patterns": []}

        # Build timeline snapshots
        timeline = self._build_timeline(commits, snapshots)

        # Detect churn (files that change most frequently)
        churn = self._compute_churn(commits)

        # Detect evolution patterns
        patterns = self._detect_patterns(timeline)

        return {
            "total_commits": len(commits),
            "first_commit": commits[-1].committed_datetime.isoformat() if commits else None,
            "last_commit": commits[0].committed_datetime.isoformat() if commits else None,
            "timeline": timeline,
            "churn_hotspots": churn[:10],
            "patterns": patterns,
        }

    def _build_timeline(self, commits: list, snapshots: int) -> list[dict]:
        """Build time-based snapshots of the project's evolution."""
        if len(commits) < 2:
            return []

        step = max(1, len(commits) // snapshots)
        timeline = []

        for i in range(0, len(commits), step):
            commit = commits[i]
            date = commit.committed_datetime.strftime("%Y-%m-%d")

            # Count files at this point
            try:
                file_count = sum(1 for _ in commit.tree.traverse() if _.type == "blob")
            except Exception:
                file_count = 0

            # Count insertions/deletions
            try:
                stats = commit.stats.total
                additions = stats.get("insertions", 0)
                deletions = stats.get("deletions", 0)
            except Exception:
                additions = 0
                deletions = 0

            timeline.append({
                "date": date,
                "commit": commit.hexsha[:8],
                "message": commit.message.strip().split("\n")[0][:60],
                "file_count": file_count,
                "additions": additions,
                "deletions": deletions,
            })

        return timeline[:snapshots]

    def _compute_churn(self, commits: list) -> list[dict]:
        """Find files with the highest change frequency (churn)."""
        file_changes: Counter = Counter()
        file_additions: defaultdict = defaultdict(int)
        file_deletions: defaultdict = defaultdict(int)

        for commit in commits[:200]:
            try:
                for filepath, stats in commit.stats.files.items():
                    file_changes[filepath] += 1
                    file_additions[filepath] += stats.get("insertions", 0)
                    file_deletions[filepath] += stats.get("deletions", 0)
            except Exception:
                pass

        return [
            {
                "file": f,
                "changes": c,
                "total_additions": file_additions[f],
                "total_deletions": file_deletions[f],
            }
            for f, c in file_changes.most_common(15)
        ]

    def _detect_patterns(self, timeline: list[dict]) -> list[str]:
        """Detect evolutionary patterns from the timeline."""
        patterns = []

        if len(timeline) < 2:
            return ["Insufficient data"]

        # Check for rapid growth
        file_counts = [t["file_count"] for t in timeline if t["file_count"] > 0]
        if len(file_counts) >= 2 and file_counts[0] > 0:
            growth_ratio = file_counts[-1] / file_counts[0] if file_counts[0] else 1
            if growth_ratio > 3:
                patterns.append("Rapid Growth")
            elif growth_ratio > 1.5:
                patterns.append("Steady Growth")
            elif growth_ratio < 0.8:
                patterns.append("Code Consolidation")

        # Check for high churn
        total_additions = sum(t["additions"] for t in timeline)
        total_deletions = sum(t["deletions"] for t in timeline)
        if total_deletions > 0 and total_additions / max(total_deletions, 1) < 1.5:
            patterns.append("High Refactoring Activity")

        if not patterns:
            patterns.append("Stable Evolution")

        return patterns
