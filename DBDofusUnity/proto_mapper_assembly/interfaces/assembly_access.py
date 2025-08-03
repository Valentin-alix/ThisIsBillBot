from collections import Counter, defaultdict
from functools import cache, cached_property
from typing import Literal, NamedTuple, TypeGuard, override

from pydantic import BaseModel, RootModel, model_validator

from proto_mapper_assembly.interfaces.counter_profile import CounterProfile
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField, FieldKey
from proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from proto_mapper_assembly.interfaces.field_category import (
    CompactFieldTypeShape,
    FieldCategoryEnum,
    FieldTypeShape,
)
from proto_mapper_assembly.interfaces.function_access_signature import (
    AccessAtomKey,
    AccessAtomSequenceKey,
    AccessAtomSignature,
    CfgStats,
    FunctionAccessSignature,
    FunctionSimilarityKey,
    ReturnRole,
)
from proto_mapper_assembly.parsers.csharp_signature_utils import get_normalized_short_type_name


class FieldAccessSignatureKey(NamedTuple):
    field_offset: int
    field_type_shape: FieldTypeShape
    accesses: AccessAtomSequenceKey


type AccessKind = Literal["read", "write", "getter", "setter", "address"]


class FieldAccessEntry(BaseModel):
    type: Literal["field"]
    access_kind: AccessKind
    cls: str
    field_name: str | None = None
    property_name: str | None
    field_offset: int | None
    index_in_function: int
    instruction_address: int

    @model_validator(mode="after")
    def validate_access_identity(self) -> "FieldAccessEntry":
        if self.access_kind in {"getter", "setter"}:
            if self.property_name is None:
                error = f"{self.access_kind} field access requires property_name"
                raise ValueError(error)
            if self.field_offset is not None:
                error = f"{self.access_kind} field access must not carry field_offset"
                raise ValueError(error)
            return self

        if self.field_offset is None:
            error = f"{self.access_kind} field access requires field_offset"
            raise ValueError(error)
        return self


class TypeInfoAccessEntry(BaseModel):
    type: Literal["typeinfo"]
    access_kind: Literal["load"]
    cls: str
    index_in_function: int
    instruction_address: int
    target_address: int


class HandlerRegistrationAccessEntry(BaseModel):
    type: Literal["handler_registration"]
    access_kind: Literal["register"]
    cls: str
    handler_method: str
    method_info_address: int
    filter_typeinfo_address: int
    index_in_function: int
    instruction_address: int
    handler_function_address: int | None
    """Native address of the handler body, i.e. the code that actually processes the message.

    Null when IL2CPP declares no address for the MethodInfo. Such a registration still proves the
    class is registered here, which is what the handler cohorts are built on, so it is kept.
    """
    registration_ordinal: int
    """Rank of this registration inside its registering function, in instruction order."""


type SignatureAccessEntry = FieldAccessEntry | TypeInfoAccessEntry
type AccessEntry = SignatureAccessEntry | HandlerRegistrationAccessEntry


def is_field_access_entry(entry: AccessEntry) -> TypeGuard[FieldAccessEntry]:
    return isinstance(entry, FieldAccessEntry)


def is_signature_access_entry(entry: AccessEntry) -> TypeGuard[SignatureAccessEntry]:
    return isinstance(entry, FieldAccessEntry | TypeInfoAccessEntry)


class FunctionAccessInfo(BaseModel):
    name: str
    parameters: list[str]
    return_type: str
    access_infos: list[AccessEntry]
    start_address: int
    end_address: int
    size: int
    group: str
    """Il2Cpp owner group, kept to audit where Core.dll wrapper aliases came from."""
    opcode_histogram: Counter[str]
    stable_callees: list[str]
    """Resolved identities of the directly called methods, obfuscated ones included.

    Which of them survive obfuscation is only knowable by intersecting both builds, so the filtering
    is left to the matching side rather than guessed here.
    """
    cfg_stats: CfgStats

    @override
    def __hash__(self) -> int:
        return self.name.__hash__()

    @cached_property
    def accesses_by_cls(self) -> dict[str, list[AccessEntry]]:
        accesses_by_cls: dict[str, list[AccessEntry]] = defaultdict(list)

        for access in self.access_infos:
            if not is_signature_access_entry(access):
                continue
            accesses_by_cls[access.cls].append(access)

        return accesses_by_cls

    @cached_property
    def normalized_parameters(self) -> set[str]:
        return {get_normalized_short_type_name(parameter) for parameter in self.parameters}

    @cached_property
    def normalized_return_type(self) -> str:
        return get_normalized_short_type_name(self.return_type)

    @cache
    def get_normalized_return_role(self, normalized_message_type: str) -> ReturnRole:
        if self.normalized_return_type == "Void":
            return ReturnRole.VOID
        if self.normalized_return_type == normalized_message_type:
            return ReturnRole.SELF
        return ReturnRole.OTHER


