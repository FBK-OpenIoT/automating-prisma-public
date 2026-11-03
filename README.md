# Automating PRISMA

Automating PRISMA provides research notebooks for literature identification,
abstract screening, and full-text dataset extraction with retrieval augmented
generation. It includes Gemini and Claude workflows and recorded results from
an Action Quality Assessment (AQA) case study.

The workflow supports a PRISMA-aligned review process. Reviewers define criteria,
resolve uncertain decisions, and complete the reporting. Low-temperature model
settings do not guarantee identical responses between runs.

## Install

Use Python 3.11 or later and [uv](https://docs.astral.sh/uv/).
Clone the public repository maintained by the unit:

```bash
git clone https://github.com/FBK-OpenIoT/automating-prisma-public.git
cd automating-prisma-public
uv sync --locked
```

From an existing checkout, run only `uv sync --locked`.

## Quickstart

Explore saved results without API credentials:

```bash
uv run jupyter notebook
```

Open [model comparison](notebooks/analysis/compare_models.ipynb) to compare recorded
reviews or [annotator agreement](notebooks/analysis/dataset_annotation_agreement.ipynb)
to inspect the dataset annotations.
Outputs are retained historical snapshots, not regenerated after source changes.

For new LLM runs, copy `.env.example` to `.env` and fill the keys and supported
model IDs. Gemini screening uses `GEMINI_API_KEY`, `MODEL`, and `MODEL_SUPERVISOR`.
Full-text extraction also uses `MODEL_EMBEDDING`. Claude uses `CLAUDE_API_KEY`,
`MODEL_CLAUDE`, and `MODEL_SUPERVISOR_CLAUDE`; its full-text workflow still
requires Gemini credentials for embeddings.

## Workflow

Choose `notebooks/gemini/` or `notebooks/claude/` and run:

1. `01_identification_screening.ipynb`: normalize exports and screen abstracts.
2. `02_screening_evaluation.ipynb`: evaluate screening and prepare full-text inputs.
3. `03_full_text_eligibility.ipynb`: extract datasets from local PDFs and combine results.

Start Jupyter anywhere inside this checkout. The notebooks locate their shared
local helper file automatically. LLM runs send text to external providers and may incur
charges. See [configuration](docs/workflow.md) before running them.

To run a new review, follow [Use your own data](docs/using-your-data.md): define
the protocol, export search metadata, screen records, obtain permitted full texts,
and map PDFs to candidate DOIs. Separate data and result folders preserve the AQA
case study. Domain-specific prompts and name mappings must be adapted explicitly.

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
- [Use your own metadata and papers](docs/using-your-data.md)
- [Data sources and rights](docs/data-sources.md)
- [Comparison with the reference article](docs/article-comparison.md)
- [Data directory guide](data/README.md)
- [Historical DOI list](DOI_list.md)

## Development

```bash
uv sync --locked
uv run pytest
```

Tests check imports, offline processing, and caches with synthetic embeddings.
Offline notebooks use temporary result copies. Tests make no LLM calls.
This is a notebook workspace: `uv` manages dependencies without installing a library.

## Citation and license

Cite the associated study when publication details are available and identify
the revision used. Author: [Romeo Silvestri](https://github.com/RomeoSilvestri).
Original software and documentation use the [MIT license](LICENSE).
