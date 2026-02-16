# Review: Neumann_etal._2025_02_Track.docx (terminology + consistency)

Reviewer: Samuel Jennings (via Copilot)  
Date: 2026-02-03  
Scope requested by authors: terminology consistency and clarity around “database” meaning, plus targeted technical/language checks. **No ERD feedback included** (explicitly deferred).

## 1) High-priority issue: “database” refers to two different things

Across the manuscript, *database* alternates between:

1. **GHFDB “database” as a research product**: the curated, DOI-released collection of heat-flow observations + metadata (distributed as flat files / export, e.g., CSV at GFZ Data Services).
2. **The web portal backend database**: the internal **relational database** (PostgreSQL) that powers [https://www.heatflow.world](https://www.heatflow.world), stores/links entities, supports ingestion/validation/review, and serves views/APIs.

This dual meaning is specifically called out by the reviewers and in Florian/Kirsten’s email, so it’s worth fixing *systematically* (not just in one paragraph), ideally by adopting one consistent naming scheme and enforcing it everywhere.

### Recommended terminology (simple, consistent)

Use these terms consistently throughout:

- **“GHFDB dataset”** or **“GHFDB release”**: the *published* data product (DOI release at GFZ Data Services; CSV export; what users download/cite).
- **“GHFDB portal” / “heatflow.world portal”**: the web application.
- **“portal backend relational database (PostgreSQL)”** or **“portal database”**: the internal RDBMS powering the portal.
- Avoid using plain **“database”** unqualified, except in phrases like **“relational database”** *when you clearly mean PostgreSQL*.

### Suggested one- or two-sentence clarification to add early

Place this in the Introduction (and optionally briefly in the Abstract), near the first usage of “database”:

> “In this paper we distinguish between (i) the **GHFDB dataset** as the curated, DOI-released collection of heat-flow observations distributed as flat export files (e.g., CSV), and (ii) the **GHFDB portal backend database**, a PostgreSQL-powered relational database that supports ingestion, curation, and online access via heatflow.world.”

That one paragraph makes many later sentences easier to disambiguate.

## 2) Locations where ambiguity appears (with suggested rewrites)

Below are the main sections where wording flips between meanings. I’m not proposing major rewrites—just targeted substitutions.

### Abstract

- The Abstract currently opens with “The Global Heat Flow Database is a comprehensive data compilation…”. That’s fine if you mean the *data product*, but later the Abstract also mentions “developing a new, modern digital data infrastructure”.
  - Suggest ensuring the Abstract uses both terms explicitly once:
    - **“GHFDB dataset (release)”** for the compilation.
    - **“web portal / relational database infrastructure”** for the system.

### Introduction

- “The database is maintained by the IHFC…” (likely means the *dataset/product*). Good, but later: “critical research infrastructure” could be read as either.
  - Suggest: “The GHFDB **dataset** is maintained…” and “the GHFDB **portal infrastructure** enables…”

- “The first release with the new database structure was in 2021…”
  - Here “database structure” appears to mean the *schema/metadata standard* (template fields), not necessarily the PostgreSQL model.
  - Suggest: “new **metadata schema / data model**” (or “new **GHFDB schema**”) to avoid readers assuming “database structure = PostgreSQL tables”.

### Section 3 (Metadata Schema and GHFDB Data Template)

- This section frequently says “database” when it really means “metadata schema”, “template fields”, or “dataset fields”. Examples include:
  - “new comprehensive metadata scheme for the Global Heat Flow Database…”
  - “Table 3: Summary of database properties.”

Suggested pattern:

- When talking about *fields/columns in the template/export*: say **“template fields”**, **“metadata fields”**, **“dataset fields”**, or **“schema properties”**.
- Reserve “database properties” for a relational context.

Also consider replacing:

- “automated information integration into the database” → “automated ingestion into the **portal backend database**” (if you mean PostgreSQL ingestion), or “integration into the **GHFDB dataset**” (if you mean assembling a release).

### Section 6 (Heat-flow data publication process)

This is close, but a couple sentences still blend meanings:

- “Once the data are reviewed… and include the data in the GHFDB infrastructure, a predefined set of metadata properties will be directly exported to GFZ Data Services…”

Suggestion:

- Explicitly name the two steps:
  1) reviewed + ingested into the **portal backend database**, then
  2) exported as the **GHFDB dataset release** for publication at GFZ Data Services.