class ProtoAccessesInfo(RootModel[dict[str, FunctionAccessInfo]]):
    root: dict[str, FunctionAccessInfo]


class FunctionAlias(BaseModel):
    name: str
    parameters: list[str]
    return_type: str
    group: str


class EnumFunctionResolvedMetadata(BaseModel):
    resolution_kind: str
    raw_name: str | None = None
    raw_signature: str | None = None
    return_type: str | None = None
    parameter_types: list[str]
    return_kind: str
    parameter_kinds: list[str]


class TracedFunction(BaseModel):
    start_address: int
    end_address: int
    size: int
    access_infos: list[AccessEntry]
    opcode_histogram: Counter[str]
    aliases: list[FunctionAlias]
    resolved_metadata: EnumFunctionResolvedMetadata | None = None
    stable_callees: list[str]
    """Resolved identities of the directly called methods, see ``FunctionAccessInfo.stable_callees``."""
    cfg_stats: CfgStats | None
    """Null on the enum placeholders, which stand in for a function nobody scanned."""

    def to_function_access_infos(self) -> list[FunctionAccessInfo]:
        cfg_stats = self.cfg_stats
        if cfg_stats is None:
            return []
        return [
            FunctionAccessInfo(
                name=alias.name,
                parameters=alias.parameters,
                return_type=alias.return_type,
                access_infos=self.access_infos,
                start_address=self.start_address,
                end_address=self.end_address,
                size=self.size,
                group=alias.group,
                opcode_histogram=self.opcode_histogram,
                stable_callees=self.stable_callees,
                cfg_stats=cfg_stats,
            )
            for alias in self.aliases
        ]


class AccessTraceDocument(BaseModel):
    functions_by_address: dict[str, TracedFunction]
    enum_signatures_by_name: dict[str, EnumSignatureEntry] = {}

    def __hash__(self) -> int:
        return id(self).__hash__()

    def to_proto_accesses(self) -> ProtoAccessesInfo:
        function_infos: dict[str, FunctionAccessInfo] = {}
        for traced_function in self.functions_by_address.values():
            for function_info in traced_function.to_function_access_infos():
                function_infos[function_info.name] = function_info
        return ProtoAccessesInfo(root=function_infos)


def format_trace_address(address: int) -> str:
    return f"0x{address:x}"


class FieldAccessSignatures(BaseModel):
    field_key: FieldKey
    field_type_shape: CompactFieldTypeShape
    accesses: list[AccessAtomSignature]
    # False when the tracer never reached this field, so ``accesses`` is empty for lack of evidence
    # rather than because the field is genuinely accessed without atoms (a getter-only field).
    # Deliberately excluded from ``field_similarity_key``: it describes how much we know about the
    # field, not what the field looks like.
    is_traced: bool = True

    @property
    def field_offset(self) -> int:
        return self.field_key.memory_offset

    @cached_property
    def accesses_key(self) -> AccessAtomSequenceKey:
        ordered = sorted(self.accesses, key=lambda access: access.index_in_function)
        return tuple(
            dict.fromkeys(
                AccessAtomKey(
                    entry_type=access.entry_type,
                    access_kind=access.access_kind,
                    field_type_shape=access.field_type_shape,
                    index_in_function=access.index_in_function,
                    field_offset=access.field_offset,
                )
                for access in ordered
            )
        )

    @cached_property
    def field_similarity_key(self) -> FieldAccessSignatureKey:
        return FieldAccessSignatureKey(
            field_offset=self.field_offset,
            field_type_shape=self.field_type_shape,
            accesses=self.accesses_key,
        )

    @override
    def __eq__(self, value: "FieldAccessSignatures|object") -> bool:
        if not isinstance(value, FieldAccessSignatures):
            err = f"{value} is not of type {FieldAccessSignatures.__name__}"
            raise TypeError(err)
        return self.field_similarity_key == value.field_similarity_key

    @override
    def __hash__(self) -> int:
        return self.field_similarity_key.__hash__()


