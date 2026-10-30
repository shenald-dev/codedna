"""Tests for CodeDNA CI Gatekeeper & Policy Enforcement."""

from __future__ import annotations

import json

import pytest

from codedna.ci.gatekeeper import Gatekeeper


@pytest.fixture
def clean_profile():
    return {
        "metadata": {
            "source": "codedna-clean",
            "analyzed_at": "2026-10-31T00:00:00Z",
        },
        "system_type": "Modular",
        "health": {
            "overall": "Healthy",
            "severity_counts": {"critical": 0, "warning": 2, "info": 4},
        },
        "dependencies": {
            "total_modules": 5,
            "total_edges": 6,
            "density": 0.12,
            "has_circular_deps": False,
            "circular_count": 0,
        },
        "security": {
            "has_secrets": False,
            "total_critical": 0,
            "vulnerabilities": [],
        },
    }


class TestGatekeeper:
    def test_clean_profile_passes_all_gates(self, clean_profile):
        gatekeeper = Gatekeeper(min_health="Fair", fail_on_secrets=True, max_critical_smells=0)
        result = gatekeeper.evaluate(clean_profile)

        assert result.passed is True
        assert result.policies_failed == 0
        assert result.overall_health == "Healthy"

    def test_health_threshold_breach(self, clean_profile):
        clean_profile["health"]["overall"] = "Needs Attention"
        gatekeeper = Gatekeeper(min_health="Fair")
        result = gatekeeper.evaluate(clean_profile)

        assert result.passed is False
        assert any(e.rule_id == "DNA-HLT-001" and not e.passed for e in result.evaluations)

    def test_secrets_breach(self, clean_profile):
        clean_profile["security"]["has_secrets"] = True
        clean_profile["security"]["total_critical"] = 1
        clean_profile["security"]["vulnerabilities"] = [
            {"type": "Hardcoded Secret", "severity": "critical", "file": "config.py:42", "detail": "Detected AWS Access Key"}
        ]
        gatekeeper = Gatekeeper(fail_on_secrets=True)
        result = gatekeeper.evaluate(clean_profile)

        assert result.passed is False
        assert any(e.rule_id == "DNA-SEC-001" and not e.passed for e in result.evaluations)

    def test_circular_dependency_gate(self, clean_profile):
        clean_profile["dependencies"]["has_circular_deps"] = True
        clean_profile["dependencies"]["circular_count"] = 1

        # Ignored when fail_on_circular is False
        gk_lenient = Gatekeeper(fail_on_circular=False)
        assert gk_lenient.evaluate(clean_profile).passed is True

        # Fails when fail_on_circular is True
        gk_strict = Gatekeeper(fail_on_circular=True)
        res_strict = gk_strict.evaluate(clean_profile)
        assert res_strict.passed is False
        assert any(e.rule_id == "DNA-DEP-001" and not e.passed for e in res_strict.evaluations)

    def test_max_smells_threshold(self, clean_profile):
        clean_profile["health"]["severity_counts"]["critical"] = 2
        gatekeeper = Gatekeeper(max_critical_smells=0)
        result = gatekeeper.evaluate(clean_profile)

        assert result.passed is False
        assert any(e.rule_id == "DNA-SML-001" and not e.passed for e in result.evaluations)

    def test_sarif_v2_generation(self, clean_profile):
        clean_profile["security"]["vulnerabilities"] = [
            {"type": "Hardcoded Secret", "severity": "critical", "file": "src/api/auth.py:15", "detail": "Slack Token"}
        ]
        gatekeeper = Gatekeeper(min_health="Healthy", max_critical_smells=0)
        result = gatekeeper.evaluate(clean_profile)

        sarif = gatekeeper.to_sarif(result, clean_profile)

        assert sarif["version"] == "2.1.0"
        assert "$schema" in sarif
        assert len(sarif["runs"]) == 1
        driver = sarif["runs"][0]["tool"]["driver"]
        assert driver["name"] == "CodeDNA Gatekeeper"
        assert len(driver["rules"]) >= 4

        # Verify results contain the security finding
        results = sarif["runs"][0]["results"]
        sec_findings = [r for r in results if r["ruleId"] == "DNA-SEC-001"]
        assert len(sec_findings) >= 1
        loc = sec_findings[0]["locations"][0]["physicalLocation"]
        assert loc["artifactLocation"]["uri"] == "src/api/auth.py"
        assert loc["region"]["startLine"] == 15

    def test_json_export(self, clean_profile):
        gatekeeper = Gatekeeper()
        result = gatekeeper.evaluate(clean_profile)
        json_str = gatekeeper.to_json(result)

        data = json.loads(json_str)
        assert data["passed"] is True
        assert data["overall_health"] == "Healthy"
        assert "evaluations" in data
