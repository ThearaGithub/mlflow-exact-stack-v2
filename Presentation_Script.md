# MLflow Exact Stack V2 — Presentation Script

This is the readable version of the speaker notes in `MLflow_Exact_Stack_V2_Presentation.pptx`.

Use **Presenter View** (`Alt+F5`) during the presentation: the audience sees the slides, and you see these notes. This file is for reading, printing, or practising.

## Speaker order

Using the group order on slide 1:

| # | Speaker | Slides | Section | Target time |
|---|---|---|---|---|
| 1 | Khon Sotheara | 1–2 | Opening + architecture | 1:15 |
| 2 | Khann Udomvirak | 3–4 | Six pieces + running proof | 1:30 |
| 3 | Chea Sela | 5 | The MLflow layer | 1:00 |
| 4 | Theng Sivchheng | 6–7 | Demo + Q&A lead | 1:15 |

Total: about 5 minutes. All four can join the Q&A; Theng leads the close.

## Before you present

- Start the stack with `Start Demo.bat`.
- If you reset first, click **Run All** once in the notebook so MLflow has the two runs and the `v1` champion.
- On a fresh machine, create the Dremio `admin` user and Nessie source once, then open the Tableau workbook.
- Put the deck in Presenter View, not Slideshow mode, if you want the notes on your screen.

## Slide 1 — Opening: Where MLflow fits — Khon Sotheara

Open with his question: where does MLflow fit, and how would you build it.

This version does not approximate anything — every box in his drawing is the real open-source component, running in Docker on this laptop.

The five-minute run: the completed picture, the six pieces, what is actually running, the MLflow bridge, the demo, then the questions we expect. Everything shown is live, not a mock-up.

## Slide 2 — Architecture: The architecture, made real — Khon Sotheara

Walk left to right.

Sources are two CSV batches; a Spark ingestion job lands them in MinIO as Parquet, under Iceberg tables, versioned by the Nessie catalog.

From that lake two engines read the same tables: Dremio for the BI branch on top, Spark for ML at the bottom, feeding Jupyter. MLflow is the violet layer that records what each model learned.

Green outline means running and verified today, all nine boxes including the Tableau dashboard. Say clearly: MinIO is the S3 API, so this is the same architecture, not a toy.

Tableau Desktop Free Edition is the dashboard tool; the workbook is included and reads Dremio.

**Handoff:** Khann Udomvirak takes slides 3–4.

## Slide 3 — Recipe: Six pieces, assembled bottom-up — Khann Udomvirak

Six pieces, bottom-up. You do not buy a lakehouse; you assemble it:

- storage
- table format
- catalog
- ingestion
- compute
- ML lifecycle

Name the versions: Spark 3.5.9, Iceberg 1.11, Nessie 0.109, MLflow 3.17.2, Dremio 26.

The role of each:

- MinIO gives the S3 API.
- Iceberg gives ACID tables on files.
- Nessie gives Git-style commits to the whole warehouse.
- Spark and Dremio read the same data.
- MLflow is the governance layer.

In production you swap MinIO for S3 and local Spark for managed Spark without touching the notebook.

## Slide 4 — Proof: What is actually running — Khann Udomvirak

This is the honest hardware slide.

On an 8 GB laptop the whole stack, Dremio included, uses about 3.3 GB of containers; MLflow is the biggest at 1.6 GB.

The trick was capping the WSL VM at 6 GB: at the old 7.4 GiB setting the first Dremio image pull froze the host. Dremio has a hard 4 GB minimum, which is why it is the heaviest piece.

The 3.3 GB figure is containers only; Tableau is a desktop app outside Docker.

Nine of nine boxes are live: Dremio and the Tableau dashboard were verified on 2026-10-27.

Rule for the demo: Dremio and Tableau do not run while the notebook kernel is active on this laptop.

**Handoff:** Chea Sela takes slide 5.

## Slide 5 — The MLflow layer: From data version to model version — Chea Sela

This is the slide that answers where MLflow fits.

The lakehouse side has two Nessie commits: 2,000 rows that we train on, 2,500 rows that represent current data. The table name can carry a commit hash, so we train on the exact historical version.

The exact hashes change on a fresh run, so the slide shows hash slots; read the live values from the notebook.

Each run logs `training_nessie_commit`, the row count, and the metrics. The better model, `rf-100` with ROC AUC 0.799 against 0.785, becomes version 1 of `churn_classifier`, and the `champion` alias points at it. A serving job loads `models:/churn_classifier@champion`.

If he asks why not a snapshot id: Nessie exposes only the snapshot for the current commit; the commit hash is the Git-like handle.

**Handoff:** Theng Sivchheng takes the demo and Q&A.

## Slide 6 — Demo: Four minutes, four stops — Theng Sivchheng

Demo script.

Double-click `Start Demo.bat`: it starts Docker Desktop if needed, brings up the stack, waits for health, makes sure the two data versions are loaded, and opens the deck and the UIs.

If you reset first, MLflow starts empty: open Jupyter and **Run All** once to recreate the two runs and the `v1` champion; the saved outputs are refreshed.

If the stack was preserved, the two runs are already loaded, so just open Jupyter to show them and do **not** Run All.

In MLflow: experiment `churn-lakehouse-exact-stack`, open a run. **Parameters** shows `training_nessie_commit`; **Metrics** compares ROC AUC; **Models** shows `churn_classifier` and the `champion` alias.

At about 3:30 open Dremio on port 9047, add the Nessie source once, and run:

```sql
SELECT * FROM nessie.lakehouse.churn_features LIMIT 20;
```

Then open `Tableau_Churn_Dashboard.twb`, enter the Dremio admin password, and show the **Churn Dashboard**: churn by contract, tenure, and internet.

The Dremio JDBC driver must be installed once. The first build takes several minutes; later runs are cached.

## Slide 7 — Q&A: Questions we expect — Theng Sivchheng, then all four

Close with the three likely questions and the one-liner: MLflow does not replace the lakehouse; it makes the lakehouse auditable.

If he asks about the dashboard box, say it is delivered: Dremio runs and Tableau Desktop Free Edition shows the included churn workbook live.

If he asks about scale, the same compose file is the recipe; managed services replace the local ones one by one, and the notebook proves the code does not change.

If he asks, **“What are you actually building?”** say:

> We are building a versioned storage system. The churn data is only the test load: it lets us prove that the same table can serve a dashboard and train a model, and that MLflow can trace the model back to the exact data version.

If he asks whether the data is real: no, it is deterministic synthetic data. The point is the system and the traceability, not churn-prediction accuracy.

## One-line close

> MLflow does not replace the lakehouse — it makes every model traceable to its data.
