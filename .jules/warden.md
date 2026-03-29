2026-03-29 — Assessment & Lifecycle
Observation / Pruned:
Discovered that `test_analyzers.py` and `test_dependency_mapper_errors.py` were failing locally without actual installation of `networkx` despite mocks in prior commits. Correctly configured the environment to use real implementations for network graph testing in `dependency_mapper.py` instead of brittle `sys.modules` patching. Re-applied aggressive `ruff check --fix` policies to purge any lingering ambiguous variable names and unused imports.

Alignment / Deferred:
Deferred resolving lines that exceed the standard PEP8 line length of 100 within HTML export strings and test JSON structures, as doing so requires massive architectural changes to `HTMLExporter` templates or test readability regressions.

2026-03-27 — Assessment & Lifecycle
Observation / Pruned:
The dependency map OS error test (`test_map_handles_oserror_on_read`) previously used a global mock for `sys.modules['networkx']`. This created unpredictable state leakage in `pytest` when `networkx` was already imported by `DependencyMapper` elsewhere in the test suite, causing an assertion failure (`AssertionError: 2 != 1`). The test was failing because real `networkx.DiGraph` implicitly adds node components to graphs during edge creation.
Alignment / Deferred:
Removed the fragile `sys.modules` patching entirely and transitioned to using the real `networkx` instance in tests. Updated the mock `ok.py` file to prevent injecting an external dependency edge (previously `import sys`), keeping the deterministic expectation strictly at `total_modules == 1`. Applied extensive `ruff` autofixes and cleanups to remove unused imports across the codebase.