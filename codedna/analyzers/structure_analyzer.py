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
            local_files = 0
            found_markers = []
            for item in items:
                if item.name in IGNORE_DIRS or item.name.startswith("."):
                    continue

                if item.is_dir():
                    total_dirs += 1

                    if current_depth < 3 and current_dict is not None:
                        new_dict = {}
                        current_dict[f"📁 {item.name}/"] = new_dict
                        dirs_to_process.append((item, new_dict, current_depth + 1))
                    else:
                        if current_dict is not None and "..." not in current_dict:
                            current_dict["..."] = None
                        dirs_to_process.append((item, None, current_depth + 1))
                else:
                    total_files += 1
                    local_files += 1

                    if current_depth < 3 and current_dict is not None:
                        current_dict[f"📄 {item.name}"] = None

                    if item.suffix in (".py", ".js", ".ts", ".go", ".rs", ".java"):
                        max_depth = max(max_depth, current_depth)
                        total_depth += current_depth
                        depth_count += 1

                    if item.name in ("__init__.py", "package.json", "go.mod", "Cargo.toml", "build.gradle"):
                        found_markers.append(item.name)

            for marker in found_markers:
                try:
                    module_path = str(current_path.relative_to(repo_path))
                    modules.append({
                        "path": module_path,
                        "marker": marker,
                        "file_count": local_files,
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
