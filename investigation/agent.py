"""
AI investigation agent contract for Financial Incident Intelligence.

This module defines the structured output expected from an
AI investigator.

The agent does not modify financial state or execute actions.
"""

from dataclasses import dataclass

from investigation.incident_report import IncidentReport
from governance.action_policy import ActionRecommendation


@dataclass
class InvestigationNarrative:
    """
    Structured explanation produced by the investigation agent.
    """

    incident_id: str
    summary: str
    root_cause: str | None
    confidence: str
    evidence_summary: list[str]
    uncertainty: list[str]
    recommended_action: str