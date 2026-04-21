# Automating PRISMA

Automating PRISMA is a research-driven framework designed to automate and standardize the systematic literature review process by aligning with the **PRISMA 2020** (Preferred Reporting Items for Systematic Reviews and Meta-Analyses) standards. 

By integrating Large Language Models (LLMs), specifically Google Gemini, and Retrieval-Augmented Generation (RAG) systems, the framework accelerates the labor-intensive phases of identification, screening, and eligibility assessment. It aims to reduce human error and variability while maintaining high methodological rigor through deterministic outputs, fallback mechanisms for uncertain cases, and "human-in-the-loop" verification.

## Project Structure

```text
automating-prisma/
├── data/               # Bibliographic exports, validation datasets, and input PDFs
├── notebooks/          # Core PRISMA workflow implementation
│   ├── 01_identification_screening.ipynb  # Identification & Title/Abstract Screening
│   ├── 02_screening_evaluation.ipynb      # Evaluation & Metadata Harmonization
│   ├── 03_eligibility_RAG.ipynb           # RAG-based Full-text Eligibility
│   └── replicated_study_workflow.ipynb    # End-to-end replication workflow
├── vectorstore/        # FAISS index storage (locally generated)
├── pyproject.toml      # Project dependencies and configuration (uv)
└── .env                # Environment variables (not tracked)
```

## Key Features

- **Standardized Identification**: Uses structured query templates to support reproducible bibliographic searches across multiple databases.
- **Automated Screening**: Leverages LLMs for rapid title and abstract screening with deterministic logic to filter studies against inclusion/exclusion criteria.
- **RAG-powered Eligibility**: Performs deep analysis of full-text manuscripts. Documents are segmented into chunks, encoded as dense vector embeddings, and retrieved to evaluate complex eligibility rules via generative AI.
- **Metadata Harmonization**: Automatically extracts and standardizes study attributes into a consistent schema, ensuring transparency and traceability.
- **Reproducibility**: Every step of the pipeline is documented within Jupyter notebooks, allowing for full replication of the systematic review.

## Getting Started

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (required for dependency management)
- Google Gemini API Key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/automating-prisma.git
   cd automating-prisma
   ```

2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```

3. Configure environment variables:
   Create a local `.env` file in the root directory (do not commit secrets). Example contents:
   ```env
   GEMINI_API_KEY=your_api_key_here
   MODEL=gemini-2.5-flash
   MODEL_SUPERVISOR=gemini-2.5-pro
   MODEL_EMBEDDING=models/text-embedding-004
   ```

   Security note: Do not commit `.env` or other secret values to version control.

## Workflow

The framework follows a sequential pipeline reflecting the PRISMA flow:

1. **Identification & Screening**: Run `01_identification_screening.ipynb`. This notebook processes bibliographic exports (CSV/XLS) from Scopus, IEEE, and WoS, then uses Gemini to filter papers based on their abstracts.
2. **Eligibility (Full-Text)**: Use `03_eligibility_RAG.ipynb` for papers that passed the initial screening. It builds a local vector store from PDFs and uses RAG to assess eligibility against detailed criteria.
   Note: Place your legally-obtained full-text PDFs in `data/full_text_pdf/` (create this folder if it does not exist) before running the eligibility notebook.
3. **Evaluation & Harmonization**: Use `02_screening_evaluation.ipynb` to compare automated results against validation datasets and harmonize the final metadata for reporting.
4. **End-to-End**: The `replicated_study_workflow.ipynb` provides a condensed version of the entire workflow for reproducing the reference study.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

