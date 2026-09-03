"""
Synthetic payment generator for Financial Incident Intelligence.

This module creates realistic-looking payment records that will later
be used to simulate refunds, webhook events, settlements, and incidents.
"""

import random
from datetime import datetime, timedelta, timezone

from configs.schema import Payment
from configs.settings import (
    DEFAULT_CURRENCY,
    PAYMENT_AMOUNTS,
    PAYMENT_METHODS
)

# ---------------------------------------------------------------------------
# Payment generation
# ---------------------------------------------------------------------------

def generate_payment(
    payment_number: int,
    merchant_id: str,
    start_time: datetime,
) -> Payment:
    """
    Generate one synthetic captured payment.

    Parameters
    ----------
    payment_number:
        Numeric identifier used to create a deterministic payment ID.

    merchant_id:
        Merchant associated with the payment.

    start_time:
        Starting point from which the payment timestamp is generated.

    Returns
    -------
    Payment
        A synthetic Payment object.
    """

    payment_id = f"PAY_{payment_number:06d}"
    order_id = f"ORD_{payment_number:06d}"

    amount = random.choice(PAYMENT_AMOUNTS)
    method = random.choice(PAYMENT_METHODS)

    created_at = start_time + timedelta(
        minutes=random.randint(0, 60 * 24 * 20)
    )

    capture_delay = timedelta(
        seconds=random.randint(5, 90)
    )

    captured_at = created_at + capture_delay

    return Payment(
        payment_id=payment_id,
        merchant_id=merchant_id,
        order_id=order_id,
        amount=amount,
        method = method,
        currency=DEFAULT_CURRENCY,
        captured_at=captured_at,
        status="CAPTURED",
    )