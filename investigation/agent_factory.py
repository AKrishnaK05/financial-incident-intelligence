"""
Factory for selecting the investigation agent implementation.
"""

from configs.settings import (
    AGENT_MODEL,
    AGENT_PROVIDER,
)

from investigation.llm_interface import InvestigationLLM
from investigation.agent_adapter import MockInvestigationAgent


def create_investigation_agent() -> InvestigationLLM:
    """
    Create the configured investigation agent.
    """

    if AGENT_PROVIDER == "mock":
        return MockInvestigationAgent()

    if AGENT_PROVIDER == "openai":
        from investigation.providers.openai_provider import (
            OpenAIInvestigationAgent,
        )

        return OpenAIInvestigationAgent(
            model=AGENT_MODEL
        )

    if AGENT_PROVIDER == "gemini":
        from investigation.providers.gemini_provider import (
            GeminiInvestigationAgent,
        )

        return GeminiInvestigationAgent(
            model=AGENT_MODEL
        )

    raise ValueError(
        f"Unsupported agent provider: "
        f"{AGENT_PROVIDER}"
    )