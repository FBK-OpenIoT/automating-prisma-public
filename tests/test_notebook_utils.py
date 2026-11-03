from pathlib import Path
import json

import pytest
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from _shared import (
    project_root, require_environment, cache_fingerprint,
    load_cached_index, save_cached_index,
)


class LocalEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text):
        return [float(len(text)), float(sum(map(ord, text)) % 101), 1.0]


def test_root_from_notebooks():
    root = Path(__file__).resolve().parents[1]
    assert project_root(root / "notebooks") == root


def test_missing_configuration_is_actionable(monkeypatch):
    monkeypatch.delenv("PRISMA_TEST_MISSING", raising=False)
    with pytest.raises(ValueError, match="PRISMA_TEST_MISSING"):
        require_environment("PRISMA_TEST_MISSING")


def test_cache_round_trip_and_invalidation(tmp_path):
    pdfs = tmp_path / "pdfs"
    pdfs.mkdir()
    pdf = pdfs / "example.pdf"
    pdf.write_bytes(b"synthetic test content, not an article")
    fingerprint = cache_fingerprint(str(pdfs), "test-model", 2000, 400)
    embedding = LocalEmbeddings()
    original = FAISS.from_documents([
        Document(page_content="synthetic dataset alpha", metadata={"source": "example.pdf"}),
        Document(page_content="synthetic dataset beta", metadata={"source": "example.pdf"}),
    ], embedding)
    cache = str(tmp_path / "cache")
    save_cached_index(original, cache, fingerprint)
    restored = load_cached_index(cache, embedding, fingerprint)
    assert restored.index.ntotal == 2
    query = "synthetic dataset alpha"
    assert restored.similarity_search(query)[0] == original.similarity_search(query)[0]
    assert not list(Path(cache).glob("*.pkl"))
    assert load_cached_index(cache, embedding, "changed-settings") is None
    pdf.write_bytes(b"changed synthetic content")
    assert cache_fingerprint(str(pdfs), "test-model", 2000, 400) != fingerprint
    assert cache_fingerprint(str(pdfs), "test-model-2", 2000, 400) != fingerprint
    (Path(cache) / "documents.json").write_text("{broken", encoding="utf-8")
    assert load_cached_index(cache, embedding, fingerprint) is None


def test_empty_pdf_input(tmp_path):
    with pytest.raises(FileNotFoundError, match="full-text PDFs"):
        cache_fingerprint(str(tmp_path), "test", 2000, 400)


@pytest.mark.parametrize("name", ["gemini/03_full_text_eligibility", "claude/03_full_text_eligibility", "analysis/full_text_sensitivity"])
def test_notebook_index_build_and_reuse(name, tmp_path):
    """Run each real notebook's index builder with synthetic texts and embeddings."""
    import ast
    import os
    from collections import Counter
    from types import SimpleNamespace
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    root = Path(__file__).resolve().parents[1]
    notebook = json.loads((root / "notebooks" / (name + ".ipynb")).read_text(encoding="utf-8"))
    source = next("".join(c["source"]) for c in notebook["cells"]
                  if "def build_or_load_index" in "".join(c["source"]))
    definition = next(node for node in ast.parse(source).body
                      if isinstance(node, ast.FunctionDef) and node.name == "build_or_load_index")
    loads = []

    class Loader:
        def __init__(self, path):
            self.path = path

        def load(self):
            loads.append(self.path)
            return [Document(page_content="Synthetic exercise dataset. " * 100)]

    fake_client = SimpleNamespace(models=SimpleNamespace(count_tokens=lambda **kwargs: SimpleNamespace(total_tokens=20)))
    namespace = dict(os=os, Counter=Counter, MODEL_EMBEDDING="synthetic",
                     API_KEY="synthetic", GEMINI_API_KEY="synthetic",
                     CHUNK_SIZE=2000, CHUNK_OVERLAP=400, _total_embedding_tokens=0,
                     GoogleGenerativeAIEmbeddings=lambda **kwargs: LocalEmbeddings(),
                     cache_fingerprint=cache_fingerprint, load_cached_index=load_cached_index,
                     save_cached_index=save_cached_index, PyPDFLoader=Loader,
                     RecursiveCharacterTextSplitter=RecursiveCharacterTextSplitter,
                     FAISS=FAISS, clean_text=lambda text: text,
                     client=fake_client, gemini_client=fake_client)
    exec(compile(ast.Module(body=[definition], type_ignores=[]), name, "exec"), namespace)
    pdfs = tmp_path / "pdfs"
    pdfs.mkdir()
    pdf = pdfs / "synthetic.PDF"
    pdf.write_bytes(b"synthetic fixture")
    build = namespace["build_or_load_index"]
    first, _, count = build(str(pdfs), str(tmp_path / "cache"))
    assert count > 0
    second, _, cached_count = build(str(pdfs), str(tmp_path / "cache"))
    assert cached_count == count
    assert len(loads) == 1  # Loading cached vectors must not reload or embed PDFs.
    pdf.write_bytes(b"changed fixture")
    build(str(pdfs), str(tmp_path / "cache"))
    assert len(loads) == 2
