"""Smoke tests for the GHFDB proxy models and the fixtures every story takes.
"""

import pathlib

import pytest

pytestmark = pytest.mark.ghfdb


class TestGHFDBProxyModels:
    """GHFDB proxy models must expose the correct Meta configuration."""

    def test_ghfdb_proxy_meta(self):
        """T018: GHFDBChild must be a proxy model with the correct verbose_name."""
        from project.ghfdb.models import GHFDBChild

        assert GHFDBChild._meta.proxy is True
        assert str(GHFDBChild._meta.verbose_name) == "GHFDB Child"
        assert str(GHFDBChild._meta.verbose_name_plural) == "GHFDB Children"

    def test_ghfdb_parent_proxy_meta(self):
        """T074 (US1b): GHFDBParent must be a proxy model with the correct verbose_name."""
        from project.ghfdb.models import GHFDBParent

        assert GHFDBParent._meta.proxy is True
        assert str(GHFDBParent._meta.verbose_name) == "GHFDB Parent"
        assert str(GHFDBParent._meta.verbose_name_plural) == "GHFDB Parents"


class TestGHFDBChildModel:
    """The ``GHFDBChild`` proxy's ``Meta`` configuration (T011, T012)."""

    def test_proxy_adds_no_table(self):
        """T011: the proxy shares ``HeatFlow``'s table and declares no
        local field of its own."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.models import GHFDBChild

        assert GHFDBChild._meta.proxy is True
        assert GHFDBChild._meta.db_table == HeatFlow._meta.db_table
        assert GHFDBChild._meta.local_fields == []

    def test_meta_carries_translated_verbose_names(self):
        """T012: both verbose names are lazy translations that name the
        published determination view rather than repeating ``HeatFlow``'s
        own name."""
        from django.utils.functional import Promise
        from heat_flow.models import HeatFlow

        from project.ghfdb.models import GHFDBChild

        verbose_name = GHFDBChild._meta.verbose_name
        verbose_name_plural = GHFDBChild._meta.verbose_name_plural

        assert isinstance(verbose_name, Promise)
        assert isinstance(verbose_name_plural, Promise)
        assert str(verbose_name) == "GHFDB Child"
        assert str(verbose_name_plural) == "GHFDB Children"
        assert str(verbose_name) != str(HeatFlow._meta.verbose_name)


class TestGHFDBParentModel:
    """The ``GHFDBParent`` proxy's ``Meta`` configuration (T042, T043)."""

    def test_proxy_adds_no_table(self):
        """T042: the proxy shares ``ParentHeatFlow``'s table and declares no
        local field of its own."""
        from heat_flow.models import ParentHeatFlow

        from project.ghfdb.models import GHFDBParent

        assert GHFDBParent._meta.proxy is True
        assert GHFDBParent._meta.db_table == ParentHeatFlow._meta.db_table
        assert GHFDBParent._meta.local_fields == []

    def test_meta_carries_translated_verbose_names(self):
        """T043: both verbose names are lazy translations that name the
        published site view rather than repeating ``ParentHeatFlow``'s own
        name."""
        from django.utils.functional import Promise
        from heat_flow.models import ParentHeatFlow

        from project.ghfdb.models import GHFDBParent

        verbose_name = GHFDBParent._meta.verbose_name
        verbose_name_plural = GHFDBParent._meta.verbose_name_plural

        assert isinstance(verbose_name, Promise)
        assert isinstance(verbose_name_plural, Promise)
        assert str(verbose_name) == "GHFDB Parent"
        assert str(verbose_name_plural) == "GHFDB Parents"
        assert str(verbose_name) != str(ParentHeatFlow._meta.verbose_name)

    def test_no_dictionary_accessor(self):
        """T122 (D7): ``as_dict()`` has no caller and raises on every
        published column that exists only as an annotation. Removed."""
        from project.ghfdb.models import GHFDBParent

        assert not hasattr(GHFDBParent, "as_dict")


