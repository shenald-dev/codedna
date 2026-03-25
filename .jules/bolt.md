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

## 2025-03-05 — Fixing O(N²) Bottleneck in `_detect_long_functions`

Learning:
The `_detect_long_functions` method in `code_smell_detector.py` previously computed line numbers for each detected Python function by running `content[:match.start()].count("\n")`. This created a massive O(N²) memory allocation and CPU bottleneck when processing large files, as it duplicated the string content preceding each function and rescanned it for newlines.

Action:
Replaced the full-string regex search (`re.finditer`) and newline counting logic with a line-by-line traversal using `content.splitlines()` and `enumerate(lines)`. By calling `.match()` on each line directly and avoiding slice-based iterations (`lines[i+1:]`) via index-based iteration (`range(i+1, len(lines))`), the performance of function extraction in Python files was significantly improved (from ~57 seconds to ~3 seconds on extremely large files in synthetic benchmarks).

## 2026-03-24 — Fixing NameError Regression in SecurityDetector

Learning:
During a repository traversal refactor in `SecurityDetector._walk_source`, the loop variable was renamed from `item` to `file_path`. However, the references to the file name in `SecurityDetector.detect` for dependency manifests (`package.json` and `requirements.txt`) were not updated, resulting in a `NameError` that caused `test_detect_secrets` to fail completely.

Action:
Updated the dependency manifest checks in `SecurityDetector.detect` to correctly use `file_path.name` instead of `item.name`. Always verify that loop variable renames are consistently applied across the entire scope of the loop body to avoid correctness bugs and test failures.

## 2026-04-10 — SecurityDetector Performance & Multiline Regression Bottleneck

Learning:
String slicing and newline counting (`content[:match.start()].count('\n')`) inside a regex `finditer` loop causes severe O(N^2) slowdowns on large files with many matches due to repeated large string copies. However, iterating line-by-line via `splitlines()` hurts average case performance by executing regex matches `N_lines * M_patterns` times in Python instead of once in C, and breaks multiline pattern support.

Action:
Pre-compute newline offsets via `newline_positions = [m.start() for m in re.finditer(r'\n', content)]` and use binary search (`bisect.bisect_right(newline_positions, match.start())`) to calculate line numbers. This achieves O(log N) lookup time for matches without compromising multiline match semantics or average case scanning speed.
