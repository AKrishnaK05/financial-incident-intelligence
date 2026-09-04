"""
Investigation report for Financial Incident Intelligence.

This module aggregates deterministic investigation outputs into
a single structured incident report.

It does not calculate financial truth, determine root cause,
or modify any financial state.
"""

from dataclasses import dataclass

from incidents.detector import IncidentCandidate
from investigation.blast_radius import BlastRadius
from investigation.evidence import IncidentEvidence
from investigation.hypothesis_engine import Hypothesis
from investigation.incident_correlator import IncidentCluster
from investigation.timeline import TimelineFacts
from investigation.exposure import FinancialExposure

@dataclass
class IncidentReport:
    """
    Structured investigation result for a financial incident.
    """

    incident_id: str
    payment_id: str
    settlement_id: str

    expected_amount: int
    observed_amount: int
    variance_amount: int
    severity: str

    hypotheses: list[Hypothesis]

    timeline: TimelineFacts

    blast_radius: BlastRadius
    financial_exposure: FinancialExposure

    cluster_id: str | None
    cluster_scope: str | None
    cluster_mechanism: str | None

    @property
    def primary_hypothesis(self) -> Hypothesis | None:
        """
        Return the highest-confidence supported hypothesis.

        If no hypothesis is supported, return None.
        """

        supported_hypotheses = [
            hypothesis
            for hypothesis in self.hypotheses
            if hypothesis.status == "SUPPORTED"
        ]

        if not supported_hypotheses:
            return None

        confidence_order = {
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
        }

        return max(
            supported_hypotheses,
            key=lambda hypothesis: confidence_order.get(
                hypothesis.confidence,
                0,
            ),
        )

def build_incident_report(
    incident: IncidentCandidate,
    evidence: IncidentEvidence,
    timeline: TimelineFacts,
    hypotheses: list[Hypothesis],
    blast_radius: BlastRadius,
    financial_exposure: FinancialExposure,
    cluster: IncidentCluster | None = None,
) -> IncidentReport:
    """
    Assemble deterministic investigation outputs into one
    structured incident report.

    This function only aggregates existing analysis results.
    It does not recalculate financial values or determine
    a root cause.
    """

    cluster_id = None
    cluster_scope = None
    cluster_mechanism = None

    if cluster is not None:
        cluster_id = cluster.cluster_id
        cluster_scope = cluster.scope
        cluster_mechanism = cluster.mechanism

    return IncidentReport(
        incident_id=incident.incident_id,
        payment_id=incident.payment_id,
        settlement_id=incident.settlement_id,
        expected_amount=incident.expected_amount,
        observed_amount=incident.observed_amount,
        variance_amount=incident.variance_amount,
        severity=incident.severity,
        hypotheses=hypotheses,
        timeline=timeline,
        blast_radius=blast_radius,
        financial_exposure=financial_exposure,
        cluster_id=cluster_id,
        cluster_scope=cluster_scope,
        cluster_mechanism=cluster_mechanism,
    )
