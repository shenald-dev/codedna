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
                        "detail": f"{method_count} methods detected (threshold: {GOD_CLASS_METHODS})",  # noqa: E501
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

                # Extract just the matched line directly to avoid full splitlines()
                start_idx = 0 if line_no == 1 else newline_positions[line_no - 2] + 1
                end_idx = (
                    newline_positions[line_no - 1]
                    if line_no <= len(newline_positions) else len(content)
                )
                line_text = content[start_idx:end_idx]

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
            return sum(1 for _ in PY_METHOD_PATTERN.finditer(content))
        elif ext in (".js", ".ts", ".jsx", ".tsx"):
            return sum(1 for _ in JS_METHOD_PATTERN.finditer(content))
        elif ext == ".java":
            return sum(1 for _ in JAVA_METHOD_PATTERN.finditer(content))
        return 0

    def _detect_long_functions(self, content: str, ext: str) -> list[tuple[str, int]]:
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
                        results.append((prev_name, func_lines))

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
