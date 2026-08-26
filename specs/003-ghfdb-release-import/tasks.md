# Tasks — 003 a published release read into the portal

Written from `spec.md`, `research.md` and `decisions.md` as though the repository held no
implementation of this feature. Nothing here was derived by reading the existing resources, widgets,
formats or their tests. Two things were read and are treated as authorities rather than as
implementations: the published column definitions, which are the canonical data definition, and the
`heat_flow` models, which this feature reads into and does not own.

Writing the list this way is deliberate. A task list written by reading the implementation can only
describe the implementation, which is how a specification audit turns into a rubber stamp. The
difference between this list and what the repository holds is the measurement the exercise exists to
produce.

Tests come before the implementation they cover, per constitution principle VI. Every task is one
increment. Every implementation task names the test that proves it and the assertion that fails
before it exists.

The list was written with every box unchecked, including for behaviour the repository may already
have. It was then walked against the code, and a task was ticked only where both a code citation and
a passing test that genuinely exercises it could be given. Eight of the 114 closed that way; each
carries the evidence it closed on. [reconciliation.md](reconciliation.md) records the split, and the
six proposed closures that did not survive review.

**Removed at design review**: T010 and T094 to T096 asked for behaviour the approved specification
does not require — a readable name for the reading format, and the order of the columns on the
confirmation page. Their ids are not reused. T115 was added in the same pass, for SC-007.

**Names used below.** The reading format, the resource and the release column definitions live in
`project/ghfdb/`. Tests mirror that tree under `tests/test_ghfdb/`, per `tests/README.md`.

---

## Phase 1 — Foundations

Blocking. Every story depends on these.

- [ ] **T001** *foundations* — A test module for the release import mirroring the source tree, with
  the `ghfdb` marker, alongside the existing test package.
  **Test**: `pytest --collect-only` names the module. Before: collection reports nothing.

- [ ] **T002** *foundations* — The release format's column definitions: the ordered list of every
  column name a release file carries, held in the same module as the published parent and
  determination columns and derived from them rather than restated, plus the names a release adds —
  the two identifiers, the publication year, the quality code, the geography columns and the
  assessment columns.
  **Test**: the release list begins with the published parent columns in order and contains every
  published determination column exactly once. Before: the name does not resolve.

- [ ] **T003** *foundations* — The definition of which released columns are read, which are
  recognised and discarded, and which are refused, expressed as data rather than as behaviour
  scattered through the reader. FR-007 requires one place both the header check and the row reading
  consult.
  **Test**: the three sets are disjoint and their union is the release column list. Before: no such
  definition exists.

- [ ] **T004** *foundations* — A test fixture cut from the published release file: a small number of
  whole rows copied byte-for-byte from `assets/ghfdb/IHFC_2024_GHFDB.zip`, keeping the real header
  line, the real column order and the byte-order mark. It must include rows sharing a site, rows
  sharing an interval, rows with no depth, rows from more than one publication and at least one
  `[Unspecified]` value.
  **Test**: the fixture's header equals the release file's header, read from the archive. Before:
  the fixture does not exist.
  **Note**: the fixture is cut from the real file on purpose. A hand-built one that matches the
  reader proves nothing about the format, which is how the gap this feature exists to close stayed
  invisible.

- [ ] **T005** *foundations* — Fixture variants derived from T004 by a single deliberate change
  each: one variant per misspelled published header (there are two), an undefined header, a
  missing required header, a bad
  vocabulary value, a numeric value in a text column, two rows disagreeing about a shared site, and
  two rows disagreeing about a shared interval's probe.
  **Test**: each variant differs from the base fixture in exactly the intended cell or header.
  Before: the variants do not exist.

- [x] **T006** *foundations* — Factories for every model a row produces, one per model, so tests can
  state a starting condition without building a graph by hand.
  **Test**: each factory produces a saved instance whose required fields are populated. Before: the
  factories do not resolve.
  **Closed on**: project/heat_flow/factories.py:33 · tests/test_heat_flow/test_factories.py:39

- [ ] **T007** *foundations* — A fixture giving a bibliographic record with a known citation key, and
  one giving two records sharing a citation key, since the portal's citation keys are not unique.
  **Test**: the second fixture yields two records for one lookup. Before: the fixtures do not exist.

---

