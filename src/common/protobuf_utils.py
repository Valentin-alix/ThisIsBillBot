from __future__ import annotations

import importlib
import pkgutil

from google.protobuf.message import Message

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
