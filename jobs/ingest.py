"""Ingest the two source batches into Iceberg through the Nessie catalog.

Run inside the Spark container:
    docker compose exec -T spark spark-submit \
        --master "local[2]" /workspace/jobs/ingest.py

Nessie versions the whole catalog like Git. Each write below becomes one Nessie
commit; those commit hashes are the reproducible data versions the notebook
trains on. (Nessie deliberately returns one Iceberg snapshot per commit, so the
commit hash — not an old Iceberg snapshot id — is the time-travel handle.)
"""

import json
import sys
import urllib.request
from pathlib import Path

from pyspark.sql import SparkSession

TABLE = "nessie.lakehouse.churn_features"
BATCH_1 = "/workspace/data/churn_batch_1.csv"
BATCH_2 = "/workspace/data/churn_batch_2.csv"
STATE = Path("/workspace/state/ingest_summary.json")
NESSIE = "http://nessie:19120/api/v2"


def nessie_head() -> str:
    with urllib.request.urlopen(f"{NESSIE}/trees/main", timeout=10) as response:
        return json.load(response)["reference"]["hash"]


def at_commit(commit: str) -> str:
    """Nessie time-travel table name: table@commit is not valid for hashes,
    table#<commit> is the documented form."""
    return f"nessie.lakehouse.`churn_features#{commit}`"


def main() -> int:
    spark = SparkSession.builder.appName("lakehouse-ingest").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    spark.sql("CREATE NAMESPACE IF NOT EXISTS nessie.lakehouse")
    spark.sql(f"DROP TABLE IF EXISTS {TABLE}")

    batch_1 = spark.read.csv(BATCH_1, header=True, inferSchema=True)
    batch_1.writeTo(TABLE).createOrReplace()
    commit_1 = nessie_head()
    print(f"\n=== batch 1 loaded: {batch_1.count():,} rows ===")
    print(f"    Nessie commit: {commit_1}")

    batch_2 = spark.read.csv(BATCH_2, header=True, inferSchema=True)
    batch_2.writeTo(TABLE).append()
    commit_2 = nessie_head()
    print(f"\n=== batch 2 appended: {batch_2.count():,} new rows ===")
    print(f"    Nessie commit: {commit_2}")

    if commit_1 == commit_2:
        print("ERROR: expected two Nessie commits", file=sys.stderr)
        return 1

    print("\n=== Nessie time-travel check ===")
    first_count = spark.sql(f"SELECT COUNT(*) AS n FROM {at_commit(commit_1)}").first()["n"]
    current_count = spark.sql(f"SELECT COUNT(*) AS n FROM {TABLE}").first()["n"]
    print(f"    table#{commit_1[:12]}... -> {first_count:,} rows")
    print(f"    table#{commit_2[:12]}... -> {current_count:,} rows")

    assert first_count == 2_000, first_count
    assert current_count == 2_500, current_count

    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(
        json.dumps(
            {
                "table": "lakehouse.churn_features",
                "batch_1": {"commit": commit_1, "rows": first_count},
                "batch_2": {"commit": commit_2, "rows": current_count},
            },
            indent=2,
        )
    )
    print(f"\nwrote {STATE}")
    print("OK: the lakehouse has two Nessie versions (2,000 then 2,500 rows).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
