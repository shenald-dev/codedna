"""Evolution Engine — tracks how the codebase architecture changed over time."""

from __future__ import annotations

import re
=======>>>>>>> origin/master
from collections import Counter, defaultdict
from pathlib import Path
if typing.TYPE_CHECKING:
    from git import Repo


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
        from git import Repo
        from git.exc import InvalidGitRepositoryError

        try:
            repo = Repo(str(repo_path))
        except InvalidGitRepositoryError:
            return {"error": "Not a Git repository", "timeline": []}

        try:
            log_output = repo.git.log(
                "--format=tformat:COMMIT::%H::%cI::%cd::%s",
                "--date=short",
                "--shortstat",
                "-n", "500"
            )
        except Exception:            log_output = ""

        commits = []
        current_commit = {}
        for line in log_output.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith("COMMIT::"):
                if current_commit:
                    commits.append(current_commit)
                parts = line.split("::", 4)
                current_commit = {
                    "hexsha": parts[1] if len(parts) > 1 else "",
                    "iso_date": parts[2] if len(parts) > 2 else "",
                    "date": parts[3] if len(parts) > 3 else "",
                    "message": parts[4].strip().split("\n")[0][:60] if len(parts) > 4 else "",
                    "additions": 0,
                    "deletions": 0,
                }
            elif current_commit and ("files changed" in line or "file changed" in line):
                ins_match = re.search(r'(\d+)\s+insertion', line)
                del_match = re.search(r'(\d+)\s+deletion', line)
                if ins_match:
                    current_commit["additions"] = int(ins_match.group(1))
                if del_match:
                    current_commit["deletions"] = int(del_match.group(1))

        if current_commit:
            commits.append(current_commit)

        if not commits:
            return {"timeline": [], "patterns": []}

        # Build timeline snapshots
        timeline = self._build_timeline(commits, snapshots, repo)

        # Detect churn (files that change most frequently)
        churn = self._compute_churn(repo)

        # Detect evolution patterns
        patterns = self._detect_patterns(timeline)

        return {
            "total_commits": len(commits),
            "first_commit": commits[-1]["iso_date"] if commits else None,
            "last_commit": commits[0]["iso_date"] if commits else None,
            "timeline": timeline,
            "churn_hotspots": churn[:10],
            "patterns": patterns,
        }

    def _build_timeline(self, commits: list[dict], snapshots: int, repo: Repo) -> list[dict]:
        """Build time-based snapshots of the project's evolution."""
        if len(commits) < 2:            return []

        step = max(1, len(commits) // snapshots)
        timeline = []

        for i in range(0, len(commits), step):
            commit = commits[i]

            # Count files at this point
            try:
                output = repo.git.ls_tree("-r", commit["hexsha"])
                file_count = output.count('\n') + 1 if output else 0
            except Exception:
                file_count = 0

            timeline.append({
                "date": commit["date"],
                "commit": commit["hexsha"][:8],
                "message": commit["message"],
                "file_count": file_count,
                "additions": commit["additions"],
                "deletions": commit["deletions"],
            })

        return timeline[:snapshots]

    def _compute_churn(self, repo: 'Repo') -> list[dict]:
        """Find files with the highest change frequency (churn)."""
        file_changes: Counter = Counter()
        file_additions: defaultdict = defaultdict(int)
        file_deletions: defaultdict = defaultdict(int)

        try:
            # Note: Explicit tformat: prefix is required by newer Git versions for custom strings
            output = repo.git.log(
                "--numstat",
                "--format=format:COMMIT",                "-n 200",
                "--no-renames"            )
        except Exception:
            return {"timeline": [], "patterns": []}

        commits_data = []
        current_commit = None        file_changes: Counter = Counter()
        file_additions: defaultdict = defaultdict(int)
        file_deletions: defaultdict = defaultdict(int)

        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith("COMMIT::"):
                parts = line.split("::", 3)
                if len(parts) >= 4:
                    current_commit = {
                        "hexsha": parts[1],
                        "date": parts[2][:10],
                        "iso_date": parts[2],
                        "message": parts[3].strip().split("\n")[0][:60],
                        "additions": 0,
                        "deletions": 0,
                    }
                    commits_data.append(current_commit)
            elif current_commit is not None:
                parts = line.split('\t')
                if len(parts) >= 3:
                    ins, dels, filepath = parts[0], parts[1], parts[2]
                    try:
                        ins_int = int(ins) if ins != '-' else 0
                        del_int = int(dels) if dels != '-' else 0
                    except ValueError:
                        ins_int, del_int = 0, 0

                    current_commit["additions"] += ins_int
                    current_commit["deletions"] += del_int

                    if len(commits_data) <= 200:
                        file_changes[filepath] += 1
                        file_additions[filepath] += ins_int
                        file_deletions[filepath] += del_int

        if not commits_data:
            return {"timeline": [], "patterns": []}

        # Build timeline snapshots
        timeline = []
        if len(commits_data) >= 2:
            step = max(1, len(commits_data) // snapshots)
            for i in range(0, len(commits_data), step):
                c = commits_data[i]

                try:
                    tree_output = repo.git.ls_tree("-r", c["hexsha"])
                    file_count = tree_output.count('\n') + 1 if tree_output else 0
                except Exception:
                    file_count = 0

                timeline.append({
                    "date": c["date"],
                    "commit": c["hexsha"][:8],
                    "message": c["message"],
                    "file_count": file_count,
                    "additions": c["additions"],
                    "deletions": c["deletions"],
                })
                if len(timeline) == snapshots:
                    break

        churn = [
            {
                "file": f,
                "changes": c,
                "total_additions": file_additions[f],
                "total_deletions": file_deletions[f],
            }
            for f, c in file_changes.most_common(15)
        ]

        patterns = self._detect_patterns(timeline)

        return {
            "total_commits": len(commits_data),
            "first_commit": commits_data[-1]["iso_date"],
            "last_commit": commits_data[0]["iso_date"],
            "timeline": timeline,
            "churn_hotspots": churn[:10],
            "patterns": patterns,
        }

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
