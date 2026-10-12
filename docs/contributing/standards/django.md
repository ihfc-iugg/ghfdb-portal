# Django standards

These guidelines cover where code lives in a Django codebase and when a new abstraction is
worth adding. `CONSTITUTION.md` points here, and its articles on simplicity, abstraction and
cohesion set the general rules that this document applies to Django. Section 10 says how
exceptions are made. The sections above **Project additions** are shared unchanged with our
other repositories, so edit this repository's rules in that last section only.

They guide code as it is written. They are never a reason to rewrite, flatten or remove
something the repository already has.

Before writing anything, ask where an experienced Django developer would expect to find it. Ask
what abstraction to create only when that question has no answer. A change is right when a
Django developer who has never seen this repository can find it by following the framework's
conventions and the ones this repository has already set.

## 1. Where code lives

| The code is | It lives in | Never in |
|---|---|---|
| A rule about one record, or something a record does | A method or property on the model | A view, a form's `save()`, a free function taking the instance |
| A rule that must hold for every row, and that the database can express | `Meta.constraints` | `clean()` alone |
| A query used in more than one place | A method on the model's `QuerySet` | A view, a template tag |
| Checking and converting what a user submitted | A `Form` or `ModelForm` | The view body |
| Reading the request, checking access, choosing the response | The view | A model or a form |
| How a value is shown | The template, or a template tag or filter when reused | A model method that returns HTML |
| An operation across several models | A method on the model the operation is named after (section 2) | A view, a signal |
| Something run from the command line or a scheduler | A management command that calls the model or queryset | Logic written in the command itself |

Dependencies point one way: models, then forms, then views, then templates. A model never imports
a form or a view. A form never imports a view.

### Modules

Code lives in the modules a Django developer already knows: `models.py`, `managers.py`,
`forms.py`, `views.py`, `urls.py`, `admin.py`, `apps.py`, `signals.py`, `templatetags/`,
`management/commands/`. Look there first.

**Code that fits none of them goes in `utils.py`.** That is where a Django developer looks for
standalone helper functions, so it is the default. It is not a way around the table above: code
that belongs on a model, a queryset or a form still goes there.

**When `utils.py` grows too large, it becomes a `utils/` package**, with one submodule per group
of related functions: `utils/dates.py`, `utils/text.py`.

**A module of its own is for code with a defined character**: it has one clear subject, and it
is likely to be added to or extended. `menus.py` holds the app's menus. `importing.py` holds its
importer. The name states the scope plainly enough that a reader knows what is inside without
opening it.

## 2. Models

- **Behaviour goes on the model it concerns.** `invoice.mark_paid()`, never
  `mark_invoice_paid(invoice)` in another module.
- **`save()` does not validate.** `clean()`, field validators and `choices` run only through
  `full_clean()`, which a `ModelForm` calls and `save()`, `create()`, `update()` and
  `bulk_create()` do not. A rule that must hold however the row is written is a database
  constraint where the database can express it. Where it cannot, as with a rule that spans
  tables, the rule lives in the one model method every write goes through. A rule that only
  shapes what a person may enter is validation.
- **An operation across several models belongs to the model it is named after.** Publishing a
  vocabulary freezes its concepts, so it is `Vocabulary.publish()`. A bulk operation is a
  `QuerySet` method.
- **When no model owns the operation**, it goes in `utils.py`, or in a module of its own when it
  has a clear subject and is likely to be extended (section 1, Modules).
- **Override `save()` and `delete()` only for what must happen on every write of that model.**
  Neither runs for `QuerySet.update()`, `bulk_create()` or a cascade delete, so nothing that must
  always hold may depend on them.

## 3. Queries

- **A reusable query is a `QuerySet` method**, exposed with `Manager.from_queryset()` or
  `QuerySet.as_manager()`. Write the method on the queryset, never on the manager alone, so that
  it chains.
- **Methods are small and compose.** `Concept.objects.published().in_scheme(scheme)`, never one
  `get_published_concepts_for_scheme()`.
- **The second use moves a query.** A filter written once stays in the view that needs it. The
  same `filter`, `exclude` or `annotate` chain appearing a second time becomes a method.
- **Database work is visible at the call site.** A property or template tag that runs a query on
  every access hides an N+1 problem. Load related rows with `select_related`, `prefetch_related`
  or an annotation in the queryset the view builds.
- **Compute in the database when the result is used to filter, order or count.** Use an
  annotation or aggregate. A Python loop over a queryset is for work the database cannot do.

## 4. Forms

- **Input that has to be checked or converted goes through a form.** A view never validates
  `request.POST` or `request.GET` by hand. A search term or page number read straight from the
  query string, and a button that posts no fields, need no form.
- **A form checks what was entered: format, required fields, how fields relate.** A rule that
  holds without a form is a model rule (section 2). Do not repeat a model's validators on its
  form, because a `ModelForm` already runs them.
- **A form's `save()` saves.** Anything more is a model method that `save()` or the view calls.

## 5. Views

- **Class-based views are strongly preferred**, built on Django's generic views or the
  repository's own base views. This is a house preference, not a claim about Django: our
  packages publish their views for projects to subclass, and a function cannot be subclassed. A
  function view is fine for a small endpoint nobody will extend, such as a webhook or a health
  check.
- **A view deals with the request and the response:** who is asking, what they sent, which model
  or queryset method to call, what to send back, and what the template needs.
