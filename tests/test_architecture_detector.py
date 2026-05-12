import shutil
import tempfile
import unittest
from pathlib import Path

from codedna.analyzers.architecture_detector import ArchitectureDetector


class TestArchitectureDetectorWalk(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp())
        self.detector = ArchitectureDetector()

    def tearDown(self):
        shutil.rmtree(self.tmp_path)

    def test_walk_redundant_path_splitting_optimization(self):
        # Create a deep nested structure
        src = self.tmp_path / "src"
        src.mkdir()
        models = src / "models"
        models.mkdir()
        views = models / "views"
        views.mkdir()
        (views / "test.py").write_text("")

        # Add ignored dir
        ignored = self.tmp_path / "node_modules"
        ignored.mkdir()
        (ignored / "index.js").write_text("")

        # Add hidden dir
        hidden = self.tmp_path / ".git"
        hidden.mkdir()
        (hidden / "config").write_text("")

        items = list(self.detector._walk(self.tmp_path))
        names = [item[0].name.lower() if isinstance(item, tuple) else item.name.lower() for item in items]

        self.assertIn("src", names)
        self.assertIn("models", names)
        self.assertIn("views", names)
        self.assertIn("test.py", names)
        self.assertNotIn("node_modules", names)
        self.assertNotIn("index.js", names)
        self.assertNotIn(".git", names)
        self.assertNotIn("config", names)

if __name__ == "__main__":
    unittest.main()