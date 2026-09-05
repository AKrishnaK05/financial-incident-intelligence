"""FastAPI interface for Financial Incident Intelligence.

The API keeps the latest deterministic pipeline result in memory. It is
intentionally small for a buildathon demo: no database, authentication,
or external queue is required.
"""

from dataclasses import is_dataclass
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from evaluation.evaluate import evaluate, report_to_dict
from pipeline import PipelineResult, investigate_report, run_pipeline
from governance.approval import review_approval_request


app = FastAPI(
    title="Financial Incident Intelligence API",
    description=(
        "Evidence-backed financial incident investigation with deterministic "
        "financial truth, AI-assisted explanation, and human-governed action."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_last_result: PipelineResult | None = None


class ApprovalDecision(BaseModel):
    """Human decision submitted for an approval request."""

    approved: bool
    reviewer: str = Field(min_length=1, max_length=100)
    reason: str = Field(min_length=1, max_length=500)


def _json_safe(value):
    """Convert project dataclasses and temporal values into JSON-safe data."""

    if is_dataclass(value) and not isinstance(value, type):
        return {
            name: _json_safe(getattr(value, name))
            for name in value.__dataclass_fields__
        }
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (datetime, timedelta)):
        return str(value)
    return value


def _require_result() -> PipelineResult:
    if _last_result is None:
        raise HTTPException(
            status_code=409,
            detail="No pipeline run yet. Call POST /run first.",
        )
    return _last_result


def _find_report(result: PipelineResult, incident_id: str):
    report = next(
        (item for item in result.incident_reports if item.incident_id == incident_id),
        None,
    )
    if report is None:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return report


def _incident_summary(result: PipelineResult) -> list[dict]:
    summaries = []
    for incident in result.detected_incidents:
        report = result.report_by_payment(incident.payment_id)
        recommendation = result.action_recommendations.get(incident.incident_id)
        cluster = result.cluster_map.get(incident.incident_id)
        summaries.append(
            {
                "incident_id": incident.incident_id,
                "payment_id": incident.payment_id,
                "settlement_id": incident.settlement_id,
                "variance_amount": incident.variance_amount,
                "severity": incident.severity,
                "primary_hypothesis": (
                    report.primary_hypothesis.name
                    if report and report.primary_hypothesis
                    else None
                ),
                "cluster_scope": cluster.scope if cluster else "ISOLATED",
                "recommended_action": (
                    recommendation.action if recommendation else None
                ),
                "resolution_status": "UNRESOLVED",
            }
        )
    return summaries


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run")
def run(base_payment_count: int = 30, random_seed: int = 42):
    """Generate a deterministic synthetic batch and investigate its exceptions."""

    global _last_result
    if base_payment_count < 30 or base_payment_count > 50000:
        raise HTTPException(status_code=400, detail="base_payment_count must be 30..50000 so the default finance-controller run always contains 50+ records")

    _last_result = run_pipeline(
        base_payment_count=base_payment_count,
        random_seed=random_seed,
    )
    result = _last_result

    total = len(result.state_graph.settlements)
    exceptions = len(result.detected_incidents)
    matched = total - exceptions

    return {
        "batch_summary": {
            "records_processed": total,
            "matched": matched,
            "exceptions": exceptions,
            "match_rate_percent": round(matched / total * 100, 2) if total else 0.0,
            "gross_variance": result.financial_exposure.gross_variance,
            "unresolved_exposure": result.financial_exposure.unresolved_exposure,
            "affected_payments": result.financial_exposure.affected_payment_count,
            "resolved_exceptions": 0,
            "unresolved_exceptions": exceptions,
            "loop_status": "INVESTIGATED_PENDING_HUMAN_REVIEW",
            "financial_remediation_executed": False,
        },
        "clusters": [
            {
                "cluster_id": cluster.cluster_id,
                "mechanism": cluster.mechanism,
                "scope": cluster.scope,
                "scope_reason": cluster.scope_reason,
                "incident_count": len(cluster.incidents),
                "affected_merchants": len(cluster.affected_merchants),
            }
            for cluster in result.clusters
        ],
        "incidents": _incident_summary(result),
        "hero_incident_id": result.hero_report.incident_id if result.hero_report else None,
    }


@app.get("/evaluation")
def evaluation():
    """Return deterministic benchmark metrics for the latest run."""
    result = _require_result()
    return report_to_dict(evaluate(result))


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    """Return deterministic investigation detail for one incident."""
    result = _require_result()
    report = _find_report(result, incident_id)
    return {
        "report": _json_safe(report),
        "reasoning": _json_safe(result.reasoning_map[incident_id]),
        "recommendation": _json_safe(result.action_recommendations.get(incident_id)),
        "approval": _json_safe(result.approval_requests.get(incident_id)),
    }


@app.post("/incidents/{incident_id}/investigate")
def investigate(incident_id: str):
    """Run the configured AI investigator and validate its output."""
    result = _require_result()
    report = _find_report(result, incident_id)

    try:
        response = investigate_report(result, report)
    except Exception as error:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(error)) from error

    return {
        "provider": response.provider,
        "model": response.model,
        "narrative": _json_safe(response.narrative),
    }


@app.post("/incidents/{incident_id}/approval")
def decide_approval(incident_id: str, decision: ApprovalDecision):
    """Record an explicit human approval/rejection for a recommendation."""
    result = _require_result()
    _find_report(result, incident_id)

    request = result.approval_requests.get(incident_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Approval request not found.")

    try:
        updated = review_approval_request(
            request,
            approved=decision.approved,
            reviewer=decision.reviewer,
            reason=decision.reason,
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    return _json_safe(updated)
