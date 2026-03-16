## 2024-05-24 — Path.rglob("*") scans ignored directories

Learning:
Using `Path.rglob("*")` alongside a filter like `if item.name not in IGNORE_DIRS` is a hidden performance bottleneck. `rglob` will still traverse entirely inside ignored directories (like `node_modules` or `.git`), performing unnecessary file stat operations on thousands of files.

Action:
Avoid `rglob("*")` when traversing repositories. Implement custom recursive directory walking using `os.walk` (modifying `dirnames` in-place) or custom `Path.iterdir()` recursion to prune ignored directories early.
