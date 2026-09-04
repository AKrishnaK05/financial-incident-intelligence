"""
Validation layer for Financial Incident Intelligence.

This module validates investigation-agent output against the
deterministic investigation context and governance policy.

It does not perform financial calculations or execute actions.
"""

from investigation.agent import InvestigationNarrative
from investigation.agent_context import AgentContext


VALID_CONFIDENCE_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
}


def validate_investigation_narrative(
    narrative: InvestigationNarrative,
    context: AgentContext,
) -> None:
    """
    Validate an AI-generated investigation narrative.

    Raises
    ------
    ValueError
        If the narrative violates the investigation or
        governance constraints.
    """

    if narrative.incident_id != context.report.incident_id:
        raise ValueError(
            "Agent narrative references a different incident."
        )

    if narrative.confidence not in VALID_CONFIDENCE_LEVELS:
        raise ValueError(
            f"Invalid confidence level: "
            f"{narrative.confidence}"
        )

    if narrative.recommended_action != (
        context.recommendation.action
    ):
        raise ValueError(
            "Agent recommended action does not match "
            "the governed recommendation."
        )

    primary_hypothesis = (
        context.report.primary_hypothesis
    )

    if primary_hypothesis is None:
        if narrative.root_cause is not None:
            raise ValueError(
                "Agent supplied a root cause even though "
                "no supported hypothesis exists."
            )

    else:
        if narrative.root_cause != (
            primary_hypothesis.name
        ):
            raise ValueError(
                "Agent root cause does not match the "
                "strongest supported hypothesis."
            )

        if narrative.confidence != (
            primary_hypothesis.confidence
        ):
            raise ValueError(
                "Agent confidence does not match the "
                "evidence-backed confidence level."
            )