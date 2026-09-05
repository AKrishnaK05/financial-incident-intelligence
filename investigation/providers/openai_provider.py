"""
OpenAI investigation provider for Financial Incident Intelligence.

This module connects the investigation system to an OpenAI model.

The provider is responsible only for model interaction.
Financial validation and governance remain outside the provider.
"""

import os

from openai import OpenAI

from investigation.agent_context import AgentContext
from investigation.agent_prompt import build_investigation_prompt
from investigation.investigation_models import (
    AgentResponse,
    InvestigationNarrative,
)
from investigation.llm_interface import InvestigationLLM
from investigation.agent_schema import (
    AGENT_OUTPUT_SCHEMA,
    convert_agent_output,
    parse_agent_output,
)


class OpenAIInvestigationAgent(InvestigationLLM):
    """
    Investigation agent backed by an OpenAI model.
    """

    provider = "openai"

    def __init__(
        self,
        model: str = "gpt-5.6-luna",
    ):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set."
            )

        self.client = OpenAI(
            api_key=api_key
        )

        self.model = model

    def investigate(
        self,
        context: AgentContext,
    ) -> AgentResponse:
        """
        Send curated investigation context to the model and
        convert its structured response into an InvestigationNarrative.
        """

        prompt = build_investigation_prompt(
            context
        )

        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Investigate the supplied financial incident. "
                "Use only the provided evidence. "
                "Do not invent financial facts. "
                "Return the required structured investigation."
            ),
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "financial_incident_investigation",
                    "strict": True,
                    "schema": AGENT_OUTPUT_SCHEMA,
                }
            },
        )

        output = parse_agent_output(
            response.output_text
        )

        narrative = convert_agent_output(
            output
        )

        return AgentResponse(
            narrative=narrative,
            provider=self.provider,
            model=self.model,
        )

