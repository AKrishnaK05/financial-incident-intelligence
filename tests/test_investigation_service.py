from pipeline import run_pipeline
from investigation.service import InvestigationService


def test_investigation_service_returns_validated_mock_response(monkeypatch):
    monkeypatch.setenv("AGENT_PROVIDER", "mock")
    result = run_pipeline()
    report = result.hero_report

    # The factory reads settings at import time, so the repository's
    # default mock provider is used in the test environment.
    response = InvestigationService().investigate(
        report=report,
        evidence=result.evidence_map[report.incident_id],
        timeline=result.timeline_map[report.incident_id],
        hypotheses=result.hypotheses_map[report.incident_id],
        reasoning=result.reasoning_map[report.incident_id],
        recommendation=result.action_recommendations[report.incident_id],
    )

    assert response.narrative.root_cause == "REFUND_EVENT_LATENCY"
    assert response.narrative.reasoning.primary_hypothesis == "REFUND_EVENT_LATENCY"
    assert response.narrative.reasoning.evidence_margin == 0.94
