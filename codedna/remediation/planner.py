"""Automated Intelligent Remediation Planner for CodeDNA.

Translates security vulnerabilities, code smells, and quality gate failures
into structured, deterministic, reviewable remediation diffs and patches.
"""

from __future__ import annotations

import difflib
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

IGNORE_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "venv", ".venv", "env",
    "__pycache__", ".pytest_cache", "build", "dist", "target"
}


@dataclass
class RemediationAction:
    rule_id: str
    title: str
    file_path: str
    line_number: int
    severity: str
    description: str
    original_text: str
    proposed_text: str
    unified_diff: str
    autofixable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "file": self.file_path,
            "line": self.line_number,
            "severity": self.severity,
            "description": self.description,
            "original_text": self.original_text,
            "proposed_text": self.proposed_text,
            "diff": self.unified_diff,
            "autofixable": self.autofixable,
            "metadata": self.metadata,
        }


class RemediationPlanner:
    """Analyzes codebase findings and plans safe, deterministic code patches."""

    def __init__(self, repo_path: str | Path = ".") -> None:
        self.repo_path = Path(repo_path).resolve()

    def plan(self, rule_filter: Optional[List[str]] = None) -> List[RemediationAction]:
        """Scans the repository and produces prioritized remediation proposals."""
        actions: List[RemediationAction] = []

        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

            for fname in files:
                fpath = Path(root) / fname
                rel_path = str(fpath.relative_to(self.repo_path))

                # Python remediations
                if fname.endswith(".py"):
                    actions.extend(self._scan_python_file(fpath, rel_path))

                # Node.js package.json wildcard remediations
                elif fname == "package.json":
                    actions.extend(self._scan_package_json(fpath, rel_path))

        if rule_filter:
            allowed = set(r.upper() for r in rule_filter)
            actions = [a for a in actions if a.rule_id.upper() in allowed]

        actions.sort(key=lambda a: (0 if a.severity == "critical" else 1 if a.severity == "warning" else 2, a.file_path, a.line_number))
        return actions

    def _scan_python_file(self, path: Path, rel_path: str) -> List[RemediationAction]:
        actions: List[RemediationAction] = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines(keepends=True)

            # 1. Bare except: -> except Exception:
            for idx, line in enumerate(lines):
                bare_match = re.search(r"^([ \t]*)except[ \t]*:", line)
                if bare_match:
                    indent = bare_match.group(1)
                    orig_line = line
                    fixed_line = f"{indent}except Exception:\n" if line.endswith("\n") else f"{indent}except Exception:"
                    diff = self._make_diff(orig_line, fixed_line, rel_path, idx + 1)
                    actions.append(RemediationAction(
                        rule_id="SMELL-BARE-EXCEPT",
                        title="Narrow Bare Exception Handler",
                        file_path=rel_path,
                        line_number=idx + 1,
                        severity="warning",
                        description="Bare 'except:' catches system interrupts (KeyboardInterrupt, SystemExit). Narrow to 'except Exception:'.",
                        original_text=orig_line.strip(),
                        proposed_text=fixed_line.strip(),
                        unified_diff=diff,
                        autofixable=True
                    ))

            # 2. Dangerous eval / exec calls with user input or direct strings
            for idx, line in enumerate(lines):
                if re.search(r"\b(eval|exec)\s*\(", line) and not line.strip().startswith("#"):
                    actions.append(RemediationAction(
                        rule_id="SEC-DANGEROUS-DYNAMIC-EXEC",
                        title="Refactor Dynamic Code Execution",
                        file_path=rel_path,
                        line_number=idx + 1,
                        severity="critical",
                        description=f"Direct invocation of {line.strip()[:30]}... allows arbitrary code execution. Refactor to ast.literal_eval or structured parsers.",
                        original_text=line.strip(),
                        proposed_text="# TODO: Replace dynamic execution with safe ast.literal_eval or parser",
                        unified_diff=self._make_diff(line, f"# Refactor dynamic exec: {line}", rel_path, idx + 1),
                        autofixable=False
                    ))

            # 3. High-entropy hardcoded secret assignment
            secret_pattern = re.compile(
                r"^([ \t]*)(?:api_key|secret_key|auth_token|password|access_token)\s*=\s*['\"][A-Za-z0-9_\-+/]{24,}['\"]",
                re.IGNORECASE
            )
            for idx, line in enumerate(lines):
                m = secret_pattern.search(line)
                if m and not line.strip().startswith("#"):
                    indent = m.group(1)
                    var_name = line.split("=")[0].strip()
                    env_var = var_name.upper()
                    orig_line = line
                    fixed_line = f"{indent}{var_name} = os.getenv('{env_var}', '')\n" if line.endswith("\n") else f"{indent}{var_name} = os.getenv('{env_var}', '')"
                    diff = self._make_diff(orig_line, fixed_line, rel_path, idx + 1)
                    actions.append(RemediationAction(
                        rule_id="SEC-HARDCODED-SECRET",
                        title="Extract Hardcoded Secret to Environment Variable",
                        file_path=rel_path,
                        line_number=idx + 1,
                        severity="critical",
                        description=f"Hardcoded sensitive token assigned to {var_name}. Extract to os.getenv('{env_var}').",
                        original_text=orig_line.strip(),
                        proposed_text=fixed_line.strip(),
                        unified_diff=diff,
                        autofixable=True
                    ))

        except Exception as e:
            logger.debug("Failed scanning %s for remediation: %s", path, e)
        return actions

    def _scan_package_json(self, path: Path, rel_path: str) -> List[RemediationAction]:
        actions: List[RemediationAction] = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines(keepends=True)
            for idx, line in enumerate(lines):
                # Pattern: "some-pkg": "*"
                m = re.search(r'([ \t]*"[^"]+"\s*:\s*)"\*"(,?)', line)
                if m:
                    prefix = m.group(1)
                    comma = m.group(2)
                    orig_line = line
                    fixed_line = f'{prefix}"^1.0.0"{comma}\n' if line.endswith("\n") else f'{prefix}"^1.0.0"{comma}'
                    diff = self._make_diff(orig_line, fixed_line, rel_path, idx + 1)
                    actions.append(RemediationAction(
                        rule_id="DEP-WILDCARD-PIN",
                        title="Pin Wildcard Dependency Version",
                        file_path=rel_path,
                        line_number=idx + 1,
                        severity="warning",
                        description="Unrestricted wildcard version '*' exposes builds to supply-chain tampering. Pin to semantic range.",
                        original_text=orig_line.strip(),
                        proposed_text=fixed_line.strip(),
                        unified_diff=diff,
                        autofixable=True
                    ))
        except Exception as e:
            logger.debug("Failed scanning %s for remediation: %s", path, e)
        return actions

    def _make_diff(self, original: str, proposed: str, file_path: str, line_no: int) -> str:
        orig_lines = [original if original.endswith("\n") else original + "\n"]
        prop_lines = [proposed if proposed.endswith("\n") else proposed + "\n"]
        diff = difflib.unified_diff(
            orig_lines,
            prop_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            n=1
        )
        return "".join(diff)

    def apply(self, actions: List[RemediationAction], dry_run: bool = False) -> Dict[str, Any]:
        """Applies autofixable remediation actions to workspace files."""
        autofixable = [a for a in actions if a.autofixable]
        files_modified = set()
        applied_count = 0

        # Group actions by file path
        by_file: Dict[str, List[RemediationAction]] = {}
        for a in autofixable:
            by_file.setdefault(a.file_path, []).append(a)

        for rel_file, file_actions in by_file.items():
            full_path = self.repo_path / rel_file
            if not full_path.exists():
                continue

            try:
                content = full_path.read_text(encoding="utf-8")
                modified_content = content
                file_changed = False

                for act in file_actions:
                    if act.original_text and act.original_text in modified_content:
                        modified_content = modified_content.replace(act.original_text, act.proposed_text, 1)
                        applied_count += 1
                        file_changed = True

                if file_changed:
                    files_modified.add(rel_file)
                    if not dry_run:
                        full_path.write_text(modified_content, encoding="utf-8")

            except Exception as e:
                logger.error("Error applying remediation to %s: %s", rel_file, e)

        return {
            "success": True,
            "dry_run": dry_run,
            "applied_count": applied_count,
            "total_candidates": len(actions),
            "files_modified": sorted(list(files_modified)),
        }
