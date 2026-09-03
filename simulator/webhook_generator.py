"""
Synthetic webhook event generator for Financial Incident Intelligence.

This module generates asynchronous webhook delivery events for
financial business events such as refunds.
"""

import random
from datetime import timedelta

from configs.schema import Refund, WebhookEvent


WEBHOOK_DELIVERY_MINUTES = 5
WEBHOOK_DELIVERY_MAX_MINUTES = 120

INCIDENT_DELIVERY_DELAY_MINUTES = 180


def generate_refund_webhook(
    event_number: int,
    refund: Refund,
    scenario: str | None = None,
) -> WebhookEvent:
    """
    Generate a webhook event for a processed refund.

    Parameters
    ----------
    event_number:
        Numeric identifier used to create the event ID.

    refund:
        The processed refund associated with the webhook.

    scenario:
        Optional incident scenario that modifies webhook behavior.

    Returns
    -------
    WebhookEvent
        A synthetic refund webhook event.
    """

    event_id = f"EVT_{event_number:06d}"

    business_event_at = refund.processed_at

    emitted_at = business_event_at + timedelta(
        seconds=random.randint(1, 30)
    )

    if scenario == "REFUND_EVENT_LATENCY":
        delivery_delay = timedelta(
            minutes=INCIDENT_DELIVERY_DELAY_MINUTES
        )
    else:
        delivery_delay = timedelta(
            minutes=random.randint(
                WEBHOOK_DELIVERY_MINUTES,
                WEBHOOK_DELIVERY_MAX_MINUTES,
            )
        )

    delivered_at = emitted_at + delivery_delay

    return WebhookEvent(
        event_id=event_id,
        entity_id=refund.refund_id,
        event_type="refund.processed",
        business_event_at=business_event_at,
        emitted_at=emitted_at,
        delivered_at=delivered_at,
        delivery_status="DELIVERED",
    )