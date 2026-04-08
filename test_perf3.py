import time
from pathlib import Path
from codedna.analyzers.structure_analyzer import StructureAnalyzer

repo_path = Path(".git").resolve().parent
analyzer = StructureAnalyzer()

start = time.time()
for _ in range(100):
    analyzer.analyze(repo_path)
print("Before:", time.time() - start)
