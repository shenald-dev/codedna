import re

# Resolve dependency_mapper.py
with open("codedna/analyzers/dependency_mapper.py", "r") as f:
    content = f.read()

# Since we want to use the regex fix, we find the conflict block and replace it
# The conflict block will have <<<<<<<, =======, >>>>>>>
content = re.sub(
    r"<<<<<<< HEAD\n.*?=======\n\s*def _normalize_import\(self, dep: str\) -> str:\n.*?>>>>>>> origin/master\n",
    r"    def _normalize_import(self, dep: str) -> str:\n        return re.sub(r'^(?:\.\./|\./)+', '', dep)\n",
    content,
    flags=re.DOTALL
)
# Let's handle variations. It's safer to just do a string replacement.
