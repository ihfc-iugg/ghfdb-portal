"""Project settings: wires fairdm, then applies project-specific overrides."""

import fairdm

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

MVP_CONFIG["layout"]["sidebar"]["title"] = "Heatflow.world"


EASY_ICONS["svg"]["icons"]["ihfc"] = "ihfc.svg"

# FairDM's fields name their vocabularies by address, and that address answers with the
# vocabulary's own record. The whole vocabulary is the file with ``.ttl`` added.
CONTROLLED_VOCABULARIES = {
    slug: {"source": f"https://w3id.org/fairdm/vocabularies/{slug}.ttl"}
    for slug in (
        "contributor-roles",
        "date-types",
        "description-types",
        "identifier-types",
        "sample-status",
    )
}

CSRF_TRUSTED_ORIGINS = [
    f"https://{domain}" for domain in globals().get("ALLOWED_HOSTS", [])
]
