"""Tests for expanded security detection in CodeDNA."""

from __future__ import annotations

from pathlib import Path

from codedna.analyzers.security_detector import SecurityDetector
from codedna.config import CodeDNAConfig


def test_detect_ai_api_tokens(tmp_path: Path):
    """Verify detection of modern AI & LLM provider tokens."""
    # Build tokens dynamically to avoid static push protection triggers
    openai_key = "sk-" + "proj-" + "abc123456789012345678901234567890"
    anthropic_key = "sk-ant-" + "api03-" + "xyz123456789012345678901234567890"
    hf_key = "hf_" + "qwertyuiopasdfghjklzxcvbnm123456"
    pinecone_key = "pcsk_" + "0987654321fedcba0987654321fedcba"

    test_file = tmp_path / "keys.py"
    test_file.write_text(
        f"""
OPENAI_KEY = "{openai_key}"
ANTHROPIC_KEY = "{anthropic_key}"
HF_TOKEN = "{hf_key}"
PINECONE_KEY = "{pinecone_key}"
""",
        encoding="utf-8",
    )

    detector = SecurityDetector()
    results = detector.detect(tmp_path)

    assert results["has_secrets"] is True
    assert results["total_critical"] >= 4
    details = [v.get("detail", "") for v in results["vulnerabilities"]]
    assert any("OpenAI" in d for d in details)
    assert any("Anthropic" in d for d in details)
    assert any("Hugging Face" in d for d in details)
    assert any("Pinecone" in d for d in details)


def test_detect_command_injection(tmp_path: Path):
    """Verify detection of insecure shell=True executions."""
    test_file = tmp_path / "runner.py"
    test_file.write_text(
        """
import subprocess

def run_user_cmd(cmd):
    return subprocess.Popen(cmd, shell=True)
""",
        encoding="utf-8",
    )

    detector = SecurityDetector()
    results = detector.detect(tmp_path)

    vuln_types = [v["type"] for v in results["vulnerabilities"]]
    assert "Command Injection Risk" in vuln_types


def test_detect_sql_injection(tmp_path: Path):
    """Verify detection of direct f-string SQL query execution."""
    test_file = tmp_path / "database.py"
    test_file.write_text(
        """
def get_user(db, user_id):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    return db.execute(query)
""",
        encoding="utf-8",
    )

    detector = SecurityDetector()
    results = detector.detect(tmp_path)

    vuln_types = [v["type"] for v in results["vulnerabilities"]]
    assert "Raw SQL String Injection" in vuln_types


def test_security_with_config_whitelist(tmp_path: Path):
    """Verify secrets can be whitelisted or paths ignored via config."""
    dummy_key = "sk-" + "proj-" + "allowedkey123456789012345678901234"

    test_file = tmp_path / "mock_keys.py"
    test_file.write_text(
        f"""
MOCK_KEY = "{dummy_key}"
""",
        encoding="utf-8",
    )

    # Without whitelist: detected
    res1 = SecurityDetector().detect(tmp_path)
    assert res1["has_secrets"] is True

    # With whitelist: suppressed
    cfg = CodeDNAConfig(whitelisted_secrets=["*allowedkey*"])
    res2 = SecurityDetector(config=cfg).detect(tmp_path)
    assert res2["has_secrets"] is False

    # With path ignore: suppressed
    cfg_ignore = CodeDNAConfig(ignore_paths=["mock_keys.py"])
    res3 = SecurityDetector(config=cfg_ignore).detect(tmp_path)
    assert res3["has_secrets"] is False
