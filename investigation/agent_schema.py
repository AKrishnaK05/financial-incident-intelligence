"""
Structured output schema for the Financial Incident Intelligence agent.

This module defines the exact structure expected from a language model.
"""

from pydantic import BaseModel

from investigation.investigation_models import InvestigationNarrative


class AgentOutput(BaseModel):
    """
    Structured response returned by the investigation agent.
    """

    incident_id: str
    summary: str
    root_cause: str | None
    confidence: str
    evidence_summary: list[str]
    uncertainty: list[str]
    recommended_action: str

def convert_agent_output(
    output: AgentOutput,
) -> InvestigationNarrative:
    """
    Convert validated structural output into the domain
    investigation narrative.
    """

    return InvestigationNarrative(
        incident_id=output.incident_id,
        summary=output.summary,
        root_cause=output.root_cause,
        confidence=output.confidence,
        evidence_summary=output.evidence_summary,
        uncertainty=output.uncertainty,
        recommended_action=output.recommended_action,
    )