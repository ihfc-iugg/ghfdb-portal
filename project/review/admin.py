from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from fairdm.contrib.contributors.models import Person

from review.models import Review


class RelatedPersonFilter(admin.SimpleListFilter):
    title = _("person")
    parameter_name = "person"

    def lookups(self, request, model_admin):
        # Get only Person instances linked to at least one MyModel instance
        linked_people = Person.objects.filter(heat_flow_reviews__isnull=False).distinct()
        return [(person.id, str(person)) for person in linked_people]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(reviewers__id=self.value())
        return queryset


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model."""

    list_display = (
        "id",
        "dataset_link",
        "literature_link",
        "_reviewers",
        "start_date",
        "end_date",
        "status",
    )
    search_fields = ("dataset__name", "literature__title")
    list_filter = ("status", RelatedPersonFilter)

    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).select_related("dataset", "literature").prefetch_related("reviewers")

    @admin.display(description="Dataset")
    def dataset_link(self, obj):
        url = obj.dataset.get_absolute_url()
        return format_html('<a href="{}">{}</a>', url, obj.dataset.uuid)

    @admin.display(description="Literature")
    def literature_link(self, obj):
        """Display literature title as a link."""
        url = obj.literature.get_absolute_url()
        title = obj.literature.title
        if title:
            title = title[:30] + "..." if len(title) > 30 else title
        return format_html('<a href="{}">{}</a>', url, title or "No title")

    def _reviewers(self, obj):
        """Display reviewers as a comma-separated list."""
        links = []
        for reviewer in obj.reviewers.all():
            url = reviewer.get_absolute_url()
            links.append(f'<a href="{url}">{reviewer}</a>')
        return mark_safe(", ".join(links))

    _reviewers.short_description = "Reviewers"
