from dataclasses import MISSING, fields, is_dataclass
from datetime import datetime
from typing import Any, TypeAlias, TypeGuard, TypedDict, cast

from google.protobuf.json_format import MessageToJson
from google.protobuf.message import Message
from pydantic import BaseModel, ConfigDict

from python_utils.json_types import to_object_dict, to_object_list, to_str_object_dict


class AppModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class SerializedProtoMessagePayload(TypedDict):
    msg_full_name: str
    content: str


SerializedValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
    | list["SerializedValue"]
    | dict[str, "SerializedValue"]
)


def is_serialized_value(value: object) -> TypeGuard[SerializedValue]:
    if value is None or isinstance(value, (str, int, float, bool)):
        return True
    typed_list = to_object_list(value)
    if typed_list is not None:
        return all(is_serialized_value(item) for item in typed_list)
    typed_dict = to_str_object_dict(value)
    if typed_dict is None:
        return False
    return all(is_serialized_value(item) for item in typed_dict.values())


def is_serialized_content(value: object) -> TypeGuard[dict[str, SerializedValue]]:
    typed_dict = to_str_object_dict(value)
    if typed_dict is None:
        return False
    return all(is_serialized_value(item) for item in typed_dict.values())


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
        payload: dict[str, SerializedValue] = {
            "msg_full_name": value.DESCRIPTOR.full_name,
            "content": MessageToJson(value, preserving_proto_field_name=True),
        }
        return payload
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    if is_dataclass(value):
        return dataclass_to_dict(value)
    typed_mapping = to_object_dict(value)
    if typed_mapping is not None:
        serialized_dict: dict[str, SerializedValue] = {}
        for key, item in typed_mapping.items():
            serialized_item = _serialize_value(item)
            if serialized_item is not None:
                serialized_dict[str(key)] = serialized_item
        return serialized_dict
    typed_list = to_object_list(value)
    if typed_list is not None:
        serialized_list: list[SerializedValue] = []
        for item in typed_list:
            serialized_item = _serialize_value(item)
            if serialized_item is not None:
                serialized_list.append(serialized_item)
        return serialized_list
    if isinstance(value, (tuple, set)):
        serialized_list = []
        typed_iterable = cast(tuple[object, ...] | set[object], value)
        for item in typed_iterable:
            serialized_item = _serialize_value(item)
            if serialized_item is not None:
                serialized_list.append(serialized_item)
        return serialized_list
    return None
