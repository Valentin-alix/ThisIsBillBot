from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeGuard, cast

from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField
from proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from proto_mapper_assembly.interfaces.runtime import (
    ChildMappingResolution,
    MappingFailureOrigin,
    RemapOutcome,
    RuntimeRemappingContext,
    RuntimeRemappingResult,
    RuntimeRemappingTraceEvent,
    RuntimeValidationCandidate,
)


def remap_runtime_instances(
    *,
    normalized_instances: Sequence[dict[str, object]],
    candidate: RuntimeValidationCandidate,
    obf_message: DumpCSMessage,
    non_obf_message: DumpCSMessage,
    remapping_context: RuntimeRemappingContext,
    trace_handler: Callable[[RuntimeRemappingTraceEvent], None] | None = None,
) -> RuntimeRemappingResult:
    """
    Remap every normalized runtime instance through the current candidate.

    The function accumulates remapped instances by message type and stops early
    as soon as a child-field mapping proves incompatible.
    """
    instances_by_type: dict[str, list[dict[str, object]]] = defaultdict(list)
    mapping_failure: str | None = None
    mapping_failure_origin: str | None = None
    for normalized_instance in normalized_instances:
        remap_outcome = _remap_runtime_instance(
            instance=normalized_instance,
            current_candidate=candidate,
            obf_message=obf_message,
            non_obf_message=non_obf_message,
            remapping_context=remapping_context,
            instances_by_type=instances_by_type,
            trace_handler=trace_handler,
            path=(),
        )
        if remap_outcome.mapping_failure is None:
            continue
        mapping_failure = remap_outcome.mapping_failure
        mapping_failure_origin = remap_outcome.mapping_failure_origin
        break

    return RuntimeRemappingResult(
        instances_by_type=instances_by_type,
        mapping_failure=mapping_failure,
        mapping_failure_origin=mapping_failure_origin,
    )


def _remap_runtime_instance(
    *,
    instance: dict[str, object],
    current_candidate: RuntimeValidationCandidate,
    obf_message: DumpCSMessage,
    non_obf_message: DumpCSMessage,
    remapping_context: RuntimeRemappingContext,
    instances_by_type: dict[str, list[dict[str, object]]],
    trace_handler: Callable[[RuntimeRemappingTraceEvent], None] | None,
    path: tuple[str, ...],
) -> RemapOutcome:
    """Remap one runtime instance, including nested child messages when needed."""
    remapped_instance: dict[str, object] = {}
    obf_metadata = remapping_context.get_obf_metadata(obf_message)
    non_obf_metadata = remapping_context.get_non_obf_metadata(non_obf_message)

    for obf_key, raw_value in instance.items():
        remapped_key = current_candidate.field_mapping_result.field_mapping.get(obf_key, obf_key)
        obf_live_field = obf_metadata.live_runtime_fields_by_name.get(obf_key)
        non_obf_live_field = non_obf_metadata.live_runtime_fields_by_name.get(remapped_key)
        if obf_live_field is None:
            continue
        if non_obf_live_field is None and obf_live_field.category in {
            FieldCategoryEnum.MESSAGE,
            FieldCategoryEnum.REPEATED,
            FieldCategoryEnum.MAP,
        }:
            continue

        if non_obf_live_field is None:
            continue

        remap_outcome = _remap_field_value(
            raw_value=raw_value,
            obf_field=obf_live_field,
            non_obf_field=non_obf_live_field,
            parent_obf_message=obf_message,
            parent_non_obf_message=non_obf_message,
            remapping_context=remapping_context,
            instances_by_type=instances_by_type,
            trace_handler=trace_handler,
            path=(*path, obf_key),
        )
        if remap_outcome.mapping_failure is not None:
            return RemapOutcome(
                value=remapped_instance,
                mapping_failure=remap_outcome.mapping_failure,
                mapping_failure_origin=remap_outcome.mapping_failure_origin,
            )
        remapped_instance[remapped_key] = remap_outcome.value

    instances_by_type[non_obf_message.name].append(remapped_instance)
    return RemapOutcome(value=remapped_instance)


