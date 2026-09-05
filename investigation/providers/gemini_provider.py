"""
Gemini investigation provider for Financial Incident Intelligence.

This module connects the investigation system to a Gemini model.

The provider is responsible only for model interaction.
Financial validation and governance remain outside the provider.
"""

import os

from google import genai
from google.genai import types

from investigation.agent_context import AgentContext
from investigation.agent_prompt import build_investigation_prompt
from investigation.agent_schema import (
    AgentOutput,
    convert_agent_output,
)
from investigation.investigation_models import AgentResponse
from investigation.llm_interface import InvestigationLLM


class GeminiInvestigationAgent(InvestigationLLM):
    """
    Investigation agent backed by Gemini.
    """

    provider = "gemini"

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
    ):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

    def investigate(
        self,
        context: AgentContext,
    ) -> AgentResponse:
        """
        Send curated investigation context to Gemini
        and receive a structured investigation response.
        """

        prompt = build_investigation_prompt(
            context
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AgentOutput,
            ),
        )

        output = AgentOutput.model_validate_json(
            response.text
        )

        narrative = convert_agent_output(
            output
        )

        narrative.reasoning = context.reasoning


        return AgentResponse(
            narrative=narrative,
            provider=self.provider,
            model=self.model,
        )