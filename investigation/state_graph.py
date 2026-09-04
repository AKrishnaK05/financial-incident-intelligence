"""
Financial state graph for Financial Incident Intelligence.

This module connects financial entities into an investigation-ready
representation.
"""

from dataclasses import dataclass, field

from configs.schema import (
    Merchant,
    Payment,
    Refund,
    Settlement,
    SettlementBatch,
    WebhookEvent,
)


@dataclass
class FinancialStateGraph:
    merchants: dict[str, Merchant] = field(default_factory=dict)
    payments: dict[str, Payment] = field(default_factory=dict)
    refunds: dict[str, Refund] = field(default_factory=dict)
    webhook_events: dict[str, WebhookEvent] = field(default_factory=dict)
    settlements: dict[str, Settlement] = field(default_factory=dict)
    batches: dict[str, SettlementBatch] = field(default_factory=dict)

    def get_payment_refunds(
        self,
        payment_id: str,
    ) -> list[Refund]:
        """Return all refunds associated with a payment."""

        return [
            refund
            for refund in self.refunds.values()
            if refund.payment_id == payment_id
        ]


    def get_refund_events(
        self,
        refund_id: str,
    ) -> list[WebhookEvent]:
        """Return all webhook events associated with a refund."""

        return [
            event
            for event in self.webhook_events.values()
            if event.entity_id == refund_id
        ]


    def get_payment_settlement(
        self,
        payment_id: str,
    ) -> Settlement | None:
        """Return the settlement associated with a payment."""

        for settlement in self.settlements.values():
            if settlement.payment_id == payment_id:
                return settlement

        return None


    def get_payment_batch(
        self,
        payment_id: str,
    ) -> SettlementBatch | None:
        """Return the settlement batch containing a payment."""

        settlement = self.get_payment_settlement(payment_id)

        if settlement is None:
            return None

        return self.batches.get(settlement.batch_id)

def build_state_graph(
    merchants: list[Merchant],
    payments: list[Payment],
    refunds: list[Refund],
    webhook_events: list[WebhookEvent],
    settlements: list[Settlement],
    batches: list[SettlementBatch],
) -> FinancialStateGraph:
    """
    Build an investigation-ready financial state graph.
    """

    graph = FinancialStateGraph()

    for merchant in merchants:
        graph.merchants[merchant.merchant_id] = merchant

    for payment in payments:
        graph.payments[payment.payment_id] = payment

    for refund in refunds:
        graph.refunds[refund.refund_id] = refund

    for event in webhook_events:
        graph.webhook_events[event.event_id] = event

    for settlement in settlements:
        graph.settlements[settlement.settlement_id] = settlement

    for batch in batches:
        graph.batches[batch.batch_id] = batch

    return graph