"""Unit and integration tests for CodeDNA v1.3.0 CLI additions (audit, complexity, mcp)."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from codedna.cli import main


def test_cli_version():
    """Verify codedna --version reports v1.3.0."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "1.3.0" in result.output


def test_cli_audit_clean_repo(tmp_path: Path):
    """Verify codedna audit runs and exits 0 on a clean repository."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("def hello():\n    return 'world'\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["audit", str(tmp_path)])
    assert result.exit_code == 0
    assert "Audit Scorecard" in result.output
    assert "Audit Completed: PASSED" in result.output


def test_cli_audit_detects_security_breach(tmp_path: Path):
    """Verify codedna audit exits 1 when a critical vulnerability is present."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "insecure.py").write_text(
        """
import subprocess
def execute(cmd):
    return subprocess.Popen(cmd, shell=True)
""",
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(main, ["audit", str(tmp_path)])
    assert result.exit_code == 1
    assert "POLICY BREACH" in result.output
    assert "Command Injection Risk" in result.output


def test_cli_complexity_command(tmp_path: Path):
    """Verify codedna complexity command displays metrics and function table."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "complex.py").write_text(
        """
def complex_calc(x):
    if x > 1:
        if x > 2:
            if x > 3:
                return x * 3
    return 0
""",
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(main, ["complexity", str(tmp_path)])
    assert result.exit_code == 0
    assert "Maintainability Index" in result.output
    assert "Average Cyclomatic Complexity" in result.output
    assert "Functions Analyzed" in result.output
