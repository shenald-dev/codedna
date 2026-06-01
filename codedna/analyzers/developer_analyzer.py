"""Developer Analyzer — analyzes Git commit history for contributor behavior patterns."""

from __future__ import annotations

import itertools
from collections import Counter, defaultdict
from pathlib import Path


class DeveloperAnalyzer:
    """Analyzes developer contribution patterns from Git history."""

    def analyze(self, repo_path: Path, max_commits: int = 500) -> dict:
        """Analyze developer behavior from Git history.

        Returns:
            Dict with contributors, hotspots, collaboration data, and commit patterns.
        """
        import git
        try:
            repo = git.Repo(str(repo_path))
        except git.exc.InvalidGitRepositoryError:
            return {"error": "Not a Git repository", "contributors": []}

        contributors: Counter = Counter()
        file_changes: Counter = Counter()
        monthly_commits: defaultdict = defaultdict(int)
        contributor_files: defaultdict = defaultdict(set)
        commit_count = 0

        try:
            # Note: Explicit tformat: prefix is required by newer Git versions for custom strings
            log_output = repo.git.log(
                "--name-only",
                "--format=tformat:COMMIT::%H::%aN::%aE::%ad",
                "--date=short",
                f"-n {max_commits}"
            )

            current_author = None

            for line in log_output.split('\n'):
                line = line.strip()
                if not line:
                    continue

                if line.startswith("COMMIT::"):
                    parts = line.split("::")
                    if len(parts) >= 5:
                        name = parts[2]
                        email = parts[3]
                        date = parts[4]
                        current_author = name or email
                        contributors[current_author] += 1
                        commit_count += 1

                        if len(date) >= 7:
                            month_key = date[:7]
                            monthly_commits[month_key] += 1
                elif current_author:
                    file_changes[line] += 1
                    contributor_files[current_author].add(line)
        except Exception:
            pass

        # Build contributor profiles
        total_commits = commit_count or 1
        contributor_list = []
        for author, count in contributors.most_common():
            files_touched_count = len(contributor_files.get(author, set()))
            role = self._classify_role(count, total_commits, files_touched_count)  # noqa: E501
            contributor_list.append({
                "name": author,
                "commits": count,
                "percentage": round((count / total_commits) * 100, 1),
                "files_touched": files_touched_count,
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
        file_to_authors = defaultdict(list)
        for author, files in contributor_files.items():
            for f in files:
                file_to_authors[f].append(author)

        pair_counts = defaultdict(int)
        for authors in file_to_authors.values():
            if len(authors) > 1:
                for a1, a2 in itertools.combinations(sorted(authors), 2):
                    pair_counts[(a1, a2)] += 1

        pairs = []
        for (a1, a2), count in pair_counts.items():
            if count > 2:
                pairs.append({
                    "pair": [a1, a2],
                    "shared_files": count,
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
