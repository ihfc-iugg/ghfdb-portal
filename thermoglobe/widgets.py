from import_export.widgets import ForeignKeyWidget
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from thermoglobe.models import Correction

def get_non_relational_fields(model,row,exclude=[]):
    return [f for f in model._meta.concrete_fields if row.get(f.name) and f.name not in exclude and not f.is_relation]
   
class SiteWidget(ForeignKeyWidget):
    def __init__(self, model, field=None, render_field=None,id_fields=[], *args, **kwargs):
        self.render_field = render_field
        self.id_fields = list(id_fields)
        super().__init__(model, field=field, *args, **kwargs)

    def clean(self,value,row=None):

        if not row.get('latitude') or not row.get('longitude'):
            return None
        params = {k:row[k] for k in self.id_fields}

        defaults = {f.name: row.get(f.name) for f in get_non_relational_fields(self.model, row)}

        errors_dict = {}
        # Validate coordinates
        if not -90 <= float(row['latitude']) <= 90:
            errors_dict['latitude'] = ValidationError(_('latitude must be between -90 and 90 degrees'),code='invalid')
        if not -180 <= float(row['longitude']) <= 180:
            errors_dict['longitude'] = ValidationError(_('Longitude must be between -90 and 90 degrees'),code='invalid')
        if 'well_depth' in defaults.keys() and float(row['well_depth']) > 12200:
            errors_dict['well_depth'] = ValidationError(_('Well depth cannot be deeper than 12,200 m. Have you supplied the correct units?'),code='invalid')

        # challenger deep to mt everest
        if 'elevation' in defaults.keys() and not -11034 <= float(row['elevation']) <= 8848:
            errors_dict['elevation'] = ValidationError(_('Your elevation value looks wrong. Have you supplied this data in the correct units?'),code='invalid')

        if errors_dict:
            raise ValidationError(errors_dict)


        try:
            obj = self.model.objects.get(**params)
            for key, value in defaults.items():
                setattr(obj, key, value)
            # obj.save()
        except self.model.DoesNotExist:
            # new_values = {'first_name': 'John', 'last_name': 'Lennon'}
            params.update(defaults)
            obj = self.model(**params)

        row['site'] = obj

        # try:
        #     obj = self.model.objects.get(**params)
        # except self.mode.DoesNotExist:
        #     obj = self.model(**params,**defaults)
        # row['site'] = self.model.objects.update_or_create(**params,defaults=defaults)[0]

        if row.get('other_references'):
            row['site'].reference.add(*row['other_references'])

        # if isinstance(row['reference'],Publication):
        #     row['site'].reference.add(row['reference'])

        return row['site']

    def render(self, value, obj=None):

        if self.render_field:
            value = getattr(value,self.render_field)
            if value is None:
                return ''
        return value 

class CorrectionsWidget(ForeignKeyWidget):

    def __init__(self, field=None, *args, **kwargs):

        self.model = Correction
        self.field = field

    def clean(self, value, row=None):

        # gets all columns that correlate to the corrections field and stores them in a new dict
        params = {k.replace('_correction',''):v for k,v in row.items() if k.replace('_correction','') in [f.name for f in self.model._meta.concrete_fields]}

        # remove empty values from dict
        params = {k:v for k,v in params.items() if v}

        #try to find object based on id_fields
        if params:
            try:
                obj = self.model.objects.get(heatflow__pk=row.get('hf_id'))
                for key, value in params.items():
                    setattr(obj, key, value)
            except self.model.DoesNotExist:
                obj = self.model(**params)
            row['corrections'] = obj

            # row['corrections'] = self.model.objects.update_or_create(heatflow__pk=row.get('hf_id'), defaults=params)[0]
            return row['corrections']

    def render(self, value, obj=None):

        if self.field:
            value = getattr(value,self.field)
            if value is None:
                return ''
        return value
