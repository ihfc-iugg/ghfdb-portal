# Testing standards

These rules apply to every change in this repository. `CONSTITUTION.md` makes them binding. The
sections above **Project additions** are shared unchanged with our other repositories, so edit
this repository's rules in that last section only.

## 1. What gets a test

A test exists to catch a behaviour that breaks by accident. Before writing one, ask what decides
whether the result is right.

- **A specification, a contract or a computation decides it.** Write a test.
- **Only a person looking at the page decides it.** Write no test. Make the change and have it
  reviewed by eye.

A useful second check is whether the test could fail for any reason other than someone
deliberately changing the value it asserts. If it could not, it is a change detector. It only
records a decision, and it has to be edited every time that decision changes. Do not write it.

### Tested

- The right records, values and fields appear, and the wrong ones do not.
- Conditional states: empty, absent, hidden from users without permission.
- Link and redirect targets.
- Form behaviour: validation, what is saved, where the user is sent afterwards.
- Values computed from data, including how a missing value is shown (`—` rather than `0`).
- Escaping of user and model data.
- Ids, `data-` attributes and other hooks that a script depends on.
- Permissions and access control.
- Query counts on list and detail pages (section 5).

### Not tested

- Wording: headings, labels, captions, help text, button text, empty-state text.
- Styling and layout: colours, widths, spacing, stacking, alignment, icons, component variants,
  the order of sections on a page.
- CSS classes in project templates.

### Markup that consumers depend on

A package that publishes template components has consumers who write their own CSS and templates
against the markup those components emit. For a published component, that markup is behaviour:

- the element it renders,
- the classes that make up the component's styling,
- the attributes and slots a caller can pass in.

Decorative choices inside the component stay untested. In a project, all markup is design.

### Text

Text is behaviour only when it is computed from data: pluralised, formatted, or chosen by a
condition. Fixed wording is never asserted.

Messages that do a job are tested for the job, not the sentence:

- A validation error is asserted by the field it is attached to and its error code
  (`form.has_error("date", code="future_date")`). Raise every `ValidationError` with a `code`.
- A flash message is asserted by its level and that it was added.
- An email is asserted by its recipient and the data or link it carries.

### Finding elements

A test that needs an element finds it by data from its fixtures, by role, or by id, never by the
surrounding wording. Renaming a heading must not break a behaviour test. When an existing test is
anchored on text that changes, update the string and nothing else.

### Specifications

An acceptance criterion states behaviour, never wording or appearance. "Shows the record's
licence" is a criterion. "Headed 'Licence'" is not, because a criterion is the thing a test is
written against.

## 2. Test-first

Every behaviour change follows the red, green, refactor cycle.

1. **Red.** Write a test and watch it fail for the right reason. A test that passes on its first
   run is testing nothing new.
2. **Green.** Write the least code that makes it pass.
3. **Refactor.** Clean up with the tests still green. A refactor that needs an assertion edited
   has changed behaviour and is not a refactor.

**Defects are reproduced first.** Write a test that fails with the reported symptom, then fix it.
If no test can reproduce it, say so in the pull request.

**Changes to wording or appearance skip the cycle.** They are not defects. Make the change and
move on.

Never weaken an assertion, add `skip` or `xfail`, broaden an `except`, or special-case production
code to make a test pass.

## 3. Writing tests

- **Assert outcomes, not call sequences.** `assert response.context["concepts"] == [...]`
  survives a refactor. `mock_filter.assert_called_with(...)` breaks on one that changed nothing.
- **Real objects over fakes, fakes over mocks.** Mock only what is slow, non-deterministic or has
  side effects outside the test: network calls, email, the clock. Never mock the ORM.
- **One behaviour per test**, named for it: `test_publishing_a_vocabulary_freezes_its_concepts`,
  never `test_publish_works`.
- **Arrange, act, assert**, visibly separated, in that order.
- **Readable over DRY.** A test should read as a specification without tracing helpers.

## 4. Structure and fixtures

