with open(".jules/bolt.md", "r") as f:
    content = f.read()

content = content.replace(
"""<<<<<<< HEAD

=======
## 2026-05-27 — Performance & Reliability Optimizations
Learning: Inline standard library imports in frequently called methods add execution overhead, and failing to log when falling back from malformed environment variables limits user visibility.
Action: Hoisted inline imports to module level scope to improve execution speed and added logging.warning within try/except ValueError blocks when parsing CODEDNA_MAX_FILE_SIZE to ensure safe fallback with clear feedback.
>>>>>>> origin/master""",
"""## 2026-05-27 — Performance & Reliability Optimizations
Learning: Inline standard library imports in frequently called methods add execution overhead, and failing to log when falling back from malformed environment variables limits user visibility.
Action: Hoisted inline imports to module level scope to improve execution speed and added logging.warning within try/except ValueError blocks when parsing CODEDNA_MAX_FILE_SIZE to ensure safe fallback with clear feedback.
"""
)

with open(".jules/bolt.md", "w") as f:
    f.write(content)
