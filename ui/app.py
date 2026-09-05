"""Streamlit command center for Financial Incident Intelligence."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from governance.approval import (
    resolve_approval_request,
    review_approval_request,
)
from pipeline import investigate_report, run_pipeline  # noqa: E402


st.set_page_config(
    page_title="Financial Incident Intelligence",
    page_icon="💳",
    layout="wide",
)

st.title("Financial Incident Intelligence")
st.caption(
    "From settlement exception → causal investigation → blast radius → governed response."
)

with st.sidebar:
    st.header("Simulation")
    base_payment_count = st.number_input(
        "Base payments (30+)" ,
        min_value=30,
        max_value=5000,
        value=30,
        step=10,
        help="Synthetic non-incident payments. Controlled hero/systemic incidents are added separately.",
    )
    random_seed = st.number_input("Random seed", value=42, step=1)
    run_clicked = st.button("Run investigation pipeline", type="primary", use_container_width=True)

if "resolved_incidents" not in st.session_state:
    st.session_state.resolved_incidents = set()

if "result" not in st.session_state or run_clicked:
    with st.spinner("Building financial state and detecting incidents..."):
        st.session_state.result = run_pipeline(
            base_payment_count=int(base_payment_count),
            random_seed=int(random_seed),
        )
    st.session_state.resolved_incidents = set()
    st.session_state.pop("ai_responses", None)

result = st.session_state.result

# ---------------------------------------------------------------------------
# Executive metrics
# ---------------------------------------------------------------------------

total = len(result.state_graph.settlements)
exceptions = len(result.detected_incidents)

resolved_count = sum(
    1
    for incident in result.detected_incidents
    if incident.incident_id in st.session_state.resolved_incidents
)

unresolved_count = exceptions - resolved_count
matched = total - exceptions
match_rate = matched / total * 100 if total else 0.0

st.subheader("Finance operations overview")
cols = st.columns(7)
cols[0].metric("Records", f"{total:,}")
cols[1].metric("Matched", f"{matched:,}")
cols[2].metric("Exceptions", f"{exceptions:,}")
cols[3].metric("Match rate", f"{match_rate:.2f}%")
cols[4].metric("Unresolved", f"{unresolved_count:,}")
cols[5].metric("Gross variance", f"₹{result.financial_exposure.gross_variance:,}")
cols[6].metric("Affected payments", f"{result.financial_exposure.affected_payment_count:,}")

st.info(
    f"Finance-ops loop: {total:,} records processed → {matched:,} matched → "
    f"{exceptions:,} exceptions investigated ({resolved_count:,} resolved, {unresolved_count:,} unresolved). "
    "Exceptions require governed human review; no financial remediation is executed automatically."
)

# ---------------------------------------------------------------------------
# Incident clusters
# ---------------------------------------------------------------------------

if result.clusters:
    st.subheader("Correlated incident clusters")
    cluster_rows = [
        {
            "Cluster": cluster.cluster_id,
            "Mechanism": cluster.mechanism,
            "Scope": cluster.scope,
            "Incidents": len(cluster.incidents),
            "Merchants": len(cluster.affected_merchants),
            "Window": f"{cluster.first_affected_at} → {cluster.last_affected_at}",
        }
        for cluster in result.clusters
    ]
    st.dataframe(pd.DataFrame(cluster_rows), use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Incident queue
# ---------------------------------------------------------------------------

st.subheader("Incident queue")
st.caption(
    "Exceptions requiring human review are shown explicitly; no financial remediation is executed automatically."
)
incident_rows = []
for incident in result.detected_incidents:
    report = result.report_by_payment(incident.payment_id)
    cluster = result.cluster_map.get(incident.incident_id)
    recommendation = result.action_recommendations[incident.incident_id]
    reasoning = result.reasoning_map[incident.incident_id]
    status = (
        "RESOLVED"
        if incident.incident_id in st.session_state.resolved_incidents
        else (
            result.approval_requests[incident.incident_id].status
            if incident.incident_id in result.approval_requests
            else "UNRESOLVED"
        )
    )
    incident_rows.append(
        {
            "Incident": incident.incident_id,
            "Payment": incident.payment_id,
            "Variance (₹)": abs(incident.variance_amount),
            "Severity": incident.severity,
            "Root-cause mechanism": reasoning.primary_hypothesis or "UNRESOLVED",
            "Score": reasoning.primary_score,
            "Margin": reasoning.evidence_margin,
            "Scope": cluster.scope if cluster else "ISOLATED",
            "Action": recommendation.action,
            "Status": status,
        }
    )

st.dataframe(
    pd.DataFrame(incident_rows),
    use_container_width=True,
    hide_index=True,
    height=320,
)

# ---------------------------------------------------------------------------
# Drill-down
# ---------------------------------------------------------------------------

incident_ids = [item.incident_id for item in result.detected_incidents]
if not incident_ids:
    st.info("No financial incidents were detected in this run.")
    st.stop()

default_index = 0
if result.hero_report and result.hero_report.incident_id in incident_ids:
    default_index = incident_ids.index(result.hero_report.incident_id)

selected_id = st.selectbox("Open incident", incident_ids, index=default_index)
report = next(item for item in result.incident_reports if item.incident_id == selected_id)
evidence = result.evidence_map[selected_id]
timeline = result.timeline_map[selected_id]
hypotheses = result.hypotheses_map[selected_id]
reasoning = result.reasoning_map[selected_id]
recommendation = result.action_recommendations[selected_id]
approval = result.approval_requests.get(selected_id)

st.divider()
left, right = st.columns([3, 2])

with left:
    st.subheader(f"{report.incident_id} — {report.severity}")
    st.write(
        f"**Payment:** `{report.payment_id}` · **Settlement:** `{report.settlement_id}`"
    )
    a, b, c = st.columns(3)
    a.metric("Expected", f"₹{report.expected_amount:,}")
    b.metric("Observed", f"₹{report.observed_amount:,}")
    c.metric("Variance", f"₹{abs(report.variance_amount):,}")

    st.markdown("#### Event timeline")
    st.write(
        {
            "Refund processed before cutoff": timeline.refund_processed_before_cutoff,
            "Webhook delivered before cutoff": timeline.webhook_delivered_before_cutoff,
            "Webhook delivery delay": str(timeline.webhook_delivery_delay),
            "Refund → webhook delay": str(timeline.refund_to_webhook_delay),
        }
    )

    st.markdown("#### Evidence")
    for refund in evidence.refunds:
        st.markdown(
            f"- **Refund `{refund.refund_id}`** — ₹{refund.amount:,} — "
            f"processed `{refund.processed_at}`"
        )
    for event in evidence.webhook_events:
        st.markdown(
            f"- **Event `{event.event_id}`** — `{event.event_type}` — "
            f"delivered `{event.delivered_at}`"
        )

    st.markdown("#### Competing hypotheses")
    for hypothesis in hypotheses:
        assessment = next(
            item for item in reasoning.assessments
            if item.hypothesis_name == hypothesis.name
        )
        with st.expander(
            f"{hypothesis.name} · {hypothesis.status} · score {assessment.evidence_score}"
        ):
            st.markdown("**Supporting evidence**")
            for item in hypothesis.supporting_evidence:
                st.markdown(f"- {item}")
            st.markdown("**Contradicting evidence**")
            for item in hypothesis.contradicting_evidence:
                st.markdown(f"- {item}")

with right:
    st.subheader("Deterministic reasoning")
    st.metric("Primary mechanism", reasoning.primary_hypothesis or "UNRESOLVED")
    r1, r2 = st.columns(2)
    r1.metric("Evidence score", reasoning.primary_score)
    r2.metric("Evidence margin", reasoning.evidence_margin)

    st.markdown("#### Blast radius")
    st.write(
        {
            "Affected payments": report.blast_radius.affected_payment_count,
            "Affected merchants": report.blast_radius.affected_merchant_count,
            "Payment methods": report.blast_radius.affected_payment_methods,
            "Cluster": report.cluster_id,
            "Scope": report.cluster_scope,
        }
    )

    st.markdown("#### Governance")
    st.markdown(f"**{recommendation.action}** · {recommendation.priority}")
    st.caption(recommendation.reason)
    if approval:
        if approval.status == "PENDING_APPROVAL":
            st.warning(
                f"Human approval required · `{approval.request_id}` · {approval.status}"
            )
            reviewer = st.text_input(
                "Reviewer",
                key=f"reviewer_{selected_id}",
                value="Finance Ops",
            )
            decision_reason = st.text_input(
                "Decision reason",
                key=f"reason_{selected_id}",
                value="Approved based on verified telemetry evidence.",
            )
            if st.button(
                "Approve recommendation",
                key=f"approve_{selected_id}",
                use_container_width=True,
            ):
                review_approval_request(
                    approval,
                    approved=True,
                    reviewer=reviewer.strip() or "Finance Ops",
                    reason=decision_reason.strip() or "Approved",
                )
                st.rerun()

        elif approval.status == "APPROVED":
            st.success(
                f"Approval `{approval.request_id}` · **APPROVED** · "
                f"Reviewer: {approval.reviewer or '—'}"
            )

            if approval.decision_reason:
                st.caption(
                    f"Approval reason: {approval.decision_reason}"
                )

            if selected_id not in st.session_state.resolved_incidents:

                st.markdown("##### Close exception")

                st.caption(
                    "Approval authorizes the recommended finance-ops follow-up. "
                    "Closing below records a simulated resolution; it does not move money."
                )

                resolver = st.text_input(
                    "Resolver",
                    key=f"resolver_{selected_id}",
                    value=approval.reviewer or "",
                    placeholder="e.g. Finance Ops",
                )

                resolution_note = st.text_area(
                    "Resolution note",
                    key=f"resolution_note_{selected_id}",
                    placeholder=(
                        "e.g. Exception reviewed and remediation workflow completed."
                    ),
                )

                if st.button(
                    "Resolve exception",
                    key=f"resolve_{selected_id}",
                    type="primary",
                    use_container_width=True,
                ):
                    if not resolver.strip() or not resolution_note.strip():
                        st.error(
                            "Resolver and resolution note are required."
                        )
                    else:
                        resolve_approval_request(
                            approval,
                            resolver=resolver.strip(),
                            note=resolution_note.strip(),
                        )

                        st.session_state.resolved_incidents.add(
                            selected_id
                        )

                        st.success(
                            "Exception resolved. The demo records closure "
                            "without executing a real financial action."
                        )

                        st.rerun()

            else:
                st.success(
                    f"Exception **RESOLVED** · "
                    f"Resolver: {approval.resolver or '—'}"
                )

                if approval.resolution_note:
                    st.caption(
                        f"Resolution note: {approval.resolution_note}"
                    )

        elif approval.status == "RESOLVED":
            st.success(
                f"Exception **RESOLVED** · "
                f"Resolver: {approval.resolver or '—'}"
            )

            if approval.resolution_note:
                st.caption(
                    f"Resolution note: {approval.resolution_note}"
                )

    st.markdown("#### AI investigation")
    if "ai_responses" not in st.session_state:
        st.session_state.ai_responses = {}

    if st.button("Investigate with AI", key=f"ai_{selected_id}", use_container_width=True):
        with st.spinner("Gemini is investigating the curated evidence..."):
            try:
                st.session_state.ai_responses[selected_id] = investigate_report(result, report)
            except Exception as error:  # noqa: BLE001
                st.error(f"AI investigation failed: {error}")

    response = st.session_state.ai_responses.get(selected_id)
    if response:
        narrative = response.narrative
        st.success(f"{response.provider} · {response.model}")
        st.write(narrative.summary)
        st.markdown(f"**Root cause:** `{narrative.root_cause}`")
        st.markdown(f"**Confidence:** **{narrative.confidence}**")
        if narrative.recommended_action:
            st.markdown(f"**Recommended action:** `{narrative.recommended_action}`")
        st.markdown("**Remaining uncertainty**")
        for item in narrative.uncertainty:
            st.markdown(f"- {item}")
