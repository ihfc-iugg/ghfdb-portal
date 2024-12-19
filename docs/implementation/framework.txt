<!-- > {sub-ref}`wordcount-words` words | {sub-ref}`wordcount-minutes` min read -->
# Framework

## Geoluminate
```{figure} /_static/geoluminate.svg
:align: center
:target: https://www.geoluminate.io
:width: 100%
```

The web portal for the Global Heat Flow Database is constructed using [Geoluminate](https://docs.geoluminate.net/), an opionated web framework that aims to simplify the creation, deployment and upkeep of research data repositories. Geoluminate itself is built on top of the [Django Web Framework](https://www.djangoproject.com/), a high-level Python-based framework that encourages rapid development and clean, pragmatic design. Geoluminate enhances Django by providing a set of core data models, tools and conventions that are tailored to the specific needs of research communities like the Internation Heat Flow Commission. In utilizing Geoluminate, the Global Heat Flow Database benefits from a consistent user experience and data model that promotes integration with exisiting research initiatives (DOI, DataCite, ROR, ORCID) and therefore maximizes findability, accessibility, interoperability, and reusability under the FAIR data principles. 

The codebase defining the Global Heat Flow Database web portal is publicly available at [github.com/ihfc-iugg/ghfdb-portal/](https://github.com/ihfc-iugg/ghfdb-portal/). Within this codebase are the two data models described by the international heat flow community as the basis for collecting high-quality heat flow data and metadata. These two data models integrate directly with the [core data model](https://docs.geoluminate.net/contributing/core_data_model.html#core-data-model) of the Geoluminate framework, which is then capable of presenting and distributing the data in the context of a modern, user-friendly web interface.   

Also included in the codebase are the necessary tools, scripts and configuration files for deploying the web portal to local or remote infrastructures in a consistent and reproducible manner. The configuration files are designed to work with [Docker](https://www.docker.com/) and [Kubernetes](https://kubernetes.io/), two popular containerization technologies that are widely used in development communities for deploying web applications. By using these technologies, individual instances of the Global Heat Flow Database portal can be deployed on a wide range of infrastructures, from personal computers to self-hosted servers (e.g. on private networks) to cloud-based services like [Google Cloud](https://cloud.google.com/) and [Amazon Web Services](https://aws.amazon.com/). This ensures that the data and metadata standards defined as part of the World Heat Flow Database Project may be utilized by members of the international heat flow community, regardless of legal or technical constraints that prevent direct contributions to an international database.
   
The configuration files define several services that make up the backend architecture and are critical to the deployment and functionality of the web portal. These services include:

- The web application (as described above)
- PostgreSQL - a modern relational database for data storage. Also included by default is the [PostGIS](https://postgis.net/) extension for collecting spatial data
- Redis - an in-memory data structure store used as a cache and message broker for asynchronous background tasks
- Celery - a distributed task queue used to execute background tasks asynchronously (e.g. sending emails, processing uploaded files, etc.)
- MinIO - an object storage server that is compatible with Amazon S3 and is used to store user-uploaded files (e.g. images, documents, etc.)
- Traefik - a modern reverse proxy and load balancer that routes incoming requests to the appropriate service

Configuration files for several computing environments are included in the codebase, including development, staging, and production environments. Each configuration file defines the necessary volumes, and network settings that are required for the services to communicate with each other and with the outside world. The configuration files are designed to be easily modified and extended to suit the needs of individual instances of the web portal. An example stack.env file is also included that defines environment variables that can be modified to configure individual instances of the protal. These environment variables include sensitive information such as database passwords, API keys, and other secrets that should not be stored in the configuration files themselves.






The configuration file also defines the necessary environment variables, volumes, and network settings that are required for the services to communicate with each other and with the outside world.

These configuration files are based on Docker and are used by GFZ Potsdam to host and deploy the Global Heat Flow Database web portal on a single-server setup using [Portainer CE](https://www.portainer.io), a lightweight, browser-based, container management tool. These same configuration files may also be used by third-parties to deploy the web portal on personal computers, internal network servers, or cloud-based services like Google Cloud and Amazon Web Services. 

The production-ready configuration file defines several services that are critical to the deployment of the web portal, including the web server, the database server, the reverse proxy server, and the container management tool. The configuration file also defines the necessary environment variables, volumes, and network settings that are required for the services to communicate with each other and with the outside world.



```{seealso}


This includes the necessary configuration files for deploying the web portal using [Docker](https://www.docker.com/) and [Kubernetes](https://kubernetes.io/), as well as the necessary scripts for automating the deployment process.



```{seealso}

repository defines two data models (heat flow parent and heat flow child) specific to the collection of high-quality heat flow data, as defined by the internation heat flow community.

## Why Geoluminate?

Alternative frameworks aimed at the research community require us to map fields onto an existing data model or store domain relevant data as plain text/json objects in the database. This approach is not ideal for a number of reasons:

- It requires us to maintain a separate data model in addition to the database schema, which is not only redundant but also increases the risk of data inconsistencies.
- It makes it difficult to query the database using SQL, which is the standard language for relational databases.
- It makes it difficult to integrate with other applications that use a relational database.

Geoluminate solves these problems by allowing us to define our data model in such a way that the database schema itself is altered. In doing so, the fields in our data model always exist in the database schema and we therefore retain all the benefits of a modern relational database including data integrity, data validation, and table indexing.

```{seealso}
For more information on Geoluminate, please visit [geoluminate.io](www.geoluminate.io) or view the [online documentation](https://geoluminate.github.io/geoluminate/).
```
