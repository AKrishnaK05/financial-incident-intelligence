from datetime import datetime, timezone

from configs.schema import Settlement
from incidents.detector import calculate_severity, detect_incidents


def make_settlement(settlement_id, payment_id, expected, observed):
    return Settlement(
        settlement_id=settlement_id,
        batch_id="BATCH_TEST",
        merchant_id="MER_TEST",
        payment_id=payment_id,
        gross_amount=max(expected, observed),
        refund_adjustment=0,
        expected_net_amount=expected,
        observed_net_amount=observed,
        cutoff_at=datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc),
        status="MATCHED" if expected == observed else "EXCEPTION",
    )


def test_matched_settlement_produces_no_incident():
    settlements = [make_settlement("SET_1", "PAY_1", 7000, 7000)]

    incidents = detect_incidents(settlements)

    assert incidents == []


def test_variance_produces_one_incident_with_correct_amounts():
    settlements = [make_settlement("SET_1", "PAY_1", 7000, 10000)]

    incidents = detect_incidents(settlements)

    assert len(incidents) == 1
    incident = incidents[0]
    assert incident.payment_id == "PAY_1"
    assert incident.expected_amount == 7000
    assert incident.observed_amount == 10000
    assert incident.variance_amount == -3000


def test_only_exceptions_are_returned_from_mixed_batch():
    settlements = [
        make_settlement("SET_1", "PAY_1", 7000, 7000),
        make_settlement("SET_2", "PAY_2", 4000, 5000),
        make_settlement("SET_3", "PAY_3", 2000, 2000),
    ]

    incidents = detect_incidents(settlements)

    assert len(incidents) == 1
    assert incidents[0].payment_id == "PAY_2"


def test_severity_thresholds():
    assert calculate_severity(500) == "LOW"
    assert calculate_severity(999) == "LOW"
    assert calculate_severity(1000) == "MEDIUM"
    assert calculate_severity(2999) == "MEDIUM"
    assert calculate_severity(3000) == "HIGH"
    assert calculate_severity(9999) == "HIGH"
    assert calculate_severity(10000) == "CRITICAL"
    assert calculate_severity(-15000) == "CRITICAL"
