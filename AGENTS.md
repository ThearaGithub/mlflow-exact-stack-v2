# AGENTS.md

Presentation project (paper 2310.08697, Group 6) answering the professor's follow-up: "where does MLflow fit in the lakehouse, and how would you build it?" V2 (the exact Docker stack) is the active deliverable; V1 (pip-only) is a frozen backup; plus the original deck. Not a git repo; no build/test/lint — verification means running the demo and keeping docs consistent.

## Layout
- `Paper Presentation/` — original graded deck (frozen), paper PDF, rehearsal scripts.
- `MLflow PIP Only V1/` — frozen backup of the first follow-up demo: deck, `followup_script.md`, `qa_prep.md`, and the pip-only `Demo/`. Do not edit; V2 is the active deliverable.
- `MLflow Exact Stack V2/` — **active deliverable**: Docker replica of the professor's diagram (MinIO, Nessie, Spark/Jupyter, MLflow; Dremio optional profile, verified running) plus the live `Tableau_Churn_Dashboard.twb` (Tableau Desktop Free Edition; three churn charts over Dremio) and its own 7-slide deck (rebuilt 2026-10-25, Tableau update 2026-10-27; speaker notes are the talk track, Q&A slide is the answer set). Self-documented in its README and `START HERE.md`.
- `building-presentation-on-2310-08697-paper.json` — 19 MB OpenCode session export, not project config. Do not read or parse.
- `thread-*.md` — ~2 MB exported chat transcript from the session that built V2 and its deck. Useful history; not authoritative — verify against files.

## PIP-only demo (V1)
- Run `Demo/lakehouse_mlflow_demo.ipynb` top-to-bottom, then `Demo/See the Results.bat` (or run `mlflow ui` from inside `Demo/`).
- Disposable per-run artifacts in `Demo/`: `lake_warehouse/`, `lake_catalog.db`, `mlruns/`, `mlflow.db`. Delete all four for a clean presentation state — stop the Jupyter kernel and dashboard first, they lock the `.db` files.

## Exact stack (V2)
- Requires Docker Desktop (the single launcher `Start Demo.bat` starts it if installed), starts the full stack including Dremio, loads the two Iceberg versions only when Nessie does not match `state/ingest_summary.json`, and opens the deck + UIs. `Reset Demo.bat` (or `docker compose --profile dremio down -v`) wipes all volumes; force ingestion with the `spark-submit` command from the README.
- The launcher's skip is deliberate: it preserves an existing lakehouse and saved notebook state. It does not execute the notebook. After a reset, click Run All once to create the two runs and v1 `champion`; on a preserved stack with the verified headless run, open the notebook and show them. Running it again adds versions (v2+) and moves `champion`. Slide 5 uses hash slots, not fixed values, so a reset does not invalidate the deck; the live notebook/MLflow show the new commits.
- Dremio **is verified running on this laptop** (2026-10-25) with the WSL VM capped at 6 GB (`~/.wslconfig`: `memory=6GB`, `swap=4GB`). The old 7.4 GiB cap plus a Dremio image pull froze the host — keep the 6 GB cap, pull only while the stack is stopped, and don't run the notebook (Spark kernel) while Dremio is up. Measured with full stack + Dremio: ~3.3 GB of containers, ~0.7 GB host RAM free. Portable setup steps are in `README.md` and `START HERE.md`; use `Start Demo.bat` there and keep the 6 GB cap on 8 GB machines (10 GB on 16 GB). Bigger-machine setup is untested. Spark driver 768 MB, Nessie 512 MB heap, MLflow `--workers=1` are deliberate memory tuning — do not raise them.
- The Tableau dashboard is included: `Tableau_Churn_Dashboard.twb` uses a custom SQL relation on `nessie.lakehouse.churn_features` over the Dremio native connector at `localhost:31010`; it has three bar charts and percentage labels. The Dremio JDBC driver is bundled in `Tableau Driver/` and must be copied to `%USERPROFILE%\Documents\My Tableau Repository\Drivers` before opening the workbook. Tableau Desktop Free Edition is enough; it is a desktop app outside Docker, so it is excluded from the 3.3 GB container figure. Proof: `assets/Tableau_Churn_Dashboard.png`.
- Versions are pinned deliberately: Spark 3.5.9, Iceberg 1.11.0, Nessie 0.109.0, MLflow 3.17.2, Dremio 26.0.5, MinIO and aws-cli image digests. Do not bump casually.
- Both demos bind port 5000, and V2 also holds 8888 (JupyterLab) and 9047 (Dremio, optional) — run one demo at a time.

## MLflow 3.17 gotchas (non-obvious)
- Default tracking store is `sqlite:///mlflow.db` in the **process CWD**, not `mlruns/` (that folder holds only model artifacts). `mlflow ui` must run from the folder containing `mlflow.db`, or Experiments looks empty while runs exist elsewhere. A file-store backend would additionally require `MLFLOW_ALLOW_FILE_STORE=true`.
- V1 logs `training_snapshot_id`; V2 logs `training_nessie_commit` (Nessie only exposes the current commit's snapshot; time travel uses the Nessie commit hash). Do not cross-copy parameter names between variants.
- Windows cleanup: killing the `mlflow ui` parent leaves `python.exe ... multiprocessing-fork` children holding port 5000 — kill all `python.exe` matching `mlflow|uvicorn|multiprocessing-fork`; stop ipykernel before deleting `.db` files.

## .bat files
- `Start Demo.bat` is the only launcher; it always uses the full Dremio profile. `Reset Demo.bat` is the only utility.
- CRLF + ASCII only. The Write tool emits LF — write via PowerShell:
  `[System.IO.File]::WriteAllText($path, (($lines -join "`r`n") + "`r`n"), [System.Text.Encoding]::ASCII)`
- Every bat starts with `cd /d "%~dp0"` and pauses on failure so double-click errors stay visible.

## Environment
- Windows + PowerShell. Demo packages are already installed in the system Python (`python`, 3.14 — `python3` does not exist): mlflow 3.17.1, pyiceberg, scikit-learn, pandas, pyarrow, jupyterlab. Do not create a venv for local runs.

## Doc consistency is the only "test"
- A V2 change must update every synced artifact: V2 deck speaker notes (the talk track), V2 README, and `START HERE.md` when setup behavior changes. V1 is frozen — do not sync edits into it.
- Grep before and after edits for: `training_snapshot_id`, `training_nessie_commit`, `champion`, `models:/churn_classifier@champion`, notebook filenames, ports.
- Known weak spots (fix if touched, never copy blindly): V2 has no standalone script/qa md (deck notes + Q&A slide carry it); reset and forced ingestion are manual CLI commands; the Dremio first-user + Nessie source setup is manual, not scripted; the Tableau driver install is a manual copy; the portable setup in `README.md`/`START HERE.md` is untested on a bigger machine. The Tableau workbook was verified on the 8 GB laptop with Dremio live, but not on a 16 GB machine.
