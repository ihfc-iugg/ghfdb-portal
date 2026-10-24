# FS-012 decisions

Ambiguities resolved while specifying, recorded so they can be overruled.

## Why this is a feature

After this work, a visitor can browse, filter and sort the parent heat flow values as a table and
open the list of any parent's children from its row. Today that needs the API or the map viewer. No
existing spec describes a table of parents, so it is a feature.

## D1. The table follows the API's visibility rule

A parent is listed when the visitor may see both its dataset and its site. This is the rule the
published-structure API's parent endpoint already applies (FS-006), because a parent's own
visibility does not close the case of a parent whose site is not public. Using the same rule keeps
the table and the API from disagreeing about which parents exist.

**ADR:** none — it applies docs/adr/0021-a-determination-is-served-only-through-a-served-parent.md to one more page; the rule is the ADR's, only its single home is new

## D2. Dataset and project are the FairDM filters

A parent belongs to a dataset, and a dataset to a project, so those are the two FairDM records a
reader can narrow by. Contributor was left out: a filter over people is a different question,
"what has this person contributed", and is better served on the person's own page.

**ADR:** none — a scope choice for this feature's filters, nothing downstream inherits it

## D3. Latitude and longitude are a box

Two independent range filters on latitude and longitude describe a box, which is what a reader
means by "sites in this region" without a map. Drawing an area on a map belongs to the map viewer.

**ADR:** none — local to this feature's filters

## D4. The group is labelled GHFDB

The group holds the two ways of browsing the GHFDB, so it is named for it. The two entries read
"Map Viewer" and "Parent Table", as settled at the sketch.

**ADR:** none — a label, settled by eye

## D5. The counts on a row are of the children the visitor may see

A parent can have a child in a dataset the visitor may not see. Counting it on the row would make
the row's "n (m)" disagree with its window, which names only the children the visitor may open
(SC-004). The row therefore counts the visible children, and the window still says how many more
belong to datasets that have not been published.

**ADR:** none — how one page counts its rows; it follows from the existing visibility rule and binds no other code

## D6. Exploration purpose sorts by its first term

`explo_purpose` holds several terms. FR-007 asks that every column sort, so it sorts by the
alphabetically first of its terms, read by a subquery so the table's counts are not multiplied.
`p_comment` sorts like any other column.

**ADR:** none — local to this table's sorting

## D7. Every sort ends in the parent's ID

A sort on a column with many equal values (environment, quality) gives the database no order among
them, so a page could repeat a parent or skip one. Every sort, the default included, ends in
`ghfdb_id`.

**ADR:** none — local to this table's sorting

## D8. The site name search matches any word

The toolbar's search is django-mvp's `SearchFilter`, which lists a site whose name contains any
word of what was typed, as every other list in the portal does. A typed fragment of one word,
which is what US-2 scenario 7 describes, matches as the spec says.

**ADR:** none — the toolbar search's existing behaviour, recorded for this feature

## D9. Invalid values are reported on the filters a person types into

FR-016 is met for the range filters, which take typed input and report an error against the
filter. The toolbar's checkbox filters only send their own values from the page. A value edited
into the address by hand is dropped without a message.

**ADR:** none — local to this feature's filters

## D10. A vocabulary column reads the concept's own label

**Decision**: `TermColumn` takes no vocabulary and renders `value.label()`. The annotated environment and
exploration method arrive as vocabulary concepts that already know their label, so the column holds no
vocabulary instance at all, per cell or per column.

**Why**: the sketch called `vocabulary().choices` for every cell, and a concept's `label` is a method, so the
fallback it returned was the bound method itself. Reading the label off the concept needs no lookup.

**Revisit if**: a published column ever carries a plain stored key instead of a concept.

**ADR:** none — local to this table's columns

## D11. The empty-cell mark is a span, built when the table is

**Decision**: the not-recorded mark is a `<span data-state="not-recorded">` inside the cell, built by
`not_recorded()` each time a table is constructed.

**Why**: the table is built per request, so the screen-reader text is translated for that request and the
module holds only a lazy string. django-tables2 renders a table-level default as given, so a function that
runs per table is the way to get both.

**Revisit if**: the hook should sit on the `td` itself, which needs a custom `BoundRow`.

**ADR:** none — local to this table's columns
