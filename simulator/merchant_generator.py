"""
Synthetic merchant generator for Financial Incident Intelligence.
"""

import random

from configs.schema import Merchant
from configs.settings import DEFAULT_CURRENCY


MERCHANT_SEGMENTS = [
    "SMB",
    "MID_MARKET",
    "ENTERPRISE",
]

SETTLEMENT_CYCLES = [
    "T1",
    "T2",
]


def generate_merchant(merchant_number: int) -> Merchant:
    """
    Generate one synthetic merchant.

    Parameters
    ----------
    merchant_number:
        Numeric identifier used to create a unique merchant ID.

    Returns
    -------
    Merchant
        A synthetic Merchant object.
    """

    merchant_id = f"MER_{merchant_number:04d}"

    merchant_name = f"Merchant {merchant_number:04d}"

    segment = random.choice(MERCHANT_SEGMENTS)

    settlement_cycle = random.choice(SETTLEMENT_CYCLES)

    return Merchant(
        merchant_id=merchant_id,
        merchant_name=merchant_name,
        segment=segment,
        currency=DEFAULT_CURRENCY,
        settlement_cycle=settlement_cycle,
    )