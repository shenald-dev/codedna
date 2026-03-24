"""Security & Vulnerability Scanner — detects hardcoded secrets and risky patterns."""

from __future__ import annotations

import re
from pathlib import Path

from .language_detector import IGNORE_DIRS

SECRET_PATTERNS = {
    "AWS Access Key": re.compile(r"((?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16})"),
    "Generic API Key / Token": re.compile(r"(?:key|token|secret|password|pw|auth)[-\s_:=]+['\"]([0-9a-zA-Z\-_]{20,})['\"]", re.IGNORECASE),
    "RSA Private Key": re.compile(r"-----BEGIN RSA PRIVATE KEY-----"),
    "SSH Private Key": re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----"),
    "GitHub Token": re.compile(r"((?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36})"),
    "Stripe Secret Key": re.compile(r"(sk_live_[0-9a-zA-Z]{24})"),
    "Slack Token": re.compile(r"(xox[baprs]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24})"),
    "Google API Key": re.compile(r"(AIza[0-9A-Za-z\-_]{35})"),
    "Discord Bot Token": re.compile(r"[MND][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}"),
    "SendGrid API Key": re.compile(r"SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}"),
    "MailChimp API Key": re.compile(r"[0-9a-f]{32}-us[0-9]{1,2}"),
}


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
                    # To avoid printing real secrets, we truncate/mask the matched value
                    matched_value = match.group(0)
                    if len(matched_value) > 10:
                        masked = f"{matched_value[:4]}***{matched_value[-4:]}"
                    else:
                        masked = "***"

                    # Get line number approximation
                    line_no = content[:match.start()].count('\n') + 1

                    vulnerabilities.append({
                        "type": "Hardcoded Secret",
                        "severity": "critical",
                        "file": f"{relative}:{line_no}",
                        "detail": f"Detected {secret_type} ({masked})",
                    })

            # Check dependency manifests for outdated or naive flags
            if file_path.name == "package.json":
                self._check_package_manifest(content, relative, vulnerabilities)
            elif file_path.name == "requirements.txt":
                self._check_requirements(content, relative, vulnerabilities)

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

    def _check_package_manifest(self, content: str, relative: str, vulnerabilities: list):
        """Scans package.json for known bad practices or dangerous dependencies."""
        import json
        try:
            data = json.loads(content)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "node-ipc" in deps and "10" in str(deps["node-ipc"]):
                vulnerabilities.append({
                    "type": "Vulnerable Dependency",
                    "severity": "critical",
                    "file": relative,
                    "detail": "node-ipc heavily compromised version detected."
                })
            # Check for overly broad wildcard resolutions
            for pkg, ver in deps.items():
                if ver == "*":
                    vulnerabilities.append({
                        "type": "Security Risk",
                        "severity": "warning",
                        "file": relative,
                        "detail": f"Dependency '{pkg}' uses unrestricted version wildcard '*'"
                    })
        except Exception:
            pass

    def _check_requirements(self, content: str, relative: str, vulnerabilities: list):
        """Scans requirements.txt for outdated known flags."""
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            line = line.strip().lower()
            if line.startswith("django<2") or line.startswith("django==") and "1." in line:
                vulnerabilities.append({
                    "type": "Vulnerable Dependency",
                    "severity": "critical",
                    "file": f"{relative}:{idx + 1}",
                    "detail": "Extremely outdated Django version detected."
                })
