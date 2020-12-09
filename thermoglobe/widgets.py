from import_export.widgets import Widget, ForeignKeyWidget, ManyToManyWidget, FloatWidget
from .models import Interval, Temperature, Conductivity, Correction, Author, Publication
from django.utils.encoding import smart_text, force_text
from django.core.exceptions import ValidationError
from django import forms
from django.forms.widgets import Input
from django.utils.translation import ugettext as _
import bibtexparser as bib
import bibtexparser.customization as custom
import re
from bibtexparser.bibdatabase import BibDatabase
import re
from django.apps import apps

def get_non_relational_fields(model,row,exclude=[]):
    return [f for f in model._meta.concrete_fields if row.get(f.name) and f.name not in exclude and not f.is_relation]

def create_fields_dictionary(row, model_fields):
    return {key: val for key,val in row.items() if key in [field.name for field in model_fields] and val != ''}

def get_keywords_list(entry_dict,sep):
    """
    Split keyword field into a list.

    :param entry_dict: the record.
    :param sep: pattern used for the splitting regexp.
    :type sep: string, optional
    :returns: dict -- the modified record.

    """
    if "keywords" in entry_dict:
        return [i.strip() for i in re.split(sep, entry_dict["keywords"].strip())]
   
def update_or_create_object(model=None, row=None, id_fields='', exclude='',recursive=False, is_recursion=False):

    exclude = list(exclude)
    id_fields = list(id_fields)

    #get all fields within model that are not a relational field
    model_fields = get_non_relational_fields(model,row,exclude)

    #create a dictionary of all non relational fields that are not ''
    fields = create_fields_dictionary(row, model_fields)

    # return if no id_fields can be found
    # found_id_fields = [i for i in id_fields if i in fields.keys()]

    if not row['latitude'] or not row['longitude']:
        return 'The current row is missing either latitude or longitude data'

    # if len(found_id_fields) != len(id_fields) and not is_recursion:
    #     not_found = [f for f in id_fields if f not in found_id_fields]
    #     return 'The current row is missing the following required fields "{}"'.format(', '.join(not_found))

    #ATTEMPT TO RECURSIVELY ADD FOREIGN KEYS
    for f in model_fields:
        if f.is_relation and f.name not in exclude and not isinstance(fields[f.name],f.related_model):
            fields[f.name] = update_or_create_object(f.related_model,row,is_recursion=True)

    if id_fields:
        id_fields = {key: val for key,val in fields.items() if key in id_fields}
    else:
        id_fields = fields

    #try to find object based on id_fields
    try:
        return model.objects.update_or_create(**id_fields,defaults=fields)[0]
    except model.MultipleObjectsReturned:
        raise ValidationError('Found more than one {} object with the given information.'.format(model._meta.object_name))

def site_property(model,row,varmap,exclude,id_fields,required_fields):
    if varmap:
        row = {varmap[k] if k in varmap.keys() else k:v for k,v in row.items()}

    #get all fields within model that are not a relational field
    model_fields = get_non_relational_fields(model,row,exclude)

    # The temperature model contains additional relationships that we don't want to include
    if model != Temperature:
        model_fields += [f for f in model._meta.related_objects if row.get(f.name) and f not in model_fields]

    #create a dictionary of all non relational fields that are not ''
    fields = {key: val for key,val in row.items() if key in [field.name for field in model_fields] and val != ''}

    # return if required fields are not found
    if not [i for i in required_fields if i in fields.keys()]:
        return '',''

    if id_fields is not None:
        id_fields = {k:v for k,v in row.items() if k in id_fields and v != ''}
    else:
        id_fields = fields

    if 'surface_temp' in varmap.keys() or 'heatgeneration' in varmap.keys():
        id_fields['depth'] = 0

    return id_fields, fields



class NoRenderWidget(Widget):

    def render(self, value, obj=None):
        return ''

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

# class PublicationWidget(ManyToManyWidget):
class PublicationWidget(ForeignKeyWidget):
    def __init__(self, model, field=None, reference_dict=None, *args, **kwargs):
        super().__init__(model, field=field, *args, **kwargs)
        self.ref_dict = reference_dict

    def clean(self,value,row=None, bib_db=None):
        if value:
            if isinstance(value,Publication):
                return value
            # If an actual bibtex string is provided
            try:
                entry = bib.loads(value).entries[0]
            except IndexError:
                pass
            else:
                bib_id = entry.get('ID','')
                ref, created = self.model.objects.get_or_create(bib_id=bib_id)
                if created:
                    # save new bibtex entry to bibtex file on server
                    pass
                else:
                    # save the existing reference entry with the new bibtex file
                    ref.bibtex = value
                    ref.save()
                row['reference'] = ref
                return row['reference']

            # just in case multiple refs are supplied
            refs = value.split(';')
            refs.sort(key=self.get_year)
            row['reference'] = self.model.objects.get_or_create(bib_id=refs.pop().strip())[0]
            if refs:
                row['other_references'] = [self.model.objects.get_or_create(bib_id=ref.strip())[0] for ref in refs]


            # row['reference'] = self.model.objects.get_or_create(pk=value)[0]
            return row['reference']

    def render(self, value, obj=None):
        return getattr(value,'bib_id') 

    def get_year(self,ref):
        year = re.findall(r'\d+', ref)
        if year:
            return int(year[0])
        else:
            return 0

