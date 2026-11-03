# Notebook guide

Run `uv sync --locked`, then `uv run jupyter notebook` from the repository.
All notebooks resolve paths from the checkout, including when Jupyter starts in
a notebook subdirectory. No local library installation is required.

## Main experiments

Choose a provider and execute its three notebooks in order:

| Stage | Gemini | Claude |
| --- | --- | --- |
| Identification and abstract screening | [01](gemini/01_identification_screening.ipynb) | [01](claude/01_identification_screening.ipynb) |
| Evaluation and full-text preparation | [02](gemini/02_screening_evaluation.ipynb) | [02](claude/02_screening_evaluation.ipynb) |
| Full-text eligibility and final review | [03](gemini/03_full_text_eligibility.ipynb) | [03](claude/03_full_text_eligibility.ipynb) |

Stages 01 and 03 call external APIs. Stage 02 operates on local tables. Claude's
full-text stage uses Gemini embeddings. Configure `.env` before starting API runs.
For a new review, follow [Use your own data](../docs/using-your-data.md). Results
are separated by provider under the active data directory.

## Analysis of recorded results

| Notebook | Purpose | API calls |
| --- | --- | --- |
| [Model comparison](analysis/compare_models.ipynb) | Compare study and dataset coverage | None |
| [Dataset annotation agreement](analysis/dataset_annotation_agreement.ipynb) | Agreement between annotators | None |
| [Run stability and costs](analysis/run_stability_and_costs.ipynb) | Compare five saved runs | None |
| [Full-text sensitivity](analysis/full_text_sensitivity.ipynb) | Run RAG on the complementary screening subset | Gemini |

## Reference baseline

[Reproduce identification](reference/reproduce_identification.ipynb) reconstructs
the reference search corpus from the study exports. It does not repeat the
reference study's manual screening and eligibility decisions.

Outputs and numeric comparison notes are retained historical observations.
General methodological descriptions live in the [workflow guide](../docs/workflow.md).
The [article comparison](../docs/article-comparison.md) distinguishes verified
agreement from limitations of the saved artifacts.

`_shared.py` contains local configuration, input, matching, and cache utilities.
Do not execute it as a pipeline. New runs can overwrite tables; see the workflow
guide for a separate results directory.
