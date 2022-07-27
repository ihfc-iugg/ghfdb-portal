from django import template

register = template.Library()

@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)


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