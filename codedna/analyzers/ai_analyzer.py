"""AI Analyzer — synthesizes a natural language Executive Summary from the raw DNA profile."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AIResult:
    executive_summary: str
    refactoring_recommendations: list[str]
    success: bool
    error_message: Optional[str] = None


class AIAnalyzer:
    """Uses an LLM to generate insights from the CodeDNA profile."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def synthesize(self, raw_dna_profile: dict) -> AIResult:
        """Sends the raw DNA profile to the LLM and parses the response.

        Args:
            raw_dna_profile: The JSON-serializable dictionary of all generated metrics.

        Returns:
            An AIResult containing the summary and recommendations.
        """
        if not self.api_key:
            return AIResult(
                executive_summary="AI Analysis skipped. Set the `OPENAI_API_KEY` environment variable to enable intelligent synthesis.",  # noqa: E501
                refactoring_recommendations=[],
                success=False,
                error_message="Missing OPENAI_API_KEY"
            )

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
        except ImportError:
            return AIResult(
                executive_summary="AI Analysis skipped. The `openai` python package is not installed.",  # noqa: E501
                refactoring_recommendations=[],
                success=False,
                error_message="Missing openai package"
            )

        # Truncate profile elements if they are too large to fit in context
        safe_profile = self._minimize_payload(raw_dna_profile)

        system_prompt = (
            "You are CodeDNA, an expert software architect and senior code reviewer. "
            "You are provided with a 'DNA Profile' of a codebase containing metrics about languages, "  # noqa: E501
            "architecture, dependencies, developers, and code smells. "
            "Your task is to synthesize this raw data into a brilliant, concise 'Executive Summary' (2-3 paragraphs) "  # noqa: E501
            "and extract EXACTLY 3 major 'Refactoring Recommendations' based on the worst code smells or architectural flaws detected.\n\n"  # noqa: E501
            "Format the output strictly as a JSON object with two keys:\n"
            '{"executive_summary": "...", "refactoring_recommendations": ["...", "...", "..."]}'
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(safe_profile, default=str)}
                ],
                response_format={"type": "json_object"},
                timeout=30.0
            )

            raw_response = response.choices[0].message.content
            parsed = json.loads(raw_response)

            return AIResult(
                executive_summary=parsed.get("executive_summary", "Synthesis failed structurally."),
                refactoring_recommendations=parsed.get("refactoring_recommendations", []),
                success=True
            )

        except Exception as e:
            return AIResult(
                executive_summary="AI Analysis failed due to an API error.",
                refactoring_recommendations=[],
                success=False,
                error_message=str(e)
            )

    def _minimize_payload(self, profile: dict) -> dict:
        """Removes large arrays or deeply nested structures before sending to LLM."""
        clone = dict(profile)
        # Drop raw file lists if they exist
        if "structure_stats" in clone and "modules" in clone["structure_stats"]:
            clone["structure_stats"]["modules"] = len(clone["structure_stats"]["modules"])

        # Keep only top 5 risks to avoid blowing up context token limits
        if "risks" in clone:
            clone["risks"] = clone["risks"][:5]

        # Strip out massive raw graphs
        if "mermaid_graph" in clone:
            del clone["mermaid_graph"]

        return clone
