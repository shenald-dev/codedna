import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from codedna.analyzers.developer_analyzer import DeveloperAnalyzer
from codedna.analyzers.evolution_engine import EvolutionEngine
import git

class TestGitLogFormatting:
    @patch('codedna.analyzers.developer_analyzer.git.Repo')
    def test_developer_analyzer_git_log_format(self, mock_repo_cls):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo

        # Simulate successful git log output
        mock_repo.git.log.return_value = "COMMIT::abc1234::John Doe::john@example.com::2026-05-27"

        analyzer = DeveloperAnalyzer()
        result = analyzer.analyze(Path("dummy_path"))

        # Verify git log was called with the correct tformat: prefix
        mock_repo.git.log.assert_called_with(
            "--name-only",
            "--format=tformat:COMMIT::%H::%aN::%aE::%ad",
            "--date=short",
            "-n 500"
        )
        assert result["total_commits"] == 1

    @patch('codedna.analyzers.evolution_engine.Repo')
    def test_evolution_engine_git_log_format(self, mock_repo_cls):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo

        # We need iter_commits to return something so it proceeds to _compute_churn
        mock_commit = MagicMock()
        mock_repo.iter_commits.return_value = [mock_commit]

        # Simulate git log output for churn computation
        mock_repo.git.log.return_value = "COMMIT\n10\t5\tsrc/main.py"

        analyzer = EvolutionEngine()
        result = analyzer.analyze(Path("dummy_path"))

        # Verify git log was called with the correct tformat: prefix
        mock_repo.git.log.assert_called_with(
            "--numstat",
            "--format=tformat:COMMIT",
            "-n 200",
            "--no-renames"
        )
