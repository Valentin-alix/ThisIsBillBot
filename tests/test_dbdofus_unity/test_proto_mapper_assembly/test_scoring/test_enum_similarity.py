from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.enum_builders import (
    enum_entry_with_member,
    enum_function_ref,
    enum_trace_document,
    enum_traced_function,
)

from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import (
    EnumMemberGroup,
    EnumSignatureEntry,
    EnumSwitchPattern,
)
from DBDofusUnity.proto_mapper_assembly.scoring.enum_similarity import (
    EnumSimilarityContext,
    enum_member_similarity,
    enum_signature_similarity,
)


class TestEnumMemberSimilarity:
    def test_expands_multi_value_groups_per_member_value(self) -> None:
        left_entry = enum_entry_with_member(
            member_value=3,
            member_groups=[
                EnumMemberGroup(
                    member_values=[0, 3, 5],
                    called_functions=[enum_function_ref(call_target_addr=0x1000, occurrence_count=2)],
                )
            ],
        )
        right_entry = enum_entry_with_member(
            member_value=8,
            member_groups=[
                EnumMemberGroup(
                    member_values=[8, 9],
                    called_functions=[enum_function_ref(call_target_addr=0x2000, occurrence_count=2)],
                )
            ],
        )
        context = EnumSimilarityContext(
            enum_trace_document(enum_traced_function(function_addr=0x1000)),
            enum_trace_document(enum_traced_function(function_addr=0x2000)),
        )

        assert enum_member_similarity(left_entry, 3, right_entry, 8, context=context) == 1.0

    def test_returns_zero_when_member_value_is_missing(self) -> None:
        left_entry = enum_entry_with_member(
            member_value=1,
            member_groups=[
                EnumMemberGroup(
                    member_values=[1],
                    called_functions=[enum_function_ref(call_target_addr=0x1000)],
                )
            ],
        )
        right_entry = enum_entry_with_member(
            member_value=2,
            member_groups=[
                EnumMemberGroup(
                    member_values=[2],
                    called_functions=[enum_function_ref(call_target_addr=0x2000)],
                )
            ],
        )
        context = EnumSimilarityContext(
            enum_trace_document(enum_traced_function(function_addr=0x1000)),
            enum_trace_document(enum_traced_function(function_addr=0x2000)),
        )

        assert enum_member_similarity(left_entry, 1, right_entry, 3, context=context) == 0.0

    def test_penalizes_occurrence_count_mismatch(self) -> None:
        left_entry = enum_entry_with_member(
            member_value=1,
            member_groups=[
                EnumMemberGroup(
                    member_values=[1],
                    called_functions=[enum_function_ref(call_target_addr=0x1000, occurrence_count=3)],
                )
            ],
        )
        right_entry = enum_entry_with_member(
            member_value=7,
            member_groups=[
                EnumMemberGroup(
                    member_values=[7],
                    called_functions=[enum_function_ref(call_target_addr=0x2000, occurrence_count=1)],
                )
            ],
        )
        context = EnumSimilarityContext(
            enum_trace_document(enum_traced_function(function_addr=0x1000)),
            enum_trace_document(enum_traced_function(function_addr=0x2000)),
        )

        score = enum_member_similarity(left_entry, 1, right_entry, 7, context=context)

        assert score < 1.0
        assert score > 0.0


class TestEnumSignatureSimilarity:
    def test_scores_high_for_structurally_equivalent_enums(self) -> None:
        left_entry = EnumSignatureEntry(
            member_value_to_name={"0": "Global", "1": "Team"},
            switch_patterns=[
                EnumSwitchPattern(
                    function_addr=0x1000,
                    field_offset=24,
                    member_groups=[
                        EnumMemberGroup(
                            member_values=[0],
                            called_functions=[enum_function_ref(call_target_addr=0x1100)],
                        ),
                        EnumMemberGroup(
                            member_values=[1],
                            called_functions=[enum_function_ref(call_target_addr=0x1200)],
                        ),
                    ],
                )
            ],
        )
        right_entry = EnumSignatureEntry(
            member_value_to_name={"8": "Global", "9": "Team"},
            switch_patterns=[
                EnumSwitchPattern(
                    function_addr=0x2000,
                    field_offset=24,
                    member_groups=[
                        EnumMemberGroup(
                            member_values=[8],
                            called_functions=[enum_function_ref(call_target_addr=0x2100)],
                        ),
                        EnumMemberGroup(
                            member_values=[9],
                            called_functions=[enum_function_ref(call_target_addr=0x2200)],
                        ),
                    ],
                )
            ],
        )
        context = EnumSimilarityContext(
            enum_trace_document(
                enum_traced_function(function_addr=0x1100),
                enum_traced_function(function_addr=0x1200),
            ),
            enum_trace_document(
                enum_traced_function(function_addr=0x2100),
                enum_traced_function(function_addr=0x2200),
            ),
        )

        assert enum_signature_similarity(left_entry, right_entry, context=context) == 1.0

    def test_penalizes_unmatched_members(self) -> None:
        shared_group = EnumMemberGroup(
            member_values=[0],
            called_functions=[enum_function_ref(call_target_addr=0x1100)],
        )
        left_entry = EnumSignatureEntry(
            member_value_to_name={"0": "Global", "1": "Team"},
            switch_patterns=[
                EnumSwitchPattern(
                    function_addr=0x1000,
                    field_offset=24,
                    member_groups=[
                        shared_group,
                        EnumMemberGroup(
                            member_values=[1],
                            called_functions=[enum_function_ref(call_target_addr=0x1200)],
                        ),
                    ],
                )
            ],
        )
        right_entry = EnumSignatureEntry(
            member_value_to_name={"8": "Global"},
            switch_patterns=[
                EnumSwitchPattern(
                    function_addr=0x2000,
                    field_offset=24,
                    member_groups=[
                        EnumMemberGroup(
                            member_values=[8],
                            called_functions=[enum_function_ref(call_target_addr=0x2100)],
                        )
                    ],
                )
            ],
        )
        context = EnumSimilarityContext(
            enum_trace_document(
                enum_traced_function(function_addr=0x1100),
                enum_traced_function(function_addr=0x1200),
            ),
            enum_trace_document(enum_traced_function(function_addr=0x2100)),
        )

        assert enum_signature_similarity(left_entry, right_entry, context=context) == 0.5
