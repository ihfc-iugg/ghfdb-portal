"""Role predicates for the assessment upload workflow (T004, plan.md
"Roles and access").

Every view, navigation check and template condition calls these two
functions rather than testing group names inline — the single place the
group names live, so the case-sensitivity defect the current code carries
(``groups__name="reviewers"`` vs. the fixture's ``"reviewers"`` vs. the admin
group named ``"Reviewers"``) cannot recur.
"""

DATA_ASSESSOR_GROUP = "Data Assessor"
DATA_CURATOR_GROUP = "Data Curator"


def is_data_assessor(user) -> bool:
    """Whether *user* belongs to the Data Assessor group."""
    return user.groups.filter(name=DATA_ASSESSOR_GROUP).exists()


def is_data_curator(user) -> bool:
    """Whether *user* belongs to the Data Curator group."""
    return user.groups.filter(name=DATA_CURATOR_GROUP).exists()
