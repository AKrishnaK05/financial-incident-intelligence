"""
Synthetic refund generator for Financial Incident Intelligence.

This module generates zero or more refunds associated with a payment.
"""

import random
from datetime import timedelta

from configs.schema import Payment, Refund
from configs.settings import DEFAULT_CURRENCY


REFUND_PROBABILITY = 0.20
MAX_REFUNDS_PER_PAYMENT = 3


def generate_refunds(
    payment: Payment,
    refund_number_start: int,
) -> list[Refund]:
    """
    Generate zero or more refunds for a captured payment.

    Parameters
    ----------
    payment:
        The payment that may receive refunds.

    refund_number_start:
        Starting number used to create refund IDs.

    Returns
    -------
    list[Refund]
        A list containing zero or more Refund objects.
    """

    should_refund = random.random() < REFUND_PROBABILITY

    if not should_refund:
        return []

    refund_count = random.randint(
        1,
        MAX_REFUNDS_PER_PAYMENT,
    )

    refunds = []

    remaining_amount = payment.amount

    for refund_index in range(refund_count):

        if remaining_amount <= 1:
            break

        refund_id = (
            f"RFND_{refund_number_start + refund_index:06d}"
        )

        minimum_refund = max(
            1,
            remaining_amount // 5,
        )

        refund_amount = random.randint(
            minimum_refund,
            remaining_amount,
        )

        requested_at = payment.captured_at + timedelta(
            hours=random.randint(1, 48)
        )

        processed_at = requested_at + timedelta(
            minutes=random.randint(1, 180)
        )

        refund = Refund(
            refund_id=refund_id,
            payment_id=payment.payment_id,
            merchant_id=payment.merchant_id,
            amount=refund_amount,
            currency=DEFAULT_CURRENCY,
            requested_at=requested_at,
            processed_at=processed_at,
            status="PROCESSED",
        )

        refunds.append(refund)

        remaining_amount -= refund_amount

    return refunds