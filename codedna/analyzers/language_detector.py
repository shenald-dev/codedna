"""Language Detector — identifies programming languages used in a repository."""

from __future__ import annotations

import os
from collections import Counter
from pathlib import Path

try:
    MAX_FILE_SIZE = int(os.environ.get("CODEDNA_MAX_FILE_SIZE", 5 * 1024 * 1024))
except ValueError:
<<<<<<< HEAD
=======
    import logging
    logging.getLogger(__name__).warning("Invalid CODEDNA_MAX_FILE_SIZE value. Using default 5MB.")
>>>>>>> origin/master
    MAX_FILE_SIZE = 5 * 1024 * 1024

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
        overall_lines = 0

        for file_path in self._walk_files(repo_path):
            ext = file_path.suffix.lower()
            lang = LANGUAGE_MAP.get(ext)
            if lang:
                counter[lang] += 1
                total_files += 1
                try:
                    with file_path.open("rb") as f:
                        lines = 0
                        last_chunk = b''
                        for chunk in iter(lambda: f.read(65536), b''):
                            lines += chunk.count(b'\n')
                            last_chunk = chunk
                        if last_chunk and not last_chunk.endswith(b'\n'):
                            lines += 1
                    line_counter[lang] += lines
                    overall_lines += lines
                except OSError:
                    pass

        if not counter:
            return {"languages": {}, "primary": "Unknown", "total_files": 0}

        total_lines = overall_lines or 1

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
            "total_lines": overall_lines,
        }

    def _walk_files(self, root: Path):
        """Walk files, skipping ignored directories."""
        stack = [root]
        while stack:
            current = stack.pop()
            try:
                for item in current.iterdir():
                    if item.name in IGNORE_DIRS:
                        continue
                    if item.is_dir():
                        stack.append(item)
                    elif item.is_file():
                        try:
                            if item.stat().st_size <= MAX_FILE_SIZE:
                                yield item
                        except OSError:
                            pass
            except PermissionError:
                pass
