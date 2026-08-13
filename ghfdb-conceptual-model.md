# Global Heat Flow Database: Conceptual Data Model

## Overview

The Global Heat Flow Database (GHFDB) organizes heat flow information using a hierarchical structure that distinguishes between aggregated, site-level heat flow values (parent entities) and the detailed interval-level measurements from which they are derived (child entities). This separation enables transparent provenance tracking from raw measurements through to quality-controlled surface heat flow estimates.

---

## Conceptual Architecture

The data model comprises **ten primary entities** organized into three conceptual groups:

1. **Parent-Related Entities** — Site-level metadata and aggregated heat flow values
2. **Child-Related Entities** — Interval-level measurements and derived heat flow determinations
3. **Relational Infrastructure** — Junction tables connecting parent and child records

A **spatial reference entity** (Point) supports geographic positioning across both groups.

---

## Entity Descriptions

### Parent-Related Entities

These entities capture stable, site-level information that typically remains constant across multiple measurements at the same location.

#### **HeatFlowSite**
Represents a geographic location where heat flow measurements are acquired. A heat flow site may be a terrestrial borehole, a marine sediment core location, or any other exploration site.

**Attributes:**
- **Identification**: Unique identifier, site name, and IGSN sample identifiers
- **Geographic Context**: Country, region, continent, geological domain, and environment type (e.g., continental, oceanic, lake)
- **Spatial Reference**: Link to geographic coordinates via a Point entity
- **Exploration Metadata**: Exploration method (drilling, coring, etc.) and purpose (scientific research, resource exploration)
- **Depth Information**: Total measured depth, true vertical depth, and surface elevation

#### **ParentHeatFlow**
Stores the aggregated, quality-controlled surface heat flow density for a given site. Each site has one parent heat flow record that synthesizes potentially multiple child heat flow determinations from different depth intervals.

**Attributes:**
- **Reference**: Association to a HeatFlowSite
- **Heat Flow Value**: Surface heat flow density (mW/m²) with uncertainty estimate (1-sigma)
- **Correction Status**: Flag indicating whether heat production corrections have been applied
- **Comments**: Textual annotations and metadata

#### **Point**
Defines geographic coordinates in a specified coordinate reference system. Points are reusable spatial references that can be shared across multiple heat flow sites.

**Attributes:**
- **Coordinates**: X-coordinate (longitude), Y-coordinate (latitude)
- **Reference System**: Coordinate reference system identifier (e.g., WGS84, EPSG codes)

---

### Child-Related Entities

These entities represent interval-specific measurements and calculations. Multiple child entities may exist for a single heat flow site, each corresponding to different depth intervals or measurement campaigns.

#### **GeoDepthInterval**
Defines a depth-stratified section within a heat flow site, characterized by specific geological and stratigraphic properties. This entity serves as the spatial and geological context for measurements.

**Attributes:**
- **Site Association**: Link to the parent HeatFlowSite
- **Depth Boundaries**: Top and bottom depths defining the interval extent
- **Vertical Reference**: Vertical depth and datum (e.g., mean sea level)
- **Geological Context**: Lithology, geologic age, stratigraphic unit
- **Annotations**: Additional notes about the interval

#### **ThermalGradient**
Represents temperature gradient measurements over a specific depth interval. The thermal gradient quantifies the rate of temperature change with depth.

**Attributes:**
- **Interval Association**: Link to a GeoDepthInterval
- **Gradient Values**: Raw and corrected temperature gradient (K/km) with uncertainties
- **Measurement Methodology**: Temperature acquisition methods at interval boundaries (top and bottom)
- **Equilibration**: Shut-in times at top and bottom boundaries (hours)
- **Corrections**: Methods applied to correct for drilling disturbances or transient effects
- **Quality Metrics**: Number of temperature recordings and quality score

#### **IntervalConductivity**
Stores the mean thermal conductivity over a depth interval, derived from laboratory measurements or estimated from other properties.

