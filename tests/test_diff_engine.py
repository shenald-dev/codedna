"""Tests for CodeDNA Genetic Diff & Drift Engine."""

from __future__ import annotations

import json

import pytest

from codedna.analyzers.diff_engine import DiffEngine


@pytest.fixture
def base_profile():
    return {
        "metadata": {
            "source": "https://github.com/org/repo-main",
            "analyzed_at": "2026-10-01T10:00:00Z",
            "version": "1.0.0",
        },
        "signature": "LANG:PYT | ARCH:LAY | SIZE:MD | TEAM:DUO | HEALTH:3",
        "system_type": "Layered",
        "languages": {
            "languages": {
                "Python": {"percentage": 80.0, "files": 20, "lines": 2000},
                "JavaScript": {"percentage": 20.0, "files": 5, "lines": 500},
            }
        },
        "architecture": {
            "primary_pattern": "Layered",
            "traits": ["CI/CD Enabled", "Tested"],
            "coupling": "Low",
        },
        "structure_stats": {
            "total_files": 25,
            "total_dirs": 5,
            "max_depth": 3,
            "modules": 4,
        },
        "dependencies": {
            "total_modules": 4,
            "total_edges": 6,
            "density": 0.25,
            "has_circular_deps": False,
            "circular_count": 0,
        },
        "health": {
            "overall": "Healthy",
            "severity_counts": {"critical": 0, "warning": 2, "info": 5},
            "coupling": "Low",
            "circular_deps": False,
        },
        "risks": [],
        "developer_genome": {
            "total_contributors": 2,
            "bus_factor": 2,
            "primary_architect": "Alice",
            "top_contributors": [{"name": "Alice", "role": "Architect", "commits": 50}],
        },
        "evolution": {
            "total_commits": 100,
            "first_commit": "2025-01-01T00:00:00Z",
            "patterns": ["Consistent"],
        },
        "security": {
            "vulnerabilities": [],
            "total_critical": 0,
            "has_secrets": False,
        },
    }


class TestDiffEngine:
    def test_identical_profiles(self, base_profile):
        engine = DiffEngine()
        diff = engine.compare(base_profile, base_profile)

        assert diff["similarity_score"] == 100.0
        assert diff["mutation_verdict"] == "Identical Genome"
        assert diff["structure_delta"]["files"] == 0
        assert diff["structure_delta"]["modules"] == 0
        assert diff["architecture_shift"]["pattern_changed"] is False
        assert diff["dependency_shift"]["circular_deps"]["status"] == "clean"

    def test_language_shift(self, base_profile):
        target_profile = json.loads(json.dumps(base_profile))
        target_profile["languages"]["languages"] = {
            "Python": {"percentage": 50.0, "files": 15, "lines": 1500},
            "TypeScript": {"percentage": 50.0, "files": 15, "lines": 1500},
        }

        engine = DiffEngine()
        diff = engine.compare(base_profile, target_profile)

        assert "TypeScript" in diff["languages_added"]
        assert "JavaScript" in diff["languages_removed"]
        assert diff["language_deltas"]["Python"]["delta"] == -30.0
        assert diff["similarity_score"] < 100.0

    def test_circular_dependency_introduced_and_resolved(self, base_profile):
        mutated_profile = json.loads(json.dumps(base_profile))
        mutated_profile["dependencies"]["has_circular_deps"] = True
        mutated_profile["dependencies"]["circular_count"] = 2
        mutated_profile["health"]["overall"] = "Needs Attention"

        engine = DiffEngine()
        # Intro test
        diff_intro = engine.compare(base_profile, mutated_profile)
        assert diff_intro["dependency_shift"]["circular_deps"]["status"] == "introduced"
        assert diff_intro["health_shift"]["status"] == "degraded"

        # Resolved test
        diff_resolved = engine.compare(mutated_profile, base_profile)
        assert diff_resolved["dependency_shift"]["circular_deps"]["status"] == "resolved"
        assert diff_resolved["health_shift"]["status"] == "improved"

    def test_secrets_introduced_verdict(self, base_profile):
        leaked_profile = json.loads(json.dumps(base_profile))
        leaked_profile["security"]["has_secrets"] = True
        leaked_profile["security"]["total_critical"] = 1
        leaked_profile["health"]["overall"] = "Critical"

        engine = DiffEngine()
        diff = engine.compare(base_profile, leaked_profile)

        assert diff["health_shift"]["secrets_introduced"] is True
        assert diff["mutation_verdict"] == "Critical Regression (Secrets Exposed)"

    def test_architecture_pattern_migration(self, base_profile):
        migrated_profile = json.loads(json.dumps(base_profile))
        migrated_profile["system_type"] = "Microservices"
        migrated_profile["architecture"]["primary_pattern"] = "Microservices"

        engine = DiffEngine()
        diff = engine.compare(base_profile, migrated_profile)

        assert diff["architecture_shift"]["pattern_changed"] is True
        assert diff["architecture_shift"]["from_pattern"] == "Layered"
        assert diff["architecture_shift"]["to_pattern"] == "Microservices"
        assert diff["mutation_verdict"] == "Paradigm Shift / Architectural Migration"

    def test_to_markdown_and_json(self, base_profile):
        engine = DiffEngine()
        diff = engine.compare(base_profile, base_profile)

        md = engine.to_markdown(diff)
        assert "# 🧬 CodeDNA Genetic Drift & Mutation Diff" in md
        assert "Identical Genome" in md
        assert "100.0%" in md

        json_str = engine.to_json(diff)
        parsed = json.loads(json_str)
        assert parsed["similarity_score"] == 100.0
