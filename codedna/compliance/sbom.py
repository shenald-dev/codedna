"""Software Bill of Materials (SBOM) Engine for CodeDNA.

Discovers multi-ecosystem project dependencies and generates industry-standard
CycloneDX (v1.5 JSON) and SPDX (v2.3 JSON) software manifests.
"""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

IGNORE_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "venv", ".venv", "env",
    "__pycache__", ".pytest_cache", "build", "dist", "target", "vendor"
}


class SBOMGenerator:
    """Discovers project dependencies and exports CycloneDX / SPDX SBOM specifications."""

    def __init__(self, repo_path: str | Path = ".") -> None:
        self.repo_path = Path(repo_path).resolve()

    def discover_dependencies(self) -> List[Dict[str, Any]]:
        """Scans workspace manifests across Python, Node.js, Rust, and Go ecosystems."""
        dependencies: List[Dict[str, Any]] = []
        seen_keys = set()

        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

            # 1. Python: pyproject.toml
            if "pyproject.toml" in files:
                pyproject_path = Path(root) / "pyproject.toml"
                deps = self._parse_pyproject(pyproject_path)
                for d in deps:
                    key = (d["name"], d.get("version", "*"), d["ecosystem"])
                    if key not in seen_keys:
                        seen_keys.add(key)
                        dependencies.append(d)

            # 2. Python: requirements.txt
            for f in files:
                if f == "requirements.txt" or f.endswith(".requirements.txt"):
                    req_path = Path(root) / f
                    deps = self._parse_requirements_txt(req_path)
                    for d in deps:
                        key = (d["name"], d.get("version", "*"), d["ecosystem"])
                        if key not in seen_keys:
                            seen_keys.add(key)
                            dependencies.append(d)

            # 3. Node.js: package.json & package-lock.json
            if "package.json" in files:
                pkg_path = Path(root) / "package.json"
                lock_path = Path(root) / "package-lock.json" if "package-lock.json" in files else None
                deps = self._parse_package_json(pkg_path, lock_path)
                for d in deps:
                    key = (d["name"], d.get("version", "*"), d["ecosystem"])
                    if key not in seen_keys:
                        seen_keys.add(key)
                        dependencies.append(d)

            # 4. Rust: Cargo.toml & Cargo.lock
            if "Cargo.toml" in files:
                cargo_path = Path(root) / "Cargo.toml"
                cargo_lock = Path(root) / "Cargo.lock" if "Cargo.lock" in files else None
                deps = self._parse_cargo_toml(cargo_path, cargo_lock)
                for d in deps:
                    key = (d["name"], d.get("version", "*"), d["ecosystem"])
                    if key not in seen_keys:
                        seen_keys.add(key)
                        dependencies.append(d)

            # 5. Go: go.mod
            if "go.mod" in files:
                go_mod_path = Path(root) / "go.mod"
                deps = self._parse_go_mod(go_mod_path)
                for d in deps:
                    key = (d["name"], d.get("version", "*"), d["ecosystem"])
                    if key not in seen_keys:
                        seen_keys.add(key)
                        dependencies.append(d)

        dependencies.sort(key=lambda x: (x["ecosystem"], x["name"]))
        return dependencies

    def _parse_pyproject(self, path: Path) -> List[Dict[str, Any]]:
        results = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            # 1. Standard PEP 621 dependencies = [...]
            pep621_match = re.search(r"dependencies\s*=\s*\[(.*?)\]", content, re.DOTALL)
            if pep621_match:
                raw_deps = pep621_match.group(1)
                for item in re.finditer(r'["\']([A-Za-z0-9_.\-]+)(?:([><=~!^]+.*?)?)?["\']', raw_deps):
                    name = item.group(1).strip()
                    ver = item.group(2).strip() if item.group(2) else "*"
                    results.append({
                        "name": name,
                        "version": ver,
                        "ecosystem": "pypi",
                        "manifest": str(path.relative_to(self.repo_path)),
                        "scope": "required",
                        "purl": f"pkg:pypi/{name.lower()}@{ver}" if ver != "*" else f"pkg:pypi/{name.lower()}"
                    })

            # 2. Poetry tool.poetry.dependencies
            poetry_match = re.search(r"\[tool\.poetry\.dependencies\](.*?)(?:\[|\Z)", content, re.DOTALL)
            if poetry_match:
                for line in poetry_match.group(1).splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("python"):
                        continue
                    m = re.match(r'([A-Za-z0-9_.\-]+)\s*=\s*["\']?([^"\']+)["\']?', line)
                    if m:
                        name = m.group(1).strip()
                        ver = m.group(2).strip()
                        results.append({
                            "name": name,
                            "version": ver,
                            "ecosystem": "pypi",
                            "manifest": str(path.relative_to(self.repo_path)),
                            "scope": "required",
                            "purl": f"pkg:pypi/{name.lower()}@{ver}"
                        })
        except Exception as e:
            logger.debug("Failed to parse pyproject.toml at %s: %s", path, e)
        return results

    def _parse_requirements_txt(self, path: Path) -> List[Dict[str, Any]]:
        results = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                m = re.match(r"^([A-Za-z0-9_.\-]+)(?:([><=~!^]+[A-Za-z0-9_.\-+]+))?", line)
                if m:
                    name = m.group(1).strip()
                    ver = m.group(2).strip() if m.group(2) else "*"
                    results.append({
                        "name": name,
                        "version": ver,
                        "ecosystem": "pypi",
                        "manifest": str(path.relative_to(self.repo_path)),
                        "scope": "required",
                        "purl": f"pkg:pypi/{name.lower()}@{ver}" if ver != "*" else f"pkg:pypi/{name.lower()}"
                    })
        except Exception as e:
            logger.debug("Failed to parse requirements.txt at %s: %s", path, e)
        return results

    def _parse_package_json(self, path: Path, lock_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        results = []
        locked_versions: Dict[str, str] = {}
        if lock_path and lock_path.exists():
            try:
                lock_data = json.loads(lock_path.read_text(encoding="utf-8", errors="ignore"))
                packages = lock_data.get("packages", {})
                for pkg_key, pkg_info in packages.items():
                    name = pkg_key.replace("node_modules/", "")
                    if name and "version" in pkg_info:
                        locked_versions[name] = pkg_info["version"]
                for name, info in lock_data.get("dependencies", {}).items():
                    if "version" in info:
                        locked_versions[name] = info["version"]
            except Exception as e:
                logger.debug("Failed to parse package-lock.json: %s", e)

        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            manifest_str = str(path.relative_to(self.repo_path))

            # Runtime dependencies
            for name, ver in data.get("dependencies", {}).items():
                resolved_ver = locked_versions.get(name, str(ver))
                results.append({
                    "name": name,
                    "version": resolved_ver,
                    "declared_version": str(ver),
                    "ecosystem": "npm",
                    "manifest": manifest_str,
                    "scope": "required",
                    "purl": f"pkg:npm/{name}@{resolved_ver}"
                })

            # Dev dependencies
            for name, ver in data.get("devDependencies", {}).items():
                resolved_ver = locked_versions.get(name, str(ver))
                results.append({
                    "name": name,
                    "version": resolved_ver,
                    "declared_version": str(ver),
                    "ecosystem": "npm",
                    "manifest": manifest_str,
                    "scope": "optional",
                    "purl": f"pkg:npm/{name}@{resolved_ver}"
                })
        except Exception as e:
            logger.debug("Failed to parse package.json at %s: %s", path, e)
        return results

    def _parse_cargo_toml(self, path: Path, lock_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        results = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            in_deps = False
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("[dependencies]") or line.startswith("[dev-dependencies]"):
                    in_deps = True
                    continue
                if line.startswith("[") and in_deps:
                    in_deps = False
                    continue
                if in_deps and "=" in line and not line.startswith("#"):
                    name, val = line.split("=", 1)
                    name = name.strip()
                    val = val.strip().strip('"\'')
                    ver = val
                    if "version" in val:
                        m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', val)
                        if m:
                            ver = m.group(1)
                    results.append({
                        "name": name,
                        "version": ver,
                        "ecosystem": "cargo",
                        "manifest": str(path.relative_to(self.repo_path)),
                        "scope": "required",
                        "purl": f"pkg:cargo/{name}@{ver}"
                    })
        except Exception as e:
            logger.debug("Failed to parse Cargo.toml at %s: %s", path, e)
        return results

    def _parse_go_mod(self, path: Path) -> List[Dict[str, Any]]:
        results = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            in_require = False
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("require ("):
                    in_require = True
                    continue
                if in_require and line == ")":
                    in_require = False
                    continue
                if in_require and line and not line.startswith("//"):
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        ver = parts[1]
                        results.append({
                            "name": name,
                            "version": ver,
                            "ecosystem": "golang",
                            "manifest": str(path.relative_to(self.repo_path)),
                            "scope": "required",
                            "purl": f"pkg:golang/{name}@{ver}"
                        })
                elif line.startswith("require ") and not in_require:
                    parts = line.replace("require ", "").split()
                    if len(parts) >= 2:
                        name = parts[0]
                        ver = parts[1]
                        results.append({
                            "name": name,
                            "version": ver,
                            "ecosystem": "golang",
                            "manifest": str(path.relative_to(self.repo_path)),
                            "scope": "required",
                            "purl": f"pkg:golang/{name}@{ver}"
                        })
        except Exception as e:
            logger.debug("Failed to parse go.mod at %s: %s", path, e)
        return results

    def generate_cyclonedx_json(self) -> Dict[str, Any]:
        """Generates an OASIS / OWASP CycloneDX v1.5 JSON standard document."""
        deps = self.discover_dependencies()
        now = datetime.now(timezone.utc).isoformat()
        root_name = self.repo_path.name or "application"

        components = []
        dependencies_refs = []

        for d in deps:
            comp_id = f"{d['ecosystem']}-{d['name']}-{d['version']}".replace("/", "-")
            comp = {
                "bom-ref": comp_id,
                "type": "library",
                "name": d["name"],
                "version": d["version"],
                "purl": d["purl"],
                "scope": d["scope"],
                "properties": [
                    {"name": "codedna:ecosystem", "value": d["ecosystem"]},
                    {"name": "codedna:manifest", "value": d["manifest"]}
                ]
            }
            components.append(comp)
            dependencies_refs.append(comp_id)

        doc = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": now,
                "tools": [
                    {
                        "vendor": "CodeDNA",
                        "name": "codedna-sbom-engine",
                        "version": "1.4.0"
                    }
                ],
                "component": {
                    "type": "application",
                    "name": root_name,
                    "version": "latest",
                    "bom-ref": f"app-{root_name}"
                }
            },
            "components": components,
            "dependencies": [
                {
                    "ref": f"app-{root_name}",
                    "dependsOn": dependencies_refs
                }
            ]
        }
        return doc

    def generate_spdx_json(self) -> Dict[str, Any]:
        """Generates a Linux Foundation SPDX v2.3 JSON specification document."""
        deps = self.discover_dependencies()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        doc_name = self.repo_path.name or "codedna-project"

        packages = [
            {
                "name": doc_name,
                "SPDXID": "SPDXRef-RootPackage",
                "versionInfo": "1.0.0",
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION"
            }
        ]
        relationships = [
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relatedSpdxElement": "SPDXRef-RootPackage",
                "relationshipType": "DESCRIBES"
            }
        ]

        for idx, d in enumerate(deps, start=1):
            spdx_id = f"SPDXRef-Package-{idx}-{re.sub(r'[^A-Za-z0-9.-]', '-', d['name'])}"
            pkg = {
                "name": d["name"],
                "SPDXID": spdx_id,
                "versionInfo": d["version"],
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": d["purl"]
                    }
                ]
            }
            packages.append(pkg)
            relationships.append({
                "spdxElementId": "SPDXRef-RootPackage",
                "relatedSpdxElement": spdx_id,
                "relationshipType": "DEPENDS_ON"
            })

        doc = {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": f"{doc_name}-SBOM",
            "documentNamespace": f"https://spdx.org/spdxdocs/{doc_name}-{uuid.uuid4()}",
            "creationInfo": {
                "creators": ["Tool: CodeDNA-1.4.0", "Organization: CodeDNA Intelligence"],
                "created": now
            },
            "packages": packages,
            "relationships": relationships
        }
        return doc
