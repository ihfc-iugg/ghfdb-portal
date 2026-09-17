# Feature Specification: Upload a completed assessment template through the portal

**Feature Branch**: `005-assessment-upload-workflow`

**Created**: 2026-09-15

**Status**: Draft

**Goals**: G4 (the assessment team can add datasets one at a time), with G5 behind it

**Roadmap**: R6, the page the team uploads through. Takes on the role, the private-until-approved
rule and the approval step from R7.

**Issue**: #209

**Input**: A member of the data assessment team uploads one completed GHFDB upload template at a
time through the portal's own pages. Before choosing a file they record the publication the dataset
belongs to, the people who carried out the assessment, the dates, and an optional title. The file is
always checked before anything is written, failures are reported in the spreadsheet's own terms, and
nothing is written until the uploader confirms. A Data Curator's upload is public immediately. A
Data Assessor's upload stays private until a Data Curator approves it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The assessments are visible, and the team can add to them (Priority: P1)

Anyone can see what the assessment team has been working on: an entry in the site navigation leading
to a list of the assessments, each showing the publication it covers and where it has got to, and
each opening onto the assessment's own page. The list can be narrowed to the assessments a reader
cares about — by state, by who assessed or uploaded them, by who decided on them. A member of the
team additionally finds a route to start a new one, which nobody else sees.

**Why this priority**: it is the entry point. Without it every other story is reachable only by
typing a URL, and the roles that gate the rest of the feature are defined here. The filters are what
let one list serve a reader looking for a publication and a curator looking for work waiting on
them, which is why there is no second listing page.

**Independent Test**: browse the portal as an anonymous visitor and confirm the navigation entry
appears and the list it leads to renders, narrow it by state and by assessor and confirm only
matching assessments remain, then sign in as a member of the team and confirm the route to start a
new assessment appears, and that it does not for a signed-in user outside the team.

**Acceptance Scenarios**:

1. **Given** an anonymous visitor, **When** any portal page renders, **Then** the assessment entry
   appears in the site navigation, and the list it leads to shows each assessment's publication and
   the state it has reached.
2. **Given** a signed-in Data Assessor, **When** the list renders, **Then** it carries a visible
   route to start a new assessment.
3. **Given** a signed-in Data Curator, **When** any portal page renders, **Then** the navigation
   entry carries the number of assessments awaiting a decision, and leads to the list already
   narrowed to those.
4. **Given** a visitor in neither role, signed in or not, **When** the list renders, **Then** the
   route to start a new assessment is absent, and requesting the create page's URL directly is
   refused.
5. **Given** a Data Assessor with two assessments in different states, **When** the list renders,
   **Then** each row names the publication it covers, who uploaded it, and the state it has reached,
   and links to that assessment's own page.
6. **Given** assessments in several states by several people, **When** the reader narrows the list by
   state, by assessor, by uploader or by who decided, **Then** only the assessments matching every
   chosen filter remain, and the narrowing survives being shared as a link.

---

### User Story 2 - An assessment is described before a file is chosen (Priority: P1)

Starting a new assessment asks for what the data is before it asks for the data. The uploader names
the publication the dataset comes from, picking it out of the portal's literature catalogue or
adding it from a bibliography file when it is not there yet. They name the people who carried out
the assessment, give the dates the work ran between, and may give the dataset a title. Leaving the
title blank takes the publication's own title.

**Why this priority**: the assessment record is what the file is later attached to, and the template
carries no trustworthy version of any of it. The team's own template has reviewer columns, and this
form is what replaces them.

**Independent Test**: complete the form for a publication already in the catalogue and confirm an
assessment record exists, carrying its publication, its assessors and its dates, with a dataset that
holds no data yet.

**Acceptance Scenarios**:

1. **Given** a publication already in the catalogue, **When** the form is completed and submitted,
   **Then** an assessment record exists linking that publication to a new dataset that holds no
   data, and the record carries the named assessors and dates.
2. **Given** a publication absent from the catalogue, **When** its bibliography file is supplied
   through the same form, **Then** the publication is added to the catalogue and the assessment
   links to it without the uploader leaving the form.
3. **Given** the title field left blank, **When** the form is submitted, **Then** the dataset takes
   the publication's own title.
4. **Given** a publication that already has an assessment, **When** the form names it again,
   **Then** it is refused, naming the existing assessment, because one publication is one dataset.
5. **Given** a person who contributes to the portal but has never signed in, **When** they are named
   as an assessor, **Then** they are accepted, because assessors are contributors rather than
   necessarily account holders.