class MessageAccessSignature(BaseModel):
    message_cls: str
    file_descriptor: str
    dump_cs_msg: DumpCSMessage
    function_signatures: list[FunctionAccessSignature]
    field_signatures: list[FieldAccessSignatures]

    @override
    def __hash__(self) -> int:
        return self.dump_cs_msg.__hash__()

    @cached_property
    def field_signature_keys(self) -> tuple[FieldAccessSignatureKey, ...]:
        return tuple(signature.field_similarity_key for signature in self.field_signatures)

    @cached_property
    def function_similarity_keys(self) -> tuple[FunctionSimilarityKey, ...]:
        # Dédup les wrappers C# qui partagent la même fonction native (alias IL2Cpp).
        # Le tracer remonte une entrée par alias C# ; le nombre d'aliases visibles n'est pas
        # une feature stable entre builds. On garde un représentant par similarity_key distinct.
        # Pas un set : cet ordre nourrit un appariement hongrois, et l'ordre d'un set de cles
        # str change d'un process a l'autre.
        return tuple(dict.fromkeys(sig.similarity_key for sig in self.function_signatures))

    @cached_property
    def declared_proto_fields(self) -> tuple[DumpCSMessageField, ...]:
        return tuple(
            sorted(
                (field for field in self.dump_cs_msg.fields if field.is_declared_proto_shape_field),
                key=lambda field: field.memory_offset,
            )
        )

    @cached_property
    def field_signature_by_field_key(self) -> dict[FieldKey, FieldAccessSignatures]:
        field_signatures_by_key: dict[FieldKey, FieldAccessSignatures] = {}
        for field_signature in self.field_signatures:
            if field_signature.field_key in field_signatures_by_key:
                message = (
                    f"Duplicate field signature for {field_signature.field_key} for msg {self.message_cls}"
                )
                raise ValueError(message)
            field_signatures_by_key[field_signature.field_key] = field_signature
        return field_signatures_by_key

    @cached_property
    def live_field_keys(self) -> frozenset[FieldKey]:
        return frozenset(field_signature.field_key for field_signature in self.field_signatures)

    @cached_property
    def active_oneof_group_names(self) -> frozenset[str]:
        return frozenset(
            field.oneof_group_name
            for field in self.declared_proto_fields
            if field.oneof_group_name is not None
            and field.is_synthetic_oneof_variant
            and field.field_key in self.live_field_keys
        )

    @cached_property
    def static_exportable_fields(self) -> tuple[DumpCSMessageField, ...]:
        return tuple(field for field in self.declared_proto_fields if field.property_name is not None)

    @cache
    def get_exportable_fields(
        self, *, forced_field_names: frozenset[str] = frozenset()
    ) -> tuple[DumpCSMessageField, ...]:
        return tuple(field for field in self.declared_proto_fields if field.property_name is not None)

    @cached_property
    def declared_similarity_fields(self) -> tuple[DumpCSMessageField, ...]:
        return tuple(field for field in self.declared_proto_fields if field.field_key in self.live_field_keys)

    @cached_property
    def declared_field_count(self) -> int:
        return len(self.declared_similarity_fields)

    @cached_property
    def declared_shape_counter(self) -> Counter[str]:
        """Multiset of declared proto field shapes, independent of runtime traces and obfuscation."""
        return Counter(field.declared_shape_token for field in self.declared_proto_fields)

    @cached_property
    def declared_shape_profile(self) -> CounterProfile:
        return CounterProfile(self.declared_shape_counter)

    @cached_property
    def evidence_coverage(self) -> float | None:
        """Fraction of declared proto fields backed by a runtime access trace; None when none declared."""
        declared_count = len(self.declared_proto_fields)
        if declared_count == 0:
            return None
        return len(self.declared_similarity_fields) / declared_count

    @cached_property
    def top_level_declared_field_shapes(self) -> frozenset[FieldCategoryEnum]:
        return frozenset(field.field_type_shape.category for field in self.declared_similarity_fields)

    @cached_property
    def total_complexity(self) -> int:
        return (
            len(self.declared_similarity_fields) + len(self.field_signatures) + len(self.function_signatures)
        )
