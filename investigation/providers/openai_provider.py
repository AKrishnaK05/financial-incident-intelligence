"""Optional OpenAI investigation provider."""

import os

from openai import OpenAI

from investigation.agent_context import AgentContext
from investigation.agent_prompt import build_investigation_prompt
from investigation.agent_schema import AgentOutput, convert_agent_output
from investigation.investigation_models import AgentResponse
from investigation.llm_interface import InvestigationLLM


class OpenAIInvestigationAgent(InvestigationLLM):
    """Investigation agent backed by an OpenAI Responses API model."""

    provider = "openai"

    def __init__(self, model: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def investigate(self, context: AgentContext) -> AgentResponse:
        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Investigate the supplied financial incident using only the evidence. "
                "Never invent financial facts. Return the required JSON schema."
            ),
            input=build_investigation_prompt(context),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "financial_incident_investigation",
                    "strict": True,
                    "schema": AgentOutput.model_json_schema(),
                }
            },
        )
        output = AgentOutput.model_validate_json(response.output_text)
        narrative = convert_agent_output(output, context.reasoning)
        return AgentResponse(
            narrative=narrative,
            provider=self.provider,
            model=self.model,
        )
