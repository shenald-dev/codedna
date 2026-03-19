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
