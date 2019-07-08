from import_export.widgets import Widget, ForeignKeyWidget, ManyToManyWidget
from .models import HeatFlow,Temperature, TemperatureGradient
from django.utils.encoding import smart_text, force_text
from django.core.exceptions import ValidationError
from reference.models import Author

def get_non_relational_fields(model,row,exclude=[]):
    return [f for f in model._meta.concrete_fields if row.get(f.name) and f.name not in exclude]

def create_fields_dictionary(row, model_fields):
    return {key: val for key,val in row.items() if key in [field.name for field in model_fields] and val != ''}

def get_reference(model,row,id_fields=None):

    if row.get('authors'):
        first_author, co_authors = get_authors(row.get('authors'),Author)
    else:
        return 

    #get all fields within model that are not a relational field
    model_fields = get_non_relational_fields(model, row)

    #create a dictionary of all non relational fields that are not ''
    fields = create_fields_dictionary(row, model_fields)

    fields.update({'first_author':first_author})

    if id_fields is not None:
        id_fields = {key: val for key,val in fields.items() if key in id_fields}
    else:
        id_fields = fields
    
    #have to chain co_author queries until we find a match
    query = model.objects.filter(**id_fields)
    for author in co_authors:
        query = query.filter(co_authors=author)

    if query.count() == 1:
        if query[0].co_authors.all().count() == len(co_authors):
            obj = model.objects.update_or_create(id=query[0].pk,defaults=fields)[0]
        else:
            obj = model.objects.create(**fields)
    elif query.count() > 1:
        for q in query:
            if q.co_authors.all().count() == len(co_authors):
                obj = model.objects.update_or_create(id=q.id,defaults=fields)[0]
                break
        # obj = model.objects.create(**fields)
    else:
        obj = model.objects.create(**fields)
    
    #add the co_author ids. must be done after save() is called.
    for author in co_authors:
        obj.co_authors.add(author)

    # obj.save()
    return obj

def get_authors(authors, model):
    #split string into authors by ','
    authors = authors.split(',')
    author_list = []
    for author in authors:
        author = {k:v for k,v in zip(['last_name','first_name'],author.split('.')) if v != ''}

        #if a first name is not specified
        if 'first_name' not in author.keys():
            try:
                author_list.append(model.objects.update_or_create(last_name=author['last_name'],defaults=author)[0])
            except model.MultipleObjectsReturned:
                raise ValueError('Found more than one author in the database with the last name "{last_name}". Please specify a first name or first initial and try again. (Eg {last_name}.J or {last_name}.John)'.format(last_name=author['last_name']))
        #if a first name IS specified
        else:
            #First: try search by FULL first name
            try:
                author_list.append(model.objects.get(last_name=author['last_name'],
                                                    first_name=author['first_name']))
            except model.DoesNotExist:
                #If the given full name does not exist in the database, check if an abbreviated name exists
                try: 
                    obj = model.objects.get(last_name=author['last_name'],
                                            first_name__startswith=author['first_name'][0])
                    
                    #if it does, update the db entry with the given full name
                    if len(author['first_name']) > len(obj.first_name):
                        obj.first_name = author['first_name']
                        obj.save()
                    author_list.append(obj)
                except model.DoesNotExist:
                    #if the abbreviated name does not exist in the database, check if a last name exists. If so, update the database entry with the full name
                    author_list.append(model.objects.update_or_create(last_name=author['last_name'],
                                                        defaults=author)[0])
                except model.MultipleObjectsReturned:
                    #if more than one db entry exists for the given last name, inform user that more information is required.
                    query_set = model.objects.filter(last_name=author['last_name'],
                                            first_name__startswith=author['first_name'][0])
                    first_names = [f.first_name for f in query_set]
                    raise ValueError('Found more than one author with the last name "{}" and first initial "{}". Found {} and {}. Please specify a full first name and try again.'.format(author['last_name'],author['first_name'][0],', '.join(first_names[:-1]),first_names[-1]))

    return author_list[0],author_list[1:]

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
        raise ValueError('Found more than one {} object with the given information.'.format(model._meta.object_name))

class SiteWidget(ForeignKeyWidget):
    def __init__(self, model, field=None, render_field=None, *args, **kwargs):
        self.render_field = render_field
        super().__init__(model, field=field, *args, **kwargs)

    def clean(self,value,row=None):

        value = row[self.field]
        if not isinstance(value,self.model):
            raise ValidationError(value)

        if value:
            return self.model.objects.get_or_create(**{'pk': value.id})[0]

    def render(self, value, obj=None):

        if self.render_field:
            value = getattr(value,self.render_field)
            if value is None:
                return ''
        return value 

class ReferenceWidget(ForeignKeyWidget):
    def __init__(self, model, field=None, render_field=None, *args, **kwargs):
        self.render_field = render_field
        super().__init__(model, field=field, *args, **kwargs)

    def clean(self,value,row=None):

        value = row[self.field]

        if value:
            return self.model.objects.get_or_create(**{'pk': value.id})[0]

    def render(self, value, obj=None):

        if self.render_field:
            value = getattr(value,self.render_field)
            if value is None:
                return ''
        return value 

class SitePropertyWidget(ForeignKeyWidget):
    
    def __init__(self, model, field, id_fields=None, required_fields='', varmap=None, exclude='', *args, **kwargs):
        # super().__init__(model, field, *args, **kwargs)

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
        if self.varmap:
            row = {self.varmap[k] if k in self.varmap.keys() else k:v for k,v in row.items()}

        if self.model == HeatFlow and row['site_name'] == 'AD-1X':
            y=8

        #get all fields within model that are not a relational field
        model_fields = get_non_relational_fields(self.model,row,self.exclude)

        # The temperature model contains additional relationships that we don't want to include
        if self.model != Temperature:
            model_fields += [f for f in self.model._meta.related_objects if row.get(f.name) and f not in model_fields]
        else:
            y=8
        #create a dictionary of all non relational fields that are not ''
        fields = {key: val for key,val in row.items() if key in [field.name for field in model_fields] and val != ''}

        # return if required fields are not found
        if not [i for i in self.required_fields if i in fields.keys()]:
            if self.model == HeatFlow:
                raise ValidationError('The current row does not contain a heat flow value!')
            else:
                return

        if self.id_fields is not None:
            id_fields = {k:v for k,v in row.items() if k in self.id_fields}
        else:
            id_fields = fields


        #try to find object based on id_fields
        try:
            return self.model.objects.update_or_create(**id_fields,defaults=fields)[0]
        except self.model.MultipleObjectsReturned:
            raise ValidationError('Found more than one {} object with the given information.'.format(self.model._meta.object_name))

    def render(self, value, obj=None):

        if self.field:
            value = getattr(value,self.field)
            if value is None:
                return ''
        return value

class CorrectionsWidget(ManyToManyWidget):

    def __init__(self, model, separator=',', field='pk', *args, **kwargs):
        super().__init__(model,separator,field,*args, **kwargs)

    def clean(self, value, row=None, *args, **kwargs):
        if not row.get('correction_type'):
            return self.model.objects.none() 

        types = row.get('correction_type').split(',')
        values = row.get('correction_value').split(',')

        correction_ids = []
        for x, val in zip(types,values):
            vals = {key: (value if value.strip() is not '' else None) for key,value in zip(['correction','value'],[x,val])}
            if vals:
                correction_ids.append(self.model.objects.get_or_create(**vals)[0].id)

        return correction_ids

    def render(self, value, obj=None):
        vals = [smart_text(getattr(instance,self.field)) for instance in value.all()]
        return self.separator.join(vals)

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
    
