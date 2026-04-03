import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock necessary modules
sys.modules['git'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()

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
            "ext::sh -c touch pwned",
            "file:///etc/passwd",
            "ftp://evil.com/repo",
        ]

        for source in malicious_sources:
            with self.subTest(source=source):
                with self.assertRaises(ValueError) as cm:
                    self.cloner.clone(source)
                self.assertIn("Invalid repository source", str(cm.exception))
                git.Repo.clone_from.assert_not_called()

    def test_path_traversal(self):
        import git

        # Test 1: URL that resolves to . or .. after processing should raise ValueError
        invalid_name_sources = [
            "https://github.com/user/.",
            "https://github.com/user/..",
        ]
        for source in invalid_name_sources:
            with self.subTest(source=source):
                with patch("codedna.analyzers.repo_cloner.Path.exists", return_value=False):
                    with self.assertRaises(ValueError):
                        self.cloner.clone(source)

        # Test 2: URL with path traversal elements should have its base name safely extracted
        traversal_sources = [
            "https://github.com/user/../../../etc/passwd",
            "https://github.com/user/..%2f..%2f..%2fetc%2fpasswd",
        ]
        for source in traversal_sources:
            with self.subTest(source=source):
                with patch("codedna.analyzers.repo_cloner.Path.exists", return_value=False):
                    self.cloner.clone(source)
                    git.Repo.clone_from.assert_called()
                    args, _ = git.Repo.clone_from.call_args
                    self.assertTrue(str(args[1]).endswith("passwd"))

    def test_clone_with_valid_source(self):
        import git
        valid_source = "https://github.com/user/repo.git"

        # Mock Path.exists to return False so it tries to clone
        with patch("codedna.analyzers.repo_cloner.Path.exists", return_value=False):
            self.cloner.clone(valid_source)

        git.Repo.clone_from.assert_called()
        args, _ = git.Repo.clone_from.call_args
        self.assertEqual(args[0], valid_source)

if __name__ == "__main__":
    unittest.main()
