from dataclasses import fields, is_dataclass
from datetime import datetime
from typing import Any, TypedDict, cast

from google.protobuf.json_format import MessageToJson
from google.protobuf.message import Message
from pydantic import BaseModel, ConfigDict


class AppModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class SerializedProtoMessagePayload(TypedDict):
    msg_full_name: str
    content: str


SerializedValue = str | int | float | bool | None | list["SerializedValue"] | dict[str, "SerializedValue"]


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


def _serialize_value(value: Any) -> SerializedValue | None:
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
    if isinstance(value, dict):
        serialized_dict: dict[str, SerializedValue] = {}
        value = cast(dict[str, Any], value)
        for key, item in value.items():
            serialized_item = _serialize_value(item)
            if serialized_item is not None:
                serialized_dict[str(key)] = serialized_item
        return serialized_dict
    if isinstance(value, list):
        serialized_list: list[SerializedValue] = []
        value = cast(list[Any], value)
        for item in value:
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
