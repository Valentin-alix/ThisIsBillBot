from collections import Counter
from enum import StrEnum, auto
from functools import cached_property
from typing import Literal, NamedTuple

from pydantic import BaseModel

from proto_mapper_assembly.interfaces.field_category import (
    CompactFieldTypeShape,
    FieldTypeShape,
)


class ReturnRole(StrEnum):
    VOID = auto()
    SELF = auto()
    OTHER = auto()


class CfgStats(BaseModel):
    """Control-flow shape of a traced function, a steadier size proxy than its byte count."""

    basic_block_count: int
    edge_count: int
    back_edge_count: int
    max_block_depth: int

    @property
    def cyclomatic_complexity(self) -> int:
        return self.edge_count - self.basic_block_count + 2

    @cached_property
    def shape_key(self) -> "CfgShapeKey":
        return CfgShapeKey(
            basic_block_count=self.basic_block_count,
            edge_count=self.edge_count,
            back_edge_count=self.back_edge_count,
            max_block_depth=self.max_block_depth,
        )


class CfgShapeKey(NamedTuple):
    basic_block_count: int
    edge_count: int
    back_edge_count: int
    max_block_depth: int


class AccessAtomKey(NamedTuple):
    entry_type: str
    access_kind: str
    field_type_shape: FieldTypeShape | None
    field_offset: int | None
    index_in_function: int


type AccessAtomSequenceKey = tuple[AccessAtomKey, ...]
type ForeignAccessSummaryKey = tuple[str, ...]
type StableCalleesKey = tuple[str, ...]


class FunctionSimilarityKey(NamedTuple):
    return_role: ReturnRole
    takes_message_parameter: bool
    size: int
    self_accesses: AccessAtomSequenceKey
    foreign_access_summary: ForeignAccessSummaryKey
    opcode_histogram: tuple[tuple[str, int], ...]  # pour que ca soit hashable
    stable_callees: StableCalleesKey
    cfg_shape: CfgShapeKey | None


class AccessAtomSignature(BaseModel):
    entry_type: Literal["field", "typeinfo"]
    access_kind: str
    field_type_shape: CompactFieldTypeShape | None = None
    field_offset: int | None = None
    index_in_function: int

    @cached_property
    def similarity_key(self) -> AccessAtomKey:
        return AccessAtomKey(
            entry_type=self.entry_type,
            access_kind=self.access_kind,
            field_type_shape=self.field_type_shape,
            field_offset=self.field_offset,
            index_in_function=self.index_in_function,
        )


class FunctionAccessSignature(BaseModel):
    return_role: ReturnRole
    takes_message_parameter: bool
    size: int
    self_accesses: list[AccessAtomSignature]
    foreign_access_summary: list[str]
    opcode_histogram: Counter[str]
    stable_callees: list[str] = []
    """Empty on signatures exported before callees were traced, so those files stay loadable."""

    cfg_stats: CfgStats | None = None
    """Null on the signatures synthesized for enum comparison, which describe no scanned function."""

    @cached_property
    def stable_callees_key(self) -> StableCalleesKey:
        return tuple(sorted(set(self.stable_callees)))

    @cached_property
    def stable_callees_counter(self) -> Counter[str]:
        return Counter(self.stable_callees_key)

    @cached_property
    def self_accesses_key(self) -> AccessAtomSequenceKey:
        # index_in_function brut (rang d'instruction dans la fonction) bouge un peu trop à chaque build IL2Cpp, on check juste l'ordre selon les field access / type info.
        ordered = sorted(self.self_accesses, key=lambda access: access.index_in_function)
        return tuple(
            AccessAtomKey(
                entry_type=access.entry_type,
                access_kind=access.access_kind,
                field_type_shape=access.field_type_shape,
                field_offset=access.field_offset,
                index_in_function=access.index_in_function,
            )
            for access in ordered
        )

    @cached_property
    def foreign_access_summary_key(self) -> ForeignAccessSummaryKey:
        return tuple(self.foreign_access_summary)

    @cached_property
    def foreign_access_summary_counter(self) -> Counter[str]:
        return Counter(self.foreign_access_summary_key)

    @cached_property
    def foreign_access_summary_length(self) -> int:
        return len(self.foreign_access_summary_key)

    @cached_property
    def similarity_key(self) -> FunctionSimilarityKey:
        return FunctionSimilarityKey(
            return_role=self.return_role,
            takes_message_parameter=self.takes_message_parameter,
            size=self.size,
            self_accesses=self.self_accesses_key,
            foreign_access_summary=self.foreign_access_summary_key,
            opcode_histogram=tuple(self.opcode_histogram.items()),
            stable_callees=self.stable_callees_key,
            cfg_shape=self.cfg_stats.shape_key if self.cfg_stats is not None else None,
        )
