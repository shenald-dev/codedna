import pytest
from unittest.mock import MagicMock, patch
from codedna.analyzers.evolution_engine import EvolutionEngine
from codedna.analyzers.developer_analyzer import DeveloperAnalyzer
import git

def test_evolution_engine_tformat():
    engine = EvolutionEngine()

    mock_repo = MagicMock()
    mock_repo.git.log.return_value = ""

    with patch("codedna.analyzers.developer_analyzer.git.Repo", return_value=mock_repo):
        engine._compute_churn(mock_repo)

        # Verify git.log was called with tformat
        mock_repo.git.log.assert_called_with(
            "--numstat",
            "--format=tformat:COMMIT",
            "-n 200",
            "--no-renames"
        )

def test_developer_analyzer_tformat():
    analyzer = DeveloperAnalyzer()

    mock_repo = MagicMock()
    mock_repo.git.log.return_value = ""

    with patch("codedna.analyzers.developer_analyzer.git.Repo", return_value=mock_repo):
        # We need to stub out the iteration part so it doesn't crash
        mock_repo.iter_commits = MagicMock(return_value=[])

        # we can just test the method logic
        # analyzer.analyze does the git log call
        analyzer.analyze(".", max_commits=50)

        mock_repo.git.log.assert_called_with(
            "--name-only",
            "--format=tformat:COMMIT::%H::%aN::%aE::%ad",
            "--date=short",
            "-n 50"
        )
