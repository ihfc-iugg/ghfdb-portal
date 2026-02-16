# GHFDB Field Reference Guide

## Document Overview

This document provides a comprehensive reference for all data fields in the International Heat Flow Commission (IHFC) Global Heat Flow Database (GHFDB). It combines the conceptual metadata structure with detailed field descriptions, data types, and expected values to serve as the authoritative guide for database contributors and users.

The GHFDB incorporates persistent identifiers (DOI, ORCID, IGSN, ROR) to ensure FAIR (Findable, Accessible, Interoperable, Reusable) data principles and supports long-term citability, traceability, and data integration.

## Metadata Structure: Parent-Child Relationship

The GHFDB employs a **two-level hierarchical structure** to organize heat flow data:

### Parent Level

Represents a **heat flow site or location** with terrestrial surface heat flow values. Parent entries contain geographical metadata, site characteristics, and representative heat flow values for the entire location. Each parent entry may have zero or more associated child entries.

### Child Level

Represents **depth-specific heat flow determinations** at a particular site. Child entries contain interval-specific measurements, methodological details, and quality indicators for heat flow values at defined depth ranges within a parent location. Child entries are linked to their parent through relational database keys.

### Data Domains

- **B** = Borehole/Mine data (drilling and mining access methods)
- **S** = Shallow probe-sensing data (marine and lake probe measurements)

### Field Obligations

- **M** = Mandatory (required for database entry)
- **R** = Recommended (strongly encouraged for quality assessment)
- **O** = Optional (supplementary information)

### Quality Evaluation

Fields contribute to quality scoring systems:

- **U-score** = Uncertainty score assessment
- **M-score** = Method quality score assessment
- **P-flag** = Perturbation effects flags

---

## Parent Level Metadata Elements

Parent level entries establish the geographical and contextual framework for heat flow determinations at a specific site.

### P01: Heat Flow Value (q)

**Short name**: q
**Category**: Heat Flow
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: U-score (B,S)

Terrestrial surface heat-flow value after all corrections for instrumental and environmental effects. Represents the representative heat flow for the entire location.

- **Unit**: mW/m²
- **Type**: double(7)
- **Range**: -999,999.9 to 999,999.9
- **Description**: This is the final, corrected heat flow value that represents the site. All environmental and instrumental corrections should be applied. Negative values may occur in special geological circumstances (e.g., convective downflow zones).

### P02: Heat Flow Uncertainty

**Short name**: q_unc
**Category**: Heat Flow
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: U-score (B,S)

Uncertainty standard deviation of the reported heat-flow value as estimated by error propagation from uncertainty in thermal conductivity and temperature gradient (corrected preferred over measured gradient).

- **Unit**: mW/m²
- **Type**: double(7)
- **Range**: 0 to 999,999.9
- **Description**: Represents one-sigma standard deviation. Should incorporate all sources of uncertainty including measurement errors, correction uncertainties, and spatial/temporal variability.

### P03: Site Name

**Short name**: name
**Category**: Metadata
**Domain**: B, S
**Obligation**: Mandatory

Specification of the (local) name of the related heat-flow site or the related survey. Should be consistent with the publication.

- **Unit**: —
- **Type**: Text(255)
- **Range**: —
- **Description**: Use the name as published in primary literature. May include well names, survey identifiers, or geographical features. Consistency with published names aids traceability.

### P04: Latitude (Geographical)

**Short name**: lat
**Category**: Geographical
**Domain**: B, S
**Obligation**: Mandatory

Latitude is a geographic coordinate that specifies the north–south position of a point on the Earth's surface. The Equator has a latitude of 0°, the North Pole has a latitude of +90°, and the South Pole has a latitude of -90°.

- **Unit**: degrees
- **Type**: DECIMAL(7), 2 digits, 5 decimal places (ISO 6709)
- **Range**: -90.00000 to +90.00000
- **Description**: Use decimal format rather than degrees/minutes/seconds. Negative values indicate southern hemisphere. Precision to 5 decimal places provides ~1.1 meter accuracy.

### P05: Longitude (Geographical)

**Short name**: lng
**Category**: Geographical
**Domain**: B, S
**Obligation**: Mandatory

Longitude is a geographic coordinate that specifies the east–west position of a point on the Earth's surface. The Prime Meridian (Greenwich) is defined as 0° longitude. Positive longitudes are east, negative are west.

- **Unit**: degrees
- **Type**: DECIMAL(8), 3 digits, 5 decimal places (ISO 6709)
- **Range**: -180.00000 to +180.00000
- **Description**: Use decimal format. Negative values indicate western hemisphere. Precision to 5 decimal places provides ~1.1 meter accuracy at the equator.

### P06: Elevation (Geographical)

**Short name**: elevation
**Category**: Geographical
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: M-score (S)

The elevation of a geographic location is its height above or below mean sea level. Caution: different national reference systems are used. The reference level may be diverse depending on the study (drilling, lake, marine).

- **Unit**: m
- **Type**: FLOAT 32
- **Range**: -12,000 to +9,000
- **Description**: Positive values indicate elevation above sea level, negative values indicate depth below sea level. For marine sites, this typically represents seafloor depth. Reference datum should be noted in comments if non-standard.

### P07: Basic Geographical Environment

**Short name**: env
**Category**: Metadata
**Domain**: B, S
**Obligation**: Mandatory

Describes the general geographical setting of the heat-flow site (not the applied methodology).

