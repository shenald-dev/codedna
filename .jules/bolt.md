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

## 2026-03-23 — Optimize Regex Line Number Lookups in `SecurityDetector`

Learning:
When matching regex patterns across large multi-line strings, evaluating `content[:match.start()].count('\n') + 1` for each match triggers an O(N) operation per match. For files with many matches or long contents, this leads to an O(N*M) bottleneck.

Action:
Pre-calculate the end indices for all lines in the file (`[i for i, char in enumerate(content) if char == '\n']`), and use `bisect.bisect_right` on the line ends array to look up the line number in O(log L) time per match, drastically reducing processing time for large codebases.
