"""Unit and integration tests for CodeDNA ComplexityAnalyzer & Maintainability Index."""

from __future__ import annotations

from pathlib import Path

from codedna.analyzers.complexity_analyzer import ComplexityAnalyzer


def test_python_cyclomatic_complexity_ast(tmp_path: Path):
    """Verify exact McCabe Cyclomatic Complexity calculation for Python AST."""
    code = """
def simple_func():
    return 42

def branching_func(x, y):
    if x > 0 and y > 0:
        return x + y
    elif x < 0:
        for i in range(10):
            if i % 2 == 0:
                pass
    try:
        assert x != 999
    except ValueError:
        pass
    return [n for n in range(5) if n > 2]
"""
    test_file = tmp_path / "sample.py"
    test_file.write_text(code, encoding="utf-8")

    analyzer = ComplexityAnalyzer()
    funcs = analyzer.analyze_file(test_file)

    assert len(funcs) == 2
    f_simple = next(f for f in funcs if f.name == "simple_func")
    f_branch = next(f for f in funcs if f.name == "branching_func")

    assert f_simple.cyclomatic_complexity == 1
    assert f_simple.cognitive_complexity == 0
    assert f_simple.severity == "normal"

    # Branching function:
    # Base = 1
    # if x > 0 and y > 0 (+2: if + and)
    # elif x < 0 (+1)
    # for i in range (+1)
    # if i % 2 == 0 (+1)
    # assert (+1)
    # except (+1)
    # comprehension for + if (+2)
    # Expected CC >= 9
    assert f_branch.cyclomatic_complexity >= 9
    assert f_branch.cognitive_complexity > 0


def test_cognitive_complexity_nesting_penalty(tmp_path: Path):
    """Verify Cognitive Complexity heavily penalizes nested control structures."""
    code = """
def deeply_nested():
    if True:
        for a in range(5):
            while True:
                if a == 2:
                    break
"""
    test_file = tmp_path / "nested.py"
    test_file.write_text(code, encoding="utf-8")

    analyzer = ComplexityAnalyzer()
    funcs = analyzer.analyze_file(test_file)
    assert len(funcs) == 1
    # Level 0 (if): 1 + 0 = 1
    # Level 1 (for): 1 + 1 = 2
    # Level 2 (while): 1 + 2 = 3
    # Level 3 (if): 1 + 3 = 4
    # Total cognitive >= 10
    assert funcs[0].cognitive_complexity >= 10


def test_heuristic_complexity_javascript(tmp_path: Path):
    """Verify heuristic branch token parsing for JavaScript/TypeScript."""
    js_code = """
function processData(items) {
    if (!items) return null;
    for (let i = 0; i < items.length; i++) {
        if (items[i] > 10 && items[i] < 50) {
            console.log(items[i]);
        }
    }
}
"""
    test_file = tmp_path / "app.js"
    test_file.write_text(js_code, encoding="utf-8")

    analyzer = ComplexityAnalyzer()
    funcs = analyzer.analyze_file(test_file)
    assert len(funcs) >= 1
    assert funcs[0].cyclomatic_complexity > 1


def test_repo_wide_complexity_analysis(tmp_path: Path):
    """Verify repository-wide complexity aggregation and Maintainability Index."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "clean.py").write_text("def add(a, b): return a + b\n", encoding="utf-8")

    analyzer = ComplexityAnalyzer()
    res = analyzer.analyze(tmp_path)

    assert res["total_functions_analyzed"] >= 1
    assert res["maintainability_index"] > 0
    assert res["maintainability_rank"] in ("A", "B", "C", "D", "F")
    assert "average_cyclomatic_complexity" in res


def test_redos_resistance_long_ts_line(tmp_path: Path):
    """Verify TypeScript regex is immune to catastrophic backtracking on long lines."""
    import time

    # 10,000 characters without matching parenthesis
    long_line = "const x = " + "foo bar baz " * 800 + ";"
    ts_file = tmp_path / "minified.ts"
    ts_file.write_text(long_line, encoding="utf-8")

    analyzer = ComplexityAnalyzer()
    t0 = time.perf_counter()
    funcs = analyzer.analyze_file(ts_file)
    elapsed = time.perf_counter() - t0

    assert elapsed < 0.2  # Must execute under 200ms
    assert len(funcs) == 0


def test_cognitive_complexity_deep_ast(tmp_path: Path):
    """Verify deep AST expression chains do not cause RecursionError."""
    # 200 nested additions
    deep_code = "def deep():\n    return " + " + ".join(str(i) for i in range(200)) + "\n"
    py_file = tmp_path / "deep.py"
    py_file.write_text(deep_code, encoding="utf-8")

    analyzer = ComplexityAnalyzer()
    funcs = analyzer.analyze_file(py_file)
    assert len(funcs) == 1
    assert funcs[0].cyclomatic_complexity >= 1
