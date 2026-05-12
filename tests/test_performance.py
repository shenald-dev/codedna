import time
from pathlib import Path
from codedna.analyzers.structure_analyzer import StructureAnalyzer
from codedna.analyzers.architecture_detector import ArchitectureDetector

def test_structure_analyzer_performance(tmp_path):
    # Create 1000 dummy files in directories to measure iteration performance
    for i in range(100):
        d = tmp_path / f"dir_{i}"
        d.mkdir()
        for j in range(10):
            (d / f"file_{j}.py").write_text("")
        (d / "__init__.py").write_text("") # Add a marker

    analyzer = StructureAnalyzer()

    start_time = time.perf_counter()
    result = analyzer.analyze(tmp_path)
    end_time = time.perf_counter()

    # Assert execution happens under a reasonable time frame despite large volume
    assert (end_time - start_time) < 1.0
    assert result["total_files"] == 1100
    assert len(result["modules"]) == 100

def test_architecture_detector_performance(tmp_path):
    # Create dummy structure
    for i in range(50):
        d = tmp_path / f"dir_{i}"
        d.mkdir()
        for j in range(5):
            (d / f"file_{j}.py").write_text("")

    detector = ArchitectureDetector()

    start_time = time.perf_counter()
    result = detector.detect(tmp_path)
    end_time = time.perf_counter()

    # Execution should be very fast without redundant string parsing
    assert (end_time - start_time) < 1.0
    assert result["primary_pattern"] == "Monolith" # default for dummy struct
