# GHFDB-Specific Specifications

This document contains feature specifications specific to the Global Heat Flow Database Portal, ordered by implementation priority. Critical foundational specs that affect others come first, followed by GHFDB-specific domain features, documentation and mapping specifications, and finally user experience enhancements.

**Status Key:**

- ✅ **Implemented** - Feature is complete and in production
- 🔄 **In Progress** - Currently being implemented
- 📋 **Planned** - Specified and ready for implementation
- 💡 **Proposed** - Idea stage, requires further analysis

---

## Critical Foundation (Dependencies for Other Specs)

### FS-001 - Documentation Infrastructure & Conventions

**Status:** 🔄 In Progress (spec-001)
**Test Coverage:** ~40% | **Documentation:** ~60%
**Dependencies:** None
**Affects:** All other specs (documentation requirements)

Define how documentation is authored, validated, and kept synchronized with governance and feature implementations. Establish the documentation information architecture distinguishing user guides, developer documentation, and governance materials. Define cross-linking strategies between governance documents and technical documentation. Establish a feature documentation checklist specifying what documentation must be updated when features ship. Define how specifications are referenced from documentation to enable traceability. Establish validation criteria including build processes, link checking, failure conditions, and minimum quality expectations. Ensure contributors can locate appropriate documentation locations, follow consistent checklists when shipping features, and execute repeatable documentation validation.

### FS-002 - Testing Infrastructure & Conventions

**Status:** 🔄 In Progress (spec-002)
**Test Coverage:** ~30% | **Documentation:** ~50%
**Dependencies:** None
**Affects:** All feature validation and quality assurance

Define the testing strategy, test organization layers, and foundational test fixtures supporting feature validation. Establish test layer taxonomy (unit, integration, contract) and their organizational structure. Define naming conventions for test files and test functions. Establish minimal fixture datasets covering common workflows including data import, review submission, administrative approval, and export operations. Define testing patterns for schema mapping validation and round-trip data integrity. Ensure feature specifications can reference standard test layers and fixture locations unambiguously, minimal happy-path integration tests exist covering end-to-end workflows, and testing conventions provide clear guidance on test naming, organization, and required assertions.

### FS-003 - CI/CD Pipeline & Automation

**Status:** 🔄 In Progress (spec-003)
**Test Coverage:** ~10% | **Documentation:** ~25%
**Dependencies:** FS-002 (testing infrastructure)
**Affects:** All feature quality gates and deployment

Define continuous integration and deployment automation including pull request checks, main branch integration, and scheduled or on-demand operations. Establish test execution strategies determining which test suites run in different contexts. Define coverage collection and reporting expectations. Establish build and deployment automation sequences. Define environment-specific configurations for different deployment targets. Establish failure notification and handling procedures. Ensure contributors understand what automated checks will run on their contributions, CI failures provide actionable diagnostic information, and deployment to staging and production environments follows documented, auditable procedures.

### FS-004 - IHFC-Django Model Mapping & Validation

**Status:** 🔄 In Progress (spec-004)
**Test Coverage:** ~20% | **Documentation:** ~40%
**Dependencies:** None (but validates all model specs)
**Affects:** FS-008, FS-009, FS-010, FS-011

Define validation requirements, documentation standards, and policies for mapping between IHFC conceptual model and Django relational models. Establish validation rules confirming all IHFC-defined GHFDB fields are represented in Django models, including fields inherited from base classes or FairDM framework models. Define how the GHFDB field mapping documentation (docs/ghfdb_fields.md) is maintained as authoritative source of truth with required columns (GHFDB Name, Database Table, Accessed From, Accessor, Django Model). Establish documentation conventions for mapping GHFDB conceptual fields to Django model fields, handling complex relationships like many-to-many, foreign keys, and computed properties. Define policies for derived fields, nullability mismatches, and schema divergences between GHFDB and Django models. Establish how Django model extensions beyond the GHFDB specification are documented and justified. Define automated validation capabilities for detecting missing GHFDB fields or mapping inconsistencies. Establish update process when schema changes occur, approval workflows for mapping modifications, and change management procedures when IHFC updates the GHFDB conceptual model. Ensure every GHFDB field traces to a specific Django model field or computed accessor, non-one-to-one mappings follow standardized documentation format, extensions are explicitly justified, and validation can detect model drift from specification. Cover cases like quality scores calculated from multiple inputs, denormalized parent fields (lat_NS, lon_EW), and read-only computed properties.

---

## GHFDB Core Domain Specifications

### FS-008 - GHFDB Template Import/Export Contract with Round-Trip Integrity

**Status:** 📋 Planned
**Dependencies:** FS-004 (Model Mapping), FS-009 (Vocabularies), FS-011 (Flat Query Construction)
**Affects:** Data migration and archive workflows

