from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from proto_mapper_assembly.helpers.proto_helpers import build_types_by_short_name, resolve_child_message_cls
from proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.interfaces.matching import MatchingWorkspace, SignatureIndexLookup


def build_matching_workspace(
    *,
    obf_signatures: Sequence[MessageAccessSignature],
    non_obf_signatures: Sequence[MessageAccessSignature],
    obf_messages_by_cls: dict[str, DumpCSMessage],
    non_obf_messages_by_cls: dict[str, DumpCSMessage],
) -> MatchingWorkspace:
    frozen_obf_signatures = tuple(obf_signatures)
    frozen_non_obf_signatures = tuple(non_obf_signatures)
    obf_groups = _group_signatures_by_file_descriptor(frozen_obf_signatures)
    non_obf_groups = _group_signatures_by_file_descriptor(frozen_non_obf_signatures)
    obf_type_index = build_types_by_short_name(obf_messages_by_cls)
    non_obf_type_index = build_types_by_short_name(non_obf_messages_by_cls)
    signature_indexes = SignatureIndexLookup(
        obf_index_by_cls={
            signature.message_cls: index for index, signature in enumerate(frozen_obf_signatures)
        },
        non_obf_index_by_cls={
            signature.message_cls: index for index, signature in enumerate(frozen_non_obf_signatures)
        },
    )
    return MatchingWorkspace(
        obf_signatures=frozen_obf_signatures,
        non_obf_signatures=frozen_non_obf_signatures,
        obf_signatures_by_cls={signature.message_cls: signature for signature in frozen_obf_signatures},
        non_obf_signatures_by_cls={
            signature.message_cls: signature for signature in frozen_non_obf_signatures
        },
        signature_indexes=signature_indexes,
        obf_type_index=obf_type_index,
        non_obf_type_index=non_obf_type_index,
        obf_groups=obf_groups,
        non_obf_groups=non_obf_groups,
        obf_group_root_indexes=_build_group_root_indexes(
            groups=obf_groups,
            index_by_cls=signature_indexes.obf_index_by_cls,
        ),
        non_obf_group_root_indexes=_build_group_root_indexes(
            groups=non_obf_groups,
            index_by_cls=signature_indexes.non_obf_index_by_cls,
        ),
        obf_group_complexity_by_descriptor=_build_group_complexity_by_descriptor(obf_groups),
        non_obf_group_complexity_by_descriptor=_build_group_complexity_by_descriptor(non_obf_groups),
        obf_field_message_types_by_cls=_build_field_message_types_by_cls(
            messages_by_cls=obf_messages_by_cls,
            type_index=obf_type_index,
        ),
        non_obf_field_message_types_by_cls=_build_field_message_types_by_cls(
            messages_by_cls=non_obf_messages_by_cls,
            type_index=non_obf_type_index,
        ),
    )


def _build_field_message_types_by_cls(
    messages_by_cls: dict[str, DumpCSMessage],
    type_index: dict[str, tuple[DumpCSMessage, ...]],
) -> dict[str, frozenset[str]]:
    result: dict[str, frozenset[str]] = {}
    for cls, message in messages_by_cls.items():
        child_types: set[str] = set()
        for field in message.fields:
            if not field.is_declared_proto_shape_field:
                continue
            child_cls = resolve_child_message_cls(
                field=field,
                parent_message=message,
                messages_by_cls=messages_by_cls,
                type_index=type_index,
            )
            if child_cls is not None:
                child_types.add(child_cls)
        if child_types:
            result[cls] = frozenset(child_types)
    return result


def _group_signatures_by_file_descriptor(
    signatures: Sequence[MessageAccessSignature],
) -> dict[str, tuple[MessageAccessSignature, ...]]:
    groups: dict[str, list[MessageAccessSignature]] = defaultdict(list)
    for signature in signatures:
        groups[signature.file_descriptor].append(signature)
    return {
        file_descriptor: tuple(sorted(group, key=lambda signature: signature.message_cls))
        for file_descriptor, group in groups.items()
    }


def _build_group_root_indexes(
    *,
    groups: dict[str, tuple[MessageAccessSignature, ...]],
    index_by_cls: dict[str, int],
) -> dict[str, tuple[int, ...]]:
    return {
        group_descriptor: tuple(
            index_by_cls[signature.message_cls] for signature in group if signature.dump_cs_msg.is_root_msg
        )
        for group_descriptor, group in groups.items()
    }


def _build_group_complexity_by_descriptor(
    groups: dict[str, tuple[MessageAccessSignature, ...]],
) -> dict[str, int]:
    return {
        group_descriptor: sum(signature.total_complexity for signature in group)
        for group_descriptor, group in groups.items()
    }
