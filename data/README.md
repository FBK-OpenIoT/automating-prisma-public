# Data directory

The bundled data describe the AQA case study. For a new review use a separate
private directory and `PRISMA_DATA_DIR`; see [your own data](../docs/using-your-data.md).

```text
data/
  metadata/
    review/       ieee.csv, scopus.csv, wos.xls
    reference/    ieee.csv, scopus.csv, wos.xls
  reference/
    datasets_by_doi.json
    pdf_manifests/    gemini.csv, claude.csv
  annotations/
    annotator_1.xlsx, annotator_2.xlsx, annotator_3.xlsx
  results/
    reference/identified_records.csv
    gemini/
      screening_evaluated.csv
      screening_retained.csv
      full_text_candidates.csv
      abstract_review.csv
      final_review.csv
      screening/      run_1_records.csv ... run_5_records.csv, cost_summary.csv
      eligibility/    run_1_records.csv ... run_5_records.csv, cost_summary.csv
      sensitivity/    records.csv, cost_summary.csv
    claude/
      screening_evaluated.csv
      screening_retained.csv
      full_text_candidates.csv
      abstract_review.csv
      final_review.csv
      screening/      records.csv, cost_summary.csv
      eligibility/    records.csv, cost_summary.csv
  full_text/          local only; excluded from Git
    gemini/
    claude/
    sensitivity/
```

`metadata/review/` contains the proposed dataset-oriented search exports.
`metadata/reference/` supports replication of the broader reference search.
The reference JSON maps 94 benchmark DOIs to dataset names; annotations are
independent human classifications, so they are separate from generated results.
The curated PDF manifests associate recorded reference-manager filenames with
candidate DOIs, including four truncated or punctuation-modified titles. They
contain metadata only. The Claude manifest covers 28 of 29 candidates; the
missing paper still requires manual availability review.

Both providers use the same table names inside their own directories:

| Table | Content |
| --- | --- |
| `screening_evaluated.csv` | Every screened record, decision, reason, and abstract |
| `screening_retained.csv` | Records not excluded after screening |
| `full_text_candidates.csv` | Retained records without an extracted dataset |
| `abstract_review.csv` | Review records with datasets extracted from abstracts |
| `final_review.csv` | Combined abstract and full-text review |

Gemini has five saved repetitions; Claude has one supplementary execution.
`cost_summary.csv` contains stage measurements; the notebook cost formulas are
historical estimates. Files have been moved and renamed without changing their
contents. Historical notebook outputs may still display the original filenames.

Keep full-text PDFs, manifests, extracted document stores, and embeddings local.
Abstracts remain included with their existing rights, as explained in
[data sources](../docs/data-sources.md).
