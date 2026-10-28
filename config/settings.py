"""Project settings: wires fairdm, then applies project-specific overrides."""

from pathlib import Path

import fairdm

# Read before ``setup()``, which rebinds ``__file__`` while it applies each settings layer.
VOCABULARY_FILES = Path(__file__).resolve().parent.parent / "vocabularies"

fairdm.setup(
    apps=[
        "ghfdb",
        "heat_flow",
        "review",
    ],
    addons=[
        "fairdm_discussions",
        "fairdm_geo",
    ],
)

# FairDM's own vocabularies, kept with the portal until their addresses are published
# (vocabularies/README.md). The heat flow vocabularies need no entry: their fields name
# the files they ship in.
CONTROLLED_VOCABULARIES = {
    slug: {"source": VOCABULARY_FILES / f"{slug}.ttl"}
    for slug in (
        "contributor-roles",
        "date-types",
        "description-types",
        "identifier-types",
        "organization-types",
        "project-status",
        "relation-types",
        "sample-relation-types",
        "sample-status",
    )
}

MVP_CONFIG["layout"]["sidebar"]["title"] = "Heatflow.world"


EASY_ICONS["svg"]["icons"]["ihfc"] = "ihfc.svg"

CSRF_TRUSTED_ORIGINS = [
    f"https://{domain}" for domain in globals().get("ALLOWED_HOSTS", [])
]