- **Unit**: —
- **Type**: Text(255)
- **Range**: Choice box
- **Allowed Values**:
  - Onshore (continental)
  - Onshore (lake)
  - Offshore (continental)
  - Offshore (marine)
  - Unspecified
- **Description**: Distinguishes between continental and marine environments, and whether measurements are onshore or offshore. Important for understanding environmental corrections and perturbation effects.

### P08: General Comments (Parent Level)

**Short name**: q_comment
**Category**: Metadata
**Domain**: B, S
**Obligation**: Recommended

Text field for any further comments to the reported heat-flow determination.

- **Unit**: —
- **Type**: Text(255)
- **Range**: —
- **Description**: Use this field to provide contextual information not captured elsewhere, such as site-specific conditions, anomalies, or clarifications about data processing.

### P09: Flag Heat Production of the Overburden

**Short name**: corr_HP_flag
**Category**: Data Flag
**Domain**: B, S
**Obligation**: Recommended

Specifies if corrections to the calculated heat flow consider the contribution of the heat production of the overburden to the terrestrial surface heat flow q.

- **Unit**: —
- **Type**: BIT field
- **Range**: [Yes] / [No] / [Unspecified]
- **Description**: Radiogenic heat production in near-surface rocks can significantly affect surface heat flow. This flag indicates whether such corrections have been applied.

### P10: Total Measured Depth

**Short name**: —
**Category**: Borehole Metadata
**Domain**: B
**Obligation**: Recommended

Total measured depth along the borehole trajectory.

- **Unit**: m
- **Type**: Double
- **Range**: —
- **Description**: This is the actual length drilled along the borehole path, which may differ from true vertical depth in deviated wells.

### P11: Total True Vertical Depth

**Short name**: —
**Category**: Borehole Metadata
**Domain**: B
**Obligation**: Recommended

True vertical depth of the borehole relative to surface.

- **Unit**: m
- **Type**: Double
- **Range**: —
- **Description**: Vertical depth corrected for borehole deviation. Critical for understanding depth-dependent effects.

### P12: Type of Exploration Method

**Short name**: method
**Category**: Metadata
**Domain**: B
**Obligation**: Mandatory

Specification of the general means by which the rock was accessed by temperature sensors for the respective data entry.

- **Unit**: —
- **Type**: Text(255)
- **Range**: Choice box
- **Allowed Values**:
  - Drilling
  - Mining
  - Tunneling
  - Probing (lake)
  - Probing (ocean)
  - Unspecified
- **Description**: Defines how subsurface access was achieved. Different methods have different perturbation characteristics.

### P13: Original Exploration Purpose

**Short name**: expl
**Category**: Metadata
**Domain**: B
**Obligation**: Recommended

Main purpose of the original excavation providing access for the temperature sensors.

- **Unit**: —
- **Type**: Text(255)
- **Range**: Choice box
- **Allowed Values**:
  - Hydrocarbon
  - Underground storage
  - Geothermal
  - Mapping
  - Mining
  - Tunneling
  - Unspecified
- **Description**: Original drilling/excavation purpose affects data quality. Purpose-drilled geothermal wells often have better thermal data than opportunistic measurements in hydrocarbon wells.

---

## Child Level Metadata Elements

Child level entries provide depth-specific heat flow determinations with detailed methodological information and quality indicators.

### Heat Flow Category

#### C01: Heat Flow Value (qc)

**Short name**: qc
**Category**: Heat Flow
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: U-score (B,S)

Any kind of heat-flow value for a specific depth interval. This is the child-level heat flow representing a particular depth range within the parent location.

- **Unit**: mW/m²
- **Type**: double(7)
- **Range**: -999,999.9 to 999,999.9
- **Description**: Represents heat flow for the specified interval. Multiple child entries at different depths can reveal depth-dependent trends. After all applicable corrections.

#### C02: Heat Flow Uncertainty (Child)

**Short name**: qc_unc
**Category**: Heat Flow
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: U-score (B,S)

Uncertainty standard deviation of the reported heat-flow value as estimated by an error propagation from uncertainty in thermal conductivity and temperature gradient.

- **Unit**: mW/m²
- **Type**: double(7)
- **Range**: 0 to 999,999.9
- **Description**: One-sigma standard deviation for this specific interval. Should reflect interval-specific uncertainties in temperature gradient and thermal conductivity measurements.

#### C03: Heat Flow Method

**Short name**: q_method
**Category**: Heat Flow
**Domain**: B, S
**Obligation**: Mandatory

Principal method of heat-flow density calculation from temperature and thermal conductivity data.

- **Unit**: —
- **Type**: Text(255)
- **Range**: From description
- **Allowed Values**:
  - **Fourier's Law / Product / Interval method**: Product of the mean thermal gradient to the mean thermal conductivity with reference to a specified depth interval
  - **Bullard method**: Heat-flow value given as the angular coefficient of the linear regression of the thermal resistance vs. temperature data (used when there is significant variation of thermal conductivity)
  - **Boot-strapping method**: Iterative procedure aimed at minimizing the difference between measured and modeled temperatures by solving the 1-D steady-state conductive geotherm (radiogenic heat production of rocks is accounted for)
  - **Other**: Specify method
- **Description**: Fundamental calculation approach. Different methods are appropriate for different thermal conductivity distributions and data types.

#### C04: Heat Flow Interval Top

**Short name**: q_top
**Category**: Heat Flow
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: M-score (B,S)

Describes the true vertical depth of the top end of the heat-flow determination interval relative to the land surface/ocean ground surface.

