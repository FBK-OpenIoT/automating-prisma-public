# Workflow and configuration

## Inputs and results

`data/metadata/` contains the IEEE, Scopus, and Web of Science exports.
`data/study_datasets.json` maps reference DOIs to datasets. `data/results/`
contains recorded screening, review, annotation, cost, and sensitivity tables.

By default, reruns write to `data/results/`, replacing tables or appending cost
rows. To preserve recorded results, copy that directory to `runs/my-experiment`
and set `PRISMA_RESULTS_DIR=runs/my-experiment` in `.env` or the shell. The copy
supplies annotation and historical files needed by analysis notebooks. All
notebooks honor this setting. Restart the kernel after changing configuration.

## Execution order

Run Gemini 01, 02, then 03, or Claude 01, 02, then 03. Screening writes
`df_evaluated_validation.csv`; evaluation produces `review.csv` and
`df_evaluated_validation_abstract.csv`; full-text processing combines them into
`review_final.csv`. Claude files have the `CLAUDE_` prefix. Repeated Gemini
experiments use the editable `RUN_ID` cell.

The replication notebook reconstructs the reference study. Sensitivity analysis
reads five saved runs; eligibility sensitivity executes a separate API experiment.

## Configuration

Copy `.env.example` to `.env`. Shell variables take precedence. Analysis notebooks
need no keys. Model IDs must be supported by your account. Historical IDs and
token counts appear in cost CSVs. Notebook cost formulas are study-era estimates,
not current provider quotes. Check rates before budgeting a run.

Obtain full texts through your own permitted access. Use `data/full_text_pdf/`
for Gemini, `data/CLAUDE_full_text_pdf/` for Claude, and `data/full_text_pdf_rag/`
for sensitivity. Keep filenames compatible with notebook title matching.
Missing or empty PDF directories produce an explanatory error.

## Local caches

`.cache/prisma/{gemini,claude,sensitivity}/` holds JSON document stores and FAISS
vectors. These contain full-text fragments and must remain local. No pickle is
read or written. PDF contents, filenames, embedding model, and chunk settings
control reuse. Changes rebuild the cache. To force rebuilding, close the notebook
and delete only its provider cache folder. Concurrent writes to one cache are
not supported.

## Reproducibility

`uv.lock` fixes Python dependency resolution. Retained outputs predate these
source changes. Hosted model revisions, retrieval, API failures, rate limits,
and human decisions can affect new results. Validate decisions and extracted
names before using them in a review.
