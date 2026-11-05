from pathlib import Path


def test_git_log_tformat_prefix_present():
    """Verify that the Git format strings are properly prefixed with tformat: to prevent parsing errors on modern Git."""
    root = Path(__file__).resolve().parent.parent
    dev_content = (root / "codedna/analyzers/developer_analyzer.py").read_text(encoding="utf-8")
    assert "--format=tformat:COMMIT" in dev_content, "DeveloperAnalyzer is missing the tformat: prefix in git log"

    evo_content = (root / "codedna/analyzers/evolution_engine.py").read_text(encoding="utf-8")
    assert "--format=tformat:COMMIT" in evo_content, "EvolutionEngine is missing the tformat: prefix in git log"
