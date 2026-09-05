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


def generate_all_ground_truth(
    injected_payments: list[Payment],
    refunds: list[Refund],
    settlements: list[Settlement],
) -> list[IncidentGroundTruth]:
    """
    Create ground-truth records for every intentionally-injected
    incident scenario that actually manifested as a settlement
    variance.

    An incident is only recorded as ground truth when the injected
    scenario produced a real observed/expected mismatch. A refund
    that was intentionally delayed but still arrived before the
    settlement cutoff (a boundary case) settled correctly and is
    therefore not a true incident, even though it came from the
    incident-injection path. This keeps the benchmark honest: it
    reflects what actually went wrong, not what was merely intended
    to go wrong.
    """

    refunds_by_payment = {
        refund.payment_id: refund
        for refund in refunds
    }

    settlements_by_payment = {
        settlement.payment_id: settlement
        for settlement in settlements
    }

    ground_truth = []

    incident_number = 1

    for payment in injected_payments:
        refund = refunds_by_payment.get(payment.payment_id)
        settlement = settlements_by_payment.get(payment.payment_id)

        if refund is None or settlement is None:
            continue

        if settlement.expected_net_amount == settlement.observed_net_amount:
            continue

        ground_truth.append(
            generate_incident_ground_truth(
                incident_number=incident_number,
                payment=payment,
                refund=refund,
                settlement=settlement,
            )
        )

        incident_number += 1

    return ground_truth