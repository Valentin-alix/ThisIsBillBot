import re
from collections.abc import Iterable
from pathlib import Path

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.parsers._dump_cs_message_body_parser import parse_message_body
from DBDofusUnity.proto_mapper_assembly.parsers._dump_cs_structure import (
    _Marker,
    _Span,
    build_parent_name,
    collect_file_descriptor_markers,
    collect_message_spans,
    collect_namespace_spans,
    collect_type_spans,
    find_smallest_enclosing_span,
    get_stripped_direct_body,
    parse_enum_names,
)

_BASE_CLASS_NAME_RE = re.compile(r"^\s*([\w.]+)")


def parse_messages(dump_cs_path: str) -> list[DumpCSMessage]:
    code = Path(dump_cs_path).read_text(encoding="utf-8", errors="ignore")
    return _parse_messages_impl(code, parse_enum_names(code))


def load_tracking_types(base_dir: Path) -> list[DumpCSMessage]:
    tracking_types: list[DumpCSMessage] = []
    cs_dir = base_dir / "cs"
    for current_path in _iter_tracking_cs_paths(cs_dir):
        tracking_types.extend(parse_types(str(current_path)))
    return tracking_types


def _iter_tracking_cs_paths(cs_dir: Path) -> Iterable[Path]:
    for current_path in sorted(cs_dir.glob("*.cs")):
        if current_path.name == "Core.cs" or current_path.name.startswith("Ankama.Dofus.Protocol."):
            yield current_path


def parse_types(dump_cs_path: str) -> list[DumpCSMessage]:
    code = Path(dump_cs_path).read_text(encoding="utf-8", errors="ignore")
    return _parse_types_impl(code, parse_enum_names(code))


def _parse_messages_impl(
    code: str,
    enum_names: frozenset[str] = frozenset(),
) -> list[DumpCSMessage]:
    return _parse_spans_impl(
        code,
        collect_message_spans(code),
        enum_names,
        parent_spans=collect_type_spans(code),
    )


def _parse_types_impl(
    code: str,
    enum_names: frozenset[str] = frozenset(),
) -> list[DumpCSMessage]:
    return _parse_spans_impl(code, collect_type_spans(code), enum_names)


def _parse_spans_impl(
    code: str,
    message_spans: list[_Span],
    enum_names: frozenset[str] = frozenset(),
    parent_spans: list[_Span] | None = None,
) -> list[DumpCSMessage]:
    namespace_spans = collect_namespace_spans(code)
    file_descriptor_markers = collect_file_descriptor_markers(code)
    parent_name_cache: dict[int, str | None] = {}
    resolved_parent_spans = parent_spans if parent_spans is not None else message_spans
    return [
        _build_message(
            message_span,
            code,
            file_descriptor_markers,
            namespace_spans,
            resolved_parent_spans,
            parent_name_cache,
            enum_names,
        )
        for message_span in message_spans
    ]


def _build_message(
    message_span: _Span,
    code: str,
    file_descriptor_markers: list[_Marker],
    namespace_spans: list[_Span],
    parent_spans: list[_Span],
    parent_name_cache: dict[int, str | None],
    enum_names: frozenset[str],
) -> DumpCSMessage:
    namespace_span = find_smallest_enclosing_span(namespace_spans, message_span.start)
    message_type_def_index = message_span.type_def_index
    if message_type_def_index is None:
        error_message = "Missing TypeDefIndex"
        raise ValueError(error_message)
    file_descriptor = _resolve_message_file_descriptor(
        file_descriptor_markers,
        message_type_def_index,
        message_span.name,
    )
    stripped_body = get_stripped_direct_body(message_span.start, code)
    fields, properties = parse_message_body(stripped_body, enum_names)
    return DumpCSMessage(
        file_descriptor=file_descriptor,
        name=message_span.name,
        fields=fields,
        properties=properties,
        namespace=namespace_span.name if namespace_span is not None else None,
        parent_name=build_parent_name(message_span, parent_spans, parent_name_cache),
        base_class_name=_extract_base_class_name(message_span.base_clause),
    )


def _extract_base_class_name(base_clause: str | None) -> str | None:
    if base_clause is None:
        return None
    first_base_type = base_clause.split(",", 1)[0]
    matched = _BASE_CLASS_NAME_RE.match(first_base_type)
    if matched is None:
        return None
    return matched.group(1)


def _resolve_message_file_descriptor(
    file_descriptor_markers: list[_Marker],
    message_type_def_index: int,
    fallback_name: str,
) -> str:
    previous_marker: _Marker | None = None
    for marker in file_descriptor_markers:
        if marker.type_def_index > message_type_def_index:
            return previous_marker.value if previous_marker is not None else marker.value
        previous_marker = marker
    return previous_marker.value if previous_marker is not None else fallback_name
