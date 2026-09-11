"""
Shared instance validation for the GHFDB import resources.

Both import resources set ``sample``, ``dataset`` and ``name`` in
``before_save_instance()``, which django-import-export runs *after*
``validate_instance()``. Validating those three fields at validation time
would refuse every row on relations the resource is about to set correctly.

References:
    - ``specs/004-import-upload-template/decisions.md`` D15
"""

from django.core.exceptions import ValidationError

FIELDS_SET_AFTER_VALIDATION = ("sample", "dataset", "name")


class ExcludeFieldsSetAfterValidation:
    """Validate the instance as django-import-export does, minus the fields
    ``before_save_instance()`` fills in later.

    ``sample`` and ``dataset`` are foreign keys, so the database's own NOT
    NULL constraint is a real backstop for them: a resource that failed to
    set one would refuse the file with a database-level row error. ``name``
    has no such backstop — it is a required ``CharField``, and an unset one
    saves as an empty string the constraint is perfectly happy with — so both
    resources set it on every row rather than relying on one.
    """

    def validate_instance(
        self, instance, import_validation_errors=None, validate_unique=True
    ):
        errors = (
            {} if import_validation_errors is None else import_validation_errors.copy()
        )
        if self._meta.clean_model_instances:
            try:
                instance.full_clean(
                    exclude={*errors.keys(), *FIELDS_SET_AFTER_VALIDATION},
                    validate_unique=validate_unique,
                )
            except ValidationError as e:
                errors = e.update_error_dict(errors)
        if errors:
            raise ValidationError(errors)
