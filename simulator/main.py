"""
Entry point for the synthetic financial data simulator.

For now, this program generates and displays one payment.
"""
import json
from dataclasses import asdict

from datetime import datetime, timezone

from investigation.evidence import collect_incident_evidence
from investigation.timeline import analyze_timeline
from investigation.hypothesis_engine import evaluate_hypotheses
from investigation.blast_radius import analyze_blast_radius
from investigation.incident_correlator import correlate_incidents
from investigation.incident_report import build_incident_report
from investigation.exposure import calculate_financial_exposure 
from investigation.state_graph import build_state_graph
from investigation.agent_context import build_agent_context
from investigation.agent_prompt import build_investigation_prompt
from investigation.agent_factory import create_investigation_agent
from investigation.agent_validator import validate_investigation_narrative

from incidents.detector import detect_incidents 

from financial_engine.settlement_engine import calculate_settlement
from financial_engine.batch_builder import build_settlement_batch

from simulator.payment_generator import generate_payment
from simulator.merchant_generator import generate_merchant
from simulator.refund_generator import generate_refunds
from simulator.webhook_generator import generate_refund_webhook
from simulator.scenario_assigner import assign_refund_event_latency
from simulator.incident_generator import generate_refund_event_latency_incident
from simulator.ground_truth_generator import generate_incident_ground_truth
from simulator.systemic_incident_generator import generate_systemic_refund_latency_incidents

