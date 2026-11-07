# Lakehouse + MLflow Quick Start

Keep the whole folder together; every path is relative.

- `Start Demo.bat` starts the full stack and opens the deck/UIs.
- `Reset Demo.bat` wipes all Docker volumes and asks for confirmation.

## Before you start

- Docker Desktop is installed with the WSL2 backend. Start it and wait for the engine.
- Allow about 10 GB free disk for the first image pull, plus space for Tableau Desktop.
- Ports `5000`, `8888`, `9000`, `9001`, `19120`, `9047`, `31010`, and `32010` must be free.

## 1. Reset only if reusing old data

On a fresh machine, skip this step. If Docker already has old volumes, either:

- double-click `Reset Demo.bat` and type `Y`, or
- open PowerShell in this folder and run:

```powershell
docker compose --profile dremio down -v
```

This wipes the old MinIO data, Nessie catalog, MLflow database, and Dremio data. It also removes Dremio's admin user and Nessie source, so do it before creating them. Do not reset after Dremio setup unless you want to redo it.

## 2. Start the full stack

Double-click `Start Demo.bat`.

It starts MinIO, Nessie, MLflow, Spark/Jupyter, and Dremio, loads the two Iceberg versions if the lakehouse is empty, and opens the deck and UIs. The first run pulls images and can take several minutes.

## 3. MinIO login

- URL: <http://localhost:9001>
- Username: `minioadmin`
- Password: `minioadmin`

Buckets: `warehouse` for Iceberg data and `mlflow` for MLflow artifacts. These are local demo credentials only.

## 4. MLflow: create the two runs

On a fresh machine or after a reset, MLflow is empty. This is expected.

Open <http://localhost:8888/lab/tree/notebooks/lakehouse_mlflow.ipynb> and click **Run All** once.

That creates `rf-100` and `rf-300` and makes v1 the `champion` alias.

- MLflow: <http://localhost:5000>
- Experiment: `churn-lakehouse-exact-stack`

If you click **Run All** again, it adds versions and moves the champion.

## 5. Dremio (the BI box)

Open <http://localhost:9047>.

First time (fresh machine or after a reset):

1. Create the admin user with username `admin`; choose your own password. This is not the MinIO password. Keep the username `admin` so the Tableau workbook matches.
2. Add the catalog: **Sources -> + -> Nessie**
   - Name: `nessie`
   - Endpoint: `http://nessie:19120/api/v2`
   - Nessie authentication: **none**
   - Storage: **AWS**
   - AWS root path: `warehouse` (the field already shows `s3://`; do **not** add a leading slash, or it becomes `s3:///warehouse`)
   - Authentication method: **AWS Access Key**
   - AWS access key: `minioadmin`
   - AWS access secret: `minioadmin`
   - Other: add `fs.s3a.path.style.access=true`, `fs.s3a.endpoint=minio:9000`, `dremio.s3.compat=true`; uncheck **Encrypt connection**.
3. Run:

```sql
SELECT * FROM nessie.lakehouse.churn_features LIMIT 20;
```

This shows Dremio's table/query view.

## 6. Tableau churn dashboard

Install Tableau Desktop (the free edition is enough), then copy:

```text
Tableau Driver\dremio-jdbc-driver-26.0.5.jar
```

to:

```text
C:\Users\<you>\Documents\My Tableau Repository\Drivers
```

Restart Tableau. Open `Tableau_Churn_Dashboard.twb` in this folder and enter the Dremio admin password. The **Churn Dashboard** tab shows churn by contract, tenure group, and internet service. Proof image: `assets\Tableau_Churn_Dashboard.png`.

## 7. Other UIs

- Deck: opened automatically; press `Alt+F5` in PowerPoint for Presenter View.
- JupyterLab: <http://localhost:8888>
- MLflow: <http://localhost:5000>
- MinIO: <http://localhost:9001>
- Nessie: <http://localhost:19120/api/v2/trees/main>
- Dremio: <http://localhost:9047>

## If Dremio + notebook feel slow

Docker's WSL memory limit may be tight. Do not raise it above what your PC can spare; see the hardware notes in `README.md` for the tested settings. After changing `C:\Users\<you>\.wslconfig`, run:

```powershell
wsl --shutdown
```

Then restart Docker Desktop and run `Start Demo.bat` again.

## Stop / clean

Stop and keep data:

```powershell
docker compose --profile dremio down
```

Wipe everything:

- double-click `Reset Demo.bat`, or
- run `docker compose --profile dremio down -v`.

The reset also removes the Dremio user and Nessie source, so set them up again after the next start. The Tableau workbook and its driver stay in this folder; reopen the workbook and enter the new Dremio password.
