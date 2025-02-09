import importlib
import pkgutil
from functools import cache
from typing import cast

from google.protobuf.descriptor import Descriptor
from google.protobuf.message import Message


@cache
def load_non_obf_game_message_names() -> list[str]:
    return sorted(_load_non_obf_game_message_class_names())


@cache
def _load_non_obf_game_message_class_names() -> frozenset[str]:
    return frozenset(_discover_non_obf_game_message_descriptors()[0])


@cache
def _load_non_obf_game_message_descriptors_by_name() -> dict[str, Descriptor]:
    return _discover_non_obf_game_message_descriptors()[1]


@cache
def _discover_non_obf_game_message_descriptors() -> tuple[
    set[str], dict[str, Descriptor]
]:
    import datas.protos.non_obf.game as game_pkg

    class_names: set[str] = set()
    descriptors: dict[str, Descriptor] = {}
    for module_info in pkgutil.walk_packages(
        game_pkg.__path__, f"{game_pkg.__name__}."
    ):
        if module_info.ispkg or module_info.name.endswith(".__init__"):
            continue
        module = importlib.import_module(module_info.name)
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if (
                isinstance(attribute, type)
                and issubclass(attribute, Message)
                and getattr(attribute, "DESCRIPTOR", None) is not None
            ):
                descriptor = cast(Descriptor, attribute.DESCRIPTOR)
                class_names.add(attribute.__name__)
                descriptors[attribute.__name__] = descriptor
                descriptors[descriptor.full_name] = descriptor
    return class_names, descriptors


def find_non_obf_game_message_descriptor(name: str) -> Descriptor | None:
    return _load_non_obf_game_message_descriptors_by_name().get(name)
