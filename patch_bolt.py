with open('.jules/bolt.md', 'r') as f:
    content = f.read()
import re
content = re.sub(r'<<<<<<< HEAD\n\n## 2026-05-26 — Performance Optimization: O\(N\) Traversal Bottleneck in Structure Analysis\n\nLearning:\nIn `StructureAnalyzer`, repeatedly executing `sum\(1 for p in items if p\.is_file\(\)\)` to calculate file counts for each module marker in a directory causes severe performance issues by running O\(N\) evaluations multiple times if there are multiple markers present\.\n\nAction:\nIntroduced lazy evaluation and caching via `file_count_cache` in the directory parsing loop\. The calculation is only performed once per directory, the first time a marker needs it, effectively reducing redundant calculations and keeping the operation optimized\.\n=======\n## 2026-05-21 — Configure Max File Size\n\nLearning:\nParsing environment variables inside tight file iteration loops causes severe CPU blocking and latency\.\n\nAction:\nAlways extract configurable limits \(e\.g\. `os\.environ\.get\(\'CODEDNA_MAX_FILE_SIZE\', \.\.\.\)`\) to module-level scope so they are parsed only once rather than redundantly per file\.\n>>>>>>> origin/master\n', r'''## 2026-05-21 — Configure Max File Size

Learning:
Parsing environment variables inside tight file iteration loops causes severe CPU blocking and latency.

Action:
Always extract configurable limits (e.g. `os.environ.get('CODEDNA_MAX_FILE_SIZE', ...)`) to module-level scope so they are parsed only once rather than redundantly per file.

## 2026-05-26 — Performance Optimization: O(N) Traversal Bottleneck in Structure Analysis

Learning:
In `StructureAnalyzer`, repeatedly executing `sum(1 for p in items if p.is_file())` to calculate file counts for each module marker in a directory causes severe performance issues by running O(N) evaluations multiple times if there are multiple markers present.

Action:
Introduced lazy evaluation and caching via `file_count_cache` in the directory parsing loop. The calculation is only performed once per directory, the first time a marker needs it, effectively reducing redundant calculations and keeping the operation optimized.
''', content, flags=re.DOTALL)
with open('.jules/bolt.md', 'w') as f:
    f.write(content)
