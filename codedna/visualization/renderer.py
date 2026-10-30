"""Visualization Renderer — generates Rich terminal output and Mermaid diagrams."""

from __future__ import annotations

from rich.panel import Panel
from rich.table import Table


class Renderer:
    """Renders analysis results using Rich for beautiful terminal output."""

    def __init__(self, console=None):
        """Initialize the Renderer.

        Args:
            console: Optional rich Console instance. If None, it will be lazily
                     imported and instantiated to reduce module load time.
        """
        if console is None:
            from rich.console import Console
            self.console = Console()
        else:
            self.console = console

    def render_dna_profile(self, profile: dict) -> None:
        """Render the full DNA profile to the terminal."""
        self._render_header(profile)
        self._render_languages(profile)
        self._render_architecture(profile)
        self._render_health(profile)
        self._render_dependencies(profile)
        self._render_developers(profile)
        self._render_evolution(profile)
        self._render_signature(profile)

    def render_diff(self, diff: dict) -> None:
        """Render a comparative genetic drift report to the terminal."""
        meta = diff.get("metadata", {})
        source_a = meta.get("source_a", "Baseline (A)")
        source_b = meta.get("source_b", "Target (B)")
        sim = diff.get("similarity_score", 0.0)
        verdict = diff.get("mutation_verdict", "Unknown")

        sim_color = "green" if sim >= 80 else ("yellow" if sim >= 60 else "red")
        bar_len = int(sim / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)

        self.console.print()
        self.console.print(Panel(
            f"[bold cyan]🧬 CodeDNA Genetic Drift & Mutation Diff[/]\n\n"
            f"[white]Baseline (A):[/] [dim]{source_a}[/]\n"
            f"[white]Target   (B):[/] [dim]{source_b}[/]\n\n"
            f"[white]Genetic Similarity:[/] [bold {sim_color}]{sim}%[/] [{sim_color}]{bar}[/]\n"
            f"[white]Mutation Verdict:[/]   [bold cyan]{verdict}[/]",
            title="🧬 Architecture Diff",
            border_style="cyan",
            padding=(1, 2),
        ))

        # Comparison Table
        table = Table(title="📊 Architectural & Structural Drift", border_style="dim")
        table.add_column("Dimension", style="bold")
        table.add_column("Baseline (A)", justify="center")
        table.add_column("Target (B)", justify="center")
        table.add_column("Drift / Delta", justify="left")

        # Architecture Pattern
        arch = diff.get("architecture_shift", {})
        pat_a = arch.get("from_pattern", "?")
        pat_b = arch.get("to_pattern", "?")
        pat_delta = "[dim]Unchanged[/]" if not arch.get("pattern_changed") else f"[yellow]{pat_a} ➔ {pat_b}[/]"
        table.add_row("Architecture", pat_a, pat_b, pat_delta)

        # Health
        health = diff.get("health_shift", {})
        h_a = health.get("from_health", "?")
        h_b = health.get("to_health", "?")
        h_status = health.get("status", "unchanged")
        h_color = "green" if h_status == "improved" else ("red" if h_status == "degraded" else "dim")
        h_delta = f"[{h_color}]{h_status.capitalize()}[/] [dim](crit: {health.get('critical_smells_delta', 0):+d}, warn: {health.get('warning_smells_delta', 0):+d})[/]"  # noqa: E501
        table.add_row("Health Score", h_a, h_b, h_delta)

        # Files & Modules
        struct = diff.get("structure_delta", {})
        files_delta = struct.get("files", 0)
        f_color = "green" if files_delta >= 0 else "yellow"
        table.add_row("Files Count", "-", "-", f"[{f_color}]{files_delta:+d} files[/]")

        modules_delta = struct.get("modules", 0)
        table.add_row("Modules Count", "-", "-", f"{modules_delta:+d} modules")

        # Circular Dependencies
        dep = diff.get("dependency_shift", {})
        circ = dep.get("circular_deps", {})
        c_from = "Yes ⚠️" if circ.get("from") else "None ✅"
        c_to = "Yes ⚠️" if circ.get("to") else "None ✅"
        c_status = circ.get("status", "clean")
        c_color = "red" if c_status == "introduced" else ("green" if c_status == "resolved" else "dim")
        table.add_row("Circular Deps", c_from, c_to, f"[{c_color}]{c_status.capitalize()}[/]")

        # Connections
        edges_delta = dep.get("edges_delta", 0)
        table.add_row("Dependency Edges", "-", "-", f"{edges_delta:+d} connections")

        # Bus Factor
        dev = diff.get("developer_shift", {})
        bus_delta = dev.get("bus_factor_delta", 0)
        table.add_row("Bus Factor", "-", "-", f"{bus_delta:+d}")

        self.console.print(table)

        # Language shifts
        lang_deltas = diff.get("language_deltas", {})
        active_langs = {k: v for k, v in lang_deltas.items() if v.get("pct_a", 0) > 0 or v.get("pct_b", 0) > 0}
        if active_langs:
            lang_table = Table(title="🌐 Language Composition Drift", border_style="dim")
            lang_table.add_column("Language", style="bold")
            lang_table.add_column("Baseline (A)", justify="right")
            lang_table.add_column("Target (B)", justify="right")
            lang_table.add_column("Shift", justify="right")

            for lang, ldata in active_langs.items():
                delta = ldata.get("delta", 0.0)
                d_color = "green" if delta > 0 else ("red" if delta < 0 else "dim")
                lang_table.add_row(
                    lang,
                    f"{ldata.get('pct_a', 0.0):.1f}%",
                    f"{ldata.get('pct_b', 0.0):.1f}%",
                    f"[{d_color}]{delta:+0.1f}%[/]",
                )
            self.console.print(lang_table)
            self.console.print()

    def render_gatekeeper(self, result) -> None:
        """Render CI gatekeeper evaluation to the terminal."""
        self.console.print()
        status_color = "green" if result.passed else "red"
        status_text = "PASSED" if result.passed else "FAILED"

        self.console.print(Panel(
            f"[bold {status_color}]🛡️ CodeDNA Gatekeeper — {status_text}[/]\n\n"
            f"[white]Overall Health:[/] [bold]{result.overall_health}[/]\n"
            f"[white]Policies Evaluated:[/] {result.policies_evaluated}  |  "
            f"[green]Passed:[/] {result.policies_passed}  |  "
            f"[red]Failed:[/] {result.policies_failed}",
            title="CI Gatekeeper Evaluation",
            border_style=status_color,
            padding=(1, 2),
        ))

        table = Table(title="📋 Policy Evaluations", border_style="dim")
        table.add_column("Status", justify="center", width=8)
        table.add_column("Rule ID", style="cyan", width=13)
        table.add_column("Policy", style="bold")
        table.add_column("Severity", justify="center", width=10)
        table.add_column("Message")

        for eval_item in result.evaluations:
            mark = "[bold green]PASS[/]" if eval_item.passed else "[bold red]FAIL[/]"
            sev_color = "red" if eval_item.severity == "error" else "yellow"
            sev_text = f"[{sev_color}]{eval_item.severity.upper()}[/]"
            table.add_row(mark, eval_item.rule_id, eval_item.name, sev_text, eval_item.message)

        self.console.print(table)

        if result.passed:
            self.console.print("\n[bold green]✨ All architecture and quality gates passed successfully![/]\n")
        else:
            self.console.print(f"\n[bold red]❌ Quality gate breach: {result.policies_failed} policy check(s) failed.[/]\n")

    def _render_header(self, profile: dict) -> None:
        """Render the DNA header."""
        self.console.print()
        self.console.print(Panel(
            f"[bold cyan]🧬 CodeDNA Profile[/]\n\n"
            f"[white]Source:[/] [dim]{profile['metadata']['source']}[/]\n"
            f"[white]System:[/] [bold green]{profile['system_type']}[/]\n"
            f"[white]Date:[/] [dim]{profile['metadata']['analyzed_at'][:10]}[/]",
            border_style="cyan",
            padding=(1, 2),
        ))

    def _render_languages(self, profile: dict) -> None:
        """Render language distribution."""
        lang_data = profile.get("languages", {}).get("languages", {})
        if not lang_data:
            return

        table = Table(title="📊 Language Distribution", border_style="dim")
        table.add_column("Language", style="bold")
        table.add_column("Files", justify="right")
        table.add_column("Lines", justify="right")
        table.add_column("Share", justify="right")
        table.add_column("", min_width=20)

        for lang, data in lang_data.items():
            bar_len = max(1, int(data["percentage"] / 5))
            bar = "█" * bar_len + "░" * (20 - bar_len)
            color = self._lang_color(lang)

            lines_val = data['lines']
            if isinstance(lines_val, str):
                try:
                    lines_val = float(lines_val)
                    if lines_val.is_integer():
                        lines_val = int(lines_val)
                except ValueError:
                    pass

            lines_str = f"{lines_val:,}" if isinstance(lines_val, (int, float)) else str(lines_val)

            table.add_row(
                lang,
                str(data["files"]),
                lines_str,
                f"{data['percentage']}%",
                f"[{color}]{bar}[/]",
            )

        self.console.print(table)

    def _render_architecture(self, profile: dict) -> None:
        """Render architecture analysis."""
        arch = profile.get("architecture", {})
        patterns = arch.get("detected_patterns", [])
        traits = arch.get("traits", [])

        if not patterns and not traits:
            return

        lines = []
        if patterns:
            lines.append("[bold]Detected Patterns:[/]")
            for p in patterns:
                conf = int(p["confidence"] * 100)
                bar = "█" * (conf // 10)
                lines.append(f"  • {p['pattern']} [dim]({conf}%)[/] [green]{bar}[/]")

        if traits:
            lines.append("\n[bold]Infrastructure Traits:[/]")
            for t in traits:
                lines.append(f"  ✅ {t}")

        lines.append(f"\n[bold]Coupling:[/] {arch.get('coupling', 'Unknown')}")

        self.console.print(Panel(
            "\n".join(lines),
            title="🏗️ Architecture",
            border_style="blue",
        ))

    def _render_health(self, profile: dict) -> None:
        """Render health assessment."""
        health = profile.get("health", {})
        overall = health.get("overall", "Unknown")
        counts = health.get("severity_counts", {})

        color = {"Healthy": "green", "Fair": "yellow", "Needs Attention": "dark_orange", "Critical": "red"}.get(overall, "white")  # noqa: E501

        risks = profile.get("risks", [])
        risk_text = "\n".join(risks[:6]) if risks else "  No critical risks detected ✅"

        self.console.print(Panel(
            f"[bold {color}]Overall: {overall}[/]\n\n"
            f"🔴 Critical: {counts.get('critical', 0)}  "
            f"🟡 Warning: {counts.get('warning', 0)}  "
            f"🔵 Info: {counts.get('info', 0)}\n\n"
            f"[bold]Risk Signals:[/]\n{risk_text}",
            title="🩺 Health",
            border_style=color,
        ))

    def _render_dependencies(self, profile: dict) -> None:
        """Render dependency graph stats."""
        deps = profile.get("dependencies", {})
        circular = "Yes ⚠️" if deps.get("has_circular_deps") else "None ✅"

        self.console.print(Panel(
            f"Modules: [bold]{deps.get('total_modules', 0)}[/]\n"
            f"Connections: [bold]{deps.get('total_edges', 0)}[/]\n"
            f"Density: [bold]{deps.get('density', 0)}[/]\n"
            f"Circular Deps: [bold]{circular}[/]",
            title="🔗 Dependency Graph",
            border_style="magenta",
        ))

    def _render_developers(self, profile: dict) -> None:
        """Render developer genome."""
        dev = profile.get("developer_genome", {})
        contribs = dev.get("top_contributors", [])

        if not contribs:
            return

        table = Table(title="👥 Developer Genome", border_style="dim")
        table.add_column("Developer", style="bold")
        table.add_column("Role", style="cyan")
        table.add_column("Commits", justify="right")

        for c in contribs:
            table.add_row(c["name"], c["role"], str(c["commits"]))

        self.console.print(table)
        self.console.print(f"  Bus Factor: [bold]{dev.get('bus_factor', '?')}[/]")

    def _render_evolution(self, profile: dict) -> None:
        """Render evolution timeline."""
        evo = profile.get("evolution", {})
        patterns = evo.get("patterns", [])

        self.console.print(Panel(
            f"Total Commits: [bold]{evo.get('total_commits', 0)}[/]\n"
            f"First Commit: [dim]{(evo.get('first_commit') or '?')[:10]}[/]\n"
            f"Patterns: [bold cyan]{', '.join(patterns) if patterns else 'Unknown'}[/]",
            title="📈 Evolution",
            border_style="green",
        ))

    def _render_signature(self, profile: dict) -> None:
        """Render the DNA signature."""
        sig = profile.get("signature", "")
        self.console.print(Panel(
            f"[bold cyan]{sig}[/]",
            title="🧬 DNA Signature",
            border_style="bright_cyan",
            padding=(1, 2),
        ))
        self.console.print()

    def _lang_color(self, lang: str) -> str:
        colors = {
            "Python": "yellow",
            "JavaScript": "bright_yellow",
            "TypeScript": "blue",
            "Go": "cyan",
            "Rust": "red",
            "Java": "bright_red",
            "C#": "magenta",
            "Ruby": "red",
            "PHP": "blue",
        }
        return colors.get(lang, "white")