## Phase 2 — US-1, a release file is checked in full before anything is written

- [ ] **T008** *US-1* — Test: a release file whose header is the real one passes the column check and
  its values are read.
  **Fails before**: no reader exists.

- [ ] **T009** *US-1* — The reading format: a comma-separated reader carrying a name a curator can
  recognise in the format list, reading the header from the first line and the data from the second.
  **Test**: T008.

- [ ] **T011** *US-1* — Test: a file carrying a misspelled published column name is refused, the
  error names the misspelled name, the correct name and the outdated template, and no record of any
  kind is created. Asserted separately for each of the two misspelled names the published format
  contains, per SC-001, so that a check keyed to one cannot leave the other unrefused.
  **Fails before**: nothing checks headers.
  **Note**: this refusal is required without exception, including for the published release, which
  carries both misspelled names. See D7.

- [ ] **T012** *US-1* — The misspelled-name check.
  **Test**: T011.

- [ ] **T013** *US-1* — Test: a file carrying a column name the release format does not define is
  refused with that column named.
  **Fails before**: an unknown column is ignored per row.

- [ ] **T014** *US-1* — The undefined-name check.
  **Test**: T013.

- [ ] **T015** *US-1* — Test: a file missing a column the release format requires is refused with
  that column named.
  **Fails before**: a missing column is silently skipped for every row.

- [ ] **T016** *US-1* — The missing-column check.
  **Test**: T015.

- [ ] **T017** *US-1* — Test: after a header refusal, no data row was read at all — proven by a row
  that would itself have raised, which produces no second error.
  **Fails before**: recording a header fault does not stop the row loop, so every row is still read.
  **Note**: the library offers no hook that aborts before the first row. See R3.

- [ ] **T018** *US-1* — Emptying the dataset when the header check fails, so the rows are genuinely
  not read.
  **Test**: T017.

- [ ] **T019** *US-1* — Test: a file whose header is correct but whose rows carry faults in several
  different rows reports every fault, not the first.
  **Fails before**: no reader exists.

- [ ] **T020** *US-1* — Test: a reported fault carries the row number as it appears in the file,
  counting the header line, so a fault in the first data row reports as line 2.
  **Fails before**: the library reports data-row position, which is one less.

- [ ] **T021** *US-1* — Reporting the file's line number rather than the data-row position.
  **Test**: T020.

- [ ] **T022** *US-1* — Test: a reported fault names the column as it appears in the header, not the
  model attribute the value would have been stored in.
  **Fails before**: the field name in a report is the model attribute.

- [ ] **T023** *US-1* — Naming the column in the fault, for every column that can refuse a value.
  **Test**: T022.

- [ ] **T024** *US-1* — Test: a reported fault carries the offending value and a reason that
  distinguishes it from other reasons.
  **Fails before**: no reader exists.

- [x] **T031** *US-1* — Test: a staff user without permission to add records cannot reach the import,
  and one with it can.
  **Fails before**: the route does not exist.
  **Closed on**: project/ghfdb/admin.py:197 · tests/test_ghfdb/test_admin.py:908

- [x] **T032** *US-1* — Permission gating on the import route.
  **Test**: T031.
  **Closed on**: project/ghfdb/admin.py:197 · tests/test_ghfdb/test_admin.py:916

- [ ] **T033** *US-1* — Test: an anonymous request to the import route is refused, distinguishably
  from a request that merely redirects to a login page for any administrative address.
  **Fails before**: the route does not exist.

---

## Phase 3 — US-2, the release lands as one dataset for each publication

- [ ] **T034** *US-2* — Test: a file whose rows carry several distinct publication references
  produces one dataset per reference, and no dataset holds records from two.
  **Fails before**: no dataset is created by reading a file.

- [ ] **T035** *US-2* — Collecting the file's distinct publication references once, before any row is
  read.
  **Test**: T034.

- [ ] **T036** *US-2* — Creating one dataset per distinct reference.
  **Test**: T034.

- [ ] **T037** *US-2* — Test: two references differing only by case or by surrounding whitespace are
  one reference, and produce one dataset.
  **Fails before**: they produce two.

- [ ] **T038** *US-2* — Comparing references ignoring case and surrounding whitespace.
  **Test**: T037.

