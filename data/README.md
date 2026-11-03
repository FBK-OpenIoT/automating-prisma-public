# Data directory

## Inputs

`metadata/` contains bibliographic exports. The `*_study` files support replication
of the reference identification procedure; `*_validation` files are inputs to the
proposed dataset-oriented search workflow. Export filenames are kept stable.
`study_datasets.json` maps the 94 reference-study DOIs to dataset names.

Full-text inputs remain local in `full_text_pdf/`, `CLAUDE_full_text_pdf/`, and
`full_text_pdf_rag/`. Those directories and generated caches are ignored by Git.

## Recorded results

Existing filenames remain unchanged to preserve the research artifacts and the
links between notebook stages. Files with `CLAUDE_` belong to the supplementary
Claude experiment; unprefixed counterparts belong to the primary Gemini workflow.

| Artifact | Meaning |
| --- | --- |
| `results/df_evaluated_study.csv` | Replicated reference identification corpus |
| `results/*df_evaluated_validation.csv` | Full screening decisions and abstracts |
| `results/*df_screening_passed.csv` | Records retained after screening |
| `results/*df_evaluated_validation_abstract.csv` | Unresolved records requiring full-text processing |
| `results/*review.csv` | Study metadata with datasets obtained from abstracts |
| `results/*review_final.csv` | Final combined study and dataset tables |
| `results/screening/`, `results/eligibility/` | Five Gemini run records and cost summaries |
| `results/CLAUDE_screening/`, `results/CLAUDE_eligibility/` | Supplementary Claude records and costs |
| `results/eligibility_sensitivity/` | Saved complementary full-text experiment |
| `results/datasets_annotation/` | Three independent annotation workbooks |

Abstracts and original rights are discussed in [data sources](../docs/data-sources.md).
To protect recorded results during a rerun, follow the separate-directory setup
in the [workflow guide](../docs/workflow.md).
