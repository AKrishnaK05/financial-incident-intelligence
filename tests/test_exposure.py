from incidents.detector import IncidentCandidate
from investigation.exposure import calculate_financial_exposure


def make_incident(incident_id, payment_id, variance, severity="HIGH"):
    return IncidentCandidate(
        incident_id=incident_id,
        payment_id=payment_id,
        settlement_id=f"SET_{payment_id}",
        expected_amount=0,
        observed_amount=variance,
        variance_amount=variance,
        severity=severity,
    )


def test_no_incidents_means_no_exposure():
    exposure = calculate_financial_exposure([])

    assert exposure.incident_count == 0
    assert exposure.gross_variance == 0
    assert exposure.unresolved_exposure == 0
    assert exposure.affected_payment_count == 0


def test_exposure_sums_absolute_variance_across_incidents():
    incidents = [
        make_incident("INC_1", "PAY_1", -3000),
        make_incident("INC_2", "PAY_2", 1000),
        make_incident("INC_3", "PAY_3", -500),
    ]

    exposure = calculate_financial_exposure(incidents)

    assert exposure.incident_count == 3
    assert exposure.gross_variance == 4500
    assert exposure.unresolved_exposure == 4500
    assert exposure.affected_payment_count == 3


def test_affected_payment_count_deduplicates_repeat_payments():
    incidents = [
        make_incident("INC_1", "PAY_1", -3000),
        make_incident("INC_2", "PAY_1", -1000),
    ]

    exposure = calculate_financial_exposure(incidents)

    assert exposure.affected_payment_count == 1
    assert exposure.gross_variance == 4000
