"""Narrated CLI demo for Financial Incident Intelligence.

The reusable computation lives in :mod:`pipeline`. This module only
runs it and prints a judge-friendly walkthrough of the result.

Run with::

    python -m simulator.main
"""

from pipeline import investigate_report, run_pipeline


def main() -> None:
    result = run_pipeline()

    total = len(result.state_graph.settlements)
    exceptions = len(result.detected_incidents)
    matched = total - exceptions
    match_rate = matched / total * 100 if total else 0.0

    print("\nFinancial Incident Intelligence")
    print("=" * 42)
    print("A financial state graph + autonomous investigation agent")
    print("for distributed payment operations.\n")

    print("Synthetic financial world")
    print("-----------------------------")
    print(f"Merchants:   {len(result.state_graph.merchants)}")
    print(f"Payments:    {len(result.state_graph.payments)}")
    print(f"Refunds:     {len(result.state_graph.refunds)}")
    print(f"Webhooks:    {len(result.state_graph.webhook_events)}")
    print(f"Settlements: {total}")

    print("\nDetected incidents")
    print("-----------------------------")
    print(f"Exceptions: {exceptions}")
    for incident in result.detected_incidents:
        print(
            f"{incident.incident_id}: "
            f"{incident.payment_id} | "
            f"variance ₹{abs(incident.variance_amount):,} | "
            f"{incident.severity}"
        )

    print("\nBatch finance report")
    print("-----------------------------")
    print(f"Records processed: {total}")
    print(f"Matched:           {matched}")
    print(f"Match rate:        {match_rate:.2f}%")
    print(f"Gross variance:    ₹{result.financial_exposure.gross_variance:,}")
    print(f"Unresolved exposure: ₹{result.financial_exposure.unresolved_exposure:,}")

    print("\nIncident clusters")
    print("-----------------------------")
    for cluster in result.clusters:
        print(
            f"{cluster.cluster_id}: {len(cluster.incidents)} incidents | "
            f"{cluster.scope} | {cluster.mechanism} | "
            f"{len(cluster.affected_merchants)} merchants"
        )
        print(f"  {cluster.scope_reason}")

    report = result.hero_report
    if report is None:
        print("\nHero incident was not detected.")
        return

    evidence = result.evidence_map[report.incident_id]
    timeline = result.timeline_map[report.incident_id]
    reasoning = result.reasoning_map[report.incident_id]
    recommendation = result.action_recommendations[report.incident_id]
    approval = result.approval_requests.get(report.incident_id)

    print("\nHero incident investigation")
    print("-----------------------------")
    print(f"Incident:   {report.incident_id}")
    print(f"Payment:    {report.payment_id}")
    print(f"Settlement: {report.settlement_id}")
    print(f"Expected:   ₹{report.expected_amount:,}")
    print(f"Observed:   ₹{report.observed_amount:,}")
    print(f"Variance:   ₹{abs(report.variance_amount):,}")
    print(f"Severity:   {report.severity}")

    print("\nEvidence")
    print(f"  Refunds: {len(evidence.refunds)}")
    print(f"  Webhooks: {len(evidence.webhook_events)}")
    print(
        "  Refund processed before cutoff: "
        f"{timeline.refund_processed_before_cutoff}"
    )
    print(
        "  Webhook delivered before cutoff: "
        f"{timeline.webhook_delivered_before_cutoff}"
    )
    print(f"  Delivery delay: {timeline.webhook_delivery_delay}")

    print("\nDeterministic reasoning")
    print(f"  Primary: {reasoning.primary_hypothesis}")
    print(f"  Confidence: {reasoning.primary_confidence}")
    print(f"  Evidence score: {reasoning.primary_score}")
    print(f"  Evidence margin: {reasoning.evidence_margin}")
    for assessment in reasoning.assessments:
        print(
            f"  - {assessment.hypothesis_name}: "
            f"{assessment.status} / {assessment.confidence} / "
            f"score={assessment.evidence_score}"
        )

    print("\nGovernance")
    print(f"  Action: {recommendation.action}")
    print(f"  Priority: {recommendation.priority}")
    print(f"  Approval required: {recommendation.requires_approval}")
    if approval:
        print(f"  Approval request: {approval.request_id} ({approval.status})")

    print("\nAI investigation")
    print("-----------------------------")
    try:
        response = investigate_report(result, report)
        narrative = response.narrative
        print(f"Provider: {response.provider}")
        print(f"Model: {response.model}")
        print(f"Summary: {narrative.summary}")
        print(f"Root cause: {narrative.root_cause}")
        print(f"Confidence: {narrative.confidence}")
        print(f"Recommended action: {narrative.recommended_action}")
        print("Uncertainty:")
        for item in narrative.uncertainty:
            print(f"  - {item}")
    except Exception as error:  # noqa: BLE001
        print(f"AI investigation unavailable: {error}")
        print("The deterministic investigation remains available.")


if __name__ == "__main__":
    main()
