import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from tests.fixtures.proto_mapper.message_builders import root_message
from tests.fixtures.proto_mapper.runtime_builders import runtime_entry
from google.protobuf.empty_pb2 import Empty

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.interfaces.runtime_data import RuntimeCaptureDocument
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


def _write_runtime_capture(path: Path, schema_fingerprint: str, root: dict[str, list[dict[str, object]]]) -> None:
    path.write_text(
        json.dumps({"schema_fingerprint": schema_fingerprint, "root": root}),
        encoding="utf-8",
    )


class TestRuntimeDataStore:
    @pytest.mark.parametrize("from_server", [True, False])
    def test_game_message_capture_stores_unpacked_obfuscated_payload(
        self,
        runtime_data_store: RuntimeDataStore,
        from_server: bool,
    ) -> None:
        from google.protobuf.any_pb2 import Any as ProtoAny

        from DBDofusUnity.datas.protos.obf.game.game_messages_pb2 import hea, hee, hnh, hnl
        from src.protocol.protocol_game import get_game_msg

        spells = hnl(fmuv=[hnh(fmuh=13108, fmul=1)], fmuw=True)
        event_content = ProtoAny(type_url="type.ankama.com/hnl", value=spells.SerializeToString())
        game_message = hea(fllk=hee(flme=event_content))

        get_game_msg(game_message.SerializeToString(), do_dump_values=True, from_server=from_server)
        runtime_data_store.write_captured_content()

        captured_messages = RuntimeCaptureDocument.model_validate_json(
            runtime_data_store.path.read_text(encoding="utf-8")
        )
        assert captured_messages.schema_fingerprint == runtime_data_store.schema_fingerprint
        assert captured_messages.root["hnl"][0].from_server is from_server
        assert captured_messages.root["hea"][0].from_server is None
        assert captured_messages.root["hnh"][0].from_server is None
        captured_spells = captured_messages.root["hnl"][0].model_extra
        assert captured_spells is not None
        assert captured_spells["fmuv"]
        assert captured_spells["fmux"] == []

    def test_game_message_capture_skips_root_and_payload_when_disabled(
        self,
        runtime_data_store: RuntimeDataStore,
    ) -> None:
        from google.protobuf.any_pb2 import Any as ProtoAny

        from DBDofusUnity.datas.protos.obf.game.game_messages_pb2 import hea, hee, hnh, hnl
        from src.protocol.protocol_game import get_game_msg

        spells = hnl(fmuv=[hnh(fmuh=13108, fmul=1)], fmuw=True)
        event_content = ProtoAny(type_url="type.ankama.com/hnl", value=spells.SerializeToString())
        game_message = hea(fllk=hee(flme=event_content))

        get_game_msg(game_message.SerializeToString(), do_dump_values=False, from_server=True)
        runtime_data_store.write_captured_content()

        assert not runtime_data_store.path.exists()

    def test_capture_rejects_root_payload_without_direction(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        with pytest.raises(ValidationError, match="Captured root payloads require from_server"):
            runtime_data_store.add_msg(Empty(), from_server=None, is_game_msg=False)
        runtime_data_store.write_captured_content()
        assert not runtime_data_store.path.exists()

    def test_loading_capture_rejects_root_payload_without_direction(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        _write_runtime_capture(
            runtime_data_store.path,
            runtime_data_store.schema_fingerprint,
            {"Alpha": [runtime_entry({}) | {"from_server": None}]},
        )
        with pytest.raises(ValidationError, match="Captured root payloads require from_server"):
            _ = runtime_data_store.content_by_name

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

        runtime_root = RuntimeCaptureDocument.model_validate_json(runtime_data_store.path.read_text(encoding="utf-8"))
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
        runtime_data_store.add_msg(Empty(), from_server=True, is_game_msg=False)
        runtime_data_store.write_captured_content()

        runtime_root = RuntimeCaptureDocument.model_validate_json(runtime_data_store.path.read_text(encoding="utf-8"))
        instance = runtime_root.root["google.protobuf.Empty"][0]
        assert instance.capture_sequence is None
        assert instance.capture_session_id is None

    def test_capture_sequences_by_session_ignore_samples_without_sequence(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        _write_runtime_capture(
            tmp_path / "instancied_msg_infos.json",
            runtime_data_store.schema_fingerprint,
            {
                "Alpha": [
                    runtime_entry({"value": 1}, capture_sequence=None, capture_session_id="session-a"),
                    runtime_entry({"value": 2}, capture_sequence=4, capture_session_id="session-a"),
                ]
            },
        )
        message = root_message("Alpha")

        assert runtime_data_store.get_capture_sequences_by_session_for_obf_message(
            message=message,
            obf_messages_by_cls={"Alpha": message},
        ) == {"session-a": (4,)}
        observed = runtime_data_store.get_observed_root_obf_messages()["Alpha"]
        assert observed.capture_session_ids == ("session-a",)

    def test_capture_sequences_are_grouped_by_session_and_ignore_legacy_samples(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        _write_runtime_capture(
            tmp_path / "instancied_msg_infos.json",
            runtime_data_store.schema_fingerprint,
            {
                "Alpha": [
                    runtime_entry({"value": 1}, capture_sequence=9),
                    runtime_entry({"value": 2}, capture_sequence=4, capture_session_id="session-a"),
                    runtime_entry({"value": 3}, capture_sequence=2, capture_session_id="session-a"),
                    runtime_entry({"value": 4}, capture_sequence=1, capture_session_id="session-b"),
                ]
            },
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
        _write_runtime_capture(
            tmp_path / "instancied_msg_infos.json",
            runtime_data_store.schema_fingerprint,
            {"Alpha": [runtime_entry({"value": 1}), runtime_entry({"value": 2})]},
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
        _write_runtime_capture(
            tmp_path / "instancied_msg_infos.json",
            runtime_data_store.schema_fingerprint,
            {"Beta": [runtime_entry({"value": 3})], "Gamma": []},
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

    def test_runtime_data_store_deletes_legacy_capture_without_fingerprint(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        store_path = tmp_path / "instancied_msg_infos.json"
        store_path.write_text(json.dumps({"Alpha": [runtime_entry({"value": 1})]}), encoding="utf-8")
        runtime_data_store.write_captured_content()
        assert not store_path.exists()

    def test_runtime_data_store_deletes_capture_from_another_schema(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        store_path = tmp_path / "instancied_msg_infos.json"
        _write_runtime_capture(
            store_path,
            "different-schema-fingerprint",
            {"Alpha": [runtime_entry({"value": 1})]},
        )
        message = root_message("Alpha")

        assert runtime_data_store.get_normalized_content_for_obf_message(
            message=message,
            obf_messages_by_cls={"Alpha": message},
        ) == ()
        assert not store_path.exists()

    def test_runtime_data_store_caps_per_name(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        cap = 1_500
        oversized = [{"i": index} for index in range(cap + 50)]
        _write_runtime_capture(
            tmp_path / "instancied_msg_infos.json",
            runtime_data_store.schema_fingerprint,
            {"Big": [runtime_entry(payload) for payload in oversized]},
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
        _write_runtime_capture(
            tmp_path / "instancied_msg_infos.json",
            runtime_data_store.schema_fingerprint,
            {
                "kmv.kmt": [runtime_entry({"value": 1})],
                "kmv.kmu.kmt": [runtime_entry({"value": 999})],
            },
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
        store_path = tmp_path / "instancied_msg_infos.json"
        _write_runtime_capture(
            store_path,
            runtime_data_store.schema_fingerprint,
            {"krl": []},
        )
        expected_document = store_path.read_text(encoding="utf-8")

        runtime_data_store.write_captured_content()

        assert store_path.read_text(encoding="utf-8") == expected_document
