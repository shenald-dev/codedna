import subprocess

def fix_file(file):
    with open(file, 'r') as f:
        content = f.read()

    import re
    # Remove markers and prefer HEAD (our branch) for .jules/bolt.md
    if file == '.jules/bolt.md':
        content = re.sub(r"<<<<<<< HEAD\n(.*?)\n=======\n.*?\n>>>>>>> origin/master\n", r"\1\n", content, flags=re.DOTALL)
    # For others prefer origin/master (their changes) because we already resolved bolt.md and our previous code edits were non-conflicting.
    else:
        content = re.sub(r"<<<<<<< HEAD\n.*?\n=======\n(.*?)\n>>>>>>> origin/master\n", r"\1\n", content, flags=re.DOTALL)

    with open(file, 'w') as f:
        f.write(content)

for file in [".jules/bolt.md", ".jules/warden.md", "CHANGELOG.md", "codedna/analyzers/code_smell_detector.py", "codedna/analyzers/dependency_mapper.py", "codedna/analyzers/security_detector.py", "codedna/cli.py", "pyproject.toml"]:
    fix_file(file)
    subprocess.run(["git", "add", file])

subprocess.run(["git", "commit", "-m", "Merge master"])
