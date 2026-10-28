"""Repair the identifiers of references stored before django-literature 0.3.

django-literature 0.3 stores one valid DOI, ISSN and ISBN on each reference and refuses to
convert a reference whose stored value is anything else. The portal's references were entered
over many years, and many hold values its upgrade command refuses: an ISSN whose leading zeros a
spreadsheet removed, an ISBN filed as an ISSN, several ISSNs in one field, or text that is no
identifier at all.

Run once, before ``upgrade_literature``, on a database that still holds the old
``literature_literatureitem`` table. Each value is read as an ISSN, an ISBN or a DOI where it is
one, whichever field it was in. A reference keeps its first ISSN and its first ISBN, and every
value that does not fit, an over-long number or address among them, is written into the
reference's note, so nothing is lost. Every change is printed.
"""

import json
import re

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from literature.models import Item, ItemIdentifier
from literature.validators import validate_doi, validate_isbn, validate_issn

#: The table django-literature kept references in before 0.3.
LEGACY_TABLE = "literature_literatureitem"

#: The qualifiers PubMed writes after each ISSN, such as ``0012-821X (Print)``.
ISSN_QUALIFIER = re.compile(r"\((?:print|electronic|linking|online)\)", re.IGNORECASE)

#: A DOI written as a resolver address or with a ``doi:`` prefix.
DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.IGNORECASE)


def is_valid(validator, value: str) -> bool:
    """Return whether a django-literature validator accepts a value.

    Args:
        validator: One of ``literature.validators``.
        value: The value to check.

    Returns:
        Whether it is accepted.
    """
    try:
        validator(value)
    except ValidationError:
        return False
    return True


def as_issn(token: str) -> str | None:
    """Read a token as an ISSN, restoring the leading zeros a spreadsheet removed.

    A shortened number is accepted only when its check digit confirms the restored one.

    Args:
        token: One value from an ISSN or ISBN field.

    Returns:
        The hyphenated ISSN, or ``None`` when the token is not one.
    """
    compact = token.replace("-", "").upper()
    if compact.isdigit() and 4 <= len(compact) < 8:
        compact = compact.zfill(8)
    if len(compact) != 8:
        return None
    issn = f"{compact[:4]}-{compact[4:]}"
    return issn if is_valid(validate_issn, issn) else None


def as_isbn(token: str) -> str | None:
    """Read a token as an ISBN.

    Args:
        token: One value from an ISBN, ISSN or DOI field.

    Returns:
        The token, or ``None`` when it is not an ISBN.
    """
    return token if is_valid(validate_isbn, token) else None


def text_of(value) -> str:
    """Return a stored CSL value as text, joining a list.

    Args:
        value: A string, a number or a list of them.

    Returns:
        The text.
    """
    if isinstance(value, list):
        return ", ".join(str(part) for part in value)
    return str(value).strip()


def repair(item: dict) -> tuple[dict, list[str]]:
    """Repair the identifiers and over-long fields of one stored reference.

    Args:
        item: The reference's CSL-JSON, as the old table stored it.

    Returns:
        The repaired CSL-JSON, and one line per change. No lines means it needs none.
    """
    repaired = dict(item)
    issns: list[str] = []
    isbns: list[str] = []
    noted: list[tuple[str, str]] = []

    if "ISSN" in item:
        text = ISSN_QUALIFIER.sub(" ", text_of(item["ISSN"]))
        for token in re.split(r"[,;\s]+", re.sub(r"\s*-\s*", "-", text)):
            if not token:
                continue
            if issn := as_issn(token):
                issns.append(issn)
            elif isbn := as_isbn(token):
                isbns.append(isbn)
            else:
                noted.append(("ISSN", token))
    if "ISBN" in item:
        for token in re.split(r"[,;]+", text_of(item["ISBN"])):
            token = token.strip()
            if not token:
                continue
            if isbn := as_isbn(token):
                isbns.append(isbn)
            elif issn := as_issn(token):
                issns.append(issn)
            else:
                noted.append(("ISBN", token))
    if "DOI" in item:
        doi = DOI_PREFIX.sub("", text_of(item["DOI"])).strip()
        repaired.pop("DOI")
        if is_valid(validate_doi, doi):
            repaired["DOI"] = doi
        elif isbn := as_isbn(doi):
            isbns.append(isbn)
        else:
            noted.append(("DOI", text_of(item["DOI"])))

    for field, found in (("ISSN", issns), ("ISBN", isbns)):
        repaired.pop(field, None)
        distinct = list(dict.fromkeys(found))
        if distinct:
            repaired[field] = distinct[0]
            noted.extend((field, value) for value in distinct[1:])

    limits = {
        "number": Item._meta.get_field("number").max_length,
        "URL": ItemIdentifier._meta.get_field("value").max_length,
    }
    for field, limit in limits.items():
        if field in repaired and len(text_of(repaired[field])) > limit:
            noted.append((field, text_of(repaired.pop(field))))

    if noted:
        lines = [f"{field}: {value}" for field, value in noted]
        repaired["note"] = "\n".join(
            filter(None, [text_of(item.get("note", "")), *lines])
        )

    changes = [
        f"{field} {text_of(item.get(field, ''))!r} -> {text_of(repaired.get(field, ''))!r}"
        for field in ("DOI", "ISSN", "ISBN", "number", "URL")
        if text_of(item.get(field, "")) != text_of(repaired.get(field, ""))
    ]
    changes += [f"{field} {value!r} kept in the note" for field, value in noted]
    return repaired, changes


class Command(BaseCommand):
    """Repair stored references so that django-literature 0.3 can convert them."""

    help = (
        "Repair the DOI, ISSN and ISBN of every reference stored before django-literature "
        "0.3, keeping any value that is no identifier in the reference's note. Run it before "
        "upgrade_literature."
    )

    def add_arguments(self, parser):
        """Add ``--dry-run``."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print the changes without writing them.",
        )

    def handle(self, *args, dry_run, **options):
        """Repair every reference that needs it, in one transaction."""
        with connection.cursor() as cursor:
            if LEGACY_TABLE not in connection.introspection.table_names(cursor):
                self.stdout.write(
                    "Nothing to repair: the database holds no references stored "
                    "before django-literature 0.3."
                )
                return
            cursor.execute(
                f"SELECT id, citation_key, item FROM {LEGACY_TABLE} ORDER BY id"  # noqa: S608
            )
            rows = cursor.fetchall()

        repaired = []
        for pk, key, stored in rows:
            item = json.loads(stored) if isinstance(stored, str) else stored
            fixed, changes = repair(item)
            if changes:
                repaired.append((pk, fixed))
                for change in changes:
                    self.stdout.write(f"{key}: {change}")

        if dry_run:
            self.stdout.write(f"{len(repaired)} references would be repaired.")
            return
        with transaction.atomic(), connection.cursor() as cursor:
            for pk, fixed in repaired:
                cursor.execute(
                    f"UPDATE {LEGACY_TABLE} SET item = %s WHERE id = %s",  # noqa: S608
                    [json.dumps(fixed), pk],
                )
        self.stdout.write(f"Repaired {len(repaired)} references.")
