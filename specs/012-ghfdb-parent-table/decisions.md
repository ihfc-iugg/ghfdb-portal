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
"Map Viewer" and "Table". The labels are the build's to settle at the sketch.
