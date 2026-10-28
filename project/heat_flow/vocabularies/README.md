# Shipped vocabularies

Every file below is a published SKOS vocabulary, kept unmodified so loading never needs the
network. A model field names a vocabulary in `project/heat_flow/vocabularies/__init__.py`, and
`manage.py sync_vocabularies` loads the file.

| File | Vocabulary | Source | Licence |
|---|---|---|---|
| `*.ttl` | The IHFC vocabularies for the Global Heat Flow Database | Release 2026.1 of [ihfc-iugg/ihfc-vocabularies](https://github.com/ihfc-iugg/ihfc-vocabularies/releases/tag/v2026.1), <https://doi.org/10.5880/fidgeo.2026.065> | CC BY 4.0 |
| `odm2/elevationdatum.rdf` | ODM2 Elevation Datum | <http://vocabulary.odm2.org/api/v1/elevationdatum/?format=skos>, retrieved on 2026-10-28 | See below |

The ODM2 file states no licence of its own. The
[ODM2 project](https://github.com/ODM2/ODM2/blob/master/LICENSE) publishes its source under a
BSD-style licence from the Consortium of Universities for the Advancement of Hydrologic Science.

To move to a new release of the IHFC vocabularies, replace the `.ttl` files with the release's
and run `manage.py sync_vocabularies`. A new term needs no migration.
