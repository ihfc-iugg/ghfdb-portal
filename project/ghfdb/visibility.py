"""Which GHFDB parents a request may see."""

from fairdm.api.filters import FairDMVisibilityFilter
from heat_flow.models import HeatFlowSite

from .managers import GHFDBParentQuerySet
from .models import GHFDBParent


def served_parents(request) -> GHFDBParentQuerySet:
    """Return the parents *request* may see, whose site it may see too.

    A parent's own visibility says nothing about the ``HeatFlowSite`` it
    describes: the two can sit in different datasets, so ADR 0021's second
    path (a determination attached to a site that is not public) is only
    closed by checking both. The API viewsets and the parent table all call
    this one function, so they never disagree about which parents are served.

    Args:
        request: The request whose ``user`` decides what is visible.

    Returns:
        The served parents, unordered and without annotations.
    """
    visibility = FairDMVisibilityFilter()
    served = visibility.filter_queryset(request, GHFDBParent.objects.all(), None)
    visible_sites = visibility.filter_queryset(
        request, HeatFlowSite.objects.all(), None
    )
    return served.filter(sample_id__in=visible_sites.values_list("pk", flat=True))
