import sys

def run():
    with open(".jules/bolt.md", "r") as f:
        content = f.read()

    start_str = "<<<<<<< HEAD\n"
    end_str = ">>>>>>> origin/master\n"

    if start_str in content and end_str in content:
        start_idx = content.find(start_str)
        end_idx = content.find(end_str) + len(end_str)

        replacement = """## 2026-05-26 — Fix: Git log format specifier

Learning:
When using GitPython to execute batched `git log` commands with a custom literal string format, strictly use the prefix `tformat:` (e.g., `--format=tformat:COMMIT`) instead of `format:` or just `--format=COMMIT`. Modern Git versions reject the un-prefixed version with a "fatal: invalid --pretty format" error, but using `format:` alters output semantics (separator vs. terminator) and breaks downstream parsing logic that expects standard `tformat` behavior.

Action:
Strictly prepend custom format strings with `tformat:` when making `git log` calls via GitPython to guarantee cross-version reliability and avoid suppressed exceptions.
"""
        new_content = content[:start_idx] + replacement + content[end_idx:]
        with open(".jules/bolt.md", "w") as f:
            f.write(new_content)
        print("Fixed conflict.")
    else:
        print("Could not find conflict markers.")

run()
