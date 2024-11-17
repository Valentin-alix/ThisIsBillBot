from dataclasses import MISSING, fields, is_dataclass
from datetime import datetime
from typing import Any, Callable, TypeVar

from google.protobuf.json_format import MessageToJson
from google.protobuf.message import Message
from pydantic import BaseModel, ConfigDict, validate_call


class AppModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


F = TypeVar("F", bound=Callable[..., Any])


def ValidatedCall(func: F) -> F:
    return validate_call(
        func, config=ConfigDict(arbitrary_types_allowed=True, validate_return=True)
    )  # type: ignore


def reset_fields_to_default(instance: Any, include_fields: list[str]):
    for field in fields(instance):
        if field.name not in include_fields:
            continue
        if field.default is not MISSING:
            setattr(instance, field.name, field.default)
        elif field.default_factory is not MISSING:
            setattr(instance, field.name, field.default_factory())


def dataclass_to_dict(obj: object) -> dict[str, Any]:
    result: dict[str, Any] = {}
    assert is_dataclass(obj)
    for field in fields(obj):
        name = field.name
        val = getattr(obj, name)
        serialized_value = _serialize_value(val)
        if serialized_value is not None:
            result[name] = _serialize_value(val)
    return result


def _serialize_value(value: Any) -> Any:
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
    if isinstance(value, dict):
        return {str(k): _serialize_value(val) for k, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize_value(x) for x in value]
    return None
