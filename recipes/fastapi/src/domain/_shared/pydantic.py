from pydantic.fields import FieldInfo


def inherit_field(entity: type, field: str, **overrides) -> FieldInfo:
    original = entity.model_fields[field]
    # Create a copy by using original attributes
    # Avoid copying all attributes as some are internal
    new_kwargs = {
        "annotation": original.annotation,
        "default": original.default,
        "default_factory": original.default_factory,
        "alias": original.alias,
        "title": original.title,
        "description": original.description,
        "examples": original.examples,
        "json_schema_extra": original.json_schema_extra,
    }
    # Update with overrides
    new_kwargs.update(overrides)
    # Filter out None values that override defaults if necessary?
    # No, explicitness is better.
    return FieldInfo(**new_kwargs)


def optional_field(entity: type, field: str) -> FieldInfo:
    return inherit_field(entity, field, default=None)
