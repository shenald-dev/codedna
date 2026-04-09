"""CodeDNA CLI — main command-line interface."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@click.group()
@click.version_option(version="1.0.9", prog_name="codedna")
def main():
    """🧬 CodeDNA — A genetic analyzer for software.

    Reverse-engineer any codebase into a DNA profile describing its
    architecture, structure, evolution, and developer patterns.
    """
    pass


@main.command()
@click.argument("source")
@click.option("--output", "-o", type=click.Path(), help="Output directory for reports")
@click.option("--format", "-f", "fmt", type=click.Choice(["markdown", "json", "html", "all"]), default="all", help="Output format")  # noqa: E501
@click.option("--depth", "-d", type=int, default=100, help="Git history depth (commits to analyze)")
@click.option("--no-visualize", is_flag=True, help="Skip terminal visualization")
@click.option("--ai", is_flag=True, help="Synthesize an Executive Summary via LLM")
def analyze(source: str, output: str | None, fmt: str, depth: int, no_visualize: bool, ai: bool):
    """Analyze a repository and generate its DNA profile.

    SOURCE can be a GitHub URL or a local path to a repository.

    \b
    Examples:
        codedna analyze https://github.com/user/project
        codedna analyze ./my-local-project
        codedna analyze . --output reports/
    """
    from .analyzers.ai_analyzer import AIAnalyzer
    from .analyzers.architecture_detector import ArchitectureDetector
    from .analyzers.code_smell_detector import CodeSmellDetector
    from .analyzers.dependency_mapper import DependencyMapper
    from .analyzers.developer_analyzer import DeveloperAnalyzer
    from .analyzers.dna_generator import DNAGenerator
    from .analyzers.evolution_engine import EvolutionEngine
    from .analyzers.github_analyzer import GitHubAnalyzer
    from .analyzers.language_detector import LanguageDetector
    from .analyzers.repo_cloner import RepoCloner
    from .analyzers.security_detector import SecurityDetector
    from .analyzers.structure_analyzer import StructureAnalyzer
    from .visualization.html_export import HTMLExporter
    from .visualization.renderer import Renderer

    console.print("\n[bold cyan]🧬 CodeDNA[/] [dim]v1.0.9[/]")
    console.print("[dim]━" * 50 + "[/]\n")

    cloner = RepoCloner()

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # ── Stage 1: Clone / Resolve ──
            task = progress.add_task("📥 Resolving repository...", total=None)
            repo_path = cloner.clone(source)
            progress.update(task, description="[green]✓[/] Repository resolved")

            # ── Stage 2: Language Detection ──
            progress.update(task, description="🔍 Detecting languages...")
            languages = LanguageDetector().detect(repo_path)
            progress.update(task, description=f"[green]✓[/] Found {len(languages.get('languages', {}))} languages")  # noqa: E501

            # ── Stage 3: Structure Analysis ──
            progress.update(task, description="📁 Analyzing structure...")
            structure = StructureAnalyzer().analyze(repo_path)
            progress.update(task, description=f"[green]✓[/] {structure.get('total_files', 0)} files analyzed")  # noqa: E501

            # ── Stage 4: Dependency Mapping ──
            progress.update(task, description="🔗 Mapping dependencies...")
            mapper = DependencyMapper()
            dependencies = mapper.map(repo_path)
            mermaid_graph = mapper.build_mermaid(repo_path)
            progress.update(task, description=f"[green]✓[/] {dependencies.get('total_edges', 0)} dependency edges found")  # noqa: E501

            # ── Stage 5: Architecture Detection ──
            progress.update(task, description="🏗️ Detecting architecture patterns...")
            architecture = ArchitectureDetector().detect(repo_path)
            progress.update(task, description=f"[green]✓[/] Pattern: {architecture.get('primary_pattern', '?')}")  # noqa: E501

            # ── Stage 6: Code Smell Detection ──
            progress.update(task, description="🐛 Scanning for code smells...")
            smells = CodeSmellDetector().detect(repo_path)
            progress.update(task, description=f"[green]✓[/] {smells.get('total', 0)} issues found")

            # ── Stage 6.5: Security Scanning ──
            progress.update(task, description="🔒 Scanning for security vulnerabilities...")
            security = SecurityDetector().detect(repo_path)
            progress.update(task, description=f"[green]✓[/] {security.get('total_critical', 0)} critical vulnerabilities")  # noqa: E501

            # ── Stage 7: Developer Analysis ──
            progress.update(task, description="👥 Analyzing developer behavior...")
            developers = DeveloperAnalyzer().analyze(repo_path, max_commits=depth)
            progress.update(task, description=f"[green]✓[/] {developers.get('total_contributors', 0)} contributors")  # noqa: E501

            # ── Stage 8: Evolution Engine ──
            progress.update(task, description="📈 Tracking evolution...")
            evolution = EvolutionEngine().analyze(repo_path)
            progress.update(task, description="[green]✓[/] Evolution timeline built")

            # ── Stage 8.5: GitHub Analysis ──
            progress.update(task, description="🌐 Fetching GitHub community stats...")
            github_stats = GitHubAnalyzer().analyze(source)
            progress.update(task, description="[green]✓[/] GitHub stats retrieved")

            # ── Stage 9: DNA Generation ──
            progress.update(task, description="🧬 Generating DNA profile...")
            generator = DNAGenerator()
            profile = generator.generate(
                repo_source=source,
                languages=languages,
                structure=structure,
                dependencies=dependencies,
                architecture=architecture,
                smells=smells,
                developers=developers,
                evolution=evolution,
                security=security,
                github=github_stats,
                mermaid_graph=mermaid_graph,
            )

            # ── Stage 10: AI Synthesis ──
            if ai:
                progress.update(task, description="🧠 Synthesizing executive insights via AI...")
                ai_result = AIAnalyzer().synthesize(profile)
                if ai_result.success:
                    profile["ai_insights"] = {
                        "executive_summary": ai_result.executive_summary,
                        "refactoring_recommendations": ai_result.refactoring_recommendations
                    }
                else:
                    console.print(f"[yellow]⚠️ AI Synthesis failed:[/] {ai_result.error_message}")

            progress.update(task, description="[bold green]✓ DNA profile complete![/]")

        # ── Render to terminal ──
        if not no_visualize:
            Renderer().render_dna_profile(profile)

        # ── Save outputs ──
        if output:
            output_dir = Path(output)
            output_dir.mkdir(parents=True, exist_ok=True)

            if fmt in ("markdown", "all"):
                md_path = output_dir / "dna_report.md"
                md_path.write_text(generator.to_markdown(profile), encoding="utf-8")
                console.print(f"\n  📄 Report saved: [cyan]{md_path}[/]")

            if fmt in ("json", "all"):
                json_path = output_dir / "dna_profile.json"
                json_path.write_text(generator.to_json(profile), encoding="utf-8")
                console.print(f"  📊 Data saved: [cyan]{json_path}[/]")

            if fmt in ("html", "all"):
                html_path = output_dir / "dna_dashboard.html"
                exporter = HTMLExporter()
                html_path.write_text(exporter.export(profile, mermaid_graph), encoding="utf-8")
                console.print(f"  🌐 Dashboard saved: [cyan]{html_path}[/]")

        console.print("\n[bold green]✨ Analysis complete![/]\n")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/] {e}")
        sys.exit(1)
    finally:
        # Only cleanup if we cloned (not local)
        if source.startswith("http"):
            cloner.cleanup()


if __name__ == "__main__":
    main()
