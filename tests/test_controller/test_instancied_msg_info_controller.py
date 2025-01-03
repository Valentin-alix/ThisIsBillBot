import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from google.protobuf.field_mask_pb2 import FieldMask

os.environ.setdefault("HOME", os.getcwd())
os.environ.setdefault("PC_ID", "test")

TEMP_ROOT = os.path.join(os.getcwd(), "resources", "logs")
os.makedirs(TEMP_ROOT, exist_ok=True)
TEST_PATH = os.path.join(TEMP_ROOT, "instancied_msg_infos_test.json")

from src.controller.instancied_msg_info_controller import (
    MAX_COUNT_BY_NAME,
    InstanciedMessageInfoController,
)


class InstanciedMessageInfoControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = InstanciedMessageInfoController()
        self.controller._content_by_name = {}

    def tearDown(self) -> None:
        self.controller._content_by_name = {}
        vars(self.controller).pop("path_msg_infos", None)
        if os.path.exists(TEST_PATH):
            os.remove(TEST_PATH)

    def test_update_msg_infos_content_serializes_repeated_scalar_fields(self) -> None:
        message = FieldMask(paths=["alpha", "beta"])

        serialized = self.controller._update_msg_infos_content(
            message, from_server=False, is_game_msg=True, is_root_msg=True
        )

        self.assertEqual(serialized["paths"], ["alpha", "beta"])
        self.assertEqual(
            self.controller._content_by_name,
            {message.DESCRIPTOR.full_name: [serialized]},
        )

    def test_update_msg_infos_content_keeps_empty_repeated_scalar_fields(self) -> None:
        message = FieldMask()

        serialized = self.controller._update_msg_infos_content(
            message, from_server=False, is_game_msg=True, is_root_msg=True
        )

        self.assertEqual(serialized["paths"], [])

    def test_add_msg_respects_max_count_cap(self) -> None:
        name = FieldMask.DESCRIPTOR.full_name
        assert self.controller._content_by_name is not None
        self.controller._content_by_name[name] = [
            {"paths": []} for _ in range(MAX_COUNT_BY_NAME)
        ]

        self.controller.add_msg(
            FieldMask(paths=["extra"]), from_server=False, is_game_msg=True
        )

        self.assertEqual(len(self.controller._content_by_name[name]), MAX_COUNT_BY_NAME)

    def test_content_by_name_returns_empty_when_file_missing(self) -> None:
        vars(self.controller)["path_msg_infos"] = TEST_PATH
        self.controller._content_by_name = None

        self.assertEqual(self.controller.content_by_name, {})

    def test_content_by_name_returns_empty_on_corrupt_file(self) -> None:
        with open(TEST_PATH, "w", encoding="utf-8") as file_handle:
            file_handle.write("not-json{")
        vars(self.controller)["path_msg_infos"] = TEST_PATH
        self.controller._content_by_name = None

        self.assertEqual(self.controller.content_by_name, {})

    def test_content_by_name_applies_cap_when_loading(self) -> None:
        name = "message.Big"
        oversized = [{"i": index} for index in range(MAX_COUNT_BY_NAME + 50)]
        with open(TEST_PATH, "w", encoding="utf-8") as file_handle:
            json.dump({name: oversized}, file_handle)
        vars(self.controller)["path_msg_infos"] = TEST_PATH
        self.controller._content_by_name = None

        self.assertEqual(len(self.controller.content_by_name[name]), MAX_COUNT_BY_NAME)

    def test_content_by_name_filters_non_dict_entries(self) -> None:
        with open(TEST_PATH, "w", encoding="utf-8") as file_handle:
            json.dump({"msg.name": [{"a": 1}, "ignored", 42, {"b": 2}]}, file_handle)
        vars(self.controller)["path_msg_infos"] = TEST_PATH
        self.controller._content_by_name = None

        self.assertEqual(
            self.controller.content_by_name["msg.name"], [{"a": 1}, {"b": 2}]
        )

    def test_write_msg_info_content_persists_json(self) -> None:
        name = FieldMask.DESCRIPTOR.full_name
        self.controller._content_by_name = {name: [{"paths": ["alpha", "beta"]}]}

        vars(self.controller)["path_msg_infos"] = TEST_PATH

        self.controller._write_msg_info_content()

        with open(TEST_PATH, encoding="utf-8") as file_handle:
            written = json.load(file_handle)

        self.assertEqual(written, {name: [{"paths": ["alpha", "beta"]}]})

    def test_write_msg_info_content_no_ops_when_empty(self) -> None:
        self.controller._content_by_name = {}

        vars(self.controller)["path_msg_infos"] = TEST_PATH

        self.controller._write_msg_info_content()

        self.assertFalse(os.path.exists(TEST_PATH))

    def test_write_msg_info_content_no_ops_when_dummy_path(self) -> None:
        name = FieldMask.DESCRIPTOR.full_name
        self.controller._content_by_name = {name: [{"paths": ["x"]}]}
        vars(self.controller)["path_msg_infos"] = "DUMMY_PATH"

        self.controller._write_msg_info_content()

    def test_add_msg_survives_corrupt_existing_file(self) -> None:
        with open(TEST_PATH, "wb") as file_handle:
            file_handle.write(b"garbage")
        vars(self.controller)["path_msg_infos"] = TEST_PATH
        self.controller._content_by_name = None

        self.controller.add_msg(
            FieldMask(paths=["alpha"]), from_server=False, is_game_msg=True
        )

        assert self.controller._content_by_name is not None
        self.assertEqual(
            self.controller._content_by_name[FieldMask.DESCRIPTOR.full_name],
            [
                {
                    "from_server": False,
                    "is_game_msg": True,
                    "is_root_msg": True,
                    "paths": ["alpha"],
                }
            ],
        )

    def test_path_msg_infos_uses_bot_shared_datas_dir_env(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            shared_datas_dir = Path(tmp_dir)
            with patch.dict(
                os.environ,
                {"BOT_SHARED_DATAS_DIR": str(shared_datas_dir), "PC_ID": "envtest"},
            ):
                vars(self.controller).pop("path_msg_infos", None)

                self.assertEqual(
                    self.controller.path_msg_infos,
                    str(shared_datas_dir / "instancied_msg_infos_envtest.json"),
                )
