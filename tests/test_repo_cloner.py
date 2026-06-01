import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock necessary modules
sys.modules['git'] = MagicMock()

from codedna.analyzers.repo_cloner import RepoCloner  # noqa: E402


class TestRepoCloner(unittest.TestCase):
    def setUp(self):
        self.cache_dir = "test_cache"
        self.cloner = RepoCloner(cache_dir=self.cache_dir)

    def test_clone_with_malicious_source(self):
        import git
        malicious_sources = [
            "--ext-cmd=touch pwned",
            " -u http://evil.com",
            "\t--help",
            "fd::",
        ]

        for source in malicious_sources:
            with self.subTest(source=source):
                with self.assertRaises(ValueError) as cm:
                    self.cloner.clone(source)
                self.assertTrue("Invalid repository source" in str(cm.exception) or "Unauthorized URL scheme" in str(cm.exception))
                git.Repo.clone_from.assert_not_called()

    @patch("codedna.analyzers.repo_cloner.Repo.clone_from")
    def test_clone_with_valid_source(self, mock_clone_from):
        valid_source = "https://github.com/user/repo.git"

        # Mock Path.exists to return False so it tries to clone
        with patch("codedna.analyzers.repo_cloner.Path.exists", return_value=False):
            self.cloner.clone(valid_source)

        mock_clone_from.assert_called()
        args, _ = mock_clone_from.call_args
        self.assertEqual(args[0], valid_source)

if __name__ == "__main__":
    unittest.main()
