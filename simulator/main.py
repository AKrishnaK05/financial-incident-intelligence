"""
Entry point for the synthetic financial data simulator.

For now, this program generates and displays one payment.
"""

from datetime import datetime, timezone

from simulator.payment_generator import generate_payment
from simulator.merchant_generator import generate_merchant
from simulator.refund_generator import generate_refunds

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

    refunds = []

    next_refund_number = 1

    for payment in payments:
        payment_refunds = generate_refunds(
            payment=payment,
            refund_number_start=next_refund_number,
        )

        refunds.extend(payment_refunds)

        next_refund_number += len(payment_refunds)

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

    print()
    print(f"Generated {len(refunds)} refunds")
    print("-----------------------------")

    for refund in refunds:
        print(
            f"{refund.refund_id} | "
            f"{refund.payment_id} | "
            f"₹{refund.amount} | "
            f"{refund.status}"
        )

if __name__ == "__main__":
    main()