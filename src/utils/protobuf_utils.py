from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Mapping
from dataclasses import is_dataclass
from datetime import datetime
from typing import Any, TypeVar, cast

from google.protobuf.descriptor import Descriptor
from google.protobuf.json_format import Parse
from google.protobuf.message import Message
from google.protobuf.message_factory import GetMessageClass

from src.protocol.protocol_game import POOL

GAME_PROTO_PKG = "d3_mapping.resources.protos.game"
DictT = TypeVar("DictT", bound=dict[object, object])


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
    if isinstance(value, list):
        converted_list: list[object] = []
        for item in cast(list[object], value):
            converted_list.append(_convert_from_serialized(item))
        return converted_list
    if isinstance(value, Mapping):
        mapping_value = cast(Mapping[object, object], value)
        msg_full_name = mapping_value.get("msg_full_name")
        if isinstance(msg_full_name, str):
            msg_descriptor: Descriptor = POOL.FindMessageTypeByName(msg_full_name)
            msg = GetMessageClass(msg_descriptor)()
            content = mapping_value.get("content")
            if not isinstance(content, str):
                raise TypeError("Serialized protobuf payload must contain a JSON string")
            Parse(content, msg)
            return msg
        converted_dict: dict[object, object] = {}
        for key, item in mapping_value.items():
            converted_dict[_convert_str_value(key)] = _convert_from_serialized(item)
        return converted_dict
    return value


def _restore_dict_instance(source: DictT, data: Mapping[object, object]) -> DictT:
    restored_factory = cast(Any, type(source))
    restored = cast(DictT, restored_factory(source))
    restored.update(cast(dict[object, object], data))
    return restored


def apply_dict_to_dataclass(obj: object, data: Mapping[str, object]) -> None:
    for key, value in data.items():
        if hasattr(obj, key):
            current = getattr(obj, key)
            if is_dataclass(current) and isinstance(value, Mapping):
                apply_dict_to_dataclass(current, cast(Mapping[str, object], value))
            else:
                converted_value: object = _convert_from_serialized(value)
                if isinstance(current, dict) and isinstance(converted_value, dict):
                    current_class = cast(Any, current).__class__
                    if current_class is not dict:
                        converted_value = _restore_dict_instance(
                            cast(dict[object, object], current),
                            cast(Mapping[object, object], converted_value),
                        )
                setattr(obj, key, converted_value)
        else:
            # create attribute if missing
            setattr(obj, key, _convert_from_serialized(value))
