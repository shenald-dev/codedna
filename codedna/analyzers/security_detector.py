"""Security & Vulnerability Scanner — detects hardcoded secrets and risky patterns."""

from __future__ import annotations

import json
import logging
import math
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

from .language_detector import IGNORE_DIRS

if TYPE_CHECKING:
    from codedna.config import CodeDNAConfig

try:
    MAX_FILE_SIZE = int(os.environ.get("CODEDNA_MAX_FILE_SIZE", 5 * 1024 * 1024))
except ValueError:
    logging.getLogger(__name__).warning("Invalid CODEDNA_MAX_FILE_SIZE value. Using default 5MB.")
    MAX_FILE_SIZE = 5 * 1024 * 1024

def calculate_shannon_entropy(text: str) -> float:
    """Compute Shannon Entropy H(S) = -sum(p * log2(p)) for credential detection."""
    if not text:
        return 0.0
    length = len(text)
    counts: dict[str, int] = {}
    for char in text:
        counts[char] = counts.get(char, 0) + 1
    entropy = 0.0
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 3)

SECRET_PATTERNS = {
    "AWS Access Key": re.compile(r"((?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16})"),
    "Generic API Key / Token": re.compile(r"(?:[Kk]ey|[Tt]oken|[Ss]ecret|[Pp]assword|[Pp]w|[Aa]uth|KEY|TOKEN|SECRET|PASSWORD|PW|AUTH)[-\s_:=]+['\"]([0-9a-zA-Z\-_]{20,})['\"]"),  # noqa: E501
    "OpenAI / LLM Key": re.compile(r"(sk-[A-Za-z0-9_-]{32,})"),
    "Anthropic API Key": re.compile(r"(sk-ant-[A-Za-z0-9_-]{32,})"),
    "Hugging Face Token": re.compile(r"(hf_[A-Za-z0-9]{30,})"),
    "Pinecone API Key": re.compile(r"(pcsk_[A-Za-z0-9_]{30,})"),
    "RSA Private Key": re.compile(r"-----BEGIN " + r"RSA PRIVATE KEY-----"),
    "SSH Private Key": re.compile(r"-----BEGIN " + r"OPENSSH PRIVATE KEY-----"),
    "GitHub Token": re.compile(r"((?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36})"),
    "Stripe Secret Key": re.compile(r"(sk_" + r"live_[0-9a-zA-Z]{24})"),
    "Slack Token": re.compile(r"(xox[baprs]-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24})"),
    "Google Gemini / AI Studio Key": re.compile(r"(AIzaSy[0-9A-Za-z\-_]{30,35})"),
    "Google API Key": re.compile(r"(AIza(?!Sy)[0-9A-Za-z\-_]{35})"),
    "Cohere API Key": re.compile(r"(co_[0-9a-zA-Z]{40})"),
    "Mistral API Key": re.compile(r"(mis_[0-9a-zA-Z]{32})"),
    "Perplexity API Key": re.compile(r"(pplx-[0-9a-zA-Z]{48})"),
    "DeepSeek API Key": re.compile(r"(sk-[0-9a-f]{32})"),
    "Groq API Key": re.compile(r"(gsk_[0-9a-zA-Z]{52})"),
    "Database Credential URI": re.compile(r"""((?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp):\/\/[^:\s'"]+:([^@\s'"]+)@[^\s'"]+)""", re.IGNORECASE),
    "Discord Bot Token": re.compile(r"[MND][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}"),
    "SendGrid API Key": re.compile(r"SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}"),
    "MailChimp API Key": re.compile(r"[0-9a-f]{32}-us[0-9]{1,2}"),
}

VULN_PATTERNS = {
    "Command Injection Risk": (re.compile(r"subprocess\.(?:call|Popen|run)\s*\([^)]*?shell\s*=\s*True[^)]*\)", re.IGNORECASE), "shell=True"),
    "Raw SQL String Injection": (re.compile(r'''f["']SELECT[^{}\n]+?WHERE[^{}\n]+?\{[^}]+\}''', re.IGNORECASE), "SELECT"),
    "Insecure Deserialization": (re.compile(r"(?:pickle\.(?:loads|load)|_pickle\.(?:loads|load)|yaml\.load\([^)]*?Loader\s*=\s*(?:yaml\.)?Loader|marshal\.loads)"), "pickle"),
    "Path Traversal Risk": (re.compile(r"(?:open|file)\s*\([^)]*?(?:request\.|params\[|req\.query|user_input)"), "open"),
    "Weak Cryptographic Hash (MD5/SHA1)": (re.compile(r"hashlib\.(?:md5|sha1)\s*\(\s*(?!\s*usedforsecurity\s*=\s*False)"), "hashlib"),
}

SECRET_HINTS = {
    "AWS Access Key": ("AKIA", "ABIA", "ACCA", "ASIA"),
    "Generic API Key / Token": ("key", "token", "secret", "password", "pw", "auth", "KEY", "TOKEN", "SECRET", "PASSWORD", "PW", "AUTH", "Key", "Token", "Secret", "Password", "Pw", "Auth"),
    "OpenAI / LLM Key": ("sk-",),
    "Anthropic API Key": ("sk-ant-",),
    "Hugging Face Token": ("hf_",),
    "Pinecone API Key": ("pcsk_",),
    "RSA Private Key": ("-----BEGIN " + "RSA PRIVATE KEY-----",),
    "SSH Private Key": ("-----BEGIN " + "OPENSSH PRIVATE KEY-----",),
    "GitHub Token": ("ghp_", "gho_", "ghu_", "ghs_", "ghr_"),
    "Stripe Secret Key": ("sk_" + "live_",),
    "Slack Token": ("xox",),
    "Google API Key": ("AIza",),
    "Google Gemini / AI Studio Key": ("AIzaSy",),
    "Cohere API Key": ("co_",),
    "Mistral API Key": ("mis_",),
    "Perplexity API Key": ("pplx-",),
    "DeepSeek API Key": ("sk-",),
    "Groq API Key": ("gsk_",),
    "Database Credential URI": ("://",),
    "SendGrid API Key": ("SG.",),
    "MailChimp API Key": ("-us",),
}

