import pytest
from pathlib import Path

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig
from DBDofusUnity.proto_mapper_assembly.matching.workspace import build_matching_workspace
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from tests.fixtures.proto_mapper.field_builders import dump_field
from tests.fixtures.proto_mapper.matching_builders import build_prepared_scores_for_test
from tests.fixtures.proto_mapper.message_builders import message_signature
from tests.fixtures.proto_mapper.runtime_store import seed_runtime_content


@pytest.mark.parametrize("pinned", [False, True])
@pytest.mark.parametrize("disjoint", [False, True])
def test_group_affinity_cannot_override_incompatible_structure(
    runtime_data_store: RuntimeDataStore,
    pinned: bool,
    disjoint: bool,
) -> None:
    clear_fields = [
        dump_field("request_id_", "RequestId", 24, FieldCategoryEnum.NUMBER),
        dump_field("contact_type_", "ContactType", 28, FieldCategoryEnum.ENUM),
        dump_field("name_", "Name", 32, FieldCategoryEnum.STRING),
        dump_field("id_", "Id", 40, FieldCategoryEnum.NUMBER),
    ]
    for field in clear_fields[2:]:
        field.oneof_group_name = "complement"
        field.is_synthetic_oneof_variant = True
    obf_fields = [
        dump_field("account_", "Account", 24, FieldCategoryEnum.NUMBER),
        dump_field("name_", "Name", 32, FieldCategoryEnum.STRING),
    ]
    if disjoint:
        obf_fields = [dump_field("enabled_", "Enabled", 24, FieldCategoryEnum.BOOLEAN)]
    obf = DumpCSMessage(file_descriptor="ObfGroup", name="obf", fields=obf_fields)
    clear = DumpCSMessage(file_descriptor="ContactGroup", name="ContactLookRequest", fields=clear_fields)
    anchor_fields = [dump_field("enabled_", "Enabled", 24, FieldCategoryEnum.BOOLEAN)]
    obf_anchor = DumpCSMessage(file_descriptor="ObfGroup", name="anchor", fields=anchor_fields)
    clear_anchor = DumpCSMessage(file_descriptor="ContactGroup", name="AnchorRequest", fields=anchor_fields)
    obf_messages = {"obf": obf, "anchor": obf_anchor}
    clear_messages = {"ContactLookRequest": clear, "AnchorRequest": clear_anchor}
    workspace = build_matching_workspace(
        obf_signatures=[message_signature(k, v.fields, dump_cs_msg=v) for k, v in obf_messages.items()],
        non_obf_signatures=[message_signature(k, v.fields, dump_cs_msg=v) for k, v in clear_messages.items()],
        obf_messages_by_cls=obf_messages,
        non_obf_messages_by_cls=clear_messages,
    )
    scores = build_prepared_scores_for_test(
        workspace=workspace,
        obf_messages_by_cls=obf_messages,
        non_obf_messages_by_cls=clear_messages,
        runtime_data_store=runtime_data_store,
        pinned_pairs_config=PinnedPairsConfig(
            pairs=[PinnedPair(obf="obf", non_obf="ContactLookRequest")] if pinned else [],
        ),
    )
    assert scores.file_descriptor_similarity_by_pair[("ContactGroup", "ObfGroup")] > 0
    assert scores.final_scores_matrix[0, 0] == (1.0 if pinned else 0.0)
    assert scores.rejected_pairs_by_reason[MatchPairKey("obf", "ContactLookRequest")] == "root_oneof_mismatch"


@pytest.mark.parametrize("from_server", [True, False])
def test_group_affinity_cannot_override_captured_direction(
    tmp_path: Path, runtime_data_store: RuntimeDataStore, from_server: bool
) -> None:
    seed_runtime_content(
        tmp_path,
        {"obf": [{"from_server": from_server, "is_root_msg": True, "is_game_msg": False}]},
    )
    obf = DumpCSMessage(file_descriptor="ObfGroup", name="obf")
    clear_messages = {
        name: DumpCSMessage(file_descriptor="ClearGroup", name=name)
        for name in ("ClearEvent", "ClearRequest")
    }
    workspace = build_matching_workspace(
        obf_signatures=[message_signature("obf", [], dump_cs_msg=obf)],
        non_obf_signatures=[message_signature(name, [], dump_cs_msg=msg) for name, msg in clear_messages.items()],
        obf_messages_by_cls={"obf": obf},
        non_obf_messages_by_cls=clear_messages,
    )
    scores = build_prepared_scores_for_test(
        workspace=workspace,
        obf_messages_by_cls={"obf": obf},
        non_obf_messages_by_cls=clear_messages,
        runtime_data_store=runtime_data_store,
        pinned_pairs_config=PinnedPairsConfig(pairs=[]),
    )
    assert scores.file_descriptor_similarity_by_pair[("ClearGroup", "ObfGroup")] > 0
    assert scores.final_scores_matrix[0 if from_server else 1, 0] > 0
    assert scores.final_scores_matrix[1 if from_server else 0, 0] == 0

