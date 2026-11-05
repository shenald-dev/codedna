"""Unit and integration tests for CodeDNA Model Context Protocol (MCP) server."""

from __future__ import annotations

import json
from pathlib import Path

from codedna.mcp.protocol import (
    JSONRPCRequest,
    JSONRPCResponse,
    MCPToolDefinition,
)
from codedna.mcp.server import CodeDNAMCPServer


def test_mcp_protocol_dataclasses():
    """Verify MCP protocol models serialize and deserialize correctly."""
    tool = MCPToolDefinition(
        name="test_tool",
        description="A test tool",
        inputSchema={"type": "object"},
    )
    d = tool.to_dict()
    assert d["name"] == "test_tool"
    assert "inputSchema" in d

    req = JSONRPCRequest.from_dict({
        "jsonrpc": "2.0",
        "id": 101,
        "method": "ping",
        "params": {},
    })
    assert req.id == 101
    assert req.method == "ping"

    resp = JSONRPCResponse(id=101, result={"pong": True})
    rd = resp.to_dict()
    assert rd["result"]["pong"] is True


def test_mcp_initialize_and_ping():
    """Verify MCP initialization handshake and ping."""
    server = CodeDNAMCPServer()

    init_msg = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    init_res = json.loads(server.handle_message(init_msg))

    assert init_res["result"]["serverInfo"]["name"] == "codedna-mcp"
    assert "protocolVersion" in init_res["result"]
    assert "tools" in init_res["result"]["capabilities"]

    # Handshake notification returns None
    notify_msg = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})
    assert server.handle_message(notify_msg) is None

    # Ping returns empty dict
    ping_msg = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "ping"})
    ping_res = json.loads(server.handle_message(ping_msg))
    assert ping_res["result"] == {}


def test_mcp_tools_list():
    """Verify tools/list enumerates all 7 standard CodeDNA tools."""
    server = CodeDNAMCPServer()

    list_msg = json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
    list_res = json.loads(server.handle_message(list_msg))

    tools = list_res["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert len(tools) == 7
    assert "codedna_analyze" in tool_names
    assert "codedna_inspect_architecture" in tool_names
    assert "codedna_security_audit" in tool_names
    assert "codedna_complexity_metrics" in tool_names
    assert "codedna_dependency_graph" in tool_names
    assert "codedna_quality_gate" in tool_names
    assert "codedna_drift_diff" in tool_names


def test_mcp_tools_call_execution(tmp_path: Path):
    """Verify tools/call invokes inspection and audit tools correctly."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")

    server = CodeDNAMCPServer()

    # Call codedna_inspect_architecture
    call_msg = json.dumps({
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "codedna_inspect_architecture",
            "arguments": {"path": str(tmp_path)},
        },
    })
    call_res = json.loads(server.handle_message(call_msg))
    assert call_res["result"]["isError"] is False
    content = json.loads(call_res["result"]["content"][0]["text"])
    assert "primary_pattern" in content

    # Call codedna_complexity_metrics
    call_cmp_msg = json.dumps({
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "codedna_complexity_metrics",
            "arguments": {"path": str(tmp_path)},
        },
    })
    call_cmp_res = json.loads(server.handle_message(call_cmp_msg))
    assert call_cmp_res["result"]["isError"] is False
    cmp_content = json.loads(call_cmp_res["result"]["content"][0]["text"])
    assert "maintainability_index" in cmp_content
    assert cmp_content["total_functions_analyzed"] >= 1


def test_mcp_unknown_tool_and_method():
    """Verify proper JSON-RPC error responses on invalid requests."""
    server = CodeDNAMCPServer()

    # Unknown method
    res1 = json.loads(server.handle_message(json.dumps({"jsonrpc": "2.0", "id": 6, "method": "non_existent"})))
    assert "error" in res1
    assert res1["error"]["code"] == -32601

    # Unknown tool in tools/call
    res2 = json.loads(server.handle_message(json.dumps({
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {"name": "invalid_tool_name"},
    })))
    assert "error" in res2
    assert res2["error"]["code"] == -32601


def test_mcp_malformed_and_primitive_payloads():
    """Verify MCP server handles non-dict JSON primitives without crashing."""
    server = CodeDNAMCPServer()

    # Numeric primitive
    res1 = json.loads(server.handle_message("123"))
    assert res1["error"]["code"] == -32600

    # String primitive
    res2 = json.loads(server.handle_message('"hello world"'))
    assert res2["error"]["code"] == -32600

    # Boolean primitive
    res3 = json.loads(server.handle_message("true"))
    assert res3["error"]["code"] == -32600

    # Null primitive
    res4 = json.loads(server.handle_message("null"))
    assert res4["error"]["code"] == -32600

    # Null params in request
    res5 = json.loads(server.handle_message(json.dumps({"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": None})))
    assert "error" in res5
    assert res5["error"]["code"] == -32601
