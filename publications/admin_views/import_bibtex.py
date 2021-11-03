from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from publications.models import Publication
from django.views.generic import TemplateView
from publications.forms import UploadForm
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.utils.translation import gettext as _
import pandas as pd
from io import TextIOWrapper
import bibtexparser as bib

class ImportBibtex(TemplateView):
    template_name = 'admin/publications/import_bibtex.html'
    confirm_template_name = 'upload_confirm.html'
    form = UploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(dict(
            form = self.form,
            title='Import Bibtex',
        ))
        return context

    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            # submitted form is valid so temporarily save data to cache for later use
            imported_file = form.cleaned_data.pop('file')
            f = TextIOWrapper(imported_file.file, encoding='utf-8')
            data = pd.read_csv(f,delimiter='|',header=None)

            # container for error messages
            errors = []
            publications = []
            new=0

            # try adding publications
            for i, row in data.iterrows():


                if not row[1] or pd.isnull(row[1]):
                    publications.append(Publication(id=row[0]))
                    continue
                # try:
                #     entry = bib.loads(row[1]).entries[0]
                # except IndexError:
                #     errors.append(dict(entry=row[1],
                #         message='Could not parse bibtex'))
                #     continue 

                # # add publication
                # citekey = entry.pop('ID','')
                
                # entry_type = entry.pop('type',entry.pop('ENTRYTYPE',''))
                # # entry_type = entry.pop('ENTRYTYPE','')

                # removed = {k:v for k,v in entry.items() if k not in [f.name for f in Publication._meta.fields]}
                # # print(removed)
                # entry = {k:v for k,v in entry.items() if k in [f.name for f in Publication._meta.fields]}
                bibtex_str = row[1]
                try:
                    obj, created = Publication.objects.get_or_create(id=row[0])
                    publications.append(obj)


                    obj.save(bibtex=bibtex_str)
                    if created: new+=1
                
                except Exception as e:
                    errors.append({'message': e,'entry': bibtex_str})
            if errors:
                # some error occurred
                return render(
                    request,
                    'admin/publications/import_bibtex.html', {
                        'errors': errors,
                        'title': 'Import BibTex',
                        'request': request})
            else:
                # save publications
                for publication in publications:
                    try:
                        publication.save()
                    except Exception as e:
                        msg = e

                if len(publications) > 1:
                    msg = 'Successfully added ' + str(len(publications)) + ' publications.'
                else:
                    msg = 'Successfully added ' + str(len(publications)) + ' publication.'

                # show message
                messages.info(request, msg)

                # redirect to publication listing
                if len(publications) == 1:
                    return HttpResponseRedirect(f'../{publications[0].id}/change/')
                else:
                    return HttpResponseRedirect('../')

    def get_dataset(self, data_file):
        try:
            data = data_file.read().decode('utf-8')
        except UnicodeDecodeError as e:
            return HttpResponse(_(u"<h1>Imported file has a wrong encoding: {}</h1>".format(e)))
        except Exception as e:
            return HttpResponse(_(u"<h1>{} encountered while trying to read file: {}</h1>".format(type(e).__name__)))

        return data
