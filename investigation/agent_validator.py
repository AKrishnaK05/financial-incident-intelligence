"""
Validation layer for Financial Incident Intelligence.

This module validates investigation-agent output against the
deterministic investigation context and governance policy.

It does not perform financial calculations or execute actions.
"""

from investigation.investigation_models import InvestigationNarrative
from investigation.agent_context import AgentContext


VALID_CONFIDENCE_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
}

def validate_reasoning_trace(
    narrative: InvestigationNarrative,
    context: AgentContext,
) -> None:
    """
    Validate that the reasoning trace attached to the
    agent response matches the deterministic reasoning
    established by the investigation pipeline.
    """

    expected = context.reasoning
    actual = narrative.reasoning

    if actual.primary_hypothesis != expected.primary_hypothesis:
        raise ValueError(
            "Agent reasoning primary hypothesis does not "
            "match deterministic reasoning."
        )

    if actual.primary_confidence != expected.primary_confidence:
        raise ValueError(
            "Agent reasoning confidence does not match "
            "deterministic reasoning."
        )

    if actual.primary_score != expected.primary_score:
        raise ValueError(
            "Agent reasoning primary score does not match "
            "deterministic reasoning."
        )

    if actual.second_best_score != expected.second_best_score:
        raise ValueError(
            "Agent reasoning second-best score does not "
            "match deterministic reasoning."
        )

    if actual.evidence_margin != expected.evidence_margin:
        raise ValueError(
            "Agent reasoning evidence margin does not match "
            "deterministic reasoning."
        )

    if actual.assessments != expected.assessments:
        raise ValueError(
            "Agent reasoning hypothesis assessments do not "
            "match deterministic reasoning."
        )

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

    validate_reasoning_trace(
        narrative,
        context,
    )

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