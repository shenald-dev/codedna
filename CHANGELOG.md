# Changelog

## [1.0.7] - 2026-05-02

### Changed
* **Performance:** Fixed Out-Of-Memory (OOM) hangs during the dependency mapping phase by capping the number of evaluated paths from `nx.simple_cycles` to a maximum of 10. The extraction is now safely lazily evaluated using `itertools.islice`.

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