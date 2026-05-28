import time
import shutil
import tempfile
import unittest
from pathlib import Path

from codedna.analyzers.architecture_detector import ArchitectureDetector
from codedna.analyzers.structure_analyzer import StructureAnalyzer

class TestAnalyzerPerformance(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp())
        self.detector = ArchitectureDetector()
        self.structure_analyzer = StructureAnalyzer()

        # Create a large nested structure to test O(N) constraints
        current_dir = self.tmp_path
        for i in range(10): # Depth of 10
            current_dir = current_dir / f"dir_{i}"
            current_dir.mkdir()
            for j in range(50): # 50 files per directory
                (current_dir / f"file_{j}.py").write_text("print('hello')")
            # add a module marker to trigger structure analyzer
            (current_dir / "__init__.py").write_text("")

    def tearDown(self):
        shutil.rmtree(self.tmp_path)

    def test_architecture_detector_performance(self):
        start_time = time.time()
        result = self.detector.detect(self.tmp_path)
        end_time = time.time()











        # Time should be minimal, generally well under 0.1s for this structure
        self.assertLess(end_time - start_time, 0.5, "ArchitectureDetector is too slow")
        self.assertIn("primary_pattern", result)

    def test_structure_analyzer_performance(self):
        start_time = time.time()
        result = self.structure_analyzer.analyze(self.tmp_path)
        end_time = time.time()











        # Time should be minimal, generally well under 0.1s for this structure
        self.assertLess(end_time - start_time, 0.5, "StructureAnalyzer is too slow")
        self.assertIn("modules", result)
        self.assertEqual(len(result["modules"]), 10) # 10 nested __init__.py markers

if __name__ == '__main__':
    unittest.main()
