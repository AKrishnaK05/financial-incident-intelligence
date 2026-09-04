"""
Timeline analysis for Financial Incident Intelligence.

This module derives deterministic temporal facts from incident evidence.
It does not determine the root cause.
"""

from dataclasses import dataclass
from datetime import timedelta

from investigation.evidence import IncidentEvidence


@dataclass
class TimelineFacts:
    """
    Deterministic temporal facts associated with an incident.
    """

    incident_id: str
    refund_processed_before_cutoff: bool
    webhook_delivered_before_cutoff: bool
    webhook_delivery_delay: timedelta | None
    refund_to_webhook_delay: timedelta | None


def analyze_timeline(
    evidence: IncidentEvidence,
) -> TimelineFacts:
    """
    Derive temporal relationships from incident evidence.
    """

    cutoff_at = evidence.settlement.cutoff_at

    refund_processed_before_cutoff = any(
        refund.processed_at <= cutoff_at
        for refund in evidence.refunds
    )

    webhook_delivered_before_cutoff = any(
        event.delivered_at <= cutoff_at
        for event in evidence.webhook_events
    )

    webhook_delivery_delay = None
    refund_to_webhook_delay = None

    if evidence.refunds and evidence.webhook_events:
        earliest_refund = min(
            evidence.refunds,
            key=lambda refund: refund.processed_at,
        )

        earliest_webhook = min(
            evidence.webhook_events,
            key=lambda event: event.delivered_at,
        )

        webhook_delivery_delay = (
            earliest_webhook.delivered_at
            - earliest_webhook.emitted_at
        )

        refund_to_webhook_delay = (
            earliest_webhook.delivered_at
            - earliest_refund.processed_at
        )

    return TimelineFacts(
        incident_id=evidence.incident_id,
        refund_processed_before_cutoff=(
            refund_processed_before_cutoff
        ),
        webhook_delivered_before_cutoff=(
            webhook_delivered_before_cutoff
        ),
        webhook_delivery_delay=webhook_delivery_delay,
        refund_to_webhook_delay=refund_to_webhook_delay,
    )