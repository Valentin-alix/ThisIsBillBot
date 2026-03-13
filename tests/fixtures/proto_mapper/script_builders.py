from collections import Counter
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from tests.fixtures.proto_mapper.enum_builders import enum_function_ref
from tests.fixtures.proto_mapper.field_builders import dump_field
from tests.fixtures.proto_mapper.message_builders import (
    field_signature,
    message_signature,
)
from tests.fixtures.proto_mapper.signatures import (
    DEFAULT_CFG_STATS,
    builder_field_access_entry,
)

from DBDofusUnity.proto_mapper_assembly.interfaces.matching_inputs import MatchingInputs
from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import (
    AccessEntry,
    AccessTraceDocument,
    FieldAccessSignatures,
    FunctionAccessInfo,
    FunctionAccessSignature,
    MessageAccessSignature,
    ProtoAccessesInfo,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField
from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import (
    EnumMemberGroup,
    EnumSignatureEntry,
    EnumSwitchPattern,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.interfaces.game_mappings import GameMappingEntry, GameMappingsDocument
from DBDofusUnity.proto_mapper_assembly.interfaces.new_dump_cs import NewDumpCSFile
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.signature_overrides import SignatureOverridesFile
from DBDofusUnity.proto_mapper_assembly.parsers._clr_type_utils import normalize_clr_type
from DBDofusUnity.proto_mapper_assembly.scripts.export_signature_overrides import build_signature_overrides

PINNED_PAIRS_PATH = Path("test_pinned_pairs.json")


def script_message(cls: str, fields: list[DumpCSMessageField] | None = None) -> DumpCSMessage:
    namespace, _, name = cls.rpartition(".")
    return DumpCSMessage(
        file_descriptor="FD",
        name=name,
        namespace=namespace or None,
        fields=[] if fields is None else fields,
    )


def zero_access_field(
    name: str,
    offset: int,
    clr_type: str = "int",
    category: FieldCategoryEnum = FieldCategoryEnum.NUMBER,
    enum_value_type: str | None = None,
) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type=clr_type,
        normalized_type=clr_type,
        category=category,
        memory_offset=offset,
        field_name=name,
        is_proto_field=True,
        enum_value_type=enum_value_type,
    )


def proto_accesses(entries: list[tuple[str, int]]) -> ProtoAccessesInfo:
    access_infos: list[AccessEntry] = [
        builder_field_access_entry(
            access_kind="read",
            cls=cls,
            field=f"field_{offset}",
            property_name=None,
            instruction_address=0,
            field_offset=offset,
        )
        for cls, offset in entries
    ]
    return proto_accesses_with_function_infos({"TestFunc::Void test()": access_infos})


def proto_accesses_with_function_infos(
    function_infos: dict[str, list[AccessEntry]],
) -> ProtoAccessesInfo:
    return ProtoAccessesInfo(
        root={
            function_key: FunctionAccessInfo(
                name=function_key,
                parameters=[],
                return_type="Void",
                access_infos=access_infos,
                start_address=0,
                end_address=10,
                size=10,
                group="Core.dll/TestFunc",
                opcode_histogram=Counter(),
                stable_callees=[],
                cfg_stats=DEFAULT_CFG_STATS,
            )
            for function_key, access_infos in function_infos.items()
        }
    )


def empty_proto_accesses() -> ProtoAccessesInfo:
    return ProtoAccessesInfo(root={})


def zero_access_enum_signatures(patterns: dict[str, list[int]]) -> dict[str, EnumSignatureEntry]:
    root: dict[str, EnumSignatureEntry] = {}
    for enum_name, offsets in patterns.items():
        root[enum_name] = EnumSignatureEntry(
            member_value_to_name={"0": "NONE", "1": "A"},
            switch_patterns=[
                EnumSwitchPattern(
                    function_addr=1000,
                    field_offset=offset,
                    member_groups=[
                        EnumMemberGroup(member_values=[0, 1], is_default=False, called_functions=[])
                    ],
                )
                for offset in offsets
            ],
        )
    return root


def empty_enum_signatures() -> dict[str, EnumSignatureEntry]:
    return {}


def pinned_config(
    obf: str = "xyz",
    non_obf: str = "Com.Ankama.Msg",
    field_mapping_by_obf: dict[str, str] | None = None,
) -> PinnedPairsConfig:
    return PinnedPairsConfig(
        pairs=[PinnedPair(obf=obf, non_obf=non_obf, field_mapping_by_obf=field_mapping_by_obf or {})]
    )


def export_signature(cls: str, field_offsets: list[int]) -> MessageAccessSignature:
    return message_signature(
        cls,
        declared_field_signatures=[],
        field_signatures=[field_signature(offset, None) for offset in field_offsets],
        dump_cs_msg=script_message(cls),
    )


def field_with_shape(
    *,
    field_name: str,
    property_name: str,
    offset: int,
    clr_type: str,
    category: FieldCategoryEnum,
) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type=clr_type,
        normalized_type=normalize_clr_type(clr_type),
        category=category,
        memory_offset=offset,
        field_name=field_name,
        property_name=property_name,
    )


