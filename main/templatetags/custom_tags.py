from django import template
from django.core.exceptions import FieldDoesNotExist
register = template.Library()
# from thermoglobe.choices import UNITS
from django.utils.html import mark_safe

# @register.filter(name='units')
# def units(field_name):
#     units = UNITS.get(field_name,None)
#     if units is not None:
#         return mark_safe(units)

@register.filter(name='choices')
def choices(obj):
    x=8
    return


@register.filter(name='get_mean')
def get_mean(qs, field_names):
    #gets the mean value of field_name in the query set 'qs'
    field_names = field_names.split(',')
    
    tmp = []
    field=field_names[0]
    for x in qs:
        if x is not None:
            tmp.append(x.getattr(field))

    for field in field_names:
        tmp_val = [getattr(x,field) for x in qs if x is not None]
        
        for f in field.split('__'):
            field = getattr(qs,f)

        if tmp_val:
            if tmp_val[0] is not None:
                tmp = tmp + tmp_val
    tmp = sum(tmp)
    if tmp == 0:
        return None
    else:
        return tmp/len(qs)

@register.filter(name='de_underscore')
def de_underscore(str_input):
    return str_input.replace('_',' ')

@register.filter(name='field_type')
def field_type(field):
    return field.field.widget.__class__.__name__

@register.simple_tag
def field_name(value, field, model=None):
    '''
    Django template filter which returns the verbose name of an object's,
    model's or related manager's field.
    '''
    if model:
        try:
            value = model._meta.get_field(field).verbose_name.title()
            return value
        except FieldDoesNotExist:
            pass
           
    elif hasattr(value, 'model'):
        value = value.model
        return value._meta.get_field(field).verbose_name.title()

    return field.replace('_',' ').title()

@register.filter
def get_obj_attr(obj):
    try:
        value = obj.field.queryset.get(pk=obj.initial)
    except AttributeError:
        value = obj.initial

    if getattr(obj.field,'choices',False):
        for choice in obj.field.choices:
            if value == choice[0]:
                value = choice[1]

    return '<tr><td class="w-50">{}:</td><td>{}</td></tr>'.format(obj.name.replace('_',' ').title(),value)