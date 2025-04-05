import importlib
import pkgutil
from functools import cache

from google.protobuf.descriptor import Descriptor


@cache
def load_non_obf_game_message_full_names() -> list[str]:
    return sorted(_load_non_obf_game_message_full_names())


@cache
def _load_non_obf_game_message_full_names() -> frozenset[str]:
    return frozenset(
        build_non_obf_game_message_pinned_name(descriptor)
        for lookup_name, descriptor in _load_non_obf_game_message_descriptors_by_name().items()
        if lookup_name == descriptor.full_name
    )


@cache
def _load_non_obf_game_message_descriptors_by_name() -> dict[str, Descriptor]:
    return _discover_non_obf_game_message_descriptors_by_name()


@cache
def _discover_non_obf_game_message_descriptors_by_name() -> dict[str, Descriptor]:
    import datas.protos.non_obf.game as game_pkg

    descriptors: dict[str, Descriptor] = {}
    for module_info in pkgutil.walk_packages(
        game_pkg.__path__, f"{game_pkg.__name__}."
    ):
        if module_info.ispkg or module_info.name.endswith(".__init__"):
            continue
        module = importlib.import_module(module_info.name)
        for descriptor in module.DESCRIPTOR.message_types_by_name.values():
            _record_non_obf_game_message_descriptor(
                descriptors, descriptor, is_top_level=True
            )
    return descriptors


def _record_non_obf_game_message_descriptor(
    descriptors: dict[str, Descriptor],
    descriptor: Descriptor,
    *,
    is_top_level: bool,
) -> None:
    if is_top_level:
        descriptors[descriptor.name] = descriptor
    descriptors[descriptor.full_name] = descriptor
    descriptors[build_non_obf_game_message_pinned_name(descriptor)] = descriptor
    for nested_descriptor in descriptor.nested_types:
        _record_non_obf_game_message_descriptor(
            descriptors, nested_descriptor, is_top_level=False
        )


def build_non_obf_game_message_pinned_name(descriptor: Descriptor) -> str:
    return ".".join(
        _normalize_non_obf_game_message_name_part(name_part)
        for name_part in descriptor.full_name.split(".")
    )


def _normalize_non_obf_game_message_name_part(name_part: str) -> str:
    return f"{name_part[:1].upper()}{name_part[1:]}" if name_part else name_part


def find_non_obf_game_message_descriptor(name: str) -> Descriptor | None:
    return _load_non_obf_game_message_descriptors_by_name().get(name)
