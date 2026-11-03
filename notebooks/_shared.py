"""Notebook infrastructure. Importing this module never contacts an API."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv


def project_root(start: str | Path | None = None) -> Path:
    start = Path(start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "notebooks").is_dir():
            return candidate
    raise FileNotFoundError("Start Jupyter inside this repository.")


def load_environment() -> None:
    load_dotenv(project_root() / ".env", override=False)


def require_environment(*names: str) -> None:
    missing = [name for name in names if not os.environ.get(name, "").strip()]
    if missing:
        raise ValueError("Configure these variables in .env: " + ", ".join(missing))


def data_directory() -> str:
    path = Path(os.environ.get("PRISMA_DATA_DIR", "data"))
    if not path.is_absolute():
        path = project_root() / path
    return str(path.resolve()) + os.sep


def results_directory(provider: str | None = None) -> str:
    """Use an optional separate results directory; default to the study workspace."""
    root = project_root()
    path = Path(os.environ.get("PRISMA_RESULTS_DIR", str(Path(data_directory()) / "results")))
    if not path.is_absolute():
        path = root / path
    if provider:
        if provider not in {"gemini", "claude", "reference"}:
            raise ValueError("Unknown results provider")
        path = path / provider
    path.mkdir(parents=True, exist_ok=True)
    return str(path.resolve()) + os.sep


def metadata_directory(kind: str = "review") -> str:
    if kind not in {"review", "reference"}:
        raise ValueError("Unknown metadata corpus")
    return str(Path(data_directory()) / "metadata" / kind) + os.sep


def pdf_directory(provider: str) -> str:
    path = Path(os.environ.get("PRISMA_PDF_DIR", str(Path(data_directory()) / "full_text" / provider)))
    if not path.is_absolute():
        path = project_root() / path
    return str(path.resolve())


def reference_datasets() -> dict:
    path = Path(data_directory()) / "reference" / "datasets_by_doi.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def case_study_filters() -> bool:
    default = Path(data_directory()) == project_root() / "data"
    return os.environ.get("PRISMA_CASE_STUDY_FILTERS", str(default)).lower() in {"true", "1", "yes"}


def review_records():
    """Optional normalized input; avoids requiring exports from all three engines."""
    import pandas as pd

    path = Path(metadata_directory()) / "records.csv"
    if not path.is_file():
        return None
    frame = pd.read_csv(path)
    required = {"DOI", "Title", "Year", "Abstract"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError("records.csv is missing columns: " + ", ".join(sorted(missing)))
    if "Authors" not in frame:
        frame["Authors"] = ""
    frame["Citations"] = frame.get("Citations", 0)
    return frame.dropna(subset=["DOI", "Title", "Abstract"])


def align_full_text_results(metadata, extracted, folder: str):
    """Join extracted names to metadata by manifest DOI or unambiguous title."""
    import re
    import pandas as pd

    def doi(value):
        return re.sub(r"^(?:https?://(?:dx\.)?doi.org/|doi:\s*)", "", str(value).strip().lower())

    left = metadata.copy()
    right = extracted.copy()
    manifest_path = Path(folder) / "manifest.csv"
    # Explicitly curated filename mappings support the archived AQA inputs,
    # whose reference-manager filenames include truncation and punctuation changes.
    if not manifest_path.is_file() and Path(data_directory()) == project_root() / "data":
        provider = Path(folder).name
        if Path(folder).resolve() == (Path(data_directory()) / "full_text" / provider).resolve():
            bundled_manifest = Path(data_directory()) / "reference" / "pdf_manifests" / (provider + ".csv")
            if bundled_manifest.is_file():
                manifest_path = bundled_manifest
    if manifest_path.is_file():
        manifest = pd.read_csv(manifest_path, keep_default_na=False)
        if not {"Filename", "DOI"}.issubset(manifest.columns):
            raise ValueError("manifest.csv requires Filename and DOI columns")
        if "PDF Filename" not in right:
            raise ValueError("Extraction results must preserve PDF Filename")
        manifest["_key"] = manifest["DOI"].map(doi)
        left["_key"] = left["DOI"].map(doi)
        if manifest["Filename"].duplicated().any() or manifest["_key"].duplicated().any():
            raise ValueError("Manifest filenames and DOIs must be unique")
        right = right.merge(manifest[["Filename", "_key"]], left_on="PDF Filename", right_on="Filename", how="left", validate="one_to_one")
        if right["_key"].isna().any():
            raise ValueError("Some PDFs are not mapped in manifest.csv")
    else:
        normalize = lambda value: " ".join(re.findall(r"\w+", str(value).casefold()))
        left["_key"] = left["Title"].map(normalize)
        right["_key"] = right["Title"].map(normalize)
    if left["_key"].duplicated().any() or right["_key"].duplicated().any():
        raise ValueError("Ambiguous study mapping: provide a unique Filename/DOI manifest")
    if not set(right["_key"]).issubset(set(left["_key"])):
        raise ValueError("PDFs do not match candidate studies; check manifest.csv or titles")
    merged = left.drop(columns=["Data Source"], errors="ignore").merge(
        right[["_key", "Data Source"]], on="_key", how="left", validate="one_to_one")
    missing = int(merged["Data Source"].isna().sum())
    if missing:
        print(f"[REVIEW] {missing} candidate studies have no PDF/extraction result; resolve manually.")
    present = merged["Data Source"].fillna("").astype(str).str.strip().ne("")
    columns = ["DOI", "Title", "Authors", "Year", "Data Source"]
    return merged.loc[present, columns].reset_index(drop=True)


def cache_directory(name: str) -> str:
    if name not in {"gemini", "claude", "sensitivity"}:
        raise ValueError("Unknown cache namespace")
    return str(project_root() / ".cache" / "prisma" / name)


def cache_fingerprint(folder: str, model: str, chunk_size: int, overlap: int) -> str:
    directory = Path(folder)
    pdfs = sorted(p for p in directory.iterdir() if p.suffix.lower() == ".pdf") if directory.is_dir() else []
    if not pdfs:
        raise FileNotFoundError(f"Add your locally obtained full-text PDFs to {directory}")
    digest = hashlib.sha256(json.dumps([model, chunk_size, overlap, 1]).encode())
    for pdf in pdfs:
        digest.update(pdf.name.encode())
        digest.update(hashlib.sha256(pdf.read_bytes()).digest())
    return digest.hexdigest()


def load_cached_index(path: str, embeddings, fingerprint: str):
    """Read only JSON and FAISS, never pickle. Old or incomplete caches are rebuilt."""
    import faiss
    from langchain_core.documents import Document
    from langchain_community.docstore.in_memory import InMemoryDocstore
    from langchain_community.vectorstores import FAISS

    directory = Path(path)
    try:
        data = json.loads((directory / "documents.json").read_text(encoding="utf-8"))
        if data["fingerprint"] != fingerprint:
            return None
        if hashlib.sha256((directory / "index.faiss").read_bytes()).hexdigest() != data["index_sha256"]:
            return None
        index = faiss.read_index(str(directory / "index.faiss"))
        mapping = {int(k): v for k, v in data["mapping"].items()}
        documents = {key: Document(**value) for key, value in data["documents"].items()}
        if index.ntotal != len(mapping) or any(key not in documents for key in mapping.values()):
            return None
        return FAISS(embeddings, index, InMemoryDocstore(documents), mapping)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError):
        return None


def save_cached_index(vectorstore, path: str, fingerprint: str) -> None:
    import faiss

    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    documents = {}
    for key in vectorstore.index_to_docstore_id.values():
        document = vectorstore.docstore.search(key)
        documents[key] = {"id": document.id, "page_content": document.page_content, "metadata": document.metadata}
    data = {"fingerprint": fingerprint, "mapping": vectorstore.index_to_docstore_id,
            "documents": documents}
    # Publish metadata last so interrupted writes cannot look like a complete cache.
    index_path = directory / "index.faiss"
    faiss.write_index(vectorstore.index, str(index_path.with_suffix(".tmp")))
    data["index_sha256"] = hashlib.sha256(index_path.with_suffix(".tmp").read_bytes()).hexdigest()
    index_path.with_suffix(".tmp").replace(index_path)
    metadata = directory / "documents.json"
    temporary = directory / "documents.tmp"
    temporary.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    temporary.replace(metadata)
