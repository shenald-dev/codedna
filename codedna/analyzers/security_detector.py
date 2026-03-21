"""Security & Vulnerability Scanner — detects hardcoded secrets and risky patterns."""

from __future__ import annotations

import re
from pathlib import Path

from .language_detector import IGNORE_DIRS

SECRET_PATTERNS = {
    "AWS Access Key": re.compile(r"(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}"),
    "Generic API Key / Token": re.compile(r"['\"]([0-9a-zA-Z\-_]{20,})['\"]"),
    "RSA Private Key": re.compile(r"-----BEGIN RSA PRIVATE KEY-----"),
    "SSH Private Key": re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----"),
    "GitHub Token": re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36}"),
    "Stripe Secret Key": re.compile(r"sk_live_[0-9a-zA-Z]{24}"),
    "Slack Token": re.compile(r"xox[baprs]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}"),
    "Google API Key": re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
}

GENERIC_PREFIX_PATTERN = re.compile(r"(?i)(?:key|token|secret|password|pw)[\s:=]+$")


class SecurityDetector:
    """Scans codebase for security vulnerabilities and hardcoded secrets."""

    def detect(self, repo_path: Path) -> dict:
        """Scan repository for security issues.

        Returns:
            Dict containing detected secrets and vulnerabilities.
        """
        vulnerabilities = []

        for file_path in self._walk_source(repo_path):
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                relative = str(file_path.relative_to(repo_path))
            except (OSError, ValueError):
                continue

            # Check for secrets
            for secret_type, pattern in SECRET_PATTERNS.items():
                for match in pattern.finditer(content):
                    if secret_type == "Generic API Key / Token":
                        # Verify left context for generic keys
                        left_context = content[max(0, match.start() - 30):match.start()]
                        if not GENERIC_PREFIX_PATTERN.search(left_context):
                            continue

                        # Extract the actual token from the capture group
                        matched_value = match.group(1)
                    else:
                        matched_value = match.group(0)

                    # To avoid printing real secrets, we truncate/mask the matched value
                    if len(matched_value) > 10:
                        masked = f"{matched_value[:4]}***{matched_value[-4:]}"
                    else:
                        masked = "***"

                    # Get line number approximation
                    line_no = content.count('\n', 0, match.start()) + 1

                    vulnerabilities.append({
                        "type": "Hardcoded Secret",
                        "severity": "critical",
                        "file": f"{relative}:{line_no}",
                        "detail": f"Detected {secret_type} ({masked})",
                    })

        return {
            "vulnerabilities": vulnerabilities,
            "total_critical": len([v for v in vulnerabilities if v["severity"] == "critical"]),
            "has_secrets": len([v for v in vulnerabilities if v["type"] == "Hardcoded Secret"]) > 0,
        }

    def _walk_source(self, root: Path):
        stack = [root]
        while stack:
            current = stack.pop()
            try:
                for item in current.iterdir():
                    if item.name in IGNORE_DIRS or item.name.startswith(".git"):
                        continue
                    if item.is_dir():
                        stack.append(item)
                    elif item.is_file():
                        # Skip known binary/media/data files
                        if item.suffix.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".tar", ".gz", ".sqlite", ".db"):
                            yield item
            except PermissionError:
                pass
