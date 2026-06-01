import pytest
import os
import logging
from codedna.analyzers.dependency_mapper import DependencyMapper
from codedna.analyzers.security_detector import SecurityDetector
from codedna.analyzers.code_smell_detector import CodeSmellDetector

def test_normalize_import_path_corruption():
    mapper = DependencyMapper()
    # Test that .env does not get corrupted into env
    assert mapper._normalize_import("../.env") == ".env"
    assert mapper._normalize_import("./utils.js") == "utils.js"
    assert mapper._normalize_import("../../my_file.py") == "my_file.py"

def test_external_dependency_filtering(tmp_path):
    # Test that external dependencies without dots or slashes are filtered out
    # but local dependencies are kept
    test_file = tmp_path / "test_deps.py"
    test_file.write_text("import os\nimport sys\nimport json\nfrom .utils import helper\n")

    mapper = DependencyMapper()
    # Mock walker to just yield our file
    mapper._walk_source = lambda path: [test_file]

    result = mapper.map(tmp_path)
    # The edges should not contain os, sys, json
    edges = result["edges"]
    edge_targets = [e["to"] for e in edges]
    assert "os" not in edge_targets
    assert "sys" not in edge_targets
    assert "json" not in edge_targets
    # It should contain utils (if normalized)
    assert ".utils" in edge_targets

import importlib
import codedna.analyzers.dependency_mapper as dm_module

def test_env_var_warning(monkeypatch, caplog):
    monkeypatch.setenv("CODEDNA_MAX_FILE_SIZE", "invalid")

    with caplog.at_level(logging.WARNING):
        # Force reload to trigger module-level execution
        importlib.reload(dm_module)

    assert any("Invalid CODEDNA_MAX_FILE_SIZE. Using default 5MB." in record.message for record in caplog.records)
    assert dm_module.MAX_FILE_SIZE == 5 * 1024 * 1024
