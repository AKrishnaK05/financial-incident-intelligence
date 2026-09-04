"""
Systemic incident generator for Financial Incident Intelligence.

This module creates a deterministic population of correlated
refund-event latency incidents.
"""

from datetime import datetime, timedelta, timezone

from configs.schema import Merchant, Payment, Refund


SYSTEMIC_INCIDENT_PAYMENT_COUNT = 20
SYSTEMIC_INCIDENT_MERCHANT_COUNT = 5


def generate_systemic_refund_latency_incidents():
    """
    Generate a deterministic population of correlated incidents.

    Returns
    -------
    tuple[list[Merchant], list[Payment], list[Refund]]
        Merchants, payments, and refunds participating in the
        systemic incident.
    """

    merchants = []
    payments = []
    refunds = []

    base_time = datetime(
        2026,
        8,
        20,
        8,
        0,
        tzinfo=timezone.utc,
    )

    for merchant_number in range(
        1,
        SYSTEMIC_INCIDENT_MERCHANT_COUNT + 1,
    ):
        merchant = Merchant(
            merchant_id=f"MER_SYS_{merchant_number:04d}",
            merchant_name=(
                f"Systemic Merchant {merchant_number:04d}"
            ),
            segment="MID_MARKET",
            currency="INR",
            settlement_cycle="T1",
        )

        merchants.append(merchant)

    for payment_number in range(
        1,
        SYSTEMIC_INCIDENT_PAYMENT_COUNT + 1,
    ):
        merchant_index = (
            (payment_number - 1)
            % SYSTEMIC_INCIDENT_MERCHANT_COUNT
        )

        merchant = merchants[merchant_index]

        payment_time = base_time + timedelta(
            minutes=payment_number * 10
        )

        payment = Payment(
            payment_id=f"PAY_SYS_{payment_number:06d}",
            merchant_id=merchant.merchant_id,
            order_id=f"ORD_SYS_{payment_number:06d}",
            amount=5000,
            method="UPI",
            currency="INR",
            captured_at=payment_time,
            status="CAPTURED",
        )

        refund = Refund(
            refund_id=f"RFND_SYS_{payment_number:06d}",
            payment_id=payment.payment_id,
            merchant_id=merchant.merchant_id,
            amount=1000,
            currency="INR",
            requested_at=payment_time + timedelta(
                minutes=20
            ),
            processed_at=payment_time + timedelta(
                minutes=30
            ),
            status="PROCESSED",
        )

        payments.append(payment)
        refunds.append(refund)

    return merchants, payments, refunds