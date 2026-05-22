@@ -1,5 +1,10 @@
 # Changelog
 
+## [1.0.21] - 2026-05-21
+
+### Changed
+* **Reliability:** Fixed `git log` crashes on modern Git versions by updating custom literal format strings to use the `tformat:` prefix instead of `format:` in `DeveloperAnalyzer` and `EvolutionEngine`. Pruned zero files.
+
 ## [1.0.20] - 2026-05-20
 
 ### Changed