"""Factory for selecting the configured investigation provider."""

from configs.settings import AGENT_MODEL, AGENT_PROVIDER
from investigation.agent_adapter import MockInvestigationAgent
from investigation.llm_interface import InvestigationLLM


def create_investigation_agent() -> InvestigationLLM:
    if AGENT_PROVIDER == "mock":
        return MockInvestigationAgent()
    if AGENT_PROVIDER == "gemini":
        from investigation.providers.gemini_provider import GeminiInvestigationAgent
        return GeminiInvestigationAgent(model=AGENT_MODEL)
    if AGENT_PROVIDER == "openai":
        from investigation.providers.openai_provider import OpenAIInvestigationAgent
        return OpenAIInvestigationAgent(model=AGENT_MODEL)
    raise ValueError(f"Unsupported agent provider: {AGENT_PROVIDER}")
