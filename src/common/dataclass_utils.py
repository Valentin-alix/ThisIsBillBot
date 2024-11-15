from dataclasses import MISSING, fields, is_dataclass
from datetime import datetime
from typing import Any

from d3_mapping.protocol.protocol_game import POOL
from google.protobuf.descriptor import Descriptor
from google.protobuf.json_format import MessageToJson, Parse
from google.protobuf.message import Message
from google.protobuf.message_factory import GetMessageClass


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
    for field in fields(obj):  # type: ignore
        name = field.name
        val = getattr(obj, name)
        serialized_value = _serialize_value(val)
        if serialized_value is not None:
            result[name] = _serialize_value(val)
    return result


def apply_dict_to_dataclass(obj: object, data: dict[str, Any]) -> None:
    for key, value in data.items():
        if hasattr(obj, key):
            current = getattr(obj, key)
            if is_dataclass(current) and isinstance(value, dict):
                apply_dict_to_dataclass(current, value)
            else:
                setattr(obj, key, _convert_from_serialized(value))
        else:
            # create attribute if missing
            setattr(obj, key, _convert_from_serialized(value))


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


def _convert_str_value(value: str):
    try:
        return datetime.fromisoformat(value)
    except Exception:
        if value.isnumeric():
            return int(value)
        return value


def _convert_from_serialized(value: Any) -> Any:
    if value is None:
        return None
    # attempt datetime parse
    if isinstance(value, str):
        return _convert_str_value(value)
    if isinstance(value, list):
        return [_convert_from_serialized(x) for x in value]
    if isinstance(value, dict):
        if "msg_full_name" in value:
            msg_descriptor: Descriptor = POOL.FindMessageTypeByName(
                value["msg_full_name"]
            )
            msg = GetMessageClass(msg_descriptor)()
            Parse(value["content"], msg)
            return msg
        return {
            _convert_str_value(k): _convert_from_serialized(val)
            for k, val in value.items()
        }
    return value
