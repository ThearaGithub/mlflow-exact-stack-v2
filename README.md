# Exact-Stack Lakehouse — MinIO + Iceberg + Nessie + Spark + Jupyter + MLflow

This is the exact-stack follow-up demo: it keeps the architecture from the
professor's drawing and uses the **actual components**:

```
Sources (CSV batches)
      |
      v
Spark ingestion job
      |
      v
MinIO (S3)  ──  Parquet data files
      |          Iceberg table metadata
      |          Nessie catalog (warehouse = s3://warehouse/)
      |
      +──────────────> Spark (local[2]) ──> JupyterLab ──> MLflow
      |
      +──────────────> Dremio (optional profile) ──> Tableau dashboard
```

The data path is real: the table is stored in object storage, cataloged by
Nessie, and read by Spark. MLflow is the added layer that records which exact
data version each model learned from.

## What is running

| Diagram box | In this folder | Version |
|---|---|---|
| Sources | `data/churn_batch_1.csv`, `data/churn_batch_2.csv` | 2,000 + 500 rows |
| Data ingestion | `jobs/ingest.py` (Spark) | Spark 3.5.9 |
| S3 data lake | **MinIO**, bucket `warehouse` | `RELEASE.2026-10-23` |
| Iceberg tables | Apache Iceberg, Parquet data files | 1.11.0 |
| Catalog | **Nessie** REST catalog, RocksDB persistence | 0.109.0 |
| Compute engine (ML path) | Spark `local[2]` | 3.5.9 |
| Notebooks | JupyterLab | 4.4+ |
| Model lifecycle | **MLflow** tracking server + registry, artifacts in S3 | 3.17.2 |
| Compute engine (BI path) | Dremio | optional profile; verified running here |
| Dashboards | **Tableau Desktop (Free Edition)** via Dremio | `Tableau_Churn_Dashboard.twb` included |

### Dremio and the BI branch

For the full Dremio + Tableau stack, double-click **`Start Demo.bat`**. It starts the
stack with Dremio, waits for port 9047, loads the two versions if needed, and
opens the UIs. Then do the one-time user + Nessie source setup below. The
manual commands here are the fallback.

Dremio is an optional Compose profile and **it now runs on this laptop**:
verified on 2026-10-25 with the full stack (measured ~3.3 GB of containers,
host RAM bottoming at ~0.5 GB free). The key is the WSL VM cap: **6 GB** in
`~/.wslconfig` (`memory=6GB`, `swap=4GB`). At the old 7.4 GiB cap the first
image pull froze the machine, so pull once with the stack stopped:

```bash
# one-time: pull the image with nothing else running
docker compose stop
docker compose --profile dremio pull dremio

# normal start (everything, including Dremio)
docker compose --profile dremio up -d
```

Then open `http://localhost:9047`, create the first user with username
**`admin`** and your own password, and add a **Nessie** source at
`http://nessie:19120/api/v2` with Nessie authentication **none**. In **Storage**
choose **AWS**, then enter `warehouse` after the fixed `s3://` prefix (the full
value is `s3://warehouse`; do not add a leading slash). Use **AWS Access Key**
with `minioadmin` / `minioadmin`, and add the connection properties
`fs.s3a.path.style.access=true`, `fs.s3a.endpoint=minio:9000`, and
`dremio.s3.compat=true`; uncheck **Encrypt connection**.
Query `SELECT * FROM nessie.lakehouse.churn_features LIMIT 20;`. The Tableau
workbook connects to this Dremio server afterwards.

### Tableau dashboard (included)

`Tableau_Churn_Dashboard.twb` is the live BI deliverable: it reads the same
`nessie.lakehouse.churn_features` table through Dremio and shows three bar
charts (churn by contract, tenure group and internet service) on the
**Churn Dashboard** tab. It uses a custom SQL relation with the same query and
the verified Dremio native connector on `localhost:31010`.

To open it on another machine:

