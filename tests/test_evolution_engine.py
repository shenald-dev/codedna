import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from codedna.analyzers.evolution_engine import EvolutionEngine
from git import Repo

def test_compute_churn_git_log_format():
    engine = EvolutionEngine()
    repo_mock = MagicMock(spec=Repo)
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
