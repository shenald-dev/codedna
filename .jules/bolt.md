## 2026-04-01 — Performance Optimization: O(N^2) Bottleneck in Long Function Detection

        Learning:
        An O(N^2) algorithmic bottleneck existed in `CodeSmellDetector._detect_long_functions` when parsing deeply nested functions or processing large Python files. The previous implementation utilized nested loops that iterated ahead through remaining lines for every function discovered, causing analysis time to jump from sub-second to over 35 seconds on deeply nested blocks.

        Action:
        Replaced the lookahead nested loop with a single-pass O(N) stack-based approach that tracks active functions and their indentation levels. The executio

        // ... 20804.6 characters truncated (middle section) ...

         redundant len() computations. Avoiding inner O(N) sum calculations over directory file listings also improves performance.
        Action: Refactored _walk in ArchitectureDetector to yield depth directly instead of re-splitting paths, and implemented lazy file_count caching in StructureAnalyzer.