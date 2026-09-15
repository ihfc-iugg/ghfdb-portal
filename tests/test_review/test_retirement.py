"""T010a: the tree must never hold two answers at once.

Asserted by a grep-style test rather than by eye: no reference to
``STATUS_CHOICES``, ``review__status`` or the old "Reviewers" group may
survive anywhere in ``project/``, once the code the new record supersedes
is retired.

Migrations are excluded deliberately: a migration is a historical record of
what the schema used to be and is never edited once written — the mapping
comment in ``0003_review_workflow_fields.py`` is expected to name the old
``STATUS_CHOICES`` values it is translating away from.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2] / "project"

FORBIDDEN_IN_PYTHON = [
    "STATUS_CHOICES",
    "review__status",
    'groups__name="Reviewers"',
    "groups__name='Reviewers'",
    'groups__name="reviewers"',
    "groups__name='reviewers'",
    'group_required = ["Reviewers"]',
]


def _python_files():
    for path in PROJECT_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts or "migrations" in path.parts:
            continue
        yield path


def _html_files():
    for path in PROJECT_ROOT.rglob("*.html"):
        yield path


class TestOldRecordVocabularyIsRetired:
    def test_no_forbidden_python_reference_remains(self):
        matches = [
            f"{path}: {pattern!r}"
            for path in _python_files()
            for pattern in FORBIDDEN_IN_PYTHON
            if pattern in path.read_text()
        ]
        assert not matches, matches

    def test_no_template_reads_the_retired_status_attribute(self):
        matches = [
            str(path) for path in _html_files() if "review.status" in path.read_text()
        ]
        assert not matches, matches
