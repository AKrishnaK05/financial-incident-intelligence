"""Factory for selecting the configured investigation provider."""

from configs import settings
from investigation.agent_adapter import MockInvestigationAgent
from investigation.llm_interface import InvestigationLLM


def create_investigation_agent() -> InvestigationLLM:
    provider = settings.AGENT_PROVIDER
    model = settings.AGENT_MODEL

    if provider == "mock":
        return MockInvestigationAgent()
    if provider == "gemini":
        from investigation.providers.gemini_provider import GeminiInvestigationAgent

        return GeminiInvestigationAgent(model=model)
    if provider == "openai":
        from investigation.providers.openai_provider import OpenAIInvestigationAgent

        return OpenAIInvestigationAgent(model=model)
    raise ValueError(f"Unsupported agent provider: {provider}")