6. **Given** an end date earlier than the start date, **When** the form is submitted, **Then** it is
   refused with the dates named.

---

### User Story 3 - A file is checked before anything is written (Priority: P1)

With the assessment described, the uploader chooses their completed template. The portal reads it
and reports what importing it would do, without having written anything. Nothing reaches the
database until the uploader has seen that report and confirmed it.

**Why this priority**: it is the safety property the whole workflow rests on, and the one the team
asked for by name. An import that writes first and reports afterwards cannot be undone by anyone
without database access.

**Independent Test**: upload a valid file against an empty assessment, confirm the report names what
would be created, and confirm the database is unchanged until confirmation is given.

**Acceptance Scenarios**:

1. **Given** a valid completed template, **When** it is uploaded, **Then** a report names how many
   sites and how many determinations would be created, and how many existing records would be
   updated.
2. **Given** that report on screen, **When** the database is inspected, **Then** the assessment's
   dataset still holds no data.
3. **Given** that report on screen, **When** the uploader abandons the page rather than confirming,
   **Then** the assessment's dataset still holds no data and the assessment can be resumed with a
   different file.
4. **Given** the check has run, **When** the uploader confirms, **Then** the data is written and the
   counts written match the counts reported.
5. **Given** any route into the upload, **When** it is used, **Then** the check runs. There is no
   setting, parameter or URL that writes without checking first.
6. **Given** a confirmation already accepted, **When** the same confirmation is submitted again by a
   refresh or a second click, **Then** the data is not written twice.

---

### User Story 4 - A file that fails is explained in the spreadsheet's own terms (Priority: P1)

When the file cannot be imported, the uploader is told what to fix in the language of the
spreadsheet in front of them. Every failure names the row and the column heading as the template
spells it, and says what specifically is wrong. They correct the file and upload it again against
the same assessment, as many times as it takes.

**Why this priority**: the team includes student helpers and people passing through, and a message
they cannot act on sends the problem to whoever maintains the portal. This is the difference between
the feature working and the feature generating support requests.

**Independent Test**: upload a file carrying a value outside a controlled vocabulary and confirm the
message names the row, the template's own column heading, the offending value and the vocabulary it
failed against.

**Acceptance Scenarios**:

1. **Given** a file with a value outside a controlled vocabulary, **When** it is checked, **Then**
   the failure names the row, the template's column heading, the supplied value and the vocabulary
   it was checked against. A message saying only that a value is unacceptable does not satisfy this.
2. **Given** a file with several distinct failures, **When** it is checked, **Then** all of them are
   reported together rather than only the first.
3. **Given** a file whose header row is not the official template's, **When** it is checked, **Then**
   it is refused on the header, no row-level failures are reported, and the message says the
   template is not the expected one.
4. **Given** a failing file, **When** the uploader corrects it and uploads again against the same
   assessment, **Then** the new file is checked afresh and the previous failures do not persist.
5. **Given** a failure report, **When** it is read, **Then** no internal field name, model name or
   traceback appears in it.

---

### User Story 5 - Confirming writes the data and decides who can see it (Priority: P1)

Confirming the report writes the data into the assessment's dataset and keeps the submitted file
against the assessment record, so the dataset can always be traced back to the spreadsheet it came
from. Where the uploader is a Data Curator the dataset is public from that moment. Where the
uploader is a Data Assessor it stays private.

**Why this priority**: it completes the upload, and it is where the trust distinction between the
two roles takes effect.

**Independent Test**: confirm an import as each role in turn and check the resulting dataset's
visibility, then check that the submitted file is retrievable from the assessment record in both
cases.

**Acceptance Scenarios**:

1. **Given** a checked file and a Data Assessor uploading it, **When** they confirm, **Then** the
   data is written, the dataset is not visible to the public, and the assessment is waiting on a
   decision.
2. **Given** a checked file and a Data Curator uploading it, **When** they confirm, **Then** the
   data is written and the dataset is public without waiting for anyone.
3. **Given** a confirmed import, **When** the assessment record is read, **Then** the submitted file
   is retrievable from it.
4. **Given** an assessment whose file was sent back and replaced, **When** the record is read,
   **Then** the earlier submitted file is still retrievable and is distinguishable from the current
   one.
5. **Given** a confirmed import, **When** the assessors named at the outset are read back from the
   dataset, **Then** each is credited as a contributor to it.
