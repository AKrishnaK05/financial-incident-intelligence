"""
Financial exposure analysis for Financial Incident Intelligence.

This module calculates deterministic financial impact from
detected incident variances.

It does not determine root cause, infer losses, or modify
financial records.
"""

from dataclasses import dataclass

from incidents.detector import IncidentCandidate


@dataclass
class FinancialExposure:
    """
    Represents the financial impact associated with
    a set of detected incidents.
    """

    incident_count: int
    gross_variance: int
    unresolved_exposure: int
    affected_payment_count: int

def calculate_financial_exposure(
    incidents: list[IncidentCandidate],
) -> FinancialExposure:
    """
    Calculate deterministic financial exposure from
    detected incident variances.

    Exposure is based only on unresolved detected variance.
    No assumption is made about actual monetary loss.
    """

    incident_count = len(incidents)

    gross_variance = sum(
        abs(incident.variance_amount)
        for incident in incidents
    )

    affected_payment_ids = {
        incident.payment_id
        for incident in incidents
    }

    affected_payment_count = len(
        affected_payment_ids
    )

    unresolved_exposure = gross_variance

    return FinancialExposure(
        incident_count=incident_count,
        gross_variance=gross_variance,
        unresolved_exposure=unresolved_exposure,
        affected_payment_count=affected_payment_count,
    )