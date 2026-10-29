"""The published vocabularies the heat flow fields draw their terms from.

The IHFC vocabularies are published by ihfc-iugg/controlled-vocabularies under
``https://w3id.org/ihfc-iugg/vocabularies/``, and ``manage.py sync_vocabularies`` reads each
one in Turtle from its address with ``.ttl`` added. The elevation datum is ODM2's, shipped
with the portal because ODM2's server cannot be relied on. ``README.md`` beside this module
gives its source and licence.

A field stores a term as the address of its concept. The text a person or an upload
template writes for a term is its label or its identifier, the last part of its address,
which is the key the GHFDB templates use.
"""

from pathlib import Path

from controlled_vocabularies.fields import Vocabulary
from controlled_vocabularies.models import Record
from django.utils.translation import gettext_lazy as _

FILES = Path(__file__).parent

#: The address every IHFC vocabulary is published under.
IHFC = "https://w3id.org/ihfc-iugg/vocabularies"


def ihfc_vocabulary(slug: str) -> Vocabulary:
    """Name an IHFC vocabulary by its slug, read in Turtle from its own address.

    Args:
        slug: The vocabulary's slug, the last part of its address.

    Returns:
        The vocabulary.
    """
    uri = f"{IHFC}/{slug}"
    return Vocabulary(uri, source=f"{uri}.ttl")


HEAT_FLOW_METHOD = ihfc_vocabulary("heat-flow-method")
PROBE_TYPE = ihfc_vocabulary("heat-flow-probes")
GEOGRAPHIC_ENVIRONMENT = ihfc_vocabulary("geographic-environments")
EXPLORATION_METHOD = ihfc_vocabulary("exploration-methods")
EXPLORATION_PURPOSE = ihfc_vocabulary("exploration-purpose")
TEMPERATURE_METHOD = ihfc_vocabulary("temperature-method")
TEMPERATURE_CORRECTION = ihfc_vocabulary("temperature-corrections")
CONDUCTIVITY_SOURCE = ihfc_vocabulary("conductivity-sources")
CONDUCTIVITY_METHOD = ihfc_vocabulary("conductivity-methods")
CONDUCTIVITY_LOCATION = ihfc_vocabulary("conductivity-location")
CONDUCTIVITY_SATURATION = ihfc_vocabulary("conductivity-saturation")
CONDUCTIVITY_PT_CONDITIONS = ihfc_vocabulary("conductivity-conditions")
CONDUCTIVITY_STRATEGY = ihfc_vocabulary("conductivity-strategy")
CONDUCTIVITY_PT_FUNCTION = ihfc_vocabulary("conductivity-pt-function")

ELEVATION_DATUM = Vocabulary(
    "http://vocabulary.odm2.org/elevationdatum",
    source=FILES / "odm2" / "elevationdatum.rdf",
)

#: The elevation datum a site starts with.
MEAN_SEA_LEVEL = f"{ELEVATION_DATUM.uri}/MSL"

#: The identifier of the concept a vocabulary offers for a value nobody recorded.
UNSPECIFIED = "unspecified"


def term(vocabulary: Vocabulary, identifier: str) -> str:
    """Return the address of one of a vocabulary's concepts.

    Args:
        vocabulary: The vocabulary.
        identifier: The concept's identifier, the last part of its address.

    Returns:
        The concept's address.
    """
    return f"{vocabulary.uri}/{identifier}"


def identifier(concept: Record) -> str:
    """Return a concept's identifier, the last part of its address.

    Args:
        concept: The concept.

    Returns:
        The identifier, such as ``LOGeq``.
    """
    return concept.uri.rsplit("/", 1)[-1]


def concepts(vocabulary: Vocabulary):
    """Return the concepts the portal has loaded for a vocabulary.

    Args:
        vocabulary: The vocabulary.

    Returns:
        A queryset of its concepts.
    """
    return Record.objects.filter(
        scheme__uri=vocabulary.uri, type=Record.Type.CONCEPT
    ).order_by("pref_label")


def choices(vocabulary: Vocabulary) -> list[tuple[str, str]]:
    """Return a vocabulary's concepts as ``(address, label)`` pairs.

    Args:
        vocabulary: The vocabulary.

    Returns:
        One pair per concept, in label order.
    """
    return [(concept.uri, concept.display_label()) for concept in concepts(vocabulary)]


