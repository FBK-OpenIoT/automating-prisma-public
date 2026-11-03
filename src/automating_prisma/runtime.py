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
    raise FileNotFoundError("Start Jupyter from this repository or its notebooks directory.")


def load_environment() -> None:
    load_dotenv(project_root() / ".env", override=False)


def require_environment(*names: str) -> None:
    missing = [name for name in names if not os.environ.get(name, "").strip()]
    if missing:
        raise ValueError("Configure these variables in .env: " + ", ".join(missing))


def data_directory() -> str:
    return str(project_root() / "data") + os.sep


def results_directory() -> str:
    """Use an optional separate results directory; default to the study workspace."""
    root = project_root()
    path = Path(os.environ.get("PRISMA_RESULTS_DIR", "data/results"))
    if not path.is_absolute():
        path = root / path
    path.mkdir(parents=True, exist_ok=True)
    return str(path.resolve()) + os.sep


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
