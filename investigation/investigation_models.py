"""
Internal investigation models for Financial Incident Intelligence.

This module contains application-level objects used to represent
the result of an AI-assisted financial investigation.

These models are independent of any specific LLM provider.
"""

from dataclasses import dataclass

from investigation.reasoning import ReasoningAssessment


@dataclass
class InvestigationNarrative:
    """
    Structured narrative produced by the investigation agent.
    """

    incident_id: str
    summary: str
    root_cause: str | None
    confidence: str
    evidence_summary: list[str]
    uncertainty: list[str]
    recommended_action: str
    reasoning: ReasoningAssessment | None = None


@dataclass
class AgentResponse:
    """
    Complete response returned by an investigation provider.
    """

    narrative: InvestigationNarrative
    provider: str
    model: str