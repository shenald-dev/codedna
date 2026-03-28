import shutil
import tempfile
import unittest
from pathlib import Path

from codedna.analyzers.code_smell_detector import CodeSmellDetector


class TestCodeSmellDetectorMinimal(unittest.TestCase):
    def setUp(self):
        self.tmp_path = Path(tempfile.mkdtemp())
        self.detector = CodeSmellDetector()

    def tearDown(self):
        shutil.rmtree(self.tmp_path)

    def test_count_methods_py(self):
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        count = self.detector._count_methods(content, ".py")
        self.assertEqual(count, 2)

    def test_count_methods_js(self):
        content = "function func1() {}\nconst func2 = () => {};"
        count = self.detector._count_methods(content, ".js")
        self.assertEqual(count, 2)

    def test_count_methods_java(self):
        content = "public void method1() {}\nprivate int method2() {}"
        count = self.detector._count_methods(content, ".java")
        self.assertEqual(count, 2)

    def test_detect_markers(self):
        file_path = self.tmp_path / "test.py"
        file_path.write_text("# TODO: fix this\n# FIXME: urgent")
        result = self.detector.detect(self.tmp_path)
        smells = [s for s in result["smells"] if s["type"] == "Code Marker"]
        self.assertEqual(len(smells), 2)

    def test_detect_long_functions_py(self):
        # Threshold is 80 lines.
        content = "def long_func():\n" + "    pass\n" * 90
        count = self.detector._detect_long_functions(content, ".py")
        self.assertEqual(len(count), 1)
        self.assertEqual(count[0][0], "long_func")

if __name__ == "__main__":
    unittest.main()
