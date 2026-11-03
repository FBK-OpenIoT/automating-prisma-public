# Workflow and configuration

## Strategy

1. Execute declared, database-specific searches and export bibliographic metadata.
2. Normalize and deduplicate records, then screen titles and abstracts and extract
   named datasets where the abstract supports it.
3. Obtain full texts for retained papers without a dataset, extract and harmonize
   dataset names with RAG, and combine the review tables.

The AQA reference notebook replicates identification only. Its broader search is
distinct from the dataset-oriented review query. Complementary full-text
sensitivity is a separate experiment. See the [article comparison](article-comparison.md).

## Execution and paths

Choose `notebooks/gemini/` or `notebooks/claude/` and execute 01, 02, then 03.
The stages write `screening_evaluated.csv`, then `abstract_review.csv` and
`full_text_candidates.csv`, and finally `final_review.csv`. Tables live below
`results/gemini/` or `results/claude/` in the active data directory.

The reference notebook writes `results/reference/identified_records.csv`.
Annotation agreement reads `annotations/annotator_*.xlsx`. Model comparison reads
both provider folders. Stability analysis reads the five saved Gemini run files;
it does not generate five new runs. Full-text sensitivity makes new Gemini calls.

See the [data guide](../data/README.md) for the full layout and
[your own data](using-your-data.md) for an independent review.

## Configuration

Copy `.env.example` to `.env` if needed. Shell variables take precedence; restart
the kernel after changes. Use model IDs supported by your account.

| Setting | Default |
| --- | --- |
| `PRISMA_DATA_DIR` | `data` in this checkout |
| `PRISMA_RESULTS_DIR` | `<data directory>/results` |
| `PRISMA_PDF_DIR` | `<data directory>/full_text/<provider>`; sensitivity uses `sensitivity` |
| `PRISMA_CASE_STUDY_FILTERS` | True for bundled `data/`, false for another data directory |

Paths may be absolute or relative to the checkout root. The results setting is
the parent of the model folders. To inspect copied historical runs, copy the
whole `data/results/` tree to your desired results directory; annotation and
reference inputs remain in the active data directory. For new reviews no copy
of study results is needed.

Analysis of saved results needs no credentials. Full-text sensitivity needs
Gemini access. Claude full-text extraction also uses Gemini embeddings.

## Full-text association

PDFs are acquired manually through permitted access, not downloaded by notebooks.
Use a local `manifest.csv` with `Filename,DOI` to map PDF files to candidate
records independently of sort order. Without a manifest, the notebooks accept
only unambiguous normalized title matches. Unknown or ambiguous matches stop
with an error. Missing extraction results are reported for manual resolution and
are not assigned another study's metadata.
For the standard bundled full-text folders, curated mappings in
`data/reference/pdf_manifests/` provide the association when no local manifest
exists. A manifest in the PDF folder always takes precedence.

## Caches and reproducibility

`.cache/prisma/{gemini,claude,sensitivity}/` contains local JSON document stores
and FAISS vectors. These include article fragments and must remain private.
No pickle is read or written. PDF contents, filenames, embedding model, and
chunk settings determine cache reuse. Close the notebook before removing its
provider cache to force a rebuild; concurrent writes to one cache are unsupported.

`uv.lock` fixes dependency resolution. Saved outputs are historical snapshots and
are not refreshed by source edits. Warm-cache runs do not reproduce cold-index
timings. Hosted model revisions, API failures, retrieval, and human decisions may
change new results. Notebook cost formulas are historical estimates; check rates
before budgeting new calls.

Notebook Markdown identifies operations and records observations. Numeric notes
such as 59 identified papers versus 50 in the reference remain beside the
historical output. General strategy belongs here; executable prompts remain
beside the code. Changing the topic requires adapting those prompts and mappings.
