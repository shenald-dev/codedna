import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from codedna.analyzers.evolution_engine import EvolutionEngine
from git import Repo

def test_compute_churn_git_log_format():
    engine = EvolutionEngine()
    repo_mock = MagicMock()
    repo_mock.git = MagicMock()

    # Mock git log output to simulate correct parsing of "--format=format:COMMIT"
    # Format:
    # COMMIT
    # 10    5   file1.py
    # COMMIT
    # 2     1   file1.py
    # 5     0   file2.py
    mock_log_output = "COMMIT\n10\t5\tfile1.py\nCOMMIT\n2\t1\tfile1.py\n5\t0\tfile2.py"
    repo_mock.git.log.return_value = mock_log_output

    churn = engine._compute_churn(repo_mock)

    # Assert log was called with correct format argument
    repo_mock.git.log.assert_called_once_with(
        "--numstat",
        "--format=format:COMMIT",
        "-n 200",
        "--no-renames"
    )

    # Verify churn results
    assert len(churn) == 2

    file1_churn = next(c for c in churn if c["file"] == "file1.py")
    assert file1_churn["changes"] == 2
    assert file1_churn["total_additions"] == 12
    assert file1_churn["total_deletions"] == 6

    file2_churn = next(c for c in churn if c["file"] == "file2.py")
    assert file2_churn["changes"] == 1
    assert file2_churn["total_additions"] == 5
    assert file2_churn["total_deletions"] == 0

def test_analyze_no_error_on_invalid_repo(tmp_path):
    engine = EvolutionEngine()
    result = engine.analyze(tmp_path)
    assert "error" in result
    assert result["error"] == "Not a Git repository"

def test_compute_churn_git_exception_handling():
    engine = EvolutionEngine()
    repo_mock = MagicMock()
    repo_mock.git = MagicMock()

    # Simulate an exception raised by git.log, e.g. GitCommandError
    repo_mock.git.log.side_effect = Exception("git command failed")

    churn = engine._compute_churn(repo_mock)

    # The method should catch the exception and return an empty list
    assert churn == []

def test_compute_churn_invalid_format_parsing():
    engine = EvolutionEngine()
    repo_mock = MagicMock()
    repo_mock.git = MagicMock()

    # Mock output with missing columns to test parsing robustness
    mock_log_output = "COMMIT\n10\tfile1.py\nCOMMIT\n-\t-\tfile2.py"
    repo_mock.git.log.return_value = mock_log_output

    churn = engine._compute_churn(repo_mock)

    # Verify it doesn't crash and handles the '-' and missing columns correctly
    assert len(churn) == 1
    file2_churn = churn[0]
    assert file2_churn["file"] == "file2.py"
    assert file2_churn["changes"] == 1
    assert file2_churn["total_additions"] == 0
    assert file2_churn["total_deletions"] == 0

def test_analyze_empty_repository(tmp_path):
    # Create an empty git repo
    repo = Repo.init(str(tmp_path))
    engine = EvolutionEngine()
    result = engine.analyze(tmp_path)

    # An empty repository has no commits. It should return empty lists without crashing.
    assert "error" not in result
    assert result.get("total_commits", 0) == 0
    assert result["timeline"] == []
    assert result.get("patterns", []) == []
