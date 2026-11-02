"""CodeDNA CLI — main command-line interface."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from . import __version__

# Ensure UTF-8 output encoding on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _analyze_repo(source: str, depth: int, console, ai: bool = False):
    """Run full analysis pipeline on a source repository or local directory.

    Returns:
        tuple: (profile, mermaid_graph, cloner)
    """
    from rich.progress import Progress, SpinnerColumn, TextColumn

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
    from .config import load_config

    # If source is an existing JSON file, load directly
    source_path = Path(source)
    if source_path.is_file() and source.endswith(".json"):
        try:
            profile = json.loads(source_path.read_text(encoding="utf-8"))
            mermaid_graph = profile.get("mermaid_graph", "")
            return profile, mermaid_graph, None
        except Exception as e:
            console.print(f"[yellow]⚠️ Failed to parse '{source}' as DNA JSON ({e}), analyzing as path...[/]")

    cloner = RepoCloner(console=console)
    mermaid_graph = ""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # ── Stage 1: Clone / Resolve ──
        task = progress.add_task(f"📥 Resolving '{source}'...", total=None)
        repo_path = cloner.clone(source)
        progress.update(task, description="[green]✓[/] Repository resolved")

        # Load project configuration if present
        config = load_config(repo_path)

        # ── Stage 2: Language Detection ──
        progress.update(task, description="🔍 Detecting languages...")
        languages = LanguageDetector().detect(repo_path)
        progress.update(task, description=f"[green]✓[/] Found {len(languages.get('languages', {}))} languages")

        # ── Stage 3: Structure Analysis ──
        progress.update(task, description="📁 Analyzing structure...")
        structure = StructureAnalyzer().analyze(repo_path)
        progress.update(task, description=f"[green]✓[/] {structure.get('total_files', 0)} files analyzed")

        # ── Stage 4: Dependency Mapping ──
        progress.update(task, description="🔗 Mapping dependencies...")
        mapper = DependencyMapper()
        dependencies = mapper.map(repo_path)
        mermaid_graph = mapper.build_mermaid(dependencies)
        progress.update(task, description=f"[green]✓[/] {dependencies.get('total_edges', 0)} dependency edges found")

        # ── Stage 5: Architecture Detection ──
        progress.update(task, description="🏗️ Detecting architecture patterns...")
        architecture = ArchitectureDetector().detect(repo_path)
        progress.update(task, description=f"[green]✓[/] Pattern: {architecture.get('primary_pattern', '?')}")

        # ── Stage 6: Code Smell Detection ──
        progress.update(task, description="🐛 Scanning for code smells...")
        smells = CodeSmellDetector(config=config).detect(repo_path)
        progress.update(task, description=f"[green]✓[/] {smells.get('total', 0)} issues found")

        # ── Stage 6.5: Security Scanning ──
        progress.update(task, description="🔒 Scanning for security vulnerabilities...")
        security = SecurityDetector(config=config).detect(repo_path)
        progress.update(task, description=f"[green]✓[/] {security.get('total_critical', 0)} critical vulnerabilities")

        # ── Stage 7: Developer Analysis ──
        progress.update(task, description="👥 Analyzing developer behavior...")
        developers = DeveloperAnalyzer().analyze(repo_path, max_commits=depth)
        progress.update(task, description=f"[green]✓[/] {developers.get('total_contributors', 0)} contributors")

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
                    "refactoring_recommendations": ai_result.refactoring_recommendations,
                }
            else:
                console.print(f"[yellow]⚠️ AI Synthesis failed:[/] {ai_result.error_message}")

        progress.update(task, description="[bold green]✓ DNA profile complete![/]")

    return profile, mermaid_graph, cloner


@click.group()
@click.version_option(version=__version__, prog_name="codedna")
def main():
    """🧬 CodeDNA — A genetic analyzer for software.

    Reverse-engineer any codebase into a DNA profile describing its
    architecture, structure, evolution, and developer patterns.
    """
    pass


@main.command()
@click.argument("directory", default=".")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing codedna.toml configuration file")
def init(directory: str, force: bool):
    """Scaffold a starter codedna.toml configuration file in DIRECTORY."""
    from rich.console import Console

    from .config import generate_default_config_toml

    console = Console()
    target_dir = Path(directory).resolve()
    target_file = target_dir / "codedna.toml"

    if target_file.exists() and not force:
        console.print(f"[yellow]⚠️ Configuration file already exists:[/] {target_file}")
        console.print("[dim]Use --force to overwrite.[/]")
        return

    target_dir.mkdir(parents=True, exist_ok=True)
    content = generate_default_config_toml()
    target_file.write_text(content, encoding="utf-8")
    console.print(f"\n[bold green]✓ Initialized CodeDNA configuration:[/] [cyan]{target_file}[/]")
    console.print("[dim]Edit this file to customize smell thresholds, secret whitelists, and CI gate policies.[/]\n")


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
    from rich.console import Console

    from .analyzers.dna_generator import DNAGenerator
    from .visualization.html_export import HTMLExporter
    from .visualization.renderer import Renderer

    console = Console()
    console.print(f"\n[bold cyan]🧬 CodeDNA[/] [dim]v{__version__}[/]")
    console.print("[dim]━" * 50 + "[/]\n")

    cloner = None
    try:
        profile, mermaid_graph, cloner = _analyze_repo(source, depth, console, ai=ai)

        # ── Render to terminal ──
        if not no_visualize:
            Renderer(console=console).render_dna_profile(profile)

        # ── Save outputs ──
        if output:
            output_dir = Path(output)
            output_dir.mkdir(parents=True, exist_ok=True)
            generator = DNAGenerator()

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
        if cloner is not None and source.startswith("http"):
            cloner.cleanup()


@main.command()
@click.argument("source_a")
@click.argument("source_b")
@click.option("--output", "-o", type=click.Path(), help="Output path for diff report (file or directory)")
@click.option("--format", "-f", "fmt", type=click.Choice(["terminal", "json", "markdown", "all"]), default="terminal", help="Output format")  # noqa: E501
@click.option("--depth", "-d", type=int, default=100, help="Git history depth for analysis")
@click.option("--fail-on-drift/--no-fail-on-drift", default=False, help="Fail with exit code 1 if architectural drift regression is detected")  # noqa: E501
def diff(source_a: str, source_b: str, output: str | None, fmt: str, depth: int, fail_on_drift: bool):
    """Compare two codebases or DNA profiles to compute genetic drift.

    SOURCE_A and SOURCE_B can each be a local path, GitHub URL, or a pre-generated dna_profile.json file.

    \b
    Examples:
        codedna diff ./repo-main ./repo-refactor
        codedna diff reports/dna_profile_v1.json reports/dna_profile_v2.json
        codedna diff https://github.com/org/repo-a https://github.com/org/repo-b --format markdown
    """
    from rich.console import Console

    from .analyzers.diff_engine import DiffEngine
    from .visualization.renderer import Renderer

    console = Console()
    console.print(f"\n[bold cyan]🧬 CodeDNA Genetic Diff[/] [dim]v{__version__}[/]")
    console.print("[dim]━" * 50 + "[/]\n")

    cloner_a = None
    cloner_b = None
    try:
        console.print("[bold]Baseline (A):[/]")
        profile_a, _, cloner_a = _analyze_repo(source_a, depth, console)

        console.print("\n[bold]Target (B):[/]")
        profile_b, _, cloner_b = _analyze_repo(source_b, depth, console)

        engine = DiffEngine()
        diff_result = engine.compare(profile_a, profile_b)

        # Terminal rendering
        if fmt in ("terminal", "all"):
            Renderer(console=console).render_diff(diff_result)

        # Output saving
        if output:
            out_path = Path(output)
            if out_path.is_dir() or (not out_path.suffix and not out_path.exists()):
                out_path.mkdir(parents=True, exist_ok=True)
                json_file = out_path / "dna_diff.json"
                md_file = out_path / "dna_diff.md"
            else:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                json_file = out_path if out_path.suffix == ".json" else out_path.with_suffix(".json")
                md_file = out_path if out_path.suffix == ".md" else out_path.with_suffix(".md")

            if fmt in ("json", "all"):
                json_file.write_text(engine.to_json(diff_result), encoding="utf-8")
                console.print(f"  📊 Diff data saved: [cyan]{json_file}[/]")

            if fmt in ("markdown", "all"):
                md_file.write_text(engine.to_markdown(diff_result), encoding="utf-8")
                console.print(f"  📄 Diff report saved: [cyan]{md_file}[/]")

        elif fmt == "json":
            click.echo(engine.to_json(diff_result))
        elif fmt == "markdown":
            click.echo(engine.to_markdown(diff_result))

        if fail_on_drift:
            passed, reasons = DiffEngine.evaluate_drift_gate(diff_result)
            if not passed:
                console.print(f"\n[bold red]❌ Drift gate breach: {len(reasons)} regression(s) detected.[/]")
                for r in reasons:
                    console.print(f"  • [red]{r}[/]")
                sys.exit(1)

    except SystemExit:
        raise
    except Exception as e:
        console.print(f"\n[bold red]❌ Error during diff:[/] {e}")
        sys.exit(1)
    finally:
        if cloner_a is not None and source_a.startswith("http"):
            cloner_a.cleanup()
        if cloner_b is not None and source_b.startswith("http"):
            cloner_b.cleanup()


@main.command()
@click.argument("baseline")
@click.argument("target")
@click.option("--allow-degradation/--no-allow-degradation", default=False, help="Allow health score degradation (e.g. Healthy -> Fair)")  # noqa: E501
@click.option("--allow-circular/--no-allow-circular", default=False, help="Allow newly introduced circular dependencies")
@click.option("--allow-secrets/--no-allow-secrets", default=False, help="Allow newly introduced secrets/credentials")
@click.option("--min-similarity", type=float, default=0.0, help="Minimum allowable genetic similarity score (0-100)")
@click.option("--format", "-f", "fmt", type=click.Choice(["terminal", "json", "markdown"]), default="terminal", help="Output format")  # noqa: E501
@click.option("--output", "-o", type=click.Path(), help="Output file path for drift gate report")
@click.option("--depth", "-d", type=int, default=100, help="Git history depth for analysis")
def gate(
    baseline: str,
    target: str,
    allow_degradation: bool,
    allow_circular: bool,
    allow_secrets: bool,
    min_similarity: float,
    fmt: str,
    output: str | None,
    depth: int,
):
    """Evaluate architectural drift between BASELINE and TARGET for CI/CD regression gating.

    Exits with code 0 if within acceptable drift parameters, or code 1 on regression breach.
    """
    from rich.console import Console

    from .analyzers.diff_engine import DiffEngine
    from .visualization.renderer import Renderer

    console = Console()
    console.print(f"\n[bold cyan]🛡️ CodeDNA Drift Regression Gate[/] [dim]v{__version__}[/]")
    console.print("[dim]━" * 50 + "[/]\n")

    cloner_a = None
    cloner_b = None
    try:
        console.print("[bold]Baseline (A):[/]")
        profile_a, _, cloner_a = _analyze_repo(baseline, depth, console)

        console.print("\n[bold]Target (B):[/]")
        profile_b, _, cloner_b = _analyze_repo(target, depth, console)

        engine = DiffEngine()
        diff_result = engine.compare(profile_a, profile_b)

        passed, reasons = DiffEngine.evaluate_drift_gate(
            diff=diff_result,
            allow_degradation=allow_degradation,
            allow_circular_deps=allow_circular,
            allow_new_secrets=allow_secrets,
            min_similarity=min_similarity,
        )

        # Terminal rendering
        if fmt == "terminal":
            Renderer(console=console).render_drift_gate(passed, reasons, diff_result)

        # JSON export
        gate_data = {
            "passed": passed,
            "reasons": reasons,
            "similarity_score": diff_result.get("similarity_score", 0.0),
            "mutation_verdict": diff_result.get("mutation_verdict", "Unknown"),
            "diff": diff_result,
        }

        if fmt == "json" or (output and output.endswith(".json")):
            gate_json = json.dumps(gate_data, indent=2)
            if output:
                out_path = Path(output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(gate_json, encoding="utf-8")
                console.print(f"  📊 Drift gate JSON written: [cyan]{out_path}[/]")
            else:
                click.echo(gate_json)

        # Markdown export
        elif fmt == "markdown" or (output and output.endswith(".md")):
            md_lines = [
                "# 🛡️ CodeDNA Architectural Drift Regression Gate",
                "",
                f"**Status:** {'✅ PASSED' if passed else '❌ FAILED'}",
                f"**Genetic Similarity:** {diff_result.get('similarity_score', 0.0)}%",
                f"**Mutation Verdict:** `{diff_result.get('mutation_verdict', 'Unknown')}`",
                "",
            ]
            if reasons:
                md_lines.append("### ⚠️ Drift Violations")
                md_lines.append("")
                for r in reasons:
                    md_lines.append(f"- ❌ {r}")
                md_lines.append("")
            else:
                md_lines.append("✨ No architectural regression detected. All drift checks passed.")
                md_lines.append("")
            md_str = "\n".join(md_lines)
            if output:
                out_path = Path(output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(md_str, encoding="utf-8")
                console.print(f"  📄 Drift gate Markdown written: [cyan]{out_path}[/]")
            else:
                click.echo(md_str)

        if not passed:
            sys.exit(1)
        sys.exit(0)

    except SystemExit:
        raise
    except Exception as e:
        console.print(f"\n[bold red]❌ Error during drift gate check:[/] {e}")
        sys.exit(1)
    finally:
        if cloner_a is not None and baseline.startswith("http"):
            cloner_a.cleanup()
        if cloner_b is not None and target.startswith("http"):
            cloner_b.cleanup()


@main.command()
@click.argument("source", default=".")
@click.option("--min-health", type=click.Choice(["Healthy", "Fair", "Needs Attention", "Critical"], case_sensitive=False), default="Fair", help="Minimum allowable overall health rating")  # noqa: E501
@click.option("--max-smells", type=int, default=None, help="Maximum allowable total code smells")
@click.option("--max-critical-smells", type=int, default=0, help="Maximum allowable critical code smells (default: 0)")  # noqa: E501
@click.option("--fail-on-secrets/--no-fail-on-secrets", default=True, help="Fail if hardcoded credentials or secrets are found")  # noqa: E501
@click.option("--fail-on-circular/--no-fail-on-circular", default=False, help="Fail if circular dependencies are detected")  # noqa: E501
@click.option("--format", "-f", "fmt", type=click.Choice(["terminal", "json", "sarif", "markdown"]), default="terminal", help="Output format")  # noqa: E501
@click.option("--output", "-o", type=click.Path(), help="Output file path for SARIF, JSON, or Markdown reports")
@click.option("--depth", "-d", type=int, default=100, help="Git history depth for analysis")
def check(
    source: str,
    min_health: str,
    max_smells: int | None,
    max_critical_smells: int,
    fail_on_secrets: bool,
    fail_on_circular: bool,
    fmt: str,
    output: str | None,
    depth: int,
):
    """Evaluate codebase against architectural quality and security gates for CI/CD.

    Returns exit code 0 if all policies pass, or exit code 1 on policy breach.
    Supports SARIF v2.1.0 output for direct GitHub Code Scanning integration,
    and Markdown for PR comments.

    \b
    Examples:
        codedna check .
        codedna check . --min-health Healthy --fail-on-circular
        codedna check . --format sarif --output codedna-results.sarif
        codedna check . --format markdown --output pr-comment.md
    """
    from rich.console import Console

    from .ci.gatekeeper import Gatekeeper
    from .config import load_config
    from .visualization.renderer import Renderer

    console = Console()
    console.print(f"\n[bold cyan]🛡️ CodeDNA Quality Gatekeeper[/] [dim]v{__version__}[/]")
    console.print("[dim]━" * 50 + "[/]\n")

    cloner = None
    try:
        profile, _, cloner = _analyze_repo(source, depth, console)

        # Resolve configuration defaults if available
        repo_dir = Path(source) if Path(source).is_dir() else Path.cwd()
        cfg = load_config(repo_dir)
        gate_cfg = cfg.gate

        resolved_min_health = min_health if min_health != "Fair" else (gate_cfg.min_health or min_health)
        resolved_max_smells = max_smells if max_smells is not None else gate_cfg.max_smells
        resolved_max_crit = max_critical_smells if max_critical_smells != 0 else gate_cfg.max_critical_smells
        resolved_fail_secrets = fail_on_secrets if not fail_on_secrets else gate_cfg.fail_on_secrets
        resolved_fail_circular = fail_on_circular if fail_on_circular else gate_cfg.fail_on_circular

        gatekeeper = Gatekeeper(
            min_health=resolved_min_health,
            max_smells=resolved_max_smells,
            max_critical_smells=resolved_max_crit,
            fail_on_secrets=resolved_fail_secrets,
            fail_on_circular=resolved_fail_circular,
        )
        result = gatekeeper.evaluate(profile)

        # Terminal Rendering
        if fmt == "terminal":
            Renderer(console=console).render_gatekeeper(result)

        # SARIF Export
        if fmt == "sarif" or (output and output.endswith(".sarif")):
            sarif_data = gatekeeper.to_sarif(result, profile)
            sarif_json = json.dumps(sarif_data, indent=2)
            if output:
                out_path = Path(output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(sarif_json, encoding="utf-8")
                console.print(f"  🛡️ SARIF report written: [cyan]{out_path}[/]")
            else:
                click.echo(sarif_json)

        # JSON Export
        elif fmt == "json" or (output and output.endswith(".json")):
            json_str = gatekeeper.to_json(result)
            if output:
                out_path = Path(output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(json_str, encoding="utf-8")
                console.print(f"  📊 Gatekeeper JSON written: [cyan]{out_path}[/]")
            else:
                click.echo(json_str)

        # Markdown Export (for PR comments)
        elif fmt == "markdown" or (output and output.endswith(".md")):
            md_str = gatekeeper.to_markdown(result, profile)
            if output:
                out_path = Path(output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(md_str, encoding="utf-8")
                console.print(f"  📄 Gatekeeper Markdown written: [cyan]{out_path}[/]")
            else:
                click.echo(md_str)

        # Exit code reflects pass/fail gate outcome
        if not result.passed:
            sys.exit(1)
        sys.exit(0)

    except SystemExit:
        raise
    except Exception as e:
        console.print(f"\n[bold red]❌ Error during gate check:[/] {e}")
        sys.exit(1)
    finally:
        if cloner is not None and source.startswith("http"):
            cloner.cleanup()


if __name__ == "__main__":
    main()