class TestFixtures:
    """The Phase 1 fixture contracts every later phase is held to (T002-T010)."""

    def test_vocabulary_concepts_are_present(self, db):
        """T002: the session concept load covers every vocabulary this
        feature filters on."""
        from heat_flow.vocabularies import (
            ExplorationMethod,
            ExplorationPurpose,
            GeographicEnvironment,
        )
        from research_vocabs.models import Concept

        for vocabulary in (GeographicEnvironment, ExplorationMethod, ExplorationPurpose):
            assert Concept.get_for_vocabulary(vocabulary).exists(), (
                f"no concepts preloaded for {vocabulary.__name__}"
            )

    def test_dataset_fixture_is_saved(self, dataset):
        """T003: ``dataset`` wraps ``DatasetFactory`` and is persisted."""
        assert dataset.pk is not None

    def test_published_chain_is_complete(self, published_chain):
        """T004: every relationship the chain names resolves, and both
        published identifiers are set."""
        child = published_chain
        parent = child.parent
        interval = child.sample
        site = interval.site

        assert site is not None
        assert hasattr(interval, "probe_metadata")
        assert child.thermal_gradient is not None
        assert child.thermal_conductivity is not None
        assert child.corrections.count() == 9
        assert parent.ghfdb_id is not None
        assert child.ghfdb_id is not None

    def test_published_chains_builds_the_number_asked_for(self, published_chains):
        """T005: the callable builds exactly as many chains as it is asked
        for, at two different sizes (R2)."""
        from heat_flow.models import HeatFlow

        first_batch = published_chains(2)
        assert len(first_batch) == 2
        assert HeatFlow.objects.count() == 2

        second_batch = published_chains(4)
        assert len(second_batch) == 4
        assert HeatFlow.objects.count() == 6

    def test_unpublished_chain_has_no_published_identifier(self, unpublished_chain):
        """T006: neither level carries a published identifier (SC-005)."""
        assert unpublished_chain.ghfdb_id is None
        assert unpublished_chain.parent.ghfdb_id is None

    def test_partial_chains_omit_only_what_they_name(
        self,
        chain_without_gradient,
        chain_without_conductivity,
        chain_without_probe_metadata,
        chain_missing_correction,
    ):
        """T007: each partial-chain fixture omits exactly the one piece it
        names, and every other relationship still resolves."""
        assert chain_without_gradient.thermal_gradient is None
        assert chain_without_gradient.thermal_conductivity is not None
        assert hasattr(chain_without_gradient.sample, "probe_metadata")
        assert chain_without_gradient.corrections.count() == 9

        assert chain_without_conductivity.thermal_conductivity is None
        assert chain_without_conductivity.thermal_gradient is not None
        assert hasattr(chain_without_conductivity.sample, "probe_metadata")
        assert chain_without_conductivity.corrections.count() == 9

        assert not hasattr(chain_without_probe_metadata.sample, "probe_metadata")
        assert chain_without_probe_metadata.thermal_gradient is not None
        assert chain_without_probe_metadata.thermal_conductivity is not None
        assert chain_without_probe_metadata.corrections.count() == 9

        missing = chain_missing_correction("IS")
        assert not missing.corrections.filter(correction_type="IS").exists()
        assert missing.corrections.count() == 8
        assert missing.thermal_gradient is not None
        assert missing.thermal_conductivity is not None
        assert hasattr(missing.sample, "probe_metadata")

    def test_sites_by_contribution_covers_the_four_shapes(self, sites_by_contribution):
        """T008: the four contribution shapes SC-004 names, and one site
        carrying two exploration purposes so the many-valued parent column
        is exercised."""
        all_contributing = sites_by_contribution["all_contributing"]
        some_contributing = sites_by_contribution["some_contributing"]
        none_contributing = sites_by_contribution["none_contributing"]
        no_determinations = sites_by_contribution["no_determinations"]

        assert all_contributing.children.count() == 2
        assert all_contributing.children.filter(is_relevant=True).count() == 2

        assert some_contributing.children.count() == 2
        assert some_contributing.children.filter(is_relevant=True).count() == 1

        assert none_contributing.children.count() == 2
        assert none_contributing.children.filter(is_relevant=True).count() == 0

        assert no_determinations.children.count() == 0

        purpose_counts = {
            parent.sample.explo_purpose.count()
            for parent in sites_by_contribution.values()
        }
        assert 2 in purpose_counts

    def test_staff_client_reaches_the_admin_index(self, staff_client):
        """T009: the staff client holds enough permission to reach the admin
        index."""
        from django.urls import reverse

        response = staff_client.get(reverse("admin:index"))
        assert response.status_code == 200


class TestConstantQueryCount:
    """T010: the query-constancy gate (R2), proven against the defect it
    exists to catch rather than only against the passing case."""

    def test_a_linear_callable_is_rejected(self, constant_query_count, db):
        """A callable whose query count grows with row count must fail the
        gate."""
        from django.contrib.contenttypes.models import ContentType

        state = {"rows": 0}

        def build(count):
            state["rows"] = count

        def call():
            for _ in range(state["rows"]):
                ContentType.objects.count()

        with pytest.raises(pytest.fail.Exception):
            constant_query_count(build, call)

    def test_a_constant_callable_is_accepted(self, constant_query_count, db):
        """A callable whose query count does not depend on row count must
        pass the gate."""
        from django.contrib.contenttypes.models import ContentType

        def build(count):
            pass

        def call():
            ContentType.objects.count()

        constant_query_count(build, call)


