"""Polished Streamlit control center for Financial Incident Intelligence."""

import sys
from datetime import datetime
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from governance.approval import resolve_approval_request, review_approval_request  # noqa: E402
from pipeline import PipelineResult, investigate_report, run_pipeline  # noqa: E402

st.set_page_config(
    page_title="FII · Financial Incident Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Visual System & Design Tokens
# ---------------------------------------------------------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg: #070b14;
    --panel: #0d1526;
    --panel-sub: #111c33;
    --border: #1c2b44;
    --border-hover: #294068;
    --muted: #798ba7;
    --text: #eef4ff;
    --text-heading: #ffffff;
    --purple: #7959ff;
    --blue: #2f8cff;
    --cyan: #35c4ff;
    --green: #24d89a;
    --amber: #ffb13b;
    --red: #ff5469;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

code, kbd, samp, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

.stApp {
    background:
        radial-gradient(circle at 85% -10%, rgba(47, 140, 255, 0.12), transparent 32%),
        radial-gradient(circle at 10% 110%, rgba(121, 89, 255, 0.08), transparent 30%),
        var(--bg);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: rgba(7, 11, 20, 0.85);
    backdrop-filter: blur(12px);
}

[data-testid="stToolbar"] {
    visibility: hidden;
}

.block-container {
    max-width: 1480px !important;
    padding: 24px 36px 64px !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: #080d18 !important;
    border-right: 1px solid #16243a !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 24px 18px !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-heading) !important;
    letter-spacing: -0.025em;
    font-weight: 750 !important;
}

/* Metrics Cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #0e182a, #0a1220);
    border: 1px solid #1a2c46;
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
    transition: transform 0.18s ease, border-color 0.18s ease;
}

[data-testid="stMetric"]:hover {
    border-color: #2b456e;
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

[data-testid="stMetricValue"] {
    color: #f7faff !important;
    font-size: 26px !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
}

/* Streamlit Native Buttons */
.stButton > button {
    border-radius: 10px !important;
    border: 1px solid #243754 !important;
    background: #0e192c !important;
    color: #edf3ff !important;
    min-height: 42px !important;
    font-weight: 650 !important;
    font-size: 13px !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.stButton > button:hover {
    border-color: #7959ff !important;
    color: #ffffff !important;
    background: #14223d !important;
    box-shadow: 0 4px 14px rgba(121, 89, 255, 0.22) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6c46ff, #387aff) !important;
    border-color: #7e5fff !important;
    color: #ffffff !important;
    box-shadow: 0 8px 24px rgba(108, 70, 255, 0.32) !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #7b57ff, #4a8bff) !important;
    box-shadow: 0 10px 28px rgba(108, 70, 255, 0.45) !important;
}

/* Inputs & Dropdowns */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
div[data-testid="stNumberInput"] input,
textarea, input {
    background: #0b1424 !important;
    border-color: #1f314d !important;
    color: #edf3ff !important;
    border-radius: 9px !important;
}

[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"] > div:focus-within,
textarea:focus, input:focus {
    border-color: #387aff !important;
    box-shadow: 0 0 0 1px #387aff !important;
}

/* DataFrame styling */
[data-testid="stDataFrame"] {
    border: 1px solid #1a2b44;
    border-radius: 12px;
    overflow: hidden;
    background: #09101d;
}

hr {
    border-color: #142033 !important;
    margin: 32px 0 !important;
}

/* Custom UI Components */
.fii-brand {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 26px;
    padding-bottom: 20px;
    border-bottom: 1px solid #152236;
}

.fii-mark {
    width: 40px;
    height: 40px;
    display: grid;
    place-items: center;
    border-radius: 11px;
    background: linear-gradient(135deg, #7959ff, #2f8cff);
    color: #fff;
    font-weight: 900;
    font-size: 20px;
    box-shadow: 0 0 20px rgba(121, 89, 255, 0.35);
}

.fii-brand-name {
    font-weight: 850;
    color: #ffffff;
    font-size: 20px;
    line-height: 1.1;
    letter-spacing: -0.02em;
}

.fii-brand-sub {
    color: #7889a3;
    font-size: 11px;
    margin-top: 3px;
    font-weight: 500;
}

.nav-label {
    color: #697a94;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 700;
    margin: 22px 0 10px;
}

.side-card {
    padding: 14px 16px;
    border: 1px solid #18273e;
    border-radius: 12px;
    background: #0a1221;
    color: #8494ab;
    font-size: 12px;
    line-height: 1.55;
    margin-top: 24px;
}

.side-card b {
    color: #dce7fa;
}

/* Hero Header */
.hero {
    border: 1px solid #203352;
    border-radius: 18px;
    padding: 28px 32px;
    margin-bottom: 28px;
    background:
        radial-gradient(circle at 82% 15%, rgba(65, 115, 255, 0.18), transparent 38%),
        linear-gradient(135deg, #101a2c, #09111e);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
}

.eyebrow {
    color: #8e7cff;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.16em;
    text-transform: uppercase;
}

.hero-title {
    color: #f7faff;
    font-size: 32px;
    font-weight: 850;
    letter-spacing: -0.035em;
    margin: 8px 0 6px;
}

.hero-sub {
    color: #8f9fb8;
    font-size: 14px;
    max-width: 820px;
    line-height: 1.5;
}

.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 18px;
}

.pill {
    border: 1px solid #223552;
    background: rgba(12, 21, 37, 0.85);
    border-radius: 999px;
    padding: 5px 12px;
    color: #a4b4cb;
    font-size: 11px;
    font-weight: 550;
    letter-spacing: 0.02em;
}

.section-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin: 32px 0 14px;
    padding-bottom: 6px;
    border-bottom: 1px solid #142033;
}

.section-title {
    font-size: 18px;
    font-weight: 780;
    color: #edf4ff;
    letter-spacing: -0.02em;
}

.section-kicker {
    color: #6a7c97;
    font-size: 12px;
    font-weight: 500;
}

/* Empty State */
.empty-shell {
    border: 1px dashed #233550;
    border-radius: 18px;
    padding: 64px 24px;
    text-align: center;
    background:
        radial-gradient(circle at 50% 30%, rgba(47, 140, 255, 0.05), transparent 40%),
        #09111f;
    margin: 20px 0;
}

.empty-icon {
    width: 62px;
    height: 62px;
    margin: 0 auto 16px;
    border-radius: 16px;
    display: grid;
    place-items: center;
    background: #111a2d;
    border: 1px solid #1f3049;
    color: #8c78ff;
    font-size: 28px;
    box-shadow: 0 0 24px rgba(140, 120, 255, 0.15);
}

.empty-title {
    color: #eaf1ff;
    font-size: 22px;
    font-weight: 780;
    letter-spacing: -0.02em;
}

.empty-copy {
    max-width: 620px;
    margin: 10px auto 22px;
    color: #798aa3;
    font-size: 13px;
    line-height: 1.65;
}

/* Panels */
.panel {
    background: linear-gradient(145deg, #0e1728, #0a1120);
    border: 1px solid #1a2a42;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
    height: 100%;
}

.panel-title {
    color: #edf3ff;
    font-weight: 750;
    font-size: 14px;
    margin-bottom: 3px;
    letter-spacing: -0.01em;
}

.panel-sub {
    color: #6f809a;
    font-size: 11px;
    margin-bottom: 15px;
    font-weight: 450;
}

/* Progress Bars */
.bar-wrap {
    margin: 10px 0 14px;
}

.bar-label {
    display: flex;
    justify-content: space-between;
    color: #92a2ba;
    font-size: 11px;
    margin-bottom: 6px;
    font-weight: 550;
}

.bar-track {
    height: 8px;
    border-radius: 99px;
    background: #152236;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #6e57ff, #36a1ff);
}

.bar-fill.amber {
    background: linear-gradient(90deg, #ff9e39, #ffc65a);
}

.bar-fill.red {
    background: linear-gradient(90deg, #ff506b, #ff7b5d);
}

.bar-fill.green {
    background: linear-gradient(90deg, #1fcf9c, #4fe0bb);
}

.bar-fill.muted {
    background: #253957;
}

/* Donut Chart */
.donut {
    width: 146px;
    height: 146px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    margin: 6px auto 12px;
    background: conic-gradient(#2f8cff 0deg var(--angle), #162438 var(--angle) 360deg);
    position: relative;
    box-shadow: 0 0 25px rgba(47, 140, 255, 0.2);
}

.donut:after {
    content: "";
    position: absolute;
    width: 104px;
    height: 104px;
    border-radius: 50%;
    background: #0a1120;
}

.donut-center {
    position: relative;
    z-index: 1;
    text-align: center;
}

.donut-value {
    color: #f5f8ff;
    font-size: 24px;
    font-weight: 850;
    letter-spacing: -0.03em;
}

.donut-caption {
    color: #72839c;
    font-size: 10px;
    font-weight: 550;
}

/* Status Chips */
.status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 10px;
    font-weight: 750;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.status.open {
    background: rgba(47, 140, 255, 0.14);
    color: #5ab1ff;
    border: 1px solid rgba(47, 140, 255, 0.28);
}

.status.high {
    background: rgba(255, 84, 105, 0.14);
    color: #ff6b7e;
    border: 1px solid rgba(255, 84, 105, 0.28);
}

.status.medium {
    background: rgba(255, 177, 59, 0.14);
    color: #ffbe57;
    border: 1px solid rgba(255, 177, 59, 0.28);
}

.status.resolved {
    background: rgba(36, 216, 154, 0.14);
    color: #3fe2a7;
    border: 1px solid rgba(36, 216, 154, 0.28);
}

/* Lineage Shell */
.lineage-shell {
    background: #08101d;
    border: 1px solid #1a2a42;
    border-radius: 16px;
    overflow: hidden;
}

.lineage-caption {
    padding: 14px 18px 0;
    color: #6b7d97;
    font-size: 11px;
    font-weight: 550;
}

/* AI & Governance Boxes */
.ai-box {
    border: 1px solid #372f69;
    border-radius: 15px;
    padding: 20px;
    background: linear-gradient(145deg, #15142f, #0d1424);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
}

.ai-title {
    color: #eae5ff;
    font-weight: 800;
    font-size: 15px;
    letter-spacing: -0.01em;
}

.ai-meta {
    color: #7b83a6;
    font-size: 11px;
    margin-top: 4px;
    margin-bottom: 16px;
}

.provenance {
    border: 1px solid #19273f;
    border-radius: 14px;
    padding: 14px 16px;
    background: #09111e;
}

.prov-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #142034;
    font-size: 11px;
}

.prov-row:last-child {
    border-bottom: 0;
}

.prov-row span:first-child {
    color: #64758f;
    font-weight: 500;
}

.prov-row span:last-child {
    color: #b8c6dc;
    font-weight: 600;
}

/* Fact row for evidence & timeline */
.fact-row {
    display: grid;
    grid-template-columns: 140px 26px 1fr auto;
    gap: 10px;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #132034;
    font-size: 11px;
}

.fact-row:last-child {
    border-bottom: none;
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Formatting Helpers
# ---------------------------------------------------------------------------

def money(value: int | float) -> str:
    """Format an integer or float into INR currency string."""
    return f"₹{int(value):,}"


def fmt_dt(value) -> str:
    """Format datetime object into human-readable timestamp."""
    return value.strftime("%d %b · %H:%M:%S") if value else "—"


def status_chip(status: str) -> str:
    """Generate HTML status chip based on status value."""
    status_clean = str(status).upper()
    if status_clean == "RESOLVED":
        css = "resolved"
    elif status_clean in ("CRITICAL", "HIGH"):
        css = "high"
    elif status_clean == "MEDIUM":
        css = "medium"
    else:
        css = "open"
    return f'<span class="status {css}">{escape(status_clean.replace("_", " "))}</span>'


def lineage_html(result, evidence, report, timeline, reasoning) -> str:
    """Build SVG visualization for financial state lineage graph."""
    payment = evidence.payment
    merchant = result.state_graph.merchants.get(payment.merchant_id)
    refund = evidence.refunds[0] if evidence.refunds else None
    event = evidence.webhook_events[0] if evidence.webhook_events else None
    settlement = evidence.settlement
    batch = evidence.batch

    nodes = [
        ("MERCHANT", merchant.merchant_id if merchant else payment.merchant_id, merchant.merchant_name if merchant else "Synthetic Merchant", "#7959ff"),
        ("PAYMENT", payment.payment_id, f"{money(payment.amount)} · {payment.status}", "#2f8cff"),
        ("REFUND", refund.refund_id if refund else "None", money(refund.amount) if refund else "No refund", "#35c4ff"),
        ("WEBHOOK", event.event_id if event else "None", f"{event.event_type} · {fmt_dt(event.delivered_at)}" if event else "No event", "#ffb13b"),
        ("SETTLEMENT", settlement.settlement_id, f"Observed {money(settlement.observed_net_amount)}", "#ff5469"),
        ("BATCH", batch.batch_id if batch else settlement.batch_id, f"Cutoff {fmt_dt(settlement.cutoff_at)}", "#24d89a"),
    ]
    xs = [105, 330, 555, 780, 1005, 1230]

    parts = [
        """
        <svg viewBox="0 0 1335 235" width="100%" role="img" aria-label="Financial state lineage" style="font-family: 'Inter', -apple-system, sans-serif;">
          <defs>
            <linearGradient id="edge" x1="0" x2="1">
              <stop offset="0" stop-color="#3d5478"/>
              <stop offset="1" stop-color="#8069ff"/>
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur"/>
              <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
        """
    ]

    for i in range(len(xs) - 1):
        parts.append(
            f'<line x1="{xs[i] + 70}" y1="95" x2="{xs[i + 1] - 70}" y2="95" stroke="url(#edge)" stroke-width="2" stroke-dasharray="5 5"/>'
        )
        parts.append(
            f'<circle cx="{(xs[i] + xs[i + 1]) // 2}" cy="95" r="3" fill="#8069ff"/>'
        )

    for (kind, ident, sub, accent), x in zip(nodes, xs):
        parts.append(
            f"""
            <g>
              <rect x="{x - 70}" y="42" width="140" height="106" rx="14" fill="#0d1729" stroke="#223654" stroke-width="1.2"/>
              <circle cx="{x - 48}" cy="64" r="5" fill="{accent}" filter="url(#glow)"/>
              <text x="{x - 36}" y="68" fill="#6f819c" font-size="10" font-weight="700" letter-spacing="1.2">{escape(kind)}</text>
              <text x="{x - 56}" y="95" fill="#edf4ff" font-size="12" font-weight="700">{escape(ident)}</text>
              <text x="{x - 56}" y="118" fill="#7d8fa8" font-size="10">{escape(sub[:24])}</text>
            </g>
            """
        )

    if event and not timeline.webhook_delivered_before_cutoff:
        parts.append(
            f'<rect x="{xs[3] - 68}" y="160" width="136" height="26" rx="13" fill="#3a2512" stroke="#724d1c" stroke-width="1.2"/>'
            f'<text x="{xs[3]}" y="177" text-anchor="middle" fill="#ffb84d" font-size="10" font-weight="750">⚠ delivery after cutoff</text>'
        )

    parts.append(
        f'<rect x="{xs[4] - 74}" y="160" width="148" height="26" rx="13" fill="#38151f" stroke="#702230" stroke-width="1.2"/>'
        f'<text x="{xs[4]}" y="177" text-anchor="middle" fill="#ff6b7e" font-size="10" font-weight="750">VARIANCE {escape(money(abs(report.variance_amount)))}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Sidebar Configuration
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="fii-brand">
            <div class="fii-mark">◆</div>
            <div>
                <div class="fii-brand-name">FII</div>
                <div class="fii-brand-sub">Financial Incident Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-label">Workspace</div>', unsafe_allow_html=True)
    st.markdown("**● Finance Control Center**")
    st.markdown("  └ Incident Queue")
    st.markdown("  └ Root-Cause Reasoning")
    st.markdown("  └ Governance Decision")

    st.markdown('<div class="nav-label">Control Settings</div>', unsafe_allow_html=True)
    base_payment_count = st.number_input(
        "Batch records",
        min_value=30,
        max_value=5000,
        value=30,
        step=10,
        help="Base payment records generated. Total records include injected anomalies.",
    )
    random_seed = st.number_input(
        "Random seed",
        value=42,
        step=1,
        help="Deterministic seed for reproducible simulations.",
    )

    run_clicked = st.button("▶  Run Financial Control", type="primary", use_container_width=True)

    st.markdown(
        """
        <div class="side-card">
            <b>● Synthetic Environment</b><br>
            All financial transactions are generated locally. Injected anomalies are verified by the evaluation harness and deterministic reconciliation.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Hero Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Financial Control Center</div>
        <div class="hero-title">Detect. Investigate. Govern. Resolve.</div>
        <div class="hero-sub">
            An autonomous finance-ops control loop that reconstructs transaction event graphs,
            isolates root-cause mechanisms, and surfaces evidence-bound governance actions.
        </div>
        <div class="pill-row">
            <span class="pill">50+ Synthetic Records</span>
            <span class="pill">Deterministic Reconciliation</span>
            <span class="pill">Evidence-Backed AI</span>
            <span class="pill">Human Governed</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Pipeline Execution & State Management
# ---------------------------------------------------------------------------

if run_clicked:
    with st.spinner("Executing financial control and deterministic reconciliation…"):
        st.session_state.result = run_pipeline(
            base_payment_count=int(base_payment_count),
            random_seed=int(random_seed),
        )
        st.session_state.ai_responses = {}
        st.session_state.resolved_incidents = set()
    st.rerun()

if "result" not in st.session_state:
    st.markdown(
        """
        <div class="empty-shell">
            <div class="empty-icon">◈</div>
            <div class="empty-title">Ready to run financial control</div>
            <div class="empty-copy">
                Generate a synthetic transaction batch, run the deterministic reconciliation engine,
                and surface discrepancies that require causal investigation and operational governance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        if st.button("▶  Run Financial Control Now", type="primary", use_container_width=True):
            with st.spinner("Running initial financial control pipeline…"):
                st.session_state.result = run_pipeline(
                    base_payment_count=int(base_payment_count),
                    random_seed=int(random_seed),
                )
                st.session_state.ai_responses = {}
                st.session_state.resolved_incidents = set()
            st.rerun()
    st.stop()

result: PipelineResult = st.session_state.result
if "ai_responses" not in st.session_state:
    st.session_state.ai_responses = {}
if "resolved_incidents" not in st.session_state:
    st.session_state.resolved_incidents = set()

# ---------------------------------------------------------------------------
# Executive KPI Row
# ---------------------------------------------------------------------------

total = len(result.state_graph.settlements)
exceptions = len(result.detected_incidents)
matched = total - exceptions
resolved = sum(1 for req in result.approval_requests.values() if req.status == "RESOLVED")
unresolved = exceptions - resolved
match_rate = (matched / total * 100) if total else 0.0

st.markdown(
    f"""
    <div class="section-head">
        <div>
            <div class="section-title">Control Run Overview</div>
            <div class="section-kicker">Deterministic reconciliation result across settlement batches</div>
        </div>
        <div class="section-kicker">Synthetic batch · Seed {random_seed}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

k = st.columns(5)
k[0].metric("Records Processed", f"{total:,}")
k[1].metric("Matched Records", f"{matched:,}", f"{match_rate:.2f}%")
k[2].metric("Exceptions Found", f"{exceptions:,}")
k[3].metric("Unresolved Exposure", money(result.financial_exposure.unresolved_exposure))
k[4].metric("Exceptions Closed", f"{resolved:,}")

# ---------------------------------------------------------------------------
# Control Health & Analytics
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="section-head">
        <div>
            <div class="section-title">Control Health & Anomaly Distribution</div>
            <div class="section-kicker">Operational breakdown of detected financial discrepancies</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    angle = match_rate / 100 * 360
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">Reconciliation Accuracy</div>
            <div class="panel-sub">Settlement records matching calculated financial state</div>
            <div class="donut" style="--angle:{angle:.1f}deg">
                <div class="donut-center">
                    <div class="donut-value">{match_rate:.1f}%</div>
                    <div class="donut-caption">{matched} / {total} matched</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    sev = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for inc in result.detected_incidents:
        sev[inc.severity] = sev.get(inc.severity, 0) + 1

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Exception Severity</div>
            <div class="panel-sub">Discrepancies ranked by financial impact priority</div>
        """,
        unsafe_allow_html=True,
    )
    for label, cls in [("CRITICAL", "red"), ("HIGH", "red"), ("MEDIUM", "amber"), ("LOW", "green")]:
        width = (sev[label] / exceptions * 100) if exceptions else 0
        st.markdown(
            f"""
            <div class="bar-wrap">
                <div class="bar-label"><span>{label}</span><span>{sev[label]} ({width:.0f}%)</span></div>
                <div class="bar-track"><div class="bar-fill {cls}" style="width:{width}%"></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    methods: dict[str, int] = {}
    for inc in result.detected_incidents:
        payment = result.state_graph.payments.get(inc.payment_id)
        if payment:
            methods[payment.method] = methods.get(payment.method, 0) + 1

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Affected Payment Channels</div>
            <div class="panel-sub">Incident distribution by underlying payment instrument</div>
        """,
        unsafe_allow_html=True,
    )
    max_method_count = max(methods.values()) if methods else 1
    for method, count in sorted(methods.items(), key=lambda x: -x[1]):
        width = (count / max_method_count * 100) if max_method_count else 0
        st.markdown(
            f"""
            <div class="bar-wrap">
                <div class="bar-label"><span>{escape(method)}</span><span>{count} incidents</span></div>
                <div class="bar-track"><div class="bar-fill" style="width:{width}%"></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Exception Queue
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="section-head">
        <div>
            <div class="section-title">Exception Queue</div>
            <div class="section-kicker">Review and select an active incident to inspect its causal evidence</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

incident_rows = []
for incident in result.detected_incidents:
    req = result.approval_requests.get(incident.incident_id)
    payment_rec = result.state_graph.payments.get(incident.payment_id)
    merchant_id = payment_rec.merchant_id if payment_rec else "—"
    incident_rows.append(
        {
            "Incident ID": incident.incident_id,
            "Payment ID": incident.payment_id,
            "Merchant": merchant_id,
            "Variance": money(abs(incident.variance_amount)),
            "Severity": incident.severity,
            "Governance Status": req.status if req else "UNRESOLVED",
        }
    )

st.dataframe(pd.DataFrame(incident_rows), use_container_width=True, hide_index=True, height=260)

incident_ids = [item.incident_id for item in result.detected_incidents]
if not incident_ids:
    st.success("No financial exceptions detected in this control run.")
    st.stop()

sel_col1, sel_col2 = st.columns([1.2, 2.8])
with sel_col1:
    selected_id = st.selectbox(
        "Open Incident Investigation",
        incident_ids,
        index=0,
        help="Choose an incident candidate to inspect its event chain, causal hypotheses, and governance resolution.",
    )

report = next(item for item in result.incident_reports if item.incident_id == selected_id)
evidence = result.evidence_map[selected_id]
timeline = result.timeline_map[selected_id]
hypotheses = result.hypotheses_map[selected_id]
reasoning = result.reasoning_map[selected_id]
recommendation = result.action_recommendations[selected_id]
approval = result.approval_requests.get(selected_id)

# ---------------------------------------------------------------------------
# Investigation Workspace
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div class="section-head">
        <div>
            <div class="section-title">Investigation Workspace: {escape(selected_id)}</div>
            <div class="section-kicker">Target payment: {escape(report.payment_id)} · Batch: {escape(report.settlement_id)}</div>
        </div>
        <div>{status_chip(approval.status if approval else "UNRESOLVED")}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Incident summary metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Expected Net Amount", money(report.expected_amount))
m2.metric("Observed Settlement", money(report.observed_amount))
m3.metric("Net Variance", money(abs(report.variance_amount)))
m4.metric("Incident Severity", report.severity)

# Lineage Graph
st.markdown(
    """
    <div class="section-head">
        <div>
            <div class="section-title">Financial State Lineage Graph</div>
            <div class="section-kicker">Reconstructed event chain from capture through settlement cutoff</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

components.html(
    f"""
    <div class="lineage-shell">
        <div class="lineage-caption">Derived from state graph relationships and webhook delivery audit log</div>
        {lineage_html(result, evidence, report, timeline, reasoning)}
    </div>
    """,
    height=245,
    scrolling=False,
)

# Two-column Investigation details
col_timeline, col_reasoning = st.columns([1.15, 0.85])

with col_timeline:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Event Timeline</div>
            <div class="panel-sub">Chronological event sequencing vs settlement cutoff window</div>
        """,
        unsafe_allow_html=True,
    )

    payment = evidence.payment
    refund = evidence.refunds[0] if evidence.refunds else None
    event = evidence.webhook_events[0] if evidence.webhook_events else None

    timeline_items = [
        (payment.captured_at, "Payment captured", money(payment.amount), "OK"),
    ]
    if refund:
        timeline_items.append((refund.processed_at, "Refund processed", money(refund.amount), "OK"))
    if event:
        timeline_items.append((event.emitted_at, "Refund event emitted", event.event_type, "OK"))
        timeline_items.append(
            (
                event.delivered_at,
                "Webhook delivered",
                event.delivery_status,
                "LATE" if not timeline.webhook_delivered_before_cutoff else "OK",
            )
        )
    timeline_items.append(
        (
            evidence.settlement.cutoff_at,
            "Settlement cutoff",
            "Observed " + money(evidence.settlement.observed_net_amount),
            "VAR",
        )
    )

    # Sort strictly chronologically
    timeline_items.sort(key=lambda item: item[0])

    for dt, label, val, state in timeline_items:
        marker = "⚠" if state in ("LATE", "VAR") else "✓"
        color = "#ffb13b" if state == "LATE" else ("#ff5469" if state == "VAR" else "#24d89a")
        st.markdown(
            f"""
            <div class="fact-row">
                <span style="color:#6e809c">{escape(fmt_dt(dt))}</span>
                <b style="color:{color}">{marker}</b>
                <span style="color:#eef4ff">{escape(label)}</span>
                <span style="color:#8ba0be">{escape(val)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with col_reasoning:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Deterministic Causal Reasoning</div>
            <div class="panel-sub">Competing hypotheses ranked from empirical telemetry facts</div>
        """,
        unsafe_allow_html=True,
    )

    assessments = {a.hypothesis_name: a for a in reasoning.assessments}
    ordered = sorted(hypotheses, key=lambda h: assessments[h.name].evidence_score, reverse=True)
    max_score = max((assessments[h.name].evidence_score for h in ordered), default=1)

    for h in ordered:
        score = assessments[h.name].evidence_score
        width = max(5, (score / max_score * 100)) if max_score else 0
        color_cls = "green" if h.status == "SUPPORTED" else "muted"
        status_text = "SUPPORTED" if h.status == "SUPPORTED" else "UNSUPPORTED"
        st.markdown(
            f"""
            <div class="bar-wrap">
                <div class="bar-label">
                    <span>{escape(h.name)}</span>
                    <span style="color:{'#24d89a' if h.status == 'SUPPORTED' else '#6b7d96'}">{status_text} · {score:.2f}</span>
                </div>
                <div class="bar-track"><div class="bar-fill {color_cls}" style="width:{width}%"></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style="margin-top:16px;padding-top:14px;border-top:1px solid #16253c;color:#9aaec7;font-size:11px">
            Primary mechanism: <b style="color:#ffffff">{escape(reasoning.primary_hypothesis or "UNRESOLVED")}</b><br>
            Evidence confidence margin: <b style="color:#35c4ff">{reasoning.evidence_margin:.2f}</b>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Evidence & Blast Radius
# ---------------------------------------------------------------------------

b1, b2 = st.columns([1, 1])

with b1:
    with st.container(border=True):
        st.markdown(
            """
            <div class="panel-title">Verified Audit Evidence</div>
            <div class="panel-sub">Empirical telemetry facts bound to this transaction</div>
            """,
            unsafe_allow_html=True,
        )
        ev_rows = [
            ("Payment", evidence.payment.payment_id, f"Captured {fmt_dt(evidence.payment.captured_at)}", money(evidence.payment.amount)),
        ]
        for r in evidence.refunds:
            ev_rows.append(("Refund", r.refund_id, f"Processed {fmt_dt(r.processed_at)}", money(r.amount)))
        for ev in evidence.webhook_events:
            ev_rows.append(("Webhook", ev.event_id, f"{ev.event_type} · {fmt_dt(ev.delivered_at)}", ev.delivery_status))
        ev_rows.append(("Settlement", evidence.settlement.settlement_id, f"Expected {money(evidence.settlement.expected_net_amount)} vs Observed {money(evidence.settlement.observed_net_amount)}", "VARIANCE"))

        for cat, ident, detail, amt in ev_rows:
            st.markdown(
                f"""
                <div class="fact-row" style="grid-template-columns: 85px 125px 1fr auto;">
                    <span style="color:#72859f;font-weight:600">{escape(cat)}</span>
                    <code style="color:#35c4ff;background:#0e192c;padding:2px 6px;border-radius:4px;font-size:10px">{escape(ident)}</code>
                    <span style="color:#8da1bd">{escape(detail)}</span>
                    <span style="color:#eef4ff;font-weight:600">{escape(amt)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

with b2:
    with st.container(border=True):
        st.markdown(
            """
            <div class="panel-title">Blast Radius & Financial Exposure</div>
            <div class="panel-sub">Systemic impact footprint across the merchant portfolio</div>
            """,
            unsafe_allow_html=True,
        )
        r1, r2, r3 = st.columns(3)
        r1.metric("Payments", f"{report.blast_radius.affected_payment_count:,}")
        r2.metric("Merchants", f"{report.blast_radius.affected_merchant_count:,}")
        r3.metric("Exposure", money(report.financial_exposure.unresolved_exposure))

        st.markdown(
            f"""
            <div style="margin-top:14px;padding-top:12px;border-top:1px solid #162438;font-size:12px;color:#8da1bd;display:flex;flex-direction:column;gap:8px">
                <div>Scope: <code style="color:#24d89a;background:#0e192c;padding:2px 6px;border-radius:4px">{escape(report.cluster_scope or 'ISOLATED')}</code> &nbsp;·&nbsp; Mechanism: <code style="color:#ffb13b;background:#0e192c;padding:2px 6px;border-radius:4px">{escape(report.cluster_mechanism or 'UNRESOLVED')}</code></div>
                <div>First affected event: <span style="color:#eef4ff;font-weight:550">{escape(fmt_dt(report.blast_radius.first_affected_at))}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Decision Layer (AI Investigation + Governance)
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="section-head">
        <div>
            <div class="section-title">Decision & Governance Layer</div>
            <div class="section-kicker">AI interprets verified evidence; policy rules and human reviewers govern actions</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

ai_col, gov_col = st.columns([1.05, 0.95])

with ai_col:
    with st.container(border=True):
        st.markdown(
            """
            <div class="panel-title" style="color:#e8e2ff">✦ AI Investigation Narrative</div>
            <div class="panel-sub" style="color:#7d86a6">Evidence-bound reasoning · No hallucinated financial facts · Deterministic ground truth authoritative</div>
            """,
            unsafe_allow_html=True,
        )

        if selected_id not in st.session_state.ai_responses:
            st.info("The investigation narrative is synthesized on demand from verified facts.")
            if st.button("✦ Investigate with AI", key=f"ai_{selected_id}", type="primary", use_container_width=True):
                with st.spinner("Synthesizing evidence-bound investigation narrative…"):
                    try:
                        st.session_state.ai_responses[selected_id] = investigate_report(result, report)
                    except Exception as error:  # noqa: BLE001
                        st.error(f"AI investigation failed: {error}")
                st.rerun()
        else:
            resp = st.session_state.ai_responses[selected_id]
            narrative = resp.narrative
            st.success(f"Provider: {resp.provider.upper()} · Model: {resp.model}")
            st.write(narrative.summary)
            st.markdown(f"**Identified Root Cause:** `{narrative.root_cause}`")
            st.markdown(f"**Confidence Level:** **{narrative.confidence}**")
            if narrative.recommended_action:
                st.markdown(f"**Suggested Operational Action:** `{narrative.recommended_action}`")
            if narrative.evidence_summary:
                st.markdown("**Evidence Summary:**")
                for item in narrative.evidence_summary:
                    st.markdown(f"- {item}")
            if narrative.uncertainty:
                st.markdown("**Remaining Uncertainty / Follow-ups:**")
                for item in narrative.uncertainty:
                    st.markdown(f"- {item}")

with gov_col:
    with st.container(border=True):
        st.markdown(
            """
            <div class="panel-title">Governance & Simulated Remediation</div>
            <div class="panel-sub">Bounded action space · Explicit reviewer sign-off · Audited resolution</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f"**Recommended Action:** `{recommendation.action}` · Priority: **{recommendation.priority}**")
        st.caption(f"Policy Justification: {recommendation.reason}")

        if approval and approval.status == "PENDING_APPROVAL":
            st.warning(f"Reviewer Sign-off Required · Request: {approval.request_id}")
            reviewer = st.text_input(
                "Reviewer Name / Role",
                key=f"rev_{selected_id}",
                value="Finance Operations Specialist",
            )
            decision_reason = st.text_area(
                "Decision Rationale",
                key=f"reason_{selected_id}",
                value="Approved based on verified telemetry event sequence.",
            )
            g1, g2 = st.columns(2)
            with g1:
                if st.button("✓ Approve Action", key=f"app_{selected_id}", type="primary", use_container_width=True):
                    try:
                        review_approval_request(
                            approval,
                            approved=True,
                            reviewer=reviewer.strip() or "Finance Ops",
                            reason=decision_reason.strip() or "Approved",
                        )
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))
            with g2:
                if st.button("✕ Reject Action", key=f"rej_{selected_id}", use_container_width=True):
                    try:
                        review_approval_request(
                            approval,
                            approved=False,
                            reviewer=reviewer.strip() or "Finance Ops",
                            reason=decision_reason.strip() or "Rejected",
                        )
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

        elif approval and approval.status == "APPROVED":
            st.success(f"Action Approved by {approval.reviewer or 'Finance Ops'}")
            resolver = st.text_input(
                "Resolver Identity",
                key=f"res_{selected_id}",
                value=approval.reviewer or "Finance Ops Specialist",
            )
            resolution_note = st.text_area(
                "Resolution Note",
                key=f"note_{selected_id}",
                placeholder="Describe simulated ledger adjustment or operational remediation note…",
            )
            if st.button("✓ Complete Simulated Resolution", key=f"close_{selected_id}", type="primary", use_container_width=True):
                try:
                    resolve_approval_request(
                        approval,
                        resolver=resolver.strip() or "Finance Ops",
                        note=resolution_note.strip() or "Resolved in simulated environment",
                    )
                    st.session_state.resolved_incidents.add(selected_id)
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))

        elif approval and approval.status == "RESOLVED":
            st.success(f"Incident Resolved by {approval.resolver or 'Finance Ops'}")
            if approval.resolution_note:
                st.caption(f"Resolution Note: {approval.resolution_note}")
            st.caption("Remediation is simulated within the test control framework; no real currency moved.")

        elif approval:
            st.error(f"Recommendation Rejected by {approval.reviewer or 'Finance Ops'}")
            st.caption(approval.decision_reason or "No decision rationale supplied.")

# ---------------------------------------------------------------------------
# Run Provenance Footer
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="section-head">
        <div>
            <div class="section-title">Control Run Provenance</div>
            <div class="section-kicker">Transparent boundaries of the synthetic demonstration</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

prov_data = [
    ("Control Type", "Synthetic Financial Operations"),
    ("Records Reconciled", f"{total:,}"),
    ("Reconciliation Engine", "Deterministic Finite State Machine"),
    ("Investigation Agent", "Evidence-Bound LLM (Gemini / OpenAI)"),
    ("Evaluation Ground Truth", "Isolated Evaluation Harness"),
    ("Financial Remediation", "Simulated Governance Closure"),
]

pcols = st.columns(3)
for i, (label, val) in enumerate(prov_data):
    with pcols[i % 3]:
        st.markdown(
            f"""
            <div class="provenance">
                <div class="prov-row">
                    <span>{escape(label)}</span>
                    <span>{escape(val)}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
