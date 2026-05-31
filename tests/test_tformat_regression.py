def test_git_log_tformat_prefix_present():
    """Verify that the Git format strings are properly prefixed with tformat: to prevent parsing errors on modern Git."""
    with open("codedna/analyzers/developer_analyzer.py", "r") as f:
        dev_content = f.read()

    assert "--format=tformat:COMMIT" in dev_content, "DeveloperAnalyzer is missing the tformat: prefix in git log"

    with open("codedna/analyzers/evolution_engine.py", "r") as f:
        evo_content = f.read()

    assert "--format=tformat:COMMIT" in evo_content, "EvolutionEngine is missing the tformat: prefix in git log"
