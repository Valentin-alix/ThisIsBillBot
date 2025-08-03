from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property, partial
from operator import attrgetter

from cachetools import LRUCache, cachedmethod

from proto_mapper_assembly.helpers.proto_helpers import (
    build_types_by_short_name,
    resolve_child_message_cls,
)
from proto_mapper_assembly.interfaces.assembly_access import AccessTraceDocument, MessageAccessSignature
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField
from proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from proto_mapper_assembly.scoring.enum_similarity import (
    EnumSimilarityContext,
    enum_signature_similarity,
)
from proto_mapper_assembly.scoring.primitives import (
    counter_profile_overlap_similarity,
    get_average_best_similarity_sequences,
    ratio_similarity,
)
from proto_mapper_assembly.scoring.signature_scoring import (
    declared_field_similarity,
    field_signature_similarity,
    function_similarity_from_keys,
)

_MESSAGE_ASSEMBLY_FUNCTION_WEIGHT = 0.35
_MESSAGE_ASSEMBLY_FIELD_WEIGHT = 0.40
_MESSAGE_ASSEMBLY_WEIGHT = _MESSAGE_ASSEMBLY_FUNCTION_WEIGHT + _MESSAGE_ASSEMBLY_FIELD_WEIGHT
_DEFAULT_MAX_STRUCTURE_CHILD_DEPTH = 8

_STRUCTURE_LIVE_ALIGNMENT_WEIGHT = 0.7
_STRUCTURE_DECLARED_SHAPE_WEIGHT = 0.3
_ONEOF_PARTITION_MISMATCH_FLOOR = 0.7
_COVERAGE_ASSEMBLY_WEIGHT_FLOOR = 0.5


@dataclass(frozen=True)
class StructureSimilarityContext:
    left_signatures_by_cls: dict[str, MessageAccessSignature]
    right_signatures_by_cls: dict[str, MessageAccessSignature]
    left_enum_signatures_by_name: dict[str, EnumSignatureEntry]
    right_enum_signatures_by_name: dict[str, EnumSignatureEntry]
    left_access_trace: AccessTraceDocument
    right_access_trace: AccessTraceDocument
    max_child_depth: int = _DEFAULT_MAX_STRUCTURE_CHILD_DEPTH
    message_similarity_cache: dict[tuple[str, str, int], float] = field(
        default_factory=dict[tuple[str, str, int], float]
    )
    _enum_similarity_cache: LRUCache[tuple[str, str], float | None] = field(
        default_factory=lambda: LRUCache(maxsize=8192)
    )

    @cached_property
    def left_messages_by_cls(self) -> dict[str, DumpCSMessage]:
        return {
            message_cls: signature.dump_cs_msg
            for message_cls, signature in self.left_signatures_by_cls.items()
        }

    @cached_property
    def right_messages_by_cls(self) -> dict[str, DumpCSMessage]:
        return {
            message_cls: signature.dump_cs_msg
            for message_cls, signature in self.right_signatures_by_cls.items()
        }

    @cached_property
    def left_type_index(self) -> dict[str, tuple[DumpCSMessage, ...]]:
        return build_types_by_short_name(self.left_messages_by_cls)

    @cached_property
    def right_type_index(self) -> dict[str, tuple[DumpCSMessage, ...]]:
        return build_types_by_short_name(self.right_messages_by_cls)

    @cachedmethod(cache=attrgetter("_enum_similarity_cache"))
    def resolve_enum_similarity(self, left_enum_type: str, right_enum_type: str) -> float | None:
        left_enum_signature = self.left_enum_signatures_by_name.get(left_enum_type)
        right_enum_signature = self.right_enum_signatures_by_name.get(right_enum_type)
        if left_enum_signature is None or right_enum_signature is None:
            return None
        return enum_signature_similarity(
            left_enum_signature,
            right_enum_signature,
            context=EnumSimilarityContext(self.left_access_trace, self.right_access_trace),
        )


@dataclass(frozen=True)
class AssemblySimilarityData:
    function_similarity: float
    fields_similarity: float

    @cached_property
    def assembly_similarity(self) -> float:
        return (
            (_MESSAGE_ASSEMBLY_FIELD_WEIGHT * self.fields_similarity)
            + (_MESSAGE_ASSEMBLY_FUNCTION_WEIGHT * self.function_similarity)
        ) / _MESSAGE_ASSEMBLY_WEIGHT

    def __str__(self) -> str:
        return f"function sim {self.function_similarity} | field sim {self.fields_similarity}"


@dataclass(frozen=True)
class MessageSimilarityScoreData:
    structure_similarity: float
    assembly_sim_data: AssemblySimilarityData
    assembly_weight: float
    """Effective assembly weight; lowered toward structure when runtime evidence is sparse."""

    @cached_property
    def static_similarity(self) -> float:
        return (self.assembly_weight * self.assembly_sim_data.assembly_similarity) + (
            (1.0 - self.assembly_weight) * self.structure_similarity
        )


