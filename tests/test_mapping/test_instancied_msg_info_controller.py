import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from google.protobuf.message import Message
from pandas import DataFrame

from D3Mapping.d3_mapping.controller.instancied_msg_info_controller import (
    InstanciedMessageInfoController,
)


class TestInstanciedMessageInfoController(unittest.TestCase):

    def setUp(self):
        if hasattr(InstanciedMessageInfoController, "_instances"):
            InstanciedMessageInfoController._instances.clear()

    def test_total_pending_rows_increments_correctly(self):
        with patch.dict(os.environ, {"PC_ID": "test"}):
            controller = InstanciedMessageInfoController()
            controller._df = DataFrame(columns=["name", "content"])
            controller._total_pending_rows = 0

            assert controller._total_pending_rows == 0

            mock_msg = MagicMock(spec=Message)
            mock_msg.DESCRIPTOR.full_name = "test.Message"
            mock_msg.DESCRIPTOR.fields = []

            controller._update_msg_infos_content(mock_msg, True)

            assert controller._total_pending_rows == 1

            controller._update_msg_infos_content(mock_msg, True)
            controller._update_msg_infos_content(mock_msg, True)

            assert controller._total_pending_rows == 3

    def test_total_pending_rows_resets_after_write(self):
        with patch.dict(os.environ, {"PC_ID": "test"}):
            controller = InstanciedMessageInfoController()
            controller._df = DataFrame(columns=["name", "content"])
            controller._total_pending_rows = 100

            controller._rows_to_add_by_name = {"test": [{"name": "test", "content": {}}]}

            with tempfile.TemporaryDirectory() as tmpdir:
                with patch(
                    "D3Mapping.d3_mapping.controller.instancied_msg_info_controller.PATH_BOT_SHARED_DATAS",
                    tmpdir,
                ):
                    controller._write_msg_info_content()

                    assert controller._total_pending_rows == 0

    def test_no_list_copy_in_sub_values(self):
        with patch.dict(os.environ, {"PC_ID": "test"}):
            controller = InstanciedMessageInfoController()
            controller._df = DataFrame(columns=["name", "content"])

            mock_msg = MagicMock(spec=Message)
            mock_msg.DESCRIPTOR.full_name = "test.ParentMessage"

            mock_field = MagicMock()
            mock_field.name = "sub_messages"
            mock_field.label = 3
            mock_field.type = 11
            mock_field.message_type.GetOptions.return_value.map_entry = False

            mock_msg.DESCRIPTOR.fields = [mock_field]

            mock_sub_msg = MagicMock(spec=Message)
            mock_sub_msg.DESCRIPTOR.full_name = "test.SubMessage"
            mock_sub_msg.DESCRIPTOR.fields = []

            mock_msg.sub_messages = [mock_sub_msg]

            result = controller._update_msg_infos_content(mock_msg, True)

            assert "sub_messages" in result
            assert isinstance(result["sub_messages"], list)

    def test_google_protobuf_any_check_outside_loop(self):
        with patch.dict(os.environ, {"PC_ID": "test"}):
            controller = InstanciedMessageInfoController()
            controller._df = DataFrame(columns=["name", "content"])

            mock_msg = MagicMock(spec=Message)
            mock_msg.DESCRIPTOR.full_name = "google.protobuf.Any"

            mock_field_value = MagicMock()
            mock_field_value.name = "value"
            mock_field_value.label = 1
            mock_field_value.type = 12

            mock_field_type_url = MagicMock()
            mock_field_type_url.name = "type_url"
            mock_field_type_url.label = 1
            mock_field_type_url.type = 9

            mock_msg.DESCRIPTOR.fields = [mock_field_type_url, mock_field_value]
            mock_msg.type_url = "type.googleapis.com/test.Message"
            mock_msg.value = b"test_value"

            result = controller._update_msg_infos_content(mock_msg, True)

            assert "value" not in result
            assert "type_url" in result

    def test_add_msg_check_within_lock(self):
        with patch.dict(os.environ, {"PC_ID": "test"}):
            controller = InstanciedMessageInfoController()
            controller._df = DataFrame(columns=["name", "content"])

            mock_msg = MagicMock(spec=Message)
            mock_msg.DESCRIPTOR.full_name = "test.Message"
            mock_msg.DESCRIPTOR.fields = []

            with patch.object(
                controller, "_write_msg_info_content"
            ) as mock_write:
                controller._total_pending_rows = 500_001

                controller.add_msg(mock_msg, True)

                mock_write.assert_called_once()


if __name__ == "__main__":
    unittest.main()
