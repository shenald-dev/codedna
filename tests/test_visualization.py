"""Tests for visualization modules."""

import html as html_lib

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
        assert html_lib.escape(custom_graph) in html
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
