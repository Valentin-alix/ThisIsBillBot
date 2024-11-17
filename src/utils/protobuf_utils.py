from __future__ import annotations

import importlib
import pkgutil
from dataclasses import is_dataclass
from datetime import datetime
from typing import Any

from google.protobuf.descriptor import Descriptor
from google.protobuf.json_format import Parse
from google.protobuf.message import Message
from google.protobuf.message_factory import GetMessageClass

from D3Mapping.d3_mapping.protocol.protocol_game import POOL

GAME_PROTO_PKG = "d3_mapping.resources.protos.game"


def find_message_class(full_name: str) -> type[Message] | None:
    """Attempt to resolve a protobuf message class by its simple or fully-qualified name.

    full_name may be either 'MessageName' or 'package.MessageName' or the
    type name returned by generated descriptors. This performs a best-effort
    search in the GAME_PROTO_PKG modules.
    """
    if "." in full_name:
        mod_name, cls = full_name.rsplit(".", 1)
        mod = importlib.import_module(mod_name)
        if hasattr(mod, cls):
            return getattr(mod, cls)
    for mod_name in _discover_proto_modules():
        mod = importlib.import_module(mod_name)
        if hasattr(mod, full_name):
            return getattr(mod, full_name)
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if hasattr(obj, "DESCRIPTOR") and obj.DESCRIPTOR.name == full_name:
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


def _convert_str_value(value):
    if not isinstance(value, str):
        return value
    try:
        return datetime.fromisoformat(value)
    except ValueError:
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


def _restore_dict_type(data: dict, dict_type: type) -> dict:
    restored = dict_type()
    for k, v in data.items():
        converted_key = _convert_str_value(k)
        converted_val = _convert_from_serialized(v)
        if isinstance(converted_val, dict):
            nested_value = restored.get(converted_key, {})
            nested_type = type(nested_value)
            if type(nested_value) is not dict:
                converted_val = _restore_dict_type(converted_val, nested_type)
        restored[converted_key] = converted_val
    return restored


def apply_dict_to_dataclass(obj: object, data: dict[str, Any]) -> None:
    for key, value in data.items():
        if hasattr(obj, key):
            current = getattr(obj, key)
            if is_dataclass(current) and isinstance(value, dict):
                apply_dict_to_dataclass(current, value)
            else:
                current_type = type(current)
                converted = _convert_from_serialized(value)
                if isinstance(converted, dict) and type(converted) is not current_type:
                    converted = _restore_dict_type(converted, current_type)
                setattr(obj, key, converted)
        else:
            # create attribute if missing
            setattr(obj, key, _convert_from_serialized(value))
