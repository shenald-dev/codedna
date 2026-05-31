import pytest
import subprocess

def test_git_log_tformat():
    # Use standard subprocess to verify git behavior directly, since
    # GitPython's test environment setup can be flaky with mocking
    result = subprocess.run(
        ["git", "log", "--numstat", "--format=tformat:COMMIT", "-n", "1", "--no-renames"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "COMMIT" in result.stdout
