import unittest
import sys
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import shutil

# Mock networkx before importing DependencyMapper
mock_nx = MagicMock()
sys.modules['networkx'] = mock_nx

# Mock DiGraph to behave somewhat like a real one for basic tracking
class MockDiGraph:
    def __init__(self):
        self.nodes = set()
        self.edges = []
    def add_node(self, node):
        self.nodes.add(node)
    def add_edge(self, u, v):
        self.edges.append((u, v))
    def __len__(self):
        return len(self.nodes)

mock_nx.DiGraph.side_effect = MockDiGraph
mock_nx.density.return_value = 0.0
mock_nx.pagerank.return_value = {}
mock_nx.betweenness_centrality.return_value = {}
mock_nx.simple_cycles.return_value = []

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
        py_file_ok.write_text("import sys")

        original_read_text = Path.read_text

        def mocked_read_text(self_path, *args, **kwargs):
            # We use string containment to handle potential path variations
            if "fail.py" in str(self_path):
                raise OSError("Simulated OS Error")
            return original_read_text(self_path, *args, **kwargs)

        with patch("pathlib.Path.read_text", side_effect=mocked_read_text, autospec=True):
            result = self.mapper.map(self.tmp_path)

        # "fail.py" should have been skipped, so only "ok.py" (module "ok") should be in nodes
        # Note: result["total_modules"] comes from len(graph.nodes)
        # In our MockDiGraph, len(graph.nodes) is len(self.nodes)
        self.assertEqual(result["total_modules"], 1)

        # We can also verify that the ok module is the one present if we want to be thorough,
        # but the main thing is it didn't crash and processed the other file.

if __name__ == "__main__":
    unittest.main()
