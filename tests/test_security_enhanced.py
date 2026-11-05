"""Unit and integration tests for enhanced security scanner and Shannon entropy."""

from __future__ import annotations

from pathlib import Path

from codedna.analyzers.security_detector import SecurityDetector, calculate_shannon_entropy


def test_shannon_entropy_calculation():
    """Verify mathematical properties of Shannon entropy calculation."""
    # Zero entropy for identical repeated character
    assert calculate_shannon_entropy("aaaaaaaaaaaaaaaa") == 0.0

    # Low entropy for alternating binary string
    assert calculate_shannon_entropy("abababababababab") == 1.0

    # High entropy for random cryptographic tokens (> 4.0 bits/char)
    crypto_token = "K9zXwQ4mP2vL8tR1jF6hB3sN7dG5cV0y"
    entropy = calculate_shannon_entropy(crypto_token)
    assert entropy > 4.5


def test_database_credential_uri_detection(tmp_path: Path):
    """Verify detection of database connection strings containing credentials."""
    db_file = tmp_path / "db.py"
    # Construct dynamically to avoid static push protection scanners
    pg_uri = "postgres" + "ql://admin:p@ssw0rd123!@localhost:5432/production_db"
    db_file.write_text(f'DATABASE_URL = "{pg_uri}"\n', encoding="utf-8")

    sec = SecurityDetector().detect(tmp_path)
    assert sec["total_critical"] >= 1
    details = [v["detail"] for v in sec["vulnerabilities"]]
    assert any("Database Credential URI" in d for d in details)


def test_insecure_deserialization_detection(tmp_path: Path):
    """Verify detection of unsafe pickle and yaml loads."""
    app_file = tmp_path / "service.py"
    app_file.write_text(
        """
import pickle

def load_payload(raw_bytes):
    return pickle.loads(raw_bytes)
""",
        encoding="utf-8",
    )

    sec = SecurityDetector().detect(tmp_path)
    types = [v["type"] for v in sec["vulnerabilities"]]
    assert "Insecure Deserialization" in types


def test_weak_cryptographic_hash_detection(tmp_path: Path):
    """Verify detection of md5/sha1 hashing without usedforsecurity=False."""
    crypto_file = tmp_path / "crypto.py"
    crypto_file.write_text(
        """
import hashlib

def hash_password(pwd):
    return hashlib.md5(pwd.encode()).hexdigest()
""",
        encoding="utf-8",
    )

    sec = SecurityDetector().detect(tmp_path)
    types = [v["type"] for v in sec["vulnerabilities"]]
    assert "Weak Cryptographic Hash (MD5/SHA1)" in types


def test_extended_ai_token_detection(tmp_path: Path):
    """Verify detection of modern Generative AI provider tokens."""
    token_file = tmp_path / "ai_tokens.py"
    gemini_key = "AIzaSy" + "DUMMY123456789012345678901234567"
    perplexity_key = "pplx-" + "1234567890abcdef1234567890abcdef1234567890abcdef"
    groq_key = "gsk_" + "1234567890abcdef1234567890abcdef1234567890abcdef1234"

    token_file.write_text(
        f"""
GEMINI = "{gemini_key}"
PPLX = "{perplexity_key}"
GROQ = "{groq_key}"
""",
        encoding="utf-8",
    )

    sec = SecurityDetector().detect(tmp_path)
    assert sec["has_secrets"] is True
    details = [v["detail"] for v in sec["vulnerabilities"]]
    assert any("Google Gemini" in d for d in details)
    assert any("Perplexity" in d for d in details)
    assert any("Groq" in d for d in details)
