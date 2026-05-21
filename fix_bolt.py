with open(".jules/bolt.md", "r") as f:
    content = f.read()

content = content.replace(
"""<<<<<<< HEAD

=======
## 2026-05-21 — Configure Max File Size

Learning:
Parsing environment variables inside tight file iteration loops causes severe CPU blocking and latency.

Action:
Always extract configurable limits (e.g. `os.environ.get('CODEDNA_MAX_FILE_SIZE', ...)`) to module-level scope so they are parsed only once rather than redundantly per file.
>>>>>>> origin/master""",
"""## 2026-05-21 — Configure Max File Size

Learning:
Parsing environment variables inside tight file iteration loops causes severe CPU blocking and latency.

Action:
Always extract configurable limits (e.g. `os.environ.get('CODEDNA_MAX_FILE_SIZE', ...)`) to module-level scope so they are parsed only once rather than redundantly per file.
"""
)

with open(".jules/bolt.md", "w") as f:
    f.write(content)
