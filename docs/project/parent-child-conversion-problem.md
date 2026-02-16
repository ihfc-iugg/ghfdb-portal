# Parent-Child Conversion Problem

**Date:** January 12, 2026
**Status:** 🚨 CRITICAL - Development Blocked
**Stakeholders:** Data Assessment Team, Development Team

---

## The Core Problem

In recent workshops, the team casually mentions "converting parents to children" when new data arrives. But I cannot build a database schema without understanding what this actually means.

**The fundamental question:**
Are parent and child **different types of data** that need conversion, or are they **role designations** on the same underlying measurement data?

---

## Why This Matters

This question determines everything:

- Whether we need 1 or 2 database tables
- Whether "conversion" adds/removes metadata or just changes a flag
- Whether existing Excel data can be imported without data loss
- Whether researchers can upload their own "parent" interpretations

**Until we answer this, the database cannot be designed.**

---

---

## Critical Questions I Need Answered

### Question 1: What does "parent becomes child" actually mean?

When you say "the existing parent becomes a child and the new data becomes the parent," walk me through **exactly** what happens:

**Before:**

- What exists in the database/spreadsheet?
- What is its metadata?

**Event:**

- New data arrives...

**After:**

- What changed?
- Was anything added, removed, or just relabeled?

**Please describe using a real example from your workflow.**

---

### Question 2: Can a site have multiple parent values?

**Scenario:** Two researchers publish datasets for the same site with different parent values.

- Dataset A (2020): Site X parent = 74.2 mW/m²
- Dataset B (2023): Site X parent = 68.5 mW/m²

**What happens?**

- [ ] Only one can be "the parent" (data team decides which)
- [ ] Both can exist as parents (dataset-specific)
- [ ] Something else: _______________________

---

### Question 3: Single-entry site

**Scenario:** A site has only ONE heat flow measurement.

**Questions:**

1. Does that single entry have:
   - [ ] Only parent metadata (10 fields)
   - [ ] Only child metadata (30 fields)
   - [ ] Both parent AND child metadata (40 fields total)

2. If it has both, are they:
   - [ ] Different values/information
   - [ ] The same information, just repeated
   - [ ] Parent is derived/extracted from child

---

### Question 4: Who decides what's a parent?

**When a researcher uploads their dataset, who decides which measurements are "parents"?**

- [ ] Researcher explicitly marks their parent choice
- [ ] GHFDB team reviews and assigns parent status later
- [ ] Automatic based on quality/depth rules
- [ ] Other: _______________________

---

### Question 5: Are parent and child the same "thing"?

**In your mental model, are parent and child:**

- [ ] **Option A:** Fundamentally different types of data
  - Parent = summary/representative (minimal metadata)
  - Child = detailed measurement (full metadata)
  - They live in separate parts of the system

- [ ] **Option B:** Same type of data with different roles
  - Both are measurements with the same metadata
  - "Parent" just means "currently selected as representative"
  - It's a designation, not a different data type

---

## Why These Answers Matter

Your answers will determine:

1. **Database design:** 1 table or 2 tables?
2. **What "conversion" means:** Change entity type or change flag?
3. **Data migration:** Can Excel data be imported without loss?
4. **Researcher workflow:** Can they submit their own parents?

---

## Next Steps

**Proposed meeting agenda:**

1. Open your Excel spreadsheet together
2. Walk through a real "conversion" scenario step-by-step
3. Answer the 5 questions above
4. Document the decisions
5. I'll design the database accordingly

**Duration:** 1-2 hours

---

## Contact

**Document Owner:** Sam Jennings (Development Team)
**Last Updated:** January 12, 2026

**To schedule the clarification meeting:** Contact project management
