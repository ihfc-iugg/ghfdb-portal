# Figure Caption: Global Heat Flow Database Entity-Relationship Diagram

**Figure X.** Entity-Relationship Diagram (ERD) for the Global Heat Flow Database (GHFDB), showing a hierarchical parent–child structure grouped into **Parent-related entities** (green-shaded cluster) and **Child-related entities** (orange-shaded cluster). ParentChildRelation (purple) is a junction table linking parent and child heat-flow records and flagging which child values contribute to the parent calculation (`is_relevant`).

Primary keys are underlined and foreign keys italicized; **crow’s-foot** style notation indicates one-to-many relationships. A special `quantity` type denotes numeric values stored with standardized units (see Technical Note). Color coding distinguishes entity roles: blue entities capture relatively stable site/interval metadata, orange/green entities capture measurement- and value-specific information, and purple denotes relational infrastructure.

This schema supports provenance tracking from interval-level inputs (e.g., thermal gradients and conductivities) through derived child heat-flow estimates (with corrections and probe metadata) to quality-controlled, site-level parent heat-flow values.

**Technical Note:** This ERD is an idealized conceptual model; the implementation uses additional joins (including polymorphic relationships) that are omitted for clarity. `quantity` fields are an application-level construct storing a magnitude alongside standardized units.
