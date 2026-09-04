"""
LLM interface for Financial Incident Intelligence.

This module defines the contract and common response object
for language-model implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from investigation.agent import InvestigationNarrative
from investigation.agent_context import AgentContext


@dataclass
class AgentResponse:
    """
    Response returned by an investigation language model.
    """

    narrative: InvestigationNarrative
    provider: str
    model: str


class InvestigationLLM(ABC):
    """
    Abstract interface for an investigation language model.
    """

    @abstractmethod
    def investigate(
        self,
        context: AgentContext,
    ) -> AgentResponse:
        """
        Generate an investigation response from curated context.
        """
        raise NotImplementedError