import sys
from pathlib import Path
from unittest.mock import MagicMock
from codedna.analyzers.developer_analyzer import DeveloperAnalyzer
import git

analyzer = DeveloperAnalyzer()
mock_repo = MagicMock()
mock_repo.git.log = MagicMock(return_value="COMMIT::926371::Test User::test@example.com::2026-05-12\nfile.py\n\nCOMMIT::123456::Test User 2::test2@example.com::2026-05-11\nfile2.py\n")

original_repo = git.Repo
git.Repo = MagicMock(return_value=mock_repo)

try:
    result = analyzer.analyze(Path("/tmp/foo"))
    print(result)
finally:
    git.Repo = original_repo
