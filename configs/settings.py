"""
Central configuration for the Financial Incident Intelligence project.
"""

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------

RANDOM_SEED = 42

MERCHANT_COUNT = 50


# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------

DEFAULT_CURRENCY = "INR"

PAYMENT_METHODS = [
    "UPI",
    "CARD",
    "NETBANKING",
    "WALLET",
]

PAYMENT_AMOUNTS = [
    499,
    799,
    999,
    1499,
    2499,
    4999,
    10000,
    15000,
]