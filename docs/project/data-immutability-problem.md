# Data Immutability and Dataset Versioning

**Date:** January 12, 2026
**Status:** Clarification Required
**Stakeholders:** Data Assessment Team, Development Team

---

## The Core Issue

Once a dataset is published with a DOI, **it becomes immutable** - it cannot be modified. This is a fundamental requirement for scientific integrity, citation stability, and DOI permanence.

**However:** The GHFDB Data Assessment Team needs to reprocess, recalculate, and improve heat flow data to create a quality-assessed, standardized database product.

---

## The Solution: Versioning and Derived Datasets

**Key principle:** Reprocessing creates **new datasets** with proper provenance, not modifications to existing datasets.

### When GHFDB needs to reprocess data

1. **Original dataset remains immutable** (preserved with its DOI)
2. **New derived dataset is created** that records:
   - **Who** performed the reprocessing
   - **What** changed and why
   - **Data provenance** (derived from original dataset)
   - **Methods** used for recalculation
3. **Both versions coexist** - users can access original or reprocessed

### Example Workflow

```
Original Dataset (2020, Dr. Smith)
├─ DOI: 10.xxxx/ghfdb-2020-001
├─ Heat Flow: 74.2 mW/m²
├─ Status: Published, immutable
└─ Cannot be modified

           ↓ GHFDB Team reprocesses (2024)

Derived Dataset (2024, GHFDB Data Assessment Team)
├─ DOI: 10.xxxx/ghfdb-2024-015
├─ Heat Flow: 72.8 mW/m² (recalculated)
├─ Derived from: 10.xxxx/ghfdb-2020-001
├─ Reprocessed by: GHFDB Team
├─ Reason: Updated thermal conductivity model
├─ Method: [Detailed methodology]
├─ Status: Published, immutable
└─ Original dataset still accessible
```

**Both datasets coexist:**

- Original preserved for reproducibility and citation integrity
- Derived version available for users wanting latest methods
- Clear provenance chain connecting them

---

## Modifications Within a Dataset

**Before publication:** Datasets can be freely edited

- Add/remove entries
- Correct errors
- Recalculate values
- Update metadata

**After publication with DOI:** Dataset becomes immutable

- Any changes require creating a new dataset version
- New version gets new DOI
- Provenance metadata connects versions

---

## Critical Questions for Data Assessment Team

### Question 1: Dataset Versioning Workflow

**When GHFDB needs to reprocess existing data:**

> What is the workflow for creating a derived/reprocessed dataset?

- [ ] Manually create new dataset with provenance metadata
- [ ] System-assisted workflow (form/wizard for derived datasets)
- [ ] Automated creation with manual review
- [ ] Other: _________________________________

**What metadata is required for derived datasets?**

- [ ] Original dataset DOI (what we derived from)
- [ ] Reprocessing team/person (who did it)
- [ ] Methods/reason for reprocessing (what changed)
- [ ] Date of reprocessing
- [ ] Version number/identifier
- [ ] Other: _________________________________

---

### Question 2: GHFDB Product Construction

> How is "GHFDB as a product" assembled from individual datasets?

**Option A: GHFDB References Datasets**

- GHFDB curates which datasets/versions to include
- Data remains in original datasets
- GHFDB provides quality flags, recommendations
- Users access data from source datasets

**Option B: GHFDB Imports and Derives**

- Data is imported from source datasets
- GHFDB creates derived versions with reprocessing
- Both original and derived coexist
- GHFDB product = collection of best/recommended versions

**Option C: Hybrid Approach**

- Some data referenced only
- Some data imported and reprocessed
- Clear distinction between types

**Please select A, B, or C:** _________________________________

---

### Question 3: Reprocessing Authority

> Who can create derived/reprocessed datasets?

- [ ] **GHFDB Data Assessment Team only** - Official curation team
- [ ] **Original authors** - Only dataset creators can reprocess their own data
- [ ] **Any registered user** - Community-driven reprocessing
- [ ] **Combination:** _________________________________

**How is reprocessing attributed?**

- [ ] New dataset has different authors (GHFDB team)
- [ ] New dataset lists both original authors + reprocessing team
- [ ] New dataset maintains original authors, flags as "GHFDB curated version"
- [ ] Other: _________________________________

---

### Question 4: User Discovery and Display

> When users search for heat flow data at a site with multiple dataset versions:

**Display approach:**

- [ ] **Show all versions** - User chooses which to use
- [ ] **Show latest/recommended only** - GHFDB highlights canonical version
- [ ] **Show original + link to derived** - Original first, derived as option
- [ ] **Show derived + link to original** - Derived first, original for reference

**Versioning display example:**

