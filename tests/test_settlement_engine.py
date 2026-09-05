from datetime import timedelta

from financial_engine.settlement_engine import calculate_settlement

from tests.conftest import make_refund, make_webhook


def test_no_refund_settles_cleanly(clean_payment, cutoff):
    settlement = calculate_settlement(
        settlement_number=1,
        payment=clean_payment,
        refunds=[],
        webhook_events=[],
        cutoff_at=cutoff,
    )

    assert settlement.expected_net_amount == clean_payment.amount
    assert settlement.observed_net_amount == clean_payment.amount
    assert settlement.status == "MATCHED"


def test_refund_processed_and_webhook_delivered_before_cutoff_matches(
    refunded_payment, cutoff
):
    refund = make_refund(
        refunded_payment,
        amount=3000,
        processed_at=cutoff - timedelta(hours=1),
    )

    webhook = make_webhook(refund, delivered_at=cutoff - timedelta(minutes=30))

    settlement = calculate_settlement(
        settlement_number=1,
        payment=refunded_payment,
        refunds=[refund],
        webhook_events=[webhook],
        cutoff_at=cutoff,
    )

    assert settlement.expected_net_amount == 7000
    assert settlement.observed_net_amount == 7000
    assert settlement.status == "MATCHED"


def test_delayed_webhook_produces_expected_variance(refunded_payment, cutoff):
    """
    The hero scenario: refund processed before cutoff, but its
    webhook is delivered after the cutoff. Settlement should show
    the refund as pending, producing an observed amount that is
    too high by exactly the refund amount.
    """

    refund = make_refund(
        refunded_payment,
        amount=3000,
        processed_at=cutoff - timedelta(hours=1),
    )

    webhook = make_webhook(refund, delivered_at=cutoff + timedelta(hours=1))

    settlement = calculate_settlement(
        settlement_number=1,
        payment=refunded_payment,
        refunds=[refund],
        webhook_events=[webhook],
        cutoff_at=cutoff,
    )

    assert settlement.expected_net_amount == 7000
    assert settlement.observed_net_amount == 10000
    assert settlement.status == "EXCEPTION"


def test_refund_processed_after_cutoff_is_not_yet_expected(
    refunded_payment, cutoff
):
    refund = make_refund(
        refunded_payment,
        amount=3000,
        processed_at=cutoff + timedelta(minutes=5),
    )

    webhook = make_webhook(refund, delivered_at=cutoff + timedelta(minutes=10))

    settlement = calculate_settlement(
        settlement_number=1,
        payment=refunded_payment,
        refunds=[refund],
        webhook_events=[webhook],
        cutoff_at=cutoff,
    )

    assert settlement.expected_net_amount == refunded_payment.amount
    assert settlement.observed_net_amount == refunded_payment.amount
    assert settlement.status == "MATCHED"
