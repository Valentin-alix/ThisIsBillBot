from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, RootModel

from proto_mapper_assembly.interfaces.function_access_signature import FunctionAccessSignature

type EnumResolutionKind = Literal[
    "method_definition",
    "api",
    "export",
    "ida_type",
    "decompiled",
    "unknown",
]
type EnumTypeKind = Literal[
    "void",
    "bool",
    "int_like",
    "float_like",
    "string_like",
    "descriptor_like",
    "function_pointer",
    "message_like",
    "pointer_like",
    "unknown",
]


class EnumCalledFunctionRef(BaseModel):
    function_address: str
    call_target_address: str
    occurrence_count: int = 1
    function_signature: FunctionAccessSignature | None = None


class EnumMemberGroup(BaseModel):
    member_values: list[int]
    is_default: bool = False
    called_functions: list[EnumCalledFunctionRef]


class EnumSwitchPattern(BaseModel):
    function_addr: int
    field_offset: int
    member_groups: list[EnumMemberGroup]


class EnumSignatureEntry(BaseModel):
    member_value_to_name: dict[str, str]
    switch_patterns: list[EnumSwitchPattern]


class EnumSignatureIndex(RootModel[dict[str, EnumSignatureEntry]]):
    root: dict[str, EnumSignatureEntry]
