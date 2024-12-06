from collections.abc import Iterable, Mapping
from dataclasses import MISSING, fields, is_dataclass
from datetime import datetime
from typing import Any, Callable, TypeAlias, TypeVar, cast

from google.protobuf.json_format import MessageToJson
from google.protobuf.message import Message
from pydantic import BaseModel, ConfigDict, validate_call


class AppModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


F = TypeVar("F", bound=Callable[..., Any])
SerializedValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
    | list["SerializedValue"]
    | dict[str, "SerializedValue"]
)


def ValidatedCall(func: F) -> F:
    return cast(
        F,
        validate_call(
            config=ConfigDict(arbitrary_types_allowed=True, validate_return=True)
        )(func),
    )


def reset_fields_to_default(instance: Any, include_fields: list[str]) -> None:
    for field in fields(instance):
        if field.name not in include_fields:
            continue
        if field.default is not MISSING:
            setattr(instance, field.name, field.default)
        elif field.default_factory is not MISSING:
            setattr(instance, field.name, field.default_factory())


def dataclass_to_dict(obj: object) -> dict[str, SerializedValue]:
    result: dict[str, SerializedValue] = {}
    assert is_dataclass(obj)
    for field in fields(obj):
        name = field.name
        value = getattr(obj, name)
        serialized_value = _serialize_value(value)
        if serialized_value is not None:
            result[name] = serialized_value
    return result


def _serialize_value(value: object) -> SerializedValue | None:
    if value is None:
        return None
    if isinstance(value, Message):
        return {
            "msg_full_name": value.DESCRIPTOR.full_name,
            "content": MessageToJson(value, preserving_proto_field_name=True),
        }
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    if is_dataclass(value):
        return dataclass_to_dict(value)
    if isinstance(value, Mapping):
        mapping_value = cast(Mapping[object, object], value)
        serialized_dict: dict[str, SerializedValue] = {}
        for key, item in mapping_value.items():
            serialized_item = _serialize_value(item)
            if serialized_item is not None:
                serialized_dict[str(key)] = serialized_item
        return serialized_dict
    if isinstance(value, (list, tuple, set)):
        serialized_list: list[SerializedValue] = []
        for item in cast(Iterable[object], value):
            serialized_item = _serialize_value(item)
            if serialized_item is not None:
                serialized_list.append(serialized_item)
        return serialized_list
    return None
