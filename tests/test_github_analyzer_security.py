import unittest
from unittest.mock import MagicMock, patch

from codedna.analyzers.github_analyzer import GitHubAnalyzer


class TestGitHubAnalyzerSecurity(unittest.TestCase):
    def setUp(self):
        self.analyzer = GitHubAnalyzer()

    def test_github_analyzer_security_malicious_urls(self):
        # Path traversal in URL
        res = self.analyzer.analyze("https://github.com/../repo")
        self.assertFalse(res["is_github"])

        res = self.analyzer.analyze("https://github.com/owner/..")
        self.assertFalse(res["is_github"])

        # Credential injection
        res = self.analyzer.analyze("https://github.com/owner/repo@evil.com")
        self.assertFalse(res["is_github"])

        # Wrong host
        res = self.analyzer.analyze("https://evil.com/owner/repo")
        self.assertFalse(res["is_github"])

        # No owner/repo
        res = self.analyzer.analyze("https://github.com/")
        self.assertFalse(res["is_github"])

    def test_github_analyzer_valid_url(self):
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.__enter__.return_value.read.return_value = b'{"stargazers_count": 10}'
            mock_urlopen.return_value = mock_response

            res = self.analyzer.analyze("https://github.com/valid-owner/valid.repo_123")
            self.assertTrue(res["is_github"])
            self.assertEqual(res["stars"], 10)

    def test_github_analyzer_extra_slashes(self):
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.__enter__.return_value.read.return_value = b'{"stargazers_count": 5}'
            mock_urlopen.return_value = mock_response

            res = self.analyzer.analyze("https://github.com///owner///repo///")
            self.assertTrue(res["is_github"])
            self.assertEqual(res["stars"], 5)

if __name__ == "__main__":
    unittest.main()
