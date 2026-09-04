"""
Blast-radius analysis for Financial Incident Intelligence.

This module determines the scope and financial exposure of a set
of detected incidents.
"""

from dataclasses import dataclass
from datetime import datetime

from configs.schema import Payment
from incidents.detector import IncidentCandidate
from investigation.state_graph import FinancialStateGraph


@dataclass
class BlastRadius:
    """
    Represents the scope of a financial incident.
    """

    affected_payment_count: int
    affected_merchant_count: int
    total_exposure: int
    affected_payment_methods: list[str]
    first_affected_at: datetime | None


def analyze_blast_radius(
    incidents: list[IncidentCandidate],
    graph: FinancialStateGraph,
) -> BlastRadius:
    """
    Calculate the financial and operational scope of detected incidents.
    """

    affected_payments: list[Payment] = []
    affected_merchants = set()
    affected_payment_methods = set()

    total_exposure = 0
    first_affected_at = None

    for incident in incidents:
        payment = graph.payments.get(incident.payment_id)

        if payment is None:
            continue

        affected_payments.append(payment)

        affected_merchants.add(payment.merchant_id)
        affected_payment_methods.add(payment.method)

        total_exposure += abs(incident.variance_amount)

        if (
            first_affected_at is None
            or payment.captured_at < first_affected_at
        ):
            first_affected_at = payment.captured_at

    return BlastRadius(
        affected_payment_count=len(affected_payments),
        affected_merchant_count=len(affected_merchants),
        total_exposure=total_exposure,
        affected_payment_methods=sorted(
            affected_payment_methods
        ),
        first_affected_at=first_affected_at,
    )