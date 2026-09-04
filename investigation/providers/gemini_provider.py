"""
Gemini investigation provider for Financial Incident Intelligence.

This module connects the investigation system to a Gemini model.

The provider is responsible only for model interaction.
Financial validation and governance remain outside the provider.
"""

import os

from google import genai
from google.genai import types

from investigation.agent import InvestigationNarrative
from investigation.agent_context import AgentContext
from investigation.agent_adapter import AgentResponse
from investigation.agent_prompt import (
    build_investigation_prompt,
)
from investigation.agent_schema import (
    convert_agent_output,
    parse_agent_output,
)
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
        and convert its structured response.
        """

        prompt = build_investigation_prompt(
            context
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        output = parse_agent_output(
            response.text
        )

        narrative = convert_agent_output(
            output
        )

        return AgentResponse(
            narrative=narrative,
            provider=self.provider,
            model=self.model,
        )