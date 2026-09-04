"""
Structured output schema for the Financial Incident Intelligence agent.

This module defines the exact shape expected from a language model.
"""
import json

from dataclasses import dataclass


@dataclass
class AgentOutput:
    """
    Raw structured output expected from the model.
    """

    incident_id: str
    summary: str
    root_cause: str | None
    confidence: str
    evidence_summary: list[str]
    uncertainty: list[str]
    recommended_action: str

AGENT_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "incident_id": {
            "type": "string",
        },
        "summary": {
            "type": "string",
        },
        "root_cause": {
            "type": ["string", "null"],
        },
        "confidence": {
            "type": "string",
            "enum": [
                "LOW",
                "MEDIUM",
                "HIGH",
            ],
        },
        "evidence_summary": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "uncertainty": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "recommended_action": {
            "type": "string",
        },
    },
    "required": [
        "incident_id",
        "summary",
        "root_cause",
        "confidence",
        "evidence_summary",
        "uncertainty",
        "recommended_action",
    ],
    "additionalProperties": False,
}

def parse_agent_output(
    output_text: str,
) -> AgentOutput:
    """
    Parse structured JSON returned by the language model.
    """

    try:
        data = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Agent returned invalid JSON."
        ) from exc

    required_fields = {
        "incident_id",
        "summary",
        "root_cause",
        "confidence",
        "evidence_summary",
        "uncertainty",
        "recommended_action",
    }

    missing_fields = (
        required_fields - data.keys()
    )

    if missing_fields:
        raise ValueError(
            "Agent output is missing required fields: "
            f"{sorted(missing_fields)}"
        )

    if not isinstance(
        data["evidence_summary"],
        list,
    ):
        raise ValueError(
            "evidence_summary must be a list."
        )

    if not isinstance(
        data["uncertainty"],
        list,
    ):
        raise ValueError(
            "uncertainty must be a list."
        )

    return AgentOutput(
        incident_id=data["incident_id"],
        summary=data["summary"],
        root_cause=data["root_cause"],
        confidence=data["confidence"],
        evidence_summary=data["evidence_summary"],
        uncertainty=data["uncertainty"],
        recommended_action=data["recommended_action"],
    )

def convert_agent_output(
    output: AgentOutput,
) -> "InvestigationNarrative":
    """
    Convert validated structural output into the domain
    investigation narrative.
    """

    from investigation.agent import InvestigationNarrative

    return InvestigationNarrative(
        incident_id=output.incident_id,
        summary=output.summary,
        root_cause=output.root_cause,
        confidence=output.confidence,
        evidence_summary=output.evidence_summary,
        uncertainty=output.uncertainty,
        recommended_action=output.recommended_action,
    )