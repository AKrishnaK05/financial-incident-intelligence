"""
Data contracts for the Financial Incident Intelligence system.

This module defines the structure and allowed values for the core
financial entities used throughout the project.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------------------------
# Merchent
# ---------------------------------------------------------------------------

@dataclass
class Merchant:
    """
    Represents a merchant using the financial system.
    """

    merchant_id: str
    merchant_name: str
    segment: str
    currency: str
    settlement_cycle: str

# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------

@dataclass
class Payment:
    """
    Represents a successfully captured payment.

    A Payment is the central financial entity that other entities
    such as refunds and settlements refer to.
    """

    payment_id: str
    merchant_id: str
    order_id: str
    amount: int
    method: str
    currency: str
    captured_at: datetime
    status: str


# ---------------------------------------------------------------------------
# Refund
# ---------------------------------------------------------------------------

@dataclass
class Refund:
    """
    Represents a refund associated with a payment.
    """

    refund_id: str
    payment_id: str
    merchant_id: str
    amount: int
    currency: str
    requested_at: datetime
    processed_at: datetime
    status: str


# ---------------------------------------------------------------------------
# Webhook Event
# ---------------------------------------------------------------------------

@dataclass
class WebhookEvent:
    """
    Represents an asynchronous event related to a financial entity.

    The important distinction here is between:

    business_event_at
        When the underlying financial event actually happened.

    emitted_at
        When the source system emitted the event.

    delivered_at
        When the downstream system received the event.
    """

    event_id: str
    entity_id: str
    event_type: str
    business_event_at: datetime
    emitted_at: datetime
    delivered_at: datetime
    delivery_status: str


# ---------------------------------------------------------------------------
# Settlement
# ---------------------------------------------------------------------------

@dataclass
class Settlement:
    """
    Represents the downstream settlement representation for a payment.
    """

    settlement_id: str
    batch_id: str
    merchant_id: str
    payment_id: str
    gross_amount: int
    refund_adjustment: int
    expected_net_amount: int
    observed_net_amount: int
    cutoff_at: datetime
    status: str


# ---------------------------------------------------------------------------
# Settlement Batch
# ---------------------------------------------------------------------------

@dataclass
class SettlementBatch:
    """
    Represents a group of settlement records processed together.
    """

    batch_id: str
    merchant_id: str
    cutoff_at: datetime
    transaction_count: int
    expected_amount: int
    observed_amount: int
    status: str