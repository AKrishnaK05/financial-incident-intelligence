"""
Investigation service for Financial Incident Intelligence.

This module orchestrates the deterministic investigation pipeline
and the AI investigation provider.

The service does not generate financial truth itself. It coordinates
the existing detection, evidence, reasoning, reporting, governance,
and validation components.
"""

from dataclasses import dataclass

from governance.action_policy import (
    ActionRecommendation,
    recommend_action,
)
from incidents.detector import IncidentCandidate
from investigation.agent_context import (
    AgentContext,
    build_agent_context,
)
from investigation.agent_factory import (
    create_investigation_agent,
)
from investigation.agent_validator import (
    validate_investigation_narrative,
)
from investigation.blast_radius import (
    BlastRadius,
    analyze_blast_radius,
)
from investigation.evidence import (
    IncidentEvidence,
    collect_incident_evidence,
)
from investigation.exposure import (
    FinancialExposure,
    calculate_financial_exposure,
)
from investigation.hypothesis_engine import (
    Hypothesis,
    evaluate_hypotheses,
)
from investigation.incident_correlator import (
    IncidentCluster,
)
from investigation.incident_report import (
    IncidentReport,
    build_incident_report,
)
from investigation.reasoning import (
    ReasoningAssessment,
)
from investigation.timeline import (
    TimelineFacts,
    analyze_timeline,
)
from investigation.investigation_models import (
    AgentResponse,
)
from investigation.state_graph import (
    FinancialStateGraph,
)


@dataclass
class InvestigationResult:
    """
    Complete result of investigating one incident.

    This object contains both deterministic investigation outputs
    and the validated AI-generated narrative.
    """

    incident: IncidentCandidate
    evidence: IncidentEvidence
    timeline: TimelineFacts
    hypotheses: list[Hypothesis]
    reasoning: ReasoningAssessment
    blast_radius: BlastRadius
    financial_exposure: FinancialExposure
    report: IncidentReport
    recommendation: ActionRecommendation
    agent_context: AgentContext
    agent_response: AgentResponse


class InvestigationService:
    """
    Orchestrates investigation of financial incidents.
    """

    def __init__(self) -> None:
        self.agent = create_investigation_agent()

    def investigate(
        self,
        incident: IncidentCandidate,
        graph: FinancialStateGraph,
        all_incidents: list[IncidentCandidate],
        evidence_map: dict[str, IncidentEvidence],
        timeline_map: dict[str, TimelineFacts],
        cluster: IncidentCluster | None = None,
    ) -> InvestigationResult:
        """
        Investigate one incident using the established
        deterministic investigation pipeline.
        """

        evidence = collect_incident_evidence(
            incident,
            graph,
        )

        timeline = analyze_timeline(
            evidence,
        )

        hypotheses = evaluate_hypotheses(
            evidence,
            timeline,
        )

        reasoning = self._build_reasoning(
            hypotheses,
        )

        blast_radius = analyze_blast_radius(
            all_incidents,
            graph,
        )

        financial_exposure = calculate_financial_exposure(
            all_incidents,
        )

        report = build_incident_report(
            incident=incident,
            evidence=evidence,
            timeline=timeline,
            hypotheses=hypotheses,
            blast_radius=blast_radius,
            financial_exposure=financial_exposure,
            cluster=cluster,
        )

        recommendation = recommend_action(
            report,
        )

        agent_context = build_agent_context(
            report=report,
            evidence=evidence,
            timeline=timeline,
            hypotheses=hypotheses,
            reasoning=reasoning,
            recommendation=recommendation,
        )

        agent_response = self.agent.investigate(
            agent_context,
        )

        validate_investigation_narrative(
            agent_response.narrative,
            agent_context,
        )

        return InvestigationResult(
            incident=incident,
            evidence=evidence,
            timeline=timeline,
            hypotheses=hypotheses,
            reasoning=reasoning,
            blast_radius=blast_radius,
            financial_exposure=financial_exposure,
            report=report,
            recommendation=recommendation,
            agent_context=agent_context,
            agent_response=agent_response,
        )

    @staticmethod
    def _build_reasoning(
        hypotheses: list[Hypothesis],
    ) -> ReasoningAssessment:
        """
        Build the deterministic reasoning assessment.

        This method exists as a small orchestration wrapper so the
        service owns the investigation flow without duplicating
        reasoning logic.
        """

        from investigation.reasoning import (
            build_reasoning_assessment,
        )

        return build_reasoning_assessment(
            hypotheses,
        )