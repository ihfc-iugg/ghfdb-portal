# Map Exploration

Heatflow.world provides a custom map interface for interacting with the Global Heat Flow Database. The map is built using [VueJS](https://vuejs.org/) as JavaScirpt Framework, [MapLibre](https://maplibre.org/) for Mapping and the [The Global Heat Flow Database](https://dataservices.gfz-potsdam.de/panmetaworks/showshort.php?id=e6755429-fbbf-11ee-967a-4ffbfe06208e) as data source.

The main purpose of the map interface is to provide users the possibility to get a first overview of the global heat flow database. This contains functionalities like information about heat flow value, custom visualization styles, filter according to properties and location, basic statistics and some heat flow specific analysis within a few clicks. Each of these functionalities is explained in more detail.

The landing page consists of the three main components like shown in the image below:

- Map + Data (Global Heat Flow Database)
- Map Controller for general interaction with map + data
- Bar to navigate to the functionalities

![Landing-Page](../../docs/_static/_mapping/mapping-landing-page.PNG)

## How to

```{toctree}
:maxdepth: 1

mapController

settings

filtering

statistics

analysis
```