- **Unit**: m
- **Type**: Double(6)
- **Range**: —
- **Description**: Always measured as true vertical depth, not measured depth. Positive values indicate depth below surface. For marine measurements, reference is seafloor.

#### C05: Heat Flow Interval Bottom

**Short name**: q_bot
**Category**: Heat Flow
**Domain**: B
**Obligation**: Mandatory
**Quality**: M-score (B)

Describes the true vertical depth of the bottom end of the heat-flow determination interval relative to the land surface.

- **Unit**: m
- **Type**: Double(6)
- **Range**: —
- **Description**: True vertical depth of interval bottom. The difference between C04 and C05 defines the interval thickness. Larger intervals may average out local variations.

#### C06: Penetration Depth

**Short name**: hf_pen
**Category**: Heat Flow
**Domain**: S
**Obligation**: Mandatory
**Quality**: M-score (S)

Depth of penetration of marine probe into the sediment.

- **Unit**: m
- **Type**: Double(5), 3 digits, 2 decimal places
- **Range**: 0 to 999.99
- **Description**: Actual penetration achieved by the probe. Shallow penetration may result in measurements affected by bottom water temperature variations.

### Metadata and Flags Category

#### C07: Primary Publication Reference

**Short name**: Ref_1
**Category**: Metadata
**Domain**: B, S
**Obligation**: Mandatory

References related to the respective heat-flow entry.

- **Unit**: —
- **Type**: Text(255)
- **Range**: —
- **Format**: [First author_Year_Title_Journal/Publisher_DOI]
- **Description**: Primary source for the data. Essential for traceability and verification. Include DOI when available.

#### C08: Primary Data Reference

**Short name**: Ref_2
**Category**: Metadata
**Domain**: B, S
**Obligation**: Recommended

Additional references related to the respective heat-flow entry.

- **Unit**: —
- **Type**: Text(255)
- **Range**: —
- **Format**: [First author_Year_Title_Journal/Publisher_DOI]
- **Description**: Secondary sources, data repositories, or related publications. May include references to original data before reprocessing.

#### C09: Relevant Child

**Short name**: childcomp
**Category**: Metadata
**Domain**: B, S
**Obligation**: Mandatory

Specifies whether the child entry is used for computation of representative location heat-flow values at the parent level or not.

- **Unit**: —
- **Type**: BIT field
- **Range**: [Yes] / [No] / [Unspecified]
- **Description**: Some child entries may be excluded from parent value calculation due to quality issues or perturbations. This flag clarifies which children contribute to the parent value.

#### C10: General Comments (Child Level)

**Short name**: q_comment
**Category**: Metadata
**Domain**: B, S
**Obligation**: Recommended

Text field for any further comments to the reported heat-flow determination at the child level.

- **Unit**: —
- **Type**: Text(255)
- **Range**: —
- **Description**: Interval-specific comments, such as lithological changes, data quality issues, or methodological notes.

#### C11: Flag In-Situ Thermal Properties

**Short name**: corr_IS_flag
**Category**: Data Flag
**Domain**: B, S
**Obligation**: Recommended

Specifies whether the in-situ pressure and temperature conditions were considered for the reported thermal conductivity value or not.

- **Unit**: —
- **Type**: BIT field
- **Range**: [Yes] / [No] / [Unspecified]
- **Description**: Thermal conductivity varies with pressure and temperature. In-situ corrections improve accuracy, especially at great depths.

#### C12: Flag Temperature Corrections

**Short name**: corr_T_flag
**Category**: Data Flag
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: M-score (S)

Specifies if corrections to the measured temperature data were performed.

- **Unit**: —
- **Type**: BIT field
- **Range**: [Yes] / [No] / [Unspecified]
- **Description**: Instrumental corrections for drilling disturbance (boreholes) or probe effects (sensing). Critical for data quality assessment.

#### C13: Flag Sedimentation Effect

**Short name**: corr_S_flag
**Category**: Data Flag
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: P-flag

Specifies if corrections with respect to sedimentation/subsidence effects were performed to the reported heat-flow value.

- **Unit**: —
- **Type**: BIT field
- **Range**: [Yes] / [No] / [Unspecified]
- **Description**: Rapid sedimentation causes transient thermal perturbations that depress heat flow. Correction methods account for burial history.

#### C14: Flag Erosion Effect

**Short name**: corr_E_flag
**Category**: Data Flag
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: P-flag

Specifies if corrections with respect to erosion effects were applied to the reported heat-flow value.

- **Unit**: —
- **Type**: BIT field
- **Range**: [Yes] / [No] / [Unspecified]
- **Description**: Erosion removes overburden and creates thermal transients that elevate observed heat flow. Corrections require erosion rate estimates.

#### C15: Flag Topographic Effect

**Short name**: corr_TOPO_flag
**Category**: Data Flag
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: P-flag

Specifies if corrections with respect to topographic effects were applied to the reported heat-flow value.

- **Unit**: —
- **Type**: BIT field
- **Range**: [Yes] / [No] / [Unspecified]
- **Description**: Topographic relief focuses or defocuses heat flow. Significant in mountainous terrain. Corrections use digital elevation models.

#### C16: Flag Paleoclimatic Effect

**Short name**: corr_PAL_flag
**Category**: Data Flag
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: P-flag

Specifies if corrections with respect to climatic conditions (glaciation, post-industrial warming, etc.) were applied to the reported heat-flow value.

- **Unit**: —
- **Type**: BIT field
- **Range**: [Yes] / [No] / [Unspecified]
- **Description**: Past climate changes create thermal transients that penetrate to depth. Particularly important in formerly glaciated regions and areas with recent rapid warming.

