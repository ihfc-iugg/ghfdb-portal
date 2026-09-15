"""Role predicates for the assessment upload workflow (T004, plan.md
"Roles and access").

Every view, navigation check and template condition calls these two
functions rather than testing group names inline — the single place the
group names live, so the retired code's case-sensitivity defect, where the
same role was spelled three different ways across a queryset filter, a
fixture and the admin's own group name, cannot recur.
"""

DATA_ASSESSOR_GROUP = "Data Assessor"
DATA_CURATOR_GROUP = "Data Curator"


def is_data_assessor(user) -> bool:
    """Whether *user* belongs to the Data Assessor group."""
    return user.groups.filter(name=DATA_ASSESSOR_GROUP).exists()


def is_data_curator(user) -> bool:
    """Whether *user* belongs to the Data Curator group."""
    return user.groups.filter(name=DATA_CURATOR_GROUP).exists()
