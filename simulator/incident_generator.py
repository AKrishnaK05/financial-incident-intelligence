"""
Controlled incident generator for Financial Incident Intelligence.

This module creates deterministic financial events used to test
known incident scenarios.
"""

from datetime import datetime, timedelta, timezone

from configs.schema import Payment, Refund


def generate_refund_event_latency_incident():
    """
    Generate the controlled REFUND_EVENT_LATENCY hero scenario.

    Returns
    -------
    tuple[Payment, Refund]
        Payment and refund forming the incident.
    """

    payment = Payment(
        payment_id="PAY_INC_000001",
        merchant_id="MER_INC_0001",
        order_id="ORD_INC_000001",
        amount=10000,
        method="UPI",
        currency="INR",
        captured_at=datetime(
            2026,
            8,
            20,
            9,
            30,
            tzinfo=timezone.utc,
        ),
        status="CAPTURED",
    )

    refund = Refund(
        refund_id="RFND_INC_000001",
        payment_id=payment.payment_id,
        merchant_id=payment.merchant_id,
        amount=3000,
        currency="INR",
        requested_at=datetime(
            2026,
            8,
            20,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        processed_at=datetime(
            2026,
            8,
            20,
            10,
            15,
            tzinfo=timezone.utc,
        ),
        status="PROCESSED",
    )

    return payment, refund