def normalize_vocab_token(raw: str) -> str:
    """Strip surrounding square brackets and lowercase a vocabulary token (FS-003 FR-016).

    GHFDB upload templates wrap vocabulary cell values in square brackets,
    e.g. '[Onshore (continental)]'. This helper normalises such tokens so they
    match a concept's label or identifier, compared in lower case.
    The caller should preserve the original raw value for error messages.

    Whitespace is stripped on both sides of the brackets, not just inside
    them. Real submissions carry cells like ``' [unspecified]'`` — a leading
    space defeats a bare ``strip("[]")``, because the first character is not
    a bracket and stripping stops there.

    Args:
        raw: The text as it was typed or written in the cell.

    Returns:
        The token without brackets, lowercased.
    """
    return raw.strip().strip("[]").strip().lower()


def lookup(vocabulary: Vocabulary) -> dict[str, Record]:
    """Map every name of a vocabulary's concepts, in lower case, to the concept.

    A concept is known by its label, its identifier and the hidden labels the upload
    template writes for it. A label or an identifier outranks a hidden label that
    happens to spell the same.

    Args:
        vocabulary: The vocabulary.

    Returns:
        The concepts by lowercased hidden label, label and identifier.
    """
    found = list(concepts(vocabulary))
    by_hidden = {
        normalize_vocab_token(entry["@value"]): concept
        for concept in found
        for entry in concept.values("skos:hiddenLabel")
        if "@value" in entry
    }
    by_label = {concept.display_label().lower(): concept for concept in found}
    by_identifier = {identifier(concept).lower(): concept for concept in found}
    return {**by_hidden, **by_label, **by_identifier}


def slug(vocabulary: Vocabulary) -> str:
    """Return the last part of a vocabulary's address, which names it in messages.

    Args:
        vocabulary: The vocabulary.

    Returns:
        The slug, such as ``geographic-environments``.
    """
    return vocabulary.uri.rstrip("/").rsplit("/", 1)[-1]


def resolve_term(vocabulary: Vocabulary, text) -> Record | None:
    """Read one vocabulary term from the text a person or a file wrote for it.

    A label or an identifier is accepted, in any case, with or without square brackets.

    Args:
        vocabulary: The vocabulary.
        text: The text to read.

    Returns:
        The concept, or ``None`` for blank text and for ``unspecified``.

    Raises:
        ValueError: If the text names no term of the vocabulary.
    """
    token = normalize_vocab_token(text or "")
    if token in ("", UNSPECIFIED):
        return None
    terms = lookup(vocabulary)
    concept = terms.get(token)
    if concept is None:
        raise ValueError(
            _(
                "Invalid value '%(val)s' for %(vocab)s vocabulary. Valid options are: %(opts)s"
            )
            % {
                "val": text,
                "vocab": slug(vocabulary),
                "opts": sorted(
                    concept.display_label().lower() for concept in concepts(vocabulary)
                ),
            }
        )
    return concept


def resolve_terms(vocabulary: Vocabulary, text):
    """Read several vocabulary terms from semicolon-separated text.

    Each token is read as ``resolve_term`` reads one, except that ``unspecified`` names the
    vocabulary's own concept when it has one and is dropped when it has none.

    Args:
        vocabulary: The vocabulary.
        text: The text to read.

    Returns:
        The vocabulary's concepts the tokens name, as a queryset. Blank text gives none.

    Raises:
        ValueError: If any token names no term of the vocabulary; the message names each.
    """
    terms = lookup(vocabulary)
    tokens = [token.strip() for token in str(text or "").split(";") if token.strip()]
    matched, unknown = [], []
    for token in tokens:
        concept = terms.get(normalize_vocab_token(token))
        if concept is not None:
            matched.append(concept.uri)
        elif normalize_vocab_token(token) != UNSPECIFIED:
            unknown.append(token)
    if unknown:
        raise ValueError(
            _(
                "The following values are not part of the %(vocab)s vocabulary: %(invalid)s"
            )
            % {"vocab": slug(vocabulary), "invalid": unknown}
        )
    return concepts(vocabulary).filter(uri__in=matched)
