from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.matching_builders import (
    child_message_mapping_signatures,
    fake_field_mapping_context,
)
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.message_builders import (
    build_field_mapping_for_test,
)

from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.matching.iterative_store import IterativeMatchingStore
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


class TestChildMessageMapping:
    def test_discovers_child_message_correspondence(self, runtime_data_store: RuntimeDataStore) -> None:
        non_obf_signature, obf_signature, non_obf_messages_by_cls, obf_messages_by_cls = (
            child_message_mapping_signatures()
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_signature,
            obf_signature=obf_signature,
            obf_messages_by_cls=obf_messages_by_cls,
            non_obf_messages_by_cls=non_obf_messages_by_cls,
            field_mapping_context=fake_field_mapping_context(runtime_data_store),
        )

        assert result.field_mapping == {"faaa": "stated_element"}
        assert len(result.discovered_message_matches) == 1
        assert result.discovered_message_matches[0].obf_message_cls == "abc"
        assert result.discovered_message_matches[0].non_obf_message_cls == "StatedElement"

    def test_rejects_child_pair_confirmed_to_another_non_obf_message(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        non_obf_signature, obf_signature, non_obf_messages_by_cls, obf_messages_by_cls = (
            child_message_mapping_signatures()
        )
        non_obf_messages_by_cls["OtherElement"] = DumpCSMessage(
            file_descriptor="GameReflection",
            name="OtherElement",
        )
        matching_store = IterativeMatchingStore(
            confirmed_non_obf_by_obf={"abc": "OtherElement"},
            confirmed_obf_by_non_obf={"OtherElement": "abc"},
            inferred_non_obf_by_obf={},
            source_by_obf={"abc": "group_match"},
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_signature,
            obf_signature=obf_signature,
            obf_messages_by_cls=obf_messages_by_cls,
            non_obf_messages_by_cls=non_obf_messages_by_cls,
            matching_store=matching_store,
            field_mapping_context=fake_field_mapping_context(runtime_data_store),
        )

        assert result.field_mapping == {}
        assert result.discovered_message_matches == ()
