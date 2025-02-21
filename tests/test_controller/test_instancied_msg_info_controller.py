from google.protobuf.field_mask_pb2 import FieldMask
from proto_mapper_assembly.runtime.runtime_store import (
    MAX_COUNT_BY_NAME,
    RuntimeDataStore,
    RuntimeInstance,
)


class TestRuntimeDataStore:
    def test_update_msg_infos_content_serializes_repeated_scalar_fields(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        message = FieldMask(paths=["alpha", "beta"])

        serialized = runtime_data_store._update_msg_infos_content(
            message,
            from_server=False,
            is_game_msg=True,
            is_root_msg=True,
        )

        assert serialized.model_dump()["paths"] == ["alpha", "beta"]
        assert runtime_data_store._writing_content == {
            message.DESCRIPTOR.full_name: [serialized],
        }

    def test_update_msg_infos_content_keeps_empty_repeated_scalar_fields(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        message = FieldMask()

        serialized = runtime_data_store._update_msg_infos_content(
            message,
            from_server=False,
            is_game_msg=True,
            is_root_msg=True,
        )

        assert serialized.model_dump()["paths"] == []

    def test_add_msg_respects_max_count_cap(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        name = FieldMask.DESCRIPTOR.full_name
        assert runtime_data_store._writing_content is not None
        runtime_data_store._writing_content[name] = [
            RuntimeInstance(from_server=None, is_game_msg=False, is_root_msg=False)
            for _ in range(MAX_COUNT_BY_NAME)
        ]

        runtime_data_store.add_msg(
            FieldMask(paths=["extra"]),
            from_server=False,
            is_game_msg=True,
        )

        assert len(runtime_data_store._writing_content[name]) == MAX_COUNT_BY_NAME

    def test_writing_content_returns_empty_when_file_missing(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        assert runtime_data_store._writing_content == {}

    def test_write_no_ops_when_content_is_empty(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        runtime_data_store._writing_content = {}
        runtime_data_store.write_captured_content()
        assert not runtime_data_store.path.exists()

    def test_write_persists_content(self, runtime_data_store: RuntimeDataStore) -> None:
        name = FieldMask.DESCRIPTOR.full_name
        runtime_data_store._writing_content = {
            name: [
                RuntimeInstance(from_server=None, is_game_msg=False, is_root_msg=False)
            ]
        }
        runtime_data_store.write_captured_content()