1. Install Tableau Desktop. The **Free Edition** is enough; publishing and
   sharing are not used.
2. Copy `Tableau Driver\dremio-jdbc-driver-26.0.5.jar` into
   `%USERPROFILE%\Documents\My Tableau Repository\Drivers` and restart Tableau
   if it was already open. Tableau does not ship the Dremio driver.
   > The ZIP includes the 48 MB driver jar; the GitHub repo does not commit it.
   > If you cloned the repo, download Dremio JDBC 26.0.5 into `Tableau Driver\`
   > first.
3. Start the full stack, open the workbook, and enter the password chosen for
   the Dremio `admin` user when prompted. Dremio must be running.
4. Open the **Churn Dashboard** tab. The proof screenshot is
   `assets/Tableau_Churn_Dashboard.png`.

The workbook stores calculated fields (`Churn Rate` = `AVG([churned])`, and
`Tenure Group` = 0-11 / 12-23 / 24-47 / 48+ months) and percentage formats, so
it opens ready to show. Tableau is a desktop app, not a Compose service; it is
not included in the container memory figures.

Caveats: on the 8 GB laptop close other heavy apps and do not run the notebook
(Spark kernel) while Dremio is up - switch between the ML and BI paths. On a
16 GB machine, 10 GB is a safe WSL cap; on 12 GB use 8 GB. Portable setup on
bigger hardware is still untested. Steps are in `START HERE.md`; the proof image
is `assets/Tableau_Churn_Dashboard.png`. Capture a Dremio query screenshot as
`Dremio proof.png` beside it if you want both branches.

## Hardware reality (important)

- Host: **8.2 GB RAM** (7.6 GiB), 12 cores. The WSL VM is capped at **6 GB**
  (`memory=6GB`, `swap=4GB` in `~/.wslconfig`); this is what lets the whole
  stack, including Dremio, run without starving Windows. The default ~3.9 GB
  was too small, and the 7.4 GiB setting froze the host during a Dremio pull.
- Measured 2026-10-25 with the full stack + Dremio: Dremio ~1.3 GB, MLflow
  ~1.6 GB, Spark/Jupyter ~90 MB idle, Nessie ~245 MB, MinIO ~62 MB - about
  **3.3 GB of containers**, host free RAM ~0.5-0.7 GB.
- The stack is tuned for this machine: MLflow runs with one worker, Spark uses a
  768 MB driver, Nessie a 512 MB heap and a 32 MB cache. Dremio runs at its
  required 4 GB heap - its minimum; smaller values are refused.
- Practical limit: one path at a time. Showing Dremio live plus running the
  notebook (Spark kernel) is too much for 8 GB; switch between them.

## Run it

### One click (recommended)

**Start here:** open **`START HERE.md`**; it has the MinIO login, Dremio setup,
and Run All step. A fresh machine does not need a reset.

Double-click **`Start Demo.bat`**. It starts Docker Desktop if it is not
already running, builds and starts the full stack including Dremio, waits for
MinIO / Nessie / MLflow / Jupyter, and loads the two Iceberg versions only when
the lakehouse does not already have them. It then opens the deck and the UIs:

- the deck (`MLflow_Exact_Stack_V2_Presentation.pptx`) - press Alt+F5 for
  Presenter View; the speaker notes are the talk track
- JupyterLab: <http://localhost:8888/lab/tree/notebooks/lakehouse_mlflow.ipynb>
- MLflow: <http://localhost:5000>
- MinIO console: <http://localhost:9001> (`minioadmin` / `minioadmin`)
- Nessie API: <http://localhost:19120/api/v2/trees/main>
- Dremio: <http://localhost:9047>

`Start Demo.bat` is the only launcher in the folder. It always uses the
full Dremio profile; `Reset Demo.bat` is the only utility, and forced ingestion
is a manual command below.

Keeping the existing lakehouse is deliberate: the saved outputs and MLflow runs
are shown as-is, and the script does not re-run the notebook. Slide 5 uses
`<training-hash>` / `<current-hash>` slots rather than fixed values, so a reset
does not invalidate it; the notebook and MLflow show the live hashes. If MLflow
has no runs yet (for example after a reset), click Run All once. Running it
again adds new runs and moves the `champion` alias; reset first for a clean
version-1 demo.

The first run downloads images and builds the Spark image (roughly 2 GB, several
minutes); the Dremio profile also pulls the Dremio image (~5 GB). Later runs are
cached. For the full BI branch, use `Start Demo.bat`; the manual
equivalent is `docker compose --profile dremio up -d` (see the Dremio section).

### Manual commands

```bash
# start everything
docker compose up -d --build

