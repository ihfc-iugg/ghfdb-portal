# Datasets

Datasets are the fundamental building block of the Global Heat Flow Database web application. Datasets serve as containers that store parent and child values for a particular literature item. Creation of a dataset is necessary to include your data within the Global Heat Flow Database and allows you to easily manage and publish your data in accordance with community standards.


**Basic Metadata:**

- title
- contributors
- descriptions
- funding
- keywords
- dates
- license

**Relationships**

Belongs to:

- A project (optional)
- A literature item (optional)
- A review entry

Contains many:

- Samples (heat flow sites)



## Dataset Creation

Easily create new datasets within the GHFDB application using the dataset creation page. The dataset creation page provides a simple form that prompts you for a title and allows you to choose whether the dataset is publicly listed or not. Once a dataset has been created, you will be redirected to the dataset detail page where you can easily manage related data and metadata.

:::{figure-md}
![dataset_list](images/dataset_create.png){}

Figure 1. The dataset creation page allows community members to easily create a new dataset within the GHFDB application.
:::

:::{admonition} Checklist

✅ Define reusable form for dataset creation

🔲 Decide on required metadata for creation

:::


## Viewing Datasets

### Viewing metadata

The dataset detail page provides access to detailed metadata related to a particular dataset that has been listed as publicly available. If the dataset meets the minimum quality standards defined by the community and passes the internal review process, then the accompanying data is available for download from this page.

### Accessing data

:::{figure-md}
![dataset_list](images/dataset_detail.png){}

Figure 2. The dataset detail page displays detailed information related to a particular dataset.
:::




## Catalogue Page

The Global Heat Flow Database web application provides a catalogue page that allows you to discover and browse public datasets that have been made public by other community members. The catalogue page provides a simple search interface that allows you to search for datasets by title, description, author, keyword, and more. The catalogue page also provides a simple filtering interface that allows you to filter datasets by keyword, author, and more.


:::{figure-md}
![dataset_list](images/dataset_list.png){}

Figure 3. The dataset catalogue page provides a simple search and filtering interface that allows you to discover and browse public datasets that have been made public by other community members.
:::


## Roadmap

- ✅ Detailed metadata collection in accordance with DataCite schema. XML metadata can be easily downloaded and submitted to GFZ Data Services for formal publication.
- 🔲 Discover and browse public datasets that have been made public by other community members via an intuitive catalogue page.