#### C17: Flag Surface Temperature/Bottom Water

**Short name**: corr_BWT_flag
**Category**: Data Flag
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: P-flag

Specifies if corrections with respect to transient bottom-water temperature effects were applied to the reported heat-flow value.

- **Unit**: —
- **Type**: BIT field
- **Range**: [Yes] / [No] / [Unspecified]
- **Description**: Relevant for marine and lake measurements where bottom water temperature varies seasonally or has long-term trends.

#### C18: Flag Convection Processes

**Short name**: corr_CONV_flag
**Category**: Data Flag
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: P-flag

Specifies if corrections with respect to convection effects were applied to the reported heat-flow value, e.g., due to numerical modeling.

- **Unit**: —
- **Type**: BIT field
- **Range**: [Yes] / [No] / [Unspecified]
- **Description**: Groundwater flow or hydrothermal convection can significantly perturb heat flow. Corrections may involve numerical modeling.

#### C19: Flag Heat Refraction Effect

**Short name**: corr_HR_flag
**Category**: Data Flag
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: P-flag

Specifies if corrections with respect to refraction effects, e.g., due to significant local conductivity contrasts, were applied to the reported heat-flow value.

- **Unit**: —
- **Type**: BIT field
- **Range**: [Yes] / [No] / [Unspecified]
- **Description**: Lateral thermal conductivity contrasts (e.g., salt domes, basement topography) refract heat flow. Corrections use 2D/3D modeling.

#### C20: Expeditions/Platforms/Ship

**Short name**: —
**Category**: Metadata
**Domain**: B, S
**Obligation**: Recommended

Identification of research vessel, platform, or expedition for marine/lake measurements.

- **Unit**: —
- **Type**: Text(255)
- **Range**: —
- **Description**: Particularly relevant for ocean drilling programs (ODP, IODP) and marine geophysical surveys. Aids in linking to other datasets from the same expedition.

#### C21: Probe Type

**Short name**: hf_probe
**Category**: Metadata
**Domain**: S
**Obligation**: Recommended

Type of heat-flow probe used for measurement.

- **Unit**: —
- **Type**: Text(255)
- **Range**: From description
- **Allowed Values**:
  - Corer-outrigger
  - Bullard probe
  - Lister Violin-Bow probe
  - Ewing probe
  - Other probe
  - Unspecified
- **Description**: Different probe designs have different measurement characteristics and accuracy. Historical context for data quality assessment.

#### C22: Probe Length

**Short name**: hf_probeL
**Category**: Metadata
**Domain**: S
**Obligation**: Recommended

Length of heat-flow probe.

- **Unit**: m
- **Type**: Double(5), 3 digits, 2 decimal places
- **Range**: 0 to 999.99
- **Description**: Longer probes penetrate deeper and are less affected by bottom water temperature variations.

#### C23: Probe Tilt

**Short name**: T_tilt
**Category**: Metadata
**Domain**: S
**Obligation**: Mandatory
**Quality**: M-score (S)

Tilt of the marine heat-flow probe.

- **Unit**: degrees
- **Type**: Integer(2)
- **Range**: 0 to 99
- **Description**: Excessive tilt indicates measurement problems. Typically measurements with tilt >10° are rejected. Affects thermal gradient measurements.

#### C24: Bottom-Water Temperature

**Short name**: wat_temp
**Category**: Metadata
**Domain**: S
**Obligation**: Optional

Seafloor temperature where heat-flow measurements were taken, e.g., PT 100 or Mudline temperature for ODP data.

- **Unit**: °C
- **Type**: Double(5), 3 digits, 2 decimal places
- **Range**: 0 to 999.99
- **Description**: Reference temperature at seafloor/lake bottom. Used to calculate thermal gradients within sediment.

#### C25: Lithology

**Short name**: geo_lith
**Category**: Metadata
**Domain**: B, S
**Obligation**: Optional

Dominant rock type/lithology within the interval of heat-flow determination. Use existing BGS rock classification scheme for naming the lithology. Multiple entries for intervals of mixed lithology are semicolon-separated.

- **Unit**: —
- **Type**: Text(255)
- **Range**: Multiple choice box
- **Description**: Lithology affects thermal properties and interpretation. Use standardized terminology (e.g., BGS Rock Classification Scheme) for consistency.

#### C26: Stratigraphic Age

**Short name**: geo_strat
**Category**: Metadata
**Domain**: B, S
**Obligation**: Optional

Stratigraphic age of the depth range involved in the reported heat-flow determination. Multiple age entries are semicolon-separated.

- **Unit**: —
- **Type**: Text(255)
- **Range**: Multiple choice box
- **Allowed Values**: (Following International Commission on Stratigraphy)
  - Cenozoic
  - Mesozoic (Cretaceous, Jurassic, Triassic)
  - Paleozoic (Permian, Carboniferous, Devonian, Silurian, Ordovician, Cambrian)
  - Proterozoic (Neo-, Meso-, Paleo-)
  - Archean
  - Unspecified
- **Description**: Geological age provides context for thermal history and lithological expectations. Use standard ICS terminology.

### Gradient Category

#### C27: Temperature Gradient (Measured)

**Short name**: T_grad_mean_meas
**Category**: Temperature Gradient
**Domain**: B, S
**Obligation**: Mandatory

Mean temperature gradient measured for the heat-flow determination interval.

