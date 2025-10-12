from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import cached_property

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField, FieldKey


@dataclass(frozen=True)
class MessageFieldResolutionLookup:
    fields: list[DumpCSMessageField]

    @cached_property
    def by_field_key(self) -> dict[FieldKey, DumpCSMessageField]:
        return {field.field_key: field for field in self.fields}

    @cached_property
    def declared_field_by_key(self) -> dict[FieldKey, DumpCSMessageField]:
        return {field.field_key: field for field in self.declared_proto_fields}

    @cached_property
    def by_property_name(self) -> dict[str, DumpCSMessageField]:
        return _build_unique_field_by_key(
            fields=self.fields,
            key_getter=lambda field: field.property_name,
        )

    @cached_property
    def by_clean_name(self) -> dict[str, DumpCSMessageField]:
        return _build_unique_field_by_key(
            fields=self.fields,
            key_getter=lambda field: field.clean_field_name,
        )

    @cached_property
    def by_instance_offset(self) -> dict[int, DumpCSMessageField]:
        return _build_unique_field_by_key(
            fields=[field for field in self.fields if field.is_instance_backed_proto_field],
            key_getter=lambda field: field.memory_offset,
        )

    @cached_property
    def by_offset(self) -> dict[int, tuple[DumpCSMessageField, ...]]:
        fields_by_offset: dict[int, list[DumpCSMessageField]] = defaultdict(list)
        for _field in self.fields:
            fields_by_offset[_field.memory_offset].append(_field)
        return {
            field_offset: tuple(fields_at_offset)
            for field_offset, fields_at_offset in fields_by_offset.items()
        }

    @cached_property
    def declared_proto_fields(self) -> tuple[DumpCSMessageField, ...]:
        return tuple(
            sorted(
                (field for field in self.fields if field.is_declared_proto_shape_field),
                key=lambda field: field.memory_offset,
            )
        )


def _build_unique_field_by_key[K](
    *,
    fields: Sequence[DumpCSMessageField],
    key_getter: Callable[[DumpCSMessageField], K | None],
) -> dict[K, DumpCSMessageField]:
    """Index fields by ``key_getter``, keeping only keys that map to a single field."""
    grouped_fields: dict[K, list[DumpCSMessageField]] = defaultdict(list)
    for _field in fields:
        key = key_getter(_field)
        if key is None:
            continue
        grouped_fields[key].append(_field)
    return {
        key: grouped_field_entries[0]
        for key, grouped_field_entries in grouped_fields.items()
        if len(grouped_field_entries) == 1
    }
