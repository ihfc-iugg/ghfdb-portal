"""The contributor roles an assessment credits people with, by their concept's address."""

from fairdm.core.vocabularies import CONTRIBUTOR_ROLES

#: The role of whoever creates the assessment's dataset.
DATA_MANAGER = f"{CONTRIBUTOR_ROLES}/data-manager"

#: The role of each assessor on the assessment's dataset.
DATA_COLLECTOR = f"{CONTRIBUTOR_ROLES}/data-collector"
