# Use your own metadata and papers

This repository implements a dataset-oriented review. It supplies executable AQA
examples, not an automatic search-engine client or a universal review protocol.
A different topic requires explicit changes to queries, prompts, and dataset-name
mappings. The following procedure follows the article's identification,
screening, eligibility, and inclusion stages.

## 1. Define the review before searching

Write down the domain, object of study, publication period, document types,
language, inclusion/exclusion criteria, and fields you want to extract. Decide
whether the objective is dataset discovery or a broader literature review.
Requiring dataset terms in a query narrows coverage by design.

Build equivalent queries using each engine's syntax. For example, a Scopus
template for dataset discovery is:

```text
TITLE-ABS-KEY(<DOMAIN_TERMS>)
AND TITLE-ABS-KEY(dataset OR "data set" OR database OR "data repository")
AND PUBYEAR > <YEAR_BEFORE_START> AND PUBYEAR < <YEAR_AFTER_END>
```

Replace the placeholders, add the protocol's qualifiers, and translate the query
for IEEE Xplore and Web of Science. These are searches to execute in the engines;
the notebooks do not submit them. Record the exact query, source, search date,
filters, and exported record count, and retain the original exports unchanged.

## 2. Create a separate private workspace

From the repository root, install dependencies:

```bash
uv sync --locked
```

Create `local/my-review/metadata/review/`. For example, in PowerShell:

