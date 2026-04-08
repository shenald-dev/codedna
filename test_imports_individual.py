import time
modules = [
    "codedna.analyzers.ai_analyzer",
    "codedna.analyzers.architecture_detector",
    "codedna.analyzers.code_smell_detector",
    "codedna.analyzers.dependency_mapper",
    "codedna.analyzers.developer_analyzer",
    "codedna.analyzers.dna_generator",
    "codedna.analyzers.evolution_engine",
    "codedna.analyzers.github_analyzer",
    "codedna.analyzers.language_detector",
    "codedna.analyzers.repo_cloner",
    "codedna.analyzers.security_detector",
    "codedna.analyzers.structure_analyzer",
    "codedna.visualization.html_export",
    "codedna.visualization.renderer",
]

for mod in modules:
    start = time.time()
    __import__(mod)
    print(f"{mod}: {time.time() - start:.4f}")
