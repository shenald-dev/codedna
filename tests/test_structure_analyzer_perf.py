import unittest
import time
import tempfile
import shutil
from pathlib import Path
from codedna.analyzers.structure_analyzer import StructureAnalyzer

class TestStructureAnalyzerPerf(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp())
        self.analyzer = StructureAnalyzer()

    def tearDown(self):
        shutil.rmtree(self.tmp_path)

    def test_performance_many_files(self):
        # Create a directory with many files and multiple markers
        for i in range(1000):
            (self.tmp_path / f"file_{i}.py").write_text("print('test')")

        (self.tmp_path / "__init__.py").write_text("")
        (self.tmp_path / "package.json").write_text("")
        (self.tmp_path / "go.mod").write_text("")

        start = time.time()
        result = self.analyzer.analyze(self.tmp_path)
        end = time.time()

        self.assertLess(end - start, 1.0, "Analysis took too long, O(N^2) behavior likely present")

        # Verify the counts are correct
        # total files = 1000 + 3 markers
        self.assertEqual(result["total_files"], 1003)
        self.assertEqual(len(result["modules"]), 3)
        for mod in result["modules"]:
            self.assertEqual(mod["file_count"], 1003)

if __name__ == "__main__":
    unittest.main()
