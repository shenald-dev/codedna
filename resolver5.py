import subprocess
import re

def fix_file(file):
    with open(file, 'r') as f:
        content = f.read()

    # We want to keep both learnings in bolt.md
    if file == '.jules/bolt.md':
        content = re.sub(r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?\n)>>>>>>> origin/master\n", r"\1\n\2", content, flags=re.DOTALL)
    # For evolution engine we keep our tformat logic
    elif file == 'codedna/analyzers/evolution_engine.py':
        content = re.sub(r"<<<<<<< HEAD\n(.*?)\n=======\n.*?\n>>>>>>> origin/master\n", r"\1\n", content, flags=re.DOTALL)
    else:
        # Accept theirs for everything else
        content = re.sub(r"<<<<<<< HEAD\n.*?\n=======\n(.*?)\n>>>>>>> origin/master\n", r"\1\n", content, flags=re.DOTALL)

    with open(file, 'w') as f:
        f.write(content)

for file in [".jules/bolt.md", ".jules/warden.md", "CHANGELOG.md", "codedna/analyzers/code_smell_detector.py", "codedna/analyzers/dependency_mapper.py", "codedna/analyzers/evolution_engine.py", "codedna/analyzers/security_detector.py", "codedna/cli.py", "pyproject.toml"]:
    try:
        fix_file(file)
        subprocess.run(["git", "add", file])
    except FileNotFoundError:
        pass

subprocess.run(["git", "commit", "-m", "Merge master"])
