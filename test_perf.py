import time
from pathlib import Path
from codedna.analyzers.developer_analyzer import DeveloperAnalyzer
from codedna.analyzers.evolution_engine import EvolutionEngine

repo_path = Path(".git").resolve().parent

start = time.time()
DeveloperAnalyzer().analyze(repo_path, max_commits=500)
print("DeveloperAnalyzer:", time.time() - start)

start = time.time()
EvolutionEngine().analyze(repo_path, snapshots=6)
print("EvolutionEngine:", time.time() - start)
