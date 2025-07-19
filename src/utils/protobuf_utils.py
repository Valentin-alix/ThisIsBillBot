from __future__ import annotations

import importlib
import pkgutil
from typing import TypedDict

from google.protobuf.message import Message

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
    for _, name, _ in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        mods.append(name)
    return mods
