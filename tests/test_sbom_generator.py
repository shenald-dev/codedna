"""Unit tests for Software Bill of Materials (SBOM) Generator.

Tests CycloneDX 1.5 and SPDX 2.3 discovery across Python, Node.js, Rust, and Go manifests.
"""

import json
from pathlib import Path

from codedna.compliance.sbom import SBOMGenerator


def test_sbom_python_pyproject_discovery(tmp_path: Path):
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text("""
[project]
name = "sample-app"
version = "0.1.0"
dependencies = [
    "requests>=2.31.0",
    "click==8.1.7",
    "flask"
]

[tool.poetry.dependencies]
pydantic = "^2.5.0"
    """, encoding="utf-8")

    gen = SBOMGenerator(tmp_path)
    deps = gen.discover_dependencies()

    dep_names = {d["name"] for d in deps}
    assert "requests" in dep_names
    assert "click" in dep_names
    assert "flask" in dep_names
    assert "pydantic" in dep_names

    # Check purl
    requests_dep = next(d for d in deps if d["name"] == "requests")
    assert requests_dep["purl"].startswith("pkg:pypi/requests@")


def test_sbom_python_requirements_discovery(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("numpy>=1.24.0\nscipy==1.11.0\n# comment\n", encoding="utf-8")

    gen = SBOMGenerator(tmp_path)
    deps = gen.discover_dependencies()
    names = {d["name"] for d in deps}
    assert "numpy" in names
    assert "scipy" in names


def test_sbom_nodejs_package_discovery(tmp_path: Path):
    pkg = tmp_path / "package.json"
    pkg.write_text(json.dumps({
        "name": "node-demo",
        "dependencies": {
            "express": "^4.18.2",
            "cors": "*"
        },
        "devDependencies": {
            "jest": "^29.5.0"
        }
    }), encoding="utf-8")

    lock = tmp_path / "package-lock.json"
    lock.write_text(json.dumps({
        "packages": {
            "node_modules/express": {"version": "4.18.2"},
            "node_modules/cors": {"version": "2.8.5"}
        }
    }), encoding="utf-8")

    gen = SBOMGenerator(tmp_path)
    deps = gen.discover_dependencies()
    names = {d["name"] for d in deps}
    assert "express" in names
    assert "cors" in names
    assert "jest" in names

    express_dep = next(d for d in deps if d["name"] == "express")
    assert express_dep["version"] == "4.18.2"
    assert express_dep["purl"] == "pkg:npm/express@4.18.2"


def test_sbom_rust_cargo_discovery(tmp_path: Path):
    cargo = tmp_path / "Cargo.toml"
    cargo.write_text("""
[package]
name = "rust-app"
version = "0.1.0"

[dependencies]
serde = "1.0.190"
tokio = { version = "1.32.0", features = ["full"] }
    """, encoding="utf-8")

    gen = SBOMGenerator(tmp_path)
    deps = gen.discover_dependencies()
    names = {d["name"] for d in deps}
    assert "serde" in names
    assert "tokio" in names


def test_sbom_go_mod_discovery(tmp_path: Path):
    gomod = tmp_path / "go.mod"
    gomod.write_text("""
module example.com/myapp

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    golang.org/x/crypto v0.14.0
)
    """, encoding="utf-8")

    gen = SBOMGenerator(tmp_path)
    deps = gen.discover_dependencies()
    names = {d["name"] for d in deps}
    assert "github.com/gin-gonic/gin" in names
    assert "golang.org/x/crypto" in names


def test_sbom_cyclonedx_json_structure(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("fastapi>=0.100.0\nuvicorn>=0.22.0\n", encoding="utf-8")

    gen = SBOMGenerator(tmp_path)
    doc = gen.generate_cyclonedx_json()

    assert doc["bomFormat"] == "CycloneDX"
    assert doc["specVersion"] == "1.5"
    assert "serialNumber" in doc
    assert "metadata" in doc
    assert len(doc["components"]) == 2
    assert any(c["name"] == "fastapi" for c in doc["components"])
    assert doc["dependencies"][0]["ref"].startswith("app-")


def test_sbom_spdx_json_structure(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("fastapi>=0.100.0\n", encoding="utf-8")

    gen = SBOMGenerator(tmp_path)
    doc = gen.generate_spdx_json()

    assert doc["spdxVersion"] == "SPDX-2.3"
    assert doc["dataLicense"] == "CC0-1.0"
    assert doc["SPDXID"] == "SPDXRef-DOCUMENT"
    assert len(doc["packages"]) >= 2  # root package + fastapi
    assert any(p["name"] == "fastapi" for p in doc["packages"])
    assert len(doc["relationships"]) >= 2
