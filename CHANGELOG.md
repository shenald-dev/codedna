@@ -1,5 +1,10 @@
  # Changelog
  
+## [1.0.23] - 2026-05-24
+
+### Changed
+* **Performance:** Verified the optimization in `EvolutionEngine` that replaces N+1 `git log` sub-processes with a single batched history parse. Pruned zero files.
+
  ## [1.0.22] - 2026-05-22
  
  ### Changed