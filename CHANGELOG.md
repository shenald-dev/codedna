# Changelog

## [1.0.2] - 2026-03-29

### Changed
* **Dependencies:** Added `networkx`, `pytest-cov`, and `pytest-profiling` to the test suite setup instructions, ensuring `tests/test_dependency_mapper_errors.py` correctly interacts with the dependency mapping logic.
* **Code Quality:** Fixed minor issues and enforced `ruff check` linting fixes across the repository, improving code cleanliness without altering functionality.

## [1.0.1] - 2026-03-27

### Changed
* **Testing:** Replaced the global `sys.modules['networkx']` mock with real networkx execution in `test_dependency_mapper_errors.py` to fix unpredictable graph node injection across tests. Empty mocked files now properly limit `total_modules` resolution to 1.
* **Code Quality:** Removed stale unused imports globally utilizing aggressive `ruff check --fix` policies.
* **Cleanup:** Removed unused orphaned scripts such as `update_security_detector.py`.