- **Use the hooks the generic view already has:** `get_queryset`, `get_form_kwargs`,
  `form_valid`, `get_context_data`, `get_success_url`. Do not override `get`, `post` or
  `dispatch` to do what a hook does.
- **A view method that makes a decision about the data is in the wrong place.** Move the decision
  to the model and call it.
- **Access control uses Django's mechanisms:** `LoginRequiredMixin`, `PermissionRequiredMixin`,
  `UserPassesTestMixin`, and for access to one record, a queryset already limited to what the
  user may see.

## 6. Templates

- **A template shows what it is given.** It may branch and loop on that data. It does not
  compute, filter querysets, or decide who may do what beyond calling `perms` or a flag the view
  set.
- **Reused presentation logic is a template tag or filter.** A value that needs several steps to
  work out is worked out in the view or on the model.
- **Content is added to a page by template inheritance:** extend the template and fill a block,
  with `{{ block.super }}` to keep what was there. Where the repository already has its own way
  to add content, such as a menu class or a plugin, use that.
- **In a repository that uses django-cotton, a reused piece of template is a component**, never
  an `{% include %}` partial.

## 7. Transactions, side effects and signals

- **A change that writes more than one row is atomic.** Wrap the whole operation in
  `transaction.atomic()` at the method that owns it (section 2), not around each step inside it.
- **Anything that leaves the database waits for the commit.** Emails, task queues and calls to
  other systems go in `transaction.on_commit()`.
- **If the operation is wrong without a step, the step is called by name.** Never from a signal.
- **A signal is for code that must not know about the sender:** reacting to another app's model,
  or letting other apps react to yours. Inside one app, call the method. Receivers live in
  `signals.py` and are connected in `AppConfig.ready()`.

## 8. Abstractions

Many of our packages exist to give developers a higher-level interface to Django: menu classes,
a registry that models are registered with, a plugin system, base views. Those abstractions are
the product. This section separates them from the plumbing a change adds for its own
convenience.

### What the repository already provides

- **Work with it, in its own style.** A new menu is a subclass of the menu class. A new model is
  registered the way the others are. A new plugin follows the existing plugins. Section 1 does
  not override this: where the repository has its own way to do something, that way is the
  convention.
- **Extend it when the work calls for it.** Adding an option, a hook or a subclass to an existing
  abstraction is ordinary work and needs no special justification.
- **Do not rewrite or remove it because of this document.** If an existing abstraction looks
  wrong, raise an issue. Replacing it is a design decision for the maintainers, never a side
  effect of another change.

### A new interface for developers

- **It is asked for, not discovered.** A new public abstraction comes from the specification or
  issue the work is done under. If the work seems to need one that nobody asked for, stop and
  ask.
- **It looks like Django.** Model it on an interface Django developers already use: a class with
  declarative attributes like `ModelAdmin`, registration like `admin.site.register`, discovery
  like `autodiscover`, options in an inner `Meta`. A developer should be able to guess how it
  works from knowing Django.
- **It can be followed.** Someone reading a subclass can find the base class, see which
  attributes and methods it reads, and work out what happens. Prefer plain classes and explicit
  registration to machinery that generates code or settings.

### Plumbing inside a change

These apply to code no downstream developer will touch.

- **Django's own mechanisms come first:** `Model`, `QuerySet`, `Form`, class-based views, template
  tags, middleware, management commands, `AppConfig`. Reach for something else when one of these
  was considered and could not do the job.
- **Patterns from other frameworks need a reason Django cannot answer:** service layers,
  repositories, data transfer objects, use cases, command or event buses. A feature that fits in
  `models.py`, `forms.py`, `views.py`, `urls.py` and `templates/` needs nothing beside them.
- **Twenty plain lines beat a generic helper that saves five.** Share code when two places hold
  the same rule and must change together. Leave it alone when two places only look alike.
- **A mixin is one behaviour with a name**, such as `OwnerRequiredMixin`, not a place to collect
  helpers. A base class, mixin or helper waits for its second use.
- **A setting exists only when the code cannot know the value itself.** A sensible default with
  no setting is better than a setting nobody changes.

## 9. Apps

- **An app is one area of the domain** and holds everything that area needs: its models, forms,
  views, templates and tests. Apps are never split by technical layer.
- **Another app is used through what it publishes:** its models and their methods, its querysets,
  its forms, its URL names, its template blocks. Never through its view internals or helper
  modules.
- **Imports between apps run one way where they can.** Two apps that import each other's models
  are usually one app.
- **Refer to a swappable model through its setting** (`settings.AUTH_USER_MODEL`), and to another
  app's model by string (`"vocabularies.Concept"`) when importing it would be circular.

## 10. Guidelines, not fixed rules

Everything above is a guideline. Every situation is different, and an exception can be made
wherever it can be justified.

- **The default holds until there is a reason.** "Never" in this document means "not without
  one".
- **The reason is written down** where a reviewer will see it: in the pull request, or in a short
  comment when the code would otherwise look like a mistake.
- **A reason is about this code:** what the usual place could not do, or why the reader is better
  served here. Habit from another framework is not a reason.
- **Review checks the reasoning, not the letter.** A finding names the guideline and says why the
  exception does not hold.

Query counts and migration completeness are the two parts that are tested, as described in
[`testing.md`](testing.md), section 5.

## Project additions

<!-- Rules that apply to this repository only. Leave empty when there are none. -->

---

**Version**: 1.0.0
