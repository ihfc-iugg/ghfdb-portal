from decimal import Decimal

from django import forms
from earth_science.imports import SampleLocationImporterMixin
from geoluminate.imports import GeoluminateBaseImporter
from quantityfield.fields import DecimalQuantityFormField

from heat_flow.models import ChildHeatFlow, HeatFlowInterval, HeatFlowSite, ParentHeatFlow


class CustomChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.display_to_value = {label: value for value, label in self.choices}

    def to_python(self, value):
        # Convert display value back to the corresponding database value
        if value in self.display_to_value:
            return self.display_to_value[value]
        raise forms.ValidationError("Invalid choice.")


class CustomSelect(forms.Select):
    def value_from_datadict(self, data, files, name):
        """Converts the display value back to the database value."""
        display_to_value = {label: value for value, label in self.choices}
        display_value = data.get(name)
        return display_to_value.get(display_value, display_value)


class CustomModelMultipleSelect(forms.SelectMultiple):
    def value_from_datadict(self, data, files, name):
        values = data.get(name)

        # allowed_values = list(self.choices.queryset.values_list("name", flat=True))

        pks = []
        invalid = []

        labels = self.choices.queryset.values_list("name", flat=True)
        for v in values:
            if v in labels:
                pks.append(v)
            else:
                invalid.append(v)
        if invalid:
            raise forms.ValidationError(f"Invalid choice(s): {', '.join(invalid)}")

        qs = self.choices.queryset.filter(name__in=values)
        return [obj.pk for obj in qs]


class GHFDBImporterMixin:
    """Mixin class that handles reading the spreadsheet template defined by the World Heat Flow Database Project (in conjunction with the IHFC) and modifying rows before they are processed."""

    df_init_kwargs = {"sheet_name": 1, "skiprows": [0, 1, 2, 3, 4, 6, 7]}

    # these fields are cleaned and converted to lists
    multi_value_fields = ["geo_lithology", "geo_stratigraphy"]

    def read_dataframe(self):
        # remove those pesky brackets
        return super().read_dataframe().replace({"\\[": "", "\\]": ""}, regex=True)

    def modify_row(self, row, model, options):
        # this is a stop gap measure for the time being until we sort out the controlled vocabularies
        row = super().modify_row(row, model, options)
        if row.get("corr_HP_flag") == "Yes":
            row["corr_HP_flag"] = True
        elif row.get("corr_HP_flag") == "No":
            row["corr_HP_flag"] = False
        else:
            row["corr_HP_flag"] = None
        return row

    def get_model_form(self, model, form_kwargs):
        form_class = super().get_model_form(model, form_kwargs)
        for field in form_class.base_fields.values():
            if isinstance(field, DecimalQuantityFormField):
                # There is currently a bug in the quantityfield library that prevents proper conversion of Decimal values
                # this fixes it for the time being until a proper fix is implemented
                field.to_number_type = lambda x: Decimal(str(x))

        return form_class


class HeatFlowParentImporter(GHFDBImporterMixin, SampleLocationImporterMixin, GeoluminateBaseImporter):
    """This imported class is responsible for iterating over the excel template and parsing the necessary data to create
    `heat_flow.ParentHeatFlow` instances and their associated `heat_flow.HeatFlowSite` instances."""

    location_fields = {
        "x": "long_EW",
        "y": "lat_NS",
    }

    models = {
        ParentHeatFlow: {
            "field_map": {
                "sample": HeatFlowSite,
            },
            "form_kwargs": {
                "exclude": ["contributors"],
                "widgets": {
                    # "corr_HP_flag": CustomSelect,
                    # "corr_HP_flag": forms.BooleanField,
                },
            },
        },
        HeatFlowSite: {
            "field_map": {
                # "top": "elevation",
                "bottom": "total_depth_TVD",
                "length": "total_depth_MD",
            },
            "form_kwargs": {
                "exclude": ["options", "contributors", "status"],
                "widgets": {
                    "environment": CustomSelect,
                    "explo_method": CustomSelect,
                    "explo_purpose": CustomSelect,
                },
            },
        },
        ChildHeatFlow: {
            "field_map": {
                "sample": HeatFlowInterval,
                "parent": ParentHeatFlow,
            },
            "form_kwargs": {
                "exclude": ["contributors"],
                "widgets": {
                    "q_method": CustomSelect,
                    "tc_strategy": CustomSelect,
                    "tc_source": CustomSelect,
                    "tc_location": CustomSelect,
                    "tc_method": CustomSelect,
                    "tc_pT_conditions": CustomSelect,
                    "tc_pT_function": CustomSelect,
                    "tc_saturation": CustomSelect,
                    "T_corr_top": CustomSelect,
                    "T_corr_bottom": CustomSelect,
                    "corr_IS_flag": CustomSelect,
                    "corr_T_flag": CustomSelect,
                    "corr_S_flag": CustomSelect,
                    "corr_E_flag": CustomSelect,
                    "corr_TOPO_flag": CustomSelect,
                    "corr_PAL_flag": CustomSelect,
                    "corr_SUR_flag": CustomSelect,
                    "corr_CONV_flag": CustomSelect,
                },
            },
        },
        HeatFlowInterval: {
            "field_map": {
                "top": "q_top",
                "bottom": "q_bottom",
                "lithology": "geo_lithology",
                "age": "geo_stratigraphy",
                "parent": HeatFlowSite,
                # "vertical_depth": "",
            },
            "form_kwargs": {
                "exclude": ["options", "contributors", "status"],
                # "widgets": {
                #     # "lithology": CustomModelMultipleSelect,
                #     # "age": CustomModelMultipleSelect,
                # },
            },
        },
    }

    # def read_dataframe(self):
    #     # for the parent model, we only want unique lat/long pairs
    #     return super().read_dataframe().drop_duplicates(subset=["lat_NS", "long_EW"])


class ChildHeatFlowImporter(GHFDBImporterMixin, GeoluminateBaseImporter):
    """This importer class is responsible for iterating over the excel template and parsing the necessary data to create
    `heat_flow.ChildHeatFlow` instances and their associated `heat_flow.HeatFlowInterval` instances."""

    models = {
        ChildHeatFlow: {
            "field_map": {
                "sample": HeatFlowInterval,
                # "parent": ParentHeatFlow,
            },
            "form_kwargs": {
                "exclude": ["contributors"],
                "widgets": {},
            },
        },
        HeatFlowInterval: {
            "field_map": {
                "top": "q_top",
                "bottom": "q_bottom",
                "lithology": "geo_lithology",
                "stratigraphy": "geo_stratigraphy",
                "parent": HeatFlowSite,
            },
            "form_kwargs": {
                "exclude": ["options", "contributors", "status"],
                "widgets": {
                    "environment": CustomSelect,
                    "explo_method": CustomSelect,
                    "explo_purpose": CustomSelect,
                },
            },
        },
    }