- [ ] **T039** *US-2* — Test: a reference matching exactly one bibliographic record gives its dataset
  that record's title, and links the two.
  **Fails before**: no bibliographic record is consulted.

- [ ] **T040** *US-2* — Matching a reference to a bibliographic record and taking its title.
  **Test**: T039.

- [ ] **T041** *US-2* — Test: a reference matching no bibliographic record creates one carrying that
  citation key, and the dataset links to it.
  **Fails before**: nothing is created.

- [ ] **T042** *US-2* — Creating a bibliographic record from a citation key alone.
  **Test**: T041.

- [ ] **T043** *US-2* — Test: a reference matching more than one bibliographic record refuses the
  rows carrying it, naming the reference and the records it matched, and creates neither a dataset
  nor a record.
  **Fails before**: the first match is taken.
  **Note**: citation keys are documented as not unique, so this is reachable rather than defensive.

- [ ] **T044** *US-2* — Refusing an ambiguous reference.
  **Test**: T043.

- [ ] **T045** *US-2* — Test: a row whose publication reference is empty is refused.
  **Fails before**: it is filed under a default.

- [ ] **T046** *US-2* — Refusing an empty reference.
  **Test**: T045.

- [ ] **T047** *US-2* — Test: the publication reference a dataset was created from can be read back
  off the dataset, rather than recovered by inspecting its records.
  **Fails before**: it is not stored.

- [ ] **T048** *US-2* — Storing the reference on the dataset.
  **Test**: T047.

- [ ] **T049** *US-2* — Test: a file whose references already have datasets from an earlier import
  reuses them and creates no duplicates.
  **Fails before**: a second set is created.

- [ ] **T050** *US-2* — Test: nothing created while checking a file survives the check — a dataset
  the check would have made does not exist afterwards.
  **Fails before**: the resolution runs once and its result is carried into the write.
  **Note**: the check and the write are separate passes over separate objects. Nothing may carry an
  identifier from one to the other. See R4.

---

## Phase 4 — US-3, every row becomes the records the portal keeps

- [ ] **T051** *US-3* — Test: one row produces a site, an interval, a determination, and the gradient
  and conductivity measured over that interval, related as the model defines.
  **Fails before**: no reader exists.

- [ ] **T052** *US-3* — Reading a row into the site.
  **Test**: T051.

- [ ] **T053** *US-3* — Reading a row into the interval.
  **Test**: T051.

- [ ] **T054** *US-3* — Reading a row into the determination.
  **Test**: T051.

- [ ] **T055** *US-3* — Reading a row into the gradient and the conductivity.
  **Test**: T051.

- [ ] **T056** *US-3* — Test: several rows sharing a published site identifier produce one site
  carrying every determination.
  **Fails before**: each row makes its own site.

- [ ] **T057** *US-3* — Identifying a site by its published site identifier.
  **Test**: T056.

- [ ] **T058** *US-3* — Test: the site's parent heat flow value is created once per site and not once per
  row.
  **Fails before**: it is created per row.

- [ ] **T059** *US-3* — Test: several rows giving one site and one depth range produce one interval
  carrying all of their determinations, each with its own gradient and conductivity.
  **Fails before**: each row makes its own interval.
  **Note**: an interval is a sample in its own right and can be measured again by someone else. See
  D15.

- [ ] **T060** *US-3* — Identifying an interval by its site and the depth range the row gives.
  **Test**: T059.

- [ ] **T061** *US-3* — Test: several rows giving one site and no depth range at all attach to one
  indeterminate interval for that site.
  **Fails before**: they produce one interval per row, or collapse into an interval with a depth.

- [ ] **T062** *US-3* — The indeterminate interval, one per site.
  **Test**: T061.

- [ ] **T063** *US-3* — Test: a site with rows giving a depth range and rows giving none holds an
  interval for each distinct range plus the one indeterminate interval, and they are distinct.
  **Fails before**: they are merged.

- [ ] **T064** *US-3* — Test: the gradient and the conductivity a row reports are identified by that
  row's determination identifier, so two determinations over one interval have their own.
  **Fails before**: the second row finds the first row's gradient and updates it.
  **Note**: the file records no way to recognise two rows as reporting one measurement, and matching
  on the value is the proximity matching the standing constraints rule out. See D16.

- [ ] **T065** *US-3* — Identifying the gradient and the conductivity by the determination.
  **Test**: T064.

