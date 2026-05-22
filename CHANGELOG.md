# Changelog

        ## [1.0.22] - 2026-05-22

        ### Changed
        * **Reliability:** Wrapped `CODEDNA_MAX_FILE_SIZE` environment variable parsing in `try...except ValueError` to prevent startup crashes when provided malformed strings. Pruned zero files.

        ## [1.0.21] - 2026-05-21

        ### Changed
        * **Reliability:** Fixed `git log` crashes on modern Git versions by upd

        // ... 6304 characters truncated (middle section) ...

        .
        * **Cleanup:** Removed unused orphaned scripts such as `update_security_detector.py`.
        * **Quality Assurance**: Deepcopy applied to `AIAnalyzer._minimize_payload` to prevent unintended mutation of the original dictionary data structures when building prompt payloads. Unused variable assignment removed from the test file and minor versions bumped.