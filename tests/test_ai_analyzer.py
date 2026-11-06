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

def test_ai_analyzer_minimizer_no_mutation():
    """Test the AI payload minimizer does not mutate the original profile."""
    analyzer = AIAnalyzer()

    heavy_profile = {
        "metadata": {"version": "1.0"},
        "structure_stats": {"modules": ["a", "b", "c", "d"]},
        "risks": ["Risk 1", "Risk 2", "Risk 3", "Risk 4", "Risk 5", "Risk 6"],
        "mermaid_graph": "graph TD; A-->B;"
    }

    _ = analyzer._minimize_payload(heavy_profile)

    assert heavy_profile["structure_stats"]["modules"] == ["a", "b", "c", "d"]
    assert len(heavy_profile["risks"]) == 6
    assert "mermaid_graph" in heavy_profile

def test_ai_analyzer_missing_openai_package(monkeypatch):
    """Test AIAnalyzer fails gracefully when the openai package is missing."""
    import builtins

    real_import = builtins.__import__
    def mock_import(name, *args, **kwargs):
        if name == 'openai':
            raise ImportError("No module named 'openai'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    monkeypatch.setattr(builtins, '__import__', mock_import)

    analyzer = AIAnalyzer()
    result = analyzer.synthesize({})

    assert not result.success
    assert "not installed" in result.executive_summary
    assert result.error_message == "Missing openai package"

def test_ai_analyzer_success(monkeypatch):
    """Test AIAnalyzer correctly parses a successful LLM response."""
    import json
    from types import SimpleNamespace

    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")

    # Mocking the deeply nested openai client structure
    class MockCompletions:
        def create(self, **kwargs):
            content = json.dumps({
                "executive_summary": "This is a great codebase.",
                "refactoring_recommendations": ["Fix tests", "Clean up imports", "Refactor classes"]
            })
            message = SimpleNamespace(content=content)
            choice = SimpleNamespace(message=message)
            return SimpleNamespace(choices=[choice])

    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.chat = MockChat()

    class MockOpenAI:
        OpenAI = MockClient

    # Patch sys.modules to mock the openai package completely
    import sys
    monkeypatch.setitem(sys.modules, "openai", MockOpenAI())

    analyzer = AIAnalyzer()
    result = analyzer.synthesize({})

    assert result.success
    assert result.executive_summary == "This is a great codebase."
    assert len(result.refactoring_recommendations) == 3
    assert result.refactoring_recommendations[0] == "Fix tests"

def test_ai_analyzer_api_error(monkeypatch):
    """Test AIAnalyzer correctly catches and handles API errors."""
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")

    class MockCompletions:
        def create(self, **kwargs):
            raise ValueError("API Rate Limit Exceeded")

    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.chat = MockChat()

    class MockOpenAI:
        OpenAI = MockClient

    import sys
    monkeypatch.setitem(sys.modules, "openai", MockOpenAI())

    analyzer = AIAnalyzer()
    result = analyzer.synthesize({})

    assert not result.success
    assert "API error" in result.executive_summary
    assert result.error_message == "API Rate Limit Exceeded"