- **Unit**: K/km
- **Type**: Double(8), 5 digits, 2 decimal places
- **Range**: -99,999.99 to 99,999.99, N/A
- **Description**: Raw measured gradient before corrections. Calculated from temperature difference over interval depth. May include drilling disturbance effects.

#### C28: Temperature Gradient Uncertainty

**Short name**: T_grad_unc_meas
**Category**: Temperature Gradient
**Domain**: B, S
**Obligation**: Recommended

Uncertainty standard deviation of mean measured temperature gradient as estimated by error propagation from the uncertainty in the top and bottom temperature determinations.

- **Unit**: K/km
- **Type**: Double(8), 5 digits, 2 decimal places
- **Range**: -99,999.99 to 99,999.99, N/A
- **Description**: Propagated uncertainty from individual temperature measurement uncertainties. Critical for heat flow uncertainty calculation.

#### C29: Mean Temperature Gradient Corrected

**Short name**: T_grad_mean_cor
**Category**: Temperature Gradient
**Domain**: B, S
**Obligation**: Optional

Mean temperature gradient corrected for borehole (drilling/mud circulation) and environmental effects (terrain effects/topography, sedimentation, erosion, magmatic intrusions, paleoclimate, etc.). Name the correction method in the corresponding item.

- **Unit**: K/km
- **Type**: Double(8), 5 digits, 2 decimal places
- **Range**: -99,999.99 to 99,999.99, N/A
- **Description**: Gradient after all applicable corrections. This value should better represent equilibrium conditions. Correction methods should be documented.

#### C30: Corrected Temperature Gradient Uncertainty

**Short name**: T_grad_unc_cor
**Category**: Temperature Gradient
**Domain**: B, S
**Obligation**: Optional

Uncertainty standard deviation of mean corrected temperature gradient as estimated by error propagation from the uncertainty of the measured gradient and the applied correction approaches.

- **Unit**: K/km
- **Type**: Double(8), 5 digits, 2 decimal places
- **Range**: -99,999.99 to 99,999.99, N/A
- **Description**: Includes both measurement and correction uncertainties. Typically larger than measured gradient uncertainty due to correction model uncertainties.

#### C31: Temperature Method (Top)

**Short name**: T_method_top
**Category**: Temperature Gradient
**Domain**: B
**Obligation**: Mandatory
**Quality**: M-score (B)

Method used for temperature determination at the top of the heat-flow determination interval.

- **Unit**: —
- **Type**: Text(255)
- **Range**: From description
- **Allowed Values**:
  - **BHT**: Bottom hole temperature (uncorrected)
  - **CBHT**: Corrected bottom hole temperature
  - **DST**: Drill stem test
  - **PT100**: Pt-100 probe
  - **PT1000**: Pt-1000 probe
  - **LOG**: Continuous temperature logging (semiconductor transducer or thermistor probe)
  - **CLOG**: Corrected temperature log
  - **DTS**: Distributed temperature sensing
  - **CPD**: Curie Point/Depth estimates
  - **XEN**: Xenolith
  - **GTM**: Geothermometry
  - **BSR**: Bottom-simulating seismic reflector
  - **APCT/SET-2**: Ocean Drilling Temperature Tool
  - **SUR**: Surface temperature
- **Description**: Different methods have different accuracy and require different correction approaches. Important for quality assessment.

#### C32: Temperature Method (Bottom)

**Short name**: T_method_bot
**Category**: Temperature Gradient
**Domain**: B
**Obligation**: Mandatory
**Quality**: M-score (B)

Method used for temperature determination at the bottom of the heat-flow determination interval.

- **Unit**: —
- **Type**: Text(255)
- **Range**: From description
- **Allowed Values**: Same as C31
- **Description**: May differ from top method if data sources are different. Asymmetric methods may introduce systematic errors.

#### C33: Shut-In Time (Top)

**Short name**: T_shutin_top
**Category**: Temperature Gradient
**Domain**: B
**Obligation**: Recommended

Time of measurement at the interval top in relation to the end of drilling/end of mud circulation. Positive values are measured after drilling, negative values are measured during drilling.

- **Unit**: hours
- **Type**: Integer(5)
- **Range**: 0 to 99,999
- **Description**: Longer shut-in times allow better thermal equilibration. Short shut-in times require more substantial corrections for drilling disturbance.

#### C34: Shut-In Time (Bottom)

**Short name**: T_shutin_bot
**Category**: Temperature Gradient
**Domain**: B
**Obligation**: Recommended

Time of measurement at the interval bottom in relation to the end of drilling/end of mud circulation. Positive values are measured after drilling, negative values are measured during drilling.

- **Unit**: hours
- **Type**: Integer(5)
- **Range**: 0 to 99,999
- **Description**: May differ from top if measurements were taken at different times. Important for correction calculations.

#### C35: Temperature Correction Method (Top)

**Short name**: T_corr_top
**Category**: Temperature Gradient
**Domain**: B
**Obligation**: Recommended

Applicable only if gradient correction for borehole effects is reported. Approach applied to correct the temperature measurement for drilling perturbations at the top of the interval.

- **Unit**: —
- **Type**: Text(255)
- **Range**: From description
- **Allowed Values**:
  - **HP**: Horner plot
  - **CSM**: Cylinder source method
  - **LSM**: Line source method
  - **IM**: Inverse numerical modeling
  - **Other** (specify authors/method)
  - **Unspecified**
  - **Not corrected**
- **Description**: Correction method affects reliability of corrected temperatures. Different methods appropriate for different shut-in time ranges.

