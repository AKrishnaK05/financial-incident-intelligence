from evaluation.evaluate import evaluate
from pipeline import investigate_report, run_pipeline


def test_pipeline_runs_end_to_end_and_finds_the_hero_incident():
    result = run_pipeline()

    assert result.hero_report is not None
    assert result.hero_report.payment_id == "PAY_INC_000001"
    assert result.hero_report.variance_amount == -3000
    assert result.hero_report.primary_hypothesis is not None
    assert result.hero_report.primary_hypothesis.name == "REFUND_EVENT_LATENCY"


def test_pipeline_is_deterministic_for_a_fixed_seed():
    first = run_pipeline(random_seed=42)
    second = run_pipeline(random_seed=42)

    assert len(first.detected_incidents) == len(second.detected_incidents)
    assert first.financial_exposure.gross_variance == (
        second.financial_exposure.gross_variance
    )
    assert {i.payment_id for i in first.detected_incidents} == {
        i.payment_id for i in second.detected_incidents
    }


def test_systemic_incidents_are_correlated_into_one_systemic_cluster():
    result = run_pipeline()

    systemic_clusters = [
        cluster for cluster in result.clusters if cluster.scope == "SYSTEMIC"
    ]

    assert len(systemic_clusters) == 1
    assert systemic_clusters[0].mechanism == "REFUND_EVENT_LATENCY"
    assert len(systemic_clusters[0].incidents) >= 5


def test_hero_incident_is_escalated_with_approval_required():
    result = run_pipeline()

    recommendation = result.action_recommendations[result.hero_report.incident_id]

    assert recommendation.requires_approval is True


def test_mock_agent_investigation_matches_deterministic_findings():
    result = run_pipeline()

    response = investigate_report(result, result.hero_report)

    assert response.provider == "mock"
    assert response.narrative.root_cause == "REFUND_EVENT_LATENCY"
    assert response.narrative.confidence == "HIGH"
    assert response.narrative.recommended_action == (
        result.action_recommendations[result.hero_report.incident_id].action
    )


def test_evaluation_report_has_no_false_positives_or_negatives():
    """
    Every detected incident should trace back to an injected
    ground-truth scenario, and every ground-truth scenario that
    actually manifested should be detected -- there is no untracked
    noise source in the simulator yet.
    """

    result = run_pipeline()
    report = evaluate(result)

    assert report.detection.false_positives == 0
    assert report.detection.false_negatives == 0
    assert report.exposure.absolute_error == 0
