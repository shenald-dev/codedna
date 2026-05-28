import pytest
from codedna.analyzers.dependency_mapper import DependencyMapper

def test_normalize_import():
    mapper = DependencyMapper()
    assert mapper._normalize_import("./module") == "module"
    assert mapper._normalize_import("../module") == "module"
    assert mapper._normalize_import("../../module") == "module"
    assert mapper._normalize_import("../.env") == ".env"
    assert mapper._normalize_import("../..config") == "..config"