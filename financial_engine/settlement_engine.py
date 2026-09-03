"""
Settlement engine for Financial Incident Intelligence.

This module calculates the expected financial state of a payment
and the observed downstream settlement representation at a cutoff.
"""

from configs.schema import Payment, Refund, WebhookEvent, Settlement


def calculate_settlement(
    settlement_number: int,
    payment: Payment,
    refunds: list[Refund],
    webhook_events: list[WebhookEvent],
    cutoff_at,
) -> Settlement:
    """
    Calculate expected and observed settlement amounts for a payment.

    Expected amount is based on refunds that were actually processed
    before the settlement cutoff.

    Observed amount is based on refund events that had been delivered
    by the settlement cutoff.
    """

    payment_refunds = [
        refund
        for refund in refunds
        if refund.payment_id == payment.payment_id
    ]

    payment_events = [
        event
        for event in webhook_events
        if event.entity_id in {
            refund.refund_id
            for refund in payment_refunds
        }
    ]

    expected_refund_amount = sum(
        refund.amount
        for refund in payment_refunds
        if refund.processed_at <= cutoff_at
    )

    observed_refund_ids = {
        event.entity_id
        for event in payment_events
        if (
            event.event_type == "refund.processed"
            and event.delivered_at <= cutoff_at
        )
    }

    observed_refund_amount = sum(
        refund.amount
        for refund in payment_refunds
        if refund.refund_id in observed_refund_ids
    )

    expected_net_amount = (
        payment.amount - expected_refund_amount
    )

    observed_net_amount = (
        payment.amount - observed_refund_amount
    )

    variance = (
        expected_net_amount - observed_net_amount
    )

    settlement_id = f"SET_{settlement_number:06d}"
    batch_id = f"BATCH_{payment.merchant_id}_{cutoff_at:%Y%m%d}"

    status = "EXCEPTION" if variance != 0 else "MATCHED"

    return Settlement(
        settlement_id=settlement_id,
        batch_id=batch_id,
        merchant_id=payment.merchant_id,
        payment_id=payment.payment_id,
        gross_amount=payment.amount,
        refund_adjustment=expected_refund_amount,
        expected_net_amount=expected_net_amount,
        observed_net_amount=observed_net_amount,
        cutoff_at=cutoff_at,
        status=status,
    )