## 2026-11-03 — Lifecycle & Assurance Ledger
- **QA & Veto Actions:** None
- **Entropy Pruned:** Removed dead code `details` field from `PolicyEvaluation` in `codedna/ci/gatekeeper.py`. Net lines deleted: 7.
- **Entropy Pruned:** Removed unused error constants (`PARSE_ERROR`, `INVALID_REQUEST`, `INVALID_PARAMS`, `INTERNAL_ERROR`) in `codedna/mcp/protocol.py` and unused `line_no` parameter in `_make_diff` within `codedna/remediation/planner.py`.
- **Deferred / Blocked:** None
## 2026-11-06 — Lifecycle & Assurance Ledger
- **QA & Veto Actions:** Verified APEX-BOLT commit 2492528. The regex finditer optimization successfully improved performance and test coverage is stable.
- **Entropy Pruned:** None for this run as unused code detected by Vulture were required fields for schemas (e.g. mcp protocol inputSchema) and dataclasses, or CLI endpoints.
- **Deferred / Blocked:** None
