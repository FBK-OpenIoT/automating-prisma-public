# Workflow and configuration

## Strategy

The validation workflow has three methodological steps:

1. Structured search: execute database-specific queries to identify papers that
   refer to datasets in the target domain, then normalize and deduplicate exports.
2. Title and abstract screening: apply declared inclusion and exclusion criteria
   with Gemini or Claude and extract named datasets when the abstract supports it.
3. Full-text eligibility: use RAG to extract datasets for retained papers without
   an associated dataset, then combine the results into the final review table.

The main experiment uses a dataset-oriented query, not the broader reference
query. The reference notebook replicates only identification. The complementary
full-text sensitivity experiment is separate from the primary eligibility run.
See [article comparison](article-comparison.md) for verified results and caveats.

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

The main notebooks live in `notebooks/gemini/` and `notebooks/claude/`, with
matching names: `01_identification_screening`, `02_screening_evaluation`, and
`03_full_text_eligibility`. Claude result files retain their historical prefix.

`notebooks/reference/reproduce_identification.ipynb` reconstructs the reference
search corpus. `notebooks/analysis/run_stability_and_costs.ipynb` reads five saved
runs; `full_text_sensitivity.ipynb` executes a separate API experiment. Model
comparison and annotation agreement are also in `notebooks/analysis/`.

## Configuration

Copy `.env.example` to `.env`. Shell variables take precedence. Analysis notebooks
that read saved results need no keys; full-text sensitivity needs Gemini access.
Model IDs must be supported by your account. Historical IDs and
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

## Notebook text

Notebook Markdown identifies the next operation or explains an observed result.
Numerical notes such as the comparison of 59 identified papers with 50 in the
reference study remain next to their outputs. These are historical observations,
not assertions about a future run. General strategy and usage belong here and
in the notebook guide. Scientific prompts and their criteria remain beside the
code that executes them.
