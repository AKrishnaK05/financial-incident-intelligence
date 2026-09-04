"""
Ground-truth generator for Financial Incident Intelligence.

This module creates evaluation records for controlled incidents.
"""

from configs.incident_schema import IncidentGroundTruth
from configs.schema import Payment, Refund, Settlement


def generate_incident_ground_truth(
    incident_number: int,
    payment: Payment,
    refund: Refund,
    settlement: Settlement,
) -> IncidentGroundTruth:
    """
    Create a ground-truth record for a controlled incident.
    """

    exposure_amount = abs(
        settlement.expected_net_amount
        - settlement.observed_net_amount
    )

    return IncidentGroundTruth(
        incident_id=f"INC_{incident_number:06d}",
        scenario="REFUND_EVENT_LATENCY",
        root_cause="REFUND_EVENT_LATENCY",
        payment_id=payment.payment_id,
        refund_id=refund.refund_id,
        settlement_id=settlement.settlement_id,
        expected_amount=settlement.expected_net_amount,
        observed_amount=settlement.observed_net_amount,
        exposure_amount=exposure_amount,
    )