class SitePropertyWidget(ForeignKeyWidget):
    
    def __init__(self, model, field, id_fields=None, required_fields='', varmap=None, exclude='', *args, **kwargs):

        self.model = model
        self.field = field
        self.id_fields = id_fields
        self.varmap = varmap

        if isinstance(required_fields, str):
            self.required_fields = [required_fields]
        else:
            self.required_fields = required_fields

        if isinstance(exclude, str):
            self.exclude = [exclude]
        else:
            self.exclude = exclude

    def clean(self, value, row=None):

        if not row.get('save_temp'):
            return None

        id_fields, fields = site_property(self.model,row,self.varmap,self.exclude,self.id_fields,self.required_fields)

        if not id_fields and not fields:
            return

        #try to find object based on id_fields
        try:
            return self.model.objects.update_or_create(**id_fields,defaults=fields)[0]
            # row[self.model._meta.model_name] = self.model.objects.update_or_create(**id_fields,defaults=fields)[0]

        except self.model.MultipleObjectsReturned:
            # row[self.model._meta.model_name] = self.model.objects.update_or_create(**id_fields,defaults=fields)[0]

            raise ValidationError('Found more than one {} object with the given information.'.format(self.model._meta.object_name))
        # finally:
        #     return row[self.model._meta.model_name]

    def render(self, value, obj=None):

        if self.field:
            value = getattr(value,self.field)
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

class ChoiceWidget(Widget):
    """
    Widget for converting text fields.
    """
    def __init__(self, choices, *args, **kwargs):
        self.choices = {v: k for k, v in choices}
        self.choices_reverse = {k:v for k, v in choices}

    def clean(self, value, row=None, *args, **kwargs):

        value = self.choices.get(value.lower())

        if value is None:
            raise ValueError('That is not a valid option for this field. Available options are: {}'.format(', '.join([choice[1] for choice in self.choices])))

        return value

    def render(self, value, obj=None):
        # return force_text(value)
        return force_text(self.choices_reverse.get(value),'')

class M2MWidget(ManyToManyWidget):

    def __init__(self, model, separator=',', field='pk', *args, **kwargs):
        super().__init__(model, separator, field, *args, **kwargs)


    def clean(self, value, row=None, *args, **kwargs):

        if not value:
            return self.model.objects.none()

        items = value.split(self.separator)
        items = filter(None, [i.strip() for i in items])

        return [self.model.objects.get_or_create(**{self.field:item})[0] for item in items]

        # return self.model.objects.filter(**{
        #     '%s__in' % self.field: ids
        # })


    def render(self, value, obj=None):
        ids = [smart_text(getattr(obj, self.field)) for obj in value.all()]
        return self.separator.join(ids)

class CustomFK(ForeignKeyWidget):
    
    def __init__(self, model, field='name', *args, **kwargs):
        super().__init__(model, field, *args, **kwargs)
        self.field = field

    def clean(self, value, row=None):
        dont_include_these = ['unknown','undefined','',None]
        if not value in dont_include_these:
            return self.model.objects.get_or_create(**{self.field: value})[0]


class RangeInput(Input):
    input_type = 'number'
    template_name = 'forms/input.html'



# -------- FILTER WIDGETS ----------
class RangeWidget(forms.MultiWidget):
    """
    A MultiWidget that allows users to provide custom suffixes instead of indexes.

    - Suffixes must be unique.
    - There must be the same number of suffixes as fields.
    """
    # template_name = 'widgets/rangewidget.html'
    suffixes = ['_gte', '_lte']
    

    def __init__(self, suffixes=None, *args, **kwargs):
        if suffixes is not None:
            self.suffixes = suffixes
        widgets = (RangeInput(attrs={'placeholder':'Min'}), RangeInput(attrs={'placeholder':'Max'}))
        super().__init__(widgets=widgets,*args, **kwargs)

        assert len(self.widgets) == len(self.suffixes)
        assert len(self.suffixes) == len(set(self.suffixes))

    def suffixed(self, name, suffix):
        return '_'.join([name, suffix]) if suffix else name

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        for subcontext, suffix in zip(context['widget']['subwidgets'], self.suffixes):
            subcontext['name'] = self.suffixed(name, suffix)

        return context

    def value_from_datadict(self, data, files, name):
        return [
            widget.value_from_datadict(data, files, self.suffixed(name, suffix))
            for widget, suffix in zip(self.widgets, self.suffixes)
        ]

    def value_omitted_from_data(self, data, files, name):
        return all(
            widget.value_omitted_from_data(data, files, self.suffixed(name, suffix))
            for widget, suffix in zip(self.widgets, self.suffixes)
        )

    def replace_name(self, output, index):
        result = search(r'name="(?P<name>.*)_%d"' % index, output)
        name = result.group('name')
        name = self.suffixed(name, self.suffixes[index])
        name = 'name="%s"' % name

        return sub(r'name=".*_%d"' % index, name, output)

    def decompress(self, value):
        if value:
            return [value.start, value.stop]
        return [None, None]

class RangeField(forms.MultiValueField):
    widget = RangeWidget

    def __init__(self, template='widgets/rangewidget.html',field=None, *args, **kwargs):
        self.template = template

        if field is None:
            fields = (
                forms.DecimalField(),
                forms.DecimalField())
        else:
            fields = (field,field)
 
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return slice(*data_list)
        return None