
"""HTML Export — generates interactive HTML dashboards for CodeDNA profiles."""

from __future__ import annotations

import html as html_lib

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
        body {{ background-color: #0f172a; color: #f8fafc; }}
        .card {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 0.5rem; }}
        .header-bg {{ background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%); border-bottom: 1px solid #334155; }}  # noqa: E501
    </style>
</head>
<body class="min-h-screen font-sans antialiased">

<div class="header-bg py-10 px-6">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center group">
        <div>
            <h1 class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mb-2">  # noqa: E501
                🧬 CodeDNA Profile
            </h1>
            <p class="text-slate-400 text-lg flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>  # noqa: E501
                {source}
            </p>
            {github_stats}
        </div>
        <div class="mt-4 md:mt-0 text-right">
            <span class="inline-block px-4 py-2 rounded-full bg-slate-800 border border-slate-700 font-mono text-cyan-400 font-semibold shadow-xl">  # noqa: E501
                {signature}
            </span>
            <p class="text-sm text-slate-500 mt-2">Analyzed on {analyzed_at}</p>
        </div>
    </div>
</div>

<main class="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 md:grid-cols-12 gap-6">

    <!-- Overviews -->
    <div class="md:col-span-12 grid grid-cols-1 md:grid-cols-4 gap-6">
        <div class="card p-6 flex flex-col justify-center">
            <h3 class="text-slate-400 text-sm uppercase tracking-wider font-semibold mb-1">System Type</h3>  # noqa: E501
            <p class="text-2xl font-bold text-white">{system_type}</p>
        </div>
        <div class="card p-6 flex flex-col justify-center">
            <h3 class="text-slate-400 text-sm uppercase tracking-wider font-semibold mb-1">Overall Health</h3>  # noqa: E501
            <p class="text-2xl font-bold {health_color}">{health_score}</p>
        </div>
        <div class="card p-6 flex flex-col justify-center">
            <h3 class="text-slate-400 text-sm uppercase tracking-wider font-semibold mb-1">Total Files</h3>  # noqa: E501
            <p class="text-2xl font-bold text-white">{total_files}</p>
        </div>
        <div class="card p-6 flex flex-col justify-center">
            <h3 class="text-slate-400 text-sm uppercase tracking-wider font-semibold mb-1">Contributors</h3>  # noqa: E501
            <p class="text-2xl font-bold text-white">{total_contributors}</p>
        </div>
    </div>

    <!-- Main Content Left Column -->
    <div class="md:col-span-8 flex flex-col gap-6">

        <!-- Architecture Graph -->
        <div class="card p-6">
            <h2 class="text-xl font-bold text-slate-200 mb-4 flex items-center gap-2">
                🔗 Module Dependencies
            </h2>
            <div class="bg-slate-900 rounded-lg p-4 w-full overflow-x-auto min-h-[300px] flex items-center justify-center">  # noqa: E501
                <div class="mermaid">
{mermaid_graph}
                </div>
            </div>
        </div>

        <!-- Languages -->
        <div class="card p-6">
            <h2 class="text-xl font-bold text-slate-200 mb-4 flex items-center gap-2">
                📊 Language Distribution
            </h2>
            <div class="space-y-4">
                {language_bars}
            </div>
        </div>

    </div>

    <!-- Sidebar Right Column -->
    <div class="md:col-span-4 flex flex-col gap-6">

        <!-- Risk Signals -->
        <div class="card p-6 border-l-4 border-l-red-500">
            <h2 class="text-xl font-bold text-slate-200 mb-4 flex items-center gap-2">
                ⚠️ Risk Signals
            </h2>
            <ul class="space-y-3 text-sm">
                {risk_signals}
            </ul>
        </div>

        <!-- Architecture Traits -->
        <div class="card p-6">
            <h2 class="text-xl font-bold text-slate-200 mb-4 flex items-center gap-2">
                🏗️ Architecture Traits
            </h2>
            <ul class="space-y-2 text-sm text-slate-300">
                {architecture_traits}
            </ul>
        </div>

        <!-- Developer Genome -->
        <div class="card p-6">
            <h2 class="text-xl font-bold text-slate-200 mb-4 flex items-center gap-2">
                👥 Developer Genome
            </h2>
            <p class="text-sm text-slate-400 mb-3">Bus Factor: <strong class="text-white">{bus_factor}</strong></p>  # noqa: E501
            <div class="space-y-3 mt-4">
                {top_contributors}
            </div>
        </div>

        <!-- Evolution -->
        <div class="card p-6">
            <h2 class="text-xl font-bold text-slate-200 mb-4 flex items-center gap-2">
                📈 Evolution
            </h2>
            <ul class="space-y-2 text-sm text-slate-300">
                <li class="flex justify-between"><span>Total Commits</span> <strong class="text-white">{total_commits}</strong></li>  # noqa: E501
                <li class="flex justify-between"><span>First Commit</span> <strong class="text-white">{first_commit}</strong></li>  # noqa: E501
            </ul>
            <div class="mt-4 pt-4 border-t border-slate-700">
                <p class="text-xs text-slate-500 uppercase font-semibold mb-2">Detected Patterns</p>
                <div class="flex flex-wrap gap-2">
                    {evolution_patterns}
                </div>
            </div>
        </div>

    </div>

</main>

<footer class="border-t border-slate-800 py-6 text-center text-slate-500 text-sm">
    Generated by <a href="https://github.com/shenald-dev/codedna" class="text-cyan-400 hover:underline">CodeDNA</a> — A genetic analyzer for software.  # noqa: E501
</footer>

</body>
</html>
"""




class HTMLExporter:
    """Exports a DNA profile to an interactive HTML dashboard."""

    def export(self, profile: dict, mermaid_graph: str = "") -> str:
        """Generate HTML string for the profile."""

        # Format GitHub Stats if present
        github_stats = ""
        if profile.get("github"):
            gh = profile["github"]
            if gh.get("is_github"):
                github_stats = f"""
                <div class="flex items-center gap-4 mt-3 text-sm font-medium text-slate-400">
                    <span class="flex items-center gap-1"><span class="text-yellow-400">★</span> {gh.get('stars', 0):,}</span>  # noqa: E501
                    <span class="flex items-center gap-1"><span class="text-slate-300">⑂</span> {gh.get('forks', 0):,}</span>  # noqa: E501
                    <span class="flex items-center gap-1"><span class="text-green-400">⊙</span> {gh.get('issues', 0):,} issues</span>  # noqa: E501
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
            lang_bars.append(f"""
            <div>
                <div class="flex justify-between text-sm mb-1">
                    <span class="font-medium text-slate-200">{html_lib.escape(str(lang))}</span>
                    <span class="text-slate-400">{pct}% <span class="text-xs ml-1">({data.get('files', 0)} files)</span></span>  # noqa: E501
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
                clean_risk = html_lib.escape(str(risk.replace("🔴 ", "").replace("🟡 ", "")))
                risk_html += f'<li class="flex items-start gap-2 text-slate-300"><span class="shrink-0">{icon}</span><span>{clean_risk}</span></li>'  # noqa: E501

        # Architecture Traits
        traits = profile.get("architecture", {}).get("traits", [])
        traits_html = "".join(f'<li class="flex items-center gap-2"><span class="text-green-400">✓</span> {html_lib.escape(str(t))}</li>' for t in traits)  # noqa: E501
        if not traits_html:
            traits_html = '<li class="text-slate-500 italic">No standard traits detected</li>'

        # Developer Genome
        devs = profile.get("developer_genome", {}).get("top_contributors", [])
        devs_html = ""
        for d in devs:
            devs_html += f"""
            <div class="flex justify-between items-center bg-slate-800/50 p-2 rounded">
                <div>
                    <p class="text-sm font-medium text-slate-200">{html_lib.escape(str(d.get('name', '')))}</p>
                    <p class="text-xs text-cyan-400">{html_lib.escape(str(d.get('role', '')))}</p>
                </div>
                <div class="text-right">
                    <p class="text-sm font-bold text-white">{d.get('commits', 0)}</p>
                    <p class="text-xs text-slate-500">commits</p>
                </div>
            </div>
            """

        # Evolution Patterns
        evo_patterns = profile.get("evolution", {}).get("patterns", [])
        evo_html = "".join(f'<span class="px-2 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded text-xs">{html_lib.escape(str(p))}</span>' for p in evo_patterns)  # noqa: E501

        # Mermaid Fallback
        if not mermaid_graph:
            mermaid_graph = "graph LR\n  A[No connection data found]"

        html_out = HTML_TEMPLATE.format(
            source=html_lib.escape(str(profile["metadata"]["source"])),
            analyzed_at=html_lib.escape(str(profile["metadata"]["analyzed_at"][:10])),
            github_stats=github_stats,
            signature=html_lib.escape(str(profile["signature"])),
            system_type=html_lib.escape(str(profile["system_type"])),
            health_score=html_lib.escape(str(health_score)),
            health_color=health_color,
            total_files=profile["structure_stats"]["total_files"],
            total_contributors=profile["developer_genome"]["total_contributors"],
            mermaid_graph=html_lib.escape(str(mermaid_graph)),
            language_bars="\n".join(lang_bars),
            risk_signals=risk_html,
            architecture_traits=traits_html,
            bus_factor=profile["developer_genome"]["bus_factor"],
            top_contributors=devs_html,
            total_commits=profile["evolution"]["total_commits"],
            first_commit=html_lib.escape(str(profile["evolution"].get("first_commit", "")[:10] if profile["evolution"].get("first_commit") else "Unknown")),  # noqa: E501
            evolution_patterns=evo_html
        )

        return html_out

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