#### C36: Temperature Correction Method (Bottom)

**Short name**: T_corr_bot
**Category**: Temperature Gradient
**Domain**: B
**Obligation**: Recommended

Applicable only if gradient correction for borehole effects is reported. Approach applied to correct the temperature measurement for drilling perturbations at the bottom of the interval.

- **Unit**: —
- **Type**: Text(255)
- **Range**: From description
- **Allowed Values**: Same as C35
- **Description**: May differ from top correction if data quality or shut-in times differ. Consistency in correction methods improves reliability.

#### C37: Number of Temperature Recordings

**Short name**: T_numb
**Category**: Temperature Gradient
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: M-score (B,S)

Number of discrete temperature points (e.g., number of used BHT values, log values, or thermistors used in probe sensing) confirming the mean temperature gradient. Not the repetition of one measurement at a certain depth.

- **Unit**: —
- **Type**: Integer(6)
- **Range**: 0 to 999,999
- **Description**: More temperature points generally improve gradient reliability. Distinguishes between single-point and multi-point gradients.

#### C38: Date of Acquisition

**Short name**: q_acq
**Category**: Metadata
**Domain**: B, S
**Obligation**: Mandatory

The entry gives the year of the acquisition of the heat-flow data (which may differ from the year of publication). If the month is unknown use 01.

- **Unit**: —
- **Type**: POSIX date (YYYY-MM)
- **Range**: 1900 to present
- **Format**: YYYY-MM or YYYY-MM; YYYY-MM for ranges
- **Description**: Acquisition date is important for temporal analyses and understanding data vintage. For multi-year campaigns, specify range.

### Thermal Conductivity Category

#### C39: Mean Thermal Conductivity

**Short name**: tc_mean
**Category**: Thermal Conductivity
**Domain**: B, S
**Obligation**: Mandatory

Mean conductivity in vertical direction representative for the interval of heat-flow determination. The value should reflect the true in-situ conditions for the corresponding heat-flow interval.

- **Unit**: W/(mK)
- **Type**: Double(4), 2 digits, 2 decimal places
- **Range**: 0 to 99.99, N/A
- **Description**: Thermal conductivity is the key material property for heat flow calculation. Should represent in-situ conditions (pressure, temperature, saturation).

#### C40: Thermal Conductivity Uncertainty

**Short name**: tc_unc
**Category**: Thermal Conductivity
**Domain**: B, S
**Obligation**: Recommended

Uncertainty of mean thermal conductivity given as one-sigma standard deviation.

- **Unit**: W/(mK)
- **Type**: Double(4), 2 digits, 2 decimal places
- **Range**: 0 to 99.99, N/A
- **Description**: Includes measurement uncertainty, spatial variability, and correction uncertainties. Critical for heat flow uncertainty calculation.

#### C41: Thermal Conductivity Source

**Short name**: tc_source
**Category**: Thermal Conductivity
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: M-score (B,S)

Nature of the samples upon which thermal conductivity was determined.

- **Unit**: —
- **Type**: Text(255)
- **Range**: From description
- **Allowed Values**:
  - Outcrop samples
  - Core samples
  - Cutting samples
  - Mineral computation
  - Well log interpretation
  - Core-log integration
  - In-situ probe
  - Other (describe method)
  - Unspecified
- **Description**: Sample source affects representativeness and quality. In-situ measurements and core samples are generally most reliable.

#### C42: Thermal Conductivity Location

**Short name**: tc_location
**Category**: Thermal Conductivity
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: M-score (B,S)

Location where thermal conductivity measurements were made relative to the heat flow site.

- **Unit**: —
- **Type**: Text(255)
- **Range**: —
- **Description**: On-site measurements are most reliable. Measurements from nearby locations or regional averages introduce additional uncertainty.

#### C43: Thermal Conductivity Method

**Short name**: tc_meth
**Category**: Thermal Conductivity
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: M-score (S)

Method used for thermal conductivity determination.

- **Unit**: —
- **Type**: Text(255)
- **Range**: From description
- **Allowed Values**:
  - **Lab** (specify technique):
    - Divided bar/comparator apparatus
    - Optical scanning
    - Needle probe
    - Half space line source
    - Transient plane source
    - Pulse technique
    - Ångström method/periodic heating
    - Mongelli method/plane-heat source
    - Other (describe)
  - **Probe** (specify technique)
  - **Well logging** (specify technique)
  - **Estimation** (specify approach):
    - Correlation with nearby values
    - Lithology mixtures with literature values
    - Water content
    - Chlorine content
    - Estimated from lithology
  - **Unspecified**
- **Description**: Measurement method affects accuracy and applicability. Different methods suited for different sample types and field conditions.

#### C44: Thermal Conductivity Saturation

**Short name**: tc_satur
**Category**: Thermal Conductivity
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: M-score (B,S)

Saturation state of the rock sample studied for thermal conductivity.

- **Unit**: —
- **Type**: Text(255)
- **Range**: From description
- **Allowed Values**:
  - **drymeas**: Dry measured (rocks technically dried before measurement)
  - **satmeas**: Saturated measured (rocks technically saturated completely before measurement)
  - **insitusatmeas**: In-situ saturated measured (measurements with probe sensing/marine)
  - **coresatmeas**: Saturated measured on closed sediment cores on-board
  - **satcalc**: Saturated calculated (from dry measurements, porosity, and pore fluid)
  - **recov**: As recovered (preserved in natural saturation state)
  - **other**: Other
  - **unspec**: Unspecified
  - **n/a**: N/A (if not measured on samples)
