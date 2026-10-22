# FS-012 planning notes

Suggestions for how this feature is built, from the person who asked for it. The build answers each
one by name.

## N1. Load the children with htmx

Load a parent's children into the window dynamically with htmx, so that the table's view does not
have to supply them.

## N2. Display the filter fields with django-mvp-forms

Go through the form fields django-mvp-forms provides thoroughly when deciding how each filter field
is displayed. Range filters in particular use joins, as the django-mvp-forms documentation shows.

## N3. Use FairDM's own fields for FairDM records

Filters against core FairDM records, such as dataset and project, use the form fields FairDM
provides for those records.

## N4. Start from the latest FairDM, django-mvp and django-mvp-forms

Update to the latest FairDM, and make sure django-mvp and django-mvp-forms are also at their latest
releases, before the build starts.
