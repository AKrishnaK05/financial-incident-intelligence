"""
Scenario assignment for Financial Incident Intelligence.

This module selects synthetic financial events that should receive
controlled incident behavior.
"""

from datetime import datetime, timedelta

from configs.schema import Refund


INCIDENT_DELIVERY_DELAY = timedelta(hours=3)


def assign_refund_event_latency(
    refunds: list[Refund],
    cutoff_at: datetime,
) -> str | None:
    """
    Select a refund that can produce a REFUND_EVENT_LATENCY incident.

    The refund must be processed before the settlement cutoff,
    while the intentionally delayed webhook must arrive after it.
    """

    for refund in refunds:

        if refund.processed_at >= cutoff_at:
            continue

        expected_delivery = (
            refund.processed_at
            + INCIDENT_DELIVERY_DELAY
        )

        if expected_delivery > cutoff_at:
            return refund.refund_id

    return None