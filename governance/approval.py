"""Human approval and simulated resolution workflow."""

from dataclasses import dataclass
from datetime import datetime, timezone

from governance.action_policy import ActionRecommendation


@dataclass
class ApprovalRequest:
    """Represents a governed decision for an incident."""

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
    """Create a pending approval request for a recommendation."""
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
    """Record a human approval/rejection. No financial action is executed."""
    if request.status != "PENDING_APPROVAL":
        raise ValueError("Only pending approval requests can be reviewed.")
    if not reviewer.strip() or not reason.strip():
        raise ValueError("Reviewer and decision reason are required.")

    request.status = "APPROVED" if approved else "REJECTED"
    request.reviewed_at = datetime.now(timezone.utc)
    request.reviewer = reviewer.strip()
    request.decision_reason = reason.strip()
    return request


def resolve_approval_request(
    request: ApprovalRequest,
    resolver: str,
    note: str,
) -> ApprovalRequest:
    """Close an approved exception in the simulated finance-ops workflow."""
    if request.status != "APPROVED":
        raise ValueError("Only approved requests can be resolved.")
    if not resolver.strip() or not note.strip():
        raise ValueError("Resolver and resolution note are required.")

    request.status = "RESOLVED"
    request.resolved_at = datetime.now(timezone.utc)
    request.resolver = resolver.strip()
    request.resolution_note = note.strip()
    return request
