# Automating PRISMA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

**Automating PRISMA** is a research-driven framework designed to automate and standardize the systematic literature review (SLR) process. It strictly aligns with the **PRISMA 2020** (Preferred Reporting Items for Systematic Reviews and Meta-Analyses) standards to ensure methodological rigor and reproducibility.

By integrating Large Language Models (LLMs)—specifically **Google Gemini**—and **Retrieval-Augmented Generation (RAG)** systems, the framework accelerates the labor-intensive phases of identification, screening, and eligibility assessment. It aims to reduce human error and variability while maintaining high transparency through deterministic outputs, fallback mechanisms, and "human-in-the-loop" verification.

---

## 🚀 Key Features

- **Standardized Identification**: Supports structured bibliographic exports from multiple databases (Scopus, IEEE Xplore, Web of Science).
- **LLM-Powered Screening**: Rapid title and abstract screening using Gemini with deterministic filtering logic based on inclusion/exclusion criteria.
- **RAG-Based Eligibility**: Deep analysis of full-text PDFs. Documents are segmented, embedded (FAISS), and retrieved to evaluate complex eligibility rules via generative AI.
- **Metadata Harmonization**: Automatically extracts and standardizes study attributes into a consistent schema for final reporting.
- **Reliability Assessment**: Built-in support for Inter-Rater Reliability (Fleiss' Kappa) to validate automated results against human annotations.
- **Reproducibility**: Entire pipeline documented in modular Jupyter notebooks, managed by `uv` for consistent dependency environments.

---

## 📂 Project Structure

```text
automating-prisma/
├── data/
│   ├── full_text_pdf/      # Input PDFs for full-text eligibility assessment
│   ├── metadata/           # Raw bibliographic exports (CSV/XLS) from Scopus, IEEE, WoS
│   ├── results/            # Output datasets from screening, eligibility, and evaluation
│   └── study_datasets.json # Mapping of study DOIs to analyzed datasets
├── notebooks/
│   ├── 01_identification_screening.ipynb # Identification & Title/Abstract Screening
│   ├── 02_screening_evaluation.ipynb     # Evaluation & Metadata Harmonization
│   ├── 03_eligibility_RAG.ipynb          # RAG-based Full-text Eligibility Assessment
│   ├── datasets_annotation.ipynb         # External rater agreement analysis
│   ├── sensitivity_analysis.ipynb        # Model reliability and cost-performance analysis
│   └── replicated_study_workflow.ipynb   # End-to-end replication of the reference study
├── vectorstore/            # Locally generated FAISS vector embeddings
├── pyproject.toml          # Project dependencies (managed by uv)
└── .env                    # Environment variables (API keys, model selection)
```

---

## 🛠️ Getting Started

### Prerequisites
- **Python 3.11+**
- **[uv](https://github.com/astral-sh/uv)**: Extremely fast Python package installer and resolver.
- **Google Gemini API Key**: Required for LLM operations.

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/RomeoSilvestri/automating-prisma.git
   cd automating-prisma
   ```

2. **Install dependencies**:
   Using `uv` ensures a reproducible virtual environment:
   ```bash
   uv sync
   ```

3. **Configure environment**:
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_api_key_here
   MODEL=gemini-2.5-flash
   MODEL_SUPERVISOR=gemini-2.5-pro
   MODEL_EMBEDDING=gemini-embedding-2
   ```

---

## 🔄 Workflow

The framework follows the sequential stages of the PRISMA flow:

### 1. Identification & Screening
Run **`01_identification_screening.ipynb`**. 
- Processes bibliographic exports from major databases.
- Uses Gemini to filter papers based on abstracts against defined inclusion criteria.
- Outputs a preliminary list of "Pass" studies for full-text review.

### 2. Full-Text Eligibility (RAG)
Run **`03_eligibility_RAG.ipynb`**.
- *Setup*: Place full-text PDFs in `data/full_text_pdf/`.
- The notebook segments PDFs, creates vector embeddings, and uses a RAG pipeline to answer specific eligibility questions for each paper.

### 3. Evaluation & Harmonization
Run **`02_screening_evaluation.ipynb`**.
- Compares automated screening results against validation datasets (if available).
- Harmonizes metadata extracted during previous steps into a final review table.

### 4. Reliability & Performance Analysis
- **`datasets_annotation.ipynb`**: Analyzes agreement between different raters (automated vs. human) using Fleiss' Kappa.
- **`sensitivity_analysis.ipynb`**: Evaluates model performance across multiple runs, including cost tracking and execution time metrics.

---

## 📖 Case Study: Action Quality Assessment (AQA)

This repository includes data and configurations used for a systematic review on **Action Quality Assessment**. The included datasets in `data/metadata/` and `data/full_text_pdf/` reflect this specific research area, demonstrating the framework's ability to handle complex computer vision literature.

---

## ⚖️ License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

Developed by [RomeoSilvestri](https://github.com/RomeoSilvestri).

