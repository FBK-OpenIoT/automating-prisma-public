# Data sources and rights

IEEE Xplore, Scopus, and Web of Science exports, abstracts, processed tables,
and notebook outputs are intentionally retained. Availability online does not
establish redistribution permission. This project does not assert an open
redistribution license for every third-party abstract.

Source and institutional agreements remain relevant:

- [IEEE Xplore terms](https://ieeexplore.ieee.org/Xplorehelp/overview-of-ieee-xplore/terms-of-use)
- [Elsevier API policies](https://dev.elsevier.com/policy.html), which cover API
  use cases and do not replace the agreement governing an exported dataset
- [Web of Science](https://clarivate.com/academia-government/scientific-and-academic-research/research-discovery-and-referencing/web-of-science/)
- [Crossref metadata rights](https://www.crossref.org/documentation/retrieve-metadata/)

MIT covers original code and documentation, granting no additional rights to
publisher texts, metadata, articles, or external AQA datasets referenced by DOI.

Full-text PDFs, private manuscripts, extracted text stores, and embeddings remain
local. RAG caches contain article text even without a PDF extension. Git ignore
rules exclude the standard input folders and generated full-text artifacts.

Screening sends titles and abstracts to Gemini or Claude. Full-text workflows
send extracted text to Google's embedding service and selected context to the
chosen LLM provider. Private Git visibility does not prevent this transfer;
confirm the permissions and provider settings applicable to your work.
