"""
Evidence collection for Financial Incident Intelligence.

This module collects factual evidence related to a detected incident.
It does not determine the root cause.
"""

from dataclasses import dataclass

from configs.schema import (
    Payment,
    Refund,
    Settlement,
    SettlementBatch,
    WebhookEvent,
)
from incidents.detector import IncidentCandidate
from investigation.state_graph import FinancialStateGraph


@dataclass
class IncidentEvidence:
    """
    Factual evidence collected for a detected incident.
    """

    incident_id: str
    payment: Payment
    refunds: list[Refund]
    webhook_events: list[WebhookEvent]
    settlement: Settlement
    batch: SettlementBatch | None


def collect_incident_evidence(
    incident: IncidentCandidate,
    graph: FinancialStateGraph,
) -> IncidentEvidence:
    """
    Collect all relevant financial entities for an incident.

    This function gathers evidence only. It does not infer
    a root cause or generate a hypothesis.
    """

    payment = graph.payments.get(incident.payment_id)

    if payment is None:
        raise ValueError(
            f"Payment {incident.payment_id} not found in state graph."
        )

    refunds = graph.get_payment_refunds(
        incident.payment_id
    )

    webhook_events = []

    for refund in refunds:
        webhook_events.extend(
            graph.get_refund_events(refund.refund_id)
        )

    settlement = graph.get_payment_settlement(
        incident.payment_id
    )

    if settlement is None:
        raise ValueError(
            f"Settlement for payment "
            f"{incident.payment_id} not found."
        )

    batch = graph.get_payment_batch(
        incident.payment_id
    )

    return IncidentEvidence(
        incident_id=incident.incident_id,
        payment=payment,
        refunds=refunds,
        webhook_events=webhook_events,
        settlement=settlement,
        batch=batch,
    )