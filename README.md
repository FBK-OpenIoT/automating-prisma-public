# Automating PRISMA

Automating PRISMA provides research notebooks for literature identification,
abstract screening, and full-text dataset extraction with retrieval augmented
generation. It includes Gemini and Claude workflows and recorded results from
an Action Quality Assessment (AQA) case study.

The workflow supports a PRISMA-aligned review process. Reviewers define criteria,
resolve uncertain decisions, and complete the reporting. Low-temperature model
settings do not guarantee identical responses between runs.

## Install

Use Python 3.11 or later and [uv](https://docs.astral.sh/uv/). From this checkout:

```bash
uv sync --locked
```

## Quickstart

Explore saved results without API credentials:

```bash
uv run jupyter notebook
```

Open `notebooks/GEMINI_CLAUDE_comparison.ipynb` to compare recorded reviews or
`notebooks/datasets_annotation.ipynb` to inspect annotator agreement.
Outputs are retained historical snapshots, not regenerated after source changes.

For new LLM runs, copy `.env.example` to `.env` and fill the keys and supported
model IDs. Gemini screening uses `GEMINI_API_KEY`, `MODEL`, and `MODEL_SUPERVISOR`.
Full-text extraction also uses `MODEL_EMBEDDING`. Claude uses `CLAUDE_API_KEY`,
`MODEL_CLAUDE`, and `MODEL_SUPERVISOR_CLAUDE`; its full-text workflow still
requires Gemini credentials for embeddings.

## Workflow

Run these notebooks in order, or their matching `CLAUDE_` variants:

1. `01_identification_screening.ipynb`: normalize exports and screen abstracts.
2. `02_screening_evaluation.ipynb`: evaluate screening and prepare full-text inputs.
3. `03_eligibility_RAG.ipynb`: extract datasets from local PDFs and combine results.

Start Jupyter from the root or `notebooks/`. `uv sync` installs shared helpers
for either location. LLM runs send text to external providers and may incur
charges. See [configuration](docs/workflow.md) before running them.

## Data and copyright

Exports, abstracts, annotations, result tables, and notebook outputs are retained.
Full-text papers, private manuscripts, credentials, and RAG caches remain local
and are excluded from Git. MIT covers original software and documentation;
third-party texts retain their rights and source terms. Inclusion does not
assert unrestricted redistribution or place those texts under MIT.
See [data sources and rights](docs/data-sources.md).

## Documentation

- [Notebook guide](notebooks/README.md)
- [Workflow and configuration](docs/workflow.md)
- [Data sources and rights](docs/data-sources.md)
- [Release preparation](docs/release.md)
- [Change log](CHANGELOG.md)

## Development

```bash
uv sync --locked
uv run pytest
uv run python scripts/check_release.py
uv build
```

Tests check imports, offline processing, and caches with synthetic embeddings.
Offline notebooks use temporary result copies. Tests make no LLM calls.

## Citation and license

Cite the associated study when publication details are available and identify
the revision used. Author: [Romeo Silvestri](https://github.com/RomeoSilvestri).
Original software and documentation use the [MIT license](LICENSE).
