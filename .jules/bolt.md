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

## 2026-03-26 — Optimize Code Smell and Security Detection

Learning:
Using `.splitlines()` and looping over every line to run a regex search is significantly slower than using `.finditer()` on the whole file content, even if we need line numbers later. The C implementation of the regex engine is much faster at scanning the text. We also discovered that eagerly computing newline positions via `.finditer(r'\n', content)` was adding unnecessary overhead to every scanned file in `SecurityDetector`, even those without secrets.

Action:
Replaced `.splitlines()` iterations in `CodeSmellDetector` for `TODO`/`FIXME` markers with `MARKER_PATTERN.finditer(content)`. For line numbers, compute newline positions lazily using `bisect` only when a match is found. Also updated `SecurityDetector` to delay computing the newline positions array until a secret match is actually identified.
## 2026-03-29 — Optimize slow regex patterns
Learning: Regex using re.IGNORECASE flag limits the engine from employing Boyer-Moore optimization on literal parts of the string.
Action: Removed IGNORECASE matching for SECRET_PATTERNS and MARKER_PATTERN, employing explicit alternative cases instead. Added exact start anchors to JS matching. This shaves ~300ms from normal analyzer execution.

## 2026-03-30 — Optimize Regex Performance with Non-Capturing Groups

Learning:
When using `re.findall` or similar methods simply to count the number of matches in a string (e.g., `len(PATTERN.findall(content))`), capturing groups `(...)` inside the pattern cause the `re` engine to allocate additional memory for the captured substrings. This results in unnecessary overhead, especially when scanning large files with many matches.

Action:
Replaced capturing groups `(...)` with non-capturing groups `(?:...)` in `JS_METHOD_PATTERN` and `JAVA_METHOD_PATTERN` within `CodeSmellDetector` where the primary goal is just counting the matches. This provides a small, measurable performance improvement during the analysis phase for JavaScript and Java codebases without altering behavior.

## 2026-03-30 — Avoid catastrophic backtracking in multiline regular expressions

Learning:
Using unbounded matching characters like `\s*` at the beginning of regular expressions combined with `re.MULTILINE` leads to extreme catastrophic backtracking when executing over large multi-line strings with scarce matches. The regex engine re-evaluates `\s*` across thousands of newlines attempting to match the subsequent literal characters, leading to massive O(N²) execution times on failed matches.

Action:
Replaced `^\s*` with `^[ \t]*` in the regular expressions within `codedna/analyzers/dependency_mapper.py` for mapping imports across languages. Restricting the match to horizontal whitespace prevents the engine from crossing newline boundaries while searching, achieving ~500x speedup (from 56 seconds to 0.1 seconds in synthetic benchmarks) for large files without altering the matching behavior.

## 2026-04-12 — Memory Efficiency when Counting Regex Matches

Learning:
When simply counting the number of occurrences of a regular expression pattern in a large string, using `len(PATTERN.findall(content))` creates a large intermediate list containing all the matched substrings in memory. For extremely large files with many matches, this can cause significant memory allocation overhead.

Action:
Instead of `len(PATTERN.findall(content))`, use the generator expression `sum(1 for _ in PATTERN.finditer(content))` to lazily evaluate matches. This effectively turns an O(N) memory allocation into an O(1) memory operation, making analyzers like `CodeSmellDetector` significantly more memory-efficient when analyzing large source files.
