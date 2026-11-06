"""Complexity Analyzer — computes Cyclomatic Complexity, Cognitive Complexity, and Maintainability Index."""

from __future__ import annotations

import ast
import math
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .language_detector import IGNORE_DIRS

if TYPE_CHECKING:
    from codedna.config import CodeDNAConfig

MAX_FILE_SIZE = int(os.environ.get("CODEDNA_MAX_FILE_SIZE", 5 * 1024 * 1024))

# Heuristic patterns for non-Python languages (anchored to prevent ReDoS)
FUNC_PATTERNS = {
    ".js": re.compile(
        r"^[ \t]*(?:function\s+([A-Za-z0-9_$]+)|(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)",
        re.MULTILINE,
    ),
    ".ts": re.compile(
        r"^[ \t]*(?:function\s+([A-Za-z0-9_$]+)|(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|(?:(?:public|private|protected|async|static|readonly)\s+)*([A-Za-z0-9_$]+)\s*\([^)]*\)\s*:\s*[A-Za-z0-9_$<>]+\s*\{)",
        re.MULTILINE,
    ),
    ".go": re.compile(r"^[ \t]*func\s+(?:\([^)]+\)\s+)?([A-Za-z0-9_]+)\s*\(", re.MULTILINE),
    ".java": re.compile(
        r"^[ \t]*(?:(?:public|private|protected|static|final|synchronized)\s+)+[\w<>\[\]]+\s+([A-Za-z0-9_]+)\s*\([^)]*\)\s*\{",
        re.MULTILINE,
    ),
    ".rs": re.compile(r"^[ \t]*(?:pub\s+)?fn\s+([A-Za-z0-9_]+)\s*(?:<[^>]+>)?\s*\(", re.MULTILINE),
}

BRANCH_TOKEN_PATTERN = re.compile(r"\b(?:if|else\s+if|for|while|catch|case)\b|&&|\|\||\?")


@dataclass
class FunctionComplexity:
    """Complexity metrics for an individual function or method."""

    name: str
    file: str
    line: int
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    severity: str  # "normal" | "warning" | "critical"

    def to_dict(self) -> dict:
        return asdict(self)


