import tempfile
from pathlib import Path
from codedna.analyzers.structure_analyzer import StructureAnalyzer

def test_structure_analyzer_file_count_includes_hidden():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a module marker
        (tmp_path / "package.json").write_text("{}")

        # Create a regular file
        (tmp_path / "index.js").write_text("")

        # Create a hidden file
        (tmp_path / ".env").write_text("")

        analyzer = StructureAnalyzer()
        result = analyzer.analyze(tmp_path)

        assert len(result["modules"]) == 1
        module = result["modules"][0]
        assert module["marker"] == "package.json"

        # 1 marker + 1 regular file + 1 hidden file = 3
        assert module["file_count"] == 3
