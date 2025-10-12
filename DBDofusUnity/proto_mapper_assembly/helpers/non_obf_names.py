from __future__ import annotations

from collections.abc import Mapping

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage


def build_filtered_message_namespace(
    *,
    is_obf: bool,
    message: DumpCSMessage,
    messages_by_cls: Mapping[str, DumpCSMessage],
) -> str:
    message_path = message.parent_name.split(".") if message.parent_name is not None else []
    message_path.append(message.name)
    key_parts: list[str] = []
    namespace = message.namespace
    if namespace is not None:
        key_parts.extend(namespace.lower().split("."))
    for path_index, path_segment in enumerate(message_path):
        is_leaf = path_index == len(message_path) - 1
        if is_leaf:
            key_parts.append(path_segment)
            continue

        current_path = ".".join(message_path[: path_index + 1])
        path_message = messages_by_cls.get(current_path)
        if path_index == 0:
            if path_message is None:
                key_parts.append(path_segment)
                continue
            if not _is_container_only_message(path_message):
                key_parts.append(path_segment)
            continue

        if path_message is not None and not _is_container_only_message(path_message):
            key_parts.append(path_segment)
    start = "." if not is_obf else ""

    output_key = f"{start}{'.'.join(key_parts)}"

    if output_key == ".com.ankama.dofus.server.game.protocol.Message":
        return ".com.ankama.dofus.server.game.protocol.GameMessage"

    return output_key


def build_pinned_non_obf_name(
    *,
    message: DumpCSMessage,
    messages_by_cls: Mapping[str, DumpCSMessage],
) -> str:
    return normalize_exported_non_obf_namespace(
        build_filtered_message_namespace(
            is_obf=False,
            message=message,
            messages_by_cls=messages_by_cls,
        )
    )


def normalize_exported_non_obf_namespace(namespace: str) -> str:
    stripped = namespace.lstrip(".")
    if not stripped:
        return stripped
    return ".".join(_normalize_non_obf_segment(part) for part in stripped.split("."))


def _normalize_non_obf_segment(part: str) -> str:
    return f"{part[:1].upper()}{part[1:]}" if part else part


def _is_container_only_message(message: DumpCSMessage) -> bool:
    return len(message.fields) == 0 and len(message.properties) == 0
