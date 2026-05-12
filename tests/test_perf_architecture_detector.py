import time
import shutil
import tempfile
import unittest
from pathlib import Path
from codedna.analyzers.architecture_detector import ArchitectureDetector

class TestArchitectureDetectorPerf(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp())
        self.detector = ArchitectureDetector()

        # Create a deep and wide nested structure to simulate a large repo
        def create_tree(root: Path, depth: int, width: int):
            if depth == 0:
                return
            for i in range(width):
                dir_path = root / f"dir_{i}"
                dir_path.mkdir()
                for j in range(3):
                    (dir_path / f"file_{j}.py").write_text("")
                create_tree(dir_path, depth - 1, width)

        create_tree(self.tmp_path, depth=4, width=5)

    def tearDown(self):
        shutil.rmtree(self.tmp_path)

    def test_detect_performance(self):
        start = time.perf_counter()
        self.detector.detect(self.tmp_path)
        end = time.perf_counter()

        duration = end - start
        # The exact threshold will depend on the system, but the optimized
        # version should complete this tree very quickly (< 0.1s typically).
        # We assert a reasonable upper bound to catch severe regressions.
        self.assertLess(duration, 0.5, f"detect() took too long: {duration:.4f}s")

if __name__ == "__main__":
    unittest.main()
