"""Create the two source batches for the lakehouse demo.

Batch 1 = the initial 2,000 customers.
Batch 2 = a later 500-customer arrival, appended as a second Iceberg snapshot.

Run from this folder:  python jobs/make_data.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

FEATURES = [
    "customer_id",
    "tenure_months",
    "monthly_charge",
    "support_calls",
    "contract",
    "internet_service",
    "churned",
]


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def make_batch(n: int, start_id: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    tenure = rng.integers(1, 73, n)
    contract = rng.choice(
        ["month-to-month", "one-year", "two-year"], n, p=[0.55, 0.25, 0.20]
    )
    internet = rng.choice(["fiber", "dsl", "none"], n, p=[0.45, 0.40, 0.15])

    base = np.where(internet == "fiber", 75.0, np.where(internet == "dsl", 55.0, 35.0))
    monthly = base + rng.normal(0, 12, n)
    monthly += np.where(contract == "month-to-month", 5.0, 0.0)
    monthly = np.clip(monthly, 25.0, 130.0).round(2)

    support = rng.poisson(1.8 + (internet == "fiber") * 0.8, n)
    support = np.clip(support, 0, 10)

    # Churn signal: short tenure, expensive plan, many support calls and a
    # flexible contract all push the probability up. This mirrors the pattern
    # a real telco churn model would learn.
    z = -1.8 + 0.030 * (monthly - 65.0) + 0.40 * support - 0.055 * tenure
    z += np.where(
        contract == "month-to-month", 0.90, np.where(contract == "one-year", 0.10, -0.60)
    )
    z += np.where(internet == "fiber", 0.35, np.where(internet == "dsl", 0.0, -0.20))
    churned = (rng.random(n) < sigmoid(z)).astype(int)

    return pd.DataFrame(
        {
            "customer_id": np.arange(start_id, start_id + n),
            "tenure_months": tenure,
            "monthly_charge": monthly,
            "support_calls": support,
            "contract": contract,
            "internet_service": internet,
            "churned": churned,
        }
    )[FEATURES]


if __name__ == "__main__":
    first = make_batch(2_000, 1, seed=42)
    second = make_batch(500, 2_001, seed=43)

    first.to_csv(OUT / "churn_batch_1.csv", index=False)
    second.to_csv(OUT / "churn_batch_2.csv", index=False)

    print(f"batch 1: {len(first):,} rows -> {OUT / 'churn_batch_1.csv'}")
    print(f"batch 2: {len(second):,} rows -> {OUT / 'churn_batch_2.csv'}")
    print(f"churn rate: {first['churned'].mean():.1%} / {second['churned'].mean():.1%}")