6. **Given** a template whose reviewer columns are filled in, **When** it is confirmed, **Then**
   nothing from those columns is stored and the assessment's own assessors stand unchanged.

---

### User Story 6 - A curator decides on an assessor's upload (Priority: P2)

An upload from a Data Assessor waits for a Data Curator. A curator narrows the list to what is
waiting, opens one, and from its page either approves it, which makes the dataset public, or sends
it back with a note saying what is wrong. A sent-back assessment returns to its uploader, who can
replace the file and submit it again.

**Why this priority**: the workflow is usable without it, because a curator can upload directly and
an assessor's work is safely private in the meantime. It is the second half of the trust model
rather than a precondition for the first.

**Independent Test**: upload as an assessor, approve as a curator from the assessment's page, and
confirm the dataset becomes public and the decision and its maker are recorded on the assessment.

**Acceptance Scenarios**:

1. **Given** an assessment waiting on a decision, **When** a Data Curator narrows the list to what is
   waiting, **Then** it appears there, naming its publication and who uploaded it.
2. **Given** a waiting assessment, **When** a curator approves it from its page, **Then** the dataset
   becomes public and the assessment records the decision, who made it and when.
3. **Given** a waiting assessment, **When** a curator sends it back with a note, **Then** the dataset
   stays private, the note reaches the uploader, and the assessment is open for a replacement file.
4. **Given** a sent-back assessment, **When** its uploader supplies a corrected file, **Then** it is
   checked and confirmed as before and returns to waiting on a decision.
5. **Given** a Data Assessor, **When** they attempt to approve any assessment including their own,
   **Then** it is refused.
6. **Given** an assessment that becomes ready for a decision, **When** it enters that state,
   **Then** the Data Curators are notified within the portal.

---

### User Story 7 - An assessment has a page of its own (Priority: P1)

Every assessment has one page that shows what it covers, who is working on it, where it has got to,
and what has been submitted against it. It is where the assessment's related records are reached —
its publication, its dataset — and where whoever may act on it finds the routes to do so: a Data
Assessor to correct its description or supply a file, a Data Curator to decide on it.

**Why this priority**: without it the assessment is only ever a row in a list and a file upload
form, with no place to see what was submitted, what a curator said, or where the data went. It is
also what removes the need for a separate waiting-list page, since the decision is made here.

**Independent Test**: open an assessment's page as an anonymous visitor and confirm it describes the
assessment without offering any action, then open the same page as its uploader and as a curator and
confirm each is offered only the routes their role allows.

**Acceptance Scenarios**:

1. **Given** any assessment, **When** anyone opens its page, **Then** it names the publication, the
   assessors, the uploader, the dates, the state it has reached, and links to the publication and to
   the dataset.
2. **Given** an assessment with submitted files, **When** its page renders, **Then** the submissions
   appear most recent first, each showing who submitted it and when, and whether it was written.
3. **Given** an assessment sent back for changes, **When** its page renders, **Then** the curator's
   note appears on it.
4. **Given** an assessment whose uploader is signed in, **When** its page renders, **Then** it offers
   the routes to correct the description and to supply a file.
5. **Given** an assessment waiting on a decision and a signed-in Data Curator, **When** its page
   renders, **Then** it offers approving and sending back, and neither appears for anyone else or in
   any other state.
6. **Given** a signed-in visitor in neither role, **When** they open any assessment's page, **Then**
   it renders and offers no action at all.

---

### Edge Cases

- A file that is checked cleanly, followed by a confirmation arriving after the underlying data has
  changed: the counts reported and the counts written disagree. The confirmation re-checks rather
  than trusting the earlier report.
- A confirmation submitted twice, by a double click or a page refresh, must not import twice.
- A file that is not a spreadsheet at all, or an empty one.
- An assessment abandoned after the description step and never given a file: it remains in the
  uploader's list and its dataset holds nothing.
- A publication added from a bibliography file that turns out to be a duplicate of one already in
  the catalogue.
- A Data Assessor who is later made a Data Curator while an assessment of theirs is waiting.
- An assessor named on the form who is later removed from the portal.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The portal MUST offer everyone an entry in the site navigation leading to the list of
  assessments, and MUST show that list to anyone. It MUST offer members of the assessment team a
  route to start a new assessment, which is neither shown nor served to anyone else.
- **FR-002**: The portal MUST list existing assessments with the publication each covers, who
  uploaded it and the state it has reached, each linking to that assessment's own page.
- **FR-003**: The portal MUST collect the publication, the assessors, the start and end dates, and
  an optional title before any file is chosen.
