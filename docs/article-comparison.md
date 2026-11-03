# Comparison with the reference article

This check uses the supplied 50-page manuscript, *A retrieval-augmented LLM
framework for PRISMA-aligned systematic reviews: a case study on action quality
assessment*. Section and table numbers refer to that version. The manuscript
itself is not distributed in this repository. No decisions, prompts, study tables,
or historical outputs were changed to obtain agreement with it.

## Scope and methodology

The repository contains a concrete AQA case study, not a domain-independent
implementation of every procedure described in the methodological framework.
The documentation therefore describes PRISMA alignment and human review duties
without claiming that all reporting, quality control, or manual adjudication is
automated.

| Article | Repository correspondence |
| --- | --- |
| Sections 4.1-4.2; Table 5 | `reference/reproduce_identification.ipynb` replicates identification only; the saved table has 152 records. The evaluation benchmark has 94 studies and 47 named datasets, excluding `self-created`. |
| Sections 4.3-4.4.2; Figures 7-8 | Provider notebooks screen title/abstract batches of 15, use yes/no/maybe decisions, apply structured schemas and retries, and harmonize dataset names. Gemini decoding uses temperature 0, top-k 1, top-p 1. |
| Sections 4.4.3-4.4.4; Figure 9 | Full-text notebooks use 2,000-character chunks, 400-character overlap, MMR with lambda 0.9, and up to five retrieved chunks per paper. Their retrieval query targets AQA datasets. |
| Section 5.3.2 | `analysis/run_stability_and_costs.ipynb` compares five saved screening runs and five saved eligibility runs. Eligibility uses the fixed primary input, not a new input chosen from each screening replicate. |
| Section 5.3.4 | The Claude experiment is a single portability run. It uses the same Gemini embedding component and is not a second five-run stability study. |

Paths in this table are relative to `notebooks/`. A local guard keeps retrieval
counts at least one for tiny synthetic inputs; for the study-sized indexes the
formulas remain k=floor(N/3), fetch_k=floor(N/2). The current cache uses local
JSON/FAISS files rather than pickle and can reuse matching embeddings. A warm
cache does not reproduce the cold-index timings reported in the article.

## Main saved results agree

The following counts were checked directly from the included CSVs and
`data/reference/datasets_by_doi.json`, using exact DOI intersections and semicolon-separated
dataset names, excluding `self-created` from dataset counts.

| Metric | Gemini | Claude | Article |
| --- | --- | --- | --- |
| Records entering screening | 145 | 145 | Table 8 |
| Records retained after screening | 96 | 95 | Table 8 |
| Final studies | 91 | 87 | Table 8 |
| Reference studies recovered, out of 94 | 67 | 64 | Table 8 |
| Study detection rate | 71.28% | 68.09% | Table 8 |
| Unique extracted datasets | 65 | 57 | Table 9 |
| Reference datasets recovered, out of 47 | 40 | 38 | Table 9 |
| Dataset extraction recall | 85.11% | 80.85% | Table 9 |
| Additional datasets | 25 | 19 | Table 9 |

The final corpora share 84 studies and 54 datasets, also matching Tables 8-9.
Sources: [Gemini review](../data/results/gemini/final_review.csv),
[Claude review](../data/results/claude/final_review.csv), and
[reference mapping](../data/reference/datasets_by_doi.json). Retained notebook outputs may
represent different experiment runs; they are historical records, not refreshed
copies of these tables.

## Reproduction limits and points to reconcile

- **Sensitivity coverage (Section 5.3.3; Table B.2).** The article describes
  full-text analysis of all 75 papers with datasets already found in abstracts.
  The saved sensitivity records contain 64 PDF rows. The notebook also applies
  title-prefix matching and further mismatch filters, including a maximum of
  three extracted names in its final diagnostic view. This is not an exhaustive
  per-paper set-difference calculation. The saved artifacts alone do not establish
  coverage of all 75 papers or automatically reconstruct Table B.2. Establish the
  missing-input mapping and manual reconciliation before claiming exact reproduction.
- **Claude full-text input (Table 8; Table B.5).** There are 29 unresolved records
  in the abstract table, but 28 rows in the saved Claude eligibility file.
  The paper reports 29 candidate records and 28 extraction calls. Those are
  distinct quantities. The curated Claude PDF manifest now identifies those 28
  files, but the reason for the remaining candidate's absence is not documented.
  That DOI is `10.1007/978-3-031-61678-5_6`; resolve its availability manually.
- **Manual review (Sections 3.2 and 5.1).** The saved Gemini screening table has
  three `maybe` decisions; evaluation retains every decision other than `no`.
  The article describes manual resolution of three uncertain cases. No separate
  adjudication log demonstrates that resolution. Do not interpret retention of
  `maybe` as a logged manual decision. General sampling and human quality-control
  procedures in the paper are not automated by these notebooks.
- **Title alignment in eligibility.** The archived runs used sorted row positions
  to associate metadata and extracted names. For future runs this has been replaced
  with manifest DOI joins, or unambiguous normalized titles when no manifest is
  supplied. Missing PDFs are reported and cannot shift one paper's results onto
  another paper. The saved study tables and outputs have not been recomputed.
- **Harmonization detail.** The harmonization prompt guidelines match the article,
  but current screening requests contain row IDs and dataset-name fields, whereas
  Figure 8 labels its input as title/abstract. Explicit name mappings and a
  20-character cutoff are also present in post-processing. Treat the notebook
  source as the executable specification rather than assuming a verbatim figure.
- **Historical environment and costs.** Models are chosen through `.env`; the
  historical configuration uses Gemini Flash/Pro and, for portability, Claude
  Sonnet/Opus with Gemini embeddings. Current provider availability and prices
  are not verified by offline tests. The cache format and dependency cleanup are
  infrastructure changes; saved outputs and measured costs remain unchanged.

These observations document the current artifacts. They do not invalidate the
matching main results or establish exact reproduction of every supplementary
analysis. The appropriate next research step is to reconcile inputs and manual
decisions explicitly, rather than modifying historical tables to match the paper.
