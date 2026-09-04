"""
Deterministic reasoning engine for Financial Incident Intelligence.

This module compares competing incident hypotheses using
explicit evidence signals.

It does not access ground truth and does not call an LLM.
"""

from dataclasses import dataclass

from investigation.hypothesis_engine import Hypothesis


STATUS_SCORE = {
    "SUPPORTED": 1.0,
    "PLAUSIBLE": 0.5,
    "UNSUPPORTED": 0.0,
}

CONFIDENCE_SCORE = {
    "HIGH": 1.0,
    "MEDIUM": 0.6,
    "LOW": 0.2,
}


@dataclass
class HypothesisAssessment:
    """
    Deterministic assessment of one incident hypothesis.
    """

    hypothesis_name: str
    status: str
    confidence: str
    evidence_score: float
    supporting_evidence_count: int
    contradicting_evidence_count: int


@dataclass
class ReasoningAssessment:
    """
    Overall comparison of competing incident hypotheses.
    """

    primary_hypothesis: str | None
    primary_confidence: str
    primary_score: float
    second_best_score: float
    evidence_margin: float
    assessments: list[HypothesisAssessment]


def calculate_evidence_score(
    hypothesis: Hypothesis,
) -> float:
    """
    Calculate a deterministic evidence score.

    The score is not a probability.

    It represents the relative strength of the evidence
    available for the hypothesis.
    """

    status_score = STATUS_SCORE.get(
        hypothesis.status,
        0.0,
    )

    confidence_score = CONFIDENCE_SCORE.get(
        hypothesis.confidence,
        0.0,
    )

    supporting_count = len(
        hypothesis.supporting_evidence
    )

    contradicting_count = len(
        hypothesis.contradicting_evidence
    )

    total_evidence = (
        supporting_count
        + contradicting_count
    )

    if total_evidence == 0:
        evidence_balance = 0.0
    else:
        evidence_balance = (
            supporting_count
            / total_evidence
        )

    score = (
        0.5 * status_score
        + 0.3 * confidence_score
        + 0.2 * evidence_balance
    )

    return round(score, 3)


def assess_hypothesis(
    hypothesis: Hypothesis,
) -> HypothesisAssessment:
    """
    Convert a hypothesis into a deterministic assessment.
    """

    evidence_score = calculate_evidence_score(
        hypothesis
    )

    return HypothesisAssessment(
        hypothesis_name=hypothesis.name,
        status=hypothesis.status,
        confidence=hypothesis.confidence,
        evidence_score=evidence_score,
        supporting_evidence_count=len(
            hypothesis.supporting_evidence
        ),
        contradicting_evidence_count=len(
            hypothesis.contradicting_evidence
        ),
    )


def build_reasoning_assessment(
    hypotheses: list[Hypothesis],
) -> ReasoningAssessment:
    """
    Compare all supplied hypotheses and determine
    the strongest evidence-backed explanation.
    """

    assessments = [
        assess_hypothesis(hypothesis)
        for hypothesis in hypotheses
    ]

    ranked_assessments = sorted(
        assessments,
        key=lambda assessment: assessment.evidence_score,
        reverse=True,
    )

    if not ranked_assessments:
        return ReasoningAssessment(
            primary_hypothesis=None,
            primary_confidence="LOW",
            primary_score=0.0,
            second_best_score=0.0,
            evidence_margin=0.0,
            assessments=[],
        )

    best = ranked_assessments[0]

    second_best_score = (
        ranked_assessments[1].evidence_score
        if len(ranked_assessments) > 1
        else 0.0
    )

    evidence_margin = round(
        best.evidence_score
        - second_best_score,
        3,
    )

    if best.status != "SUPPORTED":
        primary_hypothesis = None
        primary_confidence = "LOW"
    else:
        primary_hypothesis = best.hypothesis_name
        primary_confidence = best.confidence

    return ReasoningAssessment(
        primary_hypothesis=primary_hypothesis,
        primary_confidence=primary_confidence,
        primary_score=best.evidence_score,
        second_best_score=second_best_score,
        evidence_margin=evidence_margin,
        assessments=ranked_assessments,
    )