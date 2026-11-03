"""Execute analysis on temporary data, leaving committed outputs untouched."""
import ast
import json
from pathlib import Path
import shutil

import nbformat
import pytest
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
OFFLINE = ["gemini/02_screening_evaluation", "claude/02_screening_evaluation",
           "reference/reproduce_identification", "analysis/dataset_annotation_agreement",
           "analysis/run_stability_and_costs", "analysis/compare_models"]


@pytest.mark.parametrize("prefix", ["", "CLAUDE_"])
def test_screening_exports_next_stage_input(prefix, tmp_path):
    import pandas as pd

    name = ("claude/" if prefix else "gemini/") + "01_identification_screening.ipynb"
    notebook = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    export = next("".join(c["source"]) for c in notebook["cells"]
                  if 'df_evaluated_final.to_csv(result_path' in "".join(c["source"]))
    frame = pd.DataFrame([dict(DOI="10.0000/synthetic", Title="Synthetic study",
                               Authors="Example", Year=2026, Abstract="Synthetic abstract",
                               Include="maybe", Reason="Needs full text", **{"Data Source": ""})])
    exec(compile(export, name, "exec"), dict(df_evaluated_final=frame, result_path=str(tmp_path) + "/"))
    path = tmp_path / "screening_evaluated.csv"
    loaded = pd.read_csv(path, keep_default_na=False)
    pd.testing.assert_frame_equal(loaded, frame)


@pytest.mark.parametrize("provider", ["gemini", "claude"])
def test_bundled_identification_keeps_original_corpus(provider, tmp_path, monkeypatch):
    from anthropic import Anthropic
    from google import genai

    def no_api(*args, **kwargs):
        raise AssertionError("Identification must stop before API initialization")

    monkeypatch.setattr(Anthropic, "__init__", no_api)
    monkeypatch.setattr(genai, "Client", no_api)
    monkeypatch.setenv("PRISMA_DATA_DIR", str(ROOT / "data"))
    monkeypatch.setenv("PRISMA_RESULTS_DIR", str(tmp_path))
    monkeypatch.setenv("PRISMA_CASE_STUDY_FILTERS", "true")
    namespace = {}
    notebook = nbformat.read(ROOT / f"notebooks/{provider}/01_identification_screening.ipynb", as_version=4)
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        if "require_environment(" in cell.source:
            break
        exec(compile(cell.source, "bundled identification", "exec"), namespace)
    assert len(namespace["df_all"]) == 145


