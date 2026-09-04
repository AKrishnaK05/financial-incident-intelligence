"""
Deterministic incident detector for Financial Incident Intelligence.

The detector identifies financial inconsistencies from settlement records.
It does not attempt to determine the root cause.
"""

from dataclasses import dataclass

from configs.schema import Settlement


@dataclass
class IncidentCandidate:
    """
    Represents a detected financial inconsistency.
    """

    incident_id: str
    payment_id: str
    settlement_id: str
    expected_amount: int
    observed_amount: int
    variance_amount: int
    severity: str


def calculate_severity(variance_amount: int) -> str:
    """
    Classify incident severity based on absolute financial variance.
    """

    absolute_variance = abs(variance_amount)

    if absolute_variance >= 10000:
        return "CRITICAL"

    if absolute_variance >= 3000:
        return "HIGH"

    if absolute_variance >= 1000:
        return "MEDIUM"

    return "LOW"


def detect_incidents(
    settlements: list[Settlement],
) -> list[IncidentCandidate]:
    """
    Detect financial inconsistencies across settlement records.

    A settlement becomes an incident candidate when its expected
    and observed amounts do not match.
    """

    incidents = []

    incident_number = 1

    for settlement in settlements:
        variance_amount = (
            settlement.expected_net_amount
            - settlement.observed_net_amount
        )

        if variance_amount == 0:
            continue

        incident = IncidentCandidate(
            incident_id=f"INC_CAND_{incident_number:06d}",
            payment_id=settlement.payment_id,
            settlement_id=settlement.settlement_id,
            expected_amount=settlement.expected_net_amount,
            observed_amount=settlement.observed_net_amount,
            variance_amount=variance_amount,
            severity=calculate_severity(variance_amount),
        )

        incidents.append(incident)
        incident_number += 1

    return incidents