# create the two Iceberg versions (2,000 then 2,500 rows)
docker compose exec -T spark spark-submit --master "local[2]" /workspace/jobs/ingest.py

# optional: run the notebook headlessly (it already has outputs saved)
docker compose exec -T spark bash -lc \
  "cd /workspace && jupyter nbconvert --to notebook --execute --inplace notebooks/lakehouse_mlflow.ipynb"

# stop, keeping the data
docker compose down

# wipe all volumes (including optional Dremio)
docker compose --profile dremio down -v
```

`Start Demo.bat` reruns ingestion only when the lakehouse does not match
`state/ingest_summary.json`. To force a rerun, use the `spark-submit` command
above; to wipe all volumes, use the reset command below.

## The 4-minute demo

1. **JupyterLab** — open `notebooks/lakehouse_mlflow.ipynb`. The saved outputs
   are already there; click **Run All** only if you want a live run. After a
   reset, Run All is required once and creates the two runs and v1.
   - Cell 3 shows the two Nessie commits and their row counts.
   - Cell 5 reads the same table at commit 1 (2,000 rows) and commit 2
     (2,500 rows): time travel on the exact data version.
   - Cell 7 trains `rf-100` and `rf-300`, logs metrics, the model and
     `training_nessie_commit` to MLflow.
   - Cell 9 sets the `champion` alias and loads it back through
     `models:/churn_classifier@champion`.
2. **MLflow** — experiment `churn-lakehouse-exact-stack`:
   - open either run → **Parameters** → `training_nessie_commit`
   - **Metrics** → compare `roc_auc` (≈0.799 vs ≈0.785)
   - **Artifacts** → `model/` and `plots/churn_by_contract.png`
   - **Models** → `churn_classifier` → versions 1/2 and the `champion` alias
3. **MinIO** — bucket `warehouse` → `lakehouse/churn_features_<uuid>/`:
   - `data/*.parquet` — the actual table data
   - `metadata/*.metadata.json` — Iceberg metadata (the current snapshot)
4. **Nessie** — `http://localhost:19120/api/v2/trees/main` shows the current
   commit hash. That hash is what MLflow logged.
5. **Dremio (optional)** — `http://localhost:9047` → Nessie source →
   `SELECT * FROM nessie.lakehouse.churn_features LIMIT 20;` (one-time user
   setup with username `admin`; see the Dremio section).
6. **Tableau** — open `Tableau_Churn_Dashboard.twb`, enter the Dremio password,
   and show the **Churn Dashboard** tab. The Dremio driver must be installed
   once (see the Tableau section).

### The Nessie nuance (say this if asked)

Nessie deliberately returns **only the Iceberg snapshot that belongs to the
current Nessie commit**. It keeps the Git-like history itself, so time travel is
done with the Nessie commit hash:

```sql
SELECT * FROM nessie.lakehouse.`churn_features#<commit-hash>`;
```

That is why the MLflow parameter is `training_nessie_commit`, not an old
`training_snapshot_id`. The data version is still exact and reproducible; the
version handle is the catalog commit.

## Reset

Double-click **`Reset Demo.bat`**, or run:

```bash
docker compose --profile dremio down -v
```

This removes the MinIO data, Nessie RocksDB store, MLflow SQLite database and
Dremio data (if the optional profile was used). The notebook's saved outputs
stay in the file. `Start Demo.bat` reloads the data; click Run All once
after the reset to recreate the two runs and v1. A reset creates new Nessie
commit hashes; slide 5
uses hash slots, so it stays valid—read the live values from the notebook or
MLflow (the row counts and metrics are deterministic). The Tableau workbook and
its driver live outside Docker and are not wiped; after the reset, recreate the
Dremio `admin` user and Nessie source, then reopen the workbook and enter the
new password.

## Troubleshooting

- **`docker compose` cannot connect** — `Start Demo.bat` starts Docker
  Desktop if it is installed. If it still fails, open Docker Desktop, wait for
  the engine, and run it again.
- **Port already in use** — change `MLFLOW_PORT`, `JUPYTER_PORT`, `MINIO_API_PORT`,
  `MINIO_CONSOLE_PORT` or `NESSIE_PORT` in a `.env` file next to
  `docker-compose.yml`. Dremio's ports `9047`, `31010`, and `32010` are fixed;
  stop the conflicting app instead.
- **Notebook says `state/ingest_summary.json` is missing** — run the manual
  `spark-submit` command above. `Start Demo.bat` loads the data
  automatically when it is missing.
- **MLflow returns `Invalid Host header`** — the compose file already allows
  the `mlflow:5000` host used inside the Docker network. If you change the
  service name, update `--allowed-hosts`.
- **Spark job is slow on the first run** — the JVM and Iceberg jars are warming
  up; subsequent runs are faster.
- **Docker Desktop crashes** — close other memory-heavy apps. This laptop has
  8 GB total; the full stack measured about 3.3 GB of containers.
- **Tableau says the Dremio driver is missing** — copy
  `Tableau Driver\dremio-jdbc-driver-26.0.5.jar` into
  `%USERPROFILE%\Documents\My Tableau Repository\Drivers`, then restart Tableau.
- **Tableau cannot connect or asks for a password** — start the full stack
  with `Start Demo.bat` (Dremio on port 9047), sign in as `admin` with the
  password chosen in Dremio; the workbook connects to `localhost:31010`.
  Recreate the Dremio source after a reset.

## Files

```
MLflow Exact Stack V2/
├── docker-compose.yml          MinIO, Nessie, MLflow, Spark+Jupyter, optional Dremio
├── Dockerfile.spark            Spark 3.5.9 + Iceberg 1.11.0 + Jupyter + MLflow client
├── Dockerfile.mlflow           MLflow 3.17.2 + boto3 for S3 artifacts
├── conf/spark-defaults.conf    Nessie REST catalog + memory settings
├── data/                       the two source batches (deterministic synthetic churn)
├── jobs/
│   ├── make_data.py            regenerate the source batches
│   └── ingest.py               Spark ingestion, two Nessie commits, time-travel check
├── notebooks/
│   └── lakehouse_mlflow.ipynb  training, MLflow logging, champion alias, chart
├── state/ingest_summary.json   commit hashes + row counts from the last ingestion
├── assets/                     logos + Tableau_Churn_Dashboard.png proof
├── Tableau_Churn_Dashboard.twb live churn dashboard (Dremio -> Tableau)
├── Tableau Driver/             Dremio JDBC driver for the workbook
├── Start Demo.bat              the single launcher: full stack + Dremio
├── Reset Demo.bat              wipe all Docker volumes
├── START HERE.md               the one-page guide for everyone
├── Presentation_Script.md      readable speaker notes / talk track
├── Lakehouse_Explainer.png     one-image visual explainer
├── MLflow_Exact_Stack_V2_Presentation.pptx   the 7-slide V2 deck
└── README.md
```

The V2 deck lives in this folder; its speaker notes are the full talk track
(no separate script). The Q&A slide is the prepared answer set.
