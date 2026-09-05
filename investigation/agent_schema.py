"""External LLM output schema and conversion boundary."""

from pydantic import BaseModel

from investigation.investigation_models import InvestigationNarrative
from investigation.reasoning import ReasoningAssessment


class AgentOutput(BaseModel):
    """Exact JSON shape accepted from an investigation LLM."""

    incident_id: str
    summary: str
    root_cause: str | None
    confidence: str
    evidence_summary: list[str]
    uncertainty: list[str]
    recommended_action: str


def convert_agent_output(
    output: AgentOutput,
    reasoning: ReasoningAssessment,
) -> InvestigationNarrative:
    """Convert external LLM output into the internal domain model."""

    return InvestigationNarrative(
        incident_id=output.incident_id,
        summary=output.summary,
        root_cause=output.root_cause,
        confidence=output.confidence,
        evidence_summary=output.evidence_summary,
        uncertainty=output.uncertainty,
        recommended_action=output.recommended_action,
        reasoning=reasoning,
    )