- **Description**: Water saturation significantly affects conductivity. In-situ saturation conditions are most representative. Dry measurements must be corrected.

#### C45: Thermal Conductivity pT Conditions

**Short name**: tc_pTcond
**Category**: Thermal Conductivity
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: M-score (B,S)

Qualified conditions of pressure and temperature under which the mean thermal conductivity used for heat-flow computation was determined.

- **Unit**: —
- **Type**: Text(255)
- **Range**: From description
- **Allowed Values**:
  - Unrecorded ambient pT conditions
  - Recorded ambient pT conditions
  - Actual in-situ (pT) conditions
  - Replicated in-situ (p)
  - Replicated in-situ (T)
  - Replicated in-situ (pT)
  - Unspecified
- **Description**: Pressure and temperature significantly affect conductivity, especially at depth. In-situ or replicated conditions provide most accurate values.

#### C46: Thermal Conductivity Assumed pT Function

**Short name**: tc_pTfunc
**Category**: Thermal Conductivity
**Domain**: B, S
**Obligation**: Recommended

Technique or approach used to correct the measured thermal conductivity towards in-situ pT conditions.

- **Unit**: —
- **Type**: Text(255)
- **Range**: From description
- **Allowed Values**:
  - Published correction (specify authors)
  - Site-specific experimental relationships
- **Description**: Correction functions are empirical or theoretical relationships. Should cite specific publication or experimental basis.

#### C47: Thermal Conductivity Number

**Short name**: tc_numb
**Category**: Thermal Conductivity
**Domain**: B, S
**Obligation**: Mandatory
**Quality**: M-score (B,S)

Number of discrete conductivity determinations used to determine the mean thermal conductivity. Not the repetition of one measurement on one rock sample or one thermistor.

- **Unit**: —
- **Type**: Integer(4)
- **Range**: 0 to 9,999
- **Description**: More measurements improve statistical reliability and capture spatial variability. Single measurements have higher uncertainty.

#### C48: Thermal Conductivity Averaging Methodology

**Short name**: tc_strategy
**Category**: Thermal Conductivity
**Domain**: B, S
**Obligation**: Recommended

Strategy that was employed to estimate the thermal conductivity over the vertical interval of heat-flow determination.

- **Unit**: —
- **Type**: Text(255)
- **Range**: From description
- **Allowed Values**:
  - Random or periodic depth sampling (specify number)
  - Characterize formation conductivities (number of samples per formation)
  - Well logging
  - Computation from probe sensing
  - Other
  - Unspecified
- **Description**: Averaging strategy affects how well the mean conductivity represents the interval. Systematic sampling better captures lithological variations.

#### C49: IGSN

**Short name**: Ref_IGSN
**Category**: Metadata
**Domain**: B, S
**Obligation**: Optional

International Geo Sample Numbers (semicolon separated) for rock samples used for laboratory measurements of thermal conductivity.

- **Unit**: —
- **Type**: Text(255)
- **Range**: —
- **Description**: IGSNs provide persistent identifiers linking to physical samples. Essential for sample-based data provenance and future reanalysis.

---

## Summary Tables

### Parent Level Fields

| ID | Field Name | Short Name | Category | Domain | Obligation | Quality | Data Type | Unit |
|----|------------|------------|----------|--------|------------|---------|-----------|------|
| P01 | Heat Flow Value | q | Heat Flow | B,S | M | U-score | double(7) | mW/m² |
| P02 | Heat Flow Uncertainty | q_unc | Heat Flow | B,S | M | U-score | double(7) | mW/m² |
| P03 | Site Name | name | Metadata | B,S | M | — | Text(255) | — |
| P04 | Latitude | lat | Geographical | B,S | M | — | DECIMAL(7) | degrees |
| P05 | Longitude | lng | Geographical | B,S | M | — | DECIMAL(8) | degrees |
| P06 | Elevation | elevation | Geographical | B,S | M | M-score(S) | FLOAT32 | m |
| P07 | Basic Geographical Environment | env | Metadata | B,S | M | — | Text(255) | — |
| P08 | General Comments | q_comment | Metadata | B,S | R | — | Text(255) | — |
| P09 | Flag Heat Production | corr_HP_flag | Flag | B,S | R | — | BIT | — |
| P10 | Total Measured Depth | — | Borehole | B | R | — | Double | m |
| P11 | Total True Vertical Depth | — | Borehole | B | R | — | Double | m |
| P12 | Type of Exploration Method | method | Metadata | B | M | — | Text(255) | — |
| P13 | Original Exploration Purpose | expl | Metadata | B | R | — | Text(255) | — |

### Child Level Fields

