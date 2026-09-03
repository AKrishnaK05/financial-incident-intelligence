"""
Settlement batch builder for Financial Incident Intelligence.

This module groups eligible payments into synthetic settlement batches.
"""

from datetime import datetime

from configs.schema import Merchant, Payment, SettlementBatch


def build_settlement_batch(
    merchant: Merchant,
    batch_number: int,
    payments: list[Payment],
    cutoff_at: datetime,
) -> SettlementBatch:
    """
    Build a settlement batch for a merchant at a given cutoff.

    Payments are eligible when they belong to the merchant and
    were captured on or before the cutoff.
    """

    eligible_payments = [
        payment
        for payment in payments
        if (
            payment.merchant_id == merchant.merchant_id
            and payment.captured_at <= cutoff_at
        )
    ]

    expected_amount = sum(
        payment.amount
        for payment in eligible_payments
    )

    batch_id = (
        f"BATCH_{merchant.merchant_id}_{cutoff_at:%Y%m%d}"
    )

    return SettlementBatch(
        batch_id=batch_id,
        merchant_id=merchant.merchant_id,
        cutoff_at=cutoff_at,
        transaction_count=len(eligible_payments),
        expected_amount=expected_amount,
        observed_amount=expected_amount,
        status="MATCHED",
    )