from datetime import datetime

from django import forms
from django.utils.dates import MONTHS
from django.utils.translation import gettext as _

from .models import Interval, Site


class YearMonthMixin(forms.ModelForm):
    month = forms.ChoiceField(
        help_text=_("Month of acquisition"),
        required=False,
        choices={0: "", **MONTHS}.items(),
    )
    year = forms.IntegerField(
        help_text=_("Year of acquisition"),
        required=False,
        min_value=1900,
        max_value=datetime.now().year,
    )

    def __init__(self, *args, **kwargs):
        if kwargs.get("instance"):
            if kwargs["instance"].q_date_acq:
                kwargs["initial"] = dict(
                    year=kwargs["instance"].q_date_acq.year,
                    month=kwargs["instance"].q_date_acq.month,
                )
        super().__init__(*args, **kwargs)

    def save(self, commit):
        instance = super().save(commit)
        instance.q_date_acq = (
            f"{self.cleaned_data['year']}-{self.cleaned_data['month']}-01"
        )
        return instance


class AdminSiteForm(YearMonthMixin):
    class Meta:
        model = Site
        fields = "__all__"


class AdminIntervalForm(YearMonthMixin):
    class Meta:
        model = Interval
        fields = "__all__"
