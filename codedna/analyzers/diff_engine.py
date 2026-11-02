"""DNA Diff Engine — compares two CodeDNA profiles and computes genetic drift."""

from __future__ import annotations

import json
import math
from datetime import datetime


class DiffEngine:
    """Computes genetic drift, architectural deltas, and similarity between two codebases."""

    HEALTH_RANKS = {
        "Healthy": 4,
        "Fair": 3,
        "Needs Attention": 2,
        "Critical": 1,
        "Unknown": 0,
    }

    def compare(self, profile_a: dict, profile_b: dict) -> dict:
        """Compare two DNA profiles and compute comprehensive structural and architectural diff.

        Args:
            profile_a: Baseline DNA profile dict.
            profile_b: Comparison / target DNA profile dict.

        Returns:
            Dictionary with similarity score, metric deltas, and mutation verdict.
        """
        source_a = profile_a.get("metadata", {}).get("source", "Profile A")
        source_b = profile_b.get("metadata", {}).get("source", "Profile B")

        # 1. Calculate similarity score (0.0 to 100.0)
        similarity_score = self.compute_similarity(profile_a, profile_b)

        # 2. Structural Deltas
        struct_a = profile_a.get("structure_stats", {})
        struct_b = profile_b.get("structure_stats", {})
        structure_delta = {
            "files": struct_b.get("total_files", 0) - struct_a.get("total_files", 0),
            "dirs": struct_b.get("total_dirs", 0) - struct_a.get("total_dirs", 0),
            "modules": struct_b.get("modules", 0) - struct_a.get("modules", 0),
            "max_depth": struct_b.get("max_depth", 0) - struct_a.get("max_depth", 0),
        }

        # 3. Language Deltas
        langs_a = profile_a.get("languages", {}).get("languages", {})
        langs_b = profile_b.get("languages", {}).get("languages", {})
        all_langs = sorted(set(langs_a.keys()) | set(langs_b.keys()))

        language_deltas = {}
        for lang in all_langs:
            pct_a = langs_a.get(lang, {}).get("percentage", 0.0)
            pct_b = langs_b.get(lang, {}).get("percentage", 0.0)
            language_deltas[lang] = {
                "pct_a": pct_a,
                "pct_b": pct_b,
                "delta": round(pct_b - pct_a, 2),
            }

        languages_added = [lang for lang in all_langs if lang in langs_b and lang not in langs_a]
        languages_removed = [lang for lang in all_langs if lang in langs_a and lang not in langs_b]

        # 4. Architecture Shift
        arch_a = profile_a.get("architecture", {})
        arch_b = profile_b.get("architecture", {})
        pattern_a = profile_a.get("system_type", arch_a.get("primary_pattern", "Unknown"))
        pattern_b = profile_b.get("system_type", arch_b.get("primary_pattern", "Unknown"))
        traits_a = set(arch_a.get("traits", []))
        traits_b = set(arch_b.get("traits", []))

        architecture_shift = {
            "from_pattern": pattern_a,
            "to_pattern": pattern_b,
            "pattern_changed": pattern_a != pattern_b,
            "traits_added": sorted(traits_b - traits_a),
            "traits_removed": sorted(traits_a - traits_b),
            "coupling_a": arch_a.get("coupling", "Unknown"),
            "coupling_b": arch_b.get("coupling", "Unknown"),
        }

        # 5. Dependency Graph Shift
        deps_a = profile_a.get("dependencies", {})
        deps_b = profile_b.get("dependencies", {})
        has_circ_a = deps_a.get("has_circular_deps", False)
        has_circ_b = deps_b.get("has_circular_deps", False)

        if not has_circ_a and has_circ_b:
            circ_status = "introduced"
        elif has_circ_a and not has_circ_b:
            circ_status = "resolved"
        elif has_circ_a and has_circ_b:
            circ_status = "persisting"
        else:
            circ_status = "clean"

        dependency_shift = {
            "modules_delta": deps_b.get("total_modules", 0) - deps_a.get("total_modules", 0),
            "edges_delta": deps_b.get("total_edges", 0) - deps_a.get("total_edges", 0),
            "density_delta": round(deps_b.get("density", 0.0) - deps_a.get("density", 0.0), 4),
            "circular_deps": {
                "from": has_circ_a,
                "to": has_circ_b,
                "status": circ_status,
                "cycles_delta": deps_b.get("circular_count", 0) - deps_a.get("circular_count", 0),
            },
        }

        # 6. Health & Quality Shift
        health_a = profile_a.get("health", {})
        health_b = profile_b.get("health", {})
        overall_a = health_a.get("overall", "Unknown")
        overall_b = health_b.get("overall", "Unknown")
        rank_a = self.HEALTH_RANKS.get(overall_a, 0)
        rank_b = self.HEALTH_RANKS.get(overall_b, 0)

        if rank_b > rank_a:
            health_status = "improved"
        elif rank_b < rank_a:
            health_status = "degraded"
        else:
            health_status = "unchanged"

        counts_a = health_a.get("severity_counts", {})
        counts_b = health_b.get("severity_counts", {})
        sec_a = profile_a.get("security", {})
        sec_b = profile_b.get("security", {})

        health_shift = {
            "from_health": overall_a,
            "to_health": overall_b,
            "status": health_status,
            "critical_smells_delta": counts_b.get("critical", 0) - counts_a.get("critical", 0),
            "warning_smells_delta": counts_b.get("warning", 0) - counts_a.get("warning", 0),
            "critical_vulns_delta": sec_b.get("total_critical", 0) - sec_a.get("total_critical", 0),
            "secrets_introduced": (not sec_a.get("has_secrets", False)) and sec_b.get("has_secrets", False),
            "secrets_resolved": sec_a.get("has_secrets", False) and (not sec_b.get("has_secrets", False)),
        }

        # 7. Developer Genome Shift
        dev_a = profile_a.get("developer_genome", {})
        dev_b = profile_b.get("developer_genome", {})
        developer_shift = {
            "contributors_delta": dev_b.get("total_contributors", 0) - dev_a.get("total_contributors", 0),
            "bus_factor_delta": dev_b.get("bus_factor", 0) - dev_a.get("bus_factor", 0),
        }

        # 8. Mutation Verdict
        verdict = self._determine_verdict(similarity_score, health_shift, architecture_shift, dependency_shift)

        return {
            "metadata": {
                "source_a": source_a,
                "source_b": source_b,
                "compared_at": datetime.now().isoformat(),
            },
            "similarity_score": similarity_score,
            "mutation_verdict": verdict,
            "structure_delta": structure_delta,
            "language_deltas": language_deltas,
            "languages_added": languages_added,
            "languages_removed": languages_removed,
            "architecture_shift": architecture_shift,
            "dependency_shift": dependency_shift,
            "health_shift": health_shift,
            "developer_shift": developer_shift,
        }

    def compute_similarity(self, profile_a: dict, profile_b: dict) -> float:
        """Compute genetic similarity score between 0.0% and 100.0%."""
        # 1. Language overlap (cosine similarity of percentage vectors) - weight: 25%
        langs_a = profile_a.get("languages", {}).get("languages", {})
        langs_b = profile_b.get("languages", {}).get("languages", {})
        all_langs = set(langs_a.keys()) | set(langs_b.keys())

        if not all_langs:
            lang_sim = 1.0
        else:
            vec_a = [langs_a.get(lang, {}).get("percentage", 0.0) for lang in all_langs]
            vec_b = [langs_b.get(lang, {}).get("percentage", 0.0) for lang in all_langs]
            dot = sum(a * b for a, b in zip(vec_a, vec_b))
            norm_a = math.sqrt(sum(a * a for a in vec_a))
            norm_b = math.sqrt(sum(b * b for b in vec_b))
            lang_sim = (dot / (norm_a * norm_b)) if (norm_a > 0 and norm_b > 0) else 0.0

        # 2. Structure size similarity - weight: 20%
        files_a = profile_a.get("structure_stats", {}).get("total_files", 0)
        files_b = profile_b.get("structure_stats", {}).get("total_files", 0)
        if files_a == 0 and files_b == 0:
            struct_sim = 1.0
        elif files_a == 0 or files_b == 0:
            struct_sim = 0.0
        else:
            struct_sim = min(files_a, files_b) / max(files_a, files_b)

        # 3. Architecture & Traits similarity - weight: 25%
        arch_a = profile_a.get("architecture", {})
        arch_b = profile_b.get("architecture", {})
        pattern_a = profile_a.get("system_type", arch_a.get("primary_pattern", ""))
        pattern_b = profile_b.get("system_type", arch_b.get("primary_pattern", ""))
        pattern_match = 1.0 if pattern_a == pattern_b else 0.0

        traits_a = set(arch_a.get("traits", []))
        traits_b = set(arch_b.get("traits", []))
        if not traits_a and not traits_b:
            traits_sim = 1.0
        else:
            union = traits_a | traits_b
            traits_sim = (len(traits_a & traits_b) / len(union)) if union else 1.0

        arch_sim = (0.6 * pattern_match) + (0.4 * traits_sim)

        # 4. Dependency topology similarity - weight: 15%
        deps_a = profile_a.get("dependencies", {})
        deps_b = profile_b.get("dependencies", {})
        circ_match = 1.0 if deps_a.get("has_circular_deps") == deps_b.get("has_circular_deps") else 0.0
        edges_a = deps_a.get("total_edges", 0)
        edges_b = deps_b.get("total_edges", 0)
        if edges_a == 0 and edges_b == 0:
            edge_sim = 1.0
        elif edges_a == 0 or edges_b == 0:
            edge_sim = 0.2
        else:
            edge_sim = min(edges_a, edges_b) / max(edges_a, edges_b)
        dep_sim = (0.5 * circ_match) + (0.5 * edge_sim)

        # 5. Health & Quality Alignment - weight: 15%
        health_a = profile_a.get("health", {}).get("overall", "Unknown")
        health_b = profile_b.get("health", {}).get("overall", "Unknown")
        rank_a = self.HEALTH_RANKS.get(health_a, 2)
        rank_b = self.HEALTH_RANKS.get(health_b, 2)
        health_diff = abs(rank_a - rank_b)
        health_sim = max(0.0, 1.0 - (health_diff / 3.0))

        # Composite score
        composite = (
            0.25 * lang_sim
            + 0.20 * struct_sim
            + 0.25 * arch_sim
            + 0.15 * dep_sim
            + 0.15 * health_sim
        )
        return round(composite * 100.0, 1)

    def _determine_verdict(
        self,
        similarity: float,
        health_shift: dict,
        arch_shift: dict,
        dep_shift: dict,
    ) -> str:
        """Formulate a pragmatic developer verdict for the mutation."""
        if similarity >= 99.5 and not health_shift["secrets_introduced"]:
            return "Identical Genome"

        if health_shift["secrets_introduced"]:
            return "Critical Regression (Secrets Exposed)"

        if health_shift["status"] == "degraded" or dep_shift["circular_deps"]["status"] == "introduced":
            return "Architectural & Health Degradation"

        if health_shift["status"] == "improved" or dep_shift["circular_deps"]["status"] == "resolved":
            return "Quality & Hygiene Improvement"

        if arch_shift["pattern_changed"]:
            return "Paradigm Shift / Architectural Migration"

        if similarity >= 85.0:
            return "Stable Evolution / Conservative Refactor"

        if similarity >= 60.0:
            return "Moderate Architectural Mutation"

        return "Radical Divergence / Genetic Drift"

    def to_markdown(self, diff: dict) -> str:
        """Format diff result as Markdown report."""
        meta = diff["metadata"]
        lines = [
            "# 🧬 CodeDNA Genetic Drift & Mutation Diff\n",
            f"> **Baseline (A):** `{meta['source_a']}`",
            f"> **Target (B):** `{meta['source_b']}`",
            f"> **Compared At:** {meta['compared_at'][:19]}",
            f"> **Genetic Similarity:** **{diff['similarity_score']}%**",
            f"> **Verdict:** `{diff['mutation_verdict']}`\n",
            "---\n",
            "## 📊 Structural & Architectural Comparison\n",
            "| Metric | Baseline (A) | Target (B) | Delta / Shift |",
            "| :--- | :--- | :--- | :--- |",
        ]

        # Files & Structure
        s_delta = diff["structure_delta"]
        lines.append(f"| **Files** | - | - | `{s_delta['files']:+d}` files |")
        lines.append(f"| **Modules** | - | - | `{s_delta['modules']:+d}` modules |")

        # Architecture Pattern
        arch = diff["architecture_shift"]
        arch_delta = "Unchanged" if not arch["pattern_changed"] else f"`{arch['from_pattern']}` ➔ `{arch['to_pattern']}`"
        lines.append(f"| **Architecture** | `{arch['from_pattern']}` | `{arch['to_pattern']}` | {arch_delta} |")

        # Health
        h = diff["health_shift"]
        h_delta = f"{h['status'].capitalize()} (`{h['critical_smells_delta']:+d}` crit, `{h['warning_smells_delta']:+d}` warn)"
        lines.append(f"| **Health Rating** | `{h['from_health']}` | `{h['to_health']}` | {h_delta} |")

        # Circular Deps
        dep = diff["dependency_shift"]
        c_status = dep["circular_deps"]["status"]
        lines.append(f"| **Circular Deps** | `{'Yes' if dep['circular_deps']['from'] else 'No'}` | `{'Yes' if dep['circular_deps']['to'] else 'No'}` | `{c_status}` |")
        lines.append(f"| **Dep Edges** | - | - | `{dep['edges_delta']:+d}` connections |")

        # Developer Bus Factor
        dev = diff["developer_shift"]
        lines.append(f"| **Bus Factor** | - | - | `{dev['bus_factor_delta']:+d}` |")

        lines.append("\n## 🌐 Language Composition Shifts\n")
        lines.append("| Language | Baseline (A) % | Target (B) % | Shift |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for lang, d in diff["language_deltas"].items():
            if d["pct_a"] > 0 or d["pct_b"] > 0:
                lines.append(f"| {lang} | {d['pct_a']}% | {d['pct_b']}% | `{d['delta']:+0.1f}%` |")

        if diff["languages_added"]:
            lines.append(f"\n- **Languages Added:** {', '.join(diff['languages_added'])}")
        if diff["languages_removed"]:
            lines.append(f"- **Languages Removed:** {', '.join(diff['languages_removed'])}")

        lines.append("\n---\n*Generated by [CodeDNA Diff Engine](https://github.com/shenald-dev/codedna)*")
        return "\n".join(lines)

    @staticmethod
    def evaluate_drift_gate(
        diff: dict,
        max_drift: float = 20.0,
        min_similarity: float | None = None,
        fail_on_circular: bool = True,
        fail_on_health_drop: bool = True,
        fail_on_secrets: bool = True,
        allow_degradation: bool | None = None,
        allow_circular_deps: bool | None = None,
        allow_new_secrets: bool | None = None,
    ) -> tuple[bool, list[str]]:
        """Evaluate diff result against architectural drift regression policies.

        Supports both policy-check naming conventions (fail_on_* and allow_*).

        Returns:
            Tuple of (passed: bool, failure_reasons: list[str])
        """
        if allow_degradation is not None:
            fail_on_health_drop = not allow_degradation
        if allow_circular_deps is not None:
            fail_on_circular = not allow_circular_deps
        if allow_new_secrets is not None:
            fail_on_secrets = not allow_new_secrets

        reasons = []
        similarity = diff.get("similarity_score", 100.0)

        if min_similarity is not None and min_similarity > 0.0:
            min_allowed_similarity = min_similarity
        else:
            min_allowed_similarity = max(0.0, 100.0 - max_drift)

        if similarity < min_allowed_similarity:
            reasons.append(
                f"Genetic similarity {similarity}% is below minimum required {min_allowed_similarity}%"
            )

        dep_shift = diff.get("dependency_shift", {})
        circ_status = dep_shift.get("circular_deps", {}).get("status", "")
        if fail_on_circular and circ_status == "introduced":
            reasons.append("Circular dependencies were introduced in target codebase")

        health_shift = diff.get("health_shift", {})
        if fail_on_health_drop and health_shift.get("status") == "degraded":
            reasons.append(
                f"Overall health degraded from '{health_shift.get('from_health')}' to '{health_shift.get('to_health')}'"
            )

        if fail_on_secrets and health_shift.get("secrets_introduced"):
            reasons.append("Hardcoded credentials or API keys were introduced in target codebase")

        crit_delta = health_shift.get("critical_smells_delta", 0)
        if crit_delta > 0:
            reasons.append(f"Critical code smells increased by +{crit_delta}")

        passed = len(reasons) == 0
        return passed, reasons

    def to_json(self, diff: dict) -> str:
        """Format diff result as formatted JSON string."""
        return json.dumps(diff, indent=2, default=str)
