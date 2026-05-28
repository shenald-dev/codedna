## 2026-04-01 — Performance Optimization: O(N^2) Bottleneck in Long Function Detection
        ... (truncated middle) ...
        ## 2026-05-21 — Fix N+1 Performance Bottleneck in Evolution Engine
        Learning:
        Accessing `commit.stats.total` via `repo.iter_commits` in GitPython spawns an individual `git diff` sub-process per commit, causing severe N+1 bottlenecks on large repositories.
        Action:
        Replaced the loop over `commit.stats` with a single, batched raw `repo.git.log('--shortstat', ...)` call, reducing execution time significantly.
        ## 2026-05-27 — Fix lstrip Path Prefix Bug
        Learning:
        When stripping path prefixes like `./` or `../` in Python, `str.lstrip("./")` treats the argument as a set of characters and strips all combinations of those characters from the start of the string (e.g., corrupting `../.env` into `env`).
        Action:
        Use exact prefix removal methods like regex substitution (`re.sub(r"^(?:\.\.?/)+", "", dep)`) or explicit string slicing instead of `lstrip` to prevent path corruption.