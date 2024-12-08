from collections.abc import Mapping
from typing import TypeGuard, cast


def is_dict_str_object(value: object) -> TypeGuard[dict[str, object]]:
    return to_str_object_dict(value) is not None


def is_mapping_str_object(value: object) -> TypeGuard[Mapping[str, object]]:
    if not isinstance(value, Mapping):
        return False
    raw_mapping = cast(Mapping[object, object], value)
    return all(isinstance(key, str) for key in raw_mapping)


def is_list_object(value: object) -> TypeGuard[list[object]]:
    return to_object_list(value) is not None


def to_str_object_dict(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    raw_dict = cast(dict[object, object], value)
    typed_dict: dict[str, object] = {}
    for raw_key, raw_value in raw_dict.items():
        if not isinstance(raw_key, str):
            return None
        typed_dict[raw_key] = raw_value
    return typed_dict


def to_object_dict(value: object) -> dict[object, object] | None:
    if not isinstance(value, dict):
        return None
    raw_dict = cast(dict[object, object], value)
    return {raw_key: raw_value for raw_key, raw_value in raw_dict.items()}


def to_object_list(value: object) -> list[object] | None:
    if not isinstance(value, list):
        return None
    raw_list = cast(list[object], value)
    return [item for item in raw_list]
