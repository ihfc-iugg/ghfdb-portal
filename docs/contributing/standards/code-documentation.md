# Code documentation standards

These rules cover the documentation that lives in the code: docstrings, component annotations and
comments. `CONSTITUTION.md` makes them binding. The sections above **Project additions** are
shared unchanged with our other repositories, so edit this repository's rules in that last section
only.

Docstrings and component annotations are reference documentation. They are complete, because
developers read them in the built docs and in their editor. Comments are the opposite. The reader
is a competent developer who can already read the code, so a comment is rare and short.

## 1. Docstrings

Docstrings use the [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

**Every class, function and method this repository defines gets a full docstring:**

- a one-line summary in the imperative ("Return the concepts a scheme publishes."),
- a longer description when the summary is not enough,
- `Args:` for every parameter,
- `Returns:` or `Yields:` unless it returns `None`,
- `Raises:` for every exception the caller is expected to handle,
- `Example:` where a usage example says more than the prose.

Types live in the annotations, not in the docstring. A class documents its constructor arguments
in the class docstring, and `__init__` has none of its own.

```python
def publish(scheme: ConceptScheme, *, notify: bool = True) -> int:
    """Publish a scheme and freeze its concepts.

    Args:
        scheme: The scheme to publish. Must not already be published.
        notify: Email the scheme's maintainers once publishing succeeds.

    Returns:
        The number of concepts frozen.

    Raises:
        AlreadyPublished: The scheme was published before.
    """
```

**An override of a framework hook gets a one-line docstring** saying what this override adds:
`get_queryset`, `get_context_data`, `form_valid`, `clean`, `save`, `dispatch` and the like. The
framework already documents the arguments and return value.

```python
def get_queryset(self):
    """Limit to the signed-in user's records."""
```

**Modules** get a one-line docstring naming what the module holds.

**No docstrings on:**

- test functions, test classes and fixtures, whose names state what they check,
- migrations,
- a model's or form's inner `Meta` class.

## 2. Component annotations

Every Cotton component documents itself with the annotations read by the
[django-cotton-gallery](https://pypi.org/project/django-cotton-gallery/) linter, at the top of its
template. They are the component's docstring and are complete in the same way:

```django
{# @description A message banner, optionally dismissible. Shows an icon, then the default slot. #}
{# @prop variant:select['info','success','warning','error'] | description:"Colour variant." #}
{# @prop dismissible:boolean | description:"Add a dismiss button that hides the alert." #}
{# @slot Your changes were saved. — The alert message. #}
<c-vars variant dismissible />
```

The comment rules in section 3 do not apply to these annotations.

## 3. Comments

These rules cover comments in Python, templates, JavaScript and CSS.

1. **Assume a competent reader.** A comment never says what the code does. If the code cannot be
   understood without one, rename or restructure it first.
2. **Comment only what the code cannot say:** why a choice was made, a trap, a constraint imposed
   from outside, or a workaround for a bug elsewhere.
3. **One line where possible, and never more than three.** When the reason takes longer to
   explain, the explanation belongs in an issue, pull request or ADR, and the comment points to
   it.
4. **A reference must resolve from this repository:** an issue or pull request number (`#123`), an
   ADR path (`docs/adr/0007-lazy-urls.md`), or a specification code (`FS-012`). Never a name, a
   date, or an identifier recorded somewhere else.
5. **Say it once.** Code that repeats shares one comment, or is factored out.
6. **No banners, dividers, change history or commented-out code.** Version control records who
   changed what, and when.

```python
# DaisyUI also defines `.loading` as its spinner, so TomSelect's state class is renamed (#141).
loading_class="ts-loading",
```

A Django `{# … #}` comment is a single line. Use `{% comment %}` for the rare comment that needs
more.

## 4. Enforcement

- `ruff` checks docstring format with `convention = "google"`.
- `pydoclint` checks that `Args:`, `Returns:` and `Raises:` match the signature and the body. It
  skips one-line docstrings, which is what lets framework overrides stay one line.
- The django-cotton-gallery linter checks component annotations.
- Section 3 is checked in review.

## Project additions

<!-- Rules that apply to this repository only. Leave empty when there are none. -->

---

**Version**: 1.0.0
