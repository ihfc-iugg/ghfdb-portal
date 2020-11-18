
import pandas as pd
pd.options.plotting.backend = "plotly"
from django_pandas.io import read_frame
import simplejson as json
from django.utils.html import mark_safe
import decimal
import re
from django.core.exceptions import FieldDoesNotExist

def apply_hyperlinks(val):
    return '<a href="{}">{}</a>'.format(val,val)

class Table():
    
    page_length = 25
    dom = '<"top d-flex justify-content-around align-items-center flex-wrap"lpf>t<"bottom"ip><"clear">'

    def __init__(self, filters={}, headers=None, qs=None):
        self.filters = filters
        self.qs=qs
        self.headers = self.Meta.headers if headers is None else headers
       
        # self.df = read_frame(self.get_queryset().values(*self.headers))
        self.df = read_frame(self.get_queryset(),self.headers,verbose=False)
        self.id = type(self).__name__.lower()
        self.name = self.Meta.model._meta.verbose_name_plural.title()
        self.meta = {k:v for k, v in self.Meta.__dict__.items() if not k.startswith('__')}
        # self.df.to_csv('{}.csv'.format(self.name))

    @property
    def options(self):
        return json.dumps({
            'dom': self.meta.get('dom',getattr(self,'dom')),
            'pageLength': self.meta.get('page_length',getattr(self,'page_length')),
            'order': self.get_order(),
            'columnDefs': self.get_column_defs(),
        })

    @property
    def has_data(self):
        return not self.df.empty

    @property
    def count(self):
        return self.df.shape[0]

    def data(self):
        # if getattr(self.Meta,'url',False) and 'slug' in self.headers:
        #     self.apply_hyperlinks()
        return  mark_safe(json.dumps({
            'options': json.dumps(self.options),
            'id': self.id,
            'data': self.to_json(),
            # **self.to_dict(),
        }))

    def to_json(self):
        return mark_safe(self.df.to_json(orient='split',index=False))

    def to_html(self):
        return self.df.to_html(
            float_format='{:.2f}'.format,
            index=False,
            classes='table-responsive',
            render_links=True,
        )

    def to_dict(self):
        df = self.df.copy()
        if self.meta.get('round_to'):
            df = self.df.round(self.meta['round_to'])
        df.columns = self.get_verbose_headers()
        return df.to_dict(orient='split')

    def get_queryset(self):
        if self.qs is None:
            return self.Meta.model.objects.filter(**self.filters)
        else:
            return self.qs

    def get_order_item(self,item):
        if item.startswith('-'):
            direction = 'desc'
            index = self.headers.index(item[1:])
        else:
            direction = 'asc'
            index = self.headers.index(item)

        return [index, direction]

    def get_order(self):
        if getattr(self.Meta,'order_by'):
            if isinstance(self.Meta.order_by, list):
                return [self.get_order_item(item) for item in self.Meta.order_by]
            else:
                return [self.get_order_item(self.Meta.order_by)]
        else:
            return []

    def apply_hyperlinks(self):
        for field in self.Meta.link_columns:
            self.df[field] = '<a href="{}'.format(self.Meta.url) + self.df['slug'] +'">' + self.df[field] +"</a>"

    def get_verbose_headers(self):
        # return [self.titleize(self.Meta.model._meta.get_field(field).verbose_name) for field in self.headers]
        out = []
        for field in self.headers:
            try:
                out.append(self.titleize(self.Meta.model._meta.get_field(field).verbose_name))
            except:
                out.append(field)
        return out

    def verbose_column_name(self,column_name):
        try:
            return self.titleize(self.Meta.model._meta.get_field(column_name).verbose_name)
        except FieldDoesNotExist:
            return column_name

    def titleize(self, string):
        units = ''
        if '[' in string:
            string, units = string.split('[')
            units = '[' + units
        string = ' '.join([word.strip().title() for word in re.split('[ _]', string)])

        return string + units

    def get_column_defs(self):
        col_defs = []
        for field in getattr(self.Meta,'hide',[]):
            col_defs.append(
                {
                "targets": [ self.headers.index(field) ],
                "visible": False, 
                }
            )
        return col_defs

    def top_n(self,n,column,include_other=True):
        vals = self.df[column].value_counts()
        top_n = vals[:n]
        if include_other:
            top_n = top_n.append(pd.Series({'Other':vals[n:].sum()}))
        return top_n