- **Mirror the source tree.** Every test module mirrors the path of the module it exercises:
  `pkg/models.py` → `tests/test_models.py`, `pkg/views/form_views.py` →
  `tests/test_views/test_form_views.py`. Test subpackages carry `__init__.py`. One source module
  that defines several units stays one test module, split by classes.

  A test whose subject is not a Python module has nothing to mirror:
  - `tests/test_factories.py` tests `tests/factories.py`.
  - `tests/test_smoke.py` checks that the package imports and its settings are valid.
  - A suite testing templates or static assets is exempt when the repository declares it:

    ```toml
    [tool.forge.conformance]
    non-mirror-paths = ["tests/test_components/"]
    ```

    A trailing slash marks a directory prefix. Declaring a path whose subject is a Python module
    is a review failure.
- **Group tests into classes**, one `Test<Subject>` class per unit, so one area can be run on its
  own: `pytest tests/test_models.py::TestConceptModel`.
- **One factory per model.** Each model has exactly one `factory_boy` `DjangoModelFactory` in
  `tests/factories.py`, using `factory.Sequence` for unique fields and `factory.SubFactory` for
  relations. Variants override fields at the call site. They are never factory subclasses.
- **Fixtures wrap factories, and shared setup lives in `conftest.py`.** `def concept(): return
  ConceptFactory()`. A one-off variation calls the factory inline. Test modules hold assertions,
  not construction.
- **Use the pytest-django toolchain.** Database access through `db`, `transactional_db` or
  `@pytest.mark.django_db`. Requests through `client`, `admin_client` or `rf`. No
  `unittest.TestCase`. The tools come pinned in the `mvp-shared[test]` bundle.
- **A run writes files only inside its own directory, and a factory attaches none unless asked.**
  `MEDIA_ROOT`, and `STATIC_ROOT` where anything writes to it, point at a directory the runner
  creates and removes for the run (`tmp_path_factory`). That has to hold under `pytest-xdist`. A
  factory that can attach a file leaves the field empty by default, and a test that needs a file
  asks for one (`ProjectFactory(with_image=True)`). A downstream project inherits a package's
  factories without its test settings, so a factory that writes on every build fills that
  project's media directory.

## 5. Django checks

| Check | How |
|---|---|
| No N+1 queries on list and detail pages | Render with one record and with several, and assert the same query count under `django_assert_num_queries`. Never pin a count that grows with rows, and never time a request. |
| Migrations are complete | `python manage.py makemigrations --check` is clean after the change. |
| Every model field has `verbose_name` and `help_text` | One parametrised test over every field of every model. Never one test per field, and never asserting the wording. |
| Template output for component changes | Render the template, not only the context. A context key can be right while the template never renders it. |
| Translated strings compare correctly | Compare `str(value)`. A lazy translation proxy can pass or fail `==` for the wrong reason. |

## 6. Coverage

- **Project ≥ 90%, patch ≥ 85%,** with a 1% tolerance, as set in `codecov.yml`. They are floors,
  not a ratchet towards 100%.
- Only Python is measured. Templates are not, so markup left untested under section 1 does not
  lower the figure. Do not enable template coverage.
- A test written only to raise coverage is still bound by section 1.

## Project additions

- **Schema-mapping round trips.** A change to a GHFDB field mapping gets an automated test
  verifying the mapping end-to-end: model → serialiser/export → flat row, and flat row → importer
  → model. Reference the row in `docs/ghfdb_fields.md` the test covers.
- **Quality-score regression tests.** `U-score` and `M-score` calculations are tested against
  reference values pinned as regression tests, with at least two example inputs each. The
  reference values are the output of the Heat Flow Quality Analysis Toolbox V0.2 itself, which
  scored the release, and the examples in Fuchs et al. (2021, 2023) are used only where they
  agree with it. Assert coordinate precision to 0.0001 degrees and heat flow values to
  0.01 mW/m².

---

**Version**: 1.0.0
