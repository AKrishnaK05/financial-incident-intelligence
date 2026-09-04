"""
Entry point for the synthetic financial data simulator.

For now, this program generates and displays one payment.
"""
import json
from dataclasses import asdict

from datetime import datetime, timezone

from financial_engine.settlement_engine import calculate_settlement
from financial_engine.batch_builder import build_settlement_batch

from simulator.payment_generator import generate_payment
from simulator.merchant_generator import generate_merchant
from simulator.refund_generator import generate_refunds
from simulator.webhook_generator import generate_refund_webhook
from simulator.scenario_assigner import assign_refund_event_latency
from simulator.incident_generator import generate_refund_event_latency_incident
from simulator.ground_truth_generator import generate_incident_ground_truth

import random

from configs.settings import RANDOM_SEED
from configs.settings import MERCHANT_COUNT


def main():
    """Generate and display one synthetic payment."""
    random.seed(RANDOM_SEED)

    start_time = datetime(
        2026,
        8,
        1,
        tzinfo=timezone.utc,
    )

    settlement_cutoff = datetime(
    2026,
    8,
    20,
    12,
    0,
    tzinfo=timezone.utc,
    )

    merchants = []

    for merchant_number in range(1, MERCHANT_COUNT + 1):
        merchant = generate_merchant(merchant_number)
        merchants.append(merchant)

    payments = []

    for payment_number in range(1,11):
        merchant = random.choice(merchants)
        payment = generate_payment(
            payment_number=payment_number,
            merchant_id=merchant.merchant_id,
            start_time=start_time,
        )

        payments.append(payment)

    refunds = []

    next_refund_number = 1

    for payment in payments:
        payment_refunds = generate_refunds(
            payment=payment,
            refund_number_start=next_refund_number,
        )

        refunds.extend(payment_refunds)

        next_refund_number += len(payment_refunds)

    incident_payment, incident_refund = (
    generate_refund_event_latency_incident()
    )

    payments.append(incident_payment)
    refunds.append(incident_refund)

    incident_refund_id = incident_refund.refund_id

    webhook_events = []

    for event_number, refund in enumerate(refunds, start=1):
        
        scenario = None

        if refund.refund_id == incident_refund_id:
            scenario = "REFUND_EVENT_LATENCY"

        event = generate_refund_webhook(
            event_number=event_number,
            refund=refund,
            scenario=scenario,
        )

        webhook_events.append(event)
    
    settlements = []

    for settlement_number, payment in enumerate(payments, start=1):
        settlement = calculate_settlement(
            settlement_number=settlement_number,
            payment=payment,
            refunds=refunds,
            webhook_events=webhook_events,
            cutoff_at=settlement_cutoff,
        )

        settlements.append(settlement)

    settlement_batches = []

    next_batch_number = 1

    incident_ground_truth = None

    for settlement in settlements:
        if settlement.payment_id == incident_payment.payment_id:
            incident_ground_truth = generate_incident_ground_truth(
                incident_number=1,
                payment=incident_payment,
                refund=incident_refund,
                settlement=settlement,
            )
            break

    for merchant in merchants:
        batch = build_settlement_batch(
            merchant=merchant,
            batch_number=next_batch_number,
            payments=payments,
            cutoff_at=settlement_cutoff,
        )

        if batch.transaction_count > 0:
            settlement_batches.append(batch)

        next_batch_number += 1

    print(f"Generated {len(payments)} payments")
    print("-----------------------------")

    for payment in payments:
        print(
            f"{payment.payment_id} | "
            f"{payment.merchant_id} | "
            f"{payment.order_id} | "
            f"₹{payment.amount} | "
            f"{payment.method} | "
            f"{payment.currency} | "
            f"{payment.captured_at} | "
            f"{payment.status}"
        )

    print()
    print(f"Generated {len(refunds)} refunds")
    print("-----------------------------")

    for refund in refunds:
        print(
            f"{refund.refund_id} | "
            f"{refund.payment_id} | "
            f"₹{refund.amount} | "
            f"{refund.status}"
        )

    print()
    print(f"Generated {len(webhook_events)} webhook events")
    print("-----------------------------")

    for event in webhook_events:
        print(
            f"{event.event_id} | "
            f"{event.entity_id} | "
            f"{event.event_type} | "
            f""
            f"business={event.business_event_at} | "
            f"emitted={event.emitted_at} | "
            f"delivered={event.delivered_at}"
        )

    print()
    print(f"Generated {len(settlements)} settlements")
    print("-----------------------------")

    for settlement in settlements:
        print(
            f"{settlement.settlement_id} | "
            f"{settlement.payment_id} | "
            f"gross=₹{settlement.gross_amount} | "
            f"expected=₹{settlement.expected_net_amount} | "
            f"observed=₹{settlement.observed_net_amount} | "
            f"status={settlement.status}"
        )

    print()
    print(f"Generated {len(settlement_batches)} settlement batches")
    print("-----------------------------")

    for batch in settlement_batches:
        print(
            f"{batch.batch_id} | "
            f"{batch.merchant_id} | "
            f"transactions={batch.transaction_count} | "
            f"expected=₹{batch.expected_amount} | "
            f"status={batch.status}"
        )

    ground_truth_path = "data/ground_truth/incidents.json"

    with open(ground_truth_path, "w", encoding="utf-8") as file:
        json.dump(
            [asdict(incident_ground_truth)],
            file,
            indent=4,
        )

    print()
    print(f"Ground truth written to {ground_truth_path}")

if __name__ == "__main__":
    main()