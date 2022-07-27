from database.models import Site, Interval, Correction
from import_export import resources
from django.utils.html import mark_safe
from import_export.instance_loaders import ModelInstanceLoader
from core.resources import ResourceMixin
from .widgets import ReferenceWidget, SiteWidget, CorrectionsWidget
from publications.models import Publication
from import_export.fields import Field

class CustomLoader(ModelInstanceLoader):

    def get_queryset(self):
        return self.resource.get_queryset()

    def get_instance(self, row):
        try:
            params = {}
            for key in self.resource.get_import_id_fields():
                field = self.resource.fields[key]
                params[field.attribute] = field.clean(row)
            if params:
                instance = self.get_queryset().get_or_create(**params)
                return instance
                # return Site(**params)
            else:
                return None
        except self.resource._meta.model.DoesNotExist:
            return None

class SiteResource(ResourceMixin):

    class Meta:
        model = Site
        exclude = ['continent','country','political','province','ocean','plate','slug','geom','date_added','id'] + [f.name for f in model._meta.related_objects]
        import_id_fields = ['name','lat','lng']
        # instance_loader_class = CustomLoader
        widgets = {
                'q_acq': {'format': '%Y-%m'},
                }
        # skip_diff=True
        # use_bulk = True
        # force_init_instance = True


    def before_import_row(self, row, row_number=None, **kwargs):
        row['id'] = row['ID']
        pass

class IntervalResource(ResourceMixin):

    site = Field(attribute='site',
        widget = SiteWidget(Site)
        )
    corrections = Field(attribute='corrections',
        widget = CorrectionsWidget(Correction)
        )

    reference_id = Field(attribute='reference',
        column_name = 'Ref_1', 
        widget = ReferenceWidget(Publication, field='label')
        )


    class Meta:
        model = Interval
        exclude = ['date_added']
        import_id_fields = ['historic_id']
        force_init_instance = True
        # raise_errors=True
        skip_unchanged = False
        report_skipped= True
        skip_diff = True
        clean_model_instances = True
        widgets = {
                'q_acq': {'format': '%Y-%m-%d'},
                }

    def before_import_row(self, row, row_number=None, **kwargs):
        row['reference_id'] = row.get('Ref_1')
        row['site'] = ''
        row['historic_id'] = row['ID']
        row['corrections'] = ""
        if not row['qc']:
            row['qc'] = row['q']
            row['childcomp'] = True

        # converts choice field inputs to lower case for consisteny
        row = self.choice_fields_to_lowercase(row)

        row = self.clean_date(row)

        pass


    def clean_date(self, row):
        if row.get('q_acq'):
            date_parts = str(row['q_acq']).split('-')

            # for format YYYY-MM
            if len(date_parts) == 2:
                row['q_acq'] = f'{row["q_acq"]}-01'

            # for format YYYY only
            elif len(date_parts) == 1:
                row['q_acq'] = f'{row["q_acq"]}-01-01'

        return row

    def choice_fields_to_lowercase(self, row):
        """Convert choice field inputs to lower case for consistency """
        choice_fields = [f.name for f in self.Meta.model._meta.fields if f.choices]

        for f in choice_fields:
            if row.get(f):
                row[f] = row[f].lower()
        return row


    # def before_import_row(self, row, row_number=None, **kwargs):
    #     for item in row['corrections']:
    #         if item[1]:
    #             item[0].save()
    #     row['corrections'] = [i[0] for i in row['corrections']]
    #     return super().before_import_row(row, row_number, **kwargs)

    #     def get_instance(row, corr_type, value):
    #         interval = Interval.objects.get(id=row.get('id'))
    #         if row.get(corr_type+'_flag'):
    #             if row.get(corr_type) != "":
    #                 return interval.corrections.create(type=value, value=row.get(corr_type))
    #             else:
    #                 return interval.corrections.create(type=value, interval=interval)
    #             # corrections.append(Correction(type='CLIM', value=val))

    #     row['corrections'] = []
    #     for value, corr_type in types:
    #         x = get_instance(row, corr_type, value)
    #         if x:
    #             row['corrections'].append(x)
      
    #     return super().before_import_row(row, row_number, **kwargs)