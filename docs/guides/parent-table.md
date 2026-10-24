# The GHFDB parent table

The GHFDB parent table lists the parents of the Global Heat Flow Database, one row each, so a
visitor can scan them, sort them and open one. It is at `/ghfdb/parents/` and is open to anyone
reading the portal, signed in or not.

## Which parents it lists

The table lists the parents the portal serves to that visitor, and nothing else. It applies the
rule the [published structure API](published-structure-api.md) applies to its parent route, from
the same function, `served_parents()`, so the two never disagree:

- A parent is listed when its dataset is public and published, or the visitor holds a level on it.
- A parent is listed only when the site it describes is visible to the visitor too. A parent in
  a public dataset whose site sits in a private one is left out.
- A parent with no published identifier is not listed.

A signed-in contributor sees their private datasets' parents beside the public ones. The number
shown above the table is the number of parents listed for that visitor.

## The columns

A row holds the parent's published columns, under their published names: `ID_parent`, `q`,
`q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `explo_method`,
`explo_purpose`, `total_depth_MD`, `total_depth_TVD`, `corr_HP_flag`, `quality_parent` and
`p_comment`, with `children` after `q_uncertainty`.

- `ID_parent` links to the parent's page and `name` to the page of its site.
- `environment` and `explo_method` show the term's label, never the stored key.
- `explo_purpose` joins a site's purposes with semicolons.
- A value that is not recorded shows a dash, read out as "Not recorded". A recorded zero shows as
  `0`: the table never turns an empty value into a number.

## Sorting

Every column sorts, ascending and then descending, by pressing its heading. `children` sorts on the
number of children, `name` on the site's name and `explo_purpose` on its alphabetically first purpose.

When rows tie on the chosen column, the table puts them in order of `ID_parent`. A parent therefore
appears on exactly one page of a sorted table, however many pages it has, and a page reached twice
shows the same rows.

## Paging

The table shows a fixed number of rows to a page and links to the others. The page is part of the
address (`?page=2`), as is the sort, so an address reopens the same page in the same order. The
number of queries the page makes does not grow with the number of rows on it.