```powershell
New-Item -ItemType Directory -Force local/my-review/metadata/review
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Or in a POSIX shell:

```bash
mkdir -p local/my-review/metadata/review
test -f .env || cp .env.example .env
```

Add these settings to `.env`, along with real API keys and supported model IDs:

```dotenv
PRISMA_DATA_DIR=local/my-review
PRISMA_CASE_STUDY_FILTERS=false
```

Leave `PRISMA_RESULTS_DIR` unset to write to `local/my-review/results/`, with
separate `gemini/` and `claude/` folders. Remove any older shell override if it
points at the bundled study results. `local/` is ignored by Git.

## 3. Export and prepare bibliographic metadata

Download metadata from the engines using your own access. Include titles,
abstracts, DOIs, publication years, authors, and the fields needed to enforce the
protocol. The notebooks require DOIs: resolve records without one manually or
extend the identifier handling explicitly; do not silently treat a missing DOI
as a unique study.

Choose one input format:

**Native exports from all three engines.** Save these files in
`local/my-review/metadata/review/`:

| File | Fields consumed by the native adapter |
| --- | --- |
| `ieee.csv` | `DOI`, `Document Title`, `Authors`, `Publication Year`, `Abstract`, `Article Citation Count` |
| `scopus.csv` | `DOI`, `Title`, `Authors`, `Year`, `Abstract`, `Cited by` |
| `wos.xls` | `DOI`, `Article Title`, `Authors`, `Publication Year`, `Abstract`, `Times Cited, All Databases` |

Use a real Excel `.xls` export for WoS; renaming `.xlsx` or a text export does not
convert it. Adapt the loader if your export format differs. The bundled AQA
filters also use IEEE `Date Added To Xplore` and WoS `Indexed Date`; these
study-specific filters and the hardcoded Scopus exclusion list are disabled for
the private workspace. Apply your own publication-date rules during search or
preparation; an indexing date is not necessarily a publication date.

**Normalized CSV from one or more sources.** If you use fewer engines, or their
export schemas differ, create `metadata/review/records.csv` instead. It takes
precedence over all native exports. Required columns are `DOI,Title,Year,Abstract`;
`Authors` is optional and defaults to an empty string. `Citations` is optional.
Preserve source provenance separately or in extra columns. For example:

```csv
DOI,Title,Year,Abstract,Authors
10.0000/example-a,Synthetic example A,2026,"A synthetic abstract for demonstrating the schema.",Example Author
```

That DOI is a schema illustration, not a real research record. Use a CSV writer
to quote commas and multiline abstracts correctly. Records missing DOI, title,
or abstract are dropped by the current preparation logic; review the difference
between the original exports and the prepared table. Normalize identifier spelling
before deduplication: the native pipeline deduplicates by exact DOI value.

`metadata/reference/` and `reference/datasets_by_doi.json` are only needed for
benchmark comparisons. A new review can run stages 01-03 without them. The
reference-replication and historical analysis notebooks are optional, not required
steps of a new review.

## 4. Adapt the executable criteria

Choose `notebooks/gemini/` or `notebooks/claude/`. Work in a separate checkout or
branch when changing the example code. Before API execution, review:

- In 01, the `BatchReviewItem` schema and `is_open_data_relevant_batch` prompt:
  change domain-specific inclusion/exclusion rules and extraction instructions.
- In 01 and 03, harmonization prompts and schemas: agree on the extracted fields
  and naming conventions.
- In 02 and 03, `dataset_map` and `map_partial_sources`: replace AQA-specific
  aliases and reconsider the 20-character name cutoff for your domain.
- In 03, the retrieval query, `ExtractedDatasets` schema, extraction prompt,
  chunk settings, and number of chunks. The shipped query targets AQA datasets.
- In the run-ID cells, choose a distinct ID when recording another Gemini run.

The model-only configuration in `.env` does not change these criteria. If you
want attributes other than datasets, adapt the downstream tables and final
eligibility rule too. The shipped rule includes a study only when a dataset has
been associated with it.

## 5. Run identification and abstract screening

```bash
uv run jupyter notebook
```

Open your provider's `01_identification_screening.ipynb` and execute in order.
Inspect the normalized and deduplicated records before running the API cells.
Configure `.env` for Gemini or Claude as described in the README. API calls are
billable and transmit the supplied text to the provider.

The final export is `results/<provider>/screening_evaluated.csv`. Inspect reasons,
resolve `maybe` decisions through human review, and record manual decisions and
their reasons separately. Then run `02_screening_evaluation.ipynb`. It writes:

- `screening_retained.csv`: records not labeled `no`;
- `abstract_review.csv`: retained studies with dataset names from abstracts;
- `full_text_candidates.csv`: retained studies still lacking a dataset.

The code retains unresolved `maybe` records; it does not implement or log manual
adjudication for you. If there are no full-text candidates, skip the RAG execution
and use the abstract-review table as the dataset-bearing corpus, after review.

To save that corpus under the final-table name, copy `abstract_review.csv` to
`final_review.csv` within the same provider folder. Do not run the PDF stage on
an empty candidate set.

## 6. Obtain PDFs and associate them with studies

Using the candidate DOI list, obtain full texts through the engine links,
publisher pages, or authorized repositories. Download only content you are
entitled to use and send to the configured providers. The notebooks do not
download papers, bypass access restrictions, or perform OCR.

Store PDFs under `local/my-review/full_text/gemini/` or `claude/`. To share one
PDF folder across providers, set `PRISMA_PDF_DIR` to that folder in `.env`.
Keep only PDFs belonging to the current candidate set. Track unavailable papers
and your manual resolution separately.

Create `manifest.csv` in the same PDF directory:

```csv
Filename,DOI
paper-a.pdf,10.0000/example-a
paper-b.pdf,10.0000/example-b
```

Use real candidate DOIs and exact filenames, including extension and case. Each
filename and DOI must be unique. The manifest permits arbitrary PDF filenames
and prevents a missing PDF from shifting results onto another paper. Without it,
only unambiguous normalized title matches are accepted, so a manifest is the
preferred route for new data. Scanned PDFs need separate text extraction/OCR
before the supplied loader can provide useful text.

## 7. Run full-text eligibility and review the final table

Run `03_full_text_eligibility.ipynb` in order. It reads the local PDFs, builds or
reuses a private cache, extracts and harmonizes dataset names, and combines them
with the abstract results by manifest DOI or verified title. Unknown or ambiguous
associations raise an error. Missing extraction results are reported for manual
resolution, not assigned by row position.

Inspect `results/<provider>/final_review.csv`. Verify the DOI-to-paper association,
dataset names, excluded/unavailable records, and remaining uncertainty. Record
search counts, duplicates, exclusions, full-text availability, and final inclusion
counts for the PRISMA report. The repository does not generate that report or
substitute for human quality control.

For maximum dataset recall, the paper recommends considering full-text extraction
across the entire screened corpus; the primary example restricts it to records
without an extracted dataset. The separate sensitivity notebook is an AQA
experiment, with limitations documented in [article comparison](article-comparison.md),
and needs its own adaptation before reuse.

Keep `.env`, PDFs, manifests, caches, and private exports out of public commits.
The `local/` workspace is ignored; the bundled abstracts and their source terms
are discussed separately in [data rights](data-sources.md).
