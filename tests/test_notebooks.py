"""Execute analysis on temporary data, leaving committed outputs untouched."""
import ast
import json
import os
from pathlib import Path
import shutil

import nbformat
import pytest
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
OFFLINE = ["02_screening_evaluation", "CLAUDE_02_screening_evaluation",
           "replicated_study_workflow", "datasets_annotation",
           "sensitivity_analysis", "GEMINI_CLAUDE_comparison"]


@pytest.mark.parametrize("path", sorted((ROOT / "notebooks").glob("*.ipynb")), ids=lambda p: p.stem)
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
def test_offline_notebook(name, tmp_path):
    results = tmp_path / "results"
    shutil.copytree(ROOT / "data/results", results)
    notebook = nbformat.read(ROOT / "notebooks" / (name + ".ipynb"), as_version=4)
    # The notebook writes only to this temporary result directory.
    notebook.cells.insert(0, nbformat.v4.new_code_cell(
        "import os\n"
        f"os.environ['PRISMA_RESULTS_DIR'] = {str(results)!r}\n"
    ))
    client = NotebookClient(notebook, timeout=180, kernel_name="python3",
                            resources={"metadata": {"path": str(ROOT / "notebooks")}})
    client.execute()
    if name.endswith("02_screening_evaluation"):
        prefix = "CLAUDE_" if name.startswith("CLAUDE") else ""
        assert (results / (prefix + "review.csv")).is_file()
        assert (results / (prefix + "df_evaluated_validation_abstract.csv")).is_file()
