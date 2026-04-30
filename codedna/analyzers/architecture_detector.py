"""Architecture Detector — identifies architecture patterns via rule-based heuristics."""

from __future__ import annotations

from pathlib import Path

from .language_detector import IGNORE_DIRS

# Architecture pattern definitions
PATTERNS = {
    "MVC": {
        "indicators": ["models", "views", "controllers", "templates"],
        "min_matches": 3,
    },
    "Layered": {
        "indicators": ["api", "services", "repositories", "models", "controllers", "routes"],
        "min_matches": 3,
    },
    "Microservices": {
        "indicators": ["docker-compose", "gateway", "services", "api-gateway"],
        "min_matches": 2,
    },
    "Plugin Architecture": {
        "indicators": ["plugins", "extensions", "addons", "hooks", "middleware"],
        "min_matches": 2,
    },
    "Event-Driven": {
        "indicators": ["events", "handlers", "listeners", "subscribers", "queues", "consumers"],
        "min_matches": 2,
    },
    "Monorepo": {
        "indicators": ["packages", "apps", "libs", "workspaces"],
        "min_matches": 2,
    },
    "CLI Tool": {
        "indicators": ["cli", "commands", "bin"],
        "min_matches": 2,
    },
}

# File/config indicators
CONFIG_PATTERNS = {
    "Containerized": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
    "CI/CD Enabled": [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", ".circleci"],
    "Tested": ["tests", "test", "__tests__", "spec", "pytest.ini", "jest.config"],
    "Documented": ["docs", "documentation", "wiki", "ARCHITECTURE.md"],
    "Type-Safe": ["tsconfig.json", "mypy.ini", ".mypy.ini", "pyproject.toml"],
}


class ArchitectureDetector:
    """Detects software architecture patterns through directory and file analysis."""

    def detect(self, repo_path: Path) -> dict:
        """Identify architecture patterns in the repository.

        Returns:
            Dict with detected patterns, traits, and confidence scores.
        """
        all_names = set()
        src_dirs = []

        for item in self._walk(repo_path):
            if item.is_dir():
                all_names.add(item.name.lower())
                if item.name not in IGNORE_DIRS:
                    try:
                        depth = len(item.relative_to(repo_path).parts)
                        src_dirs.append(depth)
                    except ValueError:
                        pass
            else:
                all_names.add(item.name.lower())
                # Also track relative paths for nested indicators
                try:
                    rel = str(item.relative_to(repo_path)).replace("\\", "/").lower()
                    for part in rel.split("/"):
                        all_names.add(part)
                except ValueError:
                    pass

        # Detect architecture patterns
        detected = []
        for pattern_name, config in PATTERNS.items():
            indicators = config["indicators"]
            matches = [ind for ind in indicators if ind in all_names]
            if len(matches) >= config["min_matches"]:
                confidence = round(len(matches) / len(indicators), 2)
                detected.append({
                    "pattern": pattern_name,
                    "confidence": confidence,
                    "matched_indicators": matches,
                })

        # Detect infrastructure traits
        traits = []
        for trait_name, indicators in CONFIG_PATTERNS.items():
            for ind in indicators:
                ind_path = repo_path / ind
                if ind_path.exists() or ind.lower() in all_names:
                    traits.append(trait_name)
                    break

        # Determine coupling level
        if not src_dirs:
            coupling = "Unknown"
        else:
            avg_depth = sum(src_dirs) / len(src_dirs)
            if avg_depth > 4:
                coupling = "High"
            elif avg_depth > 2.5:
                coupling = "Moderate"
            else:
                coupling = "Low"

        # Sort by confidence
        detected.sort(key=lambda x: x["confidence"], reverse=True)

        primary_pattern = detected[0]["pattern"] if detected else "Monolith"

        return {
            "primary_pattern": primary_pattern,
            "detected_patterns": detected,
            "traits": traits,
            "coupling": coupling,
        }

    def _walk(self, root: Path, max_depth: int = 5):
        stack = [(root, 0)]
        while stack:
            current_dir, current_depth = stack.pop()
            if current_depth >= max_depth:
                continue
            try:
                for item in current_dir.iterdir():
                    if item.name in IGNORE_DIRS or item.name.startswith("."):
                        continue
                    yield item
                    if item.is_dir():
                        stack.append((item, current_depth + 1))
            except PermissionError:
                pass
