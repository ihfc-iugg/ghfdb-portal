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

## D2. Dataset and project are the FairDM filters

A parent belongs to a dataset, and a dataset to a project, so those are the two FairDM records a
reader can narrow by. Contributor was left out: a filter over people is a different question,
"what has this person contributed", and is better served on the person's own page.

## D3. Latitude and longitude are a box

Two independent range filters on latitude and longitude describe a box, which is what a reader
means by "sites in this region" without a map. Drawing an area on a map belongs to the map viewer.

## D4. The group is labelled GHFDB

The group holds the two ways of browsing the GHFDB, so it is named for it. The two entries read
"Map Viewer" and "Parent Table", as settled at the sketch.

## D5. The counts on a row are of the children the visitor may see

A parent can have a child in a dataset the visitor may not see. Counting it on the row would make
the row's "n (m)" disagree with its window, which names only the children the visitor may open
(SC-004). The row therefore counts the visible children, and the window still says how many more
belong to datasets that have not been published.

## D6. Exploration purpose sorts by its first term

`explo_purpose` holds several terms. FR-007 asks that every column sort, so it sorts by the
alphabetically first of its terms, read by a subquery so the table's counts are not multiplied.
`p_comment` sorts like any other column.

## D7. Every sort ends in the parent's ID

A sort on a column with many equal values (environment, quality) gives the database no order among
them, so a page could repeat a parent or skip one. Every sort, the default included, ends in
`ghfdb_id`.

## D8. The site name search matches any word

The toolbar's search is django-mvp's `SearchFilter`, which lists a site whose name contains any
word of what was typed, as every other list in the portal does. A typed fragment of one word,
which is what US-2 scenario 7 describes, matches as the spec says.

## D9. Invalid values are reported on the filters a person types into

FR-016 is met for the range filters, which take typed input and report an error against the
filter. The toolbar's checkbox filters only send their own values from the page. A value edited
into the address by hand is dropped without a message.