@pytest.mark.parametrize("provider", ["gemini", "claude"])
def test_custom_review_preparation_without_benchmark(provider, tmp_path, monkeypatch):
    """Exercise new-data ingestion and evaluation without API calls or AQA cutoffs."""
    import pandas as pd
    from anthropic import Anthropic
    from google import genai

    def no_api(*args, **kwargs):
        raise AssertionError("Metadata preparation must not initialize an API client")

    monkeypatch.setattr(Anthropic, "__init__", no_api)
    monkeypatch.setattr(genai, "Client", no_api)

    metadata = tmp_path / "metadata/review"
    metadata.mkdir(parents=True)
    pd.DataFrame([
        dict(DOI="10.0000/a", Title="Study A", Authors="A", Year=2026, Abstract="Synthetic abstract A"),
        dict(DOI="10.0000/b", Title="Study B", Authors="B", Year=2026, Abstract="Synthetic abstract B"),
    ]).to_csv(metadata / "records.csv", index=False)
    monkeypatch.setenv("PRISMA_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("PRISMA_RESULTS_DIR", raising=False)
    monkeypatch.delenv("PRISMA_CASE_STUDY_FILTERS", raising=False)
    namespace = {}
    notebook = nbformat.read(ROOT / f"notebooks/{provider}/01_identification_screening.ipynb", as_version=4)
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        if "require_environment(" in cell.source or "client = Anthropic(" in cell.source:
            break
        exec(compile(cell.source, "custom review", "exec"), namespace)
    frame = namespace["df_all"].copy()
    assert len(frame) == 2
    assert frame["Year"].tolist() == [2026, 2026]
    frame["Include"] = ["yes", "maybe"]
    frame["Reason"] = "Synthetic decision"
    frame["Data Source"] = ["ToyDataset", ""]
    results = tmp_path / "results" / provider
    results.mkdir(parents=True, exist_ok=True)
    frame.to_csv(results / "screening_evaluated.csv", index=False)
    notebook = nbformat.read(ROOT / f"notebooks/{provider}/02_screening_evaluation.ipynb", as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            exec(compile(cell.source, "custom evaluation", "exec"), namespace)
    assert len(pd.read_csv(results / "abstract_review.csv")) == 1
    assert len(pd.read_csv(results / "full_text_candidates.csv")) == 1


@pytest.mark.parametrize("provider", ["gemini", "claude"])
def test_saved_full_text_postprocessing(provider, tmp_path, monkeypatch):
    """Exercise the actual PDF-to-study joins and final exports without LLM calls."""
    import os
    import re
    import pandas as pd
    from _shared import data_directory, results_directory, pdf_directory, reference_datasets, align_full_text_results

    results = tmp_path / "results"
    shutil.copytree(ROOT / "data/results", results)
    monkeypatch.setenv("PRISMA_DATA_DIR", str(ROOT / "data"))
    monkeypatch.setenv("PRISMA_RESULTS_DIR", str(results))
    raw = results / provider / "eligibility" / ("run_5_records.csv" if provider == "gemini" else "records.csv")
    namespace = dict(pd=pd, re=re, json=json, os=os, Path=Path,
                     df_results=pd.read_csv(raw), DOCUMENT_FOLDER=pdf_directory(provider),
                     data_directory=data_directory, results_directory=results_directory,
                     reference_datasets=reference_datasets, align_full_text_results=align_full_text_results)
    notebook = nbformat.read(ROOT / f"notebooks/{provider}/03_full_text_eligibility.ipynb", as_version=4)
    started = False
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        if "df_evaluated_final = df_results.copy()" in cell.source:
            started = True
        if started:
            exec(compile(cell.source, "saved full-text postprocessing", "exec"), namespace)
    final = pd.read_csv(results / provider / "final_review.csv")
    assert list(final.columns) == ["DOI", "Title", "Authors", "Year", "Data Source"]
    assert final["DOI"].is_unique
    assert not final["Data Source"].isna().any()


@pytest.mark.parametrize("path", sorted((ROOT / "notebooks").rglob("*.ipynb")), ids=lambda p: p.relative_to(ROOT / "notebooks").as_posix())
def test_notebook_syntax_and_imports(path):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        tree = ast.parse("".join(cell["source"]))
        compile(tree, str(path), "exec")
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), {})


@pytest.mark.parametrize("name", OFFLINE)
@pytest.mark.parametrize("launch_from", ["root", "notebook"])
def test_offline_notebook(name, launch_from, tmp_path):
    results = tmp_path / "results"
    shutil.copytree(ROOT / "data/results", results)
    notebook = nbformat.read(ROOT / "notebooks" / (name + ".ipynb"), as_version=4)
    # The notebook writes only to this temporary result directory.
    notebook.cells.insert(0, nbformat.v4.new_code_cell(
        "import os\n"
        f"os.environ['PRISMA_DATA_DIR'] = {str(ROOT / 'data')!r}\n"
        "os.environ['PRISMA_CASE_STUDY_FILTERS'] = 'true'\n"
        f"os.environ['PRISMA_RESULTS_DIR'] = {str(results)!r}\n"
    ))
    directory = ROOT if launch_from == "root" else (ROOT / "notebooks" / name).parent
    client = NotebookClient(notebook, timeout=180, kernel_name="python3",
                            resources={"metadata": {"path": str(directory)}})
    client.execute()
    if name.endswith("02_screening_evaluation"):
        provider = "claude" if name.startswith("claude/") else "gemini"
        assert (results / provider / "abstract_review.csv").is_file()
        assert (results / provider / "full_text_candidates.csv").is_file()
