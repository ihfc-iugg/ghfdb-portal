# World Heat Flow Database Project

```{raw} html
<style>

article {
    padding-top: 0;
}

article h1:first-of-type {
    display: none;
}
</style>
```

![World Heat Flow Database Project](_static/brand/logo.png)
<!-- [![Deutsche Forschungsgemeinschaft](./assets/img/brand/dfg_logo.gif)](https://www.dfg.de) -->

The World Heat Flow Database Project is a joint initiative by [Helmholtz Centre Potsdam - GFZ German Research Centre for Geosciences](https://www.gfz-potsdam.de/en/) and the [Technical University of Dresden](https://tu-dresden.de). Phase one of the project (2022-2025) is funded by the [Deutsche Forschungsgemeinschaft](https://www.dfg.de/en/index.jsp) (DFG, German Research Foundation) and involves the development of new research data infrastructure for the [International Heat Flow Commission'](http://ihfc-iugg.org)s (IHFC) Global Heat Flow Database.


[![GFZ Potsdam](_static/brand/GFZ_logo.png){.w-25}](https://www.gfz-potsdam.de)
[![TU Dresden](_static/brand/TU_Dresden.svg){.w-25}](https://tu-dresden.de/)
[![DFG](_static/brand/dfg_logo.gif){.w-25}](https://tu-dresden.de/)

```{seealso}
For more information regarding the project, please visit the [official project website](http://heatflow.world).
```

### Technical Revision

In 2020, the International Heat Flow Commission (IHFC) embarked on a comprehensive overhaul of the Global Heat Flow Database (GHFDB). This undertaking represented a multinational, collaborative initiative geared towards addressing both present and future requirements of the database. The primary objectives centered on the establishment of an authenticated database containing information regarding heat-flow data type and quality. Additionally, the aim was to align the database with the standards of modern research data infrastructure, encompassing extensive metadata descriptions and interoperability with existing infrastructure.

To realize these objectives, ad-hoc working groups were established to restructure and augment the preexisting database framework initially introduced in Jessop et al. (1976). These working groups comprised subject matter experts in terrestrial and marine heat flow from across the globe, concentrating their efforts on four pivotal parameters influencing heat-flow computations and interpretations: methods for heat-flow determination, metadata and flags, temperature measurements, and properties of thermal rock. Throughout this collaborative endeavor, intermediate results were openly shared and deliberated among all participants in the working groups. This fostered a shared comprehension of the database entries and encouraged discourse on the required information for evaluating the quality and uncertainty of heat-flow data.

The end result of this collaborative effort was an updated GHFDB structure, to be used for all future submissions as well as the reevaluation of preexisting data.

```{seealso}
2021, [A new database structure for the IHFC Global Heat Flow Database](https://doi.org/10.31214/ijthfa.v4i1.62): the intial revised data structure of the GHFDB.

2023, [Quality-assurance of heat-flow data: The new structure and evaluation scheme of the IHFC Global Heat Flow Database](https://doi.org/10.1016/j.tecto.2023.229976): updated data structure and evaluation scheme of the GHFDB.
```

### Modernised Infrastructure

The recent revisions of the GHFDB schema is accompanied by efforts to modernise the technical infrastructure hosting the GHFDB. This includes adaptation to a modern relational database and the development of a new web application for online, collaborative management of the database. This documentation describes the implementation, usage and development of the new web application which is built using the [Geoluminate Research Database Framework](https://geoluminate.github.io/geoluminate/).