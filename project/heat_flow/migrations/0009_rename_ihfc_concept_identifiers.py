from controlled_vocabularies.fields import ConceptField, MultiConceptField
from django.db import migrations

# The IHFC vocabularies renamed every concept to one style: lowercase words joined by
# hyphens, acronyms in capitals, ``p`` and ``T`` in their usual case. A concept's
# address ends with its identifier, so every stored address has to follow.
IHFC = "https://w3id.org/ihfc-iugg/vocabularies"

# Vocabulary slug -> old identifier -> new identifier. Identifiers not listed kept their name.
CONCEPT_IDENTIFIERS = {
    "conductivity-conditions": {
        "actualInSitu": "actual-in-situ",
        "correctedP": "corrected-p",
        "correctedPT": "corrected-pT",
        "correctedT": "corrected-T",
        "recordedAmbient": "recorded-ambient",
        "replicatedP": "replicated-p",
        "replicatedPT": "replicated-pT",
        "replicatedT": "replicated-T",
        "unrecordedAmbient": "unrecorded-ambient",
    },
    "conductivity-methods": {
        "chlorineContent": "chlorine-content",
        "laboratoryOther": "laboratory-other",
        "lineSourceFull": "line-source-full",
        "lineSourceHalf": "line-source-half",
        "mineralComposition": "mineral-composition",
        "planeSourceFull": "plane-source-full",
        "planeSourceHalf": "plane-source-half",
        "pointSource": "point-source",
        "probeContinuousHeating": "probe-continuous-heating",
        "probePulse": "probe-pulse",
        "waterContent": "water-content",
        "wellLogDeterministic": "well-log-deterministic",
        "wellLogEmpirical": "well-log-empirical",
    },
    "conductivity-pt-function": {
        "Abdulagatov2006": "pT-abdulagatov-2006",
        "Abdulagatova2009": "pT-abdulagatova-2009",
        "Anand1973": "T-anand-1973",
        "BirchClark1940": "T-birch-clark-1940",
        "Blesch1983": "T-blesch-1983",
        "Bridgman1924": "p-bridgman-1924",
        "Buntebarth1991": "pT-buntebarth-1991",
        "Chapman1984": "T-chapman-1984",
        "ChapmanFurlong1992": "pT-chapman-furlong-1992",
        "Demirci2004": "p-demirci-2004",
        "Duruturk2002": "p-duruturk-2002",
        "Emirov1997": "pT-emirov-1997",
        "Emirov2017": "pT-emirov-2017",
        "EmirovRamazanova2007": "pT-emirov-ramazanova-2007",
        "FuchsFoerster2014": "p-fuchs-foerster-2014",
        "Funnell1996": "T-funnell-1996",
        "Gorgulu2008": "p-gorgulu-2008",
        "HaenelZoth1973": "T-haenel-zoth-1973",
        "Hyndman1974": "pT-hyndman-1974",
        "Kukkonen1999": "p-kukkonen-1999",
        "KukkonenT1999": "T-kukkonen-1999",
        "KutasGordienko1971": "T-kutas-gordienko-1971",
        "Langseth1965": "pT-langseth-1965",
        "Miranda2018": "T-miranda-2018",
        "Radcliff1960": "pT-ratcliffe-1960",
        "RamazanovaEmirov2010": "pT-ramazanova-emirov-2010",
        "RamazanovaEmirov2012": "pT-ramazanova-emirov-2012",
        "Ratcliff1960": "T-ratcliffe-1960",
        "RatcliffeP1960": "p-ratcliffe-1960",
        "Sass1992": "T-sass-1992",
        "Seipold2001": "p-seipold-2001",
        "SeipoldT2001": "T-seipold-2001",
        "Sekiguchi1984": "T-sekiguchi-1984",
        "Sibbitt1975": "p-sibbitt-1975",
        "Somerton1992": "T-somerton-1992",
        "Sun2017": "T-sun-2017",
        "Tikhomirov1968": "T-tikhomirov-1968",
        "VosteenSchellschmidt2003": "T-vosteen-schellschmidt-2003",
        "ZothHaenal1988": "T-zoth-haenel-1988",
        "site_specific": "site-specific",
    },
    "conductivity-saturation": {
        "dryMeasured": "dry-measured",
        "saturatedCalculated": "saturated-calculated",
        "saturatedInSitu": "saturated-in-situ",
        "saturatedMeasured": "saturated-measured",
    },
    "conductivity-sources": {
        "assumed_from_literature": "assumed-from-literature",
        "core_log": "core-log",
        "core_samples": "core-samples",
        "cutting_samples": "cutting-samples",
        "insitu_probe": "in-situ-probe",
        "mineral_computation": "mineral-computation",
        "outcrop_samples": "outcrop-samples",
        "well_log": "well-log",
    },
    "conductivity-strategy": {
        "well_log": "well-log",
    },
    "exploration-methods": {
        "drilling_clustering": "drilling-clustering",
        "probing_clustering": "probing-clustering",
        "probing_offshore": "probing-offshore",
        "probing_onshore": "probing-onshore",
    },
    "exploration-purpose": {
        "underground_storage": "underground-storage",
    },
    "geographic-environments": {
        "offshore_continental": "offshore-continental",
        "offshore_marine": "offshore-marine",
        "onshore_continental": "onshore-continental",
        "onshore_marine": "onshore-lake-river",
    },
    "heat-flow-corrections": {
        "consideredP": "considered-p",
        "consideredPT": "considered-pT",
        "consideredT": "considered-T",
        "driftCorrected": "drift-corrected",
        "notConsidered": "not-considered",
        "notCorrected": "uncorrected",
        "not_recognized": "unrecognized",
        "present_corrected": "present-corrected",
        "present_not_corrected": "present-uncorrected",
        "present_not_significant": "present-insignificant",
        "tiltCorrected": "tilt-corrected",
    },
    "heat-flow-probes": {
        "outrigger_autonomous_no_corer": "outrigger-autonomous",
        "outrigger_autonomous_with_corer": "outrigger-autonomous-corer",
        "outrigger_ewing": "outrigger-ewing-corer",
        "outrigger_haenel": "outrigger-haenel",
        "outrigger_hybrid_lister_hylo": "outrigger-hybrid-lister",
        "outrigger_lister": "outrigger-lister-corer",
        "outrigger_von_herzen": "outrigger-von-herzen",
        "single_steel": "single-steel",
        "single_steel_insituTC": "single-steel-in-situ-TC",
        "violin_bow": "violin-bow",
    },
    "temperature-corrections": {
        "aapg": "AAPG",
        "cylinderSource": "cylinder-source",
        "hornerPlot": "horner-plot",
        "inverseNM": "inverse-numerical-modelling",
        "lineSourceExplosion": "line-source-explosion",
        "not_corrected": "uncorrected",
    },
    "temperature-method": {
        "BLK": "thermal-blanket",
        "DTSeq": "DTS-equilibrium",
        "DTSpert": "DTS-perturbed",
        "HT_FT": "HT-FT-equilibrium",
        "HT_FTpert": "HT-FT-perturbed",
        "LOGeq": "log-equilibrium",
        "LOGpert": "log-perturbed",
        "ODTT_PC": "ODTT-piston-corer",
        "ODTT_TP": "ODTT-thermistor-probe",
        "RTDeq": "RTD-equilibrium",
        "RTDpert": "RTD-perturbed",
        "SUR": "surface",
        "XEN": "xenolith",
        "cBHT": "BHT-corrected",
        "cDTS": "DTS-corrected",
        "cHT_FT": "HT-FT-corrected",
        "cLOG": "log-corrected",
        "cRTD": "RTD-corrected",
    },
}

