"""The entity relationship diagram is held to the models, and to being a diagram.

Two separate failures are guarded against. The diagram had drifted from the schema —
it carried a junction table that was never built and named a depth interval by its
abstract base class. And it reached readers as source text: the Mermaid source was
valid, no extension was configured to render it, and the build reported no problem.
"""

import re
from pathlib import Path

import pytest
from django.apps import apps

DIAGRAM_PAGE = Path(__file__).resolve().parents[2] / "docs" / "data_models" / "ghfdb-erd.md"

#: The apps whose models this portal defines. Everything else on the diagram comes
#: from FairDM and is drawn for context.
PROJECT_APPS = ("heat_flow", "ghfdb", "review")

MERMAID_BLOCK = re.compile(r"^```mermaid\n(.*?)^```", re.MULTILINE | re.DOTALL)
ENTITY = re.compile(r"^\s+(\w+)\s*\{", re.MULTILINE)


def entity_diagram() -> str:
    """The source of the page's entity relationship diagram."""
    blocks = [
        block for block in MERMAID_BLOCK.findall(DIAGRAM_PAGE.read_text(encoding="utf-8"))
        if block.lstrip().startswith("erDiagram")
    ]
    assert len(blocks) == 1, (
        f"Expected one entity relationship diagram in {DIAGRAM_PAGE.name}, found {len(blocks)}"
    )
    return blocks[0]


def project_models() -> list[str]:
    """Every model this portal's own apps define, ignoring proxies.

    A proxy shares its table with the model it proxies, so it is not a separate entity
    on a diagram of tables and keys.
    """
    return sorted(
        model.__name__
        for label in PROJECT_APPS
        for model in apps.get_app_config(label).get_models()
        if not model._meta.proxy
    )


class TestDiagramCoversTheModels:
    """Acceptance: the diagram shows every model this portal defines."""

    def test_every_project_model_is_an_entity(self):
        entities = set(ENTITY.findall(entity_diagram()))
        missing = [name for name in project_models() if name not in entities]
        assert not missing, (
            f"Models absent from the diagram in {DIAGRAM_PAGE.name}: {missing}"
        )

    def test_every_relationship_names_entities_the_diagram_defines(self):
        source = entity_diagram()
        entities = set(ENTITY.findall(source))
        relationship = re.compile(r"^\s+(\w+)\s+[|}o][|}o.-]*[|{o]\s+(\w+)\s*:", re.MULTILINE)
        pairs = relationship.findall(source)
        assert pairs, "The diagram declares no relationships"
        undefined = sorted(
            {name for pair in pairs for name in pair if name not in entities}
        )
        assert not undefined, (
            f"The diagram relates entities it never defines: {undefined}"
        )


class TestDiagramRenders:
    """Acceptance: the diagram reaches a reader as a diagram, not as source text."""

    @pytest.mark.slow
    def test_the_built_page_carries_a_diagram_rather_than_a_code_block(
        self, built_diagram_page: str
    ):
        assert "highlight-mermaid" not in built_diagram_page, (
            "The diagram was built as a syntax-highlighted code block, which is what "
            "happens when no Mermaid renderer is configured"
        )
        assert 'class="mermaid"' in built_diagram_page, (
            "The built page carries no Mermaid container"
        )
