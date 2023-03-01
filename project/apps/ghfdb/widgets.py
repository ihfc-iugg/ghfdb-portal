from django.contrib.gis.geos import Point
from django.forms import modelform_factory
from django.utils.translation import gettext as _
from geoluminate.utils.import_export import VocabularyM2MWidget
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget


class SiteWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):

        row["geom"] = Point(row["lon"], row["lat"], srid=row.get("srid", 4326))
        # row['id'] = row['ID']
        form, valid = self.get_form(row)

        geom = form.cleaned_data.pop("geom")

        del form.cleaned_data["references"]
        # del form.cleaned_data['id']
        # if row['id'] == 8:
        # x = 8
        instance, created = self.model.objects.update_or_create(
            geom=geom,
            defaults=form.cleaned_data,
        )

        return instance

    def get_form(self, row):
        form = modelform_factory(self.model, fields="__all__")(row)
        return form, form.is_valid()


class CorrectionsWidget(VocabularyM2MWidget):
    def clean(self, value, row=None, *args, **kwargs):
        """Create a list of `Choice` ids."""
        corrs = []
        for k, v in row.items():
            if v is None or not k.startswith("corr_"):
                continue

            # get the code from the row key. In the csv file,
            # correction values look like `corr_HP_flag` so split
            # by `_` and take the second item
            code = k.split("_")[1]

            # start building a dict that will represent the
            # intermerdiate model between `Interval` and `Choice`.
            # e.g. CorrectionIntervalThrough.
            data = {
                "correction": self.get_queryset(v, row).get(
                    **{self.field: k.split("_")[1]}
                )
            }

            try:
                # given value is a number so add it to the correct
                # fields
                data.update(applied="yes", value=float(v))
            except ValueError:
                # the given value is a string so update the applied
                # field only
                data.update(applied=v.lower())

            # append it to the corrs list
            corrs.append(data)

        return corrs


class CorrectionField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(widget=CorrectionsWidget(type="corrections"), *args, **kwargs)

    def save(self, obj, data, is_m2m=False, **kwargs):
        """
        If this field is not declared readonly, the object's attribute will
        be set to the value returned by :meth:`~import_export.fields.Field.clean`.
        """
        if not self.readonly:
            cleaned = self.clean(data, **kwargs)
            if cleaned is not None or self.saves_null_values:
                Intermediate = getattr(obj, self.attribute).through
                for corr in cleaned:
                    Intermediate(interval=obj, **corr).save()


class ReferenceWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            instance, created = self.get_queryset(
                value, row, *args, **kwargs
            ).get_or_create(**{self.field: value})
            return instance
        else:
            return None
