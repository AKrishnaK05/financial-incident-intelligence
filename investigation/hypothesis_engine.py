"""
Hypothesis engine for Financial Incident Intelligence.

This module evaluates possible root-cause explanations using
observable evidence and deterministic rules.

It does not access ground truth.
"""

from dataclasses import dataclass

from investigation.evidence import IncidentEvidence
from investigation.timeline import TimelineFacts


@dataclass
class Hypothesis:
    """
    Represents a possible explanation for a financial incident.
    """

    name: str
    status: str
    confidence: str
    supporting_evidence: list[str]
    contradicting_evidence: list[str]


def evaluate_refund_event_latency(
    evidence: IncidentEvidence,
    timeline: TimelineFacts,
) -> Hypothesis:
    """
    Evaluate whether delayed refund event delivery explains
    the financial discrepancy.
    """

    supporting_evidence = []
    contradicting_evidence = []

    variance_amount = abs(
        evidence.settlement.expected_net_amount
        - evidence.settlement.observed_net_amount
    )

    total_refund_amount = sum(
        refund.amount
        for refund in evidence.refunds
        if refund.processed_at <= evidence.settlement.cutoff_at
    )

    if timeline.refund_processed_before_cutoff:
        supporting_evidence.append(
            "Refund was processed before settlement cutoff."
        )
    else:
        contradicting_evidence.append(
            "No refund was processed before settlement cutoff."
        )

    if not timeline.webhook_delivered_before_cutoff:
        supporting_evidence.append(
            "Refund webhook was delivered after settlement cutoff."
        )
    else:
        contradicting_evidence.append(
            "Refund webhook was delivered before settlement cutoff."
        )

    if timeline.webhook_delivery_delay is not None:
        supporting_evidence.append(
            "Webhook delivery delay was "
            f"{timeline.webhook_delivery_delay}."
        )

    if total_refund_amount == variance_amount:
        supporting_evidence.append(
            "Refund amount matches the financial variance."
        )
    else:
        contradicting_evidence.append(
            "Refund amount does not match the financial variance."
        )

    if len(contradicting_evidence) == 0 and len(
        supporting_evidence
    ) >= 3:
        status = "SUPPORTED"
        confidence = "HIGH"

    elif len(supporting_evidence) >= 2:
        status = "PLAUSIBLE"
        confidence = "MEDIUM"

    else:
        status = "UNSUPPORTED"
        confidence = "LOW"

    return Hypothesis(
        name="REFUND_EVENT_LATENCY",
        status=status,
        confidence=confidence,
        supporting_evidence=supporting_evidence,
        contradicting_evidence=contradicting_evidence,
    )


def evaluate_hypotheses(
    evidence: IncidentEvidence,
    timeline: TimelineFacts,
) -> list[Hypothesis]:
    """
    Evaluate all currently supported root-cause hypotheses.
    """

    hypotheses = [
        evaluate_refund_event_latency(
            evidence,
            timeline,
        )
    ]

    return hypotheses