**Attributes:**
- **Interval Association**: Link to a GeoDepthInterval
- **Conductivity Value**: Mean thermal conductivity (W/mK) with uncertainty
- **Data Provenance**: Sample source type (core, cuttings, logs) and data location (measured, literature)
- **Measurement Details**: Determination method, sample saturation state
- **Pressure-Temperature Handling**: Measurement conditions and correction functions applied
- **Averaging Strategy**: Methodology for computing interval-mean conductivity
- **Quality Metrics**: Number of individual measurements and quality score

#### **HeatFlow**
A derived entity representing interval-level heat flow density calculated from thermal gradient and thermal conductivity via Fourier's law of heat conduction. This is the fundamental "child" heat flow determination.

**Attributes:**
- **Input References**: Links to ThermalGradient and IntervalConductivity entities used in calculation
- **Heat Flow Value**: Calculated heat flow density (mW/m²) with propagated uncertainty
- **Calculation Method**: Approach used (Fourier, Bullard plot for variable conductivity, etc.)
- **Acquisition Context**: Date acquired, expedition/cruise/vessel name, bottom water temperature (for marine settings)
- **Quality Assessment**:
  - U-score: Numerical uncertainty quality (U1=excellent, U2=good, U3=ok, U4=poor, Ux=unknown)
  - M-score: Methodological quality (M1=excellent, M2=good, M3=ok, M4=poor, Mx=unknown)
- **Comments**: Textual annotations

#### **ProbeMetadata**
Captures metadata specific to marine heat flow probes. This entity is relevant only for marine measurements and stores instrument-specific parameters.

**Attributes:**
- **Interval Association**: Link to the associated GeoDepthInterval
- **Probe Characteristics**: Probe type, length, penetration depth
- **Deployment Conditions**: Tilt angle during measurement

#### **HeatFlowCorrection**
Documents corrections applied (or not applied) to heat flow values. Multiple correction records may exist for a single heat flow determination, each addressing different disturbance types.

**Attributes:**
- **Heat Flow Reference**: Link to the associated HeatFlow entity
- **Correction Type**: Classification of disturbance (e.g., IS=in-situ stress, T=temperature transient, S=sedimentation, E=erosion, TOPO=topographic, PAL=paleoclimate, SUR=surface temperature changes, CONV=convection, HR=heat refraction)
- **Status**: Whether the disturbance is present, corrected, or left uncorrected

---

### Relational Infrastructure

#### **ParentChildRelation**
A junction table establishing many-to-many relationships between parent heat flow records and child heat flow determinations. This entity enables a single parent to aggregate multiple children, and (in rare cases) a single child to contribute to multiple parents.

**Attributes:**
- **Parent Reference**: Link to a ParentHeatFlow entity
- **Child Reference**: Link to a HeatFlow entity
- **Relevance Flag**: Boolean indicator specifying whether this child was used in calculating the parent value (supports exclusion of low-quality determinations)

---

## Relationship Structure

### Spatial Foundation
- **Point → HeatFlowSite** (one-to-many): A Point defines the geographic location of one or more HeatFlowSites. Multiple sites may share coordinates when measurements overlap or when different campaigns target the same location.

### Parent-Level Relationships
- **HeatFlowSite → ParentHeatFlow** (one-to-many): Each site may have one parent heat flow record per release or analysis version.

### Cross-Domain Linkage
- **HeatFlowSite → GeoDepthInterval** (one-to-many): A site contains multiple depth intervals, each representing a distinct geological or measurement segment.

### Measurement Cascade (Child Domain)
The child entities form a measurement-to-calculation cascade:

1. **GeoDepthInterval → ThermalGradient** (one-to-many): Each interval may have multiple thermal gradient determinations from different measurement campaigns or techniques.

2. **GeoDepthInterval → IntervalConductivity** (one-to-many): Similarly, each interval may have multiple conductivity determinations from different samples or methods.

3. **ThermalGradient + IntervalConductivity → HeatFlow** (many-to-one converging): A single heat flow determination requires exactly one thermal gradient and one thermal conductivity. The same gradient or conductivity may be combined with different counterparts to produce multiple heat flow estimates (for sensitivity analysis).

