"""Internal models returned by investigation providers."""

from dataclasses import dataclass

from investigation.reasoning import ReasoningAssessment


@dataclass
class InvestigationNarrative:
    """Validated, human-readable investigation result."""

    incident_id: str
    summary: str
    root_cause: str | None
    confidence: str
    evidence_summary: list[str]
    uncertainty: list[str]
    recommended_action: str
    reasoning: ReasoningAssessment


@dataclass
class AgentResponse:
    """Provider metadata plus the validated investigation narrative."""

    narrative: InvestigationNarrative
    provider: str
    model: str
