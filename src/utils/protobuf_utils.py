from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Mapping
from dataclasses import is_dataclass
from datetime import datetime
from typing import TypedDict, cast

from google.protobuf.descriptor import Descriptor
from google.protobuf.json_format import Parse
from google.protobuf.message import Message
from google.protobuf.message_factory import GetMessageClass

from src.protocol.protocol_game import POOL
from src.utils.type_guards import to_object_dict, to_object_list, to_str_object_dict

GAME_PROTO_PKG = "d3_mapping.resources.protos.game"


class SerializedMessagePayload(TypedDict):
    msg_full_name: str
    content: str


def find_message_class(full_name: str) -> type[Message] | None:
    """Attempt to resolve a protobuf message class by its simple or fully-qualified name.

    full_name may be either 'MessageName' or 'package.MessageName' or the
    type name returned by generated descriptors. This performs a best-effort
    search in the GAME_PROTO_PKG modules.
    """
    if "." in full_name:
        mod_name, cls = full_name.rsplit(".", 1)
        mod = importlib.import_module(mod_name)
        candidate = getattr(mod, cls, None)
        if isinstance(candidate, type) and issubclass(candidate, Message):
            return candidate
    for mod_name in _discover_proto_modules():
        mod = importlib.import_module(mod_name)
        candidate = getattr(mod, full_name, None)
        if isinstance(candidate, type) and issubclass(candidate, Message):
            return candidate
        for attr in dir(mod):
            obj = getattr(mod, attr)
            descriptor = getattr(obj, "DESCRIPTOR", None)
            if (
                isinstance(obj, type)
                and issubclass(obj, Message)
                and getattr(descriptor, "name", None) == full_name
            ):
                return obj
    return None


def _discover_proto_modules() -> list[str]:
    pkg = importlib.import_module(GAME_PROTO_PKG)
    mods: list[str] = []
    if not hasattr(pkg, "__path__"):
        return mods
    for finder, name, ispkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        mods.append(name)
    return mods


def _convert_str_value(value: object) -> object:
    if not isinstance(value, str):
        return value
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        if value.isnumeric():
            return int(value)
        return value


def _convert_from_serialized(value: object) -> object:
    if value is None:
        return None
    # attempt datetime parse
    if isinstance(value, str):
        return _convert_str_value(value)
    typed_list = to_object_list(value)
    if typed_list is not None:
        return [_convert_from_serialized(item) for item in typed_list]
    typed_mapping = to_str_object_dict(value)
    if typed_mapping is not None:
        serialized_payload = _extract_serialized_message_payload(typed_mapping)
        if serialized_payload is not None:
            msg_descriptor: Descriptor = POOL.FindMessageTypeByName(
                serialized_payload["msg_full_name"]
            )
            msg = GetMessageClass(msg_descriptor)()
            Parse(serialized_payload["content"], msg)
            return msg
        converted_dict: dict[object, object] = {}
        for key, item in typed_mapping.items():
            converted_dict[_convert_str_value(key)] = _convert_from_serialized(item)
        return converted_dict
    return value


def _extract_serialized_message_payload(
    value: Mapping[str, object],
) -> SerializedMessagePayload | None:
    msg_full_name = value.get("msg_full_name")
    if not isinstance(msg_full_name, str):
        return None

    content = value.get("content")
    if not isinstance(content, str):
        raise TypeError("Serialized protobuf payload must contain a JSON string")

    return {
        "msg_full_name": msg_full_name,
        "content": content,
    }


def _restore_dict_instance(
    source_class: type[object],
    source_data: dict[object, object],
    data: dict[object, object],
) -> object:
    if source_class is dict:
        restored: dict[object, object] = source_data.copy()
    else:
        restored_candidate = source_class()
        if not isinstance(restored_candidate, dict):
            raise TypeError("Custom dictionary factory must return a dictionary")
        restored = cast(dict[object, object], restored_candidate)
        restored.update(source_data)

    restored.update(data)
    return restored


def apply_dict_to_dataclass(obj: object, data: Mapping[str, object]) -> None:
    for key, value in data.items():
        if hasattr(obj, key):
            current = getattr(obj, key)
            nested_value = to_str_object_dict(value)
            if is_dataclass(current) and nested_value is not None:
                apply_dict_to_dataclass(current, nested_value)
            else:
                converted_value: object = _convert_from_serialized(value)
                typed_current = to_object_dict(current)
                typed_converted_value = to_object_dict(converted_value)
                if typed_current is not None and typed_converted_value is not None:
                    if type(current) is not dict:
                        current_object = cast(object, current)
                        current_class = type(current_object)
                        converted_value = _restore_dict_instance(
                            current_class,
                            typed_current,
                            typed_converted_value,
                        )
                setattr(obj, key, converted_value)
        else:
            # create attribute if missing
            setattr(obj, key, _convert_from_serialized(value))
