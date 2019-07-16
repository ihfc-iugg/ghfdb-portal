from django import template

register = template.Library()

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
def de_underscore(str_input,replace_with_this):
    return str_input.replace('_',replace_with_this)

