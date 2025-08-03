from collections import Counter

import pytest

from proto_mapper_assembly.controllers.enum_signatures import (
    build_canonical_enum_signature,
    validate_enum_signature_member_values,
)
from proto_mapper_assembly.interfaces.enum_mapping import (
    EnumCalledFunctionRef,
    EnumMemberGroup,
    EnumSignatureEntry,
    EnumSignatureIndex,
    EnumSwitchPattern,
)
from proto_mapper_assembly.interfaces.function_access_signature import (
    FunctionAccessSignature,
    ReturnRole,
)


def _enum_function_ref(*, occurrence_count: int = 1) -> EnumCalledFunctionRef:
    return EnumCalledFunctionRef(
        call_target_address="0xaabbcc",
        function_address="0xaabbcc",
        occurrence_count=occurrence_count,
    )


def _round_trip_entry() -> EnumSignatureEntry:
    return EnumSignatureEntry(
        member_value_to_name={"0": "Global", "1": "Team", "5": "Sales"},
        switch_patterns=[
            EnumSwitchPattern(
                function_addr=0x1810D2470,
                field_offset=24,
                member_groups=[
                    EnumMemberGroup(
                        member_values=[0, 3, 5],
                        called_functions=[_enum_function_ref(occurrence_count=2)],
                    )
                ],
            )
        ],
    )


def _enum_signature(*groups: EnumMemberGroup, members: dict[str, str]) -> EnumSignatureEntry:
    return EnumSignatureEntry(
        member_value_to_name=members,
        switch_patterns=[
            EnumSwitchPattern(
                function_addr=0x2000,
                field_offset=24,
                member_groups=list(groups),
            )
        ],
    )


class TestEnumSignatureIndex:
    def test_serialization_round_trip_preserves_enum_signature(self) -> None:
        index = EnumSignatureIndex(root={"Channel": _round_trip_entry()})

        restored = EnumSignatureIndex.model_validate_json(index.model_dump_json())

        pattern = restored.root["Channel"].switch_patterns[0]
        assert restored.root["Channel"].member_value_to_name == {"0": "Global", "1": "Team", "5": "Sales"}
        assert pattern.function_addr == 0x1810D2470
        assert pattern.member_groups[0].called_functions[0].function_address == "0xaabbcc"
        assert pattern.member_groups[0].called_functions[0].occurrence_count == 2

    def test_build_canonical_enum_signature_remaps_member_values_to_non_obf_space(self) -> None:
        entry = _enum_signature(
            EnumMemberGroup(member_values=[0, 2], called_functions=[]),
            EnumMemberGroup(member_values=[1], called_functions=[]),
            EnumMemberGroup(member_values=[], is_default=True, called_functions=[]),
            members={"0": "a", "1": "b", "2": "c"},
        )

        result = build_canonical_enum_signature(
            obf_enum_signature=entry,
            value_mapping={"0": "10", "1": "20"},
            non_obf_value_to_name={"10": "Ten", "20": "Twenty"},
            obf_function_signature_by_address={},
        )

        assert result.member_value_to_name == {"10": "Ten", "20": "Twenty"}
        assert [group.member_values for group in result.switch_patterns[0].member_groups] == [
            [10],
            [20],
            [],
        ]
        assert result.switch_patterns[0].member_groups[2].is_default is True

    def test_build_canonical_enum_signature_remaps_default_group_members(self) -> None:
        entry = _enum_signature(
            EnumMemberGroup(member_values=[0, 1], is_default=True, called_functions=[]),
            members={"0": "a", "1": "b"},
        )

        result = build_canonical_enum_signature(
            obf_enum_signature=entry,
            value_mapping={"0": "10", "1": "20"},
            non_obf_value_to_name={"10": "Ten", "20": "Twenty"},
            obf_function_signature_by_address={},
        )

        assert result.switch_patterns[0].member_groups[0].is_default is True
        assert result.switch_patterns[0].member_groups[0].member_values == [10, 20]

    def test_build_canonical_enum_signature_drops_explicit_groups_with_only_unmapped_members(
        self,
    ) -> None:
        entry = _enum_signature(
            EnumMemberGroup(member_values=[0], called_functions=[]),
            EnumMemberGroup(member_values=[1], called_functions=[]),
            members={"0": "a", "1": "b"},
        )

        result = build_canonical_enum_signature(
            obf_enum_signature=entry,
            value_mapping={"1": "20"},
            non_obf_value_to_name={"20": "Twenty"},
            obf_function_signature_by_address={},
        )

        assert result.member_value_to_name == {"20": "Twenty"}
        assert [group.member_values for group in result.switch_patterns[0].member_groups] == [[20]]

    def test_build_canonical_enum_signature_embeds_obf_function_signature(self) -> None:
        entry = _enum_signature(
            EnumMemberGroup(
                member_values=[0],
                called_functions=[
                    EnumCalledFunctionRef(
                        function_address="0xdeadbeef",
                        call_target_address="0xdeadbeef",
                    )
                ],
            ),
            members={"0": "a"},
        )
        function_signature = FunctionAccessSignature(
            return_role=ReturnRole.VOID,
            takes_message_parameter=False,
            size=16,
            self_accesses=[],
            foreign_access_summary=["resolution:unknown", "return:unknown"],
            opcode_histogram=Counter({"mov": 3}),
            stable_callees=[],
            cfg_stats=None,
        )

        result = build_canonical_enum_signature(
            obf_enum_signature=entry,
            value_mapping={"0": "10"},
            non_obf_value_to_name={"10": "Ten"},
            obf_function_signature_by_address={"0xdeadbeef": function_signature},
        )

        embedded = result.switch_patterns[0].member_groups[0].called_functions[0].function_signature
        assert embedded == function_signature

    def test_validate_enum_signature_member_values_rejects_unknown_group_value(self) -> None:
        entry = _enum_signature(
            EnumMemberGroup(member_values=[99], called_functions=[]),
            members={"10": "Ten"},
        )

        with pytest.raises(ValueError, match="undeclared member values"):
            validate_enum_signature_member_values(entry)