- **FR-004**: The portal MUST let the uploader find a publication already in its literature
  catalogue, and MUST let them add one from a bibliography file without leaving the form.
- **FR-005**: The portal MUST default a dataset's title to its publication's title when none is
  given.
- **FR-006**: The portal MUST accept as an assessor any person holding a contributor profile,
  whether or not they hold a portal account.
- **FR-007**: The portal MUST refuse a second assessment against a publication that already has one.
- **FR-008**: The portal MUST check every uploaded file and report the outcome before writing
  anything, with no route that writes without checking.
- **FR-009**: The portal MUST report, for a file that passes, the number of sites and determinations
  that would be created and the number of existing records that would be updated.
- **FR-010**: The portal MUST leave the dataset unchanged until the uploader confirms.
- **FR-011**: The portal MUST report every failure in a file, not only the first.
- **FR-012**: The portal MUST identify each failure by the row and by the column heading as the
  official template spells it, and MUST state the specific reason, naming the supplied value and the
  controlled vocabulary where a vocabulary is at fault.
- **FR-013**: The portal MUST NOT expose internal field names, model names or tracebacks in a
  failure report.
- **FR-014**: The portal MUST allow a corrected file to be uploaded against the same assessment,
  repeatedly.
- **FR-015**: The portal MUST retain every submitted file against its assessment record, including
  files superseded by a later submission.
- **FR-016**: The portal MUST credit the named assessors as contributors to the resulting dataset.
- **FR-017**: The portal MUST make a dataset public on confirmation when the uploader is a Data
  Curator.
- **FR-018**: The portal MUST keep a dataset private on confirmation when the uploader is a Data
  Assessor, and leave the assessment waiting on a decision.
- **FR-019**: The portal MUST let a Data Curator approve a waiting assessment from its own page,
  making its dataset public, and MUST record the decision, its maker and its date on the assessment.
- **FR-020**: The portal MUST let a Data Curator send a waiting assessment back with a note, leaving
  the dataset private and the assessment open for a replacement file.
- **FR-021**: The portal MUST refuse an approval from anyone who is not a Data Curator.
- **FR-022**: The portal MUST notify Data Curators within the portal when an assessment becomes
  ready for a decision, and that notice MUST lead to the assessments waiting on them.
- **FR-023**: The portal MUST ignore the reviewer columns present in the upload template, taking
  that information from the assessment record instead.
- **FR-024**: A confirmation MUST be safe to submit more than once without importing twice.
- **FR-025**: The portal MUST let a reader narrow the list by state, by assessor, by uploader and by
  the curator who decided, in any combination, and MUST carry that narrowing in the address so a
  narrowed list can be shared and returned to.
- **FR-026**: The portal MUST let a reader search the list by the title of the publication a row
  covers.
- **FR-027**: The portal MUST give every assessment a page of its own, showing to anyone the
  publication, the assessors, the uploader, the dates, the state, the submitted files with who
  supplied each and when, and links to the publication and the dataset.
- **FR-028**: The portal MUST show on that page the note a curator left when sending the assessment
  back, while it is open for a replacement file.
- **FR-029**: The portal MUST offer on that page, and only to whoever may use them, the routes to
  correct the assessment's description, to supply a file, and to decide on it. A route MUST NOT be
  drawn for a reader who may not follow it, and the page it leads to MUST refuse them in its own
  right.
- **FR-030**: The portal MUST let whoever may upload against an assessment correct the description
  it was created with.

### Key Entities *(include if feature involves data)*

- **Assessment**: the record of one publication being turned into one dataset. Carries the
  publication, the dataset, the assessors, the dates, the submitted files, the state it has reached,
  and the decision made on it. The existing `Review` model in the `review` application is this
  record.
- **Data Assessor**: a portal user who may create assessments and upload files. Their uploads wait
  for a decision.
- **Data Curator**: a portal user who may do everything an assessor may, and additionally decide on
  waiting assessments. Their own uploads do not wait.
- **Submitted file**: a completed upload template as supplied, kept against its assessment.
- **Assessment state**: where an assessment has got to, from described but not yet uploaded, through
  waiting on a decision, to decided.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A member of the assessment team can take a completed template from their desktop to a
  dataset in the portal without opening the Django admin and without help from a maintainer.
- **SC-002**: No file can enter the portal without having been checked and confirmed first. Every
  route into the import is covered by a test proving it.
