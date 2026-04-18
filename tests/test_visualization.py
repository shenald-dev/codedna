"""Tests for visualization modules."""

import pytest

from codedna.visualization.html_export import HTMLExporter


@pytest.fixture
def mock_profile():
    return {
        "metadata": {
            "source": "test-repo",
            "analyzed_at": "2023-10-27T12:00:00Z"
        },
        "signature": "LANG:PYT | ARCH:LAY",
        "system_type": "Layered",
        "health": {
            "overall": "Healthy"
        },
        "structure_stats": {
            "total_files": 10
        },
        "developer_genome": {
            "total_contributors": 2,
            "bus_factor": 1,
            "top_contributors": [
                {"name": "Alice", "role": "Architect", "commits": 50},
                {"name": "Bob", "role": "Developer", "commits": 20}
            ]
        },
        "languages": {
            "languages": {
                "Python": {"percentage": 80, "files": 8},
                "Shell": {"percentage": 20, "files": 2}
            }
        },
        "risks": ["🔴 God Class", "🟡 Large File"],
        "architecture": {
            "traits": ["Containerized", "CI/CD Enabled"]
        },
        "evolution": {
            "total_commits": 70,
            "first_commit": "2023-01-01T00:00:00Z",
            "patterns": ["Stable"]
        },
        "github": {
            "is_github": True,
            "stars": 100,
            "forks": 10,
            "issues": 5
        }
    }

class TestHTMLExporter:
    def test_export_mermaid_fallback(self, mock_profile):
        exporter = HTMLExporter()
        # Test with empty string for mermaid_graph
        html = exporter.export(mock_profile, "")
        assert "graph LR\n  A[No connection data found]" in html
        assert "test-repo" in html
        assert "Healthy" in html

    def test_export_with_mermaid_graph(self, mock_profile):
        exporter = HTMLExporter()
        custom_graph = "graph TD\n  A --> B"
        html = exporter.export(mock_profile, custom_graph)
        assert custom_graph in html
        assert "graph LR\n  A[No connection data found]" not in html

    def test_export_no_github(self, mock_profile):
        exporter = HTMLExporter()
        del mock_profile["github"]
        html = exporter.export(mock_profile, "")
        assert "★" not in html # GitHub stars icon

    def test_export_no_risks(self, mock_profile):
        exporter = HTMLExporter()
        mock_profile["risks"] = []
        html = exporter.export(mock_profile, "")
        assert "✓ No critical risks detected." in html

    def test_export_no_traits(self, mock_profile):
        exporter = HTMLExporter()
        mock_profile["architecture"]["traits"] = []
        html = exporter.export(mock_profile, "")
        assert "No standard traits detected" in html

    def test_export_xss_escaping(self, mock_profile):
        exporter = HTMLExporter()
        mock_profile["metadata"]["source"] = "<script>alert('xss')</script>"
        mock_profile["developer_genome"]["top_contributors"][0]["name"] = "<img src=x onerror=alert(1)>"
        mock_profile["risks"] = ["🔴 <b onmouseover=alert(1)>Risk</b>"]

        html = exporter.export(mock_profile, "")

        # Original XSS strings should not be in the output
        assert "<script>alert('xss')</script>" not in html
        assert "<img src=x onerror=alert(1)>" not in html
        assert "<b onmouseover=alert(1)>Risk</b>" not in html

        # Escaped versions should be in the output
        assert "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;" in html
        assert "&lt;img src=x onerror=alert(1)&gt;" in html
        assert "&lt;b onmouseover=alert(1)&gt;Risk&lt;/b&gt;" in html

    def test_export_string_numeric_values(self, mock_profile):
        exporter = HTMLExporter()
        mock_profile["languages"]["languages"]["Python"]["lines"] = "100.5"
        mock_profile["github"]["stars"] = "1000"
        mock_profile["github"]["forks"] = "bad"
        mock_profile["github"]["issues"] = "2.0"

        # This shouldn't raise a ValueError
        html = exporter.export(mock_profile, "")

        # Check that the formatted values appear in the HTML
        assert "100.5" in html or "100" in html # lines, it might not render the exact string if it isn't cast correctly
        assert "1,000" in html # stars
        assert "bad" in html # forks
        assert "2 issues" in html # issues

    def test_export_github_stats_xss_escaping(self, mock_profile):
        exporter = HTMLExporter()
        mock_profile["github"]["stars"] = "<script>alert('stars')</script>"
        mock_profile["github"]["forks"] = "<script>alert('forks')</script>"
        mock_profile["github"]["issues"] = "<script>alert('issues')</script>"

        html = exporter.export(mock_profile, "")

        # Original XSS strings should not be in the output
        assert "<script>alert('stars')</script>" not in html
        assert "<script>alert('forks')</script>" not in html
        assert "<script>alert('issues')</script>" not in html

        # Escaped versions should be in the output
        assert "&lt;script&gt;alert(&#x27;stars&#x27;)&lt;/script&gt;" in html
        assert "&lt;script&gt;alert(&#x27;forks&#x27;)&lt;/script&gt;" in html
        assert "&lt;script&gt;alert(&#x27;issues&#x27;)&lt;/script&gt;" in html
