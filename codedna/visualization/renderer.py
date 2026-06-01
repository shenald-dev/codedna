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
