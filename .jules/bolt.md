## 2026-04-01 — Performance Optimization: O(N^2) Bottleneck in Long Function Detection

Learning:
An O(N^2) algorithmic bottleneck existed in `CodeSmellDetector._detect_long_functions` when parsing deeply nested functions or processing large Python files. The previous implementation utilized nested loops that iterated ahead through remaining lines for every function discovered, causing analysis time to jump from sub-second to over 35 seconds on deeply nested blocks.

Action:
Replaced the lookahead nested loop with a single-pass O(N) stack-based approach that tracks active functions and their indentation levels. The execution time for the stress test on deeply nested mock repositories was reduced from ~35 seconds down to ~0.04 seconds, greatly improving the scalability of the analysis phase.

2026-04-02 — Security Scanner Performance Bottleneck
Learning: Running multiple complex regular expressions sequentially over every file's content is a severe performance bottleneck. Profiling `SecurityDetector` revealed that `pattern.finditer` took ~76% of the execution time, scanning for secrets that often have known, fixed prefixes (like `AKIA` or `sk_live_`).
Action: For heavily repeated regex scans, I added a fast-path literal substring check (`SECRET_HINTS`) before executing the expensive regex. Files lacking the literal substring immediately skip the regex. This drastically reduced the execution time of `SecurityDetector.detect` by avoiding the regex engine entirely on the vast majority of files.