@dataclass(frozen=True)
class StructureHardening:
    """The obfuscation-stable half of a pair's structure score, independent of its alignment."""

    declared_shape_score: float
    oneof_factor: float

    def apply(self, raw_structure: float) -> float:
        blended = (
            _STRUCTURE_LIVE_ALIGNMENT_WEIGHT * raw_structure
            + _STRUCTURE_DECLARED_SHAPE_WEIGHT * self.declared_shape_score
        )
        return blended * self.oneof_factor


def build_structure_hardening(
    left: MessageAccessSignature, right: MessageAccessSignature
) -> StructureHardening:
    oneof_score = _oneof_partition_similarity(left, right)
    return StructureHardening(
        declared_shape_score=_declared_shape_similarity(left, right),
        oneof_factor=(
            _ONEOF_PARTITION_MISMATCH_FLOOR + (1.0 - _ONEOF_PARTITION_MISMATCH_FLOOR) * oneof_score
        ),
    )


def shallow_structure_score(left: MessageAccessSignature, right: MessageAccessSignature) -> float:
    return _shallow_structure_score(left, right)


def deep_structure_score(
    left: MessageAccessSignature,
    right: MessageAccessSignature,
    *,
    context: StructureSimilarityContext,
) -> float:
    return _structure_score_with_context(left, right, context=context, depth=0, visited_pairs=frozenset())


def compute_structure_score(
    left: MessageAccessSignature,
    right: MessageAccessSignature,
    *,
    context: StructureSimilarityContext | None = None,
) -> float:
    """
    Hardened structure score for a message pair.

    Shallow live-field alignment when ``context`` is ``None``, deep recursive matching otherwise.
    The score is always blended with the declared field-shape multiset and scaled by the oneof
    partition factor, so callers cannot accidentally skip the obfuscation-stable signals.
    Root vs nested message mismatch shortcuts to ``0.0``.
    """
    if left.dump_cs_msg.is_root_msg != right.dump_cs_msg.is_root_msg:
        return 0.0
    raw_structure = _raw_structure_score(left, right, context=context)
    return _harden_structure_score(raw_structure, left, right)


def compute_message_similarity(
    left: MessageAccessSignature,
    right: MessageAccessSignature,
    *,
    structure_score: float,
) -> MessageSimilarityScoreData:
    """
    Build the final score data given an already-computed (hardened) structure score.

    Adds the runtime-evidence assembly similarity and the coverage-aware blend weight.
    """
    return MessageSimilarityScoreData(
        structure_similarity=structure_score,
        assembly_sim_data=_assembly_similarity_data(left, right),
        assembly_weight=coverage_assembly_weight(left, right),
    )


def coverage_assembly_weight(left: MessageAccessSignature, right: MessageAccessSignature) -> float:
    """
    Effective assembly weight, lowered toward structure as declared-field trace coverage thins out.
    """
    coverage = pair_evidence_coverage(left, right) or 0.0
    coverage_factor = _COVERAGE_ASSEMBLY_WEIGHT_FLOOR + (1.0 - _COVERAGE_ASSEMBLY_WEIGHT_FLOOR) * coverage
    return _MESSAGE_ASSEMBLY_WEIGHT * coverage_factor


def pair_evidence_coverage(left: MessageAccessSignature, right: MessageAccessSignature) -> float | None:
    """Lowest declared-field trace coverage across the pair; None when neither side declares fields."""
    coverages = [
        coverage for coverage in (left.evidence_coverage, right.evidence_coverage) if coverage is not None
    ]
    if not coverages:
        return None
    return min(coverages)


def _raw_structure_score(
    left: MessageAccessSignature,
    right: MessageAccessSignature,
    *,
    context: StructureSimilarityContext | None,
) -> float:
    if context is None:
        return _shallow_structure_score(left, right)
    return _structure_score_with_context(left, right, context=context, depth=0, visited_pairs=frozenset())


def _shallow_structure_score(left: MessageAccessSignature, right: MessageAccessSignature) -> float:
    return get_average_best_similarity_sequences(
        left.declared_similarity_fields,
        right.declared_similarity_fields,
        declared_field_similarity,
    )


def _structure_score_with_context(
    left: MessageAccessSignature,
    right: MessageAccessSignature,
    *,
    context: StructureSimilarityContext,
    depth: int,
    visited_pairs: frozenset[tuple[str, str]],
) -> float:
    pair_key = (left.message_cls, right.message_cls)
    if depth > context.max_child_depth or pair_key in visited_pairs:
        return _shallow_structure_score(left, right)

    remaining_depth = context.max_child_depth - depth
    cache_key = (left.message_cls, right.message_cls, remaining_depth)
    if cache_key in context.message_similarity_cache:
        return context.message_similarity_cache[cache_key]

    next_visited_pairs = visited_pairs | {pair_key}
    score = get_average_best_similarity_sequences(
        left.declared_similarity_fields,
        right.declared_similarity_fields,
        partial(
            _declared_field_structure_similarity,
            left_parent=left,
            right_parent=right,
            context=context,
            depth=depth,
            visited_pairs=next_visited_pairs,
        ),
    )
    context.message_similarity_cache[cache_key] = score
    return score


