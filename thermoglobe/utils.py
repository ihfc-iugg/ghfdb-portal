
from django.db.models import Func, F, Value, CharField
from django.db.models.functions import Concat
from _plotly_utils.basevalidators import ColorscaleValidator
from functools import wraps
from django.core.cache import caches

def plot_cache(cache_key):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            plots = caches['plots']
            if len(args) > 1:
                # an argument was supplied to the wrapped function, use it for greater specificity in cache versioning
                version = f"{args[0].field}-{args[1]}"
            else:
                #no additional args were found so just use the field attribute on the queryset
                version = args[0].field
            force_update = kwargs.pop('force_update',None)
            if plots.get(cache_key, version=version) is None or force_update:
                plots.set(cache_key, func(*args, **kwargs), version=version)
            if not force_update:
                return plots.get(cache_key, version=version)

        return wrapper
    return decorator

def plotly_cscale_nan(color,nan_color):
    c_scale = ColorscaleValidator("colorscale", "make_figure").validate_coerce(color)
    c_scale[0][0] += 0.000001
    c_scale.insert(0,[0, nan_color])
    return c_scale

class Round(Func):
    function = 'ROUND'
    template="%(function)s(%(expressions)s::numeric, 2)"

def Hyperlink(url, slug_field,field=None,icon=None):
    # mark_safe(f"<a href='{reverse('mapping:describe_field', kwargs={'model':self.model_name,'slug':row['slug']})}'>{row[self.group_by]}</a>")
    if field:
        field = F(field)
    elif icon:
        field = Value(icon)
    else:
        raise ValueError('You must specify either a field or an icon.')

    slug = F(slug_field)
    url = Value('<a href="{}'.format(url))
    return Concat(url, slug, Value('">'), field, Value("</a>"), output_field=CharField())

