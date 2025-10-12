from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    RootModel,
)

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import (
    FieldAccessSignatures,
    FunctionAccessSignature,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry

type EnumHintSlot = Literal["key", "value"]


class EnumSignatureOverrideHint(BaseModel):
    non_obf_enum_type: str
    signature: EnumSignatureEntry


class FieldOverrideBinding(BaseModel):
    obf_field_name: str
    obf_memory_offset: int


class SignatureOverrideEntry(BaseModel):
    function_signatures: Sequence[FunctionAccessSignature]
    field_signatures: dict[str, FieldAccessSignatures]
    obf_field_binding_by_non_obf_property_name: dict[str, FieldOverrideBinding] = Field(
        default_factory=dict[str, FieldOverrideBinding]
    )
    enum_signature_hints_by_non_obf_prop_name: dict[str, dict[EnumHintSlot, EnumSignatureOverrideHint]] = (
        Field(
            default_factory=dict[str, dict[EnumHintSlot, EnumSignatureOverrideHint]],
        )
    )


class SignatureOverridesFile(RootModel[dict[str, SignatureOverrideEntry]]):
    root: dict[str, SignatureOverrideEntry]