4. **GeoDepthInterval → ProbeMetadata** (one-to-many): Marine intervals may have probe metadata records documenting instrument parameters for each deployment.

5. **HeatFlow → HeatFlowCorrection** (one-to-many): Each heat flow determination may have multiple correction records, one per disturbance type.

### Parent-Child Bridge
- **ParentHeatFlow ← ParentChildRelation → HeatFlow** (many-to-many): The junction table connects parent and child heat flow entities, tracking which child determinations contribute to each parent aggregation. The `is_relevant` flag allows selective inclusion (e.g., excluding low-quality children from the parent calculation while retaining them in the database for provenance).

---

## Data Flow Narrative

The GHFDB data model supports the following conceptual workflow:

1. **Site Establishment**: A HeatFlowSite is defined with geographic coordinates (Point) and metadata (location, exploration context, depth).

2. **Interval Definition**: The site is subdivided into GeoDepthIntervals, each characterized by geological properties (lithology, age, stratigraphy).

3. **Measurement Acquisition**:
   - Temperature profiles yield ThermalGradient values per interval.
   - Rock samples or logs provide IntervalConductivity estimates.
   - Marine measurements optionally include ProbeMetadata.

4. **Heat Flow Calculation**: ThermalGradient and IntervalConductivity are combined via Fourier's law to compute interval-specific HeatFlow determinations. Quality scores (U-score, M-score) assess reliability.

5. **Correction Assessment**: HeatFlowCorrection records document whether known disturbances (topography, paleoclimate, erosion, etc.) are present, corrected, or uncorrected.

6. **Aggregation to Parent**: Multiple child HeatFlow values are aggregated (e.g., depth-weighted average) to produce a single ParentHeatFlow for the site. The ParentChildRelation junction table tracks which children contribute, with `is_relevant` flagging the subset used in aggregation.

7. **Provenance and Transparency**: The hierarchical structure preserves full provenance from raw measurements through to published heat flow values, enabling reproducibility, quality assessments, and future reanalyses as methodologies improve.

---

## Key Design Principles

### Provenance Preservation
Every parent heat flow value traces back to specific child determinations, which in turn reference explicit thermal gradient and conductivity measurements over defined geological intervals.

### Quality Stratification
Quality assessments occur at multiple levels:
- **Measurement level**: ThermalGradient and IntervalConductivity entities include quality scores.
- **Determination level**: HeatFlow entities include U-scores (uncertainty) and M-scores (methodology).
- **Aggregation level**: ParentChildRelation's `is_relevant` flag allows inclusion/exclusion in parent calculations based on quality thresholds.

### Flexibility for Marine and Terrestrial Settings
- Terrestrial boreholes: Measurements may span multiple depth intervals with varying lithologies.
- Marine cores: Typically single-interval measurements with ProbeMetadata capturing instrument-specific parameters.
- The model accommodates both scenarios without forcing artificial uniformity.

### Correction Transparency
Rather than storing only "final" corrected values, the model explicitly documents what corrections were applied, enabling users to retrieve uncorrected values or apply alternative correction schemes.

### Spatial Reusability
Point entities are independent, allowing multiple sites to reference the same coordinates (e.g., repeated measurements from different campaigns at the same location over time).

---

## Summary

The GHFDB conceptual model separates **stable site-level metadata** (parent entities) from **detailed interval-level measurements** (child entities), bridged by a **junction table** that tracks aggregation provenance. This design ensures:

- **Transparency**: Full traceability from raw measurements to published values.
- **Flexibility**: Accommodation of terrestrial and marine settings, multiple measurement campaigns, and evolving quality standards.
- **Reusability**: Shared spatial references, correction documentation, and quality-flagged aggregations enable diverse analytical workflows without data duplication.

The ten entities work in concert to represent the complexity of heat flow determination while maintaining a clear conceptual hierarchy suitable for both human understanding and computational processing.
