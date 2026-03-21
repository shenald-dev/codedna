## 2026-03-17 — Optimize Repository Traversals and File Reading

Learning:
Recursive directory traversals in Python risk `RecursionError` for deeply nested directories and have overhead. Reading entire files into memory using `read_text().splitlines()` is a major bottleneck for large repositories. Iterating through large files to check multiple substrings repeatedly is inefficient.

Action:
Replaced all recursive directory `_walk` methods with iterative, stack-based traversal (DFS). Replaced `read_text().splitlines()` with a memory-efficient generator `sum(1 for _ in f)`. Replaced multiple substring checks with a single compiled regular expression search for code marker detection.

## 2026-03-19 — Test Suite Performance

Learning:
Tests were performing real network requests (GitHub API) resulting in a slow execution time (over half of the test suite time). This made tests flaky due to rate limiting and slow due to network latency.

Action:
Ensure any external network call in `tests` uses mocking (like `unittest.mock.patch`). Added mocking to `TestGitHubAnalyzer.test_analyze_github_url` to avoid actual web requests, significantly speeding up the whole test suite.

## 2026-03-20 — Refactor missing recursive directory traversals

Learning:
While most recursive directory traversals were optimized to use iterative stack-based traversal (DFS), `SecurityDetector._walk_source` was missed. This inconsistency could still lead to `RecursionError` and overhead in deeply nested large repositories.

Action:
Replaced the recursive directory `_walk_source` method in `SecurityDetector` with the standardized iterative stack-based traversal (DFS) to safely process deeply nested trees.

## 2026-03-22 — Optimize Regex and Memory usage in Security Detector

Learning:
The `SecurityDetector` was taking an excessive amount of time (over 80s for Python's standard library) due to regex engine bottlenecks. The use of boundary markers `\b`, case insensitivity `(?i)`, and complex unbounded prefixes (e.g., `(?i)(?:key|token|...)[\s:=]+['\"]`) forces the regex engine to abandon fast Boyer-Moore literal searching. Additionally, calculating line numbers by creating large substrings (`content[:match.start()].count('\n')`) caused massive memory allocations and slowdowns.

Action:
Replaced slow regex patterns with fast literal-first searches (e.g., finding quoted strings first, then verifying the left context manually or with a strict anchored regex). Removed `\b` bounds and `(?i)` where the secret structure allowed (like `AKIA` which is always uppercase). Replaced string slicing with bounded counts (`content.count('\n', 0, match.start())`) to avoid memory copies. This reduced scanning time of the Python stdlib from ~84s to ~8s.
