"""
Data contracts for financial incidents and ground truth.
"""

from dataclasses import dataclass


@dataclass
class IncidentGroundTruth:
    incident_id: str
    scenario: str
    root_cause: str
    payment_id: str
    refund_id: str
    settlement_id: str
    expected_amount: int
    observed_amount: int
    exposure_amount: int