from import_export import resources
from django.utils.html import mark_safe
from tqdm import tqdm
from .models import Publication
import bibtexparser as bib
from taggit.utils import _parse_tags
from import_export.fields import Field
from bibtexparser.bparser import BibTexParser, parse
import bibtexparser as bib
from import_export.widgets import ManyToManyWidget, Widget
from django.utils.encoding import force_str, smart_str
import bibtexparser.customization as clean
from bibtexparser.latexenc import latex_to_unicode, string_to_latex, protect_uppercase

# def convert_to_unicode(record):
#     """
#     Convert accent from latex to unicode style.

#     :param record: the record.
#     :type record: dict
#     :returns: dict -- the modified record.
#     """
#     for val in record:
#         if isinstance(record[val], list):
#             record[val] = [
#                 latex_to_unicode(x) for x in record[val]
#             ]
#         if isinstance(record[val], dict):
#             record[val] = {
#                 k: latex_to_unicode(v) for k, v in record[val].items()
#             }
#         else:
#             record[val] = latex_to_unicode(record[val])
#     return record

def bibtex_cleaner(entry):
    entry = clean.keyword(entry)
    if entry.get('keyword'):
        entry['keyword'] = ','.join(entry['keyword']).lower()
    # print(entry.get('keyword'))
    entry = clean.page_double_hyphen(entry)
    entry = clean.convert_to_unicode(entry)
    # entry = clean.add_plaintext_fields(entry)

    entry = clean.link(entry)
    entry = clean.doi(entry)
    # print(entry.get('keyword'))

    return entry


class TaggitField(Field):
    """
    Custom field to add a list of strings (tags) to a TaggableManager instance.
    """
    def save(self, obj, data, is_m2m=False):
        if not self.readonly:
            attrs = self.attribute.split('__')
            for attr in attrs[:-1]:
                obj = getattr(obj, attr, None)
            cleaned = self.clean(data) #data parsed by TaggitWidget
            if cleaned is not None:
                obj.add(*cleaned)

    # def get_value(self, obj):
    #     """
    #     Returns the value of the object's attribute.
    #     """
    #     if self.attribute is None:
    #         return None

    #     attrs = self.attribute.split('__')
    #     value = obj

    #     for attr in attrs:
    #         try:
    #             value = getattr(value, attr, None)
    #         except (ValueError, ObjectDoesNotExist):
    #             # needs to have a primary key value before a many-to-many
    #             # relationship can be used.
    #             return None
    #         if value is None:
    #             return None

    #     # RelatedManager and ManyRelatedManager classes are callable in
    #     # Django >= 1.7 but we don't want to call them
    #     if callable(value) and not isinstance(value, Manager):
    #         value = value()
    #     return value

class TaggitWidget(Widget):

    def __init__(self, separator=', ', field='pk', force_lower=True, *args, **kwargs):
        self.separator = separator
        self.field = field
        self.force_lower = force_lower
        super().__init__(*args, **kwargs)

    def clean(self, value, row=None, *args, **kwargs):
        if value:
            if self.force_lower:
                value = value.lower()
            return _parse_tags(value)

    def render(self, value, obj=None):
        ids = [smart_str(getattr(obj, self.field)) for obj in value.all()]
        return self.separator.join(ids)


class PublicationResource(resources.ModelResource):

    keywords = TaggitField(attribute='keywords__name', widget=TaggitWidget(field='name'))

    class Meta:
        model = Publication
        exclude = ['pdf','source','is_verified','verified_by','date_verified']
        import_id_fields = ['id']

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        self.pbar = tqdm(total=len(dataset))

    def before_import_row(self,row=None,**kwargs):

        field_names = [f.name for f in Publication._meta.fields]
        if row['bibtex']:
            bibtex = parse(row['bibtex'],
                    customization = bibtex_cleaner,
                    homogenize_fields = True,
                    common_strings = True
                )
            if bibtex.entries:
                entry = bibtex.entries[0]
                row['keywords'] = entry.get('keyword')
                row.update({k:v for k,v in entry.items() if k in field_names})

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




