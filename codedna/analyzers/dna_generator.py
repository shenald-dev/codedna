"""DNA Generator — aggregates all analysis results into a final DNA profile."""

from __future__ import annotations

import json
from datetime import datetime


class DNAGenerator:
    """Produces the final DNA profile summary from all analysis modules."""

    def generate(
        self,
        repo_source: str,
        languages: dict,
        structure: dict,
        dependencies: dict,
        architecture: dict,
        smells: dict,
        developers: dict,
        evolution: dict,
        security: dict = None,
        github: dict = None,
        mermaid_graph: str = "",
    ) -> dict:
        """Aggregate all analysis into a DNA profile.

        Returns:
            Complete DNA profile dict.
        """
        # Compute overall health
        health = self._compute_overall_health(smells, dependencies, architecture, security)

        # Build risk signals
        risks = self._extract_risks(smells, dependencies, security)

        # Build DNA signature
        signature = self._build_signature(languages, architecture, developers, structure)

        return {
            "metadata": {
                "source": repo_source,
                "analyzed_at": datetime.now().isoformat(),
                "version": "1.0.0",
            },
            "signature": signature,
            "system_type": architecture.get("primary_pattern", "Unknown"),
            "languages": languages,
            "architecture": architecture,
            "structure_stats": {
                "total_files": structure.get("total_files", 0),
                "total_dirs": structure.get("total_dirs", 0),
                "max_depth": structure.get("max_depth", 0),
                "modules": len(structure.get("modules", [])),
            },
            "dependencies": {
                "total_modules": dependencies.get("total_modules", 0),
                "total_edges": dependencies.get("total_edges", 0),
                "density": dependencies.get("density", 0),
                "has_circular_deps": dependencies.get("has_circular_deps", False),
                "circular_count": len(dependencies.get("cycles", [])),
            },
            "health": health,
            "risks": risks,
            "developer_genome": {
                "total_contributors": developers.get("total_contributors", 0),
                "bus_factor": developers.get("bus_factor", 0),
                "primary_architect": (
                    developers["contributors"][0]["name"]
                    if developers.get("contributors")
                    else "Unknown"
                ),
                "top_contributors": [
                    {"name": c["name"], "role": c["role"], "commits": c["commits"]}
                    for c in developers.get("contributors", [])[:5]
                ],
            },
            "evolution": {
                "total_commits": evolution.get("total_commits", 0),
                "first_commit": evolution.get("first_commit"),
                "last_commit": evolution.get("last_commit"),
                "patterns": evolution.get("patterns", []),
            },
            "security": security or {"vulnerabilities": [], "total_critical": 0, "has_secrets": False},
            "github": github or {},
            "mermaid_graph": mermaid_graph,
        }

    def to_markdown(self, profile: dict) -> str:
        """Convert DNA profile to a markdown report."""
        lines = []
        lines.append("# 🧬 CodeDNA Profile\n")
        lines.append(f"> Analyzed: `{profile['metadata']['source']}`")
        lines.append(f"> Date: {profile['metadata']['analyzed_at'][:10]}")

        if profile.get("github", {}).get("is_github"):
            gh = profile["github"]
            lines.append(f"> ⭐️ {gh.get('stars', 0):,} Stars | 🔱 {gh.get('forks', 0):,} Forks | 🐛 {gh.get('issues', 0):,} Issues\n")
        else:
            lines.append("\n")

        lines.append("---\n")

        # System Type
        lines.append(f"## 🏗️ System Type: **{profile['system_type']}**\n")

        # Architecture
        arch = profile["architecture"]
        if arch.get("detected_patterns"):
            lines.append("### Architecture Patterns Detected")
            for p in arch["detected_patterns"]:
                bar = "█" * int(p["confidence"] * 10)
                lines.append(f"- **{p['pattern']}** ({int(p['confidence']*100)}%) `{bar}`")
            lines.append("")

        if arch.get("traits"):
            lines.append("### Infrastructure Traits")
            for t in arch["traits"]:
                lines.append(f"- ✅ {t}")
            lines.append("")

        # Languages
        lang_data = profile["languages"]
        if lang_data.get("languages"):
            lines.append("## 📊 Language Distribution\n")
            lines.append("| Language | Files | Lines | Share |")
            lines.append("|----------|-------|-------|-------|")
            for lang, data in lang_data["languages"].items():
                bar = "█" * max(1, int(data["percentage"] / 5))
                lines.append(f"| {lang} | {data['files']} | {data['lines']:,} | {data['percentage']}% `{bar}` |")
            lines.append("")

        # Health
        lines.append(f"## 🩺 Health Score: **{profile['health']['overall']}**\n")
        counts = profile["health"]["severity_counts"]
        lines.append(f"- 🔴 Critical: {counts.get('critical', 0)}")
        lines.append(f"- 🟡 Warning: {counts.get('warning', 0)}")
        lines.append(f"- 🔵 Info: {counts.get('info', 0)}")
        lines.append("")

        # Risks
        if profile["risks"]:
            lines.append("## ⚠️ Risk Signals\n")
            for risk in profile["risks"][:8]:
                lines.append(f"- {risk}")
            lines.append("")

        # Dependencies
        deps = profile["dependencies"]
        lines.append("## 🔗 Dependency Graph\n")
        lines.append(f"- Modules: **{deps['total_modules']}**")
        lines.append(f"- Connections: **{deps['total_edges']}**")
        lines.append(f"- Density: **{deps['density']}**")
        lines.append(f"- Circular Dependencies: **{'Yes ⚠️' if deps['has_circular_deps'] else 'None ✅'}**\n")

        if profile.get("mermaid_graph"):
            lines.append("```mermaid\n" + profile["mermaid_graph"] + "\n```\n")

        # Developer Genome
        dev = profile["developer_genome"]
        lines.append("## 👥 Developer Genome\n")
        lines.append(f"- Contributors: **{dev['total_contributors']}**")
        lines.append(f"- Bus Factor: **{dev['bus_factor']}**")
        lines.append(f"- Primary Architect: **{dev['primary_architect']}**\n")

        if dev["top_contributors"]:
            lines.append("| Developer | Role | Commits |")
            lines.append("|-----------|------|---------|")
            for c in dev["top_contributors"]:
                lines.append(f"| {c['name']} | {c['role']} | {c['commits']} |")
            lines.append("")

        # Evolution
        evo = profile["evolution"]
        lines.append("## 📈 Evolution\n")
        lines.append(f"- Total Commits: **{evo['total_commits']}**")
        if evo.get("first_commit"):
            lines.append(f"- First Commit: {evo['first_commit'][:10]}")
        if evo.get("patterns"):
            lines.append(f"- Patterns: {', '.join(evo['patterns'])}")
        lines.append("")

        # DNA Signature
        lines.append("## 🧬 DNA Signature\n")
        lines.append(f"```\n{profile['signature']}\n```\n")

        lines.append("---")
        lines.append("*Generated by [CodeDNA](https://github.com/shenald-dev/codedna)*")

        return "\n".join(lines)

    def to_json(self, profile: dict) -> str:
        """Convert DNA profile to JSON."""
        return json.dumps(profile, indent=2, default=str)

    def _compute_overall_health(self, smells: dict, deps: dict, arch: dict, security: dict = None) -> dict:
        """Compute overall health assessment."""
        severity = smells.get("severity_counts", {})
        health_score = smells.get("health_score", "Unknown")

        if security and security.get("has_secrets"):
            health_score = "Critical"

        return {
            "overall": health_score,
            "severity_counts": severity,
            "coupling": arch.get("coupling", "Unknown"),
            "circular_deps": deps.get("has_circular_deps", False),
        }

    def _extract_risks(self, smells: dict, deps: dict, security: dict = None) -> list[str]:
        """Extract top risk signals from analysis."""
        risks = []

        if security:
            for vuln in security.get("vulnerabilities", []):
                risks.append(f"🔴 {vuln['type']} in `{vuln['file']}`: {vuln['detail']}")

        for smell in smells.get("smells", []):
            if smell["severity"] == "critical":
                risks.append(f"🔴 {smell['type']} in `{smell['file']}`: {smell['detail']}")

        if deps.get("has_circular_deps"):
            cycle_count = len(deps.get("cycles", []))
            risks.append(f"🔴 {cycle_count} circular dependencies detected")

        for smell in smells.get("smells", []):
            if smell["severity"] == "warning" and len(risks) < 10:
                risks.append(f"🟡 {smell['type']} in `{smell['file']}`")

        return risks[:10]

    def _build_signature(self, languages: dict, architecture: dict, developers: dict, structure: dict) -> str:
        """Build a DNA-style signature string."""
        parts = []

        # Language gene
        primary = languages.get("primary", "?")
        parts.append(f"LANG:{primary[:3].upper()}")

        # Architecture gene
        arch = architecture.get("primary_pattern", "MON")[:3].upper()
        parts.append(f"ARCH:{arch}")

        # Size gene
        files = structure.get("total_files", 0)
        if files > 1000:
            size = "XL"
        elif files > 100:
            size = "LG"
        elif files > 20:
            size = "MD"
        else:
            size = "SM"
        parts.append(f"SIZE:{size}")

        # Team gene
        contribs = developers.get("total_contributors", 0)
        if contribs > 20:
            team = "ENTERPRISE"
        elif contribs > 5:
            team = "TEAM"
        elif contribs > 1:
            team = "DUO"
        else:
            team = "SOLO"
        parts.append(f"TEAM:{team}")

        # Health gene
        parts.append(f"HEALTH:{developers.get('bus_factor', 0)}")

        return " | ".join(parts)
