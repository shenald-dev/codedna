"""Integration tests for CodeDNA v1.4 CLI features (SBOM and Remediation)."""

import json
from pathlib import Path

from click.testing import CliRunner

from codedna.cli import main


def test_cli_sbom_cyclonedx(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("pytest>=8.0.0\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["sbom", str(tmp_path), "--format", "cyclonedx"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["bomFormat"] == "CycloneDX"
    assert data["specVersion"] == "1.5"


def test_cli_sbom_spdx_file_output(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("pytest>=8.0.0\n", encoding="utf-8")
    out_file = tmp_path / "out_sbom.json"

    runner = CliRunner()
    result = runner.invoke(main, ["sbom", str(tmp_path), "--format", "spdx", "-o", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["spdxVersion"] == "SPDX-2.3"


def test_cli_remediate_preview(tmp_path: Path):
    py_file = tmp_path / "demo.py"
    py_file.write_text("try:\n    pass\nexcept:\n    pass\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["remediate", str(tmp_path), "--dry-run", "--apply"])
    assert result.exit_code == 0
    assert "SMELL-BARE-EXCEPT" in result.output
    assert "DRY-RUN PREVIEW" in result.output
    # verify file untouched
    assert "except:" in py_file.read_text(encoding="utf-8")


def test_cli_fix_alias_live_apply(tmp_path: Path):
    py_file = tmp_path / "demo.py"
    py_file.write_text("try:\n    pass\nexcept:\n    pass\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["fix", str(tmp_path)])
    assert result.exit_code == 0
    assert "APPLIED" in result.output
    # verify file patched
    assert "except Exception:" in py_file.read_text(encoding="utf-8")


def test_cli_audit_with_sbom_and_remediation_summary(tmp_path: Path):
    py_file = tmp_path / "safe.py"
    py_file.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["audit", str(tmp_path)])
    assert result.exit_code == 0
    assert "Supply Chain (SBOM)" in result.output
    assert "Remediation Potential" in result.output
