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
        tree = {}
        modules = []
        max_depth = 0
        total_depth = 0
        depth_count = 0
        total_dirs = 0
        total_files = 0

        stack = [(repo_path, tree, 0)]
        while stack:
            current_path, current_dict, current_depth = stack.pop()

            try:
                items = sorted(current_path.iterdir(), key=lambda p: (p.is_file(), p.name))
            except PermissionError:
                continue

            dirs_to_process = []
            file_count = None
                            modules.append({
                                "path": module_path,
                                "marker": item.name,
                                "file_count": cached_file_count,
                            })
                        except ValueError:
                            pass

            stack.extend(reversed(dirs_to_process))

        return {
            "tree": tree,
            "modules": modules,
            "max_depth": max_depth,
            "avg_depth": round(total_depth / depth_count, 1) if depth_count > 0 else 0,
            "total_dirs": total_dirs,
            "total_files": total_files,
        }
