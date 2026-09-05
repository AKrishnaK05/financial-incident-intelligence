"""
Approval workflow for Financial Incident Intelligence.

This module models human approval of an operational recommendation.

It does not execute financial actions.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from governance.action_policy import ActionRecommendation


@dataclass
class ApprovalRequest:
    """
    Represents a human approval request for a recommended action.
    """

    request_id: str
    incident_id: str
    action: str
    priority: str
    status: str
    requested_at: datetime
    reviewed_at: datetime | None = None
    reviewer: str | None = None
    decision_reason: str | None = None
    resolved_at: datetime | None = None
    resolver: str | None = None
    resolution_note: str | None = None

def create_approval_request(
    incident_id: str,
    recommendation: ActionRecommendation,
    request_number: int,
) -> ApprovalRequest:
    """
    Create a pending approval request for a recommendation.
    """

    return ApprovalRequest(
        request_id=f"APR_{request_number:06d}",
        incident_id=incident_id,
        action=recommendation.action,
        priority=recommendation.priority,
        status="PENDING_APPROVAL",
        requested_at=datetime.now(timezone.utc),
    )

def review_approval_request(
    request: ApprovalRequest,
    approved: bool,
    reviewer: str,
    reason: str,
) -> ApprovalRequest:
    """
    Record a human decision on an approval request.

    This function only changes governance state.
    It does not execute the recommended action.
    """

    if request.status != "PENDING_APPROVAL":
        raise ValueError(
            "Only pending approval requests can be reviewed."
        )

    request.status = (
        "APPROVED"
        if approved
        else "REJECTED"
    )

    request.reviewed_at = datetime.now(timezone.utc)
    request.reviewer = reviewer
    request.decision_reason = reason

    return request


def resolve_approval_request(
    request: ApprovalRequest,
    resolver: str,
    note: str,
) -> ApprovalRequest:
    """
    Close an approved finance-ops exception in the demo workflow.

    Resolution is simulated: this changes workflow state but does not move
    money, alter a real settlement, or execute an external financial action.
    """

    if request.status != "APPROVED":
        raise ValueError(
            "Only approved requests can be resolved."
        )

    request.status = "RESOLVED"
    request.resolved_at = datetime.now(timezone.utc)
    request.resolver = resolver
    request.resolution_note = note

    return request

