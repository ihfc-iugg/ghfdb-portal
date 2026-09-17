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


def is_assessment_team_member(user) -> bool:
    """Whether *user* belongs to either role.

    "On the assessment team" is a thing the workflow asks about in its own
    right — the list, the description form and the navigation entry are open
    to both roles and care about nothing finer. Asking it once reads as the
    question it is, and costs one query rather than the two that testing each
    role in turn would.
    """
    return user.groups.filter(
        name__in=(DATA_ASSESSOR_GROUP, DATA_CURATOR_GROUP)
    ).exists()


def can_manage_upload(user, review) -> bool:
    """Whether *user* may upload against or confirm *review* (T020, plan.md
    "The pages"): its own uploader, or any Data Curator, and no one else —
    including a Data Assessor who did not create it."""
    return user.is_authenticated and (
        review.uploaded_by_id == user.pk or is_data_curator(user)
    )
