"""
Incident correlation for Financial Incident Intelligence.

This module groups detected incidents that share a common
financial, temporal, and entity signature.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from incidents.detector import IncidentCandidate
from investigation.evidence import IncidentEvidence
from investigation.timeline import TimelineFacts


CORRELATION_TIME_WINDOW = timedelta(minutes=30)


@dataclass
class IncidentCluster:
    """
    Represents a group of potentially related incidents.
    """

    cluster_id: str
    mechanism: str
    incidents: list[IncidentCandidate] = field(
        default_factory=list
    )
    affected_merchants: set[str] = field(
        default_factory=set
    )
    first_affected_at: datetime | None = None
    last_affected_at: datetime | None = None
    correlation_reasons: list[str] = field(
        default_factory=list
    )
    scope: str = "ISOLATED"
    scope_reason: str = ""

def classify_cluster_scope(
    cluster: IncidentCluster,
) -> tuple[str, str]:
    """
    Classify the operational scope of an incident cluster
    and explain the classification.
    """

    payment_count = len(cluster.incidents)
    merchant_count = len(cluster.affected_merchants)

    if payment_count >= 5 and merchant_count >= 2:
        return (
            "SYSTEMIC",
            f"{payment_count} incidents across "
            f"{merchant_count} merchants share the same "
            f"failure mechanism.",
        )

    if payment_count >= 2:
        return (
            "CLUSTERED",
            f"{payment_count} incidents share the same "
            f"failure mechanism.",
        )

    return (
        "ISOLATED",
        "Only one incident was associated with this mechanism.",
    )


def identify_mechanism(
    incident: IncidentCandidate,
    evidence: IncidentEvidence,
    timeline: TimelineFacts,
) -> tuple[str, str]:
    """
    Identify the observed failure mechanism signature.

    Returns
    -------
    tuple[str, str]
        Mechanism name and correlation reason.
    """

    refund_amount = sum(
        refund.amount
        for refund in evidence.refunds
        if refund.processed_at
        <= evidence.settlement.cutoff_at
    )

    variance_amount = abs(
        incident.variance_amount
    )

    if (
        refund_amount == variance_amount
        and timeline.refund_processed_before_cutoff
        and not timeline.webhook_delivered_before_cutoff
    ):
        return (
            "REFUND_EVENT_LATENCY",
            "Refund amount matches variance and "
            "refund webhook arrived after cutoff.",
        )

    return (
        "OTHER",
        "Incident does not match a known failure signature.",
    )


def correlate_incidents(
    incidents: list[IncidentCandidate],
    evidence_map: dict[str, IncidentEvidence],
    timeline_map: dict[str, TimelineFacts],
) -> list[IncidentCluster]:
    """
    Group incidents using mechanism and temporal continuity.
    """

    clusters: list[IncidentCluster] = []

    sorted_incidents = sorted(
        incidents,
        key=lambda incident: (
            evidence_map[incident.incident_id]
            .payment.captured_at
        ),
    )

    for incident in sorted_incidents:
        evidence = evidence_map.get(
            incident.incident_id
        )

        timeline = timeline_map.get(
            incident.incident_id
        )

        if evidence is None or timeline is None:
            continue

        mechanism, reason = identify_mechanism(
            incident,
            evidence,
            timeline,
        )

        incident_time = evidence.payment.captured_at

        matching_cluster = None

        for cluster in clusters:
            if cluster.mechanism != mechanism:
                continue

            if cluster.last_affected_at is None:
                continue

            time_gap = (
                incident_time
                - cluster.last_affected_at
            )

            if time_gap <= CORRELATION_TIME_WINDOW:
                matching_cluster = cluster
                break

        if matching_cluster is None:
            matching_cluster = IncidentCluster(
                cluster_id=f"CLUSTER_{len(clusters) + 1:03d}",
                mechanism=mechanism,
            )

            clusters.append(matching_cluster)

        matching_cluster.incidents.append(
            incident
        )

        matching_cluster.affected_merchants.add(
            evidence.payment.merchant_id
        )

        if (
            matching_cluster.first_affected_at is None
            or incident_time
            < matching_cluster.first_affected_at
        ):
            matching_cluster.first_affected_at = (
                incident_time
            )

        if (
            matching_cluster.last_affected_at is None
            or incident_time
            > matching_cluster.last_affected_at
        ):
            matching_cluster.last_affected_at = (
                incident_time
            )

        if reason not in matching_cluster.correlation_reasons:
            matching_cluster.correlation_reasons.append(
                reason
            )

    for cluster in clusters:
        scope, scope_reason = classify_cluster_scope(cluster)

        cluster.scope = scope
        cluster.scope_reason = scope_reason

    return clusters 