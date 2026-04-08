import time
start = time.time()
from codedna.analyzers.ai_analyzer import AIAnalyzer
from codedna.analyzers.architecture_detector import ArchitectureDetector
from codedna.analyzers.code_smell_detector import CodeSmellDetector
from codedna.analyzers.dependency_mapper import DependencyMapper
from codedna.analyzers.developer_analyzer import DeveloperAnalyzer
from codedna.analyzers.dna_generator import DNAGenerator
from codedna.analyzers.evolution_engine import EvolutionEngine
from codedna.analyzers.github_analyzer import GitHubAnalyzer
from codedna.analyzers.language_detector import LanguageDetector
from codedna.analyzers.repo_cloner import RepoCloner
from codedna.analyzers.security_detector import SecurityDetector
from codedna.analyzers.structure_analyzer import StructureAnalyzer
from codedna.visualization.html_export import HTMLExporter
from codedna.visualization.renderer import Renderer
print("Imports time:", time.time() - start)
