from datetime import datetime, timedelta, timezone

from configs.schema import Settlement
from investigation.evidence import IncidentEvidence
from investigation.hypothesis_engine import evaluate_hypotheses
from investigation.reasoning import build_reasoning_assessment
from investigation.timeline import analyze_timeline

from tests.conftest import make_refund, make_webhook


CUTOFF = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)


def build_evidence(payment, refunds, webhook_events, expected, observed):
    settlement = Settlement(
        settlement_id="SET_TEST",
        batch_id="BATCH_TEST",
        merchant_id=payment.merchant_id,
        payment_id=payment.payment_id,
        gross_amount=payment.amount,
        refund_adjustment=payment.amount - expected,
        expected_net_amount=expected,
        observed_net_amount=observed,
        cutoff_at=CUTOFF,
        status="MATCHED" if expected == observed else "EXCEPTION",
    )

    return IncidentEvidence(
        incident_id="INC_CAND_TEST",
        payment=payment,
        refunds=refunds,
        webhook_events=webhook_events,
        settlement=settlement,
        batch=None,
    )


def test_refund_event_latency_is_supported_with_high_confidence(
    refunded_payment,
):
    refund = make_refund(
        refunded_payment, amount=3000, processed_at=CUTOFF - timedelta(hours=1)
    )
    webhook = make_webhook(refund, delivered_at=CUTOFF + timedelta(hours=1))

    evidence = build_evidence(
        refunded_payment, [refund], [webhook], expected=7000, observed=10000
    )
    timeline = analyze_timeline(evidence)

    hypotheses = evaluate_hypotheses(evidence, timeline)
    by_name = {h.name: h for h in hypotheses}

    latency_hypothesis = by_name["REFUND_EVENT_LATENCY"]
    assert latency_hypothesis.status == "SUPPORTED"
    assert latency_hypothesis.confidence == "HIGH"
    assert latency_hypothesis.contradicting_evidence == []


def test_missing_refund_hypothesis_when_no_refund_exists(clean_payment):
    evidence = build_evidence(
        clean_payment, [], [], expected=7000, observed=10000
    )
    timeline = analyze_timeline(evidence)

    hypotheses = evaluate_hypotheses(evidence, timeline)
    by_name = {h.name: h for h in hypotheses}

    latency_hypothesis = by_name["REFUND_EVENT_LATENCY"]
    assert latency_hypothesis.status != "SUPPORTED"

    missing_refund_hypothesis = by_name["MISSING_REFUND"]
    assert missing_refund_hypothesis.status == "PLAUSIBLE"


def test_reasoning_picks_the_strongest_evidence_backed_hypothesis(
    refunded_payment,
):
    refund = make_refund(
        refunded_payment, amount=3000, processed_at=CUTOFF - timedelta(hours=1)
    )
    webhook = make_webhook(refund, delivered_at=CUTOFF + timedelta(hours=1))

    evidence = build_evidence(
        refunded_payment, [refund], [webhook], expected=7000, observed=10000
    )
    timeline = analyze_timeline(evidence)
    hypotheses = evaluate_hypotheses(evidence, timeline)

    reasoning = build_reasoning_assessment(hypotheses)

    assert reasoning.primary_hypothesis == "REFUND_EVENT_LATENCY"
    assert reasoning.primary_confidence == "HIGH"
    assert reasoning.evidence_margin >= 0


def test_reasoning_returns_no_primary_hypothesis_when_nothing_is_supported(
    clean_payment,
):
    evidence = build_evidence(
        clean_payment, [], [], expected=7000, observed=10000
    )
    timeline = analyze_timeline(evidence)
    hypotheses = evaluate_hypotheses(evidence, timeline)

    reasoning = build_reasoning_assessment(hypotheses)

    assert reasoning.primary_hypothesis is None
    assert reasoning.primary_confidence == "LOW"
