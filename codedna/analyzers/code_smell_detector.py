"""Code Smell Detector — identifies structural design problems in codebases."""

from __future__ import annotations

import re
from pathlib import Path

from .language_detector import IGNORE_DIRS

# Thresholds
MAX_FILE_LINES = 500
MAX_FUNCTION_LINES = 80
GOD_CLASS_METHODS = 15
LARGE_MODULE_FILES = 20

# Pre-compiled Regular Expressions for performance
MARKER_PATTERN = re.compile(r"(TODO|FIXME|HACK|XXX|todo|fixme|hack|xxx|Todo|Fixme|Hack|Xxx)")
PY_METHOD_PATTERN = re.compile(r"^[ \t]*def\s+\w+", re.MULTILINE)
JS_METHOD_PATTERN = re.compile(r"function\s+\w+|=>\s*\{|[a-zA-Z_]\w*\s*\([^)]*\)\s*\{")
JAVA_METHOD_PATTERN = re.compile(r"(?:public|private|protected)\s+\w+\s+\w+\s*\(")


class CodeSmellDetector:
    """Detects common code smells and structural issues."""

    def detect(self, repo_path: Path) -> dict:
        """Scan for code smells in the repository.

        Returns:
            Dict with categorized smells and severity ratings.
        """
        smells: list[dict] = []

        for file_path in self._walk_source(repo_path):
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                relative = str(file_path.relative_to(repo_path))
            except (OSError, ValueError):
                continue

            # ── Large File ──
            line_count = content.count('\n') + 1
            if line_count > MAX_FILE_LINES:
                smells.append({
                    "type": "Large File",
                    "severity": "warning" if line_count < 1000 else "critical",
                    "file": relative,
                    "line": 1,
                    "detail": f"{line_count} lines (threshold: {MAX_FILE_LINES})",
                })

            # ── God Class ──
            if file_path.suffix in (".py", ".java", ".ts", ".js"):
                method_count = self._count_methods(content, file_path.suffix)
                if method_count > GOD_CLASS_METHODS:
                    smells.append({
                        "type": "God Class",
                        "severity": "critical",
                        "file": relative,
                        "line": 1,
                        "detail": f"{method_count} methods detected (threshold: {GOD_CLASS_METHODS})",  # noqa: E501
                    })

            # ── Long Functions ──
            long_funcs = self._detect_long_functions(content, file_path.suffix)
            for func_name, length, start_line in long_funcs:
                smells.append({
                    "type": "Long Function",
                    "severity": "warning",
                    "file": relative,
                    "line": start_line,
                    "detail": f"'{func_name}' has {length} lines (threshold: {MAX_FUNCTION_LINES})",
                })

            # ── TODO/FIXME/HACK markers ──
            last_idx = 0
            current_line = 1
            for match in MARKER_PATTERN.finditer(content):
                start_idx = match.start()
                current_line += content.count('\n', last_idx, start_idx)
                last_idx = start_idx

                line_start = content.rfind('\n', 0, start_idx) + 1
                line_end = content.find('\n', start_idx)
                if line_end == -1:
                    line_end = len(content)
                line_text = content[line_start:line_end]

                smells.append({
                    "type": "Code Marker",
                    "severity": "info",
                    "file": f"{relative}:{current_line}",
                    "line": current_line,
                    "detail": f"{match.group(1).upper()} found: {line_text.strip()[:80]}",
                })

        # ── Large Modules ──
        modules = self._detect_large_modules(repo_path)
        for mod_path, count in modules:
            smells.append({
                "type": "Large Module",
                "severity": "warning",
                "file": mod_path,
                "line": 1,
                "detail": f"{count} files in module (threshold: {LARGE_MODULE_FILES})",
            })

        # Summary
        severity_counts = {"critical": 0, "warning": 0, "info": 0}
        for smell in smells:
            severity_counts[smell["severity"]] += 1

        return {
            "smells": smells,
            "total": len(smells),
            "severity_counts": severity_counts,
            "health_score": self._compute_health(severity_counts),
        }

    def _count_methods(self, content: str, ext: str) -> int:
        """Count method/function definitions in a file."""
        if ext == ".py":
            return len(PY_METHOD_PATTERN.findall(content))
        elif ext in (".js", ".ts", ".jsx", ".tsx"):
            return len(JS_METHOD_PATTERN.findall(content))
        elif ext == ".java":
            return len(JAVA_METHOD_PATTERN.findall(content))
        return 0

    def _detect_long_functions(self, content: str, ext: str) -> list[tuple[str, int, int]]:
        """Detect functions exceeding the line threshold."""
        results = []

        if ext == ".py":
            active_funcs = []
            pattern = re.compile(r"^[ \t]*(def\s+(\w+)|class\s+\w+)", re.MULTILINE)

            last_idx = 0
            current_line = 0

            for match in pattern.finditer(content):
                start_idx = match.start()

                # count newlines between last match and this match
                current_line += content.count('\n', last_idx, start_idx)
                last_idx = start_idx

                # find indent
                j = start_idx
                while j < len(content) and content[j] in ' \t':
                    j += 1
                indent = j - start_idx

                is_def = match.group(1).startswith("def")

                while active_funcs and active_funcs[-1][0] >= indent:
                    _, prev_name, prev_start = active_funcs.pop()
                    func_lines = current_line - prev_start - 1
                    if func_lines > MAX_FUNCTION_LINES:
                        results.append((prev_name, func_lines, prev_start + 1))

                if is_def:
                    name = match.group(2)
                    active_funcs.append((indent, name, current_line))

            if active_funcs:
                total_lines = current_line + content.count('\n', last_idx)
                if content and not content.endswith('\n'):
                    total_lines += 1

                for _, name, start in active_funcs:
                    func_lines = total_lines - start - 1
                    if func_lines > MAX_FUNCTION_LINES:
                        results.append((name, func_lines, start + 1))

        return results

    def _detect_large_modules(self, repo_path: Path) -> list[tuple[str, int]]:
        """Find directories with too many files."""
        results = []
        stack = [repo_path]
        while stack:
            current = stack.pop()
            try:
                file_count = 0
                for item in current.iterdir():
                    if item.name in IGNORE_DIRS:
                        continue
                    if item.is_dir():
                        stack.append(item)
                    elif item.is_file():
                        file_count += 1

                if file_count > LARGE_MODULE_FILES and current != repo_path:
                    try:
                        rel = str(current.relative_to(repo_path))
                        results.append((rel, file_count))
                    except ValueError:
                        pass
            except PermissionError:
                pass
        return results

    def _compute_health(self, counts: dict) -> str:
        """Compute overall health score."""
        if counts["critical"] > 5:
            return "Critical"
        elif counts["critical"] > 0 or counts["warning"] > 10:
            return "Needs Attention"
        elif counts["warning"] > 3:
            return "Fair"
        return "Healthy"

    def _walk_source(self, root: Path):
        source_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".rb"}
        stack = [root]
        while stack:
            current = stack.pop()
            try:
                for item in current.iterdir():
                    if item.name in IGNORE_DIRS:
                        continue
                    if item.is_dir():
                        stack.append(item)
                    elif item.is_file() and item.suffix.lower() in source_exts:
                        yield item
            except PermissionError:
                pass
