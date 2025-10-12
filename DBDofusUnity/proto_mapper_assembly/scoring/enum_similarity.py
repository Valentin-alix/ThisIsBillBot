from __future__ import annotations

from dataclasses import dataclass
from functools import cache, cached_property

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import (
    AccessAtomSignature,
    AccessTraceDocument,
    FunctionAccessSignature,
    ReturnRole,
    TracedFunction,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import EnumCalledFunctionRef, EnumSignatureEntry
from DBDofusUnity.proto_mapper_assembly.scoring.primitives import get_average_best_similarity_sequences
from DBDofusUnity.proto_mapper_assembly.scoring.signature_scoring import function_similarity_from_keys

type FunctionSignatureSequence = tuple[FunctionAccessSignature, ...]


@dataclass(frozen=True)
class EnumSimilarityContext:
    left_access_trace: AccessTraceDocument
    right_access_trace: AccessTraceDocument


@dataclass(frozen=True)
class EnumFunctionSignatureResolver:
    access_trace: AccessTraceDocument

    @cached_property
    def signature_by_address(self) -> dict[str, FunctionAccessSignature]:
        return {
            function_address: _build_enum_function_signature(traced_function)
            for function_address, traced_function in self.access_trace.functions_by_address.items()
        }

    def resolve_function_signature(self, function_ref: EnumCalledFunctionRef) -> FunctionAccessSignature:
        signature = self.signature_by_address.get(function_ref.function_address)
        assert signature is not None, f"Missing traced function for enum ref {function_ref.function_address}"
        return signature


@cache
def build_enum_function_signature_resolver(
    access_trace: AccessTraceDocument,
) -> EnumFunctionSignatureResolver:
    return EnumFunctionSignatureResolver(access_trace)


def enum_member_similarity(
    left_entry: EnumSignatureEntry,
    left_member_value: int,
    right_entry: EnumSignatureEntry,
    right_member_value: int,
    *,
    context: EnumSimilarityContext,
) -> float:
    left_resolver = build_enum_function_signature_resolver(context.left_access_trace)
    right_resolver = build_enum_function_signature_resolver(context.right_access_trace)
    left_signatures = _collect_member_function_signatures(
        entry=left_entry,
        member_value=left_member_value,
        resolver=left_resolver,
    )
    right_signatures = _collect_member_function_signatures(
        entry=right_entry,
        member_value=right_member_value,
        resolver=right_resolver,
    )
    return get_average_best_similarity_sequences(
        left_signatures,
        right_signatures,
        lambda left, right: function_similarity_from_keys(left.similarity_key, right.similarity_key),
    )


def enum_signature_similarity(
    left_entry: EnumSignatureEntry,
    right_entry: EnumSignatureEntry,
    *,
    context: EnumSimilarityContext,
) -> float:
    left_member_values = tuple(sorted(int(member_value) for member_value in left_entry.member_value_to_name))
    right_member_values = tuple(
        sorted(int(member_value) for member_value in right_entry.member_value_to_name)
    )
    return get_average_best_similarity_sequences(
        left_member_values,
        right_member_values,
        lambda left_member_value, right_member_value: enum_member_similarity(
            left_entry,
            left_member_value,
            right_entry,
            right_member_value,
            context=context,
        ),
    )


def _collect_member_function_signatures(
    *,
    entry: EnumSignatureEntry,
    member_value: int,
    resolver: EnumFunctionSignatureResolver,
) -> FunctionSignatureSequence:
    signatures: list[FunctionAccessSignature] = []
    for switch_pattern in entry.switch_patterns:
        for member_group in switch_pattern.member_groups:
            if member_value not in member_group.member_values:
                continue
            for called_function in member_group.called_functions:
                signature = called_function.function_signature or resolver.resolve_function_signature(
                    called_function
                )
                signatures.extend([signature] * called_function.occurrence_count)
    return tuple(signatures)


def _metadata_resolution_family(resolution_kind: str | None) -> str:
    if resolution_kind in {"method_definition", "api", "export"}:
        return "stable_metadata"
    if resolution_kind in {"ida_type", "decompiled"}:
        return "ida_inferred"
    return "unknown"


def _build_enum_function_signature(traced_function: TracedFunction) -> FunctionAccessSignature:
    metadata = traced_function.resolved_metadata
    parameter_kinds = [] if metadata is None else metadata.parameter_kinds
    return FunctionAccessSignature(
        return_role=_enum_return_role(None if metadata is None else metadata.return_kind),
        takes_message_parameter="message_like" in parameter_kinds,
        size=traced_function.size,
        self_accesses=[
            AccessAtomSignature(
                entry_type="typeinfo",
                access_kind=f"param:{parameter_kind}",
                field_offset=None,
                index_in_function=parameter_index,
            )
            for parameter_index, parameter_kind in enumerate(parameter_kinds)
        ],
        foreign_access_summary=_build_enum_foreign_summary(traced_function),
        opcode_histogram=traced_function.opcode_histogram,
        stable_callees=traced_function.stable_callees,
        cfg_stats=traced_function.cfg_stats,
    )


def _enum_return_role(return_kind: str | None) -> ReturnRole:
    if return_kind == "void":
        return ReturnRole.VOID
    return ReturnRole.OTHER


def _build_enum_foreign_summary(traced_function: TracedFunction) -> list[str]:
    metadata = traced_function.resolved_metadata
    if metadata is None:
        return ["resolution:unknown", "return:unknown"]
    summary = [
        f"resolution:{_metadata_resolution_family(metadata.resolution_kind)}",
        f"return:{metadata.return_kind}",
    ]
    if (
        metadata.resolution_kind in {"method_definition", "api", "export"}
        and metadata.raw_signature is not None
    ):
        joined_parameter_types = ", ".join(metadata.parameter_types)
        summary.append(f"stable_signature:{metadata.return_type or 'unknown'}({joined_parameter_types})")
    return summary
