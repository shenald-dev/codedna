# Changelog

## [1.0.26] - 2026-05-28

### Fixed
* **Reliability:** Fixed `logging.warning` to use module-level logger.

## [1.0.25] - 2026-05-27
### Fixed
* **Reliability:** Replaced `str.lstrip` with regex substitution in `DependencyMapper._normalize_import` to prevent corrupting valid path components when removing relative prefixes like `./` or `../`.

## [1.0.24] - 2026-05-24
### Changed
* **Performance:** Verified the optimization in `EvolutionEngine` that replaces N+1 `git log` sub-processes with a single batched history parse.

## [1.0.23] - 2026-05-22

### Changed
* **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings.

## [1.0.22] - 2026-05-21
### Changed
* **Reliability:** Fixed `git log` crashes on modern Git versions by updating custom literal format strings to use the `tformat:` prefix instead of `format:` in `DeveloperAnalyzer` and `EvolutionEngine`.

## [1.0.21] - 2026-05-20
* **Performance:** Removed the redundant `.relative_to` path string processing per file inside `ArchitectureDetector._walk` and optimized the file counting in `StructureAnalyzer`.
* **Testing:** Added adversarial unit tests in `tests/test_architecture_detector.py` to verify the path splitting optimization and ensure `_walk` accurately traverses directory structures while correctly bypassing ignored and hidden directories.
* **Cleanup:** Verified clean code state using static analysis (`vulture`, `ruff`), leaving 0 unused files. Updated `pip` and `playwright` dependencies to latest safe patch releases.

## [1.0.18] - 2026-05-05

### Changed
* **Quality Assurance:** Applied `copy.deepcopy` to the cloned payload in `AIAnalyzer._minimize_payload()` to prevent mutating the original `raw_dna_profile` and removed an unused `api_key` assignment in `tests/test_ai_analyzer.py`.

## [1.0.17] - 2026-05-04

### Changed
* **Performance:** Replaced iterative `commit.stats.files` and `commit.tree.traverse()` property access with batched `repo.git.log` and `repo.git.ls_tree` commands in `DeveloperAnalyzer` and `EvolutionEngine` to eliminate severe N+1 git subprocess overhead during deep history analysis.
* **Cleanup:** Pruned the mocked and invalid test `tests/test_perf_analyzers.py`. Updated minor and patch dependencies.

## [1.0.16] - 2026-05-03

### Changed
* **Performance:** Replaced unbounded temporary arrays with running scalar aggregates across `ArchitectureDetector`, `StructureAnalyzer`, `DeveloperAnalyzer`, and `LanguageDetector`. This eliminates unnecessary memory overhead and avoids redundant `O(N)` aggregate function calls (e.g., `sum()`, `len()`).
* **Cleanup:** Verified clean architecture via Vulture and retained latest non-breaking dependency versions.

## [1.0.15] - 2026-05-19

### Changed
* **Cleanup:** Pruned unused `api_key` attribute assignment in `tests/test_ai_analyzer.py` discovered via static analysis.

## [1.0.14] - 2026-04-29

### Changed
* **Performance:** Optimized `_detect_collaboration` in `DeveloperAnalyzer` to use `itertools.combinations` instead of manual nested loops, improving performance when calculating developer pair collaborations.
* **Testing:** Added test coverage for `_detect_collaboration` threshold logic.

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
* **Quality Assurance**: Deepcopy applied to `AIAnalyzer._minimize_payload` to prevent unintended mutation of the original dictionary data structures when building prompt payloads. Unused variable assignment removed from the test file and minor versions bumped.
