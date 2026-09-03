"""
Entry point for the synthetic financial data simulator.

For now, this program generates and displays one payment.
"""

from datetime import datetime, timezone

from simulator.payment_generator import generate_payment

import random

from configs.settings import RANDOM_SEED


def main():
    """Generate and display one synthetic payment."""
    random.seed(RANDOM_SEED)

    start_time = datetime(
        2026,
        8,
        1,
        tzinfo=timezone.utc,
    )

    payments = []

    for payment_number in range(1,11):
        payment = generate_payment(
            payment_number=payment_number,
            merchant_id="MER_0001",
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