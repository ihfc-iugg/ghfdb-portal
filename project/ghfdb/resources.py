from itertools import islice

import tablib
from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelform_factory
from fairdm.contrib.contributors.models import Person
from fairdm.contrib.location.models import Point
from heat_flow.models import HeatFlow, HeatFlowInterval
from heat_flow.models.measurements import IntervalConductivity, SurfaceHeatFlow, ThermalGradient
from heat_flow.models.samples import HeatFlowSite
from import_export.fields import Field
from import_export.formats.base_formats import XLSX
from import_export.resources import ModelResource
from import_export.widgets import BooleanWidget, CharWidget, ForeignKeyWidget, ManyToManyWidget
from literature.models import LiteratureItem
from research_vocabs.fields import ConceptField, ConceptManyToManyField
from research_vocabs.models import Concept
from review.models import Review

# list of fields that contains controlled vocabulary choices that need to be cleaned
# fields correlate to spreadsheet columns
MULTI_CHOICE_FIELDS = [
    "explo_purpose",
    "q_method",
    "corr_IS_flag",
    "corr_T_flag",
    "probe_type",
    "geo_lithology",
    "geo_stratigraphy",
    "T_method_top",
    "T_method_bottom",
    "T_corr_top",
    "T_corr_bottom",
    "tc_source",
    "tc_location",
    "tc_method",
    "tc_saturation",
    "tc_pT_conditions",
    "tc_pT_function",
    "tc_strategy",
]

CHOICE_FIELDS = [
    *MULTI_CHOICE_FIELDS,
    "environment",
    "corr_HP_flag",
    "explo_method",
    "corr_SUR_flag",
    "corr_CONV_flag",
    "corr_HR_flag",
    "corr_PAL_flag",
    "corr_TOPO_flag",
    "corr_E_flag",
    "corr_S_flag",
    "corr_HP_flag",
]


def my_formfield_callback(field, **kwargs):
    """
    Custom form field callback for Django model fields.

    This function determines the appropriate form field to use for a given model field,
    particularly handling custom field types such as ConceptField and ConceptManyToManyField.
    It is typically used as the `formfield_callback` argument in Django admin or forms.

    Args:
        field: The Django model field instance for which a form field is required.

    Returns:
        A Django form field instance suitable for the provided model field.

    Notes:
        - If the field is an instance of ConceptField, it returns a SimpleConceptField
          initialized with the field's vocabulary.
        - If the field is an instance of ConceptManyToManyField, it returns a CustomMultiSelect
          initialized with the field's vocabulary.
        - For all other field types, it returns the default form field.
    """
    form_field = field.formfield(**kwargs)
    if isinstance(field, ConceptField):
        form_field = SimpleConceptField(vocabulary=field.vocabulary)
    elif isinstance(field, ConceptManyToManyField):
        form_field = CustomMultiSelect(vocabulary=field.vocabulary)
    return form_field


def clean_choices(value, choices):
    """
    Cleans and maps a semicolon-separated string of display labels to their corresponding values based on provided choices.

    Args:
        value (str): A semicolon-separated string containing display labels, possibly with square brackets.
        choices (Iterable[Tuple[Any, str]]): An iterable of (value, label) pairs, where 'label' is the display string and 'value' is the corresponding internal value.

    Returns:
        List[Any]: A list of values corresponding to the cleaned and matched display labels from the input string.
    """
    # Build a mapping from display label to internal value
    display_to_value = {label: value for value, label in choices}
    # Split the input string by semicolon to get individual labels
    values = value.split(";")
    cleaned_values = []
    for v in values:
        # Remove square brackets and whitespace from each label
        item = v.replace("[", "").replace("]", "").strip()
        if item:
            # Map the cleaned label to its value using the mapping
            cleaned_values.append(display_to_value.get(item))
    return cleaned_values


