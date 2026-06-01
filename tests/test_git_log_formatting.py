from pathlib import Path
from unittest.mock import MagicMock, patch, call
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
            f"-n {500}"
        )
        assert result["total_commits"] == 1

    @patch('codedna.analyzers.evolution_engine.Repo')
    def test_evolution_engine_git_log_format(self, mock_repo_cls):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo

        # Simulate git log output for churn computation
        mock_repo.git.log.side_effect = [
            "COMMIT::12345::2026-05-27T10:00::2026-05-27::msg\n 1 file changed, 10 insertions(+), 5 deletions(-)",
            "COMMIT\n10\t5\tsrc/main.py"
        ]

        analyzer = EvolutionEngine()
        result = analyzer.analyze(Path("dummy_path"))

        # Verify git log was called with the correct tformat: prefix
        expected_calls = [
            call('--format=tformat:COMMIT::%H::%cI::%cd::%s', '--date=short', '--shortstat', '-n', '500'),
            call('--numstat', '--format=tformat:COMMIT', '-n 200', '--no-renames')
        ]
        mock_repo.git.log.assert_has_calls(expected_calls, any_order=True)
