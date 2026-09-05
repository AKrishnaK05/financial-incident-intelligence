"""
Reusable pipeline for Financial Incident Intelligence.

Runs the full loop -- synthetic data generation, settlement
calculation, incident detection, investigation, correlation,
exposure, and governance -- and returns every intermediate artifact
as plain data, with no printing and no side effects beyond
generation.

`simulator/main.py` is the narrated CLI walkthrough used for the
pitch demo; it prints each stage as it goes and is left as-is. This
module is the library entry point used by everything that needs the
same computation without the narration: the test suite, the
evaluation harness, the API, and the UI.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import random

from configs.incident_schema import IncidentGroundTruth
from configs.settings import MERCHANT_COUNT, RANDOM_SEED

from financial_engine.batch_builder import build_settlement_batch
from financial_engine.settlement_engine import calculate_settlement

from governance.action_policy import ActionRecommendation, recommend_action
from governance.approval import ApprovalRequest, create_approval_request

from incidents.detector import IncidentCandidate, detect_incidents

from investigation.blast_radius import BlastRadius, analyze_blast_radius
from investigation.evidence import IncidentEvidence, collect_incident_evidence
from investigation.exposure import FinancialExposure, calculate_financial_exposure
from investigation.hypothesis_engine import Hypothesis, evaluate_hypotheses
from investigation.incident_correlator import IncidentCluster, correlate_incidents
from investigation.incident_report import IncidentReport, build_incident_report
from investigation.investigation_models import AgentResponse
from investigation.reasoning import ReasoningAssessment, build_reasoning_assessment
from investigation.service import InvestigationService
from investigation.state_graph import FinancialStateGraph, build_state_graph
from investigation.timeline import TimelineFacts, analyze_timeline

from simulator.ground_truth_generator import generate_all_ground_truth
from simulator.incident_generator import generate_refund_event_latency_incident
from simulator.merchant_generator import generate_merchant
from simulator.payment_generator import generate_payment
from simulator.refund_generator import generate_refunds
from simulator.systemic_incident_generator import (
    generate_systemic_refund_latency_incidents,
)
from simulator.webhook_generator import generate_refund_webhook


DEFAULT_START_TIME = datetime(2026, 8, 1, tzinfo=timezone.utc)
DEFAULT_SETTLEMENT_CUTOFF = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)
DEFAULT_BASE_PAYMENT_COUNT = 30


@dataclass
class PipelineResult:
    """
    Every artifact produced by one end-to-end pipeline run.
    """

    state_graph: FinancialStateGraph
    detected_incidents: list[IncidentCandidate]

    evidence_map: dict[str, IncidentEvidence]
    timeline_map: dict[str, TimelineFacts]
    hypotheses_map: dict[str, list[Hypothesis]]
    reasoning_map: dict[str, ReasoningAssessment]

    clusters: list[IncidentCluster]
    cluster_map: dict[str, IncidentCluster]

    blast_radius: BlastRadius
    financial_exposure: FinancialExposure

    incident_reports: list[IncidentReport]
    ground_truth: list[IncidentGroundTruth]

    hero_report: IncidentReport | None

    action_recommendations: dict[str, ActionRecommendation]
    approval_requests: dict[str, ApprovalRequest]

    def report_by_payment(self, payment_id: str) -> IncidentReport | None:
        for report in self.incident_reports:
            if report.payment_id == payment_id:
                return report
        return None


def run_pipeline(
    base_payment_count: int = DEFAULT_BASE_PAYMENT_COUNT,
    merchant_count: int = MERCHANT_COUNT,
    random_seed: int = RANDOM_SEED,
    start_time: datetime = DEFAULT_START_TIME,
    settlement_cutoff: datetime = DEFAULT_SETTLEMENT_CUTOFF,
) -> PipelineResult:
    """
    Run the full Financial Incident Intelligence pipeline once and
    return every intermediate artifact.

    Deterministic for a fixed random_seed. The default scale is 30 base payments + 1 hero incident + 20
    systemic incidents = 51 settlement records, satisfying the
    buildathon batch-size requirement while keeping the run fast.
    Pass a larger base_payment_count for a bigger benchmark run.
    """

    random.seed(random_seed)

    merchants = [
        generate_merchant(merchant_number)
        for merchant_number in range(1, merchant_count + 1)
    ]

    payments = []

    for payment_number in range(1, base_payment_count + 1):
        merchant = random.choice(merchants)

        payments.append(
            generate_payment(
                payment_number=payment_number,
                merchant_id=merchant.merchant_id,
                start_time=start_time,
            )
        )

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

    systemic_merchants, systemic_payments, systemic_refunds = (
        generate_systemic_refund_latency_incidents()
    )

    merchants.extend(systemic_merchants)
    payments.extend(systemic_payments)
    refunds.extend(systemic_refunds)

    injected_payments = [incident_payment] + systemic_payments

    webhook_events = []

    for index, refund in enumerate(refunds, start=1):
        scenario = None

        if (
            refund.refund_id == incident_refund.refund_id
            or refund.refund_id.startswith("RFND_SYS_")
        ):
            scenario = "REFUND_EVENT_LATENCY"

        webhook_events.append(
            generate_refund_webhook(index, refund, scenario=scenario)
        )

    settlements = []

    for settlement_number, payment in enumerate(payments, start=1):
        settlements.append(
            calculate_settlement(
                settlement_number=settlement_number,
                payment=payment,
                refunds=refunds,
                webhook_events=webhook_events,
                cutoff_at=settlement_cutoff,
            )
        )

    ground_truth = generate_all_ground_truth(
        injected_payments,
        refunds,
        settlements,
    )

    detected_incidents = detect_incidents(settlements)

    settlement_batches = []

    for batch_number, merchant in enumerate(merchants, start=1):
        batch = build_settlement_batch(
            merchant=merchant,
            batch_number=batch_number,
            payments=payments,
            cutoff_at=settlement_cutoff,
        )

        if batch.transaction_count > 0:
            settlement_batches.append(batch)

    state_graph = build_state_graph(
        merchants=merchants,
        payments=payments,
        refunds=refunds,
        webhook_events=webhook_events,
        settlements=settlements,
        batches=settlement_batches,
    )

    financial_exposure = calculate_financial_exposure(detected_incidents)

    evidence_map: dict[str, IncidentEvidence] = {}
    timeline_map: dict[str, TimelineFacts] = {}
    hypotheses_map: dict[str, list[Hypothesis]] = {}
    reasoning_map: dict[str, ReasoningAssessment] = {}

    for incident in detected_incidents:
        evidence = collect_incident_evidence(incident, state_graph)
        timeline = analyze_timeline(evidence)
        hypotheses = evaluate_hypotheses(evidence, timeline)
        reasoning = build_reasoning_assessment(hypotheses)

        evidence_map[incident.incident_id] = evidence
        timeline_map[incident.incident_id] = timeline
        hypotheses_map[incident.incident_id] = hypotheses
        reasoning_map[incident.incident_id] = reasoning

    clusters = correlate_incidents(
        detected_incidents,
        evidence_map,
        timeline_map,
    )

    cluster_map: dict[str, IncidentCluster] = {}

    for cluster in clusters:
        for incident in cluster.incidents:
            cluster_map[incident.incident_id] = cluster

    blast_radius = analyze_blast_radius(detected_incidents, state_graph)

    incident_reports = []

    for incident in detected_incidents:
        report = build_incident_report(
            incident=incident,
            evidence=evidence_map[incident.incident_id],
            timeline=timeline_map[incident.incident_id],
            hypotheses=hypotheses_map[incident.incident_id],
            blast_radius=blast_radius,
            financial_exposure=financial_exposure,
            cluster=cluster_map.get(incident.incident_id),
        )

        incident_reports.append(report)

    hero_report = next(
        (
            report
            for report in incident_reports
            if report.payment_id == incident_payment.payment_id
        ),
        None,
    )

    action_recommendations: dict[str, ActionRecommendation] = {}
    approval_requests: dict[str, ApprovalRequest] = {}
    request_number = 1

    for report in incident_reports:
        recommendation = recommend_action(report)
        action_recommendations[report.incident_id] = recommendation

        if recommendation.requires_approval:
            approval_requests[report.incident_id] = create_approval_request(
                incident_id=report.incident_id,
                recommendation=recommendation,
                request_number=request_number,
            )
            request_number += 1

    return PipelineResult(
        state_graph=state_graph,
        detected_incidents=detected_incidents,
        evidence_map=evidence_map,
        timeline_map=timeline_map,
        hypotheses_map=hypotheses_map,
        reasoning_map=reasoning_map,
        clusters=clusters,
        cluster_map=cluster_map,
        blast_radius=blast_radius,
        financial_exposure=financial_exposure,
        incident_reports=incident_reports,
        ground_truth=ground_truth,
        hero_report=hero_report,
        action_recommendations=action_recommendations,
        approval_requests=approval_requests,
    )


def investigate_report(
    result: PipelineResult,
    report: IncidentReport,
) -> AgentResponse:
    """Run and validate the configured investigation agent for one incident."""

    incident_id = report.incident_id

    if incident_id not in result.evidence_map:
        raise KeyError(f"Evidence for incident {incident_id} was not found.")

    recommendation = result.action_recommendations.get(incident_id)
    if recommendation is None:
        raise KeyError(
            f"Governance recommendation for incident {incident_id} was not found."
        )

    service = InvestigationService()

    return service.investigate(
        report=report,
        evidence=result.evidence_map[incident_id],
        timeline=result.timeline_map[incident_id],
        hypotheses=result.hypotheses_map[incident_id],
        reasoning=result.reasoning_map[incident_id],
        recommendation=recommendation,
    )
