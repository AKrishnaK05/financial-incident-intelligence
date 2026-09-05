"""
LLM interface for Financial Incident Intelligence.

This module defines the contract that every investigation
language-model provider must implement.
"""

from abc import ABC, abstractmethod

from investigation.agent_context import AgentContext
from investigation.investigation_models import AgentResponse


class InvestigationLLM(ABC):
    """
    Common interface for investigation LLM providers.
    """

    @abstractmethod
    def investigate(
        self,
        context: AgentContext,
    ) -> AgentResponse:
        """
        Investigate a financial incident using the provider.
        """
        raise NotImplementedError