### Section 7 (New research data infrastructure)

This section is the most explicit about PostgreSQL (great), but it still uses “database” generically in several places:

- “transform the database from a desktop and file-based collection into a fully integrated online database system”

Suggestion:

- Consider: “transform the **GHFDB workflow and access** from a desktop/file-based compilation process into an integrated **portal backed by a relational database** …”

- “tabular data views that allow users to browse through individual data tables…”
  - This line risks implying end-users browse raw SQL tables. In most portals, these are *derived views*.

Suggested wording:

- “tabular data views (derived, user-oriented tables)…” or “searchable tabular views derived from the relational backend…”

### Data availability section

This section already helps the distinction by saying “CSV”. Consider sharpening it:

- “The data are provided in CSV format …”
  - Add: “(exported from the portal backend database)” if true.

## 3) Email points beyond terminology

### (A) Relational database description: precision and framing

Section 7 is generally solid and appropriately non-technical. Two small technical-precision improvements:

- Clarify *what* the PostgreSQL database contains:
  - recommended: “a normalized relational model linking sites, measurements (parent/child), references, and submitted datasets” (even if you don’t enumerate all entities).

- Clarify that end users usually interact via portal UI/API and downloadable exports, not by querying relational tables.
  - This aligns with Kirsten/Florian point (6) without requiring an ERD.

### (B) Flat tables and user perspective (emphasize more)

The manuscript already mentions CSV releases and tabular views, but the “user convenience” argument could be made more explicit:

- Explicitly state the benefit:
  - “Flat exports are easy to import into GIS, spreadsheets, and scripting environments (R/Python), and support reproducible workflows.”

- Connect the two access modes:
  - Portal = exploration/filtering + API
  - Release export = citation-stable snapshot + easy local analysis

### (C) heatflow.world now has a tabular overview

You already note “tabular data views” in Section 7. I’d make sure the emphasis matches the email request:

- Use phrasing like “**searchable tabular overview**” and tie it to user workflows (“filter, sort, and download subsets”).
- If you add a screenshot later, the table view is a strong candidate (again: not requesting ERD here).

### (D) Improved description of online infrastructure

Section 7 describes Docker, CI, etc. Consider whether the paper’s audience benefits from the dev-ops list.

- Keep it short, but ensure the “so what?” is clear: reproducibility, maintainability, open-source transparency, stable hosting.
- A simple screenshot set (portal landing page + map + table view) would support the “now online” claim.

### (E) Submission workflow clarity

Section 6 mostly covers it, but I’d make one conceptual point explicit:

- Contributors submit via **GHFDB Data Template (Excel)** → validated → ingested into **portal backend database** → curated/reviewed → exported to **release dataset** → published at GFZ Data Services (DOI).

Also: ensure wording avoids implying the dataset *is* the PostgreSQL database.

## 4) Language/grammar and small consistency notes

A few small items that look worth tightening (without rewriting sections):

- Watch for “database” vs “dataset” vs “data collection” vs “infrastructure” drift within the same paragraph.
- Capitalization consistency:
  - “Global Heat Flow Database (GHFDB)” vs “Global Heat Flow DatabaseDataTemplate” (spacing)
  - “Heat Flow Database” vs “heat-flow database”

- A couple punctuation/typo candidates noticed in the extracted text:
  - Double period in “wasalso initiated..” (Section 2)
  - Occasional missing spaces around tool names (e.g., “quality_scoresPython script”, “calledvocabulary_check”)—may be extraction artifacts, but worth checking in Word.

## 5) Quick checklist for a final pass (what I’d do in Word)

- Search for `database` and ensure each occurrence is one of:
  - “GHFDB dataset/release” (product) OR
  - “portal backend database (PostgreSQL)” (infrastructure)
  - “metadata schema/data model/template fields” (schema/standard)

- Search for `infrastructure`, `portal`, `PostgreSQL`, `export`, `CSV`, `template` and ensure the pipeline story is consistent.

---
If you want, I can also produce a short “preferred wording” block (2–3 variants) tailored to the journal’s style (e.g., ESSD-style phrasing) that you can paste into the Introduction + Section 7 without changing scientific content.
