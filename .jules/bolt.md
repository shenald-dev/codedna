## 2024-11-03 — Optimized Security Regex

- **Learning:** Found a catastrophic backtracking issue in `VULN_PATTERNS` in `codedna/analyzers/security_detector.py`. Using greedy matches (`.*`) in `Raw SQL String Injection` regex can cause hangs over 400 seconds on large source files with padded spaces.
- **Action:** Optimized the regexes to use non-greedy matching `[^{}\n]+?` and explicitly avoid catastrophic backtracking when searching for SQL/Command Injections. Future updates to `VULN_PATTERNS` should avoid `.*` and carefully consider backtracking vulnerabilities.

## 2024-11-05 — Optimized Dependency Mapper Regex

- **Learning:** Catastrophic backtracking in `dependency_mapper.py` caused O(2^N) hangs on large files when parsing JS/TS `import` regexes with `.*?`.
- **Action:** Replaced `.*?` with a non-greedy bounded negation `(?:[^'"]){1,250}?` to safely limit matching scope and explicitly avoid backtracking in all future regexes.

## 2024-11-06 — Optimized Text Parsing Memory Usage

- **Learning:** Memory overhead from `content.splitlines()` on large source files introduces serious performance and garbage collection bottlenecks in iterative functions.
- **Action:** Optimized core parsing operations to perform `pattern.finditer(content)` in C across the entire string and calculate line indices optimally using `content.count('\n', last_idx, start_idx)` to maintain precise bounds dynamically.
