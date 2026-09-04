"""
LLM adapter layer for Financial Incident Intelligence.

This module separates the investigation agent from the
underlying language model implementation.

The mock adapter is deterministic and exists for development
and testing before connecting a real LLM.
"""

from dataclasses import dataclass

from investigation.agent_context import AgentContext
from investigation.agent import InvestigationNarrative
from investigation.llm_interface import (
    AgentResponse,
    InvestigationLLM,
)

class MockInvestigationAgent(InvestigationLLM):
    """
    Deterministic investigation agent used for development.

    This implementation does not call an external LLM.
    """

    provider = "mock"
    model = "deterministic-v1"

    def investigate(
        self,
        context: AgentContext,
    ) -> AgentResponse:
        """
        Generate a deterministic investigation narrative
        from the supplied context.
        """

        primary_hypothesis = (
            context.report.primary_hypothesis
        )

        if primary_hypothesis is None:
            root_cause = None
            confidence = "LOW"

            summary = (
                "A financial discrepancy was detected, "
                "but the available evidence does not "
                "support a specific root-cause hypothesis."
            )

            evidence_summary = []

            uncertainty = [
                "No supported root-cause hypothesis "
                "was established."
            ]

        else:
            root_cause = primary_hypothesis.name
            confidence = primary_hypothesis.confidence

            summary = (
                f"Payment {context.report.payment_id} has "
                f"a financial variance of ₹"
                f"{abs(context.report.variance_amount)}. "
                f"The strongest evidence-backed hypothesis "
                f"is {root_cause}."
            )

            evidence_summary = (
                primary_hypothesis.supporting_evidence
            )

            uncertainty = (
                primary_hypothesis.contradicting_evidence
            )

        narrative = InvestigationNarrative(
            incident_id=context.report.incident_id,
            summary=summary,
            root_cause=root_cause,
            confidence=confidence,
            evidence_summary=evidence_summary,
            uncertainty=uncertainty,
            recommended_action=(
                context.recommendation.action
            ),
        )

        return AgentResponse(
            narrative=narrative,
            provider=self.provider,
            model=self.model,
        )