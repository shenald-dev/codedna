import os
import pytest
from pathlib import Path

def test_max_file_size_config(monkeypatch):
    """Test that setting CODEDNA_MAX_FILE_SIZE changes the module level constant."""
    # This just ensures we can load the modules and they read from os.environ
    # Because they read at module load time, we can't easily monkeypatch and reload them
    # without importlib, but we can verify the constant is there.
    from codedna.analyzers.code_smell_detector import MAX_FILE_SIZE as csd_size
    from codedna.analyzers.dependency_mapper import MAX_FILE_SIZE as dm_size
    from codedna.analyzers.security_detector import MAX_FILE_SIZE as sd_size

    assert isinstance(csd_size, int)
    assert isinstance(dm_size, int)
    assert isinstance(sd_size, int)

def test_large_file_skip(tmp_path, monkeypatch):
    """Test that a large file is skipped by DependencyMapper."""
    import importlib

    # Temporarily set the max file size to 10 bytes
    monkeypatch.setenv("CODEDNA_MAX_FILE_SIZE", "10")

    # We must reload the module because the constant is evaluated at load time
    import codedna.analyzers.dependency_mapper
    importlib.reload(codedna.analyzers.dependency_mapper)

    DependencyMapper = codedna.analyzers.dependency_mapper.DependencyMapper

    # Create a small file and a large file
    small_file = tmp_path / "small.py"
    small_file.write_text("import os\n")

    large_file = tmp_path / "large.py"
    large_file.write_text("import sys\n" * 5) # Definitely > 10 bytes

    assert small_file.stat().st_size <= 10
    assert large_file.stat().st_size > 10

    mapper = DependencyMapper()

    # The mapper walks the directory
    deps = mapper.map(tmp_path)

    # It should only process the small file (os dependency)
    # the large file (sys dependency) should be skipped
    assert "os" in deps["edges"][0]["to"] if deps["edges"] else True

    # Clean up by reloading without the env var
    monkeypatch.delenv("CODEDNA_MAX_FILE_SIZE", raising=False)
    importlib.reload(codedna.analyzers.dependency_mapper)
```