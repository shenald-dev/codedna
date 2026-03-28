from codedna.analyzers.ai_analyzer import AIAnalyzer


def test_ai_analyzer_no_key(monkeypatch):
    """Test AIAnalyzer fails gracefully when OPENAI_API_KEY is missing."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    analyzer = AIAnalyzer()

    dummy_profile = {"system_type": "Monolith"}
    result = analyzer.synthesize(dummy_profile)

    assert not result.success
    assert "skipped" in result.executive_summary.lower()
    assert len(result.refactoring_recommendations) == 0

def test_ai_analyzer_minimizer():
    """Test the AI payload minimizer truncates large components before LLM transmission."""
    analyzer = AIAnalyzer()
    analyzer.api_key = "dummy"

    heavy_profile = {
        "metadata": {"version": "1.0"},
        "structure_stats": {"modules": ["a", "b", "c", "d"]},
        "risks": ["Risk 1", "Risk 2", "Risk 3", "Risk 4", "Risk 5", "Risk 6"],
        "mermaid_graph": "graph TD; A-->B;"
    }

    minimized = analyzer._minimize_payload(heavy_profile)

    assert minimized["structure_stats"]["modules"] == 4
    assert len(minimized["risks"]) == 5
    assert "mermaid_graph" not in minimized
