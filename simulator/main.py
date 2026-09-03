"""
Entry point for the synthetic financial data simulator.

For now, this program generates and displays one payment.
"""

from datetime import datetime, timezone

from simulator.payment_generator import generate_payment
from simulator.merchant_generator import generate_merchant

import random

from configs.settings import RANDOM_SEED
from configs.settings import MERCHANT_COUNT


def main():
    """Generate and display one synthetic payment."""
    random.seed(RANDOM_SEED)

    start_time = datetime(
        2026,
        8,
        1,
        tzinfo=timezone.utc,
    )

    merchants = []

    for merchant_number in range(1, MERCHANT_COUNT + 1):
        merchant = generate_merchant(merchant_number)
        merchants.append(merchant)

    payments = []

    for payment_number in range(1,11):
        merchant = random.choice(merchants)
        payment = generate_payment(
            payment_number=payment_number,
            merchant_id=merchant.merchant_id,
            start_time=start_time,
        )

        payments.append(payment)

    print(f"Generated {len(payments)} payments")
    print("-----------------------------")

    for payment in payments:
        print(
            f"{payment.payment_id} | "
            f"{payment.merchant_id} | "
            f"{payment.order_id} | "
            f"₹{payment.amount} | "
            f"{payment.method} | "
            f"{payment.currency} | "
            f"{payment.captured_at} | "
            f"{payment.status}"
        )


if __name__ == "__main__":
    main()