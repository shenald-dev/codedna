import pytest
from codedna.analyzers.developer_analyzer import DeveloperAnalyzer
from codedna.analyzers.evolution_engine import EvolutionEngine
import subprocess
import git

@pytest.fixture
def git_repo(tmp_path):
    """Create a minimal sample repository initialized as a Git repo."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("print('hello')\n")

    subprocess.run(["git", "init", "-b", "main"], cwd=str(tmp_path), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(tmp_path), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(tmp_path), check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=str(tmp_path), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(tmp_path), check=True, capture_output=True)

    return tmp_path

class TestGitLogFormatting:
    def test_developer_analyzer_git_log_formatting(self, git_repo):
        analyzer = DeveloperAnalyzer()
        try:
            result = analyzer.analyze(git_repo, max_commits=5)
            assert "contributors" in result
            assert isinstance(result["contributors"], list)
            assert "error" not in result or result.get("error") != "Not a Git repository"
        except git.exc.GitCommandError as e:
            pytest.fail(f"git log command failed in DeveloperAnalyzer: {e}")

    def test_evolution_engine_git_log_formatting(self, git_repo):
        analyzer = EvolutionEngine()
        try:
            result = analyzer.analyze(git_repo)
            assert "patterns" in result
            assert isinstance(result["patterns"], list)
        except git.exc.GitCommandError as e:
            pytest.fail(f"git log command failed in EvolutionEngine: {e}")
```