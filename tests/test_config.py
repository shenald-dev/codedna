"""Tests for CodeDNA configuration engine."""

from __future__ import annotations

from pathlib import Path

from codedna.config import CodeDNAConfig, generate_default_config_toml, load_config


def test_default_config():
    """Verify default configuration values."""
    config = CodeDNAConfig()
    assert config.min_health == "Fair"
    assert config.max_critical_smells == 0
    assert config.max_smells is None
    assert config.fail_on_secrets is True
    assert config.fail_on_circular is False
    assert config.ignore_paths == []
    assert config.whitelisted_secrets == []
    assert config.max_file_lines == 500
    assert config.max_function_lines == 80
    assert config.god_class_methods == 15
    assert config.large_module_files == 20
    assert config.gate is config
    assert config.smells is config


def test_path_ignoring():
    """Verify path pattern matching."""
    config = CodeDNAConfig(ignore_paths=["tests/*", "vendor/**", "*.generated.py", "docs/"])
    assert config.is_path_ignored("tests/test_foo.py") is True
    assert config.is_path_ignored("tests\\sub\\test_bar.py") is True
    assert config.is_path_ignored("src/models.generated.py") is True
    assert config.is_path_ignored("src/app.py") is False


def test_secret_whitelisting():
    """Verify secret whitelisting matching."""
    config = CodeDNAConfig(whitelisted_secrets=["sk_test_*", "PUBLIC_KEY", "dummy_token"])
    assert config.is_secret_whitelisted("sk_test_12345") is True
    assert config.is_secret_whitelisted("dummy_token") is True
    assert config.is_secret_whitelisted("sk_live_12345") is False


def test_load_config_codedna_toml(tmp_path: Path):
    """Verify loading from codedna.toml."""
    toml_content = """
    ignore_paths = ["fixtures/*", "test_*.py"]
    whitelisted_secrets = ["example_secret"]

    [gate]
    min_health = "Healthy"
    max_critical_smells = 2
    max_smells = 25
    fail_on_secrets = false
    fail_on_circular = true
    max_drift = 15.0

    [smells]
    max_file_lines = 350
    max_function_lines = 60
    god_class_methods = 12
    large_module_files = 15
    """
    (tmp_path / "codedna.toml").write_text(toml_content, encoding="utf-8")
    cfg = load_config(tmp_path)

    assert cfg.min_health == "Healthy"
    assert cfg.max_critical_smells == 2
    assert cfg.max_smells == 25
    assert cfg.fail_on_secrets is False
    assert cfg.fail_on_circular is True
    assert cfg.max_drift == 15.0
    assert "fixtures/*" in cfg.ignore_paths
    assert "example_secret" in cfg.whitelisted_secrets
    assert cfg.max_file_lines == 350
    assert cfg.max_function_lines == 60
    assert cfg.god_class_methods == 12
    assert cfg.large_module_files == 15


def test_load_config_pyproject_toml(tmp_path: Path):
    """Verify loading from pyproject.toml [tool.codedna]."""
    toml_content = """
    [tool.codedna]
    ignore_paths = ["build/*"]

    [tool.codedna.gate]
    min_health = "Needs Attention"
    max_critical_smells = 5
    """
    (tmp_path / "pyproject.toml").write_text(toml_content, encoding="utf-8")
    cfg = load_config(tmp_path)

    assert cfg.min_health == "Needs Attention"
    assert cfg.max_critical_smells == 5
    assert "build/*" in cfg.ignore_paths


def test_generate_default_config_toml():
    """Verify default toml generation produces parseable content."""
    content = generate_default_config_toml()
    assert "CodeDNA Configuration" in content
    assert "[gate]" in content
    assert "[smells]" in content
