from dataclasses import fields, MISSING
from typing import Any


def reset_fields_to_default(instance: Any, include_fields: list[str]):
    for field in fields(instance):
        if field.name not in include_fields:
            continue
        if field.default is not MISSING:
            setattr(instance, field.name, field.default)
        elif field.default_factory is not MISSING:
            setattr(instance, field.name, field.default_factory())
