"""CodeDNA MCP Server — JSON-RPC 2.0 stdio server for AI client inter-connectivity."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

from codedna import __version__
from codedna.analyzers.architecture_detector import ArchitectureDetector
from codedna.analyzers.complexity_analyzer import ComplexityAnalyzer
from codedna.analyzers.dependency_mapper import DependencyMapper
from codedna.analyzers.diff_engine import DiffEngine
from codedna.analyzers.language_detector import LanguageDetector
from codedna.analyzers.security_detector import SecurityDetector
from codedna.analyzers.structure_analyzer import StructureAnalyzer
from codedna.ci.gatekeeper import Gatekeeper
from codedna.config import load_config

from .protocol import (
    METHOD_NOT_FOUND,
    JSONRPCRequest,
    JSONRPCResponse,
    MCPToolDefinition,
)

logger = logging.getLogger("codedna.mcp")


class CodeDNAMCPServer:
    """Stdio and programmatic Model Context Protocol server for CodeDNA."""

    def __init__(self) -> None:
        self.server_name = "codedna-mcp"
        self.server_version = __version__
        self._register_tools()

    def _register_tools(self) -> None:
        self.tools: dict[str, MCPToolDefinition] = {
            "codedna_analyze": MCPToolDefinition(
                name="codedna_analyze",
                description="Run complete reverse-engineering DNA analysis on a repository path or directory.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Local path to codebase root", "default": "."},
                    },
                },
            ),
            "codedna_inspect_architecture": MCPToolDefinition(
                name="codedna_inspect_architecture",
                description="Detect architecture patterns (MVC, Layered, Clean/Hexagonal, Microservices, Event-Driven) and infrastructure traits.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Local directory path", "default": "."},
                    },
                },
            ),
            "codedna_security_audit": MCPToolDefinition(
                name="codedna_security_audit",
                description="Scan codebase for hardcoded credentials, AI API keys, Shannon high-entropy secrets, and injection vulnerabilities.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Local directory path", "default": "."},
                    },
                },
            ),
            "codedna_complexity_metrics": MCPToolDefinition(
                name="codedna_complexity_metrics",
                description="Analyze McCabe Cyclomatic Complexity, Cognitive Complexity, and Maintainability Index (MI) across source functions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Local directory path", "default": "."},
                    },
                },
            ),
            "codedna_dependency_graph": MCPToolDefinition(
                name="codedna_dependency_graph",
                description="Build internal dependency graph, detect circular cycles, coupling density, and PageRank centrality.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Local directory path", "default": "."},
                    },
                },
            ),
            "codedna_quality_gate": MCPToolDefinition(
                name="codedna_quality_gate",
                description="Evaluate repository against CI/CD architectural quality gates and security policies.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Local directory path", "default": "."},
                        "min_health": {"type": "string", "enum": ["Healthy", "Fair", "Needs Attention", "Critical"], "default": "Fair"},
                        "fail_on_secrets": {"type": "boolean", "default": True},
                        "fail_on_circular": {"type": "boolean", "default": False},
                    },
                },
            ),
            "codedna_drift_diff": MCPToolDefinition(
                name="codedna_drift_diff",
                description="Compare two codebases or branches to calculate genetic drift, similarity percentage, and architectural deltas.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "baseline": {"type": "string", "description": "Baseline directory or DNA JSON profile"},
                        "target": {"type": "string", "description": "Target directory or DNA JSON profile"},
                    },
                    "required": ["baseline", "target"],
                },
            ),
        }

    def handle_message(self, message_str: str) -> str | None:
        """Handle raw JSON-RPC string message and return JSON string response."""
        try:
            data = json.loads(message_str)
        except Exception as e:
            err_resp = JSONRPCResponse(id=None, error={"code": -32700, "message": f"Parse error: {e}"})
            return json.dumps(err_resp.to_dict())

        if not isinstance(data, (dict, list)):
            err_resp = JSONRPCResponse(id=None, error={"code": -32600, "message": "Invalid Request: expected JSON object or array"})
            return json.dumps(err_resp.to_dict())

        if isinstance(data, list):
            responses = []
            for item in data:
                if not isinstance(item, dict):
                    responses.append(JSONRPCResponse(id=None, error={"code": -32600, "message": "Invalid Request: expected object"}).to_dict())
                    continue
                req = JSONRPCRequest.from_dict(item)
                res = self.handle_request(req)
                if res:
                    responses.append(res.to_dict())
            return json.dumps(responses) if responses else None

        req = JSONRPCRequest.from_dict(data)
        res = self.handle_request(req)
        return json.dumps(res.to_dict()) if res else None

    def handle_request(self, req: JSONRPCRequest) -> JSONRPCResponse | None:
        """Dispatch JSON-RPC request to appropriate MCP handler."""
        method = req.method

        if method == "initialize":
            return JSONRPCResponse(
                id=req.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": self.server_name,
                        "version": self.server_version,
                    },
                    "capabilities": {
                        "tools": {"listChanged": False},
                    },
                },
            )

        elif method == "notifications/initialized":
            # Handshake notification, no response required
            return None

        elif method == "ping":
            return JSONRPCResponse(id=req.id, result={})

        elif method == "tools/list":
            return JSONRPCResponse(
                id=req.id,
                result={
                    "tools": [t.to_dict() for t in self.tools.values()],
                },
            )

        elif method == "tools/call":
            params = req.params
            tool_name = params.get("name", "")
            args = params.get("arguments", {})

            if tool_name not in self.tools:
                return JSONRPCResponse(
                    id=req.id,
                    error={"code": METHOD_NOT_FOUND, "message": f"Tool '{tool_name}' not found"},
                )

            try:
                content_text = self._execute_tool(tool_name, args)
                return JSONRPCResponse(
                    id=req.id,
                    result={
                        "content": [{"type": "text", "text": content_text}],
                        "isError": False,
                    },
                )
            except Exception as e:
                return JSONRPCResponse(
                    id=req.id,
                    result={
                        "content": [{"type": "text", "text": f"Error executing '{tool_name}': {e}"}],
                        "isError": True,
                    },
                )

        else:
            return JSONRPCResponse(
                id=req.id,
                error={"code": METHOD_NOT_FOUND, "message": f"Method '{method}' not supported"},
            )

    def _execute_tool(self, name: str, args: dict[str, Any]) -> str:
        """Execute selected tool and return serialized response text."""
        target_path = Path(args.get("path", ".")).resolve()

        if name == "codedna_analyze":
            config = load_config(target_path)
            langs = LanguageDetector().detect(target_path)
            struct = StructureAnalyzer().analyze(target_path)
            arch = ArchitectureDetector().detect(target_path)
            sec = SecurityDetector(config=config).detect(target_path)
            cmp = ComplexityAnalyzer().analyze(target_path, config=config)
            deps = DependencyMapper().map(target_path)

            summary = {
                "source": str(target_path),
                "primary_language": langs.get("primary", "Unknown"),
                "system_type": arch.get("primary_pattern", "Unknown"),
                "total_files": struct.get("total_files", 0),
                "total_lines": langs.get("total_lines", 0),
                "maintainability_index": cmp.get("maintainability_index", 100.0),
                "maintainability_rank": cmp.get("maintainability_rank", "A"),
                "critical_security_vulnerabilities": sec.get("total_critical", 0),
                "has_secrets": sec.get("has_secrets", False),
                "circular_dependencies": deps.get("has_circular_deps", False),
                "dependency_density": deps.get("density", 0.0),
            }
            return json.dumps(summary, indent=2)

        elif name == "codedna_inspect_architecture":
            arch = ArchitectureDetector().detect(target_path)
            return json.dumps(arch, indent=2)

        elif name == "codedna_security_audit":
            config = load_config(target_path)
            sec = SecurityDetector(config=config).detect(target_path)
            return json.dumps(sec, indent=2)

        elif name == "codedna_complexity_metrics":
            config = load_config(target_path)
            cmp = ComplexityAnalyzer().analyze(target_path, config=config)
            return json.dumps(cmp, indent=2)

        elif name == "codedna_dependency_graph":
            deps = DependencyMapper().map(target_path)
            return json.dumps(deps, indent=2)

        elif name == "codedna_quality_gate":
            config = load_config(target_path)
            langs = LanguageDetector().detect(target_path)
            struct = StructureAnalyzer().analyze(target_path)
            arch = ArchitectureDetector().detect(target_path)
            deps = DependencyMapper().map(target_path)
            sec = SecurityDetector(config=config).detect(target_path)
            cmp = ComplexityAnalyzer().analyze(target_path, config=config)

            mock_profile = {
                "health": {
                    "overall": "Healthy" if sec.get("total_critical", 0) == 0 else "Critical",
                    "severity_counts": {"critical": sec.get("total_critical", 0), "warning": 0, "info": 0},
                },
                "dependencies": deps,
                "security": sec,
                "complexity": cmp,
                "structure_stats": struct,
                "architecture": arch,
                "languages": langs,
            }

            gatekeeper = Gatekeeper(
                min_health=args.get("min_health", config.min_health),
                fail_on_secrets=args.get("fail_on_secrets", config.fail_on_secrets),
                fail_on_circular=args.get("fail_on_circular", config.fail_on_circular),
                max_cyclomatic_complexity=config.max_cyclomatic_complexity,
                min_maintainability_index=config.min_maintainability_index,
                max_density=config.max_density,
                max_critical_smells=config.max_critical_smells,
                max_smells=config.max_smells,
            )
            result = gatekeeper.evaluate(mock_profile)
            return json.dumps(result.to_dict(), indent=2)

        elif name == "codedna_drift_diff":
            baseline_path = Path(args["baseline"]).resolve()
            target_path_b = Path(args["target"]).resolve()

            # Helper to load or analyze
            def _get_profile(p: Path) -> dict:
                if p.is_file() and p.suffix == ".json":
                    return json.loads(p.read_text(encoding="utf-8"))
                cfg = load_config(p)
                return {
                    "metadata": {"source": str(p)},
                    "languages": LanguageDetector().detect(p),
                    "structure_stats": StructureAnalyzer().analyze(p),
                    "architecture": ArchitectureDetector().detect(p),
                    "dependencies": DependencyMapper().map(p),
                    "security": SecurityDetector(config=cfg).detect(p),
                    "health": {"overall": "Healthy", "severity_counts": {"critical": 0, "warning": 0, "info": 0}},
                }

            prof_a = _get_profile(baseline_path)
            prof_b = _get_profile(target_path_b)
            diff = DiffEngine().compare(prof_a, prof_b)
            return json.dumps(diff, indent=2)

        return "{}"

    def run_stdio(self) -> None:
        """Run standard I/O loop consuming line-delimited JSON-RPC from stdin."""
        sys.stderr.write(f"🧬 CodeDNA MCP Server v{self.server_version} running on stdio...\n")
        sys.stderr.flush()

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                response_str = self.handle_message(line)
                if response_str:
                    sys.stdout.write(response_str + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_resp = JSONRPCResponse(id=None, error={"code": -32603, "message": f"Internal error: {e}"})
                sys.stdout.write(json.dumps(err_resp.to_dict()) + "\n")
                sys.stdout.flush()
