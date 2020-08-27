
class MultiTableMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tables = getattr(self,'tables',[]) 
        if getattr(self,'filter_object_on',False):
            tables = [table({self.filter_object_on:self.get_object()}) for table in tables]
        else:
            tables = [table for table in tables]
        tables = {table.id:table for table in tables}
        for table in tables.values():
            if table.has_data:
                table.active = True
                break 

        context['tables'] = tables
        return context


class TableMixin():

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def table(self, headers, qs=None, ID='dataTable', options=None, link='',data=None):
        if qs is not None:
            qs = qs
        else:
            qs = self.get_queryset()

        if qs.exists() and data is None:
            data = list(qs)
        else:
            data = data

        return dict(
        columns = headers,
        id = ID,
        options = options if options is not None else getattr(self,'table_options'),
        link = link,
        data = data,
        )