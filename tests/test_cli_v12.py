"""Tests for CodeDNA v1.2.0 CLI additions (init, gate, PR markdown)."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from codedna.analyzers.code_smell_detector import CodeSmellDetector
from codedna.cli import main


def test_cli_init_command(tmp_path: Path):
    """Verify codedna init creates starter configuration file."""
    runner = CliRunner()
    result = runner.invoke(main, ["init", str(tmp_path)])
    assert result.exit_code == 0
    config_file = tmp_path / "codedna.toml"
    assert config_file.exists()
    content = config_file.read_text(encoding="utf-8")
    assert "[gate]" in content
    assert "[smells]" in content

    # Running again without --force should warn
    result2 = runner.invoke(main, ["init", str(tmp_path)])
    assert result2.exit_code == 0
    assert "already exists" in result2.output

    # Running with --force should succeed
    result3 = runner.invoke(main, ["init", str(tmp_path), "--force"])
    assert result3.exit_code == 0
    assert "Initialized CodeDNA configuration" in result3.output


def test_cli_gate_command_pass(tmp_path: Path):
    """Verify codedna gate exits 0 on compatible profiles."""
    profile_a = {
        "metadata": {"source": "baseline", "analyzed_at": "2026-10-31T00:00:00Z"},
        "system_type": "Modular",
        "languages": {"languages": {"Python": {"files": 5, "lines": 500, "percentage": 100.0}}},
        "structure": {"total_files": 5, "total_directories": 1, "avg_file_length": 100},
        "dependencies": {"total_modules": 3, "total_edges": 2, "has_circular_deps": False, "density": 0.1},
        "architecture": {"primary_pattern": "Layered"},
        "health": {"overall": "Healthy", "severity_counts": {"critical": 0, "warning": 1, "info": 1}},
        "security": {"has_secrets": False, "total_critical": 0, "vulnerabilities": []},
        "developers": {"bus_factor": 2, "total_contributors": 2},
        "evolution": {"commit_velocity": 4.0, "code_churn": 50},
    }
    profile_b = dict(profile_a)

    path_a = tmp_path / "base.json"
    path_b = tmp_path / "target.json"
    path_a.write_text(json.dumps(profile_a), encoding="utf-8")
    path_b.write_text(json.dumps(profile_b), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["gate", str(path_a), str(path_b)])
    assert result.exit_code == 0
    assert "PASSED" in result.output


def test_cli_gate_command_fail_and_markdown(tmp_path: Path):
    """Verify codedna gate exits 1 on regression and outputs Markdown."""
    profile_a = {
        "metadata": {"source": "baseline", "analyzed_at": "2026-10-31T00:00:00Z"},
        "system_type": "Modular",
        "languages": {"languages": {"Python": {"files": 5, "lines": 500, "percentage": 100.0}}},
        "structure": {"total_files": 5, "total_directories": 1, "avg_file_length": 100},
        "dependencies": {"total_modules": 3, "total_edges": 2, "has_circular_deps": False, "density": 0.1},
        "architecture": {"primary_pattern": "Layered"},
        "health": {"overall": "Healthy", "severity_counts": {"critical": 0, "warning": 0, "info": 0}},
        "security": {"has_secrets": False, "total_critical": 0, "vulnerabilities": []},
        "developers": {"bus_factor": 2, "total_contributors": 2},
        "evolution": {"commit_velocity": 4.0, "code_churn": 50},
    }
    # Degraded profile with introduced circular deps and secrets
    profile_b = dict(profile_a)
    profile_b["health"] = {"overall": "Critical", "severity_counts": {"critical": 4, "warning": 2, "info": 0}}
    profile_b["dependencies"] = {"total_modules": 3, "total_edges": 2, "has_circular_deps": True, "density": 0.1}
    profile_b["security"] = {"has_secrets": True, "total_critical": 2, "vulnerabilities": []}

    path_a = tmp_path / "base.json"
    path_b = tmp_path / "target.json"
    out_md = tmp_path / "drift_gate.md"
    path_a.write_text(json.dumps(profile_a), encoding="utf-8")
    path_b.write_text(json.dumps(profile_b), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["gate", str(path_a), str(path_b), "--format", "markdown", "--output", str(out_md)])
    assert result.exit_code == 1
    assert out_md.exists()
    content = out_md.read_text(encoding="utf-8")
    assert "Drift Regression Gate" in content
    assert "FAILED" in content


def test_cli_check_markdown_format(tmp_path: Path):
    """Verify codedna check --format markdown outputs GitHub PR table."""
    profile = {
        "metadata": {"source": "my-repo", "analyzed_at": "2026-10-31T00:00:00Z"},
        "system_type": "Modular",
        "health": {"overall": "Healthy", "severity_counts": {"critical": 0, "warning": 1, "info": 2}},
        "dependencies": {"has_circular_deps": False},
        "security": {"has_secrets": False, "total_critical": 0, "vulnerabilities": []},
    }
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(profile), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["check", str(path), "--format", "markdown"])
    assert result.exit_code == 0
    assert "CodeDNA Quality Gatekeeper" in result.output
    assert "PASSED" in result.output
    assert "| Rule ID | Policy | Severity | Status | Message |" in result.output


def test_spaghetti_hub_smell_detection(tmp_path: Path):
    """Verify Spaghetti Hub excessive import coupling smell."""
    hub_file = tmp_path / "hub.py"
    imports = "\n".join([f"import module_{i}" for i in range(18)])
    hub_file.write_text(f"{imports}\n\ndef process():\n    pass\n", encoding="utf-8")

    smells = CodeSmellDetector().detect(tmp_path)
    types = [s["type"] for s in smells["smells"]]
    assert "Spaghetti Hub Node" in types
