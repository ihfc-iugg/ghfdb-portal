"""Fixtures shared by the documentation tests."""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs"
DIAGRAM_PAGE = DOCS_DIR / "data_models" / "ghfdb-erd.md"


@pytest.fixture(scope="session")
def built_diagram_page(tmp_path_factory) -> str:
    """The HTML Sphinx produces for the entity relationship page.

    Built rather than read from source because the failure this guards against is a
    diagram source that is perfectly valid and never rendered: without a Mermaid
    extension configured, MyST emits the diagram as a highlighted code block and the
    page still builds without error.
    """
    pytest.importorskip(
        "sphinxcontrib.mermaid",
        reason="building the documentation needs the documentation dependency group",
    )
    out_dir = tmp_path_factory.mktemp("docs-html")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "html",
            "-q",
            str(DOCS_DIR),
            str(out_dir),
            str(DIAGRAM_PAGE),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    return (out_dir / "data_models" / "ghfdb-erd.html").read_text(encoding="utf-8")
