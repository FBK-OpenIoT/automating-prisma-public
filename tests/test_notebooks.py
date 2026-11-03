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
    path = tmp_path / (prefix + "df_evaluated_validation.csv")
    loaded = pd.read_csv(path, keep_default_na=False)
    pd.testing.assert_frame_equal(loaded, frame)


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
        f"os.environ['PRISMA_RESULTS_DIR'] = {str(results)!r}\n"
    ))
    directory = ROOT if launch_from == "root" else (ROOT / "notebooks" / name).parent
    client = NotebookClient(notebook, timeout=180, kernel_name="python3",
                            resources={"metadata": {"path": str(directory)}})
    client.execute()
    if name.endswith("02_screening_evaluation"):
        prefix = "CLAUDE_" if name.startswith("claude/") else ""
        assert (results / (prefix + "review.csv")).is_file()
        assert (results / (prefix + "df_evaluated_validation_abstract.csv")).is_file()
