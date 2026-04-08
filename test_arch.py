import time
from pathlib import Path
from codedna.analyzers.architecture_detector import ArchitectureDetector

repo_path = Path(".git").resolve().parent
analyzer = ArchitectureDetector()

start = time.time()
for _ in range(100):
    analyzer.detect(repo_path)
print("Before:", time.time() - start)
