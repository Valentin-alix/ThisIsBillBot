from __future__ import annotations

import re
from dataclasses import dataclass

NAMESPACE_PATTERN = re.compile(r"^namespace\s+([\w.]+)", re.MULTILINE)
_TYPE_ACCESS_MODIFIER_PATTERN = r"(?:public|private|internal|protected(?:\s+internal)?|private\s+protected)"
TYPE_PATTERN = re.compile(
    rf"{_TYPE_ACCESS_MODIFIER_PATTERN}\s+"
    r"(?:(?:static|sealed|abstract|partial|readonly)\s+)*(class|struct|interface)\s+(\w+)"
    r"(?:\s*:\s*([^{\n]+?))?\s*//\s*TypeDefIndex:\s*(\d+)",
    re.MULTILINE,
)
ENUM_PATTERN = re.compile(r"public\s+enum\s+(\w+)\b", re.MULTILINE)
_ENUM_MEMBER_VALUE_PATTERN = re.compile(r"(\w+)\s*=\s*(-?\d+)")
_NESTED_TYPE_KW_PATTERN = re.compile(r"\b(?:class|struct|enum)\s+\w+")


@dataclass(frozen=True, slots=True)
class _Marker:
    position: int
    value: str
    type_def_index: int


@dataclass(frozen=True, slots=True)
class _Span:
    start: int
    end: int
    name: str
    type_def_index: int | None = None
    base_clause: str | None = None


def parse_enum_names(code: str) -> frozenset[str]:
    return frozenset(match.group(1) for match in ENUM_PATTERN.finditer(code))


def parse_enum_member_values(code: str) -> dict[str, dict[str, int]]:
    """Return {enum_name: {member_name: value}} for all public enums found in code."""
    result: dict[str, dict[str, int]] = {}
    for match in ENUM_PATTERN.finditer(code):
        body_span = _get_body_span(match.start(), code)
        if body_span is None:
            continue
        body = code[body_span[0] : body_span[1]]
        members = {
            member_match.group(1): int(member_match.group(2))
            for member_match in _ENUM_MEMBER_VALUE_PATTERN.finditer(body)
        }
        if members:
            result[match.group(1)] = members
    return result


def collect_file_descriptor_markers(code: str) -> list[_Marker]:
    markers: list[_Marker] = []
    for match in TYPE_PATTERN.finditer(code):
        declaration = match.group(0)
        if match.group(1) != "class" or " static " not in declaration:
            continue
        direct_body = get_stripped_direct_body(match.start(), code)
        if "FileDescriptor" not in direct_body:
            continue
        markers.append(
            _Marker(
                position=match.start(),
                value=match.group(2),
                type_def_index=int(match.group(4)),
            )
        )
    return sorted(markers, key=lambda marker: marker.type_def_index)


def collect_namespace_spans(code: str) -> list[_Span]:
    namespace_spans: list[_Span] = []
    for match in NAMESPACE_PATTERN.finditer(code):
        body_span = _get_body_span(match.start(), code)
        if body_span is None:
            continue
        _, end = body_span
        namespace_spans.append(_Span(start=match.start(), end=end, name=match.group(1)))
    return namespace_spans


def collect_message_spans(code: str) -> list[_Span]:
    message_spans: list[_Span] = []
    for match in TYPE_PATTERN.finditer(code):
        base_clause = match.group(3)
        if base_clause is None or "IMessage" not in base_clause:
            continue
        body_span = _get_body_span(match.start(), code)
        if body_span is None:
            continue
        _, end = body_span
        message_spans.append(
            _Span(
                start=match.start(),
                end=end,
                name=match.group(2),
                type_def_index=int(match.group(4)),
                base_clause=base_clause,
            )
        )
    return message_spans


def collect_type_spans(code: str) -> list[_Span]:
    type_spans: list[_Span] = []
    for match in TYPE_PATTERN.finditer(code):
        body_span = _get_body_span(match.start(), code)
        if body_span is None:
            continue
        _, end = body_span
        type_spans.append(
            _Span(
                start=match.start(),
                end=end,
                name=match.group(2),
                type_def_index=int(match.group(4)),
                base_clause=match.group(3),
            )
        )
    return type_spans


def build_parent_name(
    current_span: _Span,
    parent_spans: list[_Span],
    cache: dict[int, str | None],
) -> str | None:
    """
    Return the dotted parent chain for current_span, using parent_spans for ancestry lookup.

    The cache is keyed by span.start so it can be safely shared across calls with
    different span lists (e.g. message_spans for iteration, type_spans for ancestry).
    """
    if current_span.start in cache:
        return cache[current_span.start]
    parent_index = _find_smallest_enclosing_span_index(
        parent_spans,
        current_span.start,
        current_span.end,
        excluded_start=current_span.start,
    )
    if parent_index is None:
        cache[current_span.start] = None
        return None
    parent_span = parent_spans[parent_index]
    grand_parent_name = build_parent_name(parent_span, parent_spans, cache)
    result = f"{grand_parent_name}.{parent_span.name}" if grand_parent_name else parent_span.name
    cache[current_span.start] = result
    return result


def find_smallest_enclosing_span(spans: list[_Span], pos: int) -> _Span | None:
    best_span: _Span | None = None
    best_size: int | None = None
    for span in spans:
        if span.start < pos <= span.end:
            current_size = span.end - span.start
            if best_size is None or current_size < best_size:
                best_size = current_size
                best_span = span
    return best_span


def get_stripped_direct_body(start: int, code: str) -> str:
    return _strip_nested_type_bodies(_get_direct_body(start, code))


def _find_smallest_enclosing_span_index(
    spans: list[_Span],
    start: int,
    end: int,
    excluded_start: int | None = None,
) -> int | None:
    best_index: int | None = None
    best_size: int | None = None
    for candidate_index, span in enumerate(spans):
        if excluded_start is not None and span.start == excluded_start:
            continue
        if span.start < start <= end <= span.end:
            current_size = span.end - span.start
            if best_size is None or current_size < best_size:
                best_size = current_size
                best_index = candidate_index
    return best_index


def _get_direct_body(start: int, code: str) -> str:
    body_span = _get_body_span(start, code)
    if body_span is None:
        return ""
    body_start, body_end = body_span
    return code[body_start:body_end]


def _get_body_span(start: int, code: str) -> tuple[int, int] | None:
    opening_brace_pos = code.find("{", start)
    if opening_brace_pos == -1:
        return None
    closing_brace_pos = _find_matching_brace(opening_brace_pos, code)
    if closing_brace_pos is None:
        return None
    return opening_brace_pos + 1, closing_brace_pos


def _strip_nested_type_bodies(code: str) -> str:
    stripped_chunks: list[str] = []
    previous_end = 0
    for match in _NESTED_TYPE_KW_PATTERN.finditer(code):
        if match.start() < previous_end:
            continue
        brace_pos = code.find("{", match.end())
        if brace_pos == -1:
            continue
        closing_brace_pos = _find_matching_brace(brace_pos, code)
        if closing_brace_pos is None:
            continue
        stripped_chunks.append(code[previous_end : brace_pos + 1])
        stripped_chunks.append("}")
        previous_end = closing_brace_pos + 1
    stripped_chunks.append(code[previous_end:])
    return "".join(stripped_chunks)


def _find_matching_brace(opening_brace_pos: int, code: str) -> int | None:
    depth = 1
    cursor = opening_brace_pos + 1
    while cursor < len(code) and depth > 0:
        if code[cursor] == "{":
            depth += 1
        elif code[cursor] == "}":
            depth -= 1
        cursor += 1
    if depth != 0:
        return None
    return cursor - 1
