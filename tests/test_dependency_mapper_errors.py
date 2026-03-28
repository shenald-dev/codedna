import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from codedna.analyzers.dependency_mapper import DependencyMapper


class TestDependencyMapperErrors(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp())
        self.mapper = DependencyMapper()

    def tearDown(self):
        shutil.rmtree(self.tmp_path)

    def test_map_handles_oserror_on_read(self):
        # Create a sample python file that will fail to read
        py_file_fail = self.tmp_path / "fail.py"
        py_file_fail.write_text("import os")

        # Create another sample python file that will be read successfully
        py_file_ok = self.tmp_path / "ok.py"
        py_file_ok.write_text("def ok():\n    pass\n")

        original_read_text = Path.read_text

        def mocked_read_text(self_path, *args, **kwargs):
            # We use string containment to handle potential path variations
            if "fail.py" in str(self_path):
                raise OSError("Simulated OS Error")
            return original_read_text(self_path, *args, **kwargs)

        with patch("pathlib.Path.read_text", side_effect=mocked_read_text, autospec=True):
            result = self.mapper.map(self.tmp_path)

        # "fail.py" should have been skipped, so only "ok.py" (module "ok") should be in nodes.
        # Since ok.py has no external imports, no implicit edge nodes will be added by networkx.
        self.assertEqual(result["total_modules"], 1)

if __name__ == "__main__":
    unittest.main()
