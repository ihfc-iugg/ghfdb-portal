import django

from distutils.version import StrictVersion
from django.template import Library, RequestContext
from django.template.loader import get_template
from django.utils.html import escape
from django.utils.safestring import mark_safe
from publications.models import Publication
from re import sub

register = Library()

GREEK_LETTERS = \
	'[Aa]lpha|[Bb]eta|[Gg]amma|[Dd]elta|[Ee]psilon|[Zz]eta|' + \
	'[Ee]ta|[Tt]heta|[Ll]ambda|[Mm]u|[Nn]u|[Pp]i|[Ss]igma|[Tt]au|' + \
	'[Pp]hi|[Pp]si|[Cc]hi|[Oo]mega|[Rr]ho|[Xx]i|[Kk]appa'


def render_template(template, request, args):
	if StrictVersion(django.get_version()) < StrictVersion('1.8.0'):
		return get_template(template).render(RequestContext(request, args))
	return get_template(template).render(args, request)


def get_publications(context, template='publications/publications.html'):
	"""
	Get all publications.
	"""
	publications = Publication.objects.select_related()

	if not publications:
		return ''

	return render_template(template, context['request'], {'publications': publications})


def get_publication(context, id):
	"""
	Get a single publication.
	"""

	pbl = Publication.objects.filter(pk=int(id))

	if len(pbl) < 1:
		return ''


	return render_template(
		'publications/publication.html', context['request'], {'publication': pbl[0]})


def get_publication_list(context, list, template='publications/publications.html'):
	"""
	Get a publication list.
	"""
	publications = list.publication_set.all()

	if not publications:
		return ''

	return render_template(
		template, context['request'], {'list': list, 'publications': publications})


def tex_parse(string):
	"""
	Renders some basic TeX math to HTML.
	"""

	string = string.replace('{', '').replace('}', '')
	def tex_replace(match):
		return \
			sub(r'\^(\w)', r'<sup>\1</sup>',
			sub(r'\^\{(.*?)\}', r'<sup>\1</sup>',
			sub(r'\_(\w)', r'<sub>\1</sub>',
			sub(r'\_\{(.*?)\}', r'<sub>\1</sub>',
			sub(r'\\(' + GREEK_LETTERS + ')', r'&\1;', match.group(1))))))
	return mark_safe(sub(r'\$([^\$]*)\$', tex_replace, escape(string)))


register.simple_tag(get_publications, takes_context=True)
register.simple_tag(get_publication, takes_context=True)
register.simple_tag(get_publication_list, takes_context=True)
register.filter('tex_parse', tex_parse)