from governance.action_policy import recommend_action
from governance.approval import create_approval_request, review_approval_request

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

    incident_merchant, incident_payment, incident_refund = (
    generate_refund_event_latency_incident()
    )

    merchants.append(incident_merchant)
    payments.append(incident_payment)
    refunds.append(incident_refund)

    incident_refund_id = incident_refund.refund_id

    systemic_merchants, systemic_payments, systemic_refunds = (
    generate_systemic_refund_latency_incidents()
    )

    merchants.extend(systemic_merchants)
    payments.extend(systemic_payments)
    refunds.extend(systemic_refunds)

    webhook_events = []

    for index, refund in enumerate(refunds, start=1):
        scenario = None

        if (
            refund.refund_id == incident_refund.refund_id
            or refund.refund_id.startswith("RFND_SYS_")
        ):
            scenario = "REFUND_EVENT_LATENCY"

        webhook_event = generate_refund_webhook(
            index,
            refund,
            scenario=scenario,
        )

        webhook_events.append(webhook_event)
    
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

    detected_incidents = detect_incidents(settlements)

    print()
    print("Detected Incidents")
    print("-----------------------------")

    for incident in detected_incidents:
        print(
            f"{incident.incident_id}: "
            f"Payment={incident.payment_id}, "
            f"Settlement={incident.settlement_id}, "
            f"Variance=₹{abs(incident.variance_amount)}, "
            f"Severity={incident.severity}"
        )

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

    state_graph = build_state_graph(
    merchants=merchants,
    payments=payments,
    refunds=refunds,
    webhook_events=webhook_events,
    settlements=settlements,
    batches=settlement_batches,
    )

    incident_payment_refunds = state_graph.get_payment_refunds(
        "PAY_INC_000001"
    )

    incident_refund_events = state_graph.get_refund_events(
        "RFND_INC_000001"
    )

    incident_settlement = state_graph.get_payment_settlement(
        "PAY_INC_000001"
    )

    incident_batch = state_graph.get_payment_batch(
        "PAY_INC_000001"
    )

    financial_exposure = calculate_financial_exposure(
        detected_incidents
    )

    print()
    print("Incident Graph Traversal")
    print("-----------------------------")

    print(
        "Payment:",
        "PAY_INC_000001"
    )

    print(
        "Refunds:",
        [refund.refund_id for refund in incident_payment_refunds]
    )

    print(
        "Webhook events:",
        [event.event_id for event in incident_refund_events]
    )

    print(
        "Settlement:",
        incident_settlement.settlement_id
        if incident_settlement
        else None
    )

    print(
        "Batch:",
        incident_batch.batch_id
        if incident_batch
        else None
    )

    print()
    print("Incident Evidence")
    print("-----------------------------")

    evidence_map = {}
    timeline_map = {}
    hypotheses_map = {}

    print()
    print("Incident Evidence")
    print("-----------------------------")

    for incident in detected_incidents:
        evidence = collect_incident_evidence(
            incident,
            state_graph,
        )

        timeline = analyze_timeline(evidence)
        hypotheses = evaluate_hypotheses(
            evidence,
            timeline,
        )

        evidence_map[incident.incident_id] = evidence
        timeline_map[incident.incident_id] = timeline
        hypotheses_map[incident.incident_id] = hypotheses

        print(f"Incident: {evidence.incident_id}")

        print(
            f"Payment: {evidence.payment.payment_id} "
            f"₹{evidence.payment.amount}"
        )

        print(
            f"Refunds: "
            f"{len(evidence.refunds)}"
        )

        for refund in evidence.refunds:
            print(
                f"  {refund.refund_id}: "
                f"₹{refund.amount}, "
                f"processed={refund.processed_at}"
            )

        print(
            f"Webhook events: "
            f"{len(evidence.webhook_events)}"
        )

        for event in evidence.webhook_events:
            print(
                f"  {event.event_id}: "
                f"emitted={event.emitted_at}, "
                f"delivered={event.delivered_at}"
            )

        print(
            f"Settlement: "
            f"{evidence.settlement.settlement_id}"
        )

        print(
            f"  Expected: "
            f"₹{evidence.settlement.expected_net_amount}"
        )

        print(
            f"  Observed: "
            f"₹{evidence.settlement.observed_net_amount}"
        )

        if evidence.batch is not None:
            print(
                f"Batch: "
                f"{evidence.batch.batch_id}"
            )
        else:
            print("Batch: NOT FOUND")

    incident_clusters = correlate_incidents(
    detected_incidents,
    evidence_map,
    timeline_map,
    )

    print()
    print("Incident Clusters")
    print("-----------------------------")

    for cluster in incident_clusters:
        print(
            f"{cluster.cluster_id}: "
            f"{len(cluster.incidents)} incidents "
            f"({cluster.scope})"
        )

        print(
            f"  Mechanism: "
            f"{cluster.mechanism}"
        )

        print(
            f"  Affected merchants: "
            f"{len(cluster.affected_merchants)}"
        )

        print(
            f"  First affected: "
            f"{cluster.first_affected_at}"
        )

        print(
            f"  Last affected: "
            f"{cluster.last_affected_at}"
        )

        print(
            f"  Correlation: "
            f"{cluster.correlation_reasons}"
        )

        print(
            f"  Scope reason: "
            f"{cluster.scope_reason}"
        )

        print("  Incidents:")

        for incident in cluster.incidents:
            print(
                f"    {incident.incident_id}: "
                f"{incident.payment_id}"
            )

    timeline = analyze_timeline(evidence)

    blast_radius = analyze_blast_radius(
    detected_incidents,
    state_graph,
    )

    print()
    print("Blast Radius")
    print("-----------------------------")

    print(
        f"Affected payments: "
        f"{blast_radius.affected_payment_count}"
    )

    print(
        f"Affected merchants: "
        f"{blast_radius.affected_merchant_count}"
    )

    print(
        f"Payment methods: "
        f"{blast_radius.affected_payment_methods}"
    )

    print(
        f"First affected transaction: "
        f"{blast_radius.first_affected_at}"
    )

    cluster_map = {}

    for cluster in incident_clusters:
        for incident in cluster.incidents:
            cluster_map[incident.incident_id] = cluster

    print()
    print("Timeline Facts")
    print("-----------------------------")

    print(
        f"Refund processed before cutoff: "
        f"{timeline.refund_processed_before_cutoff}"
    )

    print(
        f"Webhook delivered before cutoff: "
        f"{timeline.webhook_delivered_before_cutoff}"
    )

    if timeline.webhook_delivery_delay is not None:
        print(
            f"Webhook delivery delay: "
            f"{timeline.webhook_delivery_delay}"
        )

    if timeline.refund_to_webhook_delay is not None:
        print(
            f"Refund to webhook delay: "
            f"{timeline.refund_to_webhook_delay}"
        )

    hypotheses = evaluate_hypotheses(
    evidence,
    timeline,
    )

    print()
    print("Hypotheses")
    print("-----------------------------")

    for hypothesis in hypotheses:
        print(
            f"{hypothesis.name}: "
            f"{hypothesis.status} "
            f"({hypothesis.confidence})"
        )

        print("Supporting evidence:")

        for item in hypothesis.supporting_evidence:
            print(f"  + {item}")

        if hypothesis.contradicting_evidence:
            print("Contradicting evidence:")

            for item in hypothesis.contradicting_evidence:
                print(f"  - {item}")
    
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

    print()
    print("State Graph")
    print("-----------------------------")
    print(f"Merchants:       {len(state_graph.merchants)}")
    print(f"Payments:        {len(state_graph.payments)}")
    print(f"Refunds:         {len(state_graph.refunds)}")
    print(f"Webhook events:  {len(state_graph.webhook_events)}")
    print(f"Settlements:     {len(state_graph.settlements)}")
    print(f"Batches:         {len(state_graph.batches)}")

    incident_reports = []

    for incident in detected_incidents:
        evidence = evidence_map.get(
            incident.incident_id
        )

        timeline = timeline_map.get(
            incident.incident_id
        )

        if evidence is None or timeline is None:
            continue

        cluster = cluster_map.get(
            incident.incident_id
        )

        report = build_incident_report(
            incident=incident,
            evidence=evidence,
            timeline=timeline,
            hypotheses=hypotheses_map[
                incident.incident_id
            ],
            blast_radius=blast_radius,
            financial_exposure=financial_exposure,
            cluster=cluster,
        )

        incident_reports.append(report)

    hero_report = next(
        report
        for report in incident_reports
        if report.payment_id == "PAY_INC_000001"
    )

    print()
    print("Incident Report")
    print("-----------------------------")

    print(
        f"Incident: {hero_report.incident_id}"
    )

    print(
        f"Payment: {hero_report.payment_id}"
    )

    print(
        f"Settlement: {hero_report.settlement_id}"
    )

    print(
        f"Expected: ₹{hero_report.expected_amount}"
    )

    print(
        f"Observed: ₹{hero_report.observed_amount}"
    )

    print(
        f"Variance: ₹{abs(hero_report.variance_amount)}"
    )

    print(
        f"Severity: {hero_report.severity}"
    )

    primary_hypothesis = (
        hero_report.primary_hypothesis
    )

    if primary_hypothesis is not None:
        print(
            f"Primary hypothesis: "
            f"{primary_hypothesis.name}"
        )

        print(
            f"Confidence: "
            f"{primary_hypothesis.confidence}"
        )

    print(
        f"Cluster: {hero_report.cluster_id}"
    )

    print(
        f"Scope: {hero_report.cluster_scope}"
    )

    print(
        f"Mechanism: {hero_report.cluster_mechanism}"
    )

    print(
        f"Affected payments: "
        f"{hero_report.blast_radius.affected_payment_count}"
    )

    print(
        f"Affected merchants: "
        f"{hero_report.blast_radius.affected_merchant_count}"
    )

    print(
        f"Incident count: "
        f"{hero_report.financial_exposure.incident_count}"
    )

    print(
        f"Gross variance: "
        f"₹{hero_report.financial_exposure.gross_variance}"
    )

    print(
        f"Unresolved exposure: "
        f"₹{hero_report.financial_exposure.unresolved_exposure}"
    )

    action_recommendation = recommend_action(hero_report)

    print()
    print("Recommended Action")
    print("-----------------------------")

    print(
        f"Action: {action_recommendation.action}"
    )

    print(
        f"Priority: {action_recommendation.priority}"
    )

    print(
        f"Requires approval: {action_recommendation.requires_approval}"
    )

    print(
        f"Reason: {action_recommendation.reason}"
    )

    approval_request = create_approval_request(
        incident_id=hero_report.incident_id,
        recommendation=action_recommendation,
        request_number=1,
    )

    print()
    print("Approval")
    print("-----------------------------")

    print(
        f"Request: "
        f"{approval_request.request_id}"
    )

    print(
        f"Status: "
        f"{approval_request.status}"
    )

    print(
        f"Requested at: "
        f"{approval_request.requested_at}"
    ) 

    hero_evidence = evidence_map[
        hero_report.incident_id
    ]

    hero_timeline = timeline_map[
        hero_report.incident_id
    ]

    hero_hypotheses = hypotheses_map[
        hero_report.incident_id
    ]

    agent_context = build_agent_context(
        report=hero_report,
        evidence=hero_evidence,
        timeline=hero_timeline,
        hypotheses=hero_hypotheses,
        recommendation=action_recommendation,
    )

    investigation_prompt = build_investigation_prompt(
        agent_context
    )

    agent = create_investigation_agent()

    agent_response = agent.investigate(
        agent_context
    )

    narrative = agent_response.narrative

    validate_investigation_narrative(
        narrative,
        agent_context,
    )
    
    print()
    print("AI Investigation")
    print("-----------------------------")

    print(
        f"Provider: "
        f"{agent_response.provider}"
    )

    print(
        f"Model: "
        f"{agent_response.model}"
    )

    print(
        f"Summary: "
        f"{narrative.summary}"
    )

    print(
        f"Root cause: "
        f"{narrative.root_cause}"
    )

    print(
        f"Confidence: "
        f"{narrative.confidence}"
    )

    print("Evidence:")

    for evidence in narrative.evidence_summary:
        print(
            f"  + {evidence}"
        )

    print("Uncertainty:")

    if narrative.uncertainty:
        for uncertainty in narrative.uncertainty:
            print(
                f"  - {uncertainty}"
            )
    else:
        print("  None identified.")

    print(
        f"Recommended action: "
        f"{narrative.recommended_action}"
    )

if __name__ == "__main__":
    main()