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


def evaluate_missing_refund(
    evidence: IncidentEvidence,
    timeline: TimelineFacts,
) -> Hypothesis:
    """
    Evaluate whether a missing refund could explain the discrepancy.
    """

    supporting_evidence = []
    contradicting_evidence = []

    variance_amount = abs(
        evidence.settlement.expected_net_amount
        - evidence.settlement.observed_net_amount
    )

    if not evidence.refunds:
        supporting_evidence.append(
            "No refund records were found for the payment."
        )
    else:
        contradicting_evidence.append(
            "A refund record exists for the payment."
        )

    refund_amount = sum(
        refund.amount
        for refund in evidence.refunds
        if refund.processed_at <= evidence.settlement.cutoff_at
    )

    if refund_amount == variance_amount and refund_amount > 0:
        contradicting_evidence.append(
            "An existing processed refund already explains "
            "the financial variance."
        )

    if len(contradicting_evidence) == 0:
        status = "PLAUSIBLE"
        confidence = "MEDIUM"
    else:
        status = "UNSUPPORTED"
        confidence = "LOW"

    return Hypothesis(
        name="MISSING_REFUND",
        status=status,
        confidence=confidence,
        supporting_evidence=supporting_evidence,
        contradicting_evidence=contradicting_evidence,
    )


def evaluate_duplicate_adjustment(
    evidence: IncidentEvidence,
    timeline: TimelineFacts,
) -> Hypothesis:
    """
    Evaluate whether a duplicate adjustment could explain
    the financial discrepancy.
    """

    supporting_evidence = []
    contradicting_evidence = []

    if len(evidence.refunds) > 1:
        supporting_evidence.append(
            "Multiple refunds exist for the payment."
        )
    else:
        contradicting_evidence.append(
            "Only one refund exists for the payment."
        )

    if not evidence.refunds:
        contradicting_evidence.append(
            "No refund adjustment exists to duplicate."
        )

    if len(supporting_evidence) == 0:
        status = "UNSUPPORTED"
        confidence = "LOW"
    else:
        status = "PLAUSIBLE"
        confidence = "MEDIUM"

    return Hypothesis(
        name="DUPLICATE_ADJUSTMENT",
        status=status,
        confidence=confidence,
        supporting_evidence=supporting_evidence,
        contradicting_evidence=contradicting_evidence,
    )


def evaluate_settlement_calculation_error(
    evidence: IncidentEvidence,
    timeline: TimelineFacts,
) -> Hypothesis:
    """
    Evaluate whether the settlement representation itself
    appears inconsistent with the underlying financial events.
    """

    supporting_evidence = []
    contradicting_evidence = []

    expected_from_events = evidence.payment.amount - sum(
        refund.amount
        for refund in evidence.refunds
        if refund.processed_at <= evidence.settlement.cutoff_at
    )

    if expected_from_events != evidence.settlement.expected_net_amount:
        supporting_evidence.append(
            "Settlement expected amount does not match "
            "underlying payment and refund events."
        )
    else:
        contradicting_evidence.append(
            "Settlement expected amount matches "
            "underlying payment and refund events."
        )

    if len(supporting_evidence) > 0:
        status = "PLAUSIBLE"
        confidence = "MEDIUM"
    else:
        status = "UNSUPPORTED"
        confidence = "LOW"

    return Hypothesis(
        name="SETTLEMENT_CALCULATION_ERROR",
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

    return [
        evaluate_refund_event_latency(
            evidence,
            timeline,
        ),
        evaluate_missing_refund(
            evidence,
            timeline,
        ),
        evaluate_duplicate_adjustment(
            evidence,
            timeline,
        ),
        evaluate_settlement_calculation_error(
            evidence,
            timeline,
        ),
    ]