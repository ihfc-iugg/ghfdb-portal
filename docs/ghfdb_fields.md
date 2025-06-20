# GHFDB Field Mapping

This page documents how each field of the community-defined **Global Heat Flow Database structure** relates to tables in the underlying **relational database** and their corresponding **Django models**.

The GHFDB spreadsheet is designed for human readability and ease of data entry, using a single table to represent a variety of concepts—ranging from site-level metadata to specific measurement records. This leads to an incorrect conclusion that all data belongs to a single logical structure within the database. In reality, however, these fields originate from different database tables and models, linked through foreign keys and object relationships defined in Django.

Below is a mapping table that clarifies how each field in the GHFDB spreadsheet corresponds to the actual database tables and Django models used in the FairDM framework. Use this table if you wish to understand how to access specific data using the Django ORM or if you simply wish to understand the underlying structure of the GHFDB data as it is stored in the database.

## Column Descriptions

| Column Name | Description |
| --- | --- |
| **GHFDB Name** | The original field name as it appears in the GHFDB spreadsheet (e.g., `q`, `lat_NS`, `elevation`). |
| **Database Table** | The name of the actual database table where the data is stored (e.g., `heat_flow_surfaceheatflow`). This reflects the low-level storage destination. |
| **Accessed From** | The Django model used to access the value (e.g., `SurfaceHeatFlow`, `HeatFlowSite`). This is typically the model from which a queryset would be created. |
| **Accessor** | The Django field name or property used to retrieve the value from the model listed in "Accessed From" (e.g., `value`, `x`, `name`). This can be a direct model field or a related field through a foreign key. |
| **Declared By** | The model where the field is originally declared. This is important when `Accessed From` accesses the field via a related object or mixin (e.g., `fairdm.location.Point`, `fairdm.core.Sample`). |

## Mapping Table

