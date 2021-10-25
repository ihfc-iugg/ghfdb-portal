import csv
from datetime import datetime as dt
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from .forms import UploadForm, ConfirmUploadForm
from django.views.generic import TemplateView
from thermoglobe.mixins import TableMixin

from django.core.cache import caches
cache = caches['file_cache']

from . import resources, import_choices

class UploadView(TableMixin, TemplateView):
    template_name = 'upload.html'
    confirm_template_name = 'upload_confirm.html'
    form = UploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['templates'] = ['heat_flow','gradient','temperature','conductivity','heat_production']
        context['upload_success'] = self.request.session.pop('upload_success',False)
        return context

    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            # submitted form is valid so temporarily save data to cache for later use
            import_file = form.cleaned_data.pop('data')

            # read in the dataset
            dataset = self.get_dataset(import_file)
            # A HTTPResponse will be returned if an error is enounctered reading the file
            if isinstance(dataset, HttpResponse):
                return dataset 

            # get the relevant resource
            resource = self.get_resource_class(form)

            #import the data
            result = resource.import_data(dataset, dry_run=True, user=request.user)

            # Something wen't wrong on our side      
            if result.has_errors():     
                context.update(
                    table= self.prepare_output_table(result, errors='error'),
                    page= self.get_page(15),
                    errors = result.rows,
                )
            # User did something wrong
            elif result.has_validation_errors():  
                context.update(
                    table= self.prepare_output_table(result, errors='validation'),
                    page = self.get_page(15),
                    validation_errors = result.invalid_rows,
                )
            else:
                # save to cache so we can redirect and load in another view
                cache.set(request.session.get('session_key'), import_file)
                context.update(
                    confirm_form = self.form(initial=form.cleaned_data,hidden=True),
                    table = self.prepare_output_table(result),
                    page = self.get_page(14),
                    sidebar='inactive',
                )
            return render(request, self.confirm_template_name,context=context)

        else:
            context['form'] = form
            return render(request, self.template_name,context=context)


    def get_bibtex_data(form):
        if not form.cleaned_data['bibtex']:
            form.cleaned_data['bibtex'] = get_unpublished_bibtex(form.cleaned_data)
        return form

    def get_template_response(self, request, context, status):
        return render(request, 
            self.get_template(status), 
            context=context,
            )

    def get_resource_class(self, form):
        resource_switch = {
            '0': resources.IntervalResource(),
            '1': resources.IntervalResource(),
            '2': resources.TempResource(),
            '3': resources.ConductivityResource(form.cleaned_data['bibtex']),
            '4': resources.HeatGenResource(),
        }
        return resource_switch[str(form.cleaned_data['data_type'])]

    def get_dataset(self, data_file):
        try:
            data = data_file.read().decode('utf-8')
        except UnicodeDecodeError as e:
            return HttpResponse(_(u"<h1>Imported file has a wrong encoding: {}</h1>".format(e)))
        except Exception as e:
            return HttpResponse(_(u"<h1>{} encountered while trying to read file: {}</h1>".format(type(e).__name__, import_file.name)))

        return Dataset().load(data, format='csv')

    def get_html_tag(self, import_type, id=None):
        tags = {
            'new': '<i class="fas fa-check-circle text-success"></i>',
            'update': '<i class="fas fa-pen-square text-info"></i>',
            # 'error': '<i class="fas fa-times-circle text-danger"></i>',
            'skip': '<i class="fas fa-forward text-info"></i>',
            'error': f'<i class="fas fa-exclamation-triangle text-warning" data-toggle="modal" data-target="#{id}"></i>',
            # 'new': '<span class="badge badge-success">{}</span>',
            # 'update': '<span class="badge badge-info">{}</span>',
            # 'error': '<span class="badge badge-danger">{}</span>', 
            # 'invalid': '<span class="badge badge-warning">{}</span>', 
            # 'skip': '<span class="badge badge-skip">{}</span>', 
            }
        return tags[import_type].format(import_type)

    def prepare_output_table(self, result, errors=False):
        # adds html icon to display import_type
        if errors == 'validation':
            table = [[self.get_html_tag('error',f"row-{id_num}")] + [str(r) for r in row.values] for id_num, row in enumerate(result.invalid_rows)]
        elif errors == 'error':
            table = [[self.get_html_tag('error',f"row-{id_num}")] + self.get_values_from_row(row) for id_num, row in enumerate(result.rows) if row.errors]
        else:
            table = [[self.get_html_tag(row.import_type)] + row.diff for row in result.rows]

        headers = result.diff_headers.copy()
        headers.insert(0, '_')

        return dict(
            id='importResult',
            data=json.dumps(table),
            columns=[field.replace('_',' ') for field in headers],
            )

    def get_values_from_row(self, row):
        # what a cunt of a thing this is!
        return [str(val) for val in row.errors[0].row.values()]


# Create your views here.
def get_upload_template(request,template_name):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}_upload_template.csv"'.format(template_name)
    writer = csv.writer(response)
    fields = getattr(import_choices, template_name)
    writer.writerow([field[1] if len(field) == 2 else field for field in fields])
    return response

@require_POST
def upload_confirm(request):
    data = cache.get(request.session.get('session_key'))
    if request.POST.get('bibtex') == '':
        updated = request.POST.copy()
        updated.update(bibtex=get_unpublished_bibtex(request.POST))
        form = ConfirmUploadForm(updated, {'data':data})
    else:
        form = ConfirmUploadForm(request.POST, {'data':data})
        
    if form.is_valid():
        form.save()
        request.session['upload_success'] = True
    return redirect(reverse("thermoglobe:upload"))

def get_unpublished_bibtex(form):
    timestamp = dt.now()
    return "@Unpublished{{{last_name}{year},\
        author    = {{{last_name}, {first_name}}},\
        title     = {{Unpublished data upload to Heatflow.org - {date}}},\
        month     = {{{month}}},\
        year      = {{{year}}},\
        timestamp = {{{date}}},\
        }}".format(
            last_name=form['last_name'],
            first_name=form['first_name'],
            month=timestamp.strftime('%b').lower(),
            year=timestamp.strftime('%Y'),
            date=timestamp.strftime('%Y-%m-%d'),
        )