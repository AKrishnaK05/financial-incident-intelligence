"""
Controlled incident scenarios for Financial Incident Intelligence.

These scenarios intentionally introduce known failures into the
synthetic financial event stream so that the investigation system
can later be evaluated against ground truth.
"""

REFUND_EVENT_LATENCY = {
    "scenario_name": "REFUND_EVENT_LATENCY",
    "description": (
        "Refund is processed before settlement cutoff, "
        "but its webhook is delivered after the cutoff."
    ),
}