# FairDM's vocabularies

FairDM stores the type of every description, date and identifier, every contributor role and
every sample status as a concept of one of these vocabularies. They are copied unmodified from
[FAIR-DM/fairdm-vocabularies](https://github.com/FAIR-DM/fairdm-vocabularies) at commit
`c19b9cc`, under its MIT licence, because their addresses under
`https://w3id.org/fairdm/vocabularies/` are not published yet. `config/settings.py` declares
each one, and `manage.py sync_vocabularies` loads them.

The portal's own heat flow vocabularies live with the code that uses them, in
`project/heat_flow/vocabularies/`.
