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

CSRF_TRUSTED_ORIGINS = [
    f"https://{domain}" for domain in globals().get("ALLOWED_HOSTS", [])
]
