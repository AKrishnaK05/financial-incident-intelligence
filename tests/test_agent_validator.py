import copy

import pytest

from pipeline import run_pipeline
from investigation.investigation_models import InvestigationNarrative
from investigation.agent_validator import validate_investigation_narrative
from investigation.agent_context import build_agent_context


def _context(result):
    report = result.hero_report
    incident_id = report.incident_id
    return build_agent_context(
        report=report,
        evidence=result.evidence_map[incident_id],
        timeline=result.timeline_map[incident_id],
        hypotheses=result.hypotheses_map[incident_id],
        reasoning=result.reasoning_map[incident_id],
        recommendation=result.action_recommendations[incident_id],
    )


def test_validator_rejects_tampered_reasoning_trace():
    result = run_pipeline()
    context = _context(result)

    tampered_reasoning = copy.deepcopy(context.reasoning)
    tampered_reasoning.primary_hypothesis = "MISSING_REFUND"

    narrative = InvestigationNarrative(
        incident_id=context.report.incident_id,
        summary="tampered",
        root_cause="REFUND_EVENT_LATENCY",
        confidence="HIGH",
        evidence_summary=[],
        uncertainty=[],
        recommended_action=context.recommendation.action,
        reasoning=tampered_reasoning,
    )

    with pytest.raises(ValueError, match="primary hypothesis"):
        validate_investigation_narrative(narrative, context)


def test_validator_rejects_unsafe_action():
    result = run_pipeline()
    context = _context(result)

    narrative = InvestigationNarrative(
        incident_id=context.report.incident_id,
        summary="tampered",
        root_cause="REFUND_EVENT_LATENCY",
        confidence="HIGH",
        evidence_summary=[],
        uncertainty=[],
        recommended_action="REPROCESS_ALL",
        reasoning=context.reasoning,
    )

    with pytest.raises(ValueError, match="recommended action"):
        validate_investigation_narrative(narrative, context)
