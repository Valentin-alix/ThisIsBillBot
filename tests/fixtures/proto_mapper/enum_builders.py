from collections import Counter

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import (
    AccessTraceDocument,
    EnumFunctionResolvedMetadata,
    TracedFunction,
    format_trace_address,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import (
    EnumCalledFunctionRef,
    EnumMemberGroup,
    EnumSignatureEntry,
    EnumSwitchPattern,
)


def enum_function_ref(
    *,
    call_target_addr: int,
    function_addr: int | None = None,
    occurrence_count: int = 1,
) -> EnumCalledFunctionRef:
    resolved_function_addr = function_addr or call_target_addr
    return EnumCalledFunctionRef(
        function_address=format_trace_address(resolved_function_addr),
        call_target_address=format_trace_address(call_target_addr),
        occurrence_count=occurrence_count,
    )


def enum_traced_function(
    *,
    function_addr: int,
    resolution_kind: str = "method_definition",
    function_size: int = 64,
    raw_name: str | None = "Describe",
    raw_signature: str | None = "MessageDescriptor Describe(Int32, Boolean)",
    return_type: str | None = "MessageDescriptor",
    parameter_types: list[str] | None = None,
    return_kind: str = "descriptor_like",
    parameter_kinds: list[str] | None = None,
) -> TracedFunction:
    resolved_parameter_types = parameter_types or ["Int32", "Boolean"]
    resolved_parameter_kinds = parameter_kinds or ["int_like", "bool"]
    return TracedFunction(
        start_address=function_addr,
        end_address=function_addr + function_size,
        size=function_size,
        access_infos=[],
        opcode_histogram=Counter(),
        aliases=[],
        stable_callees=[],
        cfg_stats=None,
        resolved_metadata=EnumFunctionResolvedMetadata(
            resolution_kind=resolution_kind,
            raw_name=raw_name,
            raw_signature=raw_signature,
            return_type=return_type,
            parameter_types=resolved_parameter_types,
            return_kind=return_kind,
            parameter_kinds=resolved_parameter_kinds,
        ),
    )


def enum_trace_document(*functions: TracedFunction) -> AccessTraceDocument:
    return AccessTraceDocument(
        functions_by_address={
            format_trace_address(function.start_address): function for function in functions
        },
        enum_signatures_by_name={},
    )


def enum_channel_entry() -> EnumSignatureEntry:
    return EnumSignatureEntry(
        member_value_to_name={"0": "Global", "1": "Team", "5": "Sales"},
        switch_patterns=[
            EnumSwitchPattern(
                function_addr=0x1810D2470,
                field_offset=24,
                member_groups=[
                    EnumMemberGroup(
                        member_values=[0, 3, 5],
                        is_default=False,
                        called_functions=[enum_function_ref(call_target_addr=0xAABBCC, occurrence_count=2)],
                    ),
                    EnumMemberGroup(
                        member_values=[4],
                        is_default=False,
                        called_functions=[enum_function_ref(call_target_addr=0xDDEEFF)],
                    ),
                    EnumMemberGroup(
                        member_values=[],
                        is_default=True,
                        called_functions=[enum_function_ref(call_target_addr=0x112233)],
                    ),
                ],
            )
        ],
    )


def enum_entry(
    *member_groups: list[int],
    member_names: dict[str, str] | None = None,
) -> EnumSignatureEntry:
    resolved_member_names = member_names or {
        str(member_value): f"Value{member_value}"
        for member_group in member_groups
        for member_value in member_group
    }
    return EnumSignatureEntry(
        member_value_to_name=resolved_member_names,
        switch_patterns=[
            EnumSwitchPattern(
                function_addr=0x1000,
                field_offset=24,
                member_groups=[
                    EnumMemberGroup(
                        member_values=member_group,
                        called_functions=[
                            enum_function_ref(
                                call_target_addr=0x2000 + (100 * len(member_group)) + sum(member_group)
                            )
                        ],
                    )
                    for member_group in member_groups
                ],
            )
        ],
    )


def enum_entry_with_member(
    *,
    member_value: int,
    member_groups: list[EnumMemberGroup],
    field_offset: int = 24,
) -> EnumSignatureEntry:
    return EnumSignatureEntry(
        member_value_to_name={str(member_value): "Value"},
        switch_patterns=[
            EnumSwitchPattern(
                function_addr=0x1000,
                field_offset=field_offset,
                member_groups=member_groups,
            )
        ],
    )
