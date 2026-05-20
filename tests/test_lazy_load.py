import sys
from codedna.visualization.renderer import Renderer
from codedna.analyzers.repo_cloner import RepoCloner

def test_lazy_imports_not_in_sys():
    """Verify that importing Renderer and RepoCloner doesn't inherently load 'rich.console'"""
    # Clean up sys.modules to simulate fresh load
    if 'rich.console' in sys.modules:
        del sys.modules['rich.console']

    # Importing the modules should NOT load rich.console at module level
    import codedna.visualization.renderer
    import codedna.analyzers.repo_cloner

    # Only if they were initialized without console, the import should occur
    assert 'rich.console' not in sys.modules, "rich.console was loaded at module level!"

    # Initialize and verify lazy loading
    renderer = Renderer()
    cloner = RepoCloner()

    assert 'rich.console' in sys.modules, "rich.console was not lazily loaded upon instantiation!"