def export_enum_signature_entry(
    *,
    member_value_to_name: dict[str, str],
    member_groups: list[list[int]] | None = None,
) -> EnumSignatureEntry:
    return EnumSignatureEntry(
        member_value_to_name=member_value_to_name,
        switch_patterns=[
            EnumSwitchPattern(
                function_addr=0x1000,
                field_offset=24,
                member_groups=[
                    EnumMemberGroup(
                        member_values=member_values,
                        is_default=False,
                        called_functions=[enum_function_ref(call_target_addr=0x2000 + group_index)],
                    )
                    for group_index, member_values in enumerate(member_groups or [], start=1)
                ],
            )
        ],
    )


def game_mapping_entry(
    *,
    field_mapping: dict[str, str],
    obf_cls: str = "xyz",
    non_obf_namespace: str = ".com.ankama.Msg",
) -> GameMappingEntry:
    return GameMappingEntry(
        full_obf_msg_namespace=obf_cls,
        obf_msg_namespace=obf_cls,
        full_non_obf_msg_namespace=non_obf_namespace,
        field_mapping=field_mapping,
        field_mapping_infos={},
        field_mapping_rejected_infos={},
        field_mapping_unmapped_non_obf_fields={},
        similarity_score=1.0,
        group_similarity_score=1.0,
        assembly_similarity_score=1.0,
        structure_similarity_score=1.0,
        runtime_confidence=None,
        match_margin=0.0,
        runner_up_obf=None,
        is_low_confidence=False,
        evidence_coverage=None,
    )


def game_mappings_doc(field_mapping: dict[str, str]) -> GameMappingsDocument:
    return GameMappingsDocument(root={".com.ankama.Msg": game_mapping_entry(field_mapping=field_mapping)})


def obf_signature_with_fields(
    field_offsets: dict[str, int],
    *,
    field_signatures: list[FieldAccessSignatures] | None = None,
    function_signatures: list[FunctionAccessSignature] | None = None,
) -> MessageAccessSignature:
    fields = [
        dump_field(name, name, offset, FieldCategoryEnum.NUMBER) for name, offset in field_offsets.items()
    ]
    message = script_message("xyz").model_copy(update={"fields": fields})
    base = message_signature(
        "xyz",
        declared_field_signatures=[],
        dump_cs_msg=message,
        field_signatures=field_signatures,
    )
    return base.model_copy(
        update={
            "function_signatures": function_signatures or [],
        }
    )


def non_obf_message_with_fields(field_offsets: dict[str, int]) -> DumpCSMessage:
    return DumpCSMessage(
        file_descriptor="FD",
        name="Msg",
        namespace="Com.Ankama",
        fields=[
            dump_field(name, name, offset, FieldCategoryEnum.NUMBER) for name, offset in field_offsets.items()
        ],
    )


