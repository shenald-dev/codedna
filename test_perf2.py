import time
from pathlib import Path
from codedna.analyzers.structure_analyzer import StructureAnalyzer
from codedna.analyzers.language_detector import LanguageDetector

repo_path = Path(".git").resolve().parent

start = time.time()
StructureAnalyzer().analyze(repo_path)
print("StructureAnalyzer:", time.time() - start)

start = time.time()
LanguageDetector().detect(repo_path)
print("LanguageDetector:", time.time() - start)