| GHFDB Name | Database Table | Accessed From | Accessor | Declared By |
| --- | --- | --- | --- | --- |
| q | heat\_flow\_surfaceheatflow | SurfaceHeatFlow | value | SurfaceHeatFlow |
| q\_uncertainty | heat\_flow\_surfaceheatflow | SurfaceHeatFlow | uncertainty | SurfaceHeatFlow |
| name | fairdm\_sample | HeatFlowSite | name | fairdm.core.Sample |
| lat\_NS | fairdm\_point | HeatFlowSite | y | fairdm.location.Point |
| long\_EW | fairdm\_point | HeatFlowSite | x | fairdm.location.Point |
| elevation | heat\_flow\_heatflowsite | HeatFlowSite | elevation | fairdm\_geo.SampleLocation |
| environment | heat\_flow\_heatflowsite | HeatFlowSite | environment | fairdm\_geo.SampleLocation |
| p\_comment | heat\_flow\_surfaceheatflow | SurfaceHeatFlow | p\_comment | SurfaceHeatFlow |
| corr\_HP\_flag | heat\_flow\_surfaceheatflow | SurfaceHeatFlow | corr\_HP\_flag | SurfaceHeatFlow |
| total\_depth\_MD | heat\_flow\_heatflowsite | HeatFlowSite | length | fairdm\_geo.SampleLocation |
| total\_depth\_TVD | heat\_flow\_heatflowsite | HeatFlowSite | vertical\_depth | fairdm\_geo.VerticalDepthInterval |
| explo\_method | heat\_flow\_heatflowsite | HeatFlowSite | explo\_method | HeatFlowSite |
| explo\_purpose | heat\_flow\_heatflowsite | HeatFlowSite | explo\_purpose | HeatFlowSite |
| qc | heat\_flow\_heatflow | HeatFlow | value |  |
| qc\_uncertainty | heat\_flow\_heatflow | HeatFlow | uncertainty |  |
| q\_method | heat\_flow\_heatflow | HeatFlow | method |  |
| q\_top | heat\_flow\_heatflow\_interval | HeatFlowInterval | top |  |
| q\_bottom | heat\_flow\_heatflow\_interval | HeatFlowInterval | bottom |  |
| probe\_penetration | heat\_flow\_heatflow | HeatFlow | probe\_penetration |  |
| publication\_reference | fairdm\_dataset | Dataset | related\_literature |  |
| data\_reference | fairdm\_dataset | Dataset | reference |  |
| relevant\_child | heat\_flow\_heatflow | HeatFlow | relevant\_child |  |
| c\_comment | heat\_flow\_heatflow | HeatFlow | c\_comment |  |
| corr\_IS\_flag | heat\_flow\_heatflow | HeatFlow | corr\_IS\_flag |  |
| corr\_T\_flag | heat\_flow\_heatflow | HeatFlow | corr\_T\_flag |  |
| corr\_S\_flag | heat\_flow\_heatflow | HeatFlow | corr\_S\_flag |  |
| corr\_E\_flag | heat\_flow\_heatflow | HeatFlow | corr\_E\_flag |  |
| corr\_TOPO\_flag | heat\_flow\_heatflow | HeatFlow | corr\_TOPO\_flag |  |
| corr\_PAL\_flag | heat\_flow\_heatflow | HeatFlow | corr\_PAL\_flag |  |
| corr\_SUR\_flag | heat\_flow\_heatflow | HeatFlow | corr\_SUR\_flag |  |
| corr\_CONV\_flag | heat\_flow\_heatflow | HeatFlow | corr\_CONV\_flag |  |
| corr\_HR\_flag | heat\_flow\_heatflow | HeatFlow | corr\_HR\_flag |  |
| expedition | heat\_flow\_heatflow | HeatFlow | expedition |  |
| probe\_type | heat\_flow\_heatflow | HeatFlow | probe\_type |  |
| probe\_length | heat\_flow\_heatflow | HeatFlow | probe\_length |  |
| probe\_tilt | heat\_flow\_heatflow | HeatFlow | probe\_tilt |  |
| water\_temperature | heat\_flow\_heatflow | HeatFlow | water\_temperature |  |
| geo\_lithology | heat\_flow\_heatflow\_interval | HeatFlowInterval | lithology |  |
| geo\_stratigraphy | heat\_flow\_heatflow\_interval | HeatFlowInterval | age |  |
| T\_grad\_mean | heat\_flow\_thermalgradient | ThermalGradient | value |  |
| T\_grad\_uncertainty | heat\_flow\_thermalgradient | ThermalGradient | uncertainty |  |
| T\_grad\_mean\_cor | heat\_flow\_thermalgradient | ThermalGradient | corrected\_value |  |
| T\_grad\_uncertainty\_cor | heat\_flow\_thermalgradient | ThermalGradient | corrected\_uncertainty |  |
| T\_method\_top | heat\_flow\_thermalgradient | ThermalGradient | method\_top |  |
| T\_method\_bottom | heat\_flow\_thermalgradient | ThermalGradient | method\_bottom |  |
| T\_shutin\_top | heat\_flow\_thermalgradient | ThermalGradient | shutin\_top |  |
| T\_shutin\_bottom | heat\_flow\_thermalgradient | ThermalGradient | shutin\_bottom |  |
| T\_corr\_top | heat\_flow\_thermalgradient | ThermalGradient | correction\_top |  |
| T\_corr\_bottom | heat\_flow\_thermalgradient | ThermalGradient | correction\_bottom |  |
| T\_number | heat\_flow\_thermalgradient | ThermalGradient | number |  |
| q\_date | heat\_flow\_heatflow | HeatFlow | date\_acquired |  |
| tc\_mean | heat\_flow\_intervalconductivity | IntervalConductivity | value |  |
| tc\_uncertainty | heat\_flow\_intervalconductivity | IntervalConductivity | uncertainty |  |
| tc\_source | heat\_flow\_intervalconductivity | IntervalConductivity | source |  |
| tc\_location | heat\_flow\_intervalconductivity | IntervalConductivity | location |  |
| tc\_method | heat\_flow\_intervalconductivity | IntervalConductivity | method |  |
| tc\_saturation | heat\_flow\_intervalconductivity | IntervalConductivity | saturation |  |
| tc\_pT\_conditions | heat\_flow\_intervalconductivity | IntervalConductivity | pT\_conditions |  |
| tc\_pT\_fuction | heat\_flow\_intervalconductivity | IntervalConductivity | pT\_function |  |
| tc\_number | heat\_flow\_intervalconductivity | IntervalConductivity | strategy |  |
| tc\_strategy | heat\_flow\_intervalconductivity | IntervalConductivity | number |  |
| Ref\_ISGN | heat\_flow\_heatflow | HeatFlow | IGSN |  |
| Reviewer\_name | heat\_flow\_review | Review | name |  |
| Reviewer\_comment | heat\_flow\_review | Review | comment |  |
| Review\_date | heat\_flow\_review | Review | completion\_date |  |
| Country | heat\_flow\_heatflowsite | HeatFlowSite | country |  |
| Region | heat\_flow\_heatflowsite | HeatFlowSite | region |  |
| Continent | heat\_flow\_heatflowsite | HeatFlowSite | continent |  |
| Domain | heat\_flow\_heatflowsite | HeatFlowSite | domain |  |