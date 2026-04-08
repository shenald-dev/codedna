import time
from pathlib import Path
from codedna.analyzers.language_detector import LanguageDetector

repo_path = Path(".git").resolve().parent
analyzer = LanguageDetector()

start = time.time()
for _ in range(100):
    analyzer.detect(repo_path)
print("LanguageDetector:", time.time() - start)
