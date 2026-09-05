"""Central configuration for Financial Incident Intelligence."""

import os

RANDOM_SEED = 42
MERCHANT_COUNT = 50
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

# Keep the default deterministic so the project runs without credentials.
# Set AGENT_PROVIDER=gemini for the real AI demo.
AGENT_PROVIDER = os.getenv("AGENT_PROVIDER", "mock").lower()
AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")
