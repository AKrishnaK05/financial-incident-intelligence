from governance.action_policy import recommend_action
from investigation.blast_radius import BlastRadius
from investigation.exposure import FinancialExposure
from investigation.hypothesis_engine import Hypothesis
from investigation.incident_report import IncidentReport


EMPTY_BLAST_RADIUS = BlastRadius(
    affected_payment_count=1,
    affected_merchant_count=1,
    affected_payment_methods=["UPI"],
    first_affected_at=None,
)

EMPTY_EXPOSURE = FinancialExposure(
    incident_count=1,
    gross_variance=3000,
    unresolved_exposure=3000,
    affected_payment_count=1,
)


def make_report(
    hypotheses,
    cluster_scope=None,
):
    return IncidentReport(
        incident_id="INC_TEST",
        payment_id="PAY_TEST",
        settlement_id="SET_TEST",
        expected_amount=7000,
        observed_amount=10000,
        variance_amount=-3000,
        severity="HIGH",
        hypotheses=hypotheses,
        timeline=None,
        blast_radius=EMPTY_BLAST_RADIUS,
        financial_exposure=EMPTY_EXPOSURE,
        cluster_id="CLUSTER_1" if cluster_scope else None,
        cluster_scope=cluster_scope,
        cluster_mechanism="REFUND_EVENT_LATENCY" if cluster_scope else None,
    )


def supported_hypothesis(confidence="HIGH"):
    return Hypothesis(
        name="REFUND_EVENT_LATENCY",
        status="SUPPORTED",
        confidence=confidence,
        supporting_evidence=["evidence"],
        contradicting_evidence=[],
    )


def test_no_supported_hypothesis_requires_manual_review():
    unsupported = Hypothesis(
        name="REFUND_EVENT_LATENCY",
        status="UNSUPPORTED",
        confidence="LOW",
        supporting_evidence=[],
        contradicting_evidence=["no evidence"],
    )

    report = make_report([unsupported])

    recommendation = recommend_action(report)

    assert recommendation.action == "MANUAL_REVIEW"
    assert recommendation.requires_approval is True


def test_systemic_scope_with_high_confidence_escalates():
    report = make_report(
        [supported_hypothesis("HIGH")],
        cluster_scope="SYSTEMIC",
    )

    recommendation = recommend_action(report)

    assert recommendation.action == "ESCALATE_INCIDENT"
    assert recommendation.priority == "CRITICAL"
    assert recommendation.requires_approval is True


def test_isolated_high_confidence_recommends_review_and_reprocess():
    report = make_report(
        [supported_hypothesis("HIGH")],
        cluster_scope=None,
    )

    recommendation = recommend_action(report)

    assert recommendation.action == "REVIEW_AND_REPROCESS"
    assert recommendation.requires_approval is True


def test_medium_confidence_requires_manual_review():
    report = make_report(
        [supported_hypothesis("MEDIUM")],
        cluster_scope=None,
    )

    recommendation = recommend_action(report)

    assert recommendation.action == "MANUAL_REVIEW"
    assert recommendation.requires_approval is True


def test_no_action_is_ever_unsupervised():
    """
    Every governance branch must require human approval -- the
    system never resolves a financial exception on its own.
    """

    scenarios = [
        make_report([supported_hypothesis("HIGH")], "SYSTEMIC"),
        make_report([supported_hypothesis("HIGH")], None),
        make_report([supported_hypothesis("MEDIUM")], None),
        make_report(
            [
                Hypothesis(
                    "REFUND_EVENT_LATENCY",
                    "UNSUPPORTED",
                    "LOW",
                    [],
                    ["no evidence"],
                )
            ],
            None,
        ),
    ]

    for report in scenarios:
        assert recommend_action(report).requires_approval is True