def _assembly_similarity_data(
    left: MessageAccessSignature,
    right: MessageAccessSignature,
) -> AssemblySimilarityData:
    function_score = get_average_best_similarity_sequences(
        left.function_similarity_keys, right.function_similarity_keys, function_similarity_from_keys
    )
    field_score = get_average_best_similarity_sequences(
        left=left.field_signatures, right=right.field_signatures, scorer=field_signature_similarity
    )
    return AssemblySimilarityData(function_similarity=function_score, fields_similarity=field_score)


def _harden_structure_score(
    raw_structure: float,
    left: MessageAccessSignature,
    right: MessageAccessSignature,
) -> float:
    """
    Reinforce the live-field structure score with obfuscation-stable structural signals.

    The live-field alignment is blended with the overlap of the full declared field-shape
    multisets, then scaled by how closely the oneof partitions match. Both extra signals come
    from the declared proto shape, so they discriminate even when few fields carry runtime traces.
    """
    return build_structure_hardening(left, right).apply(raw_structure)


def _declared_shape_similarity(left: MessageAccessSignature, right: MessageAccessSignature) -> float:
    return counter_profile_overlap_similarity(
        left=left.declared_shape_profile, right=right.declared_shape_profile
    )


def _oneof_partition_similarity(left: MessageAccessSignature, right: MessageAccessSignature) -> float:
    left_sizes = left.dump_cs_msg.oneof_group_sizes
    right_sizes = right.dump_cs_msg.oneof_group_sizes
    return get_average_best_similarity_sequences(left_sizes, right_sizes, _oneof_group_size_similarity)


def _oneof_group_size_similarity(left_size: int, right_size: int) -> float:
    return ratio_similarity(left_size, right_size, max_value=max(left_size, right_size))


def _declared_field_structure_similarity(
    left: DumpCSMessageField,
    right: DumpCSMessageField,
    *,
    left_parent: MessageAccessSignature,
    right_parent: MessageAccessSignature,
    context: StructureSimilarityContext,
    depth: int,
    visited_pairs: frozenset[tuple[str, str]],
) -> float:
    shallow_score = declared_field_similarity(left, right)
    if shallow_score == 0.0:
        return 0.0

    enum_score = _enum_field_structure_similarity(left, right, context=context)
    if enum_score is not None:
        return enum_score

    child_score = _child_field_structure_similarity(
        left,
        right,
        left_parent=left_parent,
        right_parent=right_parent,
        context=context,
        depth=depth,
        visited_pairs=visited_pairs,
    )
    if child_score is not None:
        return child_score

    return shallow_score


def _enum_field_structure_similarity(
    left: DumpCSMessageField,
    right: DumpCSMessageField,
    *,
    context: StructureSimilarityContext,
) -> float | None:
    slot_scores: list[float] = []
    key_score = _resolve_contextual_enum_slot_score(
        left_enum_type=left.enum_field_types.key,
        right_enum_type=right.enum_field_types.key,
        context=context,
    )
    if key_score is not None:
        slot_scores.append(key_score)

    value_score = _resolve_contextual_enum_slot_score(
        left_enum_type=left.enum_field_types.value,
        right_enum_type=right.enum_field_types.value,
        context=context,
    )
    if value_score is not None:
        slot_scores.append(value_score)

    if not slot_scores:
        return None
    return sum(slot_scores) / len(slot_scores)


def _resolve_contextual_enum_slot_score(
    *,
    left_enum_type: str | None,
    right_enum_type: str | None,
    context: StructureSimilarityContext,
) -> float | None:
    if left_enum_type is None or right_enum_type is None:
        return None
    return context.resolve_enum_similarity(left_enum_type, right_enum_type)


def _child_field_structure_similarity(
    left: DumpCSMessageField,
    right: DumpCSMessageField,
    *,
    left_parent: MessageAccessSignature,
    right_parent: MessageAccessSignature,
    context: StructureSimilarityContext,
    depth: int,
    visited_pairs: frozenset[tuple[str, str]],
) -> float | None:
    left_child_cls = resolve_child_message_cls(
        field=left,
        parent_message=left_parent.dump_cs_msg,
        messages_by_cls=context.left_messages_by_cls,
        type_index=context.left_type_index,
    )
    right_child_cls = resolve_child_message_cls(
        field=right,
        parent_message=right_parent.dump_cs_msg,
        messages_by_cls=context.right_messages_by_cls,
        type_index=context.right_type_index,
    )
    if left_child_cls is None or right_child_cls is None:
        return None

    left_child_signature = context.left_signatures_by_cls[left_child_cls]
    right_child_signature = context.right_signatures_by_cls[right_child_cls]

    return _structure_score_with_context(
        left_child_signature,
        right_child_signature,
        context=context,
        depth=depth + 1,
        visited_pairs=visited_pairs,
    )
