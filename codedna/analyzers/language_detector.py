"""Language Detector — identifies programming languages used in a repository."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

# Extension → Language mapping
LANGUAGE_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".kt": "Kotlin",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C",
    ".hpp": "C++",
    ".swift": "Swift",
    ".scala": "Scala",
    ".r": "R",
    ".m": "Objective-C",
    ".lua": "Lua",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".ps1": "PowerShell",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".less": "LESS",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".dart": "Dart",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
    ".json": "JSON",
    ".xml": "XML",
    ".md": "Markdown",
    ".proto": "Protobuf",
    ".graphql": "GraphQL",
    ".tf": "Terraform",
    ".sol": "Solidity",
    ".zig": "Zig",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".erl": "Erlang",
    ".hs": "Haskell",
    ".clj": "Clojure",
}

IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", "target", "vendor",
    ".tox", ".mypy_cache", ".pytest_cache", "coverage",
    ".idea", ".vscode", "env", ".env",
}


class LanguageDetector:
    """Detects programming languages in a repository by file extension analysis."""

    def detect(self, repo_path: Path) -> dict[str, any]:
        """Analyze language distribution in a repository.

        Returns:
            Dict with language counts, percentages, and primary language.
        """
        counter: Counter = Counter()
        line_counter: Counter = Counter()
        total_files = 0

        for file_path in self._walk_files(repo_path):
            ext = file_path.suffix.lower()
            lang = LANGUAGE_MAP.get(ext)
            if lang:
                counter[lang] += 1
                total_files += 1
                try:
                    lines = len(file_path.read_text(encoding="utf-8", errors="ignore").splitlines())
                    line_counter[lang] += lines
                except (OSError, UnicodeDecodeError):
                    pass

        if not counter:
            return {"languages": {}, "primary": "Unknown", "total_files": 0}

        total_lines = sum(line_counter.values()) or 1

        languages = {}
        for lang, count in counter.most_common():
            lines = line_counter.get(lang, 0)
            languages[lang] = {
                "files": count,
                "lines": lines,
                "percentage": round((lines / total_lines) * 100, 1),
            }

        primary = counter.most_common(1)[0][0]

        return {
            "languages": languages,
            "primary": primary,
            "total_files": total_files,
            "total_lines": sum(line_counter.values()),
        }

    def _walk_files(self, root: Path):
        """Walk files, skipping ignored directories."""
        for item in root.iterdir():
            if item.name in IGNORE_DIRS:
                continue
            if item.is_dir():
                yield from self._walk_files(item)
            elif item.is_file():
                yield item