| ID | Field Name | Short Name | Category | Domain | Obligation | Quality | Data Type | Unit |
|----|------------|------------|----------|--------|------------|---------|-----------|------|
| **Heat Flow** |
| C01 | Heat Flow Value | qc | Heat Flow | B,S | M | U-score | double(7) | mW/m² |
| C02 | Heat Flow Uncertainty | qc_unc | Heat Flow | B,S | M | U-score | double(7) | mW/m² |
| C03 | Heat Flow Method | q_method | Heat Flow | B,S | M | — | Text(255) | — |
| C04 | Heat Flow Interval Top | q_top | Heat Flow | B,S | M | M-score | Double(6) | m |
| C05 | Heat Flow Interval Bottom | q_bot | Heat Flow | B | M | M-score(B) | Double(6) | m |
| C06 | Penetration Depth | hf_pen | Heat Flow | S | M | M-score(S) | Double(5) | m |
| **Metadata & Flags** |
| C07 | Primary Publication Reference | Ref_1 | Metadata | B,S | M | — | Text(255) | — |
| C08 | Additional References | Ref_2 | Metadata | B,S | R | — | Text(255) | — |
| C09 | Relevant Child | childcomp | Metadata | B,S | M | — | BIT | — |
| C10 | General Comments | q_comment | Metadata | B,S | R | — | Text(255) | — |
| C11 | Flag In-Situ Properties | corr_IS_flag | Flag | B,S | R | — | BIT | — |
| C12 | Flag Temperature Corrections | corr_T_flag | Flag | B,S | M | M-score(S) | BIT | — |
| C13 | Flag Sedimentation | corr_S_flag | Flag | B,S | M | P-flag | BIT | — |
| C14 | Flag Erosion | corr_E_flag | Flag | B,S | M | P-flag | BIT | — |
| C15 | Flag Topography | corr_TOPO_flag | Flag | B,S | M | P-flag | BIT | — |
| C16 | Flag Paleoclimate | corr_PAL_flag | Flag | B,S | M | P-flag | BIT | — |
| C17 | Flag Bottom Water | corr_BWT_flag | Flag | B,S | M | P-flag | BIT | — |
| C18 | Flag Convection | corr_CONV_flag | Flag | B,S | M | P-flag | BIT | — |
| C19 | Flag Heat Refraction | corr_HR_flag | Flag | B,S | M | P-flag | BIT | — |
| C20 | Expeditions/Platform | — | Metadata | B,S | R | — | Text(255) | — |
| C21 | Probe Type | hf_probe | Metadata | S | R | — | Text(255) | — |
| C22 | Probe Length | hf_probeL | Metadata | S | R | — | Double(5) | m |
| C23 | Probe Tilt | T_tilt | Metadata | S | M | M-score(S) | Integer(2) | degrees |
| C24 | Bottom-Water Temperature | wat_temp | Metadata | S | O | — | Double(5) | °C |
| C25 | Lithology | geo_lith | Metadata | B,S | O | — | Text(255) | — |
| C26 | Stratigraphic Age | geo_strat | Metadata | B,S | O | — | Text(255) | — |
| **Temperature Gradient** |
| C27 | Temperature Gradient | T_grad_mean_meas | Gradient | B,S | M | — | Double(8) | K/km |
| C28 | Gradient Uncertainty | T_grad_unc_meas | Gradient | B,S | R | — | Double(8) | K/km |
| C29 | Gradient Corrected | T_grad_mean_cor | Gradient | B,S | O | — | Double(8) | K/km |
| C30 | Corrected Gradient Uncertainty | T_grad_unc_cor | Gradient | B,S | O | — | Double(8) | K/km |
| C31 | Temperature Method (Top) | T_method_top | Gradient | B | M | M-score(B) | Text(255) | — |
| C32 | Temperature Method (Bottom) | T_method_bot | Gradient | B | M | M-score(B) | Text(255) | — |
| C33 | Shut-In Time (Top) | T_shutin_top | Gradient | B | R | — | Integer(5) | hours |
| C34 | Shut-In Time (Bottom) | T_shutin_bot | Gradient | B | R | — | Integer(5) | hours |
| C35 | Correction Method (Top) | T_corr_top | Gradient | B | R | — | Text(255) | — |
| C36 | Correction Method (Bottom) | T_corr_bot | Gradient | B | R | — | Text(255) | — |
| C37 | Number of Temperature Recordings | T_numb | Gradient | B,S | M | M-score | Integer(6) | — |
| C38 | Date of Acquisition | q_acq | Metadata | B,S | M | — | POSIX date | — |
| **Thermal Conductivity** |
| C39 | Mean Thermal Conductivity | tc_mean | TC | B,S | M | — | Double(4) | W/(mK) |
| C40 | TC Uncertainty | tc_unc | TC | B,S | R | — | Double(4) | W/(mK) |
| C41 | TC Source | tc_source | TC | B,S | M | M-score | Text(255) | — |
| C42 | TC Location | tc_location | TC | B,S | M | M-score | Text(255) | — |
| C43 | TC Method | tc_meth | TC | B,S | M | M-score(S) | Text(255) | — |
| C44 | TC Saturation | tc_satur | TC | B,S | M | M-score | Text(255) | — |
| C45 | TC pT Conditions | tc_pTcond | TC | B,S | M | M-score | Text(255) | — |
| C46 | TC pT Function | tc_pTfunc | TC | B,S | R | — | Text(255) | — |
| C47 | TC Number | tc_numb | TC | B,S | M | M-score | Integer(4) | — |
| C48 | TC Averaging Method | tc_strategy | TC | B,S | R | — | Text(255) | — |
| C49 | IGSN | Ref_IGSN | Metadata | B,S | O | — | Text(255) | — |

---

## References

- Fuchs, S., Norden, B., & International Heat Flow Commission (2021). A new database structure for the IHFC Global Heat Flow Database. *International Journal of Terrestrial Heat Flow and Applied Geothermics*, 4(1), 1-14.
- International Heat Flow Commission Database Standards (2021)
- Fuchs, S., Norden, B., & International Heat Flow Commission (2021). The Global Heat Flow Database: Release 2021. GFZ Data Services. DOI: 10.5880/fidgeo.2021.014

---

*Document compiled from IHFC GHFDB structure documentation and published specifications (2021)*
