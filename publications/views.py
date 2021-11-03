from django.shortcuts import render
from publications.models import Publication
from collections import defaultdict
from string import capwords

def year(request, year=None):
	years = []
	publications = Publication.objects.select_related()
	if year:
		publications = publications.filter(year=year)

	for publication in publications:
		# if publication.type.hidden:
		# 	continue
		if not years or (years[-1][0] != publication.year):
			years.append((publication.year, []))
		years[-1][1].append(publication)


	return render(request, 'publications/years.html', {
			'years': years
		})

def keyword(request, keyword):
	keyword = keyword.lower().replace(' ', '+')
	candidates = Publication.objects.filter(keywords__icontains=keyword.split('+')[0])
	publications = []

	for i, publication in enumerate(candidates):
		if keyword in [k[1] for k in publication.keywords_escaped()]:
			publications.append(publication)

	return render(request, 'publications/keyword.html', {
			'publications': publications,
			'keyword': keyword.replace('+', ' ')
		})

def id(request, publication_id):
	publications = Publication.objects.filter(pk=publication_id)

	if 'plain' in request.GET:
		return render(request, 'publications/publications.txt', {
				'publications': publications
			}, content_type='text/plain; charset=UTF-8')

	if 'bibtex' in request.GET:
		return render(request, 'publications/publications.bib', {
				'publications': publications
			}, content_type='text/x-bibtex; charset=UTF-8')

	if 'mods' in request.GET:
		return render(request, 'publications/publications.mods', {
				'publications': publications
			}, content_type='application/xml; charset=UTF-8')

	if 'ris' in request.GET:
		return render(request, 'publications/publications.ris', {
				'publications': publications
			}, content_type='application/x-research-info-systems; charset=UTF-8')

	for publication in publications:
		publication.links = publication.customlink_set.all()
		publication.files = publication.customfile_set.all()

	return render(request, 'publications/id.html', {
			'publications': publications
		})

def author(request, name):
    fullname = capwords(name.replace('+', ' '))
    fullname = fullname.replace(' Von ', ' von ').replace(' Van ', ' van ')
    fullname = fullname.replace(' Der ', ' der ')

    # take care of dashes
    off = fullname.find('-')
    while off > 0:
        off += 1
        if off <= len(fullname):
            fullname = fullname[:off] + fullname[off].upper() + fullname[off + 1:]
        off = fullname.find('-', off)

    # split into forename, middlenames and surname
    names = name.replace(' ', '+').split('+')
    # handle empty values
    names = [n for n in names if n] or ['']

    # construct a liberal query
    surname = names[-1]
    surname = surname.replace(u'ä', u'%%')
    surname = surname.replace(u'ae', u'%%')
    surname = surname.replace(u'ö', u'%%')
    surname = surname.replace(u'oe', u'%%')
    surname = surname.replace(u'ü', u'%%')
    surname = surname.replace(u'ue', u'%%')
    surname = surname.replace(u'ß', u'%%')
    surname = surname.replace(u'ss', u'%%')

    query_str = u'SELECT * FROM {table} ' \
                'WHERE lower({table}.authors) LIKE lower(%s) ' \
                'ORDER BY {table}.year DESC, {table}.month DESC, {table}.id DESC'
    query_str = query_str.format(table=Publication._meta.db_table)
    query = Publication.objects.raw(query_str, ['%' + surname + '%'])

    # find publications of this author
    publications = []
    publications_by_type = defaultdict(lambda: [])

    # further filter results
    if len(names) > 1:
        name_simple = Publication.simplify_name(names[0][0] + '. ' + names[-1])
        for publication in query:
            if name_simple in publication.authors_list_simple:
                publications.append(publication)
                publications_by_type[publication.type_id].append(publication)

    elif len(names) > 0:
        for publication in query:
            if Publication.simplify_name(names[-1].lower()) in publication.authors_list_simple:
                publications.append(publication)
                publications_by_type[publication.type_id].append(publication)

    return render(request, 'publications/author.html', {
        'publications': publications,
        'author': fullname
    })