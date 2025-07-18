# Using the Map

Heatflow.world provides a custom map interface for interacting with the Global Heat Flow Database. The map is built using [VueJS](https://vuejs.org/) as JavaScirpt Framework, [MapLibre](https://maplibre.org/) for Mapping and the [The Global Heat Flow Database](https://dataservices.gfz-potsdam.de/panmetaworks/showshort.php?id=e6755429-fbbf-11ee-967a-4ffbfe06208e) as data source.

The main purpose of the map interface is to provide users the possibility to get a first overview of the global heat flow database. This contains functionalities like information about heat flow values, custom visualization styles, filter according to properties and location, basic statistics and some heat flow specific analysis. Each of these functionalities is explained in more detail.

## Data

When you open the Map Viewer, the GHFDB is loaded as CSV to your local computer. As next step the CSV gets parsed and converted into [GeoJSON format](https://geojson.org/) so it can be used as data source for MapLibre. To reduce the size of the file, only parent attributes and some general information are kept. Which attributes are availaible is shown in the following table. The information are gathered from Fuchs et al. (2021) [DOI](https://doi.org/10.31214/ijthfa.v4i1.62) and the latest ghfdb [data description](https://dataservices.gfz-potsdam.de/panmetaworks/showshort.php?id=e6755429-fbbf-11ee-967a-4ffbfe06208e).

| Property        | Type    | Unit    | Range/Values                                                                                  |
| --------------- | ------- | ------- | --------------------------------------------------------------------------------------------- |
| q               | Number  | mW/m^2  | -999,999.9 –999,999.9                                                                         |
| q_uncertainty   | Number  | mW/m^2  | 0-999,999.9                                                                                   |
| name            | String  | -       | -                                                                                             |
| lat_NS          | Number  | degrees | -90 to +90                                                                                    |
| long_EW         | Number  | degrees | -180 to +180                                                                                  |
| elevation       | Number  | m       | -12,000 to +9,000                                                                             |
| environment     | String  | -       | Onshore (continental), Onshore (lake), Offshore (continental), Offshore (marine), unspecified |
| corr_HP_flag    | Boolean | -       | Yes, No,Unspecified                                                                           |
| total_depth_MD  | Number  | m       | -                                                                                             |
| total_depth_TVD | Number  | m       | -                                                                                             |
| explo_method    | String  | -       | drilling, mining, tunneling, probing (lake), probing (ocean), unspecified                     |
| explo_purpose   | String  | -       | hydrocarbon, underground storage, geothermal, mapping, mining, tunneling, unspecified         |
| p_comment       | String  | -       | -                                                                                             |
| ID              | String  | -       | -                                                                                             |
| ID_parent       | String  | -       | -                                                                                             |
| Quality_Code    | String  | -       | Fuchs et al. (2023) [DOI](https://doi.org/10.1016/j.tecto.2023.229976)                        |

## How to

```{toctree}
:maxdepth: 1

user_interface
navigationBar
settingsPanel
filterPanel
statisticsPanel
analysisPanel
```