"""Dependency Mapper — parses import statements and builds a dependency graph."""

from __future__ import annotations

import itertools
import os
import re
from pathlib import Path

import networkx as nx

from .language_detector import IGNORE_DIRS

import logging

try:
    MAX_FILE_SIZE = int(os.environ.get("CODEDNA_MAX_FILE_SIZE", 5 * 1024 * 1024))
except ValueError:
    logging.warning("Invalid CODEDNA_MAX_FILE_SIZE environment variable. Falling back to 5MB.")
    MAX_FILE_SIZE = 5 * 1024 * 1024

# Import patterns per language
IMPORT_PATTERNS: dict[str, list[re.Pattern]] = {
    "Python": [
        re.compile(r"^[ \t]*import\s+([\w.]+)", re.MULTILINE),
        re.compile(r"^[ \t]*from\s+([\w.]+)\s+import", re.MULTILINE),
    ],
    "JavaScript": [
        re.compile(r"""import\s+.*?\s+from\s+['"]([^'"]+)['"]""", re.MULTILINE),
        re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""", re.MULTILINE),
    ],
    "TypeScript": [
        re.compile(r"""import\s+.*?\s+from\s+['"]([^'"]+)['"]""", re.MULTILINE),
        re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""", re.MULTILINE),
    ],
    "Go": [
        re.compile(r'"([^"]+)"', re.MULTILINE),
    ],
    "Java": [
        re.compile(r"^[ \t]*import\s+([\w.]+);", re.MULTILINE),
    ],
    "Rust": [
        re.compile(r"^[ \t]*use\s+([\w:]+)", re.MULTILINE),
        re.compile(r"^[ \t]*extern\s+crate\s+(\w+)", re.MULTILINE),
    ],
}

LANG_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".java": "Java",
    ".rs": "Rust",
}


class DependencyMapper:
    """Parses imports across source files and builds a NetworkX dependency graph."""

    def map(self, repo_path: Path) -> dict:
        """Build dependency map for the repository.

        Note: The betweenness centrality metric uses an approximation (k=50)
        to ensure high-performance execution on large dependency graphs at the
        trade-off of exact accuracy for less central nodes.

        Returns:
            Dict with graph stats, edges, and centrality metrics.
        """
        graph = nx.DiGraph()

        for file_path in self._walk_source(repo_path):
            ext = file_path.suffix.lower()
            lang = LANG_EXTENSIONS.get(ext)
            if not lang or lang not in IMPORT_PATTERNS:
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            relative = str(file_path.relative_to(repo_path))
            module_name = self._to_module(relative)
            graph.add_node(module_name)

            for pattern in IMPORT_PATTERNS[lang]:
                for dep in pattern.findall(content):
                    # Skip stdlib / external packages (heuristic: no dots for local)
                    if dep.startswith(".") or "/" in dep:
                        dep = self._normalize_import(dep)
                    graph.add_edge(module_name, dep)

        # Compute centrality metrics
        centrality = {}
        if len(graph.nodes) > 0:
            try:
                pr = nx.pagerank(graph)
                bc = nx.betweenness_centrality(graph, k=min(50, len(graph.nodes)), seed=42)
                centrality = {
                    node: {
                        "pagerank": round(pr.get(node, 0), 4),
                        "betweenness": round(bc.get(node, 0), 4),
                    }
                    for node in sorted(pr, key=pr.get, reverse=True)[:10]
                }
            except Exception:
                pass

        # Detect circular dependencies
        try:
            cycles = list(itertools.islice(nx.simple_cycles(graph), 10))
        except Exception:
            cycles = []

        return {
            "total_modules": len(graph.nodes),
            "total_edges": len(graph.edges),
            "density": round(nx.density(graph), 4) if len(graph.nodes) > 1 else 0,
            "cycles": [list(c) for c in cycles[:10]],
            "has_circular_deps": len(cycles) > 0,
            "top_central_modules": centrality,
            "edges": [{"from": u, "to": v} for u, v in itertools.islice(graph.edges, 100)],
        }

    def build_mermaid(self, dependencies: dict) -> str:
        """Generate a Mermaid diagram of the dependency graph from pre-computed data."""
        lines = ["graph LR"]

        seen = set()
        for edge in dependencies.get("edges", [])[:30]:  # Limit for readability
            src = edge["from"].replace(".", "_").replace("/", "_")
            tgt = edge["to"].replace(".", "_").replace("/", "_")
            key = f"{src}->{tgt}"
            if key not in seen:
                lines.append(f"    {src} --> {tgt}")
                seen.add(key)

        return "\n".join(lines)

    def _walk_source(self, root: Path):
        stack = [root]
        while stack:
            current = stack.pop()
            try:
                for item in current.iterdir():
                    if item.name in IGNORE_DIRS:
                        continue
                    if item.is_dir():
                        stack.append(item)
                    elif item.is_file() and item.suffix.lower() in LANG_EXTENSIONS:
                        try:
                            if item.stat().st_size <= MAX_FILE_SIZE:
                                yield item
                        except OSError:
                            pass
            except PermissionError:
                pass

    def _to_module(self, path: str) -> str:
        return path.replace("\\", "/").rsplit(".", 1)[0]

    def _normalize_import(self, dep: str) -> str:
        if dep.startswith("./") or dep.startswith("../"):
            return dep.lstrip("./")
        return dep
