"""Integration tests for CodeDNA v1.4 MCP tools."""

import json
from pathlib import Path

from codedna.mcp.protocol import JSONRPCRequest
from codedna.mcp.server import CodeDNAMCPServer


def test_mcp_generate_sbom(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("rich>=13.0.0\n", encoding="utf-8")

    server = CodeDNAMCPServer()
    rpc_req = JSONRPCRequest(
        jsonrpc="2.0",
        id=1,
        method="tools/call",
        params={
            "name": "codedna_generate_sbom",
            "arguments": {
                "path": str(tmp_path),
                "format": "cyclonedx",
            },
        },
    )
    resp = server.handle_request(rpc_req)
    assert resp is not None
    assert resp.error is None
    content_text = resp.result["content"][0]["text"]
    data = json.loads(content_text)
    assert data["bomFormat"] == "CycloneDX"
    assert any(c["name"] == "rich" for c in data["components"])


def test_mcp_plan_remediation(tmp_path: Path):
    py_file = tmp_path / "app.py"
    py_file.write_text("try:\n    pass\nexcept:\n    pass\n", encoding="utf-8")

    server = CodeDNAMCPServer()
    rpc_req = JSONRPCRequest(
        jsonrpc="2.0",
        id=2,
        method="tools/call",
        params={
            "name": "codedna_plan_remediation",
            "arguments": {
                "path": str(tmp_path),
                "apply_fixes": True,
            },
        },
    )
    resp = server.handle_request(rpc_req)
    assert resp is not None
    assert resp.error is None
    content_text = resp.result["content"][0]["text"]
    data = json.loads(content_text)
    assert "application" in data
    assert data["application"]["applied_count"] == 1
    # Verify file was actually fixed
    assert "except Exception:" in py_file.read_text(encoding="utf-8")
