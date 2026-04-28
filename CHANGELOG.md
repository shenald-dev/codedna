# Changelog

## [1.0.13] - 2026-04-27

### Changed
* **Performance:** Moved `console = Console()` instantiations from the global module level in `repo_cloner.py` and `renderer.py` to their respective `__init__` methods. This defers the heavy load of initializing `rich.console.Console` until the classes are actually used, effectively improving the startup time of the CodeDNA CLI.

## [1.0.12] - 2026-04-26

### Changed
* **Performance:** Extracted the length calculation of `contributor_files.get(author, set())` into a variable within the main loop of `DeveloperAnalyzer.analyze` to eliminate redundant dictionary lookups and length computations.

## [1.0.11] - 2026-04-19

### Changed
* **Performance:** Move lazy imports to module level to eliminate the repeated `sys.modules` lookup overhead during large-scale repository scans.

## [1.0.10] - 2026-04-18

### Fixed
* **Security:** Prevented Cross-Site Scripting (XSS) vulnerabilities in GitHub stats within `html_export.py` by ensuring non-numeric string values returned from the numeric formatter are properly escaped using `html.escape`. Added adversarial testing to verify escaping of malicious inputs in GitHub metrics.

## [1.0.9] - 2026-04-17

### Fixed
* **Security:** Prevented Cross-Site Scripting (XSS) vulnerabilities in `html_export.py` by ensuring all profile data interpolated into the HTML templates is properly escaped using `html.escape`. Added adversarial testing to verify escaping of malicious inputs.

## [1.0.8] - 2026-04-16

### Changed
* **Performance:** Optimized CLI startup time via lazy loading by moving heavy module imports inside the specific methods where they are used.

## [1.0.7] - 2026-04-16

### Changed
* **Reliability:** Capped the execution of `nx.simple_cycles` in `DependencyMapper` to a maximum of 10 cycles. This prevents infinite-seeming hangs and out-of-memory (OOM) crashes on heavily coupled, dense dependency graphs where cycle generation is exponential.

## [1.0.6] - 2026-04-16

### Changed
* **Performance:** Optimized `SecurityDetector` by using fast-path literal substring hints (`SECRET_HINTS`) before executing expensive regular expressions (`pattern.finditer()`). This drastically reduces overhead when scanning files that do not contain potential secrets.
* **Cleanup:** Removed unused `prev_indent` variable in `CodeSmellDetector` to ensure codebase remains entropy-free.

## [1.0.5] - 2026-04-15

### Changed
* **Code Quality:** Added adversarial tests for `CodeSmellDetector` to verify multiline marker extraction logic.
* **Cleanup:** Pruned unused `clear` method in `CacheManager` and unused `version` command in `cli.py`.

## [1.0.4] - 2026-03-31

### Changed
* **Code Quality:** Fixed various line length issues, ambiguous variable names, and unused variables. Added `# noqa: E501` to long lines in HTML exports where splitting them would cause template fragmentation. Removed unused `source_path` parameter from `_normalize_import` in `codedna/analyzers/dependency_mapper.py`. Added `# noqa: E402` to `tests/test_repo_cloner.py` to suppress module import level warnings.

## [1.0.3] - 2026-03-29

### Fixed
* **Regex Regression:** Reverted aggressive use of `re.MULTILINE` in `PY_METHOD_PATTERN` and `PY_FUNC_START_PATTERN` within `code_smell_detector.py`. The `\s*` token was improperly matching newlines, causing Python method detection logic to erroneously consume multiple blank lines and break functional counts. Added adversarial tests to ensure survival.

## [1.0.2] - 2026-03-29

### Changed
* **Dependencies:** Added `networkx`, `pytest-cov`, and `pytest-profiling` to the test suite setup instructions, ensuring `tests/test_dependency_mapper_errors.py` correctly interacts with the dependency mapping logic.
* **Code Quality:** Fixed minor issues and enforced `ruff check` linting fixes across the repository, improving code cleanliness without altering functionality.

## [1.0.1] - 2026-03-27

### Changed
* **Testing:** Replaced the global `sys.modules['networkx']` mock with real networkx execution in `test_dependency_mapper_errors.py` to fix unpredictable graph node injection across tests. Empty mocked files now properly limit `total_modules` resolution to 1.
* **Code Quality:** Removed stale unused imports globally utilizing aggressive `ruff check --fix` policies.
* **Cleanup:** Removed unused orphaned scripts such as `update_security_detector.py`.