- [ ] **T066** *US-3* — Test: a row supplying some corrections and not others produces a correction
  record for each supplied and none for the rest.
  **Fails before**: a record is created for every correction type regardless.

- [ ] **T067** *US-3* — Creating a correction only where the row supplies one.
  **Test**: T066.

- [ ] **T068** *US-3* — Test: a correction flag that is bracketed or differently cased is read, not
  lost.
  **Fails before**: it falls through to an unspecified value.

- [ ] **T069** *US-3* — Normalising a correction flag the same way as any other vocabulary value.
  **Test**: T068.

- [ ] **T070** *US-3* — Test: probe metadata is created once for an interval, and a row supplying
  none creates none.
  **Fails before**: it is created per row, or created empty.

- [ ] **T071** *US-3* — Probe metadata belonging to the interval. The relationship already exists on
  the model as a one-to-one field and needs no change; what this task delivers is the release
  reader creating at most one record per interval and none for a row that supplies no probe
  columns.
  **Test**: T070.
- [ ] **T072** *US-3* — Test: two rows sharing an interval but disagreeing about the probe that
  sampled it are refused, and the disagreement is reported.
  **Fails before**: the second row overwrites the first, or fails in a way that names nothing.
  **Note**: 974 shared intervals in the current release disagree this way. Ordinary, not remote.

- [ ] **T073** *US-3* — Refusing a disagreement about a shared interval.
  **Test**: T072.

- [ ] **T074** *US-3* — Test: two rows sharing a published site identifier but disagreeing about that
  site's own columns are refused, and the disagreement is reported.
  **Fails before**: one row's values win silently.

- [ ] **T075** *US-3* — Refusing a disagreement about a shared site.
  **Test**: T074.

- [ ] **T076** *US-3* — Test: a cell holding the published absent-value marker is read as no value,
  and creates no record the row did not describe.
  **Fails before**: it is refused as a non-numeric value in a numeric column.

- [ ] **T077** *US-3* — Reading the absent-value marker as no value.
  **Test**: T076.

- [x] **T078** *US-3* — Test: a vocabulary value that is bracketed, differently cased, or both is
  matched to its term.
  **Fails before**: it matches nothing.
  **Closed on**: project/ghfdb/resources/widgets.py:53 · tests/test_ghfdb/test_resources/test_widgets.py:487

- [x] **T079** *US-3* — Normalising a vocabulary value before matching.
  **Test**: T078.
  **Closed on**: project/ghfdb/resources/widgets.py:53 · tests/test_ghfdb/test_resources/test_widgets.py:475

- [x] **T080** *US-3* — Test: a vocabulary value matching no term is refused and reported, for a
  column holding one value.
  **Fails before**: it is stored or dropped.
  **Closed on**: project/ghfdb/resources/widgets.py:98 · tests/test_ghfdb/test_resources/test_widgets.py:507

- [x] **T081** *US-3* — Test: a vocabulary value matching no term is refused and reported, for a
  column holding several values.
  **Fails before**: the failure is caught and discarded, and the row imports with the relation empty.
  **Note**: most of a release's vocabulary surface is many-valued, so discarding these discards most
  of the checking this feature exists to do.
  **Closed on**: project/ghfdb/resources/widgets.py:292 · project/ghfdb/resources/widgets.py:350 ·
  tests/test_ghfdb/test_resources/test_release.py:1054

- [x] **T082** *US-3* — Refusing a vocabulary failure on a many-valued column.
  **Test**: T081.
  **Closed on**: project/ghfdb/resources/widgets.py:69 · project/ghfdb/resources/widgets.py:346 ·
  tests/test_ghfdb/test_resources/test_release.py:1054

- [x] **T083** *US-3* — Test: a numeric value reaching a column that holds text is refused with the
  column and the value named, rather than failing in a way that names neither.
  **Fails before**: it fails without naming the column.
  **Closed on**: project/ghfdb/resources/widgets.py:292 · project/ghfdb/resources/release.py:440 ·
  tests/test_ghfdb/test_resources/test_release.py:1082

- [x] **T084** *US-3* — Test: a text value reaching a column that holds a quantity is refused with
  the column and the value named.
  **Fails before**: it fails without naming the column.
  **Closed on**: project/ghfdb/resources/widgets.py:292 · project/ghfdb/resources/release.py:440 ·
  tests/test_ghfdb/test_resources/test_release.py:1082

