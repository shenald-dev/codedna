"""HTML Export — generates interactive HTML dashboards for CodeDNA profiles."""

from __future__ import annotations

import html as html_lib
import math

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeDNA Profile - {source}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
    </script>
    <style>
        body {{ background-color: #0f172a; color: #f8fafc; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }}
        .card {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 0.75rem; transition: border-color 0.2s ease; }}
        .card:hover {{ border-color: #475569; }}
        .header-bg {{ background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%); border-bottom: 1px solid #334155; }}
        .radar-chart polygon {{ transition: all 0.3s ease; }}
        .tab-btn.active {{ border-bottom: 2px solid #06b6d4; color: #38bdf8; }}
        @media print {{
            body {{ background: #ffffff !important; color: #000000 !important; }}
            .card {{ background: #ffffff !important; border: 1px solid #e2e8f0 !important; color: #0f172a !important; box-shadow: none !important; }}
            .header-bg {{ background: #f8fafc !important; color: #0f172a !important; border-bottom: 2px solid #cbd5e1 !important; }}
            .no-print {{ display: none !important; }}
            h1, h2, h3, p, span, li {{ color: #0f172a !important; text-shadow: none !important; }}
        }}
    </style>
</head>
<body class="min-h-screen font-sans antialiased">

<!-- Header -->
<header class="header-bg py-8 px-6">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
            <div class="flex items-center gap-3">
                <span class="text-3xl">🧬</span>
                <h1 class="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-500">
                    CodeDNA Profile
                </h1>
                <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-950/80 text-cyan-300 border border-cyan-800">v1.1.0</span>
            </div>
            <p class="text-slate-400 text-base flex items-center gap-2 mt-2">
                <svg class="w-4 h-4 text-cyan-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
                <span class="font-mono text-slate-300">{source}</span>
            </p>
            {github_stats}
        </div>
        <div class="flex flex-col items-start md:items-end">
            <span class="inline-block px-4 py-2 rounded-lg bg-slate-800/90 border border-slate-700/80 font-mono text-cyan-400 font-semibold shadow-lg text-sm">
                {signature}
            </span>
            <p class="text-xs text-slate-400 mt-2">Analyzed on {analyzed_at}</p>
        </div>
    </div>
</header>

<main class="max-w-7xl mx-auto px-6 py-8 space-y-8">

    <!-- KPI Metric Cards -->
    <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div class="card p-5">
            <h3 class="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-1">System Type</h3>
            <p class="text-2xl font-bold text-white tracking-tight">{system_type}</p>
            <p class="text-xs text-slate-400 mt-1">Architecture pattern</p>
        </div>
        <div class="card p-5">
            <h3 class="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-1">Overall Health</h3>
            <p class="text-2xl font-bold {health_color} tracking-tight">{health_score}</p>
            <p class="text-xs text-slate-400 mt-1">Quality & hygiene rating</p>
        </div>
        <div class="card p-5">
            <h3 class="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-1">Total Files</h3>
            <p class="text-2xl font-bold text-white tracking-tight">{total_files}</p>
            <p class="text-xs text-slate-400 mt-1">Source codebase size</p>
        </div>
        <div class="card p-5">
            <h3 class="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-1">Contributors</h3>
            <p class="text-2xl font-bold text-white tracking-tight">{total_contributors}</p>
            <p class="text-xs text-slate-400 mt-1">Bus Factor: <strong class="text-cyan-400">{bus_factor}</strong></p>
        </div>
    </section>

    <!-- Radar Chart & Executive Overview -->
    <section class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <div class="card p-6 lg:col-span-5 flex flex-col justify-between">
            <div>
                <h2 class="text-lg font-bold text-slate-200 mb-1 flex items-center gap-2">
                    🎯 Architecture & Quality Radar
                </h2>
                <p class="text-xs text-slate-400 mb-4">Five-dimensional assessment of software stability and design.</p>
            </div>
            <div class="flex items-center justify-center py-2">
                {radar_chart_svg}
            </div>
            <div class="text-center pt-2 border-t border-slate-800 text-xs text-slate-400">
                Balanced polygons indicate resilient, well-modularized architectures.
            </div>
        </div>

        <div class="card p-6 lg:col-span-7 flex flex-col justify-between">
            <div>
                <h2 class="text-lg font-bold text-slate-200 mb-1 flex items-center gap-2">
                    📊 Language Distribution
                </h2>
                <p class="text-xs text-slate-400 mb-4">Polyglot breakdown by percentage and source file count.</p>
                <div class="space-y-3.5">
                    {language_bars}
                </div>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800 grid grid-cols-2 gap-4 text-xs text-slate-400">
                <div>Infrastructure Traits: <strong class="text-slate-200">{traits_count}</strong></div>
                <div>Evolution Commits: <strong class="text-slate-200">{total_commits}</strong></div>
            </div>
        </div>
    </section>

    <!-- Deep Dive Grid -->
    <section class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- Left Column: Dependency Diagram & Code Smells -->
        <div class="lg:col-span-8 space-y-6">

            <!-- Architecture Dependencies -->
            <div class="card p-6">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-4">
                    <h2 class="text-lg font-bold text-slate-200 flex items-center gap-2">
                        🔗 Module Dependency Graph
                    </h2>
                    <span class="text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">
                        Interactive Topology
                    </span>
                </div>
                <div class="bg-slate-900/90 rounded-lg p-4 w-full overflow-x-auto min-h-[300px] flex items-center justify-center border border-slate-800">
                    <div class="mermaid">
{mermaid_graph}
                    </div>
                </div>
            </div>

            <!-- Risk Signals with Interactive Filter -->
            <div class="card p-6 border-l-4 border-l-red-500">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
                    <div>
                        <h2 class="text-lg font-bold text-slate-200 flex items-center gap-2">
                            ⚠️ Risk Signals & Structural Smells
                        </h2>
                        <p class="text-xs text-slate-400">Identified anti-patterns, secrets, and high-complexity modules.</p>
                    </div>
                    <div class="no-print">
                        <input type="text" id="riskSearch" onkeyup="filterRisks()" placeholder="Filter risks..."
                               class="bg-slate-900 border border-slate-700 rounded-md px-3 py-1 text-xs text-slate-200 focus:outline-none focus:border-cyan-500">
                    </div>
                </div>
                <ul id="riskList" class="space-y-2.5 text-sm">
                    {risk_signals}
                </ul>
            </div>

        </div>

        <!-- Right Column: Sidebar Specs -->
        <div class="lg:col-span-4 space-y-6">

            <!-- Architecture Traits -->
            <div class="card p-6">
                <h2 class="text-lg font-bold text-slate-200 mb-3 flex items-center gap-2">
                    🏗️ Architecture Traits
                </h2>
                <ul class="space-y-2 text-sm text-slate-300">
                    {architecture_traits}
                </ul>
            </div>

            <!-- Developer Genome -->
            <div class="card p-6">
                <div class="flex justify-between items-center mb-3">
                    <h2 class="text-lg font-bold text-slate-200 flex items-center gap-2">
                        👥 Developer Genome
                    </h2>
                    <span class="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">Bus Factor: {bus_factor}</span>
                </div>
                <div class="space-y-2.5">
                    {top_contributors}
                </div>
            </div>

            <!-- Evolution Timeline -->
            <div class="card p-6">
                <h2 class="text-lg font-bold text-slate-200 mb-3 flex items-center gap-2">
                    📈 Evolution
                </h2>
                <ul class="space-y-2 text-sm text-slate-300">
                    <li class="flex justify-between"><span>Total Commits</span> <strong class="text-white">{total_commits}</strong></li>
                    <li class="flex justify-between"><span>First Commit</span> <strong class="text-white">{first_commit}</strong></li>
                </ul>
                <div class="mt-4 pt-4 border-t border-slate-700">
                    <p class="text-xs text-slate-400 uppercase font-semibold mb-2">Detected Patterns</p>
                    <div class="flex flex-wrap gap-1.5">
                        {evolution_patterns}
                    </div>
                </div>
            </div>

        </div>

    </section>

</main>

<footer class="border-t border-slate-800 py-6 text-center text-slate-500 text-sm mt-12">
    Generated by <a href="https://github.com/shenald-dev/codedna" class="text-cyan-400 hover:underline">CodeDNA</a> — A genetic analyzer for software.
</footer>

<script>
function filterRisks() {{
    const query = document.getElementById('riskSearch').value.toLowerCase();
    const items = document.querySelectorAll('#riskList li');
    items.forEach(el => {{
        const text = el.innerText.toLowerCase();
        el.style.display = text.includes(query) ? '' : 'none';
    }});
}}
</script>

</body>
</html>
"""


class HTMLExporter:
    """Exports a DNA profile to an interactive, executive-ready HTML dashboard."""

    def export(self, profile: dict, mermaid_graph: str = "") -> str:
        """Generate HTML string for the profile."""

        # Format GitHub Stats if present
        github_stats = ""
        if profile.get("github"):
            gh = profile["github"]
            if gh.get("is_github"):
                def _fmt_num(val):
                    if isinstance(val, str):
                        try:
                            val = float(val)
                            if val.is_integer():
                                val = int(val)
                        except ValueError:
                            pass
                    return f"{val:,}" if isinstance(val, (int, float)) else html_lib.escape(str(val))

                stars_str = _fmt_num(gh.get('stars', 0))
                forks_str = _fmt_num(gh.get('forks', 0))
                issues_str = _fmt_num(gh.get('issues', 0))

                github_stats = f"""
                <div class="flex items-center gap-4 mt-3 text-sm font-medium text-slate-400">
                    <span class="flex items-center gap-1"><span class="text-yellow-400">★</span> {stars_str}</span>
                    <span class="flex items-center gap-1"><span class="text-slate-300">⑂</span> {forks_str}</span>
                    <span class="flex items-center gap-1"><span class="text-green-400">⊙</span> {issues_str} issues</span>
                </div>
                """

        # Format Health
        health_score = profile["health"]["overall"]
        health_color = (
            "text-green-400" if health_score == "Healthy"
            else "text-yellow-400" if health_score == "Fair"
            else "text-orange-400" if health_score == "Needs Attention"
            else "text-red-500"
        )

        # Format Languages
        lang_bars = []
        for lang, data in profile.get("languages", {}).get("languages", {}).items():
            pct = data['percentage']
            color = self._lang_tw_color(lang)
            files = data.get('files', 0)
            lines_str = ""
            if "lines" in data and data["lines"] is not None:
                lines_str = f", {html_lib.escape(str(data['lines']))} lines"
            lang_bars.append(f"""
            <div>
                <div class="flex justify-between text-sm mb-1">
                    <span class="font-medium text-slate-200">{html_lib.escape(str(lang))}</span>
                    <span class="text-slate-400">{html_lib.escape(str(pct))}% <span class="text-xs ml-1">({html_lib.escape(str(files))} files{lines_str})</span></span>
                </div>
                <div class="w-full bg-slate-800 rounded-full h-2">
                    <div class="{color} h-2 rounded-full" style="width: {pct}%"></div>
                </div>
            </div>
            """)

        # Format Risks
        risks = profile.get("risks", [])
        risk_html = ""
        if not risks:
            risk_html = '<li class="text-green-400">✓ No critical risks detected.</li>'
        else:
            for risk in risks:
                icon = "🔴" if "🔴" in risk else "🟡"
                clean_risk = risk.replace("🔴 ", "").replace("🟡 ", "")
                risk_html += f'<li class="flex items-start gap-2 text-slate-300 risk-item"><span class="shrink-0">{icon}</span><span>{html_lib.escape(str(clean_risk))}</span></li>'

        # Architecture Traits
        traits = profile.get("architecture", {}).get("traits", [])
        traits_html = "".join(f'<li class="flex items-center gap-2"><span class="text-green-400">✓</span> {html_lib.escape(str(t))}</li>' for t in traits)
        if not traits_html:
            traits_html = '<li class="text-slate-500 italic">No standard traits detected</li>'

        # Developer Genome
        devs = profile.get("developer_genome", {}).get("top_contributors", [])
        devs_html = ""
        for d in devs:
            devs_html += f"""
            <div class="flex justify-between items-center bg-slate-800/60 p-2.5 rounded border border-slate-700/50">
                <div>
                    <p class="text-sm font-medium text-slate-200">{html_lib.escape(str(d['name']))}</p>
                    <p class="text-xs text-cyan-400">{html_lib.escape(str(d['role']))}</p>
                </div>
                <div class="text-right">
                    <p class="text-sm font-bold text-white">{html_lib.escape(str(d['commits']))}</p>
                    <p class="text-xs text-slate-500">commits</p>
                </div>
            </div>
            """

        # Evolution Patterns
        evo_patterns = profile.get("evolution", {}).get("patterns", [])
        evo_html = "".join(f'<span class="px-2 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded text-xs">{html_lib.escape(str(p))}</span>' for p in evo_patterns)

        # Mermaid Fallback
        if not mermaid_graph:
            mermaid_graph = "graph LR\n  A[No connection data found]"

        # Generate Pure SVG Radar Chart
        radar_chart_svg = self._generate_radar_svg(profile)

        # First commit date formatting
        first_commit_raw = profile.get("evolution", {}).get("first_commit")
        first_commit = html_lib.escape(str(first_commit_raw[:10])) if first_commit_raw else "Unknown"

        html = HTML_TEMPLATE.format(
            source=html_lib.escape(str(profile["metadata"]["source"])),
            analyzed_at=html_lib.escape(str(profile["metadata"]["analyzed_at"][:10])),
            github_stats=github_stats,
            signature=html_lib.escape(str(profile["signature"])),
            system_type=html_lib.escape(str(profile["system_type"])),
            health_score=html_lib.escape(str(health_score)),
            health_color=health_color,
            total_files=html_lib.escape(str(profile["structure_stats"]["total_files"])),
            total_contributors=html_lib.escape(str(profile["developer_genome"]["total_contributors"])),
            mermaid_graph=mermaid_graph,
            language_bars="\n".join(lang_bars),
            risk_signals=risk_html,
            architecture_traits=traits_html,
            traits_count=len(traits),
            bus_factor=html_lib.escape(str(profile["developer_genome"]["bus_factor"])),
            top_contributors=devs_html,
            total_commits=html_lib.escape(str(profile["evolution"]["total_commits"])),
            first_commit=first_commit,
            evolution_patterns=evo_html,
            radar_chart_svg=radar_chart_svg,
        )

        return html

    def _generate_radar_svg(self, profile: dict) -> str:
        """Generate a responsive, standalone 5-axis SVG radar chart."""
        cx, cy, r = 160, 140, 95
        axes = [
            ("Health", self._compute_health_metric(profile)),
            ("Security", self._compute_security_metric(profile)),
            ("Modularity", self._compute_modularity_metric(profile)),
            ("Cohesion", self._compute_cohesion_metric(profile)),
            ("Resilience", self._compute_resilience_metric(profile)),
        ]
        n = len(axes)
        angles = [-math.pi / 2 + (2 * math.pi * i / n) for i in range(n)]

        # Background grid polygons (20%, 40%, 60%, 80%, 100%)
        grid_polys = []
        for level in [0.2, 0.4, 0.6, 0.8, 1.0]:
            pts = []
            for angle in angles:
                x = cx + r * level * math.cos(angle)
                y = cy + r * level * math.sin(angle)
                pts.append(f"{x:.1f},{y:.1f}")
            grid_polys.append(
                f'<polygon points="{" ".join(pts)}" fill="none" stroke="#334155" stroke-width="1" stroke-dasharray="2 2"/>'
            )

        # Spoke lines & labels
        spokes = []
        labels = []
        for (name, val), angle in zip(axes, angles):
            x2 = cx + r * math.cos(angle)
            y2 = cy + r * math.sin(angle)
            spokes.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#334155" stroke-width="1"/>')

            # Label positioned slightly outside the radius
            lx = cx + (r + 24) * math.cos(angle)
            ly = cy + (r + 14) * math.sin(angle)
            anchor = "middle" if abs(math.cos(angle)) < 0.3 else ("start" if math.cos(angle) > 0 else "end")
            labels.append(
                f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#94a3b8" font-size="11" font-weight="600" text-anchor="{anchor}">{name}</text>'
            )

        # Data polygon
        data_pts = []
        data_circles = []
        for (name, val), angle in zip(axes, angles):
            clamped = max(0.1, min(1.0, val / 100.0))
            dx = cx + r * clamped * math.cos(angle)
            dy = cy + r * clamped * math.sin(angle)
            data_pts.append(f"{dx:.1f},{dy:.1f}")
            data_circles.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="4" fill="#38bdf8" stroke="#0f172a" stroke-width="2"/>')

        data_polygon = (
            f'<polygon points="{" ".join(data_pts)}" '
            f'fill="rgba(6, 182, 212, 0.28)" stroke="#06b6d4" stroke-width="2.5"/>'
        )

        svg = f"""
        <svg viewBox="0 0 320 290" class="radar-chart w-full max-w-[320px]">
            <defs>
                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over"/>
                </filter>
            </defs>
            {' '.join(grid_polys)}
            {' '.join(spokes)}
            {data_polygon}
            {' '.join(data_circles)}
            {' '.join(labels)}
        </svg>
        """
        return svg

    def _compute_health_metric(self, profile: dict) -> float:
        overall = profile.get("health", {}).get("overall", "Unknown")
        mapping = {"Healthy": 95, "Fair": 75, "Needs Attention": 50, "Critical": 25}
        return float(mapping.get(overall, 60))

    def _compute_security_metric(self, profile: dict) -> float:
        sec = profile.get("security", {})
        if sec.get("has_secrets", False):
            return 25.0
        crit = sec.get("total_critical", 0)
        return max(30.0, 100.0 - (crit * 20.0))

    def _compute_modularity_metric(self, profile: dict) -> float:
        deps = profile.get("dependencies", {})
        score = 85.0
        if deps.get("has_circular_deps"):
            score -= 30.0
        density = deps.get("density", 0.0)
        if density > 0.5:
            score -= 20.0
        return max(20.0, score)

    def _compute_cohesion_metric(self, profile: dict) -> float:
        arch = profile.get("architecture", {})
        patterns = arch.get("detected_patterns", [])
        if patterns:
            best_conf = patterns[0].get("confidence", 0.7)
            return round(best_conf * 100.0, 1)
        return 70.0

    def _compute_resilience_metric(self, profile: dict) -> float:
        dev = profile.get("developer_genome", {})
        bus = dev.get("bus_factor", 1)
        contribs = dev.get("total_contributors", 1)
        if bus >= 3 or contribs > 10:
            return 95.0
        elif bus == 2 or contribs > 3:
            return 75.0
        elif contribs > 1:
            return 55.0
        return 35.0

    def _lang_tw_color(self, lang: str) -> str:
        colors = {
            "Python": "bg-yellow-400",
            "JavaScript": "bg-yellow-300",
            "TypeScript": "bg-blue-400",
            "Go": "bg-cyan-400",
            "Rust": "bg-orange-500",
            "Java": "bg-red-500",
            "C#": "bg-purple-500",
            "Ruby": "bg-red-400",
            "PHP": "bg-indigo-400",
            "HTML": "bg-orange-400",
            "CSS": "bg-blue-500",
            "Shell": "bg-green-400",
        }
        return colors.get(lang, "bg-slate-400")