```
Site: Gotland Heat Flow

Option 1 - List All Separately:
├─ Dataset A (2020, Smith et al.) - Original
│  Heat Flow: 74.2 mW/m², DOI: 10.xxxx/001
└─ Dataset A Reprocessed (2024, GHFDB Team) - Derived
   Heat Flow: 72.8 mW/m², DOI: 10.xxxx/015
   [Derived from 10.xxxx/001]

Option 2 - Grouped by Family:
└─ Dataset Family: Gotland Heat Flow
   ├─ v1.0 (2020, Smith et al.) - Original
   │  Heat Flow: 74.2 mW/m², DOI: 10.xxxx/001
   └─ v2.0 (2024, GHFDB Team) - Reprocessed
      Heat Flow: 72.8 mW/m², DOI: 10.xxxx/015

Option 3 - Latest with History:
└─ Gotland Heat Flow v2.0 (2024, GHFDB Team)
   Heat Flow: 72.8 mW/m², DOI: 10.xxxx/015
   [View Version History] → v1.0 (2020, Smith)

Which display approach do you prefer? _________________________________
```

---

### Question 5: Reprocessing Scenarios

**Please describe specific scenarios where reprocessing is needed:**

**Scenario 1: Improved Methodology**

- Original data: _________________________________
- What needs reprocessing: _________________________________
- New method: _________________________________
- Expected outcome: _________________________________

**Scenario 2: Error Correction**

- Original data: _________________________________
- Error identified: _________________________________
- Correction needed: _________________________________
- Who discovered error: _________________________________

**Scenario 3: Standardization**

- Original data: _________________________________
- Standardization requirement: _________________________________
- How it differs from original: _________________________________

---

## Implementation Requirements

### Database Schema

**Required fields for datasets:**

- Version identifier (v1.0, v2.0, etc.)
- Derivation relationship (`derived_from` → parent dataset DOI)
- Provenance metadata (who, what, when, why)
- Immutability flag (published = locked)
- Attribution (authors, contributors, reprocessing team)

**Required features:**

- Prevent edits to published datasets
- Version chain tracking (v1 → v2 → v3)
- Support for branching (v1 → v2a and v1 → v2b)
- Multiple source derivation (v3 derived from v1 + v2)

---

### User Interface

**Required features:**

- Dataset creation workflow
- Derived dataset creation wizard with:
  - Source dataset selection
  - Provenance metadata entry
  - Method description
  - Reprocessing reason
- Version comparison tools
- Provenance visualization (relationship diagrams)
- Clear immutability indicators

**User permissions:**

- Dataset owners: edit before publication
- GHFDB team: create derived datasets
- Public users: view all, download all

---

### DOI Management

**Each dataset version needs:**

- Unique DOI
- Permanent URL
- Metadata describing:
  - Relationship to other versions
  - Derivation source(s)
  - Provenance information
- Citation recommendation

**DOI Strategy Options:**

**Option 1: DOI per version**

- Version suffix: `10.xxxx/ghfdb-001.v1`, `10.xxxx/ghfdb-001.v2`
- Pro: Clear version relationship
- Con: May not be supported by all DOI providers

**Option 2: New DOI per version**

- Separate DOIs: `10.xxxx/ghfdb-001`, `10.xxxx/ghfdb-015`
- Metadata links versions
- Pro: Standard DOI practice
- Con: Version relationship less obvious

**Which approach do you prefer?** _________________________________

---

## Action Items

### For Data Assessment Team

**Immediate:**

- [ ] Answer all questions in this document
- [ ] Provide 3-5 real reprocessing scenarios
- [ ] Describe current workflow for data updates
- [ ] Identify team members who perform reprocessing

**Before Implementation:**

- [ ] Document reprocessing standards and methods
- [ ] Define quality criteria for derived datasets
- [ ] Establish attribution/authorship policies
- [ ] Create metadata templates for provenance

---

### For Development Team

**After Clarification:**

- [ ] Design dataset versioning system
- [ ] Implement immutability enforcement (published = locked)
- [ ] Build derived dataset creation workflow
- [ ] Create provenance tracking and visualization
- [ ] Develop version comparison UI
- [ ] Integrate DOI assignment for versions

---

## Examples from Other Domains

### GenBank/RefSeq (Biological Sequences)

- **GenBank:** Submitter-provided sequences (immutable after publication)
- **RefSeq:** NCBI-curated reference sequences (derived, improved)
- Both coexist, clearly labeled
- RefSeq links to source GenBank entries

### UniProt (Protein Data)

- **TrEMBL:** Automated translations (frequently updated)
- **SwissProt:** Manually curated (higher quality)
- Clear distinction, both accessible
- Users choose based on need

### Takeaways for GHFDB

- **Clear labeling** of original vs derived is essential
- **Provenance transparency** builds user trust
- **Both versions** serve different user needs
- **Quality indicators** help users choose

---

## Decision Log

| Date | Decision | Rationale | Sign-off |
|------|----------|-----------|----------|
| _Pending_ | Versioning approach | Based on team responses | Project Lead |
| _Pending_ | DOI strategy | DOI provider requirements | Data Team |
| | | | |

---

## Contact & Next Steps

**Document Owner:** Development Team
**Last Updated:** January 12, 2026

**Required Response:**

- Meeting scheduled by: _________________
- Initial answers completed by: _________________
- Final decision by: _________________
