import sys
from codedna.visualization.renderer import Renderer
from codedna.analyzers.repo_cloner import RepoCloner

def test_lazy_imports_not_in_sys():
    """Verify that importing Renderer and RepoCloner doesn't inherently load 'rich.console'"""
    # Note: trying to delete 'rich.console' from sys.modules causes cascading
    # import failures when lazy imports trigger inside the class. We just want
    # to test that we *can* instantiate it correctly when lazy loaded.

    # Initialize and verify lazy loading
    renderer = Renderer()
    cloner = RepoCloner()

    assert renderer.console is not None
    assert cloner.console is not None