- [x] **T085** *US-3* — Test: a site whose name is a number imports, and the stored name is what the
  file gave.
  **Fails before**: it is refused as a non-text value.
  **Note**: 10,898 sites in the current release are named with a number.
  **Closed on**: project/ghfdb/resources/release.py:721 ·
  tests/test_ghfdb/test_resources/test_release.py:1128

- [x] **T086** *US-3* — Test: a site whose name is a placeholder such as `?`, or empty, imports, and
  the stored name is what the file gave.
  **Fails before**: an empty name produces a site with no location.
  **Note**: 11,513 sites in the current release are named `?`.
  **Closed on**: project/ghfdb/resources/release.py:721 ·
  tests/test_ghfdb/test_resources/test_release.py:1128

- [x] **T087** *US-3* — Storing a site's name as given, without judging it.
  **Test**: T085 and T086.
  **Closed on**: project/ghfdb/resources/release.py:721 ·
  tests/test_ghfdb/test_resources/test_release.py:1128

- [x] **T088** *US-3* — Test: a row carrying a supplied quality code imports, and that code is not
  stored anywhere.
  **Fails before**: it is stored.
  **Closed on**: project/ghfdb/constants.py:212 ·
  tests/test_ghfdb/test_resources/test_release.py:1188

- [x] **T089** *US-3* — Recognising and discarding the supplied quality code.
  **Test**: T088.
  **Closed on**: project/ghfdb/constants.py:212 ·
  tests/test_ghfdb/test_resources/test_release.py:1188

- [x] **T090** *US-3* — Test: a file carrying the assessment columns is not refused for carrying
  them, and their values are not stored.
  **Fails before**: the columns are refused as undefined.
  **Closed on**: project/ghfdb/constants.py:212 ·
  tests/test_ghfdb/test_resources/test_release.py:1214

- [x] **T091** *US-3* — Recognising and discarding the assessment columns.
  **Test**: T090.
  **Closed on**: project/ghfdb/constants.py:212 ·
  tests/test_ghfdb/test_resources/test_release.py:1214

- [x] **T092** *US-3* — Test: a file of `n` valid rows produces `n` determinations. No row is dropped
  on the way in.
  **Fails before**: rows sharing a site are removed from the file as it is read, with no count and
  no notice.
  **Closed on**: project/ghfdb/resources/release.py:297 ·
  tests/test_ghfdb/test_resources/test_release.py:1241

- [x] **T093** *US-3* — Reading every row, or reporting it as refused, and nothing else.
  **Test**: T092.
  **Closed on**: project/ghfdb/resources/release.py:297 ·
  tests/test_ghfdb/test_resources/test_release.py:1241

- [ ] **T025** *US-1* — Test: a file in which one value is refused writes nothing at all — every
  record count is what it was before, including for the rows that were themselves valid.
  **Fails before**: the confirmed pass commits the valid rows and skips the refused one. This is the
  library's default and the specification forbids it. See R5.

- [ ] **T026** *US-1* — Rolling the confirmed pass back when any value was refused.
  **Test**: T025.

- [ ] **T027** *US-1* — Test: reinstating the library's default makes T025 fail. The guarantee is an
  override of a default that would otherwise pass every test written against a clean file.
  **Fails before**: the test does not exist, and its absence is what would let the override be
  removed silently.

- [ ] **T028** *US-1* — Test: an import in which any value was refused is not reported to the curator
  as having succeeded.
  **Fails before**: the confirmed pass reports success without inspecting its own result.

- [ ] **T029** *US-1* — Checking the confirmed pass's result before reporting it.
  **Test**: T028.

- [ ] **T030** *US-1* — Test: a file in which every value passes writes the records when the curator
  confirms.
  **Fails before**: no reader exists.

- [ ] **T116** *US-1* — Test: a determination identifier that repeats inside one file is refused at
  its second occurrence, naming the identifier and the line, and nothing from the file is written.
  Two rows carrying one identifier mean the file is wrong, so the portal refuses rather than letting
  the second row overwrite the first (spec, Edge cases). Added after US-4, which left the case
  reachable and worse: identifying a determination by that column turned a second occurrence from a
  duplicate record into a silent overwrite, and no task covered it.
  **Fails before**: the second row overwrites the first and the import reports success.