def run_build_signature_overrides(
    *,
    pinned: PinnedPairsConfig,
    obf_signatures: dict[str, MessageAccessSignature],
    obf_messages: list[DumpCSMessage] | None = None,
    non_obf_messages: list[DumpCSMessage] | None = None,
    bootstrap_messages: dict[str, DumpCSMessage] | None = None,
    game_mappings: GameMappingsDocument | None = None,
    obf_enum_signatures: dict[str, EnumSignatureEntry] | None = None,
    non_obf_enum_signatures: dict[str, EnumSignatureEntry] | None = None,
) -> SignatureOverridesFile:
    with ExitStack() as stack:
        stack.enter_context(
            patch(
                "DBDofusUnity.proto_mapper_assembly.scripts.export_signature_overrides.load_pinned_pairs",
                return_value=pinned,
            )
        )
        stack.enter_context(
            patch(
                "DBDofusUnity.proto_mapper_assembly.scripts.export_signature_overrides.parse_messages",
                side_effect=[
                    obf_messages or [signature.dump_cs_msg for signature in obf_signatures.values()],
                    non_obf_messages if non_obf_messages is not None else [],
                ],
            )
        )
        stack.enter_context(
            patch(
                "DBDofusUnity.proto_mapper_assembly.scripts.export_signature_overrides.load_message_access_signatures_from_messages",
                return_value=obf_signatures,
            )
        )
        stack.enter_context(
            patch(
                "DBDofusUnity.proto_mapper_assembly.scripts.export_signature_overrides.load_game_mappings_document",
                return_value=game_mappings or GameMappingsDocument(root={}),
            )
        )
        stack.enter_context(
            patch(
                "DBDofusUnity.proto_mapper_assembly.scripts.export_signature_overrides.load_new_dump_cs_messages",
                return_value=NewDumpCSFile(
                    root=bootstrap_messages
                    if bootstrap_messages is not None
                    else {pair.non_obf: script_message(pair.non_obf) for pair in pinned.pairs}
                ),
            )
        )
        stack.enter_context(
            patch(
                "DBDofusUnity.proto_mapper_assembly.scripts.export_signature_overrides.parse_access_trace_document",
                side_effect=[
                    AccessTraceDocument(
                        functions_by_address={},
                        enum_signatures_by_name={} if obf_enum_signatures is None else obf_enum_signatures,
                    ),
                    AccessTraceDocument(
                        functions_by_address={},
                        enum_signatures_by_name={}
                        if non_obf_enum_signatures is None
                        else non_obf_enum_signatures,
                    ),
                ],
            )
        )
        return build_signature_overrides(pinned_pairs_path=PINNED_PAIRS_PATH)


def single_pair_matching_inputs(
    *,
    obf_message: DumpCSMessage,
    non_obf_message: DumpCSMessage | None = None,
    obf_signature: MessageAccessSignature,
    non_obf_signature: MessageAccessSignature | None = None,
    non_obf_messages_by_cls: dict[str, DumpCSMessage] | None = None,
    non_obf_signatures_by_cls: dict[str, MessageAccessSignature] | None = None,
) -> MatchingInputs:
    resolved_non_obf_messages = (
        non_obf_messages_by_cls
        if non_obf_messages_by_cls is not None
        else ({} if non_obf_message is None else {non_obf_message.composed_name: non_obf_message})
    )
    resolved_non_obf_signatures = (
        non_obf_signatures_by_cls
        if non_obf_signatures_by_cls is not None
        else ({} if non_obf_signature is None else {non_obf_signature.message_cls: non_obf_signature})
    )
    return MatchingInputs(
        obf_messages_by_cls={obf_signature.message_cls: obf_message},
        non_obf_messages_by_cls=resolved_non_obf_messages,
        obf_signatures_by_cls={obf_signature.message_cls: obf_signature},
        non_obf_signatures_by_cls=resolved_non_obf_signatures,
        signature_overrides_by_non_obf_cls={},
        obf_enum_signatures_by_name={},
        non_obf_enum_signatures_by_name={},
        obf_access_trace=AccessTraceDocument(functions_by_address={}),
        non_obf_access_trace=AccessTraceDocument(functions_by_address={}),
    )
