from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.parsers._clr_type_utils import (
    extract_map_inner_types,
    extract_repeated_inner_type,
)
from DBDofusUnity.proto_mapper_assembly.parsers._dump_cs_structure import (
    ENUM_PATTERN,
    _Span,
    build_parent_name,
    find_smallest_enclosing_span,
)


def build_scoped_type_categories(
    code: str,
    type_spans: list[_Span],
    namespace_spans: list[_Span],
) -> dict[str, FieldCategoryEnum]:
    categories: dict[str, FieldCategoryEnum] = {}
    names_by_start: dict[int, str] = {}
    parent_cache: dict[int, str | None] = {}
    for span in type_spans:
        namespace = find_smallest_enclosing_span(namespace_spans, span.start)
        name = ".".join(
            part
            for part in (
                namespace.name if namespace else None,
                build_parent_name(span, type_spans, parent_cache),
                span.name,
            )
            if part
        )
        names_by_start[span.start] = name
        categories[name] = FieldCategoryEnum.MESSAGE
    for match in ENUM_PATTERN.finditer(code):
        parent = find_smallest_enclosing_span(type_spans, match.start())
        namespace = find_smallest_enclosing_span(namespace_spans, match.start())
        scope = names_by_start[parent.start] if parent else namespace.name if namespace else ""
        name = f"{scope}.{match.group(1)}" if scope else match.group(1)
        categories[name] = FieldCategoryEnum.ENUM
    return categories


def resolve_scoped_field_types(
    fields: list[DumpCSMessageField],
    scope: str,
    categories: dict[str, FieldCategoryEnum],
) -> list[DumpCSMessageField]:
    resolved: list[DumpCSMessageField] = []
    for field in fields:
        map_types = extract_map_inner_types(field.normalized_type)
        value_type = (
            map_types[1]
            if map_types
            else extract_repeated_inner_type(field.normalized_type) or field.normalized_type
        )
        value_category = _resolve_category(value_type, scope, categories)
        key_category = _resolve_category(map_types[0], scope, categories) if map_types else None
        category = field.category
        if category in {FieldCategoryEnum.MESSAGE, FieldCategoryEnum.ENUM} and value_category is not None:
            category = value_category
        resolved.append(
            field.model_copy(
                update={
                    "category": category,
                    "enum_value_type": _enum_name(value_type, value_category, field.enum_value_type),
                    "enum_key_type": (
                        _enum_name(map_types[0], key_category, field.enum_key_type) if map_types else None
                    ),
                }
            )
        )
    return resolved


def _resolve_category(
    type_name: str,
    scope: str,
    categories: dict[str, FieldCategoryEnum],
) -> FieldCategoryEnum | None:
    # Resolve relative CLR names from the enclosing type outward before considering global names.
    while scope:
        category = categories.get(f"{scope}.{type_name}")
        if category is not None:
            return category
        scope = scope.rpartition(".")[0]
    return categories.get(type_name)


def _enum_name(type_name: str, category: FieldCategoryEnum | None, previous: str | None) -> str | None:
    if category is None:
        return previous
    return type_name.rsplit(".", maxsplit=1)[-1] if category == FieldCategoryEnum.ENUM else None
