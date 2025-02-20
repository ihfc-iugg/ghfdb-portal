from itertools import islice

import tablib
from django.forms import modelform_factory
from fairdm.contrib.location.models import Point
from import_export.fields import Field
from import_export.formats.base_formats import XLSX
from import_export.resources import ModelResource
from import_export.widgets import BooleanWidget, CharWidget, ForeignKeyWidget

from heat_flow.models.measurements import IntervalConductivity, SurfaceHeatFlow, ThermalGradient
from heat_flow.models.samples import HeatFlowSite

from .importer import CustomSelect
from .models import HeatFlow, HeatFlowInterval


class YesNoWidget(BooleanWidget):
    TRUE_VALUES = ["1", 1, True, "true", "TRUE", "True", "Yes", "yes", "YES"]
    FALSE_VALUES = ["0", 0, False, "false", "FALSE", "False", "No", "no", "NO"]


class SampleWidget(ForeignKeyWidget):
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

        defaults = {"exclude": ["status"]}

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

    # sample = Field(
    #     "sample",
    #     widget=SampleWidget(
    #         model=HeatFlowInterval,
    #         field_map={
    #             "top": "q_top",
    #             "bottom": "q_bottom",
    #             "lithology": "geo_lithology",
    #             "age": "geo_stratigraphy",
    #         },
    #         factory_kwargs={
    #             "exclude": [
    #                 "image",
    #                 "lithology",
    #                 "age",
    #                 "status",
    #             ],
    #         },
    #     ),
    # )

    thermal_gradient = Field(
        "thermal_gradient",
        widget=SampleWidget(
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
            factory_kwargs={
                "exclude": ["status"],
                "widgets": {
                    "method_top": CustomSelect,
                    "method_bottom": CustomSelect,
                    "correction_top": CustomSelect,
                    "correction_bottom": CustomSelect,
                },
            },
        ),
    )

    thermal_conductivity = Field(
        "thermal_conductivity",
        widget=SampleWidget(
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
                "number": "tc_number",
            },
            factory_kwargs={
                "exclude": ["status"],
                "widgets": {
                    "source": CustomSelect,
                    "location": CustomSelect,
                    "method": CustomSelect,
                    "saturation": CustomSelect,
                    "pT_conditions": CustomSelect,
                    "pT_function": CustomSelect,
                    "strategy": CustomSelect,
                },
            },
        ),
    )

    # Child fields
    qc = Field("value")
    qc_uncertainty = Field("uncertainty")
    q_method = Field("method", widget=ConceptWidget(choices=HeatFlow.method_vocab.choices))
    q_top = Field("top")
    q_bottom = Field("bottom")
    probe_penetration = Field("probe_penetration")
    # publication_reference = Field("dataset__review__reference")
    # data_reference = Field("dataset__reference")
    relevant_child = Field("relevant_child", widget=YesNoWidget())
    c_comment = Field("c_comment")

    corr_IS_flag = Field("corr_IS_flag", widget=ConceptWidget(choices=HeatFlow.corr_IS_flag_vocab.choices))
    corr_T_flag = Field("corr_T_flag", widget=ConceptWidget(choices=HeatFlow.corr_T_flag_vocab.choices))
    corr_S_flag = Field("corr_S_flag", widget=ConceptWidget(choices=HeatFlow.corr_S_flag_vocab.choices))
    corr_E_flag = Field("corr_E_flag", widget=ConceptWidget(choices=HeatFlow.corr_E_flag_vocab.choices))
    corr_TOPO_flag = Field("corr_TOPO_flag", widget=ConceptWidget(choices=HeatFlow.corr_TOPO_flag_vocab.choices))
    corr_PAL_flag = Field("corr_PAL_flag", widget=ConceptWidget(choices=HeatFlow.corr_PAL_flag_vocab.choices))
    corr_SUR_flag = Field("corr_SUR_flag", widget=ConceptWidget(choices=HeatFlow.corr_SUR_flag_vocab.choices))
    corr_CONV_flag = Field("corr_CONV_flag", widget=ConceptWidget(choices=HeatFlow.corr_CONV_flag_vocab.choices))
    corr_HR_flag = Field("corr_HR_flag", widget=ConceptWidget(choices=HeatFlow.corr_HR_flag_vocab.choices))

    expedition = Field("expedition")
    probe_type = Field("probe_type", widget=ConceptWidget(choices=HeatFlow.probe_type_vocab.choices))
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

    # q_date = Field("sample__date")

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

    # Ref_IGSN = Field("sample__dataset__reference")

    class Meta:
        model = HeatFlow
        import_order = ["hf_site", "sample"]
        clean_model_instances = True
        store_instance = True

    def __init__(self, *args, **kwargs):
        self.dataset = kwargs.pop("dataset")
        super().__init__(*args, **kwargs)

    def import_data(self, dataset, dry_run=False, **kwargs):
        # Force errors to be raised instead of being caught
        # kwargs["raise_errors"] = True
        return super().import_data(dataset, dry_run=dry_run, **kwargs)

    def before_import_row(self, row, **kwargs):
        """Hook to modify the row before it is imported."""
        row["dataset"] = self.dataset.pk
        row["thermal_gradient"] = None
        row["thermal_conductivity"] = None

        # fix controlled vocab values surrounded by brackets
        for key, value in row.items():
            if isinstance(value, str) and value.startswith("["):
                row[key] = value[1:-1]

        # first, we get the location because we will attach it to both the heat flow site and the heat flow interval
        # sample types
        row["location"] = self.get_location(row).pk

        # next, we create the HeatFlowSite and store it in the row as sample. When we create the SurfaceHeatFlow object,
        # this sample will be attached.
        row["heat_flow_site"] = self.get_site(row).pk

        # create a SurfaceHeatFlow instance and store as parent in the row. It will be found during creation of the
        # HeatFlow child instance
        row["parent"] = self.get_parent(row).pk

        # overwrite the previous sample with the sample for the HeatFlowInterval. This will be attached to the HeatFlow
        # child instance
        row["sample"] = self.get_sample(row).pk

    def get_location(self, row):
        return SampleWidget(
            model=Point,
            field_map={
                "x": "long_EW",
                "y": "lat_NS",
            },
        ).clean(None, row)

    def get_site(self, row):
        return SampleWidget(
            model=HeatFlowSite,
            field_map={
                "length": "total_depth_MD",
                "vertical_depth": "total_depth_TVD",
            },
            factory_kwargs={
                "exclude": [
                    "status",
                    "azimuth",
                    "inclination",
                    "top",
                    "bottom",
                    "type",
                    "elevation_datum",
                ],
                "widgets": {
                    "environment": CustomSelect,
                    "explo_method": CustomSelect,
                    "explo_purpose": CustomSelect,
                },
            },
        ).clean(None, row)

    def get_parent(self, row):
        return SampleWidget(
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
            },
        ).clean(None, row)

    def get_sample(self, row):
        return SampleWidget(
            model=HeatFlowInterval,
            field_map={
                "top": "q_top",
                "bottom": "q_bottom",
                "lithology": "geo_lithology",
                "age": "geo_stratigraphy",
            },
            factory_kwargs={
                "exclude": [
                    "image",
                    "lithology",
                    "age",
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
