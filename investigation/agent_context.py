"""
Curated investigation context for Financial Incident Intelligence.

This module defines the information that may be provided to
the AI investigation agent.

The agent receives established facts rather than unrestricted
access to the financial state graph.
"""

from dataclasses import dataclass

from governance.action_policy import ActionRecommendation
from investigation.evidence import IncidentEvidence
from investigation.hypothesis_engine import Hypothesis
from investigation.incident_report import IncidentReport
from investigation.timeline import TimelineFacts


@dataclass
class AgentContext:
    """
    Curated context supplied to the investigation agent.
    """

    report: IncidentReport
    evidence: IncidentEvidence
    timeline: TimelineFacts
    hypotheses: list[Hypothesis]
    recommendation: ActionRecommendation

def build_agent_context(
    report: IncidentReport,
    evidence: IncidentEvidence,
    timeline: TimelineFacts,
    hypotheses: list[Hypothesis],
    recommendation: ActionRecommendation,
) -> AgentContext:
    """
    Build the curated context provided to the AI investigator.
    """

    if report.incident_id != evidence.incident_id:
        raise ValueError(
            "Incident report and evidence refer to different incidents."
        )

    if report.incident_id != timeline.incident_id:
        raise ValueError(
            "Incident report and timeline refer to different incidents."
        )

    return AgentContext(
        report=report,
        evidence=evidence,
        timeline=timeline,
        hypotheses=hypotheses,
        recommendation=recommendation,
    )