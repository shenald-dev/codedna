"""Tests for CodeDNA CLI commands 'diff' and 'check'."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from codedna.cli import main


def test_cli_diff_with_json_files(tmp_path: Path):
    profile_a = {
        "metadata": {"source": "repo-a", "analyzed_at": "2026-10-31T00:00:00Z"},
        "signature": "LANG:PYT | ARCH:MON | SIZE:SM",
        "system_type": "Monolith",
        "languages": {"languages": {"Python": {"percentage": 100.0, "files": 5, "lines": 500}}},
        "architecture": {"primary_pattern": "Monolith", "traits": ["Tested"]},
        "structure_stats": {"total_files": 5, "total_dirs": 1, "modules": 1, "max_depth": 1},
        "dependencies": {"total_modules": 1, "total_edges": 0, "density": 0.0, "has_circular_deps": False},
        "health": {"overall": "Healthy", "severity_counts": {"critical": 0, "warning": 0, "info": 0}},
        "security": {"has_secrets": False, "total_critical": 0, "vulnerabilities": []},
        "developer_genome": {"total_contributors": 1, "bus_factor": 1},
        "evolution": {"total_commits": 10},
    }

    file_a = tmp_path / "profile_a.json"
    file_b = tmp_path / "profile_b.json"
    file_a.write_text(json.dumps(profile_a), encoding="utf-8")
    file_b.write_text(json.dumps(profile_a), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["diff", str(file_a), str(file_b)])

    assert result.exit_code == 0
    assert "CodeDNA Genetic Drift & Mutation Diff" in result.output
    assert "100.0%" in result.output
    assert "Identical Genome" in result.output


def test_cli_diff_markdown_export(tmp_path: Path):
    profile = {
        "metadata": {"source": "repo", "analyzed_at": "2026-10-31T00:00:00Z"},
        "system_type": "Layered",
        "languages": {"languages": {}},
        "architecture": {},
        "structure_stats": {},
        "dependencies": {},
        "health": {"overall": "Healthy", "severity_counts": {}},
        "security": {"has_secrets": False},
        "developer_genome": {},
        "evolution": {},
    }
    file_path = tmp_path / "p.json"
    file_path.write_text(json.dumps(profile), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["diff", str(file_path), str(file_path), "--format", "markdown"])

    assert result.exit_code == 0
    assert "# 🧬 CodeDNA Genetic Drift & Mutation Diff" in result.output


def test_cli_check_passing_profile(tmp_path: Path):
    clean_profile = {
        "metadata": {"source": "clean-repo", "analyzed_at": "2026-10-31T00:00:00Z"},
        "system_type": "Modular",
        "health": {"overall": "Healthy", "severity_counts": {"critical": 0, "warning": 1, "info": 2}},
        "dependencies": {"total_modules": 3, "total_edges": 2, "density": 0.1, "has_circular_deps": False},
        "security": {"has_secrets": False, "total_critical": 0, "vulnerabilities": []},
    }
    file_path = tmp_path / "clean.json"
    file_path.write_text(json.dumps(clean_profile), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["check", str(file_path), "--min-health", "Fair"])

    assert result.exit_code == 0
    assert "PASSED" in result.output
    assert "All architecture and quality gates passed" in result.output


def test_cli_check_failing_exit_code(tmp_path: Path):
    degraded_profile = {
        "metadata": {"source": "degraded-repo", "analyzed_at": "2026-10-31T00:00:00Z"},
        "system_type": "Monolith",
        "health": {"overall": "Critical", "severity_counts": {"critical": 5, "warning": 10, "info": 2}},
        "dependencies": {"total_modules": 3, "total_edges": 2, "density": 0.1, "has_circular_deps": True},
        "security": {"has_secrets": True, "total_critical": 2, "vulnerabilities": []},
    }
    file_path = tmp_path / "degraded.json"
    file_path.write_text(json.dumps(degraded_profile), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["check", str(file_path), "--min-health", "Healthy", "--fail-on-secrets"])

    assert result.exit_code == 1
    assert "FAILED" in result.output
    assert "Quality gate breach" in result.output


def test_cli_check_sarif_file_export(tmp_path: Path):
    profile = {
        "metadata": {"source": "repo", "analyzed_at": "2026-10-31T00:00:00Z"},
        "system_type": "Modular",
        "health": {"overall": "Healthy", "severity_counts": {"critical": 0, "warning": 0, "info": 0}},
        "dependencies": {"has_circular_deps": False},
        "security": {"has_secrets": False, "total_critical": 0, "vulnerabilities": []},
    }
    json_path = tmp_path / "repo.json"
    sarif_output = tmp_path / "results.sarif"
    json_path.write_text(json.dumps(profile), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["check", str(json_path), "--format", "sarif", "--output", str(sarif_output)])

    assert result.exit_code == 0
    assert sarif_output.exists()
    sarif_data = json.loads(sarif_output.read_text(encoding="utf-8"))
    assert sarif_data["version"] == "2.1.0"
    assert sarif_data["runs"][0]["tool"]["driver"]["name"] == "CodeDNA Gatekeeper"