class TestSuiteHealth:
    """SC-011 is a statement about the suite, so it needs an assertion about
    the suite rather than about any one test.

    The decorators are found by parsing each module rather than by searching
    its text. A text search would match this module's own assertions, and
    excluding this module to work around that would leave the gate with a hole
    exactly where someone would put an expected failure to quiet it.
    """

    #: Import and export are `003-ghfdb-import-export`'s, and thirteen of its
    #: tests are expected to fail until the published column vocabulary is
    #: settled there. Named rather than silently swept up, so a new expected
    #: failure in this feature's own modules cannot hide among them.
    OTHER_FEATURES = ("test_resources",)

    @staticmethod
    def mark_names(expr):
        """Every `pytest.mark.<name>` attribute reachable from *expr*.

        *expr* is either one decorator-shaped node (`pytest.mark.xfail` or
        `pytest.mark.xfail(...)`) or a list/tuple of them — a module-level
        `pytestmark` assignment may be either shape.
        """
        import ast

        if isinstance(expr, ast.List | ast.Tuple):
            found: set[str] = set()
            for element in expr.elts:
                found |= TestSuiteHealth.mark_names(element)
            return found
        target = expr.func if isinstance(expr, ast.Call) else expr
        if isinstance(target, ast.Attribute):
            return {target.attr}
        return set()

    @classmethod
    def marks_in_source(cls, source):
        """Every `pytest.mark.<name>` in *source*, as a set of names.

        Walks two shapes: a decorator on a function or class, and a
        module-level `pytestmark = pytest.mark.<name>(...)` assignment —
        every module in this suite carries its marker the second way, so a
        gate that only walked decorator lists would never see it (F8).
        """
        import ast

        found: set[str] = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.FunctionDef | ast.ClassDef):
                for decorator in node.decorator_list:
                    found |= cls.mark_names(decorator)
            elif isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "pytestmark"
                for target in node.targets
            ):
                found |= cls.mark_names(node.value)
        return found

    @classmethod
    def marks(cls, path):
        """Every `pytest.mark.<name>` in *path*, as a set of names."""
        return cls.marks_in_source(path.read_text())

    def modules(self):
        root = pathlib.Path(__file__).parent
        return [
            path
            for path in root.rglob("*.py")
            if not any(part in self.OTHER_FEATURES for part in path.parts)
        ]

    def test_no_test_in_this_feature_is_expected_to_fail(self):
        """T120: an expected failure records a defect someone chose to live
        with. This feature is not allowed to leave one behind."""
        offenders = [path.name for path in self.modules() if "xfail" in self.marks(path)]
        assert offenders == []

    def test_no_test_in_this_feature_is_unconditionally_skipped(self):
        """T120: a skip that can never fire reads as coverage and is not —
        checked against both spellings, ``skip`` and the conditional
        ``skipif``, either of which reads as coverage while proving nothing
        if it can never fire (F8)."""
        offenders = [
            path.name for path in self.modules() if self.marks(path) & {"skip", "skipif"}
        ]
        assert offenders == []

    def test_the_gate_catches_a_module_level_expected_failure(self):
        """F8: proves the gate against the exact defect it exists to catch.
        ``marks()`` used to walk decorator lists only, so a module-level
        ``pytestmark = pytest.mark.xfail(...)`` — the shape every module in
        this suite actually uses for its own marker — slipped past it
        silently. A gate with no proof against its own defect is what T010
        exists to avoid."""
        source = "import pytest\n\npytestmark = pytest.mark.xfail(reason='x')\n"
        assert "xfail" in self.marks_in_source(source)

    def test_the_named_exclusion_is_real(self):
        """The exclusion above is honest only if it names something that
        exists. If import and export stop carrying expected failures, this
        fails and the exclusion comes out rather than sitting unexplained."""
        resources = pathlib.Path(__file__).parent / "test_resources"
        carriers = [
            path for path in resources.rglob("*.py") if "xfail" in self.marks(path)
        ]
        assert carriers, (
            "no expected failures remain under test_resources — remove the "
            "exclusion from OTHER_FEATURES rather than leaving it unexplained"
        )