def _remap_field_value(
    *,
    raw_value: object,
    obf_field: DumpCSMessageField,
    non_obf_field: DumpCSMessageField,
    parent_obf_message: DumpCSMessage,
    parent_non_obf_message: DumpCSMessage,
    remapping_context: RuntimeRemappingContext,
    instances_by_type: dict[str, list[dict[str, object]]],
    trace_handler: Callable[[RuntimeRemappingTraceEvent], None] | None,
    path: tuple[str, ...],
) -> RemapOutcome:
    """Remap a field value and recurse into child messages when applicable."""
    child_mapping = _resolve_child_mapping(
        obf_field=obf_field,
        non_obf_field=non_obf_field,
        parent_obf_message=parent_obf_message,
        parent_non_obf_message=parent_non_obf_message,
        remapping_context=remapping_context,
    )
    if child_mapping.status == "unresolved":
        return RemapOutcome(value=raw_value)

    child_candidate = child_mapping.child_candidate
    if child_candidate is None:
        return RemapOutcome(value=raw_value)

    child_obf_message = child_candidate.obf_msg_sig.dump_cs_msg
    child_non_obf_message = child_candidate.non_obf_msg_sig.dump_cs_msg

    if obf_field.category == FieldCategoryEnum.MESSAGE and _is_runtime_object(raw_value):
        return _remap_child_message(
            raw_value=raw_value,
            child_candidate=child_candidate,
            child_obf_message=child_obf_message,
            child_non_obf_message=child_non_obf_message,
            remapping_context=remapping_context,
            instances_by_type=instances_by_type,
            trace_handler=trace_handler,
            path=path,
        )

    if obf_field.category == FieldCategoryEnum.REPEATED and _is_runtime_list(raw_value):
        return _remap_repeated_value(
            raw_items=raw_value,
            child_candidate=child_candidate,
            child_obf_message=child_obf_message,
            child_non_obf_message=child_non_obf_message,
            remapping_context=remapping_context,
            instances_by_type=instances_by_type,
            trace_handler=trace_handler,
            path=(*path, obf_field.clean_field_name),
        )

    if obf_field.category == FieldCategoryEnum.MAP and _is_runtime_mapping(raw_value):
        return _remap_map_value(
            raw_map=raw_value,
            child_candidate=child_candidate,
            child_obf_message=child_obf_message,
            child_non_obf_message=child_non_obf_message,
            remapping_context=remapping_context,
            instances_by_type=instances_by_type,
            trace_handler=trace_handler,
            path=path,
        )

    return RemapOutcome(value=raw_value)


def _remap_repeated_value(
    *,
    raw_items: list[object],
    child_candidate: RuntimeValidationCandidate,
    child_obf_message: DumpCSMessage,
    child_non_obf_message: DumpCSMessage,
    remapping_context: RuntimeRemappingContext,
    instances_by_type: dict[str, list[dict[str, object]]],
    trace_handler: Callable[[RuntimeRemappingTraceEvent], None] | None,
    path: tuple[str, ...],
) -> RemapOutcome:
    remapped_items: list[object] = []
    for item in raw_items:
        if not _is_runtime_object(item):
            remapped_items.append(item)
            continue
        remap_outcome = _remap_child_message(
            raw_value=item,
            child_candidate=child_candidate,
            child_obf_message=child_obf_message,
            child_non_obf_message=child_non_obf_message,
            remapping_context=remapping_context,
            instances_by_type=instances_by_type,
            trace_handler=trace_handler,
            path=path,
        )
        if remap_outcome.mapping_failure is not None:
            return RemapOutcome(
                value=raw_items,
                mapping_failure=remap_outcome.mapping_failure,
                mapping_failure_origin="child",
            )
        remapped_items.append(remap_outcome.value)
    return RemapOutcome(value=remapped_items)