- [ ] **T117** *US-1* — Refusing a determination identifier that repeats within one file, checked
  against the identifiers already seen in this pass rather than against the database — a repeat
  across two separate imports is the reimport US-4 specifies, and stays an update.
  **Test**: T116, and US-4's own reimport tests unchanged.


- [x] **T115** *US-3* — Test: every column the definition marks as read lands in the field that holds
  it, asserted column by column against the fixture rather than in aggregate, and failing for any
  read column that carries no assertion. An entry in the definition that resolves to no field fails
  here rather than being dropped in silence.
  **Fails before**: the mapping is asserted only in aggregate, so a column can go nowhere unnoticed.
  **Serves**: SC-007, and the constitution's obligation that a change to the published field mapping
  carries an end-to-end test of that mapping.
  **Closed on**: project/ghfdb/resources/release.py:520 · project/ghfdb/resources/release.py:578 ·
  project/ghfdb/constants.py:212 · tests/test_ghfdb/test_resources/test_release.py:1628

---

## Phase 5 — US-4, importing the same file twice changes nothing the second time

- [ ] **T097** *US-4* — Test: importing an unchanged file twice leaves every record count identical
  to after the first import.
  **Fails before**: the second import doubles what the portal holds.

- [ ] **T098** *US-4* — Test: importing an unchanged file twice leaves every stored value identical,
  not merely the counts.
  **Fails before**: no reader exists.

- [ ] **T099** *US-4* — Test: correcting one value and re-importing updates that record and creates
  no second one.
  **Fails before**: a second record is created.

- [ ] **T100** *US-4* — Identifying a determination by its published determination identifier, so a
  repeat updates.
  **Test**: T099.

- [ ] **T101** *US-4* — Test: re-importing finds the gradient and the conductivity the determination
  was derived from, rather than creating a second pair.
  **Fails before**: a second pair is created on every import.

- [ ] **T102** *US-4* — Test: re-importing finds each correction by its determination and correction
  type, rather than creating a second record of the same type.
  **Fails before**: duplicates accumulate.

- [ ] **T103** *US-4* — Test: a site reported by two publications belongs to the dataset of the
  earlier publication year.
  **Fails before**: it belongs to whichever was imported first.

- [ ] **T104** *US-4* — Deciding a site's dataset by the earliest publication year among its
  determinations.
  **Test**: T103.

- [ ] **T105** *US-4* — Test: importing the earlier publication after the later one moves the site to
  the earlier publication's dataset.
  **Fails before**: the site stays where it was.

- [ ] **T106** *US-4* — Moving a site when a later import supplies an earlier publication year.
  **Test**: T105.

- [ ] **T107** *US-4* — Test: importing the later publication after the earlier one leaves the site
  where it is.
  **Fails before**: the site moves on every import.

- [ ] **T108** *US-4* — Test: moving a site between datasets leaves its determinations with the
  datasets of the publications that reported them.
  **Fails before**: the determinations move with the site.

- [ ] **T109** *US-4* — Keeping determinations with their own publication's dataset.
  **Test**: T108.

---

## Phase 6 — Documentation and closing

- [ ] **T110** *feature-wide* — Documentation for a curator: what file the portal reads, where the
  import is, what the check reports and how to act on it, and what happens to a file that fails.
  **Test**: the documentation builds and the page is reachable from the documentation's contents.

- [ ] **T111** *feature-wide* — Documentation of the release format's column set and which columns
  are read, recognised and discarded, or refused — generated from the definition rather than
  restated beside it.
  **Test**: the documented set equals the definition's, asserted rather than compared by eye.

- [ ] **T112** *feature-wide* — Test: no test in this feature's suite is expected to fail. The suite
  carries no expected-failure marker attributable to this feature.
  **Fails before**: the assertion does not exist.

- [ ] **T113** *feature-wide* — A migration for any model change this feature required, squashed into
  one, or an assertion that none was required.
  **Test**: this project's own applications report no missing migrations. A vendored dependency's
  migrations are outside the assertion — they already drift, and this feature does not own them.

- [ ] **T114** *feature-wide* — Test coverage meets the project's threshold for the modules this
  feature adds.
  **Test**: the coverage gate passes on the changed files.
