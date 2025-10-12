from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.matching_builders import (
    grouped_number_signature,
    simple_signature,
)

from DBDofusUnity.proto_mapper_assembly.matching.workspace import build_matching_workspace


class TestMatchingWorkspace:
    def test_indexes_signatures_by_message_class(self) -> None:
        obf_alpha = simple_signature("obf_alpha")
        obf_beta = simple_signature("obf_beta")
        clear_alpha = simple_signature("ClearAlpha")
        clear_beta = simple_signature("ClearBeta")

        workspace = build_matching_workspace(
            obf_signatures=[obf_alpha, obf_beta],
            non_obf_signatures=[clear_alpha, clear_beta],
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
        )

        assert workspace.signature_indexes.obf_index_by_cls == {"obf_alpha": 0, "obf_beta": 1}
        assert workspace.signature_indexes.non_obf_index_by_cls == {
            "ClearAlpha": 0,
            "ClearBeta": 1,
        }
        assert workspace.obf_signatures_by_cls["obf_beta"] is obf_beta
        assert workspace.non_obf_signatures_by_cls["ClearAlpha"] is clear_alpha

    def test_groups_signatures_by_file_descriptor_once(self) -> None:
        workspace = build_matching_workspace(
            obf_signatures=[
                grouped_number_signature("obf_a", "group_y"),
                grouped_number_signature("obf_b", "group_x"),
                grouped_number_signature("obf_c", "group_x"),
            ],
            non_obf_signatures=[
                grouped_number_signature("ClearA", "group_b"),
                grouped_number_signature("ClearB", "group_a"),
            ],
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
        )

        assert workspace.obf_group_descriptors == ("group_x", "group_y")
        assert workspace.non_obf_group_descriptors == ("group_a", "group_b")
        assert [signature.message_cls for signature in workspace.obf_groups["group_x"]] == [
            "obf_b",
            "obf_c",
        ]
        assert [signature.message_cls for signature in workspace.non_obf_groups["group_b"]] == [
            "ClearA",
        ]