class PyComplexityVisitor(ast.NodeVisitor):
    """AST visitor that computes Cyclomatic and Cognitive complexity for Python functions."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.functions: list[FunctionComplexity] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._analyze_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._analyze_function(node)
        self.generic_visit(node)

    def _analyze_function(self, func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        name = func_node.name
        line = func_node.lineno
        end_line = getattr(func_node, "end_lineno", line + 1)
        loc = max(1, end_line - line + 1)

        # 1. Cyclomatic Complexity (McCabe)
        # Base complexity is 1
        cc = 1
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                cc += 1
            elif isinstance(node, ast.ExceptHandler):
                cc += 1
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                cc += 1
            elif isinstance(node, ast.Assert):
                cc += 1
            elif isinstance(node, ast.IfExp):  # ternary
                cc += 1
            elif isinstance(node, ast.BoolOp):
                cc += len(node.values) - 1
            elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                cc += len(node.generators)
            elif hasattr(ast, "Match") and isinstance(node, ast.Match):
                cc += len(node.cases)

        # 2. Cognitive Complexity (Sonarsource definition)
        cognitive = self._compute_cognitive_complexity(func_node)

        # Severity determination
        if cc > 20 or cognitive > 25:
            severity = "critical"
        elif cc > 10 or cognitive > 15:
            severity = "warning"
        else:
            severity = "normal"

        self.functions.append(
            FunctionComplexity(
                name=name,
                file=self.filename,
                line=line,
                lines_of_code=loc,
                cyclomatic_complexity=cc,
                cognitive_complexity=cognitive,
                severity=severity,
            )
        )

    def _compute_cognitive_complexity(self, func_node: ast.AST) -> int:
        """Calculate cognitive complexity penalizing nesting depth and control structures."""
        score = 0
        stack: list[tuple[ast.AST, int]] = [(func_node, 0)]
        max_depth = 120

        while stack:
            current_node, nesting = stack.pop()
            if nesting > max_depth:
                continue

            for child in ast.iter_child_nodes(current_node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    score += 1 + nesting
                    stack.append((child, nesting + 1))
                elif isinstance(child, ast.ExceptHandler):
                    score += 1 + nesting
                    stack.append((child, nesting + 1))
                elif isinstance(child, ast.IfExp):
                    score += 1 + nesting
                    stack.append((child, nesting + 1))
                elif isinstance(child, ast.BoolOp):
                    score += 1
                    stack.append((child, nesting))
                else:
                    stack.append((child, nesting))

        return score


class ComplexityAnalyzer:
    """Analyzes source files for Cyclomatic Complexity, Cognitive Complexity, and Maintainability Index."""

    def analyze_file(self, file_path: Path, relative_path: str = "", content: str | None = None) -> list[FunctionComplexity]:
        """Analyze a single source file and return function complexities."""
        rel = relative_path or str(file_path)
        ext = file_path.suffix.lower()

        if content is None:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                return []

        if ext == ".py":
            try:
                tree = ast.parse(content, filename=rel)
                visitor = PyComplexityVisitor(filename=rel)
                visitor.visit(tree)
                return visitor.functions
            except (SyntaxError, ValueError, RecursionError, MemoryError):
                return []

        # Heuristic analysis for other supported languages
        if ext in FUNC_PATTERNS:
            return self._heuristic_analyze(content, rel, ext)

        return []

    def _heuristic_analyze(self, content: str, relative_path: str, ext: str) -> list[FunctionComplexity]:
        """Heuristic complexity scanner for non-Python source files."""
        pattern = FUNC_PATTERNS[ext]
        results: list[FunctionComplexity] = []

        last_idx = 0
        current_line = 1

        for match in pattern.finditer(content):
            start_idx = match.start()
            current_line += content.count('\n', last_idx, start_idx)
            last_idx = start_idx

            # Extract first non-empty capture group
            func_name = next((g for g in match.groups() if g), f"function_L{current_line}")

            # Approximate function scope: scan until matching closing brace or next 80 lines
            end_idx = start_idx
            line_count = 0
            while line_count < 80 and end_idx != -1:
                end_idx = content.find('\n', end_idx + 1)
                line_count += 1

            if end_idx == -1:
                end_idx = len(content)

            block_text = content[start_idx:end_idx]
            branches = len(BRANCH_TOKEN_PATTERN.findall(block_text))
            cc = max(1, branches + 1)
            cognitive = max(0, int(branches * 1.2))

            severity = "normal"
            if cc > 20 or cognitive > 25:
                severity = "critical"
            elif cc > 10 or cognitive > 15:
                severity = "warning"

            loc = content.count('\n', start_idx, end_idx) + 1
            if content[start_idx:end_idx].endswith('\n'):
                loc -= 1

            results.append(
                FunctionComplexity(
                    name=func_name,
                    file=relative_path,
                    line=current_line,
                    lines_of_code=max(1, loc),
                    cyclomatic_complexity=cc,
                    cognitive_complexity=cognitive,
                    severity=severity,
                )
            )

        return results

    def analyze(self, repo_path: Path, config: CodeDNAConfig | None = None) -> dict:
        """Run repository-wide complexity assessment.

        Returns:
            Dictionary with aggregated metrics, function listings, and maintainability index.
        """
        all_functions: list[FunctionComplexity] = []
        file_mi_list: list[float] = []
        total_files = 0
        supported_exts = {".py", ".js", ".ts", ".go", ".java", ".rs"}

        stack = [repo_path]
        while stack:
            current = stack.pop()
            try:
                for item in current.iterdir():
                    if item.name in IGNORE_DIRS or item.name.startswith(".git") or item.is_symlink():
                        continue
                    if item.is_dir():
                        stack.append(item)
                    elif item.is_file() and item.suffix.lower() in supported_exts:
                        try:
                            rel = str(item.relative_to(repo_path))
                            if config and config.is_path_ignored(rel):
                                continue
                            if item.stat().st_size <= MAX_FILE_SIZE:
                                content = item.read_text(encoding="utf-8", errors="ignore")
                                file_loc = max(1, content.count("\n") + 1)
                                total_files += 1

                                funcs = self.analyze_file(item, relative_path=rel, content=content)
                                all_functions.extend(funcs)

                                # Per-file maintainability index
                                file_avg_cc = (sum(f.cyclomatic_complexity for f in funcs) / len(funcs)) if funcs else 1.0
                                file_vol = max(1.0, float(file_loc * 5))
                                mi_raw = 171.0 - (5.2 * math.log(file_vol)) - (0.23 * file_avg_cc) - (16.2 * math.log(file_loc))
                                mi_file_scaled = max(0.0, min(100.0, (mi_raw / 171.0) * 100.0))
                                file_mi_list.append(mi_file_scaled)
                        except (OSError, ValueError):
                            pass
            except PermissionError:
                pass

        if not all_functions:
            return {
                "total_functions_analyzed": 0,
                "average_cyclomatic_complexity": 1.0,
                "max_cyclomatic_complexity": 1,
                "average_cognitive_complexity": 0.0,
                "max_cognitive_complexity": 0,
                "maintainability_index": 100.0,
                "maintainability_rank": "A",
                "complex_functions": [],
            }

        cc_values = [f.cyclomatic_complexity for f in all_functions]
        cog_values = [f.cognitive_complexity for f in all_functions]
        avg_cc = round(sum(cc_values) / len(cc_values), 2)
        max_cc = max(cc_values)
        avg_cog = round(sum(cog_values) / len(cog_values), 2)
        max_cog = max(cog_values)

        # Average Maintainability Index across source files
        mi_scaled = round(sum(file_mi_list) / max(1, len(file_mi_list)), 1) if file_mi_list else 100.0

        if mi_scaled >= 35.0:
            rank = "A"
        elif mi_scaled >= 25.0:
            rank = "B"
        elif mi_scaled >= 15.0:
            rank = "C"
        elif mi_scaled >= 10.0:
            rank = "D"
        else:
            rank = "F"

        # Filter complex functions
        complex_list = [
            f.to_dict()
            for f in sorted(all_functions, key=lambda x: (x.cyclomatic_complexity + x.cognitive_complexity), reverse=True)
            if f.severity in ("warning", "critical")
        ]

        return {
            "total_functions_analyzed": len(all_functions),
            "average_cyclomatic_complexity": avg_cc,
            "max_cyclomatic_complexity": max_cc,
            "average_cognitive_complexity": avg_cog,
            "max_cognitive_complexity": max_cog,
            "maintainability_index": mi_scaled,
            "maintainability_rank": rank,
            "complex_functions": complex_list[:25],
        }
