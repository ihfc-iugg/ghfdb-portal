from database.models import Site, Interval, Correction
from import_export import resources
from django.utils.html import mark_safe
from import_export.instance_loaders import ModelInstanceLoader
from core.resources import ResourceMixin

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
                # instance = self.get_queryset().get_or_create(**params)
                # return instance
                return Site(**params)
            else:
                return None
        except self.resource._meta.model.DoesNotExist:
            return None

class SiteResource(ResourceMixin):

    class Meta:
        model = Site
        exclude = ['seamount_distance','outcrop_distance','crustal_thickness','continent','country','political','province','sea','slug'] + [f.name for f in model._meta.related_objects]
        #  + [f.name for f in model._meta.many_to_many]
        # fields = [f.name for f in Site._meta.concrete_fields]

        import_id_fields = ['id']
        # skip_diff=True
        instance_loader_class = CustomLoader
        # use_bulk = True
        # force_init_instance = True

class CorrectionsMixin(resources.ModelResource):
    pass

class IntervalResource(CorrectionsMixin,ResourceMixin):
    class Meta:
        model = Interval
        exclude = ['date_added']
        import_id_fields = ['id']

    # def before_import_row(self, row, row_number=None, **kwargs):

    #     def get_instance(row, corr_type, value):
    #         interval = Interval.objects.get(id=row.get('id'))
    #         if row.get(corr_type+'_flag'):
    #             if row.get(corr_type) != "":
    #                 return interval.corrections.create(type=value, value=row.get(corr_type))
    #             else:
    #                 return interval.corrections.create(type=value, interval=interval)
    #             # corrections.append(Correction(type='CLIM', value=val))

    #     types = [
    #         ('CLIM','climate'),
    #         ('TOPO','topographic'),
    #         ('REFR','refraction'),
    #         ('EROS','sed_erosion'),
    #         ('FLUI','fluid'),
    #         ('BWV','bwv'),
    #         ('COMP','compaction'),
    #         ('OTH','other'),
    #         ('CMPS','composite'),
    #         ('TILT','tilt'),
    #     ]

    #     row['corrections'] = []
    #     for value, corr_type in types:
    #         x = get_instance(row, corr_type, value)
    #         if x:
    #             row['corrections'].append(x)
      
    #     return super().before_import_row(row, row_number, **kwargs)