"""Tests for DiffEngine architectural drift regression gating."""

from __future__ import annotations

from codedna.analyzers.diff_engine import DiffEngine


def _make_dummy_profiles(
    health_a: str = "Healthy",
    health_b: str = "Healthy",
    circular_a: bool = False,
    circular_b: bool = False,
    secrets_a: bool = False,
    secrets_b: bool = False,
    crit_a: int = 0,
    crit_b: int = 0,
):
    profile_a = {
        "metadata": {"source": "baseline", "analyzed_at": "2026-10-31T00:00:00Z"},
        "system_type": "Modular",
        "languages": {"languages": {"Python": {"files": 10, "lines": 1000, "percentage": 100.0}}},
        "structure": {"total_files": 10, "total_directories": 2, "avg_file_length": 100},
        "dependencies": {"total_modules": 5, "total_edges": 4, "has_circular_deps": circular_a, "density": 0.15},
        "architecture": {"primary_pattern": "Layered"},
        "health": {"overall": health_a, "severity_counts": {"critical": crit_a, "warning": 1, "info": 2}},
        "security": {"has_secrets": secrets_a, "total_critical": 1 if secrets_a else 0, "vulnerabilities": []},
        "developers": {"bus_factor": 3, "total_contributors": 4},
        "evolution": {"commit_velocity": 5.0, "code_churn": 100},
    }
    profile_b = {
        "metadata": {"source": "target", "analyzed_at": "2026-11-01T00:00:00Z"},
        "system_type": "Modular",
        "languages": {"languages": {"Python": {"files": 10, "lines": 1000, "percentage": 100.0}}},
        "structure": {"total_files": 10, "total_directories": 2, "avg_file_length": 100},
        "dependencies": {"total_modules": 5, "total_edges": 4, "has_circular_deps": circular_b, "density": 0.15},
        "architecture": {"primary_pattern": "Layered"},
        "health": {"overall": health_b, "severity_counts": {"critical": crit_b, "warning": 1, "info": 2}},
        "security": {"has_secrets": secrets_b, "total_critical": 1 if secrets_b else 0, "vulnerabilities": []},
        "developers": {"bus_factor": 3, "total_contributors": 4},
        "evolution": {"commit_velocity": 5.0, "code_churn": 100},
    }
    return profile_a, profile_b


def test_drift_gate_clean_pass():
    """Verify identical or non-degraded codebases pass drift gate."""
    p_a, p_b = _make_dummy_profiles()
    engine = DiffEngine()
    diff = engine.compare(p_a, p_b)

    passed, reasons = DiffEngine.evaluate_drift_gate(diff)
    assert passed is True
    assert reasons == []


def test_drift_gate_health_degradation():
    """Verify health score drop triggers drift gate failure."""
    p_a, p_b = _make_dummy_profiles(health_a="Healthy", health_b="Fair", crit_b=0)
    engine = DiffEngine()
    diff = engine.compare(p_a, p_b)

    passed, reasons = DiffEngine.evaluate_drift_gate(diff, allow_degradation=False)
    assert passed is False
    assert any("health degraded" in r.lower() for r in reasons)

    # Allowed when allow_degradation is True
    passed_allowed, reasons_allowed = DiffEngine.evaluate_drift_gate(diff, allow_degradation=True)
    assert passed_allowed is True
    assert reasons_allowed == []


def test_drift_gate_introduced_circular_deps():
    """Verify introducing circular dependencies fails gate."""
    p_a, p_b = _make_dummy_profiles(circular_a=False, circular_b=True)
    engine = DiffEngine()
    diff = engine.compare(p_a, p_b)

    passed, reasons = DiffEngine.evaluate_drift_gate(diff, allow_circular_deps=False)
    assert passed is False
    assert any("circular" in r.lower() for r in reasons)

    # Allowed when allow_circular_deps is True
    passed_allowed, _ = DiffEngine.evaluate_drift_gate(diff, allow_circular_deps=True)
    assert passed_allowed is True


def test_drift_gate_introduced_secrets():
    """Verify newly introduced secrets trigger failure."""
    p_a, p_b = _make_dummy_profiles(secrets_a=False, secrets_b=True)
    engine = DiffEngine()
    diff = engine.compare(p_a, p_b)

    passed, reasons = DiffEngine.evaluate_drift_gate(diff, allow_new_secrets=False)
    assert passed is False
    assert any("hardcoded credentials" in r.lower() or "secrets" in r.lower() for r in reasons)

    # Allowed when allow_new_secrets is True
    passed_allowed, _ = DiffEngine.evaluate_drift_gate(diff, allow_new_secrets=True)
    assert passed_allowed is True


def test_drift_gate_min_similarity():
    """Verify similarity below threshold fails gate."""
    p_a, p_b = _make_dummy_profiles()
    engine = DiffEngine()
    diff = engine.compare(p_a, p_b)

    # Set min_similarity higher than 100 or test threshold
    passed, reasons = DiffEngine.evaluate_drift_gate(diff, min_similarity=99.9)
    assert passed is True

    passed_fail, reasons_fail = DiffEngine.evaluate_drift_gate(diff, min_similarity=105.0)
    assert passed_fail is False
    assert any("Genetic similarity" in r for r in reasons_fail)
