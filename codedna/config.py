"""CodeDNA Configuration Loader — supports codedna.toml and pyproject.toml [tool.codedna]."""

from __future__ import annotations

import fnmatch
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CodeDNAConfig:
    """Configuration options for CodeDNA analysis, security, and CI quality gates."""

    # Gatekeeper policies
    min_health: str = "Fair"
    max_critical_smells: int = 0
    max_smells: int | None = None
    fail_on_secrets: bool = True
    fail_on_circular: bool = False
    max_density: float | None = None
    max_drift: float = 20.0

    # Path exclusions
    ignore_paths: list[str] = field(default_factory=list)

    # Security whitelisting
    whitelisted_secrets: list[str] = field(default_factory=list)

    # Smell thresholds
    max_file_lines: int = 500
    max_function_lines: int = 80
    god_class_methods: int = 15
    large_module_files: int = 20

    @property
    def gate(self) -> CodeDNAConfig:
        """Alias to self for structured access to gatekeeper configuration."""
        return self

    @property
    def smells(self) -> CodeDNAConfig:
        """Alias to self for structured access to smell thresholds."""
        return self

    def is_path_ignored(self, rel_path: str) -> bool:
        """Check if relative file path matches any ignore glob patterns."""
        normalized = rel_path.replace("\\", "/").strip("/")
        for pattern in self.ignore_paths:
            norm_pattern = pattern.replace("\\", "/").strip("/")
            clean_base = norm_pattern.rstrip("/*")
            if (
                normalized == clean_base
                or normalized.startswith(clean_base + "/")
                or fnmatch.fnmatch(normalized, norm_pattern)
                or fnmatch.fnmatch(Path(normalized).name, norm_pattern)
            ):
                return True
        return False

    def is_secret_whitelisted(self, secret_text: str) -> bool:
        """Check if detected secret matches any whitelisted keywords or tokens."""
        clean = secret_text.strip()
        for allowed in self.whitelisted_secrets:
            if allowed in clean or fnmatch.fnmatch(clean, allowed):
                return True
        return False


def load_config(root_path: Path) -> CodeDNAConfig:
    """Load configuration from codedna.toml, .codedna.toml, or pyproject.toml."""
    candidates = [
        root_path / "codedna.toml",
        root_path / ".codedna.toml",
        root_path / "pyproject.toml",
    ]

    for candidate in candidates:
        if candidate.is_file():
            try:
                content = candidate.read_bytes()
                data = tomllib.loads(content.decode("utf-8", errors="replace"))

                section: dict[str, Any] = {}
                if candidate.name == "pyproject.toml":
                    section = data.get("tool", {}).get("codedna", {})
                else:
                    section = data.get("codedna", data)

                if not section and candidate.name == "pyproject.toml":
                    continue

                smell_cfg = section.get("smells", {})
                gate_cfg = section.get("gate", section)

                return CodeDNAConfig(
                    min_health=str(gate_cfg.get("min_health", section.get("min_health", "Fair"))),
                    max_critical_smells=int(gate_cfg.get("max_critical_smells", section.get("max_critical_smells", 0))),
                    max_smells=int(gate_cfg["max_smells"]) if "max_smells" in gate_cfg and gate_cfg["max_smells"] is not None else None,
                    fail_on_secrets=bool(gate_cfg.get("fail_on_secrets", section.get("fail_on_secrets", True))),
                    fail_on_circular=bool(gate_cfg.get("fail_on_circular", section.get("fail_on_circular", False))),
                    max_density=float(gate_cfg["max_density"]) if "max_density" in gate_cfg and gate_cfg["max_density"] is not None else None,
                    max_drift=float(gate_cfg.get("max_drift", section.get("max_drift", 20.0))),
                    ignore_paths=list(section.get("ignore_paths", [])),
                    whitelisted_secrets=list(section.get("whitelisted_secrets", [])),
                    max_file_lines=int(smell_cfg.get("max_file_lines", section.get("max_file_lines", 500))),
                    max_function_lines=int(smell_cfg.get("max_function_lines", section.get("max_function_lines", 80))),
                    god_class_methods=int(smell_cfg.get("god_class_methods", section.get("god_class_methods", 15))),
                    large_module_files=int(smell_cfg.get("large_module_files", section.get("large_module_files", 20))),
                )
            except Exception:
                continue

    return CodeDNAConfig()


def generate_default_config_toml() -> str:
    """Generate default starter codedna.toml file content."""
    return '''# CodeDNA Configuration File (codedna.toml)
# https://github.com/shenald-dev/codedna

# Paths to exclude from analysis, smell checks, and security scans
ignore_paths = [
    "tests/*",
    "docs/*",
    "build/*",
    "dist/*",
    "*.min.js",
]

# Whitelist false-positive tokens or development test fixtures
whitelisted_secrets = [
    "PUBLIC_KEY",
    "EXAMPLE_KEY",
]

[gate]
# Minimum acceptable health rating ("Healthy", "Fair", "Needs Attention", "Critical")
min_health = "Fair"

# Maximum allowable critical smells (0 enforces zero-tolerance)
max_critical_smells = 0

# Maximum allowable total smells (omit or leave empty for no cap)
# max_smells = 50

# Fail CI immediately if secrets/credentials or circular dependencies are found
fail_on_secrets = true
fail_on_circular = false

# Maximum acceptable genetic drift percentage during drift regression gates (0-100)
max_drift = 20.0

[smells]
# Thresholds for architectural smell detection
max_file_lines = 500
max_function_lines = 80
god_class_methods = 15
large_module_files = 20
'''

