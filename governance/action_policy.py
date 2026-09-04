"""
Governed action policy for Financial Incident Intelligence.

This module converts investigation results into bounded operational
recommendations.

It does not execute financial actions or modify financial records.
"""

from dataclasses import dataclass

from investigation.incident_report import IncidentReport


@dataclass
class ActionRecommendation:
    """
    Represents a proposed operational response to an incident.
    """

    action: str
    priority: str
    requires_approval: bool
    reason: str

def recommend_action(
    report: IncidentReport,
) -> ActionRecommendation:
    """
    Recommend a bounded operational response based on
    deterministic investigation findings.

    No financial action is executed automatically.
    """

    primary_hypothesis = report.primary_hypothesis

    if primary_hypothesis is None:
        return ActionRecommendation(
            action="MANUAL_REVIEW",
            priority="HIGH",
            requires_approval=True,
            reason=(
                "No supported root-cause hypothesis was established."
            ),
        )

    if (
        report.cluster_scope == "SYSTEMIC"
        and primary_hypothesis.confidence == "HIGH"
    ):
        return ActionRecommendation(
            action="ESCALATE_INCIDENT",
            priority="CRITICAL",
            requires_approval=True,
            reason=(
                "A high-confidence failure mechanism affects "
                "multiple merchants and transactions."
            ),
        )

    if primary_hypothesis.confidence == "HIGH":
        return ActionRecommendation(
            action="REVIEW_AND_REPROCESS",
            priority="HIGH",
            requires_approval=True,
            reason=(
                "A high-confidence financial discrepancy has "
                "an evidence-backed root-cause hypothesis."
            ),
        )

    return ActionRecommendation(
        action="MANUAL_REVIEW",
        priority="MEDIUM",
        requires_approval=True,
        reason=(
            "The available evidence does not justify an "
            "automated remediation recommendation."
        ),
    )