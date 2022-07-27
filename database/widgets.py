from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from django.utils.translation import ugettext as _
from decimal import Decimal

def get_non_relational_fields(model,row,exclude=[]):
    return [f for f in model._meta.concrete_fields if row.get(f.name) and f.name not in exclude and not f.is_relation]


class SiteWidget(ForeignKeyWidget):

    def clean(self, value, row=None, *args, **kwargs):

        defaults = {f.name: row.get(f.name) for f in get_non_relational_fields(self.model, row)}

        qs = self.get_queryset(value, row)

        for k in ['name','lat','lng']:
            defaults.pop(k, None)

        # if qs.exists():
        instance, created = qs.update_or_create(
            name = row['name'],
            lat = round(row['lat'],5),
            lng = round(row['lng'],5),
            defaults = defaults,
        )
        return instance


class CorrectionsWidget(ManyToManyWidget):

    def clean(self, value, row=None, *args, **kwargs):

        corrs = []
        for k, v in row.items():
            if v is None:
                continue
            if k.startswith('corr_') and v.lower() == 'yes':
                corrs.append(
                    self.model.objects.get(
                            id = k.split('_')[1],
                            ))
        return corrs


class ReferenceWidget(ForeignKeyWidget):

    def clean(self, value, row=None, *args, **kwargs):
        val = value
        if val:
            instance, created = self.get_queryset(value, row, *args, **kwargs).get_or_create(**{self.field: val})
            return instance
        else:
            return None

