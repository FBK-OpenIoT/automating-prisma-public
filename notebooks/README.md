# Notebook guide

Run `uv sync --locked`, then `uv run jupyter notebook` from the root or this folder.
Outputs are retained historical executions, not automatically refreshed results.
See [workflow configuration](../docs/workflow.md) for separate results and PDFs.

| Notebook | Purpose | API calls |
| --- | --- | --- |
| `01_identification_screening.ipynb` | Gemini screening | Gemini |
| `02_screening_evaluation.ipynb` | Screening evaluation | None |
| `03_eligibility_RAG.ipynb` | Full-text extraction and final review | Gemini |
| `CLAUDE_01_identification_screening.ipynb` | Claude screening | Claude |
| `CLAUDE_02_screening_evaluation.ipynb` | Claude evaluation | None |
| `CLAUDE_03_eligibility_RAG.ipynb` | Full-text extraction and final review | Claude and Gemini embeddings |
| `replicated_study_workflow.ipynb` | Reference study reconstruction | None |
| `GEMINI_CLAUDE_comparison.ipynb` | Compare saved reviews | None |
| `datasets_annotation.ipynb` | Annotator agreement | None |
| `sensitivity_analysis.ipynb` | Saved-run agreement and costs | None |
| `eligibility_sensitivity.ipynb` | Separate full-text experiment | Gemini |

For each provider, run 01, 02, then 03. Analysis notebooks run independently
against included results. LLM notebooks write tables and append cost rows; use a
separate results directory to preserve the recorded data.
