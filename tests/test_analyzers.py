"""Tests for CodeDNA analyzer modules."""

import os
import tempfile
from pathlib import Path

import pytest

from codedna.analyzers.language_detector import LanguageDetector
from codedna.analyzers.structure_analyzer import StructureAnalyzer
from codedna.analyzers.dependency_mapper import DependencyMapper
from codedna.analyzers.code_smell_detector import CodeSmellDetector
from codedna.analyzers.security_detector import SecurityDetector
from codedna.analyzers.github_analyzer import GitHubAnalyzer
from codedna.analyzers.architecture_detector import ArchitectureDetector
from codedna.analyzers.dna_generator import DNAGenerator


@pytest.fixture
def sample_repo(tmp_path):
    """Create a minimal sample repository for testing."""
    # Python files
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    (src / "main.py").write_text(
        "import os\nfrom src.utils import helper\n\ndef main():\n    pass\n"
    )
    (src / "utils.py").write_text(
        "import json\n\ndef helper():\n    return 'hello'\nAWS_KEY = 'AKIAIOSFODNN7EXAMPLE'\n"
    )

    # JS file
    (tmp_path / "index.js").write_text(
        "import React from 'react';\nconst App = () => {};\n"
    )

    # Config files
    (tmp_path / "package.json").write_text('{"name": "test"}')
    (tmp_path / "README.md").write_text("# Test Project\n")
    (tmp_path / "Dockerfile").write_text("FROM node:20\n")

    # Nested dirs
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_main.py").write_text("def test_example():\n    assert True\n")

    return tmp_path


class TestLanguageDetector:
    def test_detect_languages(self, sample_repo):
        detector = LanguageDetector()
        result = detector.detect(sample_repo)
        assert "languages" in result
        assert "primary" in result
        assert result["total_files"] > 0

    def test_detects_python(self, sample_repo):
        result = LanguageDetector().detect(sample_repo)
        assert "Python" in result["languages"]

    def test_detects_javascript(self, sample_repo):
        result = LanguageDetector().detect(sample_repo)
        assert "JavaScript" in result["languages"]

    def test_calculates_percentage(self, sample_repo):
        result = LanguageDetector().detect(sample_repo)
        total_pct = sum(l["percentage"] for l in result["languages"].values())
        assert 99 <= total_pct <= 101  # Should sum to ~100%


class TestStructureAnalyzer:
    def test_analyze_structure(self, sample_repo):
        result = StructureAnalyzer().analyze(sample_repo)
        assert result["total_files"] > 0
        assert result["total_dirs"] >= 0
        assert "modules" in result

    def test_detects_modules(self, sample_repo):
        result = StructureAnalyzer().analyze(sample_repo)
        module_paths = [m["path"] for m in result["modules"]]
        assert any("src" in p for p in module_paths)


class TestDependencyMapper:
    def test_map_dependencies(self, sample_repo):
        result = DependencyMapper().map(sample_repo)
        assert "total_modules" in result
        assert "total_edges" in result
        assert result["total_modules"] > 0

    def test_detects_imports(self, sample_repo):
        result = DependencyMapper().map(sample_repo)
        assert result["total_edges"] > 0

    def test_generates_mermaid(self, sample_repo):
        mermaid = DependencyMapper().build_mermaid(sample_repo)
        assert mermaid.startswith("graph LR")


class TestCodeSmellDetector:
    def test_detect_smells(self, sample_repo):
        result = CodeSmellDetector().detect(sample_repo)
        assert "smells" in result
        assert "total" in result
        assert "health_score" in result

    def test_health_score_valid(self, sample_repo):
        result = CodeSmellDetector().detect(sample_repo)
        assert result["health_score"] in ("Healthy", "Fair", "Needs Attention", "Critical")


class TestSecurityDetector:
    def test_detect_secrets(self, sample_repo):
        result = SecurityDetector().detect(sample_repo)
        assert result["total_critical"] > 0
        assert result["has_secrets"] is True


class TestGitHubAnalyzer:
    def test_analyze_local(self):
        result = GitHubAnalyzer().analyze(".")
        assert result["is_github"] is False

    def test_analyze_github_url(self):
        result = GitHubAnalyzer().analyze("https://github.com/microsoft/typescript")
        assert "is_github" in result


class TestArchitectureDetector:
    def test_detect_architecture(self, sample_repo):
        result = ArchitectureDetector().detect(sample_repo)
        assert "primary_pattern" in result
        assert "traits" in result

    def test_detects_containerized(self, sample_repo):
        result = ArchitectureDetector().detect(sample_repo)
        assert "Containerized" in result["traits"]


class TestDNAGenerator:
    def test_generate_profile(self, sample_repo):
        gen = DNAGenerator()
        profile = gen.generate(
            repo_source="test-repo",
            languages={"languages": {"Python": {"files": 3, "lines": 20, "percentage": 80}}, "primary": "Python", "total_files": 3, "total_lines": 20},
            structure={"total_files": 5, "total_dirs": 2, "max_depth": 2, "modules": []},
            dependencies={"total_modules": 3, "total_edges": 2, "density": 0.3, "has_circular_deps": False, "cycles": []},
            architecture={"primary_pattern": "Monolith", "detected_patterns": [], "traits": [], "coupling": "Low"},
            smells={"smells": [], "total": 0, "severity_counts": {"critical": 0, "warning": 0, "info": 0}, "health_score": "Healthy"},
            developers={"total_contributors": 1, "contributors": [{"name": "dev", "role": "Primary Architect", "commits": 10}], "bus_factor": 1},
            evolution={"total_commits": 10, "patterns": ["Stable Evolution"]},
            security={"vulnerabilities": [], "total_critical": 0, "has_secrets": False},
            github={"is_github": True, "stars": 100},
            mermaid_graph="graph LR\n  A-->B",
        )
        assert profile["system_type"] == "Monolith"
        assert "signature" in profile

    def test_to_markdown(self):
        gen = DNAGenerator()
        profile = gen.generate(
            repo_source="test",
            languages={"languages": {}, "primary": "Python", "total_files": 0, "total_lines": 0},
            structure={"total_files": 0, "total_dirs": 0, "max_depth": 0, "modules": []},
            dependencies={"total_modules": 0, "total_edges": 0, "density": 0, "has_circular_deps": False, "cycles": []},
            architecture={"primary_pattern": "Unknown", "detected_patterns": [], "traits": [], "coupling": "Low"},
            smells={"smells": [], "total": 0, "severity_counts": {}, "health_score": "Healthy"},
            developers={"total_contributors": 0, "contributors": [], "bus_factor": 0},
            evolution={"total_commits": 0, "patterns": []},
        )
        md = gen.to_markdown(profile)
        assert "CodeDNA Profile" in md
        assert "DNA Signature" in md