def _remap_map_value(
    *,
    raw_map: dict[object, object],
    child_candidate: RuntimeValidationCandidate,
    child_obf_message: DumpCSMessage,
    child_non_obf_message: DumpCSMessage,
    remapping_context: RuntimeRemappingContext,
    instances_by_type: dict[str, list[dict[str, object]]],
    trace_handler: Callable[[RuntimeRemappingTraceEvent], None] | None,
    path: tuple[str, ...],
) -> RemapOutcome:
    remapped_map: dict[object, object] = {}
    for map_key, map_value in raw_map.items():
        if not _is_runtime_object(map_value):
            remapped_map[map_key] = map_value
            continue
        remap_outcome = _remap_child_message(
            raw_value=map_value,
            child_candidate=child_candidate,
            child_obf_message=child_obf_message,
            child_non_obf_message=child_non_obf_message,
            remapping_context=remapping_context,
            instances_by_type=instances_by_type,
            trace_handler=trace_handler,
            path=(*path, str(map_key)),
        )
        if remap_outcome.mapping_failure is not None:
            return RemapOutcome(
                value=raw_map,
                mapping_failure=remap_outcome.mapping_failure,
                mapping_failure_origin="child",
            )
        remapped_map[map_key] = remap_outcome.value
    return RemapOutcome(value=remapped_map)


def _is_runtime_object(value: object) -> TypeGuard[dict[str, object]]:
    if not isinstance(value, dict):
        return False
    runtime_mapping = cast("dict[object, object]", value)
    return all(isinstance(key, str) for key in runtime_mapping)


def _is_runtime_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def _is_runtime_mapping(value: object) -> TypeGuard[dict[object, object]]:
    return isinstance(value, dict)


def _remap_child_message(
    *,
    raw_value: dict[str, object],
    child_candidate: RuntimeValidationCandidate,
    child_obf_message: DumpCSMessage,
    child_non_obf_message: DumpCSMessage,
    remapping_context: RuntimeRemappingContext,
    instances_by_type: dict[str, list[dict[str, object]]],
    trace_handler: Callable[[RuntimeRemappingTraceEvent], None] | None,
    path: tuple[str, ...],
) -> RemapOutcome:
    """Remap a nested child message and propagate child-level failures."""
    remap_outcome = _remap_runtime_instance(
        instance=raw_value,
        current_candidate=child_candidate,
        obf_message=child_obf_message,
        non_obf_message=child_non_obf_message,
        remapping_context=remapping_context,
        instances_by_type=instances_by_type,
        trace_handler=trace_handler,
        path=path,
    )
    if remap_outcome.mapping_failure is None:
        return remap_outcome
    _emit_trace(
        trace_handler=trace_handler,
        path=path,
        message=remap_outcome.mapping_failure,
        mapping_failure_origin="child",
    )
    return RemapOutcome(
        value=raw_value,
        mapping_failure=remap_outcome.mapping_failure,
        mapping_failure_origin="child",
    )


def _resolve_child_mapping(
    *,
    obf_field: DumpCSMessageField,
    non_obf_field: DumpCSMessageField,
    parent_obf_message: DumpCSMessage,
    parent_non_obf_message: DumpCSMessage,
    remapping_context: RuntimeRemappingContext,
) -> ChildMappingResolution:
    """Resolve which candidate should be used for a nested child field."""
    parent_obf_metadata = remapping_context.get_obf_metadata(parent_obf_message)
    parent_non_obf_metadata = remapping_context.get_non_obf_metadata(parent_non_obf_message)
    obf_child_cls = parent_obf_metadata.child_message_cls_by_field_key.get(obf_field.field_key)
    non_obf_child_cls = parent_non_obf_metadata.child_message_cls_by_field_key.get(non_obf_field.field_key)
    if obf_child_cls is None or non_obf_child_cls is None:
        return ChildMappingResolution(status="unresolved")

    non_obf_pair_by_cls = remapping_context.candidates_by_non_obf.get(non_obf_child_cls)
    if not non_obf_pair_by_cls or not (child_candidate := non_obf_pair_by_cls.get(obf_child_cls)):
        return ChildMappingResolution(status="unresolved")

    return ChildMappingResolution(status="resolved", child_candidate=child_candidate)


def _emit_trace(
    *,
    trace_handler: Callable[[RuntimeRemappingTraceEvent], None] | None,
    path: tuple[str, ...],
    message: str,
    mapping_failure_origin: MappingFailureOrigin | None,
) -> None:
    if trace_handler is None:
        return
    trace_handler(
        RuntimeRemappingTraceEvent(
            kind="failure",
            path=path,
            message=message,
            mapping_failure_origin=mapping_failure_origin,
        )
    )
