# Reconciliation — 003 a published release read into the portal

The task list was written from the specification as though the repository were empty. This file
records what happened when it was walked against the code.

**A task closes only on both halves: a code citation that satisfies the task as written, and a test
that genuinely exercises it and passes.** Code with no test leaves the task open, and the remaining
work is the test. Partial is open. The checkbox state of the superseded task list was not consulted.

## The split

| | Tasks |
|---|---|
| Proven done | **6** |
| Open | **105** |
| Total | **111** |

Why each open task is open:

| Reason | Tasks |
|---|---|
| Never built | 81 |
| Built differently | 17 |
| Built without tests, or only under a vacuous one | 4 |
| Partial | 3 |

Four tasks were removed at design review for asking more than the approved specification does, and
one was added for a criterion no task served. The counts above are after both.

The proportion is expected rather than alarming. The feature reads a comma-separated release file
with its header on the first line; every reader the repository has is a spreadsheet reader taking
its headers from the sixth. Almost nothing could have been done.

## Proven done

| Task | Code | Test |
|---|---|---|
| T006 factories for every model a row produces | `project/heat_flow/factories.py:33,51,58,78,142,225,236,258` | `tests/test_heat_flow/test_factories.py:39` — 19 passed |
| T031 permission gating on the import route | `project/ghfdb/admin.py:197,351` | `tests/test_ghfdb/test_admin.py:908,916,939,945` — 4 passed |
| T032 the gate is the add permission | `project/ghfdb/admin.py:197,351` | `tests/test_ghfdb/test_admin.py:908,916,939,945` — 4 passed |
| T078 a bracketed or cased vocabulary value matches | `project/ghfdb/resources/widgets.py:53` | `tests/test_ghfdb/test_resources/test_widgets.py:487,497,519` — passed |
| T079 normalising before matching | `project/ghfdb/resources/widgets.py:53,93,130` | `tests/test_ghfdb/test_resources/test_widgets.py:475,519` — passed |
| T080 an unmatched value on a single-valued column is refused | `project/ghfdb/resources/widgets.py:98` | `tests/test_ghfdb/test_resources/test_widgets.py:507` — passed |

## Eight closures reversed

The reconciliation proposed fourteen. Six did not survive its own review and two more did not survive
the design review that followed. Almost all fell the same way.

**T051, T052, T053, T054, T055 — a row becoming the records.** The evidence was a passing round-trip
test, and it is a real test. But it reads the spreadsheet fixture through two resources the curator
runs separately, and this feature reads a release through one. Closing these would credit a
different reader for a different format and drop the release reader from the run entirely.

T053 fails a second way. It cannot be done while T059 to T063 are open, because they are the same
code path: the interval it creates has no identity, so a second row over one interval produces a
second interval. A task cannot be satisfied by code that the tasks below it exist to replace.

**T058 — the site's parent heat flow value created once per site.** The cited code achieves it by
deleting rows from the file as it reads, silently and without a count. That is the behaviour T092
and T093 exist to remove, and the cited test asserts the deletion is correct. Closing T058 would
lock in what the specification forbids.

### The two the design review caught

**T100 — a determination identified by its published identifier.** Closed on the contributor
template's reader and a test that drives it, which is the same evidence T051 to T055 were reversed
for. I applied that reason to five tasks and then failed to apply it to a sixth. Reopened.

The consequence is worth stating: T101 and T102 specify the gradient, conductivity and correction
identities as following from the determination's, so closing T100 would have left them resting on an
identity nobody was assigned to write.

**T071 — probe metadata belonging to the interval.** The task names T070 as its test, and T070 is
open. It was closed on a different test, belonging to another task and driving the other reader —
two breaches of the rule at the top of this file in one row. The model half is genuinely satisfied
and the task now says so; what remains is the reader's behaviour, which T070 proves.

## Two defects found that are not this feature's work

**The rollback flag on the existing import resources is inert.** Both
`project/ghfdb/resources/child.py:380` and `project/ghfdb/resources/parent.py:250` declare
`rollback_on_validation_errors = True` inside `class Meta`. It is not a resource `Meta` option in
`django-import-export` 4.3.9 — it is a keyword argument to `import_data()`. The declaration does
nothing, and the path it was meant to protect commits its valid rows and skips its refused ones.

This is the same fault T025 and T026 fix for the release reader, on a live path this feature does
not own. It belongs to the contributor template's own work rather than here, and is raised
separately so it is not lost.

**The migration check does not pass, for a reason outside the project.** Running it across every
application reports drift in a vendored dependency's own migrations, not in this project's. T113 is
reworded to assert that this project's applications owe no migration, which is what it was for.

## What the reconciliation says about the code it walked

Three findings are worth carrying into the implementation, because each is a test asserting the
opposite of what this specification requires:

- A passing test requires a numerically named site to be refused. The current release names 10,898
  sites with a number.
- A passing test asserts that nine correction records are created for every determination regardless
  of what the row supplies.
- A passing test asserts that rows sharing a site are deleted from the file as it is read.

None is a mistake by whoever wrote them; each records the behaviour agreed at the time. They are
named here because the tasks that change that behaviour will have to change these tests, and a
change to a passing test is the thing most likely to be mistaken for tampering when the branch is
reviewed.