Define the complete contract for GHFDB Excel template import, export, and round-trip integrity. **Import Contract:** Specify expected structure and validation rules for GHFDB Excel workbooks including all required sheets and mandatory column headers, how optional columns are handled, field mapping rules from workbook columns to canonical data model, and template versioning strategy. Define header row location (row 6), data start location (row 9), and sheet requirements ("data list" sheet mandatory). Establish validation behavior providing deterministic pass/fail results with actionable error messages when required sheets or columns are missing. **Export Contract:** Define rules for generating IHFC-compliant Excel exports from relational database model. Specify required columns and how relational data is denormalized into flat rows. Establish ordering rules, determinism guarantees, and formatting requirements. Define behavior for null values, derived fields, and repeated entities across relationships. Specify how parent-child relationships (HeatFlowSite → SurfaceHeatFlow → HeatFlow) are flattened into single rows, how many-to-many fields (correction flags, lithology) are serialized, and how controlled vocabularies are represented. **Round-Trip Integrity:** Define acceptance criteria for data integrity through complete import-export-reimport cycle. Specify what data must be preserved exactly and what transformations are acceptable (ordering changes, formatting normalization, derived field recalculation). Establish canonical comparison rules for determining data equivalence and fixture requirements for automated testing. Specify acceptable lossiness categories: (1) formatting normalization (whitespace, case in vocabularies), (2) derived field recalculation (quality scores), (3) ordering changes (row order may vary). Define unacceptable losses: mandatory field data, coordinate precision, heat flow values, uncertainty values, authorship information. Ensure template validation is automated, parsing errors reference specific cells, version evolution is backward-compatible, exported spreadsheets validate against published schema, exports are deterministic for identical database snapshots, and round-trip tests verify data preservation.

### FS-009 - Controlled Vocabulary & Units Normalization

**Status:** 📋 Planned
**Dependencies:** None
**Affects:** FS-008, FS-011

Define accepted controlled vocabularies and unit handling rules for heat flow data. Specify normalization rules including case-sensitivity, whitespace trimming, and canonical value mappings. Establish unit conversion rules and when conversions should occur in the data pipeline. Determine which validations occur at import-time versus publish-time. Ensure semantically equivalent values entered in different acceptable formats normalize to a single canonical representation, and invalid vocabulary or unit values produce actionable error messages. Cover GHFDB-specific vocabularies including environment types, exploration methods, measurement methods, correction flags, lithology terms, and quality score categories.

### FS-010 - Quality Scoring Calculation & Storage

**Status:** 📋 Planned
**Dependencies:** FS-004 (Model Validation)
**Affects:** FS-011

Define calculation methods, storage requirements, and export behavior for heat flow quality scores (U-score, M-score, correction flags). Specify score calculation logic with exact formulae or references to published scientific methods (Fuchs et al. 2023). Define required input fields for each score type. Establish where scores are persisted in the data model (HeatFlow.U_score, HeatFlow.M_score fields). Determine when scores are calculated (import time, curation review, on-demand). Define how scores appear in IHFC exports and public API responses. Ensure score calculations are deterministic and testable given known inputs, calculation methods are documented with scientific references, and scores are included in IHFC export format. Include validation that U-score categories (U1-U4, Ux) and M-score categories (M1-M4, Mx) are correctly assigned based on COV thresholds and methodology quality indicators.

### FS-011 - IHFC Flat Query Construction

**Status:** 📋 Planned
**Dependencies:** FS-004 (Model Mapping), FS-010 (Quality Scoring)
**Affects:** FS-008 (Import/Export Contract)

Define tools and patterns for constructing IHFC flat data structures from Django's relational models. Specify query patterns for traversing parent-child relationships (HeatFlowSite → SurfaceHeatFlow → HeatFlow) and collecting all fields required for flat GHFDB export format. Define aggregation strategies for many-to-many fields (correction flags, lithology), serialization of controlled vocabularies, and inclusion of derived fields (quality scores). Establish ORM query patterns using select_related and prefetch_related for performance. Define how to handle null values, format numeric fields, and serialize spatial data (coordinates, elevation). Specify utilities or query builders that accept a Django queryset and return IHFC-compatible flat dictionaries or row objects. Ensure queries are optimized to avoid N+1 problems, produce deterministic ordering, and handle edge cases like missing parent relationships or incomplete data. Provide reusable query components that export and import processes can both utilize.

---

## Documentation Standards

### FS-012 - Accessor Path & ORM Example Standards

**Status:** 💡 Proposed
**Dependencies:** FS-004 (Model Mapping), FS-011 (Flat Query Construction)
**Affects:** Developer documentation

Define consistent documentation patterns for querying canonical data corresponding to GHFDB fields. Specify how to document accessor paths including model.field chains and join rules. Establish standards for ORM query examples in documentation including format conventions, security considerations, and performance guidance. Ensure each GHFDB field can be traced to a documented accessor path with example queries. Provide patterns for common access scenarios: direct field access (HeatFlow.value → q), parent traversal (HeatFlow.parent.sample.location.latitude → lat_NS), many-to-many (HeatFlow.corr_IS_flag.all()), derived properties (HeatFlow.get_U_score()).
