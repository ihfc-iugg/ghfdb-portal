from .models import Site, Conductivity, Interval, HeatProduction, Temperature
from import_export import resources
from django.utils.html import mark_safe
from tqdm import tqdm


class ResourceMixin(resources.ModelResource):

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        self.pbar = tqdm(total=len(dataset))

    def before_import_row(self,row=None,**kwargs):
        pass

    def after_import_row(self, row, row_result, **kwargs):
        """ Updates the progress bar"""
        self.pbar.update(1)

    def after_import(self, dataset, result, using_transactions, dry_run,**kwargs):
        self.clean_result(result)
        print('Import Summary:')
        for key, count in result.totals.items():
            if count:
                print('\t',key,': ',count)

    def clean_result(self,result):
        """Cleans up the result preview"""
        # find the columns that do not contain any data and store the index
        remove_these = []
        if result.has_validation_errors():
            # loop through each column of the result
            for i, header in enumerate(result.diff_headers.copy()):
                has_data = False
                # look at each value in the column
                for row in result.invalid_rows: 
                    if row.values:
                        # Applies a html background to field specific errors to help user identify issues
                        if header in row.field_specific_errors.keys():
                            row.values = list(row.values)
                            row.values[i] = mark_safe('<span class="bg-danger">{}</span>'.format(row.values[i]))
                        # if a values is found in this column then mark it as containing data
                        if row.values[i] and row.values[i] != '---':
                            has_data = True
                            break
                # if no data was found in the column, delete it
                if not has_data:
                    remove_these.append(i)
                    # result.diff_headers.remove(header)

            # result.diff_headers.pop()
            for i in sorted(remove_these,reverse=True):
                result.diff_headers.pop(i)
                for row in result.invalid_rows:

                    row.values = list(row.values)
                    row.values.pop(i)
                    # row.values.pop()

        else:
            for i, header in enumerate(result.diff_headers.copy()):
                has_data = False
                for row in result.rows: 
                    if row.diff:
                        if row.diff[i]:
                            has_data = True
                            break
                if not has_data:
                    remove_these.append(i)
 
            for i in sorted(remove_these,reverse=True):
                result.diff_headers.pop(i)
                for row in result.rows:
                # remove stored indices from each row of the result
                    if row.diff:
                        del row.diff[i]


        result.diff_headers = [h.replace('_',' ').capitalize() for h in result.diff_headers]

class SiteResource(ResourceMixin):

    class Meta:
        model = Site
        exclude = ['geom','seamount_distance','outcrop_distance','crustal_thickness','continent','country','political','province','sea','slug']
        import_id_fields = ['id']


class TempResource(ResourceMixin):
    class Meta:
        model = Temperature
        exclude = ['date_added']
        import_id_fields = ['id']


class HeatProductionResource(ResourceMixin):
    class Meta:
        model = HeatProduction
        exclude = ['date_added']
        import_id_fields = ['id']



class ConductivityResource(ResourceMixin):
    class Meta:
        model = Conductivity
        exclude = ['date_added']
        import_id_fields = ['id']


class CorrectionsMixin(resources.ModelResource):
    pass

class IntervalResource(CorrectionsMixin,ResourceMixin):
    class Meta:
        model = Interval
        exclude = ['date_added']
        import_id_fields = ['id']

