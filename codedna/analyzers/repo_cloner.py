"""Repository Cloner — clones and caches GitHub repositories for analysis."""

from __future__ import annotations

import os
import urllib.parse
from pathlib import Path

from git import Repo
from rich.console import Console

from .cache_manager import CacheManager

console = Console()


class RepoCloner:
    """Clones a Git repository to a local cache directory for analysis."""

    def __init__(self, cache_dir: str | None = None):
        if cache_dir is None:
            base_dir = Path(CacheManager().cache_dir)
            self.cache_dir = base_dir / "repos"
            self.cache_dir.mkdir(exist_ok=True)
        else:
            self.cache_dir = Path(cache_dir)

    def clone(self, source: str) -> Path:
        """Clone a repository from URL or resolve a local path.

        Args:
            source: GitHub URL or local filesystem path.

        Returns:
            Path to the cloned/resolved repository.
        """
        # Security: Prevent Git command injection by ensuring source doesn't start with '-'
        # and looks like a valid URL or local path.
        source = source.strip()
        if source.startswith("-") or source.startswith("ext::"):
            raise ValueError(f"Invalid repository source: {source}")

        local_path = Path(source)
        if local_path.exists() and (local_path / ".git").exists():
            console.print(f"  📂 Using local repository: [cyan]{local_path}[/]")
            return local_path

        parsed_url = urllib.parse.urlparse(source)
        allowed_schemes = {"http", "https", "ssh", "git", ""}
        if parsed_url.scheme not in allowed_schemes:
            raise ValueError(f"Invalid repository source scheme: {parsed_url.scheme}")

        # Clone from URL
        unquoted_path = urllib.parse.unquote(parsed_url.path or source)
        repo_name = os.path.basename(unquoted_path.rstrip("/")).replace(".git", "")

        if not repo_name or repo_name in (".", ".."):
            raise ValueError(f"Invalid repository name derived from source: {source}")

        dest = self.cache_dir / repo_name

        if dest.exists():
            console.print(f"  ♻️  Using cached clone: [cyan]{dest}[/]")
            return dest

        console.print(f"  📥 Cloning [cyan]{source}[/] ...")
        Repo.clone_from(source, str(dest), depth=100)
        return dest

    def cleanup(self) -> None:
        """Remove the cache directory (No-op in V3 to allow persistent caching)."""
        pass
