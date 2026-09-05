"""
Shared pytest fixtures for the Financial Incident Intelligence
test suite.
"""

from datetime import datetime, timedelta, timezone

import pytest

from configs.schema import Payment, Refund, WebhookEvent


CUTOFF = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def cutoff():
    return CUTOFF


@pytest.fixture
def clean_payment():
    """A payment with no refunds -- should always settle cleanly."""

    return Payment(
        payment_id="PAY_TEST_001",
        merchant_id="MER_TEST_001",
        order_id="ORD_TEST_001",
        amount=10000,
        method="UPI",
        currency="INR",
        captured_at=CUTOFF - timedelta(hours=2),
        status="CAPTURED",
    )


@pytest.fixture
def refunded_payment():
    """A payment with one refund fully processed before cutoff."""

    return Payment(
        payment_id="PAY_TEST_002",
        merchant_id="MER_TEST_001",
        order_id="ORD_TEST_002",
        amount=10000,
        method="UPI",
        currency="INR",
        captured_at=CUTOFF - timedelta(hours=2),
        status="CAPTURED",
    )


def make_refund(payment: Payment, amount: int, processed_at: datetime) -> Refund:
    return Refund(
        refund_id=f"RFND_{payment.payment_id}",
        payment_id=payment.payment_id,
        merchant_id=payment.merchant_id,
        amount=amount,
        currency="INR",
        requested_at=processed_at - timedelta(minutes=15),
        processed_at=processed_at,
        status="PROCESSED",
    )


def make_webhook(
    refund: Refund,
    delivered_at: datetime,
    emitted_at: datetime | None = None,
) -> WebhookEvent:
    emitted_at = emitted_at or refund.processed_at + timedelta(seconds=5)

    return WebhookEvent(
        event_id=f"EVT_{refund.refund_id}",
        entity_id=refund.refund_id,
        event_type="refund.processed",
        business_event_at=refund.processed_at,
        emitted_at=emitted_at,
        delivered_at=delivered_at,
        delivery_status="DELIVERED",
    )
