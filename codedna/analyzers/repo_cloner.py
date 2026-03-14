"""Repository Cloner — clones and caches GitHub repositories for analysis."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from git import Repo
from rich.console import Console

console = Console()


class RepoCloner:
    """Clones a Git repository to a local cache directory for analysis."""

    def __init__(self, cache_dir: str | None = None):
        self.cache_dir = Path(cache_dir or tempfile.mkdtemp(prefix="codedna_"))

    def clone(self, source: str) -> Path:
        """Clone a repository from URL or resolve a local path.

        Args:
            source: GitHub URL or local filesystem path.

        Returns:
            Path to the cloned/resolved repository.
        """
        local_path = Path(source)
        if local_path.exists() and (local_path / ".git").exists():
            console.print(f"  📂 Using local repository: [cyan]{local_path}[/]")
            return local_path

        # Clone from URL
        repo_name = source.rstrip("/").split("/")[-1].replace(".git", "")
        dest = self.cache_dir / repo_name

        if dest.exists():
            console.print(f"  ♻️  Using cached clone: [cyan]{dest}[/]")
            return dest

        console.print(f"  📥 Cloning [cyan]{source}[/] ...")
        Repo.clone_from(source, str(dest), depth=100)
        return dest

    def cleanup(self) -> None:
        """Remove the cache directory."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir, ignore_errors=True)
