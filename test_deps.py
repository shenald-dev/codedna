import time
from pathlib import Path
from codedna.analyzers.dependency_mapper import DependencyMapper

repo_path = Path(".git").resolve().parent
mapper = DependencyMapper()

start = time.time()
for _ in range(10):
    mapper.map(repo_path)
print("Dependencies:", time.time() - start)
