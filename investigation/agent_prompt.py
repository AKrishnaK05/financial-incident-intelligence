"""
Prompt construction for the Financial Incident Intelligence agent.

This module converts curated investigation context into an
evidence-constrained prompt for an AI investigator.

It does not perform financial calculations or call an LLM.
"""

from investigation.agent_context import AgentContext


SYSTEM_INSTRUCTIONS = """
You are a financial incident investigation assistant.

Your role is to explain and reason about a financial incident
using ONLY the evidence provided in the investigation context.

Rules:

1. Treat deterministic financial values as authoritative.
2. Never invent amounts, timestamps, transaction IDs,
   merchants, or other financial facts.
3. Clearly distinguish observed facts from inferred causes.
4. Consider all supplied hypotheses before identifying
   the strongest explanation.
5. Do not claim certainty when the evidence is insufficient.
6. Preserve uncertainty and contradictory evidence.
7. Do not create a new financial root cause that is absent
   from the supplied hypotheses.
8. Do not change or reinterpret the supplied financial
   exposure, variance, or blast-radius values.
9. Do not recommend an action outside the supplied
   governance recommendation.
10. The human approval requirement is mandatory and must
    never be bypassed.
"""


def build_investigation_prompt(
    context: AgentContext,
) -> str:
    """
    Build an evidence-constrained investigation prompt.
    """

    report = context.report
    evidence = context.evidence
    timeline = context.timeline
    hypotheses = context.hypotheses
    recommendation = context.recommendation

    refund_lines = []

    for refund in evidence.refunds:
        refund_lines.append(
            (
                f"- {refund.refund_id}: "
                f"₹{refund.amount}, "
                f"processed_at={refund.processed_at}, "
                f"status={refund.status}"
            )
        )

    webhook_lines = []

    for event in evidence.webhook_events:
        webhook_lines.append(
            (
                f"- {event.event_id}: "
                f"type={event.event_type}, "
                f"emitted_at={event.emitted_at}, "
                f"delivered_at={event.delivered_at}, "
                f"status={event.delivery_status}"
            )
        )

    hypothesis_lines = []

    for hypothesis in hypotheses:
        hypothesis_lines.append(
            (
                f"- {hypothesis.name}: "
                f"status={hypothesis.status}, "
                f"confidence={hypothesis.confidence}\n"
                f"  Supporting evidence: "
                f"{hypothesis.supporting_evidence}\n"
                f"  Contradicting evidence: "
                f"{hypothesis.contradicting_evidence}"
            )
        )

    return f"""
{SYSTEM_INSTRUCTIONS}

INVESTIGATION CONTEXT

Incident:
- Incident ID: {report.incident_id}
- Payment ID: {report.payment_id}
- Settlement ID: {report.settlement_id}
- Severity: {report.severity}

Financial state:
- Expected amount: ₹{report.expected_amount}
- Observed amount: ₹{report.observed_amount}
- Variance: ₹{abs(report.variance_amount)}

Payment:
- Amount: ₹{evidence.payment.amount}
- Method: {evidence.payment.method}
- Currency: {evidence.payment.currency}
- Captured at: {evidence.payment.captured_at}

Refunds:
{chr(10).join(refund_lines) if refund_lines else "- None"}

Webhook events:
{chr(10).join(webhook_lines) if webhook_lines else "- None"}

Timeline:
- Refund processed before cutoff:
  {timeline.refund_processed_before_cutoff}
- Webhook delivered before cutoff:
  {timeline.webhook_delivered_before_cutoff}
- Webhook delivery delay:
  {timeline.webhook_delivery_delay}
- Refund-to-webhook delay:
  {timeline.refund_to_webhook_delay}

Investigation hypotheses:
{chr(10).join(hypothesis_lines)}

Blast radius:
- Affected payments:
  {report.blast_radius.affected_payment_count}
- Affected merchants:
  {report.blast_radius.affected_merchant_count}
- Payment methods:
  {report.blast_radius.affected_payment_methods}
- First affected transaction:
  {report.blast_radius.first_affected_at}

Financial exposure:
- Incident count:
  {report.financial_exposure.incident_count}
- Gross variance:
  ₹{report.financial_exposure.gross_variance}
- Unresolved exposure:
  ₹{report.financial_exposure.unresolved_exposure}

Correlation:
- Cluster ID:
  {report.cluster_id}
- Scope:
  {report.cluster_scope}
- Mechanism:
  {report.cluster_mechanism}

Governance recommendation:
- Action:
  {recommendation.action}
- Priority:
  {recommendation.priority}
- Approval required:
  {recommendation.requires_approval}
- Reason:
  {recommendation.reason}

TASK

Produce an investigation narrative containing:

1. A concise summary of what happened.
2. The strongest evidence-backed root-cause hypothesis.
3. The confidence level supported by the evidence.
4. The key evidence supporting that conclusion.
5. Any remaining uncertainty or contradictory evidence.
6. The supplied governance recommendation.

Do not invent information that is not present in this context.
"""