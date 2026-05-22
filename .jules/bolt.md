@@ -200,3 +200,17 @@ Removed the `try/except ValueError` block containing `.relative_to(repo_path)` a
 2023-10-27 — Optimization: Avoid redundant file system traversal string splitting and operations
 Learning: Traversing a directory system inherently has logic about child-depth that can avoid redundant len() computations. Avoiding inner O(N) sum calculations over directory file listings also improves performance.
 Action: Refactored _walk in ArchitectureDetector to yield depth directly instead of re-splitting paths, and implemented lazy file_count caching in StructureAnalyzer.
+## 2026-05-19 — Git Log Formatting Bug Fix
+
+Learning:
+Git format strings that do not contain a `%` placeholder or the `tformat:` / `format:` prefix are rejected with a fatal error in newer versions of Git, which silently suppressed extraction logic in the evolution engine due to broad try/except blocks.
+
+Action:
+Strictly prepend custom format strings with `tformat:` when making `git log` calls via GitPython to guarantee cross-version reliability and avoid suppressed exceptions.
+## 2026-05-21 — Configure Max File Size
+
+Learning:
+Parsing environment variables inside tight file iteration loops causes severe CPU blocking and latency.
+
+Action:
+Always extract configurable limits (e.g. `os.environ.get('CODEDNA_MAX_FILE_SIZE', ...)`) to module-level scope so they are parsed only once rather than redundantly per file.