class SimpleConceptField(forms.ChoiceField):
    """
    A custom Django ChoiceField that supports mapping between display labels and database values
    using a provided vocabulary.

    Args:
        vocabulary (callable, optional): A callable that returns an object with a 'choices' attribute,
            which should be an iterable of (value, label) pairs. If provided, these choices are used
            for the field, and an internal mapping is created to invert labels to values.

    Attributes:
        vocabulary: The vocabulary object used to provide choices.
        inverted_choices (dict): A mapping from display labels to database values.

    Methods:
        to_python(value):
            Converts the display value (label) selected by the user back to the corresponding
            database value using the inverted_choices mapping. Returns None if the value is empty.
    """

    def __init__(self, *args, **kwargs):
        self.vocabulary = kwargs.pop("vocabulary", None)
        if self.vocabulary:
            # we invert the choices because spreadsheet values are displayed as labels
            # kwargs["choices"] = [(x[1], x[0]) for x in self.vocabulary().choices]
            kwargs["choices"] = self.vocabulary().choices
        self.inverted_choices = {label: value for value, label in kwargs["choices"]}
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        """Converts the display value to the database value."""
        if not value:
            return None
        return self.inverted_choices.get(value, value)


class CustomSelect(forms.Select):
    """
    A custom Django form widget that overrides the default Select widget to allow
    conversion from a display value back to the corresponding database value.

    Methods
    -------
    value_from_datadict(data, files, name):
        Converts the display value from the submitted form data back to the
        corresponding database value using the widget's choices mapping.
    """

    def value_from_datadict(self, data, files, name):
        """Converts the display value back to the database value."""
        display_to_value = {label: value for value, label in self.choices}
        display_value = data.get(name)
        return display_to_value.get(display_value, display_value)


class MultiSelectWidget(forms.SelectMultiple):
    """
    A custom Django form widget for selecting multiple values, using a semicolon (';') as the separator.

    This widget overrides the default behavior of `forms.SelectMultiple` to handle multiple selections
    represented as a single string separated by semicolons. It provides a method to convert the
    submitted string value back into a list of individual values.

    Attributes:
        separator (str): The character used to separate multiple values in the input string.

    Methods:
        value_from_datadict(data, files, name):
            Extracts and splits the input string from the form data into a list of values,
            trimming whitespace from each value.
    """

    separator = ";"

    def value_from_datadict(self, data, files, name):
        """Converts the display value back to the database value."""
        values = super().value_from_datadict(data, files, name)
        if values is None:
            return []
        cleaned = [v.strip() for v in values.split(self.separator)]
        return [v for v in cleaned if v != "unspecified"]


def clean_concept_value(values, separator=";"):
    if values is None:
        return []
    cleaned = [v.strip() for v in values.split(separator)]
    return [v for v in cleaned if v != "unspecified"]


def validate_concept(value, vocabulary, field="label"):
    queryset = Concept.get_for_vocabulary(vocabulary)
    choices = queryset.values_list(field, flat=True)
    invalid = []
    for val in value:
        if val not in choices:
            invalid.append(val)
    if invalid:
        raise ValidationError(f"The following values are not part of the {vocabulary().label()} vocabulary: {invalid}")


class CustomMultiSelect(forms.ModelMultipleChoiceField):
    """
    A custom Django form field for selecting multiple concepts from a specific vocabulary.

    This field extends `forms.ModelMultipleChoiceField` and uses a custom widget (`MultiSelectWidget`).
    It allows filtering the queryset based on a provided vocabulary and validates that selected values
    are valid labels within that vocabulary.

    Args:
        vocabulary (Optional[Callable or str]): The vocabulary to filter concepts by. If provided,
            the queryset is set to all concepts belonging to this vocabulary.

    Methods:
        clean(value):
            Validates that the provided values are valid labels in the queryset and returns
            the filtered queryset. Raises a ValidationError if any value is invalid.

    Attributes:
        vocabulary: The vocabulary used to filter the queryset.
        widget: The widget class used for rendering the field.
    """

    widget = MultiSelectWidget

    def __init__(self, *args, **kwargs):
        self.vocabulary = kwargs.pop("vocabulary", None)
        if self.vocabulary:
            kwargs["queryset"] = Concept.get_for_vocabulary(self.vocabulary)
        super().__init__(*args, **kwargs)

    def clean(self, value):
        """Converts the display value to the database value."""
        if not value:
            return self.queryset.none()

        choices = self.queryset.values_list("label", flat=True)
        invalid = []
        for val in value:
            if val not in choices:
                invalid.append(val)
        if invalid:
            raise ValidationError(
                f"The following values are not part of the {self.vocabulary().label()} vocabulary: {invalid}"
            )
        return self.queryset.filter(label__in=value)
        # return [self.queryset.get(pk=val) for val in value if val is not None]

    # def value_from_datadict(self, data, files, name):
    #     """Converts the display value back to the database value."""
    #     values = super().value_from_datadict(data, files, name)
    #     display_to_value = {label: value for value, label in self.choices}
    #     display_value = data.get(name)
    #     return display_to_value.get(display_value, display_value)


class YesNoWidget(BooleanWidget):
    """
    An extension of the default Boolean widget that handles more true/false values including "yes" and "no".

    This widget is useful for parsing user input or data sources where boolean values may be represented in multiple formats.
    """

    TRUE_VALUES = ["1", 1, True, "true", "TRUE", "True", "Yes", "yes", "YES", "[Yes]"]
    FALSE_VALUES = ["0", 0, False, "false", "FALSE", "False", "No", "no", "NO", "[No]"]


class ForeignObjectWidget(ForeignKeyWidget):
    """
    A custom widget for handling foreign key relationships with dynamic field mapping and form creation.

    This widget extends `ForeignKeyWidget` to allow for additional flexibility when importing or processing
    data that involves foreign key relationships. It supports mapping fields from the input row to the
    target model's fields and dynamically generates a model form for validation and object creation.

    Attributes:
        field_map (dict): A mapping from the target model's field names to the corresponding keys in the input row.
        factory_kwargs (dict): Additional keyword arguments to pass to the `modelform_factory` function.

    Args:
        model (Model, optional): The Django model class to associate with this widget. Defaults to `HeatFlowInterval` if not provided.
        field_map (dict, optional): A dictionary mapping model field names to input row keys.
        **kwargs: Additional keyword arguments, including `factory_kwargs` for form factory customization.

    Methods:
        clean(value, row=None, *args, **kwargs):
            Processes the input value and row, applies field mapping, dynamically creates a model form,
            validates the data, and returns the saved model instance. Raises a ValueError if validation fails.

    Raises:
        ValueError: If the generated form is not valid, with form errors included in the exception.
    """

    def __init__(self, model=None, field_map=None, **kwargs):
        self.field_map = field_map
        self.factory_kwargs = kwargs.pop("factory_kwargs", {})
        super().__init__(model=model or HeatFlowInterval, **kwargs)

    def clean(self, value, row=None, *args, **kwargs):
        if self.field_map:
            # make a copy of row data to avoid modifying the original row
            rowx = row.copy()
            # use the field mapping to add additional row columns to the row data
            for key, val in self.field_map.items():
                rowx[key] = row.get(val)

        defaults = {
            "exclude": ["status"],
            "formfield_callback": my_formfield_callback,
        }

        defaults.update(self.factory_kwargs)

        form_class = modelform_factory(
            self.model,
            **defaults,
        )

        form = form_class(rowx)
        if form.is_valid():
            obj = form.save()
            return obj

        raise ValueError(form.errors)


class ConceptWidget(CharWidget):
    """
    A widget for handling concept choices with display-to-value mapping.

    Inherits from:
        CharWidget

    Args:
        choices (list of tuple): Optional. A list of (value, label) pairs representing the available choices.

    Attributes:
        choices (list of tuple): The list of available choices.
        display_to_value (dict): A mapping from display labels to their corresponding values.

    Methods:
        clean(value, row=None, **kwargs):
            Cleans and validates the input value. Converts "unspecified" to None, checks for empty values,
            and maps the display label to its corresponding value. Raises ValueError if the value is invalid.

    Raises:
        ValueError: If the provided value does not correspond to any valid choice.
    """

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop("choices", [])
        self.display_to_value = {label: value for value, label in self.choices}
        super().__init__(*args, **kwargs)

    def clean(self, value, row=None, **kwargs):
        if value == "unspecified":
            value = None
        val = super().clean(value, row, **kwargs)
        if val is None or val == "":
            return None

        result = self.display_to_value.get(val)
        if result is None:
            raise ValueError("Invalid choice.")
        return result


class MultiConceptWidget(ManyToManyWidget):
    """
    A widget for handling ManyToMany relationships with Concept objects filtered by a specific vocabulary.

    This widget is designed for use with import/export operations, allowing for the conversion between
    a delimited string of concept names and the corresponding queryset of Concept instances, restricted
    to a given vocabulary.

    Args:
        vocabulary: The vocabulary instance to filter Concept objects by.
        separator (str, optional): The delimiter used to separate concept names in the input/output string. Defaults to ";".
        field (str, optional): The field of the Concept model to use for matching and rendering. Defaults to "name".

    Methods:
        clean(value, row=None, *args, **kwargs):
            Converts a delimited string of concept names into a queryset of Concept objects filtered by the specified vocabulary.
            Returns an empty queryset if the input value is empty.

        render(value, obj=None):
            Converts a queryset of Concept objects into a delimited string of concept names.
            Returns an empty string if the input value is empty.
    """

    def __init__(self, vocabulary, separator=";", field="name"):
        super().__init__(Concept, separator=separator, field=field)
        self.vocabulary = vocabulary
        self.vocabulary_name = vocabulary.scheme().name
        self.queryset = Concept.get_for_vocabulary(vocabulary.__class__)

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return self.queryset.none()
        values = clean_concept_value(value, self.separator)
        validate_concept(values, self.vocabulary.__class__)
        return self.queryset.filter(label__in=values)

        # filter_kwargs = {
        #     f"{self.field}__in": names,
        #     "vocabulary__name": self.vocabulary_name,
        # }
        # return self.model.objects.filter(**filter_kwargs)

    def render(self, value, obj=None):
        if not value:
            return ""
        return self.separator.join(getattr(obj, self.field) for obj in value.all())


class GHFDBImportFormat(XLSX):
    """This is a custom import format (django-import-export) that will properly read the GHFDB spreadsheet template. It
    uses a worksheet by the name 'data list', searches for headers on the 6th row and skips the first 8 rows."""

    header_row = 6
    skip_rows = 8

    def create_dataset(self, in_stream):
        """
        Create dataset from first sheet.
        """
        from io import BytesIO

        import openpyxl

        # 'data_only' means values are read from formula cells, not the formula itself
        xlsx_book = openpyxl.load_workbook(BytesIO(in_stream), read_only=True, data_only=True)

        dataset = tablib.Dataset()
        sheet = xlsx_book["data list"]

        # get the headers from the 6th row of the worksheet
        dataset.headers = [cell.value for cell in sheet[self.header_row]]

        # iterate over rows and append to dataset
        # skip the first 8 rows
        for row in islice(sheet.rows, self.skip_rows, None):
            row_values = [cell.value for cell in row]
            dataset.append(row_values)
        return dataset


