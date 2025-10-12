import json
from pathlib import Path

from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.message_builders import root_message
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.runtime_builders import runtime_entry
from google.protobuf.empty_pb2 import Empty

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.interfaces.runtime_data import RuntimeRoot
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


class TestRuntimeDataStore:
    def test_start_connection_capture_sequence_resets_runtime_capture_index(
        self,
        runtime_data_store: RuntimeDataStore,
    ) -> None:
        runtime_data_store.start_connection_capture_sequence()
        runtime_data_store.add_msg(Empty(), from_server=True, is_game_msg=False)
        runtime_data_store.start_connection_capture_sequence()
        runtime_data_store.add_msg(Empty(), from_server=True, is_game_msg=False)
        runtime_data_store.add_msg(Empty(), from_server=True, is_game_msg=False)
        runtime_data_store.write_captured_content()

        runtime_root = RuntimeRoot.model_validate_json(runtime_data_store.path.read_text(encoding="utf-8"))
        assert [instance.capture_sequence for instance in runtime_root.root["google.protobuf.Empty"]] == [
            0,
            0,
            1,
        ]
        session_ids = [instance.capture_session_id for instance in runtime_root.root["google.protobuf.Empty"]]
        assert session_ids[0] != session_ids[1]
        assert session_ids[1] == session_ids[2]

    def test_add_msg_without_active_capture_sequence_stores_no_order_metadata(
        self,
        runtime_data_store: RuntimeDataStore,
    ) -> None:
        """Sniffer traffic has no single owning connection, so no capture sequence/session is started."""
        runtime_data_store.add_msg(Empty(), from_server=True, is_game_msg=False)
        runtime_data_store.write_captured_content()

        runtime_root = RuntimeRoot.model_validate_json(runtime_data_store.path.read_text(encoding="utf-8"))
        instance = runtime_root.root["google.protobuf.Empty"][0]
        assert instance.capture_sequence is None
        assert instance.capture_session_id is None

    def test_capture_sequences_by_session_ignore_samples_without_sequence(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        (tmp_path / "instancied_msg_infos.json").write_text(
            json.dumps(
                {
                    "Alpha": [
                        runtime_entry({"value": 1}, capture_sequence=None, capture_session_id="session-a"),
                        runtime_entry({"value": 2}, capture_sequence=4, capture_session_id="session-a"),
                    ]
                }
            ),
            encoding="utf-8",
        )
        message = root_message("Alpha")

        assert runtime_data_store.get_capture_sequences_by_session_for_obf_message(
            message=message,
            obf_messages_by_cls={"Alpha": message},
        ) == {"session-a": (4,)}

    def test_capture_sequences_are_grouped_by_session_and_ignore_legacy_samples(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        (tmp_path / "instancied_msg_infos.json").write_text(
            json.dumps(
                {
                    "Alpha": [
                        runtime_entry({"value": 1}, capture_sequence=9),
                        runtime_entry({"value": 2}, capture_sequence=4, capture_session_id="session-a"),
                        runtime_entry({"value": 3}, capture_sequence=2, capture_session_id="session-a"),
                        runtime_entry({"value": 4}, capture_sequence=1, capture_session_id="session-b"),
                    ]
                }
            ),
            encoding="utf-8",
        )
        message = root_message("Alpha")

        assert runtime_data_store.get_capture_sequences_by_session_for_obf_message(
            message=message,
            obf_messages_by_cls={"Alpha": message},
        ) == {"session-a": (2, 4), "session-b": (1,)}

    def test_runtime_data_store_caches_normalized_content(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        (tmp_path / "instancied_msg_infos.json").write_text(
            json.dumps({"Alpha": [runtime_entry({"value": 1}), runtime_entry({"value": 2})]}),
            encoding="utf-8",
        )
        message = root_message("Alpha")
        messages_by_cls = {"Alpha": message}

        first_instances = runtime_data_store.get_normalized_content_for_obf_message(
            message=message, obf_messages_by_cls=messages_by_cls
        )
        second_instances = runtime_data_store.get_normalized_content_for_obf_message(
            message=message, obf_messages_by_cls=messages_by_cls
        )

        assert first_instances is second_instances
        assert first_instances == (
            {"value": 1, "from_server": False, "is_game_msg": False, "is_root_msg": True},
            {"value": 2, "from_server": False, "is_game_msg": False, "is_root_msg": True},
        )

    def test_runtime_data_store_returns_empty_tuple_when_runtime_alias_is_missing(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        (tmp_path / "instancied_msg_infos.json").write_text(
            json.dumps({"Beta": [runtime_entry({"value": 3})], "Gamma": []}),
            encoding="utf-8",
        )
        message = root_message("Gamma")

        assert (
            runtime_data_store.get_normalized_content_for_obf_message(
                message=message, obf_messages_by_cls={"Gamma": message}
            )
            == ()
        )

    def test_runtime_data_store_handles_no_json_files(self, runtime_data_store: RuntimeDataStore) -> None:
        message = root_message("AnyMsg")

        assert (
            runtime_data_store.get_normalized_content_for_obf_message(
                message=message, obf_messages_by_cls={"AnyMsg": message}
            )
            == ()
        )

    def test_runtime_data_store_caps_per_name(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        cap = 1_500
        oversized = [{"i": index} for index in range(cap + 50)]
        (tmp_path / "instancied_msg_infos.json").write_text(
            json.dumps({"Big": [runtime_entry(payload) for payload in oversized]}),
            encoding="utf-8",
        )
        message = root_message("Big")

        assert (
            len(
                runtime_data_store.get_normalized_content_for_obf_message(
                    message=message, obf_messages_by_cls={"Big": message}
                )
            )
            == cap + 50
        )

    def test_runtime_data_store_reads_only_filtered_alias_for_nested_obf_message(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        (tmp_path / "instancied_msg_infos.json").write_text(
            json.dumps(
                {
                    "kmv.kmt": [runtime_entry({"value": 1})],
                    "kmv.kmu.kmt": [runtime_entry({"value": 999})],
                }
            ),
            encoding="utf-8",
        )
        obf_root = DumpCSMessage(file_descriptor="GameReflection", name="kmv", namespace="kmv")
        obf_container = DumpCSMessage(
            file_descriptor="GameReflection",
            name="kmu",
            namespace="kmv",
            parent_name="kmv",
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="kmt",
            namespace="kmv",
            parent_name="kmv.kmu",
        )
        messages_by_cls = {
            "kmv": obf_root,
            "kmv.kmu": obf_container,
            "kmv.kmu.kmt": obf_message,
        }

        assert runtime_data_store.get_normalized_content_for_obf_message(
            message=obf_message, obf_messages_by_cls=messages_by_cls
        ) == ({"value": 1, "from_server": False, "is_game_msg": False, "is_root_msg": True},)

    def test_write_captured_content_does_nothing_when_the_process_captured_nothing(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        """Reading the store must never be enough to rewrite it.

        `src/protocol/protocol_game.py` registers `write_captured_content` with `atexit`, so every
        process that imports it reaches this on the way out - test runs included, by which point
        RUNTIME_DATA_FILE points back at the real shared file.
        """
        store_path = tmp_path / "instancied_msg_infos.json"
        store_path.write_text('{"krl": []}', encoding="utf-8")

        # Drop the cached view so the buffer is seeded from disk, exactly as the exit hook finds it
        # once the fixture teardown has cleared every cached property.
        runtime_data_store.__dict__.pop(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            "_writing_content", None
        )
        assert runtime_data_store._writing_content == {"krl": []}  # pyright: ignore[reportPrivateUsage]

        runtime_data_store.write_captured_content()

        assert store_path.read_text(encoding="utf-8") == '{"krl": []}'
