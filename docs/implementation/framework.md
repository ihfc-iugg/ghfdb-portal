<!-- > {sub-ref}`wordcount-words` words | {sub-ref}`wordcount-minutes` min read -->
# Framework

## Geoluminate
```{figure} /_static/geoluminate.svg
:align: center
:target: https://www.geoluminate.io
:width: 100%
```

The Global Heat Flow Database is built using the [Geoluminate Research Database Framework](https://geoluminate.github.io/geoluminate/). Geoluminate is a high-level wrapper around the Django Web Framework and is designed to simplify the process of creating online data repositories for research communities that adhere to a consistent user experience and data model in order to maximize findability, accessibility, interoperability, and reusability under the FAIR data principles.

## Why Geoluminate?

Alternative frameworks aimed at the research community require us to map fields onto an existing data model or store domain relevant data as plain text/json objects in the database. This approach is not ideal for a number of reasons:

- It requires us to maintain a separate data model in addition to the database schema, which is not only redundant but also increases the risk of data inconsistencies.
- It makes it difficult to query the database using SQL, which is the standard language for relational databases.
- It makes it difficult to integrate with other applications that use a relational database.

Geoluminate solves these problems by allowing us to define our data model in such a way that the database schema itself is altered. In doing so, the fields in our data model always exist in the database schema and we therefore retain all the benefits of a modern relational database including data integrity, data validation, and table indexing.

```{seealso}
For more information on Geoluminate, please visit [geoluminate.io](www.geoluminate.io) or view the [online documentation](https://geoluminate.github.io/geoluminate/).
```