# String literal token pattern for entropy analysis
QUOTED_TOKEN_PATTERN = re.compile(r"""['"]([A-Za-z0-9+/=_-]{24,100})['"]""")


class SecurityDetector:
    """Scans codebase for security vulnerabilities and hardcoded secrets."""

    def __init__(self, config: CodeDNAConfig | None = None) -> None:
        self.config = config

    def detect(self, repo_path: Path, config: CodeDNAConfig | None = None) -> dict:
        """Scan repository for security issues.

        Returns:
            Dict containing detected secrets and vulnerabilities.
        """
        active_config = config or self.config
        vulnerabilities = []

        for file_path in self._walk_source(repo_path):
            try:
                relative = str(file_path.relative_to(repo_path))
                if active_config and active_config.is_path_ignored(relative):
                    continue
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except (OSError, ValueError):
                continue

            # Check for secrets
            self._scan_secrets(content, relative, active_config, vulnerabilities)

            # Check for code injection vulnerabilities in source code files
            source_code_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".rb", ".php", ".c", ".cpp"}
            if file_path.suffix.lower() in source_code_exts:
                self._scan_injections(content, relative, vulnerabilities)

            # Check for high-entropy secret candidates via Shannon entropy (skip lockfiles)
            is_lockfile = file_path.name in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "uv.lock", "poetry.lock")
            if not is_lockfile:
                self._scan_entropy(content, relative, active_config, vulnerabilities)

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

    def _scan_secrets(self, content: str, relative: str, active_config: CodeDNAConfig | None, vulnerabilities: list) -> None:
        """Scan file content for predefined secret patterns."""
        for secret_type, pattern in SECRET_PATTERNS.items():
            hints = SECRET_HINTS.get(secret_type)
            if hints and not any(hint in content for hint in hints):
                continue

            last_idx = 0
            current_line = 1
            for match in pattern.finditer(content):
                matched_value = match.group(0)
                if active_config and active_config.is_secret_whitelisted(matched_value):
                    continue

                if len(matched_value) > 10:
                    masked = f"{matched_value[:4]}***{matched_value[-4:]}"
                else:
                    masked = "***"

                start_idx = match.start()
                current_line += content.count('\n', last_idx, start_idx)
                last_idx = start_idx

                vulnerabilities.append({
                    "type": "Hardcoded Secret",
                    "severity": "critical",
                    "file": f"{relative}:{current_line}",
                    "detail": f"Detected {secret_type} ({masked})",
                })

    def _scan_injections(self, content: str, relative: str, vulnerabilities: list) -> None:
        """Scan source code for dangerous dynamic execution and injection patterns."""
        for vuln_type, (v_pattern, v_hint) in VULN_PATTERNS.items():
            if v_hint in content:
                last_idx = 0
                current_line = 1
                for match in v_pattern.finditer(content):
                    start_idx = match.start()
                    current_line += content.count('\n', last_idx, start_idx)
                    last_idx = start_idx
                    vulnerabilities.append({
                        "type": vuln_type,
                        "severity": "critical",
                        "file": f"{relative}:{current_line}",
                        "detail": f"Insecure dynamic execution vector: {vuln_type}",
                    })

    def _scan_entropy(self, content: str, relative: str, active_config: CodeDNAConfig | None, vulnerabilities: list) -> None:
        """Scan string literals for high Shannon entropy candidate tokens."""
        for match in QUOTED_TOKEN_PATTERN.finditer(content):
            candidate = match.group(1)
            if len(candidate) >= 28 and not candidate.startswith(("data:", "http", "sha256-", "sha512-", "file:", "assets/", "urn:", "git+")):
                entropy = calculate_shannon_entropy(candidate)
                if entropy >= 4.6:
                    if active_config and active_config.is_secret_whitelisted(candidate):
                        continue
                    masked = f"{candidate[:4]}***{candidate[-4:]}"
                    already_flagged = any(masked in v.get("detail", "") for v in vulnerabilities if v.get("file", "").startswith(relative))
                    if not already_flagged:
                        start_idx = match.start()
                        line_num = content.count('\n', 0, start_idx) + 1
                        vulnerabilities.append({
                            "type": "High-Entropy Secret Candidate",
                            "severity": "warning",
                            "file": f"{relative}:{line_num}",
                            "detail": f"High Shannon entropy token ({entropy:.2f} bits/char, {masked})",
                        })

    def _walk_source(self, root: Path):
        stack = [root]
        while stack:
            current = stack.pop()
            try:
                for item in current.iterdir():
                    if item.name in IGNORE_DIRS or item.name.startswith(".git") or item.is_symlink():
                        continue
                    if item.is_dir():
                        stack.append(item)
                    elif item.is_file():
                        if item.suffix.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".tar", ".gz", ".sqlite", ".db"):  # noqa: E501
                            try:
                                if item.stat().st_size <= MAX_FILE_SIZE:
                                    yield item
                            except OSError:
                                pass
            except PermissionError:
                pass

    def _check_package_manifest(self, content: str, relative: str, vulnerabilities: list):
        """Scans package.json for known bad practices or dangerous dependencies."""
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