# The correction status is stored as the identifier alone, not as an address, in the
# identifiers the portal chose for them.
CORRECTION_STATUSES = {
    "present_corrected": "present-corrected",
    "present_not_corrected": "present-uncorrected",
    "present_not_significant": "present-insignificant",
    "not_recognized": "unrecognized",
    "considered_p": "considered-p",
    "considered_t": "considered-T",
    "considered_pt": "considered-pT",
    "not_considered": "not-considered",
    "tilt_corrected": "tilt-corrected",
    "drift_corrected": "drift-corrected",
    "not_corrected": "uncorrected",
}


def reversed_mapping(mapping):
    """Swap each ``old: new`` pair of a mapping, per vocabulary or flat."""
    if all(isinstance(value, dict) for value in mapping.values()):
        return {slug: reversed_mapping(pairs) for slug, pairs in mapping.items()}
    return {new: old for old, new in mapping.items()}


def concept_columns(apps):
    """Yield ``(manager, column, vocabulary slug)`` for each column that holds an IHFC address.

    A single-valued concept field is a column of its own table. A many-valued one is the
    ``record`` column of its through table.
    """
    for model in apps.get_app_config("heat_flow").get_models():
        for field in model._meta.local_fields:
            if isinstance(field, ConceptField):
                for vocabulary in field.vocabulary:
                    yield model._default_manager, field.attname, vocabulary.uri
        for field in model._meta.local_many_to_many:
            if isinstance(field, MultiConceptField):
                through = field.remote_field.through
                column = f"{field.m2m_reverse_field_name()}_id"
                for vocabulary in field.vocabulary:
                    yield through._default_manager, column, vocabulary.uri


def rename_concepts(apps, mapping):
    """Point every stored address, and the concept it names, at the new identifier.

    The portal migrates before it loads the vocabularies, so a concept with the new
    identifier may not exist yet. Then the old concept is renamed in place, which
    keeps every foreign key valid, and the next load refreshes it. When the new concept
    is already loaded, the old one is dropped once nothing points at it.
    """
    Record = apps.get_model("controlled_vocabularies", "Record")
    for manager, column, vocabulary_uri in concept_columns(apps):
        renamed = mapping.get(vocabulary_uri.rsplit("/", 1)[-1], {})
        for old, new in renamed.items():
            manager.filter(**{column: f"{vocabulary_uri}/{old}"}).update(
                **{column: f"{vocabulary_uri}/{new}"}
            )
    for slug, renamed in mapping.items():
        for old, new in renamed.items():
            held = Record.objects.filter(uri=f"{IHFC}/{slug}/{old}")
            if Record.objects.filter(uri=f"{IHFC}/{slug}/{new}").exists():
                held.delete()
            else:
                held.update(uri=f"{IHFC}/{slug}/{new}", slug=new)


def rename_statuses(apps, mapping):
    """Rewrite the stored correction statuses with the identifiers in *mapping*."""
    corrections = apps.get_model("heat_flow", "HeatFlowCorrection")
    for old, new in mapping.items():
        corrections.objects.filter(status=old).update(status=new)


def forwards(apps, schema_editor):
    """Rename stored identifiers to the published ones."""
    rename_concepts(apps, CONCEPT_IDENTIFIERS)
    rename_statuses(apps, CORRECTION_STATUSES)


def backwards(apps, schema_editor):
    """Restore the identifiers the release before published."""
    rename_concepts(apps, reversed_mapping(CONCEPT_IDENTIFIERS))
    rename_statuses(apps, reversed_mapping(CORRECTION_STATUSES))


class Migration(migrations.Migration):
    dependencies = [
        ("controlled_vocabularies", "0003_record_links"),
        ("heat_flow", "0008_alter_correction_status_choices"),
    ]

    operations = [migrations.RunPython(forwards, backwards)]