class GHFDBResource(ModelResource):
    """This is a custom resource that will import the GHFDB spreadsheet structure into the 4 models defined in heat_flow.models.

    django-import-export does not have builtin way to import data into multiple models from a single spreadsheet. To solve this, we will
    import the HeatFlow data using the typical method of django-import-export, and we will create the relationships in the
    before_import_row method using standard forms.

    """

    q = Field("parent__value", readonly=True)
    q_uncertainty = Field("parent__uncertainty", readonly=True)

    # Parent fields
    # name = Field("parent__sample__name", readonly=True)
    lat_NS = Field("parent__sample__location__latitude", readonly=True)
    lon_EW = Field("parent__sample__location__longitude", readonly=True)
    elevation = Field("parent__sample__location__elevation", readonly=True)
    environment = Field("parent__sample__environment", readonly=True)
    # p_comment = Field("parent__comment", readonly=True)
    corr_HP_flag = Field("parent__correction_flag", readonly=True)
    total_depth_MD = Field("parent__sample__length", readonly=True)
    total_depth_TVD = Field("parent__sample__vertical_depth", readonly=True)
    explo_method = Field("parent__sample__explo_method", readonly=True)
    explo_purpose = Field("sample__explo_purpose", readonly=True)

    # uses the ForeignObjectWidget to create a ThermalGradient instance and associate it with the import
    thermal_gradient = Field(
        "thermal_gradient",
        widget=ForeignObjectWidget(
            model=ThermalGradient,
            field_map={
                "value": "T_grad_mean",
                "uncertainty": "T_grad_uncertainty",
                "corrected_value": "T_grad_mean_cor",
                "corrected_uncertainty": "T_grad_uncertainty_cor",
                "method_top": "T_method_top",
                "method_bottom": "T_method_bottom",
                "shutin_top": "T_shutin_top",
                "shutin_bottom": "T_shutin_bottom",
                "correction_top": "T_corr_top",
                "correction_bottom": "T_corr_bottom",
                "number": "T_number",
            },
        ),
    )

    # uses the ForeignObjectWidget to create an IntervalConductivity instance and associate it with the import
    thermal_conductivity = Field(
        "thermal_conductivity",
        widget=ForeignObjectWidget(
            model=IntervalConductivity,
            field_map={
                "value": "tc_mean",
                "uncertainty": "tc_uncertainty",
                "source": "tc_source",
                "location": "tc_location",
                "method": "tc_method",
                "saturation": "tc_saturation",
                "pT_conditions": "tc_pT_conditions",
                "pT_function": "tc_pT_function",
                "strategy": "tc_strategy",
                "number": "tc_number",
            },
        ),
    )

    # Child fields
    qc = Field("value")
    qc_uncertainty = Field("uncertainty")
    q_method = Field("method", widget=MultiConceptWidget(vocabulary=HeatFlow.method_vocab))
    q_top = Field("top")
    q_bottom = Field("bottom")
    probe_penetration = Field("probe_penetration")
    # publication_reference = Field("dataset__review__reference")
    # data_reference = Field("dataset__reference")
    relevant_child = Field("relevant_child", widget=YesNoWidget())
    c_comment = Field("c_comment")

    corr_IS_flag = Field(
        "corr_IS_flag", widget=MultiConceptWidget(vocabulary=HeatFlow.corr_IS_flag_vocab, field="label")
    )
    corr_T_flag = Field("corr_T_flag", widget=MultiConceptWidget(vocabulary=HeatFlow.corr_T_flag_vocab))
    corr_S_flag = Field("corr_S_flag", widget=ConceptWidget(choices=HeatFlow.corr_S_flag_vocab.choices))
    corr_E_flag = Field("corr_E_flag", widget=ConceptWidget(choices=HeatFlow.corr_E_flag_vocab.choices))
    corr_TOPO_flag = Field("corr_TOPO_flag", widget=ConceptWidget(choices=HeatFlow.corr_TOPO_flag_vocab.choices))
    corr_PAL_flag = Field("corr_PAL_flag", widget=ConceptWidget(choices=HeatFlow.corr_PAL_flag_vocab.choices))
    corr_SUR_flag = Field("corr_SUR_flag", widget=ConceptWidget(choices=HeatFlow.corr_SUR_flag_vocab.choices))
    corr_CONV_flag = Field("corr_CONV_flag", widget=ConceptWidget(choices=HeatFlow.corr_CONV_flag_vocab.choices))
    corr_HR_flag = Field("corr_HR_flag", widget=ConceptWidget(choices=HeatFlow.corr_HR_flag_vocab.choices))

    expedition = Field("expedition")
    probe_type = Field("probe_type", widget=MultiConceptWidget(vocabulary=HeatFlow.probe_type_vocab))
    probe_length = Field("probe_length")
    probe_tilt = Field("probe_tilt")
    water_temperature = Field("water_temperature")
    # geo_lithology = Field("sample__lithology")
    # geo_stratigraphy = Field("sample__age")

    # Temperature gradient fields
    T_grad_mean = Field("thermal_gradient__value", readonly=True)
    T_grad_uncertainty = Field("thermal_gradient__uncertainty", readonly=True)
    T_grad_mean_cor = Field("thermal_gradient__corrected_value", readonly=True)
    T_grad_uncertainty_cor = Field("thermal_gradient__corrected_uncertainty", readonly=True)
    T_method_top = Field("thermal_gradient__method_top", readonly=True)
    T_method_bottom = Field("thermal_gradient__method_bottom", readonly=True)
    T_shutin_top = Field("thermal_gradient__shutin_top", readonly=True)
    T_shutin_bottom = Field("thermal_gradient__shutin_bottom", readonly=True)
    T_corr_top = Field("thermal_gradient__correction_top", readonly=True)
    T_corr_bottom = Field("thermal_gradient__correction_bottom", readonly=True)
    T_number = Field("thermal_gradient__number", readonly=True)

    q_date = Field("date_acquired", widget=CharWidget())

    # # Thermal conductivity fields
    tc_mean = Field("thermal_conductivity__value", readonly=True)
    tc_uncertainty = Field("thermal_conductivity__uncertainty", readonly=True)
    tc_source = Field("thermal_conductivity__source", readonly=True)
    tc_location = Field("thermal_conductivity__location", readonly=True)
    tc_method = Field("thermal_conductivity__method", readonly=True)
    tc_saturation = Field("thermal_conductivity__saturation", readonly=True)
    tc_pT_conditions = Field("thermal_conductivity__pT_conditions", readonly=True)
    tc_pT_function = Field("thermal_conductivity__pT_function", readonly=True)
    tc_number = Field("thermal_conductivity__number", readonly=True)
    tc_strategy = Field("thermal_conductivity__strategy", readonly=True)

    country = Field("heat_flow_site__country", readonly=True)
    region = Field("heat_flow_site__region", readonly=True)
    continent = Field("heat_flow_site__continent", readonly=True)
    domain = Field("heat_flow_site__domain", readonly=True)

    # Ref_IGSN = Field("sample__dataset__reference")

    class Meta:
        model = HeatFlow
        import_order = ["hf_site", "sample"]
        clean_model_instances = True
        store_instance = True

    def __init__(self, *args, **kwargs):
        self.dataset = kwargs.pop("dataset")
        super().__init__(*args, **kwargs)

    def before_import(self, dataset, **kwargs):
        # rather than fetch reviewers for each imported row, we fetch them once and store them for later use
        # This is useful for large datasets to avoid repeated database queries but will only work if the same reviewers are listed on each column.
        # NOTE: Data recorded in the review columns are too heterogeneous to be reliably imported.
        # self.review = self.get_review(dataset)
        # self.dataset.review = self.review
        # self.dataset.save()
        pass

    def import_data(self, dataset, dry_run=False, **kwargs):
        # Force errors to be raised instead of being caught
        # kwargs["raise_errors"] = True
        return super().import_data(dataset, dry_run=dry_run, **kwargs)

    def clean_choices(self, row):
        """Removes brackets and whitespace from choice fields in the row."""
        for field in CHOICE_FIELDS:
            if row.get(field):
                # Clean the choices for fields that are controlled vocabularies
                row[field] = row[field].replace("[", "").replace("]", "").strip()

    def before_import_row(self, row, **kwargs):
        """Hook to modify the row before it is imported."""

        self.clean_choices(row)
        hp_flag = row.get("corr_HP_flag").lower()
        row["corr_HP_flag"] = hp_flag == "yes"

        row["dataset"] = self.dataset.pk
        row["thermal_gradient"] = None
        row["thermal_conductivity"] = None

        # first, we get the location because we will attach it to both the heat flow site and the heat flow interval
        # sample types
        row["location"] = self.get_location(row).pk

        # next, we create the HeatFlowSite and store it in the row as sample. When we create the SurfaceHeatFlow object,
        # this sample will be attached.
        row["heat_flow_site"] = self.get_heat_flow_site(row).pk

        # create a SurfaceHeatFlow instance and store as parent in the row. It will be found during creation of the
        # HeatFlow child instance
        row["parent"] = self.get_parent_heat_flow(row).pk

        # overwrite the previous sample with the sample for the HeatFlowInterval. This will be attached to the HeatFlow
        # child instance
        row["sample"] = self.get_heat_flow_interval(row).pk

    def get_review(self, dataset):
        # NOTE: need to incorporate Review_date column from the dataset
        # make sure the dataset has the required columns
        first_row = dataset.dict[0]
        if "Reviewer_name" not in first_row:
            raise ValueError("Reviewer_name column is missing from the dataset.")
        if "publication_reference" not in first_row:
            raise ValueError("publication_reference column is missing from the dataset.")

        # Collect all unique reviewer names and publication references from the dataset
        reviewer_names = set()
        literature_item = set()
        for row in dataset.dict:
            if names := row.get("Reviewer_name"):
                names = [name.strip() for name in names.split(",")]  # clean up names
                reviewer_names.update(names)  # add names to the set
            if pub_ref := row.get("publication_reference"):
                literature_item.add(pub_ref)

        # check to make sure only one publication is provided per upload
        if len(literature_item) > 1:
            raise ValueError(
                "Multiple publication references found in the dataset. "
                "Please ensure that all rows have the same publication reference."
            )
        # if no publication reference is provided, raise an error
        elif not literature_item:
            raise ValueError(
                "No publication reference found in the dataset. "
                "Please ensure that all rows have a publication reference."
            )

        # get or create Person instances for each reviewer name
        reviewer_pks = []
        for name in reviewer_names:
            contributor, created = Person.objects.get_or_create(
                name=name,
            )
            reviewer_pks.append(contributor.pk)

        # get a LiteratureItem instance for the publication reference
        citation_key = literature_item.pop() if literature_item else None
        publication_reference, created = LiteratureItem.objects.get_or_create(
            citation_key=citation_key,
        )
        # create or update the Review instance for the dataset
        review, created = Review.objects.update_or_create(
            dataset=self.dataset,
            defaults={
                "status": 2,  # Assuming '2' means 'accepted'
                "literature": publication_reference,
            },
        )
        review.reviewers.set(reviewer_pks)
        return review

    def get_location(self, row):
        loc, created = Point.objects.update_or_create(
            y=row.get("lat_NS"),
            x=row.get("long_EW"),
        )
        return loc

    def get_heat_flow_site(self, row):
        return ForeignObjectWidget(
            model=HeatFlowSite,
            field_map={
                "lithology": "geo_lithology",
                "age": "geo_stratigraphy",
                "length": "total_depth_MD",
                "vertical_depth": "total_depth_TVD",
                "country": "Country",
                "region": "Region",
                "continent": "Continent",
                "domain": "Domain",
            },
            factory_kwargs={
                "exclude": [
                    "status",
                    "azimuth",
                    "inclination",
                    "type",
                    "elevation_datum",
                ],
            },
        ).clean(None, row)

    def get_parent_heat_flow(self, row):
        return ForeignObjectWidget(
            model=SurfaceHeatFlow,
            field_map={
                "sample": "heat_flow_site",
                "value": "q",
                "uncertainty": "q_uncertainty",
                "method": "q_method",
            },
            factory_kwargs={
                "exclude": [
                    "image",
                    "lithology",
                    "age",
                    "status",
                ],
                # "widgets": {
                #     "corr_HP_flag": YesNoWidget(),
                # },
            },
        ).clean(None, row)

    def get_heat_flow_interval(self, row):
        # To include lithology and age or not to.
        # That is the question.
        return ForeignObjectWidget(
            model=HeatFlowInterval,
            field_map={
                "lithology": "geo_lithology",
                "age": "geo_stratigraphy",
                "top": "q_top",
                "bottom": "q_bottom",
            },
            factory_kwargs={
                "exclude": [
                    "image",
                    "status",
                ],
            },
        ).clean(None, row)

    # def before_save_instance(self, instance, row, **kwargs):
    # x = 8

    # instance.full_clean()  # Validate the instance
    # try:
    # except ValidationError as e:
    # raise ValueError(f"Validation failed: {e}")

    # def after_import_row(self, row, row_result, row_number=None, **kwargs):
    # return super().after_import_row(row, row_result, row_number, **kwargs)

    # def before_save_instance(self, instance, using_transactions, dry_run):
    #     return super().before_save_instance(instance, using_transactions, dry_run)

    # def get_import_fields(self):
    #     return list(super().get_import_fields()) + ["dataset"]

    # def after_import(self, dataset, result, **kwargs):
    #     """
    #     Hook to perform actions after the import is complete.
    #     """
    #     # Here you can add any post-import actions, such as logging or cleanup
    #     # print(f"Imported {result.totals['imported']} rows successfully.")
    #     # print(f"Skipped {result.totals['skipped']} rows.")
    #     # print(f"Errors: {result.errors}")
    #     x = 0
