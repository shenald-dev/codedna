"""Structure Analyzer — builds a file tree and detects module boundaries."""

from __future__ import annotations

from pathlib import Path

from .language_detector import IGNORE_DIRS


class StructureAnalyzer:
    """Analyzes the directory structure of a repository."""

    def analyze(self, repo_path: Path) -> dict:
        """Build structural analysis of the repository.

        Returns:
            Dict with file tree, depth stats, module boundaries, and top-level layout.
        """
        tree = self._build_tree(repo_path, repo_path)
        modules = self._detect_modules(repo_path)
        depth_stats = self._compute_depth(repo_path, repo_path)

        return {
            "tree": tree,
            "modules": modules,
            "max_depth": max(depth_stats) if depth_stats else 0,
            "avg_depth": round(sum(depth_stats) / len(depth_stats), 1) if depth_stats else 0,
            "total_dirs": sum(1 for _ in repo_path.rglob("*") if _.is_dir() and _.name not in IGNORE_DIRS),
            "total_files": sum(1 for _ in self._walk(repo_path) if _.is_file()),
        }

    def _build_tree(self, path: Path, root: Path, max_depth: int = 3, current: int = 0) -> dict:
        """Build a nested dict representing the file tree (limited depth)."""
        if current >= max_depth:
            return {"...": None}

        result = {}
        try:
            items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        except PermissionError:
            return result

        for item in items:
            if item.name in IGNORE_DIRS or item.name.startswith("."):
                continue
            if item.is_dir():
                result[f"📁 {item.name}/"] = self._build_tree(item, root, max_depth, current + 1)
            else:
                result[f"📄 {item.name}"] = None

        return result

    def _detect_modules(self, repo_path: Path) -> list[dict]:
        """Detect module boundaries — directories with __init__.py or package.json."""
        modules = []
        for path in self._walk(repo_path):
            if path.is_dir():
                continue
            if path.name in ("__init__.py", "package.json", "go.mod", "Cargo.toml", "build.gradle"):
                module_path = str(path.parent.relative_to(repo_path))
                file_count = sum(1 for f in path.parent.iterdir() if f.is_file())
                modules.append({
                    "path": module_path,
                    "marker": path.name,
                    "file_count": file_count,
                })
        return modules

    def _compute_depth(self, path: Path, root: Path) -> list[int]:
        """Compute nesting depth of all source files."""
        depths = []
        for item in self._walk(path):
            if item.is_file() and item.suffix in (".py", ".js", ".ts", ".go", ".rs", ".java"):
                try:
                    depth = len(item.relative_to(root).parts) - 1
                    depths.append(depth)
                except ValueError:
                    pass
        return depths

    def _walk(self, root: Path):
        """Walk files, skipping ignored directories."""
        for item in root.iterdir():
            if item.name in IGNORE_DIRS:
                continue
            if item.is_dir():
                yield from self._walk(item)
            else:
                yield item
