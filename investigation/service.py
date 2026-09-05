"""Application service for AI-assisted financial investigation."""

from investigation.agent_context import build_agent_context
from investigation.agent_factory import create_investigation_agent
from investigation.agent_validator import validate_investigation_narrative
from investigation.evidence import IncidentEvidence
from investigation.hypothesis_engine import Hypothesis
from investigation.incident_report import IncidentReport
from investigation.investigation_models import AgentResponse
from investigation.reasoning import ReasoningAssessment
from investigation.timeline import TimelineFacts
from governance.action_policy import ActionRecommendation


class InvestigationService:
    """Run one validated AI investigation over established facts."""

    def __init__(self, agent=None) -> None:
        self.agent = agent or create_investigation_agent()

    def investigate(
        self,
        report: IncidentReport,
        evidence: IncidentEvidence,
        timeline: TimelineFacts,
        hypotheses: list[Hypothesis],
        reasoning: ReasoningAssessment,
        recommendation: ActionRecommendation,
    ) -> AgentResponse:
        """Build curated context, call the provider, then validate it."""

        context = build_agent_context(
            report=report,
            evidence=evidence,
            timeline=timeline,
            hypotheses=hypotheses,
            reasoning=reasoning,
            recommendation=recommendation,
        )

        response = self.agent.investigate(context)

        validate_investigation_narrative(
            response.narrative,
            context,
        )

        return response