- **SC-003**: Every failure a checked file produces names a row, a column heading as the template
  spells it, and a reason specific enough to act on. A report containing a bare "invalid value" is a
  failing test.
- **SC-004**: A dataset uploaded by a Data Assessor is invisible to an anonymous visitor until a
  Data Curator has approved it.
- **SC-005**: Every dataset created through this workflow can be traced back to the exact file it
  was built from, including datasets whose first submitted file was rejected.
- **SC-006**: The `review` application, which has no tests at all today, has pytest coverage for
  every behaviour this feature adds or changes, in a test tree mirroring `project/review/`. The
  constitution treats coverage as a guide rather than a merge gate, so the obligation is that each
  behaviour is tested, not that a percentage is reached.

## Assumptions

- The reader delivered by FS-004 is the engine. This feature builds the pages around it and adds a
  checking mode to it. It does not change how the template is read, which columns exist, or how
  vocabulary values resolve.
- One publication is one dataset, as CONTEXT.md states and as the existing model enforces.
- Data Curator replaces the glossary's "data administrator", and Data Assessor replaces its
  "Reviewer". CONTEXT.md is updated in this feature rather than left describing vocabulary the code
  no longer uses.
- Notification means a notification inside the portal. Email is out of scope.
- The roles are group membership, not per-person flags. A portal user is a Data Assessor, a Data
  Curator, or neither.
- Datasets already in the portal, created before this workflow existed, are not migrated into it.

## Clarifications

### Session 2026-09-15

- **Q**: When a Data Curator sends an assessment back, what happens to the data already imported
  from the rejected file? **A**: it stays, and the replacement file is imported over it in the same
  way a re-import behaves elsewhere. Removing it would mean a deletion path that exists nowhere else
  in the portal, and the dataset is private throughout, so nothing incorrect is visible. Recorded in
  US-6 scenario 4.
- **Q**: Does the check report distinguish records that would be created from records that would be
  updated? **A**: yes. Re-importing a corrected file over a private dataset is the expected path
  after a send-back, and a report that counts only totals would tell the uploader nothing about
  whether their correction landed. FR-009.
- **Q**: Can an assessment be started for a publication with no bibliography record at all, neither
  in the catalogue nor in a file? **A**: no. The publication link is what makes the dataset findable
  and is the one thing the template cannot supply, so it is required. US-2 scenario 2 gives the
  route for a publication that is merely absent.
- **Q**: Who may see an assessment that is not theirs? **A**: anyone may see that it exists, what
  state it is in and what has been submitted against it, and only Data Curators may act on one they
  did not upload. US-1 scenario 5, US-7 scenario 6.
- **Q**: Is the check's report tied to the file that produced it? **A**: yes, and the confirmation
  re-runs the check rather than trusting the stored report, which is what makes FR-024 and the
  stale-report edge case safe.

### Session 2026-09-17

- **Q**: Does the waiting list need a page of its own? **A**: no. It is the assessment list narrowed
  to one state, so it is a filter rather than a page, and the filters US-1 now carries cover it along
  with every other question a reader asks of the list. The curator's count in the navigation leads to
  the narrowed list. FR-022, FR-025.
- **Q**: Where is an assessment decided on? **A**: on its own page, which is also where its
  submissions, its publication and its dataset are reached. US-7, FR-019, FR-027.
- **Q**: Does supplying a file move onto that page too? **A**: no. Uploading is a step with its own
  report and confirmation, and folding it into the page that describes the assessment would put two
  unrelated states on one screen. The page links to it. FR-029.
- **Q**: Do assessors and curators discuss an assessment on its page? **A**: not in this feature.
  Threaded comments are worth having and the portal already carries a commenting system, but how it
  attaches here has details to settle first, so the only text an assessment carries remains the note
  a curator leaves when sending it back. FR-028.

## Dependencies and risks

- **The distributed upload template is refused by ADR 0003.** Both misspelled column headings
  (`tc_pT_fuction`, `Ref_ISGN`) are still present in the template the team fills in today, and the
  reader refuses a file carrying either on its header before reading a row. This feature ships the
  refusal intact, with a message naming the template as outdated. Until the template is corrected
  upstream, no real file passes these pages. The correction is outside this feature and has to be
  chased alongside it.
- `Person.is_data_admin` in the framework is fixed to a group named "Data Administrators", and the
  framework's own import and publication views gate on it. Naming the portal's group differently
  without addressing that would silently disable those gates.
- The `review` application has no tests today, so this feature carries the cost of establishing its
  test structure as well as covering its own work.
