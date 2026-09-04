"""
AI investigation agent contract for Financial Incident Intelligence.

This module defines the structured output expected from an
AI investigator.

The agent does not modify financial state or execute actions.
"""

from dataclasses import dataclass

from investigation.incident_report import IncidentReport
from governance.action_policy import ActionRecommendation


@dataclass
class InvestigationNarrative:
    """
    Structured explanation produced by the investigation agent.
    """

    incident_id: str
    summary: str
    root_cause: str | None
    confidence: str
    evidence_summary: list[str]
    uncertainty: list[str]
    recommended_action: str

def generate_investigation_narrative(
    report: IncidentReport,
    recommendation: ActionRecommendation,
) -> InvestigationNarrative:
    """
    Generate an investigation narrative from established
    deterministic findings.

    This baseline implementation does not use an LLM.
    """

    primary_hypothesis = report.primary_hypothesis

    if primary_hypothesis is None:
        root_cause = None
        confidence = "LOW"

        summary = (
            "A financial discrepancy was detected, but "
            "the available evidence does not support a "
            "specific root-cause hypothesis."
        )

        evidence_summary = []

        uncertainty = [
            "No root-cause hypothesis reached supported status."
        ]

        recommended_action = "MANUAL_REVIEW"

    else:
        root_cause = primary_hypothesis.name
        confidence = primary_hypothesis.confidence

        summary = (
            f"Financial variance of ₹"
            f"{abs(report.variance_amount)} was detected "
            f"for payment {report.payment_id}. "
            f"The strongest evidence-backed hypothesis is "
            f"{root_cause}."
        )

        evidence_summary = (
            primary_hypothesis.supporting_evidence
        )

        uncertainty = (
            primary_hypothesis.contradicting_evidence
        )

        recommended_action = (
            recommendation.action
        )

    return InvestigationNarrative(
        incident_id=report.incident_id,
        summary=summary,
        root_cause=root_cause,
        confidence=confidence,
        evidence_summary=evidence_summary,
        uncertainty=uncertainty,
        recommended_action=recommendation.action,
    )