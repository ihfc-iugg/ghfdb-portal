
import pandas as pd
pd.options.plotting.backend = "plotly"
from django_pandas.io import read_frame
import simplejson as json
from django.utils.html import mark_safe
import decimal
import re

def apply_hyperlinks(val):
    return '<a href="{}">{}</a>'.format(val,val)

class Table():
    
    page_length = 25
    dom = '<"top d-flex justify-content-around align-items-center flex-wrap"lpf>t<"bottom"ip><"clear">'

    def __init__(self, filters={},headers=None):
        self.filters = filters
        self.headers = self.Meta.headers if headers is None else headers
       
        # self.df = read_frame(self.get_queryset().values(*self.headers))
        # self.df = read_frame(self.get_queryset(),self.headers)
        self.id = type(self).__name__.lower()
        self.name = self.Meta.model._meta.verbose_name_plural.title()
        self.meta = {k:v for k, v in self.Meta.__dict__.items() if not k.startswith('__')}
        # self.df.to_csv('{}.csv'.format(self.name))

    @property
    def options(self):
        return {
            'dom': self.meta.get('dom',getattr(self,'dom')),
            'pageLength': self.meta.get('page_length',getattr(self,'page_length')),
            'order': self.get_order(),
            'columnDefs': self.get_column_defs(),
        }

    @property
    def has_data(self):
        return not self.df.empty

    @property
    def count(self):
        return self.df.shape[0]

    def data(self):
        if getattr(self.Meta,'url',False) and 'slug' in self.headers:
            self.apply_hyperlinks()
        return  mark_safe(json.dumps({
            'options': self.options,
            'id': self.id,
            **self.to_dict(),
        }))

    def to_json(self):
        return self.df.to_json(orient='split',index=False)

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
        return self.Meta.model.objects.filter(**self.filters)

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
        return [self.titleize(self.Meta.model._meta.get_field(field).verbose_name) for field in self.headers]

    def verbose_column_name(self,column_name):
        return self.titleize(self.Meta.model._meta.get_field(column_name).verbose_name)

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
