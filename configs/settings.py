import os
from pathlib import Path

# Load .env file automatically if present
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=_env_path)
    except ImportError:
        with open(_env_path, "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    _k, _v = _k.strip(), _v.strip().strip("'\"")
                    if _k and _k not in os.environ:
                        os.environ[_k] = _v

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
AGENT_PROVIDER = os.getenv("AGENT_PROVIDER", "gemini").lower()
AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")
