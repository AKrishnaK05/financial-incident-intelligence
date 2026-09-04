"""
Controlled incident generator for Financial Incident Intelligence.

This module creates deterministic financial events used to test
known incident scenarios.
"""

from datetime import datetime, timezone

from configs.schema import Payment, Refund, Merchant


def generate_refund_event_latency_incident():
    """
    Generate the controlled REFUND_EVENT_LATENCY hero scenario.

    Returns
    -------
    tuple[Merchant, Payment, Refund]
        Merchant, payment, and refund forming the incident.
    """

    merchant = Merchant(
        merchant_id="MER_INC_0001",
        merchant_name="Incident Merchant",
        segment="ENTERPRISE",
        currency="INR",
        settlement_cycle="T1",
    )

    payment = Payment(
        payment_id="PAY_INC_000001",
        merchant_id=merchant.merchant_id,
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
        merchant_id=merchant.merchant_id,
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

    return merchant, payment, refund