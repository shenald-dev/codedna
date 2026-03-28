YYYY-MM-DD — Assessment & Lifecycle
Observation / Pruned:
The dependency map OS error test (`test_map_handles_oserror_on_read`) previously used a global mock for `sys.modules['networkx']`. This created unpredictable state leakage in `pytest` when `networkx` was already imported by `DependencyMapper` elsewhere in the test suite, causing an assertion failure (`AssertionError: 2 != 1`). The test was failing because real `networkx.DiGraph` implicitly adds node components to graphs during edge creation.
Alignment / Deferred:
Removed the fragile `sys.modules` patching entirely and transitioned to using the real `networkx` instance in tests. Updated the mock `ok.py` file to prevent injecting an external dependency edge (previously `import sys`), keeping the deterministic expectation strictly at `total_modules == 1`. Applied extensive `ruff` autofixes and cleanups to remove unused imports across the codebase.
