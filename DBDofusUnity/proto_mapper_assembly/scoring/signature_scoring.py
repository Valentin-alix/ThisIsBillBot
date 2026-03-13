from collections import Counter

from utils.cache import cache

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import (
    AccessAtomKey,
    AccessAtomSequenceKey,
    FieldAccessSignatures,
    FunctionSimilarityKey,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField
from DBDofusUnity.proto_mapper_assembly.interfaces.counter_profile import CounterProfile
from DBDofusUnity.proto_mapper_assembly.interfaces.function_access_signature import ForeignAccessSummaryKey
from DBDofusUnity.proto_mapper_assembly.scoring.primitives import (
    counter_profile_overlap_similarity,
    ratio_similarity,
)


def function_similarity_from_keys(
    left: FunctionSimilarityKey,
    right: FunctionSimilarityKey,
) -> float:
    """Self-access dominates; weak secondary signals only break ties and support acceptance."""
    if left.return_role != right.return_role:
        return 0.0

    if left.takes_message_parameter != right.takes_message_parameter:
        return 0.0

    score: float = 0.0

    score += 0.85 * access_atom_sequence_similarity(left.self_accesses, right.self_accesses)

    score += 0.05 * counter_profile_overlap_similarity(
        left=_opcode_histogram_profile(left.opcode_histogram),
        right=_opcode_histogram_profile(right.opcode_histogram),
    )

    score += 0.05 * counter_profile_overlap_similarity(
        left=_foreign_access_profile(left.foreign_access_summary),
        right=_foreign_access_profile(right.foreign_access_summary),
    )

    score += 0.05 * ratio_similarity(
        left.size,
        right.size,
        max_value=max(left.size, right.size),
    )

    return score


@cache
def _opcode_histogram_profile(opcode_histogram: tuple[tuple[str, int], ...]) -> CounterProfile:
    return CounterProfile(Counter(dict(opcode_histogram)))


@cache
def _foreign_access_profile(foreign_access_summary: ForeignAccessSummaryKey) -> CounterProfile:
    return CounterProfile(Counter(foreign_access_summary))


@cache
def access_atom_sequence_similarity(left: AccessAtomSequenceKey, right: AccessAtomSequenceKey) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0

    shared_length = min(len(left), len(right))
    total_similarity = sum(
        _access_atom_similarity_from_keys(left_access, right_access)
        for left_access, right_access in zip(left[:shared_length], right[:shared_length], strict=True)
    )
    return total_similarity / max(len(left), len(right))


@cache
def _access_atom_similarity_from_keys(left: AccessAtomKey, right: AccessAtomKey) -> float:
    """Compare access order and relative positions; ignore field offsets that drift across builds."""
    if left.entry_type != right.entry_type:
        return 0.0

    if left.field_type_shape != right.field_type_shape:
        return 0.0

    if left.access_kind != right.access_kind:
        return 0.0

    return ratio_similarity(
        left.index_in_function,
        right.index_in_function,
        max_value=max(left.index_in_function, right.index_in_function),
    )


@cache
def field_signature_similarity(left: FieldAccessSignatures, right: FieldAccessSignatures) -> float:
    if left.field_type_shape != right.field_type_shape:
        return 0
    return access_atom_sequence_similarity(left.accesses_key, right.accesses_key)


_UNTRACED_FIELD_SIMILARITY = 0.65


def field_evidence_similarity(left: FieldAccessSignatures, right: FieldAccessSignatures) -> float:
    """Missing traces are neutral; traced empty getter signatures still contradict populated ones."""
    if left.field_type_shape != right.field_type_shape:
        return 0
    if left.is_traced and right.is_traced:
        return field_signature_similarity(left, right)
    if not left.accesses_key and not right.accesses_key:
        return 1.0
    return _UNTRACED_FIELD_SIMILARITY


_NUMERIC_KIND_MISMATCH_SIMILARITY = 0.5


def declared_field_similarity(left: DumpCSMessageField, right: DumpCSMessageField) -> float:
    if left.field_type_shape != right.field_type_shape:
        return 0
    if (left.oneof_group_name is not None) != (right.oneof_group_name is not None):
        return 0
    return _numeric_kind_similarity(left, right)


def _numeric_kind_similarity(left: DumpCSMessageField, right: DumpCSMessageField) -> float:
    left_kind, right_kind = left.numeric_kind, right.numeric_kind
    if left_kind is None or right_kind is None or left_kind == right_kind:
        return 1.0
    return _NUMERIC_KIND_MISMATCH_SIMILARITY
