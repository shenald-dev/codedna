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
PY_METHOD_PATTERN = re.compile(r"^[ \t]*def\s+\w+")
JS_METHOD_PATTERN = re.compile(r"(?:function\s+\w+|=>\s*\{|\b[a-zA-Z_]\w*\s*\([^)]*\)\s*\{)")
JAVA_METHOD_PATTERN = re.compile(r"(?:public|private|protected)\s+\w+\s+\w+\s*\(")
PY_FUNC_START_PATTERN = re.compile(r"^([ \t]*)def\s+(\w+)")


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
                lines = content.splitlines()
                relative = str(file_path.relative_to(repo_path))
            except (OSError, ValueError):
                continue

            # ── Large File ──
            if len(lines) > MAX_FILE_LINES:
                smells.append({
                    "type": "Large File",
                    "severity": "warning" if len(lines) < 1000 else "critical",
                    "file": relative,
                    "detail": f"{len(lines)} lines (threshold: {MAX_FILE_LINES})",
                })

            # ── God Class ──
            if file_path.suffix in (".py", ".java", ".ts", ".js"):
                method_count = self._count_methods(content, file_path.suffix)
                if method_count > GOD_CLASS_METHODS:
                    smells.append({
                        "type": "God Class",
                        "severity": "critical",
                        "file": relative,
                        "detail": f"{method_count} methods detected (threshold: {GOD_CLASS_METHODS})",
                    })

            # ── Long Functions ──
            long_funcs = self._detect_long_functions(content, file_path.suffix)
            for func_name, length in long_funcs:
                smells.append({
                    "type": "Long Function",
                    "severity": "warning",
                    "file": relative,
                    "detail": f"'{func_name}' has {length} lines (threshold: {MAX_FUNCTION_LINES})",
                })

            # ── TODO/FIXME/HACK markers ──
            import bisect
            newline_positions = None
            for match in MARKER_PATTERN.finditer(content):
                if newline_positions is None:
                    newline_positions = [m.start() for m in re.finditer(r'\n', content)]
                line_no = bisect.bisect_right(newline_positions, match.start()) + 1

                line_text = lines[line_no - 1] if line_no <= len(lines) else ""

                smells.append({
                    "type": "Code Marker",
                    "severity": "info",
                    "file": f"{relative}:{line_no}",
                    "detail": f"{match.group(1).upper()} found: {line_text.strip()[:80]}",
                })

        # ── Large Modules ──
        modules = self._detect_large_modules(repo_path)
        for mod_path, count in modules:
            smells.append({
                "type": "Large Module",
                "severity": "warning",
                "file": mod_path,
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
            return sum(1 for line in content.splitlines() if PY_METHOD_PATTERN.match(line))
        elif ext in (".js", ".ts", ".jsx", ".tsx"):
            return len(JS_METHOD_PATTERN.findall(content))
        elif ext == ".java":
            return len(JAVA_METHOD_PATTERN.findall(content))
        return 0

    def _detect_long_functions(self, content: str, ext: str) -> list[tuple[str, int]]:
        """Detect functions exceeding the line threshold."""
        results = []

        if ext == ".py":
            lines = content.splitlines()
            for i, line in enumerate(lines):
                match = PY_FUNC_START_PATTERN.match(line)
                if match:
                    indent = len(match.group(1))
                    name = match.group(2)
                    # Count lines until next function or class at same/lower indent
                    func_lines = 0
                    for j in range(i + 1, len(lines)):
                        inner_line = lines[j]
                        stripped = inner_line.lstrip()
                        if stripped and len(inner_line) - len(stripped) <= indent and (
                            stripped.startswith("def ") or stripped.startswith("class ")
                        ):
                            break
                        func_lines += 1
                    if func_lines > MAX_FUNCTION_LINES:
                        results.append((name, func_lines))

        return results

    def _detect_large_modules(self, repo_path: Path) -> list[tuple[str, int]]:
        """Find directories with too many files."""
        results = []
        for item in self._walk_dirs(repo_path):
            file_count = sum(1 for f in item.iterdir() if f.is_file())
            if file_count > LARGE_MODULE_FILES:
                try:
                    rel = str(item.relative_to(repo_path))
                    results.append((rel, file_count))
                except ValueError:
                    pass
        return results

    def _walk_dirs(self, root: Path):
        """Walk directories, skipping ignored directories."""
        stack = [root]
        while stack:
            current = stack.pop()
            try:
                for item in current.iterdir():
                    if item.name in IGNORE_DIRS:
                        continue
                    if item.is_dir():
                        yield item
                        stack.append(item)
            except PermissionError:
                pass

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
