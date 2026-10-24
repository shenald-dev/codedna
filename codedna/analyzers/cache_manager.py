"""Cache Manager — handles disk-based caching for computationally expensive operations."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path


class CacheManager:
    """Manages local disk cache for CodeDNA analysis results."""

    def __init__(self, cache_dir: Path | str = ".codedna_cache"):
        self.cache_dir = Path(cache_dir)
        self.ttl = timedelta(days=1)
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Ensure the cache directory exists."""
        if not self.cache_dir.exists():
            try:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                # Add out to .gitignore mechanism usually, but keep it local
                ignore_file = self.cache_dir / ".gitignore"
                if not ignore_file.exists():
                    ignore_file.write_text("*\n!.gitignore\n", encoding="utf-8")
            except Exception:
                pass

    def _get_cache_key(self, scope: str, identifier: str) -> str:
        """Generate a consistent cache key."""
        raw = f"{scope}::{identifier}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, scope: str, identifier: str) -> dict | None:
        """Retrieve a value from the cache if it exists and is not expired."""
        key = self._get_cache_key(scope, identifier)
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            timestamp = datetime.fromisoformat(data["_cached_at"])

            # Check expiration
            if datetime.now() - timestamp > self.ttl:
                return None

            return data["payload"]
        except Exception:
            return None

    def set(self, scope: str, identifier: str, payload: dict) -> bool:
        """Store a value in the cache."""
        key = self._get_cache_key(scope, identifier)
        cache_file = self.cache_dir / f"{key}.json"

        data = {
            "_cached_at": datetime.now().isoformat(),
            "payload": payload
        }

        try:
            cache_file.write_text(json.dumps(data), encoding="utf-8")
            return True
        except Exception:
            return False
