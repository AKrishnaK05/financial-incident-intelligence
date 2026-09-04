"""
Curated investigation context for Financial Incident Intelligence.

This module defines the information that may be provided to
the AI investigation agent.

The agent receives established facts rather than unrestricted
access to the financial state graph.
"""

from dataclasses import dataclass

from governance.action_policy import ActionRecommendation
from investigation.evidence import IncidentEvidence
from investigation.hypothesis_engine import Hypothesis
from investigation.incident_report import IncidentReport
from investigation.timeline import TimelineFacts


@dataclass
class EvidenceBoundary:
    """
    Defines what the investigation has established and
    what remains unknown.
    """

    established_facts: list[str]
    unresolved_questions: list[str]


@dataclass
class AgentContext:
    """
    Complete curated context supplied to the AI investigator.
    """

    report: IncidentReport
    evidence: IncidentEvidence
    timeline: TimelineFacts
    hypotheses: list[Hypothesis]
    recommendation: ActionRecommendation
    evidence_boundary: EvidenceBoundary


def build_evidence_boundary(
    evidence: IncidentEvidence,
    timeline: TimelineFacts,
    report: IncidentReport,
) -> EvidenceBoundary:
    """
    Build an explicit boundary between established facts
    and unresolved questions.
    """

    established_facts = []
    unresolved_questions = []

    if timeline.refund_processed_before_cutoff:
        established_facts.append(
            "The refund was processed before the settlement cutoff."
        )

    if not timeline.webhook_delivered_before_cutoff:
        established_facts.append(
            "The refund webhook was delivered after the "
            "settlement cutoff."
        )

    if timeline.webhook_delivery_delay is not None:
        established_facts.append(
            "The observed webhook delivery delay was "
            f"{timeline.webhook_delivery_delay}."
        )

    if evidence.refunds:
        established_facts.append(
            "A refund record exists for the affected payment."
        )

    if report.variance_amount != 0:
        established_facts.append(
            "The settlement representation contains a "
            f"financial variance of ₹"
            f"{abs(report.variance_amount)}."
        )

    unresolved_questions.append(
        "The underlying reason for the webhook delivery "
        "delay has not been established."
    )

    unresolved_questions.append(
        "The available evidence does not establish whether "
        "the delay was caused by infrastructure failure, "
        "queue backlog, retry behavior, or another mechanism."
    )

    return EvidenceBoundary(
        established_facts=established_facts,
        unresolved_questions=unresolved_questions,
    )


def build_agent_context(
    report: IncidentReport,
    evidence: IncidentEvidence,
    timeline: TimelineFacts,
    hypotheses: list[Hypothesis],
    recommendation: ActionRecommendation,
) -> AgentContext:
    """
    Build the curated context supplied to the AI investigator.
    """

    if report.incident_id != evidence.incident_id:
        raise ValueError(
            "Incident report and evidence refer to different incidents."
        )

    if report.incident_id != timeline.incident_id:
        raise ValueError(
            "Incident report and timeline refer to different incidents."
        )

    evidence_boundary = build_evidence_boundary(
        evidence,
        timeline,
        report,
    )

    return AgentContext(
        report=report,
        evidence=evidence,
        timeline=timeline,
        hypotheses=hypotheses,
        recommendation=recommendation,
        evidence_boundary=evidence_boundary,
    )