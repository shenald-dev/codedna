"""Model Context Protocol (MCP) JSON-RPC 2.0 schemas and protocol primitives."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class MCPToolDefinition:
    """Definition of an exposed MCP tool with JSON Schema parameters."""

    name: str
    description: str
    inputSchema: dict[str, Any]  # noqa: N815

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class JSONRPCRequest:
    """Standard JSON-RPC 2.0 request payload."""

    jsonrpc: str
    id: str | int | None
    method: str
    params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Any) -> JSONRPCRequest:
        if not isinstance(data, dict):
            return cls(jsonrpc="2.0", id=None, method="", params={})
        raw_params = data.get("params")
        params = raw_params if isinstance(raw_params, dict) else {}
        return cls(
            jsonrpc=str(data.get("jsonrpc", "2.0")),
            id=data.get("id"),
            method=str(data.get("method", "")),
            params=params,
        )


@dataclass
class JSONRPCResponse:
    """Standard JSON-RPC 2.0 response payload."""

    jsonrpc: str = "2.0"
    id: str | int | None = None
    result: Any = None
    error: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error is not None:
            data["error"] = self.error
        else:
            data["result"] = self.result
        return data


